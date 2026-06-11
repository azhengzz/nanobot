# Nanobot 中大模型推理内容（reasoning_content）的处理机制

## 概述

Nanobot 支持两类推理内容（Reasoning Content）：

| 字段 | 适用模型 | 格式 |
|------|---------|------|
| `reasoning_content` | DeepSeek-R1、Kimi 等 | 纯字符串 |
| `thinking_blocks` | Anthropic Claude（Extended Thinking） | 结构化列表，含 `type`/`thinking`/`signature` |

整个处理流程分为四个阶段：**配置 -> Provider 提取 -> Runner 传递 -> Token 估算**。

---

## 1. 配置层：reasoning_effort

定义在 [schema.py:43](../nanobot/config/schema.py#L43)：

```python
reasoning_effort: str | None = None  # low / medium / high - enables LLM thinking mode
```

`reasoning_effort` 是一个三档开关（`low` / `medium` / `high`），通过 [runner.py:81-82](../nanobot/agent/runner.py#L81-L82) 传入 Provider：

```python
if spec.reasoning_effort is not None:
    kwargs["reasoning_effort"] = spec.reasoning_effort
```

各 Provider 对该参数的处理方式不同（见下文）。

---

## 2. 数据模型

定义在 [base.py:68-76](../nanobot/providers/base.py#L68-L76)：

```python
@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    finish_reason: str = "stop"
    usage: dict[str, int] = field(default_factory=dict)
    reasoning_content: str | None = None      # Kimi, DeepSeek-R1 etc.
    thinking_blocks: list[dict] | None = None  # Anthropic extended thinking
```

---

## 3. Provider 层：从 API 响应中提取推理内容

### 3.1 OpenAI Compatible Provider

文件：[openai_compat_provider.py](../nanobot/providers/openai_compat_provider.py)

**请求构建**（[line 262](../nanobot/providers/openai_compat_provider.py#L262)）：当存在 `reasoning_effort` 时，将其传入 API payload。

**非流式解析**（[line 359-395](../nanobot/providers/openai_compat_provider.py#L359-L395)）：

```python
# 从 response message 中提取
reasoning_content = msg0.get("reasoning_content")

# 遍历所有 choices，补充 reasoning_content（某些 Provider 可能不在首 choice 返回）
if not reasoning_content:
    reasoning_content = m.get("reasoning_content")

# 构造 LLMResponse
return LLMResponse(
    ...,
    reasoning_content=reasoning_content if isinstance(reasoning_content, str) else None,
)
```

**SDK 对象解析**（[line 431-437](../nanobot/providers/openai_compat_provider.py#L431-L437)）：

```python
return LLMResponse(
    ...,
    reasoning_content=getattr(msg, "reasoning_content", None) or None,
)
```

**消息清洗**（[line 21-24](../nanobot/providers/openai_compat_provider.py#L21-L24)）：

`reasoning_content` 被列入允许的消息键白名单，确保在 `_sanitize_messages` 时不会被丢弃：

```python
_ALLOWED_MSG_KEYS = frozenset({
    "role", "content", "tool_calls", "tool_call_id", "name",
    "reasoning_content", "extra_content",
})
```

### 3.2 Azure OpenAI Provider

文件：[azure_openai_provider.py](../nanobot/providers/azure_openai_provider.py)

**请求构建**（[line 104-108](../nanobot/providers/azure_openai_provider.py#L104-L108)）：

- 当启用 `reasoning_effort` 时，禁用 temperature（[line 75-81](../nanobot/providers/azure_openai_provider.py#L75-L81)）
- 直接在 payload 中传入 `reasoning_effort` 参数

```python
if reasoning_effort:
    payload["reasoning_effort"] = reasoning_effort
```

**响应解析**（[line 192-199](../nanobot/providers/azure_openai_provider.py#L192-L199)）：

```python
reasoning_content = message.get("reasoning_content") or None

return LLMResponse(
    ...,
    reasoning_content=reasoning_content,
)
```

### 3.3 Anthropic Provider

文件：[anthropic_provider.py](../nanobot/providers/anthropic_provider.py)

Anthropic 使用独立的 `thinking_blocks` 机制，而非 `reasoning_content`。

**请求构建**（[line 311-327](../nanobot/providers/anthropic_provider.py#L311-L327)）：

```python
thinking_enabled = bool(reasoning_effort)

if thinking_enabled:
    budget_map = {"low": 1024, "medium": 4096, "high": max(8192, max_tokens)}
    budget = budget_map.get(reasoning_effort.lower(), 4096)
    kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
    kwargs["max_tokens"] = max(max_tokens, budget + 4096)
    kwargs["temperature"] = 1.0  # thinking 模式要求 temperature=1.0
```

**响应解析**（[line 361-366](../nanobot/providers/anthropic_provider.py#L361-L366)）：

```python
elif block.type == "thinking":
    thinking_blocks.append({
        "type": "thinking",
        "thinking": block.thinking,
        "signature": getattr(block, "signature", ""),
    })
```

**消息回传**（[line 122-128](../nanobot/providers/anthropic_provider.py#L122-L128)）：

在下一轮对话中，将 `thinking_blocks` 还原为 Anthropic API 要求的格式：

```python
for tb in msg.get("thinking_blocks") or []:
    if isinstance(tb, dict) and tb.get("type") == "thinking":
        blocks.append({
            "type": "thinking",
            "thinking": tb.get("thinking", ""),
            "signature": tb.get("signature", ""),
        })
```

### 3.4 OpenAI Codex Provider

文件：[openai_codex_provider.py](../nanobot/providers/openai_codex_provider.py)

**请求构建**（[line 51-57](../nanobot/providers/openai_codex_provider.py#L51-L57)）：

```python
body["include"] = ["reasoning.encrypted_content"]

if reasoning_effort:
    body["reasoning"] = {"effort": reasoning_effort}
```

Codex 使用 `reasoning.encrypted_content` 返回加密的推理内容，请求通过 `include` 字段声明需要该内容。

---

## 4. Runner 层：在 Agent 循环中传递推理内容

文件：[runner.py](../nanobot/agent/runner.py)

Runner 通过 `build_assistant_message()` 将推理内容附加到 assistant 消息中，确保在多轮工具调用循环中推理上下文不丢失。

**工具调用轮次**（[line 108-113](../nanobot/agent/runner.py#L108-L113)）：

```python
messages.append(build_assistant_message(
    response.content or "",
    tool_calls=[tc.to_openai_tool_call() for tc in response.tool_calls],
    reasoning_content=response.reasoning_content,
    thinking_blocks=response.thinking_blocks,
))
```

**最终回复轮次**（[line 155-159](../nanobot/agent/runner.py#L155-L159)）：

```python
messages.append(build_assistant_message(
    clean,
    reasoning_content=response.reasoning_content,
    thinking_blocks=response.thinking_blocks,
))
```

---

## 5. 消息构建

文件：[helpers.py:117-131](../nanobot/utils/helpers.py#L117-L131)

```python
def build_assistant_message(
    content, tool_calls=None, reasoning_content=None, thinking_blocks=None,
) -> dict[str, Any]:
    msg = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    if reasoning_content is not None:
        msg["reasoning_content"] = reasoning_content
    if thinking_blocks:
        msg["thinking_blocks"] = thinking_blocks
    return msg
```

只有当推理内容存在时才附加到消息中，避免向不支持的 Provider 发送多余字段。

---

## 6. Token 估算

文件：[helpers.py:134-177](../nanobot/utils/helpers.py#L134-L177)

`reasoning_content` 被纳入 token 估算，确保上下文窗口管理准确：

```python
rc = msg.get("reasoning_content")
if isinstance(rc, str) and rc:
    parts.append(rc)
```

这保证了在计算上下文占用时不会遗漏推理内容消耗的 token。

---

## 7. 完整数据流

```
┌─────────────────────────────────────────────────────┐
│  配置层 (schema.py)                                  │
│  reasoning_effort = "low" | "medium" | "high"       │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Runner 层 (runner.py)                              │
│  将 reasoning_effort 传入 Provider.chat()            │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Provider 层                                        │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │ OpenAI Compat   │  │ Azure OpenAI             │  │
│  │ reasoning_effort│  │ reasoning_effort          │  │
│  │ -> API payload  │  │ -> payload, 禁用 temp    │  │
│  │                 │  │                          │  │
│  │ 响应解析:       │  │ 响应解析:                │  │
│  │ reasoning_content│  │ reasoning_content        │  │
│  └─────────────────┘  └──────────────────────────┘  │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │ Anthropic       │  │ OpenAI Codex             │  │
│  │ reasoning_effort│  │ reasoning_effort         │  │
│  │ -> thinking配置 │  │ -> reasoning.effort      │  │
│  │                 │  │                          │  │
│  │ 响应解析:       │  │ include:                 │  │
│  │ thinking_blocks │  │ reasoning.encrypted_     │  │
│  └─────────────────┘  │ content                  │  │
│                        └──────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ LLMResponse
                       ▼
┌─────────────────────────────────────────────────────┐
│  Runner 层 (runner.py)                              │
│  build_assistant_message() 保留推理字段              │
│  多轮工具调用中 reasoning 上下文完整传递             │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  Token 估算 (helpers.py)                            │
│  estimate_prompt_tokens() 计算 reasoning_content    │
│  占用的 token 数                                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│  下一轮 API 请求                                     │
│  _sanitize_messages() 白名单保留 reasoning_content   │
│  Anthropic: _assistant_blocks() 还原 thinking_blocks │
└─────────────────────────────────────────────────────┘
```

---

## 8. 关键设计决策

| 设计点 | 说明 |
|--------|------|
| **双字段分离** | `reasoning_content`（字符串）和 `thinking_blocks`（结构化）分别适配不同 Provider 的 API 规范 |
| **白名单保留** | 消息清洗时 `reasoning_content` 在 `_ALLOWED_MSG_KEYS` 中，不会被过滤 |
| **条件附加** | `build_assistant_message` 仅在字段存在时附加，避免不支持的 Provider 收到多余字段 |
| **Token 感知** | 推理内容参与 token 估算，防止上下文溢出 |
| **多 choice 容错** | OpenAI Compat Provider 遍历所有 choices 补充 reasoning_content |
| **temperature 处理** | Azure/OpenAI Provider 在启用 reasoning 时自动禁用/调整 temperature；Anthropic 强制设为 1.0 |
