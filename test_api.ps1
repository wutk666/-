# 登录并保存会话
try {
    $login = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -Method Post -Body @{ username='admin'; password='admin' } -SessionVariable sess
    Write-Host "Login Status: $($login.StatusCode)"
} catch {
    Write-Error "Login failed. Ensure the server is running on http://127.0.0.1:5000"
    exit
}

# 切换防御（关闭）
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/toggle_defense" -Method Post -Body (ConvertTo-Json @{ enabled = $false }) -ContentType 'application/json' -WebSession $sess
    Write-Host "Toggle Defense (False): $($response | ConvertTo-Json -Depth 2)"
} catch { Write-Error "Toggle Defense failed: $_" }

# 切换防御（开启）
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/toggle_defense" -Method Post -Body (ConvertTo-Json @{ enabled = $true }) -ContentType 'application/json' -WebSession $sess
    Write-Host "Toggle Defense (True): $($response | ConvertTo-Json -Depth 2)"
} catch { Write-Error "Toggle Defense failed: $_" }

# 永久封禁 IP (127.0.0.2)
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/ban_ip" -Method Post -Body (ConvertTo-Json @{ ip='127.0.0.2'; permanent=$true }) -ContentType 'application/json' -WebSession $sess
    Write-Host "Ban IP 127.0.0.2 (Permanent): $($response | ConvertTo-Json -Depth 2)"
} catch { Write-Error "Ban IP failed: $_" }

# 临时封禁 60 分钟 (127.0.0.3)
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/ban_ip" -Method Post -Body (ConvertTo-Json @{ ip='127.0.0.3'; duration=60 }) -ContentType 'application/json' -WebSession $sess
    Write-Host "Ban IP 127.0.0.3 (Temporary): $($response | ConvertTo-Json -Depth 2)"
} catch { Write-Error "Ban IP failed: $_" }

# 查看被封禁列表
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/get_banned_ips" -Method Get -WebSession $sess
    Write-Host "Banned IPs List (Before Unban):"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch { Write-Error "Get Banned IPs failed: $_" }

# 解封 (127.0.0.2)
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/unban_ip" -Method Post -Body (ConvertTo-Json @{ ip='127.0.0.2' }) -ContentType 'application/json' -WebSession $sess
    Write-Host "Unban IP 127.0.0.2: $($response | ConvertTo-Json -Depth 2)"
} catch { Write-Error "Unban IP failed: $_" }

# 再次查看被封禁列表
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/get_banned_ips" -Method Get -WebSession $sess
    Write-Host "Banned IPs List (After Unban):"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch { Write-Error "Get Banned IPs failed: $_" }
