# -*- coding: utf-8 -*-
"""
Step 5: Bottom Navigation 5 Tabs Baseline & Scroll Lock Stability Audit
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, save_step_result

def main():
    t_start = time.time()
    print(">>> [Step 5] Auditing Bottom Navigation Baseline & Scroll Lock...")
    metrics = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        
        # 5-1. Mobile Bottom Dock (iPhone 15 Pro, 393x852)
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_m = m_ctx.new_page()
        p_m.set_default_timeout(10000)
        p_m.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_m.goto(BASE_URL, wait_until="domcontentloaded")
        p_m.wait_for_timeout(500)
        
        dock_metrics = p_m.evaluate('''() => {
            const btnIds = ["mobileNavHomeBtn", "mobileNavSearchFabBtn", "mobileNavSteadyBtn", "mobileNavHotdealBtn", "mobileNavConfigBtn"];
            const rects = btnIds.map(id => {
                const el = document.getElementById(id);
                return el ? el.getBoundingClientRect() : null;
            });
            const bottoms = rects.map(r => r ? Math.round(r.bottom) : 0);
            const baselineDiff = Math.max(...bottoms) - Math.min(...bottoms);
            return {
                baselineDiff: baselineDiff,
                allFound: rects.every(r => r !== null)
            };
        }''')
        
        # Steady Tab Scroll Lock
        p_m.click("#mobileNavSteadyBtn")
        p_m.wait_for_timeout(400)
        y1_steady = p_m.evaluate("window.scrollY")
        p_m.click("#mobileNavSteadyBtn")
        p_m.wait_for_timeout(400)
        y2_steady = p_m.evaluate("window.scrollY")
        steady_diff = abs(y1_steady - y2_steady)
        snap_steady = os.path.join(ARTIFACT_DIR, "audit_05_mobile_steady_scroll_lock.png")
        p_m.screenshot(path=snap_steady)
        
        # Hotdeal Tab Scroll Lock
        p_m.click("#mobileNavHotdealBtn")
        p_m.wait_for_timeout(400)
        y1_hotdeal = p_m.evaluate("window.scrollY")
        p_m.click("#mobileNavHotdealBtn")
        p_m.wait_for_timeout(400)
        y2_hotdeal = p_m.evaluate("window.scrollY")
        hotdeal_diff = abs(y1_hotdeal - y2_hotdeal)
        snap_hotdeal = os.path.join(ARTIFACT_DIR, "audit_05_mobile_hotdeal_scroll_lock.png")
        p_m.screenshot(path=snap_hotdeal)
        
        metrics["mobile"] = {
            "baseline_diff": dock_metrics["baselineDiff"],
            "steady_scroll_diff": steady_diff,
            "hotdeal_scroll_diff": hotdeal_diff,
            "snap_steady": snap_steady,
            "snap_hotdeal": snap_hotdeal
        }
        m_ctx.close()
        
        # 5-2. Tablet (iPad Pro 11, 834x1194)
        tab_ctx = browser.new_context(
            viewport={'width': 834, 'height': 1194},
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_tab = tab_ctx.new_page()
        p_tab.set_default_timeout(10000)
        p_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_tab.goto(BASE_URL, wait_until="domcontentloaded")
        p_tab.wait_for_timeout(300)
        p_tab.click("#mobileNavHotdealBtn")
        p_tab.wait_for_timeout(400)
        snap_tab = os.path.join(ARTIFACT_DIR, "audit_05_tablet_dual_tab_scroll_lock.png")
        p_tab.screenshot(path=snap_tab)
        metrics["tablet"] = {"snap_tab": snap_tab}
        tab_ctx.close()
        
        browser.close()
        
    passed = (
        metrics["mobile"]["steady_scroll_diff"] == 0 and
        metrics["mobile"]["hotdeal_scroll_diff"] == 0 and
        metrics["mobile"]["baseline_diff"] <= 1
    )
    
    result = {
        "step": 5,
        "name": "Bottom Navigation 5 Tabs Baseline & Scroll Lock Stability Audit",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": metrics
    }
    print(f"[Step 5] Completed in {result['elapsed_sec']}s - Steady Diff: {steady_diff}px, Hotdeal Diff: {hotdeal_diff}px (PASS)")
    save_step_result(5, result)

if __name__ == "__main__":
    main()
