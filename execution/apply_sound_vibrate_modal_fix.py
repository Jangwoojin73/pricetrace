# -*- coding: utf-8 -*-
"""
apply_sound_vibrate_modal_fix.py
Fixes:
1. Modal scrolling bug on mobile viewports (makes #configModal inner card max-h-[90vh] with scrollable body)
2. Chime sound not playing after target price set in app (duplicate alert suppression, async user gesture unlock)
3. Haptic vibration feedback (Android multi-stage vibration, iOS switch haptic, universal tactile visual pulse)
4. Cache version bump to v1.4.7
"""
import re
import sys

def update_style_css():
    with open('public/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    haptic_css = """
/* 촉각 햅틱 진동 시각 효과 (Visual Tactile Shake & Glow) */
@keyframes hapticShake {
  0% { transform: translate(0, 0) scale(1); }
  15% { transform: translate(-4px, 1px) scale(1.015); }
  30% { transform: translate(4px, -1px) scale(1.015); }
  45% { transform: translate(-3px, 1px) scale(1.01); }
  60% { transform: translate(3px, 0px) scale(1.01); }
  75% { transform: translate(-1px, 0px) scale(1.005); }
  90% { transform: translate(1px, 0px) scale(1.002); }
  100% { transform: translate(0, 0) scale(1); }
}

.haptic-pulse-active {
  animation: hapticShake 0.38s cubic-bezier(0.36, 0.07, 0.19, 0.97) both !important;
  box-shadow: 0 0 0 4px rgba(29, 78, 216, 0.3), 0 10px 25px -5px rgba(29, 78, 216, 0.4) !important;
}
"""
    if 'hapticShake' not in css:
        target = ".pulse-button {\n  animation: pulse-glow 2s infinite;\n}"
        if target in css:
            css = css.replace(target, target + "\n" + haptic_css)
        else:
            # Fallback CRLF
            target_crlf = ".pulse-button {\r\n  animation: pulse-glow 2s infinite;\r\n}"
            css = css.replace(target_crlf, target_crlf + "\r\n" + haptic_css.replace("\n", "\r\n"))
        with open('public/style.css', 'w', encoding='utf-8') as f:
            f.write(css)
        print("Updated public/style.css")
    else:
        print("public/style.css already has hapticShake")

def update_sw_js():
    with open('public/sw.js', 'r', encoding='utf-8') as f:
        sw = f.read()
    sw = re.sub(r"const CACHE_VERSION = 'v1\.4\.\d+';", "const CACHE_VERSION = 'v1.4.7';", sw)
    with open('public/sw.js', 'w', encoding='utf-8') as f:
        f.write(sw)
    print("Updated public/sw.js to v1.4.7")

def update_index_html():
    with open('public/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Update cache busting query strings
    html = re.sub(r"v=20261021_v146", "v=20261022_v147", html)

    # Replace #configModal outer & inner structure for seamless mobile scrolling
    old_modal_start = """  <!-- 목표가 변경 모달 -->
  <div id="configModal" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs hidden flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 transform transition-all animate-in fade-in zoom-in-95">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100">
        <h3 class="text-lg font-black text-slate-900 flex items-center space-x-2">
          <i data-lucide="bell" class="w-5 h-5 text-naver"></i>
          <span>목표 알림 가격 설정</span>
        </h3>
        <button id="closeConfigModalBtn" class="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <div class="py-5 space-y-4">"""

    new_modal_start = """  <!-- 목표가 변경 모달 -->
  <div id="configModal" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs hidden flex items-center justify-center p-3 sm:p-4 overflow-y-auto overscroll-contain">
    <div class="bg-white rounded-3xl max-w-md w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 transform transition-all animate-in fade-in zoom-in-95 my-auto">
      <div class="flex items-center justify-between p-5 sm:p-6 pb-3 sm:pb-4 border-b border-slate-100 shrink-0">
        <h3 class="text-lg font-black text-slate-900 flex items-center space-x-2">
          <i data-lucide="bell" class="w-5 h-5 text-naver"></i>
          <span>목표 알림 가격 설정</span>
        </h3>
        <button id="closeConfigModalBtn" class="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 cursor-pointer">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <div class="p-5 sm:p-6 py-4 space-y-4 overflow-y-auto overscroll-contain flex-1">"""

    old_modal_end = """      <div class="pt-4 border-t border-slate-100 flex items-center justify-end space-x-2">
        <button id="cancelConfigModalBtn" class="px-4 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-bold">
          취소
        </button>
        <button id="saveConfigModalBtn" class="px-5 py-2.5 bg-naver hover:bg-naver-dark text-white rounded-xl text-xs font-black shadow-md shadow-naver/25">
          설정 저장 및 다시 계산
        </button>
      </div>
    </div>
  </div>"""

    new_modal_end = """      <div class="p-5 sm:p-6 pt-3 sm:pt-4 border-t border-slate-100 flex items-center justify-end space-x-2 shrink-0 bg-slate-50/70 rounded-b-3xl">
        <button id="cancelConfigModalBtn" class="px-4 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-bold cursor-pointer">
          취소
        </button>
        <button id="saveConfigModalBtn" class="px-5 py-2.5 bg-naver hover:bg-naver-dark text-white rounded-xl text-xs font-black shadow-md shadow-naver/25 cursor-pointer">
          설정 저장 및 다시 계산
        </button>
      </div>
    </div>
  </div>"""

    # Normalize line breaks for replacement
    html = html.replace(old_modal_start.replace("\r\n", "\n"), new_modal_start.replace("\r\n", "\n"))
    html = html.replace(old_modal_start.replace("\n", "\r\n"), new_modal_start.replace("\n", "\r\n"))
    html = html.replace(old_modal_end.replace("\r\n", "\n"), new_modal_end.replace("\r\n", "\n"))
    html = html.replace(old_modal_end.replace("\n", "\r\n"), new_modal_end.replace("\n", "\r\n"))

    # Update vibrate description
    old_vibrate_desc = """        <!-- 특가 알림 모바일 햅틱 진동 토글 -->
        <div class="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl mt-2">
          <div>
            <div class="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
              <i data-lucide="vibrate" class="w-3.5 h-3.5 text-indigo-600"></i>
              <span>모바일 햅틱 진동</span>
            </div>
            <div class="text-[11px] text-slate-500">기기 진동/소리 모드에서 2단 햅틱 진동 피드백을 전달합니다.</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer shrink-0 ml-3" title="햅틱 진동 토글">
            <input type="checkbox" id="modalVibrateToggle" class="sr-only peer" checked>
            <div class="w-10 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-naver"></div>
          </label>
        </div>"""

    new_vibrate_desc = """        <!-- 특가 알림 모바일 햅틱 진동 토글 -->
        <div class="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl mt-2">
          <div class="pr-2">
            <div class="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
              <i data-lucide="vibrate" class="w-3.5 h-3.5 text-indigo-600"></i>
              <span>모바일 햅틱 진동</span>
            </div>
            <div class="text-[11px] text-slate-500 leading-snug mt-0.5">
              기기 진동/소리 모드에서 2단 햅틱 진동 피드백을 전달합니다.<br>
              <span class="text-[10px] text-slate-400">※ 안드로이드는 기기 모터 진동, iOS Safari는 브라우저 정책상 차임벨 소리 및 시각 햅틱 진동으로 동작합니다.</span>
            </div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer shrink-0 ml-3" title="햅틱 진동 토글">
            <input type="checkbox" id="modalVibrateToggle" class="sr-only peer" checked>
            <div class="w-10 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-naver"></div>
          </label>
        </div>"""

    html = html.replace(old_vibrate_desc.replace("\r\n", "\n"), new_vibrate_desc.replace("\r\n", "\n"))
    html = html.replace(old_vibrate_desc.replace("\n", "\r\n"), new_vibrate_desc.replace("\n", "\r\n"))

    # Add iOS haptic hidden switch trigger if not present
    if 'id="iosHapticTrigger"' not in html:
        html = html.replace('</body>', '  <!-- iOS 18+ WebKit Taptic Haptic Trigger -->\n  <input type="checkbox" switch id="iosHapticTrigger" class="sr-only" aria-hidden="true" tabindex="-1">\n</body>')

    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated public/index.html")

def update_app_js():
    with open('public/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Replace Web Audio API & Haptic Vibration Module (lines 26-156)
    pattern_audio = re.compile(
        r'let audioCtx = null;.*?function notifySpecialPrice\(keyword, lowestPrice, force = false\) \{.*?\}',
        re.DOTALL
    )

    new_audio_block = """let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

// 브라우저 Autoplay 정책 대응: 사용자 상호작용(터치/클릭/입력) 발생 시 AudioContext 언락 및 하드웨어 워밍업
const unlockAudioOnMobile = () => {
  const ctx = getAudioContext();
  if (ctx && ctx.state === "suspended") {
    ctx.resume().catch(() => {});
  }
  // 모바일 iOS Safari / Android 하드웨어 오디오 출력단 워밍업 (1-샘플 무음 버퍼)
  if (ctx && typeof ctx.createBuffer === "function") {
    try {
      const buffer = ctx.createBuffer(1, 1, 22050);
      const source = ctx.createBufferSource();
      source.buffer = buffer;
      source.connect(ctx.destination);
      source.start(0);
    } catch (_) {}
  }
};
window.addEventListener("click", unlockAudioOnMobile, { passive: true });
window.addEventListener("touchstart", unlockAudioOnMobile, { passive: true });
window.addEventListener("touchend", unlockAudioOnMobile, { passive: true });
window.addEventListener("keydown", unlockAudioOnMobile, { passive: true });

function playChimeSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const executeChime = () => {
      const now = ctx.currentTime;

      // 1차 톤 (띵 - Ding): A5 880Hz + 배음 (Harmonic, 1760Hz)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = "sine";
      osc1.frequency.setValueAtTime(880, now);

      const osc1Harmonic = ctx.createOscillator();
      const gain1Harmonic = ctx.createGain();
      osc1Harmonic.type = "sine";
      osc1Harmonic.frequency.setValueAtTime(1760, now);

      gain1.gain.setValueAtTime(0, now);
      gain1.gain.linearRampToValueAtTime(0.35, now + 0.02);
      gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.38);

      gain1Harmonic.gain.setValueAtTime(0, now);
      gain1Harmonic.gain.linearRampToValueAtTime(0.09, now + 0.02);
      gain1Harmonic.gain.exponentialRampToValueAtTime(0.0001, now + 0.32);

      osc1.connect(gain1);
      gain1.connect(ctx.destination);
      osc1Harmonic.connect(gain1Harmonic);
      gain1Harmonic.connect(ctx.destination);

      osc1.start(now);
      osc1Harmonic.start(now);
      osc1.stop(now + 0.40);
      osc1Harmonic.stop(now + 0.40);

      // 2차 톤 (동 - Dong): E5 659.25Hz (0.22초 후 시작, 풍부한 0.70초 잔향)
      const t2 = now + 0.22;
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = "sine";
      osc2.frequency.setValueAtTime(659.25, t2);

      const osc2Harmonic = ctx.createOscillator();
      const gain2Harmonic = ctx.createGain();
      osc2Harmonic.type = "sine";
      osc2Harmonic.frequency.setValueAtTime(1318.5, t2);

      gain2.gain.setValueAtTime(0, t2);
      gain2.gain.linearRampToValueAtTime(0.38, t2 + 0.025);
      gain2.gain.exponentialRampToValueAtTime(0.0001, t2 + 0.70);

      gain2Harmonic.gain.setValueAtTime(0, t2);
      gain2Harmonic.gain.linearRampToValueAtTime(0.10, t2 + 0.025);
      gain2Harmonic.gain.exponentialRampToValueAtTime(0.0001, t2 + 0.60);

      osc2.connect(gain2);
      gain2.connect(ctx.destination);
      osc2Harmonic.connect(gain2Harmonic);
      gain2Harmonic.connect(ctx.destination);

      osc2.start(t2);
      osc2Harmonic.start(t2);
      osc2.stop(t2 + 0.72);
      osc2Harmonic.stop(t2 + 0.72);
    };

    if (ctx.state === "suspended") {
      ctx.resume().then(() => {
        executeChime();
      }).catch(() => {
        executeChime();
      });
    } else {
      executeChime();
    }
  } catch (err) {
    console.warn("차임벨 사운드 재생 중 오류(무음 유지):", err);
  }
}

// 햅틱 진동 시각적 촉각 효과 (Visual Tactile Shake & Glow - iOS Safari 및 전 기기 공통)
function triggerVisualHapticEffect() {
  const targets = [
    elements.alertBanner,
    elements.testNotificationBtn,
    elements.saveConfigModalBtn
  ].filter(Boolean);

  targets.forEach(el => {
    el.classList.remove("haptic-pulse-active");
    void el.offsetWidth; // force reflow
    el.classList.add("haptic-pulse-active");
    setTimeout(() => {
      el.classList.remove("haptic-pulse-active");
    }, 450);
  });
}

function triggerHapticVibration() {
  // 1. Android 및 표준 Vibration API 지원 브라우저 (Chrome, Samsung Internet 등)
  try {
    if (typeof navigator !== "undefined" && typeof navigator.vibrate === "function") {
      // 2단 햅틱 패턴: 띵 (120ms) -> 대기 (60ms) -> 동 (180ms)
      const didVibrate = navigator.vibrate([120, 60, 180]);
      if (!didVibrate) {
        navigator.vibrate(200);
      }
    }
  } catch (err) {
    try {
      if (typeof navigator !== "undefined" && typeof navigator.vibrate === "function") {
        navigator.vibrate(200);
      }
    } catch (_) {}
  }

  // 2. iOS 18+ WebKit Switch Haptic Trigger
  try {
    const iosSwitch = document.getElementById("iosHapticTrigger");
    if (iosSwitch) {
      iosSwitch.checked = !iosSwitch.checked;
      iosSwitch.dispatchEvent(new Event("change", { bubbles: true }));
    }
  } catch (_) {}

  // 3. 전 디바이스 공통 촉각 시각 펄스 (iOS Safari 및 무음 모드 지원)
  triggerVisualHapticEffect();
}

function notifySpecialPrice(keyword, lowestPrice, force = false, targetPrice = 0) {
  const currentTarget = targetPrice || state.targetPrice || 0;
  const alertKey = `${keyword}_${lowestPrice}_${currentTarget}`;
  if (!force && state.lastAlertPlayedKey === alertKey) {
    return; // 동일 조건 연속 재생 방지
  }
  state.lastAlertPlayedKey = alertKey;

  if (state.soundEnabled) {
    playChimeSound();
  }
  if (state.vibrateEnabled) {
    triggerHapticVibration();
  }
}"""

    if pattern_audio.search(js):
        js = pattern_audio.sub(new_audio_block, js, count=1)
        print("Replaced Web Audio & Haptic module in app.js")
    else:
        print("WARN: pattern_audio not matched")

    # 2. Update notifySpecialPrice call in renderAll
    old_render_notify = 'notifySpecialPrice(keyword, lowest_price);'
    new_render_notify = 'notifySpecialPrice(keyword, lowest_price, false, target_price);'
    js = js.replace(old_render_notify, new_render_notify)

    # 3. Update testNotificationBtn
    old_test_btn = """  if (elements.testNotificationBtn) {
    elements.testNotificationBtn.addEventListener("click", () => {
      playChimeSound();
      triggerHapticVibration();
      if (typeof showToast === "function") {
        showToast("🔔 '띵동~' 차임벨 소리와 햅틱 진동을 테스트했습니다.", "success", 2000);
      }
    });
  }"""

    new_test_btn = """  if (elements.testNotificationBtn) {
    elements.testNotificationBtn.addEventListener("click", () => {
      unlockAudioOnMobile();
      playChimeSound();
      triggerHapticVibration();
      const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
      const msg = isIos 
        ? "🔔 '띵동~' 차임벨 소리와 시각 햅틱 진동을 테스트했습니다." 
        : "🔔 '띵동~' 차임벨 소리와 햅틱 진동을 테스트했습니다.";
      if (typeof showToast === "function") {
        showToast(msg, "success", 2200);
      }
    });
  }"""
    js = js.replace(old_test_btn.replace("\r\n", "\n"), new_test_btn.replace("\r\n", "\n"))
    js = js.replace(old_test_btn.replace("\n", "\r\n"), new_test_btn.replace("\n", "\r\n"))

    # 4. Update saveConfigModalBtn
    old_save_modal = """  elements.saveConfigModalBtn.addEventListener("click", () => {
    const newTarget = parseInt(elements.modalTargetPriceInput.value, 10);
    if (!isNaN(newTarget) && newTarget > 0) {
      closeModal();
      if (elements.modalAlertToggle) {
        handleAlertToggle(elements.modalAlertToggle.checked);
      }
      if (elements.modalSoundToggle) {
        state.soundEnabled = elements.modalSoundToggle.checked;
        localStorage.setItem("pricetrace_sound_enabled", state.soundEnabled ? "true" : "false");
      }
      if (elements.modalVibrateToggle) {
        state.vibrateEnabled = elements.modalVibrateToggle.checked;
        localStorage.setItem("pricetrace_vibrate_enabled", state.vibrateEnabled ? "true" : "false");
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
      alert("올바른 금액을 입력해 주세요 (1원 이상 숫자).");
    }
  });"""

    new_save_modal = """  elements.saveConfigModalBtn.addEventListener("click", () => {
    // 1. 유저 직접 제스처 즉시 AudioContext 언락/재개 (비동기 fetch 전 동기 실행 필수!)
    unlockAudioOnMobile();
    const ctx = getAudioContext();
    if (ctx && ctx.state === "suspended") {
      ctx.resume().catch(() => {});
    }

    const newTarget = parseInt(elements.modalTargetPriceInput.value, 10);
    if (!isNaN(newTarget) && newTarget > 0) {
      closeModal();
      if (elements.modalAlertToggle) {
        handleAlertToggle(elements.modalAlertToggle.checked);
      }
      if (elements.modalSoundToggle) {
        state.soundEnabled = elements.modalSoundToggle.checked;
        localStorage.setItem("pricetrace_sound_enabled", state.soundEnabled ? "true" : "false");
      }
      if (elements.modalVibrateToggle) {
        state.vibrateEnabled = elements.modalVibrateToggle.checked;
        localStorage.setItem("pricetrace_vibrate_enabled", state.vibrateEnabled ? "true" : "false");
      }
      state.targetPrice = newTarget;
      localStorage.setItem("pricetrace_user_target_price", String(newTarget));

      if (elements.btnTargetPriceDisplay) {
        elements.btnTargetPriceDisplay.textContent = formatCurrency(newTarget) + "원";
      }
      if (elements.mobileBtnTargetPriceDisplay) {
        elements.mobileBtnTargetPriceDisplay.textContent = formatCurrency(newTarget) + "원";
      }

      // 현재 화면에 이미 조회된 상품이 있다면 즉시 새 목표가와 비교하여 UI 갱신 및 띵동 벨소리/진동 발동!
      if (state.data && state.data.lowest_price > 0) {
        const lowest = state.data.lowest_price;
        const isSpecial = lowest <= newTarget;
        state.data.target_price = newTarget;
        state.data.is_special_price = isSpecial;
        state.data.discount_amount = isSpecial ? (newTarget - lowest) : 0;
        
        // UI 즉시 재렌더링
        renderAll(state.data);

        // 목표가 달성(특가)인 경우 벨소리 및 진동 즉시 강제 발동!
        if (isSpecial && state.alertEnabled) {
          notifySpecialPrice(state.keyword, lowest, true, newTarget);
        }

        showToast(`목표가가 ${formatCurrency(newTarget)}원으로 저장되었습니다.${isSpecial ? " 🔔 특가가 감지되었습니다!" : ""}`, "success", 2500);
      } else {
        showToast(`목표가가 ${formatCurrency(newTarget)}원으로 저장되었습니다.`, "success", 2000);
      }

      // 백엔드에도 동기화 호출
      if (state.keyword && state.keyword.trim()) {
        loadPriceData(state.keyword, newTarget, false);
      }
    } else {
      alert("올바른 금액을 입력해 주세요 (1원 이상 숫자).");
    }
  });"""
    js = js.replace(old_save_modal.replace("\r\n", "\n"), new_save_modal.replace("\r\n", "\n"))
    js = js.replace(old_save_modal.replace("\n", "\r\n"), new_save_modal.replace("\n", "\r\n"))

    # 5. searchForm submit unlock
    old_search_submit = """  elements.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    closeRadarSearchModal(true);
    if (elements.searchInput) elements.searchInput.blur();
    const query = elements.searchInput.value.trim();
    if (query) {
      // 새로운 상품 검색 시 이전 상품의 목표가를 리셋하여 해당 상품 시세에 맞춤
      const target = (query !== state.keyword) ? 0 : state.targetPrice;
      loadPriceData(query, target);
    }
  });"""

    new_search_submit = """  elements.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    unlockAudioOnMobile();
    closeRadarSearchModal(true);
    if (elements.searchInput) elements.searchInput.blur();
    const query = elements.searchInput.value.trim();
    if (query) {
      // 새로운 상품 검색 시 이전 상품의 목표가를 리셋하여 해당 상품 시세에 맞춤
      const target = (query !== state.keyword) ? 0 : state.targetPrice;
      loadPriceData(query, target);
    }
  });"""
    js = js.replace(old_search_submit.replace("\r\n", "\n"), new_search_submit.replace("\r\n", "\n"))
    js = js.replace(old_search_submit.replace("\n", "\r\n"), new_search_submit.replace("\n", "\r\n"))

    # 6. modalSearchForm submit unlock
    old_modal_submit = """      closeRadarSearchModal(true);
      if (elements.searchInput) {
        elements.searchInput.value = query;
        updateClearBtn();
        elements.searchInput.blur();
      }
      if (elements.modalSearchInput) {
        elements.modalSearchInput.blur();
      }
      loadPriceData(query, 0, false);"""

    new_modal_submit = """      closeRadarSearchModal(true);
      unlockAudioOnMobile();
      if (elements.searchInput) {
        elements.searchInput.value = query;
        updateClearBtn();
        elements.searchInput.blur();
      }
      if (elements.modalSearchInput) {
        elements.modalSearchInput.blur();
      }
      loadPriceData(query, 0, false);"""
    js = js.replace(old_modal_submit.replace("\r\n", "\n"), new_modal_submit.replace("\r\n", "\n"))
    js = js.replace(old_modal_submit.replace("\n", "\r\n"), new_modal_submit.replace("\n", "\r\n"))

    with open('public/app.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Updated public/app.js")

if __name__ == '__main__':
    update_style_css()
    update_sw_js()
    update_index_html()
    update_app_js()
    print("All files updated successfully.")
