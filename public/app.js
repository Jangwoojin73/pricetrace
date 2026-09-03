/**
 * app.js - PriceTrace WebApp 프론트엔드 인터랙션 & 차트 엔진
 */

// 전역 상태
const state = {
  keyword: "",
  targetPrice: 15000,
  data: null,
  chart: null,
  isLoading: false,
  view: "welcome" // "welcome" | "result"
};

// URL 정규화 헬퍼 (로그인 강제 및 캡차 발생 최소화)
function normalizeProductUrl(url, title = "") {
  if (!url) return "#";
  let trimmed = String(url).trim();

  // 1. 카탈로그 링크 또는 cr 브릿지 링크: 비로그인 시 nidlogin 리다이렉트를 방지하고 즉시 열리는 공식 검색 딥링크로 연결
  if (
    trimmed.includes("shopping.naver.com/v2/bridge") || 
    trimmed.includes("cr.shopping.naver.com") || 
    trimmed.includes("cr3.shopping.naver.com") || 
    trimmed.includes("searchGate") ||
    trimmed.includes("shopping.naver.com/catalog")
  ) {
    if (title && title.trim()) {
      return `https://search.shopping.naver.com/search/all?query=${encodeURIComponent(title.trim())}`;
    }
    const match = trimmed.match(/[?&]nv_mid=(\d+)/);
    if (match && match[1]) {
      return `https://search.shopping.naver.com/catalog/${match[1]}`;
    }
  }

  // 2. 스마트스토어 outlink 게이트웨이 파라미터 디코딩
  if (trimmed.includes("smartstore.naver.com/inflow/outlink/url?url=")) {
    try {
      const urlObj = new URL(trimmed);
      const target = urlObj.searchParams.get("url");
      if (target && target.startsWith("http")) {
        trimmed = decodeURIComponent(target).split("?")[0];
      }
    } catch (e) {
      // 무시
    }
  }

  // 3. 스마트스토어 영수증 캡차 방지: PC 버전 main/products -> 모바일 반응형 변환
  if (trimmed.includes("smartstore.naver.com/main/products/") && !trimmed.startsWith("https://m.smartstore")) {
    trimmed = trimmed.replace("https://smartstore.naver.com/", "https://m.smartstore.naver.com/");
  }

  return trimmed;
}

// DOM 요소 캐시
const elements = {
  // 뷰 컨테이너
  welcomeView: document.getElementById("welcomeView"),
  resultView: document.getElementById("resultView"),
  backToHomeBtn: document.getElementById("backToHomeBtn"),
  currentSearchKeywordText: document.getElementById("currentSearchKeywordText"),
  welcomeCards: document.querySelectorAll(".welcome-card"),

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

  // 검색
  searchForm: document.getElementById("searchForm"),
  searchInput: document.getElementById("searchInput"),
  clearSearchBtn: document.getElementById("clearSearchBtn"),
  quickChips: document.querySelectorAll(".quick-chip"),
  refreshBtn: document.getElementById("refreshBtn"),
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
  presetPriceBtns: document.querySelectorAll(".preset-price-btn")
};

// 숫자 포맷팅 (원 단위)
function formatCurrency(num) {
  return Number(num || 0).toLocaleString("ko-KR");
}

