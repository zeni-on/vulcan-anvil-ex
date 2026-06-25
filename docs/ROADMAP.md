# Roadmap

이 문서는 Vulcan-Anvil Ex의 현재 상태와 다음 초점을 정리하는 기준 문서입니다.

다른 아이디어 문서나 오래된 인수인계 문서가 있더라도, 현재 우선순위는 이 문서를 먼저 기준으로 봅니다.

## 현재 상태

**Experimental - v0.4.x**

`0.4.x`는 Codex, Claude, Antigravity/Gemini runner를 실제 프로젝트 검수/구현/QA 흐름에 더 안전하게 연결하기 위해 audit workflow 브랜치 경계, worker 실행, staged Gate 4 QA, QA workspace 재사용, Program Design 계약 검증, trace-context 그래프, Dashboard 증적/추적 가시성을 보강하는 실험 라인입니다.

포함된 주요 기능은 다음과 같습니다.

- Phase 0 + 5-Gate 진행 흐름
- Codex/GPT adapter
- Claude adapter
- Dashboard A2
- SW Architecture 산출물
- API 정의서 산출물
- DBML 기반 논리/물리 ERD 초안
- 보안가이드 산출물
- Spring Boot, Spring Security, React, Next.js, Vue.js, FastAPI 기술스택 베이스라인 초안
- 리팩토링의 DEBT/FIND/CR 분류와 문서 영향 판단 기준
- 변경관리/릴리즈 산출물
- Build Wave 운영 규칙
- `workflow.integration_branch` 기반 구현 통합 브랜치 운영
- `branch-start impl`, `branch-status` 기반 구현 브랜치 운영과, 필요 시 선택하는 `run-exec`/`agent-run --mode work` 외부 CLI worker 실행
- worker progress watchdog과 hard timeout cap 기반 장시간 실행 관제
- subagent/thread/native branch agent 위임 결과를 `delegation_records`로 남기는 얇은 책임 추적 기준
- Codex runner 역할별 model/effort 정책과 실행 기록
- Codex runner 미지원 model alias compatibility fallback과 회귀 smoke
- `init --profile`과 `profile-status` 기반 Delivery Profile 선택/확인
- `BW-000 implementation-scaffold`를 통한 구현 전 빌드 가능한 skeleton 생성 기준
- Program Design 기반 `check-contract` 1차 검사(Python/Java class/interface/public method 존재 확인)
- Worker dependency cache와 worktree 실행 경계
- Gate 4 `QA-000`~`QA-003` staged QA 실행과 QA workspace 재사용 기준
- Gate 4 테스트 결과서를 실제 실행 상태 원본으로 사용하고, 요구사항추적표에 최종 검증 상태를 반영하는 기준
- Gate 전환 전 `prepare-transition` 통합 진단
- `check-trace` semantic diagnostics 보강
- 설계-코드 불일치 후보를 문서 자동 수정이 아니라 보고서로 남기는 `drift-report`
- Antigravity/Agy `Workspace: branch` native delegation과 `delegation_records.mode: agy-branch-agent` 기준 정렬
- Gate 4 QA 로그/독립검수/증적 문서 대시보드 표시
- 요구사항추적표 기반 `trace-context` CLI와 Dashboard Trace Explorer
- adapter별 Run 입력 문서 분리와 `docs/core/GATE_EXECUTION_CHECKLIST.md` 공통화
- Antigravity/Agy를 메인 Orchestrator로 사용할 때의 `GEMINI.md`, Gemini adapter, native subagent, `Workspace: branch` 활용 기준
- Gate 5 `release-pr` dry-run/body/branch guard
- fixture 기반 회귀 smoke harness
- `doctor` 환경 진단과 `doctor --json` 구조화 출력, Product fixture smoke, QA-000 `QA-000-doctor.json` 환경 증적 연결
- 샘플 프로젝트 로그 기반 성능/병렬화 병목 분석 초안
- PoC profile의 compact Run 완충과, 별도 PoC 템플릿 세트 설계 초안
- Upgrade와 Dashboard 운영 흐름
- 사용자용 profile 선택 가이드와 샘플/benchmark 요약 문서
- Dashboard 문서 코멘트와 `status.dashboard_comments` 기반 Orchestrator 가시성

아직 제품화된 안정 버전은 아니며, 실제 프로젝트 적용 결과에 따라 문서 체계와 CLI 명령은 계속 조정될 수 있습니다.

