# Nanobot 配置文件说明

> 配置文件位置: `~/.nanobot/config.json` (Windows: `C:\Users\<用户名>\.nanobot\config.json`)

## 配置文件结构概览

```json
{
  "agents": { ... },      // Agent 默认配置
  "channels": { ... },    // 消息渠道配置
  "providers": { ... },   // AI 模型提供商配置
  "gateway": { ... },     // 网关服务配置
  "tools": { ... }        // 工具配置
}
```

---

## 1. `agents` - Agent 配置

### `agents.defaults` - 默认配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `workspace` | string | `~/.nanobot/workspace` | Agent 工作目录，用于存储会话、技能等数据 |
| `model` | string | `anthropic/claude-opus-4-5` | 默认使用的模型名称 |
| `provider` | string | `auto` | 强制使用的提供商，`auto` 表示自动检测 |
| `maxTokens` | int | `8192` | 单次请求最大 token 数 |
| `temperature` | float | `0.1` | 温度参数 (0.0-2.0)，越高越随机 |
| `maxToolIterations` | int | `40` | 单次对话最大工具调用次数 |
| `memoryWindow` | int | `100` | 会话记忆保留的消息数量 |
| `reasoningEffort` | string \| null | `null` | 推理努力程度：`low` / `medium` / `high` |

#### 常用模型示例

```json
"model": "glm-4.7"                    // 智谱 GLM-4.7
"model": "claude-opus-4-5"            // Anthropic Claude Opus 4.5
"model": "gpt-4o"                     // OpenAI GPT-4o
"model": "deepseek-chat"              // DeepSeek 聊天模型
"model": "qwen-max"                   // 阿里通义千问
"model": "kimi-k2.5"                  // Moonshot Kimi
"model": "gemini-2.0-flash-exp"       // Google Gemini
```

---

## 2. `channels` - 消息渠道配置

### 全局配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sendProgress` | bool | `true` | 是否发送实时进度消息 |
| `sendToolHints` | bool | `false` | 是否发送工具调用提示 |

### `channels.feishu` - 飞书

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用飞书渠道 |
| `appId` | string | - | 飞书应用的 App ID |
| `appSecret` | string | - | 飞书应用的 App Secret |
| `encryptKey` | string | - | 事件订阅加密密钥 (可选) |
| `verificationToken` | string | - | 事件订阅验证令牌 (可选) |
| `allowFrom` | string[] | `[]` | 允许使用的用户 open_id 列表 |
| `reactEmoji` | string | `THUMBSUP` | 消息反应表情：`THUMBSUP` / `OK` / `DONE` / `SMILE` |

### `channels.telegram` - Telegram

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 Telegram 渠道 |
| `token` | string | - | Bot Token (从 @BotFather 获取) |
| `proxy` | string \| null | `null` | 代理 URL，如 `http://127.0.0.1:7890` 或 `socks5://127.0.0.1:1080` |
| `allowFrom` | string[] | `[]` | 允许的用户 ID 或用户名 |
| `replyToMessage` | bool | `false` | 回复时是否引用原消息 |

### `channels.discord` - Discord

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 Discord 渠道 |
| `token` | string | - | Bot Token (从 Discord Developer Portal 获取) |
| `allowFrom` | string[] | `[]` | 允许的用户 ID |
| `gatewayUrl` | string | `wss://gateway.discord.gg/?v=10&encoding=json` | Discord Gateway URL |
| `intents` | int | `37377` | Discord Intents 位掩码 |

### `channels.slack` - Slack

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 Slack 渠道 |
| `mode` | string | `socket` | 连接模式 (仅支持 `socket`) |
| `webhookPath` | string | `/slack/events` | Webhook 路径 |
| `botToken` | string | - | Bot Token (`xoxb-...`) |
| `appToken` | string | - | App Token (`xapp-...`) |
| `replyInThread` | bool | `true` | 是否在 Thread 中回复 |
| `reactEmoji` | string | `eyes` | 消息反应表情 |
| `groupPolicy` | string | `mention` | 群组策略：`mention` / `open` / `allowlist` |
| `groupAllowFrom` | string[] | `[]` | 群组白名单频道 ID |
| `dm.enabled` | bool | `true` | 是否允许私信 |
| `dm.policy` | string | `open` | 私信策略：`open` / `allowlist` |

### `channels.qq` - QQ 机器人

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 QQ 渠道 |
| `appId` | string | - | QQ 机器人 AppID (从 q.qq.com 获取) |
| `secret` | string | - | QQ 机器人 AppSecret |
| `allowFrom` | string[] | `[]` | 允许的用户 openid (空则公开) |

### `channels.dingtalk` - 钉钉

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用钉钉渠道 |
| `clientId` | string | - | AppKey |
| `clientSecret` | string | - | AppSecret |
| `allowFrom` | string[] | `[]` | 允许的员工 staff_id |

