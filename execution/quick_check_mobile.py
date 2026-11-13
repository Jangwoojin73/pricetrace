# -*- coding: utf-8 -*-
import os, sys, time, json
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"

CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-remote-fonts"
]

snap_mob = os.path.join(ARTIFACT_DIR, "verify_mobile_final_regression.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
    ctx = browser.new_context(viewport={"width": 393, "height": 852})
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
    time.sleep(1)

    page.evaluate("openRadarSearchModal()")
    time.sleep(0.6)
    
    metrics = page.evaluate('''() => {
        const drawer = document.getElementById('radarSearchDrawer');
        const dRect = drawer ? drawer.getBoundingClientRect() : null;
        return {
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            drawerWidth: dRect ? Math.round(dRect.width) : 0,
            drawerHeight: dRect ? Math.round(dRect.height) : 0,
            heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
            isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false
        };
    }''')
    print("[MOBILE_CHECK]" + json.dumps(metrics, ensure_ascii=False) + "[/MOBILE_CHECK]")
    page.screenshot(path=snap_mob)
    print(f"[✓] Mobile regression screenshot: {snap_mob}")
    browser.close()
