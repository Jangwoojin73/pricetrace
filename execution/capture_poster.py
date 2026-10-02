import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def capture_poster():
    print("=" * 60)
    print("🎨 [Poster Renderer] 청금석 PriceTrace 홍보 포스터 렌더링 캡처 시작")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # 레티나 고해상도 (device_scale_factor=2) 설정
        page = browser.new_page(
            viewport={"width": 1100, "height": 1400},
            device_scale_factor=2
        )

        url = "http://127.0.0.1:8080/poster.html"
        print(f"  - 세로 4:3 포스터 페이지 접속: {url}")
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # 1. 세로 4:3 포스터 캔버스 캡처
        poster_canvas = page.locator(".poster-canvas")
        
        path_poster_canvas = os.path.join(ARTIFACT_DIR, "proof_pricetrace_qr_poster_4_3.png")
        poster_canvas.screenshot(path=path_poster_canvas)
        print(f"  - [1] 세로 4:3 포스터 캔버스 캡처 완료: {path_poster_canvas}")

        # public 폴더 저장
        path_public_poster = os.path.join("public", "pricetrace_poster_4_3.png")
        poster_canvas.screenshot(path=path_public_poster)
        print(f"  - [2] public 폴더 저장 완료: {path_public_poster}")

        # 2. 웹 열람 화면 캡처
        path_poster_web_view = os.path.join(ARTIFACT_DIR, "proof_poster_web_view_4_3.png")
        page.screenshot(path=path_poster_web_view, full_page=True)
        print(f"  - [3] 웹 열람 화면 캡처 완료: {path_poster_web_view}")

        browser.close()

    print("=" * 60)
    print("🎉 청금석 PriceTrace 홍보 포스터 렌더링 캡처 성공!")
    print("=" * 60)

if __name__ == "__main__":
    capture_poster()
