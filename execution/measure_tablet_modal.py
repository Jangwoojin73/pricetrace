# -*- coding: utf-8 -*-
import os, sys, time, json, urllib.request, subprocess
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

    snap_tablet = os.path.join(ARTIFACT_DIR, "current_tablet_modal_baseline.png")
    snap_closeup = os.path.join(ARTIFACT_DIR, "current_tablet_modal_closeup_baseline.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        # 태블릿 800x1280 (사용자 업로드 사진과 가장 유사한 표준 안드로이드 10~11인치 태블릿 세로 뷰포트)
        ctx = browser.new_context(viewport={"width": 800, "height": 1280})
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # 하단 레이더 메뉴 탭 클릭
        page.click("#mobileNavSearchFabBtn")
        time.sleep(0.8)
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
                catChipHeight: cRect ? Math.round(cRect.height) : 0
            };
        }''')

        print("[BASELINE_METRICS]" + json.dumps(metrics, ensure_ascii=False) + "[/BASELINE_METRICS]")

        page.screenshot(path=snap_tablet)
        print(f"[✓] Tablet screenshot: {snap_tablet}")

        drawer = page.locator("#radarSearchDrawer")
        drawer.screenshot(path=snap_closeup)
        print(f"[✓] Closeup screenshot: {snap_closeup}")

        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
