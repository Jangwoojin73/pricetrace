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

    ts = time.strftime("%H%M%S")
    snap_tab_800 = os.path.join(ARTIFACT_DIR, f"verify_tablet_800x1280_expanded_{ts}.png")
    snap_tab_800_closeup = os.path.join(ARTIFACT_DIR, f"verify_tablet_800x1280_closeup_{ts}.png")
    snap_tab_820 = os.path.join(ARTIFACT_DIR, f"verify_tablet_820x1180_expanded_{ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. 800x1280 안드로이드 표준 태블릿 (사용자 실기 기기 규격)
        ctx1 = browser.new_context(viewport={"width": 800, "height": 1280})
        page1 = ctx1.new_page()
        page1.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page1.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1.2)

        # 하단 레이더 메뉴 모달 오픈
        page1.evaluate("openRadarSearchModal()")
        time.sleep(0.6)
        page1.wait_for_selector("#radarSearchModal.modal-open", timeout=5000)

        metrics_800 = page1.evaluate('''() => {
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
                device: "Android Tablet 800x1280",
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                drawerWidth: dRect ? Math.round(dRect.width) : 0,
                drawerHeight: dRect ? Math.round(dRect.height) : 0,
                widthRatio: dRect ? ((dRect.width / window.innerWidth) * 100).toFixed(1) + '%' : '0%',
                heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
                inputHeight: iRect ? Math.round(iRect.height) : 0,
                padButtonWidth: pRect ? Math.round(pRect.width) : 0,
                padButtonHeight: pRect ? Math.round(pRect.height) : 0,
                quickChipHeight: qRect ? Math.round(qRect.height) : 0,
                catChipHeight: cRect ? Math.round(cRect.height) : 0,
                isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false
            };
        }''')

        print("[METRICS_800]" + json.dumps(metrics_800, ensure_ascii=False) + "[/METRICS_800]")
        page1.screenshot(path=snap_tab_800)
        print(f"[✓] Saved 800x1280 screenshot: {snap_tab_800}")

        drawer1 = page1.locator("#radarSearchDrawer")
        drawer1.screenshot(path=snap_tab_800_closeup)
        print(f"[✓] Saved 800x1280 closeup screenshot: {snap_tab_800_closeup}")
        ctx1.close()

        # 2. 820x1180 iPad Air 규격
        ctx2 = browser.new_context(viewport={"width": 820, "height": 1180})
        page2 = ctx2.new_page()
        page2.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page2.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1.2)

        page2.evaluate("openRadarSearchModal()")
        time.sleep(0.6)
        page2.wait_for_selector("#radarSearchModal.modal-open", timeout=5000)

        metrics_820 = page2.evaluate('''() => {
            const drawer = document.getElementById('radarSearchDrawer');
            const dRect = drawer ? drawer.getBoundingClientRect() : null;
            return {
                device: "iPad Air 820x1180",
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                drawerWidth: dRect ? Math.round(dRect.width) : 0,
                drawerHeight: dRect ? Math.round(dRect.height) : 0,
                widthRatio: dRect ? ((dRect.width / window.innerWidth) * 100).toFixed(1) + '%' : '0%',
                heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
                isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false
            };
        }''')
        print("[METRICS_820]" + json.dumps(metrics_820, ensure_ascii=False) + "[/METRICS_820]")
        page2.screenshot(path=snap_tab_820)
        print(f"[✓] Saved 820x1180 screenshot: {snap_tab_820}")
        ctx2.close()

        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
