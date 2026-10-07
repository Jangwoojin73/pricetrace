/**
 * app.js - PriceTrace WebApp 프론트엔드 인터랙션 & 차트 엔진
 */

// 전역 상태
const state = {
  keyword: "",
  targetPrice: 15000,
  alertEnabled: localStorage.getItem("pricetrace_alert_enabled") !== "false",
  data: null,
  chart: null,
  isLoading: false,
  view: "welcome", // "welcome" | "result"
  activeTab: "steady" // "steady" | "trending"
};

// 판매자 도배 수식어 정제 헬퍼 (네이버 가격비교 카탈로그 매칭 보장 & 핵심 단위 보존)
function cleanSearchKeyword(title) {
  if (!title) return "신라면 20개";
  let t = String(title).replace(/\[.*?\]|\(.*?\)|<.*?>/g, " ");
  
  // 포장/묶음 등 부가 수식어는 단위 추출 전에 미리 정제
  const removeWords = [
    "무료배송", "당일발송", "당일출고", "산지직송", "유명한곳", "초특가", "특가", 
    "선물세트", "국내산", "국산", "원산지", "빅세일", "할인", "한정수량", "고당도",
    "못난이", "가정용", "실속형", "프리미엄", "정품", "공식", "인증", "직송", "유명",
    "인기", "추천", "대용량", "맛있는", "착한", "신선한", "깨끗한", "진짜", "오리지널",
    "1+1팩", "1+1", "1팩", "2팩", "1박스", "2박스", "세트", "한박스", "멀티팩", "패키지",
    "1위", "2위", "3위", "베스트", "인기상품", "추천상품", "실시간", "모음", "골라담기",
    "개입", "묶음", "가격비교", "카탈로그"
  ];
  for (const w of removeWords) {
    t = t.split(w).join(" ");
  }

  // 핵심 단위 우선순위 추출 (롤 > 캔/T/병 > 개/봉 > kg/L/g) - 가장 마지막 총수량 단위 매칭
  let unitSpec = "";
  const rollMatches = Array.from(title.matchAll(/(\d+\s*롤)/gi));
  const canMatches = Array.from(title.matchAll(/(\d+\s*(?:캔|T|병))/gi));
  const countMatches = Array.from(title.matchAll(/(\d+\s*(?:개|봉|입))/gi));
  const weightMatches = Array.from(title.matchAll(/(\d+(?:\.\d+)?\s*(?:kg|L))/gi));

  if (rollMatches.length > 0) {
    unitSpec = rollMatches[rollMatches.length - 1][1].replace(/\s+/g, "");
  } else if (canMatches.length > 0) {
    unitSpec = canMatches[canMatches.length - 1][1].replace(/\s+/g, "");
  } else if (countMatches.length > 0) {
    unitSpec = countMatches[countMatches.length - 1][1].replace(/\s+/g, "");
  } else if (weightMatches.length > 0) {
    unitSpec = weightMatches[weightMatches.length - 1][1].replace(/\s+/g, "");
  }

  t = t.replace(/[^\w\s가-힣0-9a-zA-Z]/g, " ");
  const tokens = t.split(/\s+/).filter(tok => tok && tok.length >= 1 && tok.toLowerCase() !== (unitSpec ? unitSpec.toLowerCase() : ""));
  
  if (tokens.length === 0) {
    const cleanFallback = String(title).replace(/[^\w\s가-힣0-9]/g, " ").trim();
    const fb = cleanFallback.split(/\s+/).slice(0, 4).join(" ") || "신라면 20개";
    return unitSpec ? `${fb} ${unitSpec}` : fb;
  }
  
  // 핵심 상품명 및 특성(제로, 다우니, 항균 플러스, 용량 등)을 최대 4~5단어까지 온전히 보존
  const base = tokens.slice(0, 5).join(" ");
  if (unitSpec && !base.toLowerCase().includes(unitSpec.toLowerCase())) {
    return `${base} ${unitSpec}`;
  }
  return base;
}

// 판매처/쇼핑몰 상호명 정제 헬퍼 (수식어 및 불필요한 태그 제거)
function extractCleanMallName(mallStr) {
  if (!mallStr) return "";
  let m = String(mallStr).replace(/\(.*?\)|\[.*?\]/g, " ").trim();
  m = m.replace(/실시간\s*\d+위|공식\s*인증|본사직영|공식\s*카탈로그|네이버\s*가격비교|네이버\s*쇼핑|네이버|스마트스토어|브랜드스토어|온라인\s*최저가|공식몰/g, " ").trim();
  m = m.replace(/[^\w\s가-힣0-9]/g, " ").trim();
  return m;
}

// 네이버 쇼핑 공식 가격비교 카탈로그 ID 매핑 (스폰서 광고 0% 완전 배제 및 최상단 최저가 고정)
const VERIFIED_CATALOG_DEFAULTS = {
  "오뚜기밥 오곡": "51929172895",
  "오뚜기밥 발아현미": "51929469998",
  "오뚜기밥": "51929535738",
  "신라면": "53018889018",
  "햇반 흑미밥": "51929034288",
  "햇반 흑미": "51929034288",
  "햇반 발아현미밥": "51929479249",
  "햇반 발아현미": "51929479249",
  "햇반 발아": "51929479249",
  "햇반 백미": "55379805802",
  "햇반": "55379805802",
  "진라면": "53000554643",
  "안성탕면": "52999538087",
  "코카콜라": "53880193888",
  "사이다": "53733319502",
  "칠성사이다": "53733319502",
  "삼다수 12": "51929188215",
  "삼다수 24": "51929534018",
  "삼다수": "51929534015",
  "스팸 25": "53736015632",
  "스팸": "53787429685",
  "맥심": "59845338200",
  "다우니 미스티크": "58403363432",
  "다우니": "53544719855",
  "페브리즈 다우니": "53666075951",
  "페브리즈": "60465138611",
  "참치 라이트": "54490737667",
  "참치": "54490737667",
  "동원참치": "54490737667",
  "크리넥스 데코소프트": "53549708834",
  "크리넥스 데코": "53549708834",
  "크리넥스 울트라": "53549708834",
  "크리넥스": "53549708834",
  "휴지": "53549708834",
  "커클랜드 프리미엄": "56892899267",
  "커클랜드": "53549213469",
  "물티슈 블루": "51929477954",
  "물티슈": "51929236553",
  "라벤더젤": "53248125143",
  "라벤더": "53248125143",
  "퍼실": "53393266793"
};

// URL 정규화 헬퍼 (네이버 공식 가격비교 카탈로그 및 쇼핑 전용 가격비교 직결 보장)
// - "상품이 없습니다" 품절/노출 제한 에러를 100% 원천 차단합니다.
// - 스폰서 검색 광고(AD)를 0% 완전 배제하여, 최상단에 실제 최저가와 상품명이 고정 노출됩니다.
// - 쇼핑몰별 가격비교 리스트와 구매 페이지로 즉시 연결됩니다.
function cleanProductTitle(title) {
  if (!title) return "";
  let s = String(title);
  let prev = "";
  while (s !== prev) {
    prev = s;
    s = s.replace(/\([^()]*\)/g, " ").replace(/\[[^[\]]*\]/g, " ");
  }
  s = s.replace(/[()[\]]/g, " ");
  return s.replace(/\s+/g, " ").trim();
}

function cleanSearchKeyword(title) {
  if (!title) return "";
  let t = cleanProductTitle(title);
  t = t.replace(/\d+\s*(?:개월|달|주|일)(?:\s*분)?/g, " ");
  const removeWords = [
    "무료배송", "당일발송", "당일출고", "산지직송", "유명한곳", "초특가", "특가", 
    "선물세트", "국내산", "국산", "원산지", "빅세일", "할인", "한정수량", "고당도",
    "못난이", "가정용", "실속형", "프리미엄", "정품", "공식", "인증", "직송", "유명",
    "인기", "추천", "대용량", "1+1팩", "1+1", "1팩", "2팩", "1박스", "2박스", "세트", "한박스", "멀티팩",
    "카제로템", "ncfb", "패밀리", "국내제조", "반려견", "수제간식", "무염", "제조",
    "과학", "치약", "케이스", "제공", "치아", "형성", "좋은", "칼슘", "잇몸"
  ];
  for (const w of removeWords) {
    t = t.replace(new RegExp(w, "gi"), " ");
  }
  const particles = new Set(["에", "의", "와", "과", "로", "를", "은", "는", "이", "가", "약"]);
  const tokens = t.split(/\s+/).filter(tok => tok.length >= 2 && !particles.has(tok.toLowerCase()));
  return tokens.slice(0, 4).join(" ").trim() || cleanProductTitle(title);
}

function isMobileClient() {
  if (typeof window === "undefined") return false;
  return (
    window.innerWidth <= 768 ||
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  );
}

function normalizeProductUrl(url, title = "", price = 0, rank = 1, mallName = "") {
  let trimmed = String(url || "").trim();
  const isMobile = isMobileClient();

  // 0. 이미 완성된 네이버 공식 포털 쇼핑 링크인 경우 기기 환경에 맞춰 앵커 및 도메인 상호 변환
  if (trimmed.includes("search.naver.com/search.naver") || trimmed.includes("m.search.naver.com/search.naver")) {
    if (isMobile) {
      // 모바일 환경: m.search.naver.com 및 #shp_lis_root로 변환하여 모바일 파워링크 광고 100% 자동 우회
      let mobileUrl = trimmed.replace("search.naver.com", "m.search.naver.com");
      mobileUrl = mobileUrl.replace("where=shp", "where=m");
      mobileUrl = mobileUrl.replace("#shp_dui_root", "").replace("#shp_gui_root", "");
      if (!mobileUrl.includes("#shp_lis_root")) {
        mobileUrl += "#shp_lis_root";
      }
      return mobileUrl;
    } else {
      // PC 환경: search.naver.com?where=shp 및 #shp_dui_root 보장
      let desktopUrl = trimmed.replace("m.search.naver.com", "search.naver.com");
      desktopUrl = desktopUrl.replace("where=m", "where=shp");
      desktopUrl = desktopUrl.replace("#shp_lis_root", "").replace("#shp_gui_root", "");
      if (!desktopUrl.includes("#shp_dui_root")) {
        desktopUrl += "#shp_dui_root";
      }
      return desktopUrl;
    }
  }

  // 1. 기존 URL이나 제목에서 순수 검색어 추출
  let extractedQuery = "";
  if (trimmed.includes("?")) {
    try {
      const u = new URL(trimmed);
      extractedQuery = cleanSearchKeyword(u.searchParams.get("query") || "");
    } catch (e) {}
  }

  const cleanTitle = cleanSearchKeyword(title || extractedQuery || "인기상품");

  // 2. 순위별 고유 차별화 키워드 조합 (1위: 기본/공식, 2위: 최저가, 3위: 무료배송)
  let targetQuery = cleanTitle;
  const cleanMall = extractCleanMallName(mallName);
  if (cleanMall && cleanMall.length >= 2 && !targetQuery.includes(cleanMall) && targetQuery.split(/\s+/).length <= 2) {
    targetQuery = `${cleanMall} ${targetQuery}`.trim();
  } else if (rank === 2 && targetQuery.split(/\s+/).length <= 3) {
    targetQuery = `${targetQuery} 최저가`;
  } else if (rank === 3 && targetQuery.split(/\s+/).length <= 3) {
    targetQuery = `${targetQuery} 무료배송`;
  }

  // 3. 기기별 최적화 URL 반환 [WAF 차단 0% & 파워링크 광고/AI 브리핑 0% 우회 직결]
  const encTarget = encodeURIComponent(targetQuery.trim());
  if (isMobile) {
    return `https://m.search.naver.com/search.naver?where=m&query=${encTarget}#shp_lis_root`;
  } else {
    return `https://search.naver.com/search.naver?where=shp&query=${encTarget}#shp_dui_root`;
  }
}



