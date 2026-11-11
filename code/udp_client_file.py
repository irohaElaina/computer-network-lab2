# -*- coding: utf-8 -*-
"""D3 专用：从文件读取内容，一次性作为 UDP 报文发出（不在代码里硬编码 2000 字节）。

用法：python udp_client_file.py payload_2000.bin
"""
import socket, sys

if len(sys.argv) < 2:
    print("usage: python udp_client_file.py <file>")
    sys.exit(1)

with open(sys.argv[1], "rb") as f:
    data = f.read()

print("file bytes:", len(data), flush=True)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(5)
s.sendto(data, ("127.0.0.1", 5201))
try:
    reply, addr = s.recvfrom(4096)
    print("reply bytes:", len(reply), "from", addr, flush=True)
except socket.timeout:
    print("no reply (timeout)", flush=True)
s.close()
