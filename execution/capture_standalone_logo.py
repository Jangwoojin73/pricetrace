import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def capture_logo_only():
    print("=" * 60)
    print("🎨 [Logo Capture] 새로 삽입된 로고 단독 고해상도 캡처 시작")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # 1. Capture the SVG directly loaded from the server: http://127.0.0.1:8080/logo_jwj.svg
        page_svg = browser.new_page(viewport={"width": 600, "height": 600})
        page_svg.goto("http://127.0.0.1:8080/logo_jwj.svg")
        page_svg.wait_for_timeout(1000)
        shot_svg_direct = os.path.join(ARTIFACT_DIR, "proof_new_logo_svg_direct.png")
        page_svg.screenshot(path=shot_svg_direct)
        print(f"  - [1] logo_jwj.svg 브라우저 직접 열람 캡처: {shot_svg_direct}")
        page_svg.close()

        # 2. Capture a high-resolution, pixel-perfect presentation card showing ONLY the logo with details
        page_card = browser.new_page(viewport={"width": 700, "height": 700})
        html_code = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
              width: 100vw;
              height: 100vh;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #0f172a;
              font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
            }
            .card {
              width: 520px;
              height: 520px;
              background: #ffffff;
              border-radius: 40px;
              box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              position: relative;
              overflow: hidden;
            }
            .logo-box {
              width: 380px;
              height: 380px;
              display: flex;
              align-items: center;
              justify-content: center;
            }
            svg {
              width: 100%;
              height: 100%;
            }
            .badge {
              position: absolute;
              bottom: 24px;
              padding: 8px 18px;
              background: #f1f5f9;
              border: 1px solid #e2e8f0;
              border-radius: 9999px;
              font-size: 13px;
              font-weight: 800;
              color: #0f172a;
              letter-spacing: -0.3px;
              display: flex;
              align-items: center;
              gap: 6px;
            }
            .dot {
              width: 8px;
              height: 8px;
              background: #2563eb;
              border-radius: 50%;
            }
          </style>
        </head>
        <body>
          <div class="card">
            <div class="logo-box">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none">
                <!-- 1. 미니멀 볼드 레이더 원형 림 -->
                <circle cx="24" cy="24" r="20" stroke="#0F172A" stroke-width="3" />
                
                <!-- 2. 레이더 외곽 정밀 조준 틱 (절제된 4방위 틱) -->
                <line x1="24" y1="4" x2="24" y2="8" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
                <line x1="24" y1="40" x2="24" y2="44" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
                <line x1="4" y1="24" x2="8" y2="24" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
                <line x1="40" y1="24" x2="44" y2="24" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
                
                <!-- 3. 가격 급락 트렌드 화살표 (볼드 블랙) -->
                <path d="M14 18L22 26L27 21L34 32" stroke="#0F172A" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
                <polyline points="26 32 34 32 34 24" stroke="#0F172A" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
                
                <!-- 4. 실시간 최저가 록온 포인트 (선명한 코발트 블루) -->
                <circle cx="34" cy="32" r="3.5" fill="#2563EB" />
              </svg>
            </div>
            <div class="badge">
              <span class="dot"></span>
              PriceTrace 공식 레이더 로고 (48x48 Vector)
            </div>
          </div>
        </body>
        </html>
        """
        page_card.set_content(html_code)
        page_card.wait_for_timeout(500)
        shot_card = os.path.join(ARTIFACT_DIR, "proof_new_logo_only_card.png")
        page_card.screenshot(path=shot_card)
        print(f"  - [2] 신규 로고 단독 고해상도 캡처: {shot_card}")
        page_card.close()

        # 3. Capture icon-512x512.png directly loaded from the server: http://127.0.0.1:8080/icons/icon-512x512.png
        page_png = browser.new_page(viewport={"width": 600, "height": 600})
        page_png.goto("http://127.0.0.1:8080/icons/icon-512x512.png")
        page_png.wait_for_timeout(1000)
        shot_png_direct = os.path.join(ARTIFACT_DIR, "proof_new_logo_png_direct.png")
        page_png.screenshot(path=shot_png_direct)
        print(f"  - [3] icon-512x512.png 브라우저 직접 열람 캡처: {shot_png_direct}")
        page_png.close()

        browser.close()

    print("=" * 60)
    print("🎉 신규 로고 단독 캡처 완료!")
    print("=" * 60)

if __name__ == "__main__":
    capture_logo_only()
