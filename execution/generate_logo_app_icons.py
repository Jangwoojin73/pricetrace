import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

# The EXACT SVG logo used on the website header (lines 102-115 of public/index.html)
# - Minimal bold radar rim: #0F172A
# - 4-direction precision aim ticks: #0F172A
# - Trend drop arrow: #0F172A
# - Real-time lowest price lock-on point: #2563EB
def build_html(scale_pct, is_maskable=False):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
          width: 100vw;
          height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #FFFFFF;
          overflow: hidden;
        }}
        .icon-wrapper {{
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #FFFFFF;
          position: relative;
        }}
        .logo-svg {{
          width: {scale_pct}%;
          height: {scale_pct}%;
          filter: drop-shadow(0 2px 8px rgba(15, 23, 42, 0.08));
        }}
      </style>
    </head>
    <body>
      <div class="icon-wrapper">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="logo-svg" fill="none">
          <!-- 1. 미니멀 볼드 레이더 원형 림 -->
          <circle cx="24" cy="24" r="20" stroke="#0F172A" stroke-width="3" />
          
          <!-- 2. 레이더 외곽 정밀 조준 틱 (절제된 4방위 틱) -->
          <line x1="24" y1="4" x2="24" y2="8" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
          <line x1="24" y1="40" x2="24" y2="44" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
          <line x1="4" y1="24" x2="8" y2="24" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
          <line x1="40" y1="24" x2="44" y2="24" stroke="#0F172A" stroke-width="2.5" stroke-linecap="round" />
          
          <!-- 3. 시원하고 직관적인 가격 급락 트렌드 화살표 (볼드 블랙) -->
          <path d="M14 18L22 26L27 21L34 32" stroke="#0F172A" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
          <polyline points="26 32 34 32 34 24" stroke="#0F172A" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
          
          <!-- 4. 실시간 최저가 록온 포인트 (선명한 코발트 블루) -->
          <circle cx="34" cy="32" r="3.5" fill="#2563EB" />
        </svg>
      </div>
    </body>
    </html>
    """

def generate_logo_icons():
    specs = [
        ("icon-192x192.png", 192, 75, False),
        ("icon-192x192-maskable.png", 192, 62, True),
        ("icon-512x512.png", 512, 75, False),
        ("icon-512x512-maskable.png", 512, 62, True),
        ("apple-touch-icon.png", 180, 75, False),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename, size, scale, is_maskable in specs:
            page = browser.new_page(viewport={"width": size, "height": size})
            html_code = build_html(scale, is_maskable)
            page.set_content(html_code)
            
            target_path = os.path.join(ICONS_DIR, filename)
            page.screenshot(path=target_path, omit_background=False)
            print(f"생성 완료: {target_path} ({size}x{size})")

            # Also copy to artifacts directory for visual comparison
            artifact_copy = os.path.join(ARTIFACT_DIR, f"new_logo_{filename}")
            page.screenshot(path=artifact_copy, omit_background=False)
            print(f"아티팩트 복사: {artifact_copy}")

            page.close()
        browser.close()

if __name__ == "__main__":
    generate_logo_icons()
