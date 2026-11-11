# -*- coding: utf-8 -*-
"""生成实验2 报告：每题直接回答，不展开无关内容。"""
import os, datetime
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = r"C:\Users\iroha\Desktop\lab2_251006115"
OUT = os.path.join(BASE, "report")
os.makedirs(OUT, exist_ok=True)
DOCX = os.path.join(OUT, "251006115郭久铭-lab2.docx")

GITHUB = "https://github.com/<用户名>/computer-network-lab2"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.5)
sec.top_margin = sec.bottom_margin = Cm(2.3)

st = doc.styles['Normal']
st.font.name = 'Times New Roman'
st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
st.paragraph_format.line_spacing = 1.4
st.paragraph_format.space_after = Pt(2)


def rf(run, size=10.5, ea='宋体', bold=False):
    run.font.size = Pt(size)
    run.font.name = 'Times New Roman'
    run.font.bold = bold
    e = run._element.get_or_add_rPr().get_or_add_rFonts()
    e.set(qn('w:ascii'), 'Times New Roman')
    e.set(qn('w:hAnsi'), 'Times New Roman')
    e.set(qn('w:eastAsia'), ea)


def title(t, size=20):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    rf(p.add_run(t), size=size, ea='黑体', bold=True)


def h1(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    rf(p.add_run(t), size=14, ea='黑体', bold=True)


def h2(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9); p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    rf(p.add_run(t), size=11.5, ea='黑体', bold=True)


def para(t, indent=True, after=2):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(21) if indent else Pt(0)
    p.paragraph_format.space_after = Pt(after)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rf(p.add_run(t))


def code(lines, size=8.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.4); pf.space_before = Pt(2); pf.space_after = Pt(6)
    pf.line_spacing = 1.0; pf.keep_together = True
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), 'F5F5F5')
    p._p.get_or_add_pPr().append(shd)
    for i, ln in enumerate(lines):
        r = p.add_run(ln)
        rf(r, size=size)
        r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:ascii'), 'Consolas')
        r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:hAnsi'), 'Consolas')
        if i != len(lines) - 1:
            r.add_break()


def table(headers, rows, widths, aligns=None, size=8.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ''
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
        rf(p.add_run(h), size=size, ea='黑体', bold=True)
        shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), 'EDEDED')
        c._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            if aligns and aligns[i] == 'c':
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rf(p.add_run(str(v)), size=size)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    for r in t.rows:
        r._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        for i, w in enumerate(widths):
            r.cells[i].width = Cm(w)
    for r in t.rows[:-1]:
        for c in r.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    return t


def cap(t):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(6)
    rf(p.add_run(t), size=9)


# ---------------- 封面 ----------------
title('计算机网络实验报告', 22)
title('实验2  HTTP 客户端与 TCP、UDP 协议分析', 15)
doc.add_paragraph()
table(['姓名', '郭久铭', '学号', '251006115'],
      [['班级', '网工25', '实验日期', '2026-11-11'],
       ['实验环境', 'Windows 11 物理机（同机运行）', '接入方式', 'Wi-Fi']],
      widths=[2.8, 5.2, 2.8, 4.2], size=10)
doc.add_paragraph()
para('代码仓库：' + GITHUB, indent=False)
para('抓包文件：251006115郭久铭-lab2.pcapng（含 B、C 两部分全部场景，共 80 帧）', indent=False)

h1('一、实验环境')
para('Windows 11（build 26200），Python 3.12.10。client 与 server 都跑在本机 127.0.0.1：'
     'TCP 用 12000 端口，UDP 用 5201 端口。抓包选 loopback 网卡（Npcap），因为两端都在本机。')
para('合并后的帧号：S1 1–12、S2 13–22、S3 23–32、S4 33–67、D1 68–69、D2 70–72、D3 73–74、'
     '分片对照 75–78、D4 79–80。下文帧号都指这份文件。')

