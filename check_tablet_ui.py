import sys
import os
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def check_tablet_view():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. iPad Pro 11 세로 모드 (834 x 1194)
        print("[1] iPad Pro 11 Portrait (834 x 1194) 측정...")
        ipad_context = browser.new_context(
            viewport={"width": 834, "height": 1194},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
            has_touch=True
        )
        page = ipad_context.new_page()
        page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        time.sleep(1)

        bottom_nav_visible = page.locator("#mobileBottomNav").is_visible()
        desktop_controls_visible = page.locator("#openConfigModalBtn").is_visible()

        print(f"  - 하단 네비게이션 바 노출 여부: {bottom_nav_visible}")
        print(f"  - 상단 데스크톱 컨트롤 노출 여부: {desktop_controls_visible}")

        ipad_path = os.path.join(ARTIFACT_DIR, "proof_tablet_ipad_pro_view.png")
        page.screenshot(path=ipad_path)
        print(f"  - [캡처 완료] iPad Pro 화면: {ipad_path}")

        # iPad Pro 검색 결과 테스트
        print("  - iPad Pro 검색 실행 ('농심 신라면 20개')...")
        page.fill("#searchInput", "농심 신라면 20개")
        page.press("#searchInput", "Enter")
        page.wait_for_selector("#resultView:not(.hidden)", timeout=15000)
        time.sleep(2)
        ipad_search_path = os.path.join(ARTIFACT_DIR, "proof_tablet_ipad_search_result.png")
        page.screenshot(path=ipad_search_path)
        print(f"  - [캡처 완료] iPad Pro 검색 결과 화면: {ipad_search_path}")
        ipad_context.close()

        # 2. Galaxy Tab S8 세로 모드 (800 x 1280)
        print("\n[2] Galaxy Tab S8 Portrait (800 x 1280) 측정...")
        tab_context = browser.new_context(
            viewport={"width": 800, "height": 1280},
            user_agent="Mozilla/5.0 (Linux; Android 13; SM-X700) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            device_scale_factor=2,
            has_touch=True
        )
        t_page = tab_context.new_page()
        t_page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        time.sleep(1)

        tab_bottom_nav = t_page.locator("#mobileBottomNav").is_visible()
        tab_desktop_controls = t_page.locator("#openConfigModalBtn").is_visible()
        print(f"  - Galaxy Tab 세로 하단 네비게이션 바 노출 여부: {tab_bottom_nav}")
        print(f"  - Galaxy Tab 세로 상단 데스크톱 컨트롤 노출 여부: {tab_desktop_controls}")

        tab_path = os.path.join(ARTIFACT_DIR, "proof_tablet_galaxy_tab_view.png")
        t_page.screenshot(path=tab_path)
        print(f"  - [캡처 완료] Galaxy Tab 세로 화면: {tab_path}")
        tab_context.close()

        # 3. iPad Air 5 세로 모드 (820 x 1180)
        print("\n[3] iPad Air Portrait (820 x 1180) 측정...")
        air_context = browser.new_context(
            viewport={"width": 820, "height": 1180},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
            has_touch=True
        )
        a_page = air_context.new_page()
        a_page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        time.sleep(1)

        air_bottom_nav = a_page.locator("#mobileBottomNav").is_visible()
        print(f"  - iPad Air 세로 하단 네비게이션 바 노출 여부: {air_bottom_nav}")

        air_path = os.path.join(ARTIFACT_DIR, "proof_tablet_ipad_air_view.png")
        a_page.screenshot(path=air_path)
        print(f"  - [캡처 완료] iPad Air 세로 화면: {air_path}")
        air_context.close()

        # 4. PC Desktop (1440 x 900) 비교 측정
        print("\n[4] PC Desktop (1440 x 900) 비교 측정...")
        pc_context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        p_page = pc_context.new_page()
        p_page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        time.sleep(1)

        pc_bottom_nav = p_page.locator("#mobileBottomNav").is_visible()
        pc_desktop_controls = p_page.locator("#openConfigModalBtn").is_visible()
        print(f"  - PC Desktop 하단 네비게이션 바 노출 여부: {pc_bottom_nav} (정상: False)")
        print(f"  - PC Desktop 상단 데스크톱 컨트롤 노출 여부: {pc_desktop_controls} (정상: True)")
        pc_path = os.path.join(ARTIFACT_DIR, "proof_tablet_pc_desktop_compare.png")
        p_page.screenshot(path=pc_path)
        print(f"  - [캡처 완료] PC Desktop 비교 화면: {pc_path}")
        pc_context.close()

        browser.close()

if __name__ == "__main__":
    check_tablet_view()
