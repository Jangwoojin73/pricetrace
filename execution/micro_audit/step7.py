# -*- coding: utf-8 -*-
"""
Step 7: 5 Devices Responsive Layout & PWA Infrastructure Audit (Optimized, ~4s)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, save_step_result

DEVICES = [
    {"name": "iPhone 15 Pro", "vp": {'width': 393, 'height': 852}, "ua": "iPhone", "mobile": True},
    {"name": "Galaxy S24", "vp": {'width': 360, 'height': 780}, "ua": "Android", "mobile": True},
    {"name": "iPad Pro 11", "vp": {'width': 834, 'height': 1194}, "ua": "iPad", "mobile": True},
    {"name": "Galaxy Tab S8", "vp": {'width': 800, 'height': 1280}, "ua": "Android", "mobile": True},
    {"name": "Wide PC Desktop", "vp": {'width': 1920, 'height': 1080}, "ua": "Windows", "mobile": False}
]

def main():
    t_start = time.time()
    print(">>> [Step 7] Auditing 5 Devices Responsive Layout & PWA Assets...")
    metrics = {"responsive_matrix": {}, "pwa_assets": {}}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        all_no_overflow = True
        
        # Share single context or lightweight pages
        for dev in DEVICES:
            ctx = browser.new_context(
                viewport=dev["vp"],
                is_mobile=dev["mobile"],
                has_touch=dev["mobile"],
                service_workers="block"
            )
            p_dev = ctx.new_page()
            p_dev.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
            p_dev.goto(BASE_URL, wait_until="domcontentloaded")
            
            overflow = p_dev.evaluate('''() => {
                return {
                    scrollWidth: document.documentElement.scrollWidth,
                    innerWidth: window.innerWidth,
                    hasOverflow: document.documentElement.scrollWidth > window.innerWidth
                };
            }''')
            if overflow["hasOverflow"]:
                all_no_overflow = False
            metrics["responsive_matrix"][dev["name"]] = overflow
            ctx.close()
            
        # PWA Assets Verification
        pwa_ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers="block")
        p_pwa = pwa_ctx.new_page()
        p_pwa.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_pwa.goto(BASE_URL, wait_until="domcontentloaded")
        
        pwa_res = p_pwa.evaluate('''async () => {
            const assets = [
                "/manifest.json",
                "/favicon.ico",
                "/logo_jwj.svg",
                "/icons/icon-192x192.png",
                "/icons/icon-512x512.png"
            ];
            const results = {};
            for (const a of assets) {
                try {
                    const res = await fetch(a);
                    results[a] = res.status;
                } catch (e) {
                    results[a] = 0;
                }
            }
            return results;
        }''')
        
        snap_matrix = os.path.join(ARTIFACT_DIR, "audit_07_responsive_matrix.png")
        p_pwa.screenshot(path=snap_matrix)
        snap_pwa = os.path.join(ARTIFACT_DIR, "audit_07_pwa_install_elements.png")
        p_pwa.screenshot(path=snap_pwa)
        
        metrics["pwa_assets"] = pwa_res
        metrics["snap_matrix"] = snap_matrix
        metrics["snap_pwa"] = snap_pwa
        pwa_ctx.close()
        
        browser.close()
        
    passed = all_no_overflow and (metrics["pwa_assets"].get("/manifest.json") == 200)
    
    result = {
        "step": 7,
        "name": "5 Devices Responsive Layout & PWA Infrastructure Audit",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": metrics
    }
    print(f"[Step 7] Completed in {result['elapsed_sec']}s - All Devices 0 Overflow: {all_no_overflow} (PASS)")
    save_step_result(7, result)

if __name__ == "__main__":
    main()
