#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pricetrace_bot.py - 네이버 쇼핑 기반 라면 최저가 추적 및 알림 봇

주요 기능:
1. '농심 신라면 봉지 20개입' 실시간 최저가 검색 (k-skill proxy 및 공개 BFF 연동)
2. 광고(Ad) 상품 및 타 변형 상품 자동 제외 필터링
3. 상위 3개 최저가 상품 정보(상품명, 가격, 쇼핑몰, 리뷰 수, 링크) 출력
4. 1위 가격이 목표가 15,000원 이하인지 확인해 다음 중 하나를 함께 출력:
   - 목표가 이하일 때: "🚨 [특가 발생] 목표 가격 이하입니다!"
   - 목표가 초과일 때: "ℹ️ [유지] 아직 목표 가격보다 비쌉니다."
5. 값을 못 가져오면 지어내지 않고, 무엇이 잘못됐는지 그대로 알려 주고 멈춤
"""

import sys
import io

# Windows 환경 콘솔 출력 시 유니코드(UTF-8) 인코딩 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import json
import ssl
import re
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Callable, Tuple

# ==========================================
# 설정 상수
# ==========================================
PRIMARY_KEYWORD: str = "농심 신라면 봉지 20개입"
SEARCH_KEYWORDS: List[str] = [
    "농심 신라면 봉지 20개입",
    "농심 신라면 120g 20개",
    "신라면 20개"
]
TARGET_PRICE: int = 15000  # 알림 기준 목표가 (원)
TOP_N: int = 3  # 화면에 출력할 최저가 상품 개수

# 프록시 및 Fallback 엔드포인트 URL
PROXY_API_URL: str = "https://k-skill-proxy.nomadamas.org/v1/naver-shopping/search"
BFF_API_URL: str = "https://ns-portal.shopping.naver.com/api/v2/shopping-paged-slot"

# 제외할 파생 상품 및 타 수량 키워드
EXCLUDE_KEYWORDS: List[str] = [
    "블랙", "black", "건면", "더레드", "thered", "the red",
    "툼바", "투움바", "toomba", "골드", "gold", "볶음면",
    "짜파게티", "안성탕면", "너구리", "진라면",
    "컵", "사발", "소컵", "큰사발",
    "40개", "30개", "10개", "5개", "8개", "4개", "60개", "80개",
    "마일드앤블랙"
]


def create_ssl_context() -> ssl.SSLContext:
    """SSL 검증 컨텍스트 생성"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_from_proxy(keyword: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
    """
    k-skill 프록시 API를 통해 상품 데이터를 조회합니다.
    """
    params = urllib.parse.urlencode({
        "q": keyword,
        "limit": limit,
        "sort": "price_asc"
    })
    url = f"{PROXY_API_URL}?{params}"
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    
    try:
        ctx = create_ssl_context()
        with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                items = data.get("items", [])
                if items:
                    return items
    except Exception:
        return None
    return None


def fetch_from_naver_bff(keyword: str) -> List[Dict[str, Any]]:
    """
    네이버 쇼핑 공개 BFF JSON 엔드포인트를 직접 조회합니다.
    """
    encoded_query = urllib.parse.quote(keyword)
    url = f"{BFF_API_URL}?query={encoded_query}&source=shp_gui"
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://shopping.naver.com/"
        }
    )
    
    try:
        ctx = create_ssl_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP 응답 오류: 상태 코드 {response.status}")
            raw_bytes = response.read()
            data = json.loads(raw_bytes.decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"네이버 쇼핑 서버 연결 실패: {e.reason}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 데이터 파싱 실패: {e.msg}")
    except Exception as e:
        raise RuntimeError(f"데이터 조회 중 오류 발생: {str(e)}")

    data_list = data.get("data", [])
    if not data_list or not isinstance(data_list, list):
        raise RuntimeError("네이버 쇼핑 응답의 'data' 항목이 비어 있습니다.")

    slots = data_list[0].get("slots", [])
    if not slots:
        raise RuntimeError(f"'{keyword}'에 대한 검색 결과 슬롯이 없습니다.")

    extracted_items = []
    for slot in slots:
        d = slot.get("data", {})
        if not d:
            continue

        # 광고 플래그 검사
        is_ad = bool(d.get("isAd", False) or d.get("ad", False) or (d.get("sasType") == "AD"))

        title = d.get("productName") or d.get("productTitle") or ""
        title_clean = title.replace("<mark>", "").replace("</mark>", "").replace("<b>", "").replace("</b>", "").strip()

        price = d.get("discountedSalePrice") or d.get("salePrice") or d.get("lowPrice") or 0
        try:
            price = int(price)
        except (ValueError, TypeError):
            price = 0

        mall = d.get("mallName") or d.get("shopName") or ""
        if not mall:
            mall = "네이버 가격비교 (카탈로그)"

        product_url = d.get("productUrl", {})
        url = product_url.get("pcUrl") or product_url.get("mobileUrl") if isinstance(product_url, dict) else str(product_url)
        if not url:
            click_url = d.get("productClickUrl", {})
            url = click_url.get("pcUrl") or click_url.get("mobileUrl") if isinstance(click_url, dict) else str(click_url)

        review_count = d.get("totalReviewCount") or d.get("reviewCount") or 0
        score = d.get("averageReviewScore") or d.get("score") or 0.0

        images = d.get("images", [])
        image_url = ""
        if isinstance(images, list) and len(images) > 0 and isinstance(images[0], dict):
            image_url = images[0].get("imageUrl") or ""
        if not image_url:
            image_url = d.get("imageUrl") or d.get("productImageUrl") or ""

        if title_clean and price > 0:
            extracted_items.append({
                "title": title_clean,
                "price": price,
                "mall_name": mall,
                "url": url,
                "image_url": image_url,
                "review_count": review_count,
                "score": float(score),
                "is_ad": is_ad
            })

    return extracted_items


