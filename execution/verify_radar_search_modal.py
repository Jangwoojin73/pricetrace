import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_URL = "http://127.0.0.1:8080"

def run_modal_verification():
    print("[START] 실시간 최저가 레이더 검색 & 자판 바텀시트 모달 실측 검증 시작...")
    results = {}

    with sync_playwright() as p:
        iphone_device = p.devices["iPhone 15 Pro"]
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            **iphone_device,
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )
        page = context.new_page()

        # 1. 초기 모바일 접속
        print("\n[Step 1] 모바일(iPhone 15 Pro, 393x852) 접속...")
        page.goto(BASE_URL, wait_until="networkidle")

        try:
            skip_btn = page.locator("#skipSplashBtn")
            if skip_btn.is_visible(timeout=2000):
                skip_btn.click()
                print("  - 스플래시 건너뛰기 클릭 완료")
        except Exception:
            pass

        page.wait_for_selector("#welcomeView", state="visible", timeout=10000)
        time.sleep(0.8)

        # 2. 하단 [레이더] 탭 클릭
        print("\n[Step 2] 하단 [레이더] 메뉴 탭 클릭...")
        radar_btn = page.locator("#mobileNavSearchFabBtn")
        radar_btn.wait_for(state="visible", timeout=5000)
        radar_btn.click()
        print("  - [레이더] 탭 클릭 완료, 바텀시트 모달 슬라이드 업 대기...")
        time.sleep(0.5)

        # 3. 모달 DOM 및 시각적 슬라이드 업 상태 확인
        eval_modal = page.evaluate("""() => {
            const modal = document.getElementById('radarSearchModal');
            const drawer = document.getElementById('radarSearchDrawer');
            const input = document.getElementById('modalSearchInput');
            const activeElem = document.activeElement;
            const drawerRect = drawer ? drawer.getBoundingClientRect() : null;
            const inputStyle = input ? window.getComputedStyle(input) : null;
            return {
                isModalOpen: modal && modal.classList.contains('modal-open'),
                isModalVisible: modal && !modal.classList.contains('modal-hidden'),
                isActiveElementModalInput: activeElem === input,
                activeElementId: activeElem ? activeElem.id : null,
                caretColor: inputStyle ? inputStyle.caretColor : null,
                fontSize: inputStyle ? inputStyle.fontSize : null,
                touchAction: inputStyle ? inputStyle.touchAction : null,
                viewportMeta: document.querySelector('meta[name="viewport"]') ? document.querySelector('meta[name="viewport"]').getAttribute('content') : null,
                inputMode: input ? input.getAttribute('inputmode') : null,
                enterKeyHint: input ? input.getAttribute('enterkeyhint') : null,
                drawerTop: drawerRect ? drawerRect.top : null,
                drawerHeight: drawerRect ? drawerRect.height : null,
                windowHeight: window.innerHeight
            };
        }""")

        results["modal_open_state"] = eval_modal
        print(f"  - 모달 활성화 여부 (.modal-open): {eval_modal['isModalOpen']}")
        print(f"  - 모달 바텀시트 드로어 높이: {eval_modal['drawerHeight']}px (화면 Y: {eval_modal['drawerTop']}px ~ {eval_modal['windowHeight']}px)")
        print(f"  - 모달 검색창 포커스 여부 (document.activeElement === #modalSearchInput): {eval_modal['isActiveElementModalInput']}")
        print(f"  - 모달 검색창 font-size (iOS 자동확대 방지 16px 보장): {eval_modal['fontSize']}")
        print(f"  - touch-action (더블탭 줌 방지): {eval_modal['touchAction']}")
        print(f"  - 뷰포트 메타태그 (줌 락): {eval_modal['viewportMeta']}")
        print(f"  - caret-color (선명한 코발트 블루): {eval_modal['caretColor']}")
        print(f"  - inputmode: {eval_modal['inputMode']} / enterkeyhint: {eval_modal['enterKeyHint']}")

        # 스크린샷 1: 레이더 탭 터치 시 하단에서 위로 솟아오른 자판 & 검색 모달창
        modal_open_shot = os.path.join(ARTIFACT_DIR, "radar_search_modal_open_mobile.png")
        page.screenshot(path=modal_open_shot)
        print(f"  [SAVED] {modal_open_shot}")

        # 4. 빠른 수량·단위 보조자판 및 텍스트 입력 테스트
        print("\n[Step 3] 모달 검색창에 '신라면' 입력 및 보조자판 '20개' 칩 클릭...")
        page.locator("#modalSearchInput").type("신라면", delay=80)
        time.sleep(0.3)

        # 보조자판 '20개' 칩 클릭
        chip_20 = page.locator("#modalQuantityPad button[data-append=' 20개']")
        if chip_20.is_visible(timeout=2000):
            chip_20.click()
            print("  - 보조자판 [ 20개 ] 칩 클릭 완료")
        time.sleep(0.3)

        eval_typing = page.evaluate("""() => {
            const input = document.getElementById('modalSearchInput');
            const clearBtn = document.getElementById('modalClearSearchBtn');
            return {
                value: input.value,
                clearBtnVisible: clearBtn && !clearBtn.classList.contains('hidden'),
                cursorPos: input.selectionStart
            };
        }""")
        results["typing_state"] = eval_typing
        print(f"  - 조합된 검색어: '{eval_typing['value']}'")
        print(f"  - 텍스트 지우기 버튼 노출: {eval_typing['clearBtnVisible']}")
        print(f"  - 커서 위치: {eval_typing['cursorPos']}")

        # 스크린샷 2: 검색어 입력 및 보조자판 사용 화면
        modal_typing_shot = os.path.join(ARTIFACT_DIR, "radar_search_modal_typing_mobile.png")
        page.screenshot(path=modal_typing_shot)
        print(f"  [SAVED] {modal_typing_shot}")

        # 5. 검색 실행 (조회 버튼 클릭)
        print("\n[Step 4] 검색 '조회' 버튼 클릭하여 가격비교 결과로 진입...")
        submit_btn = page.locator("#modalSearchForm button[type='submit']")
        submit_btn.click()
        print("  - 조회 버튼 클릭 완료, 결과 로딩 대기...")

        page.wait_for_selector("#resultView", state="visible", timeout=15000)
        time.sleep(1.0)

        eval_result = page.evaluate("""() => {
            const modal = document.getElementById('radarSearchModal');
            const resultView = document.getElementById('resultView');
            const headerInput = document.getElementById('searchInput');
            return {
                isModalClosed: modal && modal.classList.contains('modal-hidden'),
                isResultVisible: resultView && !resultView.classList.contains('hidden'),
                headerInputValue: headerInput ? headerInput.value : null
            };
        }""")
        results["result_state"] = eval_result
        print(f"  - 모달 닫힘 여부: {eval_result['isModalClosed']}")
        print(f"  - 검색 결과 뷰 노출 여부: {eval_result['isResultVisible']}")
        print(f"  - 헤더 검색어 동기화: '{eval_result['headerInputValue']}'")

        # 스크린샷 3: 검색 완료 후 대시보드 안착 화면
        modal_result_shot = os.path.join(ARTIFACT_DIR, "radar_search_modal_result_mobile.png")
        page.screenshot(path=modal_result_shot)
        print(f"  [SAVED] {modal_result_shot}")

        browser.close()

    # JSON 저장
    output_json = os.path.join(ARTIFACT_DIR, "radar_search_modal_audit_raw.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[RAW REPORT] {output_json}")
    print("\n[COMPLETE] 레이더 검색 모달창 및 보조자판 전수 실측 완료!")

if __name__ == "__main__":
    run_modal_verification()
