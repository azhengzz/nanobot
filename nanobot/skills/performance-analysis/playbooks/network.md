# Network 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 在性能测试过程中，对网络层进行系统性的性能分析。

适用于：

- 请求响应时间增加
- TCP 连接建立慢
- 网络吞吐下降
- Packet Loss（丢包）
- TCP Retransmission（重传）
- Connection Timeout
- DNS 解析慢
- Socket Backlog 满
- SYN Queue 满
- MTU 问题
- 长连接异常
- Kubernetes 网络异常

支持：

- Linux Network
- Kubernetes CNI
- Docker Network
- Istio / Envoy
- Service Mesh
- TCP/IP
- HTTP/HTTPS
- gRPC
- Redis
- MySQL
- Kafka
- MinIO

本 Playbook 遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于实时数据验证。

---

# 第一性原理（First Principles）

网络负责数据传输。

一次请求通常经过：

```text
Client
    │
    ▼
DNS
    │
    ▼
TCP Handshake
    │
    ▼
Load Balancer
    │
    ▼
Gateway
    │
    ▼
Service Mesh
    │
    ▼
Application
```

底层还包括：

```text
Socket
      │
      ▼
TCP/IP Stack
      │
      ▼
NIC
      │
      ▼
Switch
      │
      ▼
Router
```

因此：

```
HTTP 慢

≠

网络慢
```

必须回答：

时间耗费在哪一步？

---

# 常见现象（Symptoms）

例如：

- RTT 增加
- Packet Loss
- TCP Retransmission
- Connection Timeout
- DNS 延迟
- Socket Backlog 满
- SYN Queue 满
- Throughput 降低
- 建连慢
- TLS 握手慢

---

# Agent 调查策略（Investigation Strategy）

收到网络性能问题时，应首先回答：

1. DNS 是否正常？
2. TCP 建连是否正常？
3. RTT 是否增加？
4. 是否存在丢包？
5. 是否发生 TCP 重传？
6. 是否发生 Socket 排队？
7. 是否发生带宽瓶颈？

如果可以调用：

- ping
- traceroute
- mtr
- tcpdump
- ss
- netstat
- sar
- ip
- ethtool

应优先获取实时数据。

不要仅凭：

响应时间增加

就判断：

网络有问题。

---

# 建议收集的数据（Evidence）

## Network Interface

建议执行：

```bash
ip addr

ip link

ethtool eth0
```

关注：

- Speed
- Duplex
- Errors
- Drops

---

## TCP

建议执行：

```bash
ss -s

ss -ant

netstat -s
```

关注：

- ESTABLISHED
- TIME_WAIT
- CLOSE_WAIT
- Retransmission

---

## Throughput

建议执行：

```bash
sar -n DEV 1
```

关注：

- rxkB/s
- txkB/s
- rxdrop/s
- txdrop/s

---

## DNS

建议执行：

```bash
dig

nslookup
```

关注：

解析时间。

---

## RTT

建议执行：

```bash
ping

mtr
```

关注：

- RTT
- Jitter
- Packet Loss

---

## Route

建议执行：

```bash
ip route

traceroute
```

检查：

是否绕路。

---

## TCP Capture

建议执行：

```bash
tcpdump
```

分析：

- SYN
- ACK
- FIN
- RST
- Retransmission

---

# 推荐执行命令（Commands）

查看 Socket：

```bash
ss -s

ss -ant
```

查看网络：

```bash
ip addr

ip route
```

查看统计：

```bash
sar -n DEV 1

sar -n TCP 1
```

查看重传：

```bash
netstat -s
```

抓包：

```bash
tcpdump
```

查看网卡：

```bash
ethtool eth0
```

---

# 推荐分析流程（Workflow）

```text
确认请求慢
        │
        ▼
检查 DNS
        │
        ▼
检查 TCP 建连
        │
        ▼
检查 RTT
        │
        ▼
检查 Packet Loss
        │
        ▼
检查 Retransmission
        │
        ▼
检查 Throughput
        │
        ▼
检查 Gateway
        │
        ▼
确认 Root Cause
```

---

# 常见瓶颈分析（Analysis）

## DNS

检查：

```bash
dig

nslookup
```

第一性原理：

DNS 解析慢

↓

TCP 建连延迟

↓

请求整体变慢。

---

## TCP Handshake

检查：

tcpdump。

分析：

SYN

↓

SYN ACK

↓

ACK

是否耗时过长。

---

## Packet Loss

检查：

```bash
ping

mtr
```

如果：

```
Packet Loss > 0%
```

需要进一步分析。

第一性原理：

TCP 会触发：

Retransmission。

---

## TCP Retransmission

检查：

```bash
netstat -s
```

关注：

Retransmitted Segments。

第一性原理：

TCP 重传：

增加 RTT。

降低吞吐。

---

## Socket Backlog

检查：

```bash
ss -lnt
```

分析：

Listen Queue

是否达到：

somaxconn。

---

## TIME_WAIT

检查：

```bash
ss -ant
```

关注：

TIME_WAIT 数量。

第一性原理：

大量短连接：

导致端口占用。

---

## CLOSE_WAIT

检查：

```bash
ss -ant
```

如果：

大量 CLOSE_WAIT。

通常说明：

应用未正确关闭 Socket。

---

## MTU

检查：

```bash
ip link
```

分析：

是否发生：

Fragmentation。

---

## NIC

检查：

```bash
ethtool
```

关注：

- Errors
- Drops

---

## Bandwidth

检查：

```bash
sar -n DEV
```

分析：

是否达到：

链路带宽。

---

## Kubernetes Network

检查：

- CNI
- kube-proxy
- Service Mesh

确认：

是否：

跨节点通信。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认网络是 Root Cause：

- Packet Loss 明显增加。
- TCP Retransmission 明显增加。
- RTT 显著上升。
- Socket Queue 满。
- DNS 延迟增加。
- MTU 配置错误。
- 网络带宽已达到瓶颈。

否则：

网络

只是表现层。

继续分析：

应用、

数据库、

缓存、

Linux。

---

# 常见 Root Cause

包括：

- DNS
- Packet Loss
- TCP Retransmission
- Socket Backlog
- TIME_WAIT
- CLOSE_WAIT
- MTU
- NIC Errors
- Bandwidth Saturation
- CNI

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复 DNS
2. 修复网络丢包
3. 修复重传
4. 调整 Socket 参数
5. 优化连接池
6. 调整 MTU
7. 升级网络设备
8. 增加带宽

不要默认建议增加带宽。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件：

- 已确认网络不是 Root Cause，应继续分析应用、中间件或数据库。
- 已确认网络是 Root Cause。
- 当前缺少抓包或网络指标数据。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

接口 P99 从 300ms 增加到 2.5s。

---

## 已收集证据（Evidence）

包括：

- RTT
- DNS
- TCP
- Socket
- Packet Loss
- Retransmission
- Throughput

---

## 分析过程（Reasoning）

说明：

- 是否排除 DNS
- 是否排除建连
- 是否排除网络带宽
- 是否确认网络问题

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么网络协议栈导致当前性能下降。

例如：

```text
Packet Loss
      │
      ▼
TCP Retransmission
      │
      ▼
RTT 增加
      │
      ▼
请求等待时间增加
      │
      ▼
P95 / P99 上升
```

---

## 优化建议（Recommendations）

按优先级排序。

---

## 验证方案（Validation Plan）

优化完成后，应验证：

- RTT
- Packet Loss
- TCP Retransmission
- Throughput
- Connection Time
- TPS
- Avg
- P95
- P99
- Error Rate

确认网络优化是否真正改善性能。