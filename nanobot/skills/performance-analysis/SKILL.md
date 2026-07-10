---
name: performance-analysis
description: Diagnose performance problems during performance testing using first-principles reasoning. Analyze performance test results, metrics, logs, traces, thread dumps, heap dumps, GC logs, infrastructure metrics, and middleware behavior to identify bottlenecks, validate root causes with evidence, and recommend optimization actions.
---

# 性能分析（Performance Analysis）

## 概述

本 Skill 用于指导 AI 在性能测试过程中，采用**第一性原理（First Principles）**和**证据驱动（Evidence-based Reasoning）**的方法分析性能问题，逐层定位系统瓶颈，建立完整的证据链，并输出具有依据的根因分析和优化建议。

本 Skill 的目标不是快速猜测问题，而是通过系统化分析，回答：

- 性能为什么下降？
- 时间消耗在哪里？
- 哪个组件是真正的瓶颈？
- 为什么它会成为瓶颈？
- 有哪些证据能够证明？
- 如何优化？
- 如何验证优化方案？

适用于：

- Kubernetes
- 微服务架构
- Java / Go / Python 等应用
- JVM
- Linux
- Nginx / API Gateway
- MySQL
- PostgreSQL
- Redis
- Kafka
- Elasticsearch
- MinIO
- 网络分析
- 云原生基础设施

本 Skill **不是某个中间件的排查手册**，而是一套通用的性能诊断框架。

---

# 核心分析原则（Core Analysis Principles）

## 原则一：第一性原理

任何性能问题，都必须回归请求生命周期进行分析，而不是直接怀疑某个组件。

不要凭经验下结论。

禁止：

- 一看到响应慢就怀疑数据库
- 一看到 CPU 高就认为 CPU 是瓶颈
- 一看到 Full GC 就认为 GC 导致问题
- 没有证据就开始优化

所有结论必须建立在事实和证据基础上。

---

## 原则二：逐层分析

性能问题必须按照请求路径逐层分析。

```
Client
    ↓
Gateway
    ↓
Application
    ↓
Runtime
    ↓
Middleware
    ↓
Database
    ↓
Operating System
    ↓
Network
```

对于每一层，都需要回答：

- 是否存在性能问题？
- 是否存在证据？
- 是否可以排除？
- 是否需要继续深入？

不要跳层分析。

---

## 原则三：数据驱动

所有分析必须基于数据，而不是经验。

数据来源包括：

- Performance Test Report
- Metrics
- Logs
- Trace
- Thread Dump
- Heap Dump
- GC Log
- SQL Slow Log
- EXPLAIN
- pprof
- Flame Graph
- tcpdump
- perf
- eBPF

---

## 原则四：因果验证

相关性（Correlation）不等于因果关系（Causation）。

必须证明完整因果链：

```
问题发生
    ↓
性能下降
    ↓
发现瓶颈
    ↓
验证瓶颈
    ↓
解释原理
    ↓
确认根因
```

所有假设必须验证。

---

## 原则五：证据不足时不猜测

如果证据不足，不应输出确定性的根因。

应明确说明：

当前证据不足。

建议补充：

- Thread Dump
- Heap Dump
- GC Log
- SQL Slow Log
- Trace
- Prometheus Metrics
- pprof

严禁没有证据进行推测。

---

# 安全原则（Safety Rules）

默认采用**只读分析（Read-Only Analysis）**。

未经用户明确授权，Agent 不应主动：

- 发起压力测试
- 修改配置
- 修改 Kubernetes 资源
- 重启服务
- 扩容或缩容
- 执行数据库变更
- 清理缓存
- 删除数据
- 执行任何可能影响业务稳定性的操作

Agent 应提供验证方案，由用户决定是否执行。

---

# 性能分析流程

所有性能问题统一采用以下流程。

```
问题确认
      ↓
时间对齐
      ↓
收集证据
      ↓
逐层分析
      ↓
定位瓶颈
      ↓
验证根因
      ↓
提出优化建议
      ↓
制定验证方案
```

禁止跳过步骤。

---

# 第一步：问题确认

开始分析前，必须收集完整背景信息。

包括：

