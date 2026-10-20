# -*- coding: utf-8 -*-
"""
Apply Status Bar Blur Fix and Safe Area Clearance (Plan Component 1-4)
"""

import os

# 1. Update public/manifest.json
with open('public/manifest.json', 'r', encoding='utf-8') as f:
    manifest = f.read()

manifest = manifest.replace('"theme_color": "#2563eb"', '"theme_color": "#0f172a"')
with open('public/manifest.json', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(manifest)
print("[1/4] manifest.json updated (theme_color: #0f172a)")

# 2. Update public/sw.js
with open('public/sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()

sw = sw.replace("const CACHE_VERSION = 'v1.3.4';", "const CACHE_VERSION = 'v1.3.5';")
with open('public/sw.js', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(sw)
print("[2/4] sw.js updated (CACHE_VERSION: v1.3.5)")

# 3. Update public/index.html
with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Bump asset version strings to v135
html = html.replace('v=20261020_v134', 'v=20261020_v135')

# Update status bar meta tag
html = html.replace(
    '<meta name="apple-mobile-web-app-status-bar-style" content="default">',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black">'
)

# Update splash screen top header: padding-top & remove backdrop-blur-md
old_splash_header = '''    <!-- 2) 상단 헤더: LIVE 뱃지 & 우측 상단 건너뛰기 버튼 -->
    <div class="relative z-10 flex items-center justify-between px-5 pt-[max(1.2rem,env(safe-area-inset-top))]">
      <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 backdrop-blur-md">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        <span class="text-[11px] font-extrabold text-emerald-300 tracking-wide">RADAR LIVE</span>
      </div>
      <button 
        type="button" 
        id="splashSkipBtn" 
        class="px-3.5 py-1.5 rounded-full bg-white/15 hover:bg-white/25 active:scale-95 backdrop-blur-md border border-white/25 text-white text-xs font-bold shadow-sm transition-all flex items-center space-x-1 cursor-pointer"
        title="스플래시 화면 건너뛰기"
      >
        <span>건너뛰기</span>
        <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
      </button>
    </div>'''

new_splash_header = '''    <!-- 2) 상단 헤더: LIVE 뱃지 & 우측 상단 건너뛰기 버튼 (시간표시 54px 아래로 안전 안착, 블러 필터 완전 배제) -->
    <div class="relative z-10 flex items-center justify-between px-5 pt-[max(3.75rem,calc(env(safe-area-inset-top,3.25rem)+0.5rem))]">
      <div class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 shadow-sm" style="filter: none !important; -webkit-filter: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span class="text-[11px] font-black text-emerald-300 tracking-wide">RADAR LIVE</span>
      </div>
      <button 
        type="button" 
        id="splashSkipBtn" 
        class="px-3.5 py-1.5 rounded-full bg-white/20 hover:bg-white/30 active:scale-95 border border-white/30 text-white text-xs font-bold shadow-sm transition-all flex items-center space-x-1 cursor-pointer"
        style="filter: none !important; -webkit-filter: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important;"
        title="스플래시 화면 건너뛰기"
      >
        <span>건너뛰기</span>
        <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
      </button>
    </div>'''

html_norm = html.replace('\r\n', '\n')
old_splash_norm = old_splash_header.replace('\r\n', '\n')
new_splash_norm = new_splash_header.replace('\r\n', '\n')

if old_splash_norm in html_norm:
    html_norm = html_norm.replace(old_splash_norm, new_splash_norm)
    with open('public/index.html', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(html_norm)
    print("[3/4] index.html updated (status-bar-style: black, splash pt: 3.75rem, backdrop-blur removed)")
else:
    print("[3/4] ERROR: old_splash_header not found in index.html!")

# 4. Update public/style.css
with open('public/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css_norm = css.replace('\r\n', '\n')

old_css_part = '''/* ==========================================================================
   모바일 기기 상단 상태표시줄(시간/배터리) 안전영역(Safe Area) 및 100% 선명도 최적화
   - iOS PWA 및 노치/다이내믹 아일랜드 기기에서 상단 시간/배터리 표시에 가려지지 않도록 패딩 보장
   - 화면 상단 흐림 효과(blur, opacity pulse, subpixel aliasing) 완전 배제
   ========================================================================== */
#topLiveBanner {
  background-color: #0f172a !important;
  color: #ffffff !important;
  filter: none !important;
  -webkit-filter: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
  text-shadow: none !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
  text-rendering: optimizeLegibility !important;
  transform: none !important;
  padding-top: max(0.625rem, calc(env(safe-area-inset-top, 0px) + 0.375rem)) !important;
}

#topLiveBanner * {
  filter: none !important;
  -webkit-filter: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
  text-shadow: none !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
  text-rendering: optimizeLegibility !important;
}

/* LIVE 뱃지 펄스 애니메이션(흐릿함 유발 원인) 완전 무효화 및 100% 불투명 선명도 고정 */
#topLiveBanner .animate-pulse,
#topLiveBanner span {
  animation: none !important;
  opacity: 1 !important;
}

/* iOS PWA 및 스탠드얼론(홈 화면 추가) 모드: 상태표시줄(44px~54px) 아래로 강제 안전 여백 보장 */
@media all and (display-mode: standalone) {
  #topLiveBanner {
    padding-top: max(3rem, calc(env(safe-area-inset-top, 2.75rem) + 0.375rem)) !important;
  }
}'''

new_css_part = '''/* ==========================================================================
   모바일 기기 상단 상태표시줄(시간/배터리) 안전영역(Safe Area) 및 100% 선명도 최적화
   - iOS PWA, Safari, 크롬 등 모든 모바일 기기에서 상단 시간/배터리(54px) 아래로 56px 강제 여백 보장
   - 상단 회색 블러 그라데이션 및 잔상 0% 원천 배제
   ========================================================================== */
#topLiveBanner {
  background-color: #0f172a !important;
  color: #ffffff !important;
  filter: none !important;
  -webkit-filter: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
  text-shadow: none !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
  text-rendering: optimizeLegibility !important;
  transform: none !important;
}

/* 모바일 전용 (iOS Safari, PWA, 웹뷰 등 전 환경): 상태표시줄(54px) 아래로 깨끗하게 내려서 배치 */
@media (max-width: 1023px) {
  #topLiveBanner {
    padding-top: max(3.5rem, calc(env(safe-area-inset-top, 3.25rem) + 0.375rem)) !important;
    padding-bottom: 0.625rem !important;
  }
}

/* PC 데스크톱 전용: 상태표시줄이 없으므로 컴팩트한 상하 8px 패딩 유지 */
@media (min-width: 1024px) {
  #topLiveBanner {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
  }
}

#topLiveBanner * {
  filter: none !important;
  -webkit-filter: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;
  text-shadow: none !important;
  -webkit-font-smoothing: antialiased !important;
  -moz-osx-font-smoothing: grayscale !important;
  text-rendering: optimizeLegibility !important;
}

/* LIVE 뱃지 펄스 애니메이션(흐릿함 유발 원인) 완전 무효화 및 100% 불투명 선명도 고정 */
#topLiveBanner .animate-pulse,
#topLiveBanner span {
  animation: none !important;
  opacity: 1 !important;
}'''

if old_css_part in css_norm:
    css_norm = css_norm.replace(old_css_part, new_css_part)
    with open('public/style.css', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(css_norm)
    print("[4/4] style.css updated (mobile padding-top: 3.5rem / 56px, desktop: 0.5rem / 8px)")
else:
    print("[4/4] ERROR: old_css_part not found in style.css!")
