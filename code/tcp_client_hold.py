# -*- coding: utf-8 -*-
"""S3 专用：连上服务器、发一句，然后保持连接 60 秒，方便外部强杀进程。"""
import socket, time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 12000))
s.sendall(b"hold the line 251006115")
print("connected, waiting to be killed", flush=True)
time.sleep(60)
s.close()
