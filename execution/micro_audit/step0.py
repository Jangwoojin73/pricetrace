# -*- coding: utf-8 -*-
"""
Step 0: Local & Production Environment Audit + Version Sync Check (Pure Python)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import urllib.request
import ssl
import time
import json
from config import BASE_URL, PROD_URL, save_step_result


def check_url(url, timeout=6):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "PriceTrace-Auditor/2.0"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            elapsed = round((time.time() - t0) * 1000, 1)
            return resp.status, elapsed, body, None
    except Exception as e:
        elapsed = round((time.time() - t0) * 1000, 1)
        return 0, elapsed, "", str(e)


def main():
    t_start = time.time()
    print(">>> [Step 0] Checking Local Server & Production URL...")

    # 1. Local Server & /api/status Check
    local_status, local_ms, local_html, local_err = check_url(BASE_URL)
    local_api_status, local_api_ms, local_api_body, _ = check_url(f"{BASE_URL}/api/status")

    # 2. Production Vercel URL & /api/status Check
    prod_status, prod_ms, prod_html, prod_err = check_url(PROD_URL)
    prod_api_status, prod_api_ms, prod_api_body, _ = check_url(f"{PROD_URL}/api/status")

    # 3. Latest Version Sync Check (v1.6.2: gnbSearchSection + LOCK_DURATION_MS + high contrast refresh)
    _, _, local_appjs, _ = check_url(f"{BASE_URL}/app.js")
    _, _, prod_appjs, _ = check_url(f"{PROD_URL}/app.js")

    local_has_v161 = ("LOCK_DURATION_MS" in local_appjs) and ("setupPullToRefresh" in local_appjs)
    prod_has_v161 = ("LOCK_DURATION_MS" in prod_appjs) and ("setupPullToRefresh" in prod_appjs)
    local_has_search_id = "gnbSearchSection" in local_html
    prod_has_search_id = "gnbSearchSection" in prod_html

    # Raw API JSON sample extraction (의무 2: DB·API 런타임 원본 응답 증거)
    local_api_json = None
    try:
        local_api_json = json.loads(local_api_body)
    except Exception:
        pass
    prod_api_json = None
    try:
        prod_api_json = json.loads(prod_api_body)
    except Exception:
        pass

    passed = (
        local_status == 200
        and local_api_status == 200
        and prod_status == 200
        and local_has_v161
        and prod_has_v161
    )

    result = {
        "step": 0,
        "name": "Local/Live Environment Audit & Global Sentinel Init",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": {"total_errors": 0 if passed else 1},
        "metrics": {
            "local_url": BASE_URL,
            "local_status": local_status,
            "local_response_ms": local_ms,
            "local_api_status": local_api_status,
            "local_api_raw_sample": local_api_json,
            "local_error": local_err,
            "prod_url": PROD_URL,
            "prod_status": prod_status,
            "prod_response_ms": prod_ms,
            "prod_api_status": prod_api_status,
            "prod_api_raw_sample": prod_api_json,
            "prod_error": prod_err,
            "local_v161_synced": local_has_v161 and local_has_search_id,
            "prod_v161_synced": prod_has_v161 and prod_has_search_id,
            "measured_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    print(f"[Step 0] {result['elapsed_sec']}s | Local HTTP {local_status} ({local_ms}ms) | Prod HTTP {prod_status} ({prod_ms}ms) | v1.6.1 Sync: Local={local_has_v161}, Prod={prod_has_v161}")
    save_step_result(0, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