- 测试场景
- 测试目标
- API
- 并发数
- TPS / QPS
- Avg
- P95
- P99
- Error Rate
- 测试时间
- Kubernetes Namespace
- Deployment
- Pod 数量
- CPU / Memory Limit
- 应用版本
- 部署架构

---

# 第二步：时间对齐

时间对齐是性能分析的基础。

必须确认：

- Kubernetes
- JVM
- Linux
- MySQL
- PostgreSQL
- Redis
- Kafka
- Elasticsearch
- Prometheus

统一转换为同一时间轴。

否则无法判断因果关系。

---

# 第三步：收集证据

## 性能测试

分析：

- TPS
- QPS
- Avg
- P50
- P90
- P95
- P99
- Error Rate

---

## 监控

分析：

- CPU
- Memory
- Disk IO
- Network
- Load Average
- Context Switch
- TCP Connection
- Node Resource
- Pod Resource

---

## 日志

分析：

- Application Log
- Gateway Log
- Error Log
- Slow Log
- Audit Log

---

## 调用链

分析：

- Trace
- Span Duration
- Retry
- Timeout
- Service Dependency

---

# 第四步：逐层分析

默认按照以下顺序分析。

```
客户端
    ↓
负载均衡
    ↓
API Gateway
    ↓
应用服务
    ↓
JVM / Runtime
    ↓
Redis
    ↓
Kafka
    ↓
MySQL / PostgreSQL
    ↓
Elasticsearch
    ↓
MinIO
    ↓
Linux
    ↓
Kubernetes
    ↓
Network
```

每一层都需要分析：

- 是否耗时
- 是否存在瓶颈
- 是否有证据
- 是否可以排除

---

# 客户端分析

分析：

- 并发数
- 请求速率
- Think Time
- Connection Reuse
- DNS

重点关注：

- 压测机是否成为瓶颈
- 网络是否正常
- 参数配置是否合理

---

# Gateway 分析

分析：

- Access Log
- Upstream Response Time
- Request Queue
- Connection Count

重点关注：

- Gateway Latency
- Retry
- Timeout
- Rate Limiting

---

# 应用分析

分析：

- 应用日志
- Thread Pool
- Connection Pool
- Async Queue
- Business Metrics

重点关注：

- Thread Blocking
- Lock Contention
- Connection Pool
- 热点接口

---

# JVM 分析

分析：

- Thread Dump
- Heap Dump
- GC Log
- JFR

重点关注：

- Full GC
- Allocation Rate
- Safepoint
- Thread Blocking
- Memory Leak

---

# Redis 分析

分析：

- INFO
- SLOWLOG
- LATENCY
- MEMORY
- CLIENT LIST

重点关注：

- Hit Ratio
- Hot Key
- Big Key
- Blocked Clients
- Replication Delay
- Memory Fragmentation
- Evicted Keys

典型问题：

- Hot Key
- Big Key
- Lua Script
- 网络延迟
- 主从同步延迟

---

# Kafka 分析

分析：

- Consumer Lag
- Broker Metrics
- ISR
- Produce Latency
- Fetch Latency
- Request Queue

重点关注：

- Consumer Lag
- Replication
- Leader Election
- Disk IO
- Batch Size
- Compression
- Retry

典型问题：

- Consumer 积压
- Broker IO
- ISR Shrink
- 磁盘瓶颈

---

# MySQL 分析

分析：

- Slow Query Log
- EXPLAIN
- SHOW PROCESSLIST
- SHOW ENGINE INNODB STATUS
- Performance Schema

重点关注：

- Full Table Scan
- Index Usage
- Lock Wait
- Buffer Pool
- Connection Pool
- Deadlock

典型问题：

- LIKE '%keyword%'
- 缺少索引
- Temporary Table
- Filesort
- 大 OFFSET

---

# PostgreSQL 分析

分析：

- pg_stat_activity
- pg_stat_statements
- EXPLAIN ANALYZE
- Wait Event
- Lock

重点关注：

- Seq Scan
- Index Scan
- Buffer Hit Ratio
- Autovacuum
- Checkpoint
- Dead Tuple

---

# Elasticsearch 分析

分析：

- Search Slow Log
- Index Slow Log
- JVM
- Thread Pool
- Segment
- Cluster Health

重点关注：

- Hot Node
- Hot Shard
- Query Cache
- Merge
- Refresh
- Fielddata
- Circuit Breaker

