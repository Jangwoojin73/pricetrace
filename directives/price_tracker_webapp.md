# [Directive] 네이버 쇼핑 가격비교 경량 웹앱 운영 및 개발 지침

- **목표**: 네이버 쇼핑 가격비교 봇(`pricetrace_bot.py`)을 경량 웹 서버(`server.py`)로 노출하고, 이커머스 쇼핑몰 UI(`public/`)로 최저가 정보 및 가격비교 차트를 시각화한다.
- **도구/스크립트**:
  - `server.py`: 웹앱 및 API 엔드포인트 서빙
  - `pricetrace_bot.py`: 핵심 크롤링 및 정제 모듈
  - `test_webapp.py`: 웹앱 API 및 프론트엔드 서빙 정합성 테스트
- **입력값**:
  - 검색 키워드 (기본: "농심 신라면 봉지 20개입")
  - 목표 가격 (기본: 15,000원)
- **출력값**:
  - `http://localhost:8080` 웹 인터페이스
  - REST API JSON 응답 (`/api/summary`, `/api/search`, `/api/history`)
- **엣지 케이스 및 대응**:
  - 네이버 쇼핑 응답 지연/차단 시: 기존 로컬 캐시 JSON 데이터(`refined_shinramyun_20.json` 등)로 자동 폴백(Fallback)하여 UI가 먹통이 되지 않도록 보장
  - 포트 충돌 시: 8080 포트 사용 중일 경우 8081 등으로 자동 전환하거나 커스텀 포트 옵션(`--port`) 지원
