# -*- coding: utf-8 -*-
import os, sys, time, subprocess, urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

def is_server_up():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/status", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

try:
    if not is_server_up():
        print("[*] Starting local server.py on port 8080...")
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(15):
            time.sleep(0.4)
            if is_server_up():
                print("[✓] Server ready!")
                break

    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    ts = time.strftime("%H%M%S")
    snap_tablet = os.path.join(ARTIFACT_DIR, f"verify_tablet_radar_modal_{ts}.png")
    snap_tablet_closeup = os.path.join(ARTIFACT_DIR, f"verify_tablet_radar_modal_closeup_{ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        
        # 태블릿 표준 뷰포트 (iPad Pro 11 / Air 834 x 1194)
        ctx = browser.new_context(viewport={"width": 834, "height": 1194})
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # 태블릿에서 하단 내비게이션 바 노출 여부 확인
        nav_visible = page.is_visible("#mobileBottomNav")
        print(f"Tablet Bottom Nav Visible: {nav_visible}")

        # 레이더 탭 클릭
        page.click("#mobileNavSearchFabBtn")
        time.sleep(0.8)
        page.wait_for_selector("#radarSearchDrawer", timeout=5000)

        metrics = page.evaluate('''() => {
            const modal = document.getElementById('radarSearchModal');
            const drawer = document.getElementById('radarSearchDrawer');
            const dRect = drawer ? drawer.getBoundingClientRect() : null;
            const mStyle = window.getComputedStyle(modal);
            const dStyle = window.getComputedStyle(drawer);
            
            return {
                measuredAt: new Date().toLocaleTimeString('ko-KR'),
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                navVisible: !!document.getElementById('mobileBottomNav') && window.getComputedStyle(document.getElementById('mobileBottomNav')).display !== 'none',
                drawerWidth: dRect ? Math.round(dRect.width) : 0,
                drawerHeight: dRect ? Math.round(dRect.height) : 0,
                drawerTop: dRect ? Math.round(dRect.top) : 0,
                drawerBottom: dRect ? Math.round(dRect.bottom) : 0,
                drawerLeft: dRect ? Math.round(dRect.left) : 0,
                borderRadius: dStyle.borderRadius,
                alignPosition: (dRect.bottom >= window.innerHeight - 20) ? 'Bottom-Docked Bottom Sheet (하단 바닥 밀착 플로팅 시트)' : 'Center Modal (중앙 팝업)',
                heightRatioToViewport: ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%'
            };
        }''')
        print("Tablet Radar Modal Metrics:", metrics)

        page.screenshot(path=snap_tablet)
        print(f"[✓] Saved Tablet Full screenshot: {snap_tablet} ({os.path.getsize(snap_tablet)} bytes)")

        drawer_elem = page.locator("#radarSearchDrawer")
        drawer_elem.screenshot(path=snap_tablet_closeup)
        print(f"[✓] Saved Tablet Closeup screenshot: {snap_tablet_closeup} ({os.path.getsize(snap_tablet_closeup)} bytes)")

        ctx.close()
        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
