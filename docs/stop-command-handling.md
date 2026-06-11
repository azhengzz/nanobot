# Nanobot `/stop` 指令处理逻辑详细分析

> 本文档完整分析 Nanobot 在收到 `/stop` 指令后的处理流程，供在其他 Agent 中实现类似功能时参考。

---

## 1. 整体架构概览

```
用户输入 /stop
    │
    ▼
MessageBus.consume_inbound()          ← 消息总线接收
    │
    ▼
AgentLoop.run()                       ← 主循环检测到 priority command
    │
    ▼
CommandRouter.dispatch_priority()     ← 优先级路由分发
    │
    ▼
cmd_stop()                            ← 执行取消逻辑
    │
    ├─► loop._active_tasks.pop()      ← 取消主 Agent 任务
    │       └─ task.cancel() × N
    │
    └─► subagents.cancel_by_session() ← 取消子 Agent 任务
            └─ task.cancel() × N
    │
    ▼
返回 "Stopped N task(s)." 确认消息
```

---

## 2. 核心设计：三级命令路由

文件：`nanobot/command/router.py`

```python
class CommandRouter:
    # 三级命令优先级：
    # 1. priority  — 不经过任何锁，立即执行（/stop, /restart）
    # 2. exact     — 精确匹配，在 session lock 内执行（/new, /help）
    # 3. prefix    — 前缀匹配（如 "/team "）
    # 4. interceptors — 回退拦截器
```

**`/stop` 被注册为 priority 命令**，意味着它：
- **不经过 session lock**：不会被当前正在执行的 Agent 任务阻塞
- **不经过 concurrency gate**：不受并发请求数量限制
- **立即响应**：在 `run()` 主循环中直接同步处理

---

## 3. 完整执行流程（逐步追踪）

### 3.1 消息接收与优先级检测

文件：`nanobot/agent/loop.py:289-314`

```python
async def run(self) -> None:
    self._running = True
    while self._running:
        # ① 从消息总线取消息（1秒超时轮询）
        msg = await asyncio.wait_for(self.bus.consume_inbound(), timeout=1.0)

        raw = msg.content.strip()

        # ② 优先级命令检测 — /stop 在这里被拦截
        if self.commands.is_priority(raw):
            ctx = CommandContext(msg=msg, session=None, key=msg.session_key,
                                 raw=raw, loop=self)
            result = await self.commands.dispatch_priority(ctx)
            if result:
                await self.bus.publish_outbound(result)
            continue  # ← 跳过普通分发，不创建 task

        # ③ 普通消息才会走到这里，创建异步 task
        task = asyncio.create_task(self._dispatch(msg))
        self._active_tasks.setdefault(msg.session_key, []).append(task)
        task.add_done_callback(...)  # 完成后从列表移除
```

**关键点**：`/stop` 不进入 `_dispatch()`，不走 session lock，不进 concurrency gate。

### 3.2 stop 命令执行逻辑

文件：`nanobot/command/builtin.py:15-29`

```python
async def cmd_stop(ctx: CommandContext) -> OutboundMessage:
    loop = ctx.loop
    msg = ctx.msg

    # ── 第一步：取消主 Agent 的活跃任务 ──
    tasks = loop._active_tasks.pop(msg.session_key, [])  # 原子取出该 session 的所有 task
    cancelled = sum(1 for t in tasks if not t.done() and t.cancel())  # 只取消未完成的

    # 等待所有 task 真正停止（捕获 CancelledError 和其他异常）
    for t in tasks:
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass

    # ── 第二步：取消子 Agent 任务 ──
    sub_cancelled = await loop.subagents.cancel_by_session(msg.session_key)

    # ── 第三步：返回结果 ──
    total = cancelled + sub_cancelled
    content = f"Stopped {total} task(s)." if total else "No active task to stop."
    return OutboundMessage(channel=msg.channel, chat_id=msg.chat_id, content=content)
```

### 3.3 子 Agent 取消逻辑

文件：`nanobot/agent/subagent.py:248-256`

