# -*- coding: utf-8 -*-
with open('public/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Insert missing } after notifySpecialPrice if not present
if lines[206].strip() == '}' and lines[207].strip() != '}':
    lines.insert(207, '}\n')

# 2. Find and replace saveConfigModalBtn
start_idx = None
end_idx = None
for i, l in enumerate(lines):
    if 'elements.saveConfigModalBtn.addEventListener("click"' in l:
        start_idx = i
    if start_idx is not None and 'alert("올바른 금액을 입력해 주세요' in l:
        end_idx = i + 2
        break

if start_idx is not None and end_idx is not None:
    print(f'Replacing saveConfigModalBtn lines {start_idx+1} to {end_idx+1}')
    new_save_btn = """  elements.saveConfigModalBtn.addEventListener("click", () => {
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
      alert("올바른 금액을 입력해 주세요 (1원 이상의 숫자).");
    }
  });
"""
    lines[start_idx:end_idx] = [new_save_btn]

with open('public/app.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Updated app.js successfully.')
