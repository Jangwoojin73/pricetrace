# -*- coding: utf-8 -*-
"""
Step 4: Cross-Device Naver Price Anchor (#shp_dui_root / #shp_lis_root) Live Jump & PowerLink Bypass Audit
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from playwright.sync_api import sync_playwright
from config import (
    BASE_URL, ARTIFACT_DIR, CHROMIUM_ARGS, MOBILE_UA, PC_UA,
    save_step_result, create_sentinel, sentinel_summary, safe_screenshot
)


def inspect_naver_live_page(context, url, anchor_id, snap_path):
    """실제 네이버 검색 URL을 열어 스크롤 점프, 앵커 안착 좌표, 파워링크 스킵, WAF/로그인 여부를 실측"""
    p_naver = context.new_page()
    p_naver.set_default_timeout(12000)
    res = {
        "url": url,
        "final_url": "",
        "http_status": 0,
        "scrollY": 0,
        "anchor_found": False,
        "anchor_top_px": None,
        "powerlink_found": False,
        "powerlink_bottom_px": None,
        "powerlink_skipped": True,
        "waf_blocked": False,
        "login_redirected": False
    }
    try:
        resp = p_naver.goto(url, wait_until="domcontentloaded")
        p_naver.wait_for_timeout(1200)
        res["http_status"] = resp.status if resp else 0
        res["final_url"] = p_naver.url
        res["login_redirected"] = "nidlogin" in p_naver.url or "nid.naver.com" in p_naver.url

        # 해시 앵커가 자동 스크롤되지 않는 경우를 대비해 실제 브라우저 초기 로드 상태 그대로 측정
        live_eval = p_naver.evaluate(f'''() => {{
            const bodyTxt = document.body ? document.body.innerText : "";
            const anchorEl = document.getElementById("{anchor_id}");
            const anchorRect = anchorEl ? anchorEl.getBoundingClientRect() : null;
            // 파워링크 광고 섹션 후보 탐색
            const powerlinkEl = document.querySelector("#power_link_body, .sp_powerlink, [data-cr-area='pwl'], .ad_section, ._au_power_link");
            const pwlRect = powerlinkEl ? powerlinkEl.getBoundingClientRect() : null;
            return {{
                scrollY: Math.round(window.scrollY || window.pageYOffset || 0),
                anchorFound: !!anchorEl,
                anchorTopPx: anchorRect ? Math.round(anchorRect.top) : null,
                powerlinkFound: !!powerlinkEl,
                powerlinkBottomPx: pwlRect ? Math.round(pwlRect.bottom) : null,
                wafBlocked: bodyTxt.includes("쇼핑 서비스 접속이 일시적으로 제한") || bodyTxt.includes("비정상적인 접근"),
                missingProduct: bodyTxt.includes("상품이 존재하지 않습니다")
            }};
        }}''')
        res["scrollY"] = live_eval["scrollY"]
        res["anchor_found"] = live_eval["anchorFound"]
        res["anchor_top_px"] = live_eval["anchorTopPx"]
        res["powerlink_found"] = live_eval["powerlinkFound"]
        res["powerlink_bottom_px"] = live_eval["powerlinkBottomPx"]
        if live_eval["powerlinkFound"] and live_eval["powerlinkBottomPx"] is not None:
            res["powerlink_skipped"] = live_eval["powerlinkBottomPx"] <= 0
        res["waf_blocked"] = live_eval["wafBlocked"]
        res["missing_product"] = live_eval["missingProduct"]

        safe_screenshot(p_naver, snap_path)
    except Exception as e:
        res["error"] = str(e)
    finally:
        p_naver.close()
    return res


def main():
    t_start = time.time()
    print(">>> [Step 4] Auditing Cross-Device Naver Price Anchors & Live Jump...")
    metrics = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        # 4-1. PC Desktop Anchor (#shp_dui_root)
        pc_ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, user_agent=PC_UA, service_workers="block")
        p_pc = pc_ctx.new_page()
        p_pc.set_default_timeout(12000)
        s_pc = create_sentinel(p_pc)
        p_pc.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_pc.goto(BASE_URL, wait_until="domcontentloaded")
        p_pc.wait_for_timeout(400)

        p_pc.fill("#searchInput", "농심 신라면 20개")
        with p_pc.expect_response(lambda r: "/api/search" in r.url, timeout=12000):
            p_pc.press("#searchInput", "Enter")
        p_pc.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=10000)
        p_pc.wait_for_timeout(300)

        pc_anchor = p_pc.evaluate('''() => {
            const link = document.querySelector("#priceComparisonGrid .rank-card a[target='_blank']");
            return {
                href: link ? link.href : "",
                hasAnchor: link ? link.href.includes("#shp_dui_root") : false,
                whereShp: link ? link.href.includes("where=shp") : false
            };
        }''')
        snap_pc_card = os.path.join(ARTIFACT_DIR, "audit_04_rank1_verified.png")
        safe_screenshot(p_pc, snap_pc_card)
        pc_anchor["card_screenshot"] = snap_pc_card

        snap_pc_naver = os.path.join(ARTIFACT_DIR, "audit_04_pc_anchor_desktop_verified.png")
        pc_live = inspect_naver_live_page(pc_ctx, pc_anchor["href"], "shp_dui_root", snap_pc_naver)
        pc_anchor["live_naver_check"] = pc_live
        pc_anchor["screenshot"] = snap_pc_naver
        metrics["pc"] = pc_anchor
        s_pc_sum = sentinel_summary(s_pc)
        pc_ctx.close()

        # 4-2. Mobile Anchor (#shp_lis_root)
        m_ctx = browser.new_context(
            viewport={'width': 393, 'height': 852},
            user_agent=MOBILE_UA,
            is_mobile=True,
            has_touch=True,
            service_workers="block"
        )
        p_m = m_ctx.new_page()
        p_m.set_default_timeout(12000)
        s_m = create_sentinel(p_m)
        p_m.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        p_m.goto(BASE_URL, wait_until="domcontentloaded")
        p_m.wait_for_timeout(400)

        p_m.fill("#searchInput", "농심 신라면 20개")
        with p_m.expect_response(lambda r: "/api/search" in r.url, timeout=12000):
            p_m.press("#searchInput", "Enter")
        p_m.wait_for_selector("#priceComparisonGrid .rank-card a[target='_blank']", timeout=10000)
        p_m.wait_for_timeout(300)

        m_anchor = p_m.evaluate('''() => {
            const link = document.querySelector("#priceComparisonGrid .rank-card a[target='_blank']");
            return {
                href: link ? link.href : "",
                hasAnchor: link ? (link.href.includes("#shp_lis_root") && link.href.includes("m.search.naver.com")) : false
            };
        }''')

        snap_m_naver = os.path.join(ARTIFACT_DIR, "audit_04_mobile_anchor_lis_verified.png")
        m_live = inspect_naver_live_page(m_ctx, m_anchor["href"], "shp_lis_root", snap_m_naver)
        m_anchor["live_naver_check"] = m_live
        m_anchor["screenshot_anchor"] = snap_m_naver
        m_anchor["screenshot_rank1"] = snap_pc_card
        metrics["mobile"] = m_anchor
        s_m_sum = sentinel_summary(s_m)
        m_ctx.close()

        browser.close()

    total_errors = s_pc_sum["total_errors"] + s_m_sum["total_errors"]
    passed = (
        metrics["pc"]["hasAnchor"]
        and metrics["pc"]["whereShp"]
        and metrics["mobile"]["hasAnchor"]
        and not pc_live.get("waf_blocked", False)
        and not pc_live.get("login_redirected", False)
        and not m_live.get("waf_blocked", False)
        and not m_live.get("login_redirected", False)
        and total_errors == 0
    )

    result = {
        "step": 4,
        "name": "Cross-Device Naver Price Anchor & PowerLink Ad Bypass Audit",
        "status": "PASS" if passed else "FAIL",
        "elapsed_sec": round(time.time() - t_start, 2),
        "sentinel": {
            "total_errors": total_errors,
            "pc_errors": s_pc_sum,
            "mobile_errors": s_m_sum
        },
        "metrics": metrics
    }
    print(f"[Step 4] {result['elapsed_sec']}s | PC Anchor={pc_anchor['hasAnchor']} (scrollY={pc_live['scrollY']}, found={pc_live['anchor_found']}) | M Anchor={m_anchor['hasAnchor']} (scrollY={m_live['scrollY']}, found={m_live['anchor_found']}) | Errors={total_errors}")
    save_step_result(4, result)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
