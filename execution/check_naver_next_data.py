# -*- coding: utf-8 -*-
import urllib.request
import json
import re

def check_naver_catalog():
    # Naver Shopping search API or HTML
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Referer": "https://shopping.naver.com/"
    }
    
    # Let's inspect the HTML of search.naver.com with where=shp vs search.shopping.naver.com
    # In search.naver.com?where=shp&query=...
    url = "https://search.shopping.naver.com/search/all?query=" + urllib.parse.quote("코카콜라 제로 355ml 24캔")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            print("Length of HTML:", len(html))
            # Find __NEXT_DATA__
            m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
            if m:
                data = json.loads(m.group(1))
                print("NEXT_DATA found!")
                props = data.get("props", {}).get("pageProps", {})
                initial_state = props.get("initialState", {})
                products = initial_state.get("products", {}).get("list", [])
                print(f"Products count in NEXT_DATA: {len(products)}")
                for i, p in enumerate(products[:5]):
                    item = p.get("item", {})
                    prod_name = item.get("productTitle", "") or item.get("productName", "")
                    low_price = item.get("lowPrice", "")
                    mall_name = item.get("mallName", "")
                    is_ad = item.get("ad", False) or item.get("isAd", False)
                    cat_id = item.get("id", "")
                    channel = item.get("channel", {})
                    print(f"[{i+1}] Title: {prod_name} | Price: {low_price} | Mall: {mall_name} | Ad: {is_ad} | ID: {cat_id}")
            else:
                print("NEXT_DATA not found in HTML")
    except Exception as e:
        print("Error fetching:", e)

if __name__ == "__main__":
    check_naver_catalog()
