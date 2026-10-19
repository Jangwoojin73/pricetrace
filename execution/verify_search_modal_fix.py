# -*- coding: utf-8 -*-
import sys
import io
import json
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def run_verification():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # Scenario 1: Mobile - Tapping Top Search Input & Pressing Enter
        # -------------------------------------------------------------
        print("=== Scenario 1: Mobile Top Search Bar Direct Search ===")
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = m_ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        page.wait_for_timeout(500)

        # 1. Tap top search bar
        page.tap("#searchInput")
        page.wait_for_timeout(300)

        # Check if radarSearchModal opened on simple tap
        modal_state_on_tap = page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            return {
                isOpen: m.classList.contains("modal-open"),
                isHidden: m.classList.contains("modal-hidden"),
                visibility: window.getComputedStyle(m).visibility,
                opacity: window.getComputedStyle(m).opacity
            };
        }''')
        print(f"Modal state immediately after tapping #searchInput: {modal_state_on_tap}")

        # 2. Type query directly and press Enter
        page.fill("#searchInput", "신라면 20개")
        page.press("#searchInput", "Enter")

        # 3. Wait for resultView to be visible
        page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        page.wait_for_timeout(1000)

        modal_state_after_search = page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            const style = window.getComputedStyle(m);
            return {
                isOpen: m.classList.contains("modal-open"),
                isHidden: m.classList.contains("modal-hidden"),
                visibility: style.visibility,
                opacity: style.opacity,
                pointerEvents: style.pointerEvents
            };
        }''')
        result_visible = page.is_visible("#resultView")
        print(f"ResultView visible: {result_visible}, Modal state after search: {modal_state_after_search}")

        shot1_path = os.path.join(ARTIFACT_DIR, "scenario1_mobile_top_search_result.png")
        page.screenshot(path=shot1_path, full_page=False)
        print(f"Screenshot saved: {shot1_path}")

        results["scenario1_mobile_top_search"] = {
            "result_view_visible": result_visible,
            "modal_open": modal_state_after_search["isOpen"],
            "modal_hidden": modal_state_after_search["isHidden"],
            "modal_visibility": modal_state_after_search["visibility"],
            "modal_opacity": modal_state_after_search["opacity"],
            "modal_overlaps_results": (result_visible and modal_state_after_search["isOpen"]),
            "screenshot": shot1_path
        }

        # -------------------------------------------------------------
        # Scenario 2: Mobile - Tapping Bottom [레이더] Tab & Submitting Search
        # -------------------------------------------------------------
        print("\n=== Scenario 2: Mobile Bottom [레이더] Tab Search ===")
        page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        page.wait_for_timeout(500)

        # 1. Tap bottom [레이더] tab
        page.tap("#mobileNavSearchFabBtn")
        page.wait_for_timeout(400)

        modal_state_open = page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            return {
                isOpen: m.classList.contains("modal-open"),
                isHidden: m.classList.contains("modal-hidden"),
                visibility: window.getComputedStyle(m).visibility,
                activeId: document.activeElement ? document.activeElement.id : "none"
            };
        }''')
        print(f"Modal state after tapping [레이더] tab: {modal_state_open}")

        shot2_modal_path = os.path.join(ARTIFACT_DIR, "scenario2_mobile_radar_modal_open.png")
        page.screenshot(path=shot2_modal_path, full_page=False)

        # 2. Type query into modal search input and submit
        page.fill("#modalSearchInput", "햇반 24개")
        page.click("#modalSearchForm button[type='submit']")

        # 3. Wait for resultView to be visible
        page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        page.wait_for_timeout(1000)

        modal_state_after_modal_search = page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            const style = window.getComputedStyle(m);
            return {
                isOpen: m.classList.contains("modal-open"),
                isHidden: m.classList.contains("modal-hidden"),
                visibility: style.visibility,
                opacity: style.opacity,
                pointerEvents: style.pointerEvents
            };
        }''')
        result_visible_2 = page.is_visible("#resultView")
        print(f"ResultView visible: {result_visible_2}, Modal state after modal search: {modal_state_after_modal_search}")

        shot2_result_path = os.path.join(ARTIFACT_DIR, "scenario2_mobile_radar_modal_search_result.png")
        page.screenshot(path=shot2_result_path, full_page=False)
        print(f"Screenshot saved: {shot2_result_path}")

        results["scenario2_mobile_radar_tab_search"] = {
            "result_view_visible": result_visible_2,
            "modal_open": modal_state_after_modal_search["isOpen"],
            "modal_hidden": modal_state_after_modal_search["isHidden"],
            "modal_visibility": modal_state_after_modal_search["visibility"],
            "modal_opacity": modal_state_after_modal_search["opacity"],
            "modal_overlaps_results": (result_visible_2 and modal_state_after_modal_search["isOpen"]),
            "screenshot": shot2_result_path
        }

        # -------------------------------------------------------------
        # Scenario 3: Tablet - Dual Tab and Search Execution
        # -------------------------------------------------------------
        print("\n=== Scenario 3: Tablet Viewport (iPad Pro 11: 834 x 1194) ===")
        t_ctx = browser.new_context(
            viewport={'width': 834, 'height': 1194},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
        )
        t_page = t_ctx.new_page()
        t_page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        t_page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        t_page.wait_for_timeout(500)

        t_page.fill("#searchInput", "코카콜라 제로 24캔")
        t_page.press("#searchInput", "Enter")
        t_page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        t_page.wait_for_timeout(1000)

        t_modal_state = t_page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            const style = window.getComputedStyle(m);
            return {
                isOpen: m.classList.contains("modal-open"),
                isHidden: m.classList.contains("modal-hidden"),
                visibility: style.visibility,
                opacity: style.opacity
            };
        }''')
        t_result_visible = t_page.is_visible("#resultView")
        print(f"Tablet ResultView visible: {t_result_visible}, Modal state: {t_modal_state}")

        shot3_path = os.path.join(ARTIFACT_DIR, "scenario3_tablet_search_result.png")
        t_page.screenshot(path=shot3_path, full_page=False)
        print(f"Screenshot saved: {shot3_path}")

        results["scenario3_tablet_search"] = {
            "result_view_visible": t_result_visible,
            "modal_open": t_modal_state["isOpen"],
            "modal_hidden": t_modal_state["isHidden"],
            "modal_visibility": t_modal_state["visibility"],
            "modal_opacity": t_modal_state["opacity"],
            "modal_overlaps_results": (t_result_visible and t_modal_state["isOpen"]),
            "screenshot": shot3_path
        }

        # -------------------------------------------------------------
        # Scenario 4: Desktop Viewport (1280 x 900)
        # -------------------------------------------------------------
        print("\n=== Scenario 4: Desktop Viewport (1280 x 900) ===")
        d_ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        d_page = d_ctx.new_page()
        d_page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        d_page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        d_page.wait_for_timeout(500)

        d_page.fill("#searchInput", "커클랜드 휴지 30롤")
        d_page.press("#searchInput", "Enter")
        d_page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=10000)
        d_page.wait_for_timeout(1000)

        d_modal_state = d_page.evaluate('''() => {
            const m = document.querySelector("#radarSearchModal");
            const style = window.getComputedStyle(m);
            return {
                isOpen: m.classList.contains("modal-open"),
                isHidden: m.classList.contains("modal-hidden"),
                visibility: style.visibility,
                opacity: style.opacity
            };
        }''')
        d_result_visible = d_page.is_visible("#resultView")
        print(f"Desktop ResultView visible: {d_result_visible}, Modal state: {d_modal_state}")

        shot4_path = os.path.join(ARTIFACT_DIR, "scenario4_desktop_search_result.png")
        d_page.screenshot(path=shot4_path, full_page=False)
        print(f"Screenshot saved: {shot4_path}")

        results["scenario4_desktop_search"] = {
            "result_view_visible": d_result_visible,
            "modal_open": d_modal_state["isOpen"],
            "modal_hidden": d_modal_state["isHidden"],
            "modal_visibility": d_modal_state["visibility"],
            "modal_opacity": d_modal_state["opacity"],
            "modal_overlaps_results": (d_result_visible and d_modal_state["isOpen"]),
            "screenshot": shot4_path
        }

        # Save raw audit summary
        summary_path = os.path.join(ARTIFACT_DIR, "search_modal_audit_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("\n=== Verification Complete ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))

        browser.close()

if __name__ == "__main__":
    run_verification()
