# `/stop` 指令实现逻辑分析

## 概述

`/stop` 指令用于取消当前会话（session）中所有正在运行的后台任务和子代理（subagent），是一种**会话级**的紧急停止机制。

## 完整调用链

```
用户输入 /stop
  → MessageBus.publish_inbound()
  → AgentLoop.run() 主循环接收消息
  → commands.is_priority("/stop") == True     ← 优先级命令，跳过锁
  → commands.dispatch_priority(ctx)
  → cmd_stop(ctx)                              ← builtin.py:15
  → 取消常规任务 (_active_tasks)               ← loop.py:311-313 注册
  → 取消子代理   (subagents)                   ← subagent.py:52-79 注册
  → 返回 OutboundMessage
  → bus.publish_outbound(result)               ← 用户看到 "Stopped N task(s)."
```

## 1. 命令注册与优先级分发

### 注册（[builtin.py:103-110](nanobot/command/builtin.py#L103-L110)）

```python
def register_builtin_commands(router: CommandRouter) -> None:
    router.priority("/stop", cmd_stop)   # 注册为 priority 命令
    router.priority("/restart", cmd_restart)
    router.priority("/status", cmd_status)
    router.exact("/new", cmd_new)
    router.exact("/help", cmd_help)
```

`/stop` 被注册为 **priority** 命令（而非 exact），这意味着它会被**立即处理**，不受会话锁（per-session lock）和并发门（concurrency gate）的限制。

### 优先级分发（[loop.py:305-310](nanobot/agent/loop.py#L305-L310)）

```python
raw = msg.content.strip()
if self.commands.is_priority(raw):
    ctx = CommandContext(msg=msg, session=None, key=msg.session_key, raw=raw, loop=self)
    result = await self.commands.dispatch_priority(ctx)
    if result:
        await self.bus.publish_outbound(result)
    continue   # 不进入 _dispatch 流程
```

关键点：
- 优先级命令**直接在主循环中 `await` 执行**，不会被包装成 `asyncio.Task`
- 这保证了 `/stop` 即使在会话锁被其他任务持有时也能**立即响应**
- 执行后 `continue` 跳过正常的消息分发流程

### 路由器匹配（[router.py:57-65](nanobot/command/router.py#L57-L65)）

```python
def is_priority(self, text: str) -> bool:
    return text.strip().lower() in self._priority

async def dispatch_priority(self, ctx: CommandContext) -> OutboundMessage | None:
    handler = self._priority.get(ctx.raw.lower())
    if handler:
        return await handler(ctx)
    return None
```

## 2. `cmd_stop` 核心逻辑（[builtin.py:15-29](nanobot/command/builtin.py#L15-L29)）

```python
async def cmd_stop(ctx: CommandContext) -> OutboundMessage:
    loop = ctx.loop
    msg = ctx.msg

    # ① 弹出该会话的所有常规任务
    tasks = loop._active_tasks.pop(msg.session_key, [])

    # ② 取消尚未完成的任务，统计取消数
    cancelled = sum(1 for t in tasks if not t.done() and t.cancel())

    # ③ 等待所有任务完成清理
    for t in tasks:
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass

    # ④ 取消该会话的所有子代理
    sub_cancelled = await loop.subagents.cancel_by_session(msg.session_key)

    # ⑤ 汇总并返回
    total = cancelled + sub_cancelled
    content = f"Stopped {total} task(s)." if total else "No active task to stop."
    return OutboundMessage(channel=msg.channel, chat_id=msg.chat_id, content=content)
```

### 逐步解析

| 步骤 | 操作 | 说明 |
|------|------|------|
| ① | `_active_tasks.pop()` | 原子性地取出并清空该会话的任务列表，防止新取消请求重复处理 |
| ② | `t.cancel()` | 对每个未完成的 task 调用 `asyncio.Task.cancel()`，注入 `CancelledError` |
| ③ | `await t` | 等待每个任务真正结束，确保资源清理完成；异常全部静默吞掉 |
| ④ | `cancel_by_session()` | 取消子代理（见下文） |
| ⑤ | 汇总返回 | 向用户报告取消了多少个任务 |

