# Nanobot 上下文裁切机制

当对话历史不断累积、Prompt Token 即将超出模型上下文窗口时，Nanobot 会通过 **内存整合（Memory Consolidation）** 将旧的对话消息归档到持久化文件，从而为新对话腾出空间。

整个流程涉及以下核心模块：

| 模块 | 职责 |
|---|---|
| `nanobot/agent/memory.py` — `MemoryConsolidator` | 裁切策略、Token 预算计算、整合循环 |
| `nanobot/agent/memory.py` — `MemoryStore` | LLM 摘要生成、MEMORY.md / HISTORY.md 读写 |
| `nanobot/session/manager.py` — `Session` | 消息存储与历史视图（`get_history`） |
| `nanobot/agent/loop.py` — `AgentLoop` | 触发整合的时机、工具结果截断 |
| `nanobot/utils/helpers.py` | Token 估算工具函数 |

---

## 1. Token 估算

在决定是否裁切之前，需要先知道当前 Prompt 消耗了多少 Token。

### 1.1 单条消息估算 — `estimate_message_tokens()`

位于 `nanobot/utils/helpers.py:179`。

遍历消息中的所有字段（`content`、`tool_calls`、`reasoning_content`、`name`、`tool_call_id`），拼接后用 tiktoken（`cl100k_base` 编码）计算 Token 数。每条消息额外加 4 Token 的框架开销。最低返回 4 Token。

### 1.2 完整 Prompt 估算 — `estimate_prompt_tokens_chain()`

位于 `nanobot/utils/helpers.py:217`。

采用两级估算策略：

1. **优先使用 Provider 原生计数器** — 如果 Provider 实现了 `estimate_prompt_tokens()` 方法，优先调用，精度更高。
2. **回退到 tiktoken** — 如果 Provider 未实现或调用失败，使用 `estimate_prompt_tokens()` 走 tiktoken。

返回 `(token_count, source)` 元组，`source` 标识估算来源（`"provider_counter"` 或 `"tiktoken"`）。

### 1.3 Session 级别估算 — `estimate_session_prompt_tokens()`

位于 `nanobot/agent/memory.py:280`。

构建一个 **探测消息列表**（用 `"[token-probe]"` 作为占位用户消息），调用 `estimate_prompt_tokens_chain()` 得到完整 Prompt 的 Token 估算值。这模拟了实际发送给 LLM 的消息结构。

---

## 2. Token 预算与裁切阈值

位于 `nanobot/agent/memory.py:306` — `maybe_consolidate_by_tokens()`。

### 2.1 预算计算

```
budget = context_window_tokens - max_completion_tokens - SAFETY_BUFFER
target = budget // 2
```

| 参数 | 默认值 | 含义 |
|---|---|---|
| `context_window_tokens` | 65,536 | 配置于 `nanobot/config/schema.py:40` |
| `max_completion_tokens` | 4,096 | 由 Provider 的 `generation.max_tokens` 决定 |
| `SAFETY_BUFFER` | 1,024 | 应对 Tokenizer 估算偏差的额外缓冲（`memory.py:227`） |

以默认配置为例：

- **budget** = 65,536 − 4,096 − 1,024 = **60,416**
- **target** = 60,416 / 2 = **30,208**

### 2.2 裁切触发条件

```
if estimated < budget:
    return  # 无需裁切
```

- **estimated < budget**：当前 Token 未超出预算，跳过裁切。
- **estimated >= budget**：触发整合循环，持续裁切直到 Token 降到 target（预算的一半）。

目标是 50% 而非 100%，目的是为后续对话预留充足空间，降低裁切频率。

---

## 3. 整合循环流程