릴리즈별 변경사항은 `CHANGELOG.md`를 기준으로 확인합니다.

## 최근 완료

최근 안정화에서 완료된 항목이다. 다음 샘플/릴리즈 전에는 회귀 하네스가 이 기준을 지키는지 확인한다.

- Codex runner 미지원 model alias fallback을 `resolve_codex_model_effort()`에 고정하고, 실행 기록과 status/Dashboard에서 actual model과 fallback reason을 볼 수 있게 했다.
- Product completed fixture smoke에서 `python vulcan.py doctor --json` 구조와 기본 pass 조건을 검증한다.
- Gate 4 `QA-000` Run 입력 계약에 `python vulcan.py doctor --json` 실행과 `docs/artifacts/04-review/evidence/qa-000/QA-000-doctor.json` 증적 경로를 연결했다.
- simple hello audit fixture에 `QA-000-doctor.json`/`.log` 증적을 추가했고, `scripts/regression/run_fixture_smoke.py`가 QA-000 doctor 증적 계약 누락을 감지한다.
- QA-000 workspace가 `environment_blocked`이면 QA-001 후속 Run preflight와 실행 workspace 재사용 경로가 진행을 차단하도록 fixture smoke에 고정했다.
- 차단 메시지에는 QA-000 doctor JSON/evidence 확인, 제품 결함과 환경 차단 분리, ISSUE/environment_blocked 보류, 필요 시 qa-fix-loop 생성 안내가 포함된다.
- Run 상단 metadata와 `3. Run 입력 계약`의 `gate`/`run_type` 불일치는 `run-check`와 `run-preflight`가 차단하고, fixture smoke가 이 회귀를 고정한다.

## 다음 초점

`0.4.x`에서는 기능을 더 많이 넣기보다, 실제 샘플 프로젝트에서 반복 검증 가능한 운영 체계를 단단하게 만드는 데 집중한다.
세부 아이디어는 reference 문서로 넘기고, 이 문서는 "지금 무엇을 먼저 볼지"를 정하는 큐로 사용한다.

### Now: 0.4.x 안정화

지금 바로 반복 검증하거나 보강할 항목이다.

1. **샘플 발견 회귀의 fixture 고정**
   - 샘플 프로젝트를 매번 처음부터 재실행하는 것이 아니라, 이미 발견한 회귀를 `scripts/regression` fixture smoke로 옮긴다.
   - 공식 QA 로그 누락, Playwright 보조 report 오인, Config Hotfix scope 후보, native/Agy `delegation_records` 누락, Run 입력 계약 metadata 불일치는 fixture smoke에 고정했다.
   - 다음 고정 후보는 QA worker 수정 지시 오염처럼 실제 샘플에서 다시 관찰되는 회귀로 제한한다.
   - 새 샘플 end-to-end 재실행은 큰 프로세스 변경이나 릴리즈 전 확인이 필요할 때만 수행한다.
   - 회귀 하네스 기준은 `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md`를 따른다.

2. **Run/위임 품질 게이트 보강**
   - `run-check`, `run-preflight`, `trace-context`, `--trace-seed`, native 위임용 `delegation_records`의 MVP는 이미 들어갔다.
   - 남은 작업은 샘플에서 나온 실제 누락 사례를 기준으로 `scope.writable`, `interface_contract`, `source_documents`, `delegation_records` 진단을 더 정확하게 만드는 것이다.
   - 외부 CLI runner는 `_exec` 로그와 Run Execution Record를 유지하되, subagent/thread/Agy Workspace branch는 얇은 `delegation_records`를 기본 기록으로 정리한다.
   - 추적성 그래프 기준은 `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md`를 따른다.

3. **Gate 4 QA 안정화**
   - 신규 프로젝트 기본 `.gitignore`는 공식 QA 로그를 막지 않고 `playwright-report/`, `test-results/`를 보조 로컬 산출물로 제외한다.
   - 공식 증적은 `docs/artifacts/04-review/evidence/logs/*`와 `docs/artifacts/04-review/evidence/ui/*.png`에 둔다.
   - Audit/Product의 공식 UI Pass는 `@playwright/test`와 `npx playwright test` 실행 결과를 기준으로 한다. 커스텀 Playwright script는 PoC smoke/demo 또는 보조 증적으로만 쓴다.
   - QA-000은 `doctor --json` 환경 증적을 남긴다. `environment_blocked` 상태의 QA-000 workspace가 있으면 후속 QA-001/QA-002 진행은 차단된다.
   - 다음 보강은 실제 샘플에서 차단 후 사용자 협의 안내와 qa-fix-loop/ISSUE 후보 분기가 자연스럽게 보이는지 확인하는 것이다.
   - `run-integrate --dry-run`은 scope 밖 설정 변경을 Config Hotfix 후보로 분류하고, 자동 승인/자동 되돌림 대신 Orchestrator가 `accept`, `qa-fix-loop`, `CR`, `reject` 중 하나를 선택하게 안내한다.
   - QA worker가 테스트 실행자와 수정자 역할을 섞지 않게 하고, 수정은 승인된 `qa-fix-loop` 또는 Config Hotfix 후보로 분리한다.

