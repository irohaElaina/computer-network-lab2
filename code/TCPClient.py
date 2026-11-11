# -*- coding: utf-8 -*-
"""TCPClient.py —— 教材第2章 TCP 客户端示例

与 UDPClient 的关键差别：**有 connect()**。
connect() 触发三次握手，之后 send()/recv() 都在这一条已建立的连接上做，
不再需要每次都写对端地址。

运行：python TCPClient.py
"""

from socket import *

serverName = '127.0.0.1'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)     # SOCK_STREAM = TCP
clientSocket.connect((serverName, serverPort))  # 这一步 UDP 没有：建立连接
sentence = input('Input lowercase sentence:')
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)
print('From Server: ', modifiedSentence.decode())
clientSocket.close()                            # 关闭 -> FIN，进入挥手
