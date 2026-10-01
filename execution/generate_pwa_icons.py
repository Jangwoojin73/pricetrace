import os
from playwright.sync_api import sync_playwright

def generate_icons():
    icons_dir = os.path.join(os.path.dirname(__file__), "..", "public", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    # HTML template with modern vector graphics for PriceTrace
    # Features radar scanner rings, price tag, glowing KRW symbol, and crisp branding
    html_content = """
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
          background: transparent;
          font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
          overflow: hidden;
        }
        .icon-container {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }
        .bg-full {
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, #090d16 0%, #0f172a 45%, #1e1b4b 100%);
        }
        .bg-rounded {
          position: absolute;
          inset: 0;
          background: linear-gradient(135deg, #090d16 0%, #0f172a 45%, #1e1b4b 100%);
          border-radius: 22.5%;
        }
        .content {
          position: relative;
          z-index: 10;
          width: 72%;
          height: 72%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
        .radar-svg {
          width: 100%;
          height: 100%;
          filter: drop-shadow(0 10px 25px rgba(37, 99, 235, 0.45));
        }
      </style>
    </head>
    <body>
      <div id="container" class="icon-container">
        <div id="bg" class="bg-full"></div>
        <div class="content">
          <svg class="radar-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="blueGrad" x1="20" y1="20" x2="180" y2="180" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#38bdf8"/>
                <stop offset="50%" stop-color="#2563eb"/>
                <stop offset="100%" stop-color="#4f46e5"/>
              </linearGradient>
              <linearGradient id="accentGrad" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#34d399"/>
                <stop offset="100%" stop-color="#059669"/>
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>
            
            <!-- Radar scan circles -->
            <circle cx="100" cy="100" r="88" stroke="#1e293b" stroke-width="3" stroke-dasharray="6 6" opacity="0.6"/>
            <circle cx="100" cy="100" r="68" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 4" opacity="0.4"/>
            <circle cx="100" cy="100" r="48" stroke="#60a5fa" stroke-width="1.5" opacity="0.3"/>
            
            <!-- Scanner Beam / Sweep Sector -->
            <path d="M 100 100 L 165 45 A 88 88 0 0 0 100 12 Z" fill="url(#blueGrad)" opacity="0.22"/>
            <line x1="100" y1="100" x2="165" y2="45" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
            
            <!-- Modern Shopping Tag / Shield Body -->
            <path d="M100 42 L146 74 L146 128 L100 160 L54 128 L54 74 Z" 
                  fill="#0f172a" 
                  stroke="url(#blueGrad)" 
                  stroke-width="5" 
                  filter="url(#glow)"/>
            
            <!-- Glowing Inner Badge Gradient -->
            <path d="M100 52 L136 80 L136 122 L100 148 L64 122 L64 80 Z" 
                  fill="url(#blueGrad)" 
                  opacity="0.18"/>

            <!-- Center KRW & Trend Arrow Motif -->
            <!-- Trend up-right arrow line -->
            <path d="M80 124 L120 76 M120 76 L94 76 M120 76 L120 102" 
                  stroke="#38bdf8" 
                  stroke-width="4.5" 
                  stroke-linecap="round" 
                  stroke-linejoin="round"/>
                  
            <!-- KRW Won symbol ₩ -->
            <text x="100" y="118" 
                  text-anchor="middle" 
                  fill="#ffffff" 
                  font-family="'Pretendard', sans-serif" 
                  font-weight="900" 
                  font-size="34" 
                  letter-spacing="-1">₩</text>

            <!-- Blinking Radar Target Ping -->
            <circle cx="150" cy="58" r="6" fill="#34d399" filter="url(#glow)"/>
            <circle cx="150" cy="58" r="10" stroke="#34d399" stroke-width="1.5" opacity="0.75"/>
          </svg>
        </div>
      </div>
    </body>
    </html>
    """

    specs = [
        ("icon-192x192.png", 192, False),
        ("icon-192x192-maskable.png", 192, True),
        ("icon-512x512.png", 512, False),
        ("icon-512x512-maskable.png", 512, True),
        ("apple-touch-icon.png", 180, False),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename, size, is_maskable in specs:
            page = browser.new_page(viewport={"width": size, "height": size})
            page.set_content(html_content)
            
            # Configure maskable background (full bleed) vs standard (rounded or full bleed)
            if is_maskable:
                page.evaluate("""() => {
                    document.getElementById('bg').className = 'bg-full';
                    document.querySelector('.content').style.width = '65%';
                    document.querySelector('.content').style.height = '65%';
                }""")
            else:
                page.evaluate("""() => {
                    document.getElementById('bg').className = 'bg-full';
                    document.querySelector('.content').style.width = '74%';
                    document.querySelector('.content').style.height = '74%';
                }""")
            
            target_path = os.path.join(icons_dir, filename)
            page.screenshot(path=target_path, omit_background=False)
            print(f"Generated: {target_path} ({size}x{size}, maskable={is_maskable})")
            page.close()
        
        browser.close()

if __name__ == "__main__":
    generate_icons()
