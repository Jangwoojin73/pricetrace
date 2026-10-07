import os
import sys
import json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={'width': 393, 'height': 852},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        is_mobile=True,
        has_touch=True
    )
    page = ctx.new_page()
    page.goto("http://127.0.0.1:8080", wait_until="networkidle")
    page.wait_for_timeout(2500) # 스플래시 종료 대기

    # 메인 모바일 전체 화면 스크린샷
    full_shot = os.path.join(ARTIFACT_DIR, "verify_mobile_radar_floating_badge.png")
    page.screenshot(path=full_shot)

    # 하단 네비게이션 영역만 정밀 크롭 캡처
    nav_el = page.query_selector("#mobileBottomNav")
    dock_shot = os.path.join(ARTIFACT_DIR, "verify_mobile_bottom_nav_dock.png")
    if nav_el:
        nav_el.screenshot(path=dock_shot)

    # 수치 및 정렬 상태 정밀 측정
    metrics = page.evaluate('''() => {
        const nav = document.getElementById("mobileBottomNav");
        const navRect = nav.getBoundingClientRect();

        const badge = document.querySelector(".radar-floating-badge");
        const badgeRect = badge ? badge.getBoundingClientRect() : null;

        const buttons = Array.from(document.querySelectorAll("#mobileBottomNav .mobile-nav-btn"));
        const buttonMetrics = buttons.map(b => {
            const span = b.querySelector("span");
            const icon = b.querySelector(".mobile-nav-icon-box, .radar-floating-badge");
            const spanRect = span ? span.getBoundingClientRect() : null;
            const iconRect = icon ? icon.getBoundingClientRect() : null;
            return {
                label: span ? span.innerText : "",
                spanTop: spanRect ? spanRect.top : 0,
                spanBottom: spanRect ? spanRect.bottom : 0,
                iconTop: iconRect ? iconRect.top : 0,
                iconHeight: iconRect ? iconRect.height : 0
            };
        });

        // 텍스트 라벨 간 최대 Y 차이 (수평 일치도)
        const spanTops = buttonMetrics.map(m => m.spanTop);
        const maxSpanDiff = Math.max(...spanTops) - Math.min(...spanTops);

        // 상한선 돌출 높이 (navTop - badgeTop)
        const protrusionPx = badgeRect ? (navRect.top - badgeRect.top) : 0;

        return {
            navTop: navRect.top,
            badgeTop: badgeRect ? badgeRect.top : 0,
            protrusionPx: protrusionPx,
            maxSpanDiff: maxSpanDiff,
            buttons: buttonMetrics
        };
    }''')

    browser.close()

print("RADAR_BADGE_VERIFY_RESULT")
print(json.dumps(metrics, ensure_ascii=False, indent=2))
