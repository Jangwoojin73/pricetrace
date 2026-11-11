# -*- coding: utf-8 -*-
"""
Micro Audit Shared Configuration & Helpers
"""
import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "micro_results")
DOCS_REPORT_DIR = os.path.join(os.path.dirname(BASE_DIR), "docs", "report")
os.makedirs(ARTIFACT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(DOCS_REPORT_DIR, exist_ok=True)

BASE_URL = "http://127.0.0.1:8080"
PROD_URL = "https://pricetrace-nu.vercel.app"

CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-remote-fonts"
]

def save_step_result(step_num, data):
    out_file = os.path.join(RESULTS_DIR, f"step{step_num}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Step {step_num}] Result saved to: {out_file}")

def get_sentinel(page):
    sentinel = {
        "console_errors": [],
        "page_errors": [],
        "failed_requests": [],
        "broken_images": 0
    }
    page.on("console", lambda msg: sentinel["console_errors"].append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: sentinel["page_errors"].append(str(exc)))
    page.on("requestfailed", lambda req: sentinel["failed_requests"].append(f"{req.url} - {req.failure}"))
    return sentinel

def check_broken_images(page):
    broken_cnt = page.evaluate('''() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        return imgs.filter(img => img.complete && img.naturalWidth === 0).length;
    }''')
    return broken_cnt
