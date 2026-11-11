# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright
from PIL import Image

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
PROD_URL = "https://pricetrace-nu.vercel.app/"

async def capture_live():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-remote-fonts']
        )
        ctx = await browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            service_workers="block",
            device_scale_factor=2
        )
        page = await ctx.new_page()
        await page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page.goto(PROD_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(800)
        
        # Remove splash if present
        await page.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            if (splash) splash.remove();
        }''')
        await page.wait_for_timeout(300)
        
        # Capture full and dock crop
        live_full = os.path.join(ARTIFACT_DIR, "vercel_live_production_mobile.png")
        await page.screenshot(path=live_full)
        
        im = Image.open(live_full)
        dock_crop = im.crop((0, im.height - int(110 * 2), im.width, im.height))
        live_crop = os.path.join(ARTIFACT_DIR, "vercel_live_production_dock_crop.png")
        dock_crop.save(live_crop)
        print("Live production screenshot captured successfully:", live_crop)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_live())
