# Redis 性能分析 Playbook

## 适用范围

用于分析 Redis 延迟升高、吞吐下降、CPU 高、连接数异常、慢查询、Hot Key、Big Key、内存淘汰、阻塞命令、网络抖动、主从复制延迟、集群热点分片等问题。

## 第一性原理

Redis 主要使用单线程执行命令。任何长时间命令、大对象读写、热点 key、网络排队、持久化阻塞或内存压力，都可能让后续命令排队，从而放大 P95/P99。

```text
Application
  -> Connection Pool
  -> Redis TCP
  -> Command Queue
  -> Single-thread Command Execution
  -> Memory / Persistence / Replication
```

Redis 慢不等于 Redis 是根因。先确认应用等待 Redis 的耗时是否占请求主要部分。

## 优先证据

1. Trace：Redis span 耗时和命令类型。
2. Redis 指标：latency、ops、CPU、connected_clients、blocked_clients、evicted_keys、used_memory、hit rate、instantaneous_input/output。
3. Redis 命令：`INFO`、`SLOWLOG GET`、`LATENCY LATEST`、`LATENCY DOCTOR`、`CLIENT LIST`、`MEMORY STATS`、`COMMANDSTATS`。
4. Key 诊断：`--hotkeys`、`--bigkeys`、采样扫描结果。生产环境仅在授权后执行可能高开销扫描。
5. Linux/Network：CPU、网卡吞吐、TCP retransmission、连接队列。

## 调查流程

```text
确认 Redis span 或客户端等待变慢
  -> 对齐问题时间窗口
  -> 查询 Redis latency / slowlog / commandstats
  -> 检查连接、阻塞客户端、内存和淘汰
  -> 判断 Hot Key / Big Key / 阻塞命令 / 网络 / 持久化
  -> 检查分片或实例负载是否不均
  -> 用应用 Trace 或日志交叉验证
```

## 常见瓶颈

### Hot Key

证据：

- 单个 key 或少量 key 请求占比异常高。
- Redis 实例 CPU 或网络集中升高。
- 应用 Trace 显示 Redis 等待与热点接口/参数一致。

原理：单 key 被集中访问时，流量无法均匀分摊，单实例或单分片成为瓶颈。

### Big Key

证据：

- 大 value、大 hash/list/set/zset。
- 慢日志出现大对象相关命令。
- 网络输出、内存访问或序列化耗时升高。

原理：大对象命令会占用单线程更久，并增加网络传输和客户端反序列化成本。

### 阻塞命令或慢命令

证据：

- `SLOWLOG GET` 出现 `KEYS`、大范围 `ZRANGE`、`HGETALL`、Lua、聚合命令。
- `LATENCY LATEST` 与 P99 上升时间一致。

原理：长命令占用事件循环，后续命令排队。

### 连接池或客户端问题

证据：

- 应用连接池等待升高。
- Redis `connected_clients`、`blocked_clients` 或客户端超时升高。
- Redis 服务端指标正常但应用等待明显。

原理：瓶颈可能在客户端连接池，而非 Redis 执行。

### 内存淘汰或持久化影响

证据：

- `evicted_keys` 增加、`used_memory` 接近上限。
- RDB/AOF rewrite、fork、磁盘 IO 与延迟时间一致。

原理：内存压力和持久化可能引入额外 CPU、IO 或 fork 开销。

## Root Cause 判定标准

只有满足以下条件之一，才能确认 Redis 为根因：

- Trace 显示 Redis span 占请求主要耗时，且 Redis latency/slowlog 指向同一时间窗口。
- Hot Key/Big Key 证据与实例 CPU、网络或慢日志互相印证。
- 阻塞命令与 P95/P99 上升时间一致。
- Redis 内存淘汰、持久化或复制延迟与业务延迟一致。
- 客户端连接池等待被应用指标和 Redis 连接指标共同证明。

## 优化建议优先级

1. 修复阻塞命令，避免 `KEYS`、大范围读取、无界 `HGETALL`。
2. 拆分 Big Key，限制单次返回大小。
3. Hot Key 本地缓存、读副本、分片打散或 key 维度改造。
4. 调整客户端连接池、超时和重试，避免雪崩式重试。
5. 优化 TTL 和内存策略，减少集中失效。
6. 优化持久化策略或磁盘。
7. 最后再扩容或拆分实例。

## 验证方案

优化后验证：Redis span P95/P99、SLOWLOG 数量、LATENCY、ops、CPU、内存、evicted_keys、connected_clients、blocked_clients、网络吞吐、应用接口 P95/P99、错误率。
