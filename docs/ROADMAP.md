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
- `branch-start impl`, `branch-status`, `run-exec`, `agent-run --mode work` 기반 worker 실행
- worker progress watchdog과 hard timeout cap 기반 장시간 실행 관제
- Codex runner 역할별 model/effort 정책과 실행 기록
- `init --profile`과 `profile-status` 기반 Delivery Profile 선택/확인
- `BW-000 implementation-scaffold`를 통한 구현 전 빌드 가능한 skeleton 생성 기준
- Program Design 기반 `check-contract` 1차 검사(Python/Java class/interface/public method 존재 확인)
- Worker dependency cache와 worktree 실행 경계
- Gate 4 `QA-000`~`QA-003` staged QA 실행과 QA workspace 재사용 기준
- Gate 4 테스트 결과서를 실제 실행 상태 원본으로 사용하고, 요구사항추적표에 최종 검증 상태를 반영하는 기준
- Gate 4 QA 로그/독립검수/증적 문서 대시보드 표시
- 요구사항추적표 기반 `trace-context` CLI와 Dashboard Trace Explorer
- Gate 5 `release-pr` dry-run/body/branch guard
- fixture 기반 회귀 smoke harness
- 샘플 프로젝트 로그 기반 성능/병렬화 병목 분석 초안
- Upgrade와 Dashboard 운영 흐름

아직 제품화된 안정 버전은 아니며, 실제 프로젝트 적용 결과에 따라 문서 체계와 CLI 명령은 계속 조정될 수 있습니다.

릴리즈별 변경사항은 `CHANGELOG.md`를 기준으로 확인합니다.

## 다음 초점

`0.4.x`에서는 기능을 무작정 늘리기보다, 실제 프로젝트에서 반복 검증 가능한 운영 체계를 단단하게 만드는 데 집중합니다.

### 실행 순서

현재 우선순위는 다음 순서로 본다.

1. **샘플 프로젝트 기준 0.4.x 회귀 재검증**
   - 새 `v0.4.x` 기준으로 sample 프로젝트를 다시 진행해 Run 품질, trace-context, Gate 4 QA, release-pr, worker watchdog 흐름을 실제 사용감으로 확인한다.
   - 발견한 회귀는 fixture smoke 또는 문서 규칙으로 흡수한다.
2. **Run 생성 품질 자동화**
   - `run-new --trace-seed`와 `wave-start --trace-seed`의 최소 연동은 들어갔다.
   - 다음 단계는 샘플 프로젝트에서 생성된 Run 초안의 `scope.writable`, `interface_contract`, `source_documents` 품질을 확인하고 보강한다.
3. **Performance & Parallelization 기준 수립**
   - `sample-ex-0530-1`의 Run, worker summary, git log를 기준으로 병목을 1차 분석했다.
   - 샘플 기준 worker 실행 합계는 약 96.8분이며, 그중 Gate 4 QA와 QA-Fix가 약 73분을 차지했다.
   - 다음 단계는 `perf-report`류 CLI로 Gate별 wall-clock, worker duration, QA-Fix 왕복, timeout/watchdog 이벤트를 자동 산출하는 것이다.
   - Codex runner는 역할별 model/effort 정책을 먼저 심고, 실제 Run 기록으로 효과를 관찰한다.
   - 상세 기준은 `docs/reference/PERFORMANCE-AND-PARALLELIZATION-STRATEGY.md`를 따른다.
4. **Gate 4 QA 실사용 안정화**
   - QA worker가 테스트 실행자와 수정자 역할을 섞지 않는지 샘플 프로젝트로 반복 확인한다.
   - 실패 보고가 실제 사용자 판단에 충분한지 보고서/대시보드 관점에서 다듬는다.
5. **회귀 검증 하네스 확장**
   - 새 기능이 추가될 때마다 fixture smoke에 고정 입력/고정 결과 검증을 붙인다.
   - trace-context, release-pr, QA workspace 같은 흐름은 이미 최소 검증이 있으므로 샘플에서 나온 실제 회귀를 우선 추가한다.
6. **Dashboard Trace Explorer 후속 polish**
   - `0.4.0`에서 문서 Drawer의 Trace 버튼, `depth 1` 직접 edge 그래프, ID 제목 표시, 관련 목록 MVP는 완료했다.
   - 다음 단계는 실제 샘플 사용 후 ID 검색, upstream/downstream 전환, 그래프 복잡도 제어, Run 입력 후보 복사 UX가 필요한지 판단한다.
