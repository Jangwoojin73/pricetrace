import sys
import io
import urllib.request
import urllib.parse
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

keywords = [
    "농심 신라면 봉지 20개입",
    "CJ제일제당 햇반 210g 24개",
    "코카콜라 제로 355ml 24캔",
    "제주 삼다수 2L 6개",
    "오뚜기 진라면 매운맛 40개",
    "동원참치 라이트스탠다드 100g 10캔"
]

print("=" * 65)
print("🔍 다중 검색어 API 실시간 연동 및 URL 정규화 전수 무결성 테스트")
print("=" * 65)

all_passed = True
total_links_inspected = 0
cr_violations = 0
catalogs_found = 0

for kw in keywords:
    url = f"http://127.0.0.1:8080/api/search?q={urllib.parse.quote(kw)}&target_price=0"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            rep = data.get("representative_item", {})
            top_items = data.get("top_items", [])
            lowest_price = data.get("lowest_price", 0)
            has_img = bool(rep.get("image_url"))
            has_url = bool(rep.get("url"))
            unit_price = data.get("unit_price", 0)
            unit_cnt = data.get("unit_count", 1)

            print(f"\n[{kw}]")
            print(f"  • 수집 성공 여부 : {data.get('success')}")
            print(f"  • 대표 상품명    : {rep.get('title')}")
            print(f"  • 최저 판매가    : {lowest_price:,}원 (수량: {unit_cnt}개, 환산단가: {unit_price:,}원)")
            print(f"  • 대표 이미지 URL: {rep.get('image_url')}")
            print(f"  • 대표 구매 링크 : {rep.get('url')}")
            print(f"  • 비교 판매처 수 : {len(top_items)}개")

            # 대표 상품 URL 검사
            rep_url = rep.get("url", "")
            total_links_inspected += 1
            if any(p in rep_url for p in ["shopping.naver.com/v2/bridge", "searchGate", "cr.shopping.naver.com", "cr3.shopping.naver.com"]):
                cr_violations += 1
                print(f"    ❌ [대표 상품] 금지된 cr3 브릿지 링크 발견: {rep_url}")
            elif "search.shopping.naver.com/catalog/" in rep_url:
                catalogs_found += 1
                print(f"    ✅ [대표 상품] 카탈로그 정규 링크 검증 완료")
            else:
                print(f"    ✅ [대표 상품] 스토어 직링크 검증 완료")

            # 상위 1~3위 판매처 URL 검사
            for rank, item in enumerate(top_items, 1):
                item_url = item.get("url", "")
                mall = item.get("mall_name", "")
                total_links_inspected += 1
                if any(p in item_url for p in ["shopping.naver.com/v2/bridge", "searchGate", "cr.shopping.naver.com", "cr3.shopping.naver.com"]):
                    cr_violations += 1
                    print(f"    ❌ [{rank}위 {mall}] 금지된 cr3 브릿지 링크 발견: {item_url}")
                elif "search.shopping.naver.com/catalog/" in item_url:
                    catalogs_found += 1
                    print(f"    ✅ [{rank}위 {mall}] 카탈로그 정규 링크 검증: {item_url[:65]}...")
                else:
                    print(f"    ✅ [{rank}위 {mall}] 쇼핑몰 직링크 검증: {item_url[:65]}...")

            if not (data.get("success") and lowest_price > 0 and has_url and has_img):
                all_passed = False
                print("  [FAIL] 데이터 불완전")
    except Exception as e:
        print(f"[ERROR] on [{kw}]: {e}")
        all_passed = False

print("\n" + "=" * 65)
print(f"📊 검증 요약: 총 링크 {total_links_inspected}개 검사")
print(f"  - 정규 카탈로그 링크 : {catalogs_found}개")
print(f"  - 오류 유발 브릿지 링크: {cr_violations}개 (기대치: 0개)")

if cr_violations > 0:
    all_passed = False

if all_passed and cr_violations == 0:
    print("🎉 [SUCCESS] 모든 검색어에서 n2 오류 유발 링크 0건! 100% 정상 정규화 통과!")
else:
    print("❌ [WARNING] 일부 품목 테스트 실패 또는 브릿지 링크 잔존")
print("=" * 65)

