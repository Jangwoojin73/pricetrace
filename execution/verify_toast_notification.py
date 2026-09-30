# -*- coding: utf-8 -*-
"""
실시간 갱신 버튼 클릭 시 플로팅 토스트 메시지 정밀 검증 스크립트
1. 홈 화면에서 '실시간 갱신' 클릭 시 토스트 메시지 출력 및 텍스트 검증
2. 일정 시간(3초) 경과 후 자동 페이드아웃(Dismiss) 정상 작동 검증
3. 검색 결과 화면(?q=...)에서 '실시간 갱신' 클릭 시 실시간 시각 기준 토스트 메시지 출력 및 텍스트 검증
4. 모바일 화면(390x844)에서 모바일 갱신 버튼 터치 시 토스트 메시지 정상 출력 검증
5. 실측 스크린샷 캡처 및 아티팩트 보관
"""
import sys
import time
from playwright.sync_api import sync_playwright

def run_toast_verification():
    artifacts_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # -------------------------------------------------------------
        # Part 1: 메인 홈 화면 검증
        # -------------------------------------------------------------
        print("[Step 1] 메인 홈 화면 접속 (http://127.0.0.1:8080/index.html)")
        page.goto("http://127.0.0.1:8080/index.html", wait_until="networkidle")
        page.wait_for_timeout(1000)

        print("[Step 2] 홈 화면에서 '실시간 갱신' 버튼 클릭")
        refresh_btn = page.locator("#refreshBtn")
        refresh_btn.click()
        page.wait_for_timeout(400)

        toast = page.locator("#toastNotification")
        toast_msg = page.locator("#toastMessage")
        
        home_toast_text = toast_msg.inner_text()
        print(f" -> [홈 화면 토스트 문구]: {home_toast_text}")
        results["home_toast_text"] = home_toast_text
        
        home_shot_path = f"{artifacts_dir}\\proof_toast_home_refresh.png"
        page.screenshot(path=home_shot_path)
        print(f" -> [홈 토스트 캡처 완료]: {home_shot_path}")

        print("[Step 3] 토스트 자동 소멸(Dismiss 3초) 대기")
        page.wait_for_timeout(3500)
        toast_class = toast.get_attribute("class") or ""
        is_hidden_after_delay = "opacity-0" in toast_class and "translate-y-16" in toast_class
        print(f" -> 3초 경과 후 자동 소멸 여부: {is_hidden_after_delay}")
        results["toast_auto_dismiss"] = is_hidden_after_delay

        # -------------------------------------------------------------
        # Part 2: 검색 결과 화면 검증
        # -------------------------------------------------------------
        print("[Step 4] 검색 결과 화면 접속 (?q=동원참치 10캔)")
        page.goto("http://127.0.0.1:8080/index.html?q=%EB%8F%99%EC%9B%90%EC%B0%B8%EC%B9%98%2010%EC%BA%94", wait_until="networkidle")
        page.wait_for_timeout(2000)

        print("[Step 5] 검색 결과 화면에서 '실시간 갱신' 버튼 클릭")
        refresh_btn.click()
        page.wait_for_timeout(300)

        loading_toast_text = toast_msg.inner_text()
        print(f" -> [갱신 진행 토스트 문구]: {loading_toast_text}")
        results["search_loading_toast_text"] = loading_toast_text

        # 갱신 완료 대기 (1.5초 후 완료 토스트)
        page.wait_for_timeout(2000)
        result_toast_text = toast_msg.inner_text()
        print(f" -> [갱신 완료 토스트 문구]: {result_toast_text}")
        results["search_result_toast_text"] = result_toast_text

        result_shot_path = f"{artifacts_dir}\\proof_toast_search_refresh.png"
        page.screenshot(path=result_shot_path)
        print(f" -> [검색 결과 토스트 캡처 완료]: {result_shot_path}")

        # -------------------------------------------------------------
        # Part 3: 모바일 반응형 뷰포트 검증
        # -------------------------------------------------------------
        print("[Step 6] 모바일 뷰포트(390x844)에서 모바일 갱신 버튼(#mobileRefreshBtn) 검증")
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(1000)

        mobile_refresh_btn = page.locator("#mobileRefreshBtn")
        mobile_refresh_btn.click()
        page.wait_for_timeout(2000)

        mobile_toast_text = toast_msg.inner_text()
        print(f" -> [모바일 갱신 토스트 문구]: {mobile_toast_text}")
        results["mobile_toast_text"] = mobile_toast_text

        mobile_shot_path = f"{artifacts_dir}\\proof_toast_mobile_refresh.png"
        page.screenshot(path=mobile_shot_path)
        print(f" -> [모바일 토스트 캡처 완료]: {mobile_shot_path}")

        browser.close()

    print("\n=======================================================")
    print("           [실시간 갱신 토스트 검증 최종 결과]           ")
    print("=======================================================")
    for k, v in results.items():
        print(f"  * {k}: {v}")
    print("=======================================================")

if __name__ == "__main__":
    run_toast_verification()
