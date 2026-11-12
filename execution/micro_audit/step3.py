# -*- coding: utf-8 -*-
"""
Step 3: 3-Tier Scraping Pipeline, Live Naver Search Engine Audit & Ottogi 24 Dead-Link Prevention
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, PC_UA,
    save_step_result, create_sentinel, collect_broken_images, sentinel_summary, safe_screenshot
)


def main():
    t_start = time.time()
    print(">>> [Step 3] Auditing 3-Tier Engine & Ottogi 24 Missing Link Prevention...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, user_agent=PC_UA, service_workers="block")
        page = ctx.new_page()
        page.set_default_timeout(12000)
        s = create_sentinel(page)

        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(400)

        page.evaluate("const g = document.getElementById('priceComparisonGrid'); if (g) g.innerHTML = '';")
        page.fill("#searchInput", "오뚜기 맛있는 오뚜기밥 210g 24개")

        api_meta = {"status": 0, "source": "unknown", "item_count": 0}
        with page.expect_response(lambda r: "/api/search" in r.url, timeout=12000) as resp_info:
            page.press("#searchInput", "Enter")
        resp = resp_info.value
        api_meta["status"] = resp.status
        try:
            rj = resp.json()
            api_meta["source"] = "naver_live" if rj.get("is_live") else "preset_fallback"
            api_meta["item_count"] = rj.get("item_count") or len(rj.get("top_items") or [])
        except Exception:
            pass

        page.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=10000)
        page.wait_for_timeout(300)

        ottogi_metrics = page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll("#priceComparisonGrid .rank-card"));
            const links = Array.from(document.querySelectorAll("#priceComparisonGrid .rank-card a[target='_blank']")).map(a => a.href);
            const titles = cards.map(c => c.querySelector("h4")?.innerText?.trim() || "");
            const hasDeadLink = links.some(l => l.includes("4915664157"));
            const hasWafBlock = document.body.innerText.includes("쇼핑 서비스 접속이 일시적으로 제한되었습니다");
            const hasMissingProduct = document.body.innerText.includes("상품이 존재하지 않습니다");
            return {
                cardCount: cards.length,
                links: links,
                titles: titles,
                hasDeadLink: hasDeadLink,
                hasWafBlock: hasWafBlock,
                hasMissingProduct: hasMissingProduct
            };
        }''')

        collect_broken_images(page, s)
        snap_path = os.path.join(ARTIFACT_DIR, "audit_03_ottogi_3tier_verified.png")
        safe_screenshot(page, snap_path)
        ottogi_metrics["screenshot"] = snap_path
        ottogi_metrics["api_meta"] = api_meta

        # 실제 1위 타겟 링크 접속 무결성 확인 (WAF / 존재하지 않는 상품 여부)
        target_check = {"tested_url": "", "http_status": 0, "waf_blocked": False, "missing_product": False, "title": ""}
        if ottogi_metrics["links"]:
            target_url = ottogi_metrics["links"][0]
            target_check["tested_url"] = target_url
            t_page = ctx.new_page()
            t_page.set_default_timeout(8000)
            try:
                t_resp = t_page.goto(target_url, wait_until="domcontentloaded")
                t_page.wait_for_timeout(800)
                body_txt = t_page.inner_text("body")
                target_check["http_status"] = t_resp.status if t_resp else 0
                target_check["waf_blocked"] = "쇼핑 서비스 접속이 일시적으로 제한되었습니다" in body_txt
                target_check["missing_product"] = "상품이 존재하지 않습니다" in body_txt
                target_check["title"] = t_page.title()
            except Exception as e:
                target_check["error"] = str(e)
            finally:
                t_page.close()

        ottogi_metrics["target_link_live_check"] = target_check
        ctx.close()
        browser.close()

    s_sum = sentinel_summary(s)
    passed = (
        api_meta["status"] == 200
        and ottogi_metrics["cardCount"] >= 3
        and not ottogi_metrics["hasDeadLink"]
        and not ottogi_metrics["hasWafBlock"]
        and not ottogi_metrics["hasMissingProduct"]
        and not target_check.get("waf_blocked", False)
        and not target_check.get("missing_product", False)
        and s_sum["total_errors"] == 0
    )

    result = {
        "step": 3,
        "name": "3-Tier Engine & Ottogi Missing Link Prevention & WAF Bypass",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": s_sum,
        "metrics": ottogi_metrics
    }
    print(f"[Step 3] {result['elapsed_sec']}s | Cards={ottogi_metrics['cardCount']} | DeadLink={ottogi_metrics['hasDeadLink']} | TargetHTTP={target_check['http_status']} | Errors={s_sum['total_errors']} | Status={result['status']}")
    save_step_result(3, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
