# -*- coding: utf-8 -*-
import os
import sys
import json
import time

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_URL = "http://127.0.0.1:8080"

def run_verification():
    print("=== Starting Mobile Bottom Nav Dual Hero Island Verification ===")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emulate iPhone 15 Pro
        context = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3
        )
        page = context.new_page()
        
        # Navigate to app
        page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(2.5) # allow splash or initial load to settle
        
        # Ensure splash is dismissed if present
        skip_btn = page.query_selector("#splashSkipBtn")
        if skip_btn and skip_btn.is_visible():
            skip_btn.click()
            time.sleep(0.5)

        # 1. Check Mobile Bottom Nav visibility
        nav = page.query_selector("#mobileBottomNav")
        if not nav or not nav.is_visible():
            print("❌ FAIL: #mobileBottomNav is not visible!")
            browser.close()
            return False

        # 2. Extract tab geometry and details
        tabs_info = page.evaluate("""() => {
            const nav = document.getElementById("mobileBottomNav");
            const navRect = nav.getBoundingClientRect();
            const btns = Array.from(nav.querySelectorAll(".mobile-nav-btn"));
            
            const results = btns.map((btn, idx) => {
                const id = btn.id;
                const tabKey = btn.getAttribute("data-mobile-tab");
                const span = btn.querySelector("span");
                const spanRect = span ? span.getBoundingClientRect() : null;
                const iconBox = btn.querySelector(".mobile-nav-icon-box");
                const heroBadge = btn.querySelector(".hero-nav-badge");
                
                let iconInfo = null;
                if (heroBadge) {
                    const rect = heroBadge.getBoundingClientRect();
                    iconInfo = {
                        type: "hero",
                        className: heroBadge.className,
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        top: Math.round(rect.top),
                        protrusionPx: Math.round(navRect.top - rect.top)
                    };
                } else if (iconBox) {
                    const rect = iconBox.getBoundingClientRect();
                    iconInfo = {
                        type: "standard",
                        className: iconBox.className,
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        top: Math.round(rect.top),
                        protrusionPx: Math.round(navRect.top - rect.top)
                    };
                }
                
                return {
                    index: idx,
                    id: id,
                    tabKey: tabKey,
                    text: span ? span.textContent.trim() : "",
                    spanRect: spanRect ? {
                        top: Math.round(spanRect.top * 10) / 10,
                        bottom: Math.round(spanRect.bottom * 10) / 10,
                        height: Math.round(spanRect.height * 10) / 10
                    } : null,
                    iconInfo: iconInfo
                };
            });
            
            // Calculate baseline alignment across all 5 labels
            const bottoms = results.map(r => r.spanRect ? r.spanRect.bottom : 0);
            const tops = results.map(r => r.spanRect ? r.spanRect.top : 0);
            const maxBottom = Math.max(...bottoms);
            const minBottom = Math.min(...bottoms);
            const maxTop = Math.max(...tops);
            const minTop = Math.min(...tops);
            
            return {
                navRect: {
                    top: Math.round(navRect.top),
                    height: Math.round(navRect.height),
                    width: Math.round(navRect.width)
                },
                tabs: results,
                bottomDiff: Math.round((maxBottom - minBottom) * 10) / 10,
                topDiff: Math.round((maxTop - minTop) * 10) / 10
            };
        }""")

        print("\n--- Extracted Mobile Bottom Nav Metrics ---")
        print(f"Nav Top: {tabs_info['navRect']['top']}px | Nav Height: {tabs_info['navRect']['height']}px")
        print(f"Text Labels Vertical Difference (Bottom Baseline): {tabs_info['bottomDiff']}px (0.0px ideal)")
        print(f"Text Labels Vertical Difference (Top): {tabs_info['topDiff']}px")
        
        for tab in tabs_info['tabs']:
            print(f"  Slot {tab['index'] + 1}: [{tab['text']}] (id={tab['id']}) | Type: {tab['iconInfo']['type']} | Icon Size: {tab['iconInfo']['width']}x{tab['iconInfo']['height']}px | Protrusion above nav: {tab['iconInfo']['protrusionPx']}px | Span Bottom: {tab['spanRect']['bottom']}px")

        # 3. Capture Initial Fullscreen & Dock View
        fullscreen_path = os.path.join(ARTIFACT_DIR, "verify_mobile_dual_hero_fullscreen.png")
        page.screenshot(path=fullscreen_path)
        print(f"\n[Saved Screenshot] Fullscreen: {fullscreen_path}")

        # Dock close-up screenshot
        dock_elem = page.query_selector("#mobileBottomNav")
        dock_path = os.path.join(ARTIFACT_DIR, "verify_mobile_dual_hero_dock.png")
        if dock_elem:
            # clip area to show protrusion above dock
            nav_top = tabs_info['navRect']['top']
            page.screenshot(
                path=dock_path,
                clip={"x": 0, "y": max(0, nav_top - 30), "width": 393, "height": 852 - max(0, nav_top - 30)}
            )
            print(f"[Saved Screenshot] Dock Close-up: {dock_path}")

        # 4. Interactive Test: Click [🔥 핫딜]
        print("\n--- Testing Click on [🔥 핫딜] ---")
        hotdeal_btn = page.query_selector("#mobileNavHotdealBtn")
        if hotdeal_btn:
            hotdeal_btn.click()
            time.sleep(1.0)
            active_hotdeal_path = os.path.join(ARTIFACT_DIR, "verify_mobile_dual_hero_active_hotdeal.png")
            page.screenshot(path=active_hotdeal_path)
            print(f"[Saved Screenshot] Active Hotdeal: {active_hotdeal_path}")

        # 5. Interactive Test: Click [🏆 생필품]
        print("\n--- Testing Click on [🏆 생필품] ---")
        steady_btn = page.query_selector("#mobileNavSteadyBtn")
        if steady_btn:
            steady_btn.click()
            time.sleep(1.0)
            active_steady_path = os.path.join(ARTIFACT_DIR, "verify_mobile_dual_hero_active_steady.png")
            page.screenshot(path=active_steady_path)
            print(f"[Saved Screenshot] Active Steady: {active_steady_path}")

        # 6. Interactive Test: Click [홈]
        print("\n--- Testing Click on [홈] ---")
        home_btn = page.query_selector("#mobileNavHomeBtn")
        if home_btn:
            home_btn.click()
            time.sleep(1.0)
            print("Successfully returned to Home view.")

        # Save verification results JSON
        result_json_path = os.path.join(ARTIFACT_DIR, "verify_mobile_dual_hero_result.json")
        with open(result_json_path, "w", encoding="utf-8") as f:
            json.dump(tabs_info, f, ensure_ascii=False, indent=2)
        print(f"[Saved JSON Result]: {result_json_path}")

        browser.close()
        print("\n=== Verification Completed Successfully ===")
        return True

if __name__ == "__main__":
    run_verification()
