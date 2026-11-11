# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright
from PIL import Image

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
PROD_URL = "https://pricetrace-nu.vercel.app/"

async def verify_prod():
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
        await page.goto(PROD_URL, wait_until="networkidle")
        await page.wait_for_timeout(600)
        
        await page.evaluate('''() => {
            const s = document.getElementById("appSplashScreen");
            if (s) s.remove();
        }''')
        await page.wait_for_timeout(300)

        meas = await page.evaluate('''() => {
            const h = document.querySelector("header");
            const hero = document.getElementById("welcomeView")?.firstElementChild;
            const ptr = document.getElementById("ptrIndicator");
            const ptrStyle = ptr ? window.getComputedStyle(ptr) : null;
            return {
                headerBottom: Math.round(h.getBoundingClientRect().bottom),
                heroTop: hero ? Math.round(hero.getBoundingClientRect().top) : null,
                gap: hero ? Math.round(hero.getBoundingClientRect().top - h.getBoundingClientRect().bottom) : null,
                ptrDisplay: ptrStyle ? ptrStyle.display : null,
                ptrIsVisible: ptr ? (ptr.offsetWidth > 0 && ptr.offsetHeight > 0 && ptrStyle.display !== 'none') : false
            };
        }''')
        print("Live Production Measurements:", meas)

        full_p = os.path.join(ARTIFACT_DIR, "vercel_live_fixed_mobile.png")
        await page.screenshot(path=full_p)

        im = Image.open(full_p)
        top_crop = im.crop((0, 0, im.width, 1050))
        crop_p = os.path.join(ARTIFACT_DIR, "vercel_live_fixed_top_crop.png")
        top_crop.save(crop_p)
        print("Live Top Crop Saved:", crop_p)

        await b.close()

if __name__ == "__main__":
    asyncio.run(verify_prod())