4. **PoC 실험 기록과 Environment Readiness Track**
   - PoC profile은 "경량 audit"이 아니라 확인하려는 가설, 반복별 기능 변화, 실행 결과, 다음 판단을 남기는 실험 기록 중심으로 재정의한다.
   - `sample-ex-poc-record-0616-1` 재실행에서 `docs/poc` 3종만으로 Phase 0~Gate 4를 진행할 수 있고, Phase 0에서 구현/테스트 파일을 먼저 만들면 `status --check`가 차단하는 것을 확인했다.
   - 구현 단계에서 `BW-000`으로 처음 개발환경을 만들지 않고, Phase 0~Gate 3 동안 SA/AA 성격의 subagent가 Environment Readiness Track으로 병렬 준비할 수 있게 한다.
   - Environment Readiness Track은 폴더 구조, dependency, lint/build/test script, hello world/health check, build smoke까지만 허용하고 업무 요구사항 구현/Pass 확정은 금지한다.
   - 상세 설계는 `docs/reference/FAST-POC-AND-ENV-RUNWAY-STRATEGY.md`를 따른다.

5. **PoC template set 1차 검증**
   - PoC를 audit 템플릿의 느슨한 검사 모드로만 다루지 않고, 별도 `docs/templates/poc/` 산출물 세트로 분리하는 방향을 검증한다.
   - 1차 후보는 PoC 요구사항/가설, PoC 시스템 통합 설계, PoC 테스트/결과/판정의 3개 템플릿이다.
   - 1차 재실행 결과 현재 템플릿으로도 PoC는 가능하므로, 템플릿 대수정은 보류한다. 다음 검증은 여러 번 기능을 추가하는 반복형 PoC에서 `Fix Log / Experiment Iterations`가 충분히 복원 가능한지 확인한다.
   - 상세 전략은 `docs/reference/POC-PROFILE-TEMPLATE-SET-STRATEGY.md`를 따른다.

6. **사용자 온보딩과 샘플 증거 정리**
   - README 첫 화면에서 Ex를 "빠른 앱 빌더"가 아니라 AI-generated work Trust/Governance Layer로 설명한다.
   - `docs/WHICH_PROFILE_SHOULD_I_USE.md`로 PoC/Product/Audit 선택 기준을 분리한다.
   - `docs/EXAMPLES_AND_BENCHMARKS.md`로 샘플 소요 시간, 산출물, profile별 차이를 공개 요약한다.
   - 다음 단계는 fixture/metrics 기반으로 샘플 수치를 더 재현 가능하게 만드는 것이다.

7. **전환 진단 정리**
   - Gate 전환 판단은 `prepare-transition`을 기본으로 사용한다.
   - `check-trace`는 traceability 상세 디버깅과 회귀 검증용으로 남긴다.
   - placeholder, 빈 표, 잘못된 Run 입력 계약, thin delegation record 같은 산출물 완성도 문제는 `prepare-transition`/`run-check` 쪽으로 모은다.
   - Orchestrator가 직접 기억해야 하는 CLI 표면은 먼저 `status` 하나로 줄인다. `status --check`가 `prepare-transition` 진단을 요약하고, 원자 명령은 고급/호환 명령으로 유지한다. 상세 전략은 `docs/reference/ORCHESTRATOR-CLI-SURFACE-STRATEGY.md`를 따른다.

8. **Runtime harness UX 흡수**
   - 외부 runtime harness에서 command surface 단순화, durable progress state, verified completion loop, hooks, doctor/diagnostics 패턴을 참고한다.
   - Ex는 외부 runtime harness를 복제하거나 기본 dependency로 포함하지 않고, `delegation sidecar`, `execute` facade dry-run, worker completion state 분리, `doctor` 명령으로 흡수한다.
   - Codex role-based model fallback은 1차 구현되어 `gpt-5.3-codex` 같은 미지원 alias를 실행 전 `gpt-5.5`로 정규화하고, Dashboard/status에 actual model과 fallback reason을 표시한다.
   - 상세 정리는 `docs/reference/RUNTIME-HARNESS-LESSONS.md`를 따른다.

