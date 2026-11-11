# -*- coding: utf-8 -*-
"""
Verification Script for Optimized Bottom Navigation Bar
- Measures tabs 1, 2, 3, 4, 5 heights and baseline
- Captures close-up of bottom nav dock on iPhone 15 Pro & iPad Pro 11
- Generates side-by-side comparison with user's original image
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import asyncio
import io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-remote-fonts']
        )
        
        # 1. iPhone 15 Pro (393x852)
        ctx = await browser.new_context(
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

        # Remove splash if present
        await page.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            if (splash) splash.remove();
        }''')
        await page.wait_for_timeout(300)

        # Measure 5 tabs
        meas = await page.evaluate('''() => {
            const nav = document.getElementById('mobileBottomNav');
            const btnIds = ["mobileNavHomeBtn", "mobileNavSearchFabBtn", "mobileNavSteadyBtn", "mobileNavHotdealBtn", "mobileNavConfigBtn"];
            const tabs = btnIds.map(id => {
                const el = document.getElementById(id);
                const pill = el ? el.querySelector('.mobile-nav-pill') : null;
                const badge = el ? el.querySelector('.hero-nav-badge') : null;
                const r = el ? el.getBoundingClientRect() : null;
                const pillR = pill ? pill.getBoundingClientRect() : null;
                const badgeR = badge ? badge.getBoundingClientRect() : null;
                return {
                    id,
                    top: r ? Math.round(r.top) : null,
                    bottom: r ? Math.round(r.bottom) : null,
                    height: r ? Math.round(r.height) : null,
                    pillHeight: pillR ? Math.round(pillR.height) : null,
                    badgeSize: badgeR ? `${Math.round(badgeR.width)}x${Math.round(badgeR.height)}` : null
                };
            });
            const navRect = nav ? nav.getBoundingClientRect() : null;
            return {
                navTop: navRect ? Math.round(navRect.top) : null,
                navHeight: navRect ? Math.round(navRect.height) : null,
                tabs
            };
        }''')
        print("DOM Measurements for Bottom Nav:", meas)

        # 1. Full mobile screenshot
        full_path = os.path.join(ARTIFACT_DIR, "nav_optimized_mobile_full.png")
        await page.screenshot(path=full_path)

        # 2. Bottom Nav close-up crop
        im = Image.open(full_path)
        dock_crop = im.crop((0, im.height - int(110 * 2), im.width, im.height))
        dock_crop_path = os.path.join(ARTIFACT_DIR, "nav_optimized_dock_crop.png")
        dock_crop.save(dock_crop_path)
        print("Dock crop saved:", dock_crop_path)

        # Test active tab switching: Click steady, then click hotdeal
        await page.click("#mobileNavSteadyBtn")
        await page.wait_for_timeout(300)
        steady_bytes = await page.screenshot()
        im_steady = Image.open(io.BytesIO(steady_bytes))
        crop_steady = im_steady.crop((0, im_steady.height - int(110 * 2), im_steady.width, im_steady.height))
        steady_active_path = os.path.join(ARTIFACT_DIR, "nav_steady_active_crop.png")
        crop_steady.save(steady_active_path)

        await page.click("#mobileNavHotdealBtn")
        await page.wait_for_timeout(300)
        hotdeal_bytes = await page.screenshot()
        im_hotdeal = Image.open(io.BytesIO(hotdeal_bytes))
        crop_hotdeal = im_hotdeal.crop((0, im_hotdeal.height - int(110 * 2), im_hotdeal.width, im_hotdeal.height))
        hotdeal_active_path = os.path.join(ARTIFACT_DIR, "nav_hotdeal_active_crop.png")
        crop_hotdeal.save(hotdeal_active_path)

        # Tablet screenshot (iPad Pro 11, 834x1194)
        ctx_tab = await browser.new_context(
            viewport={"width": 834, "height": 1194},
            is_mobile=True,
            has_touch=True,
            service_workers="block",
            device_scale_factor=2
        )
        p_tab = await ctx_tab.new_page()
        await p_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await p_tab.goto(BASE_URL, wait_until="domcontentloaded")
        await p_tab.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            if (splash) splash.remove();
        }''')
        await p_tab.wait_for_timeout(300)
        tab_full_path = os.path.join(ARTIFACT_DIR, "nav_optimized_tablet_full.png")
        await p_tab.screenshot(path=tab_full_path)
        im_tab = Image.open(tab_full_path)
        crop_tab = im_tab.crop((0, im_tab.height - int(110 * 2), im_tab.width, im_tab.height))
        tab_dock_path = os.path.join(ARTIFACT_DIR, "nav_optimized_tablet_dock_crop.png")
        crop_tab.save(tab_dock_path)
        print("Tablet dock saved:", tab_dock_path)

        await browser.close()

        # Build Side-by-Side Comparison Card with user's uploaded original
        user_orig_path = os.path.join(ARTIFACT_DIR, r".user_uploaded\media_1794357822882_02b4c463.png")
        if os.path.exists(user_orig_path):
            user_orig = Image.open(user_orig_path)
            # Resize user_orig to match dock_crop width
            new_h = int(user_orig.height * (dock_crop.width / user_orig.width))
            user_orig_resized = user_orig.resize((dock_crop.width, new_h))
            
            canvas = Image.new("RGB", (dock_crop.width + 40, new_h + dock_crop.height + 150), color=(15, 23, 42))
            draw = ImageDraw.Draw(canvas)

            # Top: User's original (protruding badges)
            draw.rectangle([20, 15, dock_crop.width + 20, 65], fill=(225, 29, 72))
            draw.text((40, 30), "[이전 상태] 생필품/핫딜이 거대하게 상단으로 돌출되어 균형이 깨짐", fill=(255, 255, 255))
            canvas.paste(user_orig_resized, (20, 75))

            # Bottom: New optimized (neatly aligned inside dock)
            y_offset = 75 + new_h + 20
            draw.rectangle([20, y_offset, dock_crop.width + 20, y_offset + 50], fill=(5, 150, 105))
            draw.text((40, y_offset + 15), "[★ 신규 최적화] 평범한 크기로 축소 & 바 내부 완벽 정렬 (컬러/아이콘 100% 유지)", fill=(255, 255, 255))
            canvas.paste(dock_crop, (20, y_offset + 60))

            compare_path = os.path.join(ARTIFACT_DIR, "compare_bottom_nav_before_after.png")
            canvas.save(compare_path)
            print("Comparison card saved:", compare_path)

if __name__ == "__main__":
    asyncio.run(main())
