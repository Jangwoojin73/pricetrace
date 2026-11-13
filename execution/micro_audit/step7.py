# -*- coding: utf-8 -*-
"""
Step 7: 5 Devices Responsive Layout, Desktop Search Guard & PWA Infrastructure Audit
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, MOBILE_UA, PC_UA,
    save_step_result, create_sentinel, collect_broken_images, sentinel_summary, safe_screenshot
)

DEVICES = [
    {"name": "iPhone 15 Pro", "vp": {'width': 393, 'height': 852}, "ua": MOBILE_UA, "mobile": True},
    {"name": "Galaxy S24", "vp": {'width': 360, 'height': 780}, "ua": "Mozilla/5.0 (Linux; Android 14; SM-S921N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "mobile": True},
    {"name": "iPad Pro 11", "vp": {'width': 834, 'height': 1194}, "ua": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "mobile": True},
    {"name": "Galaxy Tab S8", "vp": {'width': 800, 'height': 1280}, "ua": "Mozilla/5.0 (Linux; Android 13; SM-X700) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", "mobile": True},
    {"name": "Wide PC Desktop", "vp": {'width': 1920, 'height': 1080}, "ua": PC_UA, "mobile": False}
]


def main():
    t_start = time.time()
    print(">>> [Step 7] Auditing 5 Devices Responsive Layout, Desktop Search Guard & PWA Assets...")
    metrics = {"responsive_matrix": {}, "pwa_assets": {}, "pwa_dom": {}}
    s_all = {"console_errors": [], "page_errors": [], "http_errors": [], "failed_requests": [], "broken_images_count": 0, "broken_image_srcs": []}

    def merge_s(s):
        for k in ["console_errors", "page_errors", "http_errors", "failed_requests", "broken_image_srcs"]:
            s_all[k].extend(s[k])
        s_all["broken_images_count"] += s["broken_images_count"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        all_no_overflow = True

        for dev in DEVICES:
            ctx = browser.new_context(
                viewport=dev["vp"],
                user_agent=dev["ua"],
                is_mobile=dev["mobile"],
                has_touch=dev["mobile"],
                service_workers="block"
            )
            p_dev = ctx.new_page()
            p_dev.set_default_timeout(8000)
            s_d = create_sentinel(p_dev)
            p_dev.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
            try:
                p_dev.goto(BASE_URL, wait_until="domcontentloaded", timeout=7000)
            except Exception:
                time.sleep(0.3)
                p_dev.goto(BASE_URL, wait_until="commit", timeout=7000)
            p_dev.wait_for_timeout(350)

            overflow = p_dev.evaluate('''() => {
                return {
                    scrollWidth: document.documentElement.scrollWidth,
                    innerWidth: window.innerWidth,
                    hasOverflow: document.documentElement.scrollWidth > window.innerWidth
                };
            }''')
            if overflow["hasOverflow"]:
                all_no_overflow = False

            # Wide PC Desktop에서 스크롤 시 검색바 상시 노출 가드 검증
            if dev["name"] == "Wide PC Desktop":
                p_dev.evaluate("window.scrollBy({ top: 500, behavior: 'instant' });")
                p_dev.wait_for_timeout(300)
                pc_guard = p_dev.evaluate('''() => {
                    const s = document.getElementById("gnbSearchSection");
                    const rect = s ? s.getBoundingClientRect() : null;
                    return {
                        searchHeight: rect ? Math.round(rect.height) : 0,
                        opacity: s ? window.getComputedStyle(s).opacity : "0",
                        alwaysVisible: rect ? rect.height > 30 && window.getComputedStyle(s).opacity === "1" : false
                    };
                }''')
                metrics["desktop_search_guard"] = pc_guard
                snap_matrix = os.path.join(ARTIFACT_DIR, "audit_07_responsive_matrix.png")
                safe_screenshot(p_dev, snap_matrix)
                metrics["snap_matrix"] = snap_matrix

            collect_broken_images(p_dev, s_d)
            merge_s(s_d)
            metrics["responsive_matrix"][dev["name"]] = overflow
            ctx.close()

        # PWA Infrastructure & Assets Check
        pwa_ctx = browser.new_context(viewport={'width': 393, 'height': 852}, user_agent=MOBILE_UA, is_mobile=True, has_touch=True, service_workers="block")
        p_pwa = pwa_ctx.new_page()
        p_pwa.set_default_timeout(8000)
        s_pwa = create_sentinel(p_pwa)
        p_pwa.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_pwa.goto(BASE_URL, wait_until="domcontentloaded")
        p_pwa.wait_for_timeout(500)

        pwa_res = p_pwa.evaluate('''async () => {
            const assets = [
                "/manifest.json",
                "/sw.js",
                "/favicon.ico",
                "/logo_jwj.svg",
                "/icons/icon-192x192.png",
                "/icons/icon-512x512.png"
            ];
            const results = {};
            for (const a of assets) {
                try {
                    const res = await fetch(a);
                    results[a] = res.status;
                } catch (e) {
                    results[a] = 0;
                }
            }
            return results;
        }''')

        pwa_dom = p_pwa.evaluate('''() => {
            const installBtn = document.getElementById("installAppBtn");
            const mobileInstallBtn = document.getElementById("mobileInstallAppBtn");
            const iosBanner = document.getElementById("pwaInstallBanner") || document.getElementById("iosInstallBanner");
            const iosModal = document.getElementById("iosInstallModal");
            return {
                hasInstallBtn: !!installBtn,
                hasMobileInstallBtn: !!mobileInstallBtn,
                hasPwaBannerOrModal: !!iosBanner || !!iosModal,
                hasIosModal: !!iosModal
            };
        }''')

        snap_pwa = os.path.join(ARTIFACT_DIR, "audit_07_pwa_install_elements.png")
        safe_screenshot(p_pwa, snap_pwa)
        merge_s(s_pwa)

        metrics["pwa_assets"] = pwa_res
        metrics["pwa_dom"] = pwa_dom
        metrics["snap_pwa"] = snap_pwa
        pwa_ctx.close()
        browser.close()

    s_sum = sentinel_summary(s_all)
    all_assets_200 = all(v == 200 for v in metrics["pwa_assets"].values())
    pc_guard_ok = metrics.get("desktop_search_guard", {}).get("alwaysVisible", False)
    passed = (
        all_no_overflow
        and all_assets_200
        and metrics["pwa_dom"]["hasInstallBtn"]
        and metrics["pwa_dom"]["hasIosModal"]
        and pc_guard_ok
        and s_sum["total_errors"] == 0
    )

    result = {
        "step": 7,
        "name": "5 Devices Responsive Layout, Desktop Search Guard & PWA Infrastructure Audit",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": s_sum,
        "metrics": metrics
    }
    print(f"[Step 7] {result['elapsed_sec']}s | NoOverflow={all_no_overflow} | PWA200={all_assets_200} | PCGuard={pc_guard_ok} | Errors={s_sum['total_errors']} | Status={result['status']}")
    save_step_result(7, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
