import subprocess, sys, time, os
from scapy.all import AsyncSniffer, wrpcapng, TCP, UDP

PY = sys.executable
CODE = r"C:\Users\iroha\Desktop\lab2_251006115\code"
OUT = r"C:\Users\iroha\Desktop\lab2_251006115\pcap"
os.makedirs(OUT, exist_ok=True)

srv = subprocess.Popen([PY, "-u", "TCPServer.py"], cwd=CODE,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
time.sleep(1.0)

sn = AsyncSniffer(iface=r"\Device\NPF_Loopback", filter="tcp port 12000", store=True)
sn.start()
time.sleep(1.0)

cli = subprocess.run([PY, "-u", "TCPClient.py"], cwd=CODE, input="hello loopback 251006115\n",
                     capture_output=True, text=True, timeout=20)
print("client stdout:", cli.stdout.strip())

time.sleep(1.0)
pkts = sn.stop()
print("captured packets:", len(pkts))
for i, p in enumerate(pkts[:8], 1):
    if TCP in p:
        f = p[TCP].flags
        print(f"  #{i} {p[TCP].sport}->{p[TCP].dport} flags={f} seq={p[TCP].seq} ack={p[TCP].ack} len={len(bytes(p[TCP].payload))}")

path = os.path.join(OUT, "test_tcp12000.pcapng")
wrpcapng(path, pkts)
print("saved", path, os.path.getsize(path), "bytes")

srv.terminate()
time.sleep(0.3)
srv.kill()
