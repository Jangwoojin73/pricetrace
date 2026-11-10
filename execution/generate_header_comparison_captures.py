# -*- coding: utf-8 -*-
"""
generate_header_comparison_captures.py
Enhanced comparison image generator with Korean TrueType fonts (Malgun Gothic)
and visual distance indicators.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"

CASES = [
    {
        "id": "current",
        "title": "현재 상태 (기준: 0px)",
        "shift": "0px 밀어올림 (기준 원본)",
        "padding_desc": "상단 여백: 50px",
        "padding_top": "max(3.125rem, calc(env(safe-area-inset-top, 2.75rem) + 0.125rem))",
        "color": (148, 163, 184) # slate-400
    },
    {
        "id": "up4px",
        "title": "후보 1: 4px 밀어올림",
        "shift": "▲ 4px 위로 밀어올림",
        "padding_desc": "상단 여백: 46px (-4px)",
        "padding_top": "max(2.875rem, calc(env(safe-area-inset-top, 2.75rem) - 0.125rem))",
        "color": (59, 130, 246) # blue-500
    },
    {
        "id": "up5px",
        "title": "후보 2: 5px 밀어올림",
        "shift": "▲ 5px 위로 밀어올림",
        "padding_desc": "상단 여백: 45px (-5px)",
        "padding_top": "max(2.8125rem, calc(env(safe-area-inset-top, 2.75rem) - 3px))",
        "color": (16, 185, 129) # emerald-500
    },
    {
        "id": "up6px",
        "title": "후보 3: 6px 밀어올림",
        "shift": "▲ 6px 위로 밀어올림",
        "padding_desc": "상단 여백: 44px (-6px)",
        "padding_top": "max(2.75rem, calc(env(safe-area-inset-top, 2.75rem) - 0.25rem))",
        "color": (245, 158, 11) # amber-500
    }
]

def run():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    captured_files = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-remote-fonts']
        )

        for case in CASES:
            context = browser.new_context(
                viewport={'width': 393, 'height': 852},
                device_scale_factor=2,
                is_mobile=True,
                has_touch=True,
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1'
            )
            page = context.new_page()

            page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
            page.goto(BASE_URL, wait_until="networkidle")
            page.wait_for_timeout(400)

            # Apply target padding
            page.evaluate(f"""() => {{
                const el = document.getElementById('topLiveBanner');
                if (el) {{
                    el.style.setProperty('padding-top', '{case["padding_top"]}', 'important');
                }}
            }}""")
            page.wait_for_timeout(300)

            # Measure real computed values
            metrics = page.evaluate("""() => {
                const banner = document.getElementById('topLiveBanner');
                const badge = banner ? banner.querySelector('span.bg-red-600') : null;
                const header = document.querySelector('header');
                const gnb = document.getElementById('gnbNavBar');
                return {
                    bannerPaddingTop: banner ? window.getComputedStyle(banner).paddingTop : '',
                    bannerHeight: banner ? Math.round(banner.getBoundingClientRect().height) : 0,
                    badgeTop: badge ? Math.round(badge.getBoundingClientRect().top) : 0,
                    headerHeight: header ? Math.round(header.getBoundingClientRect().height) : 0,
                    gnbTop: gnb ? Math.round(gnb.getBoundingClientRect().top) : 0
                };
            }""")
            print(f"[{case['id']}] {case['title']} -> {metrics}")

            # Capture full screen
            full_filename = f"verify_header_{case['id']}_full.png"
            full_path = os.path.join(ARTIFACT_DIR, full_filename)
            page.screenshot(path=full_path, animations="disabled")

            # Crop top header area (top 260px in css = 520px in 2x retina)
            crop_filename = f"verify_header_{case['id']}_crop.png"
            crop_path = os.path.join(ARTIFACT_DIR, crop_filename)

            img = Image.open(full_path)
            w, h = img.size
            crop_box = (0, 0, w, min(h, 520))
            cropped = img.crop(crop_box)
            cropped.save(crop_path)

            captured_files[case['id']] = {
                "full": full_path,
                "crop": crop_path,
                "metrics": metrics
            }

            context.close()

        browser.close()

    create_composite_comparison(captured_files)

def create_composite_comparison(captured_files):
    crops = []
    cases_data = []

    for case in CASES:
        path = captured_files[case['id']]["crop"]
        img = Image.open(path)
        crops.append(img)
        cases_data.append((case, captured_files[case['id']]["metrics"]))

    font_title = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 26)
    font_sub = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 18)
    font_body = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 16)
    font_main_hdr = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 30)
    font_main_sub = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 17)

    single_w, single_h = crops[0].size
    header_area_h = 160
    margin = 30
    gap = 24
    total_w = (single_w * len(crops)) + (gap * (len(crops) - 1)) + (margin * 2)
    total_h = single_h + header_area_h + (margin * 2)

    composite = Image.new("RGB", (total_w, total_h), color=(10, 15, 30)) # deep navy
    draw = ImageDraw.Draw(composite)

    # Main Banner at top
    draw.text((margin, 25), "📱 PriceTrace 모바일 헤더 상단 빈공간 밀어올림 4단계 정밀 실측 비교표", fill=(255, 255, 255), font=font_main_hdr)
    draw.text((margin, 70), "사용자 요청: 상단 상태바와의 빈 공간(50px)을 각각 4px, 5px, 6px 밀어올려 공간 낭비 개선 및 최적 여백 검증", fill=(148, 163, 184), font=font_main_sub)

    for i, (crop, (case, metrics)) in enumerate(zip(crops, cases_data)):
        x = margin + i * (single_w + gap)
        y = header_area_h + margin

        # Draw card header
        card_color = case["color"]
        draw.rectangle([x, 105, x + single_w, y - 8], fill=(20, 30, 55), outline=card_color, width=2)
        draw.text((x + 16, 112), case["title"], fill=card_color, font=font_title)
        draw.text((x + 16, 150), f"{case['shift']} | {case['padding_desc']} | 배너전체: {metrics['bannerHeight']}px", fill=(226, 232, 240), font=font_sub)

        # Draw border around crop
        draw.rectangle([x - 2, y - 2, x + single_w + 2, y + single_h + 2], outline=card_color, width=3)
        composite.paste(crop, (x, y))

        # Draw a visual guideline badge showing the LIVE badge Y-coordinate
        badge_y_canvas = y + int(metrics['badgeTop'] * 2) # scale factor 2
        draw.line([(x, badge_y_canvas), (x + single_w, badge_y_canvas)], fill=(239, 68, 68), width=2)
        draw.text((x + 12, badge_y_canvas - 26), f"LIVE 뱃지 Y위치: {metrics['badgeTop']}px", fill=(254, 202, 202), font=font_body)

    out_path = os.path.join(ARTIFACT_DIR, "verify_header_comparison_4cases.png")
    composite.save(out_path, quality=95)
    print(f"\n[Generated Composite Image] {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    run()
