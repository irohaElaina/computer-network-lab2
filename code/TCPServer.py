# -*- coding: utf-8 -*-
"""TCPServer.py —— 教材第2章 TCP 服务器示例

GitHub: https://github.com/<你的用户名>/<仓库名>    # 建库后替换这里

运行：python TCPServer.py
"""

from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)     # SOCK_STREAM = TCP
serverSocket.bind(('', serverPort))
serverSocket.listen(1)                          # 最多排队 1 个未处理的连接
print('The server is ready to receive')

# 面向连接：accept() 为每个客户返回一条新连接（connectionSocket），
# 关闭 connectionSocket 只结束这条连接，监听套接字继续等下一个客户。
while True:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024).decode()
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence.encode())
    connectionSocket.close()
    print('served', addr, '->', capitalizedSentence)
