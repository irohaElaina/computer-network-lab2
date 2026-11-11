import subprocess, time
from scapy.all import AsyncSniffer, IP, ICMP, wrpcapng
iface = r"\Device\NPF_{89F25026-C121-42CF-8125-36142131BD85}"
sn = AsyncSniffer(iface=iface, filter="icmp", store=True); sn.start(); time.sleep(0.6)
r = subprocess.run(["ping","-n","1","-l","2000","172.27.192.1"], capture_output=True, text=True, timeout=25)
print(r.stdout.strip()[:300])
time.sleep(1.0); p = sn.stop()
print("captured", len(p))
for i,x in enumerate(p,1):
    if IP in x:
        ip=x[IP]
        print(f"  #{i} len={ip.len} id=0x{ip.id:04x} MF={int(ip.flags&1)} off={ip.frag} payload={len(bytes(ip.payload))}")
wrpcapng(r"C:\Users\iroha\Desktop\lab2_251006115\pcap\D3c_icmp_frag.pcapng", p)
