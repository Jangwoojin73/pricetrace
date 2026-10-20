import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX_FILE = os.path.join(BASE_DIR, "public", "index.html")
FILE_URL = f"file:///{INDEX_FILE.replace(os.sep, '/')}"

def main():
    print(f"Loading {FILE_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # =====================================================================
        # 1. PC Desktop (1440 x 900) Verification
        # =====================================================================
        pc_ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page_pc = pc_ctx.new_page()
        page_pc.goto(FILE_URL)
        page_pc.wait_for_load_state("load")
        time.sleep(1)

        # Measure at scrollY = 0
        pc_metrics_0 = page_pc.evaluate("""() => {
            const banner = document.getElementById('topLiveBanner');
            const gnb = document.getElementById('gnbNavBar');
            const header = document.querySelector('header');
            const bR = banner.getBoundingClientRect();
            const gR = gnb.getBoundingClientRect();
            const hR = header.getBoundingClientRect();
            return {
                scrollY: window.scrollY,
                banner: { top: bR.top, bottom: bR.bottom, height: bR.height },
                gnb: { top: gR.top, bottom: gR.bottom, height: gR.height },
                header: { top: hR.top, bottom: hR.bottom, height: hR.height }
            };
        }""")
        print("\n=== PC Desktop (1440x900) at scrollY = 0 ===")
        print(f"Header: top={pc_metrics_0['header']['top']}px, height={pc_metrics_0['header']['height']}px")
        print(f"Banner: top={pc_metrics_0['banner']['top']}px, height={pc_metrics_0['banner']['height']}px")
        print(f"GNB   : top={pc_metrics_0['gnb']['top']}px, height={pc_metrics_0['gnb']['height']}px")

        # Scroll down 650px on PC
        page_pc.evaluate("window.scrollTo(0, 650)")
        time.sleep(1)

        pc_metrics_650 = page_pc.evaluate("""() => {
            const banner = document.getElementById('topLiveBanner');
            const gnb = document.getElementById('gnbNavBar');
            const header = document.querySelector('header');
            const bR = banner.getBoundingClientRect();
            const gR = gnb.getBoundingClientRect();
            const hR = header.getBoundingClientRect();
            return {
                scrollY: window.scrollY,
                banner: { top: bR.top, bottom: bR.bottom, height: bR.height },
                gnb: { top: gR.top, bottom: gR.bottom, height: gR.height },
                header: { top: hR.top, bottom: hR.bottom, height: hR.height }
            };
        }""")
        print("\n=== PC Desktop (1440x900) at scrollY = 650px (SCROLLED DOWN) ===")
        print(f"Actual scrollY: {pc_metrics_650['scrollY']}px")
        print(f"Header: top={pc_metrics_650['header']['top']}px (Sticky at top: 0!)")
        print(f"Banner: top={pc_metrics_650['banner']['top']}px (STILL PINNED AT TOP: 0!)")
        print(f"GNB   : top={pc_metrics_650['gnb']['top']}px (Directly below banner!)")

        # Screenshot on PC scrolled down
        pc_scrolled_path = os.path.join(ARTIFACT_DIR, "audit_pc_sticky_live_banner_scrolled.png")
        page_pc.screenshot(path=pc_scrolled_path)
        print(f"Saved: {pc_scrolled_path}")

        # =====================================================================
        # 2. Mobile (iPhone 15 Pro) Verification
        # =====================================================================
        iphone = p.devices['iPhone 15 Pro']
        mobile_ctx = browser.new_context(**iphone)
        page_mobile = mobile_ctx.new_page()
        page_mobile.goto(FILE_URL)
        page_mobile.wait_for_load_state("load")
        time.sleep(1)

        # Dismiss splash
        page_mobile.evaluate("""() => {
            const splash = document.getElementById('appSplashScreen');
            if (splash) splash.remove();
        }""")

        # Scroll down 500px on mobile
        page_mobile.evaluate("window.scrollTo(0, 500)")
        time.sleep(1)

        mobile_metrics_500 = page_mobile.evaluate("""() => {
            const banner = document.getElementById('topLiveBanner');
            const gnb = document.getElementById('gnbNavBar');
            const header = document.querySelector('header');
            const bR = banner.getBoundingClientRect();
            const gR = gnb.getBoundingClientRect();
            return {
                scrollY: window.scrollY,
                bannerTop: bR.top,
                gnbTop: gR.top
            };
        }""")
        print(f"\n=== Mobile (iPhone 15 Pro) at scrollY = 500px ===")
        print(f"Banner top: {mobile_metrics_500['bannerTop']}px (Pinned at top!)")
        print(f"GNB top   : {mobile_metrics_500['gnbTop']}px")

        mobile_scrolled_path = os.path.join(ARTIFACT_DIR, "audit_mobile_sticky_live_banner_scrolled.png")
        page_mobile.screenshot(path=mobile_scrolled_path)
        print(f"Saved: {mobile_scrolled_path}")

        browser.close()

if __name__ == '__main__':
    main()
