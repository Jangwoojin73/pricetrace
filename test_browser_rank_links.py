#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_browser_rank_links.py - 실제 웹앱 브라우저에서 1위, 2위, 3위 카드의 구매 링크 URL 실측 검증
"""

import os
import sys
import time
import socket
import subprocess
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "public", "qa_artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def ensure_server_running(port: int = 8080):
    if is_port_in_use(port):
        return None
    proc = subprocess.Popen([sys.executable, "server.py", "--port", str(port)],
                            cwd=BASE_DIR)
    time.sleep(3)
    return proc

def verify_browser_links():
    server_proc = ensure_server_running(8080)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()

            print("[TEST] 웹앱 접속...")
            page.goto("http://localhost:8080/index.html?t=" + str(time.time()), wait_until="networkidle")
            page.wait_for_timeout(2000)

            # 1. 진라면 40개 검색
            print("[TEST] '진라면 40개' 검색...")
            input_box = page.locator("#searchInput")
            input_box.fill("진라면 40개")
            input_box.press("Enter")
            page.wait_for_selector("#resultView:not(.hidden)", timeout=10000)
            page.wait_for_timeout(2000)

            # 2. 1위, 2위, 3위 카드의 '구매 페이지 열기' 링크 URL 추출
            link_locators = page.locator("#priceComparisonGrid a[target='_blank']")
            count = link_locators.count()
            print(f"[RESULT] 발견된 순위별 구매 링크 개수: {count}개")
            
            extracted_links = []
            for i in range(count):
                href = link_locators.nth(i).get_attribute("href")
                card_title = page.locator("#priceComparisonGrid h4").nth(i).inner_text()
                card_price = page.locator("#priceComparisonGrid span.text-2xl").nth(i).inner_text()
                extracted_links.append((card_title, card_price, href))
                print(f"  -> [{i+1}위 카드] {card_title} ({card_price}원)")
                print(f"     URL: {href}")

            # 스크린샷 캡처
            shot_path = os.path.join(ARTIFACTS_DIR, "verify_unique_rank_links.png")
            page.screenshot(path=shot_path, full_page=False)
            print(f"[SCREENSHOT] {shot_path}")

            # URL 고유성 검증
            urls_only = [x[2] for x in extracted_links]
            is_all_unique = len(set(urls_only)) == len(urls_only)
            print(f"[VERIFY] 1위~3위 링크 고유성(중복 없음): {is_all_unique}")

            # 3. 실시간 랭킹 품목(미강 짤순이)도 동일하게 검증
            print("\n[TEST] 실시간 랭킹 품목 '미강 다짜고짜 짤순이' 검색...")
            page.locator("#backToHomeBtn").click()
            page.wait_for_timeout(500)
            input_box = page.locator("#searchInput")
            input_box.fill("미강 다짜고짜 짤순이")
            input_box.press("Enter")
            page.wait_for_selector("#resultView:not(.hidden)", timeout=10000)
            page.wait_for_timeout(2000)

            link_locators2 = page.locator("#priceComparisonGrid a[target='_blank']")
            count2 = link_locators2.count()
            print(f"[RESULT] 발견된 순위별 구매 링크 개수: {count2}개")
            extracted_links2 = []
            for i in range(count2):
                href = link_locators2.nth(i).get_attribute("href")
                card_title = page.locator("#priceComparisonGrid h4").nth(i).inner_text()
                card_price = page.locator("#priceComparisonGrid span.text-2xl").nth(i).inner_text()
                extracted_links2.append((card_title, card_price, href))
                print(f"  -> [{i+1}위 카드] {card_title} ({card_price}원)")
                print(f"     URL: {href}")

            urls_only2 = [x[2] for x in extracted_links2]
            is_all_unique2 = len(set(urls_only2)) == len(urls_only2)
            print(f"[VERIFY] 실시간 품목 1위~3위 링크 고유성(중복 없음): {is_all_unique2}")

            shot_path2 = os.path.join(ARTIFACTS_DIR, "verify_unique_trending_links.png")
            page.screenshot(path=shot_path2, full_page=False)
            print(f"[SCREENSHOT] {shot_path2}")

            browser.close()
            assert is_all_unique, "Expected all 3 Jinramyun links to be unique!"
            assert is_all_unique2, "Expected all 3 trending links to be unique!"
            print("[SUCCESS] All Browser Rank Links Verified Successfully!")
    finally:
        if server_proc:
            server_proc.terminate()

if __name__ == "__main__":
    verify_browser_links()
