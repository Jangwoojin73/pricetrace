# -*- coding: utf-8 -*-
import os

app_js_path = r"c:\Users\ROG\.gemini\안티그래비티_2.0\pricetrace-bot\public\app.js"

with open(app_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if "elements.welcomeCardsContainer.innerHTML = displayCards.map" in line:
        start_idx = i
    if start_idx is not None and "`).join(\"\");" in line and i > start_idx:
        end_idx = i + 1
        break

print(f"Target lines: {start_idx+1} to {end_idx}")

new_template = """      elements.welcomeCardsContainer.innerHTML = displayCards.map(item => `
        <div class="welcome-card group bg-white rounded-2xl sm:rounded-3xl p-3 sm:p-5 border border-slate-200/80 shadow-xs hover:shadow-lg hover:border-blue-600/40 transition-all duration-200 flex flex-row sm:flex-col justify-between items-center sm:items-stretch gap-3 sm:gap-0 cursor-pointer active:scale-[0.99]" data-keyword="${item.keyword}">
          <!-- 모바일: 좌측 72px 썸네일, PC: 상단 48px 썸네일 -->
          <div class="flex items-center sm:items-start space-x-3 sm:mb-3 shrink-0">
            <div class="w-[72px] h-[72px] sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl ${item.bgClass || 'bg-slate-50 border-slate-100'} p-1 flex items-center justify-center shrink-0 border border-slate-200/80 overflow-hidden shadow-2xs">
              ${item.image_url ? `<img src="${item.image_url}" alt="${item.title || item.keyword}" class="w-full h-full object-cover rounded-lg sm:rounded-xl" loading="eager" onerror="this.onerror=null;this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'48\\' height=\\'48\\' viewBox=\\'0 0 48 48\\'><rect width=\\'48\\' height=\\'48\\' rx=\\'12\\' fill=\\'%23F1F5F9\\'/><text x=\\'50%25\\' y=\\'55%25\\' dominant-baseline=\\'middle\\' text-anchor=\\'middle\\' font-size=\\'24\\'>${encodeURIComponent(item.icon || '🛍️')}</text></svg>'">` : `<img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48' viewBox='0 0 48 48'><rect width='48' height='48' rx='12' fill='%23F1F5F9'/><text x='50%25' y='55%25' dominant-baseline='middle' text-anchor='middle' font-size='24'>${encodeURIComponent(item.icon || '🛍️')}</text></svg>" alt="${item.title || item.keyword}" class="w-full h-full object-cover rounded-lg sm:rounded-xl" loading="eager">`}
            </div>
            <!-- PC에서만 상단 썸네일 우측에 태그 노출 -->
            <div class="hidden sm:flex flex-col">
              <span class="text-[11px] font-bold ${isSteady ? 'text-emerald-700 bg-emerald-50 border border-emerald-200/60' : 'text-amber-700 bg-amber-50 border border-amber-200/60'} px-2 py-0.5 rounded-full inline-block self-start">${item.tag || (isSteady ? '생필품' : '오늘 핫딜')}</span>
              <span class="text-[10px] text-slate-400 font-medium mt-0.5">${item.category || (isSteady ? '국민 필수품' : '실시간 랭킹')}</span>
            </div>
          </div>

          <!-- 중앙 텍스트 정보 (모바일에서는 썸네일 우측 전체 차지, PC에서는 본문) -->
          <div class="flex-1 min-w-0">
            <!-- 모바일 전용 태그+카테고리 1줄 바 -->
            <div class="flex sm:hidden items-center gap-1.5 mb-1">
              <span class="text-[10px] font-bold ${isSteady ? 'text-emerald-700 bg-emerald-50 border border-emerald-200/60' : 'text-amber-700 bg-amber-50 border border-amber-200/60'} px-1.5 py-0.2 rounded-md leading-tight">${item.tag || (isSteady ? '생필품' : '오늘 핫딜')}</span>
              <span class="text-[10px] text-slate-400 font-medium truncate">${item.category || (isSteady ? '국민 필수품' : '실시간 랭킹')}</span>
            </div>

            <!-- 상품명 타이틀 (모바일: 13.5px 굵은 볼드, PC: 16px) -->
            <h3 class="text-[13.5px] sm:text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors truncate sm:whitespace-normal sm:line-clamp-2 leading-snug">${item.title || item.keyword}</h3>

            <!-- 상품 설명 문구 (모바일: 11px, PC: 12px) -->
            <p class="text-[11px] sm:text-xs text-slate-500 truncate mt-0.5 sm:mt-1">${item.desc || '실시간 가격비교 최저가'}</p>

            <!-- 모바일 전용 인라인 가격 & 액션 바 -->
            <div class="mt-2 flex sm:hidden items-center justify-between pt-1 border-t border-slate-100">
              <span class="text-[11px] font-semibold text-slate-600">
                오늘 최저 <strong class="text-xs font-black text-blue-600">${item.price && item.price > 0 ? `${formatCurrency(item.price)}원` : '실시간 확인'}</strong>
              </span>
              <span class="inline-flex items-center text-[10.5px] font-bold text-blue-600 group-hover:translate-x-0.5 transition-transform">
                비교 <i data-lucide="chevron-right" class="w-3.5 h-3.5 ml-0.5"></i>
              </span>
            </div>
          </div>

          <!-- PC 전용 하단 가격 바 (모바일에서는 hidden) -->
          <div class="hidden sm:flex mt-4 pt-3 border-t border-slate-100 items-center justify-between text-xs font-bold text-blue-600">
            <span>${item.price && item.price > 0 ? `오늘 최저 ${formatCurrency(item.price)}원` : '실시간 최저가 확인'}</span>
            <i data-lucide="arrow-right" class="w-4 h-4 group-hover:translate-x-1 transition-transform"></i>
          </div>
        </div>
      `).join("");
"""

if start_idx is not None and end_idx is not None:
    lines[start_idx:end_idx] = [new_template]
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("[✓] Successfully updated app.js card template!")
else:
    print("[X] Failed to find target boundaries!")
