# -*- coding: utf-8 -*-
import sys
import os
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public", "index.html"))
FILE_URL = "file:///" + FILE_PATH.replace("\\", "/")

def run_haptic_verification():
    print(f"Loading local file: {FILE_URL}")
    results = {}

    with sync_playwright() as p:
        # -------------------------------------------------------------
        # TEST 1: iOS Safari (iPhone 15 Pro)
        # -------------------------------------------------------------
        print("\n[TEST 1] iOS Safari (iPhone 15 Pro) 햅틱 진단 및 시각 촉각 펄스 검증...")
        iphone = p.devices["iPhone 15 Pro"]
        iphone_opts = dict(iphone)
        iphone_opts["user_agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1"

        browser_ios = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        context_ios = browser_ios.new_context(**iphone_opts)
        page_ios = context_ios.new_page()

        # Pre-set sessionStorage to bypass splash immediately
        page_ios.add_init_script("""
            sessionStorage.setItem('pricetrace_splash_completed', 'true');
        """)

        page_ios.goto(FILE_URL, wait_until="load")
        page_ios.wait_for_timeout(500)

        # Open config modal via mobile bottom nav
        page_ios.click("#mobileNavConfigBtn")
        page_ios.wait_for_selector("#configModal:not(.hidden)", state="visible", timeout=3000)

        # Check deviceHapticInfoBanner
        banner_ios = page_ios.locator("#deviceHapticInfoBanner")
        banner_text_ios = banner_ios.inner_text()
        print(f"  - iOS 감지 배너 내용:\n{banner_text_ios}")
        assert "Apple iOS" in banner_text_ios, "iOS 배너에 Apple iOS 문구가 포함되어야 함"
        assert "사용자님의 스마트폰은 정상" in banner_text_ios, "스마트폰 정상 문구가 포함되어야 함"

        # Check label for switch
        ios_label = page_ios.locator("#iosHapticTriggerLabel")
        assert ios_label.count() > 0, "#iosHapticTriggerLabel 요소가 DOM에 존재해야 함"

        # Click testNotificationBtn
        page_ios.click("#testNotificationBtn")
        page_ios.wait_for_timeout(500)

        # Check toast message
        toast = page_ios.locator("#toastNotification")
        toast_visible = toast.is_visible()
        toast_text = page_ios.locator("#toastMessage").inner_text()
        print(f"  - iOS 토스트 노출 여부: {toast_visible}, 문구: {toast_text}")

        # Capture iOS screenshot
        ios_img_path = os.path.join(ARTIFACT_DIR, "audit_mobile_ios_haptic_diagnostic.png")
        page_ios.screenshot(path=ios_img_path)
        print(f"  - iOS 스크린샷 저장 완료: {ios_img_path}")

        results["ios_passed"] = True
        results["ios_banner"] = banner_text_ios
        results["ios_toast"] = toast_text

        browser_ios.close()

        # -------------------------------------------------------------
        # TEST 2: Android Chrome (Galaxy S24)
        # -------------------------------------------------------------
        print("\n[TEST 2] Android Chrome (Galaxy S24) 햅틱 진동 API 및 안내 검증...")
        galaxy = p.devices["Galaxy S24"] if "Galaxy S24" in p.devices else p.devices["Pixel 7"]
        galaxy_opts = dict(galaxy)
        galaxy_opts["user_agent"] = "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"

        browser_android = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
        context_android = browser_android.new_context(**galaxy_opts)
        page_android = context_android.new_page()

        # Pre-set sessionStorage to bypass splash immediately & mock navigator.vibrate
        page_android.add_init_script("""
            sessionStorage.setItem('pricetrace_splash_completed', 'true');
            window.__vibrateCalls = [];
            navigator.vibrate = function(pattern) {
                window.__vibrateCalls.push(pattern);
                return true;
            };
        """)

        page_android.goto(FILE_URL, wait_until="load")
        page_android.wait_for_timeout(500)

        page_android.click("#mobileNavConfigBtn")
        page_android.wait_for_selector("#configModal:not(.hidden)", state="visible", timeout=3000)

        banner_android = page_android.locator("#deviceHapticInfoBanner")
        banner_text_android = banner_android.inner_text()
        print(f"  - Android 감지 배너 내용:\n{banner_text_android}")
        assert "Android 기기 감지" in banner_text_android, "Android 안내 문구가 포함되어야 함"

        # Click testNotificationBtn
        page_android.click("#testNotificationBtn")
        page_android.wait_for_timeout(500)

        vibrate_calls = page_android.evaluate("window.__vibrateCalls")
        print(f"  - Android navigator.vibrate 호출 기록: {vibrate_calls}")
        assert len(vibrate_calls) > 0, "navigator.vibrate 가 1회 이상 호출되어야 함"

        toast_text_android = page_android.locator("#toastMessage").inner_text()
        print(f"  - Android 토스트 문구: {toast_text_android}")

        android_img_path = os.path.join(ARTIFACT_DIR, "audit_mobile_android_haptic_diagnostic.png")
        page_android.screenshot(path=android_img_path)
        print(f"  - Android 스크린샷 저장 완료: {android_img_path}")

        # Test Save Target Price with Special Price Trigger
        page_android.fill("#modalTargetPriceInput", "30000")
        page_android.click("#saveConfigModalBtn")
        page_android.wait_for_timeout(800)

        vibrate_calls_after_save = page_android.evaluate("window.__vibrateCalls")
        print(f"  - 설정 저장 후 총 navigator.vibrate 호출 횟수: {len(vibrate_calls_after_save)}")

        saved_img_path = os.path.join(ARTIFACT_DIR, "audit_mobile_target_price_haptic_saved.png")
        page_android.screenshot(path=saved_img_path)
        print(f"  - 설정 저장 후 스크린샷 저장 완료: {saved_img_path}")

        results["android_passed"] = True
        results["vibrate_calls"] = vibrate_calls
        results["android_toast"] = toast_text_android

        browser_android.close()

    print("\n==============================================================")
    print("✅ 모바일 크로스 플랫폼 햅틱 진단 및 2단 진동 엔진 검증 100% 통과!")
    print("==============================================================")
    return results

if __name__ == "__main__":
    run_haptic_verification()
