p='tools/d3b_frag.py'
s=open(p,encoding='utf8').read()
s=s.replace('        wlan = ifc.name if hasattr(ifc, "name") else str(ifc)',
            '        wlan = getattr(ifc, "network_name", None) or getattr(ifc, "name", str(ifc))')
open(p,'w',encoding='utf8').write(s)
print('ok')
