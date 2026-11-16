# -*- coding: utf-8 -*-
import os, sys, time, json
from playwright.sync_api import sync_playwright

VERCEL_URL = "https://pricetrace-nu.vercel.app"
ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

def measure_search_detail():
    ts = time.strftime("%H%M%S")
    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            has_touch=True,
            is_mobile=True,
            service_workers="block"
        )
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        target_url = f"{VERCEL_URL}/?cb={time.time()}"
        print(f"Navigating to: {target_url}")
        page.goto(target_url, wait_until="networkidle", timeout=30000)
        time.sleep(1.5)

        # Trigger search for "CJ제일제당 햇반 210g 24개"
        print("Typing search query into #searchInput...")
        page.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page.press("#searchInput", "Enter")

        # Wait for search results
        print("Waiting for search results to render...")
        page.wait_for_selector("#priceComparisonGrid .rank-card", timeout=20000)
        time.sleep(2)

        # 1. Alert Banner screenshot
        snap_alert = os.path.join(ARTIFACT_DIR, f"baseline_search_detail_alert_banner_{ts}.png")
        page.evaluate("document.getElementById('alertBanner').scrollIntoView({ behavior: 'instant', block: 'center' })")
        time.sleep(0.5)
        page.screenshot(path=snap_alert, full_page=False)
        print(f"[✓] Alert banner screenshot: {snap_alert}")

        # 2. Hero Card screenshot
        snap_hero = os.path.join(ARTIFACT_DIR, f"baseline_search_detail_hero_card_{ts}.png")
        page.evaluate("document.querySelector('#resultView section:nth-of-type(1)').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.5)
        page.screenshot(path=snap_hero, full_page=False)
        print(f"[✓] Hero card screenshot: {snap_hero}")

        # 3. TOP3 Comparison Grid screenshot
        snap_grid = os.path.join(ARTIFACT_DIR, f"baseline_search_detail_comparison_grid_{ts}.png")
        page.evaluate("document.getElementById('priceComparisonGrid').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.5)
        page.screenshot(path=snap_grid, full_page=False)
        print(f"[✓] Comparison grid screenshot: {snap_grid}")

        browser.close()

if __name__ == "__main__":
    measure_search_detail()
