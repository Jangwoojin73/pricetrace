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

def verify_ui():
    os.makedirs("public/qa_artifacts", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 1080})
        page = context.new_page()

        # 1. 크리넥스 3겹 데코소프트 30롤 검증
        print("[TEST 1] Visiting localhost:8080 and searching '크리넥스 3겹 데코소프트 30롤'...")
        page.goto("http://localhost:8080")
        page.fill("#searchInput", "크리넥스 3겹 데코소프트 30롤")
        page.press("#searchInput", "Enter")
        
        # Wait for result view and title
        page.wait_for_selector("#resultView:not(.hidden)", timeout=10000)
        page.wait_for_function("() => document.getElementById('productTitle').innerText.includes('크리넥스')", timeout=10000)
        time.sleep(1.5)

        # Check main image
        img_src = page.locator("#productMainImage").get_attribute("src")
        print(f"Product Main Image: {img_src}")

        # Check rank cards count
        cards = page.locator("#priceComparisonGrid > div")
        card_count = cards.count()
        print(f"Rank Cards Count: {card_count}")

        # Screenshot
        screenshot_path = "public/qa_artifacts/verify_kleenex_3ranks.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Saved screenshot to {screenshot_path}")

        assert "660/069/071/b9cc000c5f614c179ed35a4eb82995be.jpg" in img_src or "danuri" in img_src, f"Image mismatch: {img_src}"
        assert card_count == 3, f"Expected 3 rank cards, got {card_count}"

        # 2. 퍼실 세제 검증
        print("\n[TEST 2] Searching '퍼실 딥클린 파워젤 2.7L'...")
        page.fill("#searchInput", "퍼실 딥클린 파워젤 2.7L")
        page.press("#searchInput", "Enter")
        page.wait_for_function("() => document.getElementById('productTitle').innerText.includes('퍼실')", timeout=10000)
        time.sleep(1.5)
        persil_img = page.locator("#productMainImage").get_attribute("src")
        persil_cards = page.locator("#priceComparisonGrid > div").count()
        print(f"Persil Main Image: {persil_img}")
        print(f"Persil Cards Count: {persil_cards}")
        page.screenshot(path="public/qa_artifacts/verify_persil_3ranks.png", full_page=True)
        assert "729/381/007/ed3368ec3d3a430f880b272bbea12da9.jpg" in persil_img or "danuri" in persil_img, f"Persil image mismatch: {persil_img}"
        assert persil_cards == 3, f"Expected 3 cards for Persil, got {persil_cards}"

        # 3. 신라면 검증
        print("\n[TEST 3] Searching '농심 신라면 120g 20개'...")
        page.fill("#searchInput", "농심 신라면 120g 20개")
        page.press("#searchInput", "Enter")
        page.wait_for_function("() => document.getElementById('productTitle').innerText.includes('신라면')", timeout=10000)
        time.sleep(1.5)
        shin_img = page.locator("#productMainImage").get_attribute("src")
        shin_cards = page.locator("#priceComparisonGrid > div").count()
        print(f"Shin Main Image: {shin_img}")
        print(f"Shin Cards Count: {shin_cards}")
        page.screenshot(path="public/qa_artifacts/verify_shin_3ranks.png", full_page=True)
        assert shin_cards == 3, f"Expected 3 cards for Shin, got {shin_cards}"

        browser.close()
        print("\n>>> ALL PLAYWRIGHT UI VERIFICATIONS PASSED 100%! <<<")

if __name__ == "__main__":
    verify_ui()
