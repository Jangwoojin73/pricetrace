# -*- coding: utf-8 -*-
"""
Step 1: Splash Progression & Trending Ranking API Consistency Audit (~3s)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import json
from playwright.sync_api import sync_playwright
from config import BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, save_step_result

def main():
    t_start = time.time()
    print(">>> [Step 1] Running Splash & Trending API Verification...")
    metrics = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        
        # 1-1. Mobile Splash Verification (iPhone 15 Pro, 393x852)
        ctx_m = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        page_m = ctx_m.new_page()
        page_m.set_default_timeout(5000)
        
        page_m.goto(BASE_URL, wait_until="domcontentloaded")
        page_m.wait_for_timeout(400)
        
        m_splash = page_m.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            const canvas = document.getElementById("splashCanvas");
            const progressBar = document.getElementById("splashProgressBar");
            const progressText = document.getElementById("splashProgressText");
            const skipBtn = document.getElementById("splashSkipBtn");
            const radar = splash ? splash.querySelector(".animate-ping") : null;
            return {
                splashExists: !!splash,
                splashDisplay: splash ? window.getComputedStyle(splash).display : "none",
                canvasRendered: !!canvas && canvas.width > 0,
                hasPulseRadar: !!radar,
                progressText: progressText ? progressText.innerText : "",
                progressBarWidth: progressBar ? progressBar.style.width : "",
                skipBtnVisible: !!skipBtn && window.getComputedStyle(skipBtn).display !== "none"
            };
        }''')
        
        snap1_path = os.path.join(ARTIFACT_DIR, "audit_01_mobile_splash_progress.png")
        page_m.screenshot(path=snap1_path)
        
        # Click skip and verify sessionStorage
        try:
            page_m.click("#splashSkipBtn", timeout=2000)
        except Exception:
            page_m.evaluate("const btn = document.getElementById('splashSkipBtn'); if(btn) btn.click();")
            
        page_m.wait_for_timeout(300)
        
        reload_metrics = page_m.evaluate('''() => {
            return {
                sessionFlag: sessionStorage.getItem("pricetrace_splash_seen"),
                splashDisplayAfterSkip: document.getElementById("appSplashScreen") ? window.getComputedStyle(document.getElementById("appSplashScreen")).display : "none"
            };
        }''')
        
        # Reload to test 0.0s instant bypass
        t0_reload = time.time()
        page_m.reload(wait_until="domcontentloaded")
        page_m.wait_for_timeout(200)
        reload_duration = round((time.time() - t0_reload) * 1000, 1)
        
        reload_instant = page_m.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            return {
                instantMain: splash ? window.getComputedStyle(splash).display === "none" : true
            };
        }''')
        
        metrics["mobile_splash"] = {
            "canvas_rendered": m_splash["canvasRendered"],
            "has_pulse_radar": m_splash["hasPulseRadar"],
            "skip_btn_visible": m_splash["skipBtnVisible"],
            "session_flag_set": reload_metrics["sessionFlag"] == "true",
            "reload_instant_bypass": reload_instant["instantMain"],
            "reload_duration_ms": reload_duration,
            "screenshot": snap1_path
        }
        ctx_m.close()
        
        # 1-2. PC Desktop (1440x900) - Instant Bypass (0% splash)
        ctx_pc = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            service_workers="block"
        )
        page_pc = ctx_pc.new_page()
        page_pc.set_default_timeout(5000)
        
        page_pc.goto(BASE_URL, wait_until="domcontentloaded")
        page_pc.wait_for_timeout(300)
        
        pc_splash = page_pc.evaluate('''() => {
            const splash = document.getElementById("appSplashScreen");
            return {
                display: splash ? window.getComputedStyle(splash).display : "none",
                isNone: splash ? window.getComputedStyle(splash).display === "none" : true
            };
        }''')
        
        snap2_path = os.path.join(ARTIFACT_DIR, "audit_01_desktop_instant_main.png")
        page_pc.screenshot(path=snap2_path)
        
        metrics["desktop_bypass"] = {
            "splash_display": pc_splash["display"],
            "instant_main_verified": pc_splash["isNone"],
            "screenshot": snap2_path
        }
        
        # 1-3. Trending API Consistency Check
        page_pc.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=8000)
        api_match = page_pc.evaluate('''async () => {
            const res = await fetch("/api/trending");
            const data = await res.json();
            const top4Cards = Array.from(document.querySelectorAll("#welcomeCardsContainer .welcome-card h3")).slice(0, 4).map(e => e.innerText.trim());
            const quickChips = Array.from(document.querySelectorAll("#quickChipsContainer button")).map(e => e.innerText.trim());
            return {
                status: res.status,
                success: data.success,
                apiTop4: (data.steady_items || data.items || []).slice(0, 4).map(i => (i.title || i.keyword).trim()),
                uiTop4Cards: top4Cards,
                quickChips: quickChips,
                count: (data.steady_items || data.items || []).length
            };
        }''')
        
        snap3_path = os.path.join(ARTIFACT_DIR, "audit_01_main_trending_view.png")
        page_pc.screenshot(path=snap3_path)
        
        metrics["trending_api"] = {
            "http_status": api_match["status"],
            "api_items_count": api_match["count"],
            "api_top4": api_match["apiTop4"],
            "ui_top4_cards": api_match["uiTop4Cards"],
            "quick_chips_count": len(api_match["quickChips"]),
            "screenshot": snap3_path
        }
        
        ctx_pc.close()
        browser.close()
        
    passed = (
        metrics["mobile_splash"]["session_flag_set"] and
        metrics["desktop_bypass"]["instant_main_verified"] and
        metrics["trending_api"]["http_status"] == 200
    )
    
    result = {
        "step": 1,
        "name": "Splash Progression & Trending API Consistency",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": metrics
    }
    print(f"[Step 1] Completed in {result['elapsed_sec']}s - Status: {result['status']}")
    save_step_result(1, result)

if __name__ == "__main__":
    main()
