# Changelog

## Unreleased

## 0.4.9 - 2026-06-26

`0.4.9`은 Product/PoC profile과 Orchestrator runtime 표시를 단단하게 만드는 안정화 패치 릴리즈다. Product Gate 5, PoC evidence, QA 환경 차단, delegation sidecar, Dashboard/Jest 검증 경로를 실제 샘플과 fixture smoke 기준으로 고정했다.

Release notes: [docs/releases/v0.4.9.md](docs/releases/v0.4.9.md)

- `doctor` / `doctor --json` 환경 진단을 추가하고, QA-000에서 환경 차단과 제품 결함을 분리할 수 있도록 증적 계약을 보강했다.
- `execute --dry-run` / `execute --dry-run --json`을 추가해 Run 실행 전 `run-check`, `run-preflight`, scope, verification, delegation sidecar 후보를 한 번에 확인할 수 있게 했다.
- native subagent/thread/Agy branch 위임 상태를 Dashboard와 `status`에서 읽을 수 있도록 delegation sidecar와 worker verification state 표시를 보강했다.
- Codex model fallback을 `status`와 실행 기록에 표시하고, 지원되지 않는 `gpt-5.3-codex` alias가 `gpt-5.5`로 호환 fallback되는 경로를 fixture smoke에 고정했다.
- Product profile의 실제 샘플 재실행 결과를 반영해 Gate 4 Planned regression row, Gate 5 release approval 문서 누락, Product `release-pr --dry-run` evidence 기준을 fixture smoke에 고정했다.
- PoC 반복형 샘플에서 `Pass` / `Smoke Pass`가 실제 evidence 파일 없이 구현 완료로 집계되지 않도록 PoC evidence guard를 추가했다.
- Dashboard test 경로가 `.next`, `test-results`, `playwright-report` 같은 생성물을 스캔하지 않도록 Jest 설정을 안정화했다.
- Roadmap과 reference 문서를 실제 Product/PoC 샘플 재실행 결과 기준으로 현행화했다.

## 0.4.8 - 2026-06-15

`0.4.8`은 Product profile 안정화 패치 릴리즈다. Product 프로젝트에서 release PR, Build Wave trace, ADR empty-state가 audit profile 기준과 섞여 보이던 부분을 정리했다.

Release notes: [docs/releases/v0.4.8.md](docs/releases/v0.4.8.md)

- Product profile의 `release-pr --dry-run`이 audit용 QA Finding/Test Result/Traceability Matrix 대신 `docs/product/` 원장 문서, backlog, Gate 5 승인서를 evidence로 표시하도록 했다.
- Product Build Wave record 수집이 `SCN`, `API`, `DATA`, `REG` ID를 보존하도록 보강했다. `status --check`나 session refresh 뒤 관련 ID가 `REQ/UI` 중심으로 축소되는 문제를 막는다.
- Product ADR Log 템플릿을 `ADR-NONE` empty-state로 바꿨다. 실제 의사결정이 없을 때 `ADR-001 | TBD` placeholder를 남기지 않는다.
- fixture smoke regression에 Product release body, Product Build Wave related IDs, Product ADR empty-state 검증을 추가했다.
- `solution` 입력은 `product` alias라는 현재 정책에 맞춰 regression 기대값을 정리했다.

## 0.4.7 - 2026-06-14

`0.4.7`은 Dashboard 문서 코멘트 기능과 Orchestrator 가시성을 추가한 패치 릴리즈다. 사용자는 Dashboard에서 Markdown 산출물을 읽으면서 문서 블록 단위로 코멘트를 남길 수 있고, Orchestrator는 `vulcan.py status`의 `dashboard_comments` 요약을 통해 코멘트가 있는지 먼저 확인할 수 있다.

Release notes: [docs/releases/v0.4.7.md](docs/releases/v0.4.7.md)

