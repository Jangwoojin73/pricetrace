#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api/index.py - Vercel Serverless Function 진입점

Vercel 표준 Serverless 규격(BaseHTTPRequestHandler 상속)을 준수하며,
/api/summary, /api/search, /api/history, /api/status 요청을 처리합니다.
해외 IP(Vercel 리전)에서 네이버 쇼핑 접근이 차단될 경우 안전한 캐시 데이터를 자동 반환합니다.
"""

import sys
import os
import re
import time
import json
import urllib.parse
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional, Tuple

# 상위 디렉토리 모듈 임포트 경로 추가
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

try:
    import pricetrace_bot
except ImportError:
    pricetrace_bot = None

# 캐시 파일 경로
CACHE_FILE = os.path.join(PARENT_DIR, "refined_shinramyun_20.json")

# 안전 폴백 데이터 (Vercel 해외 데이터센터 IP 차단 시 사용)
DEFAULT_FALLBACK_ITEMS = [
    {
        "title": "농심 신라면 120g 20개 한박스 멀티팩 낱개 가정용 업소용 행사용 캠핑",
        "price": 12400,
        "mall_name": "더싼 마트",
        "url": "https://smartstore.naver.com/main/products/11132243694",
        "review_count": 36,
        "score": 4.89,
        "is_ad": False
    },
    {
        "title": "농심 신라면, 120g, 20개",
        "price": 13200,
        "mall_name": "네이버 가격비교 (카탈로그)",
        "url": "https://search.shopping.naver.com/search/all?query=%EB%86%8D%EC%8B%AC%20%EC%8B%A0%EB%9D%BC%EB%A9%B4%20120g%2020%EA%B0%9C",
        "review_count": 104069,
        "score": 4.88,
        "is_ad": False
    },
    {
        "title": "농심 신라면120g 20개 1박스",
        "price": 13200,
        "mall": "신성마켓몰",
        "mall_name": "신성마켓몰",
        "url": "https://m.smartstore.naver.com/main/products/8676675032",
        "review_count": 715,
        "score": 4.88,
        "is_ad": False
    }
]

POOL_FALLBACK_DATA = {
    "햇반": [
        {
            "title": "CJ제일제당 햇반 210g 24개",
            "price": 25110,
            "mall": "다나와 가격비교",
            "mall_name": "다나와 가격비교",
            "url": "https://search.danawa.com/dsearch.php?query=%ED%96%87%EB%B0%98+24%EA%B0%9C",
            "image_url": "https://img.danuri.io/catalog-image/074/151/001/38cdd389a56f4c429c7d8ce164a1a2de.jpg",
            "review_count": 2840,
            "score": 4.91,
            "is_ad": False
        },
        {
            "title": "CJ제일제당 햇반 윤기가득쌀밥 210g 24개",
            "price": 23080,
            "mall": "스마트스토어",
            "mall_name": "스마트스토어",
            "url": "https://search.danawa.com/dsearch.php?query=%ED%96%87%EB%B0%98+24%EA%B0%9C",
            "image_url": "https://img.danuri.io/catalog-image/223/974/104/4b7a40991d644c419e7849c14f4bf68e.webp",
            "review_count": 912,
            "score": 4.88,
            "is_ad": False
        }
    ],
    "코카콜라": [
        {
            "title": "코카콜라 제로 355ml 24캔 1박스",
            "price": 18900,
            "mall": "다나와 가격비교",
            "mall_name": "다나와 가격비교",
            "url": "https://search.danawa.com/dsearch.php?query=%EC%BD%94%EC%B9%B4%EC%BD%9C%EB%9D%BC+%EC%A0%9C%EB%A1%9C+24%EC%BA%94",
            "image_url": "https://img.danuri.io/catalog-image/201/472/013/4919bce162ff4874b54fc8b6ab9fe573.jpg",
            "review_count": 5210,
            "score": 4.93,
            "is_ad": False
        }
    ],
    "삼다수": [
        {
            "title": "제주 삼다수 2L 6개",
            "price": 5980,
            "mall": "다나와 가격비교",
            "mall_name": "다나와 가격비교",
            "url": "https://search.danawa.com/dsearch.php?query=%EC%A0%9C%EC%A3%BC+%EC%82%BC%EB%8B%A4%EC%88%98+2L",
            "image_url": "https://img.danuri.io/catalog-image/118/740/014/6ebf7c9c79434e7b874850b5d1b310ce.jpg",
            "review_count": 3410,
            "score": 4.92,
            "is_ad": False
        }
    ],
    "스팸": [
        {
            "title": "CJ제일제당 스팸 클래식 200g 10개",
            "price": 25540,
            "mall": "다나와 가격비교",
            "mall_name": "다나와 가격비교",
            "url": "https://search.danawa.com/dsearch.php?query=%EC%8A%A4%ED%8C%B8+10%EC%BA%94",
            "image_url": "https://img.danuri.io/catalog-image/210/006/001/5b881f953b1947acad0eba6c5b839b7d.jpg",
            "review_count": 1890,
            "score": 4.89,
            "is_ad": False
        }
    ]
}


def get_cached_items() -> List[Dict[str, Any]]:
    """로컬 캐시 파일 또는 기본 데이터 반환"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    return DEFAULT_FALLBACK_ITEMS


