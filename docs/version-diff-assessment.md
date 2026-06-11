# Git Commit 两版本差异评估报告

## 基本信息

| 项目 | 值 |
|------|------|
| 当前 Commit | `083590f4` (Merge tag 'v0.1.5.post3') |
| 上一版本 Commit | `aa170504` |
| 变更规模 | **373 个文件**, +76,211 / -5,809 行 |
| 覆盖版本 | v0.1.5 → v0.1.5.post1 → v0.1.5.post2 → v0.1.5.post3 |
| 总计 PR | **270 PRs**, 约 76 位新贡献者 |

---

## 各版本 Release 概要

### v0.1.5 — "让建筑变得宜居" (66 PRs, 27 新贡献者)

核心主题：**长期运行可靠性 + 记忆系统架构 + 生产部署**

- **长期任务可靠性**：`CancelledError` 不再孤立子进程，重试分类使用结构化错误元数据（非正则匹配），429 配额耗尽立即停止而非盲目重试，Azure 重试不再双重计数
- **Dream 记忆系统**：两阶段记忆架构，分离实时对话历史与长期知识整合。后台整合 + Git 版本化存储，legacy `HISTORY.md` 自动迁移，Jinja2 模板系统
- **生产部署**：exec 沙盒化（bwrap），容器默认非 root 运行，API 端口默认绑定 localhost，配置支持 `${VAR}` 环境变量插值（不再硬编码密钥）
- **新 Provider**：GPT-5 支持（含温度处理）、小米 MiMo、百度千帆、DashScope/ModelArk thinking 参数控制、`reasoning_content` 全链路可见
- **Channel 增强**：Email 附件提取、WhatsApp 语音转写（Groq/OpenAI Whisper）、飞书自动移除反应 + 视频下载、Telegram 工具提示折叠引用
- **开发者体验**：内置 grep/glob 搜索工具、Tool 类 JSON Schema 重构、Python SDK facade、CLI `--config` 多实例、Web 搜索统一配置

### v0.1.5.post1 — "智能体学会了自我管理" (80 PRs, 25 新贡献者)

核心主题：**上下文自管理 + Mid-turn 注入 + WebSocket + Channel 深度增强**

- **Mid-turn 消息注入**：用户在 agent 工作期间发送后续消息不再排队等待，而是直接注入当前轮次，流式 channel 上回复在同一响应中继续
- **Dream 学习技能**：整合流程可识别重复工作流并提升为独立的工作区 skill，新增 `disabledSkills` 配置排除不需要的 skill
- **Auto Compact（自动压缩）**：监控空闲时段，主动压缩旧上下文保留近期消息。`idleCompactAfterMinutes` 精细控制
- **WebSocket Channel**：新的 WebSocket 服务端 channel，支持流式 delta/stream_end 事件、Token 认证、每连接会话、TLS
- **Channel 增强**：Telegram 位置分享、Discord 流式回复 + 代理支持、飞书 done-emoji + inline 工具提示 + Lark 全局域配置、QQ/WeCom 全媒体支持、Slack 消息工具解析 `#channel`/`@user`、API 端点支持文件上传（JSON base64 + multipart）
- **Provider**：Anthropic adaptive reasoning、Kimi thinking（k2.5/k2.6）、StepFun Plan API、非 Claude Provider 角色交替强制、工具调用参数规范化
- **MCP/工具/搜索**：MCP 资源和 prompt 暴露为只读工具、多 MCP 服务器隔离任务连接、notebook 编辑工具、Kagi 搜索、exec 工具 Windows 支持 + `allowed_env_keys`
- **Cron 修复**：4 个独立修复解决了重入存储重载、固定间隔任务重复、任务配置不重载、手动运行状态丢失

### v0.1.5.post2 — "扩展与打磨" (67 PRs, 12 新贡献者)

核心主题：**Windows/Python 3.14 + Office 文档 + MS Teams + SSE 流式 + 可靠性**

- **Windows + Python 3.14 一等支持**：完整 CI 矩阵、安装标记、运行时修复。不再需要 WSL
- **Office 文档原生读取**：`read_file` 工具支持 DOCX/XLSX/PPTX 文本提取（含表格和分组形状）
- **OpenAI 兼容 API SSE 流式**：`/v1/chat/completions` 支持 `stream=true` 的 SSE chunk 输出
- **Microsoft Teams Channel**：新增 MS Teams 支持
- **MiniMax thinking + LM Studio + MyTool**：MiniMax Anthropic-style thinking 端点、LM Studio nullable API key、MyTool 运行时自检（隐藏敏感配置）
- **可靠性加固**：会话文件原子写入 + 损坏文件修复、Memory cursor 恢复非整数损坏、Auto-compact 跳过活跃任务会话、Provider Responses API 熔断器、智谱 1302 限流识别
- **Channel 细节**：Telegram 长回复中流拆分 + Markdown 渲染、Discord bot-to-bot 消息 + 频道允许列表、Email SPF/DKIM 去重、WeCom 混合消息解析
- **WebUI 早期预览**：`webui/` 目录 landed，WebSocket 聊天流程 + i18n + 深色模式代码块（源码预览，未打包进 wheel）

