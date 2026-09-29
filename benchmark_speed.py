import urllib.request
import json
import time

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def benchmark(url, label):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Benchmark/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            elapsed = time.time() - t0
            item = data.get('representative_item', {})
            title = item.get('title', '')[:25]
            price = data.get('lowest_price', 0)
            is_live = data.get('is_live', False)
            success = data.get('success', False)
            print(f"[{label}] {elapsed:.3f}초 | 성공: {success} | 실시간: {is_live} | 최저가: {price:,}원 | 상품명: {title}")
    except Exception as e:
        print(f"[{label}] ERROR: {e}")

if __name__ == '__main__':
    print("=== 1. 콜드 검색 속도 (첫 검색 / 다나와 직결) ===")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%8B%A0%EB%9D%BC%EB%A9%B4", "신라면 콜드")
    benchmark("http://127.0.0.1:8080/api/search?q=%ED%96%87%EB%B0%98", "햇반 콜드")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%82%BC%EB%8B%A4%EC%88%98", "삼다수 콜드")

    print("\n=== 2. 캐시 히트 속도 (인메모리 캐시 재검색) ===")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%8B%A0%EB%9D%BC%EB%A9%B4", "신라면 캐시")
    benchmark("http://127.0.0.1:8080/api/search?q=%ED%96%87%EB%B0%98", "햇반 캐시")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%82%BC%EB%8B%A4%EC%88%98", "삼다수 캐시")

    print("\n=== 3. 강제 갱신 속도 (refresh=true) ===")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%8B%A0%EB%9D%BC%EB%A9%B4&refresh=true", "신라면 강제갱신")

    print("\n=== 4. 신규 미캐시 키워드 콜드 크롤링 속도 ===")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%BD%94%EC%B9%B4%EC%BD%9C%EB%9D%BC", "코카콜라 신규")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%8A%A4%ED%8C%B8", "스팸 신규")
    benchmark("http://127.0.0.1:8080/api/search?q=%EC%A7%9C%ED%8C%8C%EA%B2%8C%ED%8B%B0", "짜파게티 신규")
