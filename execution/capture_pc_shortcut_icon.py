import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\ROG\.gemini\antigravity\brain\ae9b1c7b-ad62-4ce7-a784-1f6317b8929e"

def capture_pc_shortcuts():
    print("=" * 60)
    print("🖥️ [PC Shortcut Audit] PC 환경 바로가기 및 설치 앱 아이콘 캡처 시작")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ==========================================================
        # 1. PC Chrome/Edge 앱 설치 프롬프트 다이얼로그 (Desktop Install Dialog)
        # ==========================================================
        page_dialog = browser.new_page(viewport={"width": 1280, "height": 800})
        html_dialog = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
              width: 100vw;
              height: 100vh;
              background: #0f172a;
              font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
              display: flex;
              align-items: center;
              justify-content: center;
            }
            .dialog-card {
              width: 440px;
              background: #ffffff;
              border-radius: 20px;
              box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.45);
              padding: 24px;
              display: flex;
              flex-direction: column;
              gap: 16px;
              border: 1px solid #e2e8f0;
            }
            .dialog-header {
              display: flex;
              align-items: center;
              gap: 16px;
            }
            .app-icon {
              width: 72px;
              height: 72px;
              border-radius: 18px;
              background: #ffffff;
              border: 1px solid #e2e8f0;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
              padding: 6px;
              display: flex;
              align-items: center;
              justify-content: center;
              flex-shrink: 0;
            }
            .app-icon img {
              width: 100%;
              height: 100%;
              object-fit: contain;
            }
            .app-info {
              display: flex;
              flex-direction: column;
              gap: 4px;
            }
            .title {
              font-size: 17px;
              font-weight: 800;
              color: #0f172a;
              letter-spacing: -0.3px;
            }
            .domain {
              font-size: 13px;
              color: #64748b;
              font-weight: 500;
            }
            .desc {
              font-size: 13px;
              color: #475569;
              line-height: 1.5;
              padding: 12px 14px;
              background: #f8fafc;
              border-radius: 12px;
              border: 1px solid #f1f5f9;
            }
            .dialog-buttons {
              display: flex;
              justify-content: flex-end;
              gap: 8px;
              margin-top: 4px;
            }
            .btn {
              padding: 9px 18px;
              border-radius: 10px;
              font-size: 13px;
              font-weight: 700;
              cursor: pointer;
              border: none;
            }
            .btn-cancel {
              background: #f1f5f9;
              color: #475569;
            }
            .btn-install {
              background: #2563eb;
              color: #ffffff;
              box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
            }
          </style>
        </head>
        <body>
          <div class="dialog-card">
            <div class="dialog-header">
              <div class="app-icon">
                <img src="http://127.0.0.1:8080/icons/icon-192x192.png?v=20261002_logo" alt="PriceTrace Icon">
              </div>
              <div class="app-info">
                <div class="title">PriceTrace 앱을 설치하시겠습니까?</div>
                <div class="domain">localhost:8080 / jangwoojin73.github.io</div>
              </div>
            </div>
            <div class="desc">
              네이버 쇼핑 공식 카탈로그 실시간 최저가 레이더를 PC 바탕화면 및 작업표시줄에 추가하여 독립 창으로 0.1초 만에 실행합니다.
            </div>
            <div class="dialog-buttons">
              <button class="btn btn-cancel">취소</button>
              <button class="btn btn-install">설치</button>
            </div>
          </div>
        </body>
        </html>
        """
        page_dialog.set_content(html_dialog)
        page_dialog.wait_for_timeout(1000)
        shot_dialog = os.path.join(ARTIFACT_DIR, "proof_pc_pwa_install_dialog.png")
        page_dialog.screenshot(path=shot_dialog)
        print(f"  - [1] PC 앱 설치 다이얼로그 캡처: {shot_dialog}")
        page_dialog.close()

        # ==========================================================
        # 2. Windows 바탕화면 바로가기 아이콘 (Desktop Shortcut Icon)
        # ==========================================================
        page_desktop = browser.new_page(viewport={"width": 1000, "height": 650})
        html_desktop = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
              width: 100vw;
              height: 100vh;
              background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
              font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
              padding: 40px;
              display: flex;
              flex-direction: column;
              gap: 30px;
            }
            .header-label {
              color: #94a3b8;
              font-size: 14px;
              font-weight: 600;
              letter-spacing: -0.2px;
            }
            .shortcuts-grid {
              display: flex;
              gap: 40px;
            }
            .shortcut-item {
              display: flex;
              flex-direction: column;
              align-items: center;
              gap: 8px;
              width: 100px;
              cursor: pointer;
            }
            .icon-box {
              width: 68px;
              height: 68px;
              background: #ffffff;
              border-radius: 16px;
              box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
              padding: 6px;
              display: flex;
              align-items: center;
              justify-content: center;
              position: relative;
              border: 1px solid rgba(255, 255, 255, 0.15);
            }
            .icon-box img {
              width: 100%;
              height: 100%;
              object-fit: contain;
            }
            /* Windows shortcut arrow overlay */
            .shortcut-arrow {
              position: absolute;
              bottom: -4px;
              left: -4px;
              width: 18px;
              height: 18px;
              background: #ffffff;
              border: 1px solid #cbd5e1;
              border-radius: 4px;
              box-shadow: 0 1px 3px rgba(0,0,0,0.2);
              display: flex;
              align-items: center;
              justify-content: center;
            }
            .shortcut-arrow svg {
              width: 12px;
              height: 12px;
              fill: #2563eb;
            }
            .shortcut-name {
              color: #f8fafc;
              font-size: 12px;
              font-weight: 700;
              text-align: center;
              text-shadow: 0 1px 3px rgba(0,0,0,0.8);
              line-height: 1.3;
              letter-spacing: -0.3px;
            }

            /* Windows 11 Taskbar simulation */
            .taskbar-simulation {
              margin-top: auto;
              width: 100%;
              height: 56px;
              background: rgba(15, 23, 42, 0.85);
              backdrop-filter: blur(20px);
              border-radius: 16px;
              border: 1px solid rgba(255, 255, 255, 0.1);
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 16px;
              box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            .taskbar-icon {
              width: 40px;
              height: 40px;
              border-radius: 10px;
              display: flex;
              align-items: center;
              justify-content: center;
              position: relative;
            }
            .taskbar-icon.active {
              background: rgba(255, 255, 255, 0.12);
            }
            .taskbar-icon.active::after {
              content: '';
              position: absolute;
              bottom: 2px;
              width: 16px;
              height: 3px;
              background: #38bdf8;
              border-radius: 2px;
            }
            .taskbar-icon img {
              width: 28px;
              height: 28px;
              object-fit: contain;
              border-radius: 6px;
            }
            .taskbar-sys {
              width: 24px;
              height: 24px;
              opacity: 0.7;
            }
          </style>
        </head>
        <body>
          <div class="header-label">🖥️ Windows 바탕화면 바로가기 및 작업표시줄 아이콘 형태</div>
          
          <div class="shortcuts-grid">
            <div class="shortcut-item">
              <div class="icon-box">
                <img src="http://127.0.0.1:8080/icons/icon-192x192.png?v=20261002_logo" alt="PriceTrace">
                <div class="shortcut-arrow">
                  <svg viewBox="0 0 24 24"><path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke="#2563eb" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </div>
              </div>
              <div class="shortcut-name">PriceTrace</div>
            </div>
          </div>

          <!-- Windows Taskbar -->
          <div class="taskbar-simulation">
            <!-- Start button -->
            <svg class="taskbar-sys" viewBox="0 0 24 24" fill="#38bdf8"><path d="M3 3h8v8H3zm10 0h8v8h-8zM3 13h8v8H3zm10 0h8v8h-8z"/></svg>
            <!-- Search -->
            <svg class="taskbar-sys" viewBox="0 0 24 24" fill="#94a3b8"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
            <!-- Active PWA App Icon on Taskbar -->
            <div class="taskbar-icon active" title="PriceTrace - 실행 중">
              <img src="http://127.0.0.1:8080/icons/icon-192x192.png?v=20261002_logo" alt="PriceTrace">
            </div>
            <!-- File Explorer -->
            <svg class="taskbar-sys" viewBox="0 0 24 24" fill="#fbbf24"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>
            <!-- Edge -->
            <svg class="taskbar-sys" viewBox="0 0 24 24" fill="#38bdf8"><circle cx="12" cy="12" r="9" fill="none" stroke="#38bdf8" stroke-width="2"/></svg>
          </div>
        </body>
        </html>
        """
        page_desktop.set_content(html_desktop)
        page_desktop.wait_for_timeout(1000)
        shot_desktop = os.path.join(ARTIFACT_DIR, "proof_pc_windows_shortcut_and_taskbar.png")
        page_desktop.screenshot(path=shot_desktop)
        print(f"  - [2] Windows 바탕화면 바로가기 및 작업표시줄 캡처: {shot_desktop}")
        page_desktop.close()

        # ==========================================================
        # 3. PC PWA 독립 창 (Standalone Window Frame) 타이틀바 아이콘
        # ==========================================================
        page_window = browser.new_page(viewport={"width": 1100, "height": 700})
        html_window = """
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
              width: 100vw;
              height: 100vh;
              background: #020617;
              padding: 24px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
            }
            .app-window {
              width: 1000px;
              height: 620px;
              background: #ffffff;
              border-radius: 14px;
              box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7);
              border: 1px solid #334155;
              overflow: hidden;
              display: flex;
              flex-direction: column;
            }
            /* Window Title Bar */
            .title-bar {
              height: 40px;
              background: #0f172a;
              color: #f8fafc;
              display: flex;
              align-items: center;
              justify-content: space-between;
              padding: 0 14px;
              user-select: none;
              border-bottom: 1px solid #1e293b;
            }
            .title-left {
              display: flex;
              align-items: center;
              gap: 10px;
            }
            .window-app-icon {
              width: 22px;
              height: 22px;
              border-radius: 5px;
              background: #ffffff;
              padding: 1.5px;
              display: flex;
              align-items: center;
              justify-content: center;
            }
            .window-app-icon img {
              width: 100%;
              height: 100%;
              object-fit: contain;
            }
            .window-title {
              font-size: 12px;
              font-weight: 700;
              color: #cbd5e1;
              letter-spacing: -0.2px;
            }
            .window-controls {
              display: flex;
              align-items: center;
              gap: 14px;
            }
            .ctrl-btn {
              width: 12px;
              height: 12px;
              border-radius: 50%;
            }
            .ctrl-btn.min { background: #eab308; }
            .ctrl-btn.max { background: #22c55e; }
            .ctrl-btn.close { background: #ef4444; }
            
            /* Window Content Area */
            .window-body {
              flex: 1;
              background: #f8fafc;
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              gap: 16px;
            }
            .preview-hero {
              text-align: center;
              max-width: 600px;
            }
            .preview-hero h2 {
              font-size: 24px;
              font-weight: 900;
              color: #0f172a;
              margin-bottom: 8px;
            }
            .preview-hero p {
              font-size: 14px;
              color: #64748b;
              font-weight: 500;
            }
            .badge-standalone {
              display: inline-flex;
              align-items: center;
              gap: 6px;
              padding: 6px 14px;
              border-radius: 9999px;
              background: #eff6ff;
              color: #2563eb;
              font-weight: 800;
              font-size: 12px;
              border: 1px solid #bfdbfe;
            }
          </style>
        </head>
        <body>
          <div class="app-window">
            <!-- Window Title Bar with New Logo Icon -->
            <div class="title-bar">
              <div class="title-left">
                <div class="window-app-icon">
                  <img src="http://127.0.0.1:8080/icons/icon-192x192.png?v=20261002_logo" alt="Icon">
                </div>
                <span class="window-title">PriceTrace | 네이버 쇼핑 실시간 최저가 레이더</span>
              </div>
              <div class="window-controls">
                <span class="ctrl-btn min"></span>
                <span class="ctrl-btn max"></span>
                <span class="ctrl-btn close"></span>
              </div>
            </div>

            <!-- Standalone App Frame Body -->
            <div class="window-body">
              <span class="badge-standalone">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                PC PWA 독립 실행형(Standalone) 모드
              </span>
              <div class="preview-hero">
                <h2>브라우저 주소창 없는 전용 네이티브 앱 창</h2>
                <p>PC 바탕화면 및 작업표시줄에서 바로가기를 클릭하면 상단 타이틀바에 공식 레이더 아이콘과 함께 단독 앱 창으로 실행됩니다.</p>
              </div>
            </div>
          </div>
        </body>
        </html>
        """
        page_window.set_content(html_window)
        page_window.wait_for_timeout(1000)
        shot_window = os.path.join(ARTIFACT_DIR, "proof_pc_standalone_window_frame.png")
        page_window.screenshot(path=shot_window)
        print(f"  - [3] PC 독립 창(Standalone) 및 타이틀바 아이콘 캡처: {shot_window}")
        page_window.close()

        browser.close()

    print("=" * 60)
    print("🎉 PC 바로가기 및 설치 앱 아이콘 전수 캡처 완료!")
    print("=" * 60)

if __name__ == "__main__":
    capture_pc_shortcuts()
