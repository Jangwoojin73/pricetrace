# -*- coding: utf-8 -*-
"""
Step 8: UI Enhancements Audit, Live Production Cross-Check & Dynamic Full Inspection Markdown Assembly
- 절대 하드코딩 금지: 모든 명도대비, 패딩, 블러, 클리어런스, 판정은 실제 DOM/CSS 실측치로만 계산 및 기록
"""
import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import json
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, PROD_URL, ARTIFACT_DIR, RESULTS_DIR, DOCS_REPORT_DIR, CHROMIUM_ARGS, MOBILE_UA, PC_UA,
    save_step_result, create_sentinel, collect_broken_images, sentinel_summary, safe_screenshot
)


def parse_rgb(color_str):
    if not color_str:
        return None
    m = re.findall(r"(\d+(?:\.\d+)?)", color_str)
    if len(m) >= 3:
        return (float(m[0]), float(m[1]), float(m[2]))
    return None


def calculate_contrast_ratio(rgb1, rgb2):
    if not rgb1 or not rgb2:
        return 0.0
    def get_luminance(r, g, b):
        a = [v / 255.0 for v in [r, g, b]]
        a = [((v + 0.055) / 1.055) ** 2.4 if v > 0.03928 else v / 12.92 for v in a]
        return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722
    l1 = get_luminance(*rgb1)
    l2 = get_luminance(*rgb2)
    if l1 < l2:
        l1, l2 = l2, l1
    return round((l1 + 0.05) / (l2 + 0.05), 2)


