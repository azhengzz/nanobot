# JVM 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 对 Java 应用在性能测试过程中的 JVM 性能问题进行调查和分析。

适用于：

- Java 应用响应时间增加
- TPS 下降
- P95 / P99 延迟升高
- CPU 使用率异常
- Full GC
- Young GC 频繁
- Memory Leak
- Old Gen 增长
- Thread Blocking
- Safepoint 停顿
- Object Allocation 过高
- Direct Memory 压力
- 类加载异常

支持分析：

- HotSpot JVM
- OpenJDK
- Oracle JDK
- Spring Boot
- Tomcat
- Netty
- Java 微服务

本 Playbook 遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于 JVM 数据验证。

---

# 第一性原理（First Principles）

JVM 应用性能，本质由以下几个因素决定：

```text
Request
   │
   ▼
Thread
   │
   ▼
Application Code
   │
   ├── CPU Execution
   │
   ├── Memory Allocation
   │
   ├── Lock Competition
   │
   └── IO Waiting
          │
          ▼
       JVM Runtime
          │
          ├── GC
          │
          ├── JIT
          │
          └── Safepoint
```

Java 应用性能下降通常来自：

1. CPU 执行时间增加
2. 线程等待增加
3. 锁竞争增加
4. GC 停顿增加
5. 内存不足
6. IO 等待增加

因此：

```text
GC 高

≠

一定是 GC 导致慢
```

必须分析：

- GC 是否发生在性能下降时间段
- GC 停顿是否占据请求时间
- GC 是否导致线程阻塞

---

# 常见现象（Symptoms）

例如：

- API 响应时间增加
- TPS 下降
- CPU 持续升高
- Full GC 增加
- Young GC 频繁
- Heap 使用持续增长
- Old Gen 不下降
- Thread 数增加
- Deadlock
- Lock Wait
- 应用无响应

---

# Agent 调查策略（Investigation Strategy）

收到 JVM 性能问题时，应优先回答：

1. 是 CPU 问题？
2. 是 GC 问题？
3. 是线程问题？
4. 是锁竞争？
5. 是内存问题？
6. 是业务代码执行慢？

不要看到：

- Heap 高
- GC 存在
- CPU 高

就直接判断 JVM 是根因。

必须获取：

- GC Log
- Thread Dump
- Heap 信息
- CPU Profile

进行验证。

---

# 建议收集的数据（Evidence）

## JVM 基础信息

收集：

```bash
jcmd <pid> VM.version

jcmd <pid> VM.flags

jcmd <pid> VM.command_line
```

关注：

- JDK 版本
- GC 算法
- Heap 参数
- Direct Memory

---

## Heap 使用情况

收集：

```bash
jcmd <pid> GC.heap_info
```

关注：

- Heap Used
- Heap Max
- Old Generation
- Metaspace

---

## GC 数据

收集：

```bash
jstat -gcutil <pid> 1000

jstat -gc <pid>
```

关注：

- YGC
- YGCT
- FGC
- FGCT
- GCT

重点：

```text
FGCT / Response Time
```

---

## GC Log

收集：

- GC Pause Time
- Allocation Failure
- Full GC Reason

分析：

- Full GC 是否发生在性能下降时间
- Pause 是否影响请求

---

## Thread Dump

收集：

```bash
jstack <pid>
```

关注：

- BLOCKED
- WAITING
- RUNNABLE

分析：

- 锁竞争
- 死锁
- 线程池耗尽

---

## CPU Profile

工具：

- async-profiler
- Java Flight Recorder（JFR）
- Arthas profiler

关注：

- CPU Hot Method
- Object Allocation
- Lock

---

## Arthas

常用命令：

查看线程：

```bash
thread
```

查看热点：

```bash
profiler start

profiler stop
```

查看方法耗时：

```bash
trace
```

---

# 推荐执行命令（Commands）

## 查看 JVM 参数

```bash
jcmd <pid> VM.flags
```

---

## 查看 GC

```bash
jstat -gcutil <pid> 1000
```

---

## 查看线程

```bash
jstack <pid>
```

---

## 查看进程

```bash
jps -l
```

---

## 查看 CPU

```bash
top -H -p <pid>
```

---

# 推荐分析流程（Workflow）

