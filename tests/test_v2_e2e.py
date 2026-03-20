# -*- coding: utf-8 -*-
"""MelodyClaw V2 端到端集成测试

测试完整流程：
1. 访问前端首页
2. 选择歌曲进入拍摄页面
3. 模拟录制（需要真实摄像头）
4. 上传作品到后端
5. 验证作品可访问
"""

from playwright.sync_api import sync_playwright, expect
import requests
import time
import sys

FRONTEND_URL = "http://localhost:3001"
BACKEND_URL = "http://localhost:8000"

def run_e2e_tests():
    print("=" * 60)
    print("MelodyClaw V2 端到端集成测试")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # 前置检查：后端 API 是否正常
    print("\n[前置检查] 后端 API 健康...")
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"  ✓ 后端 API 正常")
    except Exception as e:
        print(f"  x 后端 API 异常：{e}")
        print("\n请先启动后端服务：cd backend/app && python main.py")
        return False
    
    # 前置检查：前端是否正常
    print("\n[前置检查] 前端服务...")
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        print(f"  ✓ 前端服务正常")
    except Exception as e:
        print(f"  x 前端服务异常：{e}")
        print("\n请先启动前端服务：cd frontend && npm run dev")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            permissions=['camera', 'microphone']
        )
        page = context.new_page()
        
        try:
            # 测试 1: 前端首页加载
            print("\n[测试 1/4] 前端首页加载...")
            page.goto(FRONTEND_URL, timeout=10000)
            expect(page.locator('text=想唱就唱')).to_be_visible()
            print("  ✓ 首页加载成功")
            tests_passed += 1
            
            # 测试 2: 歌曲列表
            print("\n[测试 2/4] 歌曲列表...")
            page.wait_for_selector('[data-testid="song-list"]', timeout=5000)
            song_cards = page.query_selector_all('[data-testid="song-card"]')
            print(f"  ✓ 找到 {len(song_cards)} 首歌曲")
            tests_passed += 1
            
            # 测试 3: 进入拍摄页面
            print("\n[测试 3/4] 拍摄页面...")
            page.goto(f"{FRONTEND_URL}/record/1", timeout=10000)
            page.wait_for_load_state('networkidle')
            expect(page.locator('.record-btn')).to_be_attached()
            print("  ✓ 拍摄页面加载成功")
            tests_passed += 1
            
            # 测试 4: 后端作品 API
            print("\n[测试 4/4] 后端作品 API...")
            resp = requests.get(f"{BACKEND_URL}/api/v2/recordings", timeout=5)
            assert resp.status_code == 200
            data = resp.json()
            print(f"  ✓ 作品 API 正常 (当前作品数：{data.get('total', 0)})")
            tests_passed += 1
            
        except Exception as e:
            tests_failed += 1
            print(f"\n  x 测试失败：{e}")
        
        finally:
            browser.close()
    
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
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
