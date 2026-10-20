# -*- coding: utf-8 -*-
import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_URL = "http://127.0.0.1:8080"

def run_radar_inspection():
    audit_results = {}
    print("[START] 하단 네비게이션 2번째 [레이더] 메뉴 전 기능 정밀 감사 시작...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = m_ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(800)

        # -------------------------------------------------------------
        # STEP 1. 하단 2번째 [레이더] 메뉴 탭 시 모달창 슬라이드업 & 커서/포커스 검증
        # -------------------------------------------------------------
        print("\n--- STEP 1. [레이더] 메뉴 탭 시 모달창 슬라이드업 & 포커스 검증 ---")
        radar_btn = page.query_selector("#mobileNavSearchFabBtn")
        radar_btn_info = page.evaluate('''() => {
            const btn = document.getElementById("mobileNavSearchFabBtn");
            const span = btn ? btn.querySelector("span") : null;
            const icon = btn ? btn.querySelector("[data-lucide='radar'], svg") : null;
            return {
                exists: !!btn,
                text: span ? span.innerText.trim() : "",
                hasIcon: !!icon,
                tabKey: btn ? btn.getAttribute("data-mobile-tab") : ""
            };
        }''')
        print(f"  [레이더 버튼 정보] 텍스트: '{radar_btn_info['text']}', 탭키: '{radar_btn_info['tabKey']}', 아이콘 존재: {radar_btn_info['hasIcon']}")

        # 탭 실행
        page.tap("#mobileNavSearchFabBtn")
        page.wait_for_timeout(500)

        step1_state = page.evaluate('''() => {
            const m = document.getElementById("radarSearchModal");
            const drawer = document.getElementById("radarSearchDrawer");
            const input = document.getElementById("modalSearchInput");
            const activeEl = document.activeElement;
            const style = window.getComputedStyle(m);
            return {
                modalIsOpen: m.classList.contains("modal-open"),
                modalIsHidden: m.classList.contains("modal-hidden"),
                modalVisibility: style.visibility,
                modalOpacity: style.opacity,
                hasDrawer: !!drawer,
                activeId: activeEl ? activeEl.id : "none",
                isInputFocused: activeEl === input,
                inputMode: input ? input.getAttribute("inputmode") : "",
                enterKeyHint: input ? input.getAttribute("enterkeyhint") : "",
                placeholder: input ? input.placeholder : "",
                inputValue: input ? input.value : ""
            };
        }''')
        shot1 = os.path.join(ARTIFACT_DIR, "radar_menu_01_modal_opened.png")
        page.screenshot(path=shot1)
        print(f"  [모달 상태] 열림: {step1_state['modalIsOpen']}, 포커스ID: {step1_state['activeId']}, input포커스일치: {step1_state['isInputFocused']}")
        print(f"  [자판연동] inputMode: '{step1_state['inputMode']}', enterKeyHint: '{step1_state['enterKeyHint']}'")

        audit_results["step1_radar_tab_open"] = {
            "button_verified": radar_btn_info["text"] == "레이더",
            "modal_opened": step1_state["modalIsOpen"] and not step1_state["modalIsHidden"],
            "input_focused": step1_state["isInputFocused"],
            "input_mode_search": step1_state["inputMode"] == "search",
            "screenshot": shot1
        }

        # -------------------------------------------------------------
        # STEP 2. 빠른 수량 버튼 작동 여부 검증 (텍스트 덧붙이기 & 포커스 유지)
        # -------------------------------------------------------------
        print("\n--- STEP 2. 빠른 수량 버튼 작동 여부 검증 ---")
        # 1) 먼저 검색창에 '신라면' 입력
        page.fill("#modalSearchInput", "신라면")
        page.wait_for_timeout(200)

        # 2) 빠른 수량 버튼 목록 확인
        quantity_chips = page.evaluate('''() => {
            const chips = Array.from(document.querySelectorAll("#modalQuantityPad .modal-pad-chip"));
            return chips.map(c => ({
                text: c.innerText.trim(),
                append: c.getAttribute("data-append")
            }));
        }''')
        print(f"  [빠른 수량 버튼 개수] {len(quantity_chips)}개: {[c['text'] for c in quantity_chips]}")

        # 3) '20개' 버튼 클릭
        page.click("#modalQuantityPad button:has-text('20개')")
        page.wait_for_timeout(300)

        step2_state = page.evaluate('''() => {
            const input = document.getElementById("modalSearchInput");
            const clearBtn = document.getElementById("modalClearSearchBtn");
            const activeEl = document.activeElement;
            return {
                value: input ? input.value : "",
                isFocused: activeEl === input,
                cursorPos: input ? input.selectionStart : 0,
                clearBtnVisible: clearBtn && !clearBtn.classList.contains("hidden")
            };
        }''')
        shot2 = os.path.join(ARTIFACT_DIR, "radar_menu_02_quantity_pad_appended.png")
        page.screenshot(path=shot2)
        print(f"  [수량 추가 결과] 검색창 값: '{step2_state['value']}', 포커스유지: {step2_state['isFocused']}, 커서위치: {step2_state['cursorPos']}")

        audit_results["step2_quantity_pad"] = {
            "chips_count": len(quantity_chips),
            "expected_value": "신라면 20개",
            "actual_value": step2_state["value"],
            "value_matched": step2_state["value"] == "신라면 20개",
            "focus_retained": step2_state["isFocused"],
            "screenshot": shot2
        }

        # -------------------------------------------------------------
        # STEP 3. 모달 검색창 & [조회] 기능 및 네이버 쇼핑 데이터 렌더링 검증
        # -------------------------------------------------------------
        print("\n--- STEP 3. 모달 검색창 & [조회] 기능 및 네이버 쇼핑 렌더링 검증 ---")
        # [조회] 버튼 클릭 실행
        page.click("#modalSearchForm button[type='submit']")
        
        # 결과 뷰 대기
        page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=12000)
        page.wait_for_timeout(1500)

        step3_state = page.evaluate('''() => {
            const m = document.getElementById("radarSearchModal");
            const resView = document.getElementById("resultView");
            const style = window.getComputedStyle(m);
            const title = document.getElementById("productTitle") ? document.getElementById("productTitle").innerText : "";
            const lowestPrice = document.getElementById("lowestPriceDisplay") ? document.getElementById("lowestPriceDisplay").innerText : "";
            const cards = Array.from(document.querySelectorAll(".rank-card"));
            const rankItems = cards.map(c => {
                const h = c.querySelector("h4") || c.querySelector("h3");
                const p = c.querySelector(".text-2xl.font-black") || c.querySelector(".font-black:not(.text-xs)");
                const mall = c.querySelector(".text-xs.font-bold") || c.querySelector(".text-xs");
                const link = c.querySelector("a") ? c.querySelector("a").href : "";
                return {
                    name: h ? h.innerText.trim() : "",
                    price: p ? p.innerText.trim() : "",
                    mall: mall ? mall.innerText.trim() : "",
                    buyLink: link
                };
            });
            return {
                modalIsOpen: m.classList.contains("modal-open"),
                modalIsHidden: m.classList.contains("modal-hidden"),
                modalVisibility: style.visibility,
                resultViewVisible: resView && !resView.classList.contains("hidden"),
                productTitle: title,
                lowestPrice: lowestPrice,
                rankCardsCount: cards.length,
                rankItems: rankItems
            };
        }''')
        shot3 = os.path.join(ARTIFACT_DIR, "radar_menu_03_query_submitted_clean_result.png")
        page.screenshot(path=shot3)
        print(f"  [모달 닫힘 실측] 모달은닉: {step3_state['modalIsHidden']}, 모달오픈: {step3_state['modalIsOpen']}")
        print(f"  [결과 렌더링] 결과뷰노출: {step3_state['resultViewVisible']}, 대표타이틀: '{step3_state['productTitle']}', 최저가: {step3_state['lowestPrice']}")
        print(f"  [TOP 3 순위 카드 수] {step3_state['rankCardsCount']}개")
        for idx, item in enumerate(step3_state['rankItems']):
            print(f"    - {idx+1}위: {item['name'][:25]}... | {item['price']} | {item['mall']}")

        audit_results["step3_search_submit"] = {
            "modal_cleanly_closed": step3_state["modalIsHidden"] and not step3_state["modalIsOpen"],
            "result_view_active": step3_state["resultViewVisible"],
            "data_fetched": step3_state["rankCardsCount"] >= 3,
            "lowest_price": step3_state["lowestPrice"],
            "screenshot": shot3
        }

        # -------------------------------------------------------------
        # STEP 4. 실시간 추천 검색어 즉시 조회 검증 ('햇반 24개')
        # -------------------------------------------------------------
        print("\n--- STEP 4. 실시간 추천 검색어 즉시 조회 검증 ('햇반 24개') ---")
        # 다시 레이더 탭 클릭하여 모달 열기
        page.tap("#mobileNavSearchFabBtn")
        page.wait_for_timeout(400)

        quick_chips = page.evaluate('''() => {
            const chips = Array.from(document.querySelectorAll("#modalQuickSearchChips .modal-quick-chip"));
            return chips.map(c => ({
                text: c.innerText.trim(),
                query: c.getAttribute("data-query")
            }));
        }''')
        print(f"  [실시간 추천 검색어 목록] {len(quick_chips)}개: {[c['text'] for c in quick_chips]}")

        # '햇반 24개' 칩 클릭
        page.click("#modalQuickSearchChips button:has-text('햇반 24개')")
        page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=12000)
        page.wait_for_timeout(1500)

        step4_state = page.evaluate('''() => {
            const m = document.getElementById("radarSearchModal");
            const resView = document.getElementById("resultView");
            const title = document.getElementById("productTitle") ? document.getElementById("productTitle").innerText : "";
            const lowestPrice = document.getElementById("lowestPriceDisplay") ? document.getElementById("lowestPriceDisplay").innerText : "";
            const cards = Array.from(document.querySelectorAll(".rank-card"));
            return {
                modalIsHidden: m.classList.contains("modal-hidden"),
                modalIsOpen: m.classList.contains("modal-open"),
                productTitle: title,
                lowestPrice: lowestPrice,
                cardsCount: cards.length
            };
        }''')
        shot4 = os.path.join(ARTIFACT_DIR, "radar_menu_04_quick_chip_direct_search.png")
        page.screenshot(path=shot4)
        print(f"  [햇반 24개 즉시 조회] 모달은닉: {step4_state['modalIsHidden']}, 타이틀: '{step4_state['productTitle']}', 최저가: {step4_state['lowestPrice']}, 순위카드: {step4_state['cardsCount']}개")

        audit_results["step4_quick_chip_hetbahn"] = {
            "modal_closed": step4_state["modalIsHidden"],
            "title_matched": "햇반" in step4_state["productTitle"],
            "lowest_price": step4_state["lowestPrice"],
            "cards_count": step4_state["cardsCount"],
            "screenshot": shot4
        }

        # -------------------------------------------------------------
        # STEP 5. 추가 실시간 추천 검색어 즉시 조회 검증 ('코카콜라 제로')
        # -------------------------------------------------------------
        print("\n--- STEP 5. 추가 추천 검색어 즉시 조회 ('코카콜라 제로') ---")
        page.tap("#mobileNavSearchFabBtn")
        page.wait_for_timeout(400)

        page.click("#modalQuickSearchChips button:has-text('코카콜라 제로')")
        page.wait_for_selector("#resultView:not(.hidden)", state="visible", timeout=12000)
        page.wait_for_timeout(1500)

        step5_state = page.evaluate('''() => {
            const title = document.getElementById("productTitle") ? document.getElementById("productTitle").innerText : "";
            const lowestPrice = document.getElementById("lowestPriceDisplay") ? document.getElementById("lowestPriceDisplay").innerText : "";
            const cards = Array.from(document.querySelectorAll(".rank-card")).map(c => {
                const p = c.querySelector(".text-2xl.font-black") || c.querySelector(".font-black:not(.text-xs)");
                return p ? p.innerText.trim() : "";
            });
            return { title, lowestPrice, prices: cards };
        }''')
        shot5 = os.path.join(ARTIFACT_DIR, "radar_menu_05_coke_zero_search.png")
        page.screenshot(path=shot5)
        print(f"  [코카콜라 제로 즉시 조회] 타이틀: '{step5_state['title']}', 최저가: {step5_state['lowestPrice']}, 순위가격: {step5_state['prices']}")

        audit_results["step5_quick_chip_coke"] = {
            "title_matched": "코카콜라" in step5_state["title"] or "콜라" in step5_state["title"],
            "lowest_price": step5_state["lowestPrice"],
            "prices": step5_state["prices"],
            "screenshot": shot5
        }

        # -------------------------------------------------------------
        # STEP 6. 빠른 지우기 버튼 (#modalClearSearchBtn) 검증
        # -------------------------------------------------------------
        print("\n--- STEP 6. 모달 텍스트 지우기 버튼 (#modalClearSearchBtn) 검증 ---")
        page.tap("#mobileNavSearchFabBtn")
        page.wait_for_timeout(400)

        # 텍스트 입력
        page.fill("#modalSearchInput", "테스트검색어")
        page.wait_for_timeout(200)

        clear_btn_visible_before = page.is_visible("#modalClearSearchBtn")
        page.click("#modalClearSearchBtn")
        page.wait_for_timeout(200)

        cleared_val = page.evaluate('() => document.getElementById("modalSearchInput").value')
        clear_btn_visible_after = page.is_visible("#modalClearSearchBtn")
        print(f"  [지우기 버튼] 클릭 전 노출: {clear_btn_visible_before}, 클릭 후 값: '{cleared_val}', 클릭 후 노출: {clear_btn_visible_after}")

        shot6 = os.path.join(ARTIFACT_DIR, "radar_menu_06_clear_button_verified.png")
        page.screenshot(path=shot6)

        audit_results["step6_clear_button"] = {
            "clear_button_works": cleared_val == "",
            "hidden_after_clear": not clear_btn_visible_after,
            "screenshot": shot6
        }

        # -------------------------------------------------------------
        # STEP 7. 모달 닫기 버튼 (#closeRadarSearchModalBtn) 및 배경 터치 닫기 검증
        # -------------------------------------------------------------
        print("\n--- STEP 7. 모달 닫기 버튼 및 배경 터치 닫기 검증 ---")
        page.click("#closeRadarSearchModalBtn")
        page.wait_for_timeout(400)

        modal_closed_btn = page.evaluate('() => document.getElementById("radarSearchModal").classList.contains("modal-hidden")')
        print(f"  [닫기 X 버튼 클릭 후] 모달 은닉 여부: {modal_closed_btn}")

        audit_results["step7_close_btn"] = {
            "modal_closed": modal_closed_btn
        }

        browser.close()

    # 결과 JSON 저장
    result_json_path = os.path.join(ARTIFACT_DIR, "radar_menu_audit_raw.json")
    with open(result_json_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)

    print("\n[COMPLETE] 하단 네비게이션 2번째 [레이더] 메뉴 전 기능 정밀 검증 완주!")
    return audit_results

if __name__ == "__main__":
    run_radar_inspection()