def main():
    t_start = time.time()
    print(">>> [Step 8] Auditing UI Enhancements, Contrast Ratios, Footer Clearance & Vercel Live Cross-Check...")
    metrics = {}
    s_all = {"console_errors": [], "page_errors": [], "http_errors": [], "failed_requests": [], "broken_images_count": 0, "broken_image_srcs": []}

    def merge_s(s):
        for k in ["console_errors", "page_errors", "http_errors", "failed_requests", "broken_image_srcs"]:
            s_all[k].extend(s[k])
        s_all["broken_images_count"] += s["broken_images_count"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # -----------------------------------------------------------------
        # 8-1. Mobile UI Enhancements (Header 3D/Blur, Banner Sharpness, 34px Safe-Area, Refresh Contrast/Spin, Footer Clearance)
        # -----------------------------------------------------------------
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent=MOBILE_UA,
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_m = m_ctx.new_page()
        p_m.set_default_timeout(10000)
        s_m = create_sentinel(p_m)
        p_m.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_m.goto(BASE_URL, wait_until="domcontentloaded")
        p_m.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=8000)
        p_m.wait_for_timeout(500)

        header_eval = p_m.evaluate('''() => {
            const hdr = document.querySelector("header.sticky");
            const gnb = document.getElementById("gnbNavBar");
            const banner = document.getElementById("topLiveBanner");
            const bannerText = document.getElementById("topBannerText");
            const hdrStyle = hdr ? window.getComputedStyle(hdr) : null;
            const gnbStyle = gnb ? window.getComputedStyle(gnb) : null;
            const bannerStyle = banner ? window.getComputedStyle(banner) : null;
            const textStyle = bannerText ? window.getComputedStyle(bannerText) : null;
            return {
                headerBgImage: hdrStyle ? hdrStyle.backgroundImage : "",
                gnbBackdropFilter: gnbStyle ? (gnbStyle.backdropFilter || gnbStyle.webkitBackdropFilter || "") : "",
                bannerFilter: bannerStyle ? bannerStyle.filter : "",
                bannerOpacity: bannerStyle ? bannerStyle.opacity : "",
                bannerPaddingTop: bannerStyle ? bannerStyle.paddingTop : "",
                bannerTextFilter: textStyle ? textStyle.filter : ""
            };
        }''')
        snap_banner = os.path.join(ARTIFACT_DIR, "audit_08_mobile_calibrated_header_10px.png")
        safe_screenshot(p_m, snap_banner)

        # Mobile Refresh Button Color & Dynamic Spin Check
        m_refresh_style = p_m.evaluate('''() => {
            const btn = document.getElementById("mobileRefreshBtn");
            const icon = btn ? (btn.querySelector("svg") || btn.querySelector("i")) : null;
            const btnS = btn ? window.getComputedStyle(btn) : null;
            const iconS = icon ? window.getComputedStyle(icon) : null;
            return {
                bgColor: btnS ? btnS.backgroundColor : "",
                iconStroke: iconS ? (iconS.stroke !== "none" ? iconS.stroke : iconS.color) : ""
            };
        }''')
        m_contrast = calculate_contrast_ratio(
            parse_rgb(m_refresh_style["bgColor"]),
            parse_rgb(m_refresh_style["iconStroke"])
        )

        p_m.click("#mobileRefreshBtn")
        p_m.wait_for_timeout(50)
        spin_connected = p_m.evaluate('''() => {
            const icon = document.querySelector("#mobileRefreshBtn svg, #mobileRefreshBtn i");
            return icon ? icon.classList.contains("animate-spin") : false;
        }''')
        p_m.wait_for_timeout(600)

        # Footer Layout, Badges & Bottom Dock Clearance
        # PWA 배너가 푸터를 가리지 않도록 닫기 처리 후 순수 푸터-독 간격 실측
        p_m.evaluate('''() => {
            const dismiss = document.getElementById("pwaBannerDismissBtn");
            if (dismiss) dismiss.click();
        }''')
        p_m.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        p_m.wait_for_timeout(450)
        # 하단 독을 화면에 띄우기 위해 미세 업스크롤 (-40px -> 독 노출 상태에서 푸터 최하단 겹침 여부 정밀 실측)
        for _ in range(2):
            p_m.mouse.wheel(0, -25)
            p_m.wait_for_timeout(60)
        p_m.wait_for_timeout(450)

        footer_eval = p_m.evaluate('''() => {
            const footer = document.querySelector("footer");
            const nav = document.getElementById("mobileBottomNav");
            const layoutRow = footer ? footer.querySelector("div.text-left") : null;
            const fStyle = footer ? window.getComputedStyle(footer) : null;
            const badges = footer ? footer.querySelectorAll("div.flex-wrap > span") : [];
            const badgesWrap = footer ? footer.querySelector("div.flex-wrap") : null;
            const bRect = badgesWrap ? badgesWrap.getBoundingClientRect() : null;
            const nRect = nav ? nav.getBoundingClientRect() : null;
            const navVisible = nav ? !nav.classList.contains("nav-dock-hidden") : false;
            return {
                textLeftAligned: !!layoutRow && window.getComputedStyle(layoutRow).textAlign === "left",
                footerPaddingBottom: fStyle ? fStyle.paddingBottom : "",
                badgeCount: badges.length,
                badgeBottomY: bRect ? Math.round(bRect.bottom) : 0,
                navTopY: nRect ? Math.round(nRect.top) : 0,
                navVisible: navVisible,
                clearancePx: (bRect && nRect) ? Math.round(nRect.top - bRect.bottom) : 0,
                hasOverlap: (bRect && nRect) ? bRect.bottom > nRect.top : false
            };
        }''')
        snap_footer = os.path.join(ARTIFACT_DIR, "audit_08_mobile_footer_clearance.png")
        safe_screenshot(p_m, snap_footer)

        collect_broken_images(p_m, s_m)
        merge_s(s_m)

        metrics["mobile_ui"] = {
            "header": header_eval,
            "mobile_refresh": m_refresh_style,
            "mobile_contrast": m_contrast,
            "spin_connected": spin_connected,
            "footer_clearance": footer_eval,
            "snap_banner": snap_banner,
            "snap_footer": snap_footer
        }
        m_ctx.close()

        # -----------------------------------------------------------------
        # 8-2. PC Refresh Button Contrast (#refreshBtn) - Real Computed Style
        # -----------------------------------------------------------------
        pc_ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, user_agent=PC_UA, service_workers="block")
        p_pc = pc_ctx.new_page()
        p_pc.set_default_timeout(10000)
        s_pc = create_sentinel(p_pc)
        p_pc.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_pc.goto(BASE_URL, wait_until="domcontentloaded")
        p_pc.wait_for_timeout(400)

        pc_refresh = p_pc.evaluate('''() => {
            const btn = document.getElementById("refreshBtn");
            const span = btn ? btn.querySelector("span") : null;
            const btnS = btn ? window.getComputedStyle(btn) : null;
            const spanS = span ? window.getComputedStyle(span) : null;
            return {
                bgColor: btnS ? btnS.backgroundColor : "",
                textColor: spanS ? spanS.color : (btnS ? btnS.color : ""),
                fontWeight: spanS ? spanS.fontWeight : (btnS ? btnS.fontWeight : ""),
                textShadow: spanS ? spanS.textShadow : (btnS ? btnS.textShadow : "")
            };
        }''')
        pc_contrast = calculate_contrast_ratio(
            parse_rgb(pc_refresh["bgColor"]),
            parse_rgb(pc_refresh["textColor"])
        )
        snap_pc = os.path.join(ARTIFACT_DIR, "audit_08_pc_header_high_contrast.png")
        safe_screenshot(p_pc, snap_pc)

        collect_broken_images(p_pc, s_pc)
        merge_s(s_pc)
        metrics["pc_ui"] = {
            "style": pc_refresh,
            "pc_contrast": pc_contrast,
            "snap_pc": snap_pc
        }
        pc_ctx.close()

        # -----------------------------------------------------------------
        # 8-3. Production Vercel Live Cross-Check (Search Bar Smart Scroll v1.6.1)
        # -----------------------------------------------------------------
        live_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent=MOBILE_UA,
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_live = live_ctx.new_page()
        p_live.set_default_timeout(12000)
        s_live = create_sentinel(p_live)
        p_live.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_live.goto(PROD_URL, wait_until="domcontentloaded")
        p_live.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=10000)
        p_live.wait_for_timeout(1000)

        for _ in range(5):
            p_live.mouse.wheel(0, 100)
            p_live.wait_for_timeout(70)
        p_live.wait_for_timeout(500)
        live_down = p_live.evaluate('''() => ({
            scrollY: window.scrollY,
            headerHeight: Math.round(document.querySelector("header.sticky").getBoundingClientRect().height),
            searchHeight: Math.round(document.getElementById("gnbSearchSection").getBoundingClientRect().height),
            isCollapsed: document.body.classList.contains("header-search-collapsed")
        })''')

        for _ in range(3):
            p_live.mouse.wheel(0, -100)
            p_live.wait_for_timeout(70)
        p_live.wait_for_timeout(500)
        live_up = p_live.evaluate('''() => ({
            scrollY: window.scrollY,
            headerHeight: Math.round(document.querySelector("header.sticky").getBoundingClientRect().height),
            searchHeight: Math.round(document.getElementById("gnbSearchSection").getBoundingClientRect().height),
            isCollapsed: document.body.classList.contains("header-search-collapsed")
        })''')
        merge_s(s_live)
        metrics["prod_live_crosscheck"] = {
            "url": PROD_URL,
            "down_collapsed": live_down,
            "up_revealed": live_up,
            "live_v161_verified": live_down["isCollapsed"] and live_down["searchHeight"] == 0 and (not live_up["isCollapsed"]) and live_up["searchHeight"] >= 70
        }
        live_ctx.close()

        browser.close()

    s_sum = sentinel_summary(s_all)
    fail_reasons = []
    if "header_bg_pricetracker" not in header_eval["headerBgImage"]:
        fail_reasons.append(f"Header background image mismatch: {header_eval['headerBgImage']}")
    if "blur(10px)" not in header_eval["gnbBackdropFilter"]:
        fail_reasons.append(f"GNB backdropFilter mismatch: {header_eval['gnbBackdropFilter']}")
    if header_eval["bannerFilter"] != "none" or header_eval["bannerOpacity"] != "1":
        fail_reasons.append(f"Banner sharpness failed: filter={header_eval['bannerFilter']}, opacity={header_eval['bannerOpacity']}")
    if m_contrast < 8.5:
        fail_reasons.append(f"Mobile Refresh Button contrast {m_contrast}:1 < 8.5:1 (actual stroke={m_refresh_style['iconStroke']}, bg={m_refresh_style['bgColor']})")
    if pc_contrast < 7.0:
        fail_reasons.append(f"PC Refresh Button contrast {pc_contrast}:1 < 7.0:1")
    if not spin_connected:
        fail_reasons.append("Refresh icon animate-spin not triggered on click")
    if not footer_eval["textLeftAligned"] or footer_eval["hasOverlap"]:
        fail_reasons.append(f"Footer layout/clearance failed: left={footer_eval['textLeftAligned']}, overlap={footer_eval['hasOverlap']}")
    if not metrics["prod_live_crosscheck"]["live_v161_verified"]:
        fail_reasons.append("Vercel live production v1.6.1 crosscheck mismatch")
    if s_sum["total_errors"] > 0:
        fail_reasons.append(f"Sentinel detected {s_sum['total_errors']} errors")

    passed = len(fail_reasons) == 0

    result = {
        "step": 8,
        "name": "UI Enhancements Audit, Vercel Cross-Check & Final Report Assembly",
        "status": "PASS" if passed else "FAIL",
        "fail_reasons": fail_reasons,
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": s_sum,
        "metrics": metrics
    }
    print(f"[Step 8] {result['elapsed_sec']}s | Contrast M={m_contrast}:1 / PC={pc_contrast}:1 | Spin={spin_connected} | Clearance={footer_eval['clearancePx']}px | LiveSync={metrics['prod_live_crosscheck']['live_v161_verified']} | Status={result['status']}")
    save_step_result(8, result)

    # 8-4. Assemble Full Dynamic Markdown Report from actual JSON files
    assemble_final_markdown()
    sys.exit(0 if passed else 1)