- Dashboard 문서 뷰어에 sidecar 기반 코멘트 패널을 추가했다. 코멘트는 원본 Markdown을 직접 수정하지 않고 프로젝트의 `.vulcan/comments/comments.jsonl`에 저장한다.
- Markdown 렌더링 블록에서 `+` 버튼으로 코멘트를 추가하고, sticky 패널에서 문서별 open/closed 코멘트를 확인할 수 있게 했다.
- 코멘트 상태를 `open`/`closed` 중심으로 단순화했다. 이전 상태값(`resolved`, `converted`, `stale`)은 읽을 때 `closed`로 정규화한다.
- `python vulcan.py status`와 `status --json`에 `dashboard_comments` 요약을 추가했다. Orchestrator는 Gate/Run 작업 전에 Dashboard 코멘트와 FIND/CR 후보를 먼저 확인할 수 있다.
- `AGENTS.md`와 Codex CLI 가이드에 Dashboard 코멘트 확인 루틴을 반영했다.

## 0.4.6 - 2026-06-07

`0.4.6`은 GitHub release 기준 `0.4.4` 이후 누적된 Codex custom agent, PoC profile 완충, Agy native main Orchestrator, Workspace branch delegation, Run preflight guard, Gate 전환 완성도 검사를 묶은 패치 릴리즈다. `0.4.5`는 문서상 버전으로 정리되었지만 별도 GitHub tag/release는 만들지 않았으므로, 공개 릴리즈 기준으로는 `0.4.6`이 다음 패치 릴리즈다.

Release notes: [docs/releases/v0.4.6.md](docs/releases/v0.4.6.md)

- `check-trace`의 진단 출력을 더 구체화했다. 단순 실패 요약이 아니라 문제가 된 산출물/ID/상태를 더 잘 추적할 수 있게 하여 Orchestrator가 잘못된 문서를 추측으로 고치지 않도록 했다.
- `prepare-transition` 명령을 추가했다. Gate 전환 전에 Run 완료 여부, 추적성 정합성, 전환 차단 사유를 한 번에 확인하는 사전 진단 명령이다.
- `drift-report` 명령을 추가했다. 설계 산출물과 실제 코드/API/DB surface의 불일치를 공식 문서에 바로 덮어쓰지 않고 drift 후보 보고서로 생성한다.
- Run 생성 시 `source_documents.read_first`에 Codex 전용 `GATE_PROMPTS.md`를 모든 runner에게 주입하지 않도록 정리했다. 공통 Gate 실행 기준은 `docs/core/GATE_EXECUTION_CHECKLIST.md`로 분리하고, Codex/Claude/Gemini는 각 adapter 전용 Gate prompt만 추가로 받는다.
- Core Run 입력 샘플에서 Codex adapter 전용 prompt 참조를 제거하고 공통 Gate 실행 체크리스트를 사용하도록 정리했다.
- Codex subagent/thread, Claude subagent, Agy workspace branch agent 같은 native 위임 결과를 `delegation_records`로 남기는 Core 기준을 추가했다. 외부 CLI runner는 기존 `Run Execution Record`와 `_exec` 로그를 유지하고, native 위임은 위임 대상, 범위, 변경 파일, 결과 요약, Orchestrator 재검증 명령 중심으로 얇게 추적한다.
- Antigravity/Agy `Workspace: branch`와 `delegation_records.mode: agy-branch-agent` 정합성 검토 기록을 `docs/reference/_reviews/AGY-WORKSPACE-BRANCH-DELEGATION-REVIEW.md`에 추가하고, Getting Started, Concepts, Roadmap, Gemini adapter README에서 연결했다.
- `run-check`와 `run-preflight`가 Run 상단 metadata와 `3. Run 입력 계약` YAML의 핵심 필드(`profile`, `adapter`, `run_type`, `gate`, `persona`, `skill`) 불일치를 잡도록 보강했다.
- `prepare-transition`이 현재 Gate에서 완료된 worker Run의 preflight 차단 항목을 사후 안전망으로 점검한다. native subagent/thread/Agy branch 위임 전 preflight 실행은 여전히 Orchestrator의 필수 절차다.
- `prepare-transition`에 산출물 내용 완성도 검사를 추가했다. 완료/승인 상태 문서의 템플릿 placeholder와 빈 Markdown 표 행을 Gate 전환 전에 드러낸다.
- `BW-000` scaffold Run이 요구사항/테스트/UI 상태를 `Implemented`, `Verified`, `Pass`로 확정하지 못하도록 `run-check`/`run-preflight` 기준을 보강했다.
- QA Finding 템플릿에 `No Findings` 표준 양식을 추가하고, Playwright dialog는 예상 여부를 기록한 뒤 처리하도록 QA 실행 기준을 정리했다.

