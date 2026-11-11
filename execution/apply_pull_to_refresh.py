# -*- coding: utf-8 -*-
import os

HTML_PATH = r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\index.html"
CSS_PATH = r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\style.css"
JS_PATH = r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\app.js"

# 1. Update index.html
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

target_main = '<main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-28 lg:pb-8 space-y-8">'
ptr_snippet = '''<main id="mainContent" class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 pb-28 lg:pb-8 space-y-8">

    <!-- 모바일/태블릿 전용 커스텀 Pull-to-Refresh 인디케이터 (헤더 고정, 히어로 섹션 상단에서 동작) -->
    <div id="ptrIndicator" class="ptr-indicator-wrap" aria-hidden="true">
      <div class="ptr-pill">
        <span id="ptrIconBox" class="ptr-icon-box">
          <svg id="ptrArrow" class="w-4 h-4 text-sky-400 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
          </svg>
          <svg id="ptrSpinner" class="w-4 h-4 text-sky-400 animate-spin hidden" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        <span id="ptrText" class="text-xs font-bold text-sky-200 tracking-tight">당겨서 최저가 새로고침</span>
      </div>
    </div>'''

if target_main in html:
    html = html.replace(target_main, ptr_snippet, 1)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("1. index.html updated successfully.")
elif '<main id="mainContent"' in html:
    print("1. index.html already has mainContent and ptrIndicator.")
else:
    print("1. Warning: target_main not found in index.html.")

# 2. Update style.css
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

ptr_css = '''
/* ==========================================================================
   모바일 & 태블릿 전용 Pull-to-Refresh 및 브라우저 기본 오버스크롤 차단
   - 헤더(LIVE 배너, 로고, 검색창)는 화면 최상단에 바위처럼 고정
   - 히어로 섹션(#mainContent)부터 아래로 당겨졌다가 탄성 복귀하며 새로고침
   ========================================================================== */
@media (max-width: 1023px) {
  html, body {
    overscroll-behavior-y: none !important;
    -webkit-overflow-scrolling: touch;
  }

  header.sticky {
    position: sticky !important;
    top: 0 !important;
    z-index: 40 !important;
    transform: none !important;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.4) !important;
  }
}

#mainContent {
  will-change: transform;
}

.ptr-indicator-wrap {
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: max-height 0.2s cubic-bezier(0.2, 0.8, 0.2, 1), opacity 0.2s ease, margin 0.2s ease;
  pointer-events: none;
  margin-bottom: 0;
  will-change: max-height, opacity;
}

.ptr-indicator-wrap.ptr-active {
  opacity: 1;
  margin-bottom: 0.5rem;
}

.ptr-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 1rem;
  border-radius: 9999px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.4);
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.35), 0 0 16px rgba(56, 189, 248, 0.25);
}

.ptr-icon-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.125rem;
  height: 1.125rem;
}
'''

if ".ptr-indicator-wrap" not in css:
    css += ptr_css
    with open(CSS_PATH, "w", encoding="utf-8") as f:
        f.write(css)
    print("2. style.css updated successfully.")
else:
    print("2. style.css already contains PTR styles.")

# 3. Update app.js (Inject setupPullToRefresh)
with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