### `channels.matrix` - Matrix (Element)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 Matrix 渠道 |
| `homeserver` | string | `https://matrix.org` | Matrix 服务器地址 |
| `accessToken` | string | - | 访问令牌 |
| `userId` | string | - | 用户 ID (如 `@bot:matrix.org`) |
| `deviceId` | string | - | 设备 ID |
| `e2eeEnabled` | bool | `true` | 是否启用端到端加密 |
| `syncStopGraceSeconds` | int | `2` | 同步停止等待秒数 |
| `maxMediaBytes` | int | `20971520` | 最大媒体文件字节数 |
| `groupPolicy` | string | `open` | 群组策略：`open` / `mention` / `allowlist` |
| `groupAllowFrom` | string[] | `[]` | 群组白名单 |
| `allowRoomMentions` | bool | `false` | 是否允许房间提及 |

### `channels.email` - 邮件

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用邮件渠道 |
| `consentGranted` | bool | `false` | 是否授予邮箱访问权限 |
| `imapHost` | string | - | IMAP 服务器地址 |
| `imapPort` | int | `993` | IMAP 端口 |
| `imapUsername` | string | - | IMAP 用户名 |
| `imapPassword` | string | - | IMAP 密码 |
| `imapMailbox` | string | `INBOX` | IMAP 收件箱名称 |
| `imapUseSsl` | bool | `true` | IMAP 是否使用 SSL |
| `smtpHost` | string | - | SMTP 服务器地址 |
| `smtpPort` | int | `587` | SMTP 端口 |
| `smtpUsername` | string | - | SMTP 用户名 |
| `smtpPassword` | string | - | SMTP 密码 |
| `smtpUseTls` | bool | `true` | SMTP 是否使用 TLS |
| `smtpUseSsl` | bool | `false` | SMTP 是否使用 SSL |
| `fromAddress` | string | - | 发件人地址 |
| `autoReplyEnabled` | bool | `true` | 是否自动回复 |
| `pollIntervalSeconds` | int | `30` | 邮件轮询间隔 (秒) |
| `markSeen` | bool | `true` | 是否标记已读 |
| `maxBodyChars` | int | `12000` | 邮件正文最大字符数 |
| `subjectPrefix` | string | `Re: ` | 回复主题前缀 |
| `allowFrom` | string[] | `[]` | 允许的发件人邮箱 |

### `channels.mochat` - Mochat

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 Mochat 渠道 |
| `baseUrl` | string | `https://mochat.io` | Mochat 服务地址 |
| `socketUrl` | string | - | Socket URL |
| `socketPath` | string | `/socket.io` | Socket 路径 |
| `clawToken` | string | - | Claw Token |
| `agentUserId` | string | - | Agent 用户 ID |
| `sessions` | string[] | `[]` | 会话列表 |
| `panels` | string[] | `[]` | 面板列表 |
| `allowFrom` | string[] | `[]` | 允许的用户 ID |
| `mention.requireInGroups` | bool | `false` | 群组是否需要 @ 机器人 |
| `groups` | object | `{}` | 各群组提及规则 |
| `replyDelayMode` | string | `non-mention` | 延迟回复模式：`off` / `non-mention` |
| `replyDelayMs` | int | `120000` | 延迟回复毫秒数 |

### `channels.whatsapp` - WhatsApp

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `false` | 是否启用 WhatsApp 渠道 |
| `bridgeUrl` | string | `ws://localhost:3001` | Bridge 服务地址 |
| `bridgeToken` | string | - | Bridge 认证令牌 (推荐) |
| `allowFrom` | string[] | `[]` | 允许的手机号码 |

---

## 3. `providers` - AI 模型提供商配置

每个 Provider 的通用配置结构：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `apiKey` | string | - | API 密钥 |
| `apiBase` | string \| null | `null` | API 基础 URL (可选) |
| `extraHeaders` | object \| null | `null` | 额外 HTTP 请求头 (如 AiHubMix 的 APP-Code) |

### 支持的 Provider 列表

