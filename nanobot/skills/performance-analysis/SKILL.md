---
name: performance-analysis
description: Diagnose performance problems during performance testing using first-principles reasoning. Investigate systems using real-time evidence, identify bottlenecks, validate root causes, and recommend optimization actions.
always: true
---

# 性能分析（Performance Analysis）

## Skill 目标

本 Skill 用于指导 Agent 在性能测试过程中，对性能问题进行系统化调查（Investigation），定位真正的性能瓶颈，并输出具有证据支撑的根因分析与优化建议。

本 Skill 的目标**不是猜测最可能的原因**，而是利用可获取的实时数据和工具，对当前系统进行调查，建立完整证据链，并最终确认 Root Cause。

如果证据不足，应明确指出缺失的数据，并继续调查，而不是直接给出结论。


## 分析要求
Agent 不应仅依据历史知识、经验或已有上下文直接得出结论。

对于能够通过命令、API 或日志实时获取的信息，应优先执行查询进行验证。

例如：

错误示例：

用户："为什么 Redis 很慢？"

Agent：
Redis 大概率是 Hot Key 导致。

正确示例：

Agent：

1. 查询 INFO
2. 查询 SLOWLOG
3. 查询 LATENCY
4. 查询 CLIENT LIST
5. 根据实时结果分析是否存在 Hot Key、Big Key 或其他瓶颈。

如果当前环境无法执行查询，应明确说明：

"由于无法访问目标环境，以下分析基于已有信息，结论需要进一步验证。"

不得将推测作为最终结论。


## 工具执行
除非用户明确授权，否则 Agent 默认工作模式为：

**Read Only Investigation（只读调查）**

Agent 不应主动：

- 发起压测
- 执行 Benchmark
- 写入大量数据
- 修改线上配置



---

# 能力范围

本 Skill 适用于：

- Kubernetes
- 微服务架构
- Java / Go / Python 应用
- JVM
- Linux
- 网络
- API Gateway
- MySQL
- PostgreSQL
- Redis
- Kafka
- Elasticsearch
- MinIO

支持分析：

- 性能测试结果
- 系统监控
- 应用日志
- 调用链（Trace）
- Thread Dump
- Heap Dump
- GC Log
- SQL Slow Log
- Prometheus Metrics
- Grafana Dashboard
- pprof
- Flame Graph
- eBPF
- tcpdump
- Linux Performance Tools

---

# 核心理念

性能分析不是回答：

> "最可能是什么问题？"

而是回答：

> "证据能够证明真正的问题是什么？"

所有分析都必须遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 逐层分析（Layer-by-Layer Analysis）
- 因果验证（Cause Before Conclusion）

禁止凭经验直接下结论。

---

# 分析流程

所有性能问题统一采用以下流程：

```text
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

任何步骤都不应跳过。

---

# 调查对象

分析时，应优先确定性能瓶颈位于哪一层，而不是直接怀疑某个组件。

典型请求路径：

```text
Client
    ↓
Load Balancer
    ↓
API Gateway
    ↓
Application
    ↓
Runtime（JVM / Go Runtime）
    ↓
Redis
    ↓
Kafka
    ↓
Database
    ↓
Object Storage
    ↓
Operating System
    ↓
Network
```

每一层都应回答：

- 是否存在异常？
- 是否有证据证明？
- 是否可以排除？
- 是否需要继续深入？

---

# 工作方式

本 Skill 采用"调查（Investigation）"模式，而不是"问答（Q&A）"模式。

当用户提出性能问题时，应优先：

1. 理解问题现象。
2. 收集相关证据。
3. 调查涉及的组件。
4. 建立完整证据链。
5. 验证根因。
6. 提供优化建议。
7. 制定验证方案。

如果证据不足，应停止推断，并明确说明需要补充哪些数据。

---

# Playbook 使用方式

不同组件具有不同的分析方法。

Agent 应根据当前问题涉及的组件，参考对应 Playbook。

例如：

| 组件 | Playbook |
|-------|----------|
| Gateway | playbooks/gateway.md |
| Application | playbooks/application.md |
| JVM | playbooks/jvm.md |
| Kubernetes | playbooks/kubernetes.md |
| Linux | playbooks/linux.md |
| Network | playbooks/network.md |
| MySQL | playbooks/mysql.md |
| PostgreSQL | playbooks/postgresql.md |
| Redis | playbooks/redis.md |
| Kafka | playbooks/kafka.md |
| Elasticsearch | playbooks/elasticsearch.md |
| MinIO | playbooks/minio.md |

如果涉及多个组件，应按照请求链路逐层分析，而不是只分析单个组件。

---

# 案例参考

对于典型问题，可参考 examples 目录中的案例。

例如：

- MySQL LIKE 导致全表扫描
- Redis Hot Key
- Kafka Consumer Lag
- Elasticsearch Hot Node
- Kubernetes CPU Throttling

案例用于帮助理解分析思路，不应用于直接推断当前系统的问题。

每一次分析都必须基于当前系统的实时数据。

---

# 输出要求

每次分析应至少包含以下内容：

1. 问题现象（Symptoms）
2. 已收集证据（Evidence）
3. 分析过程（Reasoning）
4. 根因（Root Cause）
5. 第一性原理解释
6. 优化建议（Recommendations）
7. 验证方案（Validation Plan）

如果证据不足，应明确说明：

- 当前缺少哪些数据
- 建议收集哪些信息
- 当前无法确认 Root Cause

不得使用猜测替代结论。

---

# 行为约束

本 Skill 的具体执行规范定义于：

> **policies.md**

包括但不限于：

- 第一性原理
- 工具调用策略
- 安全策略
- 证据等级
- Root Cause 判定标准
- 输出规范

Agent 在开始分析前，应遵循 policies.md 中定义的所有规则。

---

# 黄金法则（Golden Rules）

1. 调查优于猜测。
2. 证据优于经验。
3. 数据优于假设。
4. 时间轴优于主观判断。
5. 逐层分析优于局部分析。
6. 相关性不等于因果关系。
7. 每一个结论都必须能够证明。
8. 每一个优化建议都应能够解释其原理。
9. 默认采用只读分析，不主动执行可能影响业务的操作。
10. 优化完成后，应制定验证方案，并验证优化效果。