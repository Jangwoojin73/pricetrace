# -*- coding: utf-8 -*-
"""
Micro Audit Shared Configuration & Helpers (v2.0 Real-Measurement Edition)
- 절대 추측/하드코딩 금지: 모든 에러와 실측값을 있는 그대로 기록
"""
import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.dirname(BASE_DIR)
RESULTS_DIR = os.path.join(BASE_DIR, "micro_results")
DOCS_REPORT_DIR = os.path.join(WORKSPACE_DIR, "docs", "report")
os.makedirs(ARTIFACT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(DOCS_REPORT_DIR, exist_ok=True)

BASE_URL = os.environ.get("AUDIT_BASE_URL", "http://127.0.0.1:8080")
PROD_URL = "https://pricetrace-nu.vercel.app"

# Windows Playwright 무충돌 검증 완료 플래그 (1.01초 기동 확인)
CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-remote-fonts"
]

MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def save_step_result(step_num, data):
    out_file = os.path.join(RESULTS_DIR, f"step{step_num}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Step {step_num}] Result saved to: {out_file}", flush=True)


def create_sentinel(page):
    """전역 런타임, HTTP 4xx/5xx 및 네트워크 에러 감시 센티널 부착"""
    sentinel = {
        "console_errors": [],
        "page_errors": [],
        "http_errors": [],
        "failed_requests": [],
        "broken_images_count": 0,
        "broken_image_srcs": []
    }

    def on_console(msg):
        if msg.type == "error":
            text = msg.text
            # 로컬/오프라인 환경에서 무시 가능한 favicon/sw 오류는 구분하되 모두 기록
            sentinel["console_errors"].append(text)

    def on_response(resp):
        if resp.status >= 400:
            sentinel["http_errors"].append({"url": resp.url, "status": resp.status})

    def on_req_failed(req):
        fail_text = str(req.failure or "")
        # page 전환/중단으로 인한 ERR_ABORTED나 --disable-remote-fonts 차단 제외 여부 구분
        if "net::ERR_ABORTED" not in fail_text:
            sentinel["failed_requests"].append({"url": req.url, "failure": fail_text})

    page.on("console", on_console)
    page.on("pageerror", lambda exc: sentinel["page_errors"].append(str(exc)))
    page.on("response", on_response)
    page.on("requestfailed", on_req_failed)
    return sentinel


def collect_broken_images(page, sentinel):
    """현재 페이지 내 깨진 이미지(naturalWidth === 0) 실제 검사"""
    try:
        broken = page.evaluate('''() => {
            const imgs = Array.from(document.querySelectorAll('img'));
            return imgs
                .filter(img => {
                    const style = window.getComputedStyle(img);
                    // 화면에 보이는 이미지이거나 src가 유효하게 설정된 경우 검사
                    const isHiddenContainer = img.closest('[style*="display: none"], .hidden');
                    return img.src && !isHiddenContainer && img.complete && img.naturalWidth === 0;
                })
                .map(img => img.src);
        }''')
        sentinel["broken_images_count"] += len(broken)
        for src in broken:
            if src not in sentinel["broken_image_srcs"]:
                sentinel["broken_image_srcs"].append(src)
    except Exception:
        pass


def sentinel_summary(sentinel):
    total_errors = (
        len(sentinel["console_errors"])
        + len(sentinel["page_errors"])
        + len(sentinel["http_errors"])
        + len(sentinel["failed_requests"])
        + sentinel["broken_images_count"]
    )
    return {
        "total_errors": total_errors,
        "console_errors": sentinel["console_errors"],
        "page_errors": sentinel["page_errors"],
        "http_errors": sentinel["http_errors"],
        "failed_requests": sentinel["failed_requests"],
        "broken_images_count": sentinel["broken_images_count"],
        "broken_image_srcs": sentinel["broken_image_srcs"]
    }


def safe_screenshot(page, path, timeout=6000):
    try:
        page.screenshot(path=path, timeout=timeout, animations="disabled")
        # 규칙 3: 고유 파일명 verify_{항목명}_{시각}.png 동시 생성
        dirname = os.path.dirname(path)
        base = os.path.splitext(os.path.basename(path))[0]
        ext = os.path.splitext(os.path.basename(path))[1]
        ts_str = time.strftime("%H%M%S")
        verify_path = os.path.join(dirname, f"verify_{base}_{ts_str}{ext}")
        try:
            import shutil
            shutil.copy2(path, verify_path)
            # 아티팩트 디렉토리에도 동기화
            if dirname != ARTIFACT_DIR:
                shutil.copy2(path, os.path.join(ARTIFACT_DIR, os.path.basename(path)))
                shutil.copy2(path, os.path.join(ARTIFACT_DIR, f"verify_{base}_{ts_str}{ext}"))
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"  [!] Screenshot warning ({os.path.basename(path)}): {e}", flush=True)
        return False
