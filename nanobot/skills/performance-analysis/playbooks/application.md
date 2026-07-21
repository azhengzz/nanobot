# Application 性能分析 Playbook

## 适用范围

用于分析 Java / Go / Python / Node.js 等应用层性能问题，包括接口延迟升高、吞吐下降、错误率升高、线程池耗尽、连接池耗尽、异步队列堆积、GC/Runtime 停顿、下游依赖慢、日志阻塞等。

## 第一性原理

应用层处理请求通常经历：

```text
Gateway
  -> Route / Middleware
  -> Handler
  -> Business Logic
  -> Thread / Coroutine / Event Loop
  -> Connection Pool
  -> Downstream: Redis / MQ / DB / HTTP / Object Storage
```

接口慢不等于应用代码慢。必须拆分应用自身耗时和等待下游耗时。

## 优先证据

1. Trace：接口 span、内部方法 span、下游 span、错误 span。
2. Metrics：QPS/TPS、P50/P95/P99、错误率、线程池、连接池、队列长度、GC/runtime、CPU/memory。
3. Logs：慢请求日志、超时日志、异常栈、限流/熔断日志。
4. Diagnostic：thread dump、pprof、heap dump、event loop lag、async profiler。
5. Config：超时、连接池、线程池、队列、限流、重试、熔断配置。

## 调查流程

```text
确认问题接口和时间窗口
  -> 用 Trace 拆分耗时
  -> 判断耗时在应用自身还是下游等待
  -> 检查错误率、超时、重试、限流
  -> 检查线程池/协程/event loop/连接池/队列
  -> 检查 Runtime 和 Linux 资源
  -> 继续深入下游组件或确认应用层根因
```

## 必查问题

- 慢请求是否集中在少数接口、少数租户、少数参数或少数实例？
- Trace 中最大耗时 span 是业务代码、锁等待、连接池等待还是下游调用？
- 是否存在重试放大流量？
- 线程池、连接池、队列是否接近上限？
- GC、Stop-the-world、event loop lag、GIL/锁竞争是否与延迟上升时间一致？
- 日志是否同步写盘或异常量暴增？
- CPU 高是应用计算、序列化、加解密、压缩、正则、JSON 处理，还是系统调用/IO wait？

## Root Cause 判定标准

满足以下之一，并由至少两个数据源交叉验证，才能确认应用层为根因：

- Trace 显示应用内部 span 占主要耗时，且日志/诊断数据指向同一代码路径。
- 线程池、连接池或队列达到瓶颈，且延迟/超时随等待时间同步升高。
- Runtime 停顿、锁竞争或 event loop 阻塞与 P95/P99 上升时间一致。
- 重试、超时、限流或熔断配置导致请求放大或排队。
- 应用实例负载明显不均，并与调度、连接复用或热点流量一致。

如果耗时主要在下游 span，应退出应用层并继续分析对应组件。

## 优化建议优先级

1. 修复异常代码路径或低效算法。
2. 减少下游调用次数和串行等待。
3. 调整超时、重试、熔断，避免放大流量。
4. 修正线程池、连接池和队列容量。
5. 优化序列化、日志、压缩、加解密等 CPU 热点。
6. 优化 Runtime 参数。
7. 最后再考虑扩容。

## 验证方案

验证优化后至少对比：TPS/QPS、P50/P95/P99、错误率、最大耗时 span、线程池/连接池等待、队列长度、GC/runtime 指标、CPU、内存、下游调用耗时。
