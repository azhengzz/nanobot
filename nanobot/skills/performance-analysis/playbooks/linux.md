# Linux 性能分析 Playbook

## 概述（Overview）

本 Playbook 用于指导 Agent 在性能测试过程中，对 Linux 操作系统进行系统性的性能分析。

适用于：

- CPU 使用率高
- Load Average 高
- Memory 使用率高
- Swap 使用
- Disk IO 高
- IO Wait 高
- 网络吞吐下降
- TCP 重传
- Context Switch 高
- 中断异常
- NUMA 不均衡
- 文件句柄耗尽
- Socket 耗尽

支持：

- CentOS
- Ubuntu
- Debian
- RHEL
- Rocky Linux
- openEuler
- 麒麟操作系统
- 其他 Linux 发行版

本 Playbook 遵循：

- 第一性原理（First Principles）
- 证据驱动（Evidence-Based）
- 实时调查（Real-time Investigation）

所有 Root Cause 必须基于实时数据验证。

---

# 第一性原理（First Principles）

Linux 是所有应用运行的基础。

所有应用最终都会消耗：

```text
            Request
                │
                ▼
        Application Process
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
      CPU    Memory     IO
        │       │        │
        └───────┼────────┘
                ▼
            Linux Kernel
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
      CPU    Disk      Network
```

因此：

```
CPU 高

≠

CPU 是 Root Cause
```

必须回答：

CPU 为什么高？

Disk 为什么忙？

Network 为什么慢？

---

# 常见现象（Symptoms）

例如：

- CPU 使用率高
- Load Average 持续增长
- IO Wait 高
- Disk Busy
- Memory 持续增长
- Swap 使用
- TCP Retransmission
- Packet Loss
- Context Switch 高
- Interrupt 高
- Socket 数过多

---

# Agent 调查策略（Investigation Strategy）

收到 Linux 性能问题时，应首先回答：

1. CPU 是否真正繁忙？
2. 是否 IO 等待？
3. 是否内存不足？
4. 是否网络异常？
5. 是否磁盘瓶颈？
6. 是否线程切换过多？
7. 是否文件句柄耗尽？

如果可以调用：

- top
- vmstat
- iostat
- pidstat
- sar
- mpstat
- ss
- netstat
- perf
- eBPF

应优先获取实时数据。

不要只根据 CPU 百分比或 Load Average 下结论。

---

# 建议收集的数据（Evidence）

## CPU

建议执行：

```bash
top

mpstat -P ALL 1

pidstat -u 1
```

关注：

- us
- sy
- id
- wa
- st

重点：

- CPU 是否真正繁忙
- 是否大量 IO Wait
- 是否 SoftIRQ 高

---

## Memory

建议执行：

```bash
free -h

vmstat 1

cat /proc/meminfo
```

关注：

- Free
- Available
- Buffers
- Cached
- Swap
- Dirty

重点：

不要只看 Free。

应重点关注：

Available Memory。

---

## Disk

建议执行：

```bash
iostat -x 1

pidstat -d 1
```

关注：

- util
- await
- svctm（旧版本）
- r/s
- w/s
- rkB/s
- wkB/s

重点：

```
await

>>

svctm
```

说明：

请求排队。

---

## Network

建议执行：

```bash
sar -n DEV 1

sar -n TCP 1

ss -s

netstat -s
```

关注：

- Throughput
- Retransmission
- Active Connection
- Passive Connection
- Listen Queue

---

## Process

建议执行：

```bash
ps -ef

top -H

pidstat -u -r -d -w 1
```

关注：

- CPU
- Memory
- IO
- Context Switch

---

## Filesystem

建议执行：

```bash
df -h

df -i

mount
```

关注：

- 空间
- inode
- 挂载方式

---

## File Descriptor

建议执行：

```bash
ulimit -n

cat /proc/sys/fs/file-max

lsof | wc -l
```

关注：

是否达到限制。

---

# 推荐执行命令（Commands）

CPU：

```bash
top

mpstat -P ALL 1

pidstat -u 1
```

Memory：

```bash
free -h

vmstat 1
```

Disk：

```bash
iostat -x 1
```

Network：

```bash
sar -n DEV 1

ss -s
```

Socket：

```bash
ss -ant

netstat -an
```

Process：

```bash
pidstat

top -H
```

---

# 推荐分析流程（Workflow）

```text
确认性能下降
        │
        ▼
CPU
        │
        ▼
Memory
        │
        ▼
Disk
        │
        ▼
Network
        │
        ▼
Process
        │
        ▼
Kernel
        │
        ▼
Root Cause
```

