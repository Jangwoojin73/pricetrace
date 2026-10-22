# -*- coding: utf-8 -*-
"""
test_modal_sound_vibrate_verification.py
Playwright automated E2E test verifying:
1. Modal scrolling and layout fit on mobile (iPhone 15 Pro: 393x852)
2. '미리 테스트' chime sound and haptic vibration trigger
3. Target price setting in app triggers chime sound and vibration when special price reached
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8080"
ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def run_tests():
    print("=== [PriceTrace] Modal Scroll & Sound/Vibrate Verification Started ===", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--autoplay-policy=no-user-gesture-required"]
        )
        context = browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
            service_workers="block",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
        )

        # Set sessionStorage to skip splash on initial load for instant testing
        context.add_init_script("""
            sessionStorage.setItem('pricetrace_splash_seen', 'true');
        """)

        page = context.new_page()
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}", flush=True))
        page.on("console", lambda msg: print(f"[{msg.type}] {msg.text}", flush=True))

        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(800)

        # Ensure splash is removed
        page.evaluate("""() => {
            const sp = document.getElementById('appSplashScreen');
            if (sp) sp.remove();
        }""")
        page.wait_for_timeout(300)

        # Hook functions to spy on audio & vibration calls
        page.evaluate("""() => {
            window.__spy = {
                soundCalls: 0,
                vibrateCalls: 0,
                vibratePatterns: [],
                hapticPulseCount: 0
            };

            const origPlay = window.playChimeSound;
            window.playChimeSound = function() {
                window.__spy.soundCalls++;
                if (origPlay) origPlay();
            };

            if ('vibrate' in navigator) {
                const origVib = navigator.vibrate.bind(navigator);
                navigator.vibrate = function(pat) {
                    window.__spy.vibrateCalls++;
                    window.__spy.vibratePatterns.push(pat);
                    return origVib(pat);
                };
            } else {
                navigator.vibrate = function(pat) {
                    window.__spy.vibrateCalls++;
                    window.__spy.vibratePatterns.push(pat);
                    return true;
                };
            }

            const observer = new MutationObserver((mutations) => {
                mutations.forEach((m) => {
                    if (m.type === 'attributes' && m.attributeName === 'class') {
                        if (m.target.classList.contains('haptic-pulse-active')) {
                            window.__spy.hapticPulseCount++;
                        }
                    }
                });
            });
            observer.observe(document.body, { attributes: true, subtree: true });
        }""")

        print("\n--- [Step 1: Modal Scroll & Viewport Fit Test on Mobile] ---", flush=True)
        # Click 5th tab '설정' (#mobileNavConfigBtn) in bottom dock
        page.click("#mobileNavConfigBtn")
        page.wait_for_timeout(500)

        classes = page.evaluate("() => document.getElementById('configModal') ? document.getElementById('configModal').className : 'none'")
        print("configModal classes:", classes, flush=True)

        # Check #configModal visibility
        assert page.is_visible("#configModal"), f"#configModal did not open! classes: {classes}"

        # Check inner card height and body scrollability
        modal_metrics = page.evaluate("""() => {
            const modal = document.getElementById('configModal');
            const card = modal.querySelector('div.bg-white');
            const body = card.querySelector('.overflow-y-auto');
            const saveBtn = document.getElementById('saveConfigModalBtn');
            const cardRect = card.getBoundingClientRect();
            const saveBtnRect = saveBtn.getBoundingClientRect();

            // Test scrolling down
            const initialScrollTop = body.scrollTop;
            body.scrollTop = 120;
            const scrolledTop = body.scrollTop;

            return {
                windowHeight: window.innerHeight,
                cardHeight: cardRect.height,
                cardMaxH: window.getComputedStyle(card).maxHeight,
                bodyScrollHeight: body.scrollHeight,
                bodyClientHeight: body.clientHeight,
                isBodyScrollable: body.scrollHeight > body.clientHeight,
                didScroll: scrolledTop > 0,
                scrolledTop: scrolledTop,
                saveBtnVisible: saveBtnRect.bottom <= window.innerHeight && saveBtnRect.top >= 0,
                saveBtnY: saveBtnRect.top
            };
        }""")

        print(f" - Window Height: {modal_metrics['windowHeight']}px", flush=True)
        print(f" - Modal Card Height: {modal_metrics['cardHeight']:.1f}px (fits <= {modal_metrics['windowHeight']}px: {modal_metrics['cardHeight'] <= modal_metrics['windowHeight']})", flush=True)
        print(f" - Body scrollHeight: {modal_metrics['bodyScrollHeight']}px vs clientHeight: {modal_metrics['bodyClientHeight']}px", flush=True)
        print(f" - Body is scrollable: {modal_metrics['isBodyScrollable']}, did scroll: {modal_metrics['didScroll']} (scrollTop={modal_metrics['scrolledTop']}px)", flush=True)
        print(f" - Save Button fully visible without clipping: {modal_metrics['saveBtnVisible']} (Y={modal_metrics['saveBtnY']:.1f}px)", flush=True)

        shot1 = os.path.join(ARTIFACT_DIR, "audit_mobile_modal_scroll_verified.png")
        page.screenshot(path=shot1, timeout=5000, animations="disabled")
        print(f" -> Captured {shot1}", flush=True)

        assert modal_metrics['cardHeight'] <= modal_metrics['windowHeight'], "Modal card exceeds screen height!"
        assert modal_metrics['saveBtnVisible'], "Save button is clipped or off-screen!"

        print("\n--- [Step 2: '미리 테스트' Button Sound & Vibration Test] ---", flush=True)
        initial_sound = page.evaluate("() => window.__spy.soundCalls")
        initial_vibrate = page.evaluate("() => window.__spy.vibrateCalls")

        page.click("#testNotificationBtn")
        page.wait_for_timeout(500)

        post_sound = page.evaluate("() => window.__spy.soundCalls")
        post_vibrate = page.evaluate("() => window.__spy.vibrateCalls")
        vibrate_patterns = page.evaluate("() => window.__spy.vibratePatterns")
        toast_text = page.evaluate("() => { const t = document.getElementById('toastMessage'); return t ? t.textContent : ''; }")
        haptic_count = page.evaluate("() => window.__spy.hapticPulseCount")

        print(f" - Sound count: {initial_sound} -> {post_sound} (Played: {post_sound > initial_sound})", flush=True)
        print(f" - Vibrate count: {initial_vibrate} -> {post_vibrate} (Triggered: {post_vibrate > initial_vibrate})", flush=True)
        print(f" - Vibrate pattern args: {vibrate_patterns}", flush=True)
        print(f" - Visual haptic pulse count: {haptic_count}", flush=True)
        print(f" - Toast notification text: '{toast_text}'", flush=True)

        assert post_sound > initial_sound, "Sound did not play on '미리 테스트'!"
        assert post_vibrate > initial_vibrate, "Vibrate was not called on '미리 테스트'!"

        shot2 = os.path.join(ARTIFACT_DIR, "audit_mobile_test_btn_verified.png")
        page.screenshot(path=shot2, timeout=5000, animations="disabled")
        print(f" -> Captured {shot2}", flush=True)

        # Close modal
        page.click("#closeConfigModalBtn")
        page.wait_for_timeout(300)

        print("\n--- [Step 3: App Search & Target Price Setting Special Price Alarm Test] ---", flush=True)
        # Search for '신라면 20개'
        page.fill("#searchInput", "농심 신라면 20개")
        page.press("#searchInput", "Enter")
        page.wait_for_timeout(2000)

        result_info = page.evaluate("""() => ({
            keyword: state.keyword,
            lowestPrice: state.data ? state.data.lowest_price : 0,
            targetPrice: state.targetPrice,
            isSpecial: state.data ? state.data.is_special_price : false
        })""")
        print(f" - Search Result: {result_info['keyword']}, lowest_price={result_info['lowestPrice']}원, current_target={result_info['targetPrice']}원", flush=True)

        # Now open '설정' modal to set a new target price
        page.click("#mobileNavConfigBtn")
        page.wait_for_timeout(400)

        # Set target price to 15,000원 (higher than lowest_price 13,200원 -> Special Price Trigger!)
        page.fill("#modalTargetPriceInput", "15000")

        sound_before_save = page.evaluate("() => window.__spy.soundCalls")
        vibrate_before_save = page.evaluate("() => window.__spy.vibrateCalls")

        # Click '설정 저장 및 다시 계산'
        page.click("#saveConfigModalBtn")
        page.wait_for_timeout(1000)

        sound_after_save = page.evaluate("() => window.__spy.soundCalls")
        vibrate_after_save = page.evaluate("() => window.__spy.vibrateCalls")

        app_state_after = page.evaluate("""() => {
            const banner = document.getElementById('alertBanner');
            const statusBadge = document.getElementById('alertStatusBadge');
            return {
                targetPrice: state.targetPrice,
                isSpecial: state.data ? state.data.is_special_price : false,
                bannerSpecial: banner ? banner.classList.contains('banner-special') : false,
                statusText: statusBadge ? statusBadge.textContent.trim() : '',
                lastAlertKey: state.lastAlertPlayedKey
            };
        }""")

        print(f" - Sound count before save: {sound_before_save} -> after save: {sound_after_save} (Played: {sound_after_save > sound_before_save})", flush=True)
        print(f" - Vibrate count before save: {vibrate_before_save} -> after save: {vibrate_after_save} (Triggered: {vibrate_after_save > vibrate_before_save})", flush=True)
        print(f" - App State: targetPrice={app_state_after['targetPrice']}원, isSpecial={app_state_after['isSpecial']}", flush=True)
        print(f" - Banner Special Style: {app_state_after['bannerSpecial']}, Status Badge: '{app_state_after['statusText']}'", flush=True)
        print(f" - lastAlertKey: '{app_state_after['lastAlertKey']}'", flush=True)

        shot3 = os.path.join(ARTIFACT_DIR, "audit_mobile_target_price_saved_alarm.png")
        page.screenshot(path=shot3, timeout=5000, animations="disabled")
        print(f" -> Captured {shot3}", flush=True)

        assert sound_after_save > sound_before_save, "Chime sound did NOT play after saving target price!"
        assert vibrate_after_save > vibrate_before_save, "Vibration was NOT triggered after saving target price!"
        assert app_state_after['isSpecial'], "is_special_price should be true when lowest <= target!"
        assert app_state_after['statusText'] == "특가 감지", "Status badge should be '특가 감지'!"

        browser.close()
        print("\n=== ALL 3 AUDIT STEPS VERIFIED & PASSED 100%! ===", flush=True)

if __name__ == '__main__':
    run_tests()
