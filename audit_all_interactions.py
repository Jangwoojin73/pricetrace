import sys
import io
import time
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_total_audit():
    print("=" * 80)
    print("🚀 [PriceTrace WebApp] 사용자 관점 전수 인터랙션 및 버튼 무결성 전수 감사")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 콘솔 에러 리스너
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("\n--- [STEP 1] 초기 웰컴 화면 접속 및 기본 요소 검증 ---")
        page.goto("http://127.0.0.1:8080")
        page.wait_for_timeout(1000)

        assert page.locator("#welcomeView").is_visible(), "welcomeView가 표시되지 않았습니다."
        assert not page.locator("#resultView").is_visible(), "resultView가 숨겨지지 않았습니다."
        
        logo_text = page.locator("header a").inner_text().replace("\n", " ").strip()
        print(f"  ✓ 로고 텍스트: {logo_text}")
        assert "PriceTrace" in logo_text.replace(" ", ""), "로고에 PriceTrace가 없습니다."
        assert "Bot" not in logo_text, "로고에 Bot 단어가 남아있습니다."

        chips_count = page.locator("#quickChipsContainer .quick-chip").count()
        cards_count = page.locator("#welcomeCardsContainer .welcome-card").count()
        print(f"  ✓ 동적 칩 개수: {chips_count}개, 웰컴 카드 개수: {cards_count}개")
        assert chips_count == 5, f"인기 칩이 5개가 아닙니다 ({chips_count}개)."
        assert cards_count == 4, f"웰컴 카드가 4개가 아닙니다 ({cards_count}개)."

        print("\n--- [STEP 2] 셔플 및 추천 로테이션 버튼 인터랙션 검증 ---")
        initial_first_chip = page.locator("#quickChipsContainer .quick-chip").first.inner_text()
        initial_first_card = page.locator("#welcomeCardsContainer .welcome-card h3").first.inner_text()
        print(f"  • 초기 1번 칩: {initial_first_chip}, 초기 1번 카드: {initial_first_card}")

        # 칩 셔플 버튼 클릭
        page.locator("#shuffleChipsBtn").click()
        page.wait_for_timeout(300)
        shuffled_chip = page.locator("#quickChipsContainer .quick-chip").first.inner_text()
        print(f"  ✓ 칩 셔플 클릭 후 1번 칩: {shuffled_chip}")

        # 카드 '다른 추천 보기' 버튼 클릭
        page.locator("#refreshRecommendCardsBtn").click()
        page.wait_for_timeout(400)
        shuffled_card = page.locator("#welcomeCardsContainer .welcome-card h3").first.inner_text()
        print(f"  ✓ 카드 셔플 클릭 후 1번 카드: {shuffled_card}")

        print("\n--- [STEP 3] 검색창 입력 및 클리어(X) 버튼 검증 ---")
        search_input = page.locator("#searchInput")
        clear_btn = page.locator("#clearSearchBtn")
        
        assert not clear_btn.is_visible(), "초기 상태에서는 클리어 버튼이 숨겨져 있어야 합니다."
        search_input.fill("삼다수 2L 6개")
        page.wait_for_timeout(200)
        assert clear_btn.is_visible(), "텍스트 입력 시 클리어 버튼이 나타나야 합니다."
        print("  ✓ 텍스트 입력 시 클리어 버튼 노출 확인")

        clear_btn.click()
        page.wait_for_timeout(200)
        assert search_input.input_value() == "", "클리어 버튼 클릭 시 입력창이 비워져야 합니다."
        assert not clear_btn.is_visible(), "클리어 버튼 클릭 후 버튼이 숨겨져야 합니다."
        print("  ✓ 클리어 버튼 클릭 시 입력창 완전 초기화 확인")

        # 빈 상태에서 검색 시도 -> 에러 없이 웰컴 뷰 유지 확인
        page.locator("#searchForm button[type=submit]").click()
        page.wait_for_timeout(300)
        assert page.locator("#welcomeView").is_visible(), "빈 검색 시 웰컴 뷰가 안전하게 유지되어야 합니다."
        print("  ✓ 빈 검색어 제출 시 방어 로직 정상 작동 확인")

        print("\n--- [STEP 4] 웰컴 추천 카드 클릭 -> 검색 결과 화면 전환 검증 ---")
        target_card = page.locator("#welcomeCardsContainer .welcome-card").first
        selected_kw = target_card.get_attribute("data-keyword")
        selected_title = target_card.locator("h3").inner_text()
        print(f"  • 선택한 카드: [{selected_title}] (키워드: {selected_kw})")
        target_card.click()
        page.wait_for_timeout(2500)

        assert not page.locator("#welcomeView").is_visible(), "welcomeView가 숨겨져야 합니다."
        assert page.locator("#resultView").is_visible(), "resultView가 표시되어야 합니다."

        res_keyword = page.locator("#currentSearchKeywordText").inner_text()
        lowest_price = page.locator("#lowestPriceDisplay").inner_text().strip()
        comp_cards = page.locator("#priceComparisonGrid > div").count()
        print(f"  ✓ 검색 결과 뷰 활성화: 키워드=[{res_keyword}], 최저가=[{lowest_price}원], 비교판매처=[{comp_cards}개]")
        assert comp_cards >= 1, "판매처 카드가 최소 1개 이상 렌더링되어야 합니다."

        print("\n--- [STEP 5] 목표가 모달(Modal) 전수 인터랙션 검증 ---")
        open_modal_btn = page.locator("#openConfigModalBtn")
        modal = page.locator("#configModal")
        modal_input = page.locator("#modalTargetPriceInput")

        # 5-1. 모달 열기
        open_modal_btn.click()
        page.wait_for_timeout(200)
        assert modal.is_visible(), "모달이 열리지 않았습니다."
        print("  ✓ 상단 헤더 목표가 버튼 클릭 -> 모달 정상 오픈")

        # 5-2. 프리셋 버튼 클릭
        page.locator(".preset-price-btn[data-price='14000']").click()
        assert modal_input.input_value() == "14000", "프리셋 클릭 시 인풋에 14000이 반영되어야 합니다."
        print("  ✓ 모달 내 프리셋 버튼(14,000원) 연동 정상")

        # 5-3. ESC 키로 닫기
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        assert not modal.is_visible(), "ESC 키 입력 시 모달이 닫혀야 합니다."
        print("  ✓ ESC 키 입력 -> 모달 정상 닫힘")

        # 5-4. 다시 열고 바깥 배경(dim) 클릭으로 닫기
        open_modal_btn.click()
        page.wait_for_timeout(200)
        assert modal.is_visible(), "모달이 다시 열리지 않았습니다."
        # 바깥 영역(상단 여백 클릭)
        modal.click(position={"x": 10, "y": 10})
        page.wait_for_timeout(200)
        assert not modal.is_visible(), "모달 바깥 클릭 시 닫혀야 합니다."
        print("  ✓ 모달 바깥 배경 클릭 -> 모달 정상 닫힘")

        # 5-5. 목표가 변경 저장 및 동적 재계산 검증 (낮은 목표가 -> 유지 판정)
        open_modal_btn.click()
        page.wait_for_timeout(200)
        modal_input.fill("5000") # 매우 낮은 목표가
        page.keyboard.press("Enter") # 엔터키 저장 테스트
        page.wait_for_timeout(2000)

        assert not modal.is_visible(), "엔터키 저장 후 모달이 닫혀야 합니다."
        btn_target_text = page.locator("#btnTargetPriceDisplay").inner_text()
        print(f"  ✓ 헤더 목표가 텍스트: {btn_target_text}")
        assert "5,000" in btn_target_text, "헤더 목표가 표시가 5,000원으로 갱신되지 않았습니다."
        
        status_msg = page.locator("#alertMainMessage").inner_text()
        print(f"  ✓ 5,000원 설정 시 알림 상태: [{status_msg}]")
        assert "유지" in status_msg or "비쌉니다" in status_msg, "목표가보다 비싼데 유지 상태가 아닙니다."

        # 5-6. 목표가를 최저가보다 높게 설정 -> 특가 발생 검증
        open_modal_btn.click()
        page.wait_for_timeout(200)
        modal_input.fill("50000") # 매우 높은 목표가
        page.locator("#saveConfigModalBtn").click()
        page.wait_for_timeout(2000)

        status_msg_special = page.locator("#alertMainMessage").inner_text()
        print(f"  ✓ 50,000원 설정 시 알림 상태: [{status_msg_special}]")
        assert "특가 발생" in status_msg_special or "목표 가격 이하" in status_msg_special, "목표가 이하인데 특가 알림이 발동되지 않았습니다."

        print("\n--- [STEP 6] 결과 화면 내 각종 버튼 및 아웃링크 무결성 검증 ---")
        # 6-1. 대표 구매 버튼 링크 검사
        buy_btn = page.locator("#buyButton")
        buy_url = buy_btn.get_attribute("href")
        rel_attr = buy_btn.get_attribute("rel")
        ref_policy = buy_btn.get_attribute("referrerpolicy")
        print(f"  ✓ 대표 상품 구매 링크: {buy_url[:60]}...")
        print(f"    - rel 속성: {rel_attr}, referrerpolicy: {ref_policy}")
        assert "cr3.shopping.naver.com" not in buy_url, "오류 유발 cr3 브릿지 링크가 감지되었습니다."
        assert "catalog" not in buy_url or "search/all" in buy_url, "로그인 강제 링크가 남아있습니다."
        assert "no-referrer-when-downgrade" == ref_policy, "referrerpolicy 설정이 누락되었습니다."

        # 6-2. 하단 1~3위 판매처 카드 링크 전수 검사
        grid_links = page.locator("#priceComparisonGrid a")
        link_cnt = grid_links.count()
        print(f"  • 판매처 비교 카드 링크 개수: {link_cnt}개 검사 중...")
        for idx in range(link_cnt):
            lk = grid_links.nth(idx).get_attribute("href")
            print(f"    [{idx+1}위 판매처 URL]: {lk[:70]}...")
            assert "cr3.shopping.naver.com" not in lk, f"{idx+1}위에 오류 유발 cr3 링크 잔존!"
        print("  ✓ 모든 아웃링크 n2 오류 0건 및 캡차 방지 URL 정상 확인 완료")

        # 6-3. 실시간 갱신 버튼(refreshBtn) 동작 확인
        refresh_btn = page.locator("#refreshBtn")
        refresh_btn.click()
        page.wait_for_timeout(2000)
        assert page.locator("#resultView").is_visible(), "갱신 후 결과 화면이 유지되어야 합니다."
        print("  ✓ 실시간 갱신(refreshBtn) 인터랙션 성공")

        print("\n--- [STEP 7] 홈 복귀 및 브라우저 네비게이션(뒤로가기/앞으로가기) 검증 ---")
        # 7-1. [← 초기 화면으로 돌아가기] 버튼 클릭
        page.locator("#backToHomeBtn").click()
        page.wait_for_timeout(500)
        assert page.locator("#welcomeView").is_visible(), "홈 버튼 클릭 시 welcomeView가 떠야 합니다."
        assert not page.locator("#resultView").is_visible(), "홈 버튼 클릭 시 resultView는 숨겨져야 합니다."
        print("  ✓ [← 초기 화면으로 돌아가기] 버튼 클릭 시 웰컴 뷰 100% 정상 복귀 확인")

        # 7-2. 브라우저 뒤로가기 및 앞으로가기 검증
        # 다시 신라면 검색 실행
        page.locator("#searchInput").fill("농심 신라면 봉지 20개입")
        page.locator("#searchForm button[type=submit]").click()
        page.wait_for_timeout(2000)
        assert page.locator("#resultView").is_visible(), "검색 결과 진입 실패"

        # 브라우저 뒤로가기
        page.go_back()
        page.wait_for_timeout(800)
        assert page.locator("#welcomeView").is_visible(), "뒤로가기 시 웰컴 뷰로 복귀해야 합니다."
        print("  ✓ 브라우저 [뒤로가기] -> 웰컴 뷰 복귀 확인")

        # 브라우저 앞으로가기
        page.go_forward()
        page.wait_for_timeout(1000)
        assert page.locator("#resultView").is_visible(), "앞으로가기 시 검색 결과로 복귀해야 합니다."
        print("  ✓ 브라우저 [앞으로가기] -> 검색 결과 복귀 확인")

        # 스크린샷 저장
        page.screenshot(path="public/test_artifacts/total_audit_verified.png")
        print(f"\n  ✓ 전수 감사 최종 검증 스크린샷 저장 완료: public/test_artifacts/total_audit_verified.png")

        print("\n--- [STEP 8] 브라우저 콘솔 에러 로그 감사 ---")
        print(f"  • 발생한 콘솔 에러 수: {len(console_errors)}개")
        if console_errors:
            for err in console_errors:
                print(f"    ⚠️ Console Error: {err}")
        assert len(console_errors) == 0, "브라우저 콘솔 에러가 발생했습니다!"
        print("  ✓ 콘솔 에러 0건 (완전 무결) 확인!")

        browser.close()

    print("\n" + "=" * 80)
    print("🎉 [AUDIT COMPLETE] 모든 버튼과 인터랙션이 100% 무결하게 작동함을 확인했습니다!")
    print("=" * 80)

if __name__ == "__main__":
    run_total_audit()
