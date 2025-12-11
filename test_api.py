#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 XSS 防御系统 API"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"
s = requests.Session()

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}")

# 1. 登录
print(">>> 开始测试 XSS 防御系统 API...")
try:
    r = s.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin"})
    print(f"\n✓ 登录成功 (Status: {r.status_code})")
except Exception as e:
    print(f"\n✗ 登录失败: {e}")
    print("请确保 Flask 服务正在运行: .venv/bin/python run.py")
    exit(1)

# 2. 切换防御（关闭）
try:
    r = s.post(f"{BASE_URL}/toggle_defense", json={"enabled": False})
    print_response("切换防御（关闭）", r)
except Exception as e:
    print(f"✗ 切换防御失败: {e}")

# 3. 切换防御（开启）
try:
    r = s.post(f"{BASE_URL}/toggle_defense", json={"enabled": True})
    print_response("切换防御（开启）", r)
except Exception as e:
    print(f"✗ 切换防御失败: {e}")

# 4. 永久封禁 IP
try:
    r = s.post(f"{BASE_URL}/ban_ip", json={"ip": "127.0.0.2", "permanent": True})
    print_response("永久封禁 127.0.0.2", r)
except Exception as e:
    print(f"✗ 封禁失败: {e}")

# 5. 临时封禁 IP（60分钟）
try:
    r = s.post(f"{BASE_URL}/ban_ip", json={"ip": "127.0.0.3", "duration": 60})
    print_response("临时封禁 127.0.0.3 (60分钟)", r)
except Exception as e:
    print(f"✗ 封禁失败: {e}")

# 6. 查看被封禁列表
try:
    r = s.get(f"{BASE_URL}/get_banned_ips")
    print_response("被封禁 IP 列表（解封前）", r)
except Exception as e:
    print(f"✗ 获取列表失败: {e}")

# 7. 解封 IP
try:
    r = s.post(f"{BASE_URL}/unban_ip", json={"ip": "127.0.0.2"})
    print_response("解封 127.0.0.2", r)
except Exception as e:
    print(f"✗ 解封失败: {e}")

# 8. 再次查看被封禁列表
try:
    r = s.get(f"{BASE_URL}/get_banned_ips")
    print_response("被封禁 IP 列表（解封后）", r)
except Exception as e:
    print(f"✗ 获取列表失败: {e}")

# 9. 测试 XSS 攻击（防御开启状态）
try:
    r = s.post(f"{BASE_URL}/test_xss", json={"input": "<script>alert('XSS')</script>"})
    print_response("测试 XSS 攻击（防御开启）", r)
except Exception as e:
    print(f"✗ 测试失败: {e}")

# 10. 获取攻击统计
try:
    r = s.get(f"{BASE_URL}/api/stats/attacks")
    print_response("攻击趋势统计", r)
except Exception as e:
    print(f"✗ 获取统计失败: {e}")

try:
    r = s.get(f"{BASE_URL}/api/stats/top_ips")
    print_response("Top 攻击 IP", r)
except Exception as e:
    print(f"✗ 获取统计失败: {e}")

print("\n>>> 测试完成！")
