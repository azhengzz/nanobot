# coding=utf-8

import json
import re
from pathlib import Path
from typing import Any

import aiofiles
import asyncssh

from nanobot.agent.tools.base import Tool, tool_parameters
from nanobot.agent.tools.schema import IntegerSchema, StringSchema, tool_parameters_schema


__all__ = ("SSHCommand", "GetSSHAccessInfo")

SSH_CONNECTIONS: dict[str, Any] = {}

ENV_JSON_FILE = Path(__file__).parent / "env.json"


def _connection_key(ip: str, port: str, username: str) -> str:
    return f"{username}@{ip}:{port}"


async def _update_ssh_access_info(ip: str, port: int, username: str, password: str) -> None:
    try:
        async with aiofiles.open(ENV_JSON_FILE, "r", encoding="utf-8") as f:
            content = await f.read()
            ssh_list = json.loads(content) if content.strip() else []
    except (FileNotFoundError, json.JSONDecodeError):
        ssh_list = []

    exists = any(
        item.get("ip") == ip and item.get("port") == str(port) and item.get("username") == username
        for item in ssh_list
    )

    if not exists:
        ssh_list.append({
            "ip": ip,
            "port": str(port),
            "username": username,
            "password": password,
            "alias": [f"{username}@{ip}:{port}", ip],
        })
        async with aiofiles.open(ENV_JSON_FILE, "w", encoding="utf-8") as f:
            await f.write(json.dumps(ssh_list, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# ssh_command
# ---------------------------------------------------------------------------

_DENY_PATTERNS = [
    r"\brm\s+-[rf]{1,2}\b",
    r"\bdel\s+/[fq]\b",
    r"\brmdir\s+/s\b",
    r"(?:^|[;&|]\s*)format\b",
    r"\b(mkfs|diskpart)\b",
    r"\bdd\s+if=",
    r">\s*/dev/sd",
    r"\b(shutdown|reboot|poweroff)\b",
    r":\(\)\s*\{.*\};\s*:",
]


def _guard_command(command: str, allow_patterns: list[str] | None = None) -> str | None:
    lower = command.strip().lower()
    for pattern in _DENY_PATTERNS:
        if re.search(pattern, lower):
            return "Error: Command blocked by safety guard (dangerous pattern detected)"
    if allow_patterns and not any(re.search(p, lower) for p in allow_patterns):
        return "Error: Command blocked by safety guard (not in allowlist)"
    return None


@tool_parameters(
    tool_parameters_schema(
        command=StringSchema("The shell command to execute"),
        ip=StringSchema("IP address of the remote server"),
        port=StringSchema("SSH port of the remote server"),
        username=StringSchema("SSH login username"),
        password=StringSchema("SSH login password"),
        timeout=IntegerSchema(60, description="Command timeout in seconds", minimum=1),
        required=["command", "ip", "port", "username", "password"],
    )
)
class SSHCommand(Tool):
    """Execute shell commands on remote server via SSH."""
    _scopes = {"core"}

    def __init__(
        self,
        timeout: int = 60,
        allow_patterns: list[str] | None = None,
    ):
        self._timeout = timeout
        self._allow_patterns = allow_patterns or []

    @property
    def name(self) -> str:
        return "ssh_command"

    @property
    def description(self) -> str:
        return (
            "Execute a shell command on a remote server via SSH and return its output. Use with caution."
        )

    async def execute(
        self,
        command: str | None = None,
        ip: str | None = None,
        port: str | None = None,
        username: str | None = None,
        password: str | None = None,
        **_kwargs: Any,
    ) -> str:
        if not command:
            return json.dumps({"stdout": [], "stderr": ["Error: command is required"]}, ensure_ascii=False)
        if not ip or not port or not username or not password:
            return json.dumps({"stdout": [], "stderr": ["Error: ip, port, username, password are required"]}, ensure_ascii=False)

        port_int = int(port)
        conn_key = _connection_key(ip=ip, port=port, username=username)
        conn = SSH_CONNECTIONS.get(conn_key)

        if not conn:
            try:
                conn = await asyncssh.connect(
                    host=ip,
                    port=port_int,
                    username=username,
                    password=password,
                    known_hosts=None,
                )
                SSH_CONNECTIONS[conn_key] = conn
            except Exception as e:
                return json.dumps({"stdout": [], "stderr": [f"Connection failed: {e}"]}, ensure_ascii=False)

        await _update_ssh_access_info(ip=ip, port=port_int, username=username, password=password)

        guard_error = _guard_command(command, self._allow_patterns)
        if guard_error:
            return guard_error

        try:
            result = await conn.run(command, timeout=self._timeout)
            outs = result.stdout.splitlines() if result.stdout else []
            errs = result.stderr.splitlines() if result.stderr else []
            return json.dumps({
                "stdout": outs,
                "stderr": errs,
                "exit_status": result.exit_status,
            }, ensure_ascii=False)
        except asyncssh.TimeoutError:
            return json.dumps({"stdout": [], "stderr": [f"Error: Command timed out after {self._timeout} seconds"]}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"stdout": [], "stderr": [f"Command failed: {e}"]}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# get_ssh_access_info
# ---------------------------------------------------------------------------

@tool_parameters(
    tool_parameters_schema(
        required=[],
    )
)
class GetSSHAccessInfo(Tool):
    """Get cached SSH connection info."""
    _scopes = {"core"}

    @property
    def name(self) -> str:
        return "get_ssh_access_info"

    @property
    def description(self) -> str:
        return (
            "Get cached SSH connection info including aliases, IP address, port, username and password. "
            "LLM can select appropriate authentication credentials based on the retrieved alias information."
        )

    @property
    def read_only(self) -> bool:
        return True

    async def execute(self, **kwargs) -> str:
        try:
            async with aiofiles.open(ENV_JSON_FILE, "r", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)
            return json.dumps(data, ensure_ascii=False, indent=2)
        except FileNotFoundError:
            return json.dumps({"error": f"env.json not found at {ENV_JSON_FILE}"}, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON format: {e}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