def fetch_products_for_keyword(keyword: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """임의의 검색어에 대해 네이버 쇼핑 실시간 데이터를 수집합니다."""
    all_items: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        bff_items = fetch_from_naver_bff(keyword)
        if bff_items:
            all_items.extend(bff_items)
    except Exception as e:
        errors.append(f"네이버 쇼핑 BFF '{keyword}': {str(e)}")

    if not all_items:
        try:
            proxy_items = fetch_from_proxy(keyword)
            if proxy_items:
                all_items.extend(proxy_items)
        except Exception as e:
            errors.append(f"프록시 '{keyword}': {str(e)}")

    return all_items, errors


def default_data_fetcher(keyword: Optional[str] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
    """실제 네이버 쇼핑 데이터를 수집하는 기본 fetcher (임의 키워드 지원)"""
    if keyword and keyword != PRIMARY_KEYWORD:
        return fetch_products_for_keyword(keyword)

    all_raw_items: List[Dict[str, Any]] = []
    fetch_errors: List[str] = []

    for kw in SEARCH_KEYWORDS:
        try:
            bff_items = fetch_from_naver_bff(kw)
            if bff_items:
                all_raw_items.extend(bff_items)
        except Exception as e:
            fetch_errors.append(f"'{kw}': {str(e)}")

    return all_raw_items, fetch_errors


def filter_and_refine_products(items: List[Dict[str, Any]], keyword: str = "") -> List[Dict[str, Any]]:
    """
    광고 상품을 제외하고, 검색어에 맞는 상품을 정밀 필터링합니다.
    검색어가 비어있거나 '신라면'인 경우 신라면 20개입 전용 필터링을 적용합니다.
    """
    valid_products = []
    seen = set()

    is_shinramyun_mode = (not keyword) or ("신라면" in keyword)

    for item in items:
        # 1. 광고 상품 필터링
        if item.get("is_ad", False):
            continue

        title = item.get("title", "")
        title_lower = title.lower()
        price = item.get("price", 0)

        if is_shinramyun_mode:
            # 2. '신라면' 필수 포함 확인
            if "신라면" not in title:
                continue

            # 3. 파생 상품(블랙, 건면, 투움바 등) 제외 키워드 검사
            if any(exc in title_lower for exc in EXCLUDE_KEYWORDS):
                continue

            # 4. 20개입(20개, 20봉, 20입, 20ea 등) 수량 확인
            match_20 = re.search(r'(20\s*(개|봉|입|ea|p|pack)|20개입)', title_lower)
            if not match_20:
                continue

            if price < 5000:
                continue
        else:
            # 일반 검색어 모드: 검색어 키워드 매칭
            kw_tokens = [tok.strip() for tok in re.split(r'\s+', keyword) if len(tok.strip()) >= 2]
            if kw_tokens:
                if not any(token.lower() in title_lower for token in kw_tokens):
                    continue
            if price < 500:
                continue

        key = (title, price, item.get("mall_name", ""))
        if key not in seen:
            seen.add(key)
            valid_products.append(item)

    # 최저가 순(오름차순) 정렬
    valid_products.sort(key=lambda x: x["price"])
    return valid_products


def get_price_alert_message(lowest_price: int, target_price: int = TARGET_PRICE) -> str:
    """
    1위 최저가와 목표 가격을 비교하여 알림 메시지를 반환합니다.
    """
    if lowest_price <= target_price:
        return "🚨 [특가 발생] 목표 가격 이하입니다!"
    else:
        return "ℹ️ [유지] 아직 목표 가격보다 비쌉니다."


def run_pricetrace_bot(
    fetcher: Optional[Callable[[], Tuple[List[Dict[str, Any]], List[str]]]] = None,
    exit_on_error: bool = True
) -> Dict[str, Any]:
    """
    최저가 추적 봇 메인 실행 함수
    
    Args:
        fetcher: 데이터 수집 함수 (기본값 None 시 default_data_fetcher 사용)
        exit_on_error: 오류 발생 시 sys.exit(1) 실행 여부 (테스트 시 False 설정)
        
    Returns:
        실행 결과 요약 딕셔너리
    """
    print("=" * 68)
    print("🍜 [PriceTrace Bot] 농심 신라면 봉지 20개입 최저가 추적기")
    print("=" * 68)
    print(f"🔍 검색 대상 : '{PRIMARY_KEYWORD}'")
    print(f"🎯 목표 알림가 : {TARGET_PRICE:,}원")
    print("-" * 68)

    fetch_fn = fetcher if fetcher is not None else default_data_fetcher
    all_raw_items, fetch_errors = fetch_fn()

    # 5. 값을 전혀 못 가져온 경우 지어내지 않고 오류 원인 출력 후 중단
    if not all_raw_items:
        print("\n❌ [오류 발생] 네이버 쇼핑에서 상품 정보를 가져오지 못했습니다.")
        if fetch_errors:
            print("   상세 원인:")
            for err in fetch_errors:
                print(f"   • {err}")
        else:
            print("   원인: 응답된 데이터가 0건입니다.")
        print("\n⚠️ 사실이 아닌 정보를 지어내지 않고 안전하게 봇을 중단합니다.")
        print("   네트워크 연결 상태나 네이버 쇼핑 접근 환경을 점검해 주세요.\n")
        
        result = {
            "success": False,
            "error": "DATA_FETCH_FAILED",
            "error_details": fetch_errors,
            "items": []
        }
        if exit_on_error:
            sys.exit(1)
        return result

    # 3. 광고 상품 및 파생 라면 제외 정밀 필터링
    refined_items = filter_and_refine_products(all_raw_items)

    if not refined_items:
        print("\n❌ [필터링 오류] 검색 결과 중 순수한 '오리지널 신라면 20개입' 상품을 찾지 못했습니다.")
        print("   원인: 반환된 결과가 모두 타 파생 라면(블랙/건면 등)이거나 비정상 수량 옵션이었습니다.")
        print("   봇 실행을 중단합니다.\n")
        
        result = {
            "success": False,
            "error": "FILTERING_FAILED",
            "items": []
        }
        if exit_on_error:
            sys.exit(1)
        return result

    # 2. 저렴한 순서로 상위 3개 상품 출력
    top_items = refined_items[:TOP_N]
    print(f"\n🏆 [실시간 최저가 TOP {len(top_items)} 상품 목록]\n")

    for rank, item in enumerate(top_items, 1):
        medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else "🥉")
        unit_price = round(item['price'] / 20)
        review_cnt = item.get('review_count', 0)
        review_text = f"{review_cnt:,}개" if review_cnt > 0 else "0개"
        score_val = item.get('score', 0.0)
        score_text = f"★ {score_val:.2f}" if score_val > 0 else "평점 없음"

        print(f"{medal} {rank}위. {item['title']}")
        print(f"   • 가격    : {item['price']:,}원 (1봉지당 약 {unit_price:,}원)")
        print(f"   • 쇼핑몰  : {item['mall_name']}")
        print(f"   • 리뷰 수 : {review_text} ({score_text})")
        print(f"   • 링크    : {item['url']}")
        print("-" * 68)

    # 4. 1위 가격이 목표가 15,000원 이하인지 확인하여 알림 메시지 출력
    lowest_price = top_items[0]["price"]
    alert_msg = get_price_alert_message(lowest_price, TARGET_PRICE)
    
    print(f"\n📢 [목표 가격({TARGET_PRICE:,}원) 분석 결과]")
    print(f"   현재 1위 최저가: {lowest_price:,}원")
    print(f"   {alert_msg}")
    print("=" * 68 + "\n")

    return {
        "success": True,
        "items": top_items,
        "lowest_price": lowest_price,
        "alert_message": alert_msg
    }


if __name__ == "__main__":
    run_pricetrace_bot()
