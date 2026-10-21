import urllib.request
import urllib.parse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

for kw in ["농심 신라면 봉지 20개입", "CJ제일제당 햇반 210g 24개", "사과"]:
    enc = urllib.parse.quote(kw)
    url = f"http://127.0.0.1:8080/api/search?keyword={enc}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    top = data.get("top_items", [])
    print(f"\n[{kw}] top_items count: {len(top)}")
    for i, it in enumerate(top[:3]):
        img = it.get("image") or it.get("image_url")
        lnk = it.get("link") or it.get("url")
        print(f"  Rank {i+1}: {it.get('title')} | {it.get('price')}원 | Mall: {it.get('mall')} | Img: {bool(img)} ({str(img)[:30]}...) | Link: {bool(lnk)}")
