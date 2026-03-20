# -*- coding: utf-8 -*-
"""MelodyClaw V3 用户系统测试"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_user_system():
    print("=" * 60)
    print("MelodyClaw V3 用户系统测试")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    auth_token = None
    
    try:
        # 测试 1: 用户注册
        print("\n[测试 1/7] 用户注册...")
        resp = requests.post(f"{BASE_URL}/api/v3/auth/register", json={
            "username": "test_user",
            "password": "test123456",
            "email": "test@example.com",
            "nickname": "测试用户"
        }, timeout=5)
        
        if resp.status_code == 200:
            print(f"  ✓ 注册成功")
            auth_token = resp.json().get('access_token')
            tests_passed += 1
        elif resp.status_code == 400:
            print(f"  - 用户已存在（跳过）")
            tests_passed += 1
        else:
            print(f"  x 注册失败：{resp.status_code}")
            tests_failed += 1
        
        # 测试 2: 用户登录
        print("\n[测试 2/7] 用户登录...")
        from requests.auth import HTTPBasicAuth
        resp = requests.post(
            f"{BASE_URL}/api/v3/auth/login",
            data={"username": "test_user", "password": "test123456"},
            timeout=5
        )
        
        if resp.status_code == 200:
            print(f"  ✓ 登录成功")
            auth_token = resp.json().get('access_token')
            tests_passed += 1
        else:
            print(f"  x 登录失败：{resp.status_code}")
            tests_failed += 1
        
        # 测试 3: 获取当前用户信息
        print("\n[测试 3/7] 获取用户信息...")
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = requests.get(f"{BASE_URL}/api/v3/auth/me", headers=headers, timeout=5)
        
        if resp.status_code == 200:
            user = resp.json()
            print(f"  ✓ 获取成功：{user.get('username')}")
            tests_passed += 1
        else:
            print(f"  x 获取失败：{resp.status_code}")
            tests_failed += 1
        
        # 测试 4: 获取 VIP 套餐
        print("\n[测试 4/7] 获取 VIP 套餐...")
        resp = requests.get(f"{BASE_URL}/api/v3/vip/packages", timeout=5)
        
        if resp.status_code == 200:
            packages = resp.json().get('packages', [])
            print(f"  ✓ 获取成功：{len(packages)} 个套餐")
            tests_passed += 1
        else:
            print(f"  x 获取失败：{resp.status_code}")
            tests_failed += 1
        
        # 测试 5: 获取 VIP 音色
        print("\n[测试 5/7] 获取 VIP 音色...")
        resp = requests.get(f"{BASE_URL}/api/v3/vip/voices", timeout=5)
        
        if resp.status_code == 200:
            voices = resp.json().get('voices', [])
            print(f"  ✓ 获取成功：{len(voices)} 个音色")
            tests_passed += 1
        else:
            print(f"  x 获取失败：{resp.status_code}")
            tests_failed += 1
        
        # 测试 6: 获取 VIP 状态
        print("\n[测试 6/7] 获取 VIP 状态...")
        resp = requests.get(f"{BASE_URL}/api/v3/vip/status", headers=headers, timeout=5)
        
        if resp.status_code == 200:
            status = resp.json()
            print(f"  ✓ VIP 状态：{'是' if status.get('is_vip') else '否'}")
            tests_passed += 1
        else:
            print(f"  x 获取失败：{resp.status_code}")
            tests_failed += 1
        
        # 测试 7: 数据库表验证
        print("\n[测试 7/7] 数据库表验证...")
        import sqlite3
        from pathlib import Path
        
        db_path = Path(__file__).parent.parent / "backend" / "app" / "melodyclaw.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        tables = ['users', 'user_follows', 'user_favorites', 'comments', 'vip_packages', 'vip_voices']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"  ✓ 表 {table} 存在")
            else:
                print(f"  x 表 {table} 不存在")
                tests_failed += 1
                break
        else:
            tests_passed += 1
        
        conn.close()
        
    except Exception as e:
        tests_failed += 1
        print(f"\n  x 测试异常：{e}")
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"  通过：{tests_passed}")
    print(f"  失败：{tests_failed}")
    print(f"  总计：{tests_passed + tests_failed}")
    print("=" * 60)
    
    return tests_failed == 0


if __name__ == "__main__":
    success = test_user_system()
    sys.exit(0 if success else 1)
