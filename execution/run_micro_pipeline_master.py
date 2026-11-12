# -*- coding: utf-8 -*-
"""
One-Click Master Runner for Micro Audit Pipeline (Step 0 to Step 8)
- Starts local server.py on port 8080 within the same process tree if not running,
  runs Step 0 ~ Step 8 in isolated subprocesses, then cleanly shuts down the temporary server.
"""
import os
import sys
import time
import urllib.request
import subprocess

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(BASE_DIR)
AUDIT_DIR = os.path.join(BASE_DIR, "micro_audit")

STEPS = [
    ("Step 0", "step0.py", "환경 점검 & 로컬·프로덕션 v1.6.1 동기화"),
    ("Step 1", "step1.py", "모바일·태블릿 스플래시, PC 0초 바이패스 & 랭킹 API"),
    ("Step 2", "step2.py", "32대 듀얼 탭(16+16), 5대 품목 오름차순 & 사과 노이즈 0%"),
    ("Step 3", "step3.py", "3단계 수집 & 오뚜기밥 24개 단종 배제 & 타겟 직결"),
    ("Step 4", "step4.py", "PC/모바일 네이버 앵커 자동 분기 & 파워링크 우회 실측"),
    ("Step 5", "step5.py", "하단 독(25px)·고정 스크롤·실터치 PTR·검색바 3중 떨림 방지"),
    ("Step 6", "step6.py", "레이더 모달 오토포커스·즉시 은닉·iOS 줌 방지 & 임의 검색"),
    ("Step 7", "step7.py", "5대 디바이스 반응형·PC 검색 가드 & PWA 인프라"),
    ("Step 8", "step8.py", "UI 개선 실측, Vercel 교차 검증 & 동적 리포트 어셈블리")
]


def is_local_server_up():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8080/api/status", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    print("=" * 72, flush=True)
    print("🚀 [PriceTrace] 8-Step Micro Pipeline Master Runner v2.0 Started", flush=True)
    print("=" * 72, flush=True)
    t_global_start = time.time()

    server_proc = None
    if not is_local_server_up():
        print("[*] Starting local server.py on port 8080 for isolated audit...", flush=True)
        server_proc = subprocess.Popen(
            [sys.executable, os.path.join(WORKSPACE_DIR, "server.py"), "--port", "8080"],
            cwd=WORKSPACE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(15):
            time.sleep(0.4)
            if is_local_server_up():
                print("[✓] Local server.py ready on http://127.0.0.1:8080", flush=True)
                break
        else:
            print("[✗] Failed to start local server.py!", flush=True)

    total_steps = len(STEPS)
    all_passed = True
    step_results = []

    try:
        for idx, (step_id, script_name, description) in enumerate(STEPS):
            script_path = os.path.join(AUDIT_DIR, script_name)
            progress_pct = int(((idx + 1) / total_steps) * 100)
            filled_bars = int(progress_pct / 5)
            bar_str = "█" * filled_bars + "░" * (20 - filled_bars)

            print(f"\n▶ [{idx+1}/{total_steps}] [{bar_str}] {progress_pct}%: {step_id} - {description}", flush=True)
            t0 = time.time()

            try:
                res = subprocess.run(
                    [sys.executable, script_path],
                    cwd=BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=45
                )
                elapsed = round(time.time() - t0, 2)
                lines = [l.strip() for l in res.stdout.strip().split("\n") if l.strip()]
                last_line = lines[-1] if lines else ""
                if res.returncode == 0:
                    print(f"  ✓ {step_id} PASS ({elapsed}s) -> {last_line}", flush=True)
                    step_results.append((step_id, description, "PASS", elapsed))
                else:
                    print(f"  ✗ {step_id} FAIL ({elapsed}s) -> {last_line}", flush=True)
                    if res.stderr.strip():
                        print(f"    Stderr: {res.stderr.strip()[:300]}", flush=True)
                    step_results.append((step_id, description, "FAIL", elapsed))
                    all_passed = False
            except subprocess.TimeoutExpired:
                elapsed = round(time.time() - t0, 2)
                print(f"  ✗ {step_id} TIMEOUT ({elapsed}s)", flush=True)
                step_results.append((step_id, description, "TIMEOUT", elapsed))
                all_passed = False

        # If Step 8 failed before running assemble_final_markdown or partially failed, ensure report gets assembled from JSONs
        if step_results and step_results[-1][2] != "PASS":
            try:
                subprocess.run(
                    [sys.executable, "-c", "import sys; sys.path.insert(0, 'micro_audit'); import step8; step8.assemble_final_markdown()"],
                    cwd=BASE_DIR,
                    timeout=10
                )
            except Exception:
                pass
    finally:
        if server_proc is not None:
            print("\n[*] Terminating temporary local server.py...", flush=True)
            server_proc.terminate()
            try:
                server_proc.wait(timeout=3)
            except Exception:
                server_proc.kill()

    total_elapsed = round(time.time() - t_global_start, 2)
    print("\n" + "=" * 72, flush=True)
    print(f"🏁 Pipeline Finished in {total_elapsed}s | Overall: {'ALL PASS ✅' if all_passed else 'FAILURES DETECTED ❌'}", flush=True)
    print("=" * 72, flush=True)

    for sid, desc, st, el in step_results:
        mark = "✓ PASS" if st == "PASS" else f"✗ {st}"
        print(f" - {sid} ({el}s): {desc} [{mark}]", flush=True)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
