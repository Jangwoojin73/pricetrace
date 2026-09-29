#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    url = "https://search.shopping.naver.com/search/all?query=%EC%98%A4%EB%9A%9C%EA%B8%B0%20%EC%A7%84%EB%9D%BC%EB%A9%B4%2040%EA%B0%9C&sort=price_asc&minPrice=20000&maxPrice=23000"
    page.goto(url, wait_until="networkidle", timeout=15000)
    print("Page Title:", page.title())
    
    # 상품명 및 가격 텍스트 수집
    items = page.locator("div[class*='product_item']").all()
    print("Items found:", len(items))
    if not items:
        # 다른 셀렉터 시도
        items = page.locator("div[class*='adProduct_item'], div[class*='basicList_item']").all()
    
    texts = page.locator("span[class*='price_num'], em[class*='price_num']").all_text_contents()
    print("Top prices on page:", texts[:5])
    browser.close()