## 0.4.5 - 2026-06-06

`0.4.5`는 `0.4.4`의 PoC compact Run 흐름 위에 Codex custom agent 정의, PoC profile 검사 완충, Gate 4 QA workspace 기본값 정리를 더한 패치 릴리즈다.

Release notes: [docs/releases/v0.4.5.md](docs/releases/v0.4.5.md)

- `.codex/agents/`에 `trace-scout`, `run-drafter`, `contract-reviewer`, `qa-reader` 정의를 추가했다.
- README와 Codex adapter 문서에 Codex repo-local skill과 custom agent 사용 섹션을 추가했다.
- PoC profile에서 사유와 후속 판단 시점이 있는 `TBD`/`확정필요`, 상세 추적 누락, 미실행, `environment_blocked`를 차단 이슈보다 경고/판단 항목으로 우선 분류하도록 했다.
- Gate 4 QA 기본 workspace를 별도 QA worktree가 아니라 `workflow.integration_branch`의 현재 작업공간으로 정리했다. QA worktree는 명시적으로 활성화한 경우에만 사용한다.
- Codex runner model policy에서 지원되지 않는 이전 기본 모델을 `gpt-5.5`로 보정하고, upgrade 시 config migration을 수행한다.
- `AGENTS.md`, `GETTING_STARTED`, `DELIVERY_PROFILES`, `TRACEABILITY_RULES`, `POC-RUN-COMPACT-STRATEGY`를 PoC 경량화와 custom agent 운영 기준에 맞게 현행화했다.

## 0.4.4 - 2026-05-31

`0.4.4`는 `0.4.3`의 trace-seed와 Gate 4 QA 안정화 흐름을 유지하면서 PoC Profile의 Run 입력 문서와 Antigravity 결과 회수를 경량화한 패치 릴리즈다.

Release notes: [docs/releases/v0.4.4.md](docs/releases/v0.4.4.md)

- PoC Profile에서 `run-new`와 `wave-start`의 기본 `--trace-depth`를 1로 낮췄다. audit profile은 기존 기본 depth 2를 유지한다.
- PoC Run의 `source_documents.reference_on_demand`를 직접 관련 문서 중심으로 제한하고, worker Run에 `worker_run_sizing_policy`와 오케스트레이터용 Run protocol 문서가 반복 삽입되지 않도록 했다.
- `docs/reference/POC-RUN-COMPACT-STRATEGY.md`를 추가해 PoC 경량화의 목적, 적용 범위, 후속 작업을 문서화했다.
- Windows `agy.exe` runner가 stdout을 비워도 `transcript_full.jsonl` 우선, `transcript.jsonl` fallback 순서로 마지막 모델 응답을 회수한다.
- fixture smoke에 PoC compact Run과 PoC trace-depth 기본값 검증을 추가했다.

## 0.4.3 - 2026-05-31

`0.4.3`은 `0.4.2`의 worker watchdog 흐름을 유지하면서 Run 입력 품질, Gate 4 QA 결과 판정, 요구사항추적표 최종 상태 정리를 보강한 패치 릴리즈다.

