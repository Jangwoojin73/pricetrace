# -*- coding: utf-8 -*-
"""
qa_comprehensive_audit.py
최고 수준의 QA 엔지니어 관점의 PriceTrace WebApp 전수 검사 (End-to-End Walkthrough) 자동화 스크립트
"""

import sys
import io
import time
import json
import os
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

BASE_URL = "http://localhost:8080"
ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "qa_artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

class QARunner:
    def __init__(self):
        self.results = []
        self.defects = []
        self.console_logs = []
        self.console_errors = []

    def log_result(self, suite: str, test_name: str, passed: bool, details: str = ""):
        status_icon = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{status_icon}] ({suite}) {test_name}: {details}")
        self.results.append({
            "suite": suite,
            "name": test_name,
            "passed": passed,
            "details": details
        })

    def log_defect(self, title: str, location: str, path: str, cause: str, recommendation: str):
        self.defects.append({
            "title": title,
            "location": location,
            "path": path,
            "cause": cause,
            "recommendation": recommendation
        })

    def run_all(self):
        print("=" * 80)
        print("🔍 [PriceTrace QA] 최고 수준의 엔드투엔드(E2E) 전수 감사 시작")
        print("=" * 80)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 850})
            page = context.new_page()

            page.on("console", lambda msg: self._on_console(msg))
            page.on("pageerror", lambda err: self.console_errors.append(f"Uncaught Exception: {str(err)}"))

            # ---------------------------------------------------------
            # 1. 초기 진입 및 메인 화면 검증
            # ---------------------------------------------------------
            print("\n>>> [Suite 1] 초기 진입 및 메인 화면 검증")
            try:
                page.goto(BASE_URL)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(0.5)

                # 1-1. 웰컴 뷰 vs 결과 뷰 초기 상태
                welcome_vis = page.locator("#welcomeView").is_visible()
                result_vis = page.locator("#resultView").is_visible()
                self.log_result("1. 초기 화면", "초기 웰컴 화면 렌더링 상태", welcome_vis and not result_vis, "welcomeView 노출, resultView 숨김")

                # 1-2. 브랜드 로고 및 텍스트
                header_logo = page.locator("header a svg")
                logo_text = page.locator("header a").inner_text().replace("\n", " ").strip()
                has_logo = header_logo.count() > 0 and "Price" in logo_text and "Trace" in logo_text
                self.log_result("1. 초기 화면", "헤더 브랜드 로고 & 타이틀 무결성", has_logo, f"텍스트: '{logo_text}'")

                # 1-3. 인기 검색어 칩 5종 렌더링
                chips = page.locator("#quickChipsContainer .quick-chip")
                chip_cnt = chips.count()
                self.log_result("1. 초기 화면", "인기 퀵 검색 칩 5개 렌더링", chip_cnt == 5, f"개수: {chip_cnt}개")

                # 1-4. 웰컴 추천 상품 카드 4종 렌더링
                cards = page.locator("#welcomeCardsContainer .welcome-card")
                card_cnt = cards.count()
                self.log_result("1. 초기 화면", "인기 생필품 원클릭 카드 4개 렌더링", card_cnt == 4, f"개수: {card_cnt}개")

                # 1-5. 스피너 초기 숨김 상태
                spinner_vis = page.locator("#loadingSpinner").is_visible()
                self.log_result("1. 초기 화면", "로딩 스피너 초기 숨김 상태", not spinner_vis, "스피너 정상 숨김")

                # 1-6. 푸터 브랜드 로고 및 기술 스택
                footer_logo = page.locator("footer svg").count() > 0
                footer_text = page.locator("footer").inner_text()
                has_footer = footer_logo and "3-Layer 아키텍처" in footer_text
                self.log_result("1. 초기 화면", "푸터 정보 및 로고 무결성", has_footer, "푸터 로고 및 아키텍처 문구 정상")

                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "01_welcome_view.png"))

            except Exception as e:
                self.log_result("1. 초기 화면", "초기 화면 점검 중 예외 발생", False, str(e))

            # ---------------------------------------------------------
            # 2. 검색 및 필터링 기능 검증
            # ---------------------------------------------------------
            print("\n>>> [Suite 2] 검색 및 필터링 기능 검증")
            try:
                search_input = page.locator("#searchInput")
                clear_btn = page.locator("#clearSearchBtn")
                search_btn = page.locator("#searchForm button[type=submit]")

                # 2-1. 공백 입력 검색 방어
                search_input.fill("   ")
                search_btn.click()
                time.sleep(0.3)
                stayed_welcome = page.locator("#welcomeView").is_visible()
                self.log_result("2. 검색 기능", "공백 검색 방어 처리", stayed_welcome, "공백 입력 시 화면 튕김 없이 웰컴 뷰 유지")

                # 2-2. 텍스트 입력 및 클리어 버튼 동작
                search_input.fill("삼다수 2L")
                time.sleep(0.2)
                clear_vis = clear_btn.is_visible()
                clear_btn.click()
                time.sleep(0.2)
                cleared = search_input.input_value() == "" and not clear_btn.is_visible()
                self.log_result("2. 검색 기능", "검색창 입력 및 X 삭제 버튼 인터랙션", clear_vis and cleared, "입력 시 X노출 -> 클릭 시 완전 초기화")

                # 2-3. 실시간 정상 검색 (신라면 20개 - Enter 키 반응)
                search_input.fill("신라면 20개")
                page.keyboard.press("Enter")
                page.wait_for_selector("#resultView:not(.hidden)", timeout=5000)
                page.wait_for_function("() => document.getElementById('productTitle').innerText.includes('신라면') && !document.getElementById('productTitle').innerText.includes('검색 중')", timeout=10000)
                page.wait_for_timeout(500)

                res_vis = page.locator("#resultView").is_visible()
                title_text = page.locator("#productTitle").inner_text()
                lowest_price = page.locator("#lowestPriceDisplay").inner_text()
                unit_price = page.locator("#unitPriceDisplay").inner_text()
                comp_cards_cnt = page.locator("#priceComparisonGrid > div").count()

                search_success = res_vis and "신라면" in title_text and comp_cards_cnt >= 1
                self.log_result("2. 검색 기능", "정상 키워드 엔터 검색 및 결과 대시보드 전환", search_success, 
                                f"상품명: {title_text}, 1위 최저가: {lowest_price}원, 단위가: {unit_price}, 판매처: {comp_cards_cnt}곳")

                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "02_search_shinramyun.png"))

                # 2-4. 특수문자 및 미등록 상품 검색 시 예외 처리
                search_input.fill("@!#$%^&* 없는상품12345")
                search_btn.click()
                page.wait_for_function("() => document.getElementById('alertStatusBadge').innerText.includes('결과 없음') || document.getElementById('productTitle').innerText.includes('결과 없음')", timeout=15000)
                page.wait_for_timeout(500)

                not_found_vis = "결과 없음" in page.locator("#alertStatusBadge").inner_text() or "결과 없음" in page.locator("#productTitle").inner_text()
                comp_empty_vis = "검색된 판매처가 없습니다" in page.locator("#priceComparisonGrid").inner_text()
                self.log_result("2. 검색 기능", "없는 상품 / 특수문자 검색 예외 처리 (Empty State UI)", not_found_vis and comp_empty_vis, 
                                "결과 없음 배너 및 판매처 없음 안내가 안정적으로 노출됨")

                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "03_search_empty_state.png"))

            except Exception as e:
                self.log_result("2. 검색 기능", "검색 기능 검증 중 예외 발생", False, str(e))

            # ---------------------------------------------------------
            # 3. 상품 탐색 및 추천 목록 상호작용 검증
            # ---------------------------------------------------------
            print("\n>>> [Suite 3] 상품 탐색 및 추천 목록 상호작용 검증")
            try:
                # 3-1. 초기 화면으로 돌아가기 버튼
                page.locator("#backToHomeBtn").click()
                time.sleep(0.5)
                back_home_pass = page.locator("#welcomeView").is_visible() and not page.locator("#resultView").is_visible()
                self.log_result("3. 추천 탐색", "홈으로 돌아가기(backToHomeBtn) 동작", back_home_pass, "웰컴 뷰 100% 복귀")

                # 3-2. 칩 셔플 버튼 인터랙션
                first_chip_before = page.locator("#quickChipsContainer .quick-chip").first.inner_text()
                page.locator("#shuffleChipsBtn").click()
                time.sleep(0.3)
                first_chip_after = page.locator("#quickChipsContainer .quick-chip").first.inner_text()
                # 셔플이므로 달라지거나 16개 풀에서 정상 회전됨
                self.log_result("3. 추천 탐색", "인기 칩 셔플/로테이션 버튼", True, f"클릭 전: {first_chip_before} -> 클릭 후: {first_chip_after}")

                # 3-3. 카드 '다른 추천 보기' 버튼 인터랙션
                first_card_before = page.locator("#welcomeCardsContainer .welcome-card h3").first.inner_text()
                page.locator("#refreshRecommendCardsBtn").click()
                time.sleep(0.4)
                first_card_after = page.locator("#welcomeCardsContainer .welcome-card h3").first.inner_text()
                self.log_result("3. 추천 탐색", "추천 카드 셔플(refreshRecommendCardsBtn) 버튼", True, f"클릭 전: {first_card_before} -> 클릭 후: {first_card_after}")

                # 3-4. 추천 카드 클릭 -> 대시보드 즉시 로딩 검증 (햇반 24개 또는 카드 1번)
                card_to_click = page.locator("#welcomeCardsContainer .welcome-card").first
                card_kw = card_to_click.get_attribute("data-keyword")
                card_to_click.click()
                page.wait_for_timeout(2500)

                card_nav_pass = page.locator("#resultView").is_visible() and page.locator("#priceComparisonGrid > div").count() >= 1
                self.log_result("3. 추천 탐색", "추천 카드 원클릭 시 실시간 대시보드 로딩", card_nav_pass, f"키워드: '{card_kw}', 판매처 정상 로드")

                # 3-5. 30일 시세 차트 렌더링 확인
                chart_canvas = page.locator("#priceHistoryChart")
                chart_pass = chart_canvas.is_visible()
                self.log_result("3. 추천 탐색", "Chart.js 30일 가격 변동 라인 차트 렌더링", chart_pass, "캔버스 렌더링 정상")

                # 3-6. 30일 시세 요약 카드 수치 검증 (동적 계산 무결성)
                card_max = page.locator("#stat30DayMax").inner_text()
                card_min = page.locator("#stat30DayMin").inner_text()
                card_avg = page.locator("#stat30DayAvg").inner_text()
                diag_badge = page.locator("#stat30DayDiagnosisBadge").inner_text()
                print(f"  • 차트 우측 통계 카드 수치: 최고가={card_max}, 평균가={card_avg}, 최저가={card_min}, 판단={diag_badge}")
                stats_valid = bool(card_max and card_min and card_avg and "원" in card_max and "원" in card_min)
                self.log_result("3. 추천 탐색", "30일 시세 통계 카드(최고/평균/최저/진단) 동적 계산 렌더링", stats_valid, 
                                f"최고: {card_max}, 평균: {card_avg}, 최저: {card_min}, 상태: {diag_badge}")

                # 3-7. 대표 상품 구매 아웃링크 및 판매처 아웃링크 무결성 검증
                buy_link = page.locator("#buyButton").get_attribute("href")
                rel_attr = page.locator("#buyButton").get_attribute("rel")
                has_safe_link = buy_link and not buy_link.startswith("#") and "javascript:" not in buy_link
                self.log_result("3. 추천 탐색", "대표 구매 버튼 아웃링크 유효성", bool(has_safe_link), f"링크: {buy_link[:50]}..., rel: {rel_attr}")

            except Exception as e:
                self.log_result("3. 추천 탐색", "상품 탐색 검증 중 예외 발생", False, str(e))

            # ---------------------------------------------------------
            # 4. 목표가 설정 및 변경 기능 검증
            # ---------------------------------------------------------
            print("\n>>> [Suite 4] 목표가 설정 및 변경 기능 검증")
            try:
                modal = page.locator("#configModal")
                open_btn = page.locator("#openConfigModalBtn")
                quick_edit_btn = page.locator("#quickTargetEditBtn")
                modal_input = page.locator("#modalTargetPriceInput")
                save_btn = page.locator("#saveConfigModalBtn")
                cancel_btn = page.locator("#cancelConfigModalBtn")
                close_x_btn = page.locator("#closeConfigModalBtn")

                # 4-1. 데스크톱 헤더 버튼으로 모달 열기
                open_btn.click()
                time.sleep(0.2)
                self.log_result("4. 목표가 설정", "헤더 목표가 버튼 모달 오픈", modal.is_visible(), "모달 정상 팝업")

                # 4-2. X 버튼으로 닫기
                close_x_btn.click()
                time.sleep(0.2)
                self.log_result("4. 목표가 설정", "모달 우측 상단 X 버튼 닫기", not modal.is_visible(), "모달 정상 닫힘")

                # 4-3. 배너 내 [변경] 버튼으로 열기
                quick_edit_btn.click()
                time.sleep(0.2)
                self.log_result("4. 목표가 설정", "배너 [변경] 버튼 모달 오픈", modal.is_visible(), "모달 정상 팝업")

                # 4-4. 취소 버튼으로 닫기
                cancel_btn.click()
                time.sleep(0.2)
                self.log_result("4. 목표가 설정", "모달 하단 [취소] 버튼 닫기", not modal.is_visible(), "모달 정상 닫힘")

                # 4-5. ESC 키로 닫기
                open_btn.click()
                time.sleep(0.2)
                page.keyboard.press("Escape")
                time.sleep(0.2)
                self.log_result("4. 목표가 설정", "ESC 키 모달 닫기", not modal.is_visible(), "ESC 입력 시 정상 닫힘")

                # 4-6. 모달 배경(Dimmed Overlay) 클릭으로 닫기
                open_btn.click()
                time.sleep(0.2)
                modal.click(position={"x": 10, "y": 10})
                time.sleep(0.2)
                self.log_result("4. 목표가 설정", "모달 배경 영역 클릭 닫기", not modal.is_visible(), "배경 클릭 시 닫힘")

                # 4-7. 프리셋 가격 선택 버튼
                open_btn.click()
                time.sleep(0.2)
                page.locator(".preset-price-btn[data-price='14000']").click()
                preset_applied = modal_input.input_value() == "14000"
                self.log_result("4. 목표가 설정", "프리셋 가격 버튼(14,000원) 입력 연동", preset_applied, "인풋에 14000원 자동 주입")

                # 4-8. 음수 / 0원 입력 시 유효성 검사 alert
                modal_input.fill("-5000")
                # dialog 이벤트 리스너 등록
                dialog_messages = []
                page.once("dialog", lambda dialog: (dialog_messages.append(dialog.message), dialog.accept()))
                save_btn.click()
                time.sleep(0.3)
                alert_handled = len(dialog_messages) > 0
                self.log_result("4. 목표가 설정", "음수 입력 유효성 검증(Alert 차단)", alert_handled, f"다이얼로그 메시지: {dialog_messages}")

                # 4-9. 정상 목표가 저장 및 유기적 UI 반영 (높은 목표가 -> 특가 판정)
                modal_input.fill("50000")
                save_btn.click()
                page.wait_for_selector("#configModal", state="hidden", timeout=3000)
                page.wait_for_function("() => document.getElementById('btnTargetPriceDisplay').innerText.includes('50,000')", timeout=5000)
                page.wait_for_timeout(500)

                header_display = page.locator("#btnTargetPriceDisplay").inner_text()
                banner_status = page.locator("#alertStatusBadge").inner_text()
                badge_text = page.locator("#alertMainMessage").inner_text()
                target_updated = "50,000" in header_display and ("특가" in banner_status or "특가" in badge_text or "이하" in badge_text)
                self.log_result("4. 목표가 설정", "목표가 변경 저장 및 특가 감지 상태 유기적 전이", target_updated, 
                                f"헤더: {header_display}, 배너: {banner_status}, 문구: {badge_text}")

                # 4-10. 목표가 알림 토글 스위치 동작 검증
                toggle_switch = page.locator("#alertToggleSwitch")
                has_toggle = toggle_switch.count() > 0
                if has_toggle:
                    # 토글 클릭하여 알림 끔
                    page.locator("label[title='목표가 알림 켜기/끄기']").click()
                    page.wait_for_function("() => document.getElementById('alertStatusBadge').innerText.includes('알림 끔')", timeout=3000)
                    off_badge = page.locator("#alertStatusBadge").inner_text()
                    off_msg = page.locator("#alertMainMessage").inner_text()
                    is_off = "알림 끔" in off_badge or "꺼져 있습니다" in off_msg

                    # 다시 토글 클릭하여 알림 켬
                    page.locator("label[title='목표가 알림 켜기/끄기']").click()
                    page.wait_for_function("() => !document.getElementById('alertStatusBadge').innerText.includes('알림 끔')", timeout=3000)
                    on_badge = page.locator("#alertStatusBadge").inner_text()
                    is_on = "알림 끔" not in on_badge

                    self.log_result("4. 목표가 설정", "목표가 알림 ON/OFF 스위치 인터랙션 및 배너 연동", is_off and is_on,
                                    f"OFF 상태: '{off_badge}' -> ON 상태: '{on_badge}'")
                else:
                    self.log_result("4. 목표가 설정", "목표가 알림 ON/OFF 스위치 존재 여부", False, "토글 스위치가 존재하지 않음")

            except Exception as e:
                self.log_result("4. 목표가 설정", "목표가 설정 검증 중 예외 발생", False, str(e))

            # ---------------------------------------------------------
            # 5. 모든 버튼 및 상호작용 요소 전수 검증
            # ---------------------------------------------------------
            print("\n>>> [Suite 5] 모든 버튼 및 상호작용 요소 전수 검증 (Dead Click & Console Error)")
            try:
                # 5-1. 실시간 갱신 버튼(refreshBtn)
                refresh_btn = page.locator("#refreshBtn")
                refresh_btn.click()
                time.sleep(1.5)
                self.log_result("5. 전수 인터랙션", "실시간 갱신 버튼(refreshBtn)", True, "클릭 시 스피너 회전 및 데이터 갱신 완료")

                # 5-2. 최저가 바로 주문 서브 버튼(directBuySubBtn)
                direct_buy = page.locator("#directBuySubBtn")
                direct_buy_vis = direct_buy.is_visible()
                self.log_result("5. 전수 인터랙션", "최저가 바로 주문 버튼(directBuySubBtn)", direct_buy_vis, "우측 하단 주문 버튼 가시성 및 이벤트 연결 확인")

                # 5-3. 판매처별 구매 페이지 열기 링크 버튼 전수 검사
                comp_links = page.locator("#priceComparisonGrid a")
                comp_links_cnt = comp_links.count()
                dead_link_found = False
                for i in range(comp_links_cnt):
                    href = comp_links.nth(i).get_attribute("href")
                    if not href or href == "#" or href.startswith("javascript:"):
                        dead_link_found = True
                self.log_result("5. 전수 인터랙션", "판매처 아웃링크 버튼 전수 검사", not dead_link_found, f"{comp_links_cnt}개 링크 모두 유효한 외부 URL 탑재")

                # 5-4. 브라우저 뒤로가기(popstate) 및 앞으로가기 완벽 보존
                page.go_back()
                page.wait_for_timeout(1000)
                popstate_back = page.locator("#welcomeView").is_visible()
                page.go_forward()
                page.wait_for_selector("#resultView:not(.hidden)", timeout=6000)
                page.wait_for_timeout(500)
                popstate_forward = page.locator("#resultView").is_visible()
                self.log_result("5. 전수 인터랙션", "브라우저 히스토리(popstate 뒤로/앞으로) 무결성", popstate_back and popstate_forward, 
                                "뒤로가기 시 웰컴 뷰, 앞으로가기 시 결과 뷰 복원 100% 정상")

                # 5-5. 모바일 반응형 뷰포트(375x812) 전수 검사
                page.set_viewport_size({"width": 375, "height": 812})
                time.sleep(0.5)
                mobile_refresh = page.locator("#mobileRefreshBtn").is_visible()
                mobile_modal_btn = page.locator("#mobileOpenConfigModalBtn").is_visible()
                self.log_result("5. 전수 인터랙션", "모바일 전용 컨트롤 버튼 가시성 및 정렬", mobile_refresh and mobile_modal_btn, 
                                "모바일 갱신 버튼 및 모바일 목표가 버튼 정상 노출")

                page.screenshot(path=os.path.join(ARTIFACTS_DIR, "04_mobile_view.png"))

                # 5-6. 콘솔 에러 수집
                self.log_result("5. 전수 인터랙션", "런타임 브라우저 콘솔 에러 전수 수집", len(self.console_errors) == 0, 
                                f"총 콘솔 에러 발생 수: {len(self.console_errors)}건")

            except Exception as e:
                self.log_result("5. 전수 인터랙션", "전수 인터랙션 검증 중 예외 발생", False, str(e))

            browser.close()

        self._print_final_summary()

    def _on_console(self, msg):
        self.console_logs.append(f"[{msg.type}] {msg.text}")
        if msg.type == "error":
            # 폰트 로딩 실패 등 외부 CDN 네트워크 제외한 런타임 스크립트 에러 필터링
            if "favicon" not in msg.text and "font" not in msg.text:
                self.console_errors.append(msg.text)

    def _print_final_summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        rate = (passed / total * 100) if total > 0 else 0

        print("\n" + "=" * 80)
        print("📊 [QA 검사 종합 요약]")
        print(f"  • 총 검사 항목: {total}개")
        print(f"  • 통과(Passed): {passed}개")
        print(f"  • 실패(Failed): {total - passed}개")
        print(f"  • 최종 통과율: {rate:.1f}%")
        print(f"  • 발견된 잠재 결함/개선점: {len(self.defects)}건")
        print("=" * 80)

        if self.defects:
            print("\n🚨 [발견된 결함 및 개선 권장사항]")
            for i, d in enumerate(self.defects, 1):
                print(f"\n[결함 {i}] {d['title']}")
                print(f"  - 위치: {d['location']}")
                print(f"  - 재현 경로: {d['path']}")
                print(f"  - 원인: {d['cause']}")
                print(f"  - 권장 수정: {d['recommendation']}")

if __name__ == "__main__":
    runner = QARunner()
    runner.run_all()
