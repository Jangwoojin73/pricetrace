import os
import sys
import json
import urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
test_url = "https://search.naver.com/search.naver?where=shp&query=%EB%86%8D%EC%8B%AC%20%EC%8B%A0%EB%9D%BC%EB%A9%B4%20120g%2020%EA%B0%9C#shp_dui_root"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # 1. PC 데스크톱 테스트
    d_ctx = browser.new_context(
        viewport={'width': 1440, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    )
    d_page = d_ctx.new_page()
    d_page.goto(test_url, wait_until='networkidle')
    d_page.wait_for_timeout(1500)
    d_final_url = d_page.url
    d_scroll_y = d_page.evaluate('window.scrollY')
    d_dui_count = d_page.evaluate('document.querySelectorAll("#shp_dui_root").length')
    d_rect = d_page.evaluate('''() => {
        const el = document.querySelector("#shp_dui_root");
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { top: r.top, bottom: r.bottom, height: r.height };
    }''')
    desktop_png = os.path.join(ARTIFACT_DIR, "empirical_pc_desktop_result.png")
    d_page.screenshot(path=desktop_png)
    d_ctx.close()

    # 2. 모바일 (아이폰 15 Pro) 기존 URL 접속 테스트
    m_ctx = browser.new_context(
        viewport={'width': 393, 'height': 852},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        is_mobile=True,
        has_touch=True
    )
    m_page = m_ctx.new_page()
    m_page.goto(test_url, wait_until='networkidle')
    m_page.wait_for_timeout(1500)
    m_final_url = m_page.url
    m_scroll_y = m_page.evaluate('window.scrollY')
    m_dui_count = m_page.evaluate('document.querySelectorAll("#shp_dui_root").length')
    
    # 모바일 DOM에서 무엇이 있는지 확인
    m_powerlink_count = m_page.evaluate('document.querySelectorAll(".ad_section, .ad_area, [class*=\'powerlink\'], [class*=\'ad_\']").length')
    m_shopping_containers = m_page.evaluate('''() => {
        return Array.from(document.querySelectorAll("[id*='shp'], [class*='shp'], [id*='shop'], [class*='shop']"))
            .map(el => ({ id: el.id, className: el.className.toString(), tagName: el.tagName, top: el.getBoundingClientRect().top }))
            .slice(0, 10);
    }''')
    
    # 상단 300px 이내에 보이는 텍스트
    m_visible_top_text = m_page.evaluate('''() => {
        const textElements = Array.from(document.querySelectorAll('body *'))
            .filter(el => {
                const r = el.getBoundingClientRect();
                return r.top >= 0 && r.bottom <= 400 && el.innerText && el.children.length === 0;
            })
            .map(el => el.innerText.trim())
            .filter(t => t.length > 0);
        return textElements.slice(0, 15);
    }''')

    mobile_png = os.path.join(ARTIFACT_DIR, "empirical_mobile_current_url_result.png")
    m_page.screenshot(path=mobile_png)

    # 3. 모바일에서 쇼핑 전용 URL이나 적절한 앵커 탐색
    # 후보 1: msearch.shopping.naver.com/search/all?query=농심 신라면 120g 20개
    cand1_url = "https://msearch.shopping.naver.com/search/all?query=%EB%86%8D%EC%8B%AC%20%EC%8B%A0%EB%9D%BC%EB%A9%B4%20120g%2020%EA%B0%9C"
    m_page.goto(cand1_url, wait_until='networkidle')
    m_page.wait_for_timeout(1500)
    cand1_final_url = m_page.url
    cand1_png = os.path.join(ARTIFACT_DIR, "empirical_mobile_msearch_shopping_result.png")
    m_page.screenshot(path=cand1_png)
    cand1_top_text = m_page.evaluate('''() => {
        return Array.from(document.querySelectorAll('body *'))
            .filter(el => {
                const r = el.getBoundingClientRect();
                return r.top >= 0 && r.bottom <= 400 && el.innerText && el.children.length === 0;
            })
            .map(el => el.innerText.trim())
            .filter(t => t.length > 0)
            .slice(0, 15);
    }''')

    # 후보 2: m.search.naver.com/search.naver?where=m_view 또는 where=m&query=...#shp_lis_root
    cand2_url = "https://m.search.naver.com/search.naver?where=m&query=%EB%86%8D%EC%8B%AC%20%EC%8B%A0%EB%9D%BC%EB%A9%B4%20120g%2020%EA%B0%9C#shp_lis_root"
    m_page.goto(cand2_url, wait_until='networkidle')
    m_page.wait_for_timeout(1500)
    cand2_scroll_y = m_page.evaluate('window.scrollY')
    cand2_rect = m_page.evaluate('''() => {
        const el = document.querySelector("#shp_lis_root");
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { top: r.top, bottom: r.bottom, height: r.height };
    }''')
    cand2_png = os.path.join(ARTIFACT_DIR, "empirical_mobile_shp_lis_root_result.png")
    m_page.screenshot(path=cand2_png)

    m_ctx.close()
    browser.close()

result = {
    "desktop": {
        "final_url": d_final_url,
        "scrollY": d_scroll_y,
        "dui_count": d_dui_count,
        "rect": d_rect,
        "screenshot": desktop_png
    },
    "mobile_current": {
        "final_url": m_final_url,
        "scrollY": m_scroll_y,
        "dui_count": m_dui_count,
        "visible_top_text": m_visible_top_text,
        "screenshot": mobile_png
    },
    "candidate1_msearch_shopping": {
        "final_url": cand1_final_url,
        "visible_top_text": cand1_top_text,
        "screenshot": cand1_png
    },
    "candidate2_m_search_shp_lis": {
        "scrollY": cand2_scroll_y,
        "rect": cand2_rect,
        "screenshot": cand2_png
    }
}

output_path = os.path.join(ARTIFACT_DIR, "empirical_device_comparison_result.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("EMPIRICAL_AUDIT_SUCCESS")
print(json.dumps(result, ensure_ascii=False, indent=2))
