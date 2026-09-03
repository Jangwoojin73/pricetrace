# [TRD] 네이버 쇼핑 가격비교 경량 반응형 웹앱 (Technical Requirements Document)

- **버전**: 1.0.0
- **스택**: Python 내장 HTTP 서버 (Layer 3) + HTML5 / Modern CSS (Tailwind CDN) / Vanilla JS ES6+ (Layer 2 UI)
- **작성일자**: 2026-09-03

---

## 1. 시스템 아키텍처 (3-Layer 매핑)

```
[User Browser (Client)]
       │
       ▼ HTTP (GET / , /api/*)
┌────────────────────────────────────────────────────────┐
│ Python Lightweight Server (`server.py`)               │
│                                                        │
│  ├─ Static Server: index.html, style.css, app.js       │
│  └─ REST API Router:                                   │
│       ├─ GET /api/summary  -> 타깃 상품 최저가 및 목표가 비교 │
│       ├─ GET /api/search   -> 키워드 기반 실시간 크롤링       │
│       └─ GET /api/history  -> 최근 30일 가격 추이 데이터    │
└──────────────────────────┬─────────────────────────────┘
                           │ 함수 호출 (Module Import)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Core Scraping & Filtering (`pricetrace_bot.py`)        │
│                                                        │
│  ├─ fetch_from_proxy() / fetch_from_naver_bff()        │
│  ├─ filter_and_refine_products() (광고/파생라면 필터링)│
│  └─ get_price_alert_message()                          │
└────────────────────────────────────────────────────────┘
```

---

## 2. API 엔드포인트 명세

### 1) `GET /api/summary`
- **목적**: 기본 메인 상품('농심 신라면 봉지 20개입')의 실시간 최저가 요약 및 알림 상태 반환
- **Response Example**:
```json
{
  "success": true,
  "keyword": "농심 신라면 봉지 20개입",
  "target_price": 15000,
  "lowest_price": 13200,
  "unit_price": 660,
  "alert_message": "🚨 [특가 발생] 목표 가격 이하입니다!",
  "is_special_price": true,
  "discount_amount": 1800,
  "representative_item": {
    "title": "농심 신라면, 120g, 20개",
    "price": 13200,
    "mall_name": "네이버 가격비교 (카탈로그)",
    "url": "https://cr3.shopping.naver.com/...",
    "review_count": 104064,
    "score": 4.88
  },
  "top_items": [ ... 3개 상품 목록 ... ],
  "timestamp": "2026-09-03T10:20:00"
}
```

### 2) `GET /api/search?q={keyword}&target_price={price}`
- **목적**: 동적 검색어에 대한 실시간 수집 및 필터링
- **Parameters**: `q` (필수, 검색어), `target_price` (선택, 기본 15000)
- **Response**: 위 `summary`와 동일한 스키마

### 3) `GET /api/history`
- **목적**: 최근 30일간의 가격 추이 데이터 반환 (Chart.js 렌더링용)
- **Response**: `[{ "date": "08-04", "price": 15800 }, ... { "date": "09-03", "price": 13200 }]`

---

## 3. 프론트엔드 UI 컴포넌트 설계

1. **GNB (Global Navigation Bar)**:
   - 로고: `🍜 PriceTrace (최저가 레이더)`
   - 검색창: 자동 포커스, 엔터 키 트리거, 빠른 검색 칩 (`#신라면 20개`, `#진라면 20개`, `#짜파게티 20개`)
   - 라이브 상태 펄스: "🟢 실시간 네이버 데이터 동기화됨"

2. **Hero 최저가 대시보드 (`#heroSection`)**:
   - 상품 썸네일 카드: 고화질 라면 패키지 이미지, 정품 인증 뱃지
   - 가격 하이라이트: 큰 글씨 실시간 가격, 목표가 대비 절감액(`-1,800원`)
   - 단위 가격 계산기: 1개(봉)당 가격 자동 표시
   - 실시간 특가 배너: 15,000원 이하 시 붉은색 펄스 애니메이션 + 특가 축하 배너
   - 구매 버튼: 네이버 최저가 쇼핑몰로 새 탭 링크

3. **판매처별 가격 비교 테이블 (`#comparisonSection`)**:
   - 순위 1, 2, 3위 메달 및 쇼핑몰 아이콘
   - 배송비 포함 실결제 예상가
   - 클린 필터링 뱃지: "광고 및 변형 상품 제외됨"

4. **가격 변동 트렌드 차트 (`#trendSection`)**:
   - Chart.js를 사용한 모던 그라데이션 라인 차트
   - 최저가 라인 + 목표가(15,000원) 기준 점선 가이드라인 표시
   - "지금 살 때인가?" 진단 지표

---

## 4. 디렉토리 배치 계획

```
pricetrace-bot/
├── pricetrace_bot.py       # 기존 크롤링 & 필터링 핵심 로직
├── test_harness.py         # 기존 봇 단위 테스트
├── server.py               # [NEW] 경량 웹 서버 & REST API 라우터
├── public/                 # [NEW] 프론트엔드 정적 에셋
│   ├── index.html          # 메인 UI 구조
│   ├── style.css           # 커스텀 테마 & 애니메이션
│   └── app.js              # 데이터 패칭, 차트 및 인터랙션
├── test_webapp.py          # [NEW] 웹앱 통합 테스트 스크립트
├── directives/
│   └── price_tracker_webapp.md # Layer 1 SOP
└── docs/
    ├── plan/PRD_pricetrace_webapp.md
    ├── design/TRD_pricetrace_webapp.md
    ├── analysis/pricetrace_webapp.md
    └── report/completion_report.md
```
