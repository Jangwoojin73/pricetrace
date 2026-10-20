import sys

def main():
    with open('public/index.html', 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Status bar style: change black-translucent to default
    c = c.replace('content="black-translucent"', 'content="default"')

    # 2. Theme color: change to #0f172a (matches top banner background)
    c = c.replace('<meta name="theme-color" content="#2563eb">', '<meta name="theme-color" content="#0f172a">')

    # 3. Add id="topLiveBanner" to top banner
    c = c.replace(
        '<div class="bg-slate-900 text-white text-[11px] sm:text-xs py-1.5 sm:py-2 px-3 sm:px-4 shadow-sm border-b border-slate-800">',
        '<div id="topLiveBanner" class="bg-slate-900 text-white text-[11px] sm:text-xs py-1.5 sm:py-2 px-3 sm:px-4 shadow-sm border-b border-slate-800">'
    )

    # 4. Remove backdrop-blur-md on header and ensure solid background
    c = c.replace('bg-white/95 backdrop-blur-md', 'bg-white')

    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(c)

    print("Successfully updated public/index.html")

    # Now update public/style.css
    with open('public/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    safe_area_css = """
/* ==========================================================================
   모바일 기기 상단 상태표시줄(시간/배터리) 안전영역(Safe Area) 및 선명도 최적화
   - iOS PWA 및 노치/다이내믹 아일랜드 기기에서 상단 시간/배터리 표시에 가려지지 않도록 패딩 보장
   - 화면 상단 흐림 효과(blur) 배제 및 시간표시 아래부터 깨끗하게 시작되도록 위치 조정
   ========================================================================== */
#topLiveBanner {
  padding-top: max(0.375rem, env(safe-area-inset-top, 0.375rem));
}

/* GNB 헤더 상단 텍스트 및 로고 선명도 100% 보장 (흐림 효과 원천 배제) */
header {
  -webkit-backdrop-filter: none !important;
  backdrop-filter: none !important;
  background-color: #ffffff !important;
}
"""

    if '#topLiveBanner' not in css:
        css += safe_area_css
        with open('public/style.css', 'w', encoding='utf-8') as f:
            f.write(css)
        print("Successfully updated public/style.css")
    else:
        print("#topLiveBanner already in public/style.css")

if __name__ == '__main__':
    main()
