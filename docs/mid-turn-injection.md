# Mid-turn 消息注入 — 技术细则

## 概述

Mid-turn 消息注入是 nanobot v0.1.5.post1 引入的核心特性。它允许用户在 agent 正在处理上一个请求的工作期间发送后续消息，这些消息不再排队等待下一轮次，而是直接注入当前轮次的对话上下文中，agent 在当前响应流中继续处理。

**解决的问题**：传统模式下，agent 处理一条消息时会锁定整个会话，用户必须等待 agent 完成后才能发送补充说明或修正指令。对于执行耗时工具调用（如搜索、代码执行、文件读写）的场景，这种等待体验较差。

---

## 架构总览

```
┌──────────┐     publish_inbound     ┌──────────────┐
│  Channel  │ ──────────────────────► │  MessageBus  │
│ (Telegram │                        │  (asyncio.Queue)│
│  Discord  │                        └──────┬───────┘
│  WebUI…)  │                               │ consume_inbound
└──────────┘                               ▼
                                    ┌──────────────┐
                                    │  AgentLoop   │
                                    │   .run()     │
                                    └──────┬───────┘
                                           │
                          ┌────────────────┼────────────────┐
                          │ 检查 _pending_queues           │
                          │                                │
                   session 有活跃任务？              session 无活跃任务
                          │                                │
                   ┌──────▼──────┐                  ┌──────▼──────┐
                   │ pending_queue│                  │  新建 task   │
                   │ .put_nowait()│                  │ _dispatch() │
                   └──────┬──────┘                  └─────────────┘
                          │
                   runner 消费 via
                   injection_callback
                          │
                   ┌──────▼──────┐
                   │ AgentRunner │
                   │   .run()    │
                   └─────────────┘
```

---

## 核心数据结构

### 1. Per-session Pending Queue