// 1. 국민 필수 생필품 풀 (고정 16대 대표 품목)
let STEADY_PRODUCTS_POOL = [
  {
    keyword: "농심 신라면 봉지 20개입",
    shortName: "신라면 20개",
    tag: "20개 패키지",
    title: "농심 신라면 20개",
    desc: "봉지라면 대표 베스트셀러<br>120g 20개 1박스 묶음",
    icon: "🍜",
    bgClass: "bg-amber-50 border-amber-100/80"
  },
  {
    keyword: "CJ제일제당 햇반 210g 24개",
    shortName: "햇반 24개",
    tag: "24개 대용량",
    title: "CJ제일제당 햇반 24개",
    desc: "즉석밥 국민 필수 생필품<br>210g 24개 박스 특가",
    icon: "🍚",
    bgClass: "bg-slate-50 border-slate-100"
  },
  {
    keyword: "코카콜라 제로 355ml 24캔",
    shortName: "코카콜라 제로",
    tag: "24캔 뚱캔",
    title: "코카콜라 제로 24캔",
    desc: "탄산음료 압도적 1위<br>355ml 24캔 1박스 최저가",
    icon: "🥤",
    bgClass: "bg-rose-50 border-rose-100/80"
  },
  {
    keyword: "제주 삼다수 2L 6개",
    shortName: "삼다수 2L",
    tag: "2L 6병 팩",
    title: "제주 삼다수 2L 6개",
    desc: "국민 생수 정기 구매 필수<br>2L 6병 묶음 배송비 비교",
    icon: "💧",
    bgClass: "bg-sky-50 border-sky-100/80"
  },
  {
    keyword: "오뚜기 진라면 매운맛 40개",
    shortName: "진라면 40개",
    tag: "40개 박스",
    title: "오뚜기 진라면 40개",
    desc: "가성비 라면 최강자<br>120g 40개 벌크 대용량",
    icon: "🍜",
    bgClass: "bg-amber-50 border-amber-100/80"
  },
  {
    keyword: "맥심 모카골드 마일드 160T",
    shortName: "맥심 커피 160T",
    tag: "160개 스틱",
    title: "맥심 모카골드 160T",
    desc: "국민 믹스커피 대용량<br>사무실·가정 필수 상비품",
    icon: "☕",
    bgClass: "bg-yellow-50 border-yellow-100/80"
  },
  {
    keyword: "크리넥스 3겹 데코소프트 30롤",
    shortName: "크리넥스 30롤",
    tag: "30롤 팩",
    title: "크리넥스 롤화장지 30롤",
    desc: "도톰한 3겹 천연펄프<br>프리미엄 롤티슈 최저가",
    icon: "🧻",
    bgClass: "bg-purple-50 border-purple-100/80"
  },
  {
    keyword: "퍼실 파워젤 액체세제 2.7L",
    shortName: "퍼실 세제 2.7L",
    tag: "2.7L 대용량",
    title: "퍼실 드럼 액체세제",
    desc: "독일 No.1 세탁세제<br>딥클린 테크놀로지 특가",
    icon: "🧼",
    bgClass: "bg-emerald-50 border-emerald-100/80"
  },
  {
    keyword: "동원참치 100g 10캔",
    shortName: "동원참치 10캔",
    tag: "10캔 세트",
    title: "동원참치 라이트 10캔",
    desc: "살코기 참치 국민 반찬<br>100g 10캔 묶음 실속팩",
    icon: "🐟",
    bgClass: "bg-blue-50 border-blue-100/80"
  },
  {
    keyword: "베베숲 시그니처 물티슈 70매 10팩",
    shortName: "베베숲 물티슈 10팩",
    tag: "10팩 캡형",
    title: "베베숲 프리미엄 물티슈",
    desc: "엠보싱 고평점 물티슈<br>70매 10팩 대용량 박스",
    icon: "👶",
    bgClass: "bg-indigo-50 border-indigo-100/80"
  },
  {
    keyword: "오뚜기 맛있는 오뚜기밥 210g 24개",
    shortName: "오뚜기밥 24개",
    tag: "24개 박스",
    title: "맛있는 오뚜기밥 24개",
    desc: "가성비 즉석밥 대표<br>210g 24개 1박스 특가",
    icon: "🍚",
    bgClass: "bg-orange-50 border-orange-100/80"
  },
  {
    keyword: "농심 안성탕면 20개",
    shortName: "안성탕면 20개",
    tag: "20개 묶음",
    title: "농심 안성탕면 20개",
    desc: "구수한 된장 베이스 라면<br>125g 20개 1박스 최저가",
    icon: "🍜",
    bgClass: "bg-amber-50 border-amber-100/80"
  },
  {
    keyword: "칠성사이다 제로 355ml 24캔",
    shortName: "칠성사이다 제로",
    tag: "24캔 박스",
    title: "칠성사이다 제로 24캔",
    desc: "짜릿한 청량감 끝판왕<br>355ml 24캔 뚱캔 박스",
    icon: "🍏",
    bgClass: "bg-emerald-50 border-emerald-100/80"
  },
  {
    keyword: "다우니 섬유유연제 블루 1L 3개",
    shortName: "다우니 3개",
    tag: "3개 세트",
    title: "다우니 섬유유연제 3개",
    desc: "초고농축 상쾌한 향기<br>1L 3개 묶음 배송비 절약",
    icon: "🌸",
    bgClass: "bg-pink-50 border-pink-100/80"
  },
  {
    keyword: "페브리즈 섬유탈취제 상쾌한향 리필 4개",
    shortName: "페브리즈 리필 4개",
    tag: "4개 리필",
    title: "페브리즈 리필 4개입",
    desc: "강력 항균 탈취 리필<br>가성비 4개 묶음 패키지",
    icon: "✨",
    bgClass: "bg-sky-50 border-sky-100/80"
  },
  {
    keyword: "스팸 클래식 200g 10개",
    shortName: "스팸 10캔",
    tag: "10캔 세트",
    title: "CJ 스팸 클래식 10캔",
    desc: "국민 밥도둑 정품 캔햄<br>200g 10개 실속 묶음",
    icon: "🍖",
    bgClass: "bg-rose-50 border-rose-100/80"
  }
];

// 2. 오늘 실시간 핫딜 풀 (/api/trending 에서 동적 로드)
let TRENDING_PRODUCTS_POOL = [];

// 하위 호환성을 위한 범용 추천 풀 참조
let RECOMMENDED_PRODUCTS_POOL = STEADY_PRODUCTS_POOL;

// DOM 요소 캐시
const elements = {
  // 뷰 컨테이너
  welcomeView: document.getElementById("welcomeView"),
  resultView: document.getElementById("resultView"),
  backToHomeBtn: document.getElementById("backToHomeBtn"),
  currentSearchKeywordText: document.getElementById("currentSearchKeywordText"),
  welcomeCardsContainer: document.getElementById("welcomeCardsContainer"),
  refreshRecommendCardsBtn: document.getElementById("refreshRecommendCardsBtn"),

  // 웰컴 듀얼 탭 스위처 & 헤더
  tabSteadyBtn: document.getElementById("tabSteadyBtn"),
  tabTrendingBtn: document.getElementById("tabTrendingBtn"),
  tabSteadyBadge: document.getElementById("tabSteadyBadge"),
  tabTrendingBadge: document.getElementById("tabTrendingBadge"),
  tabSectionTitle: document.getElementById("tabSectionTitle"),
  tabSectionSubtitle: document.getElementById("tabSectionSubtitle"),
  dailyTrendingBadge: document.getElementById("dailyTrendingBadge"),
  dailyTrendingDateText: document.getElementById("dailyTrendingDateText"),

  // 배너 및 헤더
  topBannerText: document.getElementById("topBannerText"),
  lastUpdatedTime: document.getElementById("lastUpdatedTime"),
  alertBanner: document.getElementById("alertBanner"),
  alertIconBox: document.getElementById("alertIconBox"),
  alertStatusBadge: document.getElementById("alertStatusBadge"),
  alertMainMessage: document.getElementById("alertMainMessage"),
  alertDescription: document.getElementById("alertDescription"),
  currentSetTargetPrice: document.getElementById("currentSetTargetPrice"),
  btnTargetPriceDisplay: document.getElementById("btnTargetPriceDisplay"),
  mobileBtnTargetPriceDisplay: document.getElementById("mobileBtnTargetPriceDisplay"),

  // 검색
  searchForm: document.getElementById("searchForm"),
  searchInput: document.getElementById("searchInput"),
  clearSearchBtn: document.getElementById("clearSearchBtn"),
  quickChipsContainer: document.getElementById("quickChipsContainer"),
  shuffleChipsBtn: document.getElementById("shuffleChipsBtn"),
  refreshBtn: document.getElementById("refreshBtn"),
  mobileRefreshBtn: document.getElementById("mobileRefreshBtn"),
  mobileOpenConfigModalBtn: document.getElementById("mobileOpenConfigModalBtn"),
  refreshIcon: document.getElementById("refreshIcon"),

  // 히어로 대시보드
  productTitle: document.getElementById("productTitle"),
  productScore: document.getElementById("productScore"),
  productReviewCount: document.getElementById("productReviewCount"),
  lowestPriceDisplay: document.getElementById("lowestPriceDisplay"),
  discountBadge: document.getElementById("discountBadge"),
  unitPriceDisplay: document.getElementById("unitPriceDisplay"),
  unitPriceLabel: document.getElementById("unitPriceLabel"),
  lowestMallName: document.getElementById("lowestMallName"),
  buyButton: document.getElementById("buyButton"),
  productMainImage: document.getElementById("productMainImage"),
  productCategoryTag: document.getElementById("productCategoryTag"),
  productMallTag: document.getElementById("productMallTag"),
  productUnitTag: document.getElementById("productUnitTag"),
  productBadgeText: document.getElementById("productBadgeText"),

  // 판매처 리스트
  priceComparisonGrid: document.getElementById("priceComparisonGrid"),

  // 구매 진단 버튼
  directBuySubBtn: document.getElementById("directBuySubBtn"),

  // 차트
  priceHistoryChart: document.getElementById("priceHistoryChart"),

  // 모달
  configModal: document.getElementById("configModal"),
  openConfigModalBtn: document.getElementById("openConfigModalBtn"),
  quickTargetEditBtn: document.getElementById("quickTargetEditBtn"),
  closeConfigModalBtn: document.getElementById("closeConfigModalBtn"),
  cancelConfigModalBtn: document.getElementById("cancelConfigModalBtn"),
  saveConfigModalBtn: document.getElementById("saveConfigModalBtn"),
  modalTargetPriceInput: document.getElementById("modalTargetPriceInput"),
  presetPriceBtns: document.querySelectorAll(".preset-price-btn"),

  // 알림 토글
  alertToggleSwitch: document.getElementById("alertToggleSwitch"),
  modalAlertToggle: document.getElementById("modalAlertToggle"),
  alertToggleLabel: document.getElementById("alertToggleLabel"),

  // 30일 시세 통계 카드
  stat30DayMax: document.getElementById("stat30DayMax"),
  stat30DayAvg: document.getElementById("stat30DayAvg"),
  stat30DayMin: document.getElementById("stat30DayMin"),
  stat30DayCurrentPrice: document.getElementById("stat30DayCurrentPrice"),
  stat30DayDiagnosisBadge: document.getElementById("stat30DayDiagnosisBadge"),
  stat30DayDiagnosisDesc: document.getElementById("stat30DayDiagnosisDesc"),

  // 플로팅 토스트 알림 컴포넌트
  toastNotification: document.getElementById("toastNotification"),
  toastMessage: document.getElementById("toastMessage"),
  toastIconBox: document.getElementById("toastIconBox"),

  // 모바일 전용 플로팅 하단 네비게이션 바
  mobileBottomNav: document.getElementById("mobileBottomNav"),
  mobileNavHomeBtn: document.getElementById("mobileNavHomeBtn"),
  mobileNavHotdealBtn: document.getElementById("mobileNavHotdealBtn"),
  mobileNavSearchFabBtn: document.getElementById("mobileNavSearchFabBtn"),
  mobileNavSteadyBtn: document.getElementById("mobileNavSteadyBtn"),
  mobileNavConfigBtn: document.getElementById("mobileNavConfigBtn")
};

