# MySQL 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 在性能测试过程中，对 MySQL 数据库进行系统性的性能分析。

适用于：

- SQL 响应慢
- TPS/QPS 不达预期
- API 响应时间增加
- 慢查询增多
- CPU 高
- Buffer Pool 命中率下降
- Lock Wait
- Deadlock
- Connection 数过多
- IO 等待高
- 主从复制延迟

支持：

- MySQL 5.7
- MySQL 8.x
- Percona Server
- MariaDB（大部分适用）
- PolarDB MySQL
- TDSQL MySQL
- Aurora MySQL

本 Playbook 遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于实时数据验证。

---

# 第一性原理（First Principles）

数据库不是计算系统，而是数据访问系统。

一次 SQL 请求通常经历：

```text
Application
      │
      ▼
Connection Pool
      │
      ▼
MySQL Connection
      │
      ▼
Parser
      │
      ▼
Optimizer
      │
      ▼
Execution Engine
      │
      ▼
Buffer Pool
      │
      ▼
Index
      │
      ▼
Disk
```

因此：

```
SQL 慢

≠

MySQL 有问题
```

真正耗时可能发生在：

- Connection Pool
- Lock
- Optimizer
- Index
- Disk IO
- Buffer Pool
- Network

必须回答：

SQL 为什么慢？

时间耗费在哪一步？

---

# 常见现象（Symptoms）

例如：

- SQL 超过 1 秒
- 慢查询数量增加
- P95/P99 增高
- CPU 持续高
- Lock Wait
- Deadlock
- Buffer Pool Miss
- Filesort
- Temporary Table
- Full Table Scan
- IO Wait 高

---

# Agent 调查策略（Investigation Strategy）

收到 MySQL 性能问题时，应首先回答：

1. 是哪条 SQL 慢？
2. SQL 是否真的占用了请求的大部分时间？
3. 是否发生锁等待？
4. 是否走索引？
5. 是否发生全表扫描？
6. 是否 Buffer Pool 不足？
7. 是否磁盘 IO 成为瓶颈？

如果可以调用：

- mysql
- kubectl
- Prometheus
- Shell

应优先获取实时数据。

不要看到：

CPU 高

就直接认为：

MySQL 是 Root Cause。

---

# 建议收集的数据（Evidence）

## 数据库基本信息

执行：

```sql
SELECT VERSION();

SHOW VARIABLES LIKE 'version%';

SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
```

---

## 当前连接

```sql
SHOW FULL PROCESSLIST;
```

关注：

- Sleep
- Query
- Locked
- Waiting

---

## 慢查询配置

```sql
SHOW VARIABLES LIKE 'slow_query_log';

SHOW VARIABLES LIKE 'long_query_time';
```

确认：

慢日志是否开启。

---

## 慢查询日志

建议分析：

- Query Time
- Lock Time
- Rows Examined
- Rows Sent

重点：

Rows Examined

远大于

Rows Sent

通常意味着：

扫描过多。

---

## EXPLAIN

执行：

```sql
EXPLAIN
SELECT ...
```

重点关注：

- type
- rows
- key
- possible_keys
- filtered
- Extra

尤其：

```
ALL

Using Filesort

Using Temporary
```

---

## InnoDB

执行：

```sql
SHOW ENGINE INNODB STATUS;
```

关注：

- Lock
- Deadlock
- Buffer Pool
- Semaphore

---

## Buffer Pool

```sql
SHOW GLOBAL STATUS
LIKE 'Innodb_buffer_pool%';
```

重点：

- Read Requests
- Reads

计算：

Hit Ratio。

---

## Connection

执行：

```sql
SHOW STATUS LIKE 'Threads%';

SHOW STATUS LIKE 'Max_used_connections';
```

关注：

连接是否耗尽。

---

## Performance Schema

建议分析：

- Top SQL
- Wait Event
- IO
- Lock

---

# 推荐执行命令（Commands）

查看连接：

```sql
SHOW FULL PROCESSLIST;
```

查看锁：

```sql
SHOW ENGINE INNODB STATUS;
```

查看变量：

```sql
SHOW VARIABLES;
```

查看状态：

```sql
SHOW GLOBAL STATUS;
```

查看执行计划：

```sql
EXPLAIN
```

查看统计：

```sql
ANALYZE TABLE
```

