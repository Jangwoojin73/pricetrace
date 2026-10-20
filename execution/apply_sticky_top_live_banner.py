import re

def update_index():
    with open('public/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Find where topLiveBanner starts and where header ends
    old_pattern = r'<!-- 1\. 최상단 실시간 특가 알림 바.*?<!-- 2\. GNB 헤더.*?<header[^>]*>\s*<div class="max-w-7xl'
    
    # Let's locate lines 150-175 specifically
    start_tag = '<!-- 1. 최상단 실시간 특가 알림 바'
    idx_start = html.find(start_tag)
    assert idx_start != -1, "start_tag not found"

    gnb_inner_tag = '<div class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-2 lg:py-0 lg:h-20 flex flex-col lg:flex-row lg:items-center justify-between gap-2 lg:gap-4">'
    idx_gnb = html.find(gnb_inner_tag)
    assert idx_gnb != -1, "gnb_inner_tag not found"

    # Replace the outer header structure
    header_block = html[idx_start:idx_gnb]
    print("Old header block:\n", header_block)

    new_header_block = """<!-- 최상단 고정 헤더 통합 컨테이너 (LIVE 특가 배너 + GNB 네비게이션 PC/모바일 동시 상단 영구 고정) -->
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
        </div>
        <div class="hidden lg:flex items-center space-x-5 text-xs text-white shrink-0 font-medium">
          <span class="flex items-center text-slate-100"><i data-lucide="shield-check" class="w-3.5 h-3.5 mr-1.5 text-yellow-300"></i> 광고 상품 100% 자동 필터링</span>
          <span class="flex items-center text-slate-100"><i data-lucide="clock" class="w-3.5 h-3.5 mr-1.5 text-sky-300"></i> <span id="lastUpdatedTime" class="text-yellow-300 font-bold ml-0.5">방금 갱신됨</span></span>
        </div>
      </div>
    </div>

    <!-- 2. GNB 네비게이션 바 (모바일/태블릿 반응형 2단 / 데스크톱 1단 완벽 최적화) -->
    <div id="gnbNavBar" class="bg-white border-b border-slate-200/80">
      """

    html = html[:idx_start] + new_header_block + html[idx_gnb:]

    # Now close the #gnbNavBar div right before </header>
    old_end_header = """          <span class="hidden sm:inline">목표가</span> <span id="btnTargetPriceDisplay">15,000원</span>
        </button>
      </div>

    </div>
  </header>"""

    new_end_header = """          <span class="hidden sm:inline">목표가</span> <span id="btnTargetPriceDisplay">15,000원</span>
        </button>
      </div>

    </div>
    </div><!-- /#gnbNavBar -->
  </header>"""

    assert old_end_header in html, "old_end_header not found"
    html = html.replace(old_end_header, new_end_header)

    # Bump version
    html = html.replace('v=20261020_v132', 'v=20261020_v133')
    html = html.replace('v1.3.2', 'v1.3.3')

    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully updated public/index.html")

def update_sw():
    with open('public/sw.js', 'r', encoding='utf-8') as f:
        sw = f.read()
    sw = sw.replace("const CACHE_VERSION = 'v1.3.2';", "const CACHE_VERSION = 'v1.3.3';")
    with open('public/sw.js', 'w', encoding='utf-8') as f:
        f.write(sw)
    print("Successfully updated public/sw.js to v1.3.3")

def update_style():
    with open('public/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    # Ensure scroll-margin-top is adjusted for the combined sticky header
    css = css.replace("scroll-margin-top: 130px;", "scroll-margin-top: 140px;")
    
    # Add gnbNavBar background style
    if '#gnbNavBar' not in css:
        extra_css = """
/* 최상단 LIVE 특가 배너 + GNB 네비게이션 일체형 상단 고정 */
header.sticky {
  position: sticky !important;
  top: 0 !important;
  z-index: 40 !important;
  width: 100% !important;
}

header #gnbNavBar {
  background-color: #ffffff !important;
}
"""
        css += extra_css

    with open('public/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("Successfully updated public/style.css")

if __name__ == '__main__':
    update_index()
    update_sw()
    update_style()
