# -*- coding: utf-8 -*-
import os, sys, time, json
from playwright.sync_api import sync_playwright

VERCEL_URL = "https://pricetrace-nu.vercel.app"
ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

def run_vercel_live_verification():
    ts = time.strftime("%H%M%S")
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] Starting Vercel Live Tablet Config Modal Verification...")

    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    with sync_playwright() as p:
        # 1. TABLET VERIFICATION (800x1280)
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx_tab = browser.new_context(
            viewport={"width": 800, "height": 1280},
            service_workers="block"
        )
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        target_url = f"{VERCEL_URL}/?cb={time.time()}"
        print(f"Navigating to tablet live target: {target_url}")
        page_tab.goto(target_url, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # Trigger Config Modal
        page_tab.click("#mobileNavConfigBtn")
        time.sleep(0.8)

        tablet_metrics = page_tab.evaluate("""() => {
            const modalBox = document.querySelector('#configModal > div');
            const rect = modalBox.getBoundingClientRect();
            
            const titleEl = modalBox.querySelector('h3 span');
            const titleCs = titleEl ? window.getComputedStyle(titleEl) : null;
            
            const inputEl = document.querySelector('#modalTargetPriceInput');
            const inputRect = inputEl ? inputEl.getBoundingClientRect() : null;
            
            const presetBtn = modalBox.querySelector('.preset-price-btn');
            const presetRect = presetBtn ? presetBtn.getBoundingClientRect() : null;
            
            const itemTitle = modalBox.querySelector('label.flex div.text-xs, label.flex div.text-base');
            const itemTitleCs = itemTitle ? window.getComputedStyle(itemTitle) : null;
            
            const itemSub = modalBox.querySelector('label.flex div.text-\\\\[11px\\\\], label.flex div.text-sm');
            const itemSubCs = itemSub ? window.getComputedStyle(itemSub) : null;
            
            const saveBtn = document.querySelector('#saveConfigModalBtn');
            const saveRect = saveBtn ? saveBtn.getBoundingClientRect() : null;
            
            const toggleSpan = modalBox.querySelector('input[type="checkbox"] + div');
            const toggleRect = toggleSpan ? toggleSpan.getBoundingClientRect() : null;

            return {
                device: "Tablet 800x1280 (Vercel Live)",
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                modalWidth: Math.round(rect.width),
                modalHeight: Math.round(rect.height),
                widthRatio: ((rect.width / window.innerWidth) * 100).toFixed(1) + "%",
                inputHeight: inputRect ? Math.round(inputRect.height) : 0,
                presetBtnWidth: presetRect ? Math.round(presetRect.width) : 0,
                presetBtnHeight: presetRect ? Math.round(presetRect.height) : 0,
                titleFontSize: titleCs ? titleCs.fontSize : 'N/A',
                itemTitleFontSize: itemTitleCs ? itemTitleCs.fontSize : 'N/A',
                itemSubFontSize: itemSubCs ? itemSubCs.fontSize : 'N/A',
                saveBtnHeight: saveRect ? Math.round(saveRect.height) : 0,
                toggleWidth: toggleRect ? Math.round(toggleRect.width) : 0,
                toggleHeight: toggleRect ? Math.round(toggleRect.height) : 0,
                rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
            };
        }""")

        print(f"[VERCEL_TAB_METRICS]{json.dumps(tablet_metrics)}[/VERCEL_TAB_METRICS]")

        tablet_full_path = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_tablet_config_expanded_{ts}.png")
        page_tab.screenshot(path=tablet_full_path, full_page=False)
        print(f"[✓] Vercel Tablet full screenshot: {tablet_full_path}")

        r = tablet_metrics['rect']
        tablet_closeup_path = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_tablet_config_closeup_{ts}.png")
        page_tab.screenshot(
            path=tablet_closeup_path,
            clip={"x": max(0, r["x"] - 20), "y": max(0, r["y"] - 20), "width": r["width"] + 40, "height": min(r["height"] + 40, 1280 - r["y"])}
        )
        print(f"[✓] Vercel Tablet closeup screenshot: {tablet_closeup_path}")
        browser.close()

        # 2. MOBILE REGRESSION VERIFICATION (393x852)
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx_mob = browser.new_context(
            viewport={"width": 393, "height": 852},
            service_workers="block"
        )
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_mob.goto(f"{VERCEL_URL}/?cb={time.time()}", wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # Trigger Config Modal
        page_mob.click("#mobileNavConfigBtn")
        time.sleep(0.8)

        mobile_metrics = page_mob.evaluate("""() => {
            const modalBox = document.querySelector('#configModal > div');
            const rect = modalBox.getBoundingClientRect();
            return {
                device: "Mobile 393x852 (Vercel Live)",
                modalWidth: Math.round(rect.width),
                modalHeight: Math.round(rect.height),
                widthRatio: ((rect.width / window.innerWidth) * 100).toFixed(1) + "%"
            };
        }""")
        print(f"[VERCEL_MOB_METRICS]{json.dumps(mobile_metrics)}[/VERCEL_MOB_METRICS]")

        mobile_path = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_mobile_config_regression_{ts}.png")
        page_mob.screenshot(path=mobile_path, full_page=False)
        print(f"[✓] Vercel Mobile regression screenshot: {mobile_path}")
        browser.close()

if __name__ == "__main__":
    run_vercel_live_verification()
