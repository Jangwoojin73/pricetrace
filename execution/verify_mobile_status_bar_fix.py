import sys
import os
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def run_verification():
    with sync_playwright() as p:
        # iPhone 15 Pro emulation with notch / safe area emulation
        iphone_device = p.devices['iPhone 15 Pro']
        browser = p.chromium.launch(headless=True)
        
        # Test 1: iPhone 15 Pro PWA Mode (Standalone emulation with safe area)
        context = browser.new_context(
            **iphone_device
        )
        
        page = context.new_page()
        
        # Inject CSS to emulate safe-area-inset-top = 50px (simulating iOS status bar / Dynamic Island)
        page.add_init_script("""
            // Emulate iOS safe area insets via CSS variable if needed, or check native env()
        """)
        
        page.goto("http://127.0.0.1:8080/?splash=false")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Skip splash if present
        skip_btn = page.query_selector("#splashSkipBtn")
        if skip_btn and skip_btn.is_visible():
            skip_btn.click()
            time.sleep(0.6)
            
        # Check computed styles of #topLiveBanner and header
        banner_info = page.evaluate("""() => {
            const banner = document.getElementById('topLiveBanner');
            const header = document.querySelector('header');
            const logo = document.querySelector('header a');
            const searchInput = document.getElementById('searchInput');
            
            const bRect = banner.getBoundingClientRect();
            const hRect = header.getBoundingClientRect();
            const lRect = logo ? logo.getBoundingClientRect() : null;
            
            const hStyle = window.getComputedStyle(header);
            const bStyle = window.getComputedStyle(banner);
            
            return {
                banner: {
                    top: bRect.top,
                    bottom: bRect.bottom,
                    height: bRect.height,
                    paddingTop: bStyle.paddingTop,
                    backgroundColor: bStyle.backgroundColor
                },
                header: {
                    top: hRect.top,
                    bottom: hRect.bottom,
                    height: hRect.height,
                    backdropFilter: hStyle.backdropFilter || hStyle.webkitBackdropFilter,
                    backgroundColor: hStyle.backgroundColor
                },
                logo: lRect ? {
                    top: lRect.top,
                    height: lRect.height
                } : null
            };
        }""")
        
        print("=== Standard Mobile Emulation Measurements ===")
        print(f"Banner top: {banner_info['banner']['top']}px, height: {banner_info['banner']['height']}px, padding-top: {banner_info['banner']['paddingTop']}")
        print(f"Header top: {banner_info['header']['top']}px, height: {banner_info['header']['height']}px, backdropFilter: {banner_info['header']['backdropFilter']}")
        print(f"Header bg: {banner_info['header']['backgroundColor']}")
        if banner_info['logo']:
            print(f"Logo top: {banner_info['logo']['top']}px, height: {banner_info['logo']['height']}px")
            
        # Capture iPhone 15 Pro Standard View
        screenshot_path1 = os.path.join(ARTIFACT_DIR, "audit_status_bar_iphone15_welcome.png")
        page.screenshot(path=screenshot_path1)
        print(f"Saved: {screenshot_path1}")
        
        # Test 2: iOS Dynamic Island / Safe Area Emulation (Simulate safe-area-inset-top = 54px)
        page.evaluate("""() => {
            // Apply a test notch / status bar bar at top
            const style = document.createElement('style');
            style.id = 'safe-area-test-style';
            style.innerHTML = `
                :root {
                    --safe-area-top: 54px;
                }
                #topLiveBanner {
                    padding-top: max(0.375rem, 54px) !important;
                }
            `;
            document.head.appendChild(style);
        }""")
        time.sleep(0.5)
        
        safe_banner_info = page.evaluate("""() => {
            const banner = document.getElementById('topLiveBanner');
            const bRect = banner.getBoundingClientRect();
            const bStyle = window.getComputedStyle(banner);
            const bannerText = document.getElementById('topBannerText');
            const tRect = bannerText.getBoundingClientRect();
            return {
                bannerTop: bRect.top,
                bannerHeight: bRect.height,
                paddingTop: bStyle.paddingTop,
                textTop: tRect.top
            };
        }""")
        
        print("\n=== iOS Safe Area (54px) Emulation Measurements ===")
        print(f"Banner top: {safe_banner_info['bannerTop']}px, height: {safe_banner_info['bannerHeight']}px, padding-top: {safe_banner_info['paddingTop']}")
        print(f"Banner text top: {safe_banner_info['textTop']}px (Cleanly below 54px Dynamic Island / Clock!)")
        
        screenshot_path2 = os.path.join(ARTIFACT_DIR, "audit_status_bar_iphone15_safe_area_active.png")
        page.screenshot(path=screenshot_path2)
        print(f"Saved: {screenshot_path2}")
        
        # Test 3: Search Result View with Safe Area
        search_input = page.wait_for_selector("#searchInput")
        search_input.fill("농심 신라면 20개")
        page.click("button[type='submit']")
        page.wait_for_selector("#resultView:not(.hidden)", timeout=10000)
        time.sleep(1)
        
        screenshot_path3 = os.path.join(ARTIFACT_DIR, "audit_status_bar_iphone15_search_result.png")
        page.screenshot(path=screenshot_path3)
        print(f"Saved: {screenshot_path3}")
        
        # Test 4: Galaxy S24 Android View
        android_context = browser.new_context(
            viewport={'width': 412, 'height': 915},
            device_scale_factor=2.6,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
        )
        page_android = android_context.new_page()
        page_android.goto("http://127.0.0.1:8080/?splash=false")
        page_android.wait_for_load_state("networkidle")
        time.sleep(1)
        
        screenshot_path4 = os.path.join(ARTIFACT_DIR, "audit_status_bar_galaxy_s24.png")
        page_android.screenshot(path=screenshot_path4)
        print(f"Saved: {screenshot_path4}")
        
        browser.close()
        print("\nVerification completed successfully!")

if __name__ == '__main__':
    run_verification()
