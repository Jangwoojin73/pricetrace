# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright

PROD_URL = "https://pricetrace-nu.vercel.app/"
ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

async def test_live_touch():
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
            device_scale_factor=2
        )
        page = await ctx.new_page()
        await page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page.goto(PROD_URL, wait_until="networkidle")
        await page.wait_for_timeout(800)

        # 1. Real touch drag down on live Vercel
        touch_res = await page.evaluate('''() => {
            const main = document.getElementById("mainContent");
            const t0 = new Touch({ identifier: 1, target: main, clientX: 200, clientY: 200 });
            window.dispatchEvent(new TouchEvent("touchstart", { touches: [t0], targetTouches: [t0], changedTouches: [t0], bubbles: true, cancelable: true }));

            const t1 = new Touch({ identifier: 1, target: main, clientX: 200, clientY: 380 });
            window.dispatchEvent(new TouchEvent("touchmove", { touches: [t1], targetTouches: [t1], changedTouches: [t1], bubbles: true, cancelable: true }));

            return {
                transformAfterTouchMove: main.style.transform,
                ptrText: document.getElementById("ptrText")?.textContent,
                ptrDisplay: window.getComputedStyle(document.getElementById("ptrIndicator")).display
            };
        }''')
        print("Vercel Live Real Touch Drag Result:", touch_res)

        # Capture live pulling screenshot
        p_live_pull = os.path.join(ARTIFACT_DIR, "vercel_live_real_touch_pulled.png")
        await page.screenshot(path=p_live_pull)

        # 2. Real touchend
        end_res = await page.evaluate('''() => {
            const main = document.getElementById("mainContent");
            const tEnd = new Touch({ identifier: 1, target: main, clientX: 200, clientY: 380 });
            window.dispatchEvent(new TouchEvent("touchend", { touches: [], targetTouches: [], changedTouches: [tEnd], bubbles: true, cancelable: true }));

            return {
                transformOnEnd: main.style.transform,
                ptrText: document.getElementById("ptrText")?.textContent,
                spinnerVisible: !document.getElementById("ptrSpinner")?.classList.contains("hidden")
            };
        }''')
        print("Vercel Live Real Touch End Result:", end_res)

        p_live_refresh = os.path.join(ARTIFACT_DIR, "vercel_live_real_touch_refreshing.png")
        await page.screenshot(path=p_live_refresh)

        await b.close()

if __name__ == "__main__":
    asyncio.run(test_live_touch())
