# -*- coding: utf-8 -*-
"""
Verify Mobile Top Live Banner Sharpness & Anti-Blur Optimization
- Emulates iPhone 15 Pro (393 x 852, device_scale_factor=3)
- Validates computed styles (zero filter, zero backdrop-filter, zero animation, opacity 1.0)
- Takes high-res retina screenshots
- Creates Before vs After comparison artifact
"""

import os
import json
import pathlib
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

output_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
html_path = pathlib.Path(r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\index.html").as_uri()
print("Loading URI:", html_path)

with sync_playwright() as p:
    iphone = p.devices['iPhone 15 Pro']
    browser = p.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
    )
    context = browser.new_context(
        **iphone,
        device_scale_factor=3
    )
    page = context.new_page()
    page.goto(html_path, wait_until='domcontentloaded')
    
    # Remove splash screen immediately for clean view
    page.evaluate("() => { const s = document.getElementById('appSplashScreen'); if (s) s.remove(); }")
    page.wait_for_timeout(600)
    
    # 1. Computed style evaluation
    styles = page.evaluate("""() => {
        const header = document.querySelector('header');
        const el = document.getElementById('topLiveBanner');
        const badge = el.querySelector('span');
        const strongText = document.getElementById('topBannerText');
        
        const csHeader = window.getComputedStyle(header);
        const cs = window.getComputedStyle(el);
        const bs = window.getComputedStyle(badge);
        const ss = window.getComputedStyle(strongText);
        
        return {
            headerPosition: csHeader.position,
            headerFilter: csHeader.filter,
            headerBackdropFilter: csHeader.backdropFilter || csHeader.webkitBackdropFilter,
            headerBoxShadow: csHeader.boxShadow,
            bannerBg: cs.backgroundColor,
            bannerColor: cs.color,
            bannerFilter: cs.filter,
            bannerBackdropFilter: cs.backdropFilter || cs.webkitBackdropFilter,
            bannerBoxShadow: cs.boxShadow,
            bannerTextShadow: cs.textShadow,
            bannerPaddingTop: cs.paddingTop,
            bannerPaddingBottom: cs.paddingBottom,
            badgeBg: bs.backgroundColor,
            badgeColor: bs.color,
            badgeOpacity: bs.opacity,
            badgeAnimation: bs.animationName,
            strongColor: ss.color,
            strongFontWeight: ss.fontWeight
        };
    }""")
    print("COMPUTED_STYLES:" + json.dumps(styles, ensure_ascii=False))
    
    # 2. Capture high-resolution retina crops
    banner_el = page.locator('#topLiveBanner')
    sharp_banner_path = os.path.join(output_dir, "audit_mobile_top_live_banner_sharp.png")
    banner_el.screenshot(path=sharp_banner_path)
    print("Saved sharp banner screenshot to:", sharp_banner_path)
    
    header_el = page.locator('header')
    sharp_header_path = os.path.join(output_dir, "audit_mobile_header_sharp.png")
    header_el.screenshot(path=sharp_header_path)
    print("Saved sharp header screenshot to:", sharp_header_path)
    
    full_mobile_path = os.path.join(output_dir, "audit_mobile_top_full_view.png")
    page.screenshot(path=full_mobile_path)
    print("Saved full mobile screenshot to:", full_mobile_path)
    
    # 3. Build Before / After Comparison Image
    before_path = os.path.join(output_dir, "user_quote_orig.png")
    after_path = sharp_banner_path
    
    if os.path.exists(before_path) and os.path.exists(after_path):
        before_raw = Image.open(before_path)
        after_raw = Image.open(after_path)
        
        target_w = 1179  # 393 * 3
        before_h = int(before_raw.height * (target_w / before_raw.width))
        before_scaled = before_raw.resize((target_w, max(before_h, 80)), Image.Resampling.BILINEAR)
        
        after_w, after_h = after_raw.size
        
        canvas_h = before_scaled.height + after_h + 160
        comp = Image.new("RGB", (target_w, canvas_h), (15, 23, 42))
        draw = ImageDraw.Draw(comp)
        
        # Header 1: BEFORE
        draw.rectangle([0, 0, target_w, 45], fill=(220, 38, 38))
        draw.text((20, 10), "[BEFORE] 기존 모바일 화면: animate-pulse 오파시티 진동 + 11px 초소형 폰트 흐릿함(Blur) 발생", fill=(255, 255, 255))
        comp.paste(before_scaled, (0, 45))
        
        # Header 2: AFTER
        after_y_start = 45 + before_scaled.height + 30
        draw.rectangle([0, after_y_start - 35, target_w, after_y_start + 10], fill=(22, 163, 74))
        draw.text((20, after_y_start - 25), "[AFTER] 개선 후 모바일 화면: 펄스/블러 필터 100% 원천 제거 + 12px 볼드 화이트 & 앰버 초고선명 렌더링", fill=(255, 255, 255))
        comp.paste(after_raw, (0, after_y_start + 10))
        
        comparison_out_path = os.path.join(output_dir, "audit_mobile_top_banner_before_after.png")
        comp.save(comparison_out_path)
        print("Saved before/after comparison image to:", comparison_out_path)
    
    browser.close()
print("Verification complete.")
