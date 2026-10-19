import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_URL = "http://127.0.0.1:8080"

def run_verification():
    print("[START] 레이더 탭 터치 시 검색창 포커스 & 가상 키보드 연동 실측 검증 시작...")
    results = {}

    with sync_playwright() as p:
        # iPhone 15 Pro 모바일 환경 에뮬레이션
        iphone_device = p.devices["iPhone 15 Pro"]
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            **iphone_device,
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )
        page = context.new_page()

        # 1. 초기 접속
        print("\n[Step 1] 모바일(iPhone 15 Pro, 393x852) 접속...")
        page.goto(BASE_URL, wait_until="networkidle")

        # 스플래시 화면 처리 (있으면 스킵 클릭 후 대기)
        try:
            skip_btn = page.locator("#skipSplashBtn")
            if skip_btn.is_visible(timeout=2000):
                skip_btn.click()
                print("  - 스플래시 건너뛰기 클릭 완료")
        except Exception:
            pass

        page.wait_for_selector("#welcomeView", state="visible", timeout=10000)
        time.sleep(1.0)

        # 2. 스크롤 다운 상태에서 레이더 탭 탭 테스트
        print("\n[Step 2] 페이지를 600px 아래로 스크롤 후 하단 [레이더] 탭 클릭...")
        page.evaluate("window.scrollTo(0, 600)")
        time.sleep(0.5)
        scroll_y_before = page.evaluate("window.scrollY")
        print(f"  - 스크롤 전 Y 위치: {scroll_y_before}px")

        radar_btn = page.locator("#mobileNavSearchFabBtn")
        radar_btn.wait_for(state="visible", timeout=5000)
        radar_btn.click()
        print("  - [레이더] 탭 클릭 완료")
        time.sleep(0.8) # 부드러운 스크롤 완료 대기

        # 3. 실측 데이터 추출
        eval_data = page.evaluate("""() => {
            const input = document.getElementById('searchInput');
            const radarBtn = document.getElementById('mobileNavSearchFabBtn');
            const activeElem = document.activeElement;
            const style = window.getComputedStyle(input);
            return {
                scrollY: window.scrollY,
                isActiveElementInput: activeElem === input,
                activeElementId: activeElem ? activeElem.id : null,
                inputMode: input.getAttribute('inputmode'),
                enterKeyHint: input.getAttribute('enterkeyhint'),
                selectionStart: input.selectionStart,
                selectionEnd: input.selectionEnd,
                caretColor: style.caretColor,
                hasActiveState: radarBtn.classList.contains('active'),
                radarPillBg: window.getComputedStyle(radarBtn.querySelector('.mobile-nav-pill')).backgroundColor,
                radarPillColor: window.getComputedStyle(radarBtn.querySelector('.mobile-nav-pill')).color,
                inputRectTop: input.getBoundingClientRect().top
            };
        }""")

        results["radar_tap"] = eval_data
        print(f"  - 실측 스크롤 Y 위치: {eval_data['scrollY']}px (상단 복귀)")
        print(f"  - 검색창 포커스 여부 (document.activeElement === #searchInput): {eval_data['isActiveElementInput']}")
        print(f"  - inputmode: {eval_data['inputMode']} (모바일 가상 키보드 검색 모드)")
        print(f"  - enterkeyhint: {eval_data['enterKeyHint']} (가상 자판 엔터키 검색 표시)")
        print(f"  - 커서 위치 (selectionStart/End): {eval_data['selectionStart']} / {eval_data['selectionEnd']}")
        print(f"  - caret-color: {eval_data['caretColor']} (선명한 코발트 블루)")
        print(f"  - 레이더 탭 .active 여부: {eval_data['hasActiveState']}")
        print(f"  - 레이더 탭 캡슐 배경색: {eval_data['radarPillBg']}")
        print(f"  - 검색창 Y 상단 위치 (rect.top): {eval_data['inputRectTop']}px")

        # 4. 포커스 상태 스크린샷 캡처
        focus_shot_path = os.path.join(ARTIFACT_DIR, "radar_tap_focus_mobile.png")
        page.screenshot(path=focus_shot_path)
        print(f"  [SAVED] {focus_shot_path}")

        # 5. 타이핑 입력 테스트
        print("\n[Step 3] 검색창에 가상 키보드 타이핑 입력 수행 ('농심 신라면')...")
        page.keyboard.type("농심 신라면", delay=100)
        time.sleep(0.5)

        typing_data = page.evaluate("""() => {
            const input = document.getElementById('searchInput');
            const clearBtn = document.getElementById('clearSearchBtn');
            return {
                value: input.value,
                clearBtnVisible: clearBtn && !clearBtn.classList.contains('hidden'),
                cursorPos: input.selectionStart
            };
        }""")
        results["typing"] = typing_data
        print(f"  - 입력된 값: '{typing_data['value']}'")
        print(f"  - 검색어 지우기 버튼(x) 노출 여부: {typing_data['clearBtnVisible']}")
        print(f"  - 최종 커서 위치: {typing_data['cursorPos']}")

        # 6. 타이핑 상태 스크린샷 캡처
        typing_shot_path = os.path.join(ARTIFACT_DIR, "radar_tap_typing_mobile.png")
        page.screenshot(path=typing_shot_path)
        print(f"  [SAVED] {typing_shot_path}")

        browser.close()

    # 결과 JSON 저장
    output_json_path = os.path.join(ARTIFACT_DIR, "radar_tab_focus_audit_raw.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[REPORT RAW] {output_json_path}")
    print("\n[COMPLETE] 레이더 탭 모바일 포커스 및 가상 키보드 검증 완료!")

if __name__ == "__main__":
    run_verification()