Release notes: [docs/releases/v0.4.3.md](docs/releases/v0.4.3.md)

- `run-new`와 `wave-start`에 `--trace-seed`, `--trace-depth` 옵션을 추가했다. 추적성 그래프에서 `related_ids`, `target_contracts`, `source_documents.reference_on_demand` 초안을 보강해 worker Run 입력 품질을 높인다.
- fixture smoke가 `run-new --trace-seed`와 `wave-start --trace-seed` 생성 결과를 검증하도록 확장했다.
- `simple-hello-audit` fixture Run 문서를 최신 `run-check` 기준에 맞게 정규화했다.
- Gate 4 `check-trace`가 Gate 3 테스트케이스의 계획 상태보다 QA 테스트 결과서(`DOC-QA-G4-002_Test-Result_v0.1.md`)의 실제 실행 결과를 우선 읽도록 변경했다.
- QA 결과서 파서는 `UT-001`, `IT-001`, `PT-001`, `UI-001-01` 같은 실행 단위만 집계하고 `UI-001` 화면 그룹 ID, `EV-*` 증적 ID, `UICMP-*` 비교 ID를 실행 결과에서 제외한다.
- Gate 3 테스트케이스는 계획/기대 기준, Gate 4 테스트 결과서는 실제 실행 원본, 요구사항추적표는 최종 검증 상태 원장이라는 문서 역할을 README, Getting Started, Concepts, Traceability Rules, 템플릿에 반영했다.
- Gate 4 `qa-fix-loop` Run 계약을 `run_type: QAFix`, worker 실행, FIND 기반 범위 제한, Orchestrator 재검증 기준으로 보강했다.
- Dashboard Agent 패널의 watchdog 문구를 `Worker active`, `Worker quiet`, `Worker stalled`, `Hard timeout` 기준으로 정리하고, 오래된 activity 파일에서도 timeout/watchdog fallback을 표시하도록 보강했다.
- Delivery Profile 문서를 Core + Profile Overlay 방향으로 보강해 audit, solution, poc, lite profile의 운영 강도 차이를 정리했다.

## 0.4.2 - 2026-05-30

`0.4.2`는 `0.4.1`의 worker timeout 안정화 흐름을 한 단계 더 다듬어, 장시간 worker를 즉시 kill하거나 soft extension에만 의존하지 않고 주기적 progress watchdog으로 관제하는 패치 릴리즈다.

Release notes: [docs/releases/v0.4.2.md](docs/releases/v0.4.2.md)

- `run-exec`/`agent-run --mode work`의 worker timeout 정책을 soft-timeout 중심에서 progress watchdog 중심으로 확장했다. `progress_probe_seconds`, `no_progress_timeout_seconds`, `min_runtime_seconds`를 추가하고, 주기적 progress probe로 `active`, `quiet`, `stalled`, `timeout_hard` 상태를 기록한다.
- Dashboard Agent 패널에서 worker watchdog 상태, 마지막 진척, timeout policy/reason을 확인할 수 있게 했다.
- `ROADMAP.md`를 `0.4.x` 안정화 흐름과 worker watchdog 관제 항목 기준으로 현행화했다.

## 0.4.1 - 2026-05-30

`0.4.1`은 `0.4.0`의 trace-context, staged QA, release-pr 흐름을 유지하면서 worker 실행 안정성을 보강한 패치 릴리즈다. 장시간 worker 실행에서 즉시 kill 대신 soft timeout 기반 연장을 적용하고, Windows Agy runner의 빈 stdout 문제를 transcript fallback으로 보완했다.

Release notes: [docs/releases/v0.4.1.md](docs/releases/v0.4.1.md)

### Added

