# [PRD] 모바일 스마트 스크롤 하단 네비게이션 바 (Smart Scroll-Hide Bottom Nav)

- **작성일자**: 2026-10-30
- **프로젝트 레벨**: Dynamic 레벨 (모바일 웹/PWA 인터랙션 고도화)
- **문서 상태**: 계획 수립 (Plan 단계) - 사용자 승인 대기

---

## 1. 배경 및 필요성

### 1.1. 사용자 Pain Point 및 관찰된 행동
- 모바일 환경에서 스마트폰 화면 높이는 한정되어 있으나, PriceTrace 메인 화면에는 상단 헤더, 인기 검색어 칩, 32대 듀얼 탭(생필품 16종 + 핫딜 16종), 상품 카드 리스트 등 탐색해야 할 정보가 풍부함.
- 사용자가 아래로 스크롤하여 상품 카드와 실시간 가격 정보를 서칭할 때, 고정된 하단 네비게이션 바(높이 약 60px + safe-area)가 화면 하단을 계속 차지하여 유효 뷰포트 공간이 약 12~15% 감소함.
- 반면, 다른 탭으로 이동하거나 검색 모달을 열고자 할 때는 엄지손가락으로 화면을 살짝 위로 올리는 제스처를 취하게 됨.

### 1.2. 벤치마크 레퍼런스 분석 (네이버 쇼핑 스토어 흐름)
- **n01 (초기 진입 / 최상단)**: 하단 네비게이션 바 기본 노출. 사용자가 주요 5대 메뉴(홈, 레이더, 생필품, 핫딜, 설정)를 즉시 인지하고 선택 가능.
- **n02 (다운 스크롤 / 탐색 단계)**: 사용자가 아래로 스크롤을 시작하면 하단 네비게이션 바가 화면 하단 바깥으로 부드럽게 슬라이드 다운(`translateY(100%)`). 메인 컨텐츠를 화면 가득 시원하게 노출.
- **n03 (미세 업 스크롤 / 메뉴 전환 의도)**: 아래로 탐색 도중 사용자가 조금이라도 위로 스크롤하면, 하단 네비게이션 바가 즉시 스르륵 올라와 제자리에 복귀(`translateY(0)`). 동시에 맨 위로 즉시 복귀할 수 있는 보조 플로팅 탑 버튼(Top FAB) 제공.

---

## 2. 기능 요구사항 (Functional Requirements)

| 번호 | 요구사항 명 | 세부 설명 | 우선순위 |
| :---: | :--- | :--- | :---: |
| **FR-01** | **다운 스크롤 시 자동 숨김 (Hide)** | `window.scrollY`가 아래로 연속 이동할 때 (`deltaY > 8px`), `#mobileBottomNav`를 화면 아래로 슬라이드 다운 숨김 | P0 (필수) |
| **FR-02** | **업 스크롤 시 즉시 복귀 (Reveal)** | 아래로 스크롤된 상태에서 사용자가 조금이라도 위로 스크롤하면 (`deltaY < -5px`), 즉시 스르륵 위로 복귀 | P0 (필수) |
| **FR-03** | **최상단 안전 구간 고정 (Top Guard)** | 페이지 상단(`scrollY <= 60px`)에서는 스크롤 방향과 무관하게 하단 바 상시 100% 노출 유지 | P0 (필수) |
| **FR-04** | **프로그래밍 스크롤 보호 (Scroll Lock Guard)** | 듀얼 탭 클릭(`scrollToDualTabs()`)이나 홈 버튼 클릭 시 발생하는 자바스크립트 자동 스크롤 중에는 바가 오작동으로 숨겨지지 않도록 방어 | P0 (필수) |
| **FR-05** | **모달 및 오버레이 활성 시 제어 (Modal Isolation)** | 레이더 검색 바텀시트, 목표가 설정 모달, PWA 설치 모달 등이 열려 있을 때는 전역 스크롤 숨김 동작 일시 비활성화 | P1 (중요) |
| **FR-06** | **플로팅 탑 버튼(Top FAB) 연동** | n03 레퍼런스처럼 스크롤이 일정 깊이(`scrollY > 300px`) 내려간 상태에서 우측 하단에 부드럽게 나타나는 '맨 위로 이동' 버튼 지원 | P1 (권장) |
| **FR-07** | **토스트 알림 및 플로팅 요소 간섭 방지** | 하단 바의 가시성 상태에 따라 토스트 알림 위치(`bottom-24` ↔ `bottom-6`)가 어색하게 붕 뜨지 않도록 부드러운 위치 적응 | P2 (선택) |

---

## 3. 기술 사양 및 아키텍처 (Technical Specifications)

### 3.1. 제어 메커니즘 (Throttle + RequestAnimationFrame)
- 스크롤 이벤트의 과도한 리플로우(Reflow)를 방지하기 위해 `requestAnimationFrame`을 사용한 rAF 쓰로틀링 적용.
- 직전 스크롤 위치(`lastScrollY`)와 현재 스크롤 위치(`currentScrollY`)의 차이(`delta = currentScrollY - lastScrollY`)를 수리적으로 계산.

### 3.2. 임계값(Hysteresis Thresholds)
```javascript
const SCROLL_THRESHOLDS = {
  TOP_SAFE_ZONE: 60,      // 상단 60px 이내에서는 무조건 표시
  DOWN_MIN_DELTA: 8,      // 아래로 8px 이상 내려갈 때 숨김 (손가락 미세 떨림 방지)
  UP_MIN_DELTA: -5,       // 위로 5px만 올려도 즉시 감지하여 복귀 (반응성 극대화)
};
```

### 3.3. CSS 트랜지션 및 하드웨어 가속
```css
/* 하단 독 슬라이드 애니메이션 */
#mobileBottomNav {
  transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease-out;
  will-change: transform;
}

#mobileBottomNav.nav-dock-hidden {
  transform: translateY(calc(100% + env(safe-area-inset-bottom, 0px) + 8px)) !important;
  pointer-events: none;
}
```

### 3.4. iOS Safari 탄성 바운스(Rubber-banding) 방어
- `const maxScroll = document.documentElement.scrollHeight - window.innerHeight;`
- `const safeScrollY = Math.max(0, Math.min(scrollY, maxScroll));`
- 탄성 영역(화면 맨 위 위쪽 튕김 `scrollY < 0`, 맨 아래 바닥 튕김 `scrollY > maxScroll`)에서는 delta 계산을 무시하여 떨림 현상 원천 차단.

---

## 4. 품질 검증 및 기존 감사(Audit) 무결성 보존 계획

1. **Step 05 감사 무결성**: 하단 독 5대 탭의 수평 베이스라인 편차(`0.0px`)와 듀얼 탭 스크롤 락(`|y1 - y2| === 0px`)이 신규 스크롤 로직 추가 후에도 100% 정상 유지되는지 확인.
2. **Step 08 푸터 클리어런스 무결성**: 하단 바 숨김 상태에서도 푸터 콘텐츠 영역이 자연스럽게 바닥과 조화를 이루는지 확인.
3. **Playwright 자동화 E2E 테스트**:
   - 모바일 뷰포트(iPhone 15 Pro, 393x852)에서 `window.scrollBy(0, 300)` 실행 후 `getBoundingClientRect().top`이 화면 밖(>= 852px)으로 완전히 이동했는지 실측.
   - 이어서 `window.scrollBy(0, -30)` 실행 후 즉시 `getBoundingClientRect().top`이 다시 화면 하단 안착 위치(약 785px)로 복귀하는지 실측.