| Provider 名称 | 关键词模型 | API Key 环境变量 | 说明 |
|---------------|-----------|-----------------|------|
| `custom` | - | - | 自定义 OpenAI 兼容接口 (直连，不经过 LiteLLM) |
| `openrouter` | `openrouter` | `OPENROUTER_API_KEY` | OpenRouter 网关 (API Key 以 `sk-or-` 开头) |
| `aihubmix` | `aihubmix` | `OPENAI_API_KEY` | AiHubMix 网关 |
| `siliconflow` | `siliconflow` | `OPENAI_API_KEY` | 硅基流动网关 |
| `volcengine` | `volcengine`, `volces`, `ark` | `OPENAI_API_KEY` | 火山引擎网关 |
| `anthropic` | `anthropic`, `claude` | `ANTHROPIC_API_KEY` | Anthropic Claude |
| `openai` | `openai`, `gpt` | `OPENAI_API_KEY` | OpenAI GPT |
| `openaiCodex` | `openai-codex` | - | OpenAI Codex (OAuth 认证) |
| `githubCopilot` | `github_copilot`, `copilot` | - | GitHub Copilot (OAuth 认证) |
| `deepseek` | `deepseek` | `DEEPSEEK_API_KEY` | DeepSeek |
| `gemini` | `gemini` | `GEMINI_API_KEY` | Google Gemini |
| `zhipu` | `zhipu`, `glm`, `zai` | `ZAI_API_KEY` | 智谱 AI (GLM 模型) |
| `dashscope` | `qwen`, `dashscope` | `DASHSCOPE_API_KEY` | 阿里云通义千问 |
| `moonshot` | `moonshot`, `kimi` | `MOONSHOT_API_KEY` | Moonshot Kimi |
| `minimax` | `minimax` | `MINIMAX_API_KEY` | MiniMax |
| `vllm` | `vllm` | `HOSTED_VLLM_API_KEY` | vLLM / 本地 OpenAI 兼容服务 |
| `groq` | `groq` | `GROQ_API_KEY` | Groq (主要用于语音转写) |

### Provider 自动检测规则

1. **显式前缀**: 模型名带 provider 前缀 (如 `zhipu/glm-4`) 直接匹配
2. **关键词匹配**: 模型名包含 provider 关键词 (如 `glm-4` → `zhipu`)
3. **网关检测**: API Key 前缀或 apiBase URL 关键词
4. **回退**: 顺序遍历有 API Key 的 provider

### OAuth Provider

`openaiCodex` 和 `githubCopilot` 不需要 API Key，使用 OAuth 流程认证。

---

## 4. `gateway` - 网关服务配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `host` | string | `0.0.0.0` | 监听地址 |
| `port` | int | `18790` | 监听端口 |
| `heartbeat.enabled` | bool | `true` | 是否启用心跳 |
| `heartbeat.intervalS` | int | `1800` | 心跳间隔 (秒，默认 30 分钟) |

---

## 5. `tools` - 工具配置

### `tools.web` - Web 工具

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `search.apiKey` | string | - | Brave Search API 密钥 (用于网络搜索) |
| `search.maxResults` | int | `5` | 搜索结果最大数量 |

### `tools.exec` - Shell 执行工具

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout` | int | `60` | 命令执行超时时间 (秒) |
| `pathAppend` | string | - | 追加到 PATH 环境变量的路径 |

### 全局工具配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `restrictToWorkspace` | bool | `false` | 是否限制工具只能访问 workspace 目录 |

### `tools.mcpServers` - MCP 服务器配置

MCP (Model Context Protocol) 服务器配置，支持 stdio 和 HTTP 两种连接方式。

#### Stdio 连接方式

```json
"mcpServers": {
  "server-name": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-example"],
    "env": {},
    "toolTimeout": 30
  }
}
```

#### HTTP 连接方式

```json
"mcpServers": {
  "server-name": {
    "url": "http://localhost:3000/mcp",
    "headers": {
      "Authorization": "Bearer xxx"
    },
    "toolTimeout": 30
  }
}
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `command` | string | - | (Stdio) 要执行的命令 |
| `args` | string[] | `[]` | (Stdio) 命令参数 |
| `env` | object | `{}` | (Stdio) 额外的环境变量 |
| `url` | string | - | (HTTP) HTTP 端点 URL |
| `headers` | object | `{}` | (HTTP) 自定义 HTTP 请求头 |
| `toolTimeout` | int | `30` | 工具调用超时时间 (秒) |

---

## 配置示例

### 最小化配置 (仅启用飞书 + 智谱 AI)

```json
{
  "agents": {
    "defaults": {
      "model": "glm-4.7",
      "provider": "zhipu"
    }
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "allowFrom": ["ou_xxx"]
    }
  },
  "providers": {
    "zhipu": {
      "apiKey": "your-api-key",
      "apiBase": "https://open.bigmodel.cn/api/coding/paas/v4"
    }
  }
}
```

### 使用 OpenRouter 网关

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "provider": "auto"
    }
  },
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-xxx"
    }
  }
}
```

### 使用本地 vLLM

```json
{
  "agents": {
    "defaults": {
      "model": "Llama-3-8B",
      "provider": "vllm"
    }
  },
  "providers": {
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://localhost:8000/v1"
    }
  }
}
```

---

## 环境变量支持

所有配置项都可以通过环境变量覆盖，格式为 `NANOBOT__<Section>__<Key>`。

例如：

```bash
export NANOBOT__AGENTS__DEFAULTS__MODEL="gpt-4o"
export NANOBOT__PROVIDERS__OPENAI__API_KEY="sk-xxx"
export NANOBOT__CHANNELS__FEISHU__APP_ID="cli_xxx"
```

---

## 相关文件

- 配置 Schema: `nanobot/config/schema.py`
- Provider 注册表: `nanobot/providers/registry.py`
