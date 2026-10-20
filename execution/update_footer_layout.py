import sys

def main():
    with open('public/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    old_footer_start = '  <!-- 7. 푸터 (기술 스택 및 출처) -->'
    old_footer_end = '  </footer>'

    idx1 = html.find(old_footer_start)
    if idx1 == -1:
        print("old_footer_start not found")
        sys.exit(1)

    idx2 = html.find(old_footer_end, idx1)
    if idx2 == -1:
        print("old_footer_end not found")
        sys.exit(1)

    idx2 += len(old_footer_end)

    new_footer = """  <!-- 7. 푸터 (기술 스택 및 출처) - 모바일 좌측 정렬 & 뱃지 랩 & 하단 네비 겹침 0% 최적화 -->
  <footer class="mt-12 bg-white border-t border-slate-200/80 pt-8 pb-32 lg:pb-10 text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 text-left">
        
        <!-- 좌측: 브랜드 로고 + 타이틀 + 데이터 출처 및 저작권 안내 (모바일 완벽 좌측 정렬) -->
        <div class="space-y-2">
          <div class="flex items-center space-x-2.5">
            <!-- 헤더와 통일된 최저가 레이더 로고 심볼 -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="w-8 h-8 sm:w-10 sm:h-10 object-contain shrink-0" fill="none">
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
            <div class="flex items-center space-x-2">
              <span class="text-base sm:text-lg font-black tracking-tight text-slate-900 flex items-center gap-0.5">
                Price<span class="text-blue-600">Trace</span>
              </span>
              <span class="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200/60">v1.3.1</span>
            </div>
          </div>
          
          <p class="text-slate-600 font-medium text-xs leading-relaxed break-keep">
            데이터 출처: 네이버 쇼핑 공개 BFF API 및 k-skill proxy 엔드포인트 실시간 연동
          </p>
          <p class="text-slate-400 font-normal text-[11px] sm:text-xs">
            © 2026 JANG WOO JIN. All rights reserved.
          </p>
        </div>

        <!-- 우측: 3대 핵심 기술 아키텍처 뱃지 (단어 중간 줄바꿈 방지 & 유연한 가로 랩) -->
        <div class="flex flex-wrap items-center gap-2 pt-1 lg:pt-0 lg:justify-end text-slate-700 font-semibold text-[11px] sm:text-xs">
          <span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200/60 whitespace-nowrap">
            <span class="w-1.5 h-1.5 rounded-full bg-blue-500 mr-1.5 shrink-0"></span>
            3-Layer 아키텍처
          </span>
          <span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200/60 whitespace-nowrap">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 shrink-0"></span>
            결정론적 클린 필터
          </span>
          <span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200/60 whitespace-nowrap">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 mr-1.5 shrink-0"></span>
            경량 Python 서버
          </span>
        </div>

      </div>
    </div>
  </footer>"""

    html = html[:idx1] + new_footer + html[idx2:]

    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully replaced footer in public/index.html")

if __name__ == '__main__':
    main()
