# -*- coding: utf-8 -*-
import os, sys, time, json, urllib.request, subprocess
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

def is_server_up():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/status", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False

try:
    if not is_server_up():
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(15):
            time.sleep(0.4)
            if is_server_up():
                break

    ts = time.strftime("%H%M%S")
    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        ctx = browser.new_context(
            viewport={"width": 800, "height": 1280},
            device_scale_factor=2,
            has_touch=True,
            service_workers="block"
        )
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(f"{BASE_URL}/?cb={time.time()}", wait_until="networkidle", timeout=20000)
        time.sleep(1)

        page.fill("#searchInput", "CJ제일제당 햇반 210g 24개")
        page.press("#searchInput", "Enter")
        page.wait_for_selector("#priceComparisonGrid .rank-card", timeout=15000)
        time.sleep(1.5)

        tab_metrics = page.evaluate("""() => {
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
                device: "Tablet 800x1280",
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

        print(f"[TAB_HERO_BASELINE]{json.dumps(tab_metrics, indent=2)}[/TAB_HERO_BASELINE]")

        snap_tab_hero = os.path.join(ARTIFACT_DIR, f"current_tablet_hero_card_baseline_{ts}.png")
        page.evaluate("document.querySelector('#resultView section:nth-of-type(1)').scrollIntoView({ behavior: 'instant', block: 'start' })")
        time.sleep(0.5)
        page.screenshot(path=snap_tab_hero, full_page=False)
        print(f"[✓] Tablet hero baseline screenshot: {snap_tab_hero}")

        browser.close()

finally:
    if server_proc:
        server_proc.terminate()
        server_proc.wait()