注意：`ANALYZE TABLE` 可能修改统计信息并影响线上执行计划，默认不得执行；仅在用户明确授权后作为优化或验证动作。

---

# 推荐分析流程（Workflow）

```text
确认接口响应慢
          │
          ▼
确认 SQL 耗时
          │
          ▼
分析慢查询
          │
          ▼
执行 EXPLAIN
          │
          ▼
分析 Buffer Pool
          │
          ▼
分析 Lock
          │
          ▼
分析磁盘 IO
          │
          ▼
确认 Root Cause
```

不要跳过：

EXPLAIN。

---

# 常见瓶颈分析（Analysis）

## Full Table Scan

检查：

EXPLAIN：

```
type = ALL
```

第一性原理：

没有利用索引。

必须扫描全部数据。

---

## Full Index Scan

检查：

rows

非常大。

原因：

例如：

```sql
LIKE '%keyword%'
```

第一性原理：

B+Tree 无法定位前缀。

只能扫描。

---

## Filesort

检查：

Extra：

```
Using Filesort
```

说明：

排序无法利用索引。

---

## Temporary Table

检查：

```
Using Temporary
```

第一性原理：

需要额外建立临时表。

增加：

CPU

IO

Memory

开销。

---

## Lock Wait

检查：

```sql
SHOW ENGINE INNODB STATUS;
```

关注：

Waiting。

分析：

谁阻塞谁。

---

## Deadlock

检查：

LATEST DETECTED DEADLOCK

分析：

事务顺序。

---

## Buffer Pool Miss

检查：

Hit Ratio。

如果：

磁盘读取明显增加。

说明：

缓存命中率下降。

---

## Connection Pool

检查：

Threads Connected。

Max Used Connections。

分析：

是否达到连接上限。

---

## Disk IO

检查：

Linux：

```bash
iostat -x
```

重点：

- await
- util

---

## Optimizer

检查：

EXPLAIN。

分析：

为什么：

选择了错误索引。

是否需要：

```sql
ANALYZE TABLE
```

更新统计信息。

默认只读调查阶段不得执行 `ANALYZE TABLE`；如果怀疑统计信息问题，应先用 `EXPLAIN`、慢日志和现有统计视图说明证据缺口。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认 MySQL 是 Root Cause：

- SQL 耗时占请求时间主要部分。
- EXPLAIN 证明执行计划存在问题。
- Lock Wait 导致请求阻塞。
- Buffer Pool Miss 导致大量磁盘访问。
- Disk IO 与 SQL 延迟一致。
- Connection Pool 已耗尽。

否则：

MySQL

只是现象。

继续分析：

应用、

缓存、

网络。

---

# 常见 Root Cause

包括：

- Full Table Scan
- Full Index Scan
- LIKE '%keyword%'
- Filesort
- Temporary Table
- Lock Wait
- Deadlock
- Missing Index
- Buffer Pool 不足
- Disk IO
- Connection Exhaustion

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复 SQL
2. 修复索引
3. 更新统计信息
4. 减少扫描数据量
5. 优化事务
6. 调整 Buffer Pool
7. 调整连接池
8. 增加资源
9. 扩容数据库

不要首先建议：

增加数据库节点。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件：

- 已确认 MySQL 不是 Root Cause，应继续分析应用、Redis、Kafka 或网络。
- 已确认 MySQL 是 Root Cause。
- 当前缺少慢查询日志、EXPLAIN 等关键数据。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

接口 P99 从 800ms 增加到 6s。

---

## 已收集证据（Evidence）

包括：

- Slow Log
- EXPLAIN
- Processlist
- Buffer Pool
- Lock
- Disk IO

---

## 分析过程（Reasoning）

说明：

- 是否排除锁等待
- 是否排除 Buffer Pool
- 是否确认 SQL 执行计划问题

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么 MySQL 内部机制导致当前性能下降。

例如：

```
LIKE '%keyword%'
        │
        ▼
无法利用 B+Tree 前缀索引
        │
        ▼
Full Index Scan
        │
        ▼
Rows Examined 急剧增加
        │
        ▼
CPU、IO 增加
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
- Rows Examined
- Rows Sent
- Buffer Pool Hit Ratio
- Lock Wait
- Deadlock
- CPU
- Disk IO

确认 MySQL 优化是否真正改善性能。
