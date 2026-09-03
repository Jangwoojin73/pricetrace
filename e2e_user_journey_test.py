#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
e2e_user_journey_test.py - 전 주기적 사용자 사용성 E2E 자동 검증 스크립트

Step 1. 최초 진입 및 메인 대시보드 로딩 검증
Step 2. 목표가 변경 인터랙션 및 상태 전환 (특가 -> 관망) 검증
Step 3. 목표가 복귀 (관망 -> 특가) 인터랙션 검증
Step 4. 퀵 칩 원클릭 검색 및 데이터 동기화 검증
Step 5. 판매처 비교 매트릭스 및 구매 아웃링크 유효성 검증
Step 6. 모바일 반응형 뷰포트(iPhone 375x812) 검증
"""

import sys
import io
import os
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "test_artifacts")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def run_e2e_test():
    print("=" * 70)
    print("🚀 [E2E User Journey Test] 전 주기적 사용자 사용성 검증 시작")
    print("=" * 70)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # ----------------------------------------------------
        # Step 1. 최초 진입 및 초기 로딩
        # ----------------------------------------------------
        print("\n[Step 1] 웹앱 최초 접속 및 메인 대시보드 로딩 검사...")
        page.goto("http://localhost:8080")
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # 주요 요소 점검
        title = page.locator("#productTitle").inner_text()
        lowest_price = page.locator("#lowestPriceDisplay").inner_text()
        unit_price = page.locator("#unitPriceDisplay").inner_text()
        alert_msg = page.locator("#alertMainMessage").inner_text()
        banner_class = page.locator("#alertBanner").get_attribute("class")

        step1_pass = (
            "신라면" in title and
            len(lowest_price.strip()) > 0 and
            "약" in unit_price and
            "목표 가격 이하" in alert_msg and
            "banner-special" in banner_class
        )
        step1_img = os.path.join(SCREENSHOT_DIR, "step1_initial.png")
        page.screenshot(path=step1_img, full_page=True)

        results.append((
            "Step 1: 최초 진입 및 최저가 카탈로그 로딩",
            step1_pass,
            f"상품: '{title[:25]}...', 최저가: {lowest_price}원, 봉당: {unit_price}, 배너: '{alert_msg[:20]}...'"
        ))

        # ----------------------------------------------------
        # Step 2. 목표가 변경 (10,000원으로 인하 -> 가격 관망 상태로 전환)
        # ----------------------------------------------------
        print("\n[Step 2] 목표가 변경 인터랙션 (10,000원 설정 -> 관망 전환 검사)...")
        # 모달 열기
        page.click("#quickTargetEditBtn")
        page.wait_for_selector("#configModal:not(.hidden)", state="visible")

        # 목표가를 10,000원으로 입력
        page.fill("#modalTargetPriceInput", "10000")
        page.click("#saveConfigModalBtn")
        page.wait_for_selector("#configModal.hidden", state="attached")
        
        # API 응답 및 DOM 반영 대기 (목표가 10,000원 및 관망 텍스트 감지)
        page.wait_for_function("() => document.getElementById('currentSetTargetPrice').textContent.includes('10,000')", timeout=15000)
        page.wait_for_selector("text=아직 목표 가격보다 비쌉니다", timeout=15000)

        alert_msg_step2 = page.locator("#alertMainMessage").inner_text()
        badge_text_step2 = page.locator("#alertStatusBadge").inner_text()
        banner_class_step2 = page.locator("#alertBanner").get_attribute("class")

        step2_pass = (
            "비쌉니다" in alert_msg_step2 and
            "가격 관망" in badge_text_step2 and
            "banner-normal" in banner_class_step2
        )
        step2_img = os.path.join(SCREENSHOT_DIR, "step2_price_watch.png")
        page.screenshot(path=step2_img, full_page=True)

        results.append((
            "Step 2: 목표가 하향 시 가격 관망(유지) 상태 전환",
            step2_pass,
            f"상태 뱃지: '{badge_text_step2}', 배너 메시지: '{alert_msg_step2[:25]}...'"
        ))

        # ----------------------------------------------------
        # Step 3. 목표가 복귀 (15,000원 프리셋 클릭 -> 특가 발생 상태 복귀)
        # ----------------------------------------------------
        print("\n[Step 3] 목표가 프리셋 복귀 (15,000원 설정 -> 특가 상태 복구 검사)...")
        page.click("#openConfigModalBtn")
        page.wait_for_selector("#configModal:not(.hidden)", state="visible")
        
        # 15,000원 프리셋 버튼 클릭
        page.click('.preset-price-btn[data-price="15000"]')
        page.click("#saveConfigModalBtn")
        page.wait_for_selector("#configModal.hidden", state="attached")

        # API 응답 및 DOM 반영 대기 (목표가 15,000원 및 특가 발생 텍스트 감지)
        page.wait_for_function("() => document.getElementById('currentSetTargetPrice').textContent.includes('15,000')", timeout=15000)
        page.wait_for_selector("text=목표 가격 이하입니다", timeout=15000)

        alert_msg_step3 = page.locator("#alertMainMessage").inner_text()
        badge_text_step3 = page.locator("#alertStatusBadge").inner_text()
        banner_class_step3 = page.locator("#alertBanner").get_attribute("class")

        step3_pass = (
            "목표 가격 이하" in alert_msg_step3 and
            "특가 발생" in badge_text_step3 and
            "banner-special" in banner_class_step3
        )
        step3_img = os.path.join(SCREENSHOT_DIR, "step3_special_restored.png")
        page.screenshot(path=step3_img, full_page=True)

        results.append((
            "Step 3: 목표가 프리셋 복귀 시 특가 발생 배너 복원",
            step3_pass,
            f"상태 뱃지: '{badge_text_step3}', 배너 메시지: '{alert_msg_step3[:25]}...'"
        ))

        # ----------------------------------------------------
        # Step 4. 퀵 칩 원클릭 검색 인터랙션
        # ----------------------------------------------------
        print("\n[Step 4] 퀵 칩 태그 클릭 및 동적 검색 인터랙션 검사...")
        chip_btn = page.locator('.quick-chip[data-keyword="농심 신라면 120g 20개"]')
        chip_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        input_val = page.locator("#searchInput").input_value()
        step4_pass = "농심 신라면 120g 20개" in input_val

        results.append((
            "Step 4: 인기 검색어 퀵 칩 클릭 및 자동 검색",
            step4_pass,
            f"검색창 자동 반영 키워드: '{input_val}'"
        ))

        # ----------------------------------------------------
        # Step 5. 판매처 비교 매트릭스 및 구매 링크 유효성
        # ----------------------------------------------------
        print("\n[Step 5] 판매처별 가격 비교 TOP 3 카드 및 링크 유효성 검사...")
        cards = page.locator("#priceComparisonGrid > div")
        card_count = cards.count()

        first_buy_link = page.locator("#buyButton").get_attribute("href")
        matrix_links = [cards.nth(i).locator("a").get_attribute("href") for i in range(card_count)]

        step5_pass = (
            card_count >= 3 and
            bool(first_buy_link and first_buy_link.startswith("http")) and
            all(bool(link and link.startswith("http")) for link in matrix_links)
        )

        results.append((
            "Step 5: 판매처 비교 TOP 3 카드 및 아웃링크 유효성",
            step5_pass,
            f"카드 개수: {card_count}개, 1위 링크: '{first_buy_link[:35]}...', 전체 링크 유효함"
        ))

        # ----------------------------------------------------
        # Step 6. 모바일 반응형 뷰포트 (iPhone 375x812) 검증
        # ----------------------------------------------------
        print("\n[Step 6] 모바일 뷰포트 (375x812) 레이아웃 적응성 검사...")
        page.set_viewport_size({"width": 375, "height": 812})
        time.sleep(1)

        # 모바일에서도 메인 가격과 배너가 정상 노출되는지 확인
        m_price_visible = page.locator("#lowestPriceDisplay").is_visible()
        m_banner_visible = page.locator("#alertBanner").is_visible()
        m_buy_visible = page.locator("#buyButton").is_visible()

        step6_pass = m_price_visible and m_banner_visible and m_buy_visible
        step6_img = os.path.join(SCREENSHOT_DIR, "step6_mobile_layout.png")
        page.screenshot(path=step6_img, full_page=True)

        results.append((
            "Step 6: 모바일 뷰포트 반응형 레이아웃 적응성",
            step6_pass,
            f"모바일 최저가 표시: {m_price_visible}, 특가 배너: {m_banner_visible}, 구매버튼: {m_buy_visible}"
        ))

        browser.close()

    # 결과 종합 출력
    print("\n" + "=" * 70)
    print("📊 [E2E User Journey 최종 검증 결과 목록]")
    print("=" * 70)
    all_passed = True
    for name, passed, detail in results:
        status_tag = "✅ [PASS]" if passed else "❌ [FAIL]"
        if not passed:
            all_passed = False
        print(f"{status_tag} {name}")
        print(f"   └─ {detail}")

    print("=" * 70)
    if all_passed:
        print("🎉 [전체 검증 완료] 모든 전 주기적 사용자 사용성 검사가 100% PASS 되었습니다!")
    else:
        print("⚠️ [일부 실패] 검증 중 실패 항목이 존재합니다.")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = run_e2e_test()
    if not success:
        sys.exit(1)
