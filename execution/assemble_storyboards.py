# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

font_title = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 22)
font_label = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 15)
font_desc = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 13)
font_small = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 12)

def fit_w(img, w):
    h = int(img.height * (w / img.width))
    return img.resize((w, h), Image.Resampling.LANCZOS)

# =========================================================================
# CARD 1: Pull-to-Refresh 5대 단계별 전 과정 실측 스토리보드
# =========================================================================
p_s1 = os.path.join(ARTIFACT_DIR, "step1_1_idle_crop.png")
p_s2 = os.path.join(ARTIFACT_DIR, "step1_2_pulling_35px_crop.png")
p_s3 = os.path.join(ARTIFACT_DIR, "step1_3_threshold_crop.png")
p_s4 = os.path.join(ARTIFACT_DIR, "step1_4_refreshing_crop.png")
p_s5 = os.path.join(ARTIFACT_DIR, "step1_5_restored_crop.png")

imgs_ptr = [
    ("Step 1. 평상시 기본 대기 (Idle)", (30, 41, 59), fit_w(Image.open(p_s1), 220), "간격 24px | 은닉: 100%"),
    ("Step 2. 아래로 당김 (Pull 35px)", (14, 116, 144), fit_w(Image.open(p_s2), 220), "헤더고정 | 캡슐출현"),
    ("Step 3. 임계치 도달 (Pull 65px)", (217, 119, 6), fit_w(Image.open(p_s3), 220), "화살표 180° 회전"),
    ("Step 4. 갱신 실행 중 (Refreshing)", (225, 29, 72), fit_w(Image.open(p_s4), 220), "회전 스피너 작동"),
    ("Step 5. 탄성 복귀 완료 (Restored)", (5, 150, 105), fit_w(Image.open(p_s5), 220), "원위치 복귀 | 은닉 0px")
]

card1_w = (220 * 5) + (20 * 6) # 1100 + 120 = 1220
max_ptr_h = max(img.height for _, _, img, _ in imgs_ptr)
card1_h = 110 + max_ptr_h + 120

c1 = Image.new("RGB", (card1_w, card1_h), color=(15, 23, 42))
d1 = ImageDraw.Draw(c1)

# Header
d1.rounded_rectangle([20, 15, card1_w - 20, 85], radius=10, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
d1.text((35, 25), "■ 상단 고정 헤더 & 히어로 섹션 Pull-to-Refresh 단계별 전 과정 실측 스토리보드 (Step 1 ~ Step 5)", font=font_title, fill=(248, 250, 252))
d1.text((35, 55), "✔ 헤더 0px 고정 | ✔ 평상시 100% 완전 은닉(간격 24px) | ✔ 터치 풀다운 시만 플로팅 등장 | ✔ 손을 놓으면 탄성 복귀", font=font_desc, fill=(148, 163, 184))

x_cursor = 20
for title, color, img, sub in imgs_ptr:
    # Tag
    d1.rounded_rectangle([x_cursor, 98, x_cursor + 220, 134], radius=6, fill=color)
    d1.text((x_cursor + 10, 104), title, font=font_label, fill=(255, 255, 255))
    
    # Image
    img_y = 142
    d1.rounded_rectangle([x_cursor - 2, img_y - 2, x_cursor + 222, img_y + img.height + 2], radius=8, fill=(30, 41, 59), outline=(71, 85, 105), width=2)
    c1.paste(img, (x_cursor, img_y))
    
    # Sub
    d1.text((x_cursor + 5, img_y + img.height + 8), sub, font=font_small, fill=(203, 213, 225))
    x_cursor += 240

card1_path = os.path.join(ARTIFACT_DIR, "storyboard_ptr_5stages.png")
c1.save(card1_path, quality=95)
print("Storyboard 1 saved:", card1_path)

# =========================================================================
# CARD 2: 하단 네비게이션 독 5대 탭 최적화 & 태블릿 기기 실측 스토리보드
# =========================================================================
p_n1 = os.path.join(ARTIFACT_DIR, "step2_1_nav_dock_default.png")
p_n2 = os.path.join(ARTIFACT_DIR, "step2_2_nav_steady_active.png")
p_n3 = os.path.join(ARTIFACT_DIR, "step2_3_nav_hotdeal_active.png")
p_t1 = os.path.join(ARTIFACT_DIR, "step3_1_tablet_mini_dock.png")
p_t2 = os.path.join(ARTIFACT_DIR, "step3_2_tablet_pro11_dock.png")

im_n1 = fit_w(Image.open(p_n1), 540)
im_n2 = fit_w(Image.open(p_n2), 540)
im_n3 = fit_w(Image.open(p_n3), 540)
im_t1 = fit_w(Image.open(p_t1), 540)
im_t2 = fit_w(Image.open(p_t2), 540)

card2_w = 1160
card2_h = 100 + (im_n1.height + 55) * 3 + 80
c2 = Image.new("RGB", (card2_w, card2_h), color=(15, 23, 42))
d2 = ImageDraw.Draw(c2)

d2.rounded_rectangle([20, 15, card2_w - 20, 85], radius=10, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
d2.text((35, 25), "■ 하단 네비게이션 독 5대 탭 최적화 & 모바일·태블릿 크로스 실측 스토리보드", font=font_title, fill=(248, 250, 252))
d2.text((35, 55), "✔ 생필품·핫딜 48px -> 25px 축소 및 독 내부 안착 | ✔ 5개 탭 바닥면 오차 0.0px | ✔ iPad Mini & Pro11 동일 적용", font=font_desc, fill=(148, 163, 184))

# Left Column (Mobile 3 states)
y_cur = 98
def render_row(d, canvas, x, y, title, color, img, spec):
    d.rounded_rectangle([x, y, x + 540, y + 36], radius=6, fill=color)
    d.text((x + 12, y + 8), title, font=font_label, fill=(255, 255, 255))
    d.text((x + 360, y + 10), spec, font=font_small, fill=(255, 255, 255))
    img_y = y + 42
    d.rounded_rectangle([x - 2, img_y - 2, x + 542, img_y + img.height + 2], radius=8, fill=(30, 41, 59), outline=(71, 85, 105), width=1)
    canvas.paste(img, (x, img_y))
    return img_y + img.height + 14

# Left: Nav Mobile
y1 = render_row(d2, c2, 25, 100, "① 하단 독 기본 정렬 (Default)", (37, 99, 235), im_n1, "돌출 0.0px | 바닥 844px 일치")
y1 = render_row(d2, c2, 25, y1, "② [생필품] 탭 선택 활성화 (Steady Active)", (5, 150, 105), im_n2, "에메랄드 캡슐(#ecfdf5)")
y1 = render_row(d2, c2, 25, y1, "③ [핫딜] 탭 선택 활성화 (Hotdeal Active)", (225, 29, 72), im_n3, "로즈 캡슐(#fff1f2)")

# Right: Tablet
y2 = render_row(d2, c2, 595, 100, "④ 태블릿 (iPad Mini, 768 × 1024)", (13, 148, 136), im_t1, "독 높이 75px | 뱃지 25x25px")
y2 = render_row(d2, c2, 595, y2, "⑤ 태블릿 (iPad Pro 11, 834 × 1194)", (124, 58, 237), im_t2, "독 높이 75px | 뱃지 25x25px")

card2_path = os.path.join(ARTIFACT_DIR, "storyboard_bottom_nav_and_tablet.png")
c2.save(card2_path, quality=95)
print("Storyboard 2 saved:", card2_path)
