# -*- coding: utf-8 -*-
"""UDPServer.py —— 教材 Kurose & Ross 第2章 2.7 节 UDP 服务器示例

改动：只把监听端口改成 5201（实验 A1 要求），其余保持教材原样。
GitHub: https://github.com/<你的用户名>/<仓库名>    # 建库后替换这里

运行：python UDPServer.py
"""

from socket import *

serverPort = 5201
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive')

# 无连接：没有 accept/listen，来一个数据报就处理一个，处理完继续等
while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
    print('recv from', clientAddress, '->', modifiedMessage)
