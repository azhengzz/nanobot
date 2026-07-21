# MySQL LIKE Query

## 现象

搜索接口慢，Rows Examined 远大于 Rows Sent，数据库 CPU 或 IO 增高。

## 必收证据

- Trace：SQL span 占请求主要耗时。
- Slow log：query_time、lock_time、rows_examined、rows_sent。
- `EXPLAIN`：type、key、rows、Extra。

## 判定

已确认需要同时满足：慢 SQL 是主要耗时；`LIKE '%keyword%'` 或函数表达式导致索引不可用；Rows Examined 与延迟升高一致。

## 建议

改前缀匹配、全文索引、倒排索引或搜索引擎；验证 Rows Examined、SQL P95/P99、接口 P99。
