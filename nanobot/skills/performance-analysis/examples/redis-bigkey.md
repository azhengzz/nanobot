# Redis Big Key

## 现象

Redis 命令偶发慢，网络输出或客户端反序列化耗时升高，接口 P99 长尾明显。

## 必收证据

- Trace：Redis span 长尾与具体命令相关。
- Redis：slowlog、latency、memory stats、commandstats。
- Key 诊断：授权后采样 `MEMORY USAGE` 或离线 big key 报告。

## 判定

已确认需要同时满足：大对象 key 存在；相关命令在慢日志或 Trace 中出现；网络/CPU/序列化耗时与时间窗口一致。

## 建议

拆 key、分页/限长读取、压缩策略评估、避免无界 `HGETALL`/大范围 `ZRANGE`；验证 slowlog 和接口 P99。
