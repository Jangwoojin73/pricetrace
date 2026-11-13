# -*- coding: utf-8 -*-
import os, sys, time, json
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
LIVE_URL = "https://pricetrace-nu.vercel.app"

CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-remote-fonts"
]

ts = time.strftime("%H%M%S")
snap_live_tab = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_tablet_expanded_{ts}.png")
snap_live_tab_closeup = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_tablet_closeup_{ts}.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
    ctx = browser.new_context(viewport={"width": 800, "height": 1280})
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    
    print(f"[*] Navigating to {LIVE_URL}...")
    page.goto(f"{LIVE_URL}/?v={time.time()}", wait_until="networkidle", timeout=25000)
    time.sleep(1.5)

    # 태블릿 환경에서 레이더 모달 오픈
    page.click("#mobileNavSearchFabBtn")
    time.sleep(1.0)
    page.wait_for_selector("#radarSearchDrawer", timeout=5000)

    metrics = page.evaluate('''() => {
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
            measuredAt: new Date().toLocaleTimeString('ko-KR'),
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            drawerWidth: dRect ? Math.round(dRect.width) : 0,
            drawerHeight: dRect ? Math.round(dRect.height) : 0,
            drawerTop: dRect ? Math.round(dRect.top) : 0,
            widthRatio: dRect ? ((dRect.width / window.innerWidth) * 100).toFixed(1) + '%' : '0%',
            heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
            inputHeight: iRect ? Math.round(iRect.height) : 0,
            padButtonWidth: pRect ? Math.round(pRect.width) : 0,
            padButtonHeight: pRect ? Math.round(pRect.height) : 0,
            quickChipHeight: qRect ? Math.round(qRect.height) : 0,
            catChipHeight: cRect ? Math.round(cRect.height) : 0,
            isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false,
            rect: dRect ? { x: dRect.x, y: dRect.y, width: dRect.width, height: dRect.height } : null
        };
    }''')

    print("[VERCEL_LIVE_METRICS]" + json.dumps(metrics, ensure_ascii=False) + "[/VERCEL_LIVE_METRICS]")

    page.screenshot(path=snap_live_tab)
    print(f"[✓] Live Tablet full screenshot: {snap_live_tab}")

    r = metrics.get("rect")
    if r:
        page.screenshot(path=snap_live_tab_closeup, clip={"x": max(0, r["x"] - 10), "y": max(0, r["y"] - 10), "width": min(800, r["width"] + 20), "height": min(1280, r["height"] + 20)})
        print(f"[✓] Live Tablet closeup screenshot: {snap_live_tab_closeup}")

    browser.close()
