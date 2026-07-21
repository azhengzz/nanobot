# Elasticsearch Hot Node

## 现象

查询或写入 P99 升高，少数 ES 节点 CPU、heap、IO 或 search/write queue 明显高于其他节点。

## 必收证据

- ES：node stats、hot threads、thread pool queue/rejected、shard 分布。
- Query：慢查询日志、请求 Trace、索引和 shard 命中。
- OS：CPU、IO wait、磁盘 util、网络。

## 判定

已确认需要同时满足：热点节点指标异常；热点 shard/query/索引能解释负载不均；业务慢请求命中该节点或 shard。

## 建议

调整 shard 分布、routing、查询条件、索引设计或冷热分层；验证节点负载均衡和查询 P99。