- `run-exec`/`agent-run --mode work`에 soft timeout 진행 감지와 hard timeout cap을 추가했다. status JSON, worktree diff, 변경 파일 수, runner log 진척을 확인해 의미 있는 진행이 있으면 제한적으로 실행 시간을 연장한다.
- worker 실행 기록에 `timeout_policy`, `extensions_used`, `timeout_reason`, extension event 정보를 남긴다.
- Windows `agy.exe` runner에서 stdout이 비어 있어도 Antigravity transcript의 `MODEL` 응답을 찾아 last-message와 실행 판정에 반영한다.

### Changed

- `Verified`/`Completed` Wave 처리 전에 Run 상태와 `open_issues`를 확인해 미해결 이슈가 있는 Run을 완료로 닫지 못하게 했다.
- `git diff --name-status`와 porcelain status 파싱을 정리해 한글 경로와 tab-separated path에서 첫 글자가 잘리는 문제를 줄였다.
- Independent Execution, Getting Started, Gemini runtime 문서를 worker timeout과 Agy transcript fallback 기준으로 현행화했다.

### Verification

- `python -m py_compile vulcan.py`
- `python scripts/regression/run_audit_smoke.py`
- `git diff --check`

## 0.4.0 - 2026-05-29

`0.4.0`은 `0.3.x`의 브랜치/worker/QA 실행 흐름 위에 trace-context 그래프, Dashboard Trace Explorer, Gate 4 실패 보고 계약, Release PR 안정화, 회귀 smoke 검증을 묶어 올린 마이너 릴리즈다. 요구사항추적표를 단순 표가 아니라 ID 그래프 원장으로 활용하고, Run/QA/release 자동화가 같은 기준으로 검증되도록 정리했다.

Release notes: [docs/releases/v0.4.0.md](docs/releases/v0.4.0.md)

### Added

- `trace-context` 명령을 추가했다. 요구사항추적표를 그래프 원장으로 파싱해 seed ID 주변의 `related_ids`, `target_contracts`, 관련 문서 후보를 YAML/JSON으로 출력한다.
- Gate 4 `qa-execution` Run에 `qa_failure_report_contract`와 `failure_reports` 출력 기준을 추가했다. QA worker는 실패를 고치지 않고 명령, cwd, exit code, 로그, 재현 명령, 영향 ID, FIND/CR/ISSUE 후보를 구조화해 반환한다.
- Dashboard 문서 Drawer에 Trace Explorer 레이어를 추가했다. 문서 본문은 그대로 두고, 감지한 ID를 `depth 1` 직접 edge 그래프와 목록 중심으로 탐색할 수 있다.

### Changed

- Fixture smoke harness가 `trace-context` JSON 결과, `release-pr` body 파일, 없는 base 브랜치, 잘못된 현재 브랜치, dirty worktree 차단을 함께 검증한다.
- `release-pr` body를 임시 디렉터리 대신 프로젝트 내부 `.vulcan/release/release-pr-body.md`에 생성해 dry-run과 수동 PR 작성 경로를 안정화했다.
- `release-pr`가 base/head 브랜치 존재 여부를 먼저 확인하고 명확한 오류를 출력하도록 보강했다.
- Gate 5에서 `workflow.integration_branch`를 `workflow.release_merge_to` 또는 `main`으로 보내는 `release-pr` 명령을 추가했다. Release PR은 생성/갱신까지만 자동화하며 merge는 명시 승인 뒤 수동으로 수행한다.
- `dev`를 고정 브랜치명처럼 설명하던 문구를 `workflow.integration_branch` 역할 기준으로 정리했다. 기본값은 `dev`지만 프로젝트별로 `develop`, `dev-happy` 같은 브랜치명을 사용할 수 있다.
- `GETTING_STARTED`, `CONCEPTS`, `UPGRADE_AND_DASHBOARD`, `ROADMAP`을 0.4.0 기준으로 보강하고, 브랜치 전략, `QA-000` workspace 재사용 흐름, trace-context 탐색 흐름을 그림과 절차로 설명했다.

## 0.3.0 - 2026-05-24

