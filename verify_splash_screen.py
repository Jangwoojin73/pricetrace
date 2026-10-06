import sys
import os
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def verify_splash():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ----------------------------------------------------
        # 1. iPhone 15 Pro (393 x 852): 오프닝 스플래시 & 프로그레스 바 전진
        # ----------------------------------------------------
        print("[1] iPhone 15 Pro: 스플래시 화면 및 프로그레스 바 실측...")
        iphone_ctx = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
            has_touch=True
        )
        page = iphone_ctx.new_page()
        page.goto("http://127.0.0.1:8080", wait_until="domcontentloaded")
        time.sleep(0.5)

        # 데모 트리거로 0%부터 정밀 측정
        page.evaluate("() => window.showSplashDemo()")
        time.sleep(0.35) # 약 20% 시점

        splash_visible = page.locator("#appSplashScreen").is_visible()
        progress_text = page.locator("#splashProgressText").inner_text()
        progress_percent = page.locator("#splashProgressPercent").inner_text()
        print(f"  - 스플래시 노출 여부: {splash_visible}")
        print(f"  - 초기 진행 상태: {progress_text} ({progress_percent})")
        
        start_path = os.path.join(ARTIFACT_DIR, "proof_splash_starting.png")
        page.screenshot(path=start_path)
        print(f"  - [캡처 1 완료] 스플래시 시작 화면: {start_path}")

        # 진행 중 (약 60% 시점)
        time.sleep(0.65)
        mid_progress_text = page.locator("#splashProgressText").inner_text()
        mid_progress_percent = page.locator("#splashProgressPercent").inner_text()
        print(f"  - 중간 진행 상태: {mid_progress_text} ({mid_progress_percent})")
        
        mid_path = os.path.join(ARTIFACT_DIR, "proof_splash_progressing.png")
        page.screenshot(path=mid_path)
        print(f"  - [캡처 2 완료] 스플래시 중간 진행 화면: {mid_path}")

        # 완료 및 페이드아웃 대기 (총 2.2초 경과)
        time.sleep(1.6)
        is_hidden_after = page.evaluate("() => document.getElementById('appSplashScreen').classList.contains('splash-hidden')")
        print(f"  - 완료 후 스플래시 자동 숨김 여부: {is_hidden_after}")
        
        main_path = os.path.join(ARTIFACT_DIR, "proof_splash_main_after.png")
        page.screenshot(path=main_path)
        print(f"  - [캡처 3 완료] 완료 후 메인 진입 화면: {main_path}")
        iphone_ctx.close()

        # ----------------------------------------------------
        # 2. Galaxy S24 (412 x 915): [건너뛰기] 즉시 스킵 검증
        # ----------------------------------------------------
        print("\n[2] Galaxy S24: [건너뛰기] 버튼 즉시 스킵 검증...")
        galaxy_ctx = browser.new_context(
            viewport={"width": 412, "height": 915},
            user_agent="Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            device_scale_factor=2,
            has_touch=True
        )
        g_page = galaxy_ctx.new_page()
        g_page.goto("http://127.0.0.1:8080", wait_until="domcontentloaded")
        time.sleep(0.5)
        g_page.evaluate("() => window.showSplashDemo()")
        time.sleep(0.3)

        # 건너뛰기 버튼 클릭
        print("  - [건너뛰기] 버튼 클릭 실행...")
        g_page.click("#splashSkipBtn")
        time.sleep(0.6) # 페이드아웃 대기

        g_is_hidden = g_page.evaluate("() => document.getElementById('appSplashScreen').classList.contains('splash-hidden')")
        print(f"  - 건너뛰기 후 스플래시 숨김 여부: {g_is_hidden}")
        
        skip_path = os.path.join(ARTIFACT_DIR, "proof_splash_skipped.png")
        g_page.screenshot(path=skip_path)
        print(f"  - [캡처 4 완료] 건너뛰기 후 메인 화면: {skip_path}")
        galaxy_ctx.close()

        # ----------------------------------------------------
        # 3. iPad Pro 11 (834 x 1194): 태블릿 뷰포트 스플래시 화면
        # ----------------------------------------------------
        print("\n[3] iPad Pro 11: 태블릿 환경 스플래시 화면 렌더링...")
        ipad_ctx = browser.new_context(
            viewport={"width": 834, "height": 1194},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
            has_touch=True
        )
        i_page = ipad_ctx.new_page()
        i_page.goto("http://127.0.0.1:8080", wait_until="domcontentloaded")
        time.sleep(0.5)
        i_page.evaluate("() => window.showSplashDemo()")
        time.sleep(0.7) # 중간 시점

        tab_path = os.path.join(ARTIFACT_DIR, "proof_splash_tablet_view.png")
        i_page.screenshot(path=tab_path)
        print(f"  - [캡처 5 완료] iPad Pro 스플래시 화면: {tab_path}")
        ipad_ctx.close()

        # ----------------------------------------------------
        # 4. PC Desktop (1440 x 900): 와이드 PC에서는 스플래시 자동 생략
        # ----------------------------------------------------
        print("\n[4] PC Desktop: 데스크톱 진입 시 스플래시 자동 생략 확인...")
        pc_ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        p_page = pc_ctx.new_page()
        p_page.goto("http://127.0.0.1:8080")
        time.sleep(0.3)

        pc_is_hidden = p_page.evaluate("() => document.getElementById('appSplashScreen').classList.contains('splash-hidden')")
        print(f"  - PC Desktop 스플래시 자동 숨김 여부: {pc_is_hidden} (정상: True)")
        
        pc_path = os.path.join(ARTIFACT_DIR, "proof_splash_desktop_instant.png")
        p_page.screenshot(path=pc_path)
        print(f"  - [캡처 6 완료] PC 데스크톱 즉시 진입 화면: {pc_path}")
        pc_ctx.close()

        browser.close()
        print("\n=== 모든 스플래시 및 프로그레스 바 실측 검증 완료 ===")

if __name__ == "__main__":
    verify_splash()
