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
    snap_modal = os.path.join(ARTIFACT_DIR, f"current_radar_modal_{ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={"width": 393, "height": 852})
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # 하단 레이더 메뉴 탭 클릭 (ID: mobileNavSearchFabBtn)
        page.click("#mobileNavSearchFabBtn")
        time.sleep(0.8)
        page.wait_for_selector("#radarSearchDrawer", timeout=5000)

        metrics = page.evaluate('''() => {
            const drawer = document.getElementById('radarSearchDrawer');
            const rect = drawer ? drawer.getBoundingClientRect() : null;
            const chips = Array.from(document.querySelectorAll('.modal-pad-chip'));
            const quickChips = Array.from(document.querySelectorAll('.modal-quick-chip'));
            return {
                measuredAt: new Date().toLocaleTimeString('ko-KR'),
                drawerWidth: rect ? Math.round(rect.width) : 0,
                drawerHeight: rect ? Math.round(rect.height) : 0,
                viewportHeight: window.innerHeight,
                heightRatio: rect ? ((rect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
                padChipCount: chips.length,
                quickChipCount: quickChips.length,
                firstChipHeight: chips[0] ? Math.round(chips[0].getBoundingClientRect().height) : 0
            };
        }''')
        print("Current Radar Modal Metrics:", metrics)

        page.screenshot(path=snap_modal)
        print(f"[✓] Saved Current Radar Modal screenshot: {snap_modal}")

        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
