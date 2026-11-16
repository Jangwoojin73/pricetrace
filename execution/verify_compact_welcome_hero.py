# -*- coding: utf-8 -*-
import os, sys, time, json, urllib.request, subprocess
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

os.environ['NO_PROXY'] = '127.0.0.1,localhost'
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def is_server_up():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/status", headers={"User-Agent": "Mozilla/5.0"})
        with opener.open(req, timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False

try:
    if not is_server_up():
        print("Launching local server on port 8080...")
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(20):
            time.sleep(0.3)
            if is_server_up():
                print("Server successfully launched!")
                break

    print("Server ready. Starting Playwright verification for compact welcome hero...")
    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    ts = time.strftime("%H%M%S")
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. MOBILE VERIFICATION (393x852)
        print("\n[Mobile 393x852 Testing]")
        ctx_mob = browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            has_touch=True,
            is_mobile=True
        )
        page_mob = ctx_mob.new_page()
        page_mob.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        target_url = f"{BASE_URL}/?cb={time.time()}"
        print(f"Navigating to mobile local target: {target_url}")
        page_mob.goto(target_url, wait_until="load", timeout=20000)
        page_mob.wait_for_selector("#welcomeHeroSection", timeout=10000)
        page_mob.wait_for_selector("#dualTabButtonsTray", timeout=10000)
        time.sleep(1.5)

        mob_metrics = page_mob.evaluate("""() => {
            const hero = document.getElementById('welcomeHeroSection');
            const r = hero ? hero.getBoundingClientRect() : null;
            const cs = hero ? window.getComputedStyle(hero) : null;
            
            const dualTabs = document.getElementById('dualTabButtonsTray');
            const dtR = dualTabs ? dualTabs.getBoundingClientRect() : null;

            const cardsContainer = document.getElementById('welcomeCardsContainer');
            const firstCard = cardsContainer ? cardsContainer.querySelector('.recommend-card') : null;
            const firstCardR = firstCard ? firstCard.getBoundingClientRect() : null;

            return {
                timestamp: new Date().toLocaleTimeString(),
                heroHeight: r ? Math.round(r.height * 10) / 10 : null,
                heroWidth: r ? Math.round(r.width * 10) / 10 : null,
                heroPadding: cs ? cs.padding : null,
                dualTabsTop: dtR ? Math.round(dtR.top * 10) / 10 : null,
                firstCardTop: firstCardR ? Math.round(firstCardR.top * 10) / 10 : null,
                viewportHeight: window.innerHeight
            };
        }""")

        results['mobile'] = mob_metrics
        print("Mobile Metrics:", json.dumps(mob_metrics, indent=2, ensure_ascii=False))

        # Screenshots
        path_hero_shot = os.path.join(ARTIFACT_DIR, f"verify_compact_welcome_hero_mobile_{ts}.png")
        page_mob.locator("#welcomeHeroSection").screenshot(path=path_hero_shot)
        print(f"Captured: {path_hero_shot}")

        path_full_first_frame = os.path.join(ARTIFACT_DIR, f"verify_mobile_welcome_full_first_frame_{ts}.png")
        page_mob.screenshot(path=path_full_first_frame, full_page=False)
        print(f"Captured: {path_full_first_frame}")

        ctx_mob.close()

        # 2. TABLET VERIFICATION (800x1280)
        print("\n[Tablet 800x1280 Testing]")
        ctx_tab = browser.new_context(
            viewport={"width": 800, "height": 1280},
            device_scale_factor=2,
            has_touch=True,
            is_mobile=False
        )
        page_tab = ctx_tab.new_page()
        page_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        page_tab.goto(target_url, wait_until="load", timeout=20000)
        page_tab.wait_for_selector("#welcomeHeroSection", timeout=10000)
        time.sleep(1.5)

        tab_metrics = page_tab.evaluate("""() => {
            const hero = document.getElementById('welcomeHeroSection');
            const r = hero ? hero.getBoundingClientRect() : null;
            const dualTabs = document.getElementById('dualTabButtonsTray');
            const dtR = dualTabs ? dualTabs.getBoundingClientRect() : null;

            return {
                timestamp: new Date().toLocaleTimeString(),
                heroHeight: r ? Math.round(r.height * 10) / 10 : null,
                dualTabsTop: dtR ? Math.round(dtR.top * 10) / 10 : null
            };
        }""")

        results['tablet'] = tab_metrics
        print("Tablet Metrics:", json.dumps(tab_metrics, indent=2, ensure_ascii=False))

        path_tab_hero = os.path.join(ARTIFACT_DIR, f"verify_compact_welcome_hero_tablet_{ts}.png")
        page_tab.locator("#welcomeHeroSection").screenshot(path=path_tab_hero)
        print(f"Captured: {path_tab_hero}")

        ctx_tab.close()
        browser.close()

    metrics_path = os.path.join(ARTIFACT_DIR, f"metrics_compact_welcome_hero_{ts}.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nAll validations completed! Metrics saved to: {metrics_path}")

finally:
    if server_proc:
        print("Terminating test server...")
        server_proc.terminate()
        server_proc.wait()
