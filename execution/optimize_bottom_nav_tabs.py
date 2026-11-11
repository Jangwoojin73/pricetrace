# -*- coding: utf-8 -*-
"""
Optimize Bottom Nav Tabs 3 (Steady) & 4 (Hotdeal)
- Scale down to normal size matching tabs 1, 2, 5
- Place neatly inside bottom nav bar (remove top protrusion margin-top: -16px)
- Retain exact colors (emerald gradient, rose gradient) and icons (trophy, flame)
"""

HTML_PATH = r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\index.html"
CSS_PATH = r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\style.css"

# 1. Update HTML
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

old_tabs_html = '''      <!-- 3. [🏆 국민 필수 생필품] 탭 (상단 돌출 히어로 볼륨 뱃지 & 특화 강조) -->
      <button 
        type="button" 
        id="mobileNavSteadyBtn" 
        data-mobile-tab="steady" 
        title="국민 필수 생필품 TOP 16" 
        class="mobile-nav-btn hero-tab steady-tab flex flex-col items-center justify-end flex-1 pb-1 pt-0 transition-all cursor-pointer text-emerald-700 font-bold relative"
      >
        <div class="hero-nav-badge steady-badge active:scale-95">
          <i data-lucide="trophy" class="text-white"></i>
        </div>
        <span class="text-[10px] tracking-tight mt-1 leading-none font-black text-emerald-700">생필품</span>
      </button>

      <!-- 4. [🔥 오늘 실시간 핫딜] 탭 (상단 돌출 히어로 볼륨 뱃지 & 특화 강조) -->
      <button 
        type="button" 
        id="mobileNavHotdealBtn" 
        data-mobile-tab="trending" 
        title="오늘 실시간 핫딜 TOP 16" 
        class="mobile-nav-btn hero-tab hotdeal-tab flex flex-col items-center justify-end flex-1 pb-1 pt-0 transition-all cursor-pointer text-rose-600 font-bold relative"
      >
        <div class="hero-nav-badge hotdeal-badge active:scale-95">
          <i data-lucide="flame" class="text-white"></i>
        </div>
        <span class="text-[10px] tracking-tight mt-1 leading-none font-black text-rose-600">핫딜</span>
      </button>'''

new_tabs_html = '''      <!-- 3. [🏆 국민 필수 생필품] 탭 (평범한 크기 축소 & 메뉴 바 안으로 최적화) -->
      <button 
        type="button" 
        id="mobileNavSteadyBtn" 
        data-mobile-tab="steady" 
        title="국민 필수 생필품 TOP 16" 
        class="mobile-nav-btn hero-tab steady-tab group flex flex-col items-center justify-end flex-1 pb-1 pt-1 rounded-2xl transition-all cursor-pointer relative"
      >
        <div class="mobile-nav-pill flex flex-col items-center justify-center w-full max-w-[62px] py-1.5 px-1 rounded-2xl transition-all">
          <div class="hero-nav-badge steady-badge flex items-center justify-center transition-all">
            <i data-lucide="trophy" class="text-white"></i>
          </div>
          <span class="text-[10px] tracking-tight mt-1 leading-none font-bold text-emerald-700">생필품</span>
        </div>
      </button>

      <!-- 4. [🔥 오늘 실시간 핫딜] 탭 (평범한 크기 축소 & 메뉴 바 안으로 최적화) -->
      <button 
        type="button" 
        id="mobileNavHotdealBtn" 
        data-mobile-tab="trending" 
        title="오늘 실시간 핫딜 TOP 16" 
        class="mobile-nav-btn hero-tab hotdeal-tab group flex flex-col items-center justify-end flex-1 pb-1 pt-1 rounded-2xl transition-all cursor-pointer relative"
      >
        <div class="mobile-nav-pill flex flex-col items-center justify-center w-full max-w-[62px] py-1.5 px-1 rounded-2xl transition-all">
          <div class="hero-nav-badge hotdeal-badge flex items-center justify-center transition-all">
            <i data-lucide="flame" class="text-white"></i>
          </div>
          <span class="text-[10px] tracking-tight mt-1 leading-none font-bold text-rose-600">핫딜</span>
        </div>
      </button>'''

