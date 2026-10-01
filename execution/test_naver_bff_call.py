# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json

def test_bff():
    keyword = "코카콜라 제로 355ml 24캔"
    encoded_query = urllib.parse.quote(keyword)
    url = f"https://ns-portal.shopping.naver.com/api/v2/shopping-paged-slot?query={encoded_query}&source=shp_gui"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://shopping.naver.com/"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("BFF Success! Keys:", list(data.keys()))
            items = []
            for slot in data.get("slots", []):
                for card in slot.get("cards", []):
                    item = card.get("item", {})
                    if item:
                        items.append(item)
            print(f"Total items found: {len(items)}")
            for i, it in enumerate(items[:5]):
                title = it.get("productTitle", "") or it.get("name", "")
                price = it.get("lowPrice", "") or it.get("price", "")
                mall = it.get("mallName", "")
                nv_mid = it.get("id", "") or it.get("nvMid", "")
                cr_url = it.get("crUrl", "")
                mall_pid = it.get("mallPid", "")
                channel = it.get("channel", {})
                is_catalog = it.get("isCatalog", False) or it.get("productType", "") == "CATALOG"
                print(f"[{i+1}] Title: {title} | Price: {price} | Mall: {mall} | ID: {nv_mid} | isCatalog: {is_catalog} | crUrl: {cr_url[:50] if cr_url else 'None'}")
    except Exception as e:
        print("BFF Error:", e)

if __name__ == "__main__":
    test_bff()
