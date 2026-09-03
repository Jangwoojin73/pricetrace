#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
get_kakao_token.py - 초보자를 위한 카카오 리프레시 토큰 자동 발급 헬퍼

사용법:
1. python get_kakao_token.py 실행
2. 콘솔의 안내에 따라 REST API 키와 Client Secret 입력 (또는 엔터)
3. 브라우저에서 카카오 로그인 및 메시지 전송 동의 진행
4. 자동으로 리프레시 토큰을 발급받아 .env 파일에 저장해 줍니다.
"""

import sys
import io
import os
import json
import webbrowser
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Windows 콘솔 인코딩 대응
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

PORT = 5000
REDIRECT_URI = f"http://localhost:{PORT}/oauth"
auth_code = None


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            success_html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"><title>카카오 인증 성공</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #22c55e;">🎉 카카오 인증 성공!</h1>
                <p>인가 코드가 안전하게 전달되었습니다. 이 브라우저 창을 닫고 터미널(콘솔)을 확인해 주세요.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Failed to receive authorization code.")

    def log_message(self, format, *args):
        # 터미널에 불필요한 HTTP 로그 생략
        return


def main():
    print("=" * 65)
    print("🔑 [Kakao OAuth Helper] 카카오 토큰 간편 발급기")
    print("=" * 65)
    print("이 도구는 카카오 로그인 창을 열어 '리프레시 토큰'을 쉽게 발급받게 도와줍니다.\n")

    client_id = input("1. 카카오 REST API 키를 입력하세요: ").strip()
    if not client_id:
        print("❌ REST API 키가 입력되지 않았습니다. 종료합니다.")
        return

    client_secret = input("2. 카카오 Client Secret을 입력하세요 (없으면 엔터): ").strip()

    # 인가 코드 요청 URL 생성
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"response_type=code&"
        f"scope=talk_message"
    )

    print("\n🌐 잠시 후 브라우저가 열립니다. 카카오 로그인 후 [동의하고 계속하기]를 눌러주세요...")
    print(f"👉 브라우저가 안 열리면 이 링크를 직접 여세요:\n{auth_url}\n")
    
    webbrowser.open(auth_url)

    # 로컬 콜백 웹서버 시작
    server = HTTPServer(("localhost", PORT), OAuthCallbackHandler)
    while auth_code is None:
        server.handle_request()
    server.server_close()

    print("✅ 인가 코드를 성공적으로 수신했습니다! 토큰 발급을 요청합니다...")

    # 카카오 토큰 발급 API 호출
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "code": auth_code
    }
    if client_secret:
        token_data["client_secret"] = client_secret

    encoded_data = urllib.parse.urlencode(token_data).encode("utf-8")
    req = urllib.request.Request(
        token_url,
        data=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"\n❌ 토큰 발급 실패: {e}")
        return

    refresh_token = tokens.get("refresh_token")
    access_token = tokens.get("access_token")

    if not refresh_token:
        print(f"❌ 리프레시 토큰을 받지 못했습니다. 응답 내용: {tokens}")
        return

    print("\n" + "=" * 65)
    print("🎉 발급 완료! 아래 정보를 .env 파일에 저장합니다.")
    print("=" * 65)
    print(f"KAKAO_REST_API_KEY={client_id}")
    if client_secret:
        print(f"KAKAO_CLIENT_SECRET={client_secret}")
    print(f"KAKAO_REFRESH_TOKEN={refresh_token}")
    print("-" * 65)

    # .env 파일 자동 작성/업데이트
    env_content = f"KAKAO_REST_API_KEY={client_id}\n"
    if client_secret:
        env_content += f"KAKAO_CLIENT_SECRET={client_secret}\n"
    env_content += f"KAKAO_REFRESH_TOKEN={refresh_token}\n"

    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("💾 현재 폴더의 .env 파일에 성공적으로 저장되었습니다!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
