# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright
from PIL import Image

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"

async def main():
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
            service_workers="block",
            device_scale_factor=2
        )
        page = await ctx.new_page()
        await page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(600)
        
        # Remove splash
        await page.evaluate('''() => {
            const s = document.getElementById("appSplashScreen");
            if (s) s.remove();
        }''')
        await page.wait_for_timeout(300)

        # 1. Measure Clean Default State
        meas = await page.evaluate('''() => {
            const h = document.querySelector("header");
            const main = document.getElementById("mainContent");
            const ptr = document.getElementById("ptrIndicator");
            const welcome = document.getElementById("welcomeView");
            const hero = welcome ? welcome.firstElementChild : null;

            const hRect = h ? h.getBoundingClientRect() : null;
            const heroRect = hero ? hero.getBoundingClientRect() : null;
            const ptrStyle = ptr ? window.getComputedStyle(ptr) : null;

            return {
                headerBottom: hRect ? Math.round(hRect.bottom) : null,
                heroTop: heroRect ? Math.round(heroRect.top) : null,
                gapBetweenHeaderAndHero: (hRect && heroRect) ? Math.round(heroRect.top - hRect.bottom) : null,
                ptrDisplay: ptrStyle ? ptrStyle.display : null,
                ptrVisibility: ptrStyle ? ptrStyle.visibility : null,
                ptrOpacity: ptrStyle ? ptrStyle.opacity : null,
                ptrIsVisible: ptr ? (ptr.offsetWidth > 0 && ptr.offsetHeight > 0 && ptrStyle.display !== 'none') : false
            };
        }''')
        print("Default State Measurements:", meas)

        # 2. Capture Clean Main Screen Screenshot
        clean_full_path = os.path.join(ARTIFACT_DIR, "mobile_main_clean_fixed.png")
        await page.screenshot(path=clean_full_path)
        print("Clean screenshot saved:", clean_full_path)

        # 3. Simulate touch pull down
        # Start touch at center
        await page.touchscreen.tap(196, 250)
        # Mouse down & drag down
        await page.mouse.move(196, 250)
        await page.mouse.down()
        await page.mouse.move(196, 420, steps=10)
        await page.wait_for_timeout(300)

        pull_meas = await page.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const ptrStyle = ptr ? window.getComputedStyle(ptr) : null;
            const ptrRect = ptr ? ptr.getBoundingClientRect() : null;
            const main = document.getElementById("mainContent");
            return {
                mainTransform: main ? main.style.transform : null,
                ptrDisplay: ptrStyle ? ptrStyle.display : null,
                ptrOpacity: ptrStyle ? ptrStyle.opacity : null,
                ptrTop: ptrRect ? Math.round(ptrRect.top) : null
            };
        }''')
        print("Pulling State Measurements:", pull_meas)

        pull_path = os.path.join(ARTIFACT_DIR, "mobile_main_pulling_state.png")
        await page.screenshot(path=pull_path)

        # Release mouse
        await page.mouse.up()
        await page.wait_for_timeout(1000)

        # After release measurements
        after_meas = await page.evaluate('''() => {
            const h = document.querySelector("header");
            const hero = document.getElementById("welcomeView")?.firstElementChild;
            const ptr = document.getElementById("ptrIndicator");
            const ptrStyle = ptr ? window.getComputedStyle(ptr) : null;
            return {
                gapAfterRelease: hero ? Math.round(hero.getBoundingClientRect().top - h.getBoundingClientRect().bottom) : null,
                ptrDisplay: ptrStyle ? ptrStyle.display : null
            };
        }''')
        print("After Release Measurements:", after_meas)

        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
