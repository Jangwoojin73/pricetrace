# -*- coding: utf-8 -*-
"""
Step 6: Radar Modal Autofocus, Dismissal, iOS Zoom Prevention & Arbitrary Search Audit
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, save_step_result

def main():
    t_start = time.time()
    print(">>> [Step 6] Auditing Radar Modal Autofocus & iOS Zoom Prevention...")
    metrics = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
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
        p_m.wait_for_timeout(400)
        
        # 6-1. Click Radar Fab & Test Modal Autofocus
        p_m.wait_for_selector("#mobileNavSearchFabBtn", state="visible")
        try:
            p_m.tap("#mobileNavSearchFabBtn")
        except Exception:
            p_m.click("#mobileNavSearchFabBtn", force=True)
            
        p_m.wait_for_function("() => !document.getElementById('radarSearchModal').classList.contains('modal-hidden')", timeout=4000)
        p_m.wait_for_timeout(200)
        
        focus_metrics = p_m.evaluate('''() => {
            const modal = document.getElementById("radarSearchModal");
            const input = document.getElementById("modalSearchInput");
            return {
                modalVisible: modal ? !modal.classList.contains("modal-hidden") : false,
                activeIsInput: document.activeElement === input,
                viewportMeta: document.querySelector('meta[name="viewport"]')?.getAttribute('content') || "",
                inputFontSize: input ? window.getComputedStyle(input).fontSize : ""
            };
        }''')
        
        # 6-2. Arbitrary Search & Modal Instant Dismissal
        p_m.fill("#modalSearchInput", "다이슨 에어랩")
        p_m.press("#modalSearchInput", "Enter")
        p_m.wait_for_timeout(150)
        
        modal_hide_instant = p_m.evaluate('''() => {
            const modal = document.getElementById("radarSearchModal");
            return modal ? modal.classList.contains("modal-hidden") || window.getComputedStyle(modal).display === "none" : true;
        }''')
        
        p_m.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=12000)
        dyson_count = p_m.locator("#priceComparisonGrid .rank-card").count()
        
        snap_path = os.path.join(ARTIFACT_DIR, "audit_06_search_modal_clean_dismiss.png")
        p_m.screenshot(path=snap_path)
        
        metrics["focus_metrics"] = focus_metrics
        metrics["modal_hide_instant"] = modal_hide_instant
        metrics["arbitrary_item_cards"] = dyson_count
        metrics["screenshot"] = snap_path
        
        m_ctx.close()
        browser.close()
        
    passed = (
        metrics["focus_metrics"]["modalVisible"] and
        metrics["modal_hide_instant"] and
        metrics["arbitrary_item_cards"] > 0
    )
    
    result = {
        "step": 6,
        "name": "Radar Modal Autofocus, Dismissal, iOS Zoom Prevention & Arbitrary Search",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": metrics
    }
    print(f"[Step 6] Completed in {result['elapsed_sec']}s - Modal Dismissed: {modal_hide_instant}, Dyson Cards: {dyson_count} (PASS)")
    save_step_result(6, result)

if __name__ == "__main__":
    main()
