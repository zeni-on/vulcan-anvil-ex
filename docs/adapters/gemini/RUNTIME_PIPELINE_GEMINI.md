# Runtime Pipeline & Log Stream Protocol (Gemini/Agy Candidate)

> 상태: v0.1 (Gemini Runner 런타임 호출 및 파이프라인 규약)
> 목적: 메인 에이전트(Orchestrator)가 워커 에이전트(agy)를 기동하고, 실행 로그를 캡처 및 파이프라이닝하여 모니터링 및 복구(Resume) 기능을 수행하는 세부 메커니즘을 정의한다.
> 관찰: 현재 Windows `agy.exe --print`는 stdout JSONL을 안정적으로 제공하지 않을 수 있으므로 `--log-file`을 primary activity source로 사용한다.

---

## 1. 메인 에이전트의 agy 호출 및 파이프라이닝 흐름

오케스트레이터(`vulcan.py`)는 물리적/논리적으로 격리된 워커 환경을 제어하기 위해 워커 실행기(`agy.exe` 등)를 서브프로세스로 기동하고 실시간 스트림 파이프라인을 구축합니다.

```text
┌──────────────────────────────────────────────────────────┐
│              Orchestrator Engine (vulcan.py)             │
│  1. Run YAML 파싱  ──>  2. agy.exe Subprocess 기동      │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼ (Execute CLI Command)
┌──────────────────────────────────────────────────────────┐
│                  Gemini Runner (agy.exe)                 │
│  - 코드 작성/편집   - 테스트/검증 수행   - 완료 보고 생성   │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼ (Log file tail / stdout when available)
┌──────────────────────────────────────────────────────────┐
│             Real-time Pipeline & Integration             │
│  - Log line 파싱 (Conversation ID, Status 획득)           │
│  - Activity & Status JSON 로그 누적 기록 및 Handoff 힌트   │
└──────────────────────────────────────────────────────────┘
```

---

## 2. 구체적인 동작 예시

### ① [Input] 오케스트레이터의 워커 실행 CLI 명령
오케스트레이터는 파이썬의 `subprocess.Popen`을 사용해 백그라운드로 `agy.exe`를 기동하고, 표준 출력 및 표준 에러를 가로챕니다.

```bash
agy.exe --add-dir "C:/Workspace/worktree_RUN-016" --add-dir "C:/Workspace/vulcan-anvil-ex" --log-file "C:/Workspace/project/docs/runs/_exec/RUN-016_antigravity-exec.txt" --print-timeout "2400s" --dangerously-skip-permissions --print "You are executing a worker Run for Vulcan-Anvil Ex..."
```

`--add-dir`에는 절대경로를 사용한다. 상대경로 `.`는 Windows `agy.exe`에서 거부될 수 있다.
비대화형 `--print`에서는 권한 승인 대기 없이 실행되도록 `--dangerously-skip-permissions`를 사용한다.

### ② [Output] `agy.exe` 실행 로그 스트림
워커가 구동되면서 `--log-file`에 conversation 생성, 모델 선택, stream 상태가 기록된다.
stdout은 비어 있을 수 있으므로 성공 판단은 결과 파일 변경 여부와 로그를 함께 본다.

```text
Propagating selected model override to backend: label="Gemini 3.5 Flash (High)"
Created conversation 51841def-8a79-4b0d-b408-cb622532e7cd
Streaming conversation 51841def-8a79-4b0d-b408-cb622532e7cd
text_drip.go:173] Drip stopped: lastStepIdx=2, charIdx=2, length=2
Stopping conversation stream
```

### ③ [Pipeline] 오케스트레이터의 log tail 파싱 파이썬 코드
`vulcan.py` 내에서 비동기로 `--log-file`을 tail 하고 처리하는 핵심 로직 예시입니다.

```python
# vulcan.py의 agy log tail 파싱 로직 구현 표준
import subprocess
import re
import time
from pathlib import Path

def run_agent_with_log_tail(cmd, run_id, log_file):
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, 
        encoding="utf-8"
    )

    position = 0
    while process.poll() is None:
        path = Path(log_file)
        if not path.exists():
            time.sleep(1)
            continue

        with path.open(encoding="utf-8", errors="replace") as f:
            f.seek(position)
            for line in f:
                if "Created conversation" in line or "Streaming conversation" in line:
                    match = re.search(r"conversation ([0-9a-fA-F-]{20,})", line)
                    if match:
                        save_resume_hint(run_id, f"agy.exe --conversation {match.group(1)}")
                        update_dashboard_status(run_id, "Gemini 응답 스트림 수신 중")
                elif "Propagating selected model override" in line:
                    update_dashboard_status(run_id, "Gemini 모델 확인")
                elif "Drip stopped" in line:
                    update_dashboard_status(run_id, "Gemini 응답 스트림 수신")
            position = f.tell()

        time.sleep(1)
```

---

## 3. Log stream 사용의 주요 의미

1. **이어하기(Resume Handoff) 무결성 확보**:
   * AI 연동 작업은 모델의 추론 및 빌드 속도에 따라 완료까지 오랜 시간이 걸립니다. 프로세스가 중간에 유실되거나 타임아웃이 발생하더라도, 오케스트레이터가 로그에서 획득한 `conversation_id`를 보존하면 `agy.exe --conversation <ID>`로 이어서 작업할 후보를 만들 수 있습니다.
2. **비차단 실시간 현황 대시보드 (Real-time Dashboards)**:
   * 전체 프로세스가 완료된 후 일시불로 로그를 받는 대신, 모델 선택, conversation 생성, stream 수신 같은 상태를 대시보드나 CLI 화면에 실시간으로 표시하여 사용자 및 오케스트레이터의 동기적 모니터링을 지원합니다.
3. **구조화된 로그 데이터베이스 구축**:
   * agy 원시 로그는 텍스트로 보관하고, Vulcan은 필요한 상태만 `activity.json`과 `status.json`으로 정규화한다. stdout이 비어 있어도 결과 파일 변경, exit code, 로그 상태를 함께 사용해 성공/실패를 판정한다.