```text
确认响应时间增加
          │
          ▼
检查 JVM Metrics
          │
          ▼
CPU 是否异常？
          │
     ┌────┴────┐
     │         │
    是         否
     │         │
CPU Profile    GC分析
     │         │
     ▼         ▼
热点方法      GC Pause
     │         │
     ▼         ▼
Thread Dump  Memory
     │         │
     └────┬────┘
          ▼
     Root Cause验证
```

---

# 常见瓶颈分析（Analysis）

## CPU 高

检查：

- top
- pidstat
- async-profiler

重点：

找到 CPU 消耗在哪个方法。

不要只看 CPU 使用率。

第一性原理：

CPU 高只是现象。

真正原因可能：

- 死循环
- 大量计算
- JSON 序列化
- 正则匹配
- GC
- 锁竞争

---

## Full GC

检查：

- GC Log
- Old Gen

重点：

确认 Full GC 时间是否与性能下降一致。

第一性原理：

Full GC 会 Stop The World。

期间所有业务线程暂停。

---

## Young GC 频繁

检查：

- Allocation Rate
- Eden 使用率

可能原因：

- 创建大量临时对象
- JSON 转换
- String 拼接
- 高频集合创建

第一性原理：

对象创建速度超过 GC 回收速度。

---

## Memory Leak

检查：

```text
Heap Used 持续增长

↓

GC 后无法下降
```

进一步分析：

Heap Dump：

- Dominator Tree
- Reference Chain

---

## Thread Blocking

检查：

Thread Dump。

重点关注：

```text
BLOCKED
```

可能原因：

- synchronized
- ReentrantLock
- 数据库连接池等待
- Redis 连接池等待

第一性原理：

线程无法继续执行，只能等待资源释放。

---

## Thread Pool Exhaustion

检查：

- Active Thread
- Queue Size

例如：

Tomcat：

```text
maxThreads
currentThreadsBusy
```

第一性原理：

请求进入速度大于处理速度。

线程耗尽后，请求开始排队。

---

## Lock Competition

检查：

Thread Dump。

关注：

- BLOCKED
- Lock Owner

原因：

多个线程竞争同一资源。

---

## Safepoint

检查：

GC Log。

关注：

Safepoint Time。

第一性原理：

JVM 在执行 GC、类加载等操作时，需要暂停所有线程。

---

## Direct Memory

检查：

Netty 等场景。

关注：

- Direct Buffer
- OOM Direct Buffer

第一性原理：

堆外内存不足会导致 Buffer 分配失败或频繁回收。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认 JVM 是 Root Cause。

## GC Root Cause

必须满足：

- GC 时间与性能下降时间一致。
- Pause Time 足够影响请求。
- GC 次数明显增加。

---

## CPU Root Cause

必须满足：

- CPU 消耗集中在具体方法。
- Profiling 证明热点代码。

---

## Memory Leak Root Cause

必须满足：

- Heap 持续增长。
- GC 后无法释放。
- Heap Dump 定位对象引用。

---

## Thread Blocking Root Cause

必须满足：

- Thread Dump 显示大量阻塞线程。
- 明确锁竞争位置。

否则只能作为：

Hypothesis。

---

# 常见 Root Cause

包括：

- Full GC
- Allocation Rate 高
- Memory Leak
- CPU Hot Method
- Thread Pool Exhaustion
- Lock Competition
- Deadlock
- Safepoint
- Direct Memory OOM
- 类加载异常
- JIT 编译异常

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复业务代码问题
2. 优化对象创建
3. 减少锁竞争
4. 优化线程模型
5. 优化 JVM 参数
6. 调整 Heap 配置
7. 调整 GC 策略
8. 增加资源
9. 扩容

不要默认建议调整 JVM 参数或扩容。

应优先修复真正 Root Cause。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件，应结束 JVM 分析：

- 已确认 JVM 不是瓶颈，应继续分析数据库、缓存、MQ 或网络。
- 已确认 JVM 是 Root Cause。
- 当前缺少 GC Log、Thread Dump、Profiling 等关键数据。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

接口 P99 从 500ms 增加到 5s。

---

## 已收集证据（Evidence）

包括：

- JVM Metrics
- GC Log
- Thread Dump
- CPU Profile
- Heap 信息

---

## 分析过程（Reasoning）

说明：

- 是否排除 GC
- 是否排除 CPU
- 是否排除线程问题
- 为什么确认或排除 JVM

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么 JVM 内部机制导致当前性能下降。

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
- GC Pause Time
- CPU
- Heap
- Thread Count
- Error Rate

确认 JVM 优化是否真正改善性能。