# Dream 记忆系统技术实现细则

## 1. 系统概述

Dream 是 nanobot 的**定期后台记忆整理子系统**，灵感源自人类睡眠时的记忆巩固机制。它在 Bot 空闲时自动唤醒，扫描未处理的对话历史摘要，提炼关键事实并编辑持久化记忆文件。

**核心设计哲学：**

- **两阶段处理**：Phase 1 分析产出变更清单，Phase 2 通过工具执行精确编辑
- **人类可审计**：所有变更通过 Git 版本控制，支持查看 diff 和一键回滚
- **渐进式更新**：基于游标的增量处理，永不重放已处理的历史

---

## 2. 架构全景

```
┌───────────────────────────────────────────────────────────────┐
│                       Agent Loop                              │
│                                                               │
│  ┌─────────────┐    ┌───────────────┐    ┌────────────────┐  │
│  │  Session     │    │ Consolidator  │    │     Dream      │  │
│  │  Messages    │───>│ (Token Budget)│───>│  (Scheduled)   │  │
│  │  (短期)      │    │               │    │                │  │
│  └─────────────┘    └───────┬───────┘    └───────┬────────┘  │
│                             │                     │            │
│                             ▼                     ▼            │
│                    history.jsonl            SOUL.md            │
│                    (归档摘要)               USER.md            │
│                                            MEMORY.md          │
│                                     ┌──────────────────┐     │
│                                     │   GitStore       │     │
│                                     │ (版本控制/回滚)   │     │
│                                     └──────────────────┘     │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. 三层记忆体系

### 3.1 文件层级

| 文件 | 用途 | 生命周期 | 谁可写入 |
|------|------|----------|----------|
| `SOUL.md` | Bot 人格、行为准则、沟通风格 | 永久 | Dream |
| `USER.md` | 用户身份、偏好、习惯 | 永久 | Dream |
| `memory/MEMORY.md` | 项目上下文、关键事实、决策记录 | 长期（有老化机制） | Dream |
| `memory/history.jsonl` | 对话摘要归档（JSONL 格式） | 中期（有上限压缩） | Consolidator |
| `memory/.cursor` | 写入游标（Consolidator 用） | — | 系统内部 |
| `memory/.dream_cursor` | Dream 消费游标 | — | Dream |

### 3.2 游标机制

系统维护两个独立游标：

```
.cursor          →  Consolidator 写入位置（history.jsonl 最后写入的 cursor 值）
.dream_cursor    →  Dream 已处理到的位置（Phase 1 读取起点）
```

**增量处理保证：** Dream 每次只读取 `cursor > dream_cursor` 的条目，处理完毕后推进 `dream_cursor`。即使 Phase 2 失败，游标也会推进，防止无限重处理。

---

## 4. MemoryStore：纯文件 I/O 层

**源码位置：** `nanobot/agent/memory.py:33`

### 4.1 核心职责

- 管理所有记忆文件的读写操作
- 维护 history.jsonl 的追加写入、游标递增
- 处理 legacy HISTORY.md → history.jsonl 的一次性迁移
- 提供 GitStore 集成用于版本控制

### 4.2 history.jsonl 格式

每行一条 JSON 记录：

```json
{"cursor": 42, "timestamp": "2026-06-08 14:30", "content": "用户偏好简短回答..."}
```

**写入保护链：**

1. `strip_think()` — 过滤模板泄漏（未闭合的 `<think`、`<channel|>` 标记）
2. `truncate_text()` — 硬性字符上限（`_HISTORY_ENTRY_HARD_CAP = 64,000`）
3. 空内容保护 — 若 `strip_think` 清空了原始内容，仍写入空字符串而非丢弃记录

### 4.3 原子写入

`_write_entries()` 方法使用 write-to-temp + rename 模式确保 history.jsonl 不会因中断而损坏：

```python
tmp_path = self.history_file.with_suffix(".jsonl.tmp")
# 写入临时文件 → fsync → os.replace 原子替换
# Windows 上跳过目录 fsync（NTFS 元数据同步日志）
```

### 4.4 历史压缩

`compact_history()` 维护 `max_history_entries`（默认 1000）上限。超出时丢弃最旧的条目，保留最新的。在每次 Dream run 结束后自动调用。

---

## 5. Consolidator：Token 预算驱动的即时压缩

**源码位置：** `nanobot/agent/memory.py:443`

### 5.1 触发条件

Consolidator 不是定时运行的——它在每次 agent 响应后检查 token 预算：

```
当前 prompt token 数 > 输入 token 预算 → 触发压缩
```

**输入 token 预算计算：**

```python
_input_token_budget = context_window_tokens - max_completion_tokens - 1024（安全余量）
```

**目标压缩比：** 默认 `consolidation_ratio = 0.5`，即压缩到预算的 50%。

### 5.2 压缩流程

```
1. estimate_session_prompt_tokens() → 构造探测消息，估算当前 token 用量
2. pick_consolidation_boundary() → 在 user-turn 边界处找到安全切割点
3. archive() → 调用 LLM 生成摘要，追加到 history.jsonl
4. 推进 session.last_consolidated 游标
5. 重复直到 token 数 ≤ 目标值（最多 5 轮）
```

### 5.3 边界选择算法

`pick_consolidation_boundary()` 保证只在 **user turn 边界**处切割，避免在 assistant 回复中间截断：

```python
for idx in range(start, len(messages)):
    if idx > start and message.role == "user":
        last_boundary = (idx, removed_tokens)
        if removed_tokens >= tokens_to_remove:
            return last_boundary
