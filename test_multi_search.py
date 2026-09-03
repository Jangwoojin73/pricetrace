import urllib.request
import urllib.parse
import json

keywords = [
    "농심 신라면 봉지 20개입",
    "CJ제일제당 햇반 210g 24개",
    "코카콜라 제로 355ml 24캔",
    "제주 삼다수 2L 6개",
    "오뚜기 진라면 매운맛 40개"
]

print("=== 다중 검색어 API 실시간 연동 테스트 ===")
all_passed = True

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
            print(f"  - 성공: {data.get('success')}")
            print(f"  - 대표 상품명: {rep.get('title')}")
            print(f"  - 최저 판매가: {lowest_price:,}원 (감지 수량: {unit_cnt}개, 환산단가: {unit_price:,}원)")
            print(f"  - 이미지 URL: {rep.get('image_url')}")
            print(f"  - 구매 링크: {rep.get('url')}")
            print(f"  - 판매처 수: {len(top_items)}개")

            if not (data.get("success") and lowest_price > 0 and has_url and has_img):
                all_passed = False
                print("  [FAIL] 데이터 불완전")
            else:
                print("  [PASS] 정상 수집 및 매핑")
    except Exception as e:
        print(f"[ERROR] on [{kw}]: {e}")
        all_passed = False

print("\n" + "=" * 50)
if all_passed:
    print("[SUCCESS] 5개 인기 품목 모두 실시간 최저가, 이미지, 링크 연동 성공!")
else:
    print("[WARNING] 일부 품목 테스트 실패")
print("=" * 50)
