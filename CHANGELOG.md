# Changelog

## Unreleased

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
