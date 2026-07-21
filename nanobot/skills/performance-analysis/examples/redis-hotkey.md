# Redis Hot Key

## 现象

Redis 相关接口 P99 升高，单个 Redis 实例或分片 CPU/网络明显高于其他实例。

## 必收证据

- Trace：Redis span 占请求主要耗时。
- Redis：`INFO commandstats`、latency、slowlog、实例 CPU/网络。
- Key 维度：热点 key 采样、客户端日志、业务参数分布。生产环境避免未授权全量扫描。

## 判定

已确认需要同时满足：少量 key 访问占比异常；热点实例资源升高；应用慢请求与这些 key 或业务参数一致。

## 建议

本地缓存、读副本、key 打散、TTL 抖动或业务访问模式调整；验证热点实例负载和 Redis span P99。
