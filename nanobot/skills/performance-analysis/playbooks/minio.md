# MinIO 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 对 MinIO（S3 Object Storage）在性能测试过程中的性能问题进行调查和分析。

适用于：

- PUT 上传慢
- GET 下载慢
- ListObjects 慢
- Multipart Upload 慢
- S3 API 延迟增加
- 吞吐量下降
- 小文件性能差
- 磁盘 IO 高
- 网络带宽不足
- Healing 导致性能下降
- Erasure Coding 开销过高

支持：

- MinIO Standalone
- MinIO Distributed
- Kubernetes MinIO
- S3 Compatible Object Storage

本 Playbook 遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于实时数据验证。

---

# 第一性原理（First Principles）

MinIO 本质是对象存储。

一次对象请求通常经过：

```text
Client
      │
      ▼
Network
      │
      ▼
MinIO API
      │
      ▼
Erasure Coding
      │
      ▼
Disk
      │
      ▼
Filesystem
```

因此：

```
GET 慢

≠

MinIO 有问题
```

真正耗时可能发生在：

- 网络
- Erasure Coding
- 磁盘
- 文件系统
- 小对象处理
- Healing
- 后端存储

必须确定：

时间到底耗费在哪一层。

---

# 常见现象（Symptoms）

例如：

- PUT Latency 增加
- GET Latency 增加
- ListObjects 慢
- Multipart Upload 慢
- 吞吐下降
- Disk Busy
- CPU 高
- Healing 中
- Network Throughput 不足
- 小对象性能差

---

# Agent 调查策略（Investigation Strategy）

收到 MinIO 性能问题时，应首先回答：

1. 上传还是下载慢？
2. 是否仅小对象慢？
3. 是否发生 Healing？
4. 是否磁盘成为瓶颈？
5. 是否网络成为瓶颈？
6. 是否 Erasure Coding 开销过高？
7. 是否对象数量过多？

如果可以调用：

- mc admin
- mc admin trace
- Prometheus
- kubectl
- Shell

应优先获取实时数据。

不要看到：

Disk Busy

就直接认为：

磁盘是 Root Cause。

---

# 建议收集的数据（Evidence）

## MinIO Metrics

建议收集：

- S3 Requests
- PUT Latency
- GET Latency
- Throughput
- Error Rate
- Active Requests

---

## MinIO Health

建议执行：

```bash
mc admin info <alias>

mc admin heal info <alias>
```

关注：

- Online Drives
- Offline Drives
- Healing Status

---

## MinIO Trace

建议执行：

```bash
mc admin trace <alias>
```

关注：

- API
- Latency
- Duration
- Error

---

## Disk

建议执行：

```bash
iostat -x 1

df -h
```

关注：

- util
- await
- IO Wait
- Free Space

---

## Network

建议执行：

```bash
sar -n DEV 1

ss -s
```

关注：

- Throughput
- Retransmission
- Errors

---

## Kubernetes

建议执行：

```bash
kubectl top pod

kubectl describe pod
```

关注：

- CPU
- Memory
- Restart
- PVC

---

# 推荐执行命令（Commands）

查看集群：

```bash
mc admin info <alias>
```

查看 Healing：

```bash
mc admin heal info <alias>
```

查看 Trace：

```bash
mc admin trace <alias>
```

查看磁盘：

```bash
iostat -x 1
```

查看网络：

```bash
sar -n DEV 1
```

查看 Pod：

```bash
kubectl top pod
```

---

# 推荐分析流程（Workflow）

```text
确认 PUT / GET 延迟
        │
        ▼
分析 API Trace
        │
        ▼
分析 MinIO Metrics
        │
        ▼
检查磁盘
        │
        ▼
检查网络
        │
        ▼
检查 Healing
        │
        ▼
检查 Erasure Coding
        │
        ▼
确认 Root Cause
```

---

# 常见瓶颈分析（Analysis）

## PUT Latency 高

检查：

- Disk IO
- Erasure Coding
- Network

第一性原理：

PUT 必须：

写磁盘

↓

编码

↓

同步

磁盘和网络通常决定写入性能。

---

## GET Latency 高

检查：

- Cache
- Disk Read
- Network

第一性原理：

GET 本质：

读取对象

↓

磁盘

↓

网络返回。

---

## ListObjects 慢

检查：

对象数量。

Bucket 是否：

包含大量对象。

第一性原理：

对象越多：

遍历时间越长。

---

## Small Object

检查：

对象大小。

第一性原理：

大量小对象：

元数据开销远高于数据本身。

容易导致：

CPU

IO

Metadata

成为瓶颈。

---

## Multipart Upload

检查：

- Part Size
- Part Count

第一性原理：

Part 太小：

请求数量增加。

Part 太大：

单次上传时间增加。

---

## Healing

检查：

```bash
mc admin heal info
```

第一性原理：

Healing 会：

扫描对象

↓

重新校验

↓

重新写盘。

期间可能影响业务性能。

---

## Erasure Coding

检查：

编码方式。

分析：

CPU 是否因为编码升高。

磁盘是否写放大。

---

## Disk IO

检查：

```bash
iostat -x
```

重点：

- util
- await

如果：

```
util

≈100%
```

说明：

磁盘可能已达到瓶颈。

---

## Network

检查：

```bash
sar -n DEV

netstat -s
```

关注：

- Throughput
- Retransmission
- Packet Loss

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认 MinIO 是 Root Cause：

- PUT/GET Latency 与磁盘或网络指标一致。
- Healing 导致业务请求延迟增加。
- Erasure Coding 导致 CPU 或 IO 饱和。
- 小对象请求导致元数据成为瓶颈。
- Disk IO 饱和影响对象读写。

否则：

应继续分析：

- 应用
- Kubernetes
- Linux
- 网络

---

# 常见 Root Cause

包括：

- Disk IO Saturation
- Healing
- Erasure Coding
- Small Object Storm
- Multipart Upload 配置不合理
- Network Bottleneck
- Metadata 开销
- Bucket 对象数量过多

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复磁盘瓶颈
2. 修复网络瓶颈
3. 优化对象大小
4. 调整 Multipart Upload 参数
5. 合理规划 Bucket
6. 优化 Erasure Coding 配置
7. 调整资源
8. 扩容 MinIO 集群

不要直接建议扩容。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件：

- 已确认 MinIO 不是 Root Cause，应继续分析网络、应用或 Linux。
- 已确认 MinIO 是 Root Cause。
- 当前缺少 Metrics 或 Trace 数据。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

PUT P99 从 200ms 增加到 2s。

---

## 已收集证据（Evidence）

包括：

- MinIO Metrics
- API Trace
- Healing 状态
- Disk
- Network
- Kubernetes Metrics

---

## 分析过程（Reasoning）

说明：

- 是否排除磁盘
- 是否排除网络
- 是否排除 Healing
- 是否确认 MinIO

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么 MinIO 内部机制导致当前性能下降。

---

## 优化建议（Recommendations）

按优先级排序。

---

## 验证方案（Validation Plan）

优化完成后，应验证：

- PUT Latency
- GET Latency
- Throughput
- Error Rate
- Disk Util
- Network Throughput
- Healing 状态
- P95
- P99

确认 MinIO 优化是否真正改善性能。