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
    snap_tab_800 = os.path.join(ARTIFACT_DIR, f"verify_tablet_800x1280_final_{ts}.png")
    snap_tab_closeup = os.path.join(ARTIFACT_DIR, f"verify_tablet_800x1280_closeup_final_{ts}.png")
    snap_mobile = os.path.join(ARTIFACT_DIR, f"verify_mobile_regression_check_{ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. 태블릿 800x1280 실측
        ctx_tab = browser.new_context(viewport={"width": 800, "height": 1280})
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_tab.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1.0)

        page_tab.evaluate("openRadarSearchModal()")
        time.sleep(0.5)
        page_tab.wait_for_selector("#radarSearchModal.modal-open", timeout=5000)

        tab_metrics = page_tab.evaluate('''() => {
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
                device: "Tablet 800x1280",
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
        print("[TAB_METRICS]" + json.dumps(tab_metrics, ensure_ascii=False) + "[/TAB_METRICS]")

        page_tab.screenshot(path=snap_tab_800)
        print(f"[✓] Tablet full screenshot: {snap_tab_800}")

        r = tab_metrics.get("rect")
        if r:
            # 안전 클립 캡처
            page_tab.screenshot(path=snap_tab_closeup, clip={"x": max(0, r["x"] - 10), "y": max(0, r["y"] - 10), "width": min(800, r["width"] + 20), "height": min(1280, r["height"] + 20)})
            print(f"[✓] Tablet closeup screenshot: {snap_tab_closeup}")

        ctx_tab.close()

        # 2. 모바일 393x852 회귀 검증
        ctx_mob = browser.new_context(viewport={"width": 393, "height": 852})
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_mob.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1.0)

        page_mob.evaluate("openRadarSearchModal()")
        time.sleep(0.5)
        page_mob.wait_for_selector("#radarSearchModal.modal-open", timeout=5000)

        mob_metrics = page_mob.evaluate('''() => {
            const drawer = document.getElementById('radarSearchDrawer');
            const dRect = drawer ? drawer.getBoundingClientRect() : null;
            return {
                device: "Mobile 393x852",
                drawerWidth: dRect ? Math.round(dRect.width) : 0,
                drawerHeight: dRect ? Math.round(dRect.height) : 0,
                heightRatio: dRect ? ((dRect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
                isZeroScroll: drawer ? drawer.scrollHeight <= drawer.clientHeight : false
            };
        }''')
        print("[MOB_METRICS]" + json.dumps(mob_metrics, ensure_ascii=False) + "[/MOB_METRICS]")

        page_mob.screenshot(path=snap_mobile)
        print(f"[✓] Mobile regression check screenshot: {snap_mobile}")

        ctx_mob.close()
        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