### Next: 0.5 후보

`0.4.x` 안정화 뒤 제품성이나 생산성을 키우는 항목이다.

1. **Spec-to-Scaffold MVP**
   - Gate 2 Program Design에서 class/component, public method, DTO/entity, test mapping을 읽어 skeleton 후보를 만든다.
   - 자동 반영이 아니라 `scaffold-plan`, `scaffold-generate --dry-run`, Orchestrator 확인 순서로 둔다.
   - 코드에서 설계로 역투영하는 기능은 자동 수정이 아니라 `drift-report` 후보로 남긴다.

2. **Performance & Parallelization**
   - `perf-report`류 CLI로 Gate별 wall-clock, Run별 worker duration, QA-Fix 왕복, timeout/watchdog 이벤트를 산출한다.
   - 병렬화는 review, 독립검수, QA command group, UI viewport 증적부터 제한적으로 검토한다.
   - 구현 병렬화는 API/DTO/interface contract와 merge 전략이 충분히 안정된 뒤 검토한다.
   - 상세 기준은 `docs/reference/PERFORMANCE-AND-PARALLELIZATION-STRATEGY.md`를 따른다.

3. **Delivery Profile 구체화**
   - Audit/SI, Product, PoC profile의 Run preset, 검사 엄격도, Dashboard 표시를 더 분명하게 나눈다.
   - Product profile은 OWASP/CWE 기반 보안 기준선과 프로젝트 단어사전/데이터 매핑을 기본으로 삼고, KISA/공공데이터 공통표준은 Audit 전환 gap으로 정리한다.
   - Product profile은 현재 문서 세트, Gate별 필수 산출물, trace 검사, `release-pr --dry-run` evidence 기준이 1차 구현되어 있다.
   - Product fixture smoke 기준은 `docs/reference/PRODUCT-FIXTURE-SMOKE-STRATEGY.md`에 고정했다. 다음 작업은 실제 Product 샘플 재실행으로 fixture가 놓치는 운영 마찰을 확인하는 것이다.
   - PoC compact Run 기준은 `docs/reference/POC-RUN-COMPACT-STRATEGY.md`를 따른다.
   - PoC 산출물 세트 분리 기준은 `docs/reference/POC-PROFILE-TEMPLATE-SET-STRATEGY.md`를 따른다.
   - Product 기준은 `docs/core/PRODUCT_PROFILE_BASELINE.md`를 따른다.

4. **Dashboard 증적/추적 polish**
   - Trace Explorer는 MVP가 들어갔으므로, 샘플 사용 결과를 보고 ID 검색, upstream/downstream 전환, 그래프 복잡도 제어를 보강한다.
   - QA evidence 확대 보기, UIREF와 screenshot side-by-side 비교는 실제 Gate 4 사용감 확인 뒤 진행한다.

5. **Orchestrator CLI facade**
   - `status` MVP부터 시작해 `branch-status`, `profile-status`, `prepare-transition` 진단을 한 화면으로 요약한다.
   - `transition check` 같은 유사 진단 명령은 만들지 않는다. 진단 표면은 `status --check`로 모은다.
   - `execute --dry-run` MVP는 Run 실행 전 `run-check`, `run-preflight`, sidecar 후보, scope, 검증 명령을 한 번에 확인하는 수준으로 들어갔다.
   - 이후 필요성이 검증되면 `plan`, 실제 `execute`, `transition`은 후보로 다시 검토한다.
   - 상세 설계는 `docs/reference/ORCHESTRATOR-CLI-SURFACE-STRATEGY.md`를 따른다.

6. **Delegation sidecar와 worker completion state**
   - native subagent/thread/Agy branch 진행 상태를 `.vulcan/delegations/*.json` sidecar로 읽어 Dashboard에 표시하는 MVP가 들어갔다.
   - worker 완료와 Orchestrator 검증 완료를 Dashboard와 Run 기록에서 분리한다.
   - `run-check`/`run-preflight`는 완료된 worker Run에 worker 완료 상태만 있고 Orchestrator 재검증 기록이 없으면 경고한다.
   - 외부 runtime harness에서 참고한 durable progress state와 verified completion 패턴은 `docs/reference/RUNTIME-HARNESS-LESSONS.md`를 따른다.

