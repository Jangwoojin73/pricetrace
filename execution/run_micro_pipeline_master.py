# -*- coding: utf-8 -*-
"""
One-Click Master Runner for Micro Audit Pipeline (Step 0 to Step 8)
Runs each step in an isolated subprocess to guarantee zero browser deadlocks.
"""
import os
import sys
import time
import subprocess

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_DIR = os.path.join(BASE_DIR, "micro_audit")

STEPS = [
    ("Step 0", "step0.py", "환경 점검 & 전역 센티널 초기화"),
    ("Step 1", "step1.py", "인트로 스플래시 & 메인 랭킹 API 정합성"),
    ("Step 2", "step2.py", "32대 전 품목 듀얼 탭 & 오름차순 검색"),
    ("Step 3", "step3.py", "3단계 수집 엔진 & 오뚜기밥 단종 링크 배제"),
    ("Step 4", "step4.py", "네이버 가격 앵커 자동 분기 & 광고 100% 우회"),
    ("Step 5", "step5.py", "하단 네비게이션 & 고정 스크롤 안정성"),
    ("Step 6", "step6.py", "레이더 모달 포커스, 은닉, iOS 줌 방지 & 임의 검색"),
    ("Step 7", "step7.py", "5대 디바이스 반응형 & PWA 인프라 무결성"),
    ("Step 8", "step8.py", "UI 신규 개선(34px) 실측 & 최종 리포트 어셈블리")
]

def main():
    print("=" * 70)
    print("🚀 [PriceTrace] 8-Step Micro Pipeline Master Runner Started")
    print("=" * 70)
    t_global_start = time.time()
    
    total_steps = len(STEPS)
    all_passed = True
    step_results = []
    
    for idx, (step_id, script_name, description) in enumerate(STEPS):
        script_path = os.path.join(AUDIT_DIR, script_name)
        progress_pct = int(((idx + 1) / total_steps) * 100)
        filled_bars = int(progress_pct / 10)
        bar_str = "█" * filled_bars + "░" * (10 - filled_bars)
        
        print(f"\n▶ [{idx+1}/{total_steps}] [{bar_str}] {progress_pct}%: {step_id} - {description}")
        t0 = time.time()
        
        # Execute in isolated subprocess with 35s hard timeout
        try:
            res = subprocess.run(
                [sys.executable, script_path],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                timeout=35
            )
            elapsed = round(time.time() - t0, 2)
            if res.returncode == 0:
                print(f"  ✓ {step_id} SUCCESS ({elapsed}s)")
                # Print last meaningful line from stdout
                lines = [l.strip() for l in res.stdout.strip().split("\n") if l.strip()]
                if lines:
                    print(f"    -> {lines[-1]}")
                step_results.append((step_id, description, "PASS", elapsed))
            else:
                print(f"  ✗ {step_id} FAILED ({elapsed}s)")
                print(f"    Stderr: {res.stderr.strip()[:200]}")
                step_results.append((step_id, description, "FAIL", elapsed))
                all_passed = False
        except subprocess.TimeoutExpired:
            elapsed = round(time.time() - t0, 2)
            print(f"  ✗ {step_id} TIMEOUT ({elapsed}s)")
            step_results.append((step_id, description, "TIMEOUT", elapsed))
            all_passed = False
            
    total_elapsed = round(time.time() - t_global_start, 2)
    print("\n" + "=" * 70)
    print(f"🏁 All Steps Finished in {total_elapsed}s | Overall Result: {'ALL PASS ✅' if all_passed else 'SOME FAILED ⚠️'}")
    print("=" * 70)
    
    for sid, desc, st, el in step_results:
        mark = "✓ PASS" if st == "PASS" else f"✗ {st}"
        print(f" - {sid} ({el}s): {desc} [{mark}]")

if __name__ == "__main__":
    main()
