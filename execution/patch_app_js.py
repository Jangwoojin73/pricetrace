# -*- coding: utf-8 -*-
import sys

def patch_app_js():
    with open('public/app.js', 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Update state definition
    old_state = '''const state = {
  keyword: "",
  targetPrice: 15000,
  alertEnabled: localStorage.getItem("pricetrace_alert_enabled") !== "false",
  data: null,
  chart: null,
  isLoading: false,
  view: "welcome", // "welcome" | "result"
  activeTab: "steady" // "steady" | "trending"
};'''

    new_state = '''const state = {
  keyword: "",
  targetPrice: 15000,
  alertEnabled: localStorage.getItem("pricetrace_alert_enabled") !== "false",
  soundEnabled: localStorage.getItem("pricetrace_sound_enabled") !== "false",
  vibrateEnabled: localStorage.getItem("pricetrace_vibrate_enabled") !== "false",
  lastAlertPlayedKey: "",
  data: null,
  chart: null,
  isLoading: false,
  view: "welcome", // "welcome" | "result"
  activeTab: "steady" // "steady" | "trending"
};'''

    if old_state in code:
        code = code.replace(old_state, new_state)
        print("1. state updated")
    else:
        print("WARN: old_state not found directly, checking variations")
        return False

    # 2. Add Audio & Haptic Module functions
    audio_module_code = '''
// ============================================================================
// [Web Audio API & Haptic Vibration Module]
// 특가 발생 시 경쾌한 "띵동~ 🔔" 차임벨 소리 및 모바일 햅틱 진동 피드백
// ============================================================================
let audioCtx = null;

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

// 브라우저 Autoplay 정책 대응: 사용자 상호작용 발생 시 AudioContext 언락
window.addEventListener("click", () => {
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume().catch(() => {});
  }
}, { once: false, passive: true });
window.addEventListener("touchstart", () => {
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume().catch(() => {});
  }
}, { once: false, passive: true });

function playChimeSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

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
    gain1.gain.linearRampToValueAtTime(0.28, now + 0.02);
    gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);

    gain1Harmonic.gain.setValueAtTime(0, now);
    gain1Harmonic.gain.linearRampToValueAtTime(0.07, now + 0.02);
    gain1Harmonic.gain.exponentialRampToValueAtTime(0.0001, now + 0.30);

    osc1.connect(gain1);
    gain1.connect(ctx.destination);
    osc1Harmonic.connect(gain1Harmonic);
    gain1Harmonic.connect(ctx.destination);

    osc1.start(now);
    osc1Harmonic.start(now);
    osc1.stop(now + 0.36);
    osc1Harmonic.stop(now + 0.36);

    // 2차 톤 (동 - Dong): E5 659.25Hz (0.22초 후 시작, 풍부한 0.65초 잔향)
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
    gain2.gain.linearRampToValueAtTime(0.32, t2 + 0.025);
    gain2.gain.exponentialRampToValueAtTime(0.0001, t2 + 0.65);

    gain2Harmonic.gain.setValueAtTime(0, t2);
    gain2Harmonic.gain.linearRampToValueAtTime(0.08, t2 + 0.025);
    gain2Harmonic.gain.exponentialRampToValueAtTime(0.0001, t2 + 0.55);

    osc2.connect(gain2);
    gain2.connect(ctx.destination);
    osc2Harmonic.connect(gain2Harmonic);
    gain2Harmonic.connect(ctx.destination);

    osc2.start(t2);
    osc2Harmonic.start(t2);
    osc2.stop(t2 + 0.68);
    osc2Harmonic.stop(t2 + 0.68);
  } catch (err) {
    console.warn("차임벨 사운드 재생 중 오류(무음 유지):", err);
  }
}

function triggerHapticVibration() {
  try {
    if (typeof navigator !== "undefined" && "vibrate" in navigator) {
      // 띵 (100ms) -> 대기 (60ms) -> 동 (160ms)
      navigator.vibrate([100, 60, 160]);
    }
  } catch (err) {
    console.warn("햅틱 진동 호출 불가:", err);
  }
}

function notifySpecialPrice(keyword, lowestPrice, force = false) {
  const alertKey = `${keyword}_${lowestPrice}`;
  if (!force && state.lastAlertPlayedKey === alertKey) {
    return; // 동일 상품 연속 재생 방지
  }
  state.lastAlertPlayedKey = alertKey;

  if (state.soundEnabled) {
    playChimeSound();
  }
  if (state.vibrateEnabled) {
    triggerHapticVibration();
  }
}
'''
    # Insert audio module right after cleanSearchKeyword
    clean_kw_anchor = 'function cleanSearchKeyword(title) {'
    idx_clean = code.find(clean_kw_anchor)
    code = code[:idx_clean] + audio_module_code + "\n" + code[idx_clean:]
    print("2. audio module inserted")

    # 3. Add to elements
    old_elements_alert = '''  // 알림 설정
  alertToggleSwitch: document.getElementById("alertToggleSwitch"),
  modalAlertToggle: document.getElementById("modalAlertToggle"),
  alertToggleLabel: document.getElementById("alertToggleLabel"),'''

    new_elements_alert = '''  // 알림 설정
  alertToggleSwitch: document.getElementById("alertToggleSwitch"),
  modalAlertToggle: document.getElementById("modalAlertToggle"),
  modalSoundToggle: document.getElementById("modalSoundToggle"),
  modalVibrateToggle: document.getElementById("modalVibrateToggle"),
  testNotificationBtn: document.getElementById("testNotificationBtn"),
  alertToggleLabel: document.getElementById("alertToggleLabel"),'''

    if old_elements_alert in code:
        code = code.replace(old_elements_alert, new_elements_alert)
        print("3. elements updated")
    else:
        # try find modalAlertToggle line
        anchor = 'modalAlertToggle: document.getElementById("modalAlertToggle"),'
        replacement = anchor + '\n  modalSoundToggle: document.getElementById("modalSoundToggle"),\n  modalVibrateToggle: document.getElementById("modalVibrateToggle"),\n  testNotificationBtn: document.getElementById("testNotificationBtn"),'
        code = code.replace(anchor, replacement)
        print("3. elements updated via anchor")

    # 4. Trigger notifySpecialPrice in renderAll
    old_special_block = '''    const discountRate = target_price > 0 ? Math.round((discount_amount / target_price) * 100) : 0;
    elements.alertDescription.innerHTML = `현재 1위 최저가가 설정하신 목표가 <strong>${formatCurrency(target_price)}원</strong>보다 <strong>${formatCurrency(discount_amount)}원(${discountRate}%)</strong> 저렴합니다.`;
  } else {'''

    new_special_block = '''    const discountRate = target_price > 0 ? Math.round((discount_amount / target_price) * 100) : 0;
    elements.alertDescription.innerHTML = `현재 1위 최저가가 설정하신 목표가 <strong>${formatCurrency(target_price)}원</strong>보다 <strong>${formatCurrency(discount_amount)}원(${discountRate}%)</strong> 저렴합니다.`;

    // 🔔 목표가 이하 특가 달성 시 차임벨 소리 및 햅틱 진동 피드백 발동
    notifySpecialPrice(keyword, lowest_price);
  } else {'''

    if old_special_block in code:
        code = code.replace(old_special_block, new_special_block)
        print("4. renderAll special price notification updated")
    else:
        print("WARN: old_special_block not found")
        return False

    # 5. openModal sync toggles
    old_open_modal = '''  const openModal = () => {
    elements.modalTargetPriceInput.value = state.targetPrice || 15000;
    if (elements.modalAlertToggle) elements.modalAlertToggle.checked = state.alertEnabled;
    elements.configModal.classList.remove("hidden");'''

    new_open_modal = '''  const openModal = () => {
    elements.modalTargetPriceInput.value = state.targetPrice || 15000;
    if (elements.modalAlertToggle) elements.modalAlertToggle.checked = state.alertEnabled;
    if (elements.modalSoundToggle) elements.modalSoundToggle.checked = state.soundEnabled;
    if (elements.modalVibrateToggle) elements.modalVibrateToggle.checked = state.vibrateEnabled;
    elements.configModal.classList.remove("hidden");'''

    if old_open_modal in code:
        code = code.replace(old_open_modal, new_open_modal)
        print("5. openModal updated")
    else:
        print("WARN: old_open_modal not found")
        return False

    # 6. saveConfigModalBtn & testNotificationBtn handlers
    old_save_block = '''      if (elements.modalAlertToggle) {
        handleAlertToggle(elements.modalAlertToggle.checked);
      }
      state.targetPrice = newTarget;'''

    new_save_block = '''      if (elements.modalAlertToggle) {
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
      state.targetPrice = newTarget;'''

    if old_save_block in code:
        code = code.replace(old_save_block, new_save_block)
        print("6. saveConfigModalBtn updated")
    else:
        print("WARN: old_save_block not found")
        return False

    # 7. Add testNotificationBtn and direct toggle listeners
    listener_code = '''
  // 소리/진동 즉시 테스트 버튼
  if (elements.testNotificationBtn) {
    elements.testNotificationBtn.addEventListener("click", () => {
      playChimeSound();
      triggerHapticVibration();
      if (typeof showToast === "function") {
        showToast("🔔 '띵동~' 차임벨 소리와 햅틱 진동을 테스트했습니다.", "success", 2000);
      }
    });
  }

  // 모달 내 소리 토글 즉시 반영
  if (elements.modalSoundToggle) {
    elements.modalSoundToggle.addEventListener("change", (e) => {
      state.soundEnabled = e.target.checked;
      localStorage.setItem("pricetrace_sound_enabled", state.soundEnabled ? "true" : "false");
      if (state.soundEnabled) {
        playChimeSound();
      }
    });
  }

  // 모달 내 진동 토글 즉시 반영
  if (elements.modalVibrateToggle) {
    elements.modalVibrateToggle.addEventListener("change", (e) => {
      state.vibrateEnabled = e.target.checked;
      localStorage.setItem("pricetrace_vibrate_enabled", state.vibrateEnabled ? "true" : "false");
      if (state.vibrateEnabled) {
        triggerHapticVibration();
      }
    });
  }
'''
    # Insert right before saveConfigModalBtn listener
    save_btn_anchor = 'elements.saveConfigModalBtn.addEventListener("click", () => {'
    idx_save = code.find(save_btn_anchor)
    code = code[:idx_save] + listener_code + "\n  " + code[idx_save:]
    print("7. testNotificationBtn and toggle listeners inserted")

    with open('public/app.js', 'w', encoding='utf-8') as f:
        f.write(code)
    print("public/app.js patched successfully!")
    return True

if __name__ == '__main__':
    patch_app_js()
