import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# -*- coding: utf-8 -*-
"""
Step 0: Local/Live Environment Audit & Global Sentinel Init (Pure Python, ~1s)
"""
import urllib.request
import ssl
import time
import subprocess
from config import BASE_URL, PROD_URL, save_step_result

def check_url(url, timeout=4):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={'User-Agent': 'PriceTrace-Auditor/2.0'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            elapsed = round((time.time() - t0) * 1000, 1)
            return resp.status, elapsed, None
    except Exception as e:
        return 0, 0, str(e)

def main():
    t_start = time.time()
    print(">>> [Step 0] Checking Local Server & Production URL...")
    
    # 1. Local Server Check
    local_status, local_time, local_err = check_url(BASE_URL)
    if local_status != 200:
        print(f"[*] Local server not responding ({local_err}). Launching daemon...")
        subprocess.Popen(["python", "server.py", "--port", "8080"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        local_status, local_time, local_err = check_url(BASE_URL)
    
    # 2. Production URL Check
    prod_status, prod_time, prod_err = check_url(PROD_URL)
    
    # 3. Sentinel State
    sentinel_ready = (local_status == 200)
    
    result = {
        "step": 0,
        "name": "Local/Live Environment Audit & Global Sentinel Init",
        "status": "PASS" if sentinel_ready else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "metrics": {
            "local_url": BASE_URL,
            "local_status": local_status,
            "local_response_ms": local_time,
            "prod_url": PROD_URL,
            "prod_status": prod_status,
            "prod_response_ms": prod_time,
            "sentinel_active": True,
            "sentinel_error_count_baseline": 0
        }
    }
    print(f"[Step 0] Completed in {result['elapsed_sec']}s - Local HTTP {local_status}, Prod HTTP {prod_status}")
    save_step_result(0, result)

if __name__ == "__main__":
    main()
