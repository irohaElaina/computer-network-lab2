# -*- coding: utf-8 -*-
"""D3b：把 2000 字节 UDP 报文发往公网（TEST-NET 192.0.2.1），在 WLAN 网卡上抓包，
看 IP 层如何分片；与 loopback 上的不分片形成对照。
"""
import os, time
from scapy.all import AsyncSniffer, wrpcapng, IP, UDP, Raw, conf

BASE = r"C:\Users\iroha\Desktop\lab2_251006115"
PCAP = os.path.join(BASE, "pcap")
OUT = os.path.join(BASE, "out")

# 找 WLAN 的 Npcap 设备名
wlan = None
for ifc in conf.ifaces.values():
    ip = str(getattr(ifc, "ip", "") or "")
    if ip.startswith("172.27."):
        wlan = getattr(ifc, "network_name", None) or getattr(ifc, "name", str(ifc))
        print("WLAN iface:", wlan, ip)
        break
if not wlan:
    raise SystemExit("WLAN 接口没找到")

payload = bytes((i % 26) + 65 for i in range(2000))

sn = AsyncSniffer(iface=wlan, filter="udp port 5201", store=True)
sn.start()
time.sleep(0.8)

from scapy.all import send
send(IP(dst="192.0.2.1") / UDP(sport=5201, dport=5201) / Raw(load=payload), verbose=False)
time.sleep(1.5)
pkts = sn.stop()

path = os.path.join(PCAP, "D3b_udp_2000_frag.pcapng")
wrpcapng(path, pkts)
print("captured:", len(pkts), "saved:", path)

lines = []
for i, p in enumerate(pkts, 1):
    if IP in p:
        ip = p[IP]
        frag = ip.flags & 0x1
        lines.append(
            f"{i:2d}  len={ip.len:5d} id=0x{ip.id:04x} MF={int(frag)} frag_offset={ip.frag:5d} "
            f"ttl={ip.ttl} proto={ip.proto} payload={len(bytes(p.payload))}"
        )
print("\n".join(lines))

with open(os.path.join(OUT, "D3b_udp_2000_frag_packets.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
