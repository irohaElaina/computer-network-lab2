#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""webget.py —— 手写 HTTP/1.1 客户端（只允许 Python 标准库 socket）

用法：
    python webget.py <host> <path> [port]
    python webget.py www.bjfu.edu.cn /
    python webget.py www.bjfu.edu.cn /index.html 80

设计要点（对应实验 T1–T5）：
  T1  recv 必须放进循环里，因为 TCP 是字节流，一次 recv 只保证“拿到一部分”；
      循环结束只有两种依据：
        (a) 响应头里有 Content-Length —— 收够这么多字节就停；
        (b) 没有 Content-Length —— 只能等对端关闭连接（recv 返回 b''），
            所以请求必须带 Connection: close，否则对端一直不关，循环不会结束。
      settimeout(10) 是兜底：坏服务器既不关连接也不发够数据时，别把程序挂死。
  T2  按 CRLFCRLF 把响应切成「状态行+响应头」和「body」；body 用 wb 二进制写盘。
      文本模式写图片会毁文件：解码时 '\r\n' 会被换成 '\n'、非法字节会被替换，
      再编码回去就和原始字节不一致了。
  T3  host / path / port 全部来自命令行参数，不写死。
  T4  打印 recv 的调用次数与每次字节数，用来解释“响应不是一次性到齐的”。
  T5  与抓包对照（见报告）。

GitHub: https://github.com/<你的用户名>/<仓库名>    # 建库后替换这里
"""

import re
import socket
import sys
import time

TIMEOUT = 10        # 秒；防止挂死在坏服务器上
RECV_SIZE = 4096    # 每次 recv 的缓冲区大小


def usage_and_exit():
    print("usage: python webget.py <host> <path> [port]")
    print("  e.g. python webget.py www.bjfu.edu.cn /")
    sys.exit(1)


def build_request(host, path):
    """构造最小但合规的 HTTP/1.1 请求。

    Connection: close 是 T1 的前提：没有 Content-Length 时靠对端关闭来结束 recv 循环。
    """
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "User-Agent: webget/1.0 (computer-network lab2)\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode()


def fetch(host, port, raw_request):
    """发出请求并按 T1 的两条终止条件收完整个响应。

    返回 (raw_bytes, recv_sizes)，raw_bytes 是完整响应（响应头 + body）。
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    sock.connect((host, port))
    sock.sendall(raw_request)

    buf = bytearray()
    recv_sizes = []
    head_end = -1          # 响应头结束位置（\r\n\r\n 之后）
    content_length = None  # 从响应头里解析出来的 body 长度

    while True:
        try:
            chunk = sock.recv(RECV_SIZE)
        except socket.timeout:
            # 超时说明对端既没关连接也没给够数据，按已收到的内容处理
            print(f"[warn] recv 超时（{TIMEOUT}s），按已收到的 {len(buf)} 字节处理")
            break
        if not chunk:
            # 终止条件 (b)：对端关闭，EOF
            break
        buf.extend(chunk)
        recv_sizes.append(len(chunk))

        # 第一次凑齐响应头时，解析 Content-Length（如果有）
        if head_end < 0:
            idx = bytes(buf).find(b"\r\n\r\n")
            if idx != -1:
                head_end = idx + 4
                m = re.search(rb"(?i)\r\ncontent-length:\s*(\d+)", bytes(buf[:head_end]))
                if m:
                    content_length = int(m.group(1))

        # 终止条件 (a)：body 已经收够 Content-Length 指定的字节数
        if content_length is not None and head_end >= 0:
            if len(buf) - head_end >= content_length:
                break

    sock.close()
    return bytes(buf), recv_sizes


def split_response(raw):
    """T2：按空行把「状态行 + 响应头」和「body」分开。"""
    idx = raw.find(b"\r\n\r\n")
    if idx == -1:
        return raw.decode("iso-8859-1"), b""
    head = raw[:idx].decode("iso-8859-1")
    body = raw[idx + 4:]
    return head, body


def parse_head(head):
    """返回 (状态行, 状态码, [(头名, 头值), ...])"""
    lines = head.split("\r\n")
    status_line = lines[0] if lines else ""
    m = re.match(r"HTTP/\d\.\d\s+(\d{3})", status_line)
    status_code = int(m.group(1)) if m else 0
    headers = []
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers.append((k.strip(), v.strip()))
    return status_line, status_code, headers


def dechunk(body):
    """若响应是 Transfer-Encoding: chunked，把分块编码还原成原始字节。"""
    out = bytearray()
    i = 0
    while True:
        j = body.find(b"\r\n", i)
        if j == -1:
            break
        try:
            size = int(body[i:j].split(b";")[0], 16)
        except ValueError:
            break
        if size == 0:
            break
        out.extend(body[j + 2: j + 2 + size])
        i = j + 2 + size + 2
    return bytes(out)


def main():
    if len(sys.argv) < 3:
        usage_and_exit()

    host = sys.argv[1]
    path = sys.argv[2]
    if not path.startswith("/"):
        path = "/" + path
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 80

    req = build_request(host, path)
    t0 = time.time()
    raw, recv_sizes = fetch(host, port, req)
    elapsed = time.time() - t0

    head, body = split_response(raw)
    status_line, status_code, headers = parse_head(head)

    print("=" * 60)
    print(f"请求: GET {path} HTTP/1.1   Host: {host}   port={port}")
    print(f"状态行: {status_line}")
    print(f"状态码: {status_code}")
    print("-" * 60)
    print("响应头:")
    for k, v in headers:
        print(f"  {k}: {v}")

    # 处理 chunked，保证落盘的 body 是原始内容
    hdr = {k.lower(): v for k, v in headers}
    if hdr.get("transfer-encoding", "").lower() == "chunked":
        body = dechunk(body)
        print("[info] 响应为 chunked 编码，已还原")

    # T2：body 用二进制模式写文件
    name = path.strip("/").replace("/", "_") or "index.html"
    out_name = f"body_{host}_{name}"
    with open(out_name, "wb") as f:      # wb：文本模式会毁掉图片等二进制内容
        f.write(body)
    print("-" * 60)
    print(f"body 已保存: {out_name}  ({len(body)} 字节)")
    print(f"body 预览(前 120 字节): {body[:120]!r}")

    # T4：recv 统计
    print("-" * 60)
    print(f"recv 调用次数: {len(recv_sizes)}")
    print(f"每次字节数: {recv_sizes}")
    print(f"总计: {sum(recv_sizes)} 字节，用时 {elapsed:.3f}s")
    print("=" * 60)

    return 0 if status_code == 200 else 0


if __name__ == "__main__":
    sys.exit(main())
