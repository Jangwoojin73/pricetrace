import os
import sys
import time
import json
import urllib.request
import urllib.parse
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

STEADY_KEYWORDS = [
    ("농심 신라면 봉지 20개입", "신라면 20개"),
    ("CJ제일제당 햇반 210g 24개", "햇반 24개"),
    ("코카콜라 제로 355ml 24캔", "코카콜라 제로 24캔"),
    ("제주 삼다수 2L 6개", "삼다수 2L 6개"),
    ("오뚜기 진라면 매운맛 40개", "진라면 40개"),
    ("맥심 모카골드 마일드 160T", "맥심 160T"),
    ("크리넥스 3겹 데코소프트 30롤", "크리넥스 30롤"),
    ("퍼실 파워젤 액체세제 2.7L", "퍼실 세제 2.7L"),
    ("동원참치 100g 10캔", "동원참치 10캔"),
    ("베베숲 시그니처 물티슈 70매 10팩", "베베숲 물티슈 10팩"),
    ("오뚜기 맛있는 오뚜기밥 210g 24개", "오뚜기밥 24개"),
    ("농심 안성탕면 20개", "안성탕면 20개"),
    ("칠성사이다 제로 355ml 24캔", "칠성사이다 제로 24캔"),
    ("다우니 섬유유연제 블루 1L 3개", "다우니 3개"),
    ("페브리즈 섬유탈취제 상쾌한향 리필 4개", "페브리즈 리필 4개"),
    ("스팸 클래식 200g 10개", "스팸 10캔")
]

def get_trending_keywords():
    try:
        url = "http://127.0.0.1:8080/api/trending"
        req = urllib.request.urlopen(url, timeout=5)
        data = json.loads(req.read().decode("utf-8"))
        trending = data.get("trending_items", [])
        return [(t.get("keyword") or t.get("name"), t.get("name") or t.get("title")) for t in trending]
    except Exception as e:
        print(f"Error fetching trending: {e}")
        return []

