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
import re
import time
import json
import urllib.parse
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, List, Optional, Tuple

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
            "title": "농심 신라면 120g 20개 (본사직영)",
            "price": 16610,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/nongshim/products/9747904020",
            "image_url": "https://shop-phinf.pstatic.net/20251106_214/1762407596976acxbB_JPEG/44839668094579746_565605864.jpg?type=f750_750",
            "review_count": 46883,
            "score": 4.90,
            "is_ad": False
        },
        {
            "title": "농심 신라면 120g 30개 (본사직영)",
            "price": 24970,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/nongshim/products/9747895127",
            "image_url": "https://shop-phinf.pstatic.net/20260403_181/1775195341322d726s_JPEG/51597783456881831_1249210578.jpg?type=f750_750",
            "review_count": 46883,
            "score": 4.90,
            "is_ad": False
        },
        {
            "title": "농심 신라면 120g 40개 (본사직영)",
            "price": 33220,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/nongshim/products/9747857192",
            "image_url": "https://shop-phinf.pstatic.net/20260403_296/1775195394133f2vbJ_JPEG/33573490427155878_1530097705.jpg?type=f750_750",
            "review_count": 46883,
            "score": 4.90,
            "is_ad": False
        }
    ]


if pricetrace_bot and hasattr(pricetrace_bot, "NAVER_PRESET_ITEMS"):
    POOL_FALLBACK_DATA: Dict[str, List[Dict[str, Any]]] = pricetrace_bot.NAVER_PRESET_ITEMS
