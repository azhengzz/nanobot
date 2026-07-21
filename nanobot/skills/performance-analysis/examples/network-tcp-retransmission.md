# Network TCP Retransmission

## 现象

跨服务调用 P99 升高，偶发超时，应用 CPU/DB/缓存指标不能解释延迟。

## 必收证据

- Linux：`sar -n TCP`、`netstat -s`、`ss -ti`、网卡 drop/error。
- Metrics：服务调用耗时、错误率、重试次数。
- Topology：源/目标 Pod、Node、AZ、CNI、LB 路径。

## 判定

已确认需要同时满足：重传/丢包在问题窗口升高；调用延迟或重试同窗口升高；应用和下游处理耗时不能解释等待。

## 建议

定位链路段、CNI/MTU/LB/节点网卡问题；验证 retransmission、timeout、P99。