ptr_js_code = '''
// ==========================================================================
// 모바일 & 태블릿 전용 Pull-to-Refresh (히어로 섹션 풀다운 새로고침)
// - 헤더(상단 LIVE 배너 + 로고 + 검색창)는 상단 고정 유지
// - 히어로 섹션(#mainContent)부터 아래로 당겨지며 최저가 실시간 새로고침
// ==========================================================================
function setupPullToRefresh() {
  const mainContent = document.getElementById("mainContent");
  const ptrIndicator = document.getElementById("ptrIndicator");
  const ptrArrow = document.getElementById("ptrArrow");
  const ptrSpinner = document.getElementById("ptrSpinner");
  const ptrText = document.getElementById("ptrText");
  const mobileRefreshBtn = document.getElementById("mobileRefreshBtn");
  const refreshBtn = document.getElementById("refreshBtn");

  if (!mainContent || !ptrIndicator) return;

  let startY = 0;
  let startX = 0;
  let currentY = 0;
  let isPulling = false;
  let isRefreshing = false;
  const PULL_THRESHOLD = 60; // 당김 트리거 임계값(px)

  const resetPtr = () => {
    isPulling = false;
    isRefreshing = false;
    if (mainContent) {
      mainContent.style.transition = "transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)";
      mainContent.style.transform = "translateY(0px)";
    }
    if (ptrIndicator) {
      ptrIndicator.style.maxHeight = "0px";
      ptrIndicator.classList.remove("ptr-active");
    }
    if (ptrArrow) {
      ptrArrow.classList.remove("hidden");
      ptrArrow.style.transform = "rotate(0deg)";
    }
    if (ptrSpinner) {
      ptrSpinner.classList.add("hidden");
    }
    if (ptrText) {
      ptrText.textContent = "당겨서 최저가 새로고침";
    }
  };

  window.addEventListener("touchstart", (e) => {
    if (window.innerWidth >= 1024) return; // 데스크톱 제외
    if (isRefreshing) return;
    if (window.scrollY > 4) return; // 최상단 스크롤에서만 감지

    startY = e.touches[0].clientY;
    startX = e.touches[0].clientX;
    isPulling = false;
  }, { passive: true });

  window.addEventListener("touchmove", (e) => {
    if (window.innerWidth >= 1024 || isRefreshing) return;
    if (window.scrollY > 4) {
      if (isPulling) resetPtr();
      return;
    }

    currentY = e.touches[0].clientY;
    const currentX = e.touches[0].clientX;
    const diffY = currentY - startY;
    const diffX = currentX - startX;

    // 수직 드래그가 수평보다 크고 아래로 당길 때
    if (diffY > 8 && Math.abs(diffY) > Math.abs(diffX) * 1.5) {
      isPulling = true;
      if (e.cancelable) e.preventDefault(); // 기본 브라우저 바운스 방지

      // 고무줄 저항감 계수 적용 (최대 85px)
      const pullDist = Math.min(85, diffY * 0.45);
      
      mainContent.style.transition = "none";
      mainContent.style.transform = `translateY(${pullDist * 0.75}px)`;
      
      ptrIndicator.classList.add("ptr-active");
      ptrIndicator.style.maxHeight = `${pullDist}px`;

      if (pullDist >= PULL_THRESHOLD) {
        if (ptrArrow) ptrArrow.style.transform = "rotate(180deg)";
        if (ptrText) ptrText.textContent = "손을 놓아 최저가 갱신";
      } else {
        if (ptrArrow) ptrArrow.style.transform = "rotate(0deg)";
        if (ptrText) ptrText.textContent = "당겨서 최저가 새로고침";
      }
    }
  }, { passive: false });

  window.addEventListener("touchend", () => {
    if (!isPulling || isRefreshing) return;
    
    const diffY = currentY - startY;
    const pullDist = Math.min(85, diffY * 0.45);

    if (pullDist >= PULL_THRESHOLD) {
      // 갱신 트리거 상태 진입
      isRefreshing = true;
      if (navigator.vibrate) {
        try { navigator.vibrate(25); } catch (_) {}
      }

      if (ptrArrow) ptrArrow.classList.add("hidden");
      if (ptrSpinner) ptrSpinner.classList.remove("hidden");
      if (ptrText) ptrText.textContent = "실시간 최저가 레이더 갱신 중...";

      mainContent.style.transition = "transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1)";
      mainContent.style.transform = "translateY(52px)";
      ptrIndicator.style.maxHeight = "52px";

      // 기존 새로고침 로직 트리거
      if (mobileRefreshBtn) {
        mobileRefreshBtn.click();
      } else if (refreshBtn) {
        refreshBtn.click();
      }

      // 갱신 완료 후 부드럽게 원래 위치로 복귀
      setTimeout(() => {
        resetPtr();
      }, 850);
    } else {
      resetPtr();
    }
  }, { passive: true });
}
'''

if "function setupPullToRefresh()" not in js:
    # Append the function and call it inside DOMContentLoaded
    init_call_target = "setupSplashScreen();"
    if init_call_target in js:
        js = js.replace(init_call_target, init_call_target + "\n  setupPullToRefresh();", 1)
        js += "\n" + ptr_js_code
        with open(JS_PATH, "w", encoding="utf-8") as f:
            f.write(js)
        print("3. app.js updated successfully with setupPullToRefresh.")
    else:
        print("3. Warning: setupSplashScreen() not found in app.js.")
else:
    print("3. app.js already contains setupPullToRefresh.")
