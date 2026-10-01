# [TRD] PriceTrace PWA(Progressive Web App) 기술설계서

- **문서 버전**: 1.0.0
- **기술 스택**: PWA Web Manifest (v1) + Service Worker API (CacheStorage) + Vanilla JS ES6+ + Python HTTP Server
- **작성일자**: 2026-10-01
- **상태**: 설계 완료 및 사용자 승인 대기

---

## 1. 아키텍처 개요

PWA는 기존 3-Layer 아키텍처 상에서 다음과 같이 결합됩니다:

```
[클라이언트 브라우저 / 네이티브 PWA 컨테이너]
       │
       ▼ (모든 네트워크 요청 가로채기)
┌────────────────────────────────────────────────────────┐
│ Service Worker (`public/sw.js`)                        │
│                                                        │
│  ├─ Cache-First Router:                                │
│  │    - 정적 자산: HTML, CSS, JS, SVG, Fonts, Icons     │
│  │    - 오프라인 시 CacheStorage 즉시 반환              │
│  │                                                     │
│  ├─ Network-First Router:                              │
│  │    - 실시간 API: /api/search, /api/summary          │
│  │    - 온라인: 서버 호출 후 캐시 갱신                 │
│  │    - 오프라인: 캐시된 마지막 결과 또는 폴백 반환     │
│  │                                                     │
│  └─ Background Sync & Lifecycle:                       │
│       - install: 정적 코어 파일 사전 캐싱 (Pre-caching)│
│       - activate: 구버전 캐시 정리 (Cache Pruning)      │
└──────────────────────────┬─────────────────────────────┘
                           │ Network Fetch (온라인 시)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Python Lightweight Server (`server.py`)               │
│                                                        │
│  ├─ MIME 타입 지원:                                    │
│  │    - manifest.json -> application/manifest+json    │
│  │    - sw.js -> application/javascript                │
│  └─ REST API 엔드포인트                                │
└────────────────────────────────────────────────────────┘
```

---

## 2. 파일 구성 및 세부 명세

### 2.1 Web App Manifest (`public/manifest.json`)
```json
{
  "name": "PriceTrace - 실시간 최저가 레이더",
  "short_name": "PriceTrace",
  "description": "네이버 쇼핑 공식 카탈로그 기반 실시간 생필품 최저가 비교 및 가격 추적 레이더",
  "start_url": "/",
  "id": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#2563eb",
  "orientation": "portrait-primary",
  "scope": "/",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-192x192-maskable.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-512x512-maskable.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "categories": ["shopping", "utilities", "productivity"]
}
```

### 2.2 서비스 워커 (`public/sw.js`) 수명주기 및 캐싱 로직
1. **버전 및 프리캐시 리스트**:
   - `CACHE_NAME = 'pricetrace-v1.0.0'`
   - `STATIC_ASSETS = ['/', '/index.html', '/style.css', '/app.js', '/logo_jwj.svg', '/manifest.json', '/icons/icon-192x192.png', '/icons/icon-512x512.png']`
2. **`install` 이벤트**:
   - `event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS)))`
   - `self.skipWaiting()`
3. **`activate` 이벤트**:
   - 오래된 캐시(`pricetrace-v*` 중 구버전) 자동 삭제
   - `self.clients.claim()`
4. **`fetch` 이벤트**:
   - `/api/` 요청: `Network-First` (fetch 시도 → 성공 시 동적 캐시 업데이트 → 네트워크 실패 시 캐시된 응답 반환).
   - 정적 리소스 요청: `Cache-First` (캐시 존재 시 즉시 반환 → 없으면 네트워크 fetch 후 캐시 저장).
   - 오프라인 폴백: 탐색(navigation) 요청 시 오프라인 상태이면 캐시된 `/index.html` 반환.

### 2.3 프론트엔드 연동 (`public/app.js` & `public/index.html`)
1. **서비스 워커 등록**:
   ```javascript
   if ('serviceWorker' in navigator) {
     window.addEventListener('load', () => {
       navigator.serviceWorker.register('/sw.js')
         .then(reg => console.log('PWA ServiceWorker 등록 성공:', reg.scope))
         .catch(err => console.error('PWA ServiceWorker 등록 실패:', err));
     });
   }
   ```
2. **설치 유도 이벤트 (`beforeinstallprompt`) 핸들링**:
   - 전역 변수 `deferredPrompt`에 이벤트 저장.
   - 네비게이션 헤더 및 모바일 플로팅 위젯에 "📲 앱 설치" 버튼 표시.
   - 버튼 클릭 시 `deferredPrompt.prompt()` 호출 및 결과 로깅.
   - 설치 완료(`appinstalled`) 이벤트 수신 시 버튼 제거 및 완료 토스트 표시.
3. **iOS Safari 가이드**:
   - `navigator.userAgent`에 `iPhone` or `iPad` 포함 + `navigator.standalone === false`인 경우 가이드 툴팁/모달 안내 제공.

### 2.4 고해상도 앱 아이콘 생성 (`scripts/generate_pwa_icons.py`)
- 기존 고화질 브랜드 SVG 로고(`public/logo_jwj.svg`)를 활용하거나 PIL/Canvas 기반으로 규격별(192x192, 512x512, maskable 버전) 고품질 PNG 생성.

---

## 3. 검증 계획 (Verification Strategy)

1. **로컬 서버 MIME 타입 검증**:
   - `curl -I http://localhost:8080/manifest.json` → `Content-Type: application/manifest+json` 또는 `application/json` 확인.
   - `curl -I http://localhost:8080/sw.js` → `Content-Type: application/javascript` 확인.
2. **Playwright E2E 자동 검증**:
   - 서비스 워커가 정상적으로 `activated` 상태가 되는지 확인.
   - `manifest.json`이 200 OK로 파싱되고 필수 키(`name`, `icons`, `start_url`, `display`)가 존재하는지 검증.
   - 뷰포트별(모바일, 데스크톱) 설치 유도 UI 렌더링 확인 및 스크린샷 캡처.
