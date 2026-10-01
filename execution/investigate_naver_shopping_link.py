# -*- coding: utf-8 -*-
"""
네이버 쇼핑 가격비교 화면 URL 파라미터 및 최상단 가격 일치 구조 정밀 조사
1. query=코카콜라 제로 355ml 24캔 기본 검색 시 DOM 확인 (광고 상품 노출 여부, 랭킹순 vs 낮은가격순, 가격비교 탭)
2. query=코카콜라 제로 355ml 24캔&sort=price_asc (낮은 가격순 정렬 시 최상단 상품 및 가격 확인)
3. 가격비교 탭 클릭 시 URL 변화 및 최상단 상품/가격 확인
4. 카탈로그 직결 URL(catalog/...) 구조 분석
"""
from playwright.sync_api import sync_playwright
import urllib.parse
import json

def test_naver_urls():
    artifacts_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()

        # Test 1: 현재 사용 중인 URL 패턴 (&frm=NVSCPRO)
        url1 = "https://search.shopping.naver.com/search/all?query=" + urllib.parse.quote("코카콜라 제로 355ml 24캔") + "&frm=NVSCPRO"
        print(f"[Test 1] 현재 URL 접속: {url1}")
        page.goto(url1, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        page.screenshot(path=f"{artifacts_dir}\\research_naver_current.png")
        
        # 첫 번째 상품 정보 추출
        items1 = page.locator("div[class*='product_item__']").all()
        print(f" -> 발견된 상품 아이템 수: {len(items1)}")
        if items1:
            first_title = items1[0].locator("div[class*='product_title__']").inner_text()
            first_price = items1[0].locator("span[class*='price_num__']").inner_text()
            first_ad = "광고" in items1[0].inner_text()
            print(f" -> [Test 1 1위 상품]: {first_title} | 가격: {first_price} | 광고여부: {first_ad}")

        # 가격비교 탭 버튼 찾기 및 정보 확인
        catalog_tab = page.locator("a:has-text('가격비교'), button:has-text('가격비교')")
        print(f" -> 가격비교 탭 개수: {catalog_tab.count()}")
        catalog_url = ""
        if catalog_tab.count() > 0:
            catalog_url = catalog_tab.first.get_attribute("href") or ""
            print(f" -> 가격비교 탭 href: {catalog_url}")

        # Test 2: 낮은 가격순(sort=price_asc) URL 테스트
        url2 = "https://search.shopping.naver.com/search/all?query=" + urllib.parse.quote("코카콜라 제로 355ml 24캔") + "&sort=price_asc"
        print(f"\n[Test 2] 낮은 가격순 URL 접속: {url2}")
        page.goto(url2, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        page.screenshot(path=f"{artifacts_dir}\\research_naver_sort_asc.png")

        items2 = page.locator("div[class*='product_item__']").all()
        if items2:
            first_title2 = items2[0].locator("div[class*='product_title__']").inner_text()
            first_price2 = items2[0].locator("span[class*='price_num__']").inner_text()
            first_ad2 = "광고" in items2[0].inner_text()
            print(f" -> [Test 2 1위 상품]: {first_title2} | 가격: {first_price2} | 광고여부: {first_ad2}")

        # Test 3: 가격비교 탭 클릭 후 화면
        if catalog_tab.count() > 0:
            print("\n[Test 3] 가격비교 탭 클릭")
            page.goto(url1, wait_until="networkidle")
            page.wait_for_timeout(1000)
            page.locator("a:has-text('가격비교')").first.click()
            page.wait_for_timeout(2000)
            current_tab_url = page.url
            print(f" -> 가격비교 탭 클릭 후 최종 URL: {current_tab_url}")
            page.screenshot(path=f"{artifacts_dir}\\research_naver_catalog_tab.png")

            items3 = page.locator("div[class*='product_item__']").all()
            if items3:
                first_title3 = items3[0].locator("div[class*='product_title__']").inner_text()
                first_price3 = items3[0].locator("span[class*='price_num__']").inner_text()
                print(f" -> [Test 3 1위 상품]: {first_title3} | 가격: {first_price3}")

        browser.close()

if __name__ == "__main__":
    test_naver_urls()
