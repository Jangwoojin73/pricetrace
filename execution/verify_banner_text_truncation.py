# -*- coding: utf-8 -*-
"""
Verification script for Top LIVE Banner text replacement and truncation prevention.
Checks:
- iPhone 15 Pro (393 x 852)
- Galaxy S24 (360 x 780)
- PC Desktop (1440 x 900)
Verifies scrollWidth <= clientWidth (isTruncated == False).
Captures screenshots to artifact directory.
"""

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_URL = "http://127.0.0.1:8080"

test_cases = [
    {
        "name": "iPhone 15 Pro (iOS)",
        "viewport": {"width": 393, "height": 852},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
        "screenshot_name": "audit_mobile_top_banner_no_truncation.png"
    },
    {
        "name": "Galaxy S24 (Android)",
        "viewport": {"width": 360, "height": 780},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
        "screenshot_name": "audit_android_top_banner_no_truncation.png"
    },
    {
        "name": "Desktop PC (1440x900)",
        "viewport": {"width": 1440, "height": 900},
        "device_scale_factor": 1,
        "is_mobile": False,
        "has_touch": False,
        "screenshot_name": "audit_pc_top_banner_no_truncation.png"
    }
]

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])

    for tc in test_cases:
        ctx = browser.new_context(
            viewport=tc["viewport"],
            device_scale_factor=tc["device_scale_factor"],
            is_mobile=tc["is_mobile"],
            has_touch=tc["has_touch"]
        )
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_timeout(600)

        # Measure banner text and truncation
        metrics = page.evaluate('''() => {
            const banner = document.getElementById("topLiveBanner");
            const textSpan = banner ? banner.querySelector("span.truncate") : null;
            const strong = document.getElementById("topBannerText");
            
            const clientWidth = textSpan ? textSpan.clientWidth : 0;
            const scrollWidth = textSpan ? textSpan.scrollWidth : 0;
            const isTruncated = scrollWidth > clientWidth;
            
            return {
                fullBannerText: banner ? banner.innerText.replace(/\\s+/g, ' ').trim() : '',
                spanText: textSpan ? textSpan.innerText.replace(/\\s+/g, ' ').trim() : '',
                strongText: strong ? strong.textContent.trim() : '',
                clientWidth: clientWidth,
                scrollWidth: scrollWidth,
                isTruncated: isTruncated
            };
        }''')

        print(f"[{tc['name']}] 측정 결과:")
        print(f"  - 텍스트: {metrics['spanText']}")
        print(f"  - clientWidth: {metrics['clientWidth']}px, scrollWidth: {metrics['scrollWidth']}px")
        print(f"  - 말줄임표(...) 발생 여부 (isTruncated): {metrics['isTruncated']}")

        # Header screenshot crop
        header_el = page.query_selector("header")
        if header_el:
            screenshot_path = os.path.join(ARTIFACT_DIR, tc["screenshot_name"])
            header_el.screenshot(path=screenshot_path)
            print(f"  - 스크린샷 저장 완료: {screenshot_path}")

        # Test search and home restoration on iPhone
        if "iPhone" in tc["name"]:
            page.fill("#searchInput", "신라면")
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)

            # Click logo to return home
            home_logo = page.query_selector("a[href='/']")
            if home_logo:
                home_logo.click()
                page.wait_for_timeout(600)

            restored_text = page.evaluate('''() => {
                const strong = document.getElementById("topBannerText");
                return strong ? strong.textContent.trim() : '';
            }''')
            print(f"  - [복원 검증] 검색 후 웰컴 뷰 복귀 시 텍스트: '{restored_text}'")
            metrics["restored_text"] = restored_text

        results.append({
            "device": tc["name"],
            "metrics": metrics,
            "screenshot": tc["screenshot_name"]
        })
        ctx.close()

    browser.close()

# Save JSON results
result_json_path = os.path.join(ARTIFACT_DIR, "banner_truncation_audit.json")
with open(result_json_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n전체 검증 완료!")