### Later: 장기 확장 후보

우선순위는 낮지만 방향성은 유지하는 항목이다.

- **Agent-aware output checker**: 테스트 ID 누락, 공식 로그 미추적, 완료 문서의 `TBD`, 부적절한 `N/A`, 얇은 `delegation_records` 같은 반복 실수를 가볍게 검사한다.
- **Multi-Agent Dispatcher / PR 교차검증**: Ready Run 자동 실행, worker lock, fan-in review, PR cross validation은 현재 실행 흐름이 더 안정된 뒤 검토한다.
- **제출용 문서 생성**: Markdown 원천 문서를 DOCX/XLSX/HWPX 제출본으로 합성하는 전략은 `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md`를 기준으로 한다.
- **Git log 기반 진행 이력**: 별도 통계 저장소를 만들기보다 Git commit 날짜와 메시지에서 파생하는 방향을 검토한다.
- **Canary deployment verification**: Gate 5 이후 preview/staging/canary 검증은 GitHub Actions, secret 관리, 외부 URL 보안 정책이 안정된 뒤 검토한다.
- **외부 runtime backend 후보**: Google AX 같은 event log/resume/trace 지향 runtime은 장기 실험 후보로만 추적한다.

### Parking Lot

현재는 하지 않는 항목이다.

- 파일 watcher 기반 Reactive Session Stream: 문서 임시 저장 중 불완전 상태를 읽거나 승인 전 통계가 완료처럼 보이는 위험이 있어 보류한다.
- 구현 산출물에서 설계 문서를 자동 덮어쓰기: 설계와 코드의 주종 관계가 뒤집힐 수 있으므로 `drift-report` 후보 생성까지만 허용한다.
- 대규모 병렬 구현 자동화: 계약/merge/검증 전략이 더 안정될 때까지 보류한다.

## Delivery Profile 방향

Vulcan-Anvil Ex는 모든 프로젝트에 같은 무게의 절차를 강제하지 않는 방향으로 발전합니다.

| Profile | 목적 | 문서/Gate 강도 |
| --- | --- | --- |
| Audit/SI | 감리, 인수인계, 장기 유지보수 대응 | 가장 강함 |
| Product | 제품 로드맵, 릴리즈, 품질 기준 중심 | 중간 |
| PoC | 기능/기술 가설 실험과 반복 기록 | 낮음 |
자세한 기준 초안은 `docs/core/DELIVERY_PROFILES.md`를 따릅니다.
현재 CLI는 `init --profile`과 `profile-status`를 제공하며, 검사 엄격도와 Dashboard 표시는 후속 단계에서 Profile Overlay와 연결합니다.

## 제출용 문서 전략

작업 중에는 Markdown 원천 문서를 나누어 관리합니다. 제출 시점에는 DOCX/XLSX/HWPX 템플릿과 생성 코드를 통해 필요한 내용을 합성하는 방향을 둡니다.

상세 전략은 `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md`를 기준으로 합니다. 아직 제출본 생성 기능으로 완성된 상태는 아니며, 구현 전 전략 문서로 관리합니다.

## 세션 협업 모델

세션 간 실시간 통신은 Core 전제 조건이 아닙니다.

대신 다음 파일을 공유 상태로 사용합니다.

- `session.json`
- `docs/runs/`
- 증적 파일
- 백로그 문서
- Git 커밋

이상적인 세션 협업 모델은 `docs/reference/SESSION-COORDINATION-IDEAL.md`에 정리되어 있습니다. 실시간 브로드캐스트나 watcher는 향후 확장 옵션입니다.

## 관련 문서의 상태

