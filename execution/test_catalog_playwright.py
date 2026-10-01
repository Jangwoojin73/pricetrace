# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

def test_catalog_and_sorted_search():
    artifacts_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
            locale="ko-KR"
        )
        page = context.new_page()

        # Test 1: 공식 카탈로그 직결 URL
        catalog_url = "https://search.shopping.naver.com/catalog/39564882619"
        print(f"[Test 1] 카탈로그 직결 URL 접속: {catalog_url}")
        try:
            page.goto(catalog_url, wait_until="load", timeout=15000)
            page.wait_for_timeout(2000)
            page.screenshot(path=f"{artifacts_dir}\\proof_direct_catalog_coca.png")
            print(f" -> 카탈로그 스크린샷 저장 완료: proof_direct_catalog_coca.png (URL: {page.url})")
        except Exception as e:
            print(" -> 카탈로그 로드 예외:", e)

        # Test 2: 스마트스토어/낮은가격순 URL
        sorted_url = "https://search.shopping.naver.com/search/all?query=%EC%BD%94%EC%B9%B4%EC%BD%9C%EB%9D%BC%20%EC%A0%9C%EB%A1%9C%20355ml%2024%EC%BA%94&sort=price_asc&frm=NVSCPRO"
        print(f"\n[Test 2] 낮은 가격순 URL 접속: {sorted_url}")
        try:
            page.goto(sorted_url, wait_until="load", timeout=15000)
            page.wait_for_timeout(2000)
            page.screenshot(path=f"{artifacts_dir}\\proof_sorted_search_coca.png")
            print(f" -> 정렬 검색 스크린샷 저장 완료: proof_sorted_search_coca.png (URL: {page.url})")
        except Exception as e:
            print(" -> 정렬 검색 로드 예외:", e)

        browser.close()

if __name__ == "__main__":
    test_catalog_and_sorted_search()
