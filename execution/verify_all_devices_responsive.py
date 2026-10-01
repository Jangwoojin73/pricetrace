import os
import sys
import json
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

DEVICES = [
    {
        "id": "iphone_14_pro",
        "name": "아이폰 iOS (iPhone 14/15 Pro)",
        "viewport": {"width": 393, "height": 852},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "is_mobile": True,
        "has_touch": True
    },
    {
        "id": "galaxy_s24",
        "name": "갤럭시 안드로이드 (Galaxy S24)",
        "viewport": {"width": 412, "height": 915},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "is_mobile": True,
        "has_touch": True
    },
    {
        "id": "ipad_pro_11",
        "name": "아이패드 iPadOS (iPad Pro 11)",
        "viewport": {"width": 834, "height": 1194},
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "is_mobile": True,
        "has_touch": True
    },
    {
        "id": "galaxy_tab_s8",
        "name": "갤럭시 탭 Android (Galaxy Tab S8)",
        "viewport": {"width": 800, "height": 1280},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "is_mobile": True,
        "has_touch": True
    },
    {
        "id": "pc_desktop",
        "name": "PC 데스크톱 (Wide Desktop)",
        "viewport": {"width": 1440, "height": 900},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "is_mobile": False,
        "has_touch": False
    }
]

def check_overflow(page):
    return page.evaluate("""() => {
        const docWidth = document.documentElement.scrollWidth;
        const winWidth = window.innerWidth;
        const bodyWidth = document.body ? document.body.scrollWidth : 0;
        const overflow = docWidth > winWidth || bodyWidth > winWidth;
        return {
            overflow: overflow,
            docWidth: docWidth,
            winWidth: winWidth,
            bodyWidth: bodyWidth,
            diff: Math.max(docWidth, bodyWidth) - winWidth
        };
    }""")

def run_responsive_audit():
    print("=" * 70)
    print("📱 [Multi-Device Audit] 모바일/태블릿/PC 5대 환경 반응형 전수 점검")
    print("=" * 70)

    report = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for dev in DEVICES:
            print(f"\n▶ [{dev['name']}] (Viewport: {dev['viewport']['width']}x{dev['viewport']['height']}) 점검 중...")
            
            context = browser.new_context(
                viewport=dev["viewport"],
                user_agent=dev["user_agent"],
                is_mobile=dev["is_mobile"],
                has_touch=dev["has_touch"]
            )
            page = context.new_page()

            # 1. Welcome View Test
            page.goto("http://127.0.0.1:8080/")
            page.wait_for_timeout(1500)

            # Trigger beforeinstallprompt simulation for Android & PC
            if not "iPhone" in dev["user_agent"] and not "iPad" in dev["user_agent"]:
                page.evaluate("""() => {
                    const event = new Event('beforeinstallprompt');
                    event.prompt = async () => ({ outcome: 'accepted' });
                    event.userChoice = Promise.resolve({ outcome: 'accepted' });
                    window.dispatchEvent(event);
                }""")
                page.wait_for_timeout(500)

            welcome_overflow = check_overflow(page)
            print(f"  - Welcome View 가로 오버플로우: {welcome_overflow['overflow']} (diff: {welcome_overflow['diff']}px)")

            welcome_shot = os.path.join(ARTIFACT_DIR, f"proof_responsive_{dev['id']}_welcome.png")
            page.screenshot(path=welcome_shot, full_page=False)

            # 2. Result View Test (농심 신라면 20개 검색)
            page.goto("http://127.0.0.1:8080/?q=%EB%8F%84%EC%8B%AC%20%EC%8B%A0%EB%9D%BC%EB%A9%B4%20%EB%B4%89%EC%A7%80%2020%EA%B0%9C%EC%9E%85")
            page.wait_for_timeout(2500)

            result_overflow = check_overflow(page)
            print(f"  - Result View 가로 오버플로우: {result_overflow['overflow']} (diff: {result_overflow['diff']}px)")

            result_shot = os.path.join(ARTIFACT_DIR, f"proof_responsive_{dev['id']}_result.png")
            page.screenshot(path=result_shot, full_page=False)

            dev_result = {
                "id": dev["id"],
                "name": dev["name"],
                "viewport": f"{dev['viewport']['width']}x{dev['viewport']['height']}",
                "welcome_overflow": welcome_overflow["overflow"],
                "welcome_diff": welcome_overflow["diff"],
                "result_overflow": result_overflow["overflow"],
                "result_diff": result_overflow["diff"],
                "welcome_screenshot": welcome_shot,
                "result_screenshot": result_shot,
                "status": "PASS" if not welcome_overflow["overflow"] and not result_overflow["overflow"] else "FAIL"
            }
            report.append(dev_result)
            context.close()

        browser.close()

    print("\n" + "=" * 70)
    print("📊 [Multi-Device Audit Summary]")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("=" * 70)

if __name__ == "__main__":
    run_responsive_audit()
