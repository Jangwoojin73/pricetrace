# -*- coding: utf-8 -*-
import os, time, ssl, urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
VERCEL_URL = "https://pricetrace-nu.vercel.app"

def check_deployment():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print("[*] Polling Vercel live site for update (90vh check)...")
    for i in range(20):
        try:
            req = urllib.request.Request(f"{VERCEL_URL}/?cachebust={time.time()}", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                if 'h-[90vh]' in html:
                    print(f"[✓] Vercel deployed updated version! (Attempt {i+1})")
                    return True
        except Exception as e:
            print(f"[-] Wait error: {e}")
        time.sleep(2)
    return False

def verify_live():
    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]
    
    ts = time.strftime("%H%M%S")
    snap_modal = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_zero_scroll_modal_{ts}.png")
    snap_closeup = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_zero_scroll_closeup_{ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={"width": 393, "height": 852})
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(f"{VERCEL_URL}/?v={time.time()}", wait_until="networkidle", timeout=20000)
        time.sleep(1)

        # 레이더 모달 오픈 및 실측
        page.click("#mobileNavSearchFabBtn")
        time.sleep(0.8)
        page.wait_for_selector("#radarSearchDrawer", timeout=8000)

        modal_metrics = page.evaluate('''() => {
            const drawer = document.getElementById('radarSearchDrawer');
            const dRect = drawer ? drawer.getBoundingClientRect() : null;
            const lastChip = document.querySelector('.modal-category-chip:last-child');
            const lRect = lastChip ? lastChip.getBoundingClientRect() : null;

            return {
                measuredAt: new Date().toLocaleTimeString('ko-KR'),
                drawerWidth: dRect ? Math.round(dRect.width) : 0,
                drawerHeight: dRect ? Math.round(dRect.height) : 0,
                viewportHeight: window.innerHeight,
                heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
                drawerScrollHeight: drawer ? drawer.scrollHeight : 0,
                drawerClientHeight: drawer ? drawer.clientHeight : 0,
                isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false,
                overflowPx: drawer ? Math.max(0, drawer.scrollHeight - drawer.clientHeight) : 0,
                lastChipFullyVisible: lRect && dRect ? (lRect.bottom <= dRect.bottom) : false
            };
        }''')
        print("Vercel Live Zero-Scroll Modal Metrics:", modal_metrics)

        page.screenshot(path=snap_modal)
        print(f"[✓] Saved Vercel Live Full screenshot: {snap_modal}")

        drawer_elem = page.locator("#radarSearchDrawer")
        drawer_elem.screenshot(path=snap_closeup)
        print(f"[✓] Saved Vercel Live Closeup screenshot: {snap_closeup}")

        ctx.close()
        browser.close()

if __name__ == "__main__":
    if check_deployment():
        verify_live()
    else:
        print("[!] Timeout, verifying anyway...")
        verify_live()
