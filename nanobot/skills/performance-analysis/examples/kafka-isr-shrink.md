# Kafka ISR Shrink

## 现象

生产延迟升高、acks 等待变长，Kafka ISR 频繁收缩或 Under Replicated Partitions 增加。

## 必收证据

- Kafka：UnderReplicatedPartitions、ISR shrink/expand、request latency、leader/follower 状态。
- Broker：磁盘 IO、网络、GC、CPU。
- Producer：acks、retries、timeout、error log。

## 判定

已确认需要同时满足：ISR 异常与生产延迟同窗口发生；慢 broker 或网络/磁盘瓶颈存在；producer 等待或重试同步升高。

## 建议

修复慢 broker、磁盘或网络；评估副本和 acks 策略；验证 ISR 稳定性、producer P99、错误率。
