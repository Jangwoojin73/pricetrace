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
    snap_modal = os.path.join(ARTIFACT_DIR, f"verify_expanded_radar_modal_mobile_{ts}.png")
    snap_closeup = os.path.join(ARTIFACT_DIR, f"verify_expanded_radar_modal_closeup_{ts}.png")
    snap_pc = os.path.join(ARTIFACT_DIR, f"verify_expanded_radar_modal_pc_{ts}.png")

    with sync_playwright() as p:
        # 1. 모바일 뷰포트 실측 (393x852)
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={"width": 393, "height": 852})
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
            const rect = drawer ? drawer.getBoundingClientRect() : null;
            const padChips = Array.from(document.querySelectorAll('.modal-pad-chip'));
            const quickChips = Array.from(document.querySelectorAll('.modal-quick-chip'));
            const catChips = Array.from(document.querySelectorAll('.modal-category-chip'));
            const searchInput = document.getElementById('modalSearchInput');
            const searchInputRect = searchInput ? searchInput.getBoundingClientRect() : null;

            return {
                measuredAt: new Date().toLocaleTimeString('ko-KR'),
                drawerWidth: rect ? Math.round(rect.width) : 0,
                drawerHeight: rect ? Math.round(rect.height) : 0,
                viewportHeight: window.innerHeight,
                heightRatio: rect ? ((rect.height / window.innerHeight) * 100).toFixed(1) + '%' : '0%',
                searchInputHeight: searchInputRect ? Math.round(searchInputRect.height) : 0,
                padChipCount: padChips.length,
                padChipHeight: padChips[0] ? Math.round(padChips[0].getBoundingClientRect().height) : 0,
                quickChipCount: quickChips.length,
                quickChipHeight: quickChips[0] ? Math.round(quickChips[0].getBoundingClientRect().height) : 0,
                catChipCount: catChips.length,
                catChipHeight: catChips[0] ? Math.round(catChips[0].getBoundingClientRect().height) : 0
            };
        }''')
        print("Expanded Radar Modal Metrics (Mobile):", metrics)

        page.screenshot(path=snap_modal)
        print(f"[✓] Saved Expanded Mobile screenshot: {snap_modal} ({os.path.getsize(snap_modal)} bytes)")

        drawer_elem = page.locator("#radarSearchDrawer")
        drawer_elem.screenshot(path=snap_closeup)
        print(f"[✓] Saved Expanded Closeup screenshot: {snap_closeup} ({os.path.getsize(snap_closeup)} bytes)")

        # 자판 칩 클릭 테스트 (20개 클릭)
        first_pad = page.locator(".modal-pad-chip").first
        first_pad.click()
        time.sleep(0.3)
        input_val = page.locator("#modalSearchInput").input_value()
        print(f"[✓] Tested pad chip click, search input value: '{input_val}'")

        ctx.close()

        # 2. PC 데스크톱 뷰포트 (1440x900)
        pc_ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        pc_page = pc_ctx.new_page()
        pc_page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        pc_page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # PC 상단 검색창 등에서 레이더 모달 열기 함수 호출
        pc_page.evaluate("openRadarSearchModal()")
        time.sleep(0.6)
        pc_page.wait_for_selector("#radarSearchDrawer", timeout=5000)

        pc_metrics = pc_page.evaluate('''() => {
            const drawer = document.getElementById('radarSearchDrawer');
            const rect = drawer ? drawer.getBoundingClientRect() : null;
            return {
                drawerWidth: rect ? Math.round(rect.width) : 0,
                drawerHeight: rect ? Math.round(rect.height) : 0
            };
        }''')
        print("PC Radar Modal Metrics:", pc_metrics)

        pc_page.screenshot(path=snap_pc)
        print(f"[✓] Saved PC screenshot: {snap_pc} ({os.path.getsize(snap_pc)} bytes)")

        pc_ctx.close()
        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
