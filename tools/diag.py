import socket, time
from scapy.all import AsyncSniffer, IP, UDP, Raw, conf
iface = r"\Device\NPF_{89F25026-C121-42CF-8125-36142131BD85}"
sn = AsyncSniffer(iface=iface, filter="udp port 5201 or icmp", store=True)
sn.start(); time.sleep(0.8)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b"A"*2000, ("192.0.2.1", 5201))
time.sleep(1.2); s.close()
p = sn.stop()
print("captured", len(p))
for i,x in enumerate(p[:6],1):
    print(i, x.summary()[:120])
