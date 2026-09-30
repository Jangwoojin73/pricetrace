import os
import sys
import json
import urllib.parse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server
import pricetrace_bot

TEST_KEYWORDS = [
    ("가공식품", "농심 신라면 봉지 20개입"),
    ("즉석밥", "CJ제일제당 햇반 210g 24개"),
    ("음료", "코카콜라 제로 355ml 24캔"),
    ("커피", "동서식품 맥심 모카골드 160T"),
    ("통조림", "동원참치 135g 10캔"),
    ("통조림", "스팸 클래식 200g 10캔"),
    ("신선과일", "사과"),
    ("신선수산", "새우"),
    ("대용량화장지", "코스트코 커클랜드 휴지 3겹 30롤"),
    ("화장지", "깨끗한나라 순수 3겹 30롤"),
    ("세탁세제", "퍼실 딥클린 파워젤 2.7L"),
    ("섬유탈취제", "페브리즈 섬유탈취제 다우니 4개"),
    ("프라모델", "용호모형 1 100 후쿠오카 뉴"),
    ("건담프라모델", "반다이 건담 MG 1 100"),
    ("디지털기기", "로지텍 마우스 G102")
]

results = []
print("=" * 80)
print("🚀 [전수검사] 15대 대표 검색어 무결성 & 오매칭 방지 전수 검증 시작")
print("=" * 80)

all_passed = True

for category, kw in TEST_KEYWORDS:
    res = server.fetch_price_data(kw, force_refresh=True)
    success = res.get("success", False)
    top_items = res.get("top_items", [])
    
    # 1. 0건 여부
    has_items = len(top_items) > 0
    
    # 2. 가격 오름차순 검증
    prices = [it.get("price", 0) for it in top_items]
    is_sorted = all(prices[i] <= prices[i+1] for i in range(len(prices)-1)) if len(prices) > 1 else True
    
    # 3. 오매칭 검증 (관련성 판정)
    mismatch_detected = False
    mismatched_reasons = []
    
    # 프라모델 검색어 특화 검증: 니트릴장갑, 현수막, 북어트릿 등 포함 시 즉시 FAIL
    if "용호모형" in kw or "건담" in kw:
        for it in top_items:
            t = it.get("title", "").lower()
            if any(bad in t for bad in ["장갑", "현수막", "북어", "간식", "김치", "양말"]):
                mismatch_detected = True
                mismatched_reasons.append(f"무관 품목 '{it.get('title')}' 혼입")
    
    if "사과" == kw:
        for it in top_items:
            t = it.get("title", "").lower()
            if "사과대추" in t or "사과식초" in t or "사과즙" in t:
                mismatch_detected = True
                mismatched_reasons.append(f"합성어 '{it.get('title')}' 혼입")

    if "새우" == kw:
        for it in top_items:
            t = it.get("title", "").lower()
            if "새우깡" in t or "새우칩" in t or "새우젓" in t:
                mismatch_detected = True
                mismatched_reasons.append(f"가공스낵 '{it.get('title')}' 혼입")
                
    # 4. URL 규격 검증 (search.shopping.naver.com + frm=NVSCPRO 포함)
    url_valid = True
    for it in top_items:
        u = it.get("url", "")
        if "search.shopping.naver.com/search/all" not in u or "frm=NVSCPRO" not in u:
            url_valid = False
            
    passed = has_items and is_sorted and not mismatch_detected and url_valid
    if not passed:
        all_passed = False
        
    status_str = "✅ PASS" if passed else "❌ FAIL"
    rep_title = top_items[0].get("title") if top_items else "결과없음"
    rep_price = top_items[0].get("price", 0) if top_items else 0
    rep_url = top_items[0].get("url", "") if top_items else ""
    
    print(f"[{status_str}] [{category}] {kw}")
    print(f"   - 1위: {rep_title} ({rep_price:,}원)")
    print(f"   - URL: {rep_url}")
    if mismatched_reasons:
        print(f"   - ⚠️ 결함: {', '.join(mismatched_reasons)}")
    print("-" * 80)
    
    results.append({
        "category": category,
        "keyword": kw,
        "passed": passed,
        "rep_title": rep_title,
        "rep_price": rep_price,
        "rep_url": rep_url,
        "items_count": len(top_items),
        "is_sorted": is_sorted,
        "mismatch_detected": mismatch_detected
    })

print(f"\n최종 결과: {'🎉 15개 전 품목 100% 무결성 통과!' if all_passed else '❌ 일부 품목 실패 발견'}")

# 결과 저장
with open("execution/audit_results_15.json", "w", encoding="utf-8") as f:
    json.dump({"all_passed": all_passed, "results": results}, f, ensure_ascii=False, indent=2)
