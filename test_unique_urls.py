#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import server

print("=== 1. 실시간 랭킹 품목 (미강 짤순이) 순위별 URL 검증 ===")
data1 = server.fetch_price_data("미강 다짜고짜 짤순이")
urls1 = []
for i, it in enumerate(data1.get("top_items", [])):
    rank = i + 1
    price = it.get("price")
    url = it.get("url")
    urls1.append(url)
    print(f"[{rank}위] 가격: {price:,}원 -> URL: {url}")

print(f"-> 1위, 2위, 3위 URL 중복 여부: {'중복 없음 (모두 다름)' if len(set(urls1)) == len(urls1) else '중복 발생 (오류)'}")

print("\n=== 2. 진라면 40개 순위별 URL 검증 ===")
data2 = server.fetch_price_data("진라면 40개")
urls2 = []
for i, it in enumerate(data2.get("top_items", [])):
    rank = i + 1
    price = it.get("price")
    url = it.get("url")
    urls2.append(url)
    print(f"[{rank}위] 가격: {price:,}원 -> URL: {url}")

print(f"-> 1위, 2위, 3위 URL 중복 여부: {'중복 없음 (모두 다름)' if len(set(urls2)) == len(urls2) else '중복 발생 (오류)'}")

print("\n=== 3. 일반 검색어 순위별 URL 검증 ===")
data3 = server.fetch_price_data("아이폰 16 케이스")
urls3 = []
for i, it in enumerate(data3.get("top_items", [])):
    rank = i + 1
    price = it.get("price")
    url = it.get("url")
    urls3.append(url)
    print(f"[{rank}위] 가격: {price:,}원 -> URL: {url}")

print(f"-> 1위, 2위, 3위 URL 중복 여부: {'중복 없음 (모두 다름)' if len(set(urls3)) == len(urls3) else '중복 발생 (오류)'}")
