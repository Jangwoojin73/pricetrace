# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-remote-fonts'])
    ctx = browser.new_context(
        viewport={'width': 393, 'height': 852},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X)'
    )
    page = ctx.new_page()
    page.add_init_script("sessionStorage.setItem('pricetrace_splash_seen', 'true');")
    page.goto('http://127.0.0.1:8080', wait_until='networkidle')
    page.wait_for_timeout(300)
    
    out_path = r'C:\Users\ROG\.gemini\antigravity\brain\1853f434-165f-4049-bb73-2739a84f7b41\capture_applied_header_up6px.png'
    page.screenshot(path=out_path, animations='disabled')
    print('Final verified capture saved to:', out_path)
    browser.close()