7. **PR 교차검증 자동화와 Dispatcher**
   - `run-exec`, `agent-run`, release-pr, QA 흐름이 충분히 안정된 뒤 자동 큐와 PR 교차검증을 검토한다.

### P0. 회귀 검증 하네스

기본 안전망 역할을 한다. 최소 하네스는 이미 존재하므로, 앞으로는 새 기능을 만들 때마다 회귀 케이스를 추가하는 방식으로 확장한다.

- 최소 샘플 프로젝트를 `init -> Phase 0 -> Gate 1 -> Gate 2 -> Gate 3 -> impl -> Gate 4`까지 반복 검증하는 시나리오를 만든다.
- 구현 단계에서 `branch-start impl`, `BW-000 implementation-scaffold`, `Build Wave`, `agent-run --mode work`, `run-preflight`, `run-integrate`가 기대대로 연결되는지 확인한다.
- Gate 4에서 `QA-000` workspace 준비, `QA-001` 명령 검증, `QA-002` UI/E2E 증적, `QA-003` 결과 정리가 실제로 분리되는지 확인한다.
- Gate 3 테스트케이스는 계획 상태로 유지하고, Gate 4 테스트 결과서와 요구사항추적표가 실제 Pass/Fail/Not Run 상태를 담당하는지 확인한다.
- 에이전트가 직접 구현, 직접 QA 수정, Gate 승인 선행, session 통계 누락 같은 회귀를 만들지 않는지 검사한다.

현재 최소 smoke harness는 `scripts/regression/run_audit_smoke.py`에 있다.
이 스크립트는 실제 AI runner나 frontend/backend dependency 설치 없이 `init`, 핵심 check 명령, Gate 차단, Run 생성/검사, preflight 차단을 빠르게 확인한다.
완료된 문서 세트를 사용하는 fixture smoke harness는 `scripts/regression/run_fixture_smoke.py`에 있으며, 첫 fixture는 `scripts/regression/fixtures/simple-hello-audit/`이다.
fixture smoke는 QA-001~QA-003이 QA-000의 QA workspace 기록 없이 실행되지 않도록 `run-preflight` 차단 회귀 케이스도 포함한다.
또한 `trace-context` 고정 seed의 YAML/JSON 결과와 `release-pr` dry-run body, 없는 base 브랜치, 잘못된 현재 브랜치, dirty worktree 차단을 함께 검증한다.

하네스 fixture는 새로 사람이 작성하지 않고, 기존 샘플 프로젝트에서 완결된 산출물 문서 세트를 추출해 정규화하는 방향을 우선 검토한다.
상세 기준은 `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md`를 따른다.

### P1. Run 품질 게이트 강화

`0.4.x`에서 최소 CLI와 smoke 검증, `run-new`/`wave-start` trace seed 연동은 들어갔다.
다음 단계는 worker에게 넘기는 Run 문서 초안 품질을 생성 시점부터 더 안정화하는 것이다.

- `run-check`: 형식과 완료 보고 기준 검사
- `run-preflight`: worker에게 넘겨도 되는 작업지시서인지 검사
- `check-contract`: Program Design의 class/interface/public method 계약과 코드 구조 대조
- `trace-context`: 요구사항추적표를 그래프 원장으로 사용해 Run의 `related_ids`, `target_contracts`, `source_documents`를 추천한다.

Run 입력 ID는 agent가 여러 문서를 뒤져 수동으로 긁어넣기보다 traceability graph에서 파생하는 방향을 검토한다.
상세 구상은 `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md`를 기준으로 한다.

다음 구현 후보:

- `run-new`/`wave-start --trace-seed`가 만든 초안에서 `scope.writable`과 `interface_contract`를 더 잘 좁히는 보조 규칙을 추가한다.
- edge type과 status 필터를 Run 작성 규칙에 더 직접적으로 연결한다.
- fixture smoke에 샘플 프로젝트에서 발견한 실제 trace-context 회귀 케이스를 추가한다.
- 샘플 프로젝트에서 `--trace-seed` UX를 확인한 뒤 기본 추천 여부를 판단한다.
- PoC profile의 Run 입력 문서는 `docs/reference/POC-RUN-COMPACT-STRATEGY.md`에 따라 compact preset을 우선 적용한다.

### P1. Gate 4 QA 안정화

Run 품질 게이트 다음에 진행할 실전 리스크 영역이다.

