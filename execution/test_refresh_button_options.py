# -*- coding: utf-8 -*-
"""
Test Refresh Button Brightness & Arrow Visibility Options
"""
import os
import pathlib
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

output_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
html_path = pathlib.Path(r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\index.html").resolve().as_uri()

options = [
    {
        "id": "current",
        "title": "현재 상태: 회색 반투명 배경 (#808197 계열)",
        "desc": "어두운 블러 배경과 섞여 칙칙한 회색으로 보이고 내부 화살표가 묻힘",
        "css": """
            #mobileRefreshBtn {
                background-color: rgba(255, 255, 255, 0.22) !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
            }
            #mobileRefreshBtn svg, #mobileRefreshBtn i {
                color: #ffffff !important;
                stroke: #ffffff !important;
                stroke-width: 2px !important;
            }
        """
    },
    {
        "id": "opt1_white_cobalt",
        "title": "시안 1 (추천): 순백색 캡슐 + 브랜드 코발트 블루 화살표 (#1D4ED8)",
        "desc": "화이트 캡슐로 15:1 초고대비 확보, PriceTrace 블루와 완벽 일체감",
        "css": """
            #mobileRefreshBtn {
                background-color: #ffffff !important;
                border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25), 0 1px 2px rgba(0, 0, 0, 0.1) !important;
                border-radius: 0.75rem !important;
            }
            #mobileRefreshBtn svg, #mobileRefreshBtn i {
                color: #1d4ed8 !important;
                stroke: #1d4ed8 !important;
                stroke-width: 2.6px !important;
            }
        """
    },
    {
        "id": "opt2_white_slate",
        "title": "시안 2: 순백색 캡슐 + 딥 다크 슬레이트 화살표 (#0F172A)",
        "desc": "순백색 캡슐에 먹색 화살표로 극대화된 흑백 명도 대비",
        "css": """
            #mobileRefreshBtn {
                background-color: #ffffff !important;
                border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25), 0 1px 2px rgba(0, 0, 0, 0.1) !important;
                border-radius: 0.75rem !important;
            }
            #mobileRefreshBtn svg, #mobileRefreshBtn i {
                color: #0f172a !important;
                stroke: #0f172a !important;
                stroke-width: 2.6px !important;
            }
        """
    },
    {
        "id": "opt3_ice_blue",
        "title": "시안 3: 아이스 스카이 캡슐 + 비비드 블루 화살표 (#0284C7)",
        "desc": "연한 하늘빛 캡슐로 은은한 발광감과 산뜻한 청량감 제공",
        "css": """
            #mobileRefreshBtn {
                background-color: #f0f9ff !important;
                border: 1.5px solid #bae6fd !important;
                box-shadow: 0 2px 8px rgba(2, 132, 199, 0.28) !important;
                border-radius: 0.75rem !important;
            }
            #mobileRefreshBtn svg, #mobileRefreshBtn i {
                color: #0284c7 !important;
                stroke: #0284c7 !important;
                stroke-width: 2.6px !important;
            }
        """
    }
]

with sync_playwright() as p:
    iphone = p.devices['iPhone 15 Pro']
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu'])
    context = browser.new_context(**iphone)
    page = context.new_page()
    page.goto(html_path, wait_until='domcontentloaded')
    page.wait_for_timeout(300)
    page.click('#splashSkipBtn')
    page.wait_for_timeout(300)
    
    crops = {}
    header_crops = {}
    
    for opt in options:
        # inject style
        page.evaluate(f"""() => {{
            let s = document.getElementById('test-opt-style');
            if (!s) {{
                s = document.createElement('style');
                s.id = 'test-opt-style';
                document.head.appendChild(s);
            }}
            s.innerHTML = `{opt['css']}`;
        }}""")
        page.wait_for_timeout(200)
        
        # Capture button crop
        btn = page.locator('#mobileRefreshBtn')
        btn_path = os.path.join(output_dir, f"btn_{opt['id']}.png")
        btn.screenshot(path=btn_path)
        crops[opt['id']] = btn_path
        
        # Capture header row crop
        header = page.locator('#gnbNavBar')
        header_path = os.path.join(output_dir, f"header_{opt['id']}.png")
        header.screenshot(path=header_path)
        header_crops[opt['id']] = header_path
        print(f"Captured {opt['id']}")
        
    browser.close()

# Create collage comparison
# 4 rows: for each option, show Button Crop (zoomed x2) + Header Row
card_w = 750
row_h = 130
total_h = row_h * 4 + 80
canvas = Image.new('RGB', (card_w, total_h), (15, 23, 42))
draw = ImageDraw.Draw(canvas)

draw.text((20, 15), "모바일 상단 새로고침 버튼 밝은 컬러 & 내부 화살표 선명도 시안 비교", fill=(255, 255, 255))

y = 55
for i, opt in enumerate(options):
    header_img = Image.open(header_crops[opt['id']]).convert('RGB')
    btn_img = Image.open(crops[opt['id']]).convert('RGB')
    
    # Scale header image to fit right side (width ~460px)
    hw = 480
    hh = int(header_img.height * (hw / header_img.width))
    r_header = header_img.resize((hw, hh), Image.Resampling.LANCZOS)
    
    # Scale button image (zoomed)
    bw = 64
    bh = 64
    r_btn = btn_img.resize((bw, bh), Image.Resampling.LANCZOS)
    
    # Row background box
    bg_color = (30, 41, 59) if i == 0 else (24, 34, 53)
    if i == 1:
        bg_color = (20, 45, 80) # Highlight recommended
    draw.rectangle([15, y, card_w - 15, y + row_h - 10], fill=bg_color, outline=(71, 85, 105), width=1)
    
    # Title & text
    title_color = (248, 113, 113) if i == 0 else ((56, 189, 248) if i == 1 else (226, 232, 240))
    draw.text((25, y + 8), opt['title'], fill=title_color)
    draw.text((25, y + 30), opt['desc'], fill=(148, 163, 184))
    
    # Paste Zoomed Button
    canvas.paste(r_btn, (25, y + 50))
    draw.rectangle([25, y + 50, 25 + bw, y + 50 + bh], outline=(255, 255, 255), width=1)
    draw.text((95, y + 68), "확대 아이콘", fill=(148, 163, 184))
    
    # Paste Header Context
    canvas.paste(r_header, (240, y + 50 - (hh - bh)//2))
    
    y += row_h

comp_path = os.path.join(output_dir, "refresh_button_brightness_comparison.png")
canvas.save(comp_path)
print(f"Comparison collage saved to: {comp_path}")
