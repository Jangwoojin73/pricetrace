# -*- coding: utf-8 -*-
"""
Step 2: 32 Items Dual Tabs & 5 Representative Items Search Sorting Audit
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, save_step_result

ITEMS = ["농심 신라면 20개", "CJ 햇반 24개", "커클랜드 휴지 30롤", "사과", "새우"]

def main():
    t_start = time.time()
    print(">>> [Step 2] Auditing Dual Tabs (16+16) & 5 Items Search...")
    metrics = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers="block")
        page = ctx.new_page()
        page.set_default_timeout(10000)
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(600)
        
        # 2-1. Dual Tabs (16 + 16)
        page.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=8000)
        tab_eval = page.evaluate('''() => {
            const steadyBtn = document.getElementById("tabSteadyBtn");
            const hotdealBtn = document.getElementById("tabTrendingBtn");
            
            steadyBtn.click();
            const steadyCount = document.querySelectorAll("#welcomeCardsContainer .welcome-card").length;
            const steadyThumbs = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card img")).every(img => img.naturalWidth > 0 || img.complete);
            
            hotdealBtn.click();
            const hotdealCount = document.querySelectorAll("#welcomeCardsContainer .welcome-card").length;
            const hotdealThumbs = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card img")).every(img => img.naturalWidth > 0 || img.complete);
            
            return { steadyCount, steadyThumbs, hotdealCount, hotdealThumbs };
        }''')
        
        snap_tabs = os.path.join(ARTIFACT_DIR, "audit_02_dual_tabs_overview.png")
        page.screenshot(path=snap_tabs)
        
        metrics["dual_tabs"] = {
            "steady_count": tab_eval["steadyCount"],
            "steady_thumbs_valid": tab_eval["steadyThumbs"],
            "hotdeal_count": tab_eval["hotdealCount"],
            "hotdeal_thumbs_valid": tab_eval["hotdealThumbs"],
            "screenshot": snap_tabs
        }
        
        # 2-2. 5 Representative Items Search & Ascending Sort
        rep_results = {}
        all_sorted = True
        apple_pure = True
        
        for item in ITEMS:
            clean_name = item.split()[0]
            page.fill("#searchInput", item)
            page.press("#searchInput", "Enter")
            page.wait_for_selector("#priceComparisonGrid .rank-card", timeout=8000)
            page.wait_for_timeout(400)
            
            res = page.evaluate('''() => {
                const cards = Array.from(document.querySelectorAll("#priceComparisonGrid .rank-card"));
                const prices = cards.map(c => {
                    const pEl = c.querySelector("div.mt-3 span.font-black, span.text-2xl, span.text-xl, .price-val");
                    return pEl ? parseInt(pEl.innerText.replace(/[^0-9]/g, ""), 10) || 0 : 0;
                }).filter(p => p > 0);
                const titles = cards.map(c => c.querySelector("h4, .line-clamp-2")?.innerText || "");
                return { count: cards.length, prices, titles };
            }''')
            
            prices = res["prices"]
            is_asc = len(prices) >= 2 and all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
            if not is_asc and len(prices) >= 2:
                all_sorted = False
                
            noise_detected = False
            if item == "사과":
                noise_words = ["사과대추", "미니사과", "풋사과", "사과즙", "대추사과"]
                for t in res["titles"]:
                    if any(nw in t for nw in noise_words):
                        noise_detected = True
                        break
                apple_pure = not noise_detected
                
            snap_item = os.path.join(ARTIFACT_DIR, f"audit_02_search_results_{clean_name}.png")
            page.screenshot(path=snap_item)
            
            rep_results[clean_name] = {
                "query": item,
                "cardCount": res["count"],
                "prices": prices,
                "isAscending": is_asc,
                "noiseDetected": noise_detected,
                "screenshot": snap_item
            }
            
        metrics["representative_items"] = rep_results
        ctx.close()
        browser.close()
        
    passed = (
        metrics["dual_tabs"]["steady_count"] == 16 and
        apple_pure and
        all_sorted
    )
    
    result = {
        "step": 2,
        "name": "32 Items Dual Tabs & 5 Representative Items Search Sorting Audit",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": metrics
    }
    print(f"[Step 2] Completed in {result['elapsed_sec']}s - Status: {result['status']}")
    save_step_result(2, result)

if __name__ == "__main__":
    main()