```
┌─────────────────────────────────────┐
│ maybe_consolidate_by_tokens(session) │
└──────────────┬──────────────────────┘
               │
               ▼
        估算当前 Token 数
               │
        estimated < budget?
        ├── Yes → 返回（无需裁切）
        └── No  ↓
               │
       ┌───────┴───────┐
       │ 整合循环开始    │  最多 _MAX_CONSOLIDATION_ROUNDS=5 轮
       └───────┬───────┘
               │
        estimated <= target?
        ├── Yes → 返回（已满足目标）
        └── No  ↓
               │
     pick_consolidation_boundary()
     选择裁切边界（用户轮次边界）
               │
        boundary 存在?
        ├── No → 返回（无法找到安全边界）
        └── Yes ↓
               │
     提取 messages[last_consolidated:boundary]
     调用 LLM 进行摘要整合
               │
        整合成功?
        ├── No → 返回
        └── Yes ↓
               │
     更新 session.last_consolidated
     重新估算 Token → 继续循环
```

---

## 4. 裁切边界选择 — `pick_consolidation_boundary()`

位于 `nanobot/agent/memory.py:258`。

选择一段消息进行归档时，必须遵守两个约束：

### 4.1 用户轮次边界

只在 **用户消息（`role=user`）** 处设置裁切边界。这确保裁切后剩余的历史不会从工具调用结果或 assistant 回复中间开始。

### 4.2 从已整合位置开始

从 `session.last_consolidated` 索引开始向后扫描，只处理尚未整合的消息。

### 4.3 Token 量达标

累积扫描消息的 Token 数，直到达到 `tokens_to_remove`（即 `estimated - target`）才返回边界。如果遍历完所有消息仍未达标，返回最后一个用户轮次边界。

---

## 5. LLM 摘要整合 — `MemoryStore.consolidate()`

位于 `nanobot/agent/memory.py:114`。

裁切下来的消息不会直接丢弃，而是通过 LLM 生成摘要后持久化：

### 5.1 整合 Prompt

将当前长期记忆（MEMORY.md 内容）和待整合消息拼接成 Prompt，要求 LLM 调用 `save_memory` 工具。

### 5.2 `save_memory` 工具

定义于 `memory.py:21`，包含两个必填参数：

- **`history_entry`**：一段摘要文本，写入 `HISTORY.md`。格式为 `[YYYY-MM-DD HH:MM] 摘要内容`，便于 grep 搜索。
- **`memory_update`**：更新后的完整长期记忆，写入 `MEMORY.md`。包含所有已有事实 + 新增信息。

### 5.3 工具调用策略

```python
# 优先强制调用 save_memory
tool_choice = {"type": "function", "function": {"name": "save_memory"}}
```

如果 Provider 不支持 `forced tool_choice`（检测错误关键词），自动回退为 `tool_choice="auto"`。

### 5.4 参数校验与容错

对 LLM 返回的工具参数进行多重校验：参数格式、必填字段、非空检查。任何校验失败都会进入失败处理流程。

---

## 6. 降级与容错机制

### 6.1 连续失败计数

`MemoryStore` 维护 `_consecutive_failures` 计数器（`memory.py:84`）。

### 6.2 原始归档降级 — `_fail_or_raw_archive()`

位于 `memory.py:201`。

- 失败次数 **< 3**：返回 `False`（本次整合失败，但下次仍可尝试 LLM 摘要）。
- 失败次数 **>= 3**：触发 `_raw_archive()`，直接将原始消息文本追加到 `HISTORY.md`，格式为：

  ```
  [2026-05-21 14:30] [RAW] 12 messages
  [2026-05-21 14:28] USER: ...
  [2026-05-21 14:29] ASSISTANT: ...
  ...
  ```

降级后重置失败计数器，返回 `True`（标记整合成功，消息可被跳过）。

### 6.3 `archive_messages()` 重试

位于 `memory.py:297`。

对同一批消息最多重试 `_MAX_FAILURES_BEFORE_RAW_ARCHIVE`（3）次。无论最终是 LLM 摘要还是原始归档，都能保证消息不会丢失。

---

## 7. Session 历史视图 — `get_history()`

位于 `nanobot/session/manager.py:69`。

### 7.1 核心机制

```python
unconsolidated = self.messages[self.last_consolidated:]
```

**消息列表本身是只追加的（append-only）**，不会删除或修改。`last_consolidated` 是一个偏移量，标记已归档的消息数量。`get_history()` 只返回偏移量之后的未整合消息。

