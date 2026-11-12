# -*- coding: utf-8 -*-
"""
Step 2: 32 Items Dual Tabs (16+16) & 5 Representative Items Search Sorting Audit
+ Real Naver Live Search API Source Verification
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import urllib.parse
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, PC_UA,
    save_step_result, create_sentinel, collect_broken_images, sentinel_summary, safe_screenshot
)

ITEMS = ["농심 신라면 20개", "CJ 햇반 24개", "커클랜드 휴지 30롤", "사과", "새우"]


def main():
    t_start = time.time()
    print(">>> [Step 2] Auditing Dual Tabs (16+16) & 5 Items Real Search...")
    metrics = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, user_agent=PC_UA, service_workers="block")
        page = ctx.new_page()
        page.set_default_timeout(12000)
        s = create_sentinel(page)

        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=8000)
        page.wait_for_timeout(800)  # /api/trending 로드 완료 대기

        # 2-1. Dual Tabs (16 + 16) Real Verification
        page.click("#tabSteadyBtn")
        page.wait_for_timeout(350)
        try:
            page.wait_for_function('''() => {
                const imgs = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card img"));
                return imgs.length === 16 && imgs.every(img => img.complete);
            }''', timeout=3000)
        except Exception:
            pass
        steady_eval = page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card"));
            const imgs = cards.map(c => c.querySelector("img")).filter(Boolean);
            const validThumbs = imgs.filter(img => img.complete && img.naturalWidth > 0).length;
            return { count: cards.length, totalImgs: imgs.length, validThumbs };
        }''')
        collect_broken_images(page, s)

        page.click("#tabTrendingBtn")
        page.wait_for_timeout(350)  # setTimeout(150ms) + fade 대기
        try:
            page.wait_for_function('''() => {
                const imgs = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card img"));
                return imgs.length === 16 && imgs.every(img => img.complete);
            }''', timeout=3000)
        except Exception:
            pass
        hotdeal_eval = page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card"));
            const imgs = cards.map(c => c.querySelector("img")).filter(Boolean);
            const validThumbs = imgs.filter(img => img.complete && img.naturalWidth > 0).length;
            const hasPriceLabels = cards.every(c => {
                const txt = c.innerText;
                return txt.includes("원") || txt.includes("확인");
            });
            return { count: cards.length, totalImgs: imgs.length, validThumbs, hasPriceLabels };
        }''')
        collect_broken_images(page, s)

        snap_tabs = os.path.join(ARTIFACT_DIR, "audit_02_dual_tabs_overview.png")
        safe_screenshot(page, snap_tabs)

        metrics["dual_tabs"] = {
            "steady_count": steady_eval["count"],
            "steady_valid_thumbs": steady_eval["validThumbs"],
            "hotdeal_count": hotdeal_eval["count"],
            "hotdeal_valid_thumbs": hotdeal_eval["validThumbs"],
            "hotdeal_price_labels_valid": hotdeal_eval["hasPriceLabels"],
            "screenshot": snap_tabs
        }

        # 2-2. 5 Representative Items Search & Ascending Sort
        rep_results = {}
        all_sorted = True
        all_3_cards = True
        apple_pure = True

        for item in ITEMS:
            clean_name = item.split()[0]
            # 이전 그리드 비우고 실제 API 응답 대기 (거짓/이전 카드 판독 방지)
            page.evaluate("const g = document.getElementById('priceComparisonGrid'); if (g) g.innerHTML = '';")
            page.fill("#searchInput", item)

            api_source = "unknown"
            api_status = 0
            with page.expect_response(lambda r: "/api/search" in r.url, timeout=12000) as resp_info:
                page.press("#searchInput", "Enter")
            resp = resp_info.value
            api_status = resp.status
            try:
                api_json = resp.json()
                api_source = "naver_live" if api_json.get("is_live") else "preset_fallback"
            except Exception:
                pass

            page.wait_for_selector("#priceComparisonGrid .rank-card", timeout=8000)
            page.wait_for_timeout(250)

            res = page.evaluate('''() => {
                const cards = Array.from(document.querySelectorAll("#priceComparisonGrid .rank-card"));
                const prices = cards.map(c => {
                    const pEl = c.querySelector("span.text-2xl.font-black");
                    return pEl ? parseInt(pEl.innerText.replace(/[^0-9]/g, ""), 10) || 0 : 0;
                }).filter(p => p > 0);
                const titles = cards.map(c => c.querySelector("h4")?.innerText?.trim() || "");
                return { count: cards.length, prices, titles };
            }''')

            prices = res["prices"]
            is_asc = len(prices) >= 3 and all(prices[i] <= prices[i + 1] for i in range(len(prices) - 1))
            if not is_asc:
                all_sorted = False
            if res["count"] < 3:
                all_3_cards = False

            noise_detected = False
            noise_found_list = []
            if item == "사과":
                noise_words = ["사과대추", "미니사과", "풋사과", "사과즙", "대추사과"]
                for t in res["titles"]:
                    for nw in noise_words:
                        if nw in t:
                            noise_detected = True
                            noise_found_list.append(t)
                apple_pure = not noise_detected

            snap_item = os.path.join(ARTIFACT_DIR, f"audit_02_search_results_{clean_name}.png")
            safe_screenshot(page, snap_item)

            rep_results[clean_name] = {
                "query": item,
                "apiStatus": api_status,
                "apiSource": api_source,
                "cardCount": res["count"],
                "prices": prices,
                "titles": res["titles"],
                "isAscending": is_asc,
                "noiseDetected": noise_detected,
                "noiseFound": noise_found_list,
                "screenshot": snap_item
            }

        collect_broken_images(page, s)
        metrics["representative_items"] = rep_results
        ctx.close()
        browser.close()

    s_sum = sentinel_summary(s)
    passed = (
        metrics["dual_tabs"]["steady_count"] == 16
        and metrics["dual_tabs"]["hotdeal_count"] == 16
        and all_3_cards
        and all_sorted
        and apple_pure
        and s_sum["total_errors"] == 0
    )

    result = {
        "step": 2,
        "name": "32 Items Dual Tabs & 5 Representative Items Search Sorting Audit",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": s_sum,
        "metrics": metrics
    }
    print(f"[Step 2] {result['elapsed_sec']}s | Dual={steady_eval['count']}+{hotdeal_eval['count']} | AllSorted={all_sorted} | ApplePure={apple_pure} | Errors={s_sum['total_errors']} | Status={result['status']}")
    save_step_result(2, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