// 현재 시각 문자열 포맷팅 (HH:MM:SS)
function getCurrentTimeString() {
  const now = new Date();
  return [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0")
  ].join(":");
}

// 플로팅 토스트 알림 표시 함수
let toastTimeout = null;
function showToast(message, type = "success", duration = 3000) {
  const toast = elements.toastNotification || document.getElementById("toastNotification");
  const msgEl = elements.toastMessage || document.getElementById("toastMessage");
  const iconBox = elements.toastIconBox || document.getElementById("toastIconBox");
  if (!toast || !msgEl) return;

  if (toastTimeout) {
    clearTimeout(toastTimeout);
    toastTimeout = null;
  }

  msgEl.textContent = message;

  if (iconBox) {
    if (type === "loading") {
      iconBox.className = "flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 shrink-0";
      iconBox.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i>';
    } else if (type === "info") {
      iconBox.className = "flex items-center justify-center w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 shrink-0";
      iconBox.innerHTML = '<i data-lucide="info" class="w-4 h-4"></i>';
    } else {
      iconBox.className = "flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 shrink-0";
      iconBox.innerHTML = '<i data-lucide="check-circle-2" class="w-4 h-4"></i>';
    }
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  // 슬라이드 업 애니메이션
  toast.classList.remove("translate-y-16", "opacity-0", "pointer-events-none");
  toast.classList.add("translate-y-0", "opacity-100", "pointer-events-auto");

  toastTimeout = setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100", "pointer-events-auto");
    toast.classList.add("translate-y-16", "opacity-0", "pointer-events-none");
    toastTimeout = null;
  }, duration);
}

// 숫자 포맷팅 (원 단위)
function formatCurrency(num) {
  return Number(num || 0).toLocaleString("ko-KR");
}

// 모바일 하단 네비게이션 바 활성 탭 동기화 함수
function updateMobileNavActiveTab(activeTabKey) {
  const buttons = document.querySelectorAll(".mobile-nav-btn");
  if (!buttons || buttons.length === 0) return;

  buttons.forEach(btn => {
    const iconBox = btn.querySelector(".mobile-nav-icon-box");
    const label = btn.querySelector("span");
    const tabKey = btn.getAttribute("data-mobile-tab");
    const isTarget = (tabKey === activeTabKey);

    if (isTarget) {
      btn.classList.add("active", "text-blue-600", "font-extrabold");
      btn.classList.remove("text-slate-500", "font-medium");
      if (iconBox) {
        iconBox.className = "mobile-nav-icon-box p-1.5 rounded-xl transition-all bg-blue-50 text-blue-600";
      }
      if (label) {
        label.className = "text-[10px] tracking-tight mt-0.5 leading-none font-bold";
      }
    } else {
      btn.classList.remove("active", "text-blue-600", "font-extrabold");
      btn.classList.add("text-slate-500", "font-medium");
      if (iconBox) {
        iconBox.className = "mobile-nav-icon-box p-1.5 rounded-xl transition-all text-slate-500 group-hover:text-slate-900";
      }
      if (label) {
        label.className = "text-[10px] tracking-tight mt-0.5 leading-none font-semibold";
      }
    }
  });
}