- `QA-000`이 integration branch 작업공간을 QA workspace로 기록하고 `QA-001`~`QA-003`이 재사용하는 흐름을 더 강하게 검증한다.
- `run-preflight`와 fixture smoke에서 QA-000 workspace 기록이 없는 후속 QA Run을 차단한다.
- QA worker가 테스트 실행자 역할과 수정자 역할을 섞지 않게 한다.
- `qa-fix-loop`는 사용자 또는 Orchestrator 판단 후 별도 Run으로만 시작한다.
- `qa-execution` Run이 실패를 발견했을 때 즉시 수정하지 않고 원인, 재현 명령, 로그, 영향 ID, FIND/CR/ISSUE 후보를 남기는지 검사한다.
- QA 결과서와 Finding 문서가 로그, 이미지, trace, command result를 Dashboard에서 확인할 수 있게 유지한다.

### P1. Performance & Parallelization

`audit` profile은 산출물, 추적성, 검수, 증적을 남기기 때문에 단순 구현형 coding보다 느린 것이 정상이다.
다만 샘플 프로젝트 기준으로 병목을 측정하고, 안전하게 줄일 수 있는 시간을 찾아야 한다.

`sample-ex-0530-1` 기준 1차 분석은 `docs/reference/PERFORMANCE-AND-PARALLELIZATION-STRATEGY.md`에 정리했다.

우선순위는 다음과 같다.

- `perf-report`류 CLI로 Gate별 wall-clock, Run별 worker duration, QA-Fix 왕복 횟수, timeout/watchdog 이벤트를 자동 산출한다.
- Codex model/effort routing 결과를 Run Execution Record와 summary에 남기고, role별 duration과 실패 경향을 축적한다.
- QA Test Result에서 Traceability Matrix 상태/증적 후보를 자동 생성해 Gate 4 정합성 정리 시간을 줄인다.
- `run-new`/`wave-start --trace-seed`가 만든 초안의 `scope.writable`, `interface_contract`, `source_documents` 품질을 더 구체적으로 진단한다.
- 병렬화는 review Run, 독립검수, QA command group, UI viewport 증적 순서로 제한적으로 검토한다.
- 구현 병렬화는 API/DTO/interface contract와 merge 전략이 충분히 안정된 뒤 검토한다.

Dashboard 성능 차트는 먼저 CLI 산출이 안정된 뒤 붙인다.

### P2. Delivery Profile 구체화

프로젝트 성격에 따라 문서 깊이와 Gate 강도를 조절합니다.

- Audit/SI Profile: 감리, 인수인계, 장기 유지보수 기준
- Solution/Product Profile: 제품 로드맵, 릴리즈, 품질 기준 중심
- PoC Profile: 빠른 검증과 핵심 리스크 확인 중심
- Profile은 결과물의 품질 등급이 아니라 문서 깊이, 증적 밀도, 독립검수 빈도, 변경관리 형식의 차이다.

현재는 `init --profile audit|solution|poc`와 `profile-status`로 선택 Profile과 `profile_rules`를 기록/확인하는 MVP가 들어갔다.
PoC Profile은 `run-new`/`gate-start`에서 가설, 성공 기준, smoke/demo 검증, 제품화 전환 보강 항목 중심의 얇은 Run 입력 계약을 생성한다.
`0.4.4`부터 PoC Profile은 `run-new`/`wave-start`에서 명시 `--trace-depth`가 없으면 depth 1을 기본값으로 사용하고, `source_documents.reference_on_demand`를 직접 관련 문서 중심으로 제한한다.
상세 기준은 `docs/reference/POC-RUN-COMPACT-STRATEGY.md`를 따른다.
다음 단계는 `solution`용 Run preset과 `run-check`, `run-preflight`, `check-trace`, Dashboard 표시를 Profile별 엄격도와 연결하는 것이다.

### P2. 제출용 문서 생성

감리 제출이나 대외 공유를 위해 Markdown 원천 문서를 제출본으로 합성하는 흐름을 설계합니다.

- DOCX/XLSX/HWPX 생성 전략
- Mermaid 다이어그램 이미지화 또는 읽을 수 있는 코드블록 처리
- 원천 문서 버전과 제출본 생성 commit 기록
- 민감자료 원문 유출 방지

### P3. Dashboard 관제성 개선

Dashboard는 기능 수보다 사용자가 판단해야 할 신호를 잘 보여주는 방향으로 발전한다.
Trace Explorer MVP는 `0.4.0`에서 문서 Drawer 안에 들어갔다. 다음 단계는 샘플 프로젝트 사용 결과를 보고 탐색성과 복잡도 제어가 실제로 필요한 만큼만 보강하는 것이다.