# ---------------- 第一部分 ----------------
h1('第一部分  webget')

h2('T1  recv 循环')
para('recv 一次只收到一部分数据，所以要放在循环里收。循环结束只有两种情况：')
para('① 响应头里有 Content-Length，就收够这么多字节为止；')
para('② 没有 Content-Length，就收到对端关闭（recv 返回空）为止，所以请求里带 Connection: close。')
para('另外设了 settimeout(10)，服务器不发也不关的时候不会一直卡着。')
code(["while True:",
      "    chunk = sock.recv(4096)",
      "    if not chunk:                     # ② 对端关闭",
      "        break",
      "    buf.extend(chunk); recv_sizes.append(len(chunk))",
      "    if 头部的 Content-Length 已知 and body 收够了:",
      "        break                         # ① 收够字节数"])

h2('T2  解析与保存')
para('按空行把响应切成状态行、响应头、body 三部分：打印状态码和全部响应头，body 用 wb 写文件。')
para('用文本模式会毁掉图片：文本模式会按编码解码再编码，非法字节被替换、换行被改写，字节就变了。')

h2('T3  参数化')
para('host、path、port 全部从命令行取，不写死；参数不够就打印用法退出。')
code(["usage: python webget.py <host> <path> [port]",
      "  e.g. python webget.py www.bjfu.edu.cn /"])

h2('T4  recv 了几次')
para('访问 www.bjfu.edu.cn 首页：18 次，每次字节数如下，总共 59369 字节（响应头 352 + body 59017）。')
code(["recv 调用次数: 18",
      "每次字节数: [1460, 4096, 4096, 4096, 852, 4096, 4096, 4096, 4096, 4096, 4096, 4096, 528, 1460, 4096, 4096, 4096, 1821]"])
para('访问 example.com：1 次，931 字节。')
para('所以响应不是一次到齐的。TCP 是字节流，不保留报文边界，读几次、每次读多少都不固定，'
     '只能靠 Content-Length 或连接关闭判断结束。')

h2('T5  抓包对照')
para('webget 一次请求只发 1 个 GET 包；三次握手由客户端发起（我先连，服务器才响应）。'
     'seq/ack 的推进、SYN/ACK 的置位和实验1 的 C3 完全一样，只是端口从 18080 变成 80、目的地址变成公网。')

# ---------------- 第二部分 ----------------
h1('第二部分  TCP')

h2('A1、A2  跑通教材程序')
para('UDP 监听改成 5201 后跑通，server 打印出 client 发来的内容；TCP 在 12000 端口跑通，loopback 上能看到完整握手、数据和 FIN。')
para('问：UDP 的 client 比 TCP 的 client 少了哪一步？')
para('答：少了 connect()。TCPClient.py 里的 clientSocket.connect((serverName, serverPort))，'
     'UDPClient.py 里没有这一行，UDP 直接 sendto 带上地址就发。')

h2('S1  正常交互')
table(['帧号', '方向', '标志位', 'seq', 'ack', '窗口', '载荷'],
      [['1', '56043→12000', 'SYN', '1877747910', '0', '65535', '0'],
       ['2', '12000→56043', 'SYN,ACK', '2982511978', '1877747911', '65535', '0'],
       ['3', '56043→12000', 'ACK', '1877747911', '2982511979', '255', '0'],
       ['4', '56043→12000', 'PSH,ACK', '1877747911', '2982511979', '255', '19'],
       ['5', '12000→56043', 'ACK', '2982511979', '1877747930', '255', '0'],
       ['6', '12000→56043', 'PSH,ACK', '2982511979', '1877747930', '255', '19'],
       ['7', '56043→12000', 'ACK', '1877747930', '2982511998', '255', '0'],
       ['8', '12000→56043', 'FIN,ACK', '2982511998', '1877747930', '255', '0'],
       ['9', '56043→12000', 'FIN,ACK', '1877747930', '2982511998', '255', '0'],
       ['10', '12000→56043', 'ACK', '2982511999', '1877747931', '255', '0']],
      widths=[1.4, 3.4, 3.0, 2.8, 2.8, 1.8, 1.4], aligns=['c', 'l', 'l', 'c', 'c', 'c', 'c'])
