import re

def update_sw():
    with open('public/sw.js', 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace("const CACHE_VERSION = 'v1.3.0';", "const CACHE_VERSION = 'v1.3.1';")
    with open('public/sw.js', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Updated public/sw.js to v1.3.1")

def update_app():
    with open('public/app.js', 'r', encoding='utf-8') as f:
        c = f.read()
    old_ctrl = """      navigator.serviceWorker.addEventListener("controllerchange", () => {
        if (!refreshing) {
          refreshing = true;
          console.log("[PWA] 새로운 Service Worker가 활성화되었습니다.");
        }
      });"""
    new_ctrl = """      navigator.serviceWorker.addEventListener("controllerchange", () => {
        if (!refreshing) {
          refreshing = true;
          console.log("[PWA] 새로운 Service Worker가 활성화되었습니다. 최신 버전으로 자동 갱신합니다.");
          window.location.reload();
        }
      });"""
    c = c.replace(old_ctrl, new_ctrl)
    with open('public/app.js', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Updated public/app.js with controllerchange auto-reload")

def update_index():
    with open('public/index.html', 'r', encoding='utf-8') as f:
        c = f.read()

    # Asset version bumping
    c = re.sub(r'href="/manifest\.json\?v=[^"]+"', 'href="/manifest.json?v=20261020_v131"', c)
    c = re.sub(r'href="style\.css\?v=[^"]+"', 'href="style.css?v=20261020_v131"', c)
    c = re.sub(r'src="app\.js\?v=[^"]+"', 'src="app.js?v=20261020_v131"', c)

    # Inline style on #topLiveBanner
    old_banner = '<div id="topLiveBanner" class="bg-slate-900 text-white text-[11px] sm:text-xs py-1.5 sm:py-2 px-3 sm:px-4 shadow-sm border-b border-slate-800">'
    new_banner = '<div id="topLiveBanner" class="bg-slate-900 text-white text-[11px] sm:text-xs py-1.5 sm:py-2 px-3 sm:px-4 shadow-sm border-b border-slate-800" style="padding-top: max(0.5rem, calc(env(safe-area-inset-top, 0px) + 0.375rem));">'
    c = c.replace(old_banner, new_banner)

    # Inline style on header
    old_header = '<header class="sticky top-0 z-40 bg-white border-b border-slate-200/80 shadow-xs">'
    new_header = '<header class="sticky top-0 z-40 bg-white border-b border-slate-200/80 shadow-xs" style="background-color: #ffffff !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;">'
    c = c.replace(old_header, new_header)

    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Updated public/index.html with cache-busted assets and inline safe-area styles")

def update_style():
    with open('public/style.css', 'r', encoding='utf-8') as f:
        c = f.read()

    old_rule = """#topLiveBanner {
  padding-top: max(0.375rem, env(safe-area-inset-top, 0.375rem));
}"""

    new_rule = """#topLiveBanner {
  padding-top: max(0.5rem, calc(env(safe-area-inset-top, 0px) + 0.375rem)) !important;
}

/* iOS PWA 및 스탠드얼론(홈 화면 추가) 모드: 상태표시줄(44px~54px) 아래로 강제 안전 여백 보장 */
@media all and (display-mode: standalone) {
  #topLiveBanner {
    padding-top: max(3rem, calc(env(safe-area-inset-top, 2.75rem) + 0.375rem)) !important;
  }
}"""

    c = c.replace(old_rule, new_rule)
    with open('public/style.css', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Updated public/style.css with standalone safe-area padding")

if __name__ == '__main__':
    update_sw()
    update_app()
    update_index()
    update_style()