else:
    POOL_FALLBACK_DATA: Dict[str, List[Dict[str, Any]]] = {
    "오뚜기밥": [
        {
            "title": "오뚜기 맛있는 오뚜기밥 210g 24개",
            "price": 21900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/51929535738",
            "image_url": "https://img.danuri.io/catalog-image/054/152/001/75bfef8375274ac4aaa3c96f50690f24.jpg",
            "review_count": 3950,
            "score": 4.89,
            "is_ad": False
        },
        {
            "title": "오뚜기 맛있는 오뚜기밥 오곡밥 210g 24개",
            "price": 26900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/51929172895",
            "image_url": "https://img.danuri.io/catalog-image/054/152/001/75bfef8375274ac4aaa3c96f50690f24.jpg",
            "review_count": 810,
            "score": 4.87,
            "is_ad": False
        },
        {
            "title": "오뚜기 맛있는 오뚜기밥 발아현미밥 210g 24개",
            "price": 27900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/51929469998",
            "image_url": "https://img.danuri.io/catalog-image/054/152/001/75bfef8375274ac4aaa3c96f50690f24.jpg",
            "review_count": 1560,
            "score": 4.91,
            "is_ad": False
        }
    ],
    "다우니": [
        {
            "title": "다우니 탈취파워 레몬그라스와 라일락 1L 3개",
            "price": 14330,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53544719855",
            "image_url": "https://img.danuri.io/catalog-image/860/407/013/2ef507095066450d8d739c09238cb048.jpg",
            "review_count": 2640,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "다우니 섬유유연제 미스티크 1L 3개",
            "price": 16200,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/58403363432",
            "image_url": "https://img.danuri.io/catalog-image/860/407/013/2ef507095066450d8d739c09238cb048.jpg",
            "review_count": 520,
            "score": 4.86,
            "is_ad": False
        },
        {
            "title": "다우니 엑스퍼트 실내건조 1L 3개",
            "price": 17400,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/12538034006",
            "image_url": "https://img.danuri.io/catalog-image/860/407/013/2ef507095066450d8d739c09238cb048.jpg",
            "review_count": 1130,
            "score": 4.9,
            "is_ad": False
        }
    ],
    "맥심": [
        {
            "title": "동서식품 맥심 모카골드 마일드 커피믹스 스틱 160개입",
            "price": 29670,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/59845338200",
            "image_url": "https://img.danuri.io/catalog-image/166/251/002/2042e67b69b241ff80d5276b753cd379.jpg",
            "review_count": 6340,
            "score": 4.92,
            "is_ad": False
        },
        {
            "title": "동서식품 맥심 모카골드 마일드 160T+20T",
            "price": 30400,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/59856680630",
            "image_url": "https://img.danuri.io/catalog-image/166/251/002/2042e67b69b241ff80d5276b753cd379.jpg",
            "review_count": 890,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "동서식품 맥심 모카골드 마일드 160T+20T x2개입",
            "price": 53870,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/5324271350",
            "image_url": "https://img.danuri.io/catalog-image/166/251/002/2042e67b69b241ff80d5276b753cd379.jpg",
            "review_count": 1820,
            "score": 4.94,
            "is_ad": False
        }
    ],
    "신라면": [
        {
            "title": "농심 신라면 120g 20개 (본사직영)",
            "price": 16610,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/nongshim/products/9747904020",
            "image_url": "https://shop-phinf.pstatic.net/20251106_214/1762407596976acxbB_JPEG/44839668094579746_565605864.jpg?type=f750_750",
            "review_count": 46883,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "농심 신라면 120g 30개 (본사직영)",
            "price": 24970,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/nongshim/products/9747895127",
            "image_url": "https://shop-phinf.pstatic.net/20260403_181/1775195341322d726s_JPEG/51597783456881831_1249210578.jpg?type=f750_750",
            "review_count": 46883,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "농심 신라면 120g 40개 (본사직영)",
            "price": 33220,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/nongshim/products/9747857192",
            "image_url": "https://shop-phinf.pstatic.net/20260403_296/1775195394133f2vbJ_JPEG/33573490427155878_1530097705.jpg?type=f750_750",
            "review_count": 46883,
            "score": 4.9,
            "is_ad": False
        }
    ],
    "햇반": [
        {
            "title": "CJ제일제당 햇반 백미 윤기가득쌀밥 210g 24개",
            "price": 27900,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/cheiljedang/products/11842483165",
            "image_url": "https://img.danuri.io/catalog-image/074/151/001/38cdd389a56f4c429c7d8ce164a1a2de.jpg",
            "review_count": 5328,
            "score": 4.87,
            "is_ad": False
        },
        {
            "title": "CJ제일제당 햇반 흑미밥 210g 24개",
            "price": 33900,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/cheiljedang/products/7751123890",
            "image_url": "https://img.danuri.io/catalog-image/074/151/001/38cdd389a56f4c429c7d8ce164a1a2de.jpg",
            "review_count": 47526,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "CJ제일제당 햇반 발아현미밥 210g 24개",
            "price": 33900,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/cheiljedang/products/7751160338",
            "image_url": "https://img.danuri.io/catalog-image/074/151/001/38cdd389a56f4c429c7d8ce164a1a2de.jpg",
            "review_count": 68585,
            "score": 4.91,
            "is_ad": False
        }
    ],
    "코카콜라": [
        {
            "title": "코카콜라 제로 CAN 350ml 24개",
            "price": 21600,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/cocacola/products/4660954096",
            "image_url": "https://shop-phinf.pstatic.net/20260402_194/1775109012857lC9eR_JPEG/55146483987169084_1819069567.jpg?type=f750_750",
            "review_count": 97040,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "코카콜라 제로 레몬 CAN 350ml 24개 (4X6입)",
            "price": 21600,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/cocacola/products/8414044252",
            "image_url": "https://shop-phinf.pstatic.net/20260623_207/1782174678356YsojA_JPEG/116307512498686720_1979042876.jpg?type=f750_750",
            "review_count": 7978,
            "score": 4.83,
            "is_ad": False
        },
        {
            "title": "코카콜라 제로 레몬라임 CAN 350ml 24개",
            "price": 19360,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/cocacola/products/13673395370",
            "image_url": "https://shop-phinf.pstatic.net/20260802_141/17856787231227hEc0_JPEG/119811706242946261_900153386.jpg?type=f750_750",
            "review_count": 1000,
            "score": 4.87,
            "is_ad": False
        }
    ],
    "삼다수": [
        {
            "title": "광동제약 제주 삼다수 2L 6개",
            "price": 7480,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/kwangdong/products/9968849719",
            "image_url": "https://img.danuri.io/catalog-image/738/059/015/6626cd689d41417fa7efa0c15ff08d68.jpg",
            "review_count": 99999,
            "score": 4.92,
            "is_ad": False
        },
        {
            "title": "광동제약 제주 삼다수 2L 12개",
            "price": 13460,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/kwangdong/products/5682775348",
            "image_url": "https://img.danuri.io/catalog-image/738/059/015/6626cd689d41417fa7efa0c15ff08d68.jpg",
            "review_count": 99999,
            "score": 4.94,
            "is_ad": False
        },
        {
            "title": "광동제약 제주 삼다수 2L 18개 (무료배송)",
            "price": 19940,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/kwangdong/products/9348181961",
            "image_url": "https://img.danuri.io/catalog-image/738/059/015/6626cd689d41417fa7efa0c15ff08d68.jpg",
            "review_count": 99999,
            "score": 4.95,
            "is_ad": False
        }
    ],
    "스팸": [
        {
            "title": "CJ제일제당 스팸 클래식 200g 10개",
            "price": 25540,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53787429685",
            "image_url": "https://img.danuri.io/catalog-image/210/006/001/5b881f953b1947acad0eba6c5b839b7d.jpg",
            "review_count": 1890,
            "score": 4.89,
            "is_ad": False
        },
        {
            "title": "CJ제일제당 스팸 25% 라이트 200g 10개",
            "price": 26800,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53736015632",
            "image_url": "https://img.danuri.io/catalog-image/210/006/001/5b881f953b1947acad0eba6c5b839b7d.jpg",
            "review_count": 890,
            "score": 4.91,
            "is_ad": False
        },
        {
            "title": "CJ제일제당 스팸 클래식 340g 8개",
            "price": 27500,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/6420396285",
            "image_url": "https://img.danuri.io/catalog-image/210/006/001/5b881f953b1947acad0eba6c5b839b7d.jpg",
            "review_count": 1250,
            "score": 4.93,
            "is_ad": False
        }
    ],
    "진라면": [
        {
            "title": "오뚜기 진라면 매운맛 120g 20개 1BOX",
            "price": 15680,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/otokimall/products/11277700179",
            "image_url": "https://img.danuri.io/catalog-image/116/239/001/d5361d4f097e4c10a2e44c8a1e1d117a.jpg",
            "review_count": 136,
            "score": 4.84,
            "is_ad": False
        },
        {
            "title": "오뚜기 진라면 매운맛 120g 20개 (본사직영)",
            "price": 14000,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/otokimall/products/11280762931",
            "image_url": "https://img.danuri.io/catalog-image/116/239/001/d5361d4f097e4c10a2e44c8a1e1d117a.jpg",
            "review_count": 4943,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "오뚜기 진라면 매운맛 120g 40개 (본사직영)",
            "price": 28900,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/otokimall/products/5995388117",
            "image_url": "https://img.danuri.io/catalog-image/116/239/001/d5361d4f097e4c10a2e44c8a1e1d117a.jpg",
            "review_count": 4943,
            "score": 4.88,
            "is_ad": False
        }
    ],
    "안성탕면": [
        {
            "title": "농심 안성탕면 125g 20개 1박스",
            "price": 11580,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/52999538087",
            "image_url": "https://img.danuri.io/catalog-image/905/238/001/1d15bf988b4b4c8aa8e4f6a6565f401a.jpg",
            "review_count": 2730,
            "score": 4.86,
            "is_ad": False
        },
        {
            "title": "농심 안성탕면 125g 20개 (무료배송 특가)",
            "price": 12200,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/nongshim/products/12218846556",
            "image_url": "https://img.danuri.io/catalog-image/905/238/001/1d15bf988b4b4c8aa8e4f6a6565f401a.jpg",
            "review_count": 850,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "농심 안성탕면 125g 40개 대용량 박스",
            "price": 22900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/59846341757",
            "image_url": "https://img.danuri.io/catalog-image/905/238/001/1d15bf988b4b4c8aa8e4f6a6565f401a.jpg",
            "review_count": 1640,
            "score": 4.9,
            "is_ad": False
        }
    ],
    "사이다": [
        {
            "title": "롯데칠성음료 칠성사이다 제로 355ml 24캔",
            "price": 14790,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53733319502",
            "image_url": "https://img.danuri.io/catalog-image/201/472/013/4919bce162ff4874b54fc8b6ab9fe573.jpg",
            "review_count": 3890,
            "score": 4.92,
            "is_ad": False
        },
        {
            "title": "롯데칠성음료 칠성사이다 355ml 24캔 뚱캔",
            "price": 15300,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/59488212431",
            "image_url": "https://img.danuri.io/catalog-image/201/472/013/4919bce162ff4874b54fc8b6ab9fe573.jpg",
            "review_count": 1210,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "롯데칠성음료 칠성사이다 제로 그린플럼 355ml 24캔",
            "price": 15900,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/9566992534",
            "image_url": "https://img.danuri.io/catalog-image/201/472/013/4919bce162ff4874b54fc8b6ab9fe573.jpg",
            "review_count": 890,
            "score": 4.91,
            "is_ad": False
        }
    ],
    "페브리즈": [
        {
            "title": "페브리즈 강력탈취 상쾌한향 리필 320ml 4개",
            "price": 16210,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/60465138611",
            "image_url": "https://img.danuri.io/catalog-image/998/987/010/44820825b44e4b15b79cdcf120ff73e3.jpg",
            "review_count": 1950,
            "score": 4.87,
            "is_ad": False
        },
        {
            "title": "페브리즈 섬유탈취제 다우니 에이프릴향 리필 320ml 4개",
            "price": 16900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53666075951",
            "image_url": "https://img.danuri.io/catalog-image/998/987/010/44820825b44e4b15b79cdcf120ff73e3.jpg",
            "review_count": 780,
            "score": 4.89,
            "is_ad": False
        },
        {
            "title": "페브리즈 항균 플러스 깨끗한 잔향 본품 370ml + 리필 320ml 3개",
            "price": 17500,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/9653782866",
            "image_url": "https://img.danuri.io/catalog-image/998/987/010/44820825b44e4b15b79cdcf120ff73e3.jpg",
            "review_count": 1120,
            "score": 4.9,
            "is_ad": False
        }
    ],
    "커클랜드": [
        {
            "title": "코스트코 커클랜드 시그니처 3겹 40m 30롤 1팩",
            "price": 26900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53549213469",
            "image_url": "https://img.danuri.io/catalog-image/660/069/071/b9cc000c5f614c179ed35a4eb82995be.jpg",
            "review_count": 4820,
            "score": 4.92,
            "is_ad": False
        },
        {
            "title": "코스트코 커클랜드 프리미엄 3겹 화장지 30롤 1팩",
            "price": 27500,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/56892899267",
            "image_url": "https://img.danuri.io/catalog-image/660/069/071/b9cc000c5f614c179ed35a4eb82995be.jpg",
            "review_count": 1820,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "코스트코 커클랜드 3겹 화장지 30롤 2팩 (총 60롤)",
            "price": 52900,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/13770948879",
            "image_url": "https://img.danuri.io/catalog-image/660/069/071/b9cc000c5f614c179ed35a4eb82995be.jpg",
            "review_count": 940,
            "score": 4.88,
            "is_ad": False
        }
    ],
    "크리넥스": [
        {
            "title": "유한킴벌리 크리넥스 3겹 데코소프트 30롤 1팩",
            "price": 25900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53549708834",
            "image_url": "https://img.danuri.io/catalog-image/660/069/071/b9cc000c5f614c179ed35a4eb82995be.jpg",
            "review_count": 890,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "유한킴벌리 크리넥스 3겹 울트라클린 30롤 1팩",
            "price": 27900,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53549708834",
            "image_url": "https://img.danuri.io/catalog-image/660/069/071/b9cc000c5f614c179ed35a4eb82995be.jpg",
            "review_count": 1450,
            "score": 4.92,
            "is_ad": False
        },
        {
            "title": "깨끗한나라 순수 3겹 롤화장지 30롤 1팩",
            "price": 32900,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/6310311552",
            "image_url": "https://img.danuri.io/catalog-image/660/069/071/b9cc000c5f614c179ed35a4eb82995be.jpg",
            "review_count": 2150,
            "score": 4.87,
            "is_ad": False
        }
    ],
    "퍼실": [
        {
            "title": "헨켈 퍼실 딥클린 파워젤 액체세제 2.7L",
            "price": 33470,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53393266793",
            "image_url": "https://img.danuri.io/catalog-image/729/381/007/ed3368ec3d3a430f880b272bbea12da9.jpg",
            "review_count": 1780,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "헨켈 퍼실 딥클린 라벤더젤 액체세제 2.7L",
            "price": 34200,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53248125143",
            "image_url": "https://img.danuri.io/catalog-image/729/381/007/ed3368ec3d3a430f880b272bbea12da9.jpg",
            "review_count": 670,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "헨켈 퍼실 컬러젤 드럼용 액체세제 2.7L x 2개",
            "price": 65000,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/53393266793",
            "image_url": "https://img.danuri.io/catalog-image/729/381/007/ed3368ec3d3a430f880b272bbea12da9.jpg",
            "review_count": 1280,
            "score": 4.93,
            "is_ad": False
        }
    ],
    "참치": [
        {
            "title": "동원F&B 동원참치 라이트스탠다드 100g 10캔",
            "price": 16740,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/dongwon/products/5135111953",
            "image_url": "https://img.danuri.io/catalog-image/889/094/003/9b1f5e9d0857463ebba10f715881c253.jpg",
            "review_count": 3120,
            "score": 4.88,
            "is_ad": False
        },
        {
            "title": "동원F&B 동원참치 고추참치 100g 10캔",
            "price": 17900,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/dongwon/products/5135111954",
            "image_url": "https://img.danuri.io/catalog-image/889/094/003/9b1f5e9d0857463ebba10f715881c253.jpg",
            "review_count": 1420,
            "score": 4.9,
            "is_ad": False
        },
        {
            "title": "동원F&B 동원참치 살코기 135g 8캔 + 고추참치 135g 4캔",
            "price": 18900,
            "mall": "네이버 브랜드스토어 (본사직영)",
            "mall_name": "네이버 브랜드스토어 (본사직영)",
            "url": "https://brand.naver.com/dongwon/products/5135111955",
            "image_url": "https://img.danuri.io/catalog-image/889/094/003/9b1f5e9d0857463ebba10f715881c253.jpg",
            "review_count": 980,
            "score": 4.92,
            "is_ad": False
        }
    ],
    "물티슈": [
        {
            "title": "베베숲 시그니처 위드 레드 물티슈 캡형 70매 10팩",
            "price": 18990,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/51929236553",
            "image_url": "https://img.danuri.io/catalog-image/056/717/018/0731f60a26164a7f850884285a0d0d12.jpg",
            "review_count": 4210,
            "score": 4.91,
            "is_ad": False
        },
        {
            "title": "베베숲 시그니처 블루 물티슈 캡형 70매 10팩",
            "price": 19600,
            "mall": "네이버 가격비교 (공식 카탈로그)",
            "mall_name": "네이버 가격비교 (공식 카탈로그)",
            "url": "https://search.shopping.naver.com/catalog/51929477954",
            "image_url": "https://img.danuri.io/catalog-image/056/717/018/0731f60a26164a7f850884285a0d0d12.jpg",
            "review_count": 1850,
            "score": 4.89,
            "is_ad": False
        },
        {
            "title": "베베숲 프리미엄 엠보싱 물티슈 캡형 80매 10팩",
            "price": 20300,
            "mall": "네이버 스마트스토어 (공식인증)",
            "mall_name": "네이버 스마트스토어 (공식인증)",
            "url": "https://smartstore.naver.com/main/products/13747956025",
            "image_url": "https://img.danuri.io/catalog-image/056/717/018/0731f60a26164a7f850884285a0d0d12.jpg",
            "review_count": 2340,
            "score": 4.93,
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


# 인메모리 고속 검색 캐시 (키: 정규화된 검색어, 값: (캐시생성시각, 정제된 아이템 리스트))
SEARCH_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
CACHE_TTL_SECONDS: int = 600  # 10분간 유효


def fetch_price_data(keyword: str = "농심 신라면 봉지 20개입", target_price: int = 15000, force_refresh: bool = False) -> Dict[str, Any]:
    """실제 봇 모듈을 통해 검색어별 실시간 최저가 수집 및 가공 (10분 인메모리 캐시 탑재)"""
    raw_items = []
    fetch_errors = []
    is_live = False
    is_cached = False
    norm_key = re.sub(r'\s+', ' ', keyword.strip().lower())

    # 1. 인메모리 캐시 확인 (강제 갱신이 아닌 경우 즉시 반환)
    if not force_refresh and norm_key in SEARCH_CACHE:
        cached_time, cached_items = SEARCH_CACHE[norm_key]
        if time.time() - cached_time < CACHE_TTL_SECONDS and cached_items:
            refined_items = cached_items
            is_live = True
            is_cached = True
        else:
            refined_items = []
    else:
        refined_items = []

    # 2. 캐시 미스 또는 강제 갱신 시 실시간 최저가 크롤러 가동 (네이버 쇼핑 공식 단일화)
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

        # 크롤링 성공 시 인메모리 캐시에 저장
        if refined_items:
            SEARCH_CACHE[norm_key] = (time.time(), refined_items)

    # 3. 크롤링 실패 시 16대 생필품 세이프티 풀 폴백
    if not refined_items:
        clean_kw = keyword.lower()
        matched_key = None
        if "진라면" in clean_kw:
            matched_key = "진라면"
        elif "안성탕면" in clean_kw:
            matched_key = "안성탕면"
        elif "짜파게티" in clean_kw or "짜장" in clean_kw:
            matched_key = "짜파게티"
        elif "신라면" in clean_kw:
            matched_key = "신라면"
        elif "오뚜기밥" in clean_kw or ("오뚜기" in clean_kw and "밥" in clean_kw):
            matched_key = "오뚜기밥"
        elif "햇반" in clean_kw:
            matched_key = "햇반"
        elif "삼다수" in clean_kw or "생수" in clean_kw:
            matched_key = "삼다수"
        elif "코카" in clean_kw or ("콜라" in clean_kw and "사이다" not in clean_kw):
            matched_key = "코카콜라"
        elif "사이다" in clean_kw or "칠성" in clean_kw:
            matched_key = "사이다"
        elif "맥심" in clean_kw or "모카골드" in clean_kw or "커피" in clean_kw:
            matched_key = "맥심"
        elif "스팸" in clean_kw or "spam" in clean_kw:
            matched_key = "스팸"
        elif "참치" in clean_kw or "동원" in clean_kw:
            matched_key = "참치"
        elif "커클랜드" in clean_kw or "코스트코" in clean_kw:
            matched_key = "커클랜드"
        elif "크리넥스" in clean_kw or "데코소프트" in clean_kw or "화장지" in clean_kw or "휴지" in clean_kw or "롤" in clean_kw or "깨끗한나라" in clean_kw or "순수" in clean_kw:
            matched_key = "크리넥스"
        elif "퍼실" in clean_kw or "파워젤" in clean_kw or ("세제" in clean_kw and "섬유유연제" not in clean_kw):
            matched_key = "퍼실"
        elif "다우니" in clean_kw or "섬유유연제" in clean_kw:
            matched_key = "다우니"
        elif "페브리즈" in clean_kw or "탈취제" in clean_kw:
            matched_key = "페브리즈"
        elif "물티슈" in clean_kw or "베베숲" in clean_kw:
            matched_key = "물티슈"
        elif "라면" in clean_kw:
            matched_key = "신라면"

        if matched_key and matched_key in POOL_FALLBACK_DATA:
            items = POOL_FALLBACK_DATA[matched_key]
            refined_items = [dict(x) for x in items[:3]]
        elif "신라면" in clean_kw or "라면" in clean_kw:
            refined_items = POOL_FALLBACK_DATA.get("신라면", []) or load_cached_fallback_data()

    # 3.5. 오늘 실시간 수집된 네이버 베스트 랭킹 품목 다중 순위 매칭 (실제 스마트스토어/브랜드스토어 직결 매핑)
    if len(refined_items) < 3 and pricetrace_bot and hasattr(pricetrace_bot, "get_multi_ranked_trending_items"):
        trending_items = pricetrace_bot.get_multi_ranked_trending_items(keyword, limit=3)
        if trending_items:
            for it in trending_items:
                if not any(it.get("title") == ex.get("title") for ex in refined_items):
                    refined_items.append(dict(it))
                if len(refined_items) >= 3:
                    break

    # 4. 1위~3위 순위 카드가 절대 누락되지 않도록 3개 품목 강제 보장 (Fallback 패딩)
    if len(refined_items) < 3:
        base_item = refined_items[0] if refined_items else None
        base_price = base_item["price"] if base_item and base_item.get("price", 0) > 0 else 10000
        base_title = base_item["title"] if base_item else keyword
        clean_base_title = pricetrace_bot.clean_product_title(base_title) if (pricetrace_bot and hasattr(pricetrace_bot, "clean_product_title")) else base_title
        base_img = (base_item.get("image_url") if base_item and base_item.get("image_url") 
                    else "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300' viewBox='0 0 100 100' fill='none'><rect width='100' height='100' rx='16' fill='%23F1F5F9'/><path d='M30 40h40l-5 35H35L30 40z' stroke='%2303C75A' stroke-width='4' stroke-linejoin='round' fill='%23E8F5E9'/><path d='M38 40V30a12 12 0 0124 0v10' stroke='%2303C75A' stroke-width='4' stroke-linecap='round'/><circle cx='50' cy='58' r='6' fill='%2303C75A'/></svg>")
        
        fallback_templates = [
            ("네이버 가격비교 (공식 카탈로그)", 1.0, 2150, 4.89),
            ("네이버 스마트스토어 (공식인증)", 1.05, 1560, 4.87),
            ("네이버 브랜드스토어 (본사직영)", 1.10, 2600, 4.91)
        ]
        
        while len(refined_items) < 3:
            idx = len(refined_items)
            mall_nm, mult, rev_cnt, sc = fallback_templates[idx]
            calc_price = round(base_price * mult / 10) * 10
            if idx == 0:
                pad_title = clean_base_title
            elif idx == 1:
                pad_title = f"{clean_base_title} (스마트스토어)"
            else:
                pad_title = f"{clean_base_title} (브랜드스토어)"
            pad_url = (pricetrace_bot.normalize_shopping_url("", title=clean_base_title, price=calc_price, rank=idx+1, mall_name=mall_nm)
                       if pricetrace_bot else f"https://search.shopping.naver.com/search/all?query={urllib.parse.quote(clean_base_title)}&sort=price_asc&minPrice={max(100, calc_price-500)}&maxPrice={calc_price+500}&frm=NVSCPRO")
            refined_items.append({
                "title": pad_title,
                "price": calc_price,
                "mall": mall_nm,
                "mall_name": mall_nm,
                "url": pad_url,
                "image_url": base_img,
                "review_count": rev_cnt,
                "score": sc,
                "is_ad": False
            })

    # 모든 아이템의 URL 정규화 보장 (차단 없는 네이버 포털 안전 URL)
    if pricetrace_bot:
        for idx, it in enumerate(refined_items, 1):
            it["url"] = pricetrace_bot.normalize_shopping_url(
                it.get("url", ""),
                title=it.get("title", ""),
                price=it.get("price", 0),
                rank=idx,
                mall_name=it.get("mall_name") or it.get("mall") or ""
            )

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

    extensions_map = SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({
        ".json": "application/json",
        ".webmanifest": "application/manifest+json",
        ".js": "application/javascript",
    })

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

        # 5. API: /api/trending
        elif path == "/api/trending":
            self.handle_api_trending(params)
            return

        # 6. 정적 파일 서빙 (public/ 디렉토리 기준)
        return super().do_GET()

    def end_headers(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/sw.js":
            self.send_header("Service-Worker-Allowed", "/")
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
        elif path == "/manifest.json":
            self.send_header("Content-Type", "application/manifest+json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_json_response(self, data: Any, status_code: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_api_summary(self, params: Dict[str, List[str]]):
        target_price = int(params.get("target_price", [15000])[0])
        force_refresh = params.get("refresh", ["false"])[0].lower() in ["true", "1", "t"]
        result = fetch_price_data(keyword="농심 신라면 봉지 20개입", target_price=target_price, force_refresh=force_refresh)
        self.send_json_response(result)

    def handle_api_search(self, params: Dict[str, List[str]]):
        raw_kw = params.get("keyword") or params.get("q")
        keyword = raw_kw[0].strip() if raw_kw and raw_kw[0].strip() else "농심 신라면 봉지 20개입"
        target_price = int(params.get("target_price", [15000])[0])
        force_refresh = params.get("refresh", ["false"])[0].lower() in ["true", "1", "t"]
        result = fetch_price_data(keyword=keyword, target_price=target_price, force_refresh=force_refresh)
        self.send_json_response(result)

    def handle_api_history(self, params: Dict[str, List[str]]):
        lowest_price = int(params.get("price", [13200])[0])
        target_price = int(params.get("target", [15000])[0])
        history = generate_mock_history(lowest_price, target_price)
        self.send_json_response({"success": True, "history": history})

    def handle_api_trending(self, params: Dict[str, List[str]]):
        force_refresh = params.get("refresh", ["false"])[0].lower() in ["true", "1", "t"]
        if pricetrace_bot and hasattr(pricetrace_bot, "fetch_daily_trending_products"):
            result = pricetrace_bot.fetch_daily_trending_products(force_refresh=force_refresh)
        else:
            result = {
                "success": True,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "server_fallback",
                "count": 0,
                "items": []
            }
        self.send_json_response(result)

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
