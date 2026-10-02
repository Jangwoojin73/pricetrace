import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def create_taskbar_explanation_visual():
    print("=" * 65)
    print("🔍 [Taskbar Audit] 작업표시줄 구버전 아이콘 잔존 원인 및 해결 가이드 캡처 생성")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 880}, device_scale_factor=2)

        html_content = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
          <meta charset="utf-8">
          <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
          <script src="https://cdn.tailwindcss.com"></script>
          <style>
            * { font-family: 'Pretendard', sans-serif; }
          </style>
        </head>
        <body class="bg-slate-950 text-slate-100 p-8 flex flex-col items-center justify-center min-h-screen">

          <div class="max-w-5xl w-full space-y-6">
            
            <!-- 상단 헤더 -->
            <div class="text-center space-y-2">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold">
                ⚠️ Windows OS & PWA 작업표시줄 아이콘 캐시 진단
              </span>
              <h1 class="text-2xl sm:text-3xl font-black text-white tracking-tight">
                작업표시줄 하단 아이콘이 바뀌지 않고 예전 것으로 나오는 원인
              </h1>
              <p class="text-sm text-slate-400 max-w-2xl mx-auto">
                이전에 PC에서 '앱 설치'를 진행하셨던 경우, Windows OS가 설치 시점의 구버전 아이콘을 정적으로 고정(Pin)하여 보관하기 때문에 발생합니다.
              </p>
            </div>

            <!-- 2단 대조 카드 -->
            <div class="grid grid-cols-2 gap-6">
              
              <!-- 좌측: 현재 사용자 작업표시줄 (구버전 캐시) -->
              <div class="bg-slate-900 border-2 border-red-500/40 rounded-2xl p-6 shadow-xl space-y-4">
                <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span class="px-2.5 py-1 rounded-lg bg-red-500/20 text-red-400 font-bold text-xs">
                    현재 화면 (구버전 캐시)
                  </span>
                  <span class="text-xs text-slate-400">어제 설치된 윈도우 바로가기</span>
                </div>

                <!-- 작업표시줄 재현 박스 -->
                <div class="bg-[#18181b] rounded-xl p-6 flex flex-col items-center justify-center gap-3 border border-slate-800">
                  <div class="relative p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 shadow-inner flex flex-col items-center">
                    <!-- 구버전 육각형 엠블럼 재현 SVG -->
                    <svg class="w-14 h-14" viewBox="0 0 200 200" fill="none">
                      <path d="M100 42 L146 74 L146 128 L100 160 L54 128 L54 74 Z" fill="#0f172a" stroke="#2563eb" stroke-width="8"/>
                      <path d="M80 124 L120 76 M120 76 L94 76 M120 76 L120 102" stroke="#38bdf8" stroke-width="7" stroke-linecap="round"/>
                      <text x="100" y="118" text-anchor="middle" fill="#ffffff" font-weight="900" font-size="34">₩</text>
                      <circle cx="150" cy="58" r="8" fill="#34d399"/>
                    </svg>
                    <!-- 활성 인디케이터 바 -->
                    <div class="w-4 h-1 rounded-full bg-slate-400 mt-2"></div>
                  </div>
                  <span class="text-xs font-bold text-red-400">10월 1일 최초 설치 시 고정된 구버전 육각형 아이콘</span>
                </div>

                <div class="text-xs text-slate-400 space-y-1 leading-relaxed bg-red-950/20 p-3 rounded-xl border border-red-900/30">
                  <p class="font-bold text-red-300">🚨 왜 이런가요?</p>
                  <p>Windows는 PWA 앱을 설치할 때 단축키 파일(<code>.lnk</code>) 및 작업표시줄 아이콘 캐시(<code>IconCache.db</code>)에 영구 복사해 둡니다. 웹 서버 소스가 바뀌어도 <strong>기존에 이미 설치된 앱의 윈도우 단축키는 자동으로 바뀌지 않습니다.</strong></p>
                </div>
              </div>

              <!-- 우측: 재설치 시 즉시 적용되는 최신 공식 레이더 로고 -->
              <div class="bg-slate-900 border-2 border-emerald-500/50 rounded-2xl p-6 shadow-xl space-y-4">
                <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span class="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 font-bold text-xs">
                    재설치 후 화면 (최신 공식 로고)
                  </span>
                  <span class="text-xs text-emerald-300 font-semibold">서버에 배포된 최신 자산</span>
                </div>

                <!-- 작업표시줄 재현 박스 -->
                <div class="bg-[#18181b] rounded-xl p-6 flex flex-col items-center justify-center gap-3 border border-slate-800">
                  <div class="relative p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 shadow-inner flex flex-col items-center">
                    <!-- 최신 공식 원형 레이더 로고 -->
                    <img src="http://127.0.0.1:8080/logo_jwj.svg" class="w-14 h-14 object-contain" alt="최신 로고">
                    <!-- 활성 인디케이터 바 -->
                    <div class="w-4 h-1 rounded-full bg-blue-500 mt-2"></div>
                  </div>
                  <span class="text-xs font-bold text-emerald-400">신규 공식 레이더 로고 (최저가 록온 포인트)</span>
                </div>

                <div class="text-xs text-slate-300 space-y-1 leading-relaxed bg-emerald-950/30 p-3 rounded-xl border border-emerald-800/30">
                  <p class="font-bold text-emerald-300">✨ 해결 방법 (10초 완료):</p>
                  <p>기존 설치된 구버전 앱을 <strong>[제거]</strong>한 뒤, 브라우저에서 다시 <strong>[앱 설치]</strong>를 클릭하시면 최신 공식 레이더 아이콘으로 즉시 교체됩니다!</p>
                </div>
              </div>

            </div>

            <!-- 하단 2단계 해결 절차 가이드 박스 -->
            <div class="bg-gradient-to-r from-blue-950/60 via-slate-900 to-indigo-950/60 border border-blue-800/40 rounded-2xl p-5 shadow-lg space-y-3">
              <h3 class="font-bold text-white text-sm flex items-center gap-2">
                <span class="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-black">✔</span>
                작업표시줄 아이콘을 최신 로고로 갱신하는 2단계 초간단 방법
              </h3>
              
              <div class="grid grid-cols-2 gap-4 text-xs">
                <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                  <strong class="text-amber-300 block mb-1">1단계 : 기존 구버전 앱 제거</strong>
                  <p class="text-slate-300 leading-relaxed">
                    실행 중인 PriceTrace 앱 창 상단의 <strong>세 점 메뉴 [ ⋮ ]</strong>를 누르고 <strong>[PriceTrace 제거...]</strong>를 클릭합니다. (또는 윈도우 시작 메뉴에서 우클릭 후 '제거')
                  </p>
                </div>
                <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                  <strong class="text-emerald-300 block mb-1">2단계 : 최신 버전으로 다시 설치</strong>
                  <p class="text-slate-300 leading-relaxed">
                    크롬/엣지에서 <code>https://pricetrace-nu.vercel.app/</code> 접속 후, 주소창 우측 <strong>[앱 설치 (+)]</strong> 버튼을 누르면 새 로고로 등록됩니다!
                  </p>
                </div>
              </div>
            </div>

          </div>

        </body>
        </html>
        """

        page.set_content(html_content)
        page.wait_for_timeout(800)

        path_explanation = os.path.join(ARTIFACT_DIR, "proof_taskbar_icon_explanation.png")
        page.screenshot(path=path_explanation, full_page=True)
        print(f"  - 작업표시줄 진단 캡처 완료: {path_explanation}")

        browser.close()

    print("=" * 65)
    print("🎉 작업표시줄 아이콘 캐시 진단 캡처 생성 완료!")
    print("=" * 65)

if __name__ == "__main__":
    create_taskbar_explanation_visual()
