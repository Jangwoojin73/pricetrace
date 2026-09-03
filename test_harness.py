#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_harness.py - pricetrace_bot 검증용 테스트 하네스

[검사 항목 4가지]
1. 14,000원일 때 특가 메시지("🚨 [특가 발생] 목표 가격 이하입니다!")가 나오는가?
2. 16,000원일 때 유지 메시지("ℹ️ [유지] 아직 목표 가격보다 비쌉니다.")가 나오는가?
3. 광고 상품(is_ad: True)이 섞여 있을 때 걸러 내는가?
4. 값을 못 가져왔을 때 프로그램이 비정상 종료(Crash)되지 않고 오류 원인을 명확히 안내하는가?

[원칙]
- 실제 네이버 네트워크 요청 없이 오직 가짜 데이터(Mock Data)만 사용
- 각 검사 항목별 [PASS] / [FAIL] 결과 목록 및 상세 요약 출력
"""

import sys
import io
from typing import List, Dict, Any, Tuple

# Windows 콘솔 인코딩 대응
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# pricetrace_bot 모듈 임포트
try:
    import pricetrace_bot
except ImportError:
    print("❌ [하네스 오류] pricetrace_bot.py 모듈을 찾을 수 없습니다.")
    sys.exit(1)


def test_1_special_price_alert() -> Tuple[bool, str]:
    """
    검사 1: 14,000원일 때 특가 메시지가 나오는가?
    기대 메시지: "🚨 [특가 발생] 목표 가격 이하입니다!"
    """
    mock_items = [
        {
            "title": "농심 신라면 120g 20개 (특가 상품)",
            "price": 14000,
            "mall_name": "테스트 마트 A",
            "url": "https://example.com/item1",
            "review_count": 50,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "농심 신라면 120g 20개 1박스",
            "price": 14500,
            "mall_name": "테스트 마트 B",
            "url": "https://example.com/item2",
            "review_count": 30,
            "score": 4.8,
            "is_ad": False
        },
        {
            "title": "농심 신라면 봉지 120g 20입",
            "price": 14900,
            "mall_name": "테스트 마트 C",
            "url": "https://example.com/item3",
            "review_count": 10,
            "score": 4.7,
            "is_ad": False
        }
    ]

    def mock_fetcher():
        return mock_items, []

    # 봇 실행 (표준 출력 캡처)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        res = pricetrace_bot.run_pricetrace_bot(fetcher=mock_fetcher, exit_on_error=False)
        output_text = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    expected_alert = "🚨 [특가 발생] 목표 가격 이하입니다!"
    if res.get("success") and res.get("lowest_price") == 14000:
        if expected_alert in res.get("alert_message", "") or expected_alert in output_text:
            return True, f"14,000원 입력 시 '{expected_alert}' 정상 출력 확인"
        else:
            return False, f"특가 메시지 불일치. 실제 메시지: '{res.get('alert_message')}'"
    return False, f"봇 실행 실패 또는 최저가 불일치 (결과: {res})"


def test_2_maintain_price_alert() -> Tuple[bool, str]:
    """
    검사 2: 16,000원일 때 유지 메시지가 나오는가?
    기대 메시지: "ℹ️ [유지] 아직 목표 가격보다 비쌉니다."
    """
    mock_items = [
        {
            "title": "농심 신라면 120g 20개",
            "price": 16000,
            "mall_name": "테스트 마트 D",
            "url": "https://example.com/item4",
            "review_count": 80,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "농심 신라면 120g 20개 1박스",
            "price": 16500,
            "mall_name": "테스트 마트 E",
            "url": "https://example.com/item5",
            "review_count": 40,
            "score": 4.8,
            "is_ad": False
        },
        {
            "title": "농심 신라면 봉지 120g 20입",
            "price": 17000,
            "mall_name": "테스트 마트 F",
            "url": "https://example.com/item6",
            "review_count": 20,
            "score": 4.7,
            "is_ad": False
        }
    ]

    def mock_fetcher():
        return mock_items, []

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        res = pricetrace_bot.run_pricetrace_bot(fetcher=mock_fetcher, exit_on_error=False)
        output_text = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    expected_alert = "ℹ️ [유지] 아직 목표 가격보다 비쌉니다."
    if res.get("success") and res.get("lowest_price") == 16000:
        if expected_alert in res.get("alert_message", "") or expected_alert in output_text:
            return True, f"16,000원 입력 시 '{expected_alert}' 정상 출력 확인"
        else:
            return False, f"유지 메시지 불일치. 실제 메시지: '{res.get('alert_message')}'"
    return False, f"봇 실행 실패 또는 최저가 불일치 (결과: {res})"


def test_3_ad_filter() -> Tuple[bool, str]:
    """
    검사 3: 광고 상품이 섞여 있을 때 걸러 내는가?
    가짜 데이터에 is_ad: True 상품(매우 저렴한 가짜 광고)을 섞었을 때 제외되는지 검증
    """
    mock_mixed_items = [
        {
            "title": "[광고] 농심 신라면 120g 20개 최저가 이벤트",
            "price": 9900,  # 최저가처럼 보이지만 광고 상품
            "mall_name": "광고 스토어",
            "url": "https://example.com/ad_item",
            "review_count": 999,
            "score": 5.0,
            "is_ad": True  # 광고 플래그
        },
        {
            "title": "농심 신라면 120g 20개 정품 일반판매",
            "price": 13500,
            "mall_name": "진짜 마트 1",
            "url": "https://example.com/real_item1",
            "review_count": 120,
            "score": 4.85,
            "is_ad": False
        },
        {
            "title": "농심 신라면 120g 20개 1박스",
            "price": 13800,
            "mall_name": "진짜 마트 2",
            "url": "https://example.com/real_item2",
            "review_count": 85,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "농심 신라면 봉지 120g 20입",
            "price": 14200,
            "mall_name": "진짜 마트 3",
            "url": "https://example.com/real_item3",
            "review_count": 45,
            "score": 4.90,
            "is_ad": False
        }
    ]

    def mock_fetcher():
        return mock_mixed_items, []

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        res = pricetrace_bot.run_pricetrace_bot(fetcher=mock_fetcher, exit_on_error=False)
    finally:
        sys.stdout = old_stdout

    if not res.get("success"):
        return False, "봇 실행 중 오류 발생"

    items = res.get("items", [])
    # 9900원 광고 상품이 포함되었는지 확인
    for item in items:
        if item.get("is_ad", False) or item.get("price") == 9900:
            return False, f"광고 상품(9,900원, is_ad=True)이 걸러지지 않고 결과에 포함됨"

    # 1위가 진짜 일반 상품(13,500원)인지 확인
    if res.get("lowest_price") == 13500:
        return True, "광고 상품(9,900원)을 정상 제외하고 진짜 상품(13,500원)을 1위로 선정함"
    else:
        return False, f"최저가 산정 오류: 기대 13,500원, 실제 {res.get('lowest_price')}원"


def test_4_error_handling_without_crash() -> Tuple[bool, str]:
    """
    검사 4: 값을 못 가져왔을 때 프로그램이 비정상 종료(Crash)하지 않고 오류 원인을 명확히 안내하는가?
    """
    def mock_failing_fetcher():
        # 데이터 수집 실패 및 오류 리스트 반환
        return [], ["네이버 쇼핑 서버 연결 시간 초과 (HTTP 504)", "k-skill-proxy 응답 없음 (HTTP 503)"]

    old_stdout = sys.stdout
    captured_io = io.StringIO()
    sys.stdout = captured_io
    try:
        res = pricetrace_bot.run_pricetrace_bot(fetcher=mock_failing_fetcher, exit_on_error=False)
        output_text = captured_io.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return False, f"봇이 예외를 처리하지 못하고 비정상 종료(Crash)됨: {e}"
    finally:
        sys.stdout = old_stdout

    # 오류 원인이 화면에 출력되었는지 확인
    has_error_header = "❌ [오류 발생]" in output_text or "DATA_FETCH_FAILED" == res.get("error")
    has_error_reason = "HTTP 504" in output_text or "HTTP 503" in output_text or len(res.get("error_details", [])) > 0
    no_fake_data = len(res.get("items", [])) == 0

    if has_error_header and has_error_reason and no_fake_data and (not res.get("success")):
        return True, "가짜 데이터를 지어내지 않고 수집 실패 원인을 사용자에게 명확히 안내하며 안전 처리됨"
    else:
        return False, f"오류 안내 메시지 미흡 (출력 내용: {output_text})"


def main():
    print("=" * 68)
    print("🧪 [Test Harness] pricetrace_bot.py 기능 검증 테스트 러너")
    print("=" * 68)
    print("📋 검사 모드: 가짜 데이터(Mock) 주입 방식 (네이버 실요청 없음)")
    print("-" * 68)

    tests = [
        ("1. 14,000원일 때 특가 메시지 출력 검사", test_1_special_price_alert),
        ("2. 16,000원일 때 유지 메시지 출력 검사", test_2_maintain_price_alert),
        ("3. 광고 상품(is_ad: True) 필터링 검사", test_3_ad_filter),
        ("4. 데이터 수집 실패 시 오류 안내 및 안전 처리 검사", test_4_error_handling_without_crash),
    ]

    all_passed = True
    results = []

    for name, test_fn in tests:
        passed, detail = test_fn()
        results.append((name, passed, detail))
        if not passed:
            all_passed = False

    # 결과 목록 출력
    print("\n[📊 검사 항목별 최종 결과 목록]\n")
    for name, passed, detail in results:
        status_tag = "✅ [PASS]" if passed else "❌ [FAIL]"
        print(f"{status_tag} {name}")
        print(f"   └─ 상세: {detail}")

    print("\n" + "=" * 68)
    if all_passed:
        print("🎉 [결과 요약] 총 4개 검사 항목 모두 PASS 되었습니다!")
    else:
        print("⚠️ [결과 요약] 일부 검사 항목이 FAIL 되었습니다.")
    print("=" * 68 + "\n")

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
