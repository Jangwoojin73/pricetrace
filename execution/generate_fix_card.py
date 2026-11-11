# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

err_path = os.path.join(ARTIFACT_DIR, r".user_uploaded\media_1794358879626_7536a1a9.jpg")
fixed_path = os.path.join(ARTIFACT_DIR, "mobile_main_clean_fixed.png")

im_err = Image.open(err_path)
im_fixed = Image.open(fixed_path)

font_title = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 22)
font_label = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 17)
font_desc = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 14)

target_w = 420
def resize_w(img, w):
    h = int(img.height * (w / img.width))
    return img.resize((w, h), Image.Resampling.LANCZOS)

img_err_r = resize_w(im_err, target_w)
img_fixed_r = resize_w(im_fixed, target_w)

max_h = max(img_err_r.height, img_fixed_r.height)

card_w = (target_w * 2) + 70
card_h = 130 + max_h + 100

canvas = Image.new("RGB", (card_w, card_h), color=(15, 23, 42))
draw = ImageDraw.Draw(canvas)

# Title Banner
draw.rounded_rectangle([25, 20, card_w - 25, 105], radius=12, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
draw.text((45, 32), "모바일 메인 화면 PTR 인디케이터 노출 오류 즉시 긴급 교정 완료", font=font_title, fill=(248, 250, 252))
draw.text((45, 68), "✔ 인디케이터 main 외부 분리 | ✔ 평상시 display: none 100% 완전 은닉 | ✔ 헤더-히어로 간격 96px -> 24px 정상 복구", font=font_desc, fill=(148, 163, 184))

# Left: Error (User Report)
x_left = 25
draw.rounded_rectangle([x_left, 120, x_left + target_w, 165], radius=8, fill=(225, 29, 72))
draw.text((x_left + 15, 130), "① [오류 상태] 인디케이터 노출 & 96px 빈 공간", font=font_label, fill=(255, 255, 255))
canvas.paste(img_err_r, (x_left, 175))

# Right: Fixed Clean
x_right = x_left + target_w + 20
draw.rounded_rectangle([x_right, 120, x_right + target_w, 165], radius=8, fill=(5, 150, 105))
draw.text((x_right + 15, 130), "② [수정 완료] 100% 완전 은닉 & 24px 정상 간격 복구", font=font_label, fill=(255, 255, 255))
canvas.paste(img_fixed_r, (x_right, 175))

# Bottom footer explanation
foot_y = 175 + max_h + 15
draw.rounded_rectangle([25, foot_y, card_w - 25, foot_y + 65], radius=10, fill=(30, 41, 59), outline=(71, 85, 105), width=1)
draw.text((45, foot_y + 12), "원인: PTR 인디케이터가 main 내부 자식으로 위치해 평상시에도 노출 및 32px 추가 마진 발생", font=font_desc, fill=(244, 63, 94))
draw.text((45, foot_y + 36), "해결: main 외부로 완전 격리 및 display: none !important 강제, 평상시 0.0px 점유율 및 완벽한 초기 뷰 복원", font=font_desc, fill=(52, 211, 153))

out_path = os.path.join(ARTIFACT_DIR, "compare_ptr_error_vs_fixed.png")
canvas.save(out_path, quality=95)
print("Comparison card created successfully:", out_path)
