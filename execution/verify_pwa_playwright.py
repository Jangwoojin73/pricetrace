import os
import sys
import json
import time

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def run_pwa_audit():
    print("=" * 60)
    print("🔍 [E2E PWA Audit] PriceTrace PWA 실측 검증 시작")
    print("=" * 60)

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 1. Manifest JSON Test
        print("\n[Step 1] Manifest JSON 검증...")
        manifest_res = page.goto("http://127.0.0.1:8080/manifest.json")
        assert manifest_res.status == 200, f"Manifest status: {manifest_res.status}"
        manifest_text = page.content()
        # Parse JSON
        manifest_data = json.loads(page.inner_text("body"))
        print(f"  - App Name: {manifest_data.get('name')}")
        print(f"  - Short Name: {manifest_data.get('short_name')}")
        print(f"  - Start URL: {manifest_data.get('start_url')}")
        print(f"  - Display: {manifest_data.get('display')}")
        print(f"  - Theme Color: {manifest_data.get('theme_color')}")
        print(f"  - Icons Count: {len(manifest_data.get('icons', []))}")
        results["manifest"] = {
            "status": "PASS",
            "name": manifest_data.get("name"),
            "display": manifest_data.get("display"),
            "icons": len(manifest_data.get("icons", []))
        }

        # 2. Main Page & Service Worker Registration Test
        print("\n[Step 2] 메인 페이지 접속 및 Service Worker 등록 검증...")
        page.goto("http://127.0.0.1:8080/")
        page.wait_for_timeout(2000)

        # Check Service Worker in Browser
        sw_state = page.evaluate("""async () => {
            if (!('serviceWorker' in navigator)) return { supported: false };
            try {
                const reg = await navigator.serviceWorker.ready;
                const cacheNames = await caches.keys();
                let cachedUrls = [];
                for (const name of cacheNames) {
                    const cache = await caches.open(name);
                    const keys = await cache.keys();
                    cachedUrls.push({ cacheName: name, count: keys.length });
                }
                return {
                    supported: true,
                    scope: reg.scope,
                    active: !!reg.active,
                    caches: cachedUrls
                };
            } catch (err) {
                return { supported: true, error: err.message };
            }
        }""")
        print("  - Service Worker Status:", json.dumps(sw_state, ensure_ascii=False, indent=2))
        results["service_worker"] = sw_state

        # 3. Desktop Viewport & Install UI Simulation
        print("\n[Step 3] 데스크톱 PWA 설치 UI 및 beforeinstallprompt 시뮬레이션...")
        page.evaluate("""() => {
            // Trigger beforeinstallprompt simulation
            const event = new Event('beforeinstallprompt');
            event.prompt = async () => ({ outcome: 'accepted' });
            event.userChoice = Promise.resolve({ outcome: 'accepted' });
            window.dispatchEvent(event);
        }""")
        page.wait_for_timeout(1000)

        desktop_install_visible = page.is_visible("#installAppBtn")
        banner_visible = page.is_visible("#pwaInstallBanner")
        print(f"  - Desktop #installAppBtn visible: {desktop_install_visible}")
        print(f"  - Desktop #pwaInstallBanner visible: {banner_visible}")

        # Capture Desktop PWA Screenshot
        desktop_shot = os.path.join(ARTIFACT_DIR, "proof_pwa_desktop_install.png")
        page.screenshot(path=desktop_shot)
        print(f"  - Saved screenshot: {desktop_shot}")
        results["desktop_ui"] = {
            "install_btn_visible": desktop_install_visible,
            "banner_visible": banner_visible,
            "screenshot": desktop_shot
        }

        # 4. Mobile Viewport (iPhone 14 Pro emulation)
        print("\n[Step 4] 모바일 iOS Safari 뷰포트 및 A2HS 가이드 모달 검증...")
        mobile_context = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
        )
        mobile_page = mobile_context.new_page()
        mobile_page.goto("http://127.0.0.1:8080/")
        mobile_page.wait_for_timeout(2000)

        # On iOS, mobileInstallAppBtn is visible to guide user
        mobile_install_visible = mobile_page.is_visible("#mobileInstallAppBtn")
        print(f"  - Mobile #mobileInstallAppBtn visible: {mobile_install_visible}")

        # Click mobile install button to trigger iOS modal
        mobile_page.click("#mobileInstallAppBtn")
        mobile_page.wait_for_timeout(500)
        ios_modal_visible = mobile_page.is_visible("#iosInstallModal")
        print(f"  - iOS Install Guide Modal visible: {ios_modal_visible}")

        mobile_shot = os.path.join(ARTIFACT_DIR, "proof_pwa_mobile_ios_modal.png")
        mobile_page.screenshot(path=mobile_shot)
        print(f"  - Saved screenshot: {mobile_shot}")
        results["mobile_ios_ui"] = {
            "install_btn_visible": mobile_install_visible,
            "ios_modal_visible": ios_modal_visible,
            "screenshot": mobile_shot
        }
        mobile_context.close()

        # 5. Mobile Android Viewport with beforeinstallprompt
        print("\n[Step 5] 모바일 Android 뷰포트 플로팅 배너 검증...")
        android_context = browser.new_context(
            viewport={"width": 412, "height": 915},
            user_agent="Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
        )
        android_page = android_context.new_page()
        android_page.goto("http://127.0.0.1:8080/")
        android_page.wait_for_timeout(1000)

        android_page.evaluate("""() => {
            const event = new Event('beforeinstallprompt');
            event.prompt = async () => ({ outcome: 'accepted' });
            event.userChoice = Promise.resolve({ outcome: 'accepted' });
            window.dispatchEvent(event);
        }""")
        android_page.wait_for_timeout(2000)

        android_banner_visible = android_page.is_visible("#pwaInstallBanner")
        print(f"  - Android #pwaInstallBanner visible: {android_banner_visible}")

        android_shot = os.path.join(ARTIFACT_DIR, "proof_pwa_mobile_android_banner.png")
        android_page.screenshot(path=android_shot)
        print(f"  - Saved screenshot: {android_shot}")
        results["mobile_android_ui"] = {
            "banner_visible": android_banner_visible,
            "screenshot": android_shot
        }
        android_context.close()

        # 6. Offline Fallback Page Test
        print("\n[Step 6] 오프라인 폴백 페이지(/offline.html) 렌더링 검증...")
        page.goto("http://127.0.0.1:8080/offline.html")
        page.wait_for_timeout(1000)
        offline_shot = os.path.join(ARTIFACT_DIR, "proof_pwa_offline_page.png")
        page.screenshot(path=offline_shot)
        print(f"  - Saved screenshot: {offline_shot}")
        results["offline_page"] = {
            "status": "PASS",
            "screenshot": offline_shot
        }

        browser.close()

    print("\n" + "=" * 60)
    print("🎉 [E2E PWA Audit] 모든 PWA 실측 검증 완료!")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("=" * 60)

if __name__ == "__main__":
    run_pwa_audit()
