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
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(15):
            time.sleep(0.4)
            if is_server_up():
                break

    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    ts = time.strftime("%H%M%S")
    snap_tablet_full = os.path.join(ARTIFACT_DIR, f"verify_tablet_config_modal_expanded_{ts}.png")
    snap_tablet_closeup = os.path.join(ARTIFACT_DIR, f"verify_tablet_config_modal_closeup_{ts}.png")
    snap_mobile_check = os.path.join(ARTIFACT_DIR, f"verify_mobile_config_modal_regression_{ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. 태블릿 800x1280 실측
        ctx_tab = browser.new_context(viewport={"width": 800, "height": 1280})
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_tab.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # 하단 네비게이션 바 우측 "설정" 탭 버튼 클릭
        page_tab.click("#mobileNavConfigBtn")
        time.sleep(0.6)
        page_tab.wait_for_selector("#configModal:not(.hidden)", timeout=5000)

        tab_metrics = page_tab.evaluate('''() => {
            const modal = document.querySelector('#configModal > div');
            const mRect = modal ? modal.getBoundingClientRect() : null;
            const input = document.getElementById('modalTargetPriceInput');
            const iRect = input ? input.getBoundingClientRect() : null;
            const firstPreset = document.querySelector('.preset-price-btn');
            const pRect = firstPreset ? firstPreset.getBoundingClientRect() : null;
            const titleEl = document.querySelector('#configModal h3');
            const tStyle = titleEl ? window.getComputedStyle(titleEl) : null;
            const itemLabel = document.querySelector('#configModal .text-slate-800');
            const lStyle = itemLabel ? window.getComputedStyle(itemLabel) : null;
            const itemSub = document.querySelector('#configModal .text-slate-500');
            const sStyle = itemSub ? window.getComputedStyle(itemSub) : null;
            const saveBtn = document.getElementById('saveConfigModalBtn');
            const btnRect = saveBtn ? saveBtn.getBoundingClientRect() : null;
            const toggleDiv = document.querySelector('#modalAlertToggle + div');
            const togRect = toggleDiv ? toggleDiv.getBoundingClientRect() : null;

            return {
                device: "Tablet 800x1280",
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                modalWidth: mRect ? Math.round(mRect.width) : 0,
                modalHeight: mRect ? Math.round(mRect.height) : 0,
                widthRatio: mRect ? ((mRect.width / window.innerWidth) * 100).toFixed(1) + '%' : '0%',
                inputHeight: iRect ? Math.round(iRect.height) : 0,
                presetBtnWidth: pRect ? Math.round(pRect.width) : 0,
                presetBtnHeight: pRect ? Math.round(pRect.height) : 0,
                titleFontSize: tStyle ? tStyle.fontSize : '',
                itemTitleFontSize: lStyle ? lStyle.fontSize : '',
                itemSubFontSize: sStyle ? sStyle.fontSize : '',
                saveBtnHeight: btnRect ? Math.round(btnRect.height) : 0,
                toggleWidth: togRect ? Math.round(togRect.width) : 0,
                toggleHeight: togRect ? Math.round(togRect.height) : 0,
                rect: mRect ? { x: mRect.x, y: mRect.y, width: mRect.width, height: mRect.height } : null
            };
        }''')

        print("[TAB_CONFIG_METRICS]" + json.dumps(tab_metrics, ensure_ascii=False) + "[/TAB_CONFIG_METRICS]")

        page_tab.screenshot(path=snap_tablet_full)
        print(f"[✓] Tablet full screenshot: {snap_tablet_full}")

        r = tab_metrics.get("rect")
        if r:
            page_tab.screenshot(path=snap_tablet_closeup, clip={"x": max(0, r["x"] - 15), "y": max(0, r["y"] - 15), "width": min(800, r["width"] + 30), "height": min(1280, r["height"] + 30)})
            print(f"[✓] Tablet closeup screenshot: {snap_tablet_closeup}")

        ctx_tab.close()

        # 2. 모바일 393x852 회귀 검증
        ctx_mob = browser.new_context(viewport={"width": 393, "height": 852})
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_mob.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        page_mob.click("#mobileNavConfigBtn")
        time.sleep(0.6)
        page_mob.wait_for_selector("#configModal:not(.hidden)", timeout=5000)

        mob_metrics = page_mob.evaluate('''() => {
            const modal = document.querySelector('#configModal > div');
            const mRect = modal ? modal.getBoundingClientRect() : null;
            return {
                device: "Mobile 393x852",
                modalWidth: mRect ? Math.round(mRect.width) : 0,
                modalHeight: mRect ? Math.round(mRect.height) : 0,
                widthRatio: mRect ? ((mRect.width / window.innerWidth) * 100).toFixed(1) + '%' : '0%'
            };
        }''')
        print("[MOB_CONFIG_METRICS]" + json.dumps(mob_metrics, ensure_ascii=False) + "[/MOB_CONFIG_METRICS]")

        page_mob.screenshot(path=snap_mobile_check)
        print(f"[✓] Mobile regression screenshot: {snap_mobile_check}")

        ctx_mob.close()
        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
