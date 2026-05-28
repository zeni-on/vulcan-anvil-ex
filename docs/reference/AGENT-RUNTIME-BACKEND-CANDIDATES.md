# Agent Runtime Backend Candidates

이 문서는 `run-exec`와 `agent-run`이 외부 worker를 실행할 때 사용할 수 있는 runtime backend 후보를 정리한다.

## 현재 기본값

현재 Vulcan-Anvil Ex의 기본 실행 방식은 Python `subprocess` 기반이다.

- `codex-cli`, `claude-cli`, `agy.exe` 같은 runner를 직접 호출한다.
- 실행 상태와 heartbeat는 `docs/runs/_exec/`의 status/activity 파일로 남긴다.
- Dashboard는 이 파일을 읽어 runner 상태, 최근 메시지, worktree 상태를 표시한다.

이 방식은 단순하고 Windows 로컬 개발 환경에서 바로 동작하므로 기본값으로 유지한다.

## 장기 후보: Google AX

Google AX는 event log, resume, trace, local/remote actor 조율을 제공하는 agent runtime 방향의 후보로 검토할 수 있다.

다만 현재는 즉시 도입하지 않는다.

- 프로젝트가 빠르게 변하는 early development 상태다.
- Vulcan의 현재 구조는 Python CLI와 로컬 worktree 중심이다.
- Codex, Claude, Antigravity/Gemini CLI를 바로 대체하는 도구가 아니라, 이들을 감싸는 runtime layer에 가깝다.
- 도입하려면 Vulcan Run 입력 계약과 AX event log를 상호 변환하는 wrapper가 필요하다.

## PoC 조건

AX 또는 유사 runtime을 검토할 때는 다음 조건을 만족해야 한다.

- 기존 `subprocess` backend를 대체하지 않고 `experimental` 옵션으로만 붙인다.
- 최소 PoC는 단순 echo 또는 read-only review worker부터 시작한다.
- `run_id`, runner, model, worktree, started/completed, exit code, last message, changed files를 Vulcan의 기존 `_exec` 형식으로 변환할 수 있어야 한다.
- Dashboard가 기존 worker status와 같은 방식으로 표시할 수 있어야 한다.
- failure/resume/timeout 동작이 현재 `run-exec`보다 명확히 좋아야 한다.

## 권장 방향

당장은 runtime backend보다 다음 영역에 집중한다.

- 좋은 Run 생성
- worker 실행 전 `run-preflight`
- worker 실행 로그와 heartbeat
- Orchestrator 통합 검증
- Gate 4 QA 분리

외부 runtime backend는 이 흐름이 충분히 안정된 뒤 검토한다.