`0.3.0`은 `0.2.x`의 Gate/Run 계약을 유지하면서 audit workflow의 실행 브랜치, worker 실행, Gate 4 QA 실행 방식을 한 단계 더 명확히 한 마이너 릴리즈다. 구현은 `workflow.integration_branch` 통합 브랜치(기본값 `dev`)에서 진행하고, Gate 4 QA는 `QA-000`이 준비한 재사용 workspace를 기준으로 단계별 실행/증적/판정 후보를 분리한다.

### Added

- Gate 4 QA 실행 전용 `qa-execution` skill을 추가했다. QA worker는 테스트 실행, 로그/Playwright 증적, 후보 FIND/CR/ISSUE 수집을 담당하고 소스 수정은 하지 않는다.
- audit workflow용 브랜치 정책을 `vulcan.config.json.workflow`에 추가하고, `branch-status`/`branch-start impl` 명령을 추가했다.
- Dashboard 문서 drawer에서 QA/Test Result Markdown, 이미지 증적, 로그 링크를 더 직접적으로 확인할 수 있게 했다.

### Changed

- Gate 4 기본 흐름을 QA 실행/증적 수집(`qa-execution`)과 승인된 결함 수정(`qa-fix-loop`)으로 분리했다.
- `run-new --skill qa-execution`이 worker Run으로 생성되도록 Core/Adapter Run 입력 계약과 preflight 기준을 보강했다.
- `impl`/Gate 4 작업은 `workflow.integration_branch` 통합 브랜치에서 실행하도록 Core/Adapter 문서와 `wave-start`/`run-exec` guard를 보강했다.
- Gate 4 `QA-000`이 만든 QA workspace/worktree를 `QA-001`~`QA-003`이 계속 재사용하도록 Run 계약, skill, preflight 안내를 보강했다.
- Worker dependency cache, Node/Playwright self-check, QA workspace 실행 경계를 Run 입력 계약과 worker 프롬프트에 반영했다.

### Removed

- 별도 `QaDocView`를 제거하고 일반 문서 drawer에서 QA 문서와 evidence 링크를 표시하도록 정리했다.

### Verification

- `python -m py_compile vulcan.py`
- `git diff --check`
- 임시 프로젝트 dry-run으로 `QA-000`은 QA workspace 생성 모드가 되고, `QA-001`은 기록된 `QA-000` workspace가 없으면 차단되는 것을 확인했다.

## 0.2.3 - 2026-05-24

`0.2.3`은 worker 실행, Program Design 계약 준수 검증, Gate 4 QA 증적 가시성을 보강한 패치 릴리즈다. `0.2.2`의 Gate/Run 계약을 유지하면서 worker가 구현한 코드가 설계한 interface/class/public method 구조를 따르는지 확인하고, 대시보드에서 독립검수와 QA 로그를 더 직접적으로 확인할 수 있게 했다.

### Added

