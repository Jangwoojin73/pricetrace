import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    page.goto('http://127.0.0.1:8080', wait_until='networkidle')
    page.wait_for_timeout(500)
    
    for kw in ["농심 신라면 봉지 20개입", "사과", "오뚜기밥 24개"]:
        page.fill('#searchInput', kw)
        page.keyboard.press('Enter')
        page.wait_for_timeout(2000)
        
        info = page.evaluate('''() => {
            const img = document.getElementById('productMainImage');
            const title = document.getElementById('productTitle');
            const price = document.getElementById('lowestPriceDisplay');
            return {
                title: title ? title.innerText.trim() : null,
                price: price ? price.innerText.trim() : null,
                src: img ? img.src : null,
                complete: img ? img.complete : false,
                naturalWidth: img ? img.naturalWidth : 0,
                naturalHeight: img ? img.naturalHeight : 0
            };
        }''')
        print(f"[{kw}] Title: {info['title']}, Price: {info['price']}, NaturalWidth: {info['naturalWidth']}px, Complete: {info['complete']}")
        print(f"  Src: {info['src'][:70]}...")
        
    browser.close()
