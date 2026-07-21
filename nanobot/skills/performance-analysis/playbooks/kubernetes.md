# Kubernetes 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 在性能测试过程中，对 Kubernetes 集群及运行环境进行系统性的性能分析。

适用于：

- Pod CPU 高
- Pod Memory 高
- Pod 重启
- OOMKilled
- CPU Throttling
- Node Resource Pressure
- Service 延迟增加
- DNS 解析慢
- Container 创建慢
- PVC 性能问题
- CNI 网络问题
- Pod 调度异常

支持：

- Kubernetes
- OpenShift
- K3s
- RKE2
- ACK
- EKS
- GKE
- AKS

本 Playbook 遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于实时数据验证。

---

# 第一性原理（First Principles）

Kubernetes 只是资源编排平台。

请求路径：

```text
Client
    │
    ▼
Ingress
    │
    ▼
Service
    │
    ▼
Pod
    │
    ▼
Container Runtime
    │
    ▼
Linux Kernel
    │
    ▼
CPU / Memory / Disk / Network
```

因此：

```
Pod 慢

≠

Kubernetes 有问题
```

必须明确：

性能到底耗费在哪一层。

例如：

- 应用
- JVM
- 容器
- Linux
- 网络
- 存储

Kubernetes 更多提供的是运行环境。

---

# 常见现象（Symptoms）

例如：

- Pod CPU 持续高
- Memory 持续增长
- Pod Restart
- OOMKilled
- CPU Throttling
- Pending
- Container Creating
- Node NotReady
- Network Timeout
- Service Latency 增加
- DNS 查询慢

---

# Agent 调查策略（Investigation Strategy）

收到 Kubernetes 性能问题时，应首先回答：

1. 是否是 Pod 本身的问题？
2. 是否是 Node 资源不足？
3. 是否发生 CPU Throttling？
4. 是否发生 OOM？
5. 是否发生调度问题？
6. 是否发生网络问题？
7. 是否发生存储问题？

如果可以调用：

- Kubernetes MCP
- Grafana MCP
- kubectl
- Prometheus
- Grafana
- Shell
- Metrics Server

应优先获取实时数据。

优先收集：

- Kubernetes MCP：Pod / Node / Event / Resource / Log / Metrics Server 数据。
- Grafana MCP：Prometheus 指标、Loki 日志、Dashboard 面板查询和 Datasource 信息。

不要仅因为：

- Pod Restart
- CPU 高
- Node Pressure

就直接判断 Kubernetes 是 Root Cause。

---

# 建议收集的数据（Evidence）

## Cluster 信息

建议收集：

```bash
kubectl cluster-info

kubectl version

kubectl get nodes -o wide
```

关注：

- Kubernetes Version
- Node 数量
- Runtime
- Network Plugin

如果可用，也可以通过 Kubernetes MCP 只读查询 Cluster、Node、Pod 和 Event 信息；通过 Grafana MCP 查询对应时间窗口的集群概览 Dashboard 或 Prometheus 指标。

---

## Node 状态

```bash
kubectl get nodes

kubectl describe node <node>
```

重点关注：

- Ready
- MemoryPressure
- DiskPressure
- PIDPressure
- NetworkUnavailable

---

## Pod 状态

```bash
kubectl get pods -A -o wide

kubectl describe pod <pod>
```

关注：

- Restart Count
- Events
- QoS Class
- Requests
- Limits

---

## Resource Usage

```bash
kubectl top pod

kubectl top node
```

关注：

- CPU
- Memory

同时比较：

- Requests
- Limits
- Actual Usage

---

## Events

```bash
kubectl get events \
--sort-by=.lastTimestamp
```

重点关注：

- FailedScheduling
- OOMKill
- FailedMount
- BackOff
- Unhealthy

---

## Deployment

```bash
kubectl describe deployment
```

关注：

- Replicas
- Rolling Update
- Revision

---

## PVC

```bash
kubectl get pvc

kubectl describe pvc
```

关注：

- Pending
- Bound
- StorageClass

---

## Service

```bash
kubectl get svc

kubectl describe svc
```

关注：

- Endpoint
- Selector

---

## Endpoint

```bash
kubectl get endpoints
```

检查：

Endpoint 是否完整。

---

## Network

默认优先通过 Service / Endpoint / Metrics / 日志判断网络问题。必要时可以进入容器执行短时、只读诊断命令：

```bash
kubectl exec

ping

curl

nc
```

验证：

- Service
- DNS
- Pod 网络

---

# 推荐执行命令（Commands）

查看节点：

```bash
kubectl get nodes -o wide
```

查看 Pod：

```bash
kubectl get pods -A
```

查看资源：

