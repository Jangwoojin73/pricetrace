import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8080"
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "test_artifacts")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_multi_search_verification():
    print("=" * 70)
    print(">> [Multi-product Realtime Search & Screen Rendering E2E Test]")
    print("=" * 70)

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Step 1: 최초 접속 (신라면 기본 화면)
        print("\n[Test 1] WebApp Initial Load (Shinramyun)...")
        page.goto(BASE_URL)
        page.wait_for_selector("#lowestPriceDisplay:not(.skeleton)", timeout=15000)
        
        title_initial = page.locator("#productTitle").inner_text()
        price_initial = page.locator("#lowestPriceDisplay").inner_text()
        img_initial = page.locator("#productMainImage").get_attribute("src")
        buy_link_initial = page.locator("#buyButton").get_attribute("href")

        step1_pass = "신라면" in title_initial and bool(img_initial) and bool(buy_link_initial)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "verify_01_shinramyun.png"), full_page=True)
        results.append(("1. Initial Load (Shinramyun)", step1_pass, f"Title: {title_initial[:25]}..., Price: {price_initial} KRW"))

        # Step 2: 퀵 칩 클릭 ('#햇반 24개')
        print("\n[Test 2] Quick Chip Click ('Hetban 24ea') -> Transition to Hetban...")
        page.click("button.quick-chip[data-keyword='CJ제일제당 햇반 210g 24개']")
        
        # 햇반 텍스트가 DOM에 렌더링될 때까지 대기
        page.wait_for_function("() => document.getElementById('productTitle').textContent.includes('햇반')", timeout=15000)
        page.wait_for_selector("#lowestPriceDisplay:not(.skeleton)", timeout=15000)

        title_hetban = page.locator("#productTitle").inner_text()
        price_hetban = page.locator("#lowestPriceDisplay").inner_text()
        img_hetban = page.locator("#productMainImage").get_attribute("src")
        buy_link_hetban = page.locator("#buyButton").get_attribute("href")
        unit_label_hetban = page.locator("#unitPriceLabel").inner_text()

        step2_pass = (
            "햇반" in title_hetban and
            title_hetban != title_initial and
            img_hetban != img_initial and
            "햇반" not in img_initial and
            bool(buy_link_hetban)
        )
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "verify_02_hetban.png"), full_page=True)
        results.append(("2. Quick Chip Click (Hetban)", step2_pass, f"Title: {title_hetban[:25]}..., Price: {price_hetban} KRW, Unit: {unit_label_hetban}"))

        # Step 3: 검색창 직접 입력 ('코카콜라 제로 355ml 24캔')
        print("\n[Test 3] Search Bar Input ('Coca-cola Zero') -> Transition to Coca-cola...")
        page.fill("#searchInput", "코카콜라 제로 355ml 24캔")
        page.click("#searchForm button[type='submit']")

        page.wait_for_function("() => document.getElementById('productTitle').textContent.includes('코카') || document.getElementById('productTitle').textContent.includes('칠성')", timeout=15000)
        page.wait_for_selector("#lowestPriceDisplay:not(.skeleton)", timeout=15000)

        title_coke = page.locator("#productTitle").inner_text()
        price_coke = page.locator("#lowestPriceDisplay").inner_text()
        img_coke = page.locator("#productMainImage").get_attribute("src")
        buy_link_coke = page.locator("#buyButton").get_attribute("href")

        step3_pass = (
            ("코카" in title_coke or "칠성" in title_coke) and
            title_coke != title_hetban and
            bool(img_coke) and
            bool(buy_link_coke)
        )
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "verify_03_coke.png"), full_page=True)
        results.append(("3. Search Bar Input (Coca-cola)", step3_pass, f"Title: {title_coke[:25]}..., Price: {price_coke} KRW"))

        # Step 4: 검색창 직접 입력 ('제주 삼다수 2L 6개')
        print("\n[Test 4] Search Bar Input ('Jeju Samdasoo') -> Transition to Samdasoo...")
        page.fill("#searchInput", "제주 삼다수 2L 6개")
        page.click("#searchForm button[type='submit']")

        page.wait_for_function("() => document.getElementById('productTitle').textContent.includes('삼다수')", timeout=15000)
        page.wait_for_selector("#lowestPriceDisplay:not(.skeleton)", timeout=15000)

        title_water = page.locator("#productTitle").inner_text()
        price_water = page.locator("#lowestPriceDisplay").inner_text()
        img_water = page.locator("#productMainImage").get_attribute("src")
        buy_link_water = page.locator("#buyButton").get_attribute("href")

        step4_pass = (
            "삼다수" in title_water and
            title_water != title_coke and
            bool(img_water) and
            bool(buy_link_water)
        )
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "verify_04_samdasoo.png"), full_page=True)
        results.append(("4. Search Bar Input (Samdasoo)", step4_pass, f"Title: {title_water[:25]}..., Price: {price_water} KRW"))

        # Step 5: 최저가 구매 링크 클릭 검증 (아웃링크 유효성)
        print("\n[Test 5] Checking Product Outlinks...")
        card_links = page.locator("#priceComparisonGrid a").all()
        step5_pass = len(card_links) >= 1 and all(
            "naver.com" in (link.get_attribute("href") or "") for link in card_links
        )
        results.append(("5. Shopping Mall Outlinks", step5_pass, f"Valid links count: {len(card_links)}"))

        browser.close()

    print("\n" + "=" * 70)
    print(">> [Multi-product E2E Final Results]")
    print("=" * 70)
    all_ok = True
    for name, passed, detail in results:
        status = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_ok = False
        print(f"{status} {name}")
        print(f"       -- {detail}")
    print("=" * 70)
    if all_ok:
        print("[SUCCESS] All product searches, images, and links passed 100%!")
    else:
        print("[FAIL] Some tests failed.")
    print("=" * 70)

if __name__ == "__main__":
    run_multi_search_verification()
