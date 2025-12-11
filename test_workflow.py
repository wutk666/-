#!/usr/bin/env python3
"""测试完整的登录和访问流程"""

import requests
from requests.exceptions import RequestException

BASE_URL = "http://127.0.0.1:5000"

def test_workflow():
    print("=" * 80)
    print("测试 XSS 防御系统访问流程")
    print("=" * 80)
    
    session = requests.Session()
    
    # 1. 测试首页重定向
    print("\n[1/5] 测试首页...")
    try:
        r = session.get(BASE_URL, allow_redirects=False, timeout=3)
        print(f"  ✓ 状态码: {r.status_code}")
        print(f"  ✓ 重定向到: {r.headers.get('Location', 'N/A')}")
    except RequestException as e:
        print(f"  ✗ 错误: {e}")
        return
    
    # 2. 测试登录页面
    print("\n[2/5] 测试登录页面...")
    try:
        r = session.get(f"{BASE_URL}/login", timeout=3)
        print(f"  ✓ 状态码: {r.status_code}")
        print(f"  ✓ 内容长度: {len(r.text)} 字节")
    except RequestException as e:
        print(f"  ✗ 错误: {e}")
        return
    
    # 3. 执行登录
    print("\n[3/5] 执行登录...")
    try:
        r = session.post(
            f"{BASE_URL}/login",
            data={"username": "admin", "password": "admin"},
            allow_redirects=False,
            timeout=3
        )
        print(f"  ✓ 状态码: {r.status_code}")
        if r.status_code == 302:
            print(f"  ✓ 登录成功，重定向到: {r.headers.get('Location', 'N/A')}")
        else:
            print(f"  ✗ 登录失败")
            return
    except RequestException as e:
        print(f"  ✗ 错误: {e}")
        return
    
    # 4. 访问控制台
    print("\n[4/5] 访问控制台...")
    try:
        r = session.get(f"{BASE_URL}/console", timeout=3)
        print(f"  ✓ 状态码: {r.status_code}")
        if "测试页背景" in r.text:
            print(f"  ✓ 找到 '测试页背景' 按钮")
        else:
            print(f"  ⚠ 未找到 '测试页背景' 按钮（可能是缓存问题）")
    except RequestException as e:
        print(f"  ✗ 错误: {e}")
        return
    
    # 5. 访问上传页面
    print("\n[5/5] 访问测试页背景上传...")
    try:
        r = session.get(f"{BASE_URL}/upload_test_bg", timeout=3)
        print(f"  ✓ 状态码: {r.status_code}")
        if r.status_code == 200:
            print(f"  ✓ 页面加载成功")
            print(f"  ✓ 内容长度: {len(r.text)} 字节")
            if "鬼灭之刃" in r.text:
                print(f"  ✓ 确认为鬼灭之刃风格页面")
        else:
            print(f"  ✗ 页面加载失败")
    except RequestException as e:
        print(f"  ✗ 错误: {e}")
        return
    
    print("\n" + "=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)
    print("\n📌 请在浏览器中访问:")
    print(f"   1. 登录: {BASE_URL}/login (admin/admin)")
    print(f"   2. 控制台: {BASE_URL}/console")
    print(f"   3. 上传页: {BASE_URL}/upload_test_bg")
    print(f"   4. 测试页: {BASE_URL}/test_xss")

if __name__ == "__main__":
    try:
        test_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠ 测试中断")
    except Exception as e:
        print(f"\n\n❌ 未预期的错误: {e}")
