# [PRD] PriceTrace PWA(Progressive Web App) 도입 요구사항명세서

- **문서 버전**: 1.0.0
- **프로젝트 레벨**: Dynamic / Deep Dive (PDCA Plan 단계)
- **작성일자**: 2026-10-01
- **상태**: 기획 완료 및 사용자 승인 대기

---

## 1. 개요 및 도입 배경

### 1.1 개요
PriceTrace는 네이버 쇼핑 공식 카탈로그를 기반으로 생필품 최저가를 실시간 추적하고 비교하는 서비스입니다.  
사용자가 모바일(iOS Safari, Android Chrome) 및 데스크톱(Chrome, Edge 등) 환경에서 별도의 앱스토어 설치 과정 없이 원클릭으로 홈 화면에 앱을 설치(`Add to Home Screen`)하고, 오프라인 환경에서도 캐시된 최저가 데이터와 앱 UI를 즉각 이용할 수 있도록 PWA(Progressive Web App) 표준 기술을 전면 도입합니다.

### 1.2 핵심 도입 목표
1. **앱스토어 없는 네이티브 앱 경험**: 모바일 및 데스크톱 홈 화면/작업표시줄에 단독 앱(`standalone`) 아이콘 생성 및 브라우저 주소창 없는 전체 화면 실행.
2. **초고속 로딩 및 오프라인 접근성**: 서비스 워커(`Service Worker`) 기반의 지능형 캐싱 전략(정적 자산 Cache-First, API Network-First + Cache Fallback)을 통해 네트워크 단절 시에도 안정적인 안내와 캐시 뷰 제공.
3. **직관적인 설치 UX (A2HS)**: 브라우저의 기본 안내에 의존하지 않고, 서비스 디자인에 녹아든 커스텀 "앱 설치하기" 헤더 버튼/플로팅 배너 및 iOS Safari 전용 홈 화면 추가 가이드 제공.
4. **PWA 표준 100% 충족**: Web App Manifest, Service Worker 수명주기, 192/512 해상도 및 Maskable 아이콘, HTTPS/localhost 환경 충족.

---

## 2. 사용자 페르소나 및 핵심 시나리오

- **주요 사용자**: 생필품(라면, 생수, 세제 등)의 가격 변동을 수시로 확인하고 특가 발생 시 즉시 구매하는 모바일/데스크톱 쇼핑 유저.
- **주요 시나리오**:
  1. **설치 시나리오**: 사용자가 모바일 또는 데스크톱 브라우저로 PriceTrace에 접속하면 상단에 "📲 앱으로 설치" 버튼이 부드럽게 노출되며, 클릭 한 번으로 스마트폰 홈 화면 또는 PC 앱 목록에 등록됨.
  2. **실행 시나리오**: 홈 화면의 PriceTrace 아이콘을 터치하면 상단 주소창이 없는 네이티브 앱 인터페이스로 0.1초 만에 즉시 구동.
  3. **오프라인 시나리오**: 지하철이나 엘리베이터 등 일시적으로 통신이 끊긴 환경에서도 앱이 멈추거나 백지 화면이 뜨지 않고, 최근 검색했던 최저가 데이터와 오프라인 친화적 상태 알림이 정상 표출됨.

---

## 3. 세부 기능 요구사항 (Functional Requirements)

### FR-1: 웹 앱 매니페스트 (`manifest.json`)
- `name`: "PriceTrace - 실시간 최저가 레이더"
- `short_name`: "PriceTrace"
- `start_url`: "/"
- `display`: "standalone" (주소창 및 브라우저 컨트롤 제거)
- `background_color`: "#0f172a" (다크 테마 배경)
- `theme_color`: "#2563eb" (브랜드 블루 테마)
- `orientation`: "portrait-primary" (모바일 세로 고정 우선, 반응형 자동 대응)
- `icons`: 
  - 192x192 PNG (any 및 maskable)
  - 512x512 PNG (any 및 maskable)
  - 180x180 Apple Touch Icon

### FR-2: 서비스 워커 (`sw.js`) 및 캐싱 전략
- **정적 자산 캐싱 (Cache-First)**: HTML, CSS, JavaScript, SVG 로고, 폰트, 웹 아이콘 등 UI 리소스는 캐시에서 즉각 서빙하고 백그라운드에서 최신 버전 확인/갱신.
- **동적 API 캐싱 (Network-First with Fallback)**: `/api/search`, `/api/summary`, `/api/trending` 등 실시간 가격 데이터는 네트워크 요청을 우선하여 신선한 최저가를 수신하되, 네트워크 실패 시 최근 성공했던 캐시 데이터 반환.
- **수명주기 관리**: 서비스 워커 신규 배포 시 `skipWaiting` 및 `clients.claim()`을 통한 매끄러운 핫업데이트 지원.

### FR-3: 맞춤형 설치 유도 인터랙션 (Install Experience)
- Android Chrome / Desktop Chrome / Edge: `beforeinstallprompt` 이벤트를 캡처하여 브라우저 기본 다이얼로그 대신 서비스 헤더 및 플로팅 위젯에 "앱 설치" 버튼 노출.
- iOS Safari: `standalone` 비활성 및 iOS 환경 감지 시 "하단 공유 버튼(⎋) → '홈 화면에 추가' 선택" 친절한 토스트/모달 가이드 제공.
- 이미 설치된 상태(`standalone` 모드 실행)에서는 설치 유도 UI를 자동으로 숨김.

### FR-4: 모바일 메타 태그 및 스플래시 지원
- `<meta name="theme-color" content="#2563eb">`
- `<meta name="apple-mobile-web-app-capable" content="yes">`
- `<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">`
- `<meta name="apple-mobile-web-app-title" content="PriceTrace">`
- `<link rel="apple-touch-icon" href="/icons/icon-192x192.png">`

---

## 4. 비기능적 요구사항 (Non-Functional Requirements)

1. **호환성 및 표준 준수**: W3C Web App Manifest 및 W3C Service Workers Level 1 표준 100% 준수.
2. **성능**: 서비스 워커 캐시 히트 시 초기 로드 시간 150ms 미만 달성.
3. **보안**: HTTPS 환경 및 로컬 개발용 `localhost`에서 완전 정상 동작 보장.
4. **품질 검증 (Check)**: Playwright 헤드리스 브라우저를 통한 Service Worker 등록 및 Manifest JSON 파싱 검증, 뷰포트별 설치 버튼 렌더링 E2E 검증 통과.