def generate_mock_history(lowest_price: int, target_price: int) -> List[Dict[str, Any]]:
    """최근 30일간의 가격 변동 추이 데이터 동적 생성 (실제 최저가 비율 기반)"""
    history = []
    today = datetime.now()
    if lowest_price <= 0:
        lowest_price = 10000

    multipliers = [
        1.22, 1.20, 1.19, 1.21, 1.18, 1.17, 1.15, 1.16, 1.14, 1.15,
        1.12, 1.13, 1.10, 1.09, 1.08, 1.09, 1.07, 1.06, 1.05, 1.04,
        1.03, 1.04, 1.02, 1.03, 1.02, 1.01, 1.01, 1.005, 1.002, 1.0
    ]
    for i, m in enumerate(multipliers):
        date_str = (today - timedelta(days=29 - i)).strftime("%m/%d")
        history.append({
            "date": date_str,
            "price": round(lowest_price * m / 10) * 10,
            "target": target_price
        })
    return history


def extract_unit_count(title: str, keyword: str = "") -> int:
    """상품명(또는 검색어)에서 수량(20개, 30캔, 6입 등)을 자동 감지하여 정수로 반환"""
    import re
    for text in [title, keyword]:
        if not text:
            continue
        match = re.search(r'(\d+)\s*(개|봉|입|ea|캔|병|팩|box|박스|롤|t)', text.lower())
        if match:
            try:
                cnt = int(match.group(1))
                if 1 <= cnt <= 200:
                    return cnt
            except ValueError:
                pass
    return 1


# 인메모리 고속 검색 캐시 (키: 정규화된 검색어, 값: (캐시생성시각, 정제된 아이템 리스트))
SEARCH_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
CACHE_TTL_SECONDS: int = 600  # 10분간 유효


