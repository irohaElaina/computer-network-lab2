# -*- coding: utf-8 -*-
"""把各场景 pcapng 合并成一份 251006115郭久铭-lab2.pcapng，并输出「场景→帧号范围」索引。"""
import os, json
from scapy.all import rdpcap, wrpcapng, PcapNgReader

BASE = r"C:\Users\iroha\Desktop\lab2_251006115"
PCAP = os.path.join(BASE, "pcap")
OUT = os.path.join(BASE, "out")

order = [
    "S1_tcp_normal",
    "S2_tcp_reversed",
    "S3_tcp_kill_client",
    "S4_tcp_rtt",
    "D1_udp_header",
    "D2_udp_reversed",
    "D3_udp_2000bytes",
    "D3c_icmp_frag",
    "D4_udp_no_server",
]

all_pkts = []
index = {}
for name in order:
    path = os.path.join(PCAP, name + ".pcapng")
    if not os.path.exists(path):
        print("skip", name)
        continue
    pkts = rdpcap(path)
    start = len(all_pkts) + 1
    all_pkts.extend(pkts)
    index[name] = [start, len(all_pkts)]
    print(f"{name}: {len(pkts)} pkts -> frames {start}-{len(all_pkts)}")

dst = os.path.join(PCAP, "251006115郭久铭-lab2.pcapng")
wrpcapng(dst, all_pkts)
print("merged:", dst, os.path.getsize(dst), "bytes, total frames:", len(all_pkts))

with open(os.path.join(OUT, "frame_index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
