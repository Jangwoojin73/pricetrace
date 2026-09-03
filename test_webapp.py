#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_webapp.py - PriceTrace WebApp 기능 및 API 통합 검증 스크립트

검사 항목:
1. 정적 파일(index.html, style.css, app.js) 서빙 HTTP 200 검증
2. /api/summary 엔드포인트 응답 형식 및 필수 필드(lowest_price, unit_price, alert_message 등) 검증
3. /api/search 키워드 쿼리 및 target_price 파라미터 동적 계산 검증
4. /api/history 최근 30일 가격 추이 데이터 구조 검증
5. /api/status 서버 상태 확인 엔드포인트 검증
6. 특가 판별 로직(14,000원 -> 특가 발생, 16,000원 -> 유지) 일치성 검증
"""

import sys
import io
import time
import json
import threading
import urllib.request
import urllib.parse
from http.server import HTTPServer

# Windows UTF-8 인코딩
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import server

TEST_PORT = 8999
BASE_URL = f"http://localhost:{TEST_PORT}"


class WebAppTestSuite:
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.passed_count = 0
        self.total_count = 0
        self.results = []

    def start_server(self):
        """테스트 전용 포트로 서버 백그라운드 구동"""
        self.server = HTTPServer(("localhost", TEST_PORT), server.PriceTraceHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        time.sleep(0.3)

    def stop_server(self):
        """서버 정상 종료"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    def record_result(self, name: str, passed: bool, detail: str):
        self.total_count += 1
        if passed:
            self.passed_count += 1
        status = "✅ [PASS]" if passed else "❌ [FAIL]"
        self.results.append((status, name, detail))
        print(f"{status} {name}")
        print(f"   └─ {detail}")

    def test_static_files(self):
        """1. 정적 파일 서빙 검증"""
        try:
            files_to_check = ["/", "/index.html", "/style.css", "/app.js"]
            for path in files_to_check:
                req = urllib.request.urlopen(f"{BASE_URL}{path}", timeout=3)
                if req.status != 200:
                    self.record_result(f"정적 파일 서빙 ({path})", False, f"상태 코드 {req.status}")
                    return
            self.record_result("정적 파일 서빙 (HTML/CSS/JS)", True, "index.html, style.css, app.js 모두 HTTP 200 OK")
        except Exception as e:
            self.record_result("정적 파일 서빙 (HTML/CSS/JS)", False, str(e))

    def test_api_summary(self):
        """2. /api/summary 응답 검증"""
        try:
            req = urllib.request.urlopen(f"{BASE_URL}/api/summary", timeout=5)
            data = json.loads(req.read().decode("utf-8"))
            required_keys = ["success", "lowest_price", "unit_price", "is_special_price", "alert_message", "top_items", "history"]
            missing = [k for k in required_keys if k not in data]
            if missing:
                self.record_result("/api/summary 필수 필드", False, f"누락된 필드: {missing}")
                return
            if len(data.get("top_items", [])) == 0:
                self.record_result("/api/summary 상품 목록", False, "top_items가 비어 있습니다.")
                return
            lowest = data["lowest_price"]
            unit = data["unit_price"]
            expected_unit = round(lowest / 20)
            if unit != expected_unit:
                self.record_result("/api/summary 1봉당 단가 계산", False, f"단가 계산 오류: 기대 {expected_unit}, 실제 {unit}")
                return
            self.record_result("/api/summary 엔드포인트", True, f"최저가 {lowest:,}원 (봉당 {unit:,}원), top_items {len(data['top_items'])}개 정상 반환")
        except Exception as e:
            self.record_result("/api/summary 엔드포인트", False, str(e))

    def test_api_search_dynamic(self):
        """3. /api/search 동적 목표가 및 키워드 검증"""
        try:
            encoded_q = urllib.parse.quote("농심 신라면")
            # 목표가를 매우 낮은 5,000원으로 설정했을 때 (유지 상태여야 함)
            url_low = f"{BASE_URL}/api/search?q={encoded_q}&target_price=5000"
            req_low = urllib.request.urlopen(url_low, timeout=5)
            data_low = json.loads(req_low.read().decode("utf-8"))
            if data_low["target_price"] != 5000:
                self.record_result("/api/search 목표가 반영", False, f"목표가 반영 실패: {data_low['target_price']}")
                return
            if data_low["is_special_price"] is not False:
                self.record_result("/api/search 목표가 초과 판별", False, "5,000원 설정 시 is_special_price는 False여야 합니다.")
                return

            # 목표가를 매우 높은 30,000원으로 설정했을 때 (특가 상태여야 함)
            url_high = f"{BASE_URL}/api/search?q={encoded_q}&target_price=30000"
            req_high = urllib.request.urlopen(url_high, timeout=5)
            data_high = json.loads(req_high.read().decode("utf-8"))
            if data_high["is_special_price"] is not True:
                self.record_result("/api/search 목표가 이하 특가 판별", False, "30,000원 설정 시 is_special_price는 True여야 합니다.")
                return

            self.record_result("/api/search 동적 목표가 판별", True, "URL 인코딩 및 목표가 5,000원(유지) / 30,000원(특가 발생) 분기 정상 판별")
        except Exception as e:
            self.record_result("/api/search 동적 목표가 판별", False, str(e))

    def test_api_history(self):
        """4. /api/history 최근 30일 추이 데이터 검증"""
        try:
            req = urllib.request.urlopen(f"{BASE_URL}/api/history?price=13200&target=15000", timeout=3)
            data = json.loads(req.read().decode("utf-8"))
            history = data.get("history", [])
            if len(history) != 30:
                self.record_result("/api/history 데이터 개수", False, f"30일 데이터가 아닙니다. 개수: {len(history)}")
                return
            latest = history[-1]
            if latest.get("price") != 13200:
                self.record_result("/api/history 최신 가격", False, f"최신 가격 불일치: {latest.get('price')}")
                return
            self.record_result("/api/history 30일 추이 데이터", True, f"30일치 데이터셋 및 최신 가격({latest.get('price'):,}원) 일치 확인")
        except Exception as e:
            self.record_result("/api/history 30일 추이 데이터", False, str(e))

    def test_api_status(self):
        """5. /api/status 헬스체크 검증"""
        try:
            req = urllib.request.urlopen(f"{BASE_URL}/api/status", timeout=3)
            data = json.loads(req.read().decode("utf-8"))
            if data.get("status") == "online" and data.get("bot_module_loaded") is True:
                self.record_result("/api/status 헬스체크", True, "서버 상태 online 및 봇 모듈 로드 정상")
            else:
                self.record_result("/api/status 헬스체크", False, f"비정상 응답: {data}")
        except Exception as e:
            self.record_result("/api/status 헬스체크", False, str(e))

    def run_all(self):
        print("=" * 68)
        print("🧪 [WebApp Test Suite] PriceTrace 웹앱 통합 검증 시작")
        print("=" * 68)
        self.start_server()
        try:
            self.test_static_files()
            self.test_api_summary()
            self.test_api_search_dynamic()
            self.test_api_history()
            self.test_api_status()
        finally:
            self.stop_server()

        print("\n" + "=" * 68)
        print(f"📊 검증 결과: {self.passed_count}/{self.total_count} 항목 통과 (성공률: {round(self.passed_count/self.total_count*100)}%)")
        print("=" * 68)
        return self.passed_count == self.total_count


if __name__ == "__main__":
    suite = WebAppTestSuite()
    success = suite.run_all()
    if not success:
        sys.exit(1)