def fetch_price_data(keyword: str = "농심 신라면 봉지 20개입", target_price: int = 15000, force_refresh: bool = False) -> Dict[str, Any]:
    """네이버 쇼핑 및 다나와 실시간 크롤링 또는 안전 캐시 반환 (10분 인메모리 캐시 탑재)"""
    raw_items = []
    fetch_errors = []
    is_live = False
    norm_key = re.sub(r'\s+', ' ', keyword.strip().lower())

    # 1. 인메모리 캐시 확인 (강제 갱신이 아닌 경우 즉각 반환)
    if not force_refresh and norm_key in SEARCH_CACHE:
        cached_time, cached_items = SEARCH_CACHE[norm_key]
        if time.time() - cached_time < CACHE_TTL_SECONDS and cached_items:
            refined_items = cached_items
            is_live = True
        else:
            refined_items = []
    else:
        refined_items = []

    # 2. 캐시 미스 시 실시간 다나와 크롤러 가동
    if not refined_items:
        if pricetrace_bot:
            try:
                raw_items, fetch_errors = pricetrace_bot.default_data_fetcher(keyword)
                if raw_items:
                    is_live = True
            except Exception as e:
                fetch_errors.append(str(e))

        if raw_items and pricetrace_bot:
            refined_items = pricetrace_bot.filter_and_refine_products(raw_items, keyword)
        else:
            refined_items = []

        if refined_items:
            SEARCH_CACHE[norm_key] = (time.time(), refined_items)

    # 3. 크롤링 실패 시 16대 생필품 세이프티 풀 폴백
    if not refined_items:
        if "신라면" in keyword:
            refined_items = get_cached_items()
        else:
            for k, items in POOL_FALLBACK_DATA.items():
                if k in keyword:
                    refined_items = items
                    break

    if not refined_items:
        if "신라면" in keyword:
            refined_items = DEFAULT_FALLBACK_ITEMS
        else:
            return {
                "success": False,
                "is_live": is_live,
                "keyword": keyword,
                "target_price": target_price,
                "lowest_price": 0,
                "unit_price": 0,
                "unit_count": 1,
                "is_special_price": False,
                "discount_amount": 0,
                "alert_message": f"'{keyword}'에 대한 검색 결과가 없습니다.",
                "representative_item": {},
                "top_items": [],
                "item_count": 0,
                "fetch_errors": fetch_errors,
                "history": [],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    # 모든 아이템의 URL 정규화 보장 (n2 오류 원천 차단 및 로그인/캡차 우회)
    if pricetrace_bot:
        for it in refined_items:
            it["url"] = pricetrace_bot.normalize_shopping_url(it.get("url", ""), title=it.get("title", ""))

    top_items = refined_items[:3]
    lowest_price = top_items[0]["price"] if top_items else 0
    representative = top_items[0] if top_items else {}

    unit_cnt = extract_unit_count(representative.get("title", ""), keyword=keyword)
    unit_price = round(lowest_price / unit_cnt) if lowest_price > 0 else 0

    if target_price <= 0:
        target_price = round((lowest_price * 1.1) / 100) * 100

    is_special = lowest_price <= target_price
    discount = target_price - lowest_price if is_special else 0

    alert_msg = (
        f"🚨 [특가 발생] 목표 가격({target_price:,}원) 이하입니다!"
        if is_special
        else f"ℹ️ [유지] 아직 목표 가격({target_price:,}원)보다 비쌉니다."
    )

    return {
        "success": True,
        "is_live": is_live,
        "keyword": keyword,
        "target_price": target_price,
        "lowest_price": lowest_price,
        "unit_price": unit_price,
        "unit_count": unit_cnt,
        "is_special_price": is_special,
        "discount_amount": discount,
        "alert_message": alert_msg,
        "representative_item": representative,
        "top_items": top_items,
        "item_count": len(refined_items),
        "fetch_errors": fetch_errors,
        "history": generate_mock_history(lowest_price, target_price),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function 핸들러 클래스"""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # /api/ 접두사 처리
        refresh = params.get("refresh", ["false"])[0].lower() in ("true", "1", "yes")
        if path.endswith("/summary") or path == "/api/summary":
            target_price = int(params.get("target_price", [15000])[0])
            result = fetch_price_data(keyword="농심 신라면 봉지 20개입", target_price=target_price, force_refresh=refresh)
            self.send_json(result)
        elif path.endswith("/search") or path == "/api/search":
            keyword = params.get("q", ["농심 신라면 봉지 20개입"])[0]
            target_price = int(params.get("target_price", [15000])[0])
            result = fetch_price_data(keyword=keyword, target_price=target_price, force_refresh=refresh)
            self.send_json(result)
        elif path.endswith("/history") or path == "/api/history":
            lowest_price = int(params.get("price", [13200])[0])
            target_price = int(params.get("target", [15000])[0])
            history = generate_mock_history(lowest_price, target_price)
            self.send_json({"success": True, "history": history})
        elif path.endswith("/status") or path == "/api/status":
            status = {
                "status": "online",
                "platform": "Vercel Serverless Function",
                "bot_module_loaded": pricetrace_bot is not None,
                "timestamp": datetime.now().isoformat()
            }
            self.send_json(status)
        elif path.endswith("/trending") or path == "/api/trending":
            if pricetrace_bot and hasattr(pricetrace_bot, "fetch_daily_trending_products"):
                result = pricetrace_bot.fetch_daily_trending_products(force_refresh=refresh)
            else:
                result = {
                    "success": True,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "serverless_fallback",
                    "count": 0,
                    "items": []
                }
            self.send_json(result)
        else:
            # 기본 summary 반환
            result = fetch_price_data()
            self.send_json(result)

    def send_json(self, data: Any, status_code: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)
