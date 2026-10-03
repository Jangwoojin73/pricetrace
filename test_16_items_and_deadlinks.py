# -*- coding: utf-8 -*-
"""
test_16_items_and_deadlinks.py
전수 검증 스크립트:
1. 16대 국민 필수 생필품 NAVER_PRESET_ITEMS 전수 검사
   - 3개 이상 아이템
   - 유효 가격/타이틀/쇼핑몰
   - 1위~3위 순위별 100% 고유 URL 보장 (중복 절대 금지)
   - dead link (4915664157 등) 및 불안정한 /products/ 링크 0건
   - 오염된 파라미터(Adapter, 잔여 닫는 괄호 등) 0건
2. 오뚜기밥 최저가 링크(4915664157) 차단 및 51929535738 카탈로그 전환 검증
3. server.py 및 api/index.py fetch_price_data 1위~3위 TOP 3 순위 카드 보장 및 순위별 고유 URL 검증
4. 중첩 괄호 정제 헬퍼(clean_product_title) 검증
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pricetrace_bot
import server
import api.index as api_index

class TestPriceTraceFixes(unittest.TestCase):

    def test_clean_product_title(self):
        """중첩 괄호 및 브래킷 태그가 잔여 닫는 괄호 없이 완벽 정제되는지 검증"""
        sample1 = "아이폰 16 케이스 (네이버 스마트스토어 (공식인증))"
        self.assertEqual(pricetrace_bot.clean_product_title(sample1), "아이폰 16 케이스")

        sample2 = "[특가할인] 농심 신라면 120g 20개 (본사직영 [무료배송])"
        self.assertEqual(pricetrace_bot.clean_product_title(sample2), "농심 신라면 120g 20개")

        sample3 = "미강 다짜고짜 짤순이 )"
        self.assertEqual(pricetrace_bot.clean_product_title(sample3), "미강 다짜고짜 짤순이")

    def test_ottogi_dead_link_interception(self):
        """오뚜기밥 dead link 4915664157 및 otokimall 링크가 공식 안전 포털 쇼핑 탭으로 완벽 전환되는지 검증"""
        dead_url = "https://brand.naver.com/ottogimall/products/4915664157"
        normalized = pricetrace_bot.normalize_shopping_url(dead_url, title="오뚜기 맛있는 오뚜기밥 210g 24개", rank=1)
        self.assertTrue("where=shp" in normalized or "catalog/51929535738" in normalized)
        self.assertNotIn("4915664157", normalized)

        dead_url_sub = "https://brand.naver.com/otokimall/products/4915664158"
        normalized_sub = pricetrace_bot.normalize_shopping_url(dead_url_sub, title="오뚜기 맛있는 오뚜기밥 발아현미 210g 24개", rank=1)
        self.assertTrue("where=shp" in normalized_sub or "catalog/51929469998" in normalized_sub)

    def test_naver_preset_items_integrity(self):
        """16대 국민 필수 생필품 전수 검사: 3개 이상 품목, 고유 URL, 유효 가격, dead link 0건"""
        preset_items = pricetrace_bot.NAVER_PRESET_ITEMS
        self.assertGreaterEqual(len(preset_items), 16, f"Preset keys count: {len(preset_items)}")
        
        dead_signatures = ["4915664157", "4915664158", "4915664159", "otokimall"]

        for key, items in preset_items.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(items), 3, f"Item count for '{key}' must be at least 3, got {len(items)}")
                
                urls = []
                for idx, it in enumerate(items[:3], 1):
                    title = it.get("title", "")
                    price = it.get("price", 0)
                    url = it.get("url", "")
                    mall = it.get("mall_name") or it.get("mall") or ""

                    self.assertTrue(len(title) > 0, f"{key} rank {idx} title is empty")
                    self.assertGreater(price, 0, f"{key} rank {idx} price is invalid: {price}")
                    self.assertTrue(len(url) > 0, f"{key} rank {idx} url is empty")
                    self.assertTrue(len(mall) > 0, f"{key} rank {idx} mall name is empty")

                    for dead in dead_signatures:
                        self.assertNotIn(dead, url, f"Dead link '{dead}' found in {key} rank {idx}: {url}")

                    self.assertNotIn("Adapter", url, f"Corrupted query found in {key} rank {idx}: {url}")
                    self.assertNotIn("%29", url.split("?")[-1] if "?" in url else "", f"Dangling parenthesis found in {key} rank {idx}: {url}")

                    # URL은 공식 카탈로그(catalog/...) 또는 가격비교 검색(frm=NVSCPRO 또는 where=shp)이어야 함
                    valid_url_type = ("/catalog/" in url and not "/catalog/8" in url) or ("frm=NVSCPRO" in url) or ("where=shp" in url)
                    self.assertTrue(valid_url_type, f"Invalid URL structure for {key} rank {idx}: {url}")
                    urls.append(url)

                # 1위, 2위, 3위 카드의 구매 링크는 100% 서로 달라야 함 (중복 금지)
                self.assertEqual(len(set(urls)), len(urls), f"Duplicate URLs found in {key}: {urls}")

    def test_server_fetch_price_data_padding(self):
        """server.py fetch_price_data가 모든 프리셋 및 임의 검색어에 대해 top_items 3개 및 고유 URL을 보장하는지 검증"""
        test_queries = [
            "오뚜기 맛있는 오뚜기밥 210g 24개",
            "농심 신라면 봉지 20개입",
            "CJ제일제당 햇반 210g 24개",
            "코카콜라 제로 355ml 24캔",
            "제주 삼다수 2L 6개",
            "오뚜기 진라면 매운맛 40개",
            "맥심 모카골드 마일드 160T",
            "크리넥스 3겹 데코소프트 30롤",
            "동원 참치 살코기 135g 10캔",
            "스팸 클래식 200g 10캔",
            "퍼실 딥클린 파워젤 2.7L",
            "P&G 다우니 섬유유연제 1L 3개",
            "페브리즈 공기탈취제 상쾌한향 4개",
            "베베숲 시그니처 물티슈 70매 10팩",
            "칠성사이다 제로 355ml 24캔",
            "농심 안성탕면 20개입",
            "미강 다짜고짜 짤순이",
            "희귀상품_단일결과_테스트"
        ]

        for q in test_queries:
            with self.subTest(query=q):
                res = server.fetch_price_data(q, force_refresh=False)
                self.assertTrue(res.get("success"), f"Query '{q}' failed")
                top_items = res.get("top_items", [])
                self.assertEqual(len(top_items), 3, f"Query '{q}' top_items count is {len(top_items)}, expected 3")
                
                urls = []
                for it in top_items:
                    self.assertGreater(it.get("price", 0), 0)
                    u = it.get("url", "")
                    self.assertTrue(u)
                    self.assertNotIn("4915664157", u)
                    self.assertNotIn("Adapter", u)
                    urls.append(u)
                
                # 3개 순위 카드 고유 링크 검증
                self.assertEqual(len(set(urls)), 3, f"Query '{q}' rank cards must have 3 unique URLs, got: {urls}")

    def test_api_index_fetch_price_data_padding(self):
        """api/index.py fetch_price_data가 top_items 3개 및 고유 URL을 보장하는지 검증"""
        for q in ["오뚜기밥", "신라면", "희귀임의상품", "미강 다짜고짜 짤순이"]:
            with self.subTest(query=q):
                res = api_index.fetch_price_data(q, force_refresh=False)
                self.assertTrue(res.get("success"), f"Query '{q}' failed in api/index")
                top_items = res.get("top_items", [])
                self.assertEqual(len(top_items), 3, f"Query '{q}' top_items count is {len(top_items)}, expected 3 in api/index")
                
                urls = [it.get("url") for it in top_items]
                self.assertEqual(len(set(urls)), 3, f"Query '{q}' in api/index must have 3 unique URLs, got: {urls}")

if __name__ == "__main__":
    unittest.main()