这种设计有两个好处：
1. **LLM 缓存友好**：消息索引不变，Provider 的 Prompt Cache 可以持续命中。
2. **数据安全**：原始消息始终保留在 JSONL 文件中。

### 7.2 工具调用合法性保证

`_find_legal_start()`（`manager.py:47`）确保返回的历史不会以孤立的工具调用结果开头。如果裁切导致某个 `tool` 消息的对应 `assistant` 消息被排除在外，会自动跳过这些不合法的开头消息。

### 7.3 用户轮次对齐

```python
for i, message in enumerate(sliced):
    if message.get("role") == "user":
        sliced = sliced[i:]
        break
```

丢弃开头的非用户消息，确保历史总是从一个用户消息开始。

---

## 8. 工具结果截断

除了消息级别的裁切，单条工具结果也有长度限制。

### 8.1 持久化截断 — `_save_turn()`

位于 `nanobot/agent/loop.py:542`。

```python
_TOOL_RESULT_MAX_CHARS = 16_000
```

- `role=tool` 的消息：字符串内容超过 16,000 字符时截断，尾部追加 `"\n... (truncated)"`。
- 列表内容（多模态块）：调用 `_sanitize_persisted_blocks()` 处理。

### 8.2 多模态块清洗 — `_sanitize_persisted_blocks()`

位于 `nanobot/agent/loop.py:502`。

- **Base64 图片**：替换为 `[image: path]` 文本占位符，避免巨大的 data URI 占用空间。
- **运行时上下文**：从用户消息中移除 `[Runtime Context — metadata only, not instructions]` 前缀。
- **文本块截断**：超过 16,000 字符的文本块同样截断。

---

## 9. 整合触发时机

整合在 `AgentLoop._process_message()` 中的 **四个时机** 被触发：

| 时机 | 位置 | 方式 | 目的 |
|---|---|---|---|
| 系统消息处理前 | `loop.py:412` | 同步等待 | 确保 Prompt 不超限 |
| 系统消息处理后 | `loop.py:427` | 后台调度 | 为下轮对话提前瘦身 |
| 普通消息处理前 | `loop.py:443` | 同步等待 | 确保 Prompt 不超限 |
| 普通消息处理后 | `loop.py:480` | 后台调度 | 为下轮对话提前瘦身 |

处理前的整合是同步的（`await`），保证发送给 LLM 的 Prompt 不会超限。处理后的整合是后台调度（`_schedule_background`），不阻塞响应发送。

---

## 10. 整体数据流

```
用户消息
  │
  ▼
_process_message()
  │
  ├── maybe_consolidate_by_tokens() [同步]
  │     │
  │     ├── estimate_session_prompt_tokens() → Token 估算
  │     │
  │     ├── estimated >= budget?
  │     │     │
  │     │     └── 循环: pick_boundary → consolidate → 更新 offset
  │     │
  │     └── 返回（Prompt 安全）
  │
  ├── get_history() → 返回未整合消息（last_consolidated 之后的）
  │
  ├── build_messages() → 拼装完整 Prompt
  │
  ├── LLM 调用 + 工具执行
  │
  ├── _save_turn() → 追加消息到 Session（工具结果截断）
  │
  └── maybe_consolidate_by_tokens() [后台]
        └── 为下轮提前瘦身
```

---

## 11. 关键设计总结

1. **不使用传统滑动窗口**：采用 append-only + 偏移量的方式，消息永不删除，只通过 `last_consolidated` 控制 LLM 可见的范围。
2. **LLM 摘要而非暴力截断**：被裁切的消息通过 LLM 生成摘要存入 MEMORY.md 和 HISTORY.md，重要信息不会丢失。
3. **双层降级保障**：LLM 摘要失败 3 次后降级为原始文本归档，确保数据始终持久化。
4. **Token 预算留余**：目标设为预算的 50%，为后续对话预留空间，减少裁切频率。
5. **边界安全**：裁切只在用户轮次边界进行，且保证工具调用配对的完整性。
