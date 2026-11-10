import asyncio
import os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont

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
        
        # 1. Correct splash bypass key: 'pricetrace_splash_seen' = 'true'
        await page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 2. Guarantee splash is hidden
        await page.evaluate('''() => {
            const splash = document.getElementById('appSplashScreen');
            if (splash) {
                splash.classList.add('splash-hidden');
                splash.style.display = 'none';
            }
        }''')
        await page.wait_for_timeout(500)

        # 3. Check measurements on live main screen
        measurements = await page.evaluate('''() => {
            const banner = document.getElementById('topLiveBanner');
            const badge = banner ? banner.querySelector('span.rounded-full') : null;
            const header = document.querySelector('header');
            const search = document.getElementById('searchInput');
            
            const bStyle = banner ? window.getComputedStyle(banner) : null;
            const bRect = banner ? banner.getBoundingClientRect() : null;
            const badgeRect = badge ? badge.getBoundingClientRect() : null;
            const hRect = header ? header.getBoundingClientRect() : null;
            const sRect = search ? search.getBoundingClientRect() : null;
            
            return {
                paddingTop: bStyle ? bStyle.paddingTop : null,
                paddingBottom: bStyle ? bStyle.paddingBottom : null,
                bannerHeight: bRect ? bRect.height : null,
                badgeTop: badgeRect ? badgeRect.top : null,
                headerHeight: hRect ? hRect.height : null,
                searchTop: sRect ? sRect.top : null
            };
        }''')
        print("Live Main Screen Measurements:", measurements)

        # 4. Save Main Screen Full View
        full_path = os.path.join(ARTIFACT_DIR, "capture_main_mobile_40px_full.png")
        await page.screenshot(path=full_path)
        print(f"Saved full main screenshot: {full_path}")

        # 5. Save Main Screen Header Crop (Top 260pt * 2 = 520px)
        im = Image.open(full_path)
        crop_im = im.crop((0, 0, im.width, int(280 * 2)))
        crop_path = os.path.join(ARTIFACT_DIR, "capture_main_mobile_40px_header_crop.png")
        crop_im.save(crop_path)
        print(f"Saved header crop: {crop_path}")

        # 6. Generate simulated status bar overlay (like real iPhone)
        # We can extract the status bar area from user's upload media_1794296026765_9960cb1f.jpg
        try:
            user_img = Image.open(r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41\.user_uploaded\media_1794296026765_9960cb1f.jpg")
            # Status bar in user image is top ~70px of 1024 (scaled to full_path width 786)
            sb_crop = user_img.crop((0, 0, user_img.width, int(user_img.height * 0.08)))
            sb_resized = sb_crop.resize((im.width, int(44 * 2)))
            
            simulated_im = im.copy()
            # Paste status bar with subtle blend or on top
            simulated_im.paste(sb_resized, (0, 0))
            sim_path = os.path.join(ARTIFACT_DIR, "capture_main_mobile_with_statusbar.png")
            simulated_im.save(sim_path)
            print(f"Saved simulated status bar screenshot: {sim_path}")
        except Exception as e:
            print("Status bar overlay notice:", e)

        # 7. Also capture 44px comparison to see exact 4px difference
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