```

### 5.4 降级策略

当 LLM 不可用（API 错误、超时等），`archive()` 降级为 `raw_archive()`：

- 直接格式化原始消息并写入 history.jsonl
- 添加 `[RAW]` 前缀标记为降级记录
- 保证数据不丢失（即使摘要质量下降）

### 5.5 与 Dream 的关系

```
Session Messages ──[Consolidator]──> history.jsonl ──[Dream]──> SOUL/USER/MEMORY.md
     (实时)                          (归档层)              (定期精炼)
```

Consolidator 是**被动的、即时的**（响应 token 压力），Dream 是**主动的、定期的**（深度分析并提炼长期记忆）。

---

## 6. Dream：两阶段记忆处理器

**源码位置：** `nanobot/agent/memory.py:706`

### 6.1 配置项

**配置定义：** `nanobot/config/schema.py:35`

```python
class DreamConfig(Base):
    interval_h: int = 2              # 运行间隔（小时）
    model_override: str | None       # 专用模型覆盖
    max_batch_size: int = 20         # 每次处理的最大历史条目数
    max_iterations: int = 15         # Phase 2 工具调用预算
    annotate_line_ages: bool = True  # 是否启用 git-blame 年龄标注
```

**调度方式：** 通过 `CronService` 以 `every_ms = interval_h * 3600000` 的间隔运行。支持 legacy `cron` 表达式覆盖。

### 6.2 Phase 1：分析

**模板：** `nanobot/templates/agent/dream_phase1.md`

**输入构造：**

```python
phase1_prompt = (
    f"## Conversation History\n{history_text}\n\n"
    f"## Current Date\n{current_date}\n\n"
    f"## Current MEMORY.md ({len} chars)\n{annotated_memory}\n\n"
    f"## Current SOUL.md ({len} chars)\n{current_soul}\n\n"
    f"## Current USER.md ({len} chars)\n{current_user}"
)
```

**关键机制——行年龄标注（`_annotate_with_ages`）：**

- 通过 `GitStore.line_ages()` 调用 `dulwich.porcelain.annotate()`（即 git blame）
- 对 MEMORY.md 中超过 14 天未修改的行添加 `← 30d` 标记
- SOUL.md 和 USER.md **永不标注**（它们是永久文件）
- 行数不匹配时（HEAD 与工作树不一致）跳过整个标注，避免错误标记

**Phase 1 输出格式：**

```
[FILE] 原子事实（尚未存在于记忆中）
[FILE-REMOVE] 移除原因
[SKILL] kebab-case-name: 可复用模式的简短描述
[SKIP] 无需更新
```

**分析覆盖的任务：**

1. **事实提取**：从对话历史中提取原子事实（如"有一只叫 Luna 的猫"而非"讨论了宠物"）
2. **去重扫描**：检查所有记忆文件间的冗余（MEMORY.md 不应重复 USER.md/SOUL.md 已有内容）
3. **陈旧检测**：基于行年龄标记审查过时内容（已过去的事件、已解决的跟踪、被取代的方法）
4. **技能发现**：当特定工作流在对话中出现 2+ 次时，标记为潜在 skill

### 6.3 Phase 2：精确编辑

**模板：** `nanobot/templates/agent/dream_phase2.md`

**执行方式：** 通过 `AgentRunner` 运行，赋予 LLM 以下工具：

| 工具 | 作用域 | 用途 |
|------|--------|------|
| `read_file` | workspace + builtin skills | 读取记忆文件、查看 skill 模板 |
| `edit_file` | workspace only | 精确编辑 SOUL/USER/MEMORY.md |
| `write_file` | workspace/skills/ only | 创建新 skill |

**工具安全隔离：**

- `write_file` 只允许写入 `skills/` 子目录，无法覆盖核心记忆文件
- `edit_file` 使用精确的 old_text/new_text 替换，不允许全文重写
- Shell 工具被完全排除，Dream 无法执行命令

**编辑规则：**

- 批量同文件修改合并为一次 `edit_file` 调用
- 删除操作：将 section header + 所有 bullets 作为 old_text，new_text 留空
- 不确定是否删除时保留，添加 "(verify currency)" 标记
- Skill 创建前需读取 `skill-creator/SKILL.md` 模板并做去重检查

### 6.4 Prompt 大小控制

为防止 context window 溢出，Phase 1/2 的 prompt 中各文件内容有字符上限：

```python
_MEMORY_FILE_MAX_CHARS = 32_000      # MEMORY.md 预览上限
_SOUL_FILE_MAX_CHARS = 16_000        # SOUL.md 预览上限
_USER_FILE_MAX_CHARS = 16_000        # USER.md 预览上限
_HISTORY_ENTRY_PREVIEW_MAX_CHARS = 4_000  # 每条历史预览上限
```

**注意：** 这些上限仅约束 prompt 中的预览文本。Phase 2 通过 `read_file` 工具仍可读取完整文件。

### 6.5 完整执行流程

```
Dream.run()
│
├── 1. 读取 dream_cursor，获取未处理条目
│      └── entries = store.read_unprocessed_history(since_cursor)
│
├── 2. 截取 batch（max_batch_size 条）
│
├── 3. 构造 Phase 1 输入
│      ├── history_text（每条截断到 4K chars）
│      ├── annotated_memory（git blame 年龄标注 + 32K 上限）
│      ├── current_soul（16K 上限）
│      └── current_user（16K 上限）
│
├── 4. Phase 1: 调用 LLM 分析
│      └── 输出 [FILE] / [FILE-REMOVE] / [SKILL] 清单
│
├── 5. Phase 2: AgentRunner 执行编辑
│      ├── 输入: Phase 1 分析结果 + 文件上下文 + 现有 skill 列表
│      ├── 工具: read_file, edit_file, write_file
│      └── 限制: max_iterations 次工具调用
│
├── 6. 推进 dream_cursor（始终执行，即使失败）
│
├── 7. compact_history()（维持条目上限）
│
└── 8. Git auto-commit（有实际变更时）
       └── commit message 包含分析摘要
