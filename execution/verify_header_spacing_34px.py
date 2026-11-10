import asyncio
import os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            device_scale_factor=2
        )
        page = await context.new_page()
        
        await page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        await page.wait_for_timeout(800)

        # Force remove splash
        await page.evaluate('''() => {
            const splash = document.getElementById('appSplashScreen');
            if (splash) {
                splash.remove();
            }
        }''')
        await page.wait_for_timeout(300)

        # 1. Measurements on live 34px
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
        print("DOM Measurements (34px):", measurements)

        # 2. Capture 34px Full Main Screen
        full_34_path = os.path.join(ARTIFACT_DIR, "capture_main_mobile_34px_full.png")
        await page.screenshot(path=full_34_path)

        # 3. Capture 34px Header Crop
        im34 = Image.open(full_34_path)
        crop_h = 600
        crop34 = im34.crop((0, 0, im34.width, crop_h))
        crop_path = os.path.join(ARTIFACT_DIR, "capture_main_mobile_34px_header_crop.png")
        crop34.save(crop_path)

        # 4. Also capture 40px for direct visual comparison
        await page.evaluate('''() => {
            const banner = document.getElementById('topLiveBanner');
            if (banner) {
                banner.style.setProperty('padding-top', '40px', 'important');
            }
        }''')
        await page.wait_for_timeout(300)
        temp_40_path = os.path.join(ARTIFACT_DIR, "temp_main_40px.png")
        await page.screenshot(path=temp_40_path)
        im40 = Image.open(temp_40_path)
        crop40 = im40.crop((0, 0, im40.width, crop_h))

        await browser.close()

        # 5. Build Side-by-Side Comparison (40px vs 34px)
        canvas = Image.new("RGB", (crop40.width * 2 + 40, crop_h + 100), color=(15, 23, 42))
        draw = ImageDraw.Draw(canvas)

        # Left: Previous (40px)
        draw.rectangle([15, 15, crop40.width + 15, 75], fill=(30, 41, 59))
        draw.text((35, 35), "이전 상태 (40px: 4px 상향본)", fill=(203, 213, 225))
        canvas.paste(crop40, (15, 85))

        # Right: New (34px)
        draw.rectangle([crop40.width + 25, 15, crop40.width * 2 + 25, 75], fill=(16, 78, 139))
        draw.text((crop40.width + 45, 35), "★ 신규 적용 (34px: 6px 추가 상향, 총 16px 밀착)", fill=(255, 255, 255))
        canvas.paste(crop34, (crop40.width + 25, 85))

        # Guide lines
        y_40 = 85 + int(40 * 2)
        y_34 = 85 + int(34 * 2)
        draw.line([(15, y_40), (crop40.width + 15, y_40)], fill=(239, 68, 68), width=2)
        draw.line([(crop40.width + 25, y_34), (crop40.width * 2 + 25, y_34)], fill=(34, 197, 94), width=2)
        
        draw.text((35, y_40 + 5), f"배지 Y: 40px (80px on 2x)", fill=(239, 68, 68))
        draw.text((crop40.width + 45, y_34 + 5), f"배지 Y: 34px (68px on 2x) -> 6px 추가 밀착 완료!", fill=(34, 197, 94))

        compare_path = os.path.join(ARTIFACT_DIR, "compare_main_header_40px_vs_34px.png")
        canvas.save(compare_path)
        print("Comparison saved:", compare_path)

        if os.path.exists(temp_40_path):
            os.remove(temp_40_path)

if __name__ == "__main__":
    asyncio.run(main())
