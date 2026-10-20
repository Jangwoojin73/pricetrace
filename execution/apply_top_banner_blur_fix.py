# -*- coding: utf-8 -*-
"""
Fix Top Live Banner Blurry Effect
- Eliminates animate-pulse opacity fading on the LIVE badge
- Increases font size to text-xs with bold weight and crisp text-white
- Highlights topBannerText in text-amber-300 font-black
- Force-disables any filter, backdrop-filter, text-shadow, box-shadow on header and #topLiveBanner
- Enables -webkit-font-smoothing: antialiased, -moz-osx-font-smoothing: grayscale, text-rendering: optimizeLegibility
- Bumps PWA cache to v1.3.4 and asset queries to v=20261020_v134
"""

import os

# 1. Update public/sw.js
with open('public/sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()

sw = sw.replace("const CACHE_VERSION = 'v1.3.3';", "const CACHE_VERSION = 'v1.3.4';")
with open('public/sw.js', 'w', encoding='utf-8') as f:
    f.write(sw)
print('[1/3] sw.js updated to v1.3.4')

# 2. Update public/index.html
with open('public/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Query version bumps
html = html.replace('v=20261020_v133', 'v=20261020_v134')
html = html.replace('v=20261003_v130', 'v=20261020_v134')

# Banner replacement
old_banner = '''  <!-- 최상단 고정 헤더 통합 컨테이너 (LIVE 특가 배너 + GNB 네비게이션 PC/모바일 동시 상단 영구 고정) -->
  <header class="sticky top-0 z-40 w-full shadow-xs" style="backdrop-filter: none !important; -webkit-backdrop-filter: none !important;">
    <!-- 1. 최상단 실시간 특가 알림 바 (PC 및 모바일 스크롤 시 화면 상단 영구 고정) -->
    <div id="topLiveBanner" class="bg-slate-900 text-white text-[11px] sm:text-xs py-1.5 sm:py-2 px-3 sm:px-4 shadow-sm border-b border-slate-800" style="padding-top: max(0.5rem, calc(env(safe-area-inset-top, 0px) + 0.375rem));">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-2 truncate">
          <span class="inline-flex items-center justify-center px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-coupang text-white animate-pulse shrink-0">
            LIVE
          </span>
          <span class="font-medium text-slate-100 truncate">
            실시간 최저가 추적: <strong class="text-yellow-300 font-bold ml-1" id="topBannerText">네이버 쇼핑 공식 카탈로그 실시간 최저가 레이더</strong>
          </span>
        </div>'''

new_banner = '''  <!-- 최상단 고정 헤더 통합 컨테이너 (LIVE 특가 배너 + GNB 네비게이션 PC/모바일 동시 상단 영구 고정, 흐릿한 효과 100% 완전 제거) -->
  <header class="sticky top-0 z-40 w-full" style="backdrop-filter: none !important; -webkit-backdrop-filter: none !important; filter: none !important; box-shadow: none !important;">
    <!-- 1. 최상단 실시간 특가 알림 바 (PC 및 모바일 스크롤 시 화면 상단 영구 고정, 흐릿한 효과 100% 원천 배제) -->
    <div id="topLiveBanner" class="bg-slate-900 text-white text-xs sm:text-xs py-2 px-3 sm:px-4 border-b border-slate-800" style="filter: none !important; -webkit-filter: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important; text-shadow: none !important; box-shadow: none !important; -webkit-font-smoothing: antialiased !important; -moz-osx-font-smoothing: grayscale !important; text-rendering: optimizeLegibility !important;">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-2 truncate">
          <span class="inline-flex items-center justify-center px-2 py-0.5 rounded-full text-[11px] font-black bg-red-600 text-white shrink-0 tracking-wide" style="filter: none !important; opacity: 1 !important; transform: none !important;">
            LIVE
          </span>
          <span class="font-bold text-white truncate" style="filter: none !important; -webkit-font-smoothing: antialiased !important;">
            실시간 최저가 추적: <strong class="text-amber-300 font-black ml-1 tracking-tight" id="topBannerText">네이버 쇼핑 공식 카탈로그 실시간 최저가 레이더</strong>
          </span>
        </div>'''

html_norm = html.replace('\r\n', '\n')
old_banner_norm = old_banner.replace('\r\n', '\n')
new_banner_norm = new_banner.replace('\r\n', '\n')

if old_banner_norm in html_norm:
    html_norm = html_norm.replace(old_banner_norm, new_banner_norm)
    with open('public/index.html', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(html_norm)
    print('[2/3] index.html updated successfully!')
else:
    print('[2/3] ERROR: old_banner not found in index.html!')

# 3. Update public/style.css
with open('public/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

css_norm = css.replace('\r\n', '\n')

old_css_part = '''/* ==========================================================================
   모바일 기기 상단 상태표시줄(시간/배터리) 안전영역(Safe Area) 및 선명도 최적화
   - iOS PWA 및 노치/다이내믹 아일랜드 기기에서 상단 시간/배터리 표시에 가려지지 않도록 패딩 보장
   - 화면 상단 흐림 효과(blur) 배제 및 시간표시 아래부터 깨끗하게 시작되도록 위치 조정
   ========================================================================== */
#topLiveBanner {
  padding-top: max(0.5rem, calc(env(safe-area-inset-top, 0px) + 0.375rem)) !important;
}

/* iOS PWA 및 스탠드얼론(홈 화면 추가) 모드: 상태표시줄(44px~54px) 아래로 강제 안전 여백 보장 */
@media all and (display-mode: standalone) {
  #topLiveBanner {
    padding-top: max(3rem, calc(env(safe-area-inset-top, 2.75rem) + 0.375rem)) !important;
  }
}

/* GNB 헤더 상단 텍스트 및 로고 선명도 100% 보장 (흐림 효과 원천 배제) */
header {
  -webkit-backdrop-filter: none !important;
  backdrop-filter: none !important;
  background-color: #ffffff !important;
}

/* 최상단 LIVE 특가 배너 + GNB 네비게이션 일체형 상단 고정 */
header.sticky {
  position: sticky !important;
  top: 0 !important;
  z-index: 40 !important;
  width: 100% !important;
}

header #gnbNavBar {
  background-color: #ffffff !important;
}'''

new_css_part = '''/* ==========================================================================
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
}

/* GNB 헤더 상단 텍스트 및 로고 선명도 100% 보장 (흐림 효과 원천 배제) */
header {
  -webkit-backdrop-filter: none !important;
  backdrop-filter: none !important;
  filter: none !important;
  -webkit-filter: none !important;
  box-shadow: none !important;
  background-color: #ffffff !important;
}

/* 최상단 LIVE 특가 배너 + GNB 네비게이션 일체형 상단 고정 */
header.sticky {
  position: sticky !important;
  top: 0 !important;
  z-index: 40 !important;
  width: 100% !important;
}

header #gnbNavBar {
  background-color: #ffffff !important;
}'''

if old_css_part in css_norm:
    css_norm = css_norm.replace(old_css_part, new_css_part)
    with open('public/style.css', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(css_norm)
    print('[3/3] style.css updated successfully!')
else:
    print('[3/3] ERROR: old_css_part not found in style.css!')