def audit_32_items():
    print("=================================================================")
    print("🔍 [PriceTrace] 32개 전 품목(생필품 16 + 핫딜 16) 네이버 가격비교 전수 실측 감사")
    print("=================================================================")

    trending_list = get_trending_keywords()
    print(f"생필품 풀: {len(STEADY_KEYWORDS)}개, 핫딜 풀: {len(trending_list)}개 -> 총 {len(STEADY_KEYWORDS) + len(trending_list)}개 품목")

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "steady_results": [],
        "trending_results": [],
        "summary": {
            "total": 0,
            "pass_count": 0,
            "fail_count": 0,
            "pass_rate_percent": 0.0
        }
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            locale="ko-KR"
        )
        page = ctx.new_page()

        # 1. 생필품 16개 검사
        print("\n\n▶ [PART 1] 🏆 국민 필수 생필품 16대 품목 전수 검증")
        for i, (kw, name) in enumerate(STEADY_KEYWORDS, 1):
            print(f"\n[{i}/16] 생필품: {name} ({kw})")
            
            api_url = f"http://127.0.0.1:8080/api/search?q={urllib.parse.quote(kw)}"
            try:
                res = urllib.request.urlopen(api_url, timeout=8)
                data = json.loads(res.read().decode("utf-8"))
            except Exception as e:
                print(f"  ❌ API 에러: {e}")
                results["steady_results"].append({"index": i, "name": name, "keyword": kw, "status": "API_FAIL", "error": str(e), "pass": False})
                continue

            item = data.get("representative_item") or (data.get("top_items", [{}])[0] if data.get("top_items") else {})
            card_price = item.get("price", 0)
            card_mall = item.get("mallName") or item.get("mall") or item.get("mall_name") or ""
            target_url = item.get("url") or item.get("mallUrl") or item.get("link") or ""

            print(f"  - PriceTrace 카드: {card_price:,}원 ({card_mall})")
            print(f"  - 직결 링크: {target_url}")

            if not target_url:
                print(f"  ❌ 링크 부재 오류")
                results["steady_results"].append({"index": i, "name": name, "keyword": kw, "pass": False, "error": "EMPTY_URL"})
                continue

            # 네이버 실제 접속 검증
            try:
                page.goto(target_url, wait_until="networkidle", timeout=15000)
                page.wait_for_timeout(800)
                
                check = page.evaluate("""() => {
                    const dui = document.getElementById('shp_dui_root');
                    const headings = Array.from(document.querySelectorAll('h2, h3'));
                    const priceCompareHeading = headings.find(h => h.innerText.includes('가격비교'));
                    
                    // 최상단 가격비교 영역 내 1위 품목 가격 및 상품명 추출
                    let topPrice = null;
                    let topTitle = '';
                    if (dui) {
                        const priceEl = dui.querySelector('.price_num, [class*=\"price_num\"], [class*=\"price\"] strong, .value');
                        if (priceEl) {
                            topPrice = parseInt(priceEl.innerText.replace(/[^0-9]/g, '')) || null;
                        }
                        const titleEl = dui.querySelector('a[class*=\"title\"], [class*=\"tit\"] a, h3 a');
                        if (titleEl) {
                            topTitle = titleEl.innerText.trim();
                        }
                    }
                    
                    // 뷰포트 내 파워링크 광고 가시성
                    const adSections = document.querySelectorAll('[class*=\"power_link\"], [class*=\"ad_section\"], .powerlink');
                    let adVisible = false;
                    for (const ad of adSections) {
                        const r = ad.getBoundingClientRect();
                        if (r.top >= 0 && r.top < window.innerHeight) { adVisible = true; break; }
                    }

                    return {
                        scrollY: window.scrollY,
                        hasDui: !!dui,
                        hasHeading: !!priceCompareHeading,
                        headingText: priceCompareHeading ? priceCompareHeading.innerText.trim() : 'none',
                        headingTop: priceCompareHeading ? Math.round(priceCompareHeading.getBoundingClientRect().top) : -9999,
                        topPrice: topPrice,
                        topTitle: topTitle,
                        adVisible: adVisible
                    };
                }""")

                is_pass = check["hasDui"] and check["hasHeading"] and not check["adVisible"]
                status_str = "PASS ✅" if is_pass else "FAIL ❌"
                print(f"  - 결과: {status_str} (scrollY={check['scrollY']}px, 헤딩={check['headingText']}, top={check['headingTop']}px, 1위실측가={check['topPrice']}원, 광고노출={check['adVisible']})")

                results["steady_results"].append({
                    "index": i,
                    "category": "국민 필수 생필품",
                    "name": name,
                    "keyword": kw,
                    "card_price": card_price,
                    "mall_name": card_mall,
                    "target_url": target_url,
                    "scrollY": check["scrollY"],
                    "hasDui": check["hasDui"],
                    "hasHeading": check["hasHeading"],
                    "headingTop": check["headingTop"],
                    "naver_top_price": check["topPrice"],
                    "naver_top_title": check["topTitle"],
                    "adVisible": check["adVisible"],
                    "pass": is_pass
                })
            except Exception as e:
                print(f"  ❌ 네이버 접속 에러: {e}")
                results["steady_results"].append({
                    "index": i,
                    "category": "국민 필수 생필품",
                    "name": name,
                    "keyword": kw,
                    "card_price": card_price,
                    "mall_name": card_mall,
                    "target_url": target_url,
                    "pass": False,
                    "error": str(e)
                })

        # 2. 핫딜 16개 검사
        print("\n\n▶ [PART 2] 🔥 오늘 실시간 핫딜 16대 품목 전수 검증")
        for i, (kw, name) in enumerate(trending_list, 1):
            print(f"\n[{i}/{len(trending_list)}] 핫딜: {name} ({kw})")
            
            api_url = f"http://127.0.0.1:8080/api/search?q={urllib.parse.quote(kw)}"
            try:
                res = urllib.request.urlopen(api_url, timeout=8)
                data = json.loads(res.read().decode("utf-8"))
            except Exception as e:
                print(f"  ❌ API 에러: {e}")
                results["trending_results"].append({"index": i, "name": name, "keyword": kw, "status": "API_FAIL", "error": str(e), "pass": False})
                continue

            item = data.get("representative_item") or (data.get("top_items", [{}])[0] if data.get("top_items") else {})
            card_price = item.get("price", 0)
            card_mall = item.get("mallName") or item.get("mall") or item.get("mall_name") or ""
            target_url = item.get("url") or item.get("mallUrl") or item.get("link") or ""

            print(f"  - PriceTrace 카드: {card_price:,}원 ({card_mall})")
            print(f"  - 직결 링크: {target_url}")

            if not target_url:
                print(f"  ❌ 링크 부재 오류")
                results["trending_results"].append({"index": i, "name": name, "keyword": kw, "pass": False, "error": "EMPTY_URL"})
                continue

            try:
                page.goto(target_url, wait_until="networkidle", timeout=15000)
                page.wait_for_timeout(800)
                
                check = page.evaluate("""() => {
                    const dui = document.getElementById('shp_dui_root');
                    const headings = Array.from(document.querySelectorAll('h2, h3'));
                    const priceCompareHeading = headings.find(h => h.innerText.includes('가격비교'));
                    
                    let topPrice = null;
                    let topTitle = '';
                    if (dui) {
                        const priceEl = dui.querySelector('.price_num, [class*=\"price_num\"], [class*=\"price\"] strong, .value');
                        if (priceEl) {
                            topPrice = parseInt(priceEl.innerText.replace(/[^0-9]/g, '')) || null;
                        }
                        const titleEl = dui.querySelector('a[class*=\"title\"], [class*=\"tit\"] a, h3 a');
                        if (titleEl) {
                            topTitle = titleEl.innerText.trim();
                        }
                    }
                    
                    const adSections = document.querySelectorAll('[class*=\"power_link\"], [class*=\"ad_section\"], .powerlink');
                    let adVisible = false;
                    for (const ad of adSections) {
                        const r = ad.getBoundingClientRect();
                        if (r.top >= 0 && r.top < window.innerHeight) { adVisible = true; break; }
                    }

                    return {
                        scrollY: window.scrollY,
                        hasDui: !!dui,
                        hasHeading: !!priceCompareHeading,
                        headingText: priceCompareHeading ? priceCompareHeading.innerText.trim() : 'none',
                        headingTop: priceCompareHeading ? Math.round(priceCompareHeading.getBoundingClientRect().top) : -9999,
                        topPrice: topPrice,
                        topTitle: topTitle,
                        adVisible: adVisible
                    };
                }""")

                is_pass = check["hasDui"] and check["hasHeading"] and not check["adVisible"]
                status_str = "PASS ✅" if is_pass else "FAIL ❌"
                print(f"  - 결과: {status_str} (scrollY={check['scrollY']}px, 헤딩={check['headingText']}, top={check['headingTop']}px, 1위실측가={check['topPrice']}원, 광고노출={check['adVisible']})")

                results["trending_results"].append({
                    "index": i,
                    "category": "오늘 실시간 핫딜",
                    "name": name,
                    "keyword": kw,
                    "card_price": card_price,
                    "mall_name": card_mall,
                    "target_url": target_url,
                    "scrollY": check["scrollY"],
                    "hasDui": check["hasDui"],
                    "hasHeading": check["hasHeading"],
                    "headingTop": check["headingTop"],
                    "naver_top_price": check["topPrice"],
                    "naver_top_title": check["topTitle"],
                    "adVisible": check["adVisible"],
                    "pass": is_pass
                })
            except Exception as e:
                print(f"  ❌ 네이버 접속 에러: {e}")
                results["trending_results"].append({
                    "index": i,
                    "category": "오늘 실시간 핫딜",
                    "name": name,
                    "keyword": kw,
                    "card_price": card_price,
                    "mall_name": card_mall,
                    "target_url": target_url,
                    "pass": False,
                    "error": str(e)
                })

        browser.close()

    total = len(results["steady_results"]) + len(results["trending_results"])
    passes = sum(1 for r in results["steady_results"] if r.get("pass")) + sum(1 for r in results["trending_results"] if r.get("pass"))
    fails = total - passes

    results["summary"]["total"] = total
    results["summary"]["pass_count"] = passes
    results["summary"]["fail_count"] = fails
    results["summary"]["pass_rate_percent"] = round((passes / total) * 100, 1) if total > 0 else 0

    out_file = os.path.join(ARTIFACT_DIR, "audit_all_32_items_result.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n=================================================================")
    print(f"🎯 [32개 전수 검사 최종 결과] 통과: {passes}/{total} ({results['summary']['pass_rate_percent']}%) | 실패: {fails}건")
    print(f"📁 결과 보고서: {out_file}")
    print("=================================================================")
    return results

if __name__ == "__main__":
    audit_32_items()
