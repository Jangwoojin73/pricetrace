# -*- coding: utf-8 -*-
import sys
import os
import urllib.parse
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def verify_ui_searches():
    test_searches = [
        ("나이키 운동화", "verify_search_nike.png"),
        ("맥북 에어 M3", "verify_search_macbook.png"),
        ("27인치 모니터", "verify_search_monitor.png"),
        ("아이폰 15 케이스", "verify_search_iphone_case.png"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Disable splash
        page.add_init_script("""
            sessionStorage.setItem('pricetrace_splash_seen', 'true');
        """)

        for query, shot_name in test_searches:
            url = f"http://127.0.0.1:8080/?q={urllib.parse.quote(query)}"
            print(f"\n[UI Test] Navigating to: {url}")
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=12000)
            page.wait_for_timeout(1500)

            # Check prices
            hero_price = page.evaluate('() => document.querySelector("#lowestPriceDisplay") ? document.querySelector("#lowestPriceDisplay").innerText.trim() : "N/A"')
            hero_title = page.evaluate('() => document.querySelector("#productTitle") ? document.querySelector("#productTitle").innerText.trim() : "N/A"')
            
            rank_cards = page.evaluate('''() => {
                const cards = document.querySelectorAll(".rank-card");
                return Array.from(cards).map((c, i) => {
                    const titleEl = c.querySelector("h4");
                    const priceEl = c.querySelector(".text-2xl.font-black");
                    const mallEl = c.querySelector(".truncate");
                    return {
                        rank: i + 1,
                        title: titleEl ? titleEl.innerText.trim() : "",
                        price: priceEl ? priceEl.innerText.trim() : "",
                        mall: mallEl ? mallEl.innerText.trim() : ""
                    };
                });
            }''')

            print(f" Query: '{query}'")
            print(f" Hero Title: '{hero_title}'")
            print(f" Hero Lowest Price: {hero_price}원")
            print(f" Rank Cards ({len(rank_cards)}):")
            for r in rank_cards:
                print(f"   {r['rank']}위: {r['price']}원 | {r['title'][:40]} | {r['mall']}")

            # Save screenshot
            shot_path = os.path.join(ARTIFACT_DIR, shot_name)
            page.screenshot(path=shot_path, full_page=False)
            print(f" Screenshot saved: {shot_path}")

        browser.close()

if __name__ == "__main__":
    verify_ui_searches()
