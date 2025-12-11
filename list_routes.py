#!/usr/bin/env python3
"""列出所有已注册的 Flask 路由"""

from app import create_app

app = create_app()

print("=" * 80)
print("所有已注册的路由:")
print("=" * 80)

routes = []
for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    routes.append((rule.endpoint, methods, str(rule)))

# 按路径排序
routes.sort(key=lambda x: x[2])

for endpoint, methods, path in routes:
    print(f"{path:40} {methods:20} → {endpoint}")

print("=" * 80)
print(f"总计: {len(routes)} 个路由")
print("=" * 80)

# 检查特定路由
target_routes = ['upload_test_bg_page', 'upload_mascot_page', 'test_xss_page']
print("\n关键路由检查:")
for target in target_routes:
    found = any(endpoint == target for endpoint, _, _ in routes)
    status = "✓ 已注册" if found else "✗ 未找到"
    print(f"  {target:30} {status}")
