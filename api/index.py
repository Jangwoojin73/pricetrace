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
import json
import urllib.parse
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any, List

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
        "url": "https://cr3.shopping.naver.com/v2/bridge/searchGate?nv_mid=53018889018",
        "review_count": 104069,
        "score": 4.88,
        "is_ad": False
    },
    {
        "title": "농심 신라면120g 20개 1박스",
        "price": 13200,
        "mall_name": "신성마켓몰",
        "url": "https://smartstore.naver.com/main/products/8676675032",
        "review_count": 715,
        "score": 4.88,
        "is_ad": False
    }
]


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


def extract_unit_count(title: str) -> int:
    """상품명에서 수량(20개, 30캔, 6입 등)을 자동 감지하여 정수로 반환"""
    import re
    match = re.search(r'(\d+)\s*(개|봉|입|ea|캔|병|팩|box|박스)', title.lower())
    if match:
        try:
            cnt = int(match.group(1))
            if 1 <= cnt <= 200:
                return cnt
        except ValueError:
            pass
    return 1


def fetch_price_data(keyword: str = "농심 신라면 봉지 20개입", target_price: int = 15000) -> Dict[str, Any]:
    """네이버 쇼핑 실시간 크롤링 또는 안전 캐시 반환"""
    raw_items = []
    fetch_errors = []
    is_live = False

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
        if "신라면" in keyword:
            refined_items = get_cached_items()
        else:
            refined_items = []

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

    top_items = refined_items[:3]
    lowest_price = top_items[0]["price"] if top_items else 0
    representative = top_items[0] if top_items else {}

    unit_cnt = extract_unit_count(representative.get("title", ""))
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
        if path.endswith("/summary") or path == "/api/summary":
            target_price = int(params.get("target_price", [15000])[0])
            result = fetch_price_data(keyword="농심 신라면 봉지 20개입", target_price=target_price)
            self.send_json(result)
        elif path.endswith("/search") or path == "/api/search":
            keyword = params.get("q", ["농심 신라면 봉지 20개입"])[0]
            target_price = int(params.get("target_price", [15000])[0])
            result = fetch_price_data(keyword=keyword, target_price=target_price)
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
