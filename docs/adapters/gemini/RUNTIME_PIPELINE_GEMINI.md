# Runtime Pipeline & JSONL Stream Protocol (GEMINI Standard)

> 상태: v0.1 (Gemini Runner 런타임 호출 및 파이프라인 규약)
> 목적: 메인 에이전트(Orchestrator)가 워커 에이전트(agy)를 기동하고, 실시간으로 출력되는 JSONL 로그 스트림을 캡처 및 파이프라이닝하여 모니터링 및 복구(Resume) 기능을 수행하는 세부 메커니즘을 정의한다.

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
                             ▼ (Real-time stdout JSONL Stream)
┌──────────────────────────────────────────────────────────┐
│             Real-time Pipeline & Integration             │
│  - Line-by-line JSON 파싱 (Thread ID, Status 획득)        │
│  - Activity & Status JSON 로그 누적 기록 및 Handoff 힌트   │
└──────────────────────────────────────────────────────────┘
```

---

## 2. 구체적인 동작 예시

### ① [Input] 오케스트레이터의 워커 실행 CLI 명령
오케스트레이터는 파이썬의 `subprocess.Popen`을 사용해 백그라운드로 `agy.exe`를 기동하고, 표준 출력 및 표준 에러를 가로챕니다.

```bash
agy.exe --add-dir "C:/Workspace/worktree_RUN-016" --add-dir "C:/Workspace/vulcan-anvil-ex" --print-timeout "2400s" --dangerously-skip-permissions --print "You are executing a worker Run for Vulcan-Anvil Ex..."
```

### ② [Output] `agy.exe` 실시간 JSONL 표준 출력 스트림
워커가 구동되면서 터미널(stdout)에 라인 단위로 AI의 행동 상태와 도구(Tool) 호출 이벤트를 JSONL 형태로 출력합니다.

```json
{"type": "thread.started", "thread_id": "thread_gemini_abc123", "timestamp": "2026-05-22T19:20:00Z"}
{"type": "status_update", "status": "running", "current_task": "Loading schema files", "timestamp": "2026-05-22T19:20:02Z"}
{"type": "tool_call", "tool": "view_file", "path": "backend/app/main.py", "timestamp": "2026-05-22T19:20:10Z"}
{"type": "tool_call", "tool": "replace_file_content", "path": "backend/app/main.py", "timestamp": "2026-05-22T19:21:40Z"}
{"type": "status_update", "status": "running", "current_task": "Running pytest on backend", "timestamp": "2026-05-22T19:22:15Z"}
{"type": "execution.completed", "status": "success", "timestamp": "2026-05-22T19:23:00Z"}
```

### ③ [Pipeline] 오케스트레이터의 JSONL 실시간 파싱 파이썬 코드
`vulcan.py` 내에서 비동기로 스트림을 읽고 처리하는 핵심 로직 예시입니다.

```python
# vulcan.py의 CLI Popen 및 readline 파싱 로직 구현 표준
import subprocess
import json

def run_agent_with_jsonl_stream(cmd, run_id):
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, 
        encoding="utf-8"
    )

    # 실시간 JSONL 스트림을 한 줄씩 파싱
    for line in iter(process.stdout.readline, ''):
        clean_line = line.strip()
        if not clean_line:
            continue
            
        try:
            # JSON 포맷으로 실시간 파싱 시도
            event = json.loads(clean_line)
            event_type = event.get("type")
            
            # 1. 예기치 않은 프로세스 단절 시 세션/스레드 복구를 위한 ID 획득 (Resume)
            if event_type == "thread.started":
                thread_id = event.get("thread_id")
                save_resume_hint(run_id, f"agy resume {thread_id}")
                
            # 2. 실시간 대시보드 상태 업데이트
            elif event_type == "status_update":
                current_task = event.get("current_task")
                update_dashboard_status(run_id, current_task)
                
            # 3. 상세 액티비티 로그 저장
            append_activity_log(run_id, event)
            
        except json.JSONDecodeError:
            # JSON이 아닌 예외 텍스트(예: 빌드 에러 스택)는 일반 원시 로그 파일에 기록
            write_to_raw_log(run_id, line)
```

---

## 3. JSONL 형식 사용의 주요 의미

1. **이어하기(Resume Handoff) 무결성 확보**:
   * AI 연동 작업은 모델의 추론 및 빌드 속도에 따라 완료까지 오랜 시간이 걸립니다. 프로세스가 중간에 유실되거나 타임아웃이 발생하더라도, 오케스트레이터가 스트림 맨 첫 줄에서 실시간으로 획득한 `thread_id`(`thread_gemini_abc123`)를 보존하고 있으므로, 끊긴 시점부터 컨텍스트 손실 없이 바로 작업을 재개(`resume`)할 수 있습니다.
2. **비차단 실시간 현황 대시보드 (Real-time Dashboards)**:
   * 전체 프로세스가 완료된 후 일시불로 로그를 받는 대신, 에이전트가 어떤 파일을 탐색 중인지, 테스트 명령을 돌리고 있는지 등에 관한 단위 세부 작업(`current_task`)을 대시보드나 CLI 화면에 실시간으로 표시하여 사용자 및 오케스트레이터의 동기적 모니터링을 지원합니다.
3. **구조화된 로그 데이터베이스 구축**:
   * 실행 결과를 하나의 뭉뚱그려진 텍스트 파일로 저장하는 대신, `type`별로 분류된 구조화 데이터로 저장하여 통계 분석(예: 평균 도구 호출 빈도, 구간별 소요 시간 등)을 용이하게 합니다.
