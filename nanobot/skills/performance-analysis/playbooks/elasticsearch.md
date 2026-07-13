# Elasticsearch 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 对 Elasticsearch 在性能测试过程中的性能问题进行调查与分析。

适用于：

- Search 查询性能下降
- Index 写入性能下降
- Bulk 导入速度低
- P95 / P99 响应时间增加
- 集群 CPU、Memory、Disk 使用率异常
- Hot Node
- Hot Shard
- Thread Pool Reject
- Merge / Refresh 导致性能下降
- JVM GC 导致延迟增加

本 Playbook 遵循**第一性原理**和**证据驱动分析**。

所有 Root Cause 必须通过实时数据验证，不允许凭经验直接推断。

---

# 第一性原理（First Principles）

Elasticsearch 的一次查询，本质上经历以下路径：

```text
Client
    │
    ▼
HTTP Request
    │
    ▼
Coordinating Node
    │
    ▼
Shard Routing
    │
    ▼
Primary / Replica Shard
    │
    ▼
Lucene Segment
    │
    ▼
Filesystem Cache
    │
    ▼
Disk
```

一次写入请求则经历：

```text
Client
    │
    ▼
Bulk API
    │
    ▼
Primary Shard
    │
    ▼
Translog
    │
    ▼
Refresh
    │
    ▼
Segment
    │
    ▼
Merge
```

性能问题最终都会落到以下几个环节：

- 查询复杂度
- Shard 路由
- Lucene 执行
- JVM
- Thread Pool
- Merge
- Refresh
- Disk IO
- Network

Agent 应分析请求慢在哪一层，而不是直接怀疑 Elasticsearch。

---

# 常见现象（Symptoms）

例如：

- Search 响应时间增加
- Bulk 写入变慢
- Search Timeout
- Thread Pool Reject
- JVM Heap 使用率高
- GC 时间增加
- CPU 持续高
- Disk IO 高
- Hot Node
- Hot Shard
- Cluster Health Yellow / Red

---

# Agent 调查策略（Investigation Strategy）

收到 Elasticsearch 性能问题时，应优先回答：

1. 是查询慢还是写入慢？
2. 是整个集群慢，还是部分节点慢？
3. 是单个索引慢，还是整个集群慢？
4. 是否属于 Elasticsearch 自身问题？
5. 是否实际上是磁盘、网络或 JVM 导致？

如果存在 MCP、Shell 或 Elasticsearch API，应优先获取实时数据。

不要根据历史经验直接推断：

- JVM
- Merge
- GC
- Query

---

# 建议收集的数据（Evidence）

## 集群健康

```http
GET /_cluster/health

GET /_cluster/stats

GET /_cat/nodes?v

GET /_cat/shards?v

GET /_cat/indices?v
```

关注：

- Cluster Status
- Active Shards
- Unassigned Shards
- Node Count

---

## 节点状态

```http
GET /_nodes/stats

GET /_nodes/hot_threads
```

关注：

- CPU
- Heap
- GC
- Filesystem
- Transport
- HTTP

---

## Thread Pool

```http
GET /_cat/thread_pool?v
```

关注：

- search
- write
- bulk
- refresh
- merge

重点查看：

- active
- queue
- rejected

---

## 查询分析

```http
GET index/_search/profile
```

关注：

- Took
- Query Phase
- Fetch Phase

---

## Slow Log

收集：

- Search Slow Log
- Index Slow Log

关注：

- Query Time
- Fetch Time
- Aggregation

---

## Segment

```http
GET /_cat/segments?v
```

关注：

- Segment 数量
- Deleted Docs
- Segment Size

---

## JVM

```http
GET /_nodes/stats/jvm
```

关注：

- Heap
- Young GC
- Old GC
- Memory Pressure

---

## Linux

建议同时收集：

```bash
iostat -x

vmstat

pidstat

sar -d
```

关注：

- Disk Util
- IO Wait
- Await

---

# 推荐执行命令（Commands）

## Cluster

```bash
curl http://ES:9200/_cluster/health?pretty
```

---

## Nodes

```bash
curl http://ES:9200/_cat/nodes?v
```

---

## Shards

```bash
curl http://ES:9200/_cat/shards?v
```

---

## Thread Pool

```bash
curl http://ES:9200/_cat/thread_pool?v
```

---

## Hot Threads

```bash
curl http://ES:9200/_nodes/hot_threads
```

---

## Profile API

