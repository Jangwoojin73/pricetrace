import asyncio
import os
from playwright.async_api import async_playwright
from PIL import Image

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # iPhone 15 Pro viewport
        context = await browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2
        )
        page = await context.new_page()
        
        # Bypass splash
        await page.add_init_script("sessionStorage.setItem('pt_splash_seen', 'true');")
        await page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Measurements
        measurements = await page.evaluate('''() => {
            const banner = document.getElementById('topLiveBanner');
            const badge = banner ? banner.querySelector('span.rounded-full') : null;
            const header = document.querySelector('header');
            
            const bStyle = banner ? window.getComputedStyle(banner) : null;
            const bRect = banner ? banner.getBoundingClientRect() : null;
            const badgeRect = badge ? badge.getBoundingClientRect() : null;
            const hRect = header ? header.getBoundingClientRect() : null;
            
            return {
                paddingTop: bStyle ? bStyle.paddingTop : null,
                paddingBottom: bStyle ? bStyle.paddingBottom : null,
                bannerTop: bRect ? bRect.top : null,
                bannerHeight: bRect ? bRect.height : null,
                badgeTop: badgeRect ? badgeRect.top : null,
                badgeHeight: badgeRect ? badgeRect.height : null,
                headerHeight: hRect ? hRect.height : null
            };
        }''')
        
        print("DOM Measurements:", measurements)
        
        # 1. Full screenshot
        full_path = os.path.join(ARTIFACT_DIR, "capture_applied_header_up10px.png")
        await page.screenshot(path=full_path)
        print(f"Saved full screenshot: {full_path}")
        
        # 2. Crop header area (width: 393*2=786, height: 260*2=520)
        im = Image.open(full_path)
        # crop top 0 to 260pt (scale factor 2 -> 520px)
        crop_im = im.crop((0, 0, im.width, int(260 * 2)))
        crop_path = os.path.join(ARTIFACT_DIR, "verify_header_up10px_crop.png")
        crop_im.save(crop_path)
        print(f"Saved header crop: {crop_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