典型问题：

- Wildcard Query
- Deep Pagination
- 大聚合
- 热点分片

---

# MinIO 分析

分析：

- S3 API Metrics
- Disk Metrics
- Network Metrics
- Healing Status

重点关注：

- PUT Latency
- GET Latency
- Multipart Upload
- Small Object
- Erasure Coding
- Disk Bandwidth
- Network Throughput

典型问题：

- Small Object Storm
- 慢磁盘
- 网络瓶颈
- Healing

---

# Linux 分析

分析：

- top
- vmstat
- iostat
- pidstat
- sar
- ss
- netstat

重点关注：

- CPU
- Context Switch
- IO Wait
- Disk Busy
- Interrupt
- NUMA

---

# Kubernetes 分析

分析：

- Pod
- Node
- Event
- Resource Usage
- PVC
- NetworkPolicy

重点关注：

- CPU Throttling
- OOMKill
- Pod Restart
- Node Pressure
- Resource Limit
- Affinity
- Taints

---

# 网络分析

分析：

- RTT
- Packet Loss
- Retransmission
- DNS
- TCP Connection

重点关注：

- TCP Retransmission
- Socket Backlog
- SYN Queue
- MTU
- Firewall

---

# 根因验证

瓶颈不等于根因。

必须完成验证。

例如：

```
HTTP 响应慢
      ↓
SQL 耗时增加
      ↓
EXPLAIN Full Scan
      ↓
LIKE '%keyword%'
      ↓
无法使用 B+Tree 索引
      ↓
全表扫描
      ↓
CPU 消耗增加
      ↓
SQL 延迟增加
      ↓
HTTP 延迟增加
      ↓
确认根因
```

每个根因必须包含：

- 证据
- 验证过程
- 第一性原理解释
- 优化建议

---

# 优化建议

所有建议按照优先级输出：

1. 修复根因
2. 配置优化
3. 参数优化
4. 资源调整
5. 架构优化

不要默认建议扩容。

---

# 输出规范

每次分析结果必须包含以下内容：

## 1. 问题现象（Symptoms）

描述用户反馈的问题及影响范围。

---

## 2. 已收集证据（Evidence）

列出分析过程中使用的数据、日志、监控和诊断信息。

---

## 3. 分析过程（Reasoning）

按照时间线和请求链路说明分析过程。

明确说明：

- 已排除哪些组件
- 为什么继续分析
- 为什么锁定某个组件

---

## 4. 根因（Root Cause）

说明真正原因，并提供证据。

---

## 5. 第一性原理解释

解释：

为什么该问题一定会导致性能下降。

---

## 6. 优化建议（Recommendations）

按照优先级排序。

说明每条建议的原因。

---

## 7. 风险评估（Risk Assessment）

说明：

- 是否存在风险
- 是否影响业务
- 是否需要停机
- 是否需要回滚方案

---

## 8. 验证方案（Validation Plan）

提供验证步骤。

默认只提供方案。

未经用户明确授权，不主动执行任何可能影响系统稳定性的操作。

---

# 常见误区（Anti-Patterns）

| 错误方式 | 推荐方式 |
|-----------|----------|
| 凭经验判断瓶颈 | 基于证据分析 |
| 不分析请求链路 | 按照请求生命周期逐层分析 |
| 只看平均响应时间 | 同时分析 P95、P99 |
| 只分析一个组件 | 分析完整调用路径 |
| 不查看日志 | 指标 + 日志 + Trace 联合分析 |
| 不做时间对齐 | 所有数据统一时间轴 |
| CPU 高立即扩容 | 找到 CPU 高的真正原因 |
| 没验证就优化 | 每个假设都必须验证 |
| 证据不足仍下结论 | 明确说明需要补充哪些数据 |

---

# 黄金法则（Golden Rules）

1. 证据优于经验。
2. 时间轴优于猜测。
3. 逐层分析优于局部分析。
4. 数据优于假设。
5. 相关性不等于因果关系。
6. 每一个结论都必须能够证明。
7. 每一个瓶颈都必须能够解释其原理。
8. 找到根因，再考虑优化。
9. 默认只读分析，不主动执行可能影响系统稳定性的操作。
10. 提供验证方案，由用户决定是否执行。