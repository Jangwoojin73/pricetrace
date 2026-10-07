import os
import sys
import json
import urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
query_url = "http://127.0.0.1:8080/?q=" + urllib.parse.quote("농심 신라면 봉지 20개입")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # 1. 모바일 환경 (iPhone 15 Pro)
    m_ctx = browser.new_context(
        viewport={'width': 393, 'height': 852},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        is_mobile=True,
        has_touch=True
    )
    m_page = m_ctx.new_page()
    m_page.goto(query_url, wait_until="networkidle")
    m_page.wait_for_timeout(3000)

    # 모바일에서 1위 구매 링크 URL 확인
    m_buy_btn_href = m_page.evaluate('document.querySelector("#buyButton").href')
    m_rank1_href = m_page.evaluate('document.querySelectorAll(".rank-card a")[0].href')

    print(f"[Mobile App] buyButton href: {m_buy_btn_href}")
    print(f"[Mobile App] rank1 href: {m_rank1_href}")

    # 새 탭으로 해당 링크 열기
    m_naver_page = m_ctx.new_page()
    m_naver_page.goto(m_buy_btn_href, wait_until="networkidle")
    m_naver_page.wait_for_timeout(2000)

    m_scroll_y = m_naver_page.evaluate('window.scrollY')
    m_lis_count = m_naver_page.evaluate('document.querySelectorAll("#shp_lis_root").length')
    m_lis_rect = m_naver_page.evaluate('''() => {
        const el = document.querySelector("#shp_lis_root");
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { top: r.top, bottom: r.bottom, height: r.height };
    }''')
    
    mobile_shot = os.path.join(ARTIFACT_DIR, "verify_mobile_final_price_compare.png")
    m_naver_page.screenshot(path=mobile_shot)
    m_ctx.close()

    # 2. PC 데스크톱 환경 (1440x900)
    d_ctx = browser.new_context(
        viewport={'width': 1440, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    )
    d_page = d_ctx.new_page()
    d_page.goto(query_url, wait_until="networkidle")
    d_page.wait_for_timeout(3000)

    d_buy_btn_href = d_page.evaluate('document.querySelector("#buyButton").href')
    d_rank1_href = d_page.evaluate('document.querySelectorAll(".rank-card a")[0].href')

    print(f"[Desktop App] buyButton href: {d_buy_btn_href}")
    print(f"[Desktop App] rank1 href: {d_rank1_href}")

    d_naver_page = d_ctx.new_page()
    d_naver_page.goto(d_buy_btn_href, wait_until="networkidle")
    d_naver_page.wait_for_timeout(2000)

    d_scroll_y = d_naver_page.evaluate('window.scrollY')
    d_dui_count = d_naver_page.evaluate('document.querySelectorAll("#shp_dui_root").length')
    d_dui_rect = d_naver_page.evaluate('''() => {
        const el = document.querySelector("#shp_dui_root");
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { top: r.top, bottom: r.bottom, height: r.height };
    }''')

    desktop_shot = os.path.join(ARTIFACT_DIR, "verify_desktop_final_price_compare.png")
    d_naver_page.screenshot(path=desktop_shot)
    d_ctx.close()

    browser.close()

result = {
    "mobile": {
        "href": m_buy_btn_href,
        "scrollY": m_scroll_y,
        "lis_count": m_lis_count,
        "lis_rect": m_lis_rect,
        "screenshot": mobile_shot
    },
    "desktop": {
        "href": d_buy_btn_href,
        "scrollY": d_scroll_y,
        "dui_count": d_dui_count,
        "dui_rect": d_dui_rect,
        "screenshot": desktop_shot
    }
}

print("CROSS_DEVICE_VERIFY_SUCCESS")
print(json.dumps(result, ensure_ascii=False, indent=2))
with open(os.path.join(ARTIFACT_DIR, "verify_cross_device_links_result.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
