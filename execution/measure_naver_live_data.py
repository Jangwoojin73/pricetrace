# -*- coding: utf-8 -*-
"""
Live Naver Data Fetching Reality Check
Measures actual network calls to Naver BFF, Naver Search HTML, Proxy, and Fallback
"""
import sys, os
import urllib.request
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pricetrace_bot

def test_naver_connections():
    results = {}
    test_keywords = ["신라면", "햇반 24개", "사과"]

    print("=== 1. Naver BFF Direct Call Test ===")
    for kw in test_keywords:
        t0 = time.time()
        try:
            items = pricetrace_bot.fetch_from_naver_bff(kw)
            elapsed = round(time.time() - t0, 3)
            results[f"bff_{kw}"] = {
                "status": "SUCCESS" if items else "EMPTY",
                "count": len(items) if items else 0,
                "elapsed": f"{elapsed}s",
                "sample": items[0]["title"] if items else None
            }
        except Exception as e:
            elapsed = round(time.time() - t0, 3)
            results[f"bff_{kw}"] = {
                "status": f"ERROR: {type(e).__name__} - {e}",
                "count": 0,
                "elapsed": f"{elapsed}s"
            }
        print(f"BFF [{kw}]:", results[f"bff_{kw}"])

    print("\n=== 2. Naver Proxy Call Test ===")
    for kw in test_keywords:
        t0 = time.time()
        try:
            items = pricetrace_bot.fetch_from_proxy(kw)
            elapsed = round(time.time() - t0, 3)
            results[f"proxy_{kw}"] = {
                "status": "SUCCESS" if items else "EMPTY",
                "count": len(items) if items else 0,
                "elapsed": f"{elapsed}s",
                "sample": items[0]["title"] if items else None
            }
        except Exception as e:
            elapsed = round(time.time() - t0, 3)
            results[f"proxy_{kw}"] = {
                "status": f"ERROR: {type(e).__name__} - {e}",
                "count": 0,
                "elapsed": f"{elapsed}s"
            }
        print(f"Proxy [{kw}]:", results[f"proxy_{kw}"])

    print("\n=== 3. 3-Tier Combined Pipeline Test (fetch_products_for_keyword) ===")
    for kw in test_keywords:
        t0 = time.time()
        res = pricetrace_bot.fetch_products_for_keyword(kw)
        elapsed = round(time.time() - t0, 3)
        items = res.get("items", [])
        results[f"combined_{kw}"] = {
            "source": res.get("source"),
            "success": res.get("success"),
            "count": len(items),
            "elapsed": f"{elapsed}s",
            "top1_title": items[0]["title"] if items else None,
            "top1_price": items[0]["price"] if items else None,
            "top1_mall": items[0].get("mallName") if items else None
        }
        print(f"Combined [{kw}]:", results[f"combined_{kw}"])

    print("\n=== 4. Daily Trending Products Test ===")
    t0 = time.time()
    trend = pricetrace_bot.fetch_daily_trending_products(force_refresh=True)
    elapsed = round(time.time() - t0, 3)
    results["trending"] = {
        "source": trend.get("source"),
        "date": trend.get("date"),
        "count": len(trend.get("items", [])),
        "elapsed": f"{elapsed}s",
        "sample": trend.get("items", [])[:3]
    }
    print("Trending:", {k: v for k, v in results["trending"].items() if k != "sample"})

    print("\n=== 5. Vercel Production API Live Test ===")
    vercel_apis = [
        "https://pricetrace-nu.vercel.app/api/search?q=%EC%8B%A0%EB%9D%BC%EB%A9%B4",
        "https://pricetrace-nu.vercel.app/api/trending"
    ]
    for url in vercel_apis:
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elapsed = round(time.time() - t0, 3)
                results[url] = {
                    "http_status": resp.status,
                    "source": data.get("source"),
                    "count": len(data.get("items", [])),
                    "elapsed": f"{elapsed}s",
                    "top1": data.get("items", [])[0]["title"] if data.get("items") else None
                }
        except Exception as e:
            elapsed = round(time.time() - t0, 3)
            results[url] = {
                "error": str(e),
                "elapsed": f"{elapsed}s"
            }
        print(f"Vercel [{url}]:", results[url])

    with open(r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41\naver_live_audit_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    test_naver_connections()