### v0.1.5.post3 — "对话线程化" (57 PRs, 12 新贡献者)

核心主题：**线程/话题隔离 + DeepSeek-V4 + ask_user + 会话持久化**

- **线程隔离（飞书/Discord/Slack/MS Teams）**：飞书群聊话题独立会话、Discord 线程继承父频道 allowlist + 会话隔离、Slack 保持线程上下文、MS Teams 会话引用 TTL 修剪
- **Per-channel 进度控制**：`sendProgress`/`sendToolHints` 可在每个 channel 配置中单独覆盖
- **ask_user 工具**：agent 可中途暂停询问用户选择（WebUI 渲染为按钮，其他 channel 回退文本）
- **DeepSeek-V4**：完整 thinking mode + legacy 会话兼容，follow-up 修复不完整 reasoning history 和非字符串消息内容
- **Hugging Face Inference Provider**：新增 Provider
- **Olostep Web Search**：新增 Web 搜索 Provider
- **extra_body 配置**：OpenAI 兼容端点支持 `extraBody`（用于 vLLM guided decoding 等）
- **超时控制**：`NANOBOT_LLM_TIMEOUT_S` / `NANOBOT_OPENAI_COMPAT_TIMEOUT_S` 分离外层轮次限制与内层 HTTP 超时
- **Memory/Session 加固**：`consolidationRatio` 可调（0.1-0.95）、`maxMessages` 回放上限（默认 120）、history.jsonl 原子写入 + fsync + 目录同步、会话优雅关闭 fsync
- **安全修复**：`path_append` shell 注入修复、工作区目录违规停止 agent 循环
- **WebUI 演进**：图片上传、视频渲染、ask_user 选择、模型设置（仍为源码预览）

---

## 变更分类统计

### 按模块分布

| 模块 | 变更文件数 | 关键变更 |
|------|-----------|---------|
| **Channel（渠道）** | ~50 | 新增 MSTeams、WebSocket、Weixin 重写；飞书/Discord/Telegram/Slack/QQ/WeCom 大幅增强 |
| **Agent（核心循环）** | ~30 | auto compact、mid-turn 注入、Dream skill 发现、ask_user、subagent 优化 |
| **Provider（模型）** | ~25 | GPT-5、DeepSeek-V4、MiMo、千帆、HuggingFace、Kimi thinking、adaptive reasoning |
| **Memory（记忆）** | ~15 | Dream 两阶段记忆、Git 版本化、原子写入、consolidation ratio |
| **WebUI** | ~80 | 全新 React 前端（WebSocket 聊天、i18n、图片上传、视频、深色模式） |
| **Tool（工具）** | ~20 | grep/glob、notebook、ask_user、MyTool、sandbox、exec 增强 |
| **Test（测试）** | ~120 | 大量新增测试覆盖所有新功能和修复 |
| **Config（配置）** | ~10 | env var 插值、extra_body、max_messages、consolidation_ratio |
| **Doc（文档）** | ~15 | README 重构为 docs-first、新增 docs/ 目录、部署指南 |
| **CI/Infra** | ~10 | Windows CI、Python 3.14、Docker 优化、codespell |

### 按变更类型

| 类型 | 占比 |
|------|------|
| 新功能（feat） | ~40% |
| 缺陷修复（fix） | ~40% |
| 重构（refactor） | ~10% |
| 文档（docs） | ~5% |
| 性能（perf） | ~3% |
| 其他（chore/style/ci） | ~2% |

---

## 关键架构演进

1. **记忆系统从无到有**：legacy HISTORY.md → Dream 两阶段记忆 + Git 版本化存储 + 可配置压缩比
2. **Channel 从简单到丰富**：从基础收发 → 线程隔离 + 流式 + 媒体 + 进度控制，新增 MSTeams/WebSocket
3. **Agent 循环成熟**：auto compact + mid-turn 注入 + ask_user + workspace 安全终止
4. **Provider 生态扩展**：从基础 OpenAI/Anthropic → GPT-5/DeepSeek-V4/MiMo/千帆/HuggingFace/Kimi
5. **生产就绪**：沙盒、非 root 容器、环境变量插值、原子写入、熔断器、超时控制
6. **WebUI 从零开始**：全新 React + TypeScript 前端（源码预览阶段）

---

## 总结

这两版本之间的差异涵盖了 nanobot 项目从 **v0.1.4.post6 到 v0.1.5.post3** 的全部演进，是项目历史上最大的一次版本跳跃。270 个 PR、373 个文件、超过 7.6 万行新增代码，使 nanobot 从一个原型项目转变为可生产部署的 AI Agent 基础设施。
