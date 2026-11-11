# -*- coding: utf-8 -*-
"""
Step 3: 3-Tier Scraping Pipeline & Ottogi 24 Missing Product Link Prevention & WAF Bypass Audit
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, save_step_result

def main():
    t_start = time.time()
    print(">>> [Step 3] Auditing 3-Tier Engine & Ottogi Missing Link Prevention...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers="block")
        page = ctx.new_page()
        page.set_default_timeout(10000)
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        
        page.fill("#searchInput", "오뚜기 맛있는 오뚜기밥 210g 24개")
        page.press("#searchInput", "Enter")
        page.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=10000)
        page.wait_for_timeout(400)
        
        ottogi_metrics = page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll("#priceComparisonGrid .rank-card"));
            const links = Array.from(document.querySelectorAll("#priceComparisonGrid .rank-card a[target='_blank']")).map(a => a.href);
            const hasDeadLink = links.some(l => l.includes("4915664157"));
            const hasWafBlock = document.body.innerText.includes("쇼핑 서비스 접속이 일시적으로 제한되었습니다");
            const hasMissingProduct = document.body.innerText.includes("상품이 존재하지 않습니다");
            return {
                cardCount: cards.length,
                linksCount: links.length,
                hasDeadLink: hasDeadLink,
                hasWafBlock: hasWafBlock,
                hasMissingProduct: hasMissingProduct
            };
        }''')
        
        snap_path = os.path.join(ARTIFACT_DIR, "audit_03_ottogi_3tier_verified.png")
        page.screenshot(path=snap_path)
        ottogi_metrics["screenshot"] = snap_path
        
        ctx.close()
        browser.close()
        
    passed = (
        ottogi_metrics["cardCount"] > 0 and
        not ottogi_metrics["hasDeadLink"] and
        not ottogi_metrics["hasWafBlock"] and
        not ottogi_metrics["hasMissingProduct"]
    )
    
    result = {
        "step": 3,
        "name": "3-Tier Engine & Ottogi Missing Link Prevention & WAF Bypass",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": ottogi_metrics
    }
    print(f"[Step 3] Completed in {result['elapsed_sec']}s - DeadLink: {ottogi_metrics['hasDeadLink']}, Status: {result['status']}")
    save_step_result(3, result)

if __name__ == "__main__":
    main()
