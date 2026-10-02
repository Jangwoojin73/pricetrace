import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def verify():
    print("=" * 60)
    print("🔍 [Icon Verification] 토스트 및 바로가기 아이콘 실측 검증")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 412, "height": 915},
            user_agent="Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
        )
        page = context.new_page()

        # Track network requests
        icons_requested = []
        page.on("response", lambda res: icons_requested.append((res.url, res.status)) if any(x in res.url for x in ["icon", "logo", "favicon"]) else None)

        page.goto("http://127.0.0.1:8080/")
        page.wait_for_timeout(2000)

        # Trigger beforeinstallprompt for bottom banner
        page.evaluate("""() => {
            const event = new Event('beforeinstallprompt');
            event.prompt = async () => ({ outcome: 'accepted' });
            event.userChoice = Promise.resolve({ outcome: 'accepted' });
            window.dispatchEvent(event);
        }""")
        page.wait_for_timeout(2000)

        # 1. Check banner image source
        img_src = page.evaluate("() => document.querySelector('#pwaInstallBanner img') ? document.querySelector('#pwaInstallBanner img').src : null")
        print(f"  - 배너 이미지 URL: {img_src}")

        # 2. Check favicon link tags
        favicons = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('link[rel*="icon"]'));
            return links.map(l => ({ rel: l.rel, href: l.href }));
        }""")
        print("  - 파비콘/바로가기 링크 태그:")
        for f in favicons:
            print(f"    * [{f['rel']}] -> {f['href']}")

        # 3. Capture close-up of the banner element
        banner = page.locator("#pwaInstallBanner")
        if banner.is_visible():
            banner_shot = os.path.join(ARTIFACT_DIR, "proof_toast_icon_verified.png")
            banner.screenshot(path=banner_shot)
            print(f"  - 배너 클로즈업 캡처: {banner_shot}")

        # 4. Full screen mobile shot
        full_shot = os.path.join(ARTIFACT_DIR, "proof_mobile_toast_icon_verified.png")
        page.screenshot(path=full_shot)
        print(f"  - 모바일 전체 캡처: {full_shot}")

        browser.close()

    print("\n[네트워크 수신 아이콘 내역]:")
    for url, status in icons_requested:
        print(f"  {status} {url}")
    print("=" * 60)

if __name__ == "__main__":
    verify()