## 3. 常规任务追踪：`_active_tasks`

### 数据结构（[loop.py:109](nanobot/agent/loop.py#L109)）

```python
self._active_tasks: dict[str, list[asyncio.Task]] = {}
# session_key → [asyncio.Task, ...]
```

### 任务注册（[loop.py:311-313](nanobot/agent/loop.py#L311-L313)）

当普通消息（非 priority 命令）到达时：

```python
task = asyncio.create_task(self._dispatch(msg))
self._active_tasks.setdefault(msg.session_key, []).append(task)
task.add_done_callback(
    lambda t, k=msg.session_key:
        self._active_tasks.get(k, [])
        and self._active_tasks[k].remove(t)
        if t in self._active_tasks.get(k, [])
        else None
)
```

- 每条消息创建一个 `asyncio.Task` 来执行 `_dispatch()`
- 任务追加到 `_active_tasks[session_key]` 列表
- **done callback** 自动从列表中移除已完成的任务，防止内存泄漏

### 会话键（session_key）推导

```
f"{channel}:{chat_id}"
```

示例：
- `cli:direct` — CLI 直连
- `telegram:12345` — Telegram 私聊
- `telegram:-100123:topic:42` — Telegram 群组话题

`/stop` 以 session_key 为粒度，只取消当前会话的任务，不影响其他会话。

## 4. 子代理追踪：`SubagentManager`

### 数据结构（[subagent.py:49-50](nanobot/agent/subagent.py#L49-L50)）

```python
self._running_tasks: dict[str, asyncio.Task[None]] = {}    # task_id → Task
self._session_tasks: dict[str, set[str]] = {}              # session_key → {task_id, ...}
```

两级映射：
1. `_running_tasks`：task_id → 实际的 asyncio.Task 对象
2. `_session_tasks`：session_key → 该会话下所有子代理的 task_id 集合

### 子代理注册（[subagent.py:52-79](nanobot/agent/subagent.py#L52-L79)）

```python
async def spawn(self, task, label, origin_channel, origin_chat_id, session_key) -> str:
    task_id = str(uuid.uuid4())[:8]
    bg_task = asyncio.create_task(self._run_subagent(task_id, task, display_label, origin))

    self._running_tasks[task_id] = bg_task
    if session_key:
        self._session_tasks.setdefault(session_key, set()).add(task_id)

    def _cleanup(_: asyncio.Task) -> None:
        self._running_tasks.pop(task_id, None)
        if session_key and (ids := self._session_tasks.get(session_key)):
            ids.discard(task_id)
            if not ids:
                del self._session_tasks[session_key]

    bg_task.add_done_callback(_cleanup)
```

- spawn 工具被 LLM 调用时，会创建子代理任务并注册到两个字典中
- `_cleanup` 回调在任务完成时自动清理两个字典中的记录

### 子代理取消（[subagent.py:248-256](nanobot/agent/subagent.py#L248-L256)）

```python
async def cancel_by_session(self, session_key: str) -> int:
    tasks = [self._running_tasks[tid] for tid in self._session_tasks.get(session_key, [])
             if tid in self._running_tasks and not self._running_tasks[tid].done()]
    for t in tasks:
        t.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    return len(tasks)
```

流程：
1. 从 `_session_tasks` 查找该会话的所有 task_id
2. 过滤掉已完成（`.done()`）的任务
3. 对每个活跃任务调用 `.cancel()`
4. `asyncio.gather(*tasks, return_exceptions=True)` 等待所有任务完成清理
5. 返回取消数量

## 5. `CancelledError` 的传播路径

### 常规任务中的传播

