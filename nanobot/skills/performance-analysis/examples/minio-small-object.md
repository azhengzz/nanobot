# MinIO Small Object

## 现象

对象存储请求量高但吞吐不高，小文件上传/下载 P99 升高，磁盘或元数据操作压力明显。

## 必收证据

- MinIO：S3 request latency、errors、drive stats、heal/erasure metrics。
- Client Trace：对象大小、请求次数、重试、并发。
- OS/Network：磁盘 IOPS、await、util、网络吞吐和重传。

## 判定

已确认需要同时满足：小对象请求占比高；MinIO/磁盘 IOPS 或元数据压力与 P99 同窗口升高；客户端重试或等待同步增加。

## 建议

合并小对象、批量写入、调整并发和重试、优化磁盘/网络；验证请求 P99、IOPS、错误率。
