# -*- coding: utf-8 -*-
import os, sys, time, json, urllib.request, subprocess
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

def is_server_up():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/status", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False

try:
    if not is_server_up():
        print("Launching local server on port 8080...")
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(15):
            time.sleep(0.4)
            if is_server_up():
                break

    print("Server is up. Starting Playwright verification...")
    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    ts = time.strftime("%H%M%S")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. MOBILE VERIFICATION (393x852)
        ctx_mob = browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            has_touch=True,
            is_mobile=True,
            service_workers="block"
        )
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        target_url = f"{BASE_URL}/?cb={time.time()}"
        print(f"Navigating to mobile local target: {target_url}")
        page_mob.goto(target_url, wait_until="networkidle", timeout=20000)
        time.sleep(1)

        # Search for CJ 제일제당 햇반 210g 24개
        print("Submitting search on mobile...")
        page_mob.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_mob.press("#searchInput", "Enter")

        # Wait for search results
        page_mob.wait_for_selector("#priceComparisonGrid .rank-card", timeout=15000)
        time.sleep(1.5)

        # Measure DOM
        mob_metrics = page_mob.evaluate("""() => {
            const alertBanner = document.getElementById('alertBanner');
            const alertRect = alertBanner ? alertBanner.getBoundingClientRect() : null;
            const alertCs = alertBanner ? window.getComputedStyle(alertBanner) : null;
            const alertIcon = document.getElementById('alertIconBox');
            const alertIconRect = alertIcon ? alertIcon.getBoundingClientRect() : null;

            // Hero section
            const heroSection = document.querySelector('#resultView section:nth-of-type(1)');
            const heroRect = heroSection ? heroSection.getBoundingClientRect() : null;
            const heroImg = document.getElementById('productMainImage');
            const heroImgRect = heroImg ? heroImg.getBoundingClientRect() : null;
            const heroImgContainer = heroImg ? heroImg.closest('.relative.w-full') : null;
            const heroImgContainerRect = heroImgContainer ? heroImgContainer.getBoundingClientRect() : null;
            const heroPriceBox = document.querySelector('#lowestPriceDisplay') ? document.querySelector('#lowestPriceDisplay').closest('.bg-gradient-to-br') : null;
            const heroPriceBoxRect = heroPriceBox ? heroPriceBox.getBoundingClientRect() : null;

            // Price comparison grid
            const grid = document.getElementById('priceComparisonGrid');
            const gridRect = grid ? grid.getBoundingClientRect() : null;
            const cards = grid ? Array.from(grid.querySelectorAll('.rank-card')) : [];
            const cardMetrics = cards.map((c, i) => {
                const r = c.getBoundingClientRect();
                const cs = window.getComputedStyle(c);
                return {
                    rank: i + 1,
                    width: Math.round(r.width),
                    height: Math.round(r.height),
                    padding: `${cs.paddingTop} ${cs.paddingRight} ${cs.paddingBottom} ${cs.paddingLeft}`
                };
            });

            return {
                device: "Mobile 393x852",
                documentScrollHeight: document.documentElement.scrollHeight,
                alertBanner: {
                    width: alertRect ? Math.round(alertRect.width) : 0,
                    height: alertRect ? Math.round(alertRect.height) : 0,
                    padding: alertCs ? `${alertCs.paddingTop} ${alertCs.paddingRight} ${alertCs.paddingBottom} ${alertCs.paddingLeft}` : '',
                    iconBox: alertIconRect ? { width: Math.round(alertIconRect.width), height: Math.round(alertIconRect.height) } : null
                },
                heroSection: {
                    width: heroRect ? Math.round(heroRect.width) : 0,
                    height: heroRect ? Math.round(heroRect.height) : 0,
                    imageContainerHeight: heroImgContainerRect ? Math.round(heroImgContainerRect.height) : 0,
                    priceBoxHeight: heroPriceBoxRect ? Math.round(heroPriceBoxRect.height) : 0
                },
                comparisonGrid: {
                    width: gridRect ? Math.round(gridRect.width) : 0,
                    height: gridRect ? Math.round(gridRect.height) : 0,
                    cards: cardMetrics
                }
            };
        }""")

        print(f"[MOB_COMPACT_METRICS]{json.dumps(mob_metrics, indent=2)}[/MOB_COMPACT_METRICS]")

        # 1. Alert Banner screenshot
        snap_alert = os.path.join(ARTIFACT_DIR, f"verify_mobile_search_detail_alert_banner_{ts}.png")
        page_mob.evaluate("document.getElementById('alertBanner').scrollIntoView({ behavior: 'instant', block: 'center' })")
        time.sleep(0.4)
        page_mob.screenshot(path=snap_alert, full_page=False)
        print(f"[✓] Alert banner screenshot: {snap_alert}")

        # 2. Hero Card screenshot
        snap_hero = os.path.join(ARTIFACT_DIR, f"verify_mobile_search_detail_hero_card_{ts}.png")
        page_mob.evaluate("document.querySelector('#resultView section:nth-of-type(1)').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.4)
        page_mob.screenshot(path=snap_hero, full_page=False)
        print(f"[✓] Hero card screenshot: {snap_hero}")

        # 3. TOP3 Comparison Grid screenshot
        snap_grid = os.path.join(ARTIFACT_DIR, f"verify_mobile_search_detail_comparison_grid_{ts}.png")
        page_mob.evaluate("document.getElementById('priceComparisonGrid').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.4)
        page_mob.screenshot(path=snap_grid, full_page=False)
        print(f"[✓] Comparison grid screenshot: {snap_grid}")

        # 4. TABLET REGRESSION VERIFICATION (800x1280)
        ctx_tab = browser.new_context(
            viewport={"width": 800, "height": 1280},
            device_scale_factor=2,
            has_touch=True,
            service_workers="block"
        )
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_tab.goto(f"{BASE_URL}/?cb={time.time()}", wait_until="networkidle", timeout=20000)
        time.sleep(1)
        page_tab.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_tab.press("#searchInput", "Enter")
        page_tab.wait_for_selector("#priceComparisonGrid .rank-card", timeout=15000)
        time.sleep(1.5)

        tab_metrics = page_tab.evaluate("""() => {
            const grid = document.getElementById('priceComparisonGrid');
            const rect = grid.getBoundingClientRect();
            return {
                device: "Tablet 800x1280",
                gridWidth: Math.round(rect.width),
                gridHeight: Math.round(rect.height),
                columnCount: window.getComputedStyle(grid).gridTemplateColumns.split(' ').length
            };
        }""")
        print(f"[TAB_REGRESSION_METRICS]{json.dumps(tab_metrics)}[/TAB_REGRESSION_METRICS]")

        snap_tab = os.path.join(ARTIFACT_DIR, f"verify_tablet_search_detail_regression_{ts}.png")
        page_tab.screenshot(path=snap_tab, full_page=False)
        print(f"[✓] Tablet regression screenshot: {snap_tab}")

        browser.close()

finally:
    if server_proc:
        server_proc.terminate()
        server_proc.wait()
