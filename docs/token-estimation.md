# Token 估算与上下文归档机制

## 概述

`MemoryConsolidator` 通过估算当前 prompt 的 token 数量，判断是否需要归档旧消息，以确保 LLM 请求不会超出上下文窗口。

## 核心流程

```
session 历史消息
      │
      ▼
estimate_session_prompt_tokens()   ← 构建模拟 prompt
      │
      ▼
estimate_prompt_tokens_chain()     ← 两级估算策略
      │
      ├─ 优先: provider 自带估算器
      │
      └─ 回退: tiktoken 本地估算
      │
      ▼
maybe_consolidate_by_tokens()      ← 判断是否触发归档
```

## 详细逻辑

### 1. 构建模拟 prompt

**入口**: `MemoryConsolidator.estimate_session_prompt_tokens()`
**文件**: `nanobot/agent/memory.py`

从 session 取出完整历史消息，调用 `_build_messages()` 构造与实际发给 LLM 相同格式的 messages 列表（包含系统提示词、上下文等），仅将当前用户消息替换为 `"[token-probe]"` 占位符。

```python
probe_messages = self._build_messages(
    history=history,
    current_message="[token-probe]",
    channel=channel,
    chat_id=chat_id,
)
```

### 2. 两级 token 估算

**入口**: `estimate_prompt_tokens_chain()`
**文件**: `nanobot/utils/helpers.py`

按优先级尝试两种估算方式：

| 优先级 | 方式 | 来源标识 | 说明 |
|--------|------|----------|------|
| 1 | provider 自带估算器 | `provider_counter` | 调用 `provider.estimate_prompt_tokens(messages, tools, model)`，精度最高 |
| 2 | tiktoken 本地估算 | `tiktoken` | 使用 `cl100k_base` 编码，纯本地计算 |

如果 provider 估算器不可用或抛异常，自动回退到 tiktoken。两者都失败则返回 `0`。

### 3. tiktoken 估算细节

**入口**: `estimate_prompt_tokens()`
**文件**: `nanobot/utils/helpers.py`

遍历所有 messages，收集以下文本字段统一编码：

- **`content`** — 字符串直接收取；list 类型则提取 `type == "text"` 的部分
- **`tool_calls`** — JSON 序列化后收取
- **`reasoning_content`** — 思维链内容
- **`name`、`tool_call_id`** — 工具调用元信息
- **`tools`** — 工具定义列表，JSON 序列化

额外开销：

```python
per_message_overhead = len(messages) * 4  # 每条消息 4 token framing 开销
total = len(enc.encode("\n".join(all_parts))) + per_message_overhead
```

### 4. 归档预算与触发条件

**入口**: `MemoryConsolidator.maybe_consolidate_by_tokens()`
**文件**: `nanobot/agent/memory.py`

```
budget = context_window_tokens - max_completion_tokens - 1024(safety buffer)
target = budget // 2
```

| 条件 | 动作 |
|------|------|
| 估算 token < budget | 无需归档，仅记录 debug 日志 |
| 估算 token >= budget | 按 user-turn 边界归档旧消息，直到 prompt 降到 target 以下 |

归档时通过 `pick_consolidation_boundary()` 选择归档边界：从上次归档位置开始，找到第一个累积 token 数超过 `tokens_to_remove` 的 user-turn 边界，保证按完整对话轮次归档。

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `context_window_tokens` | 由模型决定 | 上下文窗口大小 |
| `max_completion_tokens` | 4096 | 预留给模型输出的 token 数 |
| `_SAFETY_BUFFER` | 1024 | 估算误差的安全余量 |
| `_MAX_CONSOLIDATION_ROUNDS` | 5 | 单次归档最大轮数 |

## 涉及文件

| 文件 | 职责 |
|------|------|
| `nanobot/agent/memory.py` | `MemoryConsolidator` 类，归档策略与预算计算 |
| `nanobot/utils/helpers.py` | `estimate_prompt_tokens_chain()`、`estimate_prompt_tokens()` 估算函数 |
| `nanobot/command/builtin.py` | 调用 `estimate_session_prompt_tokens()` 用于 status 命令展示 |
