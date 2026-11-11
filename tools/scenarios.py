# -*- coding: utf-8 -*-
"""跑完实验2 的全部抓包场景，每个场景一份 pcapng + 一份日志。

场景：
  S1  TCP 正常交互（建立/数据/释放）
  S2  TCP 先 client 后 server（RST）
  S3  TCP 交互中强杀 client（server 侧观察 + netstat 状态）
  S4  TCP RTT（复用 S1，另外补一次多轮数据）
  D1  UDP 头字段
  D2  UDP 先 client 后 server
  D3  UDP 2000 字节大报文（看是否分片）
  D4  UDP server 不在线（ICMP port unreachable）
"""
import os, subprocess, sys, time, json
from scapy.all import AsyncSniffer, wrpcapng, TCP, UDP, IP, ICMP, Raw

PY = sys.executable
BASE = r"C:\Users\iroha\Desktop\lab2_251006115"
CODE = os.path.join(BASE, "code")
PCAP = os.path.join(BASE, "pcap")
OUT = os.path.join(BASE, "out")
LOOP = r"\Device\NPF_Loopback"
os.makedirs(PCAP, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

LOGS = {}

def log(name, msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    LOGS.setdefault(name, []).append(line)
    print(line)

def flush(name):
    with open(os.path.join(OUT, f"{name}.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOGS.get(name, [])))

def start_srv(script, name):
    p = subprocess.Popen([PY, "-u", script], cwd=CODE,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log(name, f"server started: {script} pid={p.pid}")
    time.sleep(1.2)
    return p

def stop(p, name):
    try:
        p.terminate(); time.sleep(0.3); p.kill()
    except Exception:
        pass
    try:
        out = p.stdout.read() if p.stdout else ""
        if out.strip():
            log(name, "server output: " + out.strip().replace("\n", " | "))
    except Exception:
        pass

def run_client(script, name, args=(), stdin_text=None, timeout=30):
    cmd = [PY, "-u", script] + [str(a) for a in args]
    log(name, "client: " + " ".join(cmd[1:]))
    try:
        r = subprocess.run(cmd, cwd=CODE, input=stdin_text if stdin_text is not None else "",
                           capture_output=True, text=True, timeout=timeout)
        out = (r.stdout or "").strip()
        log(name, f"client rc={r.returncode} stdout={out!r}")
        if r.stderr.strip():
            log(name, "client stderr=" + r.stderr.strip()[:400])
        return r
    except subprocess.TimeoutExpired:
        log(name, "client TIMEOUT")
        return None

def capture(name, bpf, body, pre=1.0, post=1.5):
    sn = AsyncSniffer(iface=LOOP, filter=bpf, store=True)
    log(name, f"capture start bpf='{bpf}'")
    sn.start()
    time.sleep(pre)
    body()
    time.sleep(post)
    pkts = sn.stop()
    path = os.path.join(PCAP, f"{name}.pcapng")
    wrpcapng(path, pkts)
    log(name, f"packets={len(pkts)} saved={os.path.basename(path)} size={os.path.getsize(path)}")
    return pkts

def summarize(name, pkts):
    rows = []
    t0 = float(pkts[0].time) if pkts else 0.0
    for i, p in enumerate(pkts, 1):
        proto, info = "?", ""
        if TCP in p:
            proto = "TCP"
            t = p[TCP]
            info = f"{t.sport}->{t.dport} flags={t.flags} seq={t.seq} ack={t.ack} win={t.window} len={len(bytes(t.payload))}"
        elif UDP in p:
            proto = "UDP"
            u = p[UDP]
            info = f"{u.sport}->{u.dport} len={u.len} chksum={u.chksum} payload={len(bytes(u.payload))}"
        elif ICMP in p:
            proto = "ICMP"
            info = f"type={p[ICMP].type} code={p[ICMP].code}"
        rows.append(f"{i:3d}  t={float(p.time)-t0:8.6f}  {proto:4s} {p[IP].src}->{p[IP].dst}  {info}")
    with open(os.path.join(OUT, f"{name}_packets.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    log(name, "packet summary written")

# ---------------------------------------------------------------- S1
def s1():
    name = "S1_tcp_normal"
    srv = start_srv("TCPServer.py", name)
    def body():
        run_client("TCPClient.py", name, stdin_text="hello tcp 251006115\n")
    pkts = capture(name, "tcp port 12000", body)
    stop(srv, name); summarize(name, pkts); flush(name)

# ---------------------------------------------------------------- S2
def s2():
    name = "S2_tcp_reversed"
    def body():
        run_client("TCPClient.py", name, stdin_text="client first\n", timeout=20)
        time.sleep(1.0)
        srv = start_srv("TCPServer.py", name)
        time.sleep(1.0)
        stop(srv, name)
    pkts = capture(name, "tcp port 12000", body, post=1.0)
    summarize(name, pkts); flush(name)

# ---------------------------------------------------------------- S3
def s3():
    name = "S3_tcp_kill_client"
    srv = start_srv("TCPServer.py", name)
    def body():
        cli = subprocess.Popen([PY, "-u", "tcp_client_hold.py"], cwd=CODE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log(name, f"client hold pid={cli.pid}")
        time.sleep(3)
        subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        log(name, "kill client (SIGKILL)")
        cli.kill()
        cli.wait()
        for k in range(3):
            time.sleep(10)
            r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
            lines = [l for l in r.splitlines() if ":12000" in l]
            log(name, f"t+{(k+1)*10}s netstat: " + (" | ".join(lines) if lines else "(no :12000 entries)"))
    pkts = capture(name, "tcp port 12000", body, post=2.0)
    stop(srv, name); summarize(name, pkts); flush(name)

# ---------------------------------------------------------------- S4
def s4():
    name = "S4_tcp_rtt"
    srv = start_srv("TCPServer.py", name)
    def body():
        for msg in ["round one", "round two", "round three"]:
            run_client("TCPClient.py", name, stdin_text=msg + "\n")
            time.sleep(0.5)
    pkts = capture(name, "tcp port 12000", body)
    stop(srv, name); summarize(name, pkts); flush(name)

# ---------------------------------------------------------------- D1
def d1():
    name = "D1_udp_header"
    srv = start_srv("UDPServer.py", name)
    def body():
        run_client("UDPClient.py", name, stdin_text="hello udp 251006115\n")
    pkts = capture(name, "udp port 5201", body)
    stop(srv, name); summarize(name, pkts); flush(name)

# ---------------------------------------------------------------- D2
def d2():
    name = "D2_udp_reversed"
    def body():
        run_client("UDPClient.py", name, stdin_text="no server yet\n", timeout=8)
        time.sleep(1.0)
        srv = start_srv("UDPServer.py", name)
        run_client("UDPClient.py", name, stdin_text="server now up\n")
        stop(srv, name)
    pkts = capture(name, "udp port 5201", body, post=1.0)
    summarize(name, pkts); flush(name)

# ---------------------------------------------------------------- D3
def d3():
    name = "D3_udp_2000bytes"
    payload = os.path.join(BASE, "code", "payload_2000.bin")
    if not os.path.exists(payload):
        with open(payload, "wb") as f:
            f.write(bytes((i % 26) + 65 for i in range(2000)))
    srv = start_srv("UDPServer.py", name)
    def body():
        run_client("udp_client_file.py", name, args=[payload])
    pkts = capture(name, "udp port 5201", body)
    stop(srv, name); summarize(name, pkts); flush(name)

# ---------------------------------------------------------------- D4
def d4():
    name = "D4_udp_no_server"
    def body():
        run_client("UDPClient.py", name, stdin_text="nobody here\n", timeout=8)
        time.sleep(1.0)
    pkts = capture(name, "udp port 5201 or icmp", body, post=1.0)
    summarize(name, pkts); flush(name)

if __name__ == "__main__":
    only = sys.argv[1:] or ["s1", "s2", "s3", "s4", "d1", "d2", "d3", "d4"]
    for key in only:
        globals()[key]()
        time.sleep(1.0)
    print("ALL DONE")
