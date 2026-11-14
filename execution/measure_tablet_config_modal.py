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

    snap_tablet = os.path.join(ARTIFACT_DIR, "current_tablet_config_modal_baseline.png")
    snap_closeup = os.path.join(ARTIFACT_DIR, "current_tablet_config_modal_closeup_baseline.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={"width": 800, "height": 1280})
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        time.sleep(1)

        # 하단 네비게이션 바 우측 "설정" 탭 버튼 클릭
        page.click("#mobileNavConfigBtn")
        time.sleep(0.6)
        page.wait_for_selector("#configModal:not(.hidden)", timeout=5000)

        metrics = page.evaluate('''() => {
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

            return {
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
                rect: mRect ? { x: mRect.x, y: mRect.y, width: mRect.width, height: mRect.height } : null
            };
        }''')

        print("[CONFIG_BASELINE]" + json.dumps(metrics, ensure_ascii=False) + "[/CONFIG_BASELINE]")

        page.screenshot(path=snap_tablet)
        print(f"[✓] Tablet Config Modal screenshot: {snap_tablet}")

        r = metrics.get("rect")
        if r:
            page.screenshot(path=snap_closeup, clip={"x": max(0, r["x"] - 15), "y": max(0, r["y"] - 15), "width": min(800, r["width"] + 30), "height": min(1280, r["height"] + 30)})
            print(f"[✓] Tablet Config Modal Closeup: {snap_closeup}")

        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
