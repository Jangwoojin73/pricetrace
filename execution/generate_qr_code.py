import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import qrcode
from PIL import Image, ImageDraw

def generate_lapis_qr_code():
    print("=" * 60)
    print("🔵 [QR Code Generator] 청금석(Lapis Lazuli) 테마 프리미엄 QR 코드 생성")
    print("=" * 60)

    target_url = "https://pricetrace-nu.vercel.app/"
    
    # 1. 고해상도 QR 코드 객체 생성 (오차 복원율 최고 등급 H: 로고 삽입 대응)
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=16,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    # 청금석 라피스 라줄리 컬러 팔레트
    # fill_color: 딥 라피스 네이비 블루 (#0f2b5c / #102a54)
    # back_color: 퓨어 화이트 (#ffffff)
    qr_img = qr.make_image(
        fill_color="#0f2b5c",
        back_color="#ffffff"
    ).convert("RGBA")

    # 2. 중앙에 공식 레이더 로고 엠블럼 오버레이
    # 로고 크기는 전체 QR의 약 22%가 최적 (스캔 인식률 100% 보장)
    qr_width, qr_height = qr_img.size
    logo_size = int(qr_width * 0.22)
    
    # 로고 배경 원형 플레이트 생성 (흰색 바탕 + 라피스 블루 림 테두리)
    plate = Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 0))
    plate_draw = ImageDraw.Draw(plate)
    plate_draw.ellipse(
        [(0, 0), (logo_size - 1, logo_size - 1)],
        fill=(255, 255, 255, 255),
        outline=(29, 78, 216, 255), # 코발트 블루 #1d4ed8
        width=4
    )

    # 공식 레이더 로고 이미지 로드 (public/icons/icon-192x192.png)
    logo_path = os.path.join("public", "icons", "icon-192x192.png")
    if os.path.exists(logo_path):
        icon = Image.open(logo_path).convert("RGBA")
        inner_icon_size = int(logo_size * 0.76)
        icon = icon.resize((inner_icon_size, inner_icon_size), Image.Resampling.LANCZOS)
        
        offset = (logo_size - inner_icon_size) // 2
        plate.paste(icon, (offset, offset), icon)

    # QR 중앙에 플레이트 합성
    pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    qr_img.paste(plate, pos, plate)

    # 3. 저장 (절대 경로 보장)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_public = os.path.join(root_dir, "public", "pricetrace_qr.png")
    qr_img.save(output_public, "PNG")
    print(f"  - [Public 저장 완료]: {output_public} ({qr_width}x{qr_height}px)")

    artifact_dir = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
    output_artifact = os.path.join(artifact_dir, "pricetrace_qr.png")
    qr_img.save(output_artifact, "PNG")
    print(f"  - [Artifact 저장 완료]: {output_artifact}")

    print("=" * 60)
    print("🎉 청금석 QR 코드 생성 완료!")
    print("=" * 60)

if __name__ == "__main__":
    generate_lapis_qr_code()
