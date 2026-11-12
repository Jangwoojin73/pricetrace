# -*- coding: utf-8 -*-
"""
Step 1: Splash Progression (Mobile & Tablet), Desktop Bypass, and Trending API Consistency Audit
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, MOBILE_UA, PC_UA,
    save_step_result, create_sentinel, collect_broken_images, sentinel_summary, safe_screenshot
)


def main():
    t_start = time.time()
    print(">>> [Step 1] Running Splash (Mobile/Tablet), Desktop Bypass & Trending API Audit...")
    metrics = {}
    sentinel_merged = {"console_errors": [], "page_errors": [], "http_errors": [], "failed_requests": [], "broken_images_count": 0, "broken_image_srcs": []}

    def merge_sentinel(s):
        for k in ["console_errors", "page_errors", "http_errors", "failed_requests", "broken_image_srcs"]:
            sentinel_merged[k].extend(s[k])
        sentinel_merged["broken_images_count"] += s["broken_images_count"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # -----------------------------------------------------------------
        # 1-1. Mobile Splash Verification (iPhone 15 Pro, 393x852)
        # -----------------------------------------------------------------
        ctx_m = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent=MOBILE_UA,
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        page_m = ctx_m.new_page()
        page_m.set_default_timeout(6000)
        s_m = create_sentinel(page_m)

        page_m.goto(BASE_URL, wait_until="domcontentloaded")
        page_m.wait_for_timeout(350)

        m_splash = page_m.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            const canvas = document.getElementById("splashCanvas");
            const progressBar = document.getElementById("splashProgressBar");
            const progressText = document.getElementById("splashProgressText");
            const skipBtn = document.getElementById("splashSkipBtn");
            const radar = splash ? splash.querySelector(".animate-ping") : null;
            return {
                splashExists: !!splash,
                splashDisplay: splash ? window.getComputedStyle(splash).display : "none",
                canvasRendered: !!canvas && canvas.width > 0 && canvas.height > 0,
                hasPulseRadar: !!radar,
                progressText: progressText ? progressText.innerText : "",
                progressBarWidth: progressBar ? progressBar.style.width : "",
                skipBtnVisible: !!skipBtn && window.getComputedStyle(skipBtn).display !== "none"
            };
        }''')

        snap1_path = os.path.join(ARTIFACT_DIR, "audit_01_mobile_splash_progress.png")
        safe_screenshot(page_m, snap1_path)

        # Click skip and verify sessionStorage
        try:
            page_m.click("#splashSkipBtn", timeout=2000)
        except Exception:
            page_m.evaluate("const btn = document.getElementById('splashSkipBtn'); if(btn) btn.click();")
        page_m.wait_for_timeout(350)

        after_skip = page_m.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            return {
                sessionFlag: sessionStorage.getItem("pricetrace_splash_seen"),
                splashDisplayAfterSkip: splash ? window.getComputedStyle(splash).display : "none"
            };
        }''')

        t0_reload = time.time()
        page_m.reload(wait_until="domcontentloaded")
        page_m.wait_for_timeout(200)
        reload_duration = round((time.time() - t0_reload) * 1000, 1)

        reload_instant = page_m.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            return {
                instantMain: splash ? window.getComputedStyle(splash).display === "none" : true
            };
        }''')

        collect_broken_images(page_m, s_m)
        merge_sentinel(s_m)

        metrics["mobile_splash"] = {
            "splash_display": m_splash["splashDisplay"],
            "canvas_rendered": m_splash["canvasRendered"],
            "has_pulse_radar": m_splash["hasPulseRadar"],
            "progress_text": m_splash["progressText"],
            "progress_bar_width": m_splash["progressBarWidth"],
            "skip_btn_visible": m_splash["skipBtnVisible"],
            "session_flag_set": after_skip["sessionFlag"] == "true",
            "reload_instant_bypass": reload_instant["instantMain"],
            "reload_duration_ms": reload_duration,
            "screenshot": snap1_path
        }
        ctx_m.close()

        # -----------------------------------------------------------------
        # 1-2. Tablet Splash Verification (iPad Pro 11, 834x1194)
        # -----------------------------------------------------------------
        ctx_t = browser.new_context(
            viewport={'width': 834, 'height': 1194},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        page_t = ctx_t.new_page()
        page_t.set_default_timeout(6000)
        s_t = create_sentinel(page_t)

        page_t.goto(BASE_URL, wait_until="domcontentloaded")
        page_t.wait_for_timeout(350)

        t_splash = page_t.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            const canvas = document.getElementById("splashCanvas");
            return {
                splashVisible: splash ? window.getComputedStyle(splash).display !== "none" : false,
                canvasRendered: !!canvas && canvas.width > 0
            };
        }''')
        merge_sentinel(s_t)
        metrics["tablet_splash"] = t_splash
        ctx_t.close()

        # -----------------------------------------------------------------
        # 1-3. PC Desktop (1440x900) - Instant Bypass (0s splash)
        # -----------------------------------------------------------------
        ctx_pc = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent=PC_UA,
            service_workers="block"
        )
        page_pc = ctx_pc.new_page()
        page_pc.set_default_timeout(8000)
        s_pc = create_sentinel(page_pc)

        page_pc.goto(BASE_URL, wait_until="domcontentloaded")
        page_pc.wait_for_timeout(300)

        pc_splash = page_pc.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            return {
                display: splash ? window.getComputedStyle(splash).display : "none",
                isNone: splash ? window.getComputedStyle(splash).display === "none" : true
            };
        }''')

        snap2_path = os.path.join(ARTIFACT_DIR, "audit_01_desktop_instant_main.png")
        safe_screenshot(page_pc, snap2_path)

        metrics["desktop_bypass"] = {
            "splash_display": pc_splash["display"],
            "instant_main_verified": pc_splash["isNone"],
            "screenshot": snap2_path
        }

        # -----------------------------------------------------------------
        # 1-4. Real-Time Naver Trending API Consistency Check
        # -----------------------------------------------------------------
        page_pc.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=8000)
        page_pc.wait_for_timeout(800)  # /api/trending 비동기 로드 완료 대기

        api_match = page_pc.evaluate('''async () => {
            const res = await fetch("/api/trending");
            const data = await res.json();
            const apiSteady = (data.steady_items || data.items || []);
            const apiTop4Titles = apiSteady.slice(0, 4).map(i => (i.title || i.keyword || "").trim());
            const apiTop5Keywords = apiSteady.slice(0, 5).map(i => (i.keyword || "").trim());

            const uiTop4Cards = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card h3"))
                .slice(0, 4)
                .map(e => e.innerText.trim());
            const uiQuickChips = Array.from(document.querySelectorAll("#quickChipsContainer .quick-chip"))
                .map(e => e.getAttribute("data-keyword") || e.innerText.trim());

            // 1:1 비교 (API Top 4 vs UI Card Top 4)
            let exactCardMatchCount = 0;
            for (let i = 0; i < Math.min(4, apiTop4Titles.length, uiTop4Cards.length); i++) {
                if (apiTop4Titles[i] === uiTop4Cards[i]) exactCardMatchCount++;
            }

            let exactChipMatchCount = 0;
            for (let i = 0; i < Math.min(5, apiTop5Keywords.length, uiQuickChips.length); i++) {
                if (apiTop5Keywords[i] === uiQuickChips[i]) exactChipMatchCount++;
            }

            return {
                status: res.status,
                success: !!data.success,
                source: data.source || "unknown",
                apiCount: apiSteady.length,
                trendingCount: (data.trending_items || []).length,
                apiTop4: apiTop4Titles,
                uiTop4Cards: uiTop4Cards,
                exactCardMatchCount: exactCardMatchCount,
                uiQuickChips: uiQuickChips,
                exactChipMatchCount: exactChipMatchCount
            };
        }''')

        collect_broken_images(page_pc, s_pc)
        merge_sentinel(s_pc)

        snap3_path = os.path.join(ARTIFACT_DIR, "audit_01_main_trending_view.png")
        safe_screenshot(page_pc, snap3_path)

        metrics["trending_api"] = {
            "http_status": api_match["status"],
            "source": api_match["source"],
            "steady_items_count": api_match["apiCount"],
            "trending_items_count": api_match["trendingCount"],
            "api_top4": api_match["apiTop4"],
            "ui_top4_cards": api_match["uiTop4Cards"],
            "exact_card_match_4of4": api_match["exactCardMatchCount"] == 4,
            "ui_quick_chips_count": len(api_match["uiQuickChips"]),
            "exact_chip_match_5of5": api_match["exactChipMatchCount"] == 5,
            "screenshot": snap3_path
        }

        ctx_pc.close()
        browser.close()

    s_sum = sentinel_summary(sentinel_merged)
    passed = (
        metrics["mobile_splash"]["canvas_rendered"]
        and metrics["mobile_splash"]["has_pulse_radar"]
        and metrics["mobile_splash"]["skip_btn_visible"]
        and metrics["mobile_splash"]["session_flag_set"]
        and metrics["mobile_splash"]["reload_instant_bypass"]
        and metrics["tablet_splash"]["splashVisible"]
        and metrics["desktop_bypass"]["instant_main_verified"]
        and metrics["trending_api"]["http_status"] == 200
        and metrics["trending_api"]["exact_card_match_4of4"]
        and metrics["trending_api"]["exact_chip_match_5of5"]
        and s_sum["total_errors"] == 0
    )

    result = {
        "step": 1,
        "name": "Splash Progression (Mobile/Tablet), Desktop Bypass & Trending API Consistency",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": s_sum,
        "metrics": metrics
    }
    print(f"[Step 1] {result['elapsed_sec']}s | CardMatch={metrics['trending_api']['exact_card_match_4of4']} | TabletSplash={metrics['tablet_splash']['splashVisible']} | Errors={s_sum['total_errors']} | Status={result['status']}")
    save_step_result(1, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