```bash
curl http://ES:9200/index/_search?profile=true
```

---

# 推荐分析流程（Workflow）

```text
确认问题类型
（Search / Index）
        │
        ▼
检查 Cluster Health
        │
        ▼
检查 Node Resource
        │
        ▼
检查 Thread Pool
        │
        ▼
检查 Slow Log
        │
        ▼
检查 Profile API
        │
        ▼
检查 Shard
        │
        ▼
检查 JVM
        │
        ▼
检查 Disk IO
        │
        ▼
确认 Root Cause
```

不要跳过步骤。

---

# 常见瓶颈分析（Analysis）

## 查询慢

检查：

- Search Slow Log
- Profile API

重点关注：

- Wildcard Query
- Regexp Query
- Script Query
- Aggregation
- Deep Pagination

第一性原理：

复杂查询需要扫描更多倒排索引、Doc Values 或进行大量聚合计算，因此 CPU 和磁盘访问增加，导致响应时间上升。

---

## 写入慢

检查：

- Bulk Size
- Refresh
- Merge

第一性原理：

写入最终需要生成新的 Segment，并在后台进行 Merge。

Merge 会消耗大量磁盘 IO。

---

## Hot Node

检查：

- Node CPU
- Heap
- Search Rate
- Index Rate

说明：

某一节点负载远高于其它节点。

---

## Hot Shard

检查：

```http
GET /_cat/shards?v
```

说明：

热点请求集中访问某个 Shard。

---

## Thread Pool Reject

检查：

```http
GET /_cat/thread_pool?v
```

重点关注：

- queue
- rejected

Reject 持续增加说明请求处理能力已经不足。

---

## Merge

检查：

Merge Time

Merge Count

Merge 是否长期运行。

---

## Refresh

检查：

refresh_interval

是否频繁 Refresh。

---

## JVM

检查：

- Heap
- Old GC
- Full GC

重点分析：

是否 Memory Pressure 导致 GC。

---

## Disk IO

检查：

Linux：

```bash
iostat -x

sar -d
```

重点分析：

- util
- await
- IO Wait

Lucene 最终依赖磁盘。

磁盘 IO 饱和最终会导致：

- Search
- Merge
- Refresh

全部变慢。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件之一，才能确认 Root Cause：

- Search Slow Log 与响应时间一致，并通过 Profile API 定位到具体查询。
- Thread Pool Reject 与请求量增长具有明确因果关系。
- Hot Node / Hot Shard 与请求热点一致。
- Merge、Refresh、GC 或 Disk IO 与性能下降时间完全一致。
- Cluster Health 异常直接导致请求失败。

如果只有 CPU 高或 Heap 高，而没有进一步证据：

只能作为 Hypothesis。

不得确认 Root Cause。

---

# 常见 Root Cause

包括但不限于：

- Wildcard Query
- Regexp Query
- Deep Pagination
- 大 Aggregation
- Hot Node
- Hot Shard
- Thread Pool Reject
- Merge 压力过大
- Refresh 频繁
- Segment 过多
- Heap 不足
- Full GC
- Disk IO 饱和

Root Cause 必须结合证据确认。

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 优化 Query DSL
2. 优化索引 Mapping
3. 调整 Shard 数量
4. 调整 Bulk Size
5. 调整 Refresh Interval
6. 优化 JVM Heap
7. 调整 Thread Pool（确认必要时）
8. 调整磁盘性能
9. 扩容节点

不要默认建议扩容。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件，应结束 Elasticsearch 分析：

- 已确认 Elasticsearch 不是瓶颈，应继续分析网络、应用或其它组件。
- 已确认 Elasticsearch 是 Root Cause。
- 当前证据不足，需要用户补充数据。
- 已无法继续分析，应停止推断并说明原因。

不要无限停留在 Elasticsearch 层。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

## 已收集证据（Evidence）

## 分析过程（Reasoning）

说明：

- 为什么排除了其它原因
- 为什么锁定 Elasticsearch
- 为什么确认当前 Root Cause

## 根因（Root Cause）

必须提供证据。

## 第一性原理解释

解释为什么该问题一定会导致性能下降。

## 优化建议（Recommendations）

按优先级排序。

## 验证方案（Validation Plan）

优化完成后，应验证：

- Search Latency
- Index Latency
- P95 / P99
- Thread Pool Reject
- Heap
- GC
- Disk IO
- Cluster Health

确认优化是否达到预期效果。