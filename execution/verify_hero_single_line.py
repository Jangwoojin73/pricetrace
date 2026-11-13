# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

def is_server_up():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/status", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

try:
    if not is_server_up():
        print("[*] Starting local server.py on port 8080...")
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(15):
            time.sleep(0.4)
            if is_server_up():
                print("[✓] Server ready!")
                break

    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    ts = time.strftime("%H%M%S")
    snap_pc = os.path.join(ARTIFACT_DIR, f"verify_hero_single_line_pc_{ts}.png")
    snap_closeup = os.path.join(ARTIFACT_DIR, f"verify_hero_single_line_closeup_{ts}.png")
    snap_mobile = os.path.join(ARTIFACT_DIR, f"verify_hero_single_line_mobile_{ts}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 1. PC 1440x900
        ctx_pc = browser.new_context(viewport={"width": 1440, "height": 900})
        page_pc = ctx_pc.new_page()
        page_pc.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_pc.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle")
        page_pc.wait_for_selector("#welcomeHeroSection", timeout=8000)
        page_pc.wait_for_timeout(500)

        # Line count & Height verification
        pc_metrics = page_pc.evaluate('''() => {
            const h = document.getElementById("welcomeHeroSection");
            const p = h ? h.querySelector("p.text-slate-100") : null;
            const pRect = p ? p.getBoundingClientRect() : null;
            const lineHeight = p ? parseFloat(window.getComputedStyle(p).lineHeight) : 0;
            const computedHeight = pRect ? pRect.height : 0;
            const isSingleLine = lineHeight > 0 ? (computedHeight <= lineHeight * 1.5) : false;
            return {
                measuredAt: new Date().toLocaleTimeString(),
                pText: p ? p.innerText.trim() : "",
                pWidth: pRect ? Math.round(pRect.width) : 0,
                pHeight: pRect ? Math.round(pRect.height) : 0,
                lineHeight: Math.round(lineHeight),
                isSingleLine: isSingleLine
            };
        }''')
        print("PC Single Line Metrics:", pc_metrics)

        # Screenshot PC
        page_pc.screenshot(path=snap_pc)
        print(f"[✓] Saved PC screenshot: {snap_pc} ({os.path.getsize(snap_pc)} bytes)")

        # Closeup of Hero
        hero_elem = page_pc.locator("#welcomeHeroSection")
        hero_elem.screenshot(path=snap_closeup)
        print(f"[✓] Saved Hero closeup: {snap_closeup} ({os.path.getsize(snap_closeup)} bytes)")
        ctx_pc.close()

        # 2. Mobile 393x852 (반응형 점검)
        ctx_m = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page_m = ctx_m.new_page()
        page_m.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page_m.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle")
        page_m.wait_for_selector("#welcomeHeroSection", timeout=8000)
        page_m.wait_for_timeout(500)

        m_metrics = page_m.evaluate('''() => {
            const p = document.querySelector("#welcomeHeroSection p.text-slate-100");
            const rect = p ? p.getBoundingClientRect() : null;
            return {
                width: rect ? Math.round(rect.width) : 0,
                height: rect ? Math.round(rect.height) : 0,
                hasOverflow: document.documentElement.scrollWidth > window.innerWidth
            };
        }''')
        print("Mobile Metrics (No overflow check):", m_metrics)

        page_m.screenshot(path=snap_mobile)
        print(f"[✓] Saved Mobile screenshot: {snap_mobile} ({os.path.getsize(snap_mobile)} bytes)")
        ctx_m.close()

        browser.close()

finally:
    if server_proc:
        server_proc.terminate()
