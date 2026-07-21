# JVM Full GC

## 现象

Java 服务 P99 出现周期性尖刺，错误率或超时与 GC 时间点一致。

## 必收证据

- GC log：Full GC 时间、暂停时长、原因、回收前后堆大小。
- JVM metrics：heap、old gen、allocation rate、GC pause。
- 应用 Trace/日志：慢请求与 GC pause 时间对齐。

## 判定

已确认需要同时满足：Full GC pause 与 P99 尖刺同窗口；暂停时长足以解释请求延迟；堆/分配/对象存活能解释 GC 原因。

## 建议

先定位对象分配和泄漏，再调整堆、GC 参数或缓存策略；验证 GC pause、P99、吞吐。
