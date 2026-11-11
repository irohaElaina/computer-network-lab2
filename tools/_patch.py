p='tools/d3b_frag.py'
s=open(p,encoding='utf8').read()
s=s.replace("from scapy.all import AsyncSniffer, wrpcapng, IP, UDP, Raw, get_if_list, get_ips, conf",
            "from scapy.all import AsyncSniffer, wrpcapng, IP, UDP, Raw, conf")
s=s.replace("""for name in get_if_list():
    try:
        ips = [str(i) for i in get_ips(ifname=name)]
    except Exception:
        continue
    if any(i.startswith("172.27.") for i in ips):
        wlan = name
        print("WLAN iface:", name, ips)
        break""",
"""for ifc in conf.ifaces.values():
    ip = str(getattr(ifc, "ip", "") or "")
    if ip.startswith("172.27."):
        wlan = ifc.name if hasattr(ifc, "name") else str(ifc)
        print("WLAN iface:", wlan, ip)
        break""")
open(p,'w',encoding='utf8').write(s)
print('patched')
