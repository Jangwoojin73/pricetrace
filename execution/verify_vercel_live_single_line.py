# -*- coding: utf-8 -*-
import os
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
PROD_URL = "https://pricetrace-nu.vercel.app"
ts = time.strftime("%H%M%S")
snap_prod = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_single_line_pc_{ts}.png")
snap_prod_closeup = os.path.join(ARTIFACT_DIR, f"verify_vercel_live_single_line_closeup_{ts}.png")

CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-remote-fonts"
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    page.goto(f"{PROD_URL}/?v={time.time()}", wait_until="networkidle", timeout=20000)
    page.wait_for_selector("#welcomeHeroSection", timeout=10000)
    page.wait_for_timeout(800)

    # DOM 실측
    prod_metrics = page.evaluate('''() => {
        const h = document.getElementById("welcomeHeroSection");
        const p = h ? h.querySelector("p") : null;
        const rect = p ? p.getBoundingClientRect() : null;
        const cs = p ? window.getComputedStyle(p) : null;
        const lh = cs ? parseFloat(cs.lineHeight) : 20;
        return {
            measuredAt: new Date().toLocaleTimeString(),
            pText: p ? p.innerText.trim() : "",
            pWidth: rect ? Math.round(rect.width) : 0,
            pHeight: rect ? Math.round(rect.height) : 0,
            lineHeight: Math.round(lh),
            isSingleLine: rect ? rect.height <= lh * 1.5 : false,
            hasWhitespaceNowrap: p ? p.classList.contains("lg:whitespace-nowrap") : false
        };
    }''')
    print("Vercel Live Single Line Metrics:", prod_metrics)

    page.screenshot(path=snap_prod)
    print(f"[✓] Saved Vercel Live PC screenshot: {snap_prod} ({os.path.getsize(snap_prod)} bytes)")

    hero_elem = page.locator("#welcomeHeroSection")
    hero_elem.screenshot(path=snap_prod_closeup)
    print(f"[✓] Saved Vercel Live Hero closeup: {snap_prod_closeup} ({os.path.getsize(snap_prod_closeup)} bytes)")

    ctx.close()
    browser.close()