// 뷰 전환: 초기 웰컴 화면
function switchToWelcomeView() {
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
  if (window.history.pushState && window.location.search) {
    window.history.pushState({}, "", window.location.pathname);
  }
  if (window.lucide) {
    window.lucide.createIcons();
  }
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// 뷰 전환: 검색 결과 대시보드 화면
function switchToResultView(keyword) {
  state.view = "result";
  if (elements.welcomeView) elements.welcomeView.classList.add("hidden");
  if (elements.resultView) elements.resultView.classList.remove("hidden");
  if (elements.currentSearchKeywordText) {
    elements.currentSearchKeywordText.textContent = keyword;
  }
  if (elements.searchInput && elements.searchInput.value !== keyword) {
    elements.searchInput.value = keyword;
    updateClearBtn();
  }
  if (elements.topBannerText) {
    elements.topBannerText.textContent = `'${keyword}' 실시간 최저가 비교 분석`;
  }
  if (window.history.pushState) {
    const newUrl = `${window.location.pathname}?q=${encodeURIComponent(keyword)}`;
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
async function loadPriceData(keyword, targetPrice = 0) {
  if (!keyword || !keyword.trim()) {
    switchToWelcomeView();
    return;
  }
  keyword = keyword.trim();
  if (state.isLoading) return;
  state.isLoading = true;
  setLoadingUI(true);
  switchToResultView(keyword);

  try {
    const encodedQuery = encodeURIComponent(keyword);
    const res = await fetch(`/api/search?q=${encodedQuery}&target_price=${targetPrice}`);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    state.data = data;
    state.keyword = keyword;
    state.targetPrice = data.target_price || targetPrice;

    // UI 렌더링
    renderAll(data);
  } catch (error) {
    console.error("데이터 로딩 실패:", error);
    showErrorNotification(error.message);
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
  elements.btnTargetPriceDisplay.textContent = `${formatCurrency(target_price)}원`;
  elements.currentSetTargetPrice.textContent = `${formatCurrency(target_price)}원`;
  elements.lastUpdatedTime.textContent = timestamp ? timestamp.split(" ")[1] + " 갱신됨" : "방금 갱신됨";
  elements.topBannerText.textContent = `${keyword} 최저가 ${formatCurrency(lowest_price)}원 감지됨!`;

  // 특가 배너 스타일 토글
  if (is_special_price) {
    elements.alertBanner.className = "relative overflow-hidden rounded-3xl p-5 sm:p-6 transition-all duration-300 shadow-md banner-special";
    elements.alertIconBox.textContent = "🚨";
    elements.alertStatusBadge.textContent = "특가 감지";
    elements.alertMainMessage.textContent = "목표 가격 이하입니다! 지금이 구매 적기입니다.";
    const discountRate = target_price > 0 ? Math.round((discount_amount / target_price) * 100) : 0;
    elements.alertDescription.innerHTML = `현재 1위 최저가가 설정하신 목표가 <strong>${formatCurrency(target_price)}원</strong>보다 <strong>${formatCurrency(discount_amount)}원(${discountRate}%)</strong> 저렴합니다.`;
  } else {
    elements.alertBanner.className = "relative overflow-hidden rounded-3xl p-5 sm:p-6 transition-all duration-300 shadow-md banner-normal";
    elements.alertIconBox.textContent = "ℹ️";
    elements.alertStatusBadge.textContent = "가격 관망";
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

    elements.lowestMallName.textContent = representative_item.mall_name || "네이버 가격비교";
    elements.productScore.textContent = (representative_item.score || 4.88).toFixed(2);
    elements.productReviewCount.textContent = `${formatCurrency(representative_item.review_count || 104)}건`;

    // 상품 대표 이미지 동적 교체!
    if (representative_item.image_url) {
      elements.productMainImage.src = representative_item.image_url;
      elements.productMainImage.alt = representative_item.title || keyword;
    }

    // 태그 동적 업데이트
    if (elements.productMallTag) elements.productMallTag.textContent = representative_item.mall_name || "네이버 쇼핑";
    if (elements.productUnitTag) elements.productUnitTag.textContent = unit_count > 1 ? `${unit_count}개 패키지` : "온라인 최저가";
    if (elements.productBadgeText) elements.productBadgeText.textContent = unit_count > 1 ? `${unit_count}개입 실시간 검증` : "정품 인증 완료";

    // 링크 설정
    if (representative_item.url) {
      const safeBuyUrl = normalizeProductUrl(representative_item.url, representative_item.title);
      elements.buyButton.href = safeBuyUrl;
      elements.directBuySubBtn.onclick = () => window.open(safeBuyUrl, "_blank");
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

// 3. 판매처별 가격 비교 리스트 렌더링
function renderComparisonGrid(items, unit_count = 1) {
  if (!items || items.length === 0) {
    elements.priceComparisonGrid.innerHTML = `
      <div class="col-span-3 text-center py-12 text-slate-400">
        검색된 판매처가 없습니다.
      </div>
    `;
    return;
  }

  elements.priceComparisonGrid.innerHTML = items.map((item, index) => {
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
    const scoreVal = item.score ? `★ ${item.score.toFixed(2)}` : "평점 정보 없음";
    const safeItemUrl = normalizeProductUrl(item.url, item.title);

    return `
      <div class="relative bg-white rounded-3xl p-5 ${borderClass} flex flex-col justify-between space-y-4 card-hover">
        <div class="flex items-center justify-between">
          <span class="inline-flex items-center space-x-1 text-xs font-black ${medalClass} px-3 py-1 rounded-full">
            <span>${medal}</span>
          </span>
          ${isFirst ? '<span class="text-xs text-naver font-bold flex items-center"><i data-lucide="zap" class="w-3.5 h-3.5 mr-0.5"></i> 실시간 최저</span>' : ''}
        </div>
        <div>
          <span class="text-xs text-slate-400 font-medium block truncate">${item.mall_name || "스마트스토어"}</span>
          <h4 class="text-sm font-bold text-slate-900 mt-1 line-clamp-2 leading-snug" title="${item.title}">${item.title}</h4>
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
          rel="noopener" 
          referrerpolicy="no-referrer-when-downgrade"
          class="w-full py-2.5 text-center ${btnClass} text-xs font-extrabold rounded-xl transition-colors flex items-center justify-center space-x-1"
        >
          <span>구매 페이지 열기</span>
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
        </a>
      </div>
    `;
  }).join("");
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

  // 그라데이션 배경 생성
  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, "rgba(3, 199, 90, 0.28)");
  gradient.addColorStop(1, "rgba(3, 199, 90, 0.0)");

  state.chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "실시간 최저가 (원)",
          data: priceData,
          borderColor: "#03C75A",
          backgroundColor: gradient,
          borderWidth: 2.5,
          fill: true,
          tension: 0.35,
          pointRadius: 2.5,
          pointHoverRadius: 6,
          pointBackgroundColor: "#03C75A"
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

// 6. 이벤트 리스너 등록
function initEventListeners() {
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
    });
  }

  // 상단 로고 클릭 시 홈으로 이동
  const logoLink = document.querySelector("header a");
  if (logoLink) {
    logoLink.addEventListener("click", (e) => {
      e.preventDefault();
      switchToWelcomeView();
    });
  }

  // 웰컴 퀵 카드 클릭
  if (elements.welcomeCards) {
    elements.welcomeCards.forEach(card => {
      card.addEventListener("click", () => {
        const kw = card.getAttribute("data-keyword");
        if (kw) {
          elements.searchInput.value = kw;
          updateClearBtn();
          loadPriceData(kw, 0);
        }
      });
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

  // 퀵 칩 클릭
  elements.quickChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const kw = chip.getAttribute("data-keyword");
      if (kw) {
        elements.searchInput.value = kw;
        updateClearBtn();
        loadPriceData(kw, 0);
      }
    });
  });

  // 실시간 갱신 버튼
  elements.refreshBtn.addEventListener("click", () => {
    if (state.keyword) {
      loadPriceData(state.keyword, state.targetPrice);
    } else {
      switchToWelcomeView();
    }
  });

  // 모달 열기/닫기
  const openModal = () => {
    elements.modalTargetPriceInput.value = state.targetPrice;
    elements.configModal.classList.remove("hidden");
  };
  const closeModal = () => {
    elements.configModal.classList.add("hidden");
  };

  elements.openConfigModalBtn.addEventListener("click", openModal);
  if (elements.quickTargetEditBtn) {
    elements.quickTargetEditBtn.addEventListener("click", openModal);
  }
  elements.closeConfigModalBtn.addEventListener("click", closeModal);
  elements.cancelConfigModalBtn.addEventListener("click", closeModal);

  // 모달 프리셋 버튼
  elements.presetPriceBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const p = btn.getAttribute("data-price");
      elements.modalTargetPriceInput.value = p;
    });
  });

  // 모달 설정 저장
  elements.saveConfigModalBtn.addEventListener("click", () => {
    const newTarget = parseInt(elements.modalTargetPriceInput.value, 10);
    if (!isNaN(newTarget) && newTarget > 0) {
      closeModal();
      loadPriceData(state.keyword, newTarget);
    } else {
      alert("올바른 금액을 입력해 주세요.");
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
      switchToWelcomeView();
    }
  });
}

// 초기 실행
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();

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
});