cap('表 1  S1 关键帧（第 1–10 帧，11–12 是 0.31 s 后的重复 FIN 与 ACK）')
para('① 字段：源端口 56043、目的端口 12000；seq 是本段第一个字节的序号，ack 是期望收到的下一个字节序号；'
     'SYN 只在 1、2 帧置位，ACK 从第 2 帧起都置位；窗口握手时 65535，之后是 255；校验和正确。')
para('② 握手：客户端 ISN 1877747910，服务器 ISN 2982511978；第 2 帧 ack=客户端 ISN+1，'
     '第 3 帧 seq=客户端 ISN+1、ack=服务器 ISN+1。')
para('③ 数据：第 4 帧发 19 字节，第 5 帧 ack=1877747930（1877747911+19）；第 6 帧服务器回 19 字节，第 7 帧 ack 再推进 19。')
para('④ 释放：只看到 8、9、10 三个报文就结束了，两边几乎同时 close，属于同时关闭，不是标准的四步。')

h2('S2  先 client 后 server')
para('端口上没人监听，客户端发 SYN 后立刻收到 RST，一共重试 5 次。应用层报 ConnectionRefusedError（WinError 10061）。')
para('“报错在网络上是几个包”：5 个 SYN + 5 个 RST，共 10 个包（第 13–22 帧）。')
table(['轮次', '帧号', '客户端发', '服务器回', '间隔'],
      [['1', '13、14', 'SYN', 'RST,ACK', '0 ms'],
       ['2', '15、16', 'SYN 重传', 'RST,ACK', '+517 ms'],
       ['3', '17、18', 'SYN 重传', 'RST,ACK', '+514 ms'],
       ['4', '19、20', 'SYN 重传', 'RST,ACK', '+516 ms'],
       ['5', '21、22', 'SYN 重传', 'RST,ACK', '+514 ms']],
      widths=[1.6, 2.2, 5.0, 4.6, 3.0], aligns=['c', 'c', 'l', 'l', 'c'])
cap('表 2  S2 的 SYN 重传与 RST')

h2('S3  强杀 client')
para('server 侧抓到的是 RST（第 32 帧，约 3 秒后），不是 FIN。进程被杀时 socket 被系统销毁，'
     '缓冲区里还有没读的数据，内核就发 RST。')
para('netstat -ano 看 12000 端口，杀进程后一直是 TIME_WAIT：')
code(["TCP    127.0.0.1:12000    127.0.0.1:58584    TIME_WAIT    0",
      "TCP    127.0.0.1:58584    127.0.0.1:12000    TIME_WAIT    0"])
para('TIME_WAIT 在主动关闭的一方（这里是 server，发完就 close）。它要持续 2MSL（Windows 约 2 分钟）：'
     '一是最后的 ACK 丢了还能重发 FIN，二是让旧连接的重复报文消散，不会串到新连接上。')

h2('S4  三个阶段耗时')
table(['阶段', '起点→终点', '耗时'],
      [['握手', 'SYN → ACK', '0.07–0.10 ms'],
       ['数据传输', '客户端 PSH → 服务器 ACK', '约 0.015 ms'],
       ['挥手', 'FIN → 最后 ACK', '0.05–0.07 ms']],
      widths=[3.6, 7.6, 5.0], aligns=['l', 'l', 'c'])
cap('表 3  S4 三阶段耗时（第 33–67 帧）')
para('三个阶段不一致：握手最贵，数据几乎不花时间，挥手和握手接近。')
para('和实验1 的公网 RTT 比：本机是十分之一毫秒级，校园网是毫秒级，境外是百毫秒级，差 3–4 个数量级。')

