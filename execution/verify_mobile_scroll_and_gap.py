# -*- coding: utf-8 -*-
import os, sys, time, json, urllib.request, subprocess
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

os.environ['NO_PROXY'] = '127.0.0.1,localhost'
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def is_server_up():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/status", headers={"User-Agent": "Mozilla/5.0"})
        with opener.open(req, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False

try:
    if not is_server_up():
        print("Launching local server on port 8080...")
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(20):
            time.sleep(0.3)
            if is_server_up():
                print("Server successfully launched!")
                break

    print("Server ready. Starting Playwright verification for top start position & gap...")
    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    ts = time.strftime("%H%M%S")
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. MOBILE VERIFICATION (393x852)
        print("\n[Mobile 393x852 Testing]")
        ctx_mob = browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            has_touch=True,
            is_mobile=True
        )
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        target_url = f"{BASE_URL}/?cb={time.time()}"
        print(f"Navigating to mobile local target: {target_url}")
        page_mob.goto(target_url, wait_until="load", timeout=20000)
        page_mob.wait_for_selector("#searchInput", timeout=10000)
        time.sleep(1)

        # Step 1: Scroll down on welcome view (simulate user browsing downwards)
        print("Simulating user scrolling down 500px on Welcome View...")
        page_mob.evaluate("window.scrollTo(0, 500);")
        time.sleep(0.5)
        before_scroll = page_mob.evaluate("window.scrollY")
        print(f"ScrollY before search: {before_scroll}px")

        # Step 2: Search from scrolled state
        print("Executing search for CJ 햇반...")
        page_mob.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_mob.press("#searchInput", "Enter")

        page_mob.wait_for_selector("#priceComparisonGrid .rank-card", timeout=15000)
        page_mob.wait_for_selector("#lowestPriceDisplay", timeout=10000)
        time.sleep(1.5)

        # Step 3: Measure scroll position and gap
        mob_metrics = page_mob.evaluate("""() => {
            const scrollY = window.scrollY;
            const header = document.querySelector('header');
            const headerRect = header ? header.getBoundingClientRect() : null;
            
            const backBtn = document.getElementById('backToHomeBtn');
            const backRect = backBtn ? backBtn.getBoundingClientRect() : null;

            const alertBanner = document.getElementById('alertBanner');
            const alertRect = alertBanner ? alertBanner.getBoundingClientRect() : null;

            const priceBox = document.getElementById('lowestPriceDisplay') ? 
                document.getElementById('lowestPriceDisplay').closest('.bg-gradient-to-br') : null;
            const priceBoxRect = priceBox ? priceBox.getBoundingClientRect() : null;

            // Gap between header bottom and backToHomeBtn top
            const gapHeaderToBackBtn = (headerRect && backRect) ? Math.round((backRect.top - headerRect.bottom) * 10) / 10 : null;
            // Gap between backToHomeBtn bottom and alertBanner top
            const gapBackBtnToAlert = (backRect && alertRect) ? Math.round((alertRect.top - backRect.bottom) * 10) / 10 : null;

            return {
                timestamp: new Date().toLocaleTimeString(),
                scrollY: scrollY,
                headerBottom: headerRect ? Math.round(headerRect.bottom * 10) / 10 : null,
                backBtnTop: backRect ? Math.round(backRect.top * 10) / 10 : null,
                gapHeaderToBackBtn: gapHeaderToBackBtn,
                alertBannerTop: alertRect ? Math.round(alertRect.top * 10) / 10 : null,
                gapBackBtnToAlert: gapBackBtnToAlert,
                priceBoxTop: priceBoxRect ? Math.round(priceBoxRect.top * 10) / 10 : null
            };
        }""")

        results['mobile'] = mob_metrics
        print("Mobile Metrics:", json.dumps(mob_metrics, indent=2, ensure_ascii=False))

        # Screenshots for Mobile
        # 1) Mobile First Frame Viewport (showing top start point: Alert Banner visible from the very top)
        path_mob_top = os.path.join(ARTIFACT_DIR, f"verify_mobile_top_start_alert_banner_{ts}.png")
        page_mob.screenshot(path=path_mob_top, full_page=False)
        print(f"Captured: {path_mob_top}")

        # 2) Close up of the Header to Back button & Alert Banner
        path_gap_shot = os.path.join(ARTIFACT_DIR, f"verify_compact_gap_back_to_home_{ts}.png")
        page_mob.locator("#resultView").screenshot(path=path_gap_shot)
        print(f"Captured: {path_gap_shot}")

        ctx_mob.close()

        # 2. TABLET VERIFICATION (800x1280)
        print("\n[Tablet 800x1280 Testing]")
        ctx_tab = browser.new_context(
            viewport={"width": 800, "height": 1280},
            device_scale_factor=2,
            has_touch=True,
            is_mobile=False
        )
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        page_tab.goto(target_url, wait_until="load", timeout=20000)
        page_tab.wait_for_selector("#searchInput", timeout=10000)
        time.sleep(1)

        page_tab.evaluate("window.scrollTo(0, 500);")
        time.sleep(0.5)

        page_tab.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_tab.press("#searchInput", "Enter")

        page_tab.wait_for_selector("#priceComparisonGrid .rank-card", timeout=15000)
        page_tab.wait_for_selector("#lowestPriceDisplay", timeout=10000)
        time.sleep(1.5)

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

        results['tablet'] = tab_metrics
        print("Tablet Metrics:", json.dumps(tab_metrics, indent=2, ensure_ascii=False))

        path_tab_top = os.path.join(ARTIFACT_DIR, f"verify_tablet_top_start_{ts}.png")
        page_tab.screenshot(path=path_tab_top, full_page=False)
        print(f"Captured: {path_tab_top}")

        ctx_tab.close()
        browser.close()

    metrics_path = os.path.join(ARTIFACT_DIR, f"metrics_mobile_scroll_and_gap_{ts}.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nAll validations completed! Metrics saved to: {metrics_path}")

finally:
    if server_proc:
        print("Terminating test server...")
        server_proc.terminate()
        server_proc.wait()