```

---

## 7. GitStore：版本控制层

**源码位置：** `nanobot/utils/gitstore.py`

### 7.1 职责

- 使用 [dulwich](https://github.com/dulwich/dulwich)（纯 Python Git 实现）管理内存仓库
- 跟踪 `SOUL.md`、`USER.md`、`memory/MEMORY.md` 三个文件
- 提供 commit log、diff 查看、一键回滚功能

### 7.2 初始化

```
.gitignore 策略：
  /*                    ← 排除所有
  !memory/              ← 允许 memory 目录
  !SOUL.md              ← 允许 SOUL.md
  !USER.md              ← 允许 USER.md
  !memory/MEMORY.md     ← 允许 MEMORY.md
```

**嵌套仓库保护：** 初始化前检查是否已在 Git 仓库内（包括 worktree 和 submodule），避免嵌套。

### 7.3 自动提交

Dream 每次成功运行后调用 `auto_commit()`：

```python
sha = store.git.auto_commit(f"dream: {ts}, {n} change(s)\n\n{analysis}")
```

仅在追踪文件有实际变更时提交，变更信息包含 Phase 1 的分析摘要。

### 7.4 行年龄计算（git blame）

```python
def line_ages(self, file_path: str) -> list[LineAge]:
    annotated = dulwich.porcelain.annotate(workspace, file_path)
    # 每行返回 LineAge(age_days=N)
```

用于 Dream Phase 1 的 MEMORY.md 陈旧度标注。

### 7.5 回滚机制

`revert(commit_sha)` 将所有追踪文件恢复到指定 commit 的父状态，并创建新的安全 commit：

```
HEAD → commit_A → commit_B → revert commit_B (恢复到 commit_A 的状态)
```

---

## 8. Shell 安全集成

**源码位置：** `nanobot/tools/shell.py`

Shell 工具对记忆相关文件实施写入保护：

```python
# 阻止直接写入以下文件
blocked = ["history.jsonl", ".dream_cursor"]
```

这确保只有 Consolidator 和 Dream 通过正规路径修改这些文件，避免外部工具绕过游标机制。

---

## 9. 用户命令接口

**源码位置：** `nanobot/command/builtin.py`

| 命令 | 功能 | 参数 |
|------|------|------|
| `/dream` | 手动触发 Dream 运行 | 无 |
| `/dream-log` | 查看最近一次 Dream 的变更 diff | 可选 `<sha>` 查看特定版本 |
| `/dream-restore` | 列出可回滚版本或执行回滚 | 可选 `<sha>` 回滚到指定版本 |
| `/help` | 帮助中列出 Dream 相关命令 | — |

**`/dream` 执行方式：** 使用 `asyncio.create_task()` 异步执行，立即返回 "Dreaming..." 提示，完成后异步发送结果消息。

---

## 10. 与 AgentLoop 的集成

**源码位置：** `nanobot/agent/loop.py`

```python
# AgentLoop 初始化时创建 Dream 实例
self.dream = Dream(
    store=self.context.memory,
    provider=provider,
    model=self.model,
)
```

**Provider 热更新：** 当模型/provider 运行时切换时，通过 `dream.set_provider()` 同步更新 Dream 的 LLM 配置。

---

## 11. 上下文注入

**源码位置：** `nanobot/agent/context.py:57`

在构建 agent 的 runtime context 时，Dream 未处理的历史条目会作为"近期上下文"注入：

```python
entries = self.memory.read_unprocessed_history(
    since_cursor=self.memory.get_last_dream_cursor()
)
```

这确保 Dream 尚未处理的对话摘要仍可在当前对话中被引用，避免"记忆真空期"。

---

## 12. 关键常量汇总

| 常量 | 值 | 用途 |
|------|----|------|
| `_STALE_THRESHOLD_DAYS` | 14 | MEMORY.md 行年龄陈旧阈值（天） |
| `_HISTORY_ENTRY_HARD_CAP` | 64,000 | history.jsonl 单条最大字符数 |
| `_RAW_ARCHIVE_MAX_CHARS` | 16,000 | 降级原始归档最大字符数 |
| `_ARCHIVE_SUMMARY_MAX_CHARS` | 8,000 | Consolidator LLM 摘要最大字符数 |
| `_MEMORY_FILE_MAX_CHARS` | 32,000 | Dream Phase 1/2 MEMORY.md 预览上限 |
| `_SOUL_FILE_MAX_CHARS` | 16,000 | Dream Phase 1/2 SOUL.md 预览上限 |
| `_USER_FILE_MAX_CHARS` | 16,000 | Dream Phase 1/2 USER.md 预览上限 |
| `_HISTORY_ENTRY_PREVIEW_MAX_CHARS` | 4,000 | Dream Phase 1 单条历史预览上限 |
| `_DEFAULT_MAX_HISTORY` | 1,000 | history.jsonl 最大保留条目数 |
| `_MAX_CONSOLIDATION_ROUNDS` | 5 | Consolidator 单次最大压缩轮数 |
| `_SAFETY_BUFFER` | 1,024 | Token 估算安全余量 |

---

## 13. 数据流图

```
用户消息
  │
  ▼
AgentLoop ───────────────────────────────────────────────────
  │                                                          │
  ├── 响应完成后                                               │
  │   └── Consolidator.maybe_consolidate_by_tokens()         │
  │       ├── 估算当前 prompt token 数                         │
  │       ├── 超预算 → pick_consolidation_boundary()          │
  │       ├── LLM 生成摘要 → append_history()                 │
  │       └── 推进 session.last_consolidated                  │
  │                                                          │
  ├── 定时触发（每 2h）                                        │
  │   └── Dream.run()                                        │
  │       ├── Phase 1: 分析未处理条目                          │
  │       │   ├── 读取 history.jsonl（since dream_cursor）     │
  │       │   ├── 读取 MEMORY.md + git blame 年龄标注         │
  │       │   ├── 读取 SOUL.md, USER.md                      │
  │       │   └── LLM → [FILE] / [FILE-REMOVE] / [SKILL]     │
  │       │                                                   │
  │       ├── Phase 2: 精确编辑                               │
  │       │   ├── AgentRunner + read_file/edit_file/write_file│
  │       │   └── 最大 max_iterations 次工具调用               │
  │       │                                                   │
  │       ├── 推进 dream_cursor                               │
  │       ├── compact_history()                               │
  │       └── Git auto-commit                                │
  │                                                          │
  └── 上下文构建时                                             │
      └── context.py 注入未处理历史到 prompt                   │
```

---

## 14. 错误处理与健壮性

### 14.1 游标始终推进

```python
# 即使 Phase 2 失败，游标仍会推进
new_cursor = batch[-1]["cursor"]
self.store.set_last_dream_cursor(new_cursor)
```

这防止了同一批条目被反复处理导致无限循环。

### 14.2 游标损坏容忍

`_iter_valid_entries()` 过滤非整数 cursor（如被外部工具污染的字符串值），仅记录一次告警：

```python
if isinstance(value, bool) or not isinstance(value, int):
    return None  # 跳过损坏记录
```

### 14.3 模板泄漏过滤

`strip_think()` 在写入 history.jsonl 前清理未闭合的 thinking 标签和 channel 标记。即使过滤后为空，仍写入空记录（避免重新污染上下文）。

### 14.4 Git 操作失败容忍

所有 Git 操作（init、commit、blame、revert）都有 try/except 保护，失败时仅 warning 不中断流程。Git 不可用时 Dream 仍能运行（只是失去版本控制和回滚能力）。

### 14.5 嵌套仓库保护

`_is_inside_git_repo()` 遍历父目录检查是否已在 Git 仓库内，避免创建嵌套仓库。

---

## 15. Legacy 迁移

系统支持从旧版 `HISTORY.md`（纯文本格式）一次性迁移到 `history.jsonl`：

1. 检测 `memory/HISTORY.md` 存在且 `history.jsonl` 不存在/为空
2. 解析旧格式条目（支持 `[timestamp]` 前缀和 `[RAW]` 块）
3. 写入 history.jsonl，初始化两个游标为最后一条的 cursor（避免首次启动回放全部历史）
4. 将旧文件重命名为 `HISTORY.md.bak`（或 `.bak.2`、`.bak.3`...）
