# -*- coding: utf-8 -*-
"""UDPClient.py —— 教材第2章 UDP 客户端示例

与 TCPClient 的关键差别：**没有 connect()**。
UDP 是无连接协议，sendto() 每次自己带上 (主机, 端口) 就能发，
收到的报文也用 recvfrom() 连对端地址一起拿回来。

运行：python UDPClient.py
"""

from socket import *

serverName = '127.0.0.1'    # 同机运行；虚拟机场景填 server 的 IP
serverPort = 5201

clientSocket = socket(AF_INET, SOCK_DGRAM)          # SOCK_DGRAM = UDP
message = input('Input lowercase sentence:')        # 这里没有 connect
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()
