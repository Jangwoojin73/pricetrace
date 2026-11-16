# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

VERCEL_URL = "https://pricetrace-nu.vercel.app"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
    ctx = browser.new_context(viewport={"width": 393, "height": 852}, device_scale_factor=3, is_mobile=True)
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    page.goto(VERCEL_URL, wait_until="load", timeout=20000)
    page.wait_for_selector("#welcomeHeroSection", timeout=10000)
    time.sleep(1)

    metrics = page.evaluate("""() => {
        const hero = document.getElementById('welcomeHeroSection');
        const r = hero ? hero.getBoundingClientRect() : null;
        const cs = hero ? window.getComputedStyle(hero) : null;
        const dualTabs = document.getElementById('dualTabButtonsTray');
        const dtR = dualTabs ? dualTabs.getBoundingClientRect() : null;

        return {
            heroHeight: r ? Math.round(r.height * 10) / 10 : null,
            heroWidth: r ? Math.round(r.width * 10) / 10 : null,
            heroPadding: cs ? cs.padding : null,
            dualTabsTop: dtR ? Math.round(dtR.top * 10) / 10 : null
        };
    }""")
    print("Baseline Metrics:", json.dumps(metrics, indent=2))
    page.screenshot(path=r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41\baseline_welcome_hero_mobile.png")
    browser.close()
