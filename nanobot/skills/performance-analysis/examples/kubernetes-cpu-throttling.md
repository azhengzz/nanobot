# Kubernetes CPU Throttling

## 现象

压测期间接口 P95/P99 上升，Pod CPU 使用率未必达到 limit，但响应时间抖动明显。

## 必收证据

- Prometheus：`container_cpu_cfs_throttled_seconds_total`、`container_cpu_cfs_periods_total`、CPU usage、接口 P95/P99。
- Kubernetes：Pod requests/limits、QoS、restart、events。
- 应用：Trace 或日志确认慢请求发生在同一 Pod/时间窗口。

## 判定

已确认需要同时满足：throttling ratio 在问题窗口升高；P95/P99 同窗口升高；Pod CPU limit 偏低或线程争抢能解释排队。

## 建议

优先修正 CPU limit/request 或降低 CPU 热点；验证 throttling ratio、P95/P99、错误率是否下降。
