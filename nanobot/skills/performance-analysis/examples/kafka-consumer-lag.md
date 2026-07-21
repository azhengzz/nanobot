# Kafka Consumer Lag

## 现象

异步处理延迟升高，消息积压，消费端处理结果晚于压测流量峰值。

## 必收证据

- Kafka：consumer lag、rebalance、partition 分布、produce/consume rate。
- Consumer：处理耗时、错误率、线程池/批量参数、下游调用耗时。
- 下游：DB/Redis/HTTP span 或指标。

## 判定

已确认需要同时满足：lag 持续增长；消费速率低于生产速率；消费端或下游瓶颈能解释处理能力不足。

## 建议

先修消费逻辑或下游瓶颈，再调整 batch、并发、分区和重试；验证 lag 收敛速度和端到端延迟。
