import os
import sys
import time
import json
import urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_URL = "http://127.0.0.1:8080"

report_data = {
    "stage1": {},
    "stage2": {},
    "stage3": {},
    "stage4": {},
    "stage5": {}
}

print("[START] PriceTrace 서비스 전 기능 전수검사 및 실측 증거 기반 무인 감사 시작...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # =========================================================================
    # [STAGE 01] 기기 환경별 인트로 스플래시 & 메인 랭킹 API 정합성 검증
    # =========================================================================
    print("\n--- [STAGE 01] 기기 환경별 인트로 스플래시 & 메인 랭킹 API 검증 ---")

    # 1-1. 모바일 (iPhone 15 Pro) 스플래시 검증
    m_ctx = browser.new_context(
        viewport={'width': 393, 'height': 852},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        is_mobile=True,
        has_touch=True
    )
    m_page = m_ctx.new_page()
    m_page.goto(BASE_URL)
    m_page.wait_for_timeout(500) # 스플래시 프로그레스 진행 중 캡처
    
    splash_visible = m_page.evaluate('() => { const el = document.getElementById("appSplashScreen"); return el && !el.classList.contains("splash-hidden") && el.offsetHeight > 0; }')
    progress_val = m_page.evaluate('() => document.getElementById("splashProgressPercent") ? document.getElementById("splashProgressPercent").innerText : ""')
    skip_btn_exists = m_page.evaluate('() => !!document.getElementById("splashSkipBtn")')
    
    m_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_01_mobile_splash_progress.png"))
    print(f"  [Mobile Splash] 표시여부: {splash_visible}, 프로그레스: {progress_val}, 건너뛰기버튼: {skip_btn_exists}")

    # 스플래시 종료 대기 (1.8초)
    m_page.wait_for_timeout(2500)
    splash_dismissed = m_page.evaluate('() => { const el = document.getElementById("appSplashScreen"); return el && (el.classList.contains("splash-hidden") || getComputedStyle(el).display === "none"); }')
    print(f"  [Mobile Splash] 자동종료 및 메인 전환 여부: {splash_dismissed}")
    m_ctx.close()

    # 1-2. PC 데스크톱 (1440x900) 스플래시 즉시 배제 검증
    d_ctx = browser.new_context(
        viewport={'width': 1440, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    )
    d_page = d_ctx.new_page()
    d_page.goto(BASE_URL)
    d_page.wait_for_timeout(300)
    d_splash_hidden = d_page.evaluate('() => { const el = document.getElementById("appSplashScreen"); return !el || getComputedStyle(el).display === "none" || el.classList.contains("hidden") || el.offsetHeight === 0; }')
    d_main_visible = d_page.evaluate('() => document.getElementById("welcomeView") && !document.getElementById("welcomeView").classList.contains("hidden")')
    d_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_01_desktop_instant_main.png"))
    print(f"  [PC Desktop] 스플래시 0% 배제 여부: {d_splash_hidden}, 즉시 메인 노출 여부: {d_main_visible}")

    # 1-3. 실시간 랭킹 API 및 메인 추천 카드 정합성 검증
    d_page.wait_for_timeout(1500)
    trending_api_res = d_page.evaluate('''async () => {
        const res = await fetch("/api/trending");
        const json = await res.json();
        return { ok: res.ok, count: json.trending ? json.trending.length : 0, first: json.trending && json.trending[0] ? json.trending[0].title : "" };
    }''')
    trending_cards_count = d_page.evaluate('() => document.querySelectorAll("#welcomeCardsContainer > div").length')
    quick_chips_count = d_page.evaluate('() => document.querySelectorAll("#quickChipsContainer button").length')
    d_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_01_main_trending_view.png"))
    print(f"  [Trending API] 응답: {trending_api_res['ok']}, 수집개수: {trending_api_res['count']}, 메인카드수: {trending_cards_count}, 칩개수: {quick_chips_count}")

    report_data["stage1"] = {
        "mobile_splash": splash_visible and splash_dismissed,
        "desktop_instant": d_splash_hidden and d_main_visible,
        "trending_api": trending_api_res,
        "cards_rendered": trending_cards_count
    }

    # =========================================================================
    # [STAGE 02] 32대 전 품목 듀얼 탭 & 검색 필터링 무결성 검증
    # =========================================================================
    print("\n--- [STAGE 02] 32대 전 품목 듀얼 탭 & 5대 대표 품목 검색 필터링 검증 ---")

    # 2-1. 듀얼 탭 전환 실측 (생필품 16종 + 핫딜 16종)
    d_page.evaluate('() => document.getElementById("tabSteadyBtn") && document.getElementById("tabSteadyBtn").click()')
    d_page.wait_for_timeout(500)
    steady_count = d_page.evaluate('() => document.querySelectorAll("#welcomeCardsContainer > div").length')
    
    d_page.evaluate('() => document.getElementById("tabTrendingBtn") && document.getElementById("tabTrendingBtn").click()')
    d_page.wait_for_timeout(500)
    hotdeal_count = d_page.evaluate('() => document.querySelectorAll("#welcomeCardsContainer > div").length')
    d_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_02_dual_tabs_overview.png"))
    print(f"  [Dual Tabs] 국민 필수 생필품 탭 카드: {steady_count}개, 오늘 실시간 핫딜 탭 카드: {hotdeal_count}개")

    # 2-2. 5대 대표 품목 검색 필터링 실측
    test_items = [
        {"name": "신라면", "query": "농심 신라면 봉지 20개입"},
        {"name": "햇반", "query": "CJ제일제당 햇반 210g 24개"},
        {"name": "커클랜드", "query": "코스트코 커클랜드 휴지 3겹 30롤"},
        {"name": "사과", "query": "사과"},
        {"name": "새우", "query": "새우"}
    ]
    stage2_results = []

    for item in test_items:
        d_page.goto(f"{BASE_URL}/?q=" + urllib.parse.quote(item["query"]), wait_until="networkidle")
        d_page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        d_page.wait_for_timeout(2000)
        
        ranks = d_page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll(".rank-card"));
            return cards.map(c => {
                const title = c.querySelector("h3") ? c.querySelector("h3").innerText : "";
                const priceText = c.querySelector(".font-black") ? c.querySelector(".font-black").innerText.replace(/[^0-9]/g, "") : "0";
                const buyLink = c.querySelector("a") ? c.querySelector("a").href : "";
                return { title, price: parseInt(priceText, 10), buyLink };
            });
        }''')
        
        # 사과 필터링 검증
        is_pure_apple = True
        if item["name"] == "사과":
            for r in ranks:
                if any(bad in r["title"] for bad in ["사과대추", "미니사과", "풋사과"]):
                    is_pure_apple = False
        
        # 오름차순 검증
        prices = [r["price"] for r in ranks if r["price"] > 0]
        is_sorted = (prices == sorted(prices)) and len(prices) >= 2
        
        shot_path = os.path.join(ARTIFACT_DIR, f"audit_02_search_results_{item['name']}.png")
        d_page.screenshot(path=shot_path)
        print(f"  [검색 검증: {item['name']}] 정렬여부: {is_sorted}, 가격군: {prices}, 사과무결성: {is_pure_apple}")
        stage2_results.append({
            "item": item["name"],
            "ranks": ranks,
            "prices": prices,
            "is_sorted": is_sorted,
            "is_pure_apple": is_pure_apple
        })

    report_data["stage2"] = {
        "dual_tabs": {"steady": steady_count, "hotdeal": hotdeal_count},
        "search_results": stage2_results
    }

    # =========================================================================
    # [STAGE 03] PC vs 모바일 기기별 네이버 가격비교 앵커 자동 분기 & 파워링크 광고 100% 우회 실측 검증
    # =========================================================================
    print("\n--- [STAGE 03] PC vs 모바일 기기별 네이버 가격비교 앵커 및 파워링크 광고 100% 우회 실측 검증 ---")

    # 3-1. PC 데스크톱 환경 실측
    d_page.goto(f"{BASE_URL}/?q=" + urllib.parse.quote("농심 신라면 봉지 20개입"), wait_until="networkidle")
    d_page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
    d_page.wait_for_timeout(2000)
    pc_buy_url = d_page.evaluate('() => document.querySelector("#buyButton").href')
    pc_rank1_url = d_page.evaluate('() => document.querySelectorAll(".rank-card a")[0].href')

    d_naver_page = d_ctx.new_page()
    d_naver_page.goto(pc_buy_url, wait_until="networkidle")
    d_naver_page.wait_for_timeout(2000)

    d_scroll_y = d_naver_page.evaluate('window.scrollY')
    d_dui_count = d_naver_page.evaluate('document.querySelectorAll("#shp_dui_root").length')
    d_dui_rect = d_naver_page.evaluate('''() => {
        const el = document.querySelector("#shp_dui_root");
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { top: r.top, bottom: r.bottom, height: r.height };
    }''')
    d_naver_shot = os.path.join(ARTIFACT_DIR, "audit_03_pc_anchor_desktop_verified.png")
    d_naver_page.screenshot(path=d_naver_shot)
    print(f"  [PC 네이버] 링크: {pc_buy_url[:65]}...")
    print(f"  [PC 네이버] scrollY: {d_scroll_y}px, DUI개수: {d_dui_count}, rect.top: {d_dui_rect['top'] if d_dui_rect else 'N/A'}")

    # 3-2. 모바일 (iPhone 15 Pro) 환경 실측
    m_ctx = browser.new_context(
        viewport={'width': 393, 'height': 852},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        is_mobile=True,
        has_touch=True
    )
    m_page = m_ctx.new_page()
    m_page.goto(f"{BASE_URL}/?q=" + urllib.parse.quote("농심 신라면 봉지 20개입"), wait_until="networkidle")
    m_page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
    m_page.wait_for_timeout(2000)

    m_buy_url = m_page.evaluate('() => document.querySelector("#buyButton").href')
    m_rank1_url = m_page.evaluate('() => document.querySelectorAll(".rank-card a")[0].href')
    m_rank2_url = m_page.evaluate('() => document.querySelectorAll(".rank-card a")[1].href')
    m_rank3_url = m_page.evaluate('() => document.querySelectorAll(".rank-card a")[2].href')

    m_naver_page = m_ctx.new_page()
    m_naver_page.goto(m_buy_url, wait_until="networkidle")
    m_naver_page.wait_for_timeout(2000)

    m_scroll_y = m_naver_page.evaluate('window.scrollY')
    m_lis_count = m_naver_page.evaluate('document.querySelectorAll("#shp_lis_root").length')
    m_lis_rect = m_naver_page.evaluate('''() => {
        const el = document.querySelector("#shp_lis_root");
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { top: r.top, bottom: r.bottom, height: r.height };
    }''')
    
    # 모바일 상단 400px 이내 파워링크 광고 존재 여부
    m_ad_count_in_view = m_naver_page.evaluate('''() => {
        const ads = Array.from(document.querySelectorAll('.ad_section, .ad_area, [class*="powerlink"]'));
        return ads.filter(el => {
            const r = el.getBoundingClientRect();
            return r.bottom > 0 && r.top < 400;
        }).length;
    }''')
    
    m_naver_shot = os.path.join(ARTIFACT_DIR, "audit_03_mobile_anchor_lis_verified.png")
    m_naver_page.screenshot(path=m_naver_shot)
    print(f"  [모바일 네이버] 링크: {m_buy_url[:65]}...")
    print(f"  [모바일 네이버] scrollY: {m_scroll_y}px, LIS개수: {m_lis_count}, rect.top: {m_lis_rect['top'] if m_lis_rect else 'N/A'}, 상단광고수: {m_ad_count_in_view}")

    # 1위, 2위, 3위 캡처
    m_naver_page.goto(m_rank1_url, wait_until="networkidle")
    m_naver_page.wait_for_timeout(1000)
    m_naver_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_03_rank1_verified.png"))

    m_naver_page.goto(m_rank2_url, wait_until="networkidle")
    m_naver_page.wait_for_timeout(1000)
    m_naver_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_03_rank2_verified.png"))

    m_naver_page.goto(m_rank3_url, wait_until="networkidle")
    m_naver_page.wait_for_timeout(1000)
    m_naver_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_03_rank3_verified.png"))

    report_data["stage3"] = {
        "pc": {
            "url": pc_buy_url,
            "scrollY": d_scroll_y,
            "dui_count": d_dui_count,
            "rect_top": d_dui_rect["top"] if d_dui_rect else None
        },
        "mobile": {
            "url": m_buy_url,
            "scrollY": m_scroll_y,
            "lis_count": m_lis_count,
            "rect_top": m_lis_rect["top"] if m_lis_rect else None,
            "ads_in_view": m_ad_count_in_view
        }
    }
    m_ctx.close()

    # =========================================================================
    # [STAGE 04] 모바일·태블릿 하단 네비게이션 & 듀얼 탭 고정 스크롤(Scroll Lock) 안정성 검증
    # =========================================================================
    print("\n--- [STAGE 04] 모바일·태블릿 하단 네비게이션 & 듀얼 탭 Scroll Lock 안정성 검증 ---")
    m_ctx4 = browser.new_context(
        viewport={'width': 393, 'height': 852},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        is_mobile=True,
        has_touch=True
    )
    p4 = m_ctx4.new_page()
    p4.goto(BASE_URL)
    p4.wait_for_timeout(2500) # 스플래시 종료 대기

    # 4-1. 핫딜 탭 1회 vs 2회 연속 클릭 실측
    p4.evaluate('() => document.getElementById("mobileNavHotdealBtn").click()')
    p4.wait_for_timeout(500)
    y_hotdeal_1 = p4.evaluate('window.scrollY')

    p4.evaluate('() => document.getElementById("mobileNavHotdealBtn").click()')
    p4.wait_for_timeout(500)
    y_hotdeal_2 = p4.evaluate('window.scrollY')
    diff_hotdeal = abs(y_hotdeal_1 - y_hotdeal_2)
    p4.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_04_mobile_hotdeal_scroll_lock.png"))

    # 4-2. 생필품 탭 1회 vs 2회 연속 클릭 실측
    p4.evaluate('() => document.getElementById("mobileNavSteadyBtn").click()')
    p4.wait_for_timeout(500)
    y_steady_1 = p4.evaluate('window.scrollY')

    p4.evaluate('() => document.getElementById("mobileNavSteadyBtn").click()')
    p4.wait_for_timeout(500)
    y_steady_2 = p4.evaluate('window.scrollY')
    diff_steady = abs(y_steady_1 - y_steady_2)
    p4.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_04_mobile_steady_scroll_lock.png"))

    print(f"  [Scroll Lock] 핫딜 1회({y_hotdeal_1}px) vs 2회({y_hotdeal_2}px) -> 오차: {diff_hotdeal}px")
    print(f"  [Scroll Lock] 생필품 1회({y_steady_1}px) vs 2회({y_steady_2}px) -> 오차: {diff_steady}px")

    # 4-3. 태블릿 환경 (iPad Pro 11, 834x1194) 탭 전환 검증
    t_ctx = browser.new_context(
        viewport={'width': 834, 'height': 1194},
        user_agent='Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
    )
    t_page = t_ctx.new_page()
    t_page.goto(BASE_URL)
    t_page.wait_for_timeout(2500)
    t_page.evaluate('() => document.getElementById("tabTrendingBtn") && document.getElementById("tabTrendingBtn").click()')
    t_page.wait_for_timeout(500)
    t_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_04_tablet_dual_tab_scroll_lock.png"))
    t_ctx.close()
    m_ctx4.close()

    report_data["stage4"] = {
        "hotdeal_diff": diff_hotdeal,
        "steady_diff": diff_steady,
        "lock_perfect": (diff_hotdeal == 0 and diff_steady == 0)
    }

    # =========================================================================
    # [STAGE 05] 전 기기 반응형 레이아웃 및 PWA 설치 인프라 무결성 검증
    # =========================================================================
    print("\n--- [STAGE 05] 5대 디바이스 반응형 레이아웃 및 PWA 인프라 무결성 검증 ---")
    devices = [
        {"name": "iOS 모바일 (iPhone 15 Pro)", "width": 393, "height": 852},
        {"name": "Android 모바일 (Galaxy S24)", "width": 412, "height": 915},
        {"name": "iPadOS 태블릿 (iPad Pro 11)", "width": 834, "height": 1194},
        {"name": "Android 태블릿 (Galaxy Tab S8)", "width": 800, "height": 1280},
        {"name": "PC 데스크톱 (Wide Desktop)", "width": 1440, "height": 900}
    ]
    responsive_matrix = []

    for dev in devices:
        ctx = browser.new_context(viewport={'width': dev['width'], 'height': dev['height']})
        page = ctx.new_page()
        page.goto(f"{BASE_URL}/?q=" + urllib.parse.quote("농심 신라면 봉지 20개입"))
        page.wait_for_timeout(2000)

        overflow_x = page.evaluate('() => document.documentElement.scrollWidth > window.innerWidth')
        body_overflow_x = page.evaluate('() => document.body.scrollWidth > window.innerWidth')
        scroll_w = page.evaluate('() => document.documentElement.scrollWidth')
        inner_w = page.evaluate('() => window.innerWidth')

        responsive_matrix.append({
            "device": dev["name"],
            "viewport": f"{dev['width']}x{dev['height']}",
            "overflow_x": overflow_x or body_overflow_x,
            "scroll_width": scroll_w,
            "inner_width": inner_w
        })
        print(f"  [반응형 검증: {dev['name']}] 너비: {inner_w}px, 스크롤너비: {scroll_w}px, 가로넘침: {overflow_x}")
        ctx.close()

    # PWA 인프라 검증
    pwa_ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    pwa_page = pwa_ctx.new_page()
    pwa_page.goto(BASE_URL)
    pwa_page.wait_for_timeout(1000)

    pwa_checks = pwa_page.evaluate('''() => {
        const manifest = document.querySelector('link[rel="manifest"]') ? document.querySelector('link[rel="manifest"]').href : null;
        const icon192 = document.querySelector('link[rel="apple-touch-icon"]') ? document.querySelector('link[rel="apple-touch-icon"]').href : null;
        const pwaBtn = document.getElementById("pwaInstallBtn") ? true : false;
        return { manifest, icon192, pwaBtn };
    }''')
    pwa_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_05_pwa_install_elements.png"))
    pwa_ctx.close()
    
    # 5대 기기 매트릭스 대표 스크린샷
    d_page.screenshot(path=os.path.join(ARTIFACT_DIR, "audit_05_responsive_matrix.png"))
    d_ctx.close()

    report_data["stage5"] = {
        "responsive_matrix": responsive_matrix,
        "pwa_checks": pwa_checks
    }

    browser.close()

# JSON 저장
with open(os.path.join(ARTIFACT_DIR, "full_inspection_audit_raw.json"), "w", encoding="utf-8") as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

print("\n[COMPLETE] 모든 5단계 무인 검증이 100% 실측 완료되었습니다!")
