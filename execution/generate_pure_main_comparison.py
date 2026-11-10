import asyncio
import os
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont

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

        # 1. Capture 44px (Previous state)
        await page.evaluate('''() => {
            const banner = document.getElementById('topLiveBanner');
            if (banner) {
                banner.style.setProperty('padding-top', '44px', 'important');
            }
        }''')
        await page.wait_for_timeout(300)
        path_44px = os.path.join(ARTIFACT_DIR, "temp_main_44px.png")
        await page.screenshot(path=path_44px)

        # 2. Capture 40px (Current new state)
        await page.evaluate('''() => {
            const banner = document.getElementById('topLiveBanner');
            if (banner) {
                banner.style.setProperty('padding-top', '40px', 'important');
            }
        }''')
        await page.wait_for_timeout(300)
        path_40px = os.path.join(ARTIFACT_DIR, "temp_main_40px.png")
        await page.screenshot(path=path_40px)

        await browser.close()

        # Combine both for direct visual comparison
        im44 = Image.open(path_44px)
        im40 = Image.open(path_40px)
        
        # Crop header area (width: 786, height: 600)
        crop_h = 600
        crop44 = im44.crop((0, 0, im44.width, crop_h))
        crop40 = im40.crop((0, 0, im40.width, crop_h))

        canvas = Image.new("RGB", (crop44.width * 2 + 40, crop_h + 100), color=(15, 23, 42))
        draw = ImageDraw.Draw(canvas)

        # Draw left header: Previous 44px
        draw.rectangle([15, 15, crop44.width + 15, 75], fill=(30, 41, 59))
        draw.text((35, 35), "이전 상태 (44px: 6px 상향 적용본)", fill=(203, 213, 225))
        canvas.paste(crop44, (15, 85))

        # Draw right header: Current 40px
        draw.rectangle([crop44.width + 25, 15, crop44.width * 2 + 25, 75], fill=(16, 78, 139))
        draw.text((crop44.width + 45, 35), "★ 신규 적용 (40px: 추가 4px 상향, 총 10px 밀착)", fill=(255, 255, 255))
        canvas.paste(crop40, (crop44.width + 25, 85))

        # Add red indicator lines showing the 4px shift (8 physical px on scale 2)
        # Banner top is 0, badge top at 44pt (88px) vs 40pt (80px)
        y_44 = 85 + int(44 * 2)
        y_40 = 85 + int(40 * 2)
        draw.line([(15, y_44), (crop44.width + 15, y_44)], fill=(239, 68, 68), width=2)
        draw.line([(crop44.width + 25, y_40), (crop44.width * 2 + 25, y_40)], fill=(34, 197, 94), width=2)
        
        draw.text((35, y_44 + 5), f"배지 시작 Y: 44px (88px on 2x)", fill=(239, 68, 68))
        draw.text((crop44.width + 45, y_40 + 5), f"배지 시작 Y: 40px (80px on 2x) -> 4px 상향 밀착!", fill=(34, 197, 94))

        compare_path = os.path.join(ARTIFACT_DIR, "compare_main_header_44px_vs_40px.png")
        canvas.save(compare_path)
        print("Comparison saved:", compare_path)

        # Cleanup temp
        if os.path.exists(path_44px): os.remove(path_44px)
        if os.path.exists(path_40px): os.remove(path_40px)

if __name__ == "__main__":
    asyncio.run(main())