# ---------------- 第三部分 ----------------
h1('第三部分  UDP')

h2('D1  UDP 头')
table(['帧号', '方向', '源端口', '目的端口', '长度', '校验和', '载荷'],
      [['68', '58848→5201', '58848', '5201', '27', '0xE43F', '19'],
       ['69', '5201→58848', '5201', '58848', '27', '0x84B0', '19']],
      widths=[1.6, 3.6, 2.4, 2.6, 1.8, 2.4, 1.8], aligns=['c', 'l', 'c', 'c', 'c', 'c', 'c'])
cap('表 4  D1 的 UDP 头')
para('长度 27 = 8 字节头部 + 19 字节数据。对照 S1 的 TCP 头，UDP 少了序号、确认号、标志位、窗口和选项，'
     '头部固定 8 字节。')

h2('D2  先 client 后 server')
para('第 70–72 帧：客户端第一次发的报文没有任何回应（5201 没人监听）；server 起来后第二次发就正常收到应答。')
para('和 S2 比，“无连接”体现在：不用握手，客户端不管对方在不在都直接发；丢了的报文不重传；也没有 RST。')

h2('D3  2000 字节大报文')
para('用文件发 2000 字节，在 loopback 上只有 1 个包（第 73–74 帧），UDP 长度 2008，没有分片。'
     '因为 loopback 的 MTU 是 4294967295，比 2000 大得多。')
para('换到 MTU 1500 的网卡上，用同样 2000 字节的 ICMP 抓包（第 75–78 帧），请求和应答各分成 2 个 IP 分片：')
table(['帧号', 'IP 总长', 'IP id', 'MF', '片偏移', '说明'],
      [['75', '1500', '0x1cf5', '1', '0', '第 1 片'],
       ['76', '548', '0x1cf5', '0', '185', '第 2 片，偏移 185×8=1480'],
       ['77', '1500', '0xffc2', '1', '0', '应答第 1 片'],
       ['78', '548', '0xffc2', '0', '185', '应答第 2 片']],
      widths=[1.6, 2.2, 2.2, 1.4, 2.2, 8.2], aligns=['c', 'c', 'c', 'c', 'c', 'l'])
cap('表 5  2000 字节报文的分片（第 75–78 帧）')
para('结论：分片在 IP 层。一个 UDP 报文被分片时，只有第一片带 UDP 头，后面几片只有 IP 头；'
     '丢任何一片整个报文就废了。')

h2('D4  server 不在线')
para('第 79 帧是客户端发的 UDP，第 80 帧是回来的 ICMP，type=3、code=3，就是“端口不可达”。'
     '主机在，但 5201 上没有进程监听，所以 IP 层回 ICMP 告诉发送方。')

# ---------------- 附录 ----------------
h1('附录  代码与文件')
para('代码仓库：' + GITHUB, indent=False)
para('压缩包：webget.py、UDPServer.py、UDPClient.py、TCPServer.py、TCPClient.py、'
     'tcp_client_hold.py、udp_client_file.py、report、251006115郭久铭-lab2.pcapng。', indent=False)
code(["python UDPServer.py      # 终端1，5201",
      "python UDPClient.py      # 终端2",
      "python TCPServer.py      # 终端1，12000",
      "python TCPClient.py      # 终端2",
      "python webget.py www.bjfu.edu.cn /"])

cp = doc.core_properties
cp.author = '郭久铭'
cp.last_modified_by = '郭久铭'
cp.title = '计算机网络实验2 报告'
cp.subject = 'HTTP 客户端与 TCP/UDP 协议分析'
cp.comments = ''
cp.revision = 1
cp.created = datetime.datetime(2026, 11, 11, 20, 30, 0)
cp.modified = datetime.datetime(2026, 11, 11, 21, 0, 0)
doc.save(DOCX)
print('saved', DOCX, 'tables', len(doc.tables))
