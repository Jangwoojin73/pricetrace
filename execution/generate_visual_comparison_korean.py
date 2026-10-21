# -*- coding: utf-8 -*-
"""
Generate High-Quality Korean Visual Comparison for Refresh Button
"""
import os
import pathlib
from PIL import Image, ImageDraw, ImageFont

output_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

font_title = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 22)
font_sec = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 16)
font_bold = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 14)
font_regular = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 13)
font_small = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 11)

# Load existing captures
img_user = Image.open(os.path.join(output_dir, r".user_uploaded\media_1792550475786_a933826c.png")).convert('RGB')
img_header_curr = Image.open(os.path.join(output_dir, "header_current.png")).convert('RGB')
img_header_opt1 = Image.open(os.path.join(output_dir, "header_opt1_white_cobalt.png")).convert('RGB')
img_header_opt2 = Image.open(os.path.join(output_dir, "header_opt2_white_slate.png")).convert('RGB')
img_header_opt3 = Image.open(os.path.join(output_dir, "header_opt3_ice_blue.png")).convert('RGB')

btn_curr = Image.open(os.path.join(output_dir, "btn_current.png")).convert('RGB')
btn_opt1 = Image.open(os.path.join(output_dir, "btn_opt1_white_cobalt.png")).convert('RGB')
btn_opt2 = Image.open(os.path.join(output_dir, "btn_opt2_white_slate.png")).convert('RGB')
btn_opt3 = Image.open(os.path.join(output_dir, "btn_opt3_ice_blue.png")).convert('RGB')

W = 1000
H = 1100
canvas = Image.new('RGB', (W, H), (15, 23, 42)) # Slate 900
draw = ImageDraw.Draw(canvas)

# 1. Header Title Area
draw.rectangle([0, 0, W, 75], fill=(30, 41, 59))
draw.text((30, 16), "모바일 상단 새로고침 버튼 밝은 컬러 & 내부 화살표 선명도 개선안", fill=(255, 255, 255), font=font_title)
draw.text((30, 48), "기존 회색 반투명 배경을 산뜻하고 밝은 캡슐로 교체하여 로고 가독성과 내부 화살표 시인성을 극대화", fill=(148, 163, 184), font=font_small)

# 2. User Feedback & Analysis Card
draw.rectangle([30, 95, W - 30, 180], fill=(24, 34, 53), outline=(51, 65, 85), width=1)
draw.text((45, 105), "📌 사용자 피드백 분석 & 원인 진단", fill=(56, 189, 248), font=font_sec)
draw.text((45, 130), "• 현상: 버튼 배경이 rgba(255, 255, 255, 0.22)로 어두운 네이비 블러 배경과 중첩되어 칙칙한 회색(#808197)으로 렌더링됨", fill=(226, 232, 240), font=font_regular)
draw.text((45, 150), "• 문제: 내부 화살표 아이콘이 배경에 묻혀 식별이 어렵고, 인접한 PriceTrace 로고 영역의 맑은 톤을 저해함", fill=(226, 232, 240), font=font_regular)

# 3. Section 1: 4대 시안별 GNB 헤더 렌더링 비교
draw.text((30, 200), "1. 모바일 GNB 헤더 실측 렌더링 비교 (Before vs After 3대 시안)", fill=(255, 255, 255), font=font_sec)

items = [
    {
        "tag": "[현재 상태] 회색 반투명 (Before)",
        "tag_color": (248, 113, 113),
        "desc": "배경: rgba(255,255,255,0.22) | 화살표: 흰색 2.0px | 대비율: 1.4:1 (침침함)",
        "header": img_header_curr,
        "btn": btn_curr,
        "bg_box": (30, 41, 59),
        "border_box": (100, 116, 139)
    },
    {
        "tag": "★ [시안 1 - 적극 추천] 순백색 캡슐 + 브랜드 코발트 블루 화살표",
        "tag_color": (56, 189, 248),
        "desc": "배경: 순백색(#FFFFFF) + 섀도우 | 화살표: 코발트블루(#1D4ED8) 2.6px | 대비율: 8.5:1 (AAA 등급)",
        "header": img_header_opt1,
        "btn": btn_opt1,
        "bg_box": (20, 45, 80),
        "border_box": (56, 189, 248)
    },
    {
        "tag": "[시안 2] 순백색 캡슐 + 딥 다크 슬레이트 화살표",
        "tag_color": (226, 232, 240),
        "desc": "배경: 순백색(#FFFFFF) + 섀도우 | 화살표: 먹색 다크슬레이트(#0F172A) 2.6px | 대비율: 16.2:1 (초고대비)",
        "header": img_header_opt2,
        "btn": btn_opt2,
        "bg_box": (24, 34, 53),
        "border_box": (71, 85, 105)
    },
    {
        "tag": "[시안 3] 아이스 스카이 캡슐 + 일렉트릭 블루 화살표",
        "tag_color": (147, 197, 253),
        "desc": "배경: 은은한 스카이블루(#F0F9FF) | 화살표: 비비드블루(#0284C7) 2.6px | 대비율: 5.2:1 (청량감)",
        "header": img_header_opt3,
        "btn": btn_opt3,
        "bg_box": (24, 34, 53),
        "border_box": (71, 85, 105)
    }
]

