import os
import sys
import time
from playwright.sync_api import sync_playwright
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX_FILE = os.path.join(BASE_DIR, "public", "index.html")
FILE_URL = f"file:///{INDEX_FILE.replace(os.sep, '/')}"

def main():
    print(f"Loading {FILE_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. iPhone 15 Pro (393 x 852)
        iphone = p.devices['iPhone 15 Pro']
        ctx1 = browser.new_context(**iphone)
        page1 = ctx1.new_page()
        page1.goto(FILE_URL)
        page1.wait_for_load_state("load")
        time.sleep(1)

        # Force dismiss splash if present
        page1.evaluate("""() => {
            const splash = document.getElementById('appSplashScreen');
            if (splash) splash.classList.add('splash-hidden');
            window.scrollTo(0, document.body.scrollHeight);
        }""")
        time.sleep(1)

        iphone_path = os.path.join(ARTIFACT_DIR, "audit_footer_mobile_iphone15.png")
        page1.screenshot(path=iphone_path)
        print(f"Captured: {iphone_path}")

        # 2. Galaxy S24 (412 x 915)
        ctx2 = browser.new_context(
            viewport={'width': 412, 'height': 915},
            device_scale_factor=2.6,
            is_mobile=True,
            has_touch=True
        )
        page2 = ctx2.new_page()
        page2.goto(FILE_URL)
        page2.wait_for_load_state("load")
        time.sleep(1)

        page2.evaluate("""() => {
            const splash = document.getElementById('appSplashScreen');
            if (splash) splash.classList.add('splash-hidden');
            window.scrollTo(0, document.body.scrollHeight);
        }""")
        time.sleep(1)

        galaxy_path = os.path.join(ARTIFACT_DIR, "audit_footer_mobile_galaxy_s24.png")
        page2.screenshot(path=galaxy_path)
        print(f"Captured: {galaxy_path}")

        browser.close()

    print("Creating comparison image...")

    # 3. Create Side-by-side comparison with user's uploaded image
    user_img_path = os.path.join(ARTIFACT_DIR, ".user_uploaded", "media_1792481632377_240a2f55.png")
    if os.path.exists(user_img_path):
        u_im = Image.open(user_img_path)
        # Crop footer region of user image (bottom 480px)
        u_crop = u_im.crop((0, u_im.height - 480, u_im.width, u_im.height))

        # Crop footer region of new iPhone image (bottom 480 CSS px -> ~1440 physical px)
        n_im = Image.open(iphone_path)
        crop_h = min(n_im.height, 1440)
        n_crop = n_im.crop((0, n_im.height - crop_h, n_im.width, n_im.height))

        # Resize both to width 420
        w = 420
        u_h = int(u_crop.height * (w / u_crop.width))
        n_h = int(n_crop.height * (w / n_crop.width))

        u_resized = u_crop.resize((w, u_h), Image.Resampling.LANCZOS)
        n_resized = n_crop.resize((w, n_h), Image.Resampling.LANCZOS)

        max_h = max(u_h, n_h)
        comp = Image.new('RGB', (w * 2 + 20, max_h), (241, 245, 249))
        comp.paste(u_resized, (0, 0))
        comp.paste(n_resized, (w + 20, 0))

        comp_path = os.path.join(ARTIFACT_DIR, "audit_footer_before_after_comparison.png")
        comp.save(comp_path)
        print(f"Saved comparison: {comp_path}")

if __name__ == '__main__':
    main()
