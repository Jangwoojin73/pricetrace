import os
import sys
import io
import time
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

def test_jinramyun_click():
    os.makedirs("public/qa_artifacts", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1080})

        print("[STEP 1] Navigating to http://localhost:8080...")
        page.goto("http://localhost:8080")
        time.sleep(1)

        # 1. 진라면 40개 검색
        print("[STEP 2] Searching '오뚜기 진라면 매운맛 40개'...")
        page.fill("#searchInput", "오뚜기 진라면 매운맛 40개")
        page.press("#searchInput", "Enter")

        page.wait_for_selector("#resultView:not(.hidden)", timeout=10000)
        page.wait_for_function("() => document.getElementById('productTitle').innerText.includes('진라면')", timeout=10000)
        time.sleep(1.5)

        title = page.locator("#productTitle").inner_text()
        img = page.locator("#productMainImage").get_attribute("src")
        cards = page.locator("#priceComparisonGrid > div")
        card_cnt = cards.count()

        print(f"Title: {title}")
        print(f"Image: {img}")
        print(f"Cards count: {card_cnt}")

        assert "진라면" in title, f"Title does not contain 진라면: {title}"
        assert "오뚜기밥" not in title, f"Title incorrectly contains 오뚜기밥: {title}"
        assert card_cnt == 3, f"Expected 3 cards, got {card_cnt}"

        # Capture screenshot
        screenshot_path = "public/qa_artifacts/verify_jinramyun_fix.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Saved screenshot to {screenshot_path}")

        # 2. 오뚜기밥 24개 검색하여 상호 간섭 없는지 교차 검증
        print("\n[STEP 3] Searching '오뚜기 맛있는 오뚜기밥 210g 24개' for cross-verification...")
        page.fill("#searchInput", "오뚜기 맛있는 오뚜기밥 210g 24개")
        page.press("#searchInput", "Enter")

        page.wait_for_function("() => document.getElementById('productTitle').innerText.includes('오뚜기밥')", timeout=10000)
        time.sleep(1.5)

        rice_title = page.locator("#productTitle").inner_text()
        rice_img = page.locator("#productMainImage").get_attribute("src")
        rice_cards = page.locator("#priceComparisonGrid > div").count()

        print(f"Rice Title: {rice_title}")
        print(f"Rice Image: {rice_img}")
        print(f"Rice Cards count: {rice_cards}")

        assert "오뚜기밥" in rice_title, f"Rice title does not contain 오뚜기밥: {rice_title}"
        assert "진라면" not in rice_title, f"Rice title incorrectly contains 진라면: {rice_title}"
        assert rice_cards == 3, f"Expected 3 cards, got {rice_cards}"

        page.screenshot(path="public/qa_artifacts/verify_ottogirice_fix.png", full_page=True)
        print("Saved screenshot to public/qa_artifacts/verify_ottogirice_fix.png")

        browser.close()
        print("\n>>> JINRAMYUN & OTTOGIRICE INDEPENDENT MATCHING VERIFIED 100%! <<<")

if __name__ == "__main__":
    test_jinramyun_click()