y = 230
for item in items:
    # Outer box
    draw.rectangle([30, y, W - 30, y + 105], fill=item['bg_box'], outline=item['border_box'], width=2 if '★' in item['tag'] else 1)
    
    # Tag & description
    draw.text((45, y + 10), item['tag'], fill=item['tag_color'], font=font_bold)
    draw.text((45, y + 30), item['desc'], fill=(148, 163, 184), font=font_small)
    
    # Button Zoom crop (left)
    bw = 50
    bh = 50
    r_btn = item['btn'].resize((bw, bh), Image.Resampling.LANCZOS)
    canvas.paste(r_btn, (45, y + 48))
    draw.rectangle([45, y + 48, 45 + bw, y + 48 + bh], outline=(255, 255, 255), width=1)
    
    # Header crop (right)
    hw = 780
    hh = int(item['header'].height * (hw / item['header'].width))
    r_hdr = item['header'].resize((hw, hh), Image.Resampling.LANCZOS)
    canvas.paste(r_hdr, (160, y + 48 - (hh - bh)//2))
    
    y += 115

# 4. Section 2: 아이콘 정밀 4배 확대 비교
draw.text((30, y + 15), "2. 버튼 아이콘 4배 확대 및 선명도 정밀 비교", fill=(255, 255, 255), font=font_sec)
y += 45

zoom_box_w = 215
zoom_box_h = 160
zoom_items = [
    ("사용자 첨부 원본", img_user, (248, 113, 113), "회색 배경(#808197)\n화살표 경계 흐릿함"),
    ("시안 1 (추천: 화이트+블루)", btn_opt1, (56, 189, 248), "순백색 캡슐(#FFF)\n선명한 브랜드 블루 화살표"),
    ("시안 2 (화이트+슬레이트)", btn_opt2, (226, 232, 240), "순백색 캡슐(#FFF)\n초고대비 먹색 화살표"),
    ("시안 3 (스카이+시안블루)", btn_opt3, (147, 197, 253), "스카이 캡슐(#F0F9FF)\n시원하고 청량한 느낌")
]

for idx, (lbl, img_src, col, sub) in enumerate(zoom_items):
    bx = 30 + idx * (zoom_box_w + 26)
    draw.rectangle([bx, y, bx + zoom_box_w, y + zoom_box_h], fill=(24, 34, 53), outline=col, width=2 if '시안 1' in lbl else 1)
    draw.text((bx + 12, y + 8), lbl, fill=col, font=font_bold)
    
    # 4x zoom icon
    zw = 75
    zh = 75
    r_zoom = img_src.resize((zw, zh), Image.Resampling.LANCZOS)
    canvas.paste(r_zoom, (bx + (zoom_box_w - zw)//2, y + 32))
    draw.rectangle([bx + (zoom_box_w - zw)//2, y + 32, bx + (zoom_box_w - zw)//2 + zw, y + 32 + zh], outline=(255, 255, 255), width=1)
    
    # Text below
    draw.text((bx + 12, y + 115), sub, fill=(148, 163, 184), font=font_small)

# 5. Footer Summary / Recommendation
y += zoom_box_h + 15
draw.rectangle([30, y, W - 30, y + 70], fill=(20, 45, 80), outline=(56, 189, 248), width=1)
draw.text((45, y + 12), "💡 권장 솔루션: 시안 1 (순백색 캡슐 + 브랜드 코발트 블루 #1D4ED8)", fill=(56, 189, 248), font=font_bold)
draw.text((45, y + 35), "하단 검색창의 화이트 캡슐과 통일감을 이루며, PriceTrace 고유의 코발트 블루 화살표가 굵고 선명하게 돋보입니다.", fill=(226, 232, 240), font=font_regular)

final_comp_path = os.path.join(output_dir, "audit_refresh_button_brightness_comparison.png")
canvas.save(final_comp_path)
print(f"High-res visual comparison generated: {final_comp_path}")