if old_tabs_html in html:
    html = html.replace(old_tabs_html, new_tabs_html, 1)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("1. index.html updated successfully.")
else:
    print("1. Warning: old_tabs_html not matched exactly.")

# 2. Update CSS
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

# Replace the hero-nav-badge block
import re

css_hero_badge_pattern = r'/\* ==========================================================================\s+하단 중앙 듀얼 히어로 아일랜드 뱃지.*?(?=/\* 5\. \[목표가/설정\]|\Z)'

new_css_hero_badge = '''/* ==========================================================================
   하단 5대 탭 균형 정렬 및 듀얼 히어로 뱃지 (생필품 & 핫딜 평범한 크기 축소 & 바 내부 최적화)
   ========================================================================== */
.hero-nav-badge {
  width: 25px !important;
  height: 25px !important;
  margin-top: 0 !important;
  margin-bottom: 2px !important;
  border-radius: 9999px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  border: 1.5px solid #ffffff !important;
  position: relative !important;
  z-index: 10 !important;
  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.22s ease !important;
}

.hero-nav-badge.steady-badge {
  background: linear-gradient(135deg, #059669 0%, #0d9488 50%, #0284c7 100%) !important;
  box-shadow: 0 2px 6px -1px rgba(5, 150, 105, 0.38) !important;
}

.hero-nav-badge.hotdeal-badge {
  background: linear-gradient(135deg, #f43f5e 0%, #e11d48 50%, #ea580c 100%) !important;
  box-shadow: 0 2px 6px -1px rgba(225, 29, 72, 0.38) !important;
}

.hero-nav-badge:active {
  transform: scale(0.92) !important;
}

.hero-nav-badge i,
.hero-nav-badge svg {
  width: 14px !important;
  height: 14px !important;
  color: #ffffff !important;
  stroke: #ffffff !important;
  stroke-width: 2.2px !important;
}

/* [생필품] 탭 활성화 캡슐 (산뜻한 에메랄드 소프트 캡슐 배경) */
.mobile-nav-btn.hero-tab[data-mobile-tab="steady"].active .mobile-nav-pill {
  background-color: #ecfdf5 !important;
  border-color: rgba(167, 243, 208, 0.9) !important;
  color: #047857 !important;
  box-shadow: 0 2px 8px -1px rgba(5, 150, 105, 0.16) !important;
}

.mobile-nav-btn.hero-tab[data-mobile-tab="steady"].active .mobile-nav-pill span {
  font-weight: 800 !important;
  color: #047857 !important;
}

.mobile-nav-btn.hero-tab[data-mobile-tab="steady"].active .hero-nav-badge {
  transform: scale(1.08) !important;
  box-shadow: 0 3px 10px -1px rgba(5, 150, 105, 0.55) !important;
}

/* [핫딜] 탭 활성화 캡슐 (화사한 로즈 소프트 캡슐 배경) */
.mobile-nav-btn.hero-tab[data-mobile-tab="trending"].active .mobile-nav-pill {
  background-color: #fff1f2 !important;
  border-color: rgba(254, 205, 211, 0.9) !important;
  color: #be123c !important;
  box-shadow: 0 2px 8px -1px rgba(225, 29, 72, 0.16) !important;
}

.mobile-nav-btn.hero-tab[data-mobile-tab="trending"].active .mobile-nav-pill span {
  font-weight: 800 !important;
  color: #be123c !important;
}

.mobile-nav-btn.hero-tab[data-mobile-tab="trending"].active .hero-nav-badge {
  transform: scale(1.08) !important;
  box-shadow: 0 3px 10px -1px rgba(225, 29, 72, 0.55) !important;
}

'''

match = re.search(css_hero_badge_pattern, css, re.DOTALL)
if match:
    css = css[:match.start()] + new_css_hero_badge + css[match.end():]
    with open(CSS_PATH, "w", encoding="utf-8") as f:
        f.write(css)
    print("2. style.css hero-nav-badge replaced successfully.")
else:
    print("2. Warning: css_hero_badge_pattern not matched.")
