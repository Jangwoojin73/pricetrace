import os, time, subprocess, urllib.request
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41"

# Check server
def ensure_server():
    try:
        urllib.request.urlopen("http://127.0.0.1:8080/api/status", timeout=1)
    except Exception:
        print("[*] Starting local server.py...")
        subprocess.Popen(["python", "server.py"], cwd=os.getcwd())
        time.sleep(2)

ensure_server()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-remote-fonts'])
    ctx = browser.new_context(viewport={'width': 393, 'height': 852})
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    page.goto('http://127.0.0.1:8080/?v=' + str(time.time()), wait_until='networkidle')
    page.wait_for_selector('.welcome-card', timeout=5000)
    time.sleep(1)
    
    metrics = page.evaluate('''() => {
        const cards = Array.from(document.querySelectorAll('.welcome-card'));
        if (!cards.length) return { count: 0 };
        const first = cards[0].getBoundingClientRect();
        const container = document.getElementById('welcomeCardsContainer').getBoundingClientRect();
        return {
            count: cards.length,
            cardWidth: Math.round(first.width),
            cardHeight: Math.round(first.height),
            containerHeight: Math.round(container.height),
            visibleCardsInViewport: (852 / (first.height + 16)).toFixed(1)
        };
    }''')
    print('Current Mobile Card Metrics:', metrics)
    
    # Capture current card section for visual reference
    ts = time.strftime("%H%M%S")
    cap_path = os.path.join(ARTIFACT_DIR, f"current_mobile_cards_{ts}.png")
    page.locator("#welcomeCardsContainer").screenshot(path=cap_path)
    print(f"[✓] Saved card section capture: {cap_path}")
    
    browser.close()
