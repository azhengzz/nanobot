# PostgreSQL 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 在性能测试过程中，对 PostgreSQL 数据库进行系统性的性能分析。

适用于：

- SQL 响应慢
- TPS/QPS 不达预期
- API 响应时间增加
- CPU 使用率高
- Lock Wait
- Deadlock
- Seq Scan 过多
- Buffer Cache 命中率下降
- Checkpoint 频繁
- WAL 写入压力大
- Autovacuum 影响性能
- 主备复制延迟

支持：

- PostgreSQL 12+
- PostgreSQL 13
- PostgreSQL 14
- PostgreSQL 15
- PostgreSQL 16
- PostgreSQL 17
- PolarDB PostgreSQL
- CloudNative PostgreSQL

本 Playbook 遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于实时数据验证。

---

# 第一性原理（First Principles）

PostgreSQL 是基于 MVCC（Multi-Version Concurrency Control）的关系型数据库。

一次 SQL 请求通常经历：

```text
Application
      │
      ▼
Connection Pool
      │
      ▼
PostgreSQL Backend Process
      │
      ▼
Parser
      │
      ▼
Planner
      │
      ▼
Executor
      │
      ▼
Shared Buffer
      │
      ▼
Index
      │
      ▼
Heap Table
      │
      ▼
Disk
```

因此：

```
SQL 慢

≠

PostgreSQL 有问题
```

真正耗时可能发生在：

- Planner
- Executor
- Lock
- Shared Buffer
- WAL
- Checkpoint
- Disk IO
- Autovacuum

必须明确：

时间到底耗费在哪一步。

---

# 常见现象（Symptoms）

例如：

- SQL 超过 1 秒
- Seq Scan
- Lock Wait
- Deadlock
- CPU 高
- Shared Buffer Miss
- Checkpoint 频繁
- WAL 写入高
- Autovacuum 长时间运行
- Replication Lag

---

# Agent 调查策略（Investigation Strategy）

收到 PostgreSQL 性能问题时，应首先回答：

1. 哪条 SQL 慢？
2. Planner 是否选择了正确执行计划？
3. 是否发生 Seq Scan？
4. 是否发生 Lock？
5. 是否发生 Autovacuum？
6. Shared Buffer 是否命中？
7. 是否 WAL 或 Checkpoint 成为瓶颈？

如果可以调用：

- psql
- kubectl
- Prometheus
- Shell

应优先获取实时数据。

不要仅因为：

CPU 高

就判断 PostgreSQL 是 Root Cause。

---

# 建议收集的数据（Evidence）

## 数据库版本

执行：

```sql
SELECT version();
```

---

## 当前连接

```sql
SELECT *
FROM pg_stat_activity;
```

关注：

- state
- wait_event
- query_start
- backend_type

---

## 慢 SQL

建议：

启用：

```
pg_stat_statements
```

查询：

```sql
SELECT *
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

---

## 执行计划

执行：

```sql
EXPLAIN
SELECT ...
```

重点关注：

- Seq Scan
- Index Scan
- Bitmap Scan
- Rows
- Actual Time

---

## Lock

执行：

```sql
SELECT *
FROM pg_locks;
```

关联：

```sql
pg_stat_activity
```

分析：

等待关系。

---

## Buffer

执行：

```sql
SELECT
sum(blks_hit),
sum(blks_read)
FROM pg_stat_database;
```

计算：

Buffer Hit Ratio。

---

## WAL

查看：

```sql
SELECT *
FROM pg_stat_wal;
```

关注：

WAL 写入速率。

---

## Checkpoint

执行：

```sql
SELECT *
FROM pg_stat_bgwriter;
```

关注：

- checkpoints_timed
- checkpoints_req

---

## Autovacuum

执行：

```sql
SELECT *
FROM pg_stat_progress_vacuum;
```

分析：

是否正在 Vacuum。

---

# 推荐执行命令（Commands）

查看连接：

```sql
SELECT *
FROM pg_stat_activity;
```

查看锁：

```sql
SELECT *
FROM pg_locks;
```

查看执行计划：

```sql
EXPLAIN
```

查看统计：

```sql
SELECT *
FROM pg_stat_statements;
```

查看 Vacuum：

```sql
SELECT *
FROM pg_stat_progress_vacuum;
```

---

# 推荐分析流程（Workflow）

```text
确认接口响应慢
          │
          ▼
