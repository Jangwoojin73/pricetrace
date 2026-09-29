#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py - PriceTrace WebApp 경량 API & 정적 파일 서빙 서버

주요 기능:
1. public/ 디렉토리의 정적 파일(index.html, style.css, app.js 등) HTTP 서빙
2. RESTful API 엔드포인트 제공:
   - GET /api/summary : 기본 타깃 상품(농심 신라면 20개입) 최저가 및 목표가 비교 데이터
   - GET /api/search?q={keyword}&target_price={price} : 실시간 검색 및 필터링
   - GET /api/history : 최근 30일 가격 변동 추이 데이터
   - GET /api/status : 서버 및 크롤러 상태 확인
3. 외부 의존성(pip) 없이 Python 3 내장 라이브러리만으로 동작
"""

import sys
import os
import io
import json
import urllib.parse
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, List, Optional

# Windows 콘솔 UTF-8 인코딩 보장
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 기존 pricetrace_bot 모듈 임포트
try:
    import pricetrace_bot
except ImportError:
    pricetrace_bot = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# 로컬 캐시 파일 경로
REFINED_CACHE_FILE = os.path.join(BASE_DIR, "refined_shinramyun_20.json")


def load_cached_fallback_data() -> List[Dict[str, Any]]:
    """네트워크 장애 시 로컬 캐시 데이터 반환"""
    if os.path.exists(REFINED_CACHE_FILE):
        try:
            with open(REFINED_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    # 하드코딩된 기본 안전 데이터
    return [
        {
            "title": "농심 신라면, 120g, 20개",
            "price": 13200,
            "mall": "네이버 가격비교 (카탈로그)",
            "mall_name": "네이버 가격비교 (카탈로그)",
            "url": "https://search.shopping.naver.com/search/all?query=%EB%86%8D%EC%8B%AC%20%EC%8B%A0%EB%9D%BC%EB%A9%B4%20120g%2020%EA%B0%9C",
            "review_count": 104064,
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
        },
        {
            "title": "농심 신라면 120g 20개 한박스",
            "price": 14500,
            "mall": "더싼 마트",
            "mall_name": "더싼 마트",
            "url": "https://m.smartstore.naver.com/main/products/11132243694",
            "review_count": 36,
            "score": 4.89,
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


def generate_mock_history(lowest_price: int, target_price: int) -> List[Dict[str, Any]]:
    """최근 30일간의 가격 변동 추이 데이터 동적 생성 (실제 최저가 비율 기반)"""
    history = []
    today = datetime.now()
    if lowest_price <= 0:
        lowest_price = 10000

    # 최저가 기준 +10% ~ +25% 변동 곡선 생성
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


def fetch_price_data(keyword: str = "농심 신라면 봉지 20개입", target_price: int = 15000) -> Dict[str, Any]:
    """실제 봇 모듈을 통해 검색어별 실시간 최저가 수집 및 가공"""
    raw_items = []
    fetch_errors = []
    is_live = False

    if pricetrace_bot:
        try:
            # 검색어를 넘겨 실시간 크롤링
            raw_items, fetch_errors = pricetrace_bot.default_data_fetcher(keyword)
            if raw_items:
                is_live = True
        except Exception as e:
            fetch_errors.append(str(e))

    if raw_items and pricetrace_bot:
        refined_items = pricetrace_bot.filter_and_refine_products(raw_items, keyword)
    else:
        refined_items = []

    if not refined_items:
        if "신라면" in keyword:
            refined_items = load_cached_fallback_data()
        else:
            for k, items in POOL_FALLBACK_DATA.items():
                if k in keyword:
                    refined_items = items
                    break

    # 결과가 전혀 없는 경우 안전 처리
    if not refined_items:
        # 검색 결과가 0건인 경우
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

    # 상품명 또는 검색어에서 수량 자동 감지하여 단위 가격 계산
    unit_cnt = extract_unit_count(representative.get("title", ""), keyword=keyword)
    unit_price = round(lowest_price / unit_cnt) if lowest_price > 0 else 0

    # 목표가 미지정(0 이하) 시 최저가의 110% 수준으로 자동 설정
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


class PriceTraceHandler(SimpleHTTPRequestHandler):
    """정적 파일 서빙 및 API 요청 처리 핸들러"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # 1. API: /api/summary
        if path == "/api/summary":
            self.handle_api_summary(params)
            return

        # 2. API: /api/search
        elif path == "/api/search":
            self.handle_api_search(params)
            return

        # 3. API: /api/history
        elif path == "/api/history":
            self.handle_api_history(params)
            return

        # 4. API: /api/status
        elif path == "/api/status":
            self.handle_api_status()
            return

        # 5. 정적 파일 서빙 (public/ 디렉토리 기준)
        return super().do_GET()

    def send_json_response(self, data: Any, status_code: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def handle_api_summary(self, params: Dict[str, List[str]]):
        target_price = int(params.get("target_price", [15000])[0])
        result = fetch_price_data(keyword="농심 신라면 봉지 20개입", target_price=target_price)
        self.send_json_response(result)

    def handle_api_search(self, params: Dict[str, List[str]]):
        keyword = params.get("q", ["농심 신라면 봉지 20개입"])[0]
        target_price = int(params.get("target_price", [15000])[0])
        result = fetch_price_data(keyword=keyword, target_price=target_price)
        self.send_json_response(result)

    def handle_api_history(self, params: Dict[str, List[str]]):
        lowest_price = int(params.get("price", [13200])[0])
        target_price = int(params.get("target", [15000])[0])
        history = generate_mock_history(lowest_price, target_price)
        self.send_json_response({"success": True, "history": history})

    def handle_api_status(self):
        status = {
            "status": "online",
            "service": "PriceTrace WebApp API",
            "bot_module_loaded": pricetrace_bot is not None,
            "public_dir_exists": os.path.exists(PUBLIC_DIR),
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(status)


def run_server(port: int = 8080):
    """서버 실행 함수"""
    if not os.path.exists(PUBLIC_DIR):
        os.makedirs(PUBLIC_DIR, exist_ok=True)

    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, PriceTraceHandler)
    print("=" * 68)
    print(f"🚀 [PriceTrace WebApp] 경량 웹 서버가 실행되었습니다!")
    print(f"👉 브라우저 접속 주소: http://localhost:{port}")
    print(f"📁 프론트엔드 경로   : {PUBLIC_DIR}")
    print(f"⚡ API 엔드포인트    : http://localhost:{port}/api/summary")
    print("=" * 68)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 서버를 종료합니다.")
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PriceTrace WebApp Server")
    parser.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")
    args = parser.parse_args()
    run_server(args.port)
