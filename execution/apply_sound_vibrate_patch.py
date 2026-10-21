# -*- coding: utf-8 -*-
import sys

def patch_index_html():
    with open('public/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Find the modalAlertToggle section
    start_anchor = 'id="modalAlertToggle"'
    idx_toggle = html.find(start_anchor)
    if idx_toggle == -1:
        print("ERROR: modalAlertToggle not found")
        return False

    # Find the start of this block
    block_start = html.rfind('<!--', 0, idx_toggle)
    # Find the end of this div block
    block_end = html.find('</div>\n\n', idx_toggle) + len('</div>\n\n')

    old_block = html[block_start:block_end]
    print("Found old block to replace (len:", len(old_block), ")")

    new_block = '''<!-- 목표가 도달 알림 활성화 토글 -->
        <div class="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl mt-2">
          <div>
            <div class="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
              <i data-lucide="bell" class="w-3.5 h-3.5 text-blue-600"></i>
              <span>목표가 도달 알림 활성화</span>
            </div>
            <div class="text-[11px] text-slate-500">목표가 이하로 떨어졌을 때 알림 배너 및 상태를 표시합니다.</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer shrink-0 ml-3" title="알림 활성화 토글">
            <input type="checkbox" id="modalAlertToggle" class="sr-only peer" checked>
            <div class="w-10 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-naver"></div>
          </label>
        </div>

        <!-- 특가 알림 소리(차임벨) 토글 -->
        <div class="flex items-center justify-between p-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl mt-2">
          <div>
            <div class="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
              <i data-lucide="volume-2" class="w-3.5 h-3.5 text-blue-600"></i>
              <span>특가 감지 차임벨 소리</span>
            </div>
            <div class="text-[11px] text-slate-500">목표가 이하 달성 시 경쾌한 띵동~ 🔔 벨소리를 재생합니다.</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer shrink-0 ml-3" title="차임벨 소리 토글">
            <input type="checkbox" id="modalSoundToggle" class="sr-only peer" checked>
            <div class="w-10 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-naver"></div>
          </label>
        </div>

        <!-- 특가 알림 모바일 햅틱 진동 토글 -->
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
        </div>

        <!-- 소리 / 진동 즉시 테스트 버튼 -->
        <div class="flex items-center justify-between p-3.5 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200/80 rounded-2xl mt-2">
          <div>
            <div class="text-xs font-bold text-emerald-900 flex items-center space-x-1.5">
              <i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-600"></i>
              <span>소리 및 진동 동작 테스트</span>
            </div>
            <div class="text-[11px] text-emerald-700/80">현재 설정된 차임벨 소리와 햅틱 진동을 즉시 체험해 봅니다.</div>
          </div>
          <button type="button" id="testNotificationBtn" class="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shrink-0 ml-3 shadow-xs active:scale-95 transition-all flex items-center space-x-1 cursor-pointer">
            <i data-lucide="bell-ring" class="w-3.5 h-3.5"></i>
            <span>미리 테스트</span>
          </button>
        </div>\n\n'''

    html = html[:block_start] + new_block + html[block_end:]

    # Bump asset query versions
    html = html.replace('20261021_v144', '20261021_v145')

    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("public/index.html successfully updated!")
    return True

if __name__ == '__main__':
    patch_index_html()
