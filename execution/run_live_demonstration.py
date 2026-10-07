import os
import sys
import time
import json
import re
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def sanitize_name(text):
    return re.sub(r'[^a-zA-Z0-9가-힣]', '_', text)[:10]

def run_live_demonstration():
    print("=================================================================")
    print("🚀 [PriceTrace] 2대 탭 & 전 추천 품목 실시간 브라우저 조작 라이브 시연")
    print("=================================================================")

    demo_log = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "steady_items": [],
        "trending_items": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            locale="ko-KR"
        )
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")

        # -------------------------------------------------------------
        # [시연 1] 국민 필수 생필품 탭 조작 및 품목별 시연
        # -------------------------------------------------------------
        print("\n▶ [STEP 1] 메인화면 접속 및 '🏆 국민 필수 생필품' 탭 활성화")
        page.goto("http://127.0.0.1:8080/", wait_until="networkidle")
        page.wait_for_selector("#tabSteadyBtn", state="visible")
        page.click("#tabSteadyBtn")
        page.wait_for_timeout(600)

        steady_overview_shot = os.path.join(ARTIFACT_DIR, "demo_01_steady_tab_overview.png")
        page.screenshot(path=steady_overview_shot)
        print(f"  📸 생필품 탭 메인 화면 캡처: demo_01_steady_tab_overview.png")

        tested_steady_keywords = []

        for step in range(1, 5):
            page.wait_for_selector("#welcomeCardsContainer .welcome-card", state="visible")
            
            # 현재 화면에 렌더링된 카드 중 아직 테스트하지 않은 카드 선택
            card_info = page.evaluate("""(tested) => {
                const cards = Array.from(document.querySelectorAll('#welcomeCardsContainer .welcome-card'));
                for (let i = 0; i < cards.length; i++) {
                    const kw = cards[i].getAttribute('data-keyword') || '';
                    if (!tested.includes(kw)) {
                        return {
                            index: i,
                            keyword: kw,
                            title: cards[i].querySelector('h3')?.innerText.trim() || '',
                            tag: cards[i].querySelector('[class*="rounded-full"]')?.innerText.trim() || '',
                            price: cards[i].querySelector('.text-blue-600 span')?.innerText.trim() || ''
                        };
                    }
                }
                const first = cards[0];
                return {
                    index: 0,
                    keyword: first.getAttribute('data-keyword') || '',
                    title: first.querySelector('h3')?.innerText.trim() || '',
                    tag: first.querySelector('[class*="rounded-full"]')?.innerText.trim() || '',
                    price: first.querySelector('.text-blue-600 span')?.innerText.trim() || ''
                };
            }""", tested_steady_keywords)

            kw = card_info["keyword"]
            title = card_info["title"]
            tag = card_info["tag"]
            price = card_info["price"]
            card_idx = card_info["index"]
            tested_steady_keywords.append(kw)

            safe_kw = sanitize_name(kw)
            print(f"\n  -------------------------------------------------------------")
            print(f"  👉 [생필품 {step}번 품목 탭 조작]: [{tag}] '{title}' ({kw}) - {price}")
            print(f"  -------------------------------------------------------------")

            # 메인에서 해당 카드 클릭
            page.locator("#welcomeCardsContainer .welcome-card").nth(card_idx).click()
            page.wait_for_selector("#priceComparisonGrid .rank-card, #priceComparisonGrid .card-hover", state="visible", timeout=15000)
            page.wait_for_timeout(600)

            # 가격비교 그리드가 뷰포트 중앙에 오도록 스크롤 후 캡처
            page.evaluate("() => document.getElementById('priceComparisonGrid').scrollIntoView({ behavior: 'instant', block: 'center' })")
            page.wait_for_timeout(400)
            result_shot = os.path.join(ARTIFACT_DIR, f"demo_02_steady_{step}_{safe_kw}_result.png")
            page.screenshot(path=result_shot)
            print(f"    📸 PriceTrace 결과 화면 캡처: demo_02_steady_{step}_{safe_kw}_result.png")

            # 버튼 링크 및 1~3순위 카드 정보 추출
            buy_btn_href = page.evaluate("() => document.getElementById('buyButton')?.href || ''")
            rank_cards = page.evaluate("""() => {
                const cards = document.querySelectorAll('#priceComparisonGrid .rank-card, #priceComparisonGrid .card-hover');
                return Array.from(cards).map((c, i) => ({
                    rank: i + 1,
                    title: c.querySelector('h4')?.innerText.trim() || '',
                    price: c.querySelector('.text-2xl.font-black')?.innerText.trim() || '',
                    mall: c.querySelector('.truncate')?.innerText.trim() || '',
                    href: c.querySelector('a[href]')?.href || ''
                }));
            }""")

            print(f"    최저가 바로구매 링크: {buy_btn_href}")
            for rc in rank_cards:
                print(f"      {rc['rank']}위 카드: {rc['title']} | {rc['price']}원 ({rc['mall']})")
                print(f"            링크: {rc['href']}")

            # 실제 네이버 페이지 새 탭 오픈 시연
            naver_tab = ctx.new_page()
            print(f"    🔗 실제 브라우저로 네이버 쇼핑 열기: {buy_btn_href}")
            naver_tab.goto(buy_btn_href, wait_until="networkidle")
            naver_tab.wait_for_timeout(1200)

            n_data = naver_tab.evaluate("""() => {
                const root = document.getElementById('shp_dui_root');
                const heading = Array.from(document.querySelectorAll('h2, h3')).find(h => h.innerText.includes('가격비교'));
                const adSections = document.querySelectorAll('[class*="power_link"], [class*="ad_section"], .powerlink');
                let adVisible = false;
                for (const ad of adSections) {
                    const r = ad.getBoundingClientRect();
                    if (r.top >= 0 && r.top < window.innerHeight) { adVisible = true; break; }
                }
                return {
                    scrollY: window.scrollY,
                    hasDui: !!root,
                    headingFound: !!heading,
                    headingText: heading ? heading.innerText.trim() : 'none',
                    headingTop: heading ? Math.round(heading.getBoundingClientRect().top) : -9999,
                    adVisible
                };
            }""")

            naver_shot = os.path.join(ARTIFACT_DIR, f"demo_03_steady_{step}_{safe_kw}_naver.png")
            naver_tab.screenshot(path=naver_shot)
            print(f"    📸 네이버 가격비교 착지 캡처: demo_03_steady_{step}_{safe_kw}_naver.png")
            print(f"       실측: scrollY={n_data['scrollY']}px, 헤딩='{n_data['headingText']}' (top={n_data['headingTop']}px), 파워링크 광고={n_data['adVisible']}")

            naver_tab.close()

            # 홈으로 돌아가기 버튼 클릭하여 복귀
            page.click("#backToHomeBtn")
            page.wait_for_selector("#welcomeCardsContainer", state="visible")
            page.wait_for_timeout(400)

            demo_log["steady_items"].append({
                "step": step,
                "keyword": kw,
                "title": title,
                "buy_url": buy_btn_href,
                "scrollY": n_data["scrollY"],
                "heading": n_data["headingText"],
                "headingTop": n_data["headingTop"],
                "adVisible": n_data["adVisible"],
                "pass": (n_data["hasDui"] and n_data["headingFound"] and not n_data["adVisible"]),
                "rank_cards": rank_cards
            })

        # -------------------------------------------------------------
        # [시연 2] 오늘 실시간 핫딜 탭 조작 및 품목별 시연
        # -------------------------------------------------------------
        print("\n\n▶ [STEP 2] '🔥 오늘 실시간 핫딜' 탭으로 전환 조작")
        page.click("#tabTrendingBtn")
        page.wait_for_timeout(800)

        trending_overview_shot = os.path.join(ARTIFACT_DIR, "demo_04_trending_tab_overview.png")
        page.screenshot(path=trending_overview_shot)
        print(f"  📸 실시간 핫딜 탭 메인 화면 캡처: demo_04_trending_tab_overview.png")

        tested_trending_keywords = []

        for step in range(1, 5):
            page.wait_for_selector("#welcomeCardsContainer .welcome-card", state="visible")

            # 현재 핫딜 화면에 렌더링된 카드 중 아직 테스트하지 않은 카드 선택
            card_info = page.evaluate("""(tested) => {
                const cards = Array.from(document.querySelectorAll('#welcomeCardsContainer .welcome-card'));
                for (let i = 0; i < cards.length; i++) {
                    const kw = cards[i].getAttribute('data-keyword') || '';
                    if (!tested.includes(kw)) {
                        return {
                            index: i,
                            keyword: kw,
                            title: cards[i].querySelector('h3')?.innerText.trim() || '',
                            tag: cards[i].querySelector('[class*="rounded-full"]')?.innerText.trim() || '',
                            price: cards[i].querySelector('.text-blue-600 span')?.innerText.trim() || ''
                        };
                    }
                }
                const first = cards[0];
                return {
                    index: 0,
                    keyword: first.getAttribute('data-keyword') || '',
                    title: first.querySelector('h3')?.innerText.trim() || '',
                    tag: first.querySelector('[class*="rounded-full"]')?.innerText.trim() || '',
                    price: first.querySelector('.text-blue-600 span')?.innerText.trim() || ''
                };
            }""", tested_trending_keywords)

            kw = card_info["keyword"]
            title = card_info["title"]
            tag = card_info["tag"]
            price = card_info["price"]
            card_idx = card_info["index"]
            tested_trending_keywords.append(kw)

            safe_kw = sanitize_name(kw)
            print(f"\n  -------------------------------------------------------------")
            print(f"  👉 [실시간 핫딜 {step}번 품목 탭 조작]: [{tag}] '{title}' ({kw}) - {price}")
            print(f"  -------------------------------------------------------------")

            # 메인에서 해당 카드 클릭
            page.locator("#welcomeCardsContainer .welcome-card").nth(card_idx).click()
            page.wait_for_selector("#priceComparisonGrid .rank-card, #priceComparisonGrid .card-hover", state="visible", timeout=15000)
            page.wait_for_timeout(600)

            # 가격비교 그리드가 뷰포트 중앙에 오도록 스크롤 후 캡처
            page.evaluate("() => document.getElementById('priceComparisonGrid').scrollIntoView({ behavior: 'instant', block: 'center' })")
            page.wait_for_timeout(400)
            result_shot = os.path.join(ARTIFACT_DIR, f"demo_05_trending_{step}_{safe_kw}_result.png")
            page.screenshot(path=result_shot)
            print(f"    📸 PriceTrace 결과 화면 캡처: demo_05_trending_{step}_{safe_kw}_result.png")

            # 버튼 링크 및 1~3순위 카드 정보 추출
            buy_btn_href = page.evaluate("() => document.getElementById('buyButton')?.href || ''")
            rank_cards = page.evaluate("""() => {
                const cards = document.querySelectorAll('#priceComparisonGrid .rank-card, #priceComparisonGrid .card-hover');
                return Array.from(cards).map((c, i) => ({
                    rank: i + 1,
                    title: c.querySelector('h4')?.innerText.trim() || '',
                    price: c.querySelector('.text-2xl.font-black')?.innerText.trim() || '',
                    mall: c.querySelector('.truncate')?.innerText.trim() || '',
                    href: c.querySelector('a[href]')?.href || ''
                }));
            }""")

            print(f"    최저가 바로구매 링크: {buy_btn_href}")
            for rc in rank_cards:
                print(f"      {rc['rank']}위 카드: {rc['title']} | {rc['price']}원 ({rc['mall']})")
                print(f"            링크: {rc['href']}")

            # 실제 네이버 페이지 새 탭 오픈 시연
            naver_tab = ctx.new_page()
            print(f"    🔗 실제 브라우저로 네이버 쇼핑 열기: {buy_btn_href}")
            naver_tab.goto(buy_btn_href, wait_until="networkidle")
            naver_tab.wait_for_timeout(1200)

            n_data = naver_tab.evaluate("""() => {
                const root = document.getElementById('shp_dui_root');
                const heading = Array.from(document.querySelectorAll('h2, h3')).find(h => h.innerText.includes('가격비교'));
                const adSections = document.querySelectorAll('[class*="power_link"], [class*="ad_section"], .powerlink');
                let adVisible = false;
                for (const ad of adSections) {
                    const r = ad.getBoundingClientRect();
                    if (r.top >= 0 && r.top < window.innerHeight) { adVisible = true; break; }
                }
                return {
                    scrollY: window.scrollY,
                    hasDui: !!root,
                    headingFound: !!heading,
                    headingText: heading ? heading.innerText.trim() : 'none',
                    headingTop: heading ? Math.round(heading.getBoundingClientRect().top) : -9999,
                    adVisible
                };
            }""")

            naver_shot = os.path.join(ARTIFACT_DIR, f"demo_06_trending_{step}_{safe_kw}_naver.png")
            naver_tab.screenshot(path=naver_shot)
            print(f"    📸 네이버 가격비교 착지 캡처: demo_06_trending_{step}_{safe_kw}_naver.png")
            print(f"       실측: scrollY={n_data['scrollY']}px, 헤딩='{n_data['headingText']}' (top={n_data['headingTop']}px), 파워링크 광고={n_data['adVisible']}")

            naver_tab.close()

            # 홈으로 복귀
            page.click("#backToHomeBtn")
            page.wait_for_selector("#welcomeCardsContainer", state="visible")
            page.wait_for_timeout(400)

            # 핫딜 탭 유지 확인
            active_tab = page.evaluate("() => state.activeTab")
            if active_tab != "trending":
                page.click("#tabTrendingBtn")
                page.wait_for_timeout(400)

            demo_log["trending_items"].append({
                "step": step,
                "keyword": kw,
                "title": title,
                "buy_url": buy_btn_href,
                "scrollY": n_data["scrollY"],
                "heading": n_data["headingText"],
                "headingTop": n_data["headingTop"],
                "adVisible": n_data["adVisible"],
                "pass": (n_data["hasDui"] and n_data["headingFound"] and not n_data["adVisible"]),
                "rank_cards": rank_cards
            })

        browser.close()

    log_path = os.path.join(ARTIFACT_DIR, "live_demonstration_audit_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(demo_log, f, indent=2, ensure_ascii=False)
    print(f"\n=================================================================")
    print(f"✅ 전체 시연 완수! 총 {len(demo_log['steady_items']) + len(demo_log['trending_items'])}개 품목 실측 완료")
    print(f"📁 상세 로그 저장됨: {log_path}")
    print("=================================================================")
    return demo_log

if __name__ == "__main__":
    run_live_demonstration()
