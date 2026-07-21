# MySQL Lock Wait

## 现象

接口响应突然拉长，慢查询 lock_time 增加，部分请求超时。

## 必收证据

- `SHOW FULL PROCESSLIST`：等待状态和阻塞 SQL。
- `SHOW ENGINE INNODB STATUS`：LATEST DETECTED DEADLOCK、锁等待链。
- 应用 Trace/日志：事务入口、耗时、错误。

## 判定

已确认需要同时满足：业务慢请求与锁等待同窗口发生；能找到 blocker 和 waiter；事务或 SQL 路径能解释锁持有时间。

## 建议

缩短事务、固定加锁顺序、补索引减少锁范围、拆分热点更新；验证 lock_time、deadlock、接口 P99。