def assemble_final_markdown():
    print(">>> Assembling FULL_INSPECTION_AUDIT_REPORT.md purely from observed step0~step8 JSON metrics...")
    results = {}
    for i in range(9):
        fpath = os.path.join(RESULTS_DIR, f"step{i}.json")
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                results[f"step{i}"] = json.load(f)

    total_elapsed = round(sum(r.get("elapsed_sec", 0) for r in results.values()), 2)
    total_sentinel_errors = sum(r.get("sentinel", {}).get("total_errors", 0) for r in results.values())
    all_passed = all(results.get(f"step{i}", {}).get("status") == "PASS" for i in range(9))
    overall_grade = "GRADE AAA+ (ALL PASS ✅)" if (all_passed and total_sentinel_errors == 0) else "PARTIAL / ACTION REQUIRED ⚠️"
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    def step_row(idx, title, target):
        r = results.get(f"step{idx}", {})
        st = r.get("status", "MISSING")
        el = r.get("elapsed_sec", 0)
        err = r.get("sentinel", {}).get("total_errors", 0)
        mark = "**PASS** ✅" if st == "PASS" else f"**{st}** ❌"
        return f"| **Step {idx}** | {title} | {target} | `{el}s` | {err}건 | {mark} |"

    summary_rows = "\n".join([
        step_row(0, "환경 점검 & 전역 센티널 초기화", "Local 8080 & Vercel Live & v1.6.1 동기화"),
        step_row(1, "인트로 스플래시 & 메인 랭킹 API", "Mobile/Tablet 스플래시, PC 0초 바이패스, `/api/trending` 대조"),
        step_row(2, "32대 듀얼 탭 & 5대 품목 검색", "16+16 전수, 5대 품목 오름차순, 사과 노이즈 0%"),
        step_row(3, "3단계 수집 & 오뚜기밥 단종 링크 배제", "오뚜기밥 24개 단종 URL 0건 & 타겟 직결 실측"),
        step_row(4, "네이버 가격 앵커 & 광고 우회 실측", "PC `#shp_dui_root` vs 모바일 `#shp_lis_root` 실측"),
        step_row(5, "하단 독(25px)·고정 스크롤·PTR·검색바 은닉", "5대 탭, 0px 락, 실제 TouchEvent PTR, v1.6.1 떨림 방지"),
        step_row(6, "레이더 모달 & iOS 줌 차단 & 임의 검색", "오토포커스, 모달 은닉, `fontSize >= 16px`, 다이슨·맥북"),
        step_row(7, "5대 디바이스 반응형 & PWA 인프라", "5대 해상도 오버플로우 0건, PC 검색 가드, PWA 리소스 200 OK"),
        step_row(8, "신규 UI 개선 실측 & 프로덕션 교차 검증", "헤더 블러, 동적 AAA 대비, 푸터 클리어런스, Vercel Live")
    ])

    # Extract actual measured values safely
    s0 = results.get("step0", {}).get("metrics", {})
    s1 = results.get("step1", {}).get("metrics", {})
    s2 = results.get("step2", {}).get("metrics", {})
    s3 = results.get("step3", {}).get("metrics", {})
    s4 = results.get("step4", {}).get("metrics", {})
    s5 = results.get("step5", {}).get("metrics", {})
    s6 = results.get("step6", {}).get("metrics", {})
    s7 = results.get("step7", {}).get("metrics", {})
    s8 = results.get("step8", {}).get("metrics", {})

    # Format prices from Step 2
    rep = s2.get("representative_items", {})
    rep_lines = []
    for k, v in rep.items():
        rep_lines.append(f"  - **{v.get('query', k)}**: 가격={v.get('prices', [])}, 오름차순=`{v.get('isAscending')}`, HTTP=`{v.get('apiStatus')}`, 소스=`{v.get('apiSource')}`")
    rep_detail = "\n".join(rep_lines) if rep_lines else "  - 데이터 없음"

    # PTR & Search bar metrics from Step 5
    s5_m = s5.get("mobile", {})
    s5_dock = s5_m.get("dock_and_25px_badges", {})
    s5_ptr = s5_m.get("ptr", {})
    s5_sb = s5_m.get("search_bar_smart_scroll", {})
    s5_lock = s5_m.get("dual_tab_scroll_lock", {})

    # UI metrics from Step 8
    s8_m = s8.get("metrics", {}) if "metrics" in s8 else s8
    s8_mob = s8_m.get("mobile_ui", {})
    s8_pc = s8_m.get("pc_ui", {})
    s8_live = s8_m.get("prod_live_crosscheck", {})

    # Artifacts matrix
    artifact_files = [
        "audit_01_mobile_splash_progress.png",
        "audit_01_desktop_instant_main.png",
        "audit_01_main_trending_view.png",
        "audit_02_dual_tabs_overview.png",
        "audit_02_mobile_magazine_cards.png",
        "audit_02_search_results_농심.png",
        "audit_02_search_results_CJ.png",
        "audit_02_search_results_커클랜드.png",
        "audit_02_search_results_사과.png",
        "audit_02_search_results_새우.png",
        "audit_03_ottogi_3tier_verified.png",
        "audit_04_rank1_verified.png",
        "audit_04_pc_anchor_desktop_verified.png",
        "audit_04_mobile_anchor_lis_verified.png",
        "audit_05_ptr_pulled_real_touch.png",
        "audit_05_search_bar_collapsed.png",
        "audit_05_search_bar_revealed.png",
        "audit_05_mobile_steady_scroll_lock.png",
        "audit_05_mobile_hotdeal_scroll_lock.png",
        "audit_05_tablet_dual_tab_scroll_lock.png",
        "audit_06_search_modal_clean_dismiss.png",
        "audit_06_mobile_compact_fit_modal.png",
        "audit_06_tablet_expanded_modal.png",
        "audit_07_responsive_matrix.png",
        "audit_07_pwa_install_elements.png",
        "audit_08_mobile_calibrated_header_10px.png",
        "audit_08_pc_header_high_contrast.png",
        "audit_08_mobile_footer_clearance.png"
    ]

    artifact_rows = []
    for fname in artifact_files:
        p = os.path.join(ARTIFACT_DIR, fname)
        if os.path.exists(p):
            sz = os.path.getsize(p)
            kb = round(sz / 1024, 1)
            artifact_rows.append(f"| `{fname}` | `file:///{p.replace(os.sep, '/')}` | **{kb} KB** (`{sz} B`) | ✅ 실측 생성 |")
        else:
            artifact_rows.append(f"| `{fname}` | - | 0 Byte | ⚠️ 미생성 |")
    artifacts_table = "\n".join(artifact_rows)

    report_md = f"""# 🛡️ PriceTrace 전 기능 전수검사 및 실측 증거 기반 무인 감사 보고서 (v2.0 완결판)

> **검사 일시**: `{now_str}`  
> **감사 아키텍처**: 초경량 8단계 마이크로 파이프라인 (Step 0 ~ Step 8 실제 DOM/CSS/네트워크 실측)  
> **총 검사 소요 시간**: **{total_elapsed}초**  
> **전역 런타임/네트워크/이미지 에러 합계**: **{total_sentinel_errors}건**  
> **종합 감사 판정**: **{overall_grade}**

---

## 1. Executive Summary (8대 단계별 실측 성적표)

| 단계 | 파이프라인 명칭 | 검사 대상 | 소요 시간 | 센티널 에러 | 실측 판정 |
| :---: | :--- | :--- | :---: | :---: | :---: |
{summary_rows}

---

## 2. Step-by-Step Quantitative Evidence (정량적 실측 수치 기록)

### [Step 0 & 1: 환경, 스플래시 (모바일·태블릿·PC) & 랭킹 API]
- **로컬 서버 (8080)**: HTTP `{s0.get('local_status')}` (`{s0.get('local_response_ms')}ms`) | v1.6.1 코드 동기화=`{s0.get('local_v161_synced')}`
- **프로덕션 Vercel**: HTTP `{s0.get('prod_status')}` (`{s0.get('prod_response_ms')}ms`) | v1.6.1 코드 동기화=`{s0.get('prod_v161_synced')}`
- **모바일 스플래시**: 캔버스=`{s1.get('mobile_splash', {}).get('canvas_rendered')}`, 펄스레이더=`{s1.get('mobile_splash', {}).get('has_pulse_radar')}`, Skip버튼=`{s1.get('mobile_splash', {}).get('skip_btn_visible')}`, sessionStorage=`{s1.get('mobile_splash', {}).get('session_flag_set')}`, 새로고침 즉시 진입=`{s1.get('mobile_splash', {}).get('reload_instant_bypass')}` (`{s1.get('mobile_splash', {}).get('reload_duration_ms')}ms`)
- **태블릿 스플래시**: 캔버스 렌더링=`{s1.get('tablet_splash', {}).get('canvasRendered')}`
- **PC 데스크톱 바이패스**: `display: "{s1.get('desktop_bypass', {}).get('splash_display')}"` (즉시 메인 노출=`{s1.get('desktop_bypass', {}).get('instant_main_verified')}`)
- **`/api/trending` API 정합성**: HTTP `{s1.get('trending_api', {}).get('http_status')}`, 소스=`{s1.get('trending_api', {}).get('source')}`, 생필품={s1.get('trending_api', {}).get('steady_items_count')}종, 핫딜={s1.get('trending_api', {}).get('trending_items_count')}종, Top4 카드 1:1 일치=`{s1.get('trending_api', {}).get('exact_card_match_4of4')}`, Top5 퀵칩 일치=`{s1.get('trending_api', {}).get('exact_chip_match_5of5')}`

### [Step 2 & 3: 32대 듀얼 탭, 5대 품목 정렬, 3단계 수집 & 오뚜기밥 24개]
- **듀얼 탭 카드 실측**: 생필품=`{s2.get('dual_tabs', {}).get('steady_count')}개` (유효 썸네일 `{s2.get('dual_tabs', {}).get('steady_valid_thumbs')}개`), 핫딜=`{s2.get('dual_tabs', {}).get('hotdeal_count')}개` (유효 썸네일 `{s2.get('dual_tabs', {}).get('hotdeal_valid_thumbs')}개`)
- **[오늘 세션 신규 실측] 모바일 매거진형 가로 카드 레이아웃 (v1.6.5)**:
  - 카드 수=`{s2.get('dual_tabs', {}).get('magazine_eval', {}).get('count')}개` | 가로형 비례=`{s2.get('dual_tabs', {}).get('magazine_eval', {}).get('isMagazine')}` | 1개 카드 규격=`{s2.get('dual_tabs', {}).get('magazine_eval', {}).get('cardWidth')}x{s2.get('dual_tabs', {}).get('magazine_eval', {}).get('cardHeight')}px` | 스크롤 압박 대폭 감소
- **5대 대표 품목 실측 가격 리스트**:
{rep_detail}
- **오뚜기밥 24개 단종 배제**: 카드 수=`{s3.get('cardCount')}개`, 단종 링크(`4915664157`) 포함=`{s3.get('hasDeadLink')}`, API 소스=`{s3.get('api_meta', {}).get('source')}`, 타겟 URL 실측 HTTP=`{s3.get('target_link_live_check', {}).get('http_status')}`, WAF 차단=`{s3.get('target_link_live_check', {}).get('waf_blocked')}`, 상품없음=`{s3.get('target_link_live_check', {}).get('missing_product')}`

### [Step 4: PC vs 모바일 네이버 가격비교 앵커 & 파워링크 우회 실측]
- **PC (`#shp_dui_root`)**: URL 매칭=`{s4.get('pc', {}).get('hasAnchor')}` (`where=shp`), 실제 네이버 이동 HTTP=`{s4.get('pc', {}).get('live_naver_check', {}).get('http_status')}`, `scrollY={s4.get('pc', {}).get('live_naver_check', {}).get('scrollY')}`, 앵커 발견=`{s4.get('pc', {}).get('live_naver_check', {}).get('anchor_found')}`, `rect.top={s4.get('pc', {}).get('live_naver_check', {}).get('anchor_top_px')}px`, 로그인리다이렉트=`{s4.get('pc', {}).get('live_naver_check', {}).get('login_redirected')}`
- **모바일 (`#shp_lis_root`)**: URL 매칭=`{s4.get('mobile', {}).get('hasAnchor')}`, 실제 모바일 네이버 이동 HTTP=`{s4.get('mobile', {}).get('live_naver_check', {}).get('http_status')}`, `scrollY={s4.get('mobile', {}).get('live_naver_check', {}).get('scrollY')}`, 앵커 발견=`{s4.get('mobile', {}).get('live_naver_check', {}).get('anchor_found')}`, `rect.top={s4.get('mobile', {}).get('live_naver_check', {}).get('anchor_top_px')}px`, 로그인리다이렉트=`{s4.get('mobile', {}).get('live_naver_check', {}).get('login_redirected')}`

### [Step 5: 어제·오늘 핵심 개선 전수 실측 (25px 뱃지 · Scroll Lock · PTR · 검색바 스마트 스크롤)]
- **하단 독 5대 탭 & 25px 축소 (v1.5.7)**: 베이스라인 편차=`{s5_dock.get('baselineDiff')}px`, 생필품 뱃지=`{s5_dock.get('steadyBadgeWidth')}x{s5_dock.get('steadyBadgeHeight')}px`, 핫딜 뱃지=`{s5_dock.get('hotdealBadgeWidth')}x{s5_dock.get('hotdealBadgeHeight')}px`, 독 상단 미돌출=`{s5_dock.get('noProtrusion')}`
- **듀얼 탭 고정 스크롤 (Scroll Lock)**: 모바일 생필품 Y오차=`{s5_lock.get('steady_diff_px')}px`, 핫딜 Y오차=`{s5_lock.get('hotdeal_diff_px')}px`, 트레이~헤더 간격=`{s5_lock.get('tray_header_clearance_px')}px`, 태블릿 Y오차=`{s5.get('tablet', {}).get('hotdeal_scroll_diff_px')}px`
- **Pull-to-Refresh 실측 (v1.5.8 & v1.5.9)**:
  - 기본 로드 시 인디케이터 상태: `display="{s5_ptr.get('default_hidden', {}).get('ptrDisplay')}"`, `height={s5_ptr.get('default_hidden', {}).get('ptrHeight')}px`, 헤더~본문 간격=`{s5_ptr.get('default_hidden', {}).get('headerToMainGapPx')}px`
  - 실제 TouchEvent 당김 중: 헤더 상단고정=`{s5_ptr.get('during_real_touch_pull', {}).get('headerTopFixed')}`, 본문 transform=`{s5_ptr.get('during_real_touch_pull', {}).get('mainTransform')}`, PTR 노출=`{s5_ptr.get('during_real_touch_pull', {}).get('ptrActiveClass')}`
  - 릴리즈 후 복원: `display="{s5_ptr.get('after_release', {}).get('ptrDisplayAfterRelease')}"`, `transform="{s5_ptr.get('after_release', {}).get('mainTransformAfterRelease')}"`
- **모바일 검색바 스마트 스크롤 & 3중 떨림 방어막 (v1.6.0 & v1.6.1)**:
  - 최상단 기본: 헤더 `{s5_sb.get('top', {}).get('headerHeight')}px` / 검색바 `{s5_sb.get('top', {}).get('searchHeight')}px`
  - 다운스크롤 은닉: 헤더 `{s5_sb.get('down_collapsed', {}).get('headerHeight')}px` (**-{s5_sb.get('height_saved_px')}px 절감**) / 검색바 `{s5_sb.get('down_collapsed', {}).get('searchHeight')}px` / 하단 독 숨김=`{s5_sb.get('down_collapsed', {}).get('navHidden')}`
  - 업스크롤 복귀: 헤더 `{s5_sb.get('up_revealed', {}).get('headerHeight')}px` / 검색바 `{s5_sb.get('up_revealed', {}).get('searchHeight')}px` / 하단 독 복귀=`{not s5_sb.get('up_revealed', {}).get('navHidden', True)}`
  - 5회 진동 스트레스 토글 횟수: `{s5_sb.get('stress_test_5x_toggle_count')}회` (무한 루프 억제) | 인풋 포커스 가드 중 접힘=`{s5_sb.get('focus_guard', {}).get('collapsedDuringFocus')}`

### [Step 6, 7 & 8: 레이더 모달, 5대 반응형, PWA, UI 실측 & Vercel 프로덕션 교차 검증]
- **레이더 모달 & iOS 줌 차단**: 오토포커스=`{s6.get('focus_metrics', {}).get('activeIsInput')}`, `fontSize="{s6.get('focus_metrics', {}).get('inputFontSize')}"`, `maximum-scale=1`=`{s6.get('focus_metrics', {}).get('hasMaxScaleOne')}`, 모달 즉시 은닉=`{s6.get('modal_hide_instant')}`, 임의검색(다이슨 `{s6.get('dyson_cards')}개` / 맥북 `{s6.get('macbook_cards')}개`)
- **[오늘 세션 신규 실측 #1] 모바일 레이더 모달 컴팩트 저스트 핏 (v1.6.7)**:
  - 모달 높이=`{s6.get('focus_metrics', {}).get('drawerHeight')}px` (화면 대비 `{s6.get('focus_metrics', {}).get('heightRatio')}`) | 하단 잔여 여백=`{s6.get('focus_metrics', {}).get('bottomPaddingDistance')}px` | 과도한 공백 배제=`{not s6.get('focus_metrics', {}).get('hasExcessiveWhitespace', True)}` | 무스크롤=`{s6.get('focus_metrics', {}).get('isZeroScroll')}`
- **[오늘 세션 신규 실측 #2] 태블릿 화면 레이더 모달 680px 확장 & 대형 터치 타겟 (v1.6.8)**:
  - 모달 가로폭=`{s6.get('tablet_eval', {}).get('drawerWidth')}px` (화면 대비 `{s6.get('tablet_eval', {}).get('widthRatio')}`) | 모달 높이=`{s6.get('tablet_eval', {}).get('drawerHeight')}px`
  - 검색창 인풋 높이=`{s6.get('tablet_eval', {}).get('inputHeight')}px` | 수량자판 칩=`{s6.get('tablet_eval', {}).get('padButtonWidth')}x{s6.get('tablet_eval', {}).get('padButtonHeight')}px`
  - 추천카드 높이=`{s6.get('tablet_eval', {}).get('quickChipHeight')}px` | 카테고리 칩 높이=`{s6.get('tablet_eval', {}).get('catChipHeight')}px` | 무스크롤=`{s6.get('tablet_eval', {}).get('isZeroScroll')}`
- **5대 디바이스 반응형 & PC 검색 가드**: `{s7.get('responsive_matrix')}`, PC 데스크톱 스크롤 시 검색바 상시 노출=`{s7.get('desktop_search_guard', {}).get('alwaysVisible')}`
- **PWA 에셋 상태**: `{s7.get('pwa_assets')}`
- **UI 실측 (Step 8)**:
  - `#gnbNavBar` `backdropFilter="{s8_mob.get('header', {}).get('gnbBackdropFilter')}"`
  - `#topLiveBanner`: `filter="{s8_mob.get('header', {}).get('bannerFilter')}"`, `opacity="{s8_mob.get('header', {}).get('bannerOpacity')}"`, `paddingTop="{s8_mob.get('header', {}).get('bannerPaddingTop')}"`
  - 동적 실측 명도대비(WCAG): 모바일 새로고침=`{s8_mob.get('mobile_contrast')}:1` (스핀=`{s8_mob.get('spin_connected')}`), PC 새로고침=`{s8_pc.get('pc_contrast')}:1`
  - 모바일 푸터 클리어런스: 좌측정렬=`{s8_mob.get('footer_clearance', {}).get('textLeftAligned')}`, 배지 `{s8_mob.get('footer_clearance', {}).get('badgeCount')}개`, `paddingBottom="{s8_mob.get('footer_clearance', {}).get('footerPaddingBottom')}"`, 독 노출상태=`{s8_mob.get('footer_clearance', {}).get('navVisible')}`, 독 이격=`{s8_mob.get('footer_clearance', {}).get('clearancePx')}px`, 겹침=`{s8_mob.get('footer_clearance', {}).get('hasOverlap')}`
  - **Step 8 실측 미달/결함 사항**: `{results.get('step8', {}).get('fail_reasons', [])}`
- **Vercel 프로덕션 교차 검증 (`{s8_live.get('url')}`)**: 다운 은닉=`{s8_live.get('down_collapsed')}` | 업 복귀=`{s8_live.get('up_revealed')}` | 최종 일치=`{s8_live.get('live_v161_verified')}`

---

## 3. Artifact Verification Matrix (전수 증거 스크린샷 매트릭스)

| 증거 스크린샷 파일명 | 로컬 절대 경로 링크 | 파일 용량 | 생성 상태 |
| :--- | :--- | :---: | :---: |
{artifacts_table}

---
*보고서 생성 완료: {now_str} | PriceTrace Micro Audit Engine v2.0 (100% Real DOM/Network Verified)*
"""

    report_path1 = os.path.join(ARTIFACT_DIR, "FULL_INSPECTION_AUDIT_REPORT.md")
    report_path2 = os.path.join(DOCS_REPORT_DIR, "FULL_INSPECTION_AUDIT_REPORT.md")
    with open(report_path1, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(report_path2, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Report written to:\n 1. {report_path1}\n 2. {report_path2}", flush=True)


if __name__ == "__main__":
    main()
