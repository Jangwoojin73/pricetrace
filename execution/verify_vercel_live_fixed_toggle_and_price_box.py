# -*- coding: utf-8 -*-
import os, sys, time, json
from playwright.sync_api import sync_playwright

VERCEL_URL = "https://pricetrace-nu.vercel.app"
ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

def run_vercel_live_verification():
    ts = time.strftime("%H%M%S")
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] Starting Vercel Live Fixed Toggle & Price Box Verification...")

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

        print("Executing search for CJ 햇반 on Vercel Live...")
        page_mob.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_mob.press("#searchInput", "Enter")

        page_mob.wait_for_selector("#priceComparisonGrid .rank-card", timeout=20000)
        page_mob.wait_for_selector("#lowestPriceDisplay", timeout=15000)
        time.sleep(2)

        page_mob.locator("#alertBanner").scroll_into_view_if_needed()
        time.sleep(0.5)

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

        print("Vercel Live Mobile Metrics:", json.dumps(mob_metrics, indent=2, ensure_ascii=False))

        # Screenshots
        path_toggle_shot = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_fixed_alert_toggle_{ts}.png")
        page_mob.locator("#alertBanner").screenshot(path=path_toggle_shot)
        print(f"Captured: {path_toggle_shot}")

        page_mob.locator("#lowestPriceDisplay").scroll_into_view_if_needed()
        time.sleep(0.5)
        path_price_shot = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_compact_price_box_{ts}.png")
        price_box_el = page_mob.locator("#lowestPriceDisplay").locator("xpath=ancestor::div[contains(@class, 'bg-gradient-to-br')]")
        price_box_el.screenshot(path=path_price_shot)
        print(f"Captured: {path_price_shot}")

        path_mob_view = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_mobile_full_{ts}.png")
        page_mob.screenshot(path=path_mob_view, full_page=False)
        print(f"Captured: {path_mob_view}")

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

        print("Executing search for CJ 햇반 on Vercel Live (Tablet)...")
        page_tab.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_tab.press("#searchInput", "Enter")

        page_tab.wait_for_selector("#priceComparisonGrid .rank-card", timeout=20000)
        page_tab.wait_for_selector("#lowestPriceDisplay", timeout=15000)
        time.sleep(2)

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

        print("Vercel Live Tablet Metrics:", json.dumps(tab_metrics, indent=2, ensure_ascii=False))

        path_tab_hero = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_tablet_hero_{ts}.png")
        page_tab.locator("#resultView section:first-of-type").screenshot(path=path_tab_hero)
        print(f"Captured: {path_tab_hero}")

        ctx_tab.close()
        browser.close()

    results = {
        "mobile": mob_metrics,
        "tablet": tab_metrics,
        "verified_at": now_str,
        "commit": "756f0b7"
    }
    metrics_path = os.path.join(ARTIFACT_DIR, f"metrics_vercel_live_fixed_toggle_and_price_box_{ts}.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nVercel Live Verification Finished! Metrics saved to: {metrics_path}")

if __name__ == "__main__":
    run_vercel_live_verification()