[loop.py:272-275](nanobot/agent/loop.py#L272-L275)

```python
self._pending_queues: dict[str, asyncio.Queue] = {}
```

- 以 `session_key`（格式 `channel:chat_id`）为键
- 每个 session 最多一个 pending queue
- Queue 的 `maxsize=20`，防止内存溢出

### 2. 注入限制常量

[runner.py:41-42](nanobot/agent/runner.py#L41-L42)

| 常量 | 值 | 含义 |
|------|------|------|
| `_MAX_INJECTIONS_PER_TURN` | 3 | 单次 drain 最多取 3 条消息 |
| `_MAX_INJECTION_CYCLES` | 5 | 单个 agent run 最多经历 5 次注入周期 |

### 3. AgentRunSpec.injection_callback

[runner.py:79](nanobot/agent/runner.py#L79)

```python
injection_callback: Any | None = None
```

Runner 不直接访问 pending queue，而是通过回调函数间接获取注入消息。该回调由 `AgentLoop._run_agent_loop()` 创建并传入 `_drain_pending()`。

### 4. AgentRunResult.had_injections

[runner.py:94](nanobot/agent/runner.py#L94)

```python
had_injections: bool = False
```

标记本次 agent run 是否发生了消息注入，供上层逻辑（如 checkpoint 恢复、日志记录）使用。

---

## 消息流转详解

### Phase 1: 消息入队路由

[loop.py:683-714](nanobot/agent/loop.py#L683-L714)

当 `AgentLoop.run()` 从 `MessageBus` 消费到新消息时：

```python
effective_key = self._effective_session_key(msg)
if effective_key in self._pending_queues:
    # 该 session 有活跃任务 → 路由到 pending queue
    self._pending_queues[effective_key].put_nowait(pending_msg)
else:
    # 该 session 空闲 → 创建新 task
    task = asyncio.create_task(self._dispatch(msg))
```

**关键决策逻辑**：

1. **优先级命令跳过注入**：`is_priority()` 返回 True 的命令（如 `/stop`）直接内联执行，不进入 pending queue
2. **普通命令跳过注入**：`is_dispatchable_command()` 检测到非优先级命令时也直接分发，避免命令被延迟
3. **Session key 对齐**：当 `effective_key != msg.session_key` 时（如 unified session 模式），通过 `dataclasses.replace()` 创建带 `session_key_override` 的新消息
4. **Queue 溢出处理**：`put_nowait()` 抛出 `QueueFull` 时，消息走 fallback 路径（但不重新入队到 bus，仅记录警告）

### Phase 2: Pending Queue 注册与生命周期

[loop.py:734-737](nanobot/agent/loop.py#L734-L737)

```python
pending = asyncio.Queue(maxsize=20)
self._pending_queues[session_key] = pending
```

在 `_dispatch()` 方法开头注册 pending queue，使用 `try/finally` 确保清理：

[loop.py:817-835](nanobot/agent/loop.py#L817-L835)

```python
finally:
    queue = self._pending_queues.pop(session_key, None)
    if queue is not None:
        while True:
            try:
                item = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            await self.bus.publish_inbound(item)  # 重新发布到 bus
```

**清理策略**：`_dispatch()` 的 `finally` 块会将残留消息重新发布到 `MessageBus.inbound`，使其作为新消息被后续消费循环处理。这确保了不会丢失任何消息。

### Phase 3: 消息 Drain（从 Queue 到 Runner）

[loop.py:560-618](nanobot/agent/loop.py#L560-L618)

`_drain_pending()` 是注入回调的核心实现：

```python
async def _drain_pending(*, limit=_MAX_INJECTIONS_PER_TURN) -> list[dict]:
    # 1. 非阻塞地取消息
    while len(items) < limit:
        items.append(pending_queue.get_nowait())  # QueueEmpty → break

    # 2. 特殊场景：无消息但有活跃 sub-agent → 阻塞等待
    if not items and subagents.get_running_count() > 0:
        msg = await asyncio.wait_for(pending_queue.get(), timeout=300)
        items.append(msg)
        # 非阻塞地继续取
        while len(items) < limit:
            items.append(pending_queue.get_nowait())

    return items
```

**Sub-agent 感知等待**（[loop.py:600-616](nanobot/agent/loop.py#L600-L616)）：当 pending queue 为空但当前 session 有活跃 sub-agent 时，`_drain_pending` 会阻塞最多 300 秒等待新消息。这确保 sub-agent 的完成事件可以通过 pending queue 路径有序注入，而非被独立分发。

**消息转换**：`InboundMessage` → LLM `user` 消息格式

```python
def _to_user_message(pending_msg):
    content = pending_msg.content
    media = pending_msg.media
    user_content = self.context._build_user_content(content, media)
    runtime_ctx = self.context._build_runtime_context(...)
    return {"role": "user", "content": f"{runtime_ctx}\n\n{user_content}"}
```

### Phase 4: 注入点（Injection Checkpoints）

Runner 在 6 个关键点检查是否有待注入消息：

| 检查点 | 位置 | 触发时机 |
|--------|------|---------|
| Checkpoint 1 | [runner.py:377](nanobot/agent/runner.py#L377) | 工具执行完成后、下一次 LLM 调用前 |
| Checkpoint 2 | [runner.py:457](nanobot/agent/runner.py#L457) | 最终响应生成后、stream_end 前 |
| Checkpoint 3 | [runner.py:355](nanobot/agent/runner.py#L355) | 工具执行发生致命错误后 |
| Checkpoint 4 | [runner.py:481](nanobot/agent/runner.py#L481) | LLM 调用返回错误后 |
| Checkpoint 5 | [runner.py:498](nanobot/agent/runner.py#L498) | LLM 返回空响应后 |
| Checkpoint 6 | [runner.py:546](nanobot/agent/runner.py#L546) | 达到最大迭代次数后 |

**Checkpoint 2 的特殊性**：在最终响应生成后检查注入时，如果发现注入消息，会通过 `resuming=True` 参数调用 `on_stream_end`，使流式 channel 保持流状态，不会过早地终结渲染卡片。

---

## 注入执行机制

### _try_drain_injections

[runner.py:142-184](nanobot/agent/runner.py#L142-L184)

```python
async def _try_drain_injections(self, spec, messages, assistant_message,
                                 injection_cycles, *, phase):
    if injection_cycles >= _MAX_INJECTION_CYCLES:  # 5 次上限
        return False, injection_cycles

    injections = await self._drain_injections(spec)
    if not injections:
        return False, injection_cycles

    injection_cycles += 1

    # 如果有 assistant_message，先追加到 messages
    if assistant_message is not None:
        messages.append(assistant_message)
        await self._emit_checkpoint(spec, {...})

    # 追加注入的 user 消息
    self._append_injected_messages(messages, injections)

    return True, injection_cycles  # caller 应 continue 循环
```

### _drain_injections

[runner.py:186-229](nanobot/agent/runner.py#L186-L229)

```python
async def _drain_injections(self, spec) -> list[dict]:
    if spec.injection_callback is None:
        return []

    # 自省：回调是否接受 limit 参数
    if accepts_limit:
        items = await spec.injection_callback(limit=_MAX_INJECTIONS_PER_TURN)
    else:
        items = await spec.injection_callback()

    # 过滤 + 截断
    for item in items:
        if isinstance(item, dict) and item.get("role") == "user":
            injected_messages.append(item)

    # 超限截断 + 日志警告
    if len(injected_messages) > _MAX_INJECTIONS_PER_TURN:
        injected_messages = injected_messages[:_MAX_INJECTIONS_PER_TURN]

    return injected_messages
```

**自省机制**：通过 `inspect.signature()` 检查回调是否接受 `limit` 参数，兼容不同版本的回调签名。

---

## 角色交替维护（Role Alternation）

[runner.py:120-140](nanobot/agent/runner.py#L120-L140)

LLM API 要求消息序列中 `user`/`assistant` 角色严格交替。注入消息时可能破坏这个约束（例如连续两条 user 消息）。`_append_injected_messages` 通过合并相邻的同角色消息来维持交替：

```python
@classmethod
def _append_injected_messages(cls, messages, injections):
    for injection in injections:
        # 如果最后一条也是 user，合并内容而非追加
        if messages and injection["role"] == "user" and messages[-1]["role"] == "user":
            merged = dict(messages[-1])
            merged["content"] = cls._merge_message_content(
                merged.get("content"), injection.get("content")
            )
            messages[-1] = merged
        else:
            messages.append(injection)
```

`_merge_message_content` 的合并规则：

- `str` + `str` → `"left\n\nright"`
- `list[dict]` + any → 拼接为统一 block 列表
- `None` → 空列表

---

## 流式通道协同

### Stream Segment 机制

[loop.py:744-750](nanobot/agent/loop.py#L744-L750)

```python
stream_base_id = f"{msg.session_key}:{time.time_ns()}"
stream_segment = 0

def _current_stream_id():
    return f"{stream_base_id}:{stream_segment}"
```

每次发生注入并继续循环时，stream_segment 递增，产生新的 `_stream_id`。Channel Manager 在分发端据此合并或分割流式消息。

### resuming 语义

[runner.py:454-466](nanobot/agent/runner.py#L454-L466)

```python
# Check for mid-turn injections BEFORE signaling stream end.
should_continue, injection_cycles = await self._try_drain_injections(...)

if hook.wants_streaming():
    await hook.on_stream_end(context, resuming=should_continue)
```

- `resuming=True`：通知 channel 本次流式结束但后面还有内容（工具调用或注入消息后继续生成），channel 不应终结 UI 元素
- `resuming=False`：最终结束，channel 可以完成消息渲染

---

## 并发与安全

### Per-session Lock

[loop.py:731](nanobot/agent/loop.py#L731)

```python
lock = self._session_locks.setdefault(session_key, asyncio.Lock())
async with lock, gate:
    ...
```

- 每个 session 一把 `asyncio.Lock`，保证同一 session 内串行处理
- `_concurrency_gate`（`asyncio.Semaphore`）控制跨 session 的总并发数（默认 3）

### 消息零丢失保证

1. **Queue 溢出**：`put_nowait()` 抛出 `QueueFull` → 记录日志（当前实现未重入 bus，但有日志可追溯）
2. **Dispatch 异常**：`finally` 块将残留消息重新发布到 bus
3. **Runner 超限**：超出 `_MAX_INJECTIONS_PER_TURN` 的消息被截断但记录 warning

### 限制值的设计考量

| 限制 | 值 | 理由 |
|------|------|------|
| Queue maxsize | 20 | 正常对话不可能在 agent 处理期间发送 20 条消息，超出即异常 |
| Injections per drain | 3 | 避免单次注入过多消息导致上下文膨胀和响应延迟 |
| Injection cycles | 5 | 防止注入-响应-注入的无限循环 |

---

## 时序图

```
User           Channel         MessageBus     AgentLoop              AgentRunner
 │                │                │              │                      │
 │──"分析数据"──►│                │              │                      │
 │                │──inbound─────►│              │                      │
 │                │               │──consume────►│                      │
 │                │               │              │──_dispatch()────────►│
 │                │               │              │  注册 pending_queue   │
 │                │               │              │  ┌─────────────────┐ │
 │                │               │              │  │ runner.run()    │ │
 │                │               │              │  │ LLM → 工具调用   │ │
 │                │               │              │  │                  │ │
 │"再加个图表"───►│               │              │  │                  │ │
 │                │──inbound─────►│              │  │                  │ │
 │                │               │──consume────►│  │                  │ │
 │                │               │              │──put_nowait()──────►│ pending_queue
 │                │               │              │  │                  │ │
 │                │               │              │  │ Checkpoint 1:    │ │
 │                │               │              │  │ drain_injections │ │
 │                │               │              │  │──┐               │ │
 │                │               │              │  │  │ 取出"再加个   │ │
 │                │               │              │  │  │ 图表"         │ │
 │                │               │              │  │◄─┘               │ │
 │                │               │              │  │ append to msgs   │ │
 │                │               │              │  │ continue loop    │ │
 │                │               │              │  │                  │ │
 │                │               │              │  │ LLM → 最终响应   │ │
 │                │               │              │  │ (含图表建议)     │ │
 │                │               │              │  └─────────────────┘ │
 │                │               │              │                      │
 │                │◄──outbound──────────────────────stream_end(resuming=False)
 │◄───────────────│               │              │                      │
```

---

## Sub-agent 注入路径

[loop.py:600-616](nanobot/agent/loop.py#L600-L616)

当 pending queue 为空但有活跃 sub-agent 时，`_drain_pending` 会阻塞等待。Sub-agent 的结果通过 `session_key_override` 对齐到主 agent 的 session key，确保结果能通过 pending queue 路径注入而非被独立分发：

```
Sub-agent 完成 → bus.publish_inbound(result_with_override)
                    → AgentLoop 路由到 pending_queue
                    → _drain_pending() 阻塞解除
                    → 注入到 runner messages
```

---

## 与其他特性的交互

| 特性 | 交互方式 |
|------|---------|
| **Auto Compact** | 注入消息可能触发上下文膨胀，auto compact 在空闲时段压缩历史以腾出空间 |
| **Streaming** | 注入时 `resuming=True` 保持流状态，channel 不会提前终结 UI |
| **Ask User** | `AskUserInterrupt` 会打断循环等待用户输入，该消息不经过 pending queue |
| **Dream Skill** | 后台学习流程在独立 session 中运行，不受 mid-turn 注入影响 |
| **Thread Isolation** | 飞书/Discord 等线程隔离 session 各自独立 pending queue |

---

## 涉及的关键文件

| 文件 | 职责 |
|------|------|
| [loop.py](nanobot/agent/loop.py) | 消息路由、pending queue 管理、drain 回调、流式协调 |
| [runner.py](nanobot/agent/runner.py) | 注入检查点、注入限制、角色交替维护、run 循环 |
| [queue.py](nanobot/bus/queue.py) | MessageBus 基础设施（inbound/outbound async queue） |
| [manager.py](nanobot/channels/manager.py) | Channel Manager 分发 outbound 流式消息 |
| [subagent.py](nanobot/agent/subagent.py) | Sub-agent 结果通过 session_key_override 路由到 pending queue |
| [test_runner.py](tests/agent/test_runner.py) | 20+ 测试用例覆盖注入的各种场景 |
