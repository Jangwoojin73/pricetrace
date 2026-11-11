# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import json
import time

keywords = ["신라면", "햇반 24개", "삼다수 2L 12병", "코카콜라 제로 24캔", "사과", "맥북"]
results = {}

print("=== Vercel Live Production API 실시간 네이버 데이터 수집 전수 실측 ===")

for kw in keywords:
    enc = urllib.parse.quote(kw)
    url = f"https://pricetrace-nu.vercel.app/api/search?q={enc}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            elapsed = round(time.time() - t0, 3)
            items = data.get("top_items", [])
            results[kw] = {
                "http_status": resp.status,
                "elapsed": f"{elapsed}s",
                "is_live": data.get("is_live"),
                "lowest_price": data.get("lowest_price"),
                "target_price": data.get("target_price"),
                "unit_price": data.get("unit_price"),
                "item_count": len(items),
                "items": [
                    {
                        "rank": idx + 1,
                        "title": it.get("title"),
                        "price": it.get("price"),
                        "mall": it.get("mall_name"),
                        "url": it.get("url")
                    }
                    for idx, it in enumerate(items)
                ]
            }
            print(f"[{kw}] -> HTTP {resp.status} | {elapsed}s | is_live={data.get('is_live')} | count={len(items)} | lowest={data.get('lowest_price'):,}원")
            for it in results[kw]["items"]:
                print(f"   {it['rank']}위: {it['title']} ({it['price']:,}원 / {it['mall']})")
    except Exception as e:
        elapsed = round(time.time() - t0, 3)
        results[kw] = {"error": str(e), "elapsed": f"{elapsed}s"}
        print(f"[{kw}] ERROR: {e}")

out_path = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41\naver_live_search_audit.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nSaved full live audit JSON:", out_path)