不要跳过任何层。

---

# 常见瓶颈分析（Analysis）

## CPU 高

检查：

```bash
top

mpstat

pidstat
```

分析：

CPU 消耗在哪个进程？

用户态还是内核态？

第一性原理：

CPU 高只是资源使用结果。

必须找到真正消耗 CPU 的代码或系统调用。

---

## Load Average 高

检查：

```bash
uptime
```

不要误认为：

Load 高

就是 CPU 高。

Load 包括：

- Runnable
- Uninterruptible IO

必须继续分析：

CPU

还是

IO。

---

## IO Wait 高

检查：

```bash
iostat -x
```

重点：

- await
- util

第一性原理：

IO Wait 表示 CPU 在等待 IO 完成。

真正瓶颈通常是磁盘或存储。

---

## Memory 高

检查：

```bash
free -h

vmstat
```

重点：

- Available
- Swap

不要只看：

Used。

Linux 会缓存文件。

---

## Swap

检查：

```bash
vmstat
```

关注：

si

so

第一性原理：

Swap 会导致访问磁盘。

性能可能下降数十倍。

---

## Context Switch

检查：

```bash
vmstat

pidstat -w
```

第一性原理：

线程切换本身消耗 CPU。

大量锁竞争可能导致 Context Switch 激增。

---

## Disk Busy

检查：

```bash
iostat -x
```

重点：

util

如果：

```
util

≈100%
```

说明：

磁盘已接近饱和。

---

## Network

检查：

```bash
sar -n DEV

netstat -s
```

关注：

- Retransmission
- Drop
- Error

第一性原理：

TCP 重传最终表现为：

响应时间增加。

---

## Socket

检查：

```bash
ss -s
```

关注：

- ESTAB
- TIME_WAIT
- CLOSE_WAIT

大量：

TIME_WAIT

可能说明：

短连接过多。

---

## File Descriptor

检查：

```bash
lsof

ulimit
```

分析：

FD 是否耗尽。

---

## NUMA

检查：

```bash
numactl --hardware
```

分析：

是否跨 NUMA 访问。

---

## Interrupt

检查：

```bash
cat /proc/interrupts
```

分析：

是否存在：

单核中断热点。

---

# Root Cause 判定标准（Root Cause Criteria）

只有满足以下条件，才能确认 Linux 是 Root Cause：

- IO Wait 长时间过高且磁盘饱和。
- Swap 导致性能下降。
- CPU 被系统调用或中断占满。
- TCP 重传明显增加。
- File Descriptor 耗尽。
- NUMA 导致访问延迟。
- Kernel Resource 耗尽。

否则：

Linux

只是表现层。

应继续分析：

应用、

数据库、

缓存、

MQ。

---

# 常见 Root Cause

包括：

- CPU Hot Process
- IO Wait
- Disk Saturation
- Swap
- Memory Pressure
- TCP Retransmission
- File Descriptor Exhaustion
- Socket Backlog
- NUMA
- Interrupt Hotspot

---

# 优化建议（Recommendations）

建议按以下优先级：

1. 修复应用问题
2. 修复 IO 瓶颈
3. 修复网络问题
4. 优化线程模型
5. 调整系统参数（sysctl）
6. 调整文件句柄限制
7. 增加资源
8. 扩容服务器

不要默认建议升级硬件。

---

# 组件退出条件（Exit Criteria）

满足以下任一条件：

- 已确认 Linux 不是 Root Cause，应继续分析应用、中间件或数据库。
- 已确认 Linux 是 Root Cause。
- 当前缺少关键指标数据。
- 无法继续验证，应停止推断。

---

# 输出要求（Output）

最终输出至少包含：

## 问题现象（Symptoms）

例如：

CPU 使用率达到 95%，P99 响应时间增加。

---

## 已收集证据（Evidence）

包括：

- CPU
- Memory
- Disk
- Network
- Process
- Filesystem
- Socket

---

## 分析过程（Reasoning）

说明：

- 是否排除 CPU
- 是否排除 IO
- 是否排除 Memory
- 是否排除 Network

---

## 根因（Root Cause）

必须提供：

- 证据
- 原理
- 验证过程

---

## 第一性原理解释

解释：

为什么 Linux 内核机制导致当前性能下降。

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
- CPU
- Load Average
- IO Wait
- Disk Util
- Memory
- Swap
- TCP Retransmission
- Error Rate

确认 Linux 层优化是否真正改善性能。