# -*- coding: utf-8 -*-
"""
선명한 2분할 듀얼 탭 UI 디자인 개선 검증 스크립트
1. 초기 상태: 국민 필수 생필품(선택됨 ✓) vs 오늘 실시간 핫딜(선택하기 👆)
2. 핫딜 탭 클릭 시: 오늘 실시간 핫딜(선택됨 ✓) vs 국민 필수 생필품(선택하기 👆)
3. 데스크톱 및 모바일 반응형 스크린샷 캡처
"""
from playwright.sync_api import sync_playwright

def verify_tab_ui():
    artifacts_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. 데스크톱 화면 검증
        page = browser.new_page(viewport={"width": 1280, "height": 950})
        print("[Step 1] 메인 홈 화면 접속 (데스크톱 1280x950)")
        page.goto("http://127.0.0.1:8080/index.html", wait_until="networkidle")
        page.wait_for_timeout(1000)

        # 초기 탭(국민 필수 생필품 활성) 캡처
        tab_steady_shot = f"{artifacts_dir}\\proof_tab_ui_steady_active.png"
        page.screenshot(path=tab_steady_shot)
        print(f" -> [국민 필수 생필품 활성 스크린샷 저장]: {tab_steady_shot}")

        # 오늘 실시간 핫딜 탭 클릭
        print("[Step 2] '오늘 실시간 핫딜' 탭 클릭")
        page.locator("#tabTrendingBtn").click()
        page.wait_for_timeout(1000)

        # 핫딜 탭(오늘 실시간 핫딜 활성) 캡처
        tab_trending_shot = f"{artifacts_dir}\\proof_tab_ui_trending_active.png"
        page.screenshot(path=tab_trending_shot)
        print(f" -> [오늘 실시간 핫딜 활성 스크린샷 저장]: {tab_trending_shot}")

        # 2. 모바일 화면 검증
        print("[Step 3] 모바일 뷰포트(390x844) 검증")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(500)

        tab_mobile_shot = f"{artifacts_dir}\\proof_tab_ui_mobile.png"
        page.screenshot(path=tab_mobile_shot)
        print(f" -> [모바일 탭 UI 스크린샷 저장]: {tab_mobile_shot}")

        browser.close()

    print("\n[검증 완료] 탭 UI 디자인 스크린샷 3종 생성 완료")

if __name__ == "__main__":
    verify_tab_ui()
