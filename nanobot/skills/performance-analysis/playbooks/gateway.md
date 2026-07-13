# Gateway 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 对 API Gateway、Nginx、Ingress、Envoy、Kong、APISIX 等网关组件进行性能调查。

适用于：

- HTTP 响应时间高
- P95 / P99 增加
- Gateway CPU 高
- Gateway Memory 高
- Upstream Timeout
- HTTP 502 / 503 / 504
- Retry 增加
- TLS 握手耗时高
- Connection Pool 耗尽
- Gateway 排队
- Rate Limit
- Network Latency

本 Playbook 遵循**第一性原理**和**证据驱动分析**。

所有结论必须基于实时数据验证，不允许凭经验推断。

---

# 第一性原理（First Principles）

Gateway 的职责仅是接收请求并转发到后端服务。

一次 HTTP 请求通常经历：

```text
Client
    │
    ▼
DNS
    │
    ▼
Load Balancer
    │
    ▼
Gateway
    │
    ▼
Upstream Service
    │
    ▼
Redis / MQ / Database
```

Gateway 本身不会执行业务逻辑。

因此：

```
Gateway 响应慢

≠

Gateway 是瓶颈
```

必须区分：

```
Gateway Processing Time

还是

Upstream Response Time
```

如果大量时间消耗在 Upstream，则应继续分析应用及后端组件。

---

# 常见现象（Symptoms）

例如：

- Gateway Response Time 增加
- HTTP 502
- HTTP 503
- HTTP 504
- Upstream Timeout
- Retry 增加
- Gateway CPU 高
- Gateway Memory 高
- Connection 数增加
- KeepAlive 不生效
- TLS 握手慢
- 请求排队
- Connection Reset

---

# Agent 调查策略（Investigation Strategy）

收到 Gateway 性能问题时，应首先回答：

1. Gateway 自身是否真的耗时？
2. Gateway 是否只是等待 Upstream 返回？
3. 是否存在 Retry、Timeout、Rate Limit？
4. 是否是网络问题导致？
5. Gateway 是否只是性能问题的表现，而非根因？

如果可以调用：

- MCP
- kubectl
- Shell
- Prometheus
- Grafana

应优先获取实时数据。

不要看到：

- 502
- Timeout
- Gateway 响应慢

就直接判断 Gateway 有问题。

---

# 建议收集的数据（Evidence）

## Gateway Access Log

建议收集：

- request_time
- upstream_response_time
- upstream_connect_time
- upstream_header_time
- status
- upstream_addr
- request_uri
- request_method
- request_length
- body_bytes_sent

重点关注：

```
request_time

vs

upstream_response_time
```

---

## Gateway Metrics

建议收集：

- Request Count
- Active Connection
- Connection Rate
- Request Duration
- Upstream Duration
- Retry Count
- Timeout Count
- 4xx Count
- 5xx Count

---

## Kubernetes

建议收集：

```bash
kubectl top pod

kubectl describe pod

kubectl get events

kubectl logs
```

重点关注：

- CPU
- Memory
- Restart
- OOMKill
- CPU Throttling

---

## Linux

建议收集：

```bash
ss -s

netstat -s

sar -n DEV

sar -n TCP

vmstat

iostat
```

重点关注：

- TCP Retransmission
- Socket Queue
- Active Connection
- Packet Loss
- Network Throughput

---

## Prometheus

建议关注：

- Request Duration
- Upstream Duration
- CPU Usage
- Memory Usage
- Active Connections
- Network Errors

---

# 推荐执行命令（Commands）

## Kubernetes

```bash
kubectl top pod -n <namespace>

kubectl describe pod <gateway-pod>

kubectl logs <gateway-pod>
```

---

## Nginx

查看 Access Log：

```bash
tail -100 access.log
```

统计：

```bash
grep "GET" access.log
```

---

## Envoy

查看统计信息：

```bash
curl localhost:15000/stats
```

查看 Cluster：

```bash
curl localhost:15000/clusters
```

---

## Linux

查看连接：

```bash
ss -ant
```

查看网络：

```bash
sar -n DEV
```

查看 TCP：

```bash
netstat -s
```

---

# 推荐分析流程（Workflow）

```text
确认响应时间增加
        │
        ▼
分析 Access Log
        │
        ▼
比较：

request_time

vs

upstream_response_time
        │
        ▼
Gateway 是否耗时？
        │
   ┌────┴────┐
   │         │
  是         否
   │         │
分析 Gateway   继续分析 Upstream
        │
        ▼
分析 Retry
        │
        ▼
分析 Timeout
        │
        ▼
分析 Network
        │
        ▼
确认 Root Cause
```

不要因为 Gateway 在请求链路前端，就默认它是瓶颈。

---

