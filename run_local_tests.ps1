$ErrorActionPreference = 'Continue'
$root = 'C:\Users\iroha\Desktop\lab2_251006115'
$code = Join-Path $root 'code'
$out  = Join-Path $root 'out'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$py = 'C:\Users\iroha\AppData\Local\Programs\Python\Python312\python.exe'
Set-Location $code

# ---------- UDP ----------
$udpSrv = Start-Process -FilePath $py -ArgumentList '-u','UDPServer.py' -RedirectStandardOutput (Join-Path $out 'udp_server.txt') -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2
'hello udp from 251006115' | & $py -u UDPClient.py *>&1 | Tee-Object -FilePath (Join-Path $out 'udp_client.txt')
Start-Sleep -Seconds 1
Stop-Process -Id $udpSrv.Id -Force -ErrorAction SilentlyContinue

# ---------- TCP ----------
$tcpSrv = Start-Process -FilePath $py -ArgumentList '-u','TCPServer.py' -RedirectStandardOutput (Join-Path $out 'tcp_server.txt') -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2
'hello tcp from 251006115' | & $py -u TCPClient.py *>&1 | Tee-Object -FilePath (Join-Path $out 'tcp_client.txt')
Start-Sleep -Seconds 1
Stop-Process -Id $tcpSrv.Id -Force -ErrorAction SilentlyContinue

# ---------- webget ----------
& $py -u webget.py www.bjfu.edu.cn / *>&1 | Tee-Object -FilePath (Join-Path $out 'webget_bjfu.txt')
"`n===== 文件清单 ====="
Get-ChildItem $out | Select-Object Name,Length | Format-Table -AutoSize
Get-ChildItem $code -Filter 'body_*' | Select-Object Name,Length | Format-Table -AutoSize
