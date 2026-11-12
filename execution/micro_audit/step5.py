# -*- coding: utf-8 -*-
"""
Step 5: Bottom Navigation (5 Tabs & 25px Badges), Dual Tab Scroll Lock,
Real-Touch Pull-to-Refresh (PTR), and Mobile Search Bar Smart Scroll & Anti-Jitter Audit
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, MOBILE_UA,
    save_step_result, create_sentinel, collect_broken_images, sentinel_summary, safe_screenshot
)


def main():
    t_start = time.time()
    print(">>> [Step 5] Auditing Bottom Nav (25px Badges), Scroll Lock, Real-Touch PTR & Search Bar Smart Scroll...")
    metrics = {}
    s_all = {"console_errors": [], "page_errors": [], "http_errors": [], "failed_requests": [], "broken_images_count": 0, "broken_image_srcs": []}

    def merge_s(s):
        for k in ["console_errors", "page_errors", "http_errors", "failed_requests", "broken_image_srcs"]:
            s_all[k].extend(s[k])
        s_all["broken_images_count"] += s["broken_images_count"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # -----------------------------------------------------------------
        # 5-1. Mobile Full UX Suite (iPhone 15 Pro, 393x852)
        # -----------------------------------------------------------------
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent=MOBILE_UA,
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_m = m_ctx.new_page()
        p_m.set_default_timeout(10000)
        s_m = create_sentinel(p_m)
        p_m.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_m.goto(BASE_URL, wait_until="domcontentloaded")
        p_m.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=8000)
        p_m.wait_for_timeout(600)

        # (A) Bottom Nav 5 Tabs Baseline & 25px Hero Nav Badges (v1.5.7)
        dock_metrics = p_m.evaluate('''() => {
            const nav = document.getElementById("mobileBottomNav");
            const navRect = nav ? nav.getBoundingClientRect() : null;
            const btnIds = ["mobileNavHomeBtn", "mobileNavSearchFabBtn", "mobileNavSteadyBtn", "mobileNavHotdealBtn", "mobileNavConfigBtn"];
            const rects = btnIds.map(id => {
                const el = document.getElementById(id);
                return el ? el.getBoundingClientRect() : null;
            });
            const bottoms = rects.map(r => r ? Math.round(r.bottom) : 0);
            const baselineDiff = Math.max(...bottoms) - Math.min(...bottoms);

            const steadyBadge = document.querySelector("#mobileNavSteadyBtn .hero-nav-badge");
            const hotdealBadge = document.querySelector("#mobileNavHotdealBtn .hero-nav-badge");
            const sRect = steadyBadge ? steadyBadge.getBoundingClientRect() : null;
            const hRect = hotdealBadge ? hotdealBadge.getBoundingClientRect() : null;

            return {
                allFound: rects.every(r => r !== null),
                baselineDiff: baselineDiff,
                steadyBadgeWidth: sRect ? Math.round(sRect.width) : 0,
                steadyBadgeHeight: sRect ? Math.round(sRect.height) : 0,
                hotdealBadgeWidth: hRect ? Math.round(hRect.width) : 0,
                hotdealBadgeHeight: hRect ? Math.round(hRect.height) : 0,
                noProtrusion: (sRect && hRect && navRect) ? (sRect.top >= navRect.top && hRect.top >= navRect.top) : false
            };
        }''')

        # (B) Default PTR Indicator Hidden Check (v1.5.8) - 96px bug gone check
        ptr_default = p_m.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const header = document.querySelector("header");
            const mainEl = document.getElementById("mainContent");
            const ptrStyle = ptr ? window.getComputedStyle(ptr) : null;
            const ptrRect = ptr ? ptr.getBoundingClientRect() : null;
            const hRect = header ? header.getBoundingClientRect() : null;
            const mRect = mainEl ? mainEl.getBoundingClientRect() : null;
            return {
                ptrDisplay: ptrStyle ? ptrStyle.display : "none",
                ptrHeight: ptrRect ? Math.round(ptrRect.height) : 0,
                headerToMainGapPx: (hRect && mRect) ? Math.round(mRect.top - hRect.bottom) : -1
            };
        }''')

        # (C) Real TouchEvent Pull-to-Refresh (PTR) Audit (v1.5.9)
        p_m.evaluate('''() => {
            const t1 = new Touch({ identifier: 1, target: document.body, clientX: 196, clientY: 300 });
            window.dispatchEvent(new TouchEvent("touchstart", { touches: [t1], targetTouches: [t1], changedTouches: [t1], cancelable: true }));
            const t2 = new Touch({ identifier: 1, target: document.body, clientX: 196, clientY: 460 });
            window.dispatchEvent(new TouchEvent("touchmove", { touches: [t2], targetTouches: [t2], changedTouches: [t2], cancelable: true }));
        }''')
        p_m.wait_for_timeout(150)

        ptr_pulled = p_m.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const header = document.querySelector("header");
            const mainEl = document.getElementById("mainContent");
            const ptrStyle = ptr ? window.getComputedStyle(ptr) : null;
            return {
                headerTopFixed: header ? Math.round(header.getBoundingClientRect().top) === 0 : false,
                mainTransform: mainEl ? mainEl.style.transform : "",
                ptrActiveClass: ptr ? ptr.classList.contains("ptr-active") : false,
                ptrDisplayDuringPull: ptrStyle ? ptrStyle.display : ""
            };
        }''')
        snap_ptr = os.path.join(ARTIFACT_DIR, "audit_05_ptr_pulled_real_touch.png")
        safe_screenshot(p_m, snap_ptr)

        # Release PTR
        p_m.evaluate('''() => {
            const tEnd = new Touch({ identifier: 1, target: document.body, clientX: 196, clientY: 460 });
            window.dispatchEvent(new TouchEvent("touchend", { touches: [], targetTouches: [], changedTouches: [tEnd], cancelable: true }));
        }''')
        p_m.wait_for_timeout(1000)

        ptr_restored = p_m.evaluate('''() => {
            const ptr = document.getElementById("ptrIndicator");
            const mainEl = document.getElementById("mainContent");
            return {
                ptrDisplayAfterRelease: ptr ? window.getComputedStyle(ptr).display : "",
                mainTransformAfterRelease: mainEl ? mainEl.style.transform : ""
            };
        }''')

        # (D) Mobile Header Search Bar Smart Scroll & Anti-Jitter 3x Shield (v1.6.0 & v1.6.1)
        p_m.evaluate("window.scrollTo({ top: 0, behavior: 'instant' });")
        p_m.wait_for_timeout(350)

        search_top = p_m.evaluate('''() => {
            const header = document.querySelector("header.sticky");
            const search = document.getElementById("gnbSearchSection");
            return {
                headerHeight: header ? Math.round(header.getBoundingClientRect().height) : 0,
                searchHeight: search ? Math.round(search.getBoundingClientRect().height) : 0,
                isCollapsed: document.body.classList.contains("header-search-collapsed")
            };
        }''')

        # MutationObserver로 토글 폭주 감시
        p_m.evaluate('''() => {
            window.__scrollToggleCount = 0;
            const obs = new MutationObserver(ms => {
                for (const m of ms) {
                    if (m.attributeName === "class") window.__scrollToggleCount++;
                }
            });
            obs.observe(document.body, { attributes: true });
        }''')

        # Wheel Down -> Search Bar Collapse + Bottom Nav Hide
        for _ in range(5):
            p_m.mouse.wheel(0, 100)
            p_m.wait_for_timeout(70)
        p_m.wait_for_timeout(500)

        search_down = p_m.evaluate('''() => {
            const header = document.querySelector("header.sticky");
            const search = document.getElementById("gnbSearchSection");
            const nav = document.getElementById("mobileBottomNav");
            return {
                scrollY: window.scrollY,
                headerHeight: header ? Math.round(header.getBoundingClientRect().height) : 0,
                searchHeight: search ? Math.round(search.getBoundingClientRect().height) : 0,
                isCollapsed: document.body.classList.contains("header-search-collapsed"),
                navHidden: nav ? nav.classList.contains("nav-dock-hidden") : false
            };
        }''')
        snap_collapsed = os.path.join(ARTIFACT_DIR, "audit_05_search_bar_collapsed.png")
        safe_screenshot(p_m, snap_collapsed)

        # Wheel Up -> Smooth Reveal without vibration
        for _ in range(3):
            p_m.mouse.wheel(0, -80)
            p_m.wait_for_timeout(70)
        p_m.wait_for_timeout(500)

        search_up = p_m.evaluate('''() => {
            const header = document.querySelector("header.sticky");
            const search = document.getElementById("gnbSearchSection");
            const nav = document.getElementById("mobileBottomNav");
            return {
                scrollY: window.scrollY,
                headerHeight: header ? Math.round(header.getBoundingClientRect().height) : 0,
                searchHeight: search ? Math.round(search.getBoundingClientRect().height) : 0,
                isCollapsed: document.body.classList.contains("header-search-collapsed"),
                navHidden: nav ? nav.classList.contains("nav-dock-hidden") : false
            };
        }''')
        snap_revealed = os.path.join(ARTIFACT_DIR, "audit_05_search_bar_revealed.png")
        safe_screenshot(p_m, snap_revealed)

        # Jitter Stress Test (5 rapid up/down oscillations)
        before_stress = p_m.evaluate("window.__scrollToggleCount")
        for i in range(5):
            p_m.mouse.wheel(0, 50 if i % 2 == 0 else -50)
            p_m.wait_for_timeout(50)
        p_m.wait_for_timeout(450)
        stress_toggles = p_m.evaluate("window.__scrollToggleCount") - before_stress

        # Search Input Focus Guard
        p_m.evaluate("window.scrollTo({ top: 0, behavior: 'instant' });")
        p_m.wait_for_timeout(350)
        p_m.evaluate("document.getElementById('searchInput').focus();")
        p_m.wait_for_timeout(150)
        for _ in range(3):
            p_m.mouse.wheel(0, 100)
            p_m.wait_for_timeout(60)
        p_m.wait_for_timeout(400)
        focus_guard = p_m.evaluate('''() => ({
            isFocused: document.activeElement === document.getElementById("searchInput"),
            collapsedDuringFocus: document.body.classList.contains("header-search-collapsed")
        })''')
        p_m.evaluate("document.getElementById('searchInput').blur();")

        # (E) Dual Tab Scroll Lock (0px Drift & Header No Overlap)
        p_m.evaluate("window.scrollTo({ top: 0, behavior: 'instant' });")
        p_m.wait_for_timeout(400)

        p_m.click("#mobileNavSteadyBtn")
        p_m.wait_for_timeout(550)
        y1_steady = round(p_m.evaluate("window.scrollY"))
        tray_clearance_steady = p_m.evaluate('''() => {
            const h = document.querySelector("header.sticky");
            const t = document.getElementById("dualTabButtonsTray");
            return (h && t) ? Math.round(t.getBoundingClientRect().top - h.getBoundingClientRect().bottom) : -1;
        }''')
        p_m.click("#mobileNavSteadyBtn")
        p_m.wait_for_timeout(450)
        y2_steady = round(p_m.evaluate("window.scrollY"))
        steady_diff = abs(y1_steady - y2_steady)
        snap_steady = os.path.join(ARTIFACT_DIR, "audit_05_mobile_steady_scroll_lock.png")
        safe_screenshot(p_m, snap_steady)

        p_m.click("#mobileNavHotdealBtn")
        p_m.wait_for_timeout(550)
        y1_hotdeal = round(p_m.evaluate("window.scrollY"))
        p_m.click("#mobileNavHotdealBtn")
        p_m.wait_for_timeout(450)
        y2_hotdeal = round(p_m.evaluate("window.scrollY"))
        hotdeal_diff = abs(y1_hotdeal - y2_hotdeal)
        snap_hotdeal = os.path.join(ARTIFACT_DIR, "audit_05_mobile_hotdeal_scroll_lock.png")
        safe_screenshot(p_m, snap_hotdeal)

        collect_broken_images(p_m, s_m)
        merge_s(s_m)

        metrics["mobile"] = {
            "dock_and_25px_badges": dock_metrics,
            "ptr": {
                "default_hidden": ptr_default,
                "during_real_touch_pull": ptr_pulled,
                "after_release": ptr_restored,
                "snap_ptr": snap_ptr
            },
            "search_bar_smart_scroll": {
                "top": search_top,
                "down_collapsed": search_down,
                "height_saved_px": search_top["headerHeight"] - search_down["headerHeight"],
                "up_revealed": search_up,
                "stress_test_5x_toggle_count": stress_toggles,
                "focus_guard": focus_guard,
                "snap_collapsed": snap_collapsed,
                "snap_revealed": snap_revealed
            },
            "dual_tab_scroll_lock": {
                "steady_diff_px": steady_diff,
                "hotdeal_diff_px": hotdeal_diff,
                "tray_header_clearance_px": tray_clearance_steady,
                "snap_steady": snap_steady,
                "snap_hotdeal": snap_hotdeal
            }
        }
        m_ctx.close()

        # -----------------------------------------------------------------
        # 5-2. Tablet (iPad Pro 11, 834x1194) Dual Tab Scroll Lock & 25px Dock
        # -----------------------------------------------------------------
        tab_ctx = browser.new_context(
            viewport={'width': 834, 'height': 1194},
            user_agent="Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_tab = tab_ctx.new_page()
        p_tab.set_default_timeout(10000)
        s_t = create_sentinel(p_tab)
        p_tab.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_tab.goto(BASE_URL, wait_until="domcontentloaded")
        p_tab.wait_for_selector("#welcomeCardsContainer .welcome-card", timeout=8000)
        p_tab.wait_for_timeout(300)

        p_tab.click("#mobileNavHotdealBtn")
        p_tab.wait_for_timeout(500)
        yt1 = round(p_tab.evaluate("window.scrollY"))
        p_tab.click("#mobileNavHotdealBtn")
        p_tab.wait_for_timeout(400)
        yt2 = round(p_tab.evaluate("window.scrollY"))
        tablet_diff = abs(yt1 - yt2)

        snap_tab = os.path.join(ARTIFACT_DIR, "audit_05_tablet_dual_tab_scroll_lock.png")
        safe_screenshot(p_tab, snap_tab)
        collect_broken_images(p_tab, s_t)
        merge_s(s_t)
        metrics["tablet"] = {"hotdeal_scroll_diff_px": tablet_diff, "snap_tab": snap_tab}
        tab_ctx.close()

        browser.close()

    s_sum = sentinel_summary(s_all)
    passed = (
        dock_metrics["baselineDiff"] <= 1
        and dock_metrics["steadyBadgeWidth"] == 25
        and dock_metrics["hotdealBadgeWidth"] == 25
        and dock_metrics["noProtrusion"]
        and ptr_default["ptrDisplay"] == "none"
        and ptr_default["ptrHeight"] == 0
        and ptr_pulled["headerTopFixed"]
        and ptr_pulled["ptrActiveClass"]
        and "translateY" in ptr_pulled["mainTransform"]
        and ptr_restored["ptrDisplayAfterRelease"] == "none"
        and search_down["isCollapsed"]
        and search_down["searchHeight"] == 0
        and search_down["navHidden"]
        and not search_up["isCollapsed"]
        and search_up["searchHeight"] >= 70
        and not search_up["navHidden"]
        and stress_toggles <= 3
        and not focus_guard["collapsedDuringFocus"]
        and steady_diff == 0
        and hotdeal_diff == 0
        and tablet_diff == 0
        and s_sum["total_errors"] == 0
    )

    result = {
        "step": 5,
        "name": "Bottom Nav (25px Badges), Scroll Lock, Real-Touch PTR & Search Bar Smart Scroll",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": s_sum,
        "metrics": metrics
    }
    print(f"[Step 5] {result['elapsed_sec']}s | Badges=25px({dock_metrics['noProtrusion']}) | PTR={ptr_pulled['ptrActiveClass']}->{ptr_restored['ptrDisplayAfterRelease']} | SearchCollapse=-{search_top['headerHeight']-search_down['headerHeight']}px (Jitter={stress_toggles}) | LockDiff={steady_diff}/{hotdeal_diff}px | Status={result['status']}")
    save_step_result(5, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
