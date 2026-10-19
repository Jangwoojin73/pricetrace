# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

def test_modal_behavior():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Test A: Mobile viewport (393 x 852)
        print("=== Test A: Mobile Viewport ===")
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = m_ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        page.wait_for_timeout(1000)

        # 1. Tap top searchInput on mobile
        print("1. Tapping #searchInput on mobile...")
        page.tap("#searchInput")
        page.wait_for_timeout(500)
        
        modal_classes = page.evaluate('() => document.querySelector("#radarSearchModal").className')
        print(f"Modal classes after tap searchInput: {modal_classes}")

        # 2. Type query into search
        # If modal is open, modalSearchInput or searchInput has focus
        active_id = page.evaluate('() => document.activeElement ? document.activeElement.id : "none"')
        print(f"Active element after tap searchInput: {active_id}")

        # Type in modalSearchInput or searchInput
        if active_id == "modalSearchInput":
            print("Typing '신라면 20개' into #modalSearchInput and pressing Enter...")
            page.fill("#modalSearchInput", "신라면 20개")
            page.press("#modalSearchInput", "Enter")
        else:
            print("Typing '신라면 20개' into #searchInput and pressing Enter...")
            page.fill("#searchInput", "신라면 20개")
            page.press("#searchInput", "Enter")

        # Wait for search execution
        page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        page.wait_for_timeout(1000)

        # Check modal state now!
        modal_open = page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            if (!m) return false;
            const style = window.getComputedStyle(m);
            return {
                className: m.className,
                display: style.display,
                visibility: style.visibility,
                opacity: style.opacity,
                pointerEvents: style.pointerEvents,
                isOpenClass: m.classList.contains("modal-open"),
                isHiddenClass: m.classList.contains("modal-hidden")
            };
        }''')
        print(f"Modal state AFTER search execution on mobile:\n {modal_open}")

        # Check if result items and modal are both visible
        results_visible = page.is_visible("#resultView")
        modal_visible = page.is_visible("#radarSearchModal")
        print(f"ResultView visible: {results_visible}, RadarModal visible: {modal_visible}")

        # Test B: Tap [레이더] Tab, type and submit
        print("\n=== Test B: Mobile [레이더] Tab tap and search ===")
        page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        page.wait_for_timeout(500)
        print("Tapping #mobileNavSearchFabBtn ([레이더] tab)...")
        page.tap("#mobileNavSearchFabBtn")
        page.wait_for_timeout(500)
        page.fill("#modalSearchInput", "햇반 24개")
        print("Submitting #modalSearchForm...")
        page.click("#modalSearchForm button[type='submit']")
        page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        page.wait_for_timeout(1000)
        modal_state_b = page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            return {
                className: m.className,
                isOpenClass: m.classList.contains("modal-open"),
                isHiddenClass: m.classList.contains("modal-hidden"),
                isVisible: m.offsetParent !== null
            };
        }''')
        print(f"Modal state B:\n {modal_state_b}")

        # Test C: Desktop viewport (1280 x 900)
        print("\n=== Test C: Desktop Viewport ===")
        d_ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        d_page = d_ctx.new_page()
        d_page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        d_page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        d_page.wait_for_timeout(500)
        d_page.fill("#searchInput", "코카콜라 제로")
        d_page.press("#searchInput", "Enter")
        d_page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        d_page.wait_for_timeout(1000)
        modal_state_c = d_page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            return {
                className: m.className,
                isOpenClass: m.classList.contains("modal-open"),
                isHiddenClass: m.classList.contains("modal-hidden")
            };
        }''')
        print(f"Modal state C (Desktop):\n {modal_state_c}")

        browser.close()

if __name__ == "__main__":
    test_modal_behavior()