- `vulcan.py review-request` 명령 추가: Gate 산출물을 별도 세션 또는 detached worktree에서 독립 검수하기 위한 review request/result 파일과 Run 초안을 생성한다.
- `vulcan.py review-run` 명령 추가: 생성된 Independent Review 요청을 `codex exec`로 실행하고 JSONL 로그, 마지막 응답, result 변경 여부를 Run 증적으로 남긴다.
- `vulcan.py check-contract` 명령 추가: Program Design의 Interface/Public Method Contract 표를 읽어 Python/Java 파일의 interface/class, 구현체 class, public method 존재 여부를 확인한다.
- `vulcan.config.json` 초기 생성 추가: 독립 검수 runner, trigger Gate, worktree 사용 여부를 프로젝트별로 명시한다.
- 독립 검수 모델/추론 강도 기준 추가: Gate 2/Gate 4 검수는 `gpt-5.5` + `high`를 권장하고, `review-run --model ... --reasoning-effort ...`로 실행 단위 override할 수 있다.
- 독립 검수 기본값 변경: 새 프로젝트는 `independent_enabled: true`로 생성되며, Gate 2/Gate 4 종료 전 독립 검수를 기본 권장 절차로 둔다. 단, `review-run`은 자동 실행하지 않는다.
- Gate 2 독립 검수의 상류 정합성 기준 추가: Phase 0, Gate 1, Gate 2 순서로 목표/제약/가정, REQ/NREQ/AC, 범위 drift, 미해결 DEC/ISSUE, 설계 내부 정합성을 별도 판정한다.
- `docs/core/INDEPENDENT_REVIEW_PROCESS.md`와 Codex `independent-review` skill 추가.
- 혼동을 줄이기 위해 이전 호환 경로를 제거하고 `review-request`, `review-run`, `independent_*`만 표준으로 유지한다.
- Dashboard 산출물 목록에 `docs/reviews/` 독립검수 문서와 QA log evidence 표시를 추가했다.
- Agent 패널의 worker activity drawer와 runner 상태 표시를 보강하고, Agy/Gemini 로그 이벤트를 더 구체적인 진행 상태로 변환한다.

### Changed

- Build Wave와 Worker Run의 의미를 분리했다. Wave는 통합/검증 배치이고, 실제 작업지시서는 Build Wave Run으로 정의한다.
- backend/frontend처럼 작업지시서가 달라지는 범위는 같은 Wave 내부 병렬 실행이 아니라 별도 Build Wave Run/Wave로 순차 실행하도록 정리했다.
- Program Design `Public Method Contract` 템플릿에 `IF-ID` 컬럼을 추가해 interface와 public method의 부모-자식 관계를 명확히 했다.
- Gate 4 Test Result 템플릿에 `check-contract` 결과를 설계 계약 준수 검증으로 기록하는 기준을 추가했다.
- Worker dependency cache와 worktree npm/Playwright 검증 경계를 문서와 실행 기록에 반영했다.
- 독립 검수 runner가 result 파일을 작성해야 하는 흐름에서는 `read-only` sandbox를 차단하도록 정리했다.

### Verification

- `python -m py_compile vulcan.py`
- `npm test -- --runTestsByPath src/__tests__/components/DocList.test.tsx src/__tests__/api/session-docs-commits.test.ts src/__tests__/lib/qa-doc.test.ts`
- `npm run build` in `dashboard/`

## 0.2.2 - 2026-05-18

`0.2.2`는 Codex와 Claude 양쪽 런타임의 Gate 운영 규칙, Run 계약, UI 증적, 검증 명령 기록 기준을 같은 수준으로 맞춘 패치 릴리즈다.

### Added

- Gate 완료 후 산출물 요약, 미해결 항목, 다음 Gate 제안, 사용자 승인 질문을 남기고 대기하는 Gate exit policy.
- Run 입력 계약의 `source_documents.read_first`, `working_documents`, `reference_on_demand` 3-tier 구조.
- Gate 2 설계 순서(`G2-01`~`G2-10`)와 SW Architecture 반복 보강 기준.
- UIREF/ui-baseline 기반 UI Implementation Contract와 상태/시나리오 단위 UI 증적 기준.
- 검증 명령의 cwd, OS별 명령, 성공 기준, exit code, 로그/증적 경로, Not Run/Skipped 기록 기준.

### Changed

- Codex/GPT adapter와 Claude adapter의 Gate Prompt, Run Input/Output Contract, persona/skill 지침을 정렬.
- 개발표준, 테스트케이스, 테스트결과서 템플릿이 명령 실행 기준과 증적 기준을 더 구체적으로 요구하도록 보강.
- `gate-start`와 Run 생성 흐름이 Gate 작업 시작 전 Run 초안을 기준으로 움직이도록 정리.
- Dashboard와 문서 트리가 초기 프로젝트/화면 기준 산출물을 더 명확하게 보여주도록 보강.

### Verification

