# -*- coding: utf-8 -*-
import os, sys, time, subprocess, urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"
BASE_URL = "http://127.0.0.1:8080"
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server_proc = None

def is_server_up():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/status", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

try:
    if not is_server_up():
        print("[*] Starting local server.py on port 8080...")
        server_proc = subprocess.Popen([sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"])
        for _ in range(15):
            time.sleep(0.4)
            if is_server_up():
                print("[✓] Server ready!")
                break

    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-remote-fonts"
    ]

    ts = time.strftime("%H%M%S")
    snap_mobile = os.path.join(ARTIFACT_DIR, f"verify_magazine_cards_mobile_{ts}.png")
    snap_mobile_closeup = os.path.join(ARTIFACT_DIR, f"verify_magazine_cards_mobile_closeup_{ts}.png")
    snap_hotdeal_mobile = os.path.join(ARTIFACT_DIR, f"verify_magazine_cards_hotdeal_mobile_{ts}.png")
    snap_pc = os.path.join(ARTIFACT_DIR, f"verify_magazine_cards_pc_{ts}.png")

    with sync_playwright() as p:
        # 1. 모바일 뷰포트 실측 (393x852)
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        m_ctx = browser.new_context(viewport={"width": 393, "height": 852})
        m_page = m_ctx.new_page()
        m_page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        
        m_page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        m_page.wait_for_selector(".welcome-card", timeout=8000)
        time.sleep(1)

        mobile_metrics = m_page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll('.welcome-card'));
            if (!cards.length) return { found: false };
            const first = cards[0];
            const rect = first.getBoundingClientRect();
            const imgBox = first.querySelector('div.shrink-0 > div');
            const imgRect = imgBox ? imgBox.getBoundingClientRect() : null;
            const container = document.getElementById('welcomeCardsContainer').getBoundingClientRect();
            
            return {
                found: true,
                measuredAt: new Date().toLocaleTimeString('ko-KR'),
                cardCount: cards.length,
                cardWidth: Math.round(rect.width),
                cardHeight: Math.round(rect.height),
                thumbWidth: imgRect ? Math.round(imgRect.width) : 0,
                thumbHeight: imgRect ? Math.round(imgRect.height) : 0,
                containerHeight: Math.round(container.height),
                visibleCardsInViewport: (852 / (rect.height + 10)).toFixed(1),
                firstTitle: first.querySelector('h3') ? first.querySelector('h3').innerText.trim() : '',
                firstPrice: first.querySelector('strong') ? first.querySelector('strong').innerText.trim() : ''
            };
        }''')
        print("Mobile Magazine Card Metrics (Steady):", mobile_metrics)

        # 캡처 1: 모바일 전체 뷰
        m_page.screenshot(path=snap_mobile)
        print(f"[✓] Saved Mobile screenshot: {snap_mobile} ({os.path.getsize(snap_mobile)} bytes)")

        # 캡처 2: 모바일 카드 섹션 클로즈업
        cards_elem = m_page.locator("#welcomeCardsContainer")
        cards_elem.screenshot(path=snap_mobile_closeup)
        print(f"[✓] Saved Mobile Closeup screenshot: {snap_mobile_closeup} ({os.path.getsize(snap_mobile_closeup)} bytes)")

        # 핫딜 탭 클릭 테스트
        m_page.click("#tabTrendingBtn")
        time.sleep(0.8)
        m_page.wait_for_selector(".welcome-card", timeout=5000)
        cards_elem.screenshot(path=snap_hotdeal_mobile)
        print(f"[✓] Saved Hotdeal Mobile screenshot: {snap_hotdeal_mobile} ({os.path.getsize(snap_hotdeal_mobile)} bytes)")

        m_ctx.close()

        # 2. PC 데스크톱 뷰포트 실측 (1440x900)
        pc_ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        pc_page = pc_ctx.new_page()
        pc_page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
        pc_page.goto(f"{BASE_URL}/?v={time.time()}", wait_until="networkidle", timeout=15000)
        pc_page.wait_for_selector(".welcome-card", timeout=8000)
        time.sleep(1)

        pc_metrics = pc_page.evaluate('''() => {
            const cards = Array.from(document.querySelectorAll('.welcome-card'));
            if (!cards.length) return { found: false };
            const first = cards[0];
            const rect = first.getBoundingClientRect();
            return {
                cardCount: cards.length,
                cardWidth: Math.round(rect.width),
                cardHeight: Math.round(rect.height),
                firstTitle: first.querySelector('h3') ? first.querySelector('h3').innerText.trim() : ''
            };
        }''')
        print("PC Desktop Card Metrics:", pc_metrics)

        pc_page.screenshot(path=snap_pc)
        print(f"[✓] Saved PC screenshot: {snap_pc} ({os.path.getsize(snap_pc)} bytes)")

        pc_ctx.close()
        browser.close()

finally:
    if server_proc:
        try:
            server_proc.terminate()
        except Exception:
            pass
