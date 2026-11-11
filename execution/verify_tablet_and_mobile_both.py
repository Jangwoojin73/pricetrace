# -*- coding: utf-8 -*-
import asyncio, os
from playwright.async_api import async_playwright
from PIL import Image

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"

async def test_device(browser, name, width, height, is_mobile=True):
    ctx = await browser.new_context(
        viewport={"width": width, "height": height},
        user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1" if is_mobile else "Mozilla/5.0",
        is_mobile=is_mobile,
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
    await page.wait_for_timeout(200)

    # Measure Bottom Nav & PTR
    res = await page.evaluate('''() => {
        const nav = document.getElementById("mobileBottomNav");
        const ptr = document.getElementById("ptrIndicator");
        const main = document.getElementById("mainContent");
        const steadyBtn = document.getElementById("mobileNavSteadyBtn");
        const hotdealBtn = document.getElementById("mobileNavHotdealBtn");
        const homeBtn = document.getElementById("mobileNavHomeBtn");

        const navVisible = nav ? window.getComputedStyle(nav).display !== "none" && window.getComputedStyle(nav).visibility !== "hidden" : false;
        const ptrExists = !!ptr;
        
        let navData = null;
        if (nav && navVisible) {
            const nr = nav.getBoundingClientRect();
            const sBadge = steadyBtn ? steadyBtn.querySelector(".hero-nav-badge") : null;
            const hBadge = hotdealBtn ? hotdealBtn.querySelector(".hero-nav-badge") : null;
            const sRect = sBadge ? sBadge.getBoundingClientRect() : null;
            const hRect = hBadge ? hBadge.getBoundingClientRect() : null;
            const homeRect = homeBtn ? homeBtn.getBoundingClientRect() : null;

            navData = {
                navTop: Math.round(nr.top),
                navBottom: Math.round(nr.bottom),
                navHeight: Math.round(nr.height),
                steadyBadge: sRect ? `${Math.round(sRect.width)}x${Math.round(sRect.height)}` : null,
                hotdealBadge: hRect ? `${Math.round(hRect.width)}x${Math.round(hRect.height)}` : null,
                steadyTop: sRect ? Math.round(sRect.top) : null,
                protrusion: sRect ? Math.max(0, Math.round(nr.top - sRect.top)) : null
            };
        }

        return {
            navVisible,
            ptrExists,
            navData
        };
    }''')
    
    # Capture Screenshot
    full_path = os.path.join(ARTIFACT_DIR, f"verify_{name}_full.png")
    await page.screenshot(path=full_path)
    
    # Crop dock if nav visible
    dock_path = None
    if res["navVisible"]:
        im = Image.open(full_path)
        crop = im.crop((0, im.height - int(115 * 2), im.width, im.height))
        dock_path = os.path.join(ARTIFACT_DIR, f"verify_{name}_dock_crop.png")
        crop.save(dock_path)

    # Test Pull to refresh touch
    ptr_triggered = False
    try:
        # Simulate touch drag down
        await page.touchscreen.tap(width // 2, 120)
        # Mouse / touch drag
        await page.mouse.move(width // 2, 120)
        await page.mouse.down()
        await page.mouse.move(width // 2, 280, steps=10)
        await page.wait_for_timeout(300)
        ptr_drag_path = os.path.join(ARTIFACT_DIR, f"verify_{name}_ptr_drag.png")
        await page.screenshot(path=ptr_drag_path)
        await page.mouse.up()
        await page.wait_for_timeout(400)
    except Exception as e:
        print("PTR interaction note:", e)

    await ctx.close()
    return res, full_path, dock_path

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-remote-fonts']
        )
        
        devices = [
            ("mobile_iphone15", 393, 852, True),
            ("tablet_ipad_mini", 768, 1024, True),
            ("tablet_ipad_pro11", 834, 1194, True),
        ]
        
        results = {}
        for name, w, h, is_mob in devices:
            r, full_p, dock_p = await test_device(browser, name, w, h, is_mob)
            results[name] = {
                "specs": f"{w}x{h}",
                "navVisible": r["navVisible"],
                "ptrExists": r["ptrExists"],
                "navData": r["navData"],
                "full_screenshot": full_p,
                "dock_crop": dock_p
            }
            print(f"Device [{name} {w}x{h}]: navVisible={r['navVisible']}, ptrExists={r['ptrExists']}, navData={r['navData']}")

        await browser.close()
        return results

if __name__ == "__main__":
    asyncio.run(main())