```bash
kubectl top pod

kubectl top node
```

查看 Pod：

```bash
kubectl describe pod <pod>
```

查看 Events：

```bash
kubectl get events \
--sort-by=.lastTimestamp
```

查看日志：

```bash
kubectl logs <pod>

kubectl logs <pod> --previous
```

可以进入容器执行只读查询；应优先使用非交互命令并控制超时时间。交互式 shell、写入文件、修改配置、重启进程或持续探测需要用户明确授权：

```bash
kubectl exec -it <pod> -- sh
```

---

# 推荐分析流程（Workflow）

```text
确认性能下降
        │
        ▼
检查 Pod
        │
        ▼
检查 Node
        │
        ▼
检查 Resource
        │
        ▼
检查 Events
        │
        ▼
检查 Network
        │
        ▼
检查 Storage
        │
        ▼
继续分析应用
```

Kubernetes 更多负责排除环境问题。

---

# 常见瓶颈分析（Analysis）

## CPU Throttling

检查：

```bash
kubectl describe pod
```

以及：

Prometheus：

```
container_cpu_cfs_throttled_seconds_total
```

第一性原理：

CPU 使用率高

≠

CPU 真正跑满。

如果：

```
CPU Limit 很低

↓

Linux CFS

↓

CPU 被限制

↓

请求排队
```

则 Root Cause 为：

CPU Throttling。

---

## OOMKilled

检查：

```bash
kubectl describe pod
```

查看：

```
Reason:

OOMKilled
```

第一性原理：

Memory Limit

小于

应用实际需要。

---

## Restart

检查：

```
Restart Count
```

进一步分析：

为什么：

- CrashLoopBackOff
- OOM
- Liveness Probe

不要认为：

Restart

就是 Root Cause。

---

## Pending

检查：

```bash
kubectl describe pod
```

关注：

Events：

例如：

- No Node Available
- PVC Pending
- Resource Insufficient

---

## Node Pressure

检查：

```bash
kubectl describe node
```

关注：

- MemoryPressure
- DiskPressure
- PIDPressure

说明：

Node 已经无法继续承载更多 Pod。

---

## Service

检查：

Endpoint：

是否缺失。

Service：

是否指向正确 Pod。

---

## DNS

验证：

```bash
nslookup

dig
```

分析：

DNS：

是否解析缓慢。

---

## PVC

检查：

Storage：

是否：

Pending

IO 是否异常。

如果涉及性能：

继续分析：

磁盘。

---

## CNI

检查：

Pod：

互通是否正常。

分析：

网络：

是否存在：

- Packet Loss
- RTT 高
- MTU 问题

---

## Pod Resource

检查：

Requests：

是否远小于：

实际资源需求。

分析：

是否导致：

CPU Throttling。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认 Kubernetes 是 Root Cause：

- CPU Throttling 明显影响请求。
- OOMKilled 导致服务中断。
- 调度失败导致服务不可用。
- CNI 网络异常导致请求超时。
- Storage 无法正常提供 IO。
- Node Pressure 导致资源不足。

否则：

Kubernetes

只是运行环境。

应继续分析：

应用、

数据库、

缓存、

MQ。

---

# 常见 Root Cause

包括：

- CPU Throttling
- OOMKilled
- Node Resource Pressure
- FailedScheduling
- PVC Pending
- Storage IO
- DNS
- CNI Network
- Endpoint 配置错误
- Resource Requests 配置不合理

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复应用问题
2. 修正 Requests / Limits
3. 修复 Storage
4. 修复 Network
5. 调整调度策略
6. 优化 HPA
7. 增加 Node
8. 扩容 Cluster

不要直接建议：

增加节点。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件：

- 已确认 Kubernetes 不是 Root Cause，应继续分析应用、中间件或数据库。
- 已确认 Kubernetes 是 Root Cause。
- 当前缺少 Metrics 或 Events。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

Pod CPU 持续达到 95%，P99 响应时间增加。

---

## 已收集证据（Evidence）

包括：

- Pod
- Node
- Events
- Metrics
- Resource
- Network
- Storage

---

## 分析过程（Reasoning）

说明：

- 是否排除 Kubernetes
- 是否排除 Node
- 是否排除资源限制
- 是否需要继续分析应用

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么 Kubernetes 运行机制导致当前性能下降。

---

## 优化建议（Recommendations）

按优先级排序。

---

## 验证方案（Validation Plan）

优化完成后，应验证：

- TPS
- Avg
- P95
- P99
- Pod CPU
- Pod Memory
- CPU Throttling
- Restart Count
- OOMKilled
- Node Resource
- Error Rate

制定 Kubernetes 环境优化后的验证方案，由用户决定是否执行。
