# coding=utf-8

import json
import asyncio
from pathlib import Path
from typing import Any, Optional
import asyncssh
import aiofiles
import re

from nanobot.agent.tools.base import Tool


__all__ = ("SSHCommand", "GetSSHAccessInfo")

# Store established SSH connections
# key = ip + port + username
SSH_CONNECTIONS = {}

ENV_JSON_FILE = Path(__file__).parent / "env.json"

def get_connection_key(ip: str, port: str, username: str) -> str:
    """Get SSH connection key."""
    return f'{username}@{ip}:{port}'

def get_connection_by_key(key: str) -> Optional[Any]:
    return SSH_CONNECTIONS.get(key, None)

def update_connection_by_key(key: str, conn: Any) -> None:
    SSH_CONNECTIONS.update({key: conn})


async def update_ssh_access_info(ip: str, port: int, username: str, password: str) -> None:
    """Cache SSH access info to env.json."""
    try:
        # Read existing data
        async with aiofiles.open(ENV_JSON_FILE, "r", encoding="utf-8") as f:
            content = await f.read()
            ssh_list = json.loads(content) if content.strip() else []
    except (FileNotFoundError, json.JSONDecodeError):
        ssh_list = []

    # Check if connection already exists
    exists = any(
        item.get("ip") == ip and
        item.get("port") == str(port) and
        item.get("username") == username
        for item in ssh_list
    )

    # Add if not exists
    if not exists:
        ssh_list.append({
            "ip": ip,
            "port": str(port),
            "username": username,
            "password": password,
            "alias": [f"{username}@{ip}:{port}", ip]
        })

        # Write back to file
        async with aiofiles.open(ENV_JSON_FILE, "w", encoding="utf-8") as f:
            await f.write(json.dumps(ssh_list, ensure_ascii=False, indent=2))


class SSHCommand(Tool):
    """Execute shell commands on remote server via SSH."""

    name = "ssh_command"
    description = (
        "Execute a shell command on a remote server via SSH and return its output. Use with caution."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute"
            },
            "ip": {
                "type": "string",
                "description": "IP address of the remote server"
            },
            "port": {
                "type": "string",
                "description": "SSH port of the remote server"
            },
            "username": {
                "type": "string",
                "description": "SSH login username"
            },
            "password": {
                "type": "string",
                "description": "SSH login password"
            },
        },
        "required": ["command", "ip", "port", "username", "password"]
    }

    def __init__(
            self,
            timeout: int = 60,
            deny_patterns: list[str] | None = None,
            allow_patterns: list[str] | None = None,
        ):
        self.timeout = timeout
        # Copy From agent/tools/shell.py
        self.deny_patterns = deny_patterns or [
            r"\brm\s+-[rf]{1,2}\b",          # rm -r, rm -rf, rm -fr
            r"\bdel\s+/[fq]\b",              # del /f, del /q
            r"\brmdir\s+/s\b",               # rmdir /s
            r"(?:^|[;&|]\s*)format\b",       # format (as standalone command only)
            r"\b(mkfs|diskpart)\b",          # disk operations
            r"\bdd\s+if=",                   # dd
            r">\s*/dev/sd",                  # write to disk
            r"\b(shutdown|reboot|poweroff)\b",  # system power
            r":\(\)\s*\{.*\};\s*:",          # fork bomb
        ]
        self.allow_patterns = allow_patterns or []

    async def execute(self, command: str, ip: str, port: str, username: str, password: str, **kwargs: Any) -> str:
        port = int(port)
        connection_key = get_connection_key(ip=ip, port=port, username=username)
        conn = get_connection_by_key(key=connection_key)

        if not conn:
            # 创建新的异步连接
            try:
                conn = await asyncssh.connect(
                    host=ip,
                    port=port,
                    username=username,
                    password=password,
                    known_hosts=None  # 禁用主机密钥检查（仅用于测试环境）
                )
                update_connection_by_key(key=connection_key, conn=conn)
                # 更新SSH访问信息到env.json中进行缓存
                await update_ssh_access_info(ip=ip, port=port, username=username, password=password)
            except Exception as e:
                return json.dumps({"stdout": [], "stderr": [f"Connection failed: {str(e)}"]}, ensure_ascii=False)

        guard_error = self._guard_command(command)
        if guard_error:
            return guard_error
        try:
            # 异步执行命令
            result = await conn.run(command, timeout=self.timeout)

            outs = result.stdout.splitlines() if result.stdout else []
            errs = result.stderr.splitlines() if result.stderr else []

            return json.dumps({
                "stdout": outs,
                "stderr": errs,
                "exit_status": result.exit_status
            }, ensure_ascii=False)
        except asyncssh.TimeoutError as e:
            return json.dumps({"stdout": [], "stderr": [f"Error: Command timed out after {self.timeout} seconds"]}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"stdout": [], "stderr": [f"Command failed: {str(e)}"]}, ensure_ascii=False)

    # Copy From agent/tools/shell.py
    def _guard_command(self, command: str) -> str | None:
        """Best-effort safety guard for potentially destructive commands."""
        cmd = command.strip()
        lower = cmd.lower()

        for pattern in self.deny_patterns:
            if re.search(pattern, lower):
                return "Error: Command blocked by safety guard (dangerous pattern detected)"

        if self.allow_patterns:
            if not any(re.search(p, lower) for p in self.allow_patterns):
                return "Error: Command blocked by safety guard (not in allowlist)"

        return None

class GetSSHAccessInfo(Tool):
    """Get cached SSH connection info."""

    name = "get_ssh_access_info"
    description = (
        "Get cached SSH connection info including aliases, IP address, port, username and password. "
        "LLM can select appropriate authentication credentials based on the retrieved alias information."
    )
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def __init__(self):
        pass

    async def execute(self, **kwargs) -> str:
        """Execute the tool to return cached SSH access info."""
        from pathlib import Path
        import aiofiles

        try:
            async with aiofiles.open(ENV_JSON_FILE, "r", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except FileNotFoundError:
            return json.dumps({"error": f"env.json not found at {ENV_JSON_FILE}"}, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON format: {str(e)}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)