```python
async def cancel_by_session(self, session_key: str) -> int:
    """Cancel all subagents for the given session. Returns count cancelled."""
    # 找到该 session 下所有正在运行的子 agent task
    tasks = [self._running_tasks[tid]
             for tid in self._session_tasks.get(session_key, [])
             if tid in self._running_tasks and not self._running_tasks[tid].done()]

    # 逐一调用 cancel()
    for t in tasks:
        t.cancel()

    # 等待所有 task 完成（gather + return_exceptions 确保不抛异常）
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    return len(tasks)
```

### 3.4 CancelledError 在任务链中的传播

当 `task.cancel()` 被调用后，`CancelledError` 沿以下路径传播：

```
task.cancel()
    │
    ▼
AgentLoop._dispatch(msg)                    # loop.py:315
    │   async with lock, gate:              # ← CancelledError 会中断 lock/gate
    │   ...
    │   except asyncio.CancelledError:       # loop.py:363-365
    │       logger.info("Task cancelled...")
    │       raise                            # ← 重新抛出，确保 task 真正取消
    │
    ▼
AgentLoop._process_message(msg)              # loop.py:396
    │
    ▼
AgentLoop._run_agent_loop(...)               # loop.py:208
    │
    ▼
AgentRunner.run(spec)                        # runner.py:59
    │   for iteration in range(max_iterations):
    │       response = await self.provider.chat_with_retry(...)  # ← 在 await 点被中断
    │
    ▼
AgentRunner._execute_tools(spec, tool_calls) # runner.py:180
    │   tool_results = await asyncio.gather(...)  # ← 工具执行被中断
    │
    ▼
AgentRunner._run_tool(spec, tool_call)       # runner.py:206
    │   result = await spec.tools.execute(...)
    │   except asyncio.CancelledError:
    │       raise                            # ← 工具层重新抛出，不吞掉取消信号
```

---

## 4. 数据结构设计

### 4.1 主 Agent 任务追踪

```python
# loop.py:109
self._active_tasks: dict[str, list[asyncio.Task]] = {}
# key = session_key (如 "telegram:123456")
# value = 该 session 下所有活跃的 asyncio.Task 列表
```

**生命周期**：
- 创建时：`_active_tasks.setdefault(session_key, []).append(task)` (loop.py:312)
- 完成时：通过 `done_callback` 自动从列表移除 (loop.py:313)
- 取消时：`_active_tasks.pop(session_key)` 原子取出 (builtin.py:19)

### 4.2 子 Agent 任务追踪

```python
# subagent.py:49-50
self._running_tasks: dict[str, asyncio.Task[None]] = {}      # task_id → Task
self._session_tasks: dict[str, set[str]] = {}                 # session_key → {task_ids}
```

**生命周期**：
- 创建时：`_running_tasks[task_id] = bg_task` + `_session_tasks[session_key].add(task_id)` (subagent.py:68-70)
- 完成时：通过 `_cleanup` callback 自动清理 (subagent.py:72-79)
- 取消时：`cancel_by_session()` 按 session_key 查找并取消 (subagent.py:248)

### 4.3 Session Key 设计

```python
# events.py:22-24
@property
def session_key(self) -> str:
    return self.session_key_override or f"{self.channel}:{self.chat_id}"
```

**作用**：`/stop` 只取消**当前 session** 的任务，不影响其他用户/频道的任务。

---

## 5. 安全性设计

### 5.1 Session 隔离

`/stop` 通过 `msg.session_key` 精确匹配：
- Telegram 用户 A 发 `/stop` → 只取消 A 的任务
- Discord 频道 B 的 `/stop` → 只取消 B 的任务
- 子 Agent 也按 `session_key` 隔离

### 5.2 原子操作

```python
tasks = loop._active_tasks.pop(msg.session_key, [])
```

使用 `pop()` 一次性取出并清空，防止重复取消。

### 5.3 等待任务真正停止

```python
for t in tasks:
    try:
        await t
    except (asyncio.CancelledError, Exception):
        pass
```

取消后 `await` 每个 task，确保资源释放完成再返回。不使用 `asyncio.gather` 是因为需要逐个等待。

