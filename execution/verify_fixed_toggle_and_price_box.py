# -*- coding: utf-8 -*-
import os, sys, time, json, urllib.request, subprocess
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

# Disable proxy for localhost
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

    print("Server ready. Starting Playwright verification...")
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

        # ----------------------------------------------------
        # 1. MOBILE VERIFICATION (393x852)
        # ----------------------------------------------------
        print("\n[Mobile 393x852 Testing]")
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
        page_mob.goto(target_url, wait_until="load", timeout=20000)
        page_mob.wait_for_selector("#searchInput", timeout=10000)
        # Wait for Tailwind CDN to finish compiling classes
        try:
            page_mob.wait_for_function("() => window.tailwind !== undefined", timeout=10000)
        except Exception as e:
            print("Tailwind load warning:", e)
        time.sleep(1)

        print("Executing search for CJ 햇반...")
        page_mob.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_mob.press("#searchInput", "Enter")

        page_mob.wait_for_selector("#priceComparisonGrid .rank-card", timeout=15000)
        page_mob.wait_for_selector("#lowestPriceDisplay", timeout=10000)
        time.sleep(1.5)

        # Ensure elements are scrolled and settled
        page_mob.locator("#alertBanner").scroll_into_view_if_needed()
        time.sleep(0.5)

        # Measure mobile metrics
        mob_metrics = page_mob.evaluate("""() => {
            const alertBanner = document.getElementById('alertBanner');
            const toggleSwitch = document.getElementById('alertToggleSwitch');
            const toggleTrack = toggleSwitch ? toggleSwitch.nextElementSibling : null;
            const toggleLabel = document.getElementById('alertToggleLabel');
            
            const heroSection = document.querySelector('#resultView section:first-of-type');
            const lowestPriceDisplay = document.getElementById('lowestPriceDisplay');
            const priceBox = lowestPriceDisplay ? lowestPriceDisplay.closest('.bg-gradient-to-br') : null;
            const buyButton = document.getElementById('buyButton');
            const unitPriceDisplay = document.getElementById('unitPriceDisplay');
            const lowestMallName = document.getElementById('lowestMallName');

            const getMetrics = (el) => {
                if (!el) return null;
                const r = el.getBoundingClientRect();
                const cs = window.getComputedStyle(el);
                return {
                    width: Math.round(r.width * 10) / 10,
                    height: Math.round(r.height * 10) / 10,
                    top: Math.round(r.top * 10) / 10,
                    left: Math.round(r.left * 10) / 10,
                    display: cs.display,
                    padding: cs.padding
                };
            };

            return {
                timestamp: new Date().toLocaleTimeString(),
                alertBanner: getMetrics(alertBanner),
                toggleTrack: getMetrics(toggleTrack),
                toggleLabel: toggleLabel ? toggleLabel.textContent.trim() : null,
                toggleChecked: toggleSwitch ? toggleSwitch.checked : null,
                heroSection: getMetrics(heroSection),
                priceBox: getMetrics(priceBox),
                buyButton: getMetrics(buyButton),
                lowestPriceText: lowestPriceDisplay ? lowestPriceDisplay.textContent.trim() : null,
                unitPriceText: unitPriceDisplay ? unitPriceDisplay.textContent.trim() : null,
                lowestMallText: lowestMallName ? lowestMallName.textContent.trim() : null
            };
        }""")

        results['mobile'] = mob_metrics
        print("Mobile Metrics:", json.dumps(mob_metrics, indent=2, ensure_ascii=False))

        # Screenshots for Mobile
        # 1) Alert Banner (Toggle button focus)
        banner_el = page_mob.locator("#alertBanner")
        path_toggle_shot = os.path.join(ARTIFACT_DIR, f"verify_fixed_alert_toggle_{ts}.png")
        banner_el.screenshot(path=path_toggle_shot)
        print(f"Captured: {path_toggle_shot}")

        # 2) Compact Hero Card & Price Box Focus (Scrolled to show price & buy button)
        page_mob.locator("#lowestPriceDisplay").scroll_into_view_if_needed()
        time.sleep(0.5)
        path_hero_shot = os.path.join(ARTIFACT_DIR, f"verify_compact_hero_price_box_{ts}.png")
        # Capture the price box directly
        price_box_el = page_mob.locator("#lowestPriceDisplay").locator("xpath=ancestor::div[contains(@class, 'bg-gradient-to-br')]")
        price_box_el.screenshot(path=path_hero_shot)
        print(f"Captured: {path_hero_shot}")

        # 3) Full Mobile View with price box visible
        path_mob_price_view = os.path.join(ARTIFACT_DIR, f"verify_mobile_price_box_in_view_{ts}.png")
        page_mob.screenshot(path=path_mob_price_view, full_page=False)
        print(f"Captured: {path_mob_price_view}")

        # 4) Full Page Mobile Scroll View
        path_mob_full = os.path.join(ARTIFACT_DIR, f"verify_mobile_search_detail_full_{ts}.png")
        page_mob.screenshot(path=path_mob_full, full_page=True)
        print(f"Captured: {path_mob_full}")

        ctx_mob.close()

        # ----------------------------------------------------
        # 2. TABLET VERIFICATION (800x1280)
        # ----------------------------------------------------
        print("\n[Tablet 800x1280 Testing]")
        ctx_tab = browser.new_context(
            viewport={"width": 800, "height": 1280},
            device_scale_factor=2,
            has_touch=True,
            is_mobile=False,
            service_workers="block"
        )
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        page_tab.goto(target_url, wait_until="domcontentloaded", timeout=15000)
        page_tab.wait_for_selector("#searchInput", timeout=10000)
        time.sleep(1)

        print("Executing search for CJ 햇반 on tablet...")
        page_tab.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_tab.press("#searchInput", "Enter")

        page_tab.wait_for_selector("#priceComparisonGrid .rank-card", timeout=15000)
        page_tab.wait_for_selector("#lowestPriceDisplay", timeout=10000)
        time.sleep(1.5)

        page_tab.locator("#resultView section:first-of-type").scroll_into_view_if_needed()
        time.sleep(0.5)

        tab_metrics = page_tab.evaluate("""() => {
            const alertBanner = document.getElementById('alertBanner');
            const toggleSwitch = document.getElementById('alertToggleSwitch');
            const toggleTrack = toggleSwitch ? toggleSwitch.nextElementSibling : null;
            const heroSection = document.querySelector('#resultView section:first-of-type');
            const lowestPriceDisplay = document.getElementById('lowestPriceDisplay');
            const priceBox = lowestPriceDisplay ? lowestPriceDisplay.closest('.bg-gradient-to-br') : null;
            const buyButton = document.getElementById('buyButton');

            const getMetrics = (el) => {
                if (!el) return null;
                const r = el.getBoundingClientRect();
                return {
                    width: Math.round(r.width * 10) / 10,
                    height: Math.round(r.height * 10) / 10,
                    top: Math.round(r.top * 10) / 10,
                    left: Math.round(r.left * 10) / 10
                };
            };

            return {
                timestamp: new Date().toLocaleTimeString(),
                alertBanner: getMetrics(alertBanner),
                toggleTrack: getMetrics(toggleTrack),
                heroSection: getMetrics(heroSection),
                priceBox: getMetrics(priceBox),
                buyButton: getMetrics(buyButton)
            };
        }""")

        results['tablet'] = tab_metrics
        print("Tablet Metrics:", json.dumps(tab_metrics, indent=2, ensure_ascii=False))

        path_tab_hero = os.path.join(ARTIFACT_DIR, f"verify_tablet_hero_compact_{ts}.png")
        hero_tab_el = page_tab.locator("#resultView section:first-of-type")
        hero_tab_el.screenshot(path=path_tab_hero)
        print(f"Captured: {path_tab_hero}")

        ctx_tab.close()
        browser.close()

    # Save metrics JSON to results
    metrics_path = os.path.join(ARTIFACT_DIR, f"metrics_fixed_toggle_and_price_box_{ts}.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nAll validations completed successfully! Metrics saved to: {metrics_path}")

finally:
    if server_proc:
        print("Terminating test server...")
        server_proc.terminate()
        server_proc.wait()
