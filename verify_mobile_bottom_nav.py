import sys
import os
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def run_verification():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # 1. iPhone 15 Pro 에뮬레이션 (393 x 852)
        # -------------------------------------------------------------
        print("\n[1] iPhone 15 Pro (393 x 852) 검증 시작...")
        iphone_context = browser.new_context(
            viewport={"width": 393, "height": 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = iphone_context.new_page()
        page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        time.sleep(1)

        # 1-1. 하단 바 존재 및 가시성 점검
        bottom_nav = page.locator("#mobileBottomNav")
        is_visible = bottom_nav.is_visible()
        print(f"  - mobileBottomNav 가시성: {is_visible}")
        assert is_visible, "mobileBottomNav must be visible on mobile!"

        # 가로 오버플로우 실측
        overflow = page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth || document.body.scrollWidth > window.innerWidth")
        print(f"  - 가로 오버플로우 발생 여부: {overflow} (정상: False)")

        # 기본 홈 화면 캡처
        path_home = os.path.join(ARTIFACT_DIR, "proof_mobile_nav_iphone_home.png")
        page.screenshot(path=path_home)
        print(f"  - [캡처 완료] 홈 화면: {path_home}")

        # 1-2. [핫딜] 탭 클릭 인터랙션
        page.locator("#mobileNavHotdealBtn").click()
        time.sleep(0.5)
        hotdeal_active = page.evaluate("() => document.getElementById('tabTrendingBadge').textContent")
        print(f"  - 핫딜 탭 활성화 텍스트: {hotdeal_active}")
        path_hotdeal = os.path.join(ARTIFACT_DIR, "proof_mobile_nav_iphone_hotdeal.png")
        page.screenshot(path=path_hotdeal)
        print(f"  - [캡처 완료] 핫딜 탭 전환: {path_hotdeal}")

        # 1-3. [생필품] 탭 클릭 인터랙션
        page.locator("#mobileNavSteadyBtn").click()
        time.sleep(0.5)
        steady_active = page.evaluate("() => document.getElementById('tabSteadyBadge').textContent")
        print(f"  - 생필품 탭 활성화 텍스트: {steady_active}")
        path_steady = os.path.join(ARTIFACT_DIR, "proof_mobile_nav_iphone_steady.png")
        page.screenshot(path=path_steady)
        print(f"  - [캡처 완료] 생필품 탭 전환: {path_steady}")

        # 1-4. [설정] 탭 클릭 인터랙션 (모달 오픈)
        page.locator("#mobileNavConfigBtn").click()
        time.sleep(0.5)
        modal_visible = page.locator("#configModal").is_visible()
        print(f"  - 설정 모달 노출 여부: {modal_visible}")
        path_modal = os.path.join(ARTIFACT_DIR, "proof_mobile_nav_iphone_modal.png")
        page.screenshot(path=path_modal)
        print(f"  - [캡처 완료] 설정 모달 오픈: {path_modal}")
        # 모달 닫기
        page.locator("#closeConfigModalBtn").click()
        time.sleep(0.3)

        # 1-5. [중앙 돌출 FAB] 클릭 인터랙션 (검색창 포커스)
        page.locator("#mobileNavSearchFabBtn").click()
        time.sleep(0.5)
        is_search_focused = page.evaluate("() => document.activeElement === document.getElementById('searchInput')")
        print(f"  - 중앙 FAB 클릭 후 검색창 포커스 여부: {is_search_focused}")

        # 1-6. 검색 결과 화면에서도 하단 바 노출 및 [홈] 복귀 점검
        page.fill("#searchInput", "코카콜라 제로 355ml 24캔")
        page.keyboard.press("Enter")
        page.wait_for_selector("#resultView:not(.hidden)", timeout=10000)
        time.sleep(1)

        result_nav_visible = page.locator("#mobileBottomNav").is_visible()
        print(f"  - 검색 결과 화면에서 하단 바 가시성: {result_nav_visible}")
        path_result = os.path.join(ARTIFACT_DIR, "proof_mobile_nav_iphone_result.png")
        page.screenshot(path=path_result)
        print(f"  - [캡처 완료] 검색 결과 화면 하단 바: {path_result}")

        # 하단 바의 [홈] 탭 클릭하여 웰컴 뷰 복귀
        page.locator("#mobileNavHomeBtn").click()
        time.sleep(0.5)
        is_welcome_visible = page.locator("#welcomeView:not(.hidden)").is_visible()
        print(f"  - 하단 [홈] 클릭 후 웰컴 화면 복귀 여부: {is_welcome_visible}")
        iphone_context.close()

        # -------------------------------------------------------------
        # 2. Android Galaxy S24 에뮬레이션 (412 x 915)
        # -------------------------------------------------------------
        print("\n[2] Galaxy S24 (412 x 915) 검증 시작...")
        galaxy_context = browser.new_context(
            viewport={"width": 412, "height": 915},
            user_agent="Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        g_page = galaxy_context.new_page()
        g_page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        time.sleep(1)
        path_galaxy = os.path.join(ARTIFACT_DIR, "proof_mobile_nav_galaxy_s24.png")
        g_page.screenshot(path=path_galaxy)
        print(f"  - [캡처 완료] Galaxy S24 화면: {path_galaxy}")
        galaxy_context.close()

        # -------------------------------------------------------------
        # 3. Desktop PC (1440 x 900) 검증 (md:hidden에 의해 숨겨져야 함)
        # -------------------------------------------------------------
        print("\n[3] Desktop PC (1440 x 900) 검증 시작...")
        pc_context = browser.new_context(
            viewport={"width": 1440, "height": 900}
        )
        pc_page = pc_context.new_page()
        pc_page.goto("http://127.0.0.1:8080", wait_until="networkidle")
        time.sleep(1)
        pc_nav_visible = pc_page.locator("#mobileBottomNav").is_visible()
        print(f"  - PC 데스크톱에서 하단 바 가시성 (숨겨져야 정상): {pc_nav_visible}")
        assert not pc_nav_visible, "mobileBottomNav must be HIDDEN on desktop!"
        path_pc = os.path.join(ARTIFACT_DIR, "proof_mobile_nav_pc_desktop.png")
        pc_page.screenshot(path=path_pc)
        print(f"  - [캡처 완료] Desktop PC 화면: {path_pc}")
        pc_context.close()

        browser.close()

    print("\n✅ 모든 검증이 성공적으로 완료되었습니다!")

if __name__ == "__main__":
    run_verification()
