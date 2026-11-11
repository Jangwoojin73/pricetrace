import asyncio
import os
from playwright.async_api import async_playwright
from PIL import Image

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. iPad Pro 11 Portrait (834 x 1194)
        context_portrait = await browser.new_context(
            viewport={"width": 834, "height": 1194},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2
        )
        page_p = await context_portrait.new_page()
        await page_p.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page_p.goto("http://127.0.0.1:8080", wait_until="networkidle")
        await page_p.wait_for_timeout(800)

        # Force remove splash
        await page_p.evaluate('''() => {
            const splash = document.getElementById('appSplashScreen');
            if (splash) splash.remove();
        }''')
        await page_p.wait_for_timeout(400)

        # Measurements
        meas_p = await page_p.evaluate('''() => {
            const banner = document.getElementById('topLiveBanner');
            const badge = banner ? banner.querySelector('span.rounded-full') : null;
            const header = document.querySelector('header');
            const search = document.getElementById('searchInput');
            const bottomDock = document.getElementById('mobileBottomDock');
            
            const bStyle = banner ? window.getComputedStyle(banner) : null;
            const bRect = banner ? banner.getBoundingClientRect() : null;
            const badgeRect = badge ? badge.getBoundingClientRect() : null;
            const hRect = header ? header.getBoundingClientRect() : null;
            const dockStyle = bottomDock ? window.getComputedStyle(bottomDock) : null;
            
            return {
                viewport: `${window.innerWidth}x${window.innerHeight}`,
                paddingTop: bStyle ? bStyle.paddingTop : null,
                bannerHeight: bRect ? bRect.height : null,
                badgeTop: badgeRect ? badgeRect.top : null,
                headerHeight: hRect ? hRect.height : null,
                dockDisplay: dockStyle ? dockStyle.display : null
            };
        }''')
        print("Tablet Portrait Measurements:", meas_p)

        # Full view
        full_p_path = os.path.join(ARTIFACT_DIR, "capture_tablet_main_portrait_full.png")
        await page_p.screenshot(path=full_p_path)
        print(f"Saved tablet portrait full: {full_p_path}")

        # Header crop (width: 834*2=1668, height: 280*2=560)
        im_p = Image.open(full_p_path)
        crop_p = im_p.crop((0, 0, im_p.width, int(300 * 2)))
        crop_p_path = os.path.join(ARTIFACT_DIR, "capture_tablet_main_portrait_header.png")
        crop_p.save(crop_p_path)
        print(f"Saved tablet portrait header: {crop_p_path}")

        # 2. iPad Pro 11 Landscape (1194 x 834)
        context_landscape = await browser.new_context(
            viewport={"width": 1194, "height": 834},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2
        )
        page_l = await context_landscape.new_page()
        await page_l.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page_l.goto("http://127.0.0.1:8080", wait_until="networkidle")
        await page_l.wait_for_timeout(800)

        # Force remove splash
        await page_l.evaluate('''() => {
            const splash = document.getElementById('appSplashScreen');
            if (splash) splash.remove();
        }''')
        await page_l.wait_for_timeout(400)

        full_l_path = os.path.join(ARTIFACT_DIR, "capture_tablet_main_landscape_full.png")
        await page_l.screenshot(path=full_l_path)
        print(f"Saved tablet landscape full: {full_l_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