### 5.4 子 Agent 的 `_cleanup` 回调

```python
def _cleanup(_: asyncio.Task) -> None:
    self._running_tasks.pop(task_id, None)
    if session_key and (ids := self._session_tasks.get(session_key)):
        ids.discard(task_id)
        if not ids:
            del self._session_tasks[session_key]
```

无论 task 正常完成还是被取消，`_cleanup` 都会执行，保证数据结构干净。

### 5.5 取消不影响 Session 持久化

`CancelledError` 在 `_dispatch` 层被捕获并 re-raise，不会走到 `_process_message` 的 `session.save()` 逻辑，避免保存不完整的对话状态。

---

## 6. 在其他 Agent 中实现类似功能的参考模板

### 6.1 最小实现清单

```python
# 1. 命令路由：支持优先级命令
class CommandRouter:
    def __init__(self):
        self._priority: dict[str, Handler] = {}

    def is_priority(self, text: str) -> bool:
        return text.strip().lower() in self._priority

    async def dispatch_priority(self, ctx) -> OutboundMessage | None:
        handler = self._priority.get(ctx.raw.lower())
        return await handler(ctx) if handler else None

# 2. 任务追踪：维护 session → tasks 映射
self._active_tasks: dict[str, list[asyncio.Task]] = {}

# 3. stop 处理器
async def cmd_stop(ctx: CommandContext) -> OutboundMessage:
    tasks = loop._active_tasks.pop(ctx.msg.session_key, [])
    cancelled = sum(1 for t in tasks if not t.done() and t.cancel())
    for t in tasks:
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass
    return OutboundMessage(...)

# 4. 在主循环中优先处理
async def run(self):
    while self._running:
        msg = await get_next_message()
        if self.commands.is_priority(msg.content.strip()):
            # 直接处理，不走锁、不创建 task
            result = await self.commands.dispatch_priority(ctx)
            continue
        # 普通消息才创建 tracked task
        task = asyncio.create_task(self._dispatch(msg))
        self._active_tasks.setdefault(msg.session_key, []).append(task)

# 5. CancelledError 透传
# 在 _dispatch 和工具执行层：
except asyncio.CancelledError:
    logger.info("Task cancelled")
    raise  # 不要吞掉取消信号
```

### 6.2 如果还需要子 Agent 支持

```python
class SubagentManager:
    _running_tasks: dict[str, asyncio.Task] = {}       # task_id → Task
    _session_tasks: dict[str, set[str]] = {}            # session → {task_ids}

    async def cancel_by_session(self, session_key: str) -> int:
        tasks = [self._running_tasks[tid]
                 for tid in self._session_tasks.get(session_key, [])
                 if tid in self._running_tasks and not self._running_tasks[tid].done()]
        for t in tasks:
            t.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        return len(tasks)
```

### 6.3 关键设计原则

| 原则 | 说明 |
|------|------|
| **优先级绕行** | stop 类命令必须绕过所有锁和并发控制，确保随时可执行 |
| **Session 隔离** | 取消操作只影响当前 session，不波及其他用户 |
| **原子取走** | 用 `pop()` 取出任务列表，防止重复取消 |
| **等待完成** | 取消后 `await` 所有 task，确保资源释放 |
| **异常不吞** | `CancelledError` 在各层 re-raise，不做静默处理 |
| **自动清理** | 通过 `done_callback` 自动维护任务列表 |

---

## 7. 涉及的核心文件

| 文件 | 职责 |
|------|------|
| `nanobot/command/builtin.py` | `/stop` 命令的具体实现和注册 |
| `nanobot/command/router.py` | 三级命令路由（priority / exact / prefix） |
| `nanobot/agent/loop.py` | 主循环：优先级检测、任务追踪、消息分发 |
| `nanobot/agent/runner.py` | Agent 执行引擎：CancelledError 透传 |
| `nanobot/agent/subagent.py` | 子 Agent 管理器：按 session 取消 |
| `nanobot/bus/events.py` | 消息类型定义、session_key 生成 |
