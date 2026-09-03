/**
 * app.js - PriceTrace WebApp 프론트엔드 인터랙션 & 차트 엔진
 */

// 전역 상태
const state = {
  keyword: "농심 신라면 봉지 20개입",
  targetPrice: 15000,
  data: null,
  chart: null,
  isLoading: false
};

// DOM 요소 캐시
const elements = {
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
  lowestMallName: document.getElementById("lowestMallName"),
  buyButton: document.getElementById("buyButton"),
  productMainImage: document.getElementById("productMainImage"),

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

// 1. API 데이터 로드
async function loadPriceData(keyword = state.keyword, targetPrice = state.targetPrice) {
  if (state.isLoading) return;
  state.isLoading = true;
  setLoadingUI(true);

  try {
    const encodedQuery = encodeURIComponent(keyword);
    const res = await fetch(`/api/search?q=${encodedQuery}&target_price=${targetPrice}`);
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    const data = await res.json();
    state.data = data;
    state.keyword = keyword;
    state.targetPrice = targetPrice;

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
    elements.alertStatusBadge.textContent = "특가 발생";
    elements.alertMainMessage.textContent = "목표 가격 이하입니다! 지금이 구매 적기입니다.";
    const discountRate = Math.round((discount_amount / target_price) * 100);
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
  if (representative_item) {
    elements.productTitle.textContent = representative_item.title || keyword;
    elements.lowestPriceDisplay.textContent = formatCurrency(lowest_price);
    elements.unitPriceDisplay.textContent = `약 ${formatCurrency(unit_price)}원`;
    elements.lowestMallName.textContent = representative_item.mall_name || "네이버 가격비교";
    elements.productScore.textContent = (representative_item.score || 4.88).toFixed(2);
    elements.productReviewCount.textContent = `${formatCurrency(representative_item.review_count || 104064)}건`;

    // 링크 설정
    if (representative_item.url) {
      elements.buyButton.href = representative_item.url;
      elements.directBuySubBtn.onclick = () => window.open(representative_item.url, "_blank");
    }

    // 할인 뱃지
    if (is_special_price && discount_amount > 0) {
      const discountRate = Math.round((discount_amount / target_price) * 100);
      elements.discountBadge.textContent = `목표가 대비 -${formatCurrency(discount_amount)}원 (-${discountRate}%)`;
      elements.discountBadge.className = "text-xs sm:text-sm font-bold text-coupang bg-coupang/10 px-2.5 py-0.5 rounded-lg ml-2";
    } else {
      const diff = lowest_price - target_price;
      elements.discountBadge.textContent = `목표가 대비 +${formatCurrency(diff)}원`;
      elements.discountBadge.className = "text-xs sm:text-sm font-bold text-slate-600 bg-slate-200 px-2.5 py-0.5 rounded-lg ml-2";
    }
  }

  // 판매처별 가격 비교 매트릭스 렌더링
  renderComparisonGrid(top_items);

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
function renderComparisonGrid(items) {
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
    const unitPrice = roundCalcUnitPrice(item.price);
    const reviewCnt = item.review_count ? formatCurrency(item.review_count) + "개" : "리뷰 정보 없음";
    const scoreVal = item.score ? `★ ${item.score.toFixed(2)}` : "평점 정보 없음";

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
            <span class="text-xs text-slate-400 ml-1">(봉당 ${formatCurrency(unitPrice)}원)</span>
          </div>
          <div class="mt-2 text-xs text-slate-500 flex items-center space-x-2">
            <span>${reviewCnt}</span>
            <span>·</span>
            <span>${scoreVal}</span>
          </div>
        </div>
        <a 
          href="${item.url || '#'}" 
          target="_blank" 
          rel="noopener noreferrer" 
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
  // 검색 폼
  elements.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = elements.searchInput.value.trim();
    if (query) {
      loadPriceData(query, state.targetPrice);
    }
  });

  // 퀵 칩 클릭
  elements.quickChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const kw = chip.getAttribute("data-keyword");
      elements.searchInput.value = kw;
      loadPriceData(kw, state.targetPrice);
    });
  });

  // 실시간 갱신 버튼
  elements.refreshBtn.addEventListener("click", () => {
    loadPriceData(state.keyword, state.targetPrice);
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
  elements.quickTargetEditBtn.addEventListener("click", openModal);
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
}

// 초기 실행
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  loadPriceData();
});