确认 SQL 耗时
          │
          ▼
分析执行计划
          │
          ▼
分析 Lock
          │
          ▼
分析 Shared Buffer
          │
          ▼
分析 WAL
          │
          ▼
分析 Checkpoint
          │
          ▼
分析 Autovacuum
          │
          ▼
确认 Root Cause
```

不要跳过：

EXPLAIN。

---

# 常见瓶颈分析（Analysis）

## Seq Scan

检查：

```sql
EXPLAIN
```

出现：

```
Seq Scan
```

第一性原理：

Planner 认为：

顺序扫描成本最低。

或者：

没有可用索引。

---

## Index Scan

分析：

Rows

是否远超：

预期。

检查：

统计信息是否过期。

---

## Bitmap Scan

分析：

是否由于大量随机访问导致性能下降。

---

## Lock Wait

检查：

```sql
pg_locks
```

分析：

等待链。

确认：

阻塞者。

---

## Deadlock

检查：

日志：

```
deadlock detected
```

分析：

事务顺序。

---

## Shared Buffer

计算：

Hit Ratio。

如果：

命中率下降。

磁盘读取增加。

---

## WAL

检查：

写入速率。

如果：

WAL Flush

耗时增加。

说明：

磁盘可能成为瓶颈。

---

## Checkpoint

检查：

```sql
pg_stat_bgwriter
```

如果：

Checkpoint 过于频繁。

可能导致：

IO 峰值。

---

## Autovacuum

检查：

Vacuum 是否：

持续运行。

分析：

Dead Tuple

是否过多。

---

## Replication Lag

检查：

```sql
SELECT *
FROM pg_stat_replication;
```

关注：

Replay Lag。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认 PostgreSQL 是 Root Cause：

- SQL 耗时占请求主要部分。
- EXPLAIN 证明执行计划存在问题；`EXPLAIN ANALYZE` 会实际执行 SQL，默认不得在只读调查中执行。
- Lock Wait 导致请求阻塞。
- Shared Buffer Miss 导致大量磁盘访问。
- WAL 或 Checkpoint 成为瓶颈。
- Autovacuum 明显影响业务。

否则：

PostgreSQL

只是表现层。

继续分析：

应用、

缓存、

网络。

---

# 常见 Root Cause

包括：

- Seq Scan
- Missing Index
- Lock Wait
- Deadlock
- Shared Buffer Miss
- WAL Flush
- Checkpoint
- Autovacuum
- Replication Lag
- Statistics Outdated

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复 SQL
2. 增加索引
3. 更新统计信息（ANALYZE）
4. 优化事务
5. 调整 Shared Buffer
6. 优化 Checkpoint 参数
7. 调整 Autovacuum
8. 增加资源
9. 扩容数据库

不要首先建议：

升级硬件。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件：

- 已确认 PostgreSQL 不是 Root Cause，应继续分析应用、Redis、Kafka 或网络。
- 已确认 PostgreSQL 是 Root Cause。
- 当前缺少 EXPLAIN、统计信息等关键数据。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

接口 P99 从 600ms 增加到 4s。

---

## 已收集证据（Evidence）

包括：

- pg_stat_activity
- pg_stat_statements
- EXPLAIN
- pg_locks
- Shared Buffer
- WAL
- Checkpoint
- Autovacuum

---

## 分析过程（Reasoning）

说明：

- 是否排除 Lock
- 是否排除 Buffer
- 是否确认执行计划问题

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么 PostgreSQL 内部机制导致当前性能下降。

例如：

```text
Planner 选择 Seq Scan
        │
        ▼
扫描整个 Heap Table
        │
        ▼
Shared Buffer Miss
        │
        ▼
大量磁盘读取
        │
        ▼
SQL 响应时间增加
```

---

## 优化建议（Recommendations）

按优先级排序。

---

## 验证方案（Validation Plan）

优化完成后，应验证：

- SQL Response Time
- TPS
- Avg
- P95
- P99
- Seq Scan 次数
- Buffer Hit Ratio
- Lock Wait
- WAL 写入
- Checkpoint
- CPU
- Disk IO

确认 PostgreSQL 优化是否真正改善性能。