```
task.cancel()
  → CancelledError 注入到 _dispatch() 的 await 点
    → loop.py:363-365 捕获并 re-raise
      → CancelledError 传播到 _run_agent_loop()
        → runner.py:213-214 捕获并 re-raise
          → CancelledError 传播到工具执行的 await 点
            → 工具被中断
```

关键代码（[loop.py:363-365](nanobot/agent/loop.py#L363-L365)）：

```python
except asyncio.CancelledError:
    logger.info("Task cancelled for session {}", msg.session_key)
    raise  # re-raise 保证取消信号继续传播
```

### 子代理中的传播

```
subagent task.cancel()
  → CancelledError 注入到 _run_subagent() 的 await 点
    → 工具执行被中断
      → _cleanup 回调执行，清理 _running_tasks 和 _session_tasks
```

## 6. `/stop` 对会话文件的影响分析

### 结论：不会导致会话消息文件格式异常

### CancelledError 注入点与保存逻辑的关系

`_process_message` 中的代码是**严格顺序执行**的（[loop.py:466-479](nanobot/agent/loop.py#L466-L479)）：

```python
# ① 先跑 LLM 循环 —— CancelledError 在这里的 await 点注入
final_content, _, all_msgs = await self._run_agent_loop(...)

# ② 保存到内存 session 对象 —— 被 CancelledError 跳过
self._save_turn(session, all_msgs, ...)

# ③ 写入磁盘 JSONL 文件 —— 被 CancelledError 跳过
self.sessions.save(session)
```

`asyncio.CancelledError` 只会在 `await` 挂起点注入，因此它**一定打断在 `_run_agent_loop()` 内部**。后面的 `_save_turn()` + `sessions.save()` 不会执行。

### 三层安全保障

| 层级 | 机制 | 说明 |
|------|------|------|
| 1 | 保存逻辑在 `_run_agent_loop` **之后** | CancelledError 只在 await 点注入，LLM 循环之后的保存步骤根本不会被调到 |
| 2 | `_dispatch` 无 `finally` 部分保存 | CancelledError 处理只做 `logger.info` + `raise`（[loop.py:363-365](nanobot/agent/loop.py#L363-L365)），没有 `finally` 块做部分落盘 |
| 3 | `sessions.save()` 是全量覆写 | 即使被调到，也是将完整 `session.messages` 一次性写入 JSONL（[manager.py:218-233](nanobot/session/manager.py#L218-L233)），不存在"写了一半"的情况 |

### 实际效果

`/stop` 后的会话文件状态 = **上一轮成功保存的状态**。当前这轮的用户消息 + LLM 的部分响应都**不会被持久化**，等价于这轮对话从未发生过。

### 唯一的体验问题

用户发了一条消息、LLM 正在处理中被 `/stop`，这条消息不会出现在后续的会话历史中。下次对话时 LLM 不知道用户之前问过什么。这是合理的语义——用户主动要求停止，当前轮次视为无效。

### 会话持久化流程（正常完成时）

```
_run_agent_loop() 完成
  → _save_turn(): 遍历 all_msgs，逐条 append 到 session.messages（内存）
  → sessions.save(): 打开 JSONL 文件，先写 metadata 行，再逐行写 messages
  → 整个过程是"先攒内存，后一次性写文件"
```

[manager.py:218-233](nanobot/session/manager.py#L218-L233)：

```python
def save(self, session: Session) -> None:
    path = self._get_session_path(session.key)
    with open(path, "w", encoding="utf-8") as f:   # "w" 模式全量覆写
        metadata_line = { "_type": "metadata", ... }
        f.write(json.dumps(metadata_line, ensure_ascii=False) + "\n")
        for msg in session.messages:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
```

注意 `open(path, "w")` 是覆盖写入，如果进程在写入中途被 kill（OS 级别），理论上可能产生截断文件。但这是进程崩溃场景，与 `/stop` 无关——`/stop` 时保存逻辑根本不会启动。

## 7. 与其他停止机制的区别

| 机制 | 作用范围 | 触发方式 | 说明 |
|------|----------|----------|------|
| `/stop` | 单个会话 | 用户手动 | 取消该会话的 `_active_tasks` + 子代理 |
| `AgentLoop.stop()` | 整个进程 | 外部调用 | 设置 `_running = False`，主循环退出 |
| `_background_tasks` | 不受 `/stop` 影响 | 进程关闭时 drain | 内存整理、归档等后台任务 |

`/stop` **不会取消** `_background_tasks` 中的任务（如记忆整理、消息归档），这些只在进程关闭时通过 `close_mcp()` 清理。

## 8. 边界情况

### 无活跃任务

```python
tasks = loop._active_tasks.pop(msg.session_key, [])  # 空列表
cancelled = 0
sub_cancelled = 0
total = 0
content = "No active task to stop."
```

### 任务已完成但未从列表移除

done callback 是异步清理的，可能存在已完成但仍在列表中的任务：

```python
cancelled = sum(1 for t in tasks if not t.done() and t.cancel())
```

`not t.done()` 过滤确保只尝试取消仍在运行的任务。对已完成任务调用 `cancel()` 返回 `False`，不计入统计。

### 多任务并发

同一个会话可能同时有多个活跃任务（虽然 `_dispatch` 有 per-session lock 串行化，但 lock 之前的 task 创建是并发的）。`/stop` 通过 `pop()` 原子性取出所有任务一次性取消。

## 9. 时序图

```
用户                    AgentLoop              _active_tasks        SubagentManager
 |                         |                       |                      |
 |-- "/stop" ------------->|                       |                      |
 |                         |-- pop(session_key) -->|                      |
 |                         |<-- [task1, task2] ----|                      |
 |                         |                       |                      |
 |                         |-- task1.cancel() ---->| (CancelledError)     |
 |                         |-- task2.cancel() ---->| (CancelledError)     |
 |                         |-- await task1 --------| (cleanup)            |
 |                         |-- await task2 --------| (cleanup)            |
 |                         |                       |                      |
 |                         |-- cancel_by_session() ---------------------->|
 |                         |                       |    cancel subagent1  |
 |                         |                       |    cancel subagent2  |
 |                         |                       |    gather (wait)     |
 |                         |<-- count ------------ ----------------------|
 |                         |                       |                      |
 |<-- "Stopped 4 task(s)." |                       |                      |
```

## 10. 测试覆盖

相关测试文件：[tests/agent/test_task_cancel.py](tests/agent/test_task_cancel.py)

覆盖场景：
- 无活跃任务时返回 "No active task to stop."
- 单个任务取消
- 多个任务取消
- 子代理按会话取消
- 子代理工具执行中途取消（不发送结果通知）

## 11. 关键文件索引

| 文件 | 关键行 | 内容 |
|------|--------|------|
| [builtin.py](nanobot/command/builtin.py) | 15-29 | `cmd_stop` 实现 |
| [builtin.py](nanobot/command/builtin.py) | 103-110 | 命令注册 |
| [router.py](nanobot/command/router.py) | 57-65 | 优先级路由与分发 |
| [loop.py](nanobot/agent/loop.py) | 109 | `_active_tasks` 定义 |
| [loop.py](nanobot/agent/loop.py) | 283-313 | 主循环与任务注册 |
| [loop.py](nanobot/agent/loop.py) | 363-365 | CancelledError 处理 |
| [subagent.py](nanobot/agent/subagent.py) | 49-50 | 子代理数据结构 |
| [subagent.py](nanobot/agent/subagent.py) | 52-79 | 子代理 spawn 与注册 |
| [subagent.py](nanobot/agent/subagent.py) | 248-256 | `cancel_by_session` |
| [runner.py](nanobot/agent/runner.py) | 213-214 | 工具层 CancelledError |
| [events.py](nanobot/bus/events.py) | 22-24 | session_key 推导 |
| [manager.py](nanobot/session/manager.py) | 218-233 | `sessions.save()` 全量覆写 JSONL |
