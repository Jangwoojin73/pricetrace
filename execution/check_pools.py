import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    page.goto('http://127.0.0.1:8080', wait_until='networkidle')
    page.wait_for_timeout(1000)
    
    res = page.evaluate('''() => {
        return {
            hasSteady: typeof STEADY_PRODUCTS_POOL !== 'undefined',
            steadyLen: typeof STEADY_PRODUCTS_POOL !== 'undefined' ? STEADY_PRODUCTS_POOL.length : null,
            hasTrending: typeof TRENDING_PRODUCTS_POOL !== 'undefined',
            trendingLen: typeof TRENDING_PRODUCTS_POOL !== 'undefined' ? TRENDING_PRODUCTS_POOL.length : null,
            sampleSteady: typeof STEADY_PRODUCTS_POOL !== 'undefined' ? STEADY_PRODUCTS_POOL.slice(0, 3) : [],
            sampleTrending: typeof TRENDING_PRODUCTS_POOL !== 'undefined' ? TRENDING_PRODUCTS_POOL.slice(0, 3) : [],
            dateText: document.getElementById('dailyTrendingDateText') ? document.getElementById('dailyTrendingDateText').innerText : null
        };
    }''')
    print('Pool Check Result:')
    print(f"  Steady items length: {res['steadyLen']}")
    print(f"  Trending items length: {res['trendingLen']}")
    print(f"  Header Date text: '{res['dateText']}'")
    print(f"  Sample steady item: {res['sampleSteady'][0] if res['sampleSteady'] else None}")
    browser.close()