# 常见瓶颈分析（Analysis）

## Gateway Processing Time 高

检查：

- request_time
- CPU
- Worker 数量
- Worker Connection
- Logging
- Compression

第一性原理：

Gateway 主要负责：

- HTTP 解析
- 路由
- TLS
- Proxy

如果 Gateway Processing Time 高，说明 Gateway 自身处理能力不足。

---

## Upstream Response Time 高

重点检查：

```
upstream_response_time
```

如果：

```
request_time

≈

upstream_response_time
```

说明：

绝大多数时间都消耗在后端。

Gateway 可以排除。

继续分析：

- Application
- Redis
- Kafka
- MySQL
- Elasticsearch

---

## Retry

检查：

- Retry Count
- Retry Policy
- Retry Reason

第一性原理：

Retry 会放大系统压力。

例如：

一次请求 Retry 三次：

实际系统压力可能增加三倍。

---

## Timeout

检查：

- Gateway Timeout
- Upstream Timeout

分析：

Timeout：

到底发生在哪一层。

不要仅根据 504 判断后端一定有问题。

---

## Connection Pool

检查：

- Active Connection
- Idle Connection
- KeepAlive
- Max Connection

分析：

是否：

频繁建立 TCP 连接。

---

## TLS

检查：

- TLS Handshake Time
- SSL Session Reuse

第一性原理：

TLS 握手需要：

- CPU
- RTT
- 加密运算

高并发下可能成为瓶颈。

---

## Logging

检查：

Access Log 是否同步写盘。

日志量是否异常。

第一性原理：

同步磁盘写入可能导致请求线程阻塞。

---

## Compression

检查：

是否开启：

- gzip
- brotli

分析：

CPU 是否因压缩导致升高。

---

## HTTP Status

统计：

- 2xx
- 3xx
- 4xx
- 5xx

重点分析：

- 502
- 503
- 504

持续增加通常意味着：

Gateway 无法正常访问 Upstream。

---

## Network

检查：

Linux：

```bash
ss -s

netstat -s

sar -n DEV
```

重点关注：

- Packet Loss
- Retransmission
- RTT
- Socket Queue

第一性原理：

网络异常最终表现为：

- Timeout
- Retry
- Response Time 增加

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件之一，才能确认 Gateway 为 Root Cause：

- request_time 明显高于 upstream_response_time，说明耗时发生在 Gateway。
- Gateway CPU、Memory 或 Worker 已达到瓶颈，并与响应时间增加一致。
- Retry 或 Timeout 配置导致请求放大，并有日志和指标证明。
- Gateway Connection Pool 耗尽，导致请求排队。
- TLS、Compression 或 Logging 明确导致 Gateway Processing Time 增加。

如果：

```
request_time

≈

upstream_response_time
```

说明：

Root Cause 不在 Gateway。

应继续调查 Upstream。

---

# 常见 Root Cause

包括但不限于：

- Upstream 响应慢
- Retry 放大流量
- Timeout 配置不合理
- TLS 握手耗时
- KeepAlive 配置错误
- Worker 数不足
- Connection Pool 耗尽
- Gateway CPU 饱和
- Compression 开销过高
- Logging 阻塞
- Network Retransmission

Root Cause 必须结合证据确认。

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复 Upstream 瓶颈
2. 优化 Retry 策略
3. 优化 Timeout 配置
4. 启用或优化 KeepAlive
5. 优化 TLS 配置
6. 调整 Compression
7. 优化日志策略（异步日志、降低日志级别）
8. 调整 Worker 数量
9. 增加 Gateway 资源
10. 扩容 Gateway

不要默认建议扩容。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件，应结束 Gateway 分析：

- 已确认 Gateway 不是瓶颈，应继续分析 Upstream。
- 已确认 Gateway 是 Root Cause。
- 当前证据不足，需要补充日志或指标。
- 已无法继续分析，应停止推断并说明原因。

不要长时间停留在 Gateway 层，而忽略真正的业务瓶颈。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

## 已收集证据（Evidence）

包括：

- Access Log
- Metrics
- Request Time
- Upstream Response Time
- CPU
- Memory
- Network

## 分析过程（Reasoning）

说明：

- 为什么 Gateway 是或不是瓶颈
- 为什么继续分析 Upstream
- 为什么确认当前 Root Cause

## 根因（Root Cause）

必须提供对应证据。

## 第一性原理解释

解释为什么该问题会导致响应时间增加。

## 优化建议（Recommendations）

按优先级排序。

## 验证方案（Validation Plan）

优化完成后，应验证：

- Request Time
- Upstream Response Time
- P95 / P99
- Retry Count
- Timeout Count
- Active Connection
- CPU
- Memory
- HTTP Status

确认优化是否达到预期效果。