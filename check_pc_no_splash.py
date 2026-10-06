import sys
import os
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def check_pc():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # PC Desktop 1440 x 900
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = ctx.new_page()
        page.goto("http://127.0.0.1:8080", wait_until="domcontentloaded")

        # 즉시 스타일 측정
        display_style = page.evaluate("() => window.getComputedStyle(document.getElementById('appSplashScreen')).display")
        is_visible = page.locator("#appSplashScreen").is_visible()
        main_visible = page.locator("#welcomeView").is_visible()
        gnb_visible = page.locator("header").is_visible()

        print(f"PC Desktop 측정 결과:")
        print(f"  - #appSplashScreen computed display: '{display_style}' (정상: 'none')")
        print(f"  - 스플래시 화면 노출 여부: {is_visible} (정상: False)")
        print(f"  - 메인 웰컴 대시보드 즉시 노출 여부: {main_visible} (정상: True)")
        print(f"  - 상단 1단 데스크톱 GNB 즉시 노출 여부: {gnb_visible} (정상: True)")

        pc_cap = os.path.join(ARTIFACT_DIR, "proof_pc_no_splash_guaranteed.png")
        page.screenshot(path=pc_cap)
        print(f"  - [캡처 완료] PC 화면: {pc_cap}")

        ctx.close()
        browser.close()

if __name__ == "__main__":
    check_pc()