- 현재 Gate에서 다음에 해야 할 일
- 승인 대기와 차단 상태
- QA workspace와 최근 QA 실패 원인
- Run/Review/Worker 실행 로그와 증적
- Worker watchdog 상태(active/quiet/stalled), 마지막 진척 시각, timeout reason
- Gate별 소요시간, Run별 worker duration, QA-Fix 왕복 횟수
- 추적성 drill-down과 ID 기반 Trace Context
- Trace Explorer의 ID 검색, upstream/downstream 전환, 그래프 복잡도 제어
- 감리 제출 패키지 준비율
- Git log 기반 날짜별 진행 이력 요약

날짜별 진행 이력은 새 통계 저장소를 만들기보다 Git commit 날짜와 메시지를 파생해 보여주는 방향을 우선 검토한다.
상세 구상은 `docs/reference/GIT-LOG-PROGRESS-HISTORY.md`를 기준으로 한다.

### P3. Multi-Agent Dispatcher

`run-exec`와 `agent-run` 기반 실행이 안정된 뒤, 자동 큐/dispatcher를 검토합니다.

- Ready 상태 Run 자동 실행
- worker lock과 writable scope 충돌 방지
- fan-in review
- PR cross validation
- review-import/watch 확장

외부 agent runtime backend는 현재 `subprocess` 기반 실행을 기본으로 유지한다.
Google AX 같은 event log/resume/trace 지향 runtime은 즉시 도입하지 않고, 장기 실험 후보로만 추적한다.
상세 기준은 `docs/reference/AGENT-RUNTIME-BACKEND-CANDIDATES.md`를 따른다.

## Delivery Profile 방향

Vulcan-Anvil Ex는 모든 프로젝트에 같은 무게의 절차를 강제하지 않는 방향으로 발전합니다.

| Profile | 목적 | 문서/Gate 강도 |
| --- | --- | --- |
| Audit/SI | 감리, 인수인계, 장기 유지보수 대응 | 가장 강함 |
| Solution/Product | 제품 로드맵, 릴리즈, 품질 기준 중심 | 중간 |
| PoC | 빠른 가능성 검증 | 낮음 |
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
| `docs/core/CODEX_MODEL_POLICY.md` | Codex model/effort 정책 | Codex runner의 역할별 모델 선택, 실행 기록, 성능 측정 기준 |
| `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md` | 회귀 하네스 fixture 전략 | 기존 샘플 프로젝트 문서를 정규화해 테스트 입력으로 사용하는 방향 |
| `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md` | 추적성 그래프 전략 | 추적표를 그래프 원장으로 사용해 Run 입력과 Dashboard ID 탐색을 자동 추천하는 방향 |
| `docs/reference/PERFORMANCE-AND-PARALLELIZATION-STRATEGY.md` | 성능/병렬화 전략 | 샘플 프로젝트 로그 기준 병목 분석과 perf-report, QA 정합성 자동화, 제한적 병렬화 방향 |
| `docs/reference/EX-DIRECTION-INVESTMENT-REVIEW.md` | Ex 방향성/투자 판단 기준 | 빠른 AI coding tool이 아니라 AI coding governance framework로 투자할 조건과 축소 신호를 정리 |
| `docs/reference/CODEX-REPO-LOCAL-SKILL-STRATEGY.md` | Codex repo-local skill 전략 | 전역 skill을 건드리지 않고 `.agents/skills`로 Vulcan 절차 카드를 제공하는 기준 |
| `docs/reference/CODEX-CUSTOM-AGENT-STRATEGY.md` | Codex custom agent 전략 | `.codex/agents`로 메인 Orchestrator의 읽기 중심 보조 에이전트를 정의하는 기준 |
| `docs/reference/GIT-LOG-PROGRESS-HISTORY.md` | 날짜별 진행 이력 구상 | 별도 통계 저장소 없이 Git log 기반으로 파생 |
| `docs/reference/SESSION-COORDINATION-IDEAL.md` | 세션 협업 이상형 | 실시간 통신은 Core 전제 조건 아님 |
| `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md` | 제출용 문서 생성 전략 | DOCX/XLSX/HWPX 기능 구현 전 전략 기준 |
| `docs/reference/AGENT-RUNTIME-BACKEND-CANDIDATES.md` | 외부 agent runtime backend 후보 | 기본은 subprocess, AX 등은 장기 실험 후보 |
