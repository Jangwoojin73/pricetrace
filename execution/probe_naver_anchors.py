import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pc_url = "https://search.naver.com/search.naver?where=shp&query=농심%20신라면%20120g%2020개#shp_dui_root"
mobile_url = "https://m.search.naver.com/search.naver?where=m&query=농심%20신라면%20120g%2020개#shp_lis_root"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
    
    # PC
    d_page = browser.new_page(viewport={'width': 1440, 'height': 900})
    try:
        d_page.goto(pc_url, wait_until="domcontentloaded", timeout=15000)
        d_page.wait_for_timeout(2000)
        pc_metrics = d_page.evaluate('''() => {
            const el = document.getElementById("shp_dui_root") || document.getElementById("shp_gui_root");
            const rect = el ? el.getBoundingClientRect() : null;
            const ads = Array.from(document.querySelectorAll('.ad_section, .powerlink, [data-ad]')).filter(a => {
                const r = a.getBoundingClientRect();
                return r.bottom > 0 && r.top < window.innerHeight;
            });
            return {
                scrollY: window.scrollY,
                hasAnchorEl: !!el,
                anchorId: el ? el.id : null,
                rectTop: rect ? Math.round(rect.top) : null,
                adsInViewport: ads.length,
                bodyTextSample: document.body.innerText.slice(0, 150).replace(/\\s+/g, ' ')
            };
        }''')
        print("PC Result:", pc_metrics)
    except Exception as e:
        print("PC Error:", e)
        
    # Mobile
    m_ctx = browser.new_context(
        viewport={'width': 393, 'height': 852},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        is_mobile=True,
        has_touch=True
    )
    m_page = m_ctx.new_page()
    try:
        m_page.goto(mobile_url, wait_until="domcontentloaded", timeout=15000)
        m_page.wait_for_timeout(2000)
        m_metrics = m_page.evaluate('''() => {
            const el = document.getElementById("shp_lis_root");
            const rect = el ? el.getBoundingClientRect() : null;
            const ads = Array.from(document.querySelectorAll('.ad_section, .powerlink, [data-ad]')).filter(a => {
                const r = a.getBoundingClientRect();
                return r.bottom > 0 && r.top < window.innerHeight;
            });
            return {
                scrollY: window.scrollY,
                hasAnchorEl: !!el,
                anchorId: el ? el.id : null,
                rectTop: rect ? Math.round(rect.top) : null,
                adsInViewport: ads.length,
                bodyTextSample: document.body.innerText.slice(0, 150).replace(/\\s+/g, ' ')
            };
        }''')
        print("Mobile Result:", m_metrics)
    except Exception as e:
        print("Mobile Error:", e)
        
    browser.close()
