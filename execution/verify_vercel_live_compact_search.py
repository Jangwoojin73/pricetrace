# -*- coding: utf-8 -*-
import os, sys, time, json
from playwright.sync_api import sync_playwright

VERCEL_URL = "https://pricetrace-nu.vercel.app"
ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

def run_vercel_live_verification():
    ts = time.strftime("%H%M%S")
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] Starting Vercel Live Compact Search Detail Verification...")

    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. MOBILE VERIFICATION (393x852)
        ctx_mob = browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            has_touch=True,
            is_mobile=True,
            service_workers="block"
        )
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        target_url = f"{VERCEL_URL}/?cb={time.time()}"
        print(f"Navigating to mobile live target: {target_url}")
        page_mob.goto(target_url, wait_until="networkidle", timeout=30000)
        time.sleep(1.5)

        print("Submitting search on mobile live...")
        page_mob.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_mob.press("#searchInput", "Enter")

        page_mob.wait_for_selector("#priceComparisonGrid .rank-card", timeout=20000)
        time.sleep(2)

        mob_metrics = page_mob.evaluate("""() => {
            const alertBanner = document.getElementById('alertBanner');
            const alertRect = alertBanner ? alertBanner.getBoundingClientRect() : null;
            const alertCs = alertBanner ? window.getComputedStyle(alertBanner) : null;
            const alertIcon = document.getElementById('alertIconBox');
            const alertIconRect = alertIcon ? alertIcon.getBoundingClientRect() : null;

            const heroSection = document.querySelector('#resultView section:nth-of-type(1)');
            const heroRect = heroSection ? heroSection.getBoundingClientRect() : null;
            const heroImg = document.getElementById('productMainImage');
            const heroImgContainer = heroImg ? heroImg.closest('.relative.w-full') : null;
            const heroImgContainerRect = heroImgContainer ? heroImgContainer.getBoundingClientRect() : null;
            const heroPriceBox = document.querySelector('#lowestPriceDisplay') ? document.querySelector('#lowestPriceDisplay').closest('.bg-gradient-to-br') : null;
            const heroPriceBoxRect = heroPriceBox ? heroPriceBox.getBoundingClientRect() : null;

            const grid = document.getElementById('priceComparisonGrid');
            const gridRect = grid ? grid.getBoundingClientRect() : null;
            const cards = grid ? Array.from(grid.querySelectorAll('.rank-card')) : [];
            const cardMetrics = cards.map((c, i) => {
                const r = c.getBoundingClientRect();
                return {
                    rank: i + 1,
                    width: Math.round(r.width),
                    height: Math.round(r.height)
                };
            });

            return {
                device: "Mobile 393x852 (Vercel Live)",
                documentScrollHeight: document.documentElement.scrollHeight,
                alertBanner: {
                    width: alertRect ? Math.round(alertRect.width) : 0,
                    height: alertRect ? Math.round(alertRect.height) : 0,
                    padding: alertCs ? `${alertCs.paddingTop} ${alertCs.paddingRight} ${alertCs.paddingBottom} ${alertCs.paddingLeft}` : '',
                    iconBox: alertIconRect ? { width: Math.round(alertIconRect.width), height: Math.round(alertIconRect.height) } : null
                },
                heroSection: {
                    width: heroRect ? Math.round(heroRect.width) : 0,
                    height: heroRect ? Math.round(heroRect.height) : 0,
                    imageContainerHeight: heroImgContainerRect ? Math.round(heroImgContainerRect.height) : 0,
                    priceBoxHeight: heroPriceBoxRect ? Math.round(heroPriceBoxRect.height) : 0
                },
                comparisonGrid: {
                    width: gridRect ? Math.round(gridRect.width) : 0,
                    height: gridRect ? Math.round(gridRect.height) : 0,
                    cards: cardMetrics
                }
            };
        }""")

        print(f"[VERCEL_MOB_METRICS]{json.dumps(mob_metrics, indent=2)}[/VERCEL_MOB_METRICS]")

        # 1. Alert Banner screenshot
        snap_alert = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_mobile_alert_banner_{ts}.png")
        page_mob.evaluate("document.getElementById('alertBanner').scrollIntoView({ behavior: 'instant', block: 'center' })")
        time.sleep(0.4)
        page_mob.screenshot(path=snap_alert, full_page=False)
        print(f"[✓] Vercel Mobile alert banner screenshot: {snap_alert}")

        # 2. Hero Card screenshot
        snap_hero = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_mobile_hero_card_{ts}.png")
        page_mob.evaluate("document.querySelector('#resultView section:nth-of-type(1)').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.4)
        page_mob.screenshot(path=snap_hero, full_page=False)
        print(f"[✓] Vercel Mobile hero card screenshot: {snap_hero}")

        # 3. TOP3 Comparison Grid screenshot
        snap_grid = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_mobile_comparison_grid_{ts}.png")
        page_mob.evaluate("document.getElementById('priceComparisonGrid').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.4)
        page_mob.screenshot(path=snap_grid, full_page=False)
        print(f"[✓] Vercel Mobile comparison grid screenshot: {snap_grid}")

        # 2. TABLET VERIFICATION (800x1280)
        ctx_tab = browser.new_context(
            viewport={"width": 800, "height": 1280},
            device_scale_factor=2,
            has_touch=True,
            service_workers="block"
        )
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_tab.goto(f"{VERCEL_URL}/?cb={time.time()}", wait_until="networkidle", timeout=30000)
        time.sleep(1.5)

        page_tab.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page_tab.press("#searchInput", "Enter")
        page_tab.wait_for_selector("#priceComparisonGrid .rank-card", timeout=20000)
        time.sleep(2)

        tab_metrics = page_tab.evaluate("""() => {
            const heroSection = document.querySelector('#resultView section:nth-of-type(1)');
            const heroRect = heroSection ? heroSection.getBoundingClientRect() : null;
            const heroCs = heroSection ? window.getComputedStyle(heroSection) : null;
            
            const gridDiv = heroSection ? heroSection.querySelector('.grid') : null;
            const gridCs = gridDiv ? window.getComputedStyle(gridDiv) : null;
            
            const imgBox = document.getElementById('productMainImage') ? document.getElementById('productMainImage').closest('.relative') : null;
            const imgRect = imgBox ? imgBox.getBoundingClientRect() : null;
            
            const priceBox = document.querySelector('#lowestPriceDisplay') ? document.querySelector('#lowestPriceDisplay').closest('.bg-gradient-to-br') : null;
            const priceRect = priceBox ? priceBox.getBoundingClientRect() : null;

            return {
                device: "Tablet 800x1280 (Vercel Live)",
                viewport: { width: window.innerWidth, height: window.innerHeight },
                documentScrollHeight: document.documentElement.scrollHeight,
                heroSection: {
                    width: heroRect ? Math.round(heroRect.width) : 0,
                    height: heroRect ? Math.round(heroRect.height) : 0,
                    padding: heroCs ? `${heroCs.paddingTop} ${heroCs.paddingRight} ${heroCs.paddingBottom} ${heroCs.paddingLeft}` : ''
                },
                gridTemplate: gridCs ? gridCs.gridTemplateColumns : 'N/A',
                imageBox: {
                    width: imgRect ? Math.round(imgRect.width) : 0,
                    height: imgRect ? Math.round(imgRect.height) : 0
                },
                priceBox: {
                    width: priceBox ? Math.round(priceRect.width) : 0,
                    height: priceBox ? Math.round(priceRect.height) : 0
                }
            };
        }""")

        print(f"[VERCEL_TAB_METRICS]{json.dumps(tab_metrics, indent=2)}[/VERCEL_TAB_METRICS]")

        snap_tab_hero = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_tablet_hero_compact_{ts}.png")
        page_tab.evaluate("document.querySelector('#resultView section:nth-of-type(1)').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.5)
        page_tab.screenshot(path=snap_tab_hero, full_page=False)
        print(f"[✓] Vercel Tablet hero compact screenshot: {snap_tab_hero}")

        browser.close()

if __name__ == "__main__":
    run_vercel_live_verification()
