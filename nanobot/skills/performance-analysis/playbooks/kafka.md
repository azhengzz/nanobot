# Kafka 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 对 Apache Kafka 在性能测试过程中的性能问题进行调查和分析。

适用于：

- Producer 发送慢
- Consumer 消费慢
- Consumer Lag 持续增长
- TPS 不达预期
- 消息堆积
- Broker CPU 高
- Broker 磁盘 IO 高
- 网络带宽不足
- ISR 缩减（ISR Shrink）
- Leader 频繁切换
- Request Timeout
- Produce Latency 高
- Fetch Latency 高

本 Playbook遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于实时数据验证。

---

# 第一性原理（First Principles）

Kafka 本质上是一个顺序追加（Append Only）的分布式日志系统。

消息生命周期：

```text
Producer
      │
      ▼
Network
      │
      ▼
Broker
      │
      ▼
Partition
      │
      ▼
Leader
      │
      ▼
Disk
      │
      ▼
Replica
      │
      ▼
Consumer
```

性能问题最终通常发生在：

- Producer
- Network
- Broker
- Disk
- Replica
- Consumer

不要直接认为：

- Kafka 慢
- Broker CPU 高
- Consumer Lag

就是 Root Cause。

必须分析：

消息到底在哪个阶段变慢。

---

# 常见现象（Symptoms）

例如：

- Produce Latency 增加
- Fetch Latency 增加
- Consumer Lag 增长
- Producer Timeout
- Broker CPU 高
- Broker Memory 高
- Broker Disk Busy
- ISR Shrink
- Leader Election
- Request Queue 增长
- TPS 下降

---

# Agent 调查策略（Investigation Strategy）

收到 Kafka 性能问题时，应首先回答：

1. Producer 是否发送缓慢？
2. Broker 是否处理缓慢？
3. Consumer 是否消费缓慢？
4. 是否发生 ISR Shrink？
5. 是否发生 Leader Election？
6. 是否是磁盘瓶颈？
7. 是否是网络瓶颈？

如果可以调用：

- kafka-topics.sh
- kafka-consumer-groups.sh
- kafka-configs.sh
- kafka-broker-api-versions.sh
- JMX
- Prometheus
- Shell

应优先获取实时数据。

不要因为：

Consumer Lag

就直接判断 Consumer 有问题。

---

# 建议收集的数据（Evidence）

## Broker Metrics

建议收集：

- Broker CPU
- Broker Memory
- Disk Usage
- Disk IO
- Network Throughput

重点关注：

- Request Handler Idle
- Network Processor Idle
- Request Queue
- Response Queue

---

## Producer Metrics

建议收集：

- Produce Rate
- Produce Latency
- Batch Size
- Compression Ratio
- Retry Count
- Record Error Rate

---

## Consumer Metrics

建议收集：

- Consume Rate
- Fetch Latency
- Consumer Lag
- Commit Latency
- Rebalance Count

---

## Topic 信息

建议执行：

```bash
kafka-topics.sh --describe --topic <topic> --bootstrap-server <broker>
```

关注：

- Partition
- Replication Factor
- ISR
- Leader

---

## Consumer Group

建议执行：

```bash
kafka-consumer-groups.sh \
--describe \
--group <group> \
--bootstrap-server <broker>
```

重点关注：

- Current Offset
- Log End Offset
- Lag

---

## Broker JMX

建议收集：

- Request Queue
- Produce Request Time
- Fetch Request Time
- Network
- Disk

---

## Linux

建议收集：

```bash
iostat -x

vmstat

pidstat

sar -n DEV
```

重点关注：

- util
- await
- IO Wait
- Network

---

# 推荐执行命令（Commands）

## 查看 Topic

```bash
kafka-topics.sh \
--describe \
--bootstrap-server <broker>
```

---

## 查看 Consumer Lag

```bash
kafka-consumer-groups.sh \
--describe \
--group <group> \
--bootstrap-server <broker>
```

---

## 查看 Broker 配置

```bash
kafka-configs.sh \
--bootstrap-server <broker> \
--entity-type brokers
```

---

## 查看 Broker API

```bash
kafka-broker-api-versions.sh \
--bootstrap-server <broker>
```

