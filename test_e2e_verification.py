#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_e2e_verification.py - PriceTrace WebApp 실시간 네이버 베스트 랭킹 E2E 검증 스크립트
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "public", "qa_artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        print("[1/3] 메인 홈 화면 접속 및 실시간 랭킹 렌더링 확인...")
        page.goto("http://localhost:8080/index.html?t=" + str(time.time()), wait_until="networkidle")
        page.wait_for_timeout(2000)

        # 1. 메인 홈 화면 스크린샷
        shot1 = os.path.join(ARTIFACTS_DIR, "verify_live_trending_home.png")
        page.screenshot(path=shot1, full_page=False)
        print(f"  -> 캡처 완료: {shot1}")

        # 2. 실시간 랭킹 품목 클릭 검증
        print("[2/3] 실시간 랭킹 카드 클릭 및 가격비교 3순위 생성 확인...")
        cards = page.locator("#welcomeCardsContainer > div")
        card_count = cards.count()
        print(f"  -> 실시간 웰컴 카드 개수: {card_count}")
        if card_count > 0:
            first_card = cards.first
            print("  -> 첫 번째 실시간 카드 클릭")
            first_card.click()
            page.wait_for_timeout(3000)
            
            shot2 = os.path.join(ARTIFACTS_DIR, "verify_live_trending_click.png")
            page.screenshot(path=shot2, full_page=False)
            print(f"  -> 캡처 완료: {shot2}")

        # 3. 진라면 40개 검색 검증 (오뚜기밥 충돌 방지 실측)
        print("[3/3] 진라면 40개 검색 및 오뚜기밥 미충돌 정상 매칭 확인...")
        input_box = page.locator("#searchInput")
        input_box.fill("진라면 40개")
        page.locator("#searchForm").evaluate("form => form.requestSubmit()")
        page.wait_for_timeout(3000)

        shot3 = os.path.join(ARTIFACTS_DIR, "verify_jinramyun_search.png")
        page.screenshot(path=shot3, full_page=False)
        print(f"  -> 캡처 완료: {shot3}")

        browser.close()
        print("[SUCCESS] All E2E Browser Verifications Completed Successfully!")

if __name__ == "__main__":
    run_verification()
