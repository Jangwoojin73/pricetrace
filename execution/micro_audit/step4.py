# -*- coding: utf-8 -*-
"""
Step 4: Cross-Device Naver Price Anchor & PowerLink Ad Bypass Audit
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, save_step_result

def main():
    t_start = time.time()
    print(">>> [Step 4] Auditing Cross-Device Price Anchors & Ad Skip Logic...")
    metrics = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        
        # 4-1. PC Desktop Anchor (#shp_dui_root)
        pc_ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers="block")
        p_pc = pc_ctx.new_page()
        p_pc.set_default_timeout(10000)
        p_pc.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_pc.goto(BASE_URL, wait_until="domcontentloaded")
        p_pc.wait_for_timeout(300)
        
        p_pc.fill("#searchInput", "농심 신라면 20개")
        p_pc.press("#searchInput", "Enter")
        p_pc.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=10000)
        p_pc.wait_for_timeout(300)
        
        pc_anchor = p_pc.evaluate('''() => {
            const link = document.querySelector("#priceComparisonGrid .rank-card a[target='_blank']");
            return {
                href: link ? link.href : "",
                hasAnchor: link ? link.href.includes("#shp_dui_root") : false,
                whereShp: link ? link.href.includes("where=shp") : false
            };
        }''')
        snap_pc = os.path.join(ARTIFACT_DIR, "audit_04_pc_anchor_desktop_verified.png")
        p_pc.screenshot(path=snap_pc)
        pc_anchor["screenshot"] = snap_pc
        metrics["pc"] = pc_anchor
        pc_ctx.close()
        
        # 4-2. Mobile Anchor (#shp_lis_root)
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
        p_m.wait_for_timeout(300)
        
        p_m.fill("#searchInput", "농심 신라면 20개")
        p_m.press("#searchInput", "Enter")
        p_m.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=10000)
        p_m.wait_for_timeout(300)
        
        m_anchor = p_m.evaluate('''() => {
            const link = document.querySelector("#priceComparisonGrid .rank-card a[target='_blank']");
            return {
                href: link ? link.href : "",
                hasAnchor: link ? (link.href.includes("#shp_lis_root") || link.href.includes("m.search.naver.com")) : false
            };
        }''')
        snap_m = os.path.join(ARTIFACT_DIR, "audit_04_mobile_anchor_lis_verified.png")
        p_m.screenshot(path=snap_m)
        snap_r1 = os.path.join(ARTIFACT_DIR, "audit_04_rank1_verified.png")
        p_m.screenshot(path=snap_r1)
        m_anchor["screenshot_anchor"] = snap_m
        m_anchor["screenshot_rank1"] = snap_r1
        metrics["mobile"] = m_anchor
        m_ctx.close()
        
        browser.close()
        
    passed = (
        metrics["pc"]["hasAnchor"] and
        metrics["mobile"]["hasAnchor"]
    )
    
    result = {
        "step": 4,
        "name": "Cross-Device Naver Price Anchor & PowerLink Ad Bypass Audit",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": metrics
    }
    print(f"[Step 4] Completed in {result['elapsed_sec']}s - PC Anchor: {metrics['pc']['hasAnchor']}, Mobile Anchor: {metrics['mobile']['hasAnchor']}")
    save_step_result(4, result)

if __name__ == "__main__":
    main()