| 문서 | 현재 용도 | 비고 |
| --- | --- | --- |
| `docs/ROADMAP.md` | 현재 기준 로드맵 | 우선순위 판단 기준 |
| `docs/NEXT_SESSION_HANDOFF.md` | 다음 세션 시작용 요약 | 최신 상태로 유지 |
| `docs/ARTIFACT_TEMPLATE_ROADMAP.md` | 초기 산출물 템플릿 구상 | 참고 문서. 최신 우선순위는 이 문서가 아니라 `ROADMAP.md` |
| `docs/RUN_FIRST_MULTI_AGENT_DISPATCHER.md` | dispatcher 장기 구상 | 일부는 이미 구현됨. 자동 큐/PR 교차검증 검토 시 참고 |
| `docs/core/REFACTORING_PROCESS.md` | 리팩토링 분류 기준 초안 | DEBT/FIND/CR 판단과 문서 영향 분석 기준. 자동화는 향후 보강 |
| `docs/core/DELIVERY_PROFILES.md` | Delivery Profile 기준 | `init --profile`, `profile-status`, profile_rules 기반 Overlay. 검사 엄격도/Dashboard 연동은 후속 보강 |
| `docs/WHICH_PROFILE_SHOULD_I_USE.md` | 사용자용 Profile 선택 가이드 | PoC/Product/Audit을 처음 고르는 기준과 시작 메시지 예시 |
| `docs/EXAMPLES_AND_BENCHMARKS.md` | 샘플/benchmark 요약 | 샘플 실행 결과, profile별 산출물과 시간 차이를 사용자 관점으로 요약 |
| `docs/core/PRODUCT_PROFILE_BASELINE.md` | Product Profile 기준 | 제품/업무 앱 기본 레이어의 보안, 데이터, Gate, Audit 전환 gap 기준 |
| `docs/core/CODEX_MODEL_POLICY.md` | Codex model/effort 정책 | Codex runner의 역할별 모델 선택, 실행 기록, 성능 측정 기준 |
| `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md` | 회귀 하네스 fixture 전략 | 기존 샘플 프로젝트 문서를 정규화해 테스트 입력으로 사용하는 방향 |
| `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md` | 추적성 그래프 전략 | 추적표를 그래프 원장으로 사용해 Run 입력과 Dashboard ID 탐색을 자동 추천하는 방향 |
| `docs/reference/PERFORMANCE-AND-PARALLELIZATION-STRATEGY.md` | 성능/병렬화 전략 | 샘플 프로젝트 로그 기준 병목 분석과 perf-report, QA 정합성 자동화, 제한적 병렬화 방향 |
| `docs/reference/FAST-POC-AND-ENV-RUNWAY-STRATEGY.md` | PoC와 개발환경 runway 전략 | PoC 실험 기록, Environment Readiness Track, BW-000 재정의 방향 |
| `docs/reference/POC-PROFILE-TEMPLATE-SET-STRATEGY.md` | PoC 전용 템플릿 세트 전략 | PoC를 audit 템플릿 완충이 아니라 3개 통합 산출물 세트로 검증하는 방향 |
| `docs/reference/PRODUCT-FIXTURE-SMOKE-STRATEGY.md` | Product fixture smoke 전략 | Product profile 회귀 fixture와 실제 샘플 재실행의 합격 기준 |
| `docs/reference/EX-DIRECTION-INVESTMENT-REVIEW.md` | Ex 방향성/투자 판단 기준 | 빠른 AI coding tool이 아니라 AI coding governance framework로 투자할 조건과 축소 신호를 정리 |
| `docs/reference/CODEX-REPO-LOCAL-SKILL-STRATEGY.md` | Codex repo-local skill 전략 | 전역 skill을 건드리지 않고 `.agents/skills`로 Vulcan 절차 카드를 제공하는 기준 |
| `docs/reference/CODEX-CUSTOM-AGENT-STRATEGY.md` | Codex custom agent 전략 | `.codex/agents`로 메인 Orchestrator의 읽기 중심 보조 에이전트를 정의하는 기준 |
| `docs/reference/ORCHESTRATOR-CLI-SURFACE-STRATEGY.md` | Orchestrator CLI 표면 축소 전략 | 원자 명령은 유지하고 `status` MVP부터 운영 표면을 줄이는 방향 |
| `docs/reference/RUNTIME-HARNESS-LESSONS.md` | 외부 runtime harness 참고 기능 정리 | delegation sidecar, execute facade, verified completion, doctor, model routing 등 Ex 고도화 후보 |
| `docs/reference/GIT-LOG-PROGRESS-HISTORY.md` | 날짜별 진행 이력 구상 | 별도 통계 저장소 없이 Git log 기반으로 파생 |
| `docs/reference/SESSION-COORDINATION-IDEAL.md` | 세션 협업 이상형 | 실시간 통신은 Core 전제 조건 아님 |
| `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md` | 제출용 문서 생성 전략 | DOCX/XLSX/HWPX 기능 구현 전 전략 기준 |
| `docs/reference/AGENT-RUNTIME-BACKEND-CANDIDATES.md` | 외부 agent runtime backend 후보 | 기본은 subprocess, AX 등은 장기 실험 후보 |
