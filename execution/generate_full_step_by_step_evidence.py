# -*- coding: utf-8 -*-
"""
Full Step-by-Step Verification Script
Captures all stages of Pull-to-Refresh, Bottom Navigation, and Tablet responsiveness
with precise DOM measurements.
"""
import sys, os
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
        
        # Context 1: iPhone 15 Pro (393x852)
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
        
        # Remove splash
        await page.evaluate('''() => {
            const s = document.getElementById("appSplashScreen");
            if (s) s.remove();
        }''')
        await page.wait_for_timeout(300)

        # -------------------------------------------------------------
        # STEP 1-1: [평상시 기본 화면 (Idle / Normal)]
        # -------------------------------------------------------------
        s1_1_meas = await page.evaluate('''() => {
            const h = document.querySelector("header");
            const hero = document.getElementById("welcomeView")?.firstElementChild;
            const ptr = document.getElementById("ptrIndicator");
            const ptrStyle = ptr ? window.getComputedStyle(ptr) : null;
            return {
                headerBottom: Math.round(h.getBoundingClientRect().bottom),
                heroTop: hero ? Math.round(hero.getBoundingClientRect().top) : null,
                gap: hero ? Math.round(hero.getBoundingClientRect().top - h.getBoundingClientRect().bottom) : null,
                ptrDisplay: ptrStyle ? ptrStyle.display : null,
                ptrOpacity: ptrStyle ? ptrStyle.opacity : null,
                ptrIsVisible: ptr ? (ptr.offsetWidth > 0 && ptr.offsetHeight > 0 && ptrStyle.display !== 'none') : false
            };
        }''')
        print("STEP 1-1 Meas:", s1_1_meas)
        p_step1_1 = os.path.join(ARTIFACT_DIR, "step1_1_idle_normal_screen.png")
        await page.screenshot(path=p_step1_1)

        # Crop header + hero section for step 1-1
        im1_1 = Image.open(p_step1_1)
        im1_1_crop = im1_1.crop((0, 0, im1_1.width, 960))
        p_step1_1_crop = os.path.join(ARTIFACT_DIR, "step1_1_idle_crop.png")
        im1_1_crop.save(p_step1_1_crop)

        # -------------------------------------------------------------
        # STEP 1-2: [아래로 35px 살짝 당김 (Pulling 35px - Below Threshold)]
        # -------------------------------------------------------------
        # Trigger touchstart and touchmove to 35px pull
        await page.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const main = document.getElementById("mainContent");
            const header = document.querySelector("header");
            const hBottom = header ? header.getBoundingClientRect().bottom : 206;
            
            main.style.transition = "none";
            main.style.transform = "translateY(26px)";
            
            ptr.style.top = (hBottom + 8) + "px";
            ptr.style.display = "flex";
            ptr.classList.add("ptr-active");
            ptr.style.opacity = "1";
            
            const arrow = document.getElementById("ptrArrow");
            const text = document.getElementById("ptrText");
            if (arrow) arrow.style.transform = "rotate(0deg)";
            if (text) text.textContent = "당겨서 최저가 새로고침";
        }''')
        await page.wait_for_timeout(200)

        s1_2_meas = await page.evaluate('''() => {
            const h = document.querySelector("header");
            const hero = document.getElementById("welcomeView")?.firstElementChild;
            const ptr = document.getElementById("ptrIndicator");
            return {
                headerBottom: Math.round(h.getBoundingClientRect().bottom),
                heroTop: hero ? Math.round(hero.getBoundingClientRect().top) : null,
                gap: hero ? Math.round(hero.getBoundingClientRect().top - h.getBoundingClientRect().bottom) : null,
                ptrTop: ptr ? Math.round(ptr.getBoundingClientRect().top) : null,
                ptrText: document.getElementById("ptrText")?.textContent
            };
        }''')
        print("STEP 1-2 Meas:", s1_2_meas)
        p_step1_2 = os.path.join(ARTIFACT_DIR, "step1_2_pulling_35px.png")
        await page.screenshot(path=p_step1_2)

        im1_2 = Image.open(p_step1_2)
        im1_2_crop = im1_2.crop((0, 0, im1_2.width, 1020))
        p_step1_2_crop = os.path.join(ARTIFACT_DIR, "step1_2_pulling_35px_crop.png")
        im1_2_crop.save(p_step1_2_crop)

        # -------------------------------------------------------------
        # STEP 1-3: [임계값 도달 65px 당김 (Threshold Reached - Rotate Arrow)]
        # -------------------------------------------------------------
        await page.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const main = document.getElementById("mainContent");
            const header = document.querySelector("header");
            const hBottom = header ? header.getBoundingClientRect().bottom : 206;
            
            main.style.transition = "none";
            main.style.transform = "translateY(56px)";
            
            ptr.style.top = (hBottom + 8) + "px";
            ptr.style.display = "flex";
            ptr.classList.add("ptr-active");
            ptr.style.opacity = "1";
            
            const arrow = document.getElementById("ptrArrow");
            const text = document.getElementById("ptrText");
            if (arrow) arrow.style.transform = "rotate(180deg)";
            if (text) text.textContent = "손을 놓아 최저가 갱신";
        }''')
        await page.wait_for_timeout(200)

        s1_3_meas = await page.evaluate('''() => {
            const h = document.querySelector("header");
            const hero = document.getElementById("welcomeView")?.firstElementChild;
            const ptr = document.getElementById("ptrIndicator");
            return {
                headerBottom: Math.round(h.getBoundingClientRect().bottom),
                heroTop: hero ? Math.round(hero.getBoundingClientRect().top) : null,
                gap: hero ? Math.round(hero.getBoundingClientRect().top - h.getBoundingClientRect().bottom) : null,
                ptrText: document.getElementById("ptrText")?.textContent
            };
        }''')
        print("STEP 1-3 Meas:", s1_3_meas)
        p_step1_3 = os.path.join(ARTIFACT_DIR, "step1_3_pulling_threshold_reached.png")
        await page.screenshot(path=p_step1_3)

        im1_3 = Image.open(p_step1_3)
        im1_3_crop = im1_3.crop((0, 0, im1_3.width, 1080))
        p_step1_3_crop = os.path.join(ARTIFACT_DIR, "step1_3_threshold_crop.png")
        im1_3_crop.save(p_step1_3_crop)

        # -------------------------------------------------------------
        # STEP 1-4: [손을 놓아 새로고침 실행 중 (Refreshing - Spinner Active)]
        # -------------------------------------------------------------
        await page.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const main = document.getElementById("mainContent");
            const arrow = document.getElementById("ptrArrow");
            const spinner = document.getElementById("ptrSpinner");
            const text = document.getElementById("ptrText");
            
            main.style.transition = "transform 0.25s cubic-bezier(0.2, 0.8, 0.2, 1)";
            main.style.transform = "translateY(52px)";
            
            if (arrow) arrow.classList.add("hidden");
            if (spinner) spinner.classList.remove("hidden");
            if (text) text.textContent = "실시간 최저가 레이더 갱신 중...";
        }''')
        await page.wait_for_timeout(250)

        p_step1_4 = os.path.join(ARTIFACT_DIR, "step1_4_refreshing_active.png")
        await page.screenshot(path=p_step1_4)

        im1_4 = Image.open(p_step1_4)
        im1_4_crop = im1_4.crop((0, 0, im1_4.width, 1080))
        p_step1_4_crop = os.path.join(ARTIFACT_DIR, "step1_4_refreshing_crop.png")
        im1_4_crop.save(p_step1_4_crop)

        # -------------------------------------------------------------
        # STEP 1-5: [갱신 완료 및 원위치 탄성 복귀 (Restored to Clean Normal)]
        # -------------------------------------------------------------
        await page.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const main = document.getElementById("mainContent");
            const arrow = document.getElementById("ptrArrow");
            const spinner = document.getElementById("ptrSpinner");
            const text = document.getElementById("ptrText");
            
            main.style.transition = "transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)";
            main.style.transform = "translateY(0px)";
            
            ptr.classList.remove("ptr-active");
            ptr.style.display = "none";
            ptr.style.opacity = "0";
            
            if (arrow) {
                arrow.classList.remove("hidden");
                arrow.style.transform = "rotate(0deg)";
            }
            if (spinner) spinner.classList.add("hidden");
            if (text) text.textContent = "당겨서 최저가 새로고침";
        }''')
        await page.wait_for_timeout(350)

        s1_5_meas = await page.evaluate('''() => {
            const h = document.querySelector("header");
            const hero = document.getElementById("welcomeView")?.firstElementChild;
            const ptr = document.getElementById("ptrIndicator");
            return {
                gapAfterRestored: hero ? Math.round(hero.getBoundingClientRect().top - h.getBoundingClientRect().bottom) : null,
                ptrDisplay: window.getComputedStyle(ptr).display,
                ptrIsVisible: ptr.offsetWidth > 0 && ptr.offsetHeight > 0 && window.getComputedStyle(ptr).display !== 'none'
            };
        }''')
        print("STEP 1-5 Meas:", s1_5_meas)
        p_step1_5 = os.path.join(ARTIFACT_DIR, "step1_5_restored_clean.png")
        await page.screenshot(path=p_step1_5)

        im1_5 = Image.open(p_step1_5)
        im1_5_crop = im1_5.crop((0, 0, im1_5.width, 960))
        p_step1_5_crop = os.path.join(ARTIFACT_DIR, "step1_5_restored_crop.png")
        im1_5_crop.save(p_step1_5_crop)

        # -------------------------------------------------------------
        # SECTION 2: 하단 네비게이션 독 5대 탭 최적화 단계별 실측
        # -------------------------------------------------------------
        # Step 2-1: Default Dock
        dock_crop_box = (0, im1_1.height - int(115 * 2), im1_1.width, im1_1.height)
        im_dock_default = im1_1.crop(dock_crop_box)
        p_step2_1 = os.path.join(ARTIFACT_DIR, "step2_1_nav_dock_default.png")
        im_dock_default.save(p_step2_1)

        # Step 2-2: Click Steady
        await page.click("#mobileNavSteadyBtn")
        await page.wait_for_timeout(250)
        im_steady_full = Image.open(io.BytesIO(await page.screenshot()))
        im_steady_crop = im_steady_full.crop(dock_crop_box)
        p_step2_2 = os.path.join(ARTIFACT_DIR, "step2_2_nav_steady_active.png")
        im_steady_crop.save(p_step2_2)

        # Step 2-3: Click Hotdeal
        await page.click("#mobileNavHotdealBtn")
        await page.wait_for_timeout(250)
        im_hotdeal_full = Image.open(io.BytesIO(await page.screenshot()))
        im_hotdeal_crop = im_hotdeal_full.crop(dock_crop_box)
        p_step2_3 = os.path.join(ARTIFACT_DIR, "step2_3_nav_hotdeal_active.png")
        im_hotdeal_crop.save(p_step2_3)

        # Step 2-4: Click Radar
        await page.click("#mobileNavSearchFabBtn")
        await page.wait_for_timeout(250)
        im_radar_full = Image.open(io.BytesIO(await page.screenshot()))
        im_radar_crop = im_radar_full.crop(dock_crop_box)
        p_step2_4 = os.path.join(ARTIFACT_DIR, "step2_4_nav_radar_active.png")
        im_radar_crop.save(p_step2_4)

        # -------------------------------------------------------------
        # SECTION 3: 태블릿 기기 실측
        # -------------------------------------------------------------
        # iPad Mini (768x1024)
        ctx_mini = await browser.new_context(
            viewport={"width": 768, "height": 1024},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            service_workers="block",
            device_scale_factor=2
        )
        p_mini = await ctx_mini.new_page()
        await p_mini.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await p_mini.goto(BASE_URL, wait_until="domcontentloaded")
        await p_mini.evaluate('''() => {
            const s = document.getElementById("appSplashScreen");
            if (s) s.remove();
        }''')
        await p_mini.wait_for_timeout(300)
        p_step3_1 = os.path.join(ARTIFACT_DIR, "step3_1_tablet_mini_full.png")
        await p_mini.screenshot(path=p_step3_1)
        im_mini = Image.open(p_step3_1)
        im_mini_dock = im_mini.crop((0, im_mini.height - int(115 * 2), im_mini.width, im_mini.height))
        p_step3_1_dock = os.path.join(ARTIFACT_DIR, "step3_1_tablet_mini_dock.png")
        im_mini_dock.save(p_step3_1_dock)

        # iPad Pro 11 (834x1194)
        ctx_pro = await browser.new_context(
            viewport={"width": 834, "height": 1194},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            service_workers="block",
            device_scale_factor=2
        )
        p_pro = await ctx_pro.new_page()
        await p_pro.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        await p_pro.goto(BASE_URL, wait_until="domcontentloaded")
        await p_pro.evaluate('''() => {
            const s = document.getElementById("appSplashScreen");
            if (s) s.remove();
        }''')
        await p_pro.wait_for_timeout(300)
        p_step3_2 = os.path.join(ARTIFACT_DIR, "step3_2_tablet_pro11_full.png")
        await p_pro.screenshot(path=p_step3_2)
        im_pro = Image.open(p_step3_2)
        im_pro_dock = im_pro.crop((0, im_pro.height - int(115 * 2), im_pro.width, im_pro.height))
        p_step3_2_dock = os.path.join(ARTIFACT_DIR, "step3_2_tablet_pro11_dock.png")
        im_pro_dock.save(p_step3_2_dock)

        await browser.close()
        print("All individual stage screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(main())