- `python -m py_compile vulcan.py`
- 임시 프로젝트 `init`으로 신규 템플릿 주입 확인
- Dashboard 테스트 실행
- PR #5 검토 및 merge 확인

## 0.2.1 - 2026-05-16

`0.2.1`은 `0.2.0` 이후 Gate 2 개발표준과 구현/QA 검증 기준을 보강한 패치 릴리즈다.

### Added

- `TECH_STACK_BASELINES.md` 추가: Spring Boot, Spring Security, React, Next.js, Vue.js, FastAPI 기술스택별 코딩/주석/테스트 기본 규칙.
- Spring Boot MVC, base package, feature-first package, JPA Entity/DTO 분리, transaction, repository/query 기준 추가.
- `REFACTORING_PROCESS.md` 추가: 리팩토링을 `DEBT/FIND/CR`로 분류하고 문서 영향, 테스트, 추적성을 기록하는 기준.

### Changed

- 개발표준정의서 템플릿에 기술스택 베이스라인, Spring Boot MVC/JPA 필수 확정 항목, 필수 검증 명령 표를 추가.
- Test Result, Build Wave, Traceability, Agent Run 규칙이 필수 검증 명령 실행 결과를 Run/Test Result에 남기도록 정리.
- README를 랜딩형으로 정리하고 Getting Started, Concepts, Upgrade/Dashboard, Roadmap 문서로 분리.
- Claude 런타임 템플릿이 기술스택 결정 시 `TECH_STACK_BASELINES.md`, 리팩토링 시 `REFACTORING_PROCESS.md`를 상황별로 참조하도록 보강.

### Verification

- `python -m py_compile vulcan.py`
- 임시 프로젝트 `init`으로 신규 Core 문서와 `AGENTS.md` 주입 확인
- `git diff --check`

## 0.2.0 - 2026-05-16

`0.2.0`은 Vulcan-Anvil Ex를 Codex 중심의 초기 골격에서 Codex와 Claude 양쪽 런타임이 실제 Gate 기반 프로젝트를 진행할 수 있는 수준으로 확장한 릴리즈다.

### Added

- Codex/GPT와 Claude adapter 문서 및 템플릿 정합성 강화.
- SW Architecture 산출물 템플릿과 Gate 2 설계 검증 기준 추가.
- 논리/물리 ERD의 DBML 원본 템플릿과 `docs/artifacts/02-design/data/erd/` 구조 추가.
- API 정의서, 보안가이드, 개발표준, 변경요청 상세서, 릴리즈 승인서 흐름 정리.
- Build Wave 기반 구현 계획, Wave 시작/완료, session 동기화 규칙 추가.
- Dashboard `LayoutA2` 추가: compact Gate 요약, 구현/Wave 진행률, 최근 Run/커밋, 통계/커밋 탭.
- 작업용 Markdown 산출물과 제출용 DOCX/XLSX/HWPX 문서의 관계를 정의하는 제출 문서 전략 추가.

### Changed

- 변경관리는 rollback 대신 승인된 CR의 필요한 Gate 진행과 Run 기록으로 처리하도록 정리.
- Dashboard 문서 목록을 1-depth 평면 표시에서 계층형 산출물 트리로 개선.
- 독립 `06-security` 산출물 버킷 대신 Gate 2 설계 하위 `security` 산출물로 정리.
- README를 `0.2.0` 기준 흐름, Dashboard, 다음 초점에 맞게 갱신.

### Verification

- `npm test -- LayoutToggle.test.tsx LayoutSwitch.test.tsx useLayoutTemplate.test.tsx DocList.test.tsx --runInBand`
- `python -m py_compile vulcan.py`

## 0.1.0 - 2026-05-11

- Vulcan-Anvil Ex 초기 Core, template, adapter, dashboard 실험 구조 정리.
- Phase 0, Gate, Run, Traceability, Backlog 기반의 기본 개발 흐름 정의.
