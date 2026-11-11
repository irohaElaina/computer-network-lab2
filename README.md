# 计算机网络实验2 —— HTTP 客户端与 TCP/UDP 协议分析

学号：251006115　姓名：郭久铭　班级：网工25

## 目录

| 路径 | 说明 |
|---|---|
| `code/UDPServer.py` | 教材第2章 UDP 服务器示例（监听 5201，实验 A1 要求） |
| `code/UDPClient.py` | 教材第2章 UDP 客户端示例（无 connect） |
| `code/TCPServer.py` | 教材第2章 TCP 服务器示例（监听 12000） |
| `code/TCPClient.py` | 教材第2章 TCP 客户端示例（有 connect） |
| `code/webget.py` | 手写 HTTP/1.1 客户端（Part D，T1–T5） |
| `report/` | Word 报告 |
| `pcap/` | 抓包文件（251006115郭久铭-lab2.pcapng） |

## 运行

```powershell
# A1 UDP
python code/UDPServer.py          # 终端1
python code/UDPClient.py          # 终端2，输入一句话

# A2 TCP
python code/TCPServer.py          # 终端1
python code/TCPClient.py          # 终端2

# Part D webget
python code/webget.py www.bjfu.edu.cn /
python code/webget.py www.bjfu.edu.cn /index.html 80
```

## webget 要点

- `recv` 放在循环里：TCP 是字节流，一次 `recv` 只保证拿到一部分；
- 结束条件两条：有 `Content-Length` 就收够为止；没有就等对端关闭（请求带 `Connection: close`）；
- `settimeout(10)` 兜底，避免坏服务器把程序挂死；
- body 用 `wb` 二进制写盘，文本模式会破坏图片等二进制内容。

## 环境

Python 3.12.10（Windows 11），仅使用标准库 `socket`。