---

## Linux

```bash
iostat -x

sar -n DEV

vmstat
```

---

# 推荐分析流程（Workflow）

```text
确认问题
（Producer / Consumer）
          │
          ▼
检查 Broker 状态
          │
          ▼
检查 Topic
          │
          ▼
检查 Consumer Lag
          │
          ▼
检查 ISR
          │
          ▼
检查磁盘 IO
          │
          ▼
检查网络
          │
          ▼
确认 Root Cause
```

不要跳过步骤。

---

# 常见瓶颈分析（Analysis）

## Producer 延迟高

检查：

- Batch Size
- Compression
- Retry
- Produce Latency

第一性原理：

Producer 需要等待：

- 网络
- Broker
- ACK

任一阶段变慢都会增加发送延迟。

---

## Consumer Lag

检查：

```text
Current Offset

↓

Log End Offset

↓

Lag
```

进一步分析：

Consumer：

到底是：

消费速度慢

还是：

Producer 写入过快。

Lag 只是现象。

---

## Broker CPU 高

检查：

- CPU
- Request Queue
- Thread Pool

进一步分析：

CPU：

到底消耗在哪里。

不要直接扩容。

---

## Broker Disk IO

检查：

```bash
iostat -x
```

关注：

- util
- await
- IO Wait

第一性原理：

Kafka 所有消息最终落盘。

磁盘性能决定：

写入吞吐。

---

## ISR Shrink

检查：

Topic：

ISR。

分析：

为什么：

Follower 无法及时同步。

可能原因：

- 网络
- 磁盘
- CPU

---

## Leader Election

检查：

Controller Log。

分析：

Leader 是否频繁切换。

第一性原理：

Leader 切换期间：

请求可能失败。

---

## Network

检查：

```bash
sar -n DEV

netstat -s
```

重点：

- Retransmission
- Throughput
- RTT

---

## Batch Size

检查：

Producer：

batch.size

linger.ms

第一性原理：

Batch 太小：

网络利用率低。

Batch 太大：

延迟增加。

---

## Compression

检查：

compression.type。

分析：

CPU：

是否因为压缩升高。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认 Kafka 是 Root Cause：

- Consumer Lag 与 Consumer Processing Rate 不匹配。
- Produce Latency 与 Broker Request Queue 一致。
- ISR Shrink 与网络或磁盘异常一致。
- Leader Election 导致请求失败。
- Broker Disk IO 饱和。
- Request Queue 长时间积压。

否则：

只能作为：

Hypothesis。

---

# 常见 Root Cause

包括：

- Consumer Lag
- Broker Disk IO 饱和
- ISR Shrink
- Leader Election
- Produce Retry
- Fetch Latency
- Batch Size 不合理
- Compression 开销
- Network Retransmission
- Request Queue 堆积

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复 Consumer Processing
2. 修复磁盘瓶颈
3. 优化 Batch Size
4. 优化 Compression
5. 优化 Partition 数量
6. 优化 Producer 参数
7. 优化 Consumer 参数
8. 增加 Broker 资源
9. 扩容 Broker

不要默认建议扩容。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件：

- 已确认 Kafka 不是瓶颈，应继续分析数据库、缓存、应用或网络。
- 已确认 Kafka 是 Root Cause。
- 当前缺少 Broker Metrics、Consumer Lag 等关键数据。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

Consumer Lag 持续增长。

---

## 已收集证据（Evidence）

包括：

- Broker Metrics
- Consumer Lag
- Topic 信息
- ISR
- Produce Latency
- Fetch Latency
- Linux Metrics

---

## 分析过程（Reasoning）

说明：

- Producer 是否正常
- Broker 是否正常
- Consumer 是否正常
- 为什么确认或排除 Kafka

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么 Kafka 内部机制导致当前性能下降。

---

## 优化建议（Recommendations）

按优先级排序。

---

## 验证方案（Validation Plan）

优化完成后，应验证：

- Produce Latency
- Fetch Latency
- Consumer Lag
- TPS
- Broker CPU
- Disk IO
- Network Throughput
- ISR 状态
- Leader 稳定性

确认 Kafka 优化是否真正改善性能。