# -*- coding: utf-8 -*-
import os, sys, time, json
from playwright.sync_api import sync_playwright

VERCEL_URL = "https://pricetrace-nu.vercel.app"
ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

def run_vercel_live_scroll_and_gap_verification():
    ts = time.strftime("%H%M%S")
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] Starting Vercel Live Scroll & Gap Verification...")

    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. MOBILE VERIFICATION (393x852)
        print("\n[Vercel Live: Mobile 393x852]")
        ctx_mob = browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            has_touch=True,
            is_mobile=True
        )
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        target_url = f"{VERCEL_URL}/?cb={time.time()}"
        print(f"Navigating to Vercel live: {target_url}")
        page_mob.goto(target_url, wait_until="load", timeout=25000)
        page_mob.wait_for_selector("#searchInput", timeout=15000)
        time.sleep(1)

        # Step 1: Scroll down 500px on Welcome View
        print("Simulating user scrolling down 500px on Welcome View...")
        page_mob.evaluate("window.scrollTo(0, 500);")
        time.sleep(0.5)
        before_scroll = page_mob.evaluate("window.scrollY")
        print(f"ScrollY before search: {before_scroll}px")

        # Step 2: Search from scrolled state
        print("Executing search for CJ 햇반 on Vercel Live...")
        page_mob.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_mob.press("#searchInput", "Enter")

        page_mob.wait_for_selector("#priceComparisonGrid .rank-card", timeout=20000)
        page_mob.wait_for_selector("#lowestPriceDisplay", timeout=15000)
        time.sleep(2)

        # Step 3: Measure scroll position and gap
        mob_metrics = page_mob.evaluate("""() => {
            const scrollY = window.scrollY;
            const header = document.querySelector('header');
            const headerRect = header ? header.getBoundingClientRect() : null;
            
            const backBtn = document.getElementById('backToHomeBtn');
            const backRect = backBtn ? backBtn.getBoundingClientRect() : null;

            const alertBanner = document.getElementById('alertBanner');
            const alertRect = alertBanner ? alertBanner.getBoundingClientRect() : null;

            const gapHeaderToBackBtn = (headerRect && backRect) ? Math.round((backRect.top - headerRect.bottom) * 10) / 10 : null;
            const gapBackBtnToAlert = (backRect && alertRect) ? Math.round((alertRect.top - backRect.bottom) * 10) / 10 : null;

            return {
                timestamp: new Date().toLocaleTimeString(),
                scrollY: scrollY,
                headerBottom: headerRect ? Math.round(headerRect.bottom * 10) / 10 : null,
                backBtnTop: backRect ? Math.round(backRect.top * 10) / 10 : null,
                gapHeaderToBackBtn: gapHeaderToBackBtn,
                alertBannerTop: alertRect ? Math.round(alertRect.top * 10) / 10 : null,
                gapBackBtnToAlert: gapBackBtnToAlert
            };
        }""")

        print("Vercel Live Mobile Metrics:", json.dumps(mob_metrics, indent=2, ensure_ascii=False))

        # Screenshots
        path_mob_top = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_mobile_top_start_{ts}.png")
        page_mob.screenshot(path=path_mob_top, full_page=False)
        print(f"Captured: {path_mob_top}")

        path_gap_shot = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_compact_gap_{ts}.png")
        page_mob.locator("#resultView").screenshot(path=path_gap_shot)
        print(f"Captured: {path_gap_shot}")

        ctx_mob.close()

        # 2. TABLET VERIFICATION (800x1280)
        print("\n[Vercel Live: Tablet 800x1280]")
        ctx_tab = browser.new_context(
            viewport={"width": 800, "height": 1280},
            device_scale_factor=2,
            has_touch=True,
            is_mobile=False
        )
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        page_tab.goto(target_url, wait_until="load", timeout=25000)
        page_tab.wait_for_selector("#searchInput", timeout=15000)
        time.sleep(1)

        page_tab.evaluate("window.scrollTo(0, 500);")
        time.sleep(0.5)

        page_tab.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_tab.press("#searchInput", "Enter")

        page_tab.wait_for_selector("#priceComparisonGrid .rank-card", timeout=20000)
        page_tab.wait_for_selector("#lowestPriceDisplay", timeout=15000)
        time.sleep(2)

        tab_metrics = page_tab.evaluate("""() => {
            const scrollY = window.scrollY;
            const header = document.querySelector('header');
            const headerRect = header ? header.getBoundingClientRect() : null;
            const backBtn = document.getElementById('backToHomeBtn');
            const backRect = backBtn ? backBtn.getBoundingClientRect() : null;
            const alertBanner = document.getElementById('alertBanner');
            const alertRect = alertBanner ? alertBanner.getBoundingClientRect() : null;

            return {
                timestamp: new Date().toLocaleTimeString(),
                scrollY: scrollY,
                gapHeaderToBackBtn: (headerRect && backRect) ? Math.round((backRect.top - headerRect.bottom) * 10) / 10 : null,
                alertBannerTop: alertRect ? Math.round(alertRect.top * 10) / 10 : null
            };
        }""")

        print("Vercel Live Tablet Metrics:", json.dumps(tab_metrics, indent=2, ensure_ascii=False))

        path_tab_top = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_tablet_top_start_{ts}.png")
        page_tab.screenshot(path=path_tab_top, full_page=False)
        print(f"Captured: {path_tab_top}")

        ctx_tab.close()
        browser.close()

    results = {
        "mobile": mob_metrics,
        "tablet": tab_metrics,
        "verified_at": now_str,
        "commit": "15177dc"
    }
    metrics_path = os.path.join(ARTIFACT_DIR, f"metrics_vercel_live_scroll_and_gap_{ts}.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nVercel Live Verification Finished! Metrics saved to: {metrics_path}")

if __name__ == "__main__":
    run_vercel_live_scroll_and_gap_verification()
