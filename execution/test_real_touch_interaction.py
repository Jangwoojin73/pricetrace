# -*- coding: utf-8 -*-
"""
Verify REAL touch & pointer drag interaction on localhost:8080
WITHOUT manipulating DOM styles manually!
"""
import asyncio, os
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8080"

async def test_touch():
    async with async_playwright() as p:
        b = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-remote-fonts']
        )
        ctx = await b.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        page = await ctx.new_page()
        await page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(600)
        
        # Check if setupPullToRefresh is registered and variables exist
        check = await page.evaluate('''() => {
            const main = document.getElementById("mainContent");
            const ptr = document.getElementById("ptrIndicator");
            return {
                mainExists: !!main,
                ptrExists: !!ptr,
                initialTransform: main.style.transform || "none"
            };
        }''')
        print("Initial state:", check)

        # Dispatch REAL touch events via browser
        res = await page.evaluate('''() => {
            const main = document.getElementById("mainContent");
            const ptr = document.getElementById("ptrIndicator");

            // 1. touchstart at (200, 250)
            const t0 = new Touch({ identifier: 1, target: main, clientX: 200, clientY: 250 });
            window.dispatchEvent(new TouchEvent("touchstart", { touches: [t0], targetTouches: [t0], changedTouches: [t0], bubbles: true, cancelable: true }));

            // 2. touchmove down to (200, 380) (diffY = 130px)
            const t1 = new Touch({ identifier: 1, target: main, clientX: 200, clientY: 380 });
            window.dispatchEvent(new TouchEvent("touchmove", { touches: [t1], targetTouches: [t1], changedTouches: [t1], bubbles: true, cancelable: true }));

            return {
                mainTransformAfterMove: main.style.transform,
                ptrDisplay: window.getComputedStyle(ptr).display,
                ptrOpacity: window.getComputedStyle(ptr).opacity,
                ptrText: document.getElementById("ptrText")?.textContent
            };
        }''')
        print("Real touch event result:", res)

        # 3. touchend
        end_res = await page.evaluate('''() => {
            const main = document.getElementById("mainContent");
            const ptr = document.getElementById("ptrIndicator");

            // touchend
            const tEnd = new Touch({ identifier: 1, target: main, clientX: 200, clientY: 380 });
            window.dispatchEvent(new TouchEvent("touchend", { touches: [], targetTouches: [], changedTouches: [tEnd], bubbles: true, cancelable: true }));

            return {
                mainTransformOnEnd: main.style.transform,
                ptrTextOnEnd: document.getElementById("ptrText")?.textContent,
                spinnerHidden: document.getElementById("ptrSpinner")?.classList.contains("hidden")
            };
        }''')
        print("Real touchend result:", end_res)

        await b.close()

if __name__ == "__main__":
    asyncio.run(test_touch())
