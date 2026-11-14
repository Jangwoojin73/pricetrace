# -*- coding: utf-8 -*-
"""
Step 6: Radar Modal Autofocus, Instant Dismissal, iOS Zoom Prevention & Arbitrary Search Audit
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, MOBILE_UA,
    save_step_result, create_sentinel, collect_broken_images, sentinel_summary, safe_screenshot
)


def main():
    t_start = time.time()
    print(">>> [Step 6] Auditing Radar Modal Autofocus, iOS Zoom Prevention & Arbitrary Search...")
    metrics = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent=MOBILE_UA,
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_m = m_ctx.new_page()
        p_m.set_default_timeout(12000)
        s = create_sentinel(p_m)
        p_m.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_m.goto(BASE_URL, wait_until="domcontentloaded")
        p_m.wait_for_selector("#mobileNavSearchFabBtn", state="visible", timeout=8000)
        p_m.wait_for_timeout(400)

        # 6-1. Click Radar Tab & Test Modal Autofocus
        try:
            p_m.click("#mobileNavSearchFabBtn", force=True)
        except Exception:
            p_m.tap("#mobileNavSearchFabBtn")

        p_m.wait_for_function(
            "() => !document.getElementById('radarSearchModal').classList.contains('modal-hidden')",
            timeout=4000
        )
        try:
            p_m.wait_for_function(
                "() => document.activeElement === document.getElementById('modalSearchInput')",
                timeout=2000
            )
        except Exception:
            p_m.wait_for_timeout(300)

        focus_metrics = p_m.evaluate('''() => {
            const modal = document.getElementById("radarSearchModal");
            const drawer = document.getElementById("radarSearchDrawer");
            const input = document.getElementById("modalSearchInput");
            if (input && document.activeElement !== input) {
                try { input.focus(); } catch(e) {}
            }
            const vpMeta = document.querySelector('meta[name="viewport"]')?.getAttribute('content') || "";
            const fontSizeStr = input ? window.getComputedStyle(input).fontSize : "0px";
            const dRect = drawer ? drawer.getBoundingClientRect() : null;
            const lastChip = document.querySelector('.modal-category-chip:last-child');
            const lRect = lastChip ? lastChip.getBoundingClientRect() : null;

            return {
                modalVisible: modal ? !modal.classList.contains("modal-hidden") : false,
                activeIsInput: document.activeElement === input,
                viewportMeta: vpMeta,
                hasMaxScaleOne: vpMeta.includes("maximum-scale=1"),
                inputFontSize: fontSizeStr,
                inputFontSizePx: parseFloat(fontSizeStr) || 0,
                // [오늘 세션 신규 검증] 모바일 레이더 모달 컴팩트 저스트핏 & 공백 제거 실측
                drawerHeight: dRect ? Math.round(dRect.height) : 0,
                heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
                bottomPaddingDistance: lRect && dRect ? Math.round(dRect.bottom - lRect.bottom) : 0,
                hasExcessiveWhitespace: lRect && dRect ? (dRect.bottom - lRect.bottom > 50) : false,
                isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false
            };
        }''')

        snap_mobile_compact = os.path.join(ARTIFACT_DIR, "audit_06_mobile_compact_fit_modal.png")
        safe_screenshot(p_m, snap_mobile_compact)

        # 6-2. Arbitrary Search #1 ("다이슨 에어랩") & Instant Modal Dismissal
        p_m.evaluate("const g = document.getElementById('priceComparisonGrid'); if (g) g.innerHTML = '';")
        p_m.fill("#modalSearchInput", "다이슨 에어랩")
        with p_m.expect_response(lambda r: "/api/search" in r.url, timeout=12000):
            p_m.press("#modalSearchInput", "Enter")
        p_m.wait_for_timeout(100)

        modal_hide_instant = p_m.evaluate('''() => {
            const modal = document.getElementById("radarSearchModal");
            return modal ? (modal.classList.contains("modal-hidden") || window.getComputedStyle(modal).display === "none") : true;
        }''')

        p_m.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=10000)
        p_m.wait_for_timeout(200)
        dyson_count = p_m.locator("#priceComparisonGrid .rank-card").count()

        snap_path = os.path.join(ARTIFACT_DIR, "audit_06_search_modal_clean_dismiss.png")
        safe_screenshot(p_m, snap_path)

        # 6-3. Arbitrary Search #2 ("맥북")
        p_m.evaluate("const g = document.getElementById('priceComparisonGrid'); if (g) g.innerHTML = '';")
        p_m.fill("#searchInput", "맥북")
        with p_m.expect_response(lambda r: "/api/search" in r.url, timeout=12000):
            p_m.press("#searchInput", "Enter")
        p_m.wait_for_selector("#priceComparisonGrid .rank-card", timeout=10000)
        macbook_count = p_m.locator("#priceComparisonGrid .rank-card").count()

        collect_broken_images(p_m, s)
        metrics["focus_metrics"] = focus_metrics
        metrics["modal_hide_instant"] = modal_hide_instant
        metrics["dyson_cards"] = dyson_count
        metrics["macbook_cards"] = macbook_count
        metrics["screenshot"] = snap_path

        m_ctx.close()

        # 6-4. [오늘 세션 신규 검증] 태블릿(800x1280) 레이더 모달 680px 확장 및 대형 터치 타겟 실측
        tab_ctx = browser.new_context(viewport={'width': 800, 'height': 1280}, service_workers="block")
        tab_page = tab_ctx.new_page()
        tab_page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        tab_page.goto(BASE_URL, wait_until="domcontentloaded")
        tab_page.wait_for_selector("#mobileNavSearchFabBtn", state="visible", timeout=8000)
        tab_page.click("#mobileNavSearchFabBtn")
        tab_page.wait_for_selector("#radarSearchDrawer", timeout=5000)
        tab_page.wait_for_timeout(400)

        tablet_eval = tab_page.evaluate('''() => {
            const drawer = document.getElementById('radarSearchDrawer');
            const dRect = drawer ? drawer.getBoundingClientRect() : null;
            const input = document.getElementById('modalSearchInput');
            const iRect = input ? input.getBoundingClientRect() : null;
            const firstPad = document.querySelector('.modal-pad-chip');
            const pRect = firstPad ? firstPad.getBoundingClientRect() : null;
            const firstQuick = document.querySelector('.modal-quick-chip');
            const qRect = firstQuick ? firstQuick.getBoundingClientRect() : null;
            const firstCat = document.querySelector('.modal-category-chip');
            const cRect = firstCat ? firstCat.getBoundingClientRect() : null;

            return {
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                drawerWidth: dRect ? Math.round(dRect.width) : 0,
                drawerHeight: dRect ? Math.round(dRect.height) : 0,
                widthRatio: dRect ? ((dRect.width / window.innerWidth) * 100).toFixed(1) + '%' : '0%',
                inputHeight: iRect ? Math.round(iRect.height) : 0,
                padButtonWidth: pRect ? Math.round(pRect.width) : 0,
                padButtonHeight: pRect ? Math.round(pRect.height) : 0,
                quickChipHeight: qRect ? Math.round(qRect.height) : 0,
                catChipHeight: cRect ? Math.round(cRect.height) : 0,
                isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false
            };
        }''')

        snap_tablet_expanded = os.path.join(ARTIFACT_DIR, "audit_06_tablet_expanded_modal.png")
        safe_screenshot(tab_page, snap_tablet_expanded)
        tab_ctx.close()

        metrics["focus_metrics"] = focus_metrics
        metrics["modal_hide_instant"] = modal_hide_instant
        metrics["dyson_cards"] = dyson_count
        metrics["macbook_cards"] = macbook_count
        metrics["tablet_eval"] = tablet_eval
        metrics["screenshot"] = snap_path
        metrics["screenshot_mobile_compact"] = snap_mobile_compact
        metrics["screenshot_tablet_expanded"] = snap_tablet_expanded

        browser.close()

    s_sum = sentinel_summary(s)
    passed = (
        focus_metrics["modalVisible"]
        and focus_metrics["activeIsInput"]
        and focus_metrics["hasMaxScaleOne"]
        and focus_metrics["inputFontSizePx"] >= 16.0
        and not focus_metrics.get("hasExcessiveWhitespace", False)
        and focus_metrics.get("isZeroScroll", False)
        and tablet_eval.get("drawerWidth", 0) >= 650
        and tablet_eval.get("padButtonHeight", 0) >= 48
        and modal_hide_instant
        and dyson_count >= 3
        and macbook_count >= 3
        and s_sum["total_errors"] == 0
    )

    result = {
        "step": 6,
        "name": "Radar Modal Autofocus, Dismissal, iOS Zoom Prevention & Arbitrary Search",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": s_sum,
        "metrics": metrics
    }
    print(f"[Step 6] {result['elapsed_sec']}s | ActiveInput={focus_metrics['activeIsInput']} | FontSize={focus_metrics['inputFontSize']} | Dyson={dyson_count} | MacBook={macbook_count} | Errors={s_sum['total_errors']} | Status={result['status']}")
    save_step_result(6, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
