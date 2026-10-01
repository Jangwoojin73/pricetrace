import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def capture_mobile_toasts():
    print("=" * 60)
    print("📸 [Mobile OS Toast Capture] OS별 하단 토스트/배너 캡처 시작")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ==========================================================
        # 1. Android OS (Galaxy S24: 412 x 915)
        # ==========================================================
        print("\n▶ [1] Android OS (삼성 갤럭시) 환경 캡처...")
        android_ctx = browser.new_context(
            viewport={"width": 412, "height": 915},
            user_agent="Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
            is_mobile=True,
            has_touch=True
        )
        android_page = android_ctx.new_page()
        android_page.goto("http://127.0.0.1:8080/")
        android_page.wait_for_timeout(1000)

        # Trigger Android beforeinstallprompt
        android_page.evaluate("""() => {
            const event = new Event('beforeinstallprompt');
            event.prompt = async () => ({ outcome: 'accepted' });
            event.userChoice = Promise.resolve({ outcome: 'accepted' });
            window.dispatchEvent(event);
        }""")
        android_page.wait_for_timeout(1800)

        # 1-A. Android 하단 설치 유도 플로팅 배너 캡처
        shot_android_banner = os.path.join(ARTIFACT_DIR, "proof_toast_android_install_banner.png")
        android_page.screenshot(path=shot_android_banner)
        print(f"  - 캡처 완료: {shot_android_banner}")

        # 1-B. Android 설치 완료 성공 토스트 캡처
        android_page.evaluate("""() => {
            window.dispatchEvent(new Event('appinstalled'));
        }""")
        android_page.wait_for_timeout(600)
        shot_android_success = os.path.join(ARTIFACT_DIR, "proof_toast_android_installed_success.png")
        android_page.screenshot(path=shot_android_success)
        print(f"  - 캡처 완료: {shot_android_success}")

        android_ctx.close()

        # ==========================================================
        # 2. iOS Safari (iPhone 14/15 Pro: 393 x 852)
        # ==========================================================
        print("\n▶ [2] iOS OS (애플 아이폰 Safari) 환경 캡처...")
        ios_ctx = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        ios_page = ios_ctx.new_page()
        ios_page.goto("http://127.0.0.1:8080/")
        ios_page.wait_for_timeout(2000)

        # 2-A. iOS 하단 설치 가이드 배너 캡처
        shot_ios_banner = os.path.join(ARTIFACT_DIR, "proof_toast_ios_guide_banner.png")
        ios_page.screenshot(path=shot_ios_banner)
        print(f"  - 캡처 완료: {shot_ios_banner}")

        # 2-B. 하단 배너의 '방법 보기' 클릭 -> iOS 3단계 시각적 가이드 모달 캡처
        ios_page.click("#pwaBannerInstallBtn")
        ios_page.wait_for_timeout(600)
        shot_ios_modal = os.path.join(ARTIFACT_DIR, "proof_toast_ios_modal_guide.png")
        ios_page.screenshot(path=shot_ios_modal)
        print(f"  - 캡처 완료: {shot_ios_modal}")

        ios_ctx.close()

        # ==========================================================
        # 3. 네트워크 상태 플로팅 토스트 (Offline / Online)
        # ==========================================================
        print("\n▶ [3] 모바일 상태 알림 플로팅 토스트 캡처...")
        status_ctx = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        status_page = status_ctx.new_page()
        status_page.goto("http://127.0.0.1:8080/")
        status_page.wait_for_timeout(1000)

        # 3-A. 오프라인 전환 토스트 캡처
        status_page.evaluate("""() => {
            window.dispatchEvent(new Event('offline'));
        }""")
        status_page.wait_for_timeout(600)
        shot_offline = os.path.join(ARTIFACT_DIR, "proof_toast_offline_warning.png")
        status_page.screenshot(path=shot_offline)
        print(f"  - 캡처 완료: {shot_offline}")

        # 3-B. 온라인 복구 토스트 캡처
        status_page.evaluate("""() => {
            window.dispatchEvent(new Event('online'));
        }""")
        status_page.wait_for_timeout(600)
        shot_online = os.path.join(ARTIFACT_DIR, "proof_toast_online_restored.png")
        status_page.screenshot(path=shot_online)
        print(f"  - 캡처 완료: {shot_online}")

        status_ctx.close()
        browser.close()

    print("\n" + "=" * 60)
    print("🎉 모든 모바일 OS별 하단 토스트/배너 캡처 완료!")
    print("=" * 60)

if __name__ == "__main__":
    capture_mobile_toasts()
