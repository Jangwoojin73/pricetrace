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
snap_modal = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_compact_fit_mobile_{ts}.png")
snap_closeup = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_compact_fit_closeup_{ts}.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
    ctx = browser.new_context(viewport={"width": 393, "height": 852})
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    
    print(f"[*] Navigating to {LIVE_URL}...")
    page.goto(f"{LIVE_URL}/?v={time.time()}", wait_until="networkidle", timeout=25000)
    time.sleep(1.5)

    # 하단 레이더 메뉴 탭 클릭
    page.click("#mobileNavSearchFabBtn")
    time.sleep(1.0)
    page.wait_for_selector("#radarSearchDrawer", timeout=5000)

    metrics = page.evaluate('''() => {
        const drawer = document.getElementById('radarSearchDrawer');
        const dRect = drawer ? drawer.getBoundingClientRect() : null;
        const lastChip = document.querySelector('.modal-category-chip:last-child');
        const lRect = lastChip ? lastChip.getBoundingClientRect() : null;

        return {
            measuredAt: new Date().toLocaleTimeString('ko-KR'),
            viewportHeight: window.innerHeight,
            drawerHeight: dRect ? Math.round(dRect.height) : 0,
            drawerTop: dRect ? Math.round(dRect.top) : 0,
            heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
            drawerScrollHeight: drawer ? drawer.scrollHeight : 0,
            drawerClientHeight: drawer ? drawer.clientHeight : 0,
            isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false,
            overflowPx: drawer ? Math.max(0, drawer.scrollHeight - drawer.clientHeight) : 0,
            bottomPaddingDistance: lRect && dRect ? Math.round(dRect.bottom - lRect.bottom) : 0,
            hasExcessiveWhitespace: lRect && dRect ? (dRect.bottom - lRect.bottom > 50) : false
        };
    }''')

    print("[METRICS_JSON]" + json.dumps(metrics, ensure_ascii=False) + "[/METRICS_JSON]")

    # 전체 화면 스크린샷
    page.screenshot(path=snap_modal)
    print(f"[✓] Full screenshot: {snap_modal}")

    # 모달 클로즈업 스크린샷
    drawer_elem = page.locator("#radarSearchDrawer")
    drawer_elem.screenshot(path=snap_closeup)
    print(f"[✓] Closeup screenshot: {snap_closeup}")

    browser.close()