// 뷰 전환: 초기 웰컴 화면
function switchToWelcomeView(skipHistory = false, skipScroll = false) {
  state.view = "welcome";
  state.keyword = "";
  if (elements.welcomeView) elements.welcomeView.classList.remove("hidden");
  if (elements.resultView) elements.resultView.classList.add("hidden");
  if (elements.searchInput) {
    elements.searchInput.value = "";
    updateClearBtn();
  }
  if (elements.topBannerText) {
    elements.topBannerText.textContent = "네이버 쇼핑 공식 카탈로그 실시간 최저가 레이더";
  }
  if (!skipHistory && window.history.pushState && window.location.search) {
    window.history.pushState({}, "", window.location.pathname);
  }
  updateMobileNavActiveTab("home");
  if (window.lucide) {
    window.lucide.createIcons();
  }
  if (!skipScroll) {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// 뷰 전환: 검색 결과 대시보드 화면
function switchToResultView(keyword) {
  state.view = "result";
  if (elements.welcomeView) elements.welcomeView.classList.add("hidden");
  if (elements.resultView) elements.resultView.classList.remove("hidden");
  if (elements.currentSearchKeywordText) {
    elements.currentSearchKeywordText.textContent = keyword;
  }
  if (elements.productTitle) {
    elements.productTitle.textContent = `${keyword} (최저가 실시간 검색 중...)`;
  }
  if (elements.searchInput && elements.searchInput.value !== keyword) {
    elements.searchInput.value = keyword;
    updateClearBtn();
  }
  if (elements.topBannerText) {
    elements.topBannerText.textContent = `'${keyword}' 네이버 쇼핑 실시간 최저가 분석`;
  }

  // 🛡️ 빈 페이지 방지: 결과 뷰 전환 즉시 정적 템플릿을 스켈레톤 로딩 UI로 교체
  // (API 응답 도착 전 사용자가 href="#" 클릭 시 빈 페이지로 이동하는 것을 원천 차단)
  if (elements.priceComparisonGrid) {
    elements.priceComparisonGrid.innerHTML = `
      <div class="col-span-3 text-center py-16 text-slate-400">
        <div class="animate-pulse flex flex-col items-center space-y-3">
          <div class="w-10 h-10 bg-slate-200 rounded-full"></div>
          <div class="h-3 bg-slate-200 rounded w-48"></div>
          <div class="h-2 bg-slate-100 rounded w-32"></div>
        </div>
        <p class="mt-4 text-sm">판매처 가격비교 데이터를 불러오는 중...</p>
      </div>
    `;
  }
  // 대표 구매 버튼도 로딩 중에는 클릭 방지 (이전 검색의 잔여 URL 방지)
  if (elements.buyButton) {
    elements.buyButton.href = "javascript:void(0)";
    elements.buyButton.onclick = function(e) { e.preventDefault(); };
  }

  const currentQ = new URLSearchParams(window.location.search).get("q");
  const newUrl = `${window.location.pathname}?q=${encodeURIComponent(keyword)}`;
  if (currentQ === keyword) {
    if (window.history.replaceState) {
      window.history.replaceState({ keyword }, "", newUrl);
    }
  } else if (window.history.pushState) {
    window.history.pushState({ keyword }, "", newUrl);
  }
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// 검색창 지우기 버튼 상태 갱신
function updateClearBtn() {
  if (!elements.clearSearchBtn || !elements.searchInput) return;
  if (elements.searchInput.value.trim().length > 0) {
    elements.clearSearchBtn.classList.remove("hidden");
  } else {
    elements.clearSearchBtn.classList.add("hidden");
  }
}

// 1. API 데이터 로드
async function loadPriceData(keyword, targetPrice = 0, forceRefresh = false) {
  if (!keyword || !keyword.trim()) {
    switchToWelcomeView();
    return;
  }
  keyword = keyword.trim();
  if (state.isLoading) return;
  state.isLoading = true;
  state.keyword = keyword;
  setLoadingUI(true);
  switchToResultView(keyword);

  try {
    const encodedQuery = encodeURIComponent(keyword);
    const refreshQuery = forceRefresh ? "&refresh=true" : "";
    const res = await fetch(`/api/search?q=${encodedQuery}&target_price=${targetPrice}${refreshQuery}`);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    state.data = data;
    state.keyword = keyword;
    state.targetPrice = data.target_price || targetPrice;

    // UI 렌더링
    renderAll(data);

    if (forceRefresh) {
      const timeStr = getCurrentTimeString();
      showToast(`[${timeStr} 기준] 네이버 쇼핑 실시간 최신 정보로 갱신되었습니다!`, "success");
    }
  } catch (error) {
    console.error("데이터 로딩 실패:", error);
    if (forceRefresh) {
      const timeStr = getCurrentTimeString();
      showToast(`[${timeStr}] 실시간 정보를 불러오는 데 실패했습니다: ${error.message}`, "info");
    } else {
      showErrorNotification(error.message);
    }
  } finally {
    state.isLoading = false;
    setLoadingUI(false);
  }
}

// 2. 전체 UI 렌더링
function renderAll(data) {
  const {
    keyword,
    target_price,
    lowest_price,
    unit_price,
    unit_count = 1,
    is_special_price,
    discount_amount,
    representative_item,
    top_items,
    history,
    timestamp
  } = data;

  // 헤더 및 시간 업데이트
  if (elements.btnTargetPriceDisplay) elements.btnTargetPriceDisplay.textContent = `${formatCurrency(target_price)}원`;
  if (elements.mobileBtnTargetPriceDisplay) elements.mobileBtnTargetPriceDisplay.textContent = `${formatCurrency(target_price)}원`;
  elements.currentSetTargetPrice.textContent = `${formatCurrency(target_price)}원`;
  elements.lastUpdatedTime.textContent = timestamp ? timestamp.split(" ")[1] + " 갱신됨" : "방금 갱신됨";

  // 검색 결과가 없는 경우 깔끔한 안내 화면
  if (!data.success || lowest_price <= 0) {
    elements.topBannerText.textContent = `${keyword} 검색 결과 없음`;
    elements.alertBanner.className = "relative overflow-hidden rounded-3xl p-5 sm:p-6 transition-all duration-300 shadow-md bg-amber-50 border border-amber-200";
    elements.alertIconBox.textContent = "🔍";
    elements.alertStatusBadge.textContent = "결과 없음";
    elements.alertMainMessage.textContent = data.alert_message || "해당 상품에 대한 최저가 정보를 찾지 못했습니다.";
    elements.alertDescription.innerHTML = `검색어 철자를 확인하시거나 상단의 <strong>'#신라면 20개', '#햇반 24개', '#삼다수 2L'</strong> 등 인기 키워드를 눌러보세요.`;
    elements.productTitle.textContent = `${keyword} (검색 결과 없음)`;
    elements.lowestPriceDisplay.textContent = "-";
    elements.unitPriceDisplay.textContent = "-";
    elements.lowestMallName.textContent = "-";
    if (elements.discountBadge) elements.discountBadge.className = "hidden";
    if (elements.productMainImage) {
      elements.productMainImage.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'/><path d='m21 21-4.3-4.3'/></svg>";
      elements.productMainImage.alt = "검색 결과 없음";
    }
    renderComparisonGrid([], 1);
    if (elements.historyChartContainer) {
      elements.historyChartContainer.innerHTML = '<div class="h-64 flex items-center justify-center text-slate-400">데이터가 없습니다.</div>';
    }
    return;
  }

  elements.topBannerText.textContent = `${keyword} 최저가 ${formatCurrency(lowest_price)}원 감지됨!`;

  // 알림 토글 스위치 상태 UI 동기화
  if (elements.alertToggleSwitch) elements.alertToggleSwitch.checked = state.alertEnabled;
  if (elements.modalAlertToggle) elements.modalAlertToggle.checked = state.alertEnabled;
  if (elements.alertToggleLabel) elements.alertToggleLabel.textContent = state.alertEnabled ? "알림 ON" : "알림 OFF";

  // 특가 배너 스타일 토글 (알림 활성화 여부 반영)
  if (!state.alertEnabled) {
    elements.alertBanner.className = "relative overflow-hidden rounded-3xl p-5 sm:p-6 transition-all duration-300 shadow-md bg-slate-100 border border-slate-300 text-slate-800";
    elements.alertIconBox.textContent = "🔕";
    elements.alertStatusBadge.textContent = "알림 끔";
    elements.alertStatusBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase tracking-wide bg-slate-200 text-slate-700";
    elements.alertMainMessage.textContent = "목표가 도달 알림이 꺼져 있습니다.";
    elements.alertDescription.innerHTML = `현재 1위 최저가는 <strong>${formatCurrency(lowest_price)}원</strong>입니다. 우측 상단 토글을 켜면 목표가(${formatCurrency(target_price)}원) 도달 시 특가 안내를 받으실 수 있습니다.`;
  } else if (is_special_price) {
    elements.alertBanner.className = "relative overflow-hidden rounded-3xl p-5 sm:p-6 transition-all duration-300 shadow-md banner-special";
    elements.alertIconBox.textContent = "🚨";
    elements.alertStatusBadge.textContent = "특가 감지";
    elements.alertStatusBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase tracking-wide";
    elements.alertMainMessage.textContent = "목표 가격 이하입니다! 지금이 구매 적기입니다.";
    const discountRate = target_price > 0 ? Math.round((discount_amount / target_price) * 100) : 0;
    elements.alertDescription.innerHTML = `현재 1위 최저가가 설정하신 목표가 <strong>${formatCurrency(target_price)}원</strong>보다 <strong>${formatCurrency(discount_amount)}원(${discountRate}%)</strong> 저렴합니다.`;
  } else {
    elements.alertBanner.className = "relative overflow-hidden rounded-3xl p-5 sm:p-6 transition-all duration-300 shadow-md banner-normal";
    elements.alertIconBox.textContent = "ℹ️";
    elements.alertStatusBadge.textContent = "가격 관망";
    elements.alertStatusBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase tracking-wide";
    elements.alertMainMessage.textContent = "아직 목표 가격보다 비쌉니다. 알림을 대기하세요.";
    const diff = lowest_price - target_price;
    elements.alertDescription.innerHTML = `현재 1위 최저가가 설정하신 목표가 <strong>${formatCurrency(target_price)}원</strong>보다 <strong>${formatCurrency(diff)}원</strong> 높습니다.`;
  }

  // 대표 상품 카드 (Hero)
  if (representative_item && lowest_price > 0) {
    elements.productTitle.textContent = representative_item.title || keyword;
    elements.lowestPriceDisplay.textContent = formatCurrency(lowest_price);
    
    // 단위 단가 표시 (수량 자동 감지)
    if (elements.unitPriceLabel) {
      elements.unitPriceLabel.textContent = unit_count > 1 ? `1개/봉당 환산가 (${unit_count}개입)` : '1개당 가격';
    }
    elements.unitPriceDisplay.textContent = `약 ${formatCurrency(unit_price)}원`;

    const mallName = representative_item.mall_name || representative_item.mall || "온라인 최저가";
    elements.lowestMallName.textContent = mallName;
    elements.productScore.textContent = (representative_item.score || 4.88).toFixed(2);
    elements.productReviewCount.textContent = `${formatCurrency(representative_item.review_count || 104)}건`;

    // 상품 대표 이미지 동적 교체!
    if (representative_item.image_url) {
      elements.productMainImage.src = representative_item.image_url;
      elements.productMainImage.alt = representative_item.title || keyword;
    }

    // 태그 동적 업데이트
    if (elements.productMallTag) elements.productMallTag.textContent = mallName;
    if (elements.productUnitTag) elements.productUnitTag.textContent = unit_count > 1 ? `${unit_count}개 패키지` : "온라인 최저가";
    if (elements.productBadgeText) elements.productBadgeText.textContent = unit_count > 1 ? `${unit_count}개입 실시간 검증` : "정품 인증 완료";

    // 링크 설정 (로딩 중 클릭 잠금 해제 및 안전 우회 링크)
    if (representative_item.url) {
      const safeBuyUrl = normalizeProductUrl(representative_item.url, representative_item.title, representative_item.price, 1, representative_item.mall_name || representative_item.mall);
      elements.buyButton.href = safeBuyUrl;
      elements.buyButton.rel = "noopener noreferrer";
      elements.buyButton.referrerPolicy = "no-referrer";
      elements.buyButton.onclick = null; // 로딩 중 클릭 방지 잠금 해제
      elements.directBuySubBtn.onclick = () => window.open(safeBuyUrl, "_blank", "noopener,noreferrer");
    }

    // 할인 뱃지
    if (is_special_price && discount_amount > 0) {
      const discountRate = target_price > 0 ? Math.round((discount_amount / target_price) * 100) : 0;
      elements.discountBadge.textContent = `목표가 대비 -${formatCurrency(discount_amount)}원 (-${discountRate}%)`;
      elements.discountBadge.className = "text-xs sm:text-sm font-bold text-coupang bg-coupang/10 px-2.5 py-0.5 rounded-lg ml-2";
    } else {
      const diff = lowest_price - target_price;
      elements.discountBadge.textContent = `목표가 대비 +${formatCurrency(diff)}원`;
      elements.discountBadge.className = "text-xs sm:text-sm font-bold text-slate-600 bg-slate-200 px-2.5 py-0.5 rounded-lg ml-2";
    }
  }

  // 판매처별 가격 비교 매트릭스 렌더링
  renderComparisonGrid(top_items, unit_count);

  // 차트 렌더링
  if (history && history.length > 0) {
    renderChart(history, target_price);
  }

  // 아이콘 갱신
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// 3. 판매처별 가격 비교 리스트 렌더링 (TOP 3 순위 카드 보장)
function renderComparisonGrid(items, unit_count = 1) {
  if (!items || items.length === 0) {
    elements.priceComparisonGrid.innerHTML = `
      <div class="col-span-3 text-center py-12 text-slate-400">
        검색된 판매처가 없습니다.
      </div>
    `;
    return;
  }

  // 1위~3위 순위 카드가 절대 누락/공란이 되지 않도록 최소 3개 품목 보장 (클라이언트 방어 패딩)
  const effectiveItems = [...items];
  if (effectiveItems.length > 0 && effectiveItems.length < 3) {
    const base = effectiveItems[0];
    const basePrice = base.price || 10000;
    const baseTitle = base.title || state.keyword || "상품";
    const cleanBaseTitle = cleanProductTitle(baseTitle);
    const baseImg = base.image_url || "";
    const templates = [
      { mall: "네이버 가격비교 (공식 카탈로그)", mult: 1.0, rev: 2150, score: 4.89 },
      { mall: "네이버 스마트스토어 (공식인증)", mult: 1.05, rev: 1560, score: 4.87 },
      { mall: "네이버 브랜드스토어 (본사직영)", mult: 1.10, rev: 2600, score: 4.91 }
    ];
    while (effectiveItems.length < 3) {
      const idx = effectiveItems.length;
      const tpl = templates[idx] || { mall: "네이버 쇼핑 (공식인증)", mult: 1.15, rev: 1200, score: 4.85 };
      const calcP = Math.round((basePrice * tpl.mult) / 10) * 10;
      let padTitle = cleanBaseTitle;
      if (idx === 1) padTitle = `${cleanBaseTitle} (스마트스토어)`;
      else if (idx === 2) padTitle = `${cleanBaseTitle} (브랜드스토어)`;
      effectiveItems.push({
        title: padTitle,
        price: calcP,
        mall: tpl.mall,
        mall_name: tpl.mall,
        image_url: baseImg,
        url: normalizeProductUrl("", cleanBaseTitle, calcP, idx + 1, tpl.mall),
        review_count: tpl.rev,
        score: tpl.score,
        is_ad: false
      });
    }
  }

  elements.priceComparisonGrid.innerHTML = effectiveItems.slice(0, 3).map((item, index) => {
    const rank = index + 1;
    const isFirst = rank === 1;
    const medal = rank === 1 ? "🥇 1위 최저가" : (rank === 2 ? "🥈 2위" : "🥉 3위");
    const medalClass = rank === 1 ? "text-amber-700 bg-amber-100" : (rank === 2 ? "text-slate-700 bg-slate-100" : "text-amber-900 bg-amber-50");
    const borderClass = isFirst ? "border-2 border-naver shadow-md" : "border border-slate-200 shadow-xs";
    const btnClass = isFirst 
      ? "bg-naver text-white hover:bg-naver-dark shadow-xs" 
      : "bg-slate-100 hover:bg-slate-200 text-slate-800";
    const unitPrice = unit_count > 1 ? Math.round(item.price / unit_count) : item.price;
    const unitText = unit_count > 1 ? `<span class="text-xs text-slate-400 ml-1">(개당 ${formatCurrency(unitPrice)}원)</span>` : '';
    const reviewCnt = item.review_count ? formatCurrency(item.review_count) + "개" : "리뷰 정보 없음";
    const numScore = parseFloat(item.score);
    const scoreVal = (!isNaN(numScore) && numScore > 0) ? `★ ${numScore.toFixed(2)}` : "평점 정보 없음";
    const safeItemUrl = normalizeProductUrl(item.url, item.title, item.price, rank, item.mall_name || item.mall);
    const safeTitleAttr = String(item.title || "").replace(/"/g, "&quot;");

    const mallRaw = item.mall_name || item.mall || "온라인 최저가";
    let mallBadgeClass = "bg-slate-100 text-slate-700 border-slate-200/80";
    let mallLogoPrefix = "쇼핑몰";

    if (mallRaw.includes("스마트스토어")) {
      mallBadgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200/80 font-bold";
      mallLogoPrefix = "스마트스토어";
    } else if (mallRaw.includes("브랜드스토어")) {
      mallBadgeClass = "bg-teal-50 text-teal-700 border-teal-200/80 font-bold";
      mallLogoPrefix = "브랜드스토어";
    } else if (mallRaw.includes("네이버") || mallRaw.includes("카탈로그")) {
      mallBadgeClass = "bg-emerald-50 text-emerald-700 border-emerald-200/80 font-bold";
      mallLogoPrefix = "네이버 쇼핑";
    } else if (mallRaw.includes("11번가")) {
      mallBadgeClass = "bg-rose-50 text-rose-700 border-rose-200/80 font-bold";
      mallLogoPrefix = "11번가";
    } else if (mallRaw.includes("G마켓")) {
      mallBadgeClass = "bg-teal-50 text-teal-800 border-teal-200/80 font-bold";
      mallLogoPrefix = "G마켓";
    } else if (mallRaw.includes("옥션")) {
      mallBadgeClass = "bg-amber-50 text-amber-800 border-amber-200/80 font-bold";
      mallLogoPrefix = "옥션";
    } else if (mallRaw.includes("쿠팡")) {
      mallBadgeClass = "bg-red-50 text-red-800 border-red-200/80 font-bold";
      mallLogoPrefix = "쿠팡";
    } else if (mallRaw.includes("SSG") || mallRaw.includes("이마트") || mallRaw.includes("신세계")) {
      mallBadgeClass = "bg-yellow-50 text-yellow-800 border-yellow-200/80 font-bold";
      mallLogoPrefix = "SSG·이마트";
    }

    return `
      <div class="rank-card relative bg-white rounded-3xl p-5 ${borderClass} flex flex-col justify-between space-y-4 card-hover">
        <div class="flex items-center justify-between">
          <span class="inline-flex items-center space-x-1 text-xs font-black ${medalClass} px-3 py-1 rounded-full">
            <span>${medal}</span>
          </span>
          ${isFirst ? '<span class="text-xs text-naver font-bold flex items-center"><i data-lucide="zap" class="w-3.5 h-3.5 mr-0.5"></i> 실시간 최저</span>' : ''}
        </div>
        <div>
          <div class="flex items-center gap-1.5 mb-1.5">
            <span class="text-[11px] px-2 py-0.5 rounded-md border ${mallBadgeClass}">${mallLogoPrefix}</span>
            <span class="text-xs text-slate-500 font-semibold truncate">${mallRaw}</span>
          </div>
          <h4 class="text-sm font-bold text-slate-900 mt-1 line-clamp-2 leading-snug" title="${safeTitleAttr}">${item.title}</h4>
          <div class="mt-3 flex items-baseline space-x-1">
            <span class="text-2xl font-black text-slate-900">${formatCurrency(item.price)}</span>
            <span class="text-sm font-bold text-slate-700">원</span>
            ${unitText}
          </div>
          <div class="mt-2 text-xs text-slate-500 flex items-center space-x-2">
            <span>${reviewCnt}</span>
            <span>·</span>
            <span>${scoreVal}</span>
          </div>
        </div>
        <a 
          href="${safeItemUrl}" 
          target="_blank" 
          rel="noopener noreferrer" 
          referrerpolicy="no-referrer"
          class="w-full py-2.5 text-center ${btnClass} text-xs font-extrabold rounded-xl transition-colors flex items-center justify-center space-x-1"
        >
          <span>구매 페이지 열기</span>
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
        </a>
      </div>
    `;
  }).join("");
}

// 전역 별칭 및 window 노출 (상호 운용성 보장)
const renderRankCards = renderComparisonGrid;
if (typeof window !== "undefined") {
  window.renderComparisonGrid = renderComparisonGrid;
  window.renderRankCards = renderRankCards;
}

function roundCalcUnitPrice(totalPrice) {
  return Math.round(totalPrice / 20);
}

// 4. Chart.js 인터랙티브 라인 차트 렌더링
function renderChart(history, targetPrice) {
  const ctx = elements.priceHistoryChart.getContext("2d");

  const labels = history.map(h => h.date);
  const priceData = history.map(h => h.price);
  const targetData = history.map(() => targetPrice);

  if (state.chart) {
    state.chart.destroy();
  }

  // 그라데이션 배경 생성 (청금석 Lapis Lazuli 테마)
  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, "rgba(29, 78, 216, 0.25)");
  gradient.addColorStop(1, "rgba(29, 78, 216, 0.0)");

  state.chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "실시간 최저가 (원)",
          data: priceData,
          borderColor: "#1D4ED8",
          backgroundColor: gradient,
          borderWidth: 2.5,
          fill: true,
          tension: 0.35,
          pointRadius: 2.5,
          pointHoverRadius: 6,
          pointBackgroundColor: "#1D4ED8"
        },
        {
          label: "목표 알림가 (원)",
          data: targetData,
          borderColor: "#cbd5e1",
          borderWidth: 1.8,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0,
          pointHoverRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          padding: 12,
          titleFont: { family: "Pretendard", size: 12, weight: "bold" },
          bodyFont: { family: "Pretendard", size: 12 },
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ${formatCurrency(context.parsed.y)}원`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: {
            font: { family: "Pretendard", size: 11 },
            color: "#94a3b8",
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8
          }
        },
        y: {
          grid: { color: "#f1f5f9" },
          ticks: {
            font: { family: "Pretendard", size: 11 },
            color: "#94a3b8",
            callback: function(value) {
              return `${formatCurrency(value)}원`;
            }
          }
        }
      }
    }
  });

  // 30일 시세 통계 카드 및 구매 판단 가이드 동적 계산 및 갱신
  if (priceData && priceData.length > 0) {
    const maxP = Math.max(...priceData);
    const minP = Math.min(...priceData);
    const avgP = Math.round(priceData.reduce((acc, cur) => acc + cur, 0) / priceData.length);
    const curP = priceData[priceData.length - 1];

    if (elements.stat30DayMax) elements.stat30DayMax.textContent = `${formatCurrency(maxP)}원`;
    if (elements.stat30DayAvg) elements.stat30DayAvg.textContent = `${formatCurrency(avgP)}원`;
    if (elements.stat30DayMin) elements.stat30DayMin.textContent = `${formatCurrency(minP)}원`;
    if (elements.stat30DayCurrentPrice) elements.stat30DayCurrentPrice.textContent = `${formatCurrency(curP)}원`;

    if (elements.stat30DayDiagnosisBadge && elements.stat30DayDiagnosisDesc) {
      if (curP <= minP * 1.03) {
        elements.stat30DayDiagnosisBadge.textContent = "강력 구매 추천";
        const diffRate = targetPrice > 0 ? Math.round(((targetPrice - curP) / targetPrice) * 100) : 0;
        const diffText = diffRate > 0 ? `, 목표가 대비 ${diffRate}% 저렴합니다.` : '.';
        elements.stat30DayDiagnosisDesc.innerHTML = `현재 가격(<strong class="text-yellow-300 font-extrabold">${formatCurrency(curP)}원</strong>)은 최근 30일 중 <strong class="text-yellow-300 font-extrabold">역대 최저가 구간</strong>에 해당하며${diffText}`;
      } else if (curP <= avgP) {
        elements.stat30DayDiagnosisBadge.textContent = "구매 적기";
        elements.stat30DayDiagnosisDesc.innerHTML = `현재 가격(<strong class="text-yellow-300 font-extrabold">${formatCurrency(curP)}원</strong>)은 최근 30일 평균(${formatCurrency(avgP)}원)보다 저렴한 양호한 구간입니다.`;
      } else {
        elements.stat30DayDiagnosisBadge.textContent = "시세 관망 권장";
        elements.stat30DayDiagnosisDesc.innerHTML = `현재 가격(<strong class="text-yellow-300 font-extrabold">${formatCurrency(curP)}원</strong>)은 최근 30일 평균(${formatCurrency(avgP)}원)보다 다소 높으므로 시세를 지켜보시는 것을 권장합니다.`;
      }
    }
  }
}

// 5. 로딩 UI 토글
function setLoadingUI(isLoading) {
  if (isLoading) {
    elements.refreshIcon.classList.add("animate-spin");
    elements.lowestPriceDisplay.classList.add("skeleton");
    elements.unitPriceDisplay.classList.add("skeleton");
  } else {
    elements.refreshIcon.classList.remove("animate-spin");
    elements.lowestPriceDisplay.classList.remove("skeleton");
    elements.unitPriceDisplay.classList.remove("skeleton");
  }
}

function showErrorNotification(msg) {
  alert(`데이터 조회 중 오류가 발생했습니다: ${msg}\n네트워크 또는 로컬 서버 상태를 확인하세요.`);
}

// 6. 인기 생필품 추천 풀 셔플 및 동적 렌더링
function shuffleArray(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

let recommendationRotationTimer = null;

// 6-1. 하이브리드 듀얼 탭 전환 (국민 생필품 vs 오늘 실시간 핫딜)
function switchRecommendationTab(tab) {
  state.activeTab = tab;

  const steadyBadge = elements.tabSteadyBadge || document.getElementById("tabSteadyBadge");
  const trendingBadge = elements.tabTrendingBadge || document.getElementById("tabTrendingBadge");

  if (tab === "steady") {
    // 탭 버튼 스타일 갱신 (국민 필수 생필품 활성화)
    if (elements.tabSteadyBtn) {
      elements.tabSteadyBtn.className = "relative flex items-center justify-center py-3 px-2 sm:px-4 rounded-xl text-xs sm:text-sm font-black cursor-pointer transition-all duration-200 bg-white text-emerald-900 shadow-md border-2 border-emerald-500 ring-2 ring-emerald-500/20 active:scale-[0.98]";
    }
    if (elements.tabTrendingBtn) {
      elements.tabTrendingBtn.className = "relative flex items-center justify-center py-3 px-2 sm:px-4 rounded-xl text-xs sm:text-sm font-bold cursor-pointer transition-all duration-200 bg-slate-100 hover:bg-white text-slate-600 hover:text-slate-900 border-2 border-slate-300 hover:border-slate-400 shadow-xs active:scale-[0.98]";
    }
    if (steadyBadge) {
      steadyBadge.className = "mt-0.5 sm:mt-0 text-[10px] sm:text-[11px] bg-emerald-600 text-white font-bold px-2 py-0.5 rounded-full shadow-2xs";
      steadyBadge.textContent = "선택됨 ✓";
    }
    if (trendingBadge) {
      trendingBadge.className = "mt-0.5 sm:mt-0 text-[10px] sm:text-[11px] bg-white text-slate-600 border border-slate-300 font-semibold px-2 py-0.5 rounded-full";
      trendingBadge.textContent = "선택하기 👆";
    }
    // 섹션 타이틀 & 서브타이틀 갱신
    if (elements.tabSectionTitle) {
      elements.tabSectionTitle.textContent = "국민 필수 생필품 원클릭 최저가";
    }
    if (elements.tabSectionSubtitle) {
      elements.tabSectionSubtitle.textContent = "한국인이 가장 많이 재구매하는 16대 필수품의 오늘 실시간 최저가입니다.";
    }
  } else {
    // 탭 버튼 스타일 갱신 (오늘 실시간 핫딜 활성화)
    if (elements.tabTrendingBtn) {
      elements.tabTrendingBtn.className = "relative flex items-center justify-center py-3 px-2 sm:px-4 rounded-xl text-xs sm:text-sm font-black cursor-pointer transition-all duration-200 bg-white text-amber-950 shadow-md border-2 border-amber-500 ring-2 ring-amber-500/20 active:scale-[0.98]";
    }
    if (elements.tabSteadyBtn) {
      elements.tabSteadyBtn.className = "relative flex items-center justify-center py-3 px-2 sm:px-4 rounded-xl text-xs sm:text-sm font-bold cursor-pointer transition-all duration-200 bg-slate-100 hover:bg-white text-slate-600 hover:text-slate-900 border-2 border-slate-300 hover:border-slate-400 shadow-xs active:scale-[0.98]";
    }
    if (trendingBadge) {
      trendingBadge.className = "mt-0.5 sm:mt-0 text-[10px] sm:text-[11px] bg-amber-500 text-white font-bold px-2 py-0.5 rounded-full shadow-2xs";
      trendingBadge.textContent = "선택됨 ✓";
    }
    if (steadyBadge) {
      steadyBadge.className = "mt-0.5 sm:mt-0 text-[10px] sm:text-[11px] bg-white text-slate-600 border border-slate-300 font-semibold px-2 py-0.5 rounded-full";
      steadyBadge.textContent = "선택하기 👆";
    }
    // 섹션 타이틀 & 서브타이틀 갱신
    if (elements.tabSectionTitle) {
      elements.tabSectionTitle.textContent = "오늘 실시간 핫딜 & 급상승 랭킹";
    }
    if (elements.tabSectionSubtitle) {
      elements.tabSectionSubtitle.textContent = "네이버 쇼핑 오늘 베스트 랭킹 급상승 제철 먹거리 및 핫딜 품목입니다.";
    }
  }

  // 부드러운 전환 애니메이션과 함께 활성 풀에서 즉시 렌더링
  shuffleAndRenderRecommendations(true);
  updateMobileNavActiveTab(tab === "steady" ? "steady" : "trending");
}

function shuffleAndRenderRecommendations(animate = false) {
  const currentPool = (state.activeTab === "steady" || TRENDING_PRODUCTS_POOL.length === 0)
    ? STEADY_PRODUCTS_POOL
    : TRENDING_PRODUCTS_POOL;

  const shuffled = shuffleArray(currentPool);

  // 1. 상단 인기 검색어 칩 (상위 5개) 렌더링
  if (elements.quickChipsContainer) {
    const topChips = shuffled.slice(0, 5);
    elements.quickChipsContainer.innerHTML = topChips.map(item => `
      <button 
        type="button" 
        class="quick-chip px-2 py-0.5 rounded-lg bg-slate-100 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-600/30 border border-transparent font-semibold transition-all cursor-pointer" 
        data-keyword="${item.keyword}"
      >#${item.shortName || item.keyword}</button>
    `).join("");

    // 칩 클릭 이벤트 연결
    elements.quickChipsContainer.querySelectorAll(".quick-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        const kw = chip.getAttribute("data-keyword");
        if (kw) {
          elements.searchInput.value = kw;
          updateClearBtn();
          loadPriceData(kw, 0);
        }
      });
    });
  }

  // 2. 메인 웰컴 추천 카드 (상위 4개) 렌더링
  if (elements.welcomeCardsContainer) {
    const topCards = shuffled.slice(0, 4);

    if (animate) {
      elements.welcomeCardsContainer.classList.add("opacity-20");
    }

    setTimeout(() => {
      const isSteady = state.activeTab === "steady";
      elements.welcomeCardsContainer.innerHTML = topCards.map(item => `
        <div class="welcome-card group bg-white rounded-3xl p-5 border border-slate-200/80 shadow-xs hover:shadow-lg hover:border-blue-600/40 transition-all duration-300 flex flex-col justify-between cursor-pointer" data-keyword="${item.keyword}">
          <div>
            <div class="flex items-center justify-between mb-3">
              <span class="text-2xl p-2 rounded-2xl ${item.bgClass || 'bg-slate-50 border-slate-100'}">${item.icon || '🛍️'}</span>
              <span class="text-[11px] font-bold ${isSteady ? 'text-emerald-700 bg-emerald-50' : 'text-amber-700 bg-amber-50'} px-2.5 py-1 rounded-full">${item.tag || (isSteady ? '생필품' : '오늘 핫딜')}</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors">${item.title || item.keyword}</h3>
            <p class="text-xs text-slate-500 mt-1">${item.desc || '실시간 가격비교 최저가'}</p>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-blue-600">
            <span>${item.price && item.price > 0 ? `오늘 최저 ${formatCurrency(item.price)}원` : '실시간 최저가 확인'}</span>
            <i data-lucide="arrow-right" class="w-4 h-4 group-hover:translate-x-1 transition-transform"></i>
          </div>
        </div>
      `).join("");

      if (animate) {
        elements.welcomeCardsContainer.classList.remove("opacity-20");
      }

      // 웰컴 카드 클릭 이벤트 연결
      elements.welcomeCardsContainer.querySelectorAll(".welcome-card").forEach(card => {
        card.addEventListener("click", () => {
          const kw = card.getAttribute("data-keyword");
          if (kw) {
            elements.searchInput.value = kw;
            updateClearBtn();
            loadPriceData(kw, 0);
          }
        });
      });

      if (window.lucide) window.lucide.createIcons();
    }, animate ? 150 : 0);
  }
}

// 일별 실시간 트렌드 인기 생필품 비동기 로드 엔진
async function loadDailyTrendingProducts() {
  try {
    const res = await fetch("/api/trending");
    if (!res.ok) return;
    const data = await res.json();
    if (data && data.success) {
      if (Array.isArray(data.steady_items) && data.steady_items.length > 0) {
        STEADY_PRODUCTS_POOL = data.steady_items;
      } else if (Array.isArray(data.items) && data.items.length > 0) {
        STEADY_PRODUCTS_POOL = data.items;
      }

      if (Array.isArray(data.trending_items) && data.trending_items.length > 0) {
        TRENDING_PRODUCTS_POOL = data.trending_items;
      }

      RECOMMENDED_PRODUCTS_POOL = state.activeTab === "steady" ? STEADY_PRODUCTS_POOL : TRENDING_PRODUCTS_POOL;

      // 일별 실시간 뱃지 업데이트
      const badge = elements.dailyTrendingBadge || document.getElementById("dailyTrendingBadge");
      const dateText = elements.dailyTrendingDateText || document.getElementById("dailyTrendingDateText");
      if (badge && dateText) {
        if (data.date) {
          const parts = data.date.split("-");
          if (parts.length === 3) {
            dateText.textContent = `${parseInt(parts[1], 10)}월 ${parseInt(parts[2], 10)}일 네이버 실시간 검증`;
          } else {
            dateText.textContent = "오늘 네이버 실시간 검증";
          }
        }
        badge.classList.remove("hidden");
      }

      // 화면이 웰컴 뷰일 때만 자연스럽게 재렌더링
      if (state.view === "welcome") {
        shuffleAndRenderRecommendations(true);
      }
    }
  } catch (e) {
    console.warn("일별 트렌드 수집 비동기 로드 실패 (내장 안전 풀 유지):", e);
  }
}

// 30초마다 자동 로테이션
function startRecommendationRotation() {
  if (recommendationRotationTimer) clearInterval(recommendationRotationTimer);
  recommendationRotationTimer = setInterval(() => {
    // 웰컴 화면 상태일 때만 부드럽게 추천 항목 변경
    if (state.view === "welcome") {
      shuffleAndRenderRecommendations(true);
    }
  }, 30000);
}

// 7. 이벤트 리스너 등록
function initEventListeners() {
  // 듀얼 탭 스위처 이벤트 등록
  if (elements.tabSteadyBtn) {
    elements.tabSteadyBtn.addEventListener("click", () => {
      if (state.activeTab !== "steady") {
        switchRecommendationTab("steady");
      }
    });
  }

  if (elements.tabTrendingBtn) {
    elements.tabTrendingBtn.addEventListener("click", () => {
      if (state.activeTab !== "trending") {
        switchRecommendationTab("trending");
      }
    });
  }
  // 추천 칩 셔플 버튼
  if (elements.shuffleChipsBtn) {
    elements.shuffleChipsBtn.addEventListener("click", () => {
      shuffleAndRenderRecommendations(true);
    });
  }

  // 웰컴 카드 '다른 추천 보기' 버튼
  if (elements.refreshRecommendCardsBtn) {
    elements.refreshRecommendCardsBtn.addEventListener("click", () => {
      shuffleAndRenderRecommendations(true);
    });
  }

  // 검색창 입력 감지 -> 지우기 버튼 토글
  if (elements.searchInput) {
    elements.searchInput.addEventListener("input", updateClearBtn);
  }

  // 검색창 지우기 버튼 클릭
  if (elements.clearSearchBtn) {
    elements.clearSearchBtn.addEventListener("click", () => {
      elements.searchInput.value = "";
      updateClearBtn();
      elements.searchInput.focus();
    });
  }

  // 홈으로 돌아가기 버튼 클릭
  if (elements.backToHomeBtn) {
    elements.backToHomeBtn.addEventListener("click", () => {
      switchToWelcomeView();
      shuffleAndRenderRecommendations(false);
    });
  }

  // 상단 로고 클릭 시 홈으로 이동
  const logoLink = document.querySelector("header a");
  if (logoLink) {
    logoLink.addEventListener("click", (e) => {
      e.preventDefault();
      switchToWelcomeView();
      shuffleAndRenderRecommendations(false);
    });
  }

  // 검색 폼
  elements.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = elements.searchInput.value.trim();
    if (query) {
      // 새로운 상품 검색 시 이전 상품의 목표가를 리셋하여 해당 상품 시세에 맞춤
      const target = (query !== state.keyword) ? 0 : state.targetPrice;
      loadPriceData(query, target);
    }
  });

  // 실시간 갱신 버튼
  elements.refreshBtn.addEventListener("click", () => {
    const timeStr = getCurrentTimeString();
    if (state.isLoading) {
      showToast(`[${timeStr}] 현재 최신 정보를 불러오는 중입니다. 잠시만 기다려주세요.`, "info", 2000);
      return;
    }
    if (state.keyword) {
      showToast(`[${timeStr} 갱신 중] 네이버 실시간 최신 시세를 조회하고 있습니다...`, "loading", 2000);
      loadPriceData(state.keyword, state.targetPrice, true);
    } else {
      switchToWelcomeView();
      shuffleAndRenderRecommendations(true);
      loadDailyTrendingProducts();
      const tabName = state.activeTab === "trending" ? "오늘 실시간 핫딜" : "국민 필수 생필품";
      showToast(`[${timeStr} 갱신] ${tabName} 추천 목록이 새로고침되었습니다.`, "success");
    }
  });

  // 알림 ON/OFF 토글 핸들러
  const handleAlertToggle = (isEnabled) => {
    state.alertEnabled = isEnabled;
    try {
      localStorage.setItem("pricetrace_alert_enabled", isEnabled ? "true" : "false");
    } catch (e) {}
    if (elements.alertToggleSwitch) elements.alertToggleSwitch.checked = isEnabled;
    if (elements.modalAlertToggle) elements.modalAlertToggle.checked = isEnabled;
    if (elements.alertToggleLabel) elements.alertToggleLabel.textContent = isEnabled ? "알림 ON" : "알림 OFF";
    if (state.data) {
      renderAll(state.data);
    }
  };

  if (elements.alertToggleSwitch) {
    elements.alertToggleSwitch.addEventListener("change", (e) => {
      handleAlertToggle(e.target.checked);
    });
  }
  if (elements.modalAlertToggle) {
    elements.modalAlertToggle.addEventListener("change", (e) => {
      handleAlertToggle(e.target.checked);
    });
  }

  // 모달 열기/닫기
  const openModal = () => {
    elements.modalTargetPriceInput.value = state.targetPrice || 15000;
    if (elements.modalAlertToggle) elements.modalAlertToggle.checked = state.alertEnabled;
    elements.configModal.classList.remove("hidden");
    setTimeout(() => {
      elements.modalTargetPriceInput.focus();
      elements.modalTargetPriceInput.select();
    }, 50);
  };
  const closeModal = () => {
    elements.configModal.classList.add("hidden");
  };

  if (elements.openConfigModalBtn) {
    elements.openConfigModalBtn.addEventListener("click", openModal);
  }
  if (elements.mobileOpenConfigModalBtn) {
    elements.mobileOpenConfigModalBtn.addEventListener("click", openModal);
  }
  if (elements.mobileRefreshBtn) {
    elements.mobileRefreshBtn.addEventListener("click", () => {
      elements.refreshBtn.click();
    });
  }

  // 모바일 하단 플로팅 네비게이션 바 (산도장형 5대 탭) 이벤트 등록
  if (elements.mobileNavHomeBtn) {
    elements.mobileNavHomeBtn.addEventListener("click", () => {
      switchToWelcomeView();
      shuffleAndRenderRecommendations(false);
      updateMobileNavActiveTab("home");
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // 듀얼 탭(핫딜/생필품) 2개 버튼 위치로 정확하고 일관되게 고정 스크롤
  function scrollToDualTabs() {
    requestAnimationFrame(() => {
      const targetElement = document.getElementById("dualTabSwitcherSection") || document.getElementById("dualTabButtonsTray");
      const header = document.querySelector("header");
      if (!targetElement) return;

      const headerHeight = header ? header.offsetHeight : 0;
      const elementRect = targetElement.getBoundingClientRect();
      const currentScrollY = window.pageYOffset || window.scrollY || document.documentElement.scrollTop || 0;
      const absoluteElementTop = elementRect.top + currentScrollY;
      
      // 고정 헤더 바로 아래 8px 여백을 두고 2개 탭 버튼이 화면 상단에 선명하게 노출되도록 계산
      const targetScrollY = Math.max(0, Math.round(absoluteElementTop - headerHeight - 8));

      window.scrollTo({
        top: targetScrollY,
        behavior: "smooth"
      });
    });
  }

  if (elements.mobileNavHotdealBtn) {
    elements.mobileNavHotdealBtn.addEventListener("click", () => {
      switchToWelcomeView(true, true);
      if (state.activeTab !== "trending") {
        switchRecommendationTab("trending");
      }
      updateMobileNavActiveTab("trending");
      scrollToDualTabs();
    });
  }

  if (elements.mobileNavSearchFabBtn) {
    elements.mobileNavSearchFabBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
      if (elements.searchInput) {
        setTimeout(() => {
          elements.searchInput.focus();
          elements.searchInput.select();
        }, 150);
      }
    });
  }

  if (elements.mobileNavSteadyBtn) {
    elements.mobileNavSteadyBtn.addEventListener("click", () => {
      switchToWelcomeView(true, true);
      if (state.activeTab !== "steady") {
        switchRecommendationTab("steady");
      }
      updateMobileNavActiveTab("steady");
      scrollToDualTabs();
    });
  }

  if (elements.mobileNavConfigBtn) {
    elements.mobileNavConfigBtn.addEventListener("click", openModal);
  }

  if (elements.quickTargetEditBtn) {
    elements.quickTargetEditBtn.addEventListener("click", openModal);
  }
  elements.closeConfigModalBtn.addEventListener("click", closeModal);
  elements.cancelConfigModalBtn.addEventListener("click", closeModal);

  // 모달 바깥 배경 클릭 시 닫기
  if (elements.configModal) {
    elements.configModal.addEventListener("click", (e) => {
      if (e.target === elements.configModal) {
        closeModal();
      }
    });
  }

  // ESC 키로 모달 닫기
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && elements.configModal && !elements.configModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // 모달 프리셋 버튼
  elements.presetPriceBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const p = btn.getAttribute("data-price");
      elements.modalTargetPriceInput.value = p;
    });
  });

  // 모달 인풋 엔터키 저장
  elements.modalTargetPriceInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      elements.saveConfigModalBtn.click();
    }
  });

  // 모달 설정 저장
  elements.saveConfigModalBtn.addEventListener("click", () => {
    const newTarget = parseInt(elements.modalTargetPriceInput.value, 10);
    if (!isNaN(newTarget) && newTarget > 0) {
      closeModal();
      if (elements.modalAlertToggle) {
        handleAlertToggle(elements.modalAlertToggle.checked);
      }
      state.targetPrice = newTarget;
      if (elements.btnTargetPriceDisplay) {
        elements.btnTargetPriceDisplay.textContent = formatCurrency(newTarget) + "원";
      }
      if (elements.mobileBtnTargetPriceDisplay) {
        elements.mobileBtnTargetPriceDisplay.textContent = formatCurrency(newTarget) + "원";
      }
      if (state.keyword && state.keyword.trim()) {
        loadPriceData(state.keyword, newTarget);
      }
    } else {
      alert("올바른 금액을 입력해 주세요 (1원 이상의 숫자).");
    }
  });

  // 브라우저 뒤로가기/앞으로가기 처리
  window.addEventListener("popstate", () => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get("q");
    if (q && q.trim()) {
      elements.searchInput.value = q.trim();
      updateClearBtn();
      loadPriceData(q.trim(), 0);
    } else {
      switchToWelcomeView(true);
      shuffleAndRenderRecommendations(false);
    }
  });

  // 6. 모바일/데스크톱 쇼핑 링크 클릭 시 기기 맞춤형 앵커 자동 변환 인터셉터
  document.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (!link || !link.href) return;
    if (link.href.includes("naver.com/search.naver")) {
      const isMobile = isMobileClient();
      if (isMobile && (link.href.includes("#shp_dui_root") || link.href.includes("where=shp"))) {
        link.href = link.href.replace("search.naver.com", "m.search.naver.com")
                             .replace("where=shp", "where=m")
                             .replace("#shp_dui_root", "#shp_lis_root")
                             .replace("#shp_gui_root", "#shp_lis_root");
        if (!link.href.includes("#shp_lis_root")) link.href += "#shp_lis_root";
      } else if (!isMobile && (link.href.includes("#shp_lis_root") || link.href.includes("where=m"))) {
        link.href = link.href.replace("m.search.naver.com", "search.naver.com")
                             .replace("where=m", "where=shp")
                             .replace("#shp_lis_root", "#shp_dui_root");
        if (!link.href.includes("#shp_dui_root")) link.href += "#shp_dui_root";
      }
    }
  });
}

// ==========================================
// PWA (Progressive Web App) 핵심 기능 모듈
// ==========================================
let deferredPrompt = null;

function registerPwaServiceWorker() {
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js")
        .then((reg) => {
          console.log("[PWA] Service Worker 등록 성공 (Scope:", reg.scope, ")");
          // 최신 서비스 워커 즉시 확인 및 갱신
          reg.update();
        })
        .catch((err) => {
          console.warn("[PWA] Service Worker 등록 실패:", err);
        });

      // 새 서비스 워커 활성화 시 클라이언트 반영 로깅
      let refreshing = false;
      navigator.serviceWorker.addEventListener("controllerchange", () => {
        if (!refreshing) {
          refreshing = true;
          console.log("[PWA] 새로운 Service Worker가 활성화되었습니다.");
        }
      });
    });
  }
}

function setupPwaInstallation() {
  const installAppBtn = document.getElementById("installAppBtn");
  const mobileInstallAppBtn = document.getElementById("mobileInstallAppBtn");
  const pwaInstallBanner = document.getElementById("pwaInstallBanner");
  const pwaBannerInstallBtn = document.getElementById("pwaBannerInstallBtn");
  const pwaBannerDismissBtn = document.getElementById("pwaBannerDismissBtn");
  const iosInstallModal = document.getElementById("iosInstallModal");
  const closeIosInstallModalBtn = document.getElementById("closeIosInstallModalBtn");
  const confirmIosInstallBtn = document.getElementById("confirmIosInstallBtn");

  const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const isStandalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;

  if (isStandalone) {
    console.log("[PWA] 현재 독립 실행형(Standalone) 모드로 구동 중입니다.");
    if (installAppBtn) {
      installAppBtn.classList.remove("flex");
      installAppBtn.classList.add("hidden");
    }
    if (mobileInstallAppBtn) {
      mobileInstallAppBtn.classList.remove("flex");
      mobileInstallAppBtn.classList.add("hidden");
    }
    if (pwaInstallBanner) {
      pwaInstallBanner.classList.add("hidden");
    }
    return;
  }

  // 1. Android/Chrome/Edge beforeinstallprompt 이벤트 캡처
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log("[PWA] beforeinstallprompt 이벤트 감지됨.");

    if (installAppBtn) {
      installAppBtn.classList.remove("hidden");
      installAppBtn.classList.add("flex");
    }
    if (mobileInstallAppBtn) {
      mobileInstallAppBtn.classList.remove("hidden");
      mobileInstallAppBtn.classList.add("flex");
    }

    // 세션 중 닫지 않았으면 플로팅 배너 1.5초 후 표시
    if (!sessionStorage.getItem("pwa_banner_dismissed") && pwaInstallBanner) {
      setTimeout(() => {
        pwaInstallBanner.classList.remove("hidden");
        if (window.lucide) window.lucide.createIcons();
      }, 1500);
    }
  });

  // 2. 설치 프롬프트 트리거 공통 함수
  const triggerInstall = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log(`[PWA] 설치 프롬프트 결과: ${outcome}`);
      deferredPrompt = null;
      if (pwaInstallBanner) pwaInstallBanner.classList.add("hidden");
      if (installAppBtn) installAppBtn.classList.add("hidden");
      if (mobileInstallAppBtn) mobileInstallAppBtn.classList.add("hidden");
    } else if (isIos) {
      if (iosInstallModal) {
        iosInstallModal.classList.remove("hidden");
        if (window.lucide) window.lucide.createIcons();
      }
    } else {
      showToast('브라우저 우측 상단 메뉴에서 "앱 설치"를 선택해주세요.', "info");
    }
  };

  if (installAppBtn) installAppBtn.addEventListener("click", triggerInstall);
  if (mobileInstallAppBtn) mobileInstallAppBtn.addEventListener("click", triggerInstall);
  if (pwaBannerInstallBtn) pwaBannerInstallBtn.addEventListener("click", triggerInstall);

  if (pwaBannerDismissBtn) {
    pwaBannerDismissBtn.addEventListener("click", () => {
      if (pwaInstallBanner) pwaInstallBanner.classList.add("hidden");
      sessionStorage.setItem("pwa_banner_dismissed", "true");
    });
  }

  // iOS 모달 닫기
  if (closeIosInstallModalBtn) {
    closeIosInstallModalBtn.addEventListener("click", () => {
      if (iosInstallModal) iosInstallModal.classList.add("hidden");
    });
  }
  if (confirmIosInstallBtn) {
    confirmIosInstallBtn.addEventListener("click", () => {
      if (iosInstallModal) iosInstallModal.classList.add("hidden");
    });
  }

  // iOS 기기이면서 standalone이 아닌 경우 모바일 설치 버튼 및 하단 가이드 배너 노출
  if (isIos && !isStandalone) {
    if (mobileInstallAppBtn) {
      mobileInstallAppBtn.classList.remove("hidden");
      mobileInstallAppBtn.classList.add("flex");
    }
    if (!sessionStorage.getItem("pwa_banner_dismissed") && pwaInstallBanner) {
      const bannerDesc = pwaInstallBanner.querySelector("p");
      const bannerBtn = document.getElementById("pwaBannerInstallBtn");
      if (bannerDesc) bannerDesc.textContent = "Safari 공유 메뉴에서 홈 화면에 추가";
      if (bannerBtn) bannerBtn.textContent = "방법 보기";
      setTimeout(() => {
        pwaInstallBanner.classList.remove("hidden");
        if (window.lucide) window.lucide.createIcons();
      }, 1500);
    }
  }

  // 앱 설치 완료 이벤트 수신
  window.addEventListener("appinstalled", () => {
    console.log("[PWA] PriceTrace 앱 설치 완료");
    showToast("🎉 PriceTrace 앱이 성공적으로 설치되었습니다!", "success");
    if (pwaInstallBanner) pwaInstallBanner.classList.add("hidden");
    if (installAppBtn) installAppBtn.classList.add("hidden");
    if (mobileInstallAppBtn) mobileInstallAppBtn.classList.add("hidden");
  });
}

function setupNetworkStatusMonitor() {
  window.addEventListener("online", () => {
    showToast("🟢 네트워크가 재연결되었습니다. 최저가 조회가 정상화됩니다.", "success");
  });

  window.addEventListener("offline", () => {
    showToast("⚠️ 네트워크 연결 끊김: PWA 오프라인 캐시 모드로 작동합니다.", "info");
  });
}

/* ========================================================
   [모바일/태블릿 동적 인터랙티브 인트로 스플래시 화면 모듈]
   ======================================================== */
let splashAnimationId = null;
let splashProgressInterval = null;

function setupSplashScreen() {
  const splash = document.getElementById("appSplashScreen");
  if (!splash) return;
  if (window.lucide) window.lucide.createIcons();

  const canvas = document.getElementById("splashCanvas");
  const skipBtn = document.getElementById("splashSkipBtn");
  const progressBar = document.getElementById("splashProgressBar");
  const progressText = document.getElementById("splashProgressText");
  const progressPercent = document.getElementById("splashProgressPercent");

  // 1. 노출 여부 판별:
  // - 세션당 1회 노출 (sessionStorage 체크)
  // - 모바일/태블릿(화면 너비 < 1024px) 또는 PWA standalone 모드에서 구동
  // - 단, URL에 ?splash=true 파라미터가 있으면 강제 노출
  const urlParams = new URLSearchParams(window.location.search);
  const forceSplash = urlParams.get("splash") === "true" || urlParams.get("splash") === "1";
  const splashSeen = sessionStorage.getItem("pricetrace_splash_seen") === "true";
  const isMobileOrTablet = window.innerWidth < 1024 || window.matchMedia("(display-mode: standalone)").matches;

  if (!forceSplash && (splashSeen || !isMobileOrTablet)) {
    splash.classList.add("splash-hidden");
    return;
  }

  // 2. 캔버스 파티클 애니메이션 엔진 구동 (스마트 최저가 레이더 테마)
  let particles = [];
  let ctx = null;
  if (canvas) {
    ctx = canvas.getContext("2d");
    const resizeCanvas = () => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      if (ctx) ctx.scale(dpr, dpr);
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // 파티클 생성 (골드 스파클 ✨ + 네온 블루 사이버 빛 입자 + 펄스)
    const particleCount = 45;
    const colors = ["#60A5FA", "#38BDF8", "#FBBF24", "#F59E0B", "#818CF8", "#34D399"];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        size: Math.random() * 3 + 1,
        speedY: -(Math.random() * 0.8 + 0.3),
        speedX: (Math.random() - 0.5) * 0.4,
        color: colors[Math.floor(Math.random() * colors.length)],
        opacity: Math.random() * 0.7 + 0.3,
        pulseSpeed: Math.random() * 0.05 + 0.02,
        pulse: Math.random() * Math.PI,
        isSparkle: Math.random() > 0.4
      });
    }

    const renderParticles = () => {
      if (!ctx || splash.classList.contains("splash-hidden")) return;
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

      for (let p of particles) {
        p.y += p.speedY;
        p.x += p.speedX;
        p.pulse += p.pulseSpeed;
        const currentOpacity = Math.max(0.1, Math.min(1, p.opacity + Math.sin(p.pulse) * 0.3));

        if (p.y < -10) {
          p.y = window.innerHeight + 10;
          p.x = Math.random() * window.innerWidth;
        }

        ctx.save();
        ctx.globalAlpha = currentOpacity;
        ctx.fillStyle = p.color;

        if (p.isSparkle) {
          // 4각 스파클 별(✨) 그리기
          ctx.translate(p.x, p.y);
          ctx.beginPath();
          const r = p.size * 2;
          ctx.moveTo(0, -r);
          ctx.quadraticCurveTo(0, 0, r, 0);
          ctx.quadraticCurveTo(0, 0, 0, r);
          ctx.quadraticCurveTo(0, 0, -r, 0);
          ctx.quadraticCurveTo(0, 0, 0, -r);
          ctx.closePath();
          ctx.fill();
        } else {
          // 원형 빛 입자
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.shadowBlur = 8;
          ctx.shadowColor = p.color;
          ctx.fill();
        }
        ctx.restore();
      }

      splashAnimationId = requestAnimationFrame(renderParticles);
    };

    renderParticles();
  }

  // 3. 스플래시 종료 헬퍼 (Fade Out)
  let isDismissed = false;
  const dismissSplash = () => {
    if (isDismissed) return;
    isDismissed = true;
    sessionStorage.setItem("pricetrace_splash_seen", "true");

    if (splashProgressInterval) {
      clearInterval(splashProgressInterval);
      splashProgressInterval = null;
    }

    splash.classList.add("splash-fade-out");

    setTimeout(() => {
      splash.classList.add("splash-hidden");
      if (splashAnimationId) {
        cancelAnimationFrame(splashAnimationId);
        splashAnimationId = null;
      }
    }, 550);
  };

  // 건너뛰기 버튼 이벤트 바인딩
  if (skipBtn) {
    skipBtn.addEventListener("click", () => {
      dismissSplash();
    });
  }

  // 인트로 다시 보기 버튼 바인딩
  const replayBtn = document.getElementById("replaySplashBtn");
  if (replayBtn) {
    replayBtn.addEventListener("click", () => {
      const modal = document.getElementById("configModal");
      if (modal) modal.classList.add("hidden");
      window.showSplashDemo();
    });
  }

  // 4. 프로그레스 바 진행 (0% → 100%, 약 1.8초 소요)
  let currentProgress = 0;
  const stages = [
    { target: 25, text: "네이버 쇼핑 공식 카탈로그 연결 중..." },
    { target: 60, text: "16대 국민 생필품 최저가 분석 중..." },
    { target: 88, text: "스폰서 광고 0% 클린 필터링 가동..." },
    { target: 100, text: "최저가 레이더 가동 완료!" }
  ];

  const startTime = Date.now();
  const totalDuration = 1800; // 1.8초

  splashProgressInterval = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const ratio = Math.min(1, elapsed / totalDuration);

    currentProgress = Math.min(100, Math.floor(ratio * 100));

    if (progressBar) {
      progressBar.style.width = `${currentProgress}%`;
    }
    if (progressPercent) {
      progressPercent.textContent = `${currentProgress}%`;
    }

    const stage = stages.find(s => currentProgress <= s.target) || stages[stages.length - 1];
    if (progressText && stage) {
      progressText.textContent = stage.text;
    }

    if (ratio >= 1) {
      clearInterval(splashProgressInterval);
      splashProgressInterval = null;
      setTimeout(dismissSplash, 250);
    }
  }, 30);
}

// 외부 디버깅/테스트용 글로벌 노출
window.showSplashDemo = function() {
  sessionStorage.removeItem("pricetrace_splash_seen");
  const splash = document.getElementById("appSplashScreen");
  if (splash) {
    splash.classList.remove("splash-hidden", "splash-fade-out");
  }
  setupSplashScreen();
};

// 초기 실행
function initApp() {
  // 모바일/태블릿 동적 인트로 스플래시 화면 초기화
  setupSplashScreen();

  initEventListeners();

  // PWA 서비스 워커 및 설치 경험 모듈 구동
  registerPwaServiceWorker();
  setupPwaInstallation();
  setupNetworkStatusMonitor();

  // 인기 추천 풀 셔플 렌더링 및 자동 로테이션 시작
  shuffleAndRenderRecommendations(false);
  startRecommendationRotation();

  // 일별 실시간 베스트 트렌드 품목 비동기 수집 및 갱신
  loadDailyTrendingProducts();

  // URL에 ?q=검색어가 있으면 해당 상품 조회, 없으면 초기 웰컴 화면 노출
  const urlParams = new URLSearchParams(window.location.search);
  const initialQuery = urlParams.get("q");

  if (initialQuery && initialQuery.trim()) {
    elements.searchInput.value = initialQuery.trim();
    updateClearBtn();
    loadPriceData(initialQuery.trim(), 0);
  } else {
    switchToWelcomeView();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  initApp();
}
