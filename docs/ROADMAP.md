# Roadmap

이 문서는 Vulcan-Anvil Ex의 현재 상태와 다음 초점을 정리하는 기준 문서입니다.

다른 아이디어 문서나 오래된 인수인계 문서가 있더라도, 현재 우선순위는 이 문서를 먼저 기준으로 봅니다.

## 현재 상태

**Experimental - v0.3.0**

`0.3.0`은 Codex, Claude, Antigravity/Gemini runner를 실제 프로젝트 검수/구현/QA 흐름에 더 안전하게 연결하기 위해 audit workflow 브랜치 경계, worker 실행, staged Gate 4 QA, QA workspace 재사용, Program Design 계약 검증, Dashboard 증적 가시성을 보강한 실험 버전입니다.

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
- `BW-000 implementation-scaffold`를 통한 구현 전 빌드 가능한 skeleton 생성 기준
- Program Design 기반 `check-contract` 1차 검사(Python/Java class/interface/public method 존재 확인)
- Worker dependency cache와 worktree 실행 경계
- Gate 4 `QA-000`~`QA-003` staged QA 실행과 QA workspace 재사용 기준
- Gate 4 QA 로그/독립검수/증적 문서 대시보드 표시
- Upgrade와 Dashboard 운영 흐름

아직 제품화된 안정 버전은 아니며, 실제 프로젝트 적용 결과에 따라 문서 체계와 CLI 명령은 계속 조정될 수 있습니다.

릴리즈별 변경사항은 `CHANGELOG.md`를 기준으로 확인합니다.

## 다음 초점

`0.3.0` 이후에는 기능을 무작정 늘리기보다, 실제 프로젝트에서 반복 검증 가능한 운영 체계를 단단하게 만드는 데 집중합니다.

### 실행 순서

현재 우선순위는 다음 순서로 본다.

1. **Run 품질 게이트 + trace-context MVP 1**
   - worker Run의 `related_ids`, `target_contracts`, `source_documents` 추천 품질을 먼저 높인다.
   - `python vulcan.py trace-context --id <ID> --depth 2 --emit yaml` 최소판을 만든다.
   - fixture smoke에 동일 seed가 동일 추천 결과를 내는 회귀 검사를 추가한다.
2. **Gate 4 QA 안정화**
   - QA worker가 테스트 실행자와 수정자 역할을 섞지 않게 한다.
   - 실패 시 원인, 재현 명령, 로그, 영향 ID, FIND/CR/ISSUE 후보를 남기고 즉시 수정하지 않도록 강화한다.
3. **회귀 검증 하네스 확장**
   - 새 기능이 추가될 때마다 fixture smoke에 고정 입력/고정 결과 검증을 붙인다.
   - trace-context, release-pr, QA workspace 같은 흐름을 하네스에 계속 편입한다.
   - 현재 fixture smoke는 trace-context YAML/JSON, QA workspace guard, release-pr dry-run/body/branch/dirty guard를 포함한다.
4. **Gate 5 release-pr 안정화**
   - `release-pr`는 PR 생성/갱신과 PR body 생성까지만 유지한다.
   - 자동 merge와 자동 PR 교차검증은 후속 단계로 둔다.
   - PR body는 `.vulcan/release/release-pr-body.md`에 생성하고, base/head 브랜치와 dirty worktree를 먼저 검사한다.
5. **Dashboard Trace Context**
   - CLI trace graph 기준이 안정된 뒤 Dashboard ID 클릭/검색 패널을 붙인다.
6. **PR 교차검증 자동화와 Dispatcher**
   - `run-exec`, `agent-run`, release-pr, QA 흐름이 안정된 뒤 자동 큐와 PR 교차검증을 검토한다.

### P0. 회귀 검증 하네스

기본 안전망 역할을 한다. 최소 하네스는 이미 존재하므로, 앞으로는 새 기능을 만들 때마다 회귀 케이스를 추가하는 방식으로 확장한다.

- 최소 샘플 프로젝트를 `init -> Phase 0 -> Gate 1 -> Gate 2 -> Gate 3 -> impl -> Gate 4`까지 반복 검증하는 시나리오를 만든다.
- 구현 단계에서 `branch-start impl`, `BW-000 implementation-scaffold`, `Build Wave`, `agent-run --mode work`, `run-preflight`, `run-integrate`가 기대대로 연결되는지 확인한다.
- Gate 4에서 `QA-000` workspace 준비, `QA-001` 명령 검증, `QA-002` UI/E2E 증적, `QA-003` 결과 정리가 실제로 분리되는지 확인한다.
- 에이전트가 직접 구현, 직접 QA 수정, Gate 승인 선행, session 통계 누락 같은 회귀를 만들지 않는지 검사한다.

현재 최소 smoke harness는 `scripts/regression/run_audit_smoke.py`에 있다.
이 스크립트는 실제 AI runner나 frontend/backend dependency 설치 없이 `init`, 핵심 check 명령, Gate 차단, Run 생성/검사, preflight 차단을 빠르게 확인한다.
완료된 문서 세트를 사용하는 fixture smoke harness는 `scripts/regression/run_fixture_smoke.py`에 있으며, 첫 fixture는 `scripts/regression/fixtures/simple-hello-audit/`이다.
fixture smoke는 QA-001~QA-003이 QA-000의 QA workspace 기록 없이 실행되지 않도록 `run-preflight` 차단 회귀 케이스도 포함한다.
또한 `trace-context` 고정 seed의 YAML/JSON 결과와 `release-pr` dry-run body, 없는 base 브랜치, 잘못된 현재 브랜치, dirty worktree 차단을 함께 검증한다.

하네스 fixture는 새로 사람이 작성하지 않고, 기존 샘플 프로젝트에서 완결된 산출물 문서 세트를 추출해 정규화하는 방향을 우선 검토한다.
상세 기준은 `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md`를 따른다.

### P1. Run 품질 게이트 강화

가장 먼저 진행할 실작업 영역이다.
worker에게 넘기는 Run 문서 품질을 더 안정화한다.

- `run-check`: 형식과 완료 보고 기준 검사
- `run-preflight`: worker에게 넘겨도 되는 작업지시서인지 검사
- `check-contract`: Program Design의 class/interface/public method 계약과 코드 구조 대조
- `trace-context`: 요구사항추적표를 그래프 원장으로 사용해 Run의 `related_ids`, `target_contracts`, `source_documents`를 추천한다.

Run 입력 ID는 agent가 여러 문서를 뒤져 수동으로 긁어넣기보다 traceability graph에서 파생하는 방향을 검토한다.
상세 구상은 `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md`를 기준으로 한다.

다음 구현 후보:

- `python vulcan.py trace-context --id REQ-001-01 --depth 2 --emit yaml` 1차 구현 안정화
- edge type과 status를 가진 최소 trace graph 파서
- fixture smoke에 trace-context 고정 출력 검증
- `run-new --trace-seed` 자동 주입은 그 다음 단계로 보류

### P1. Gate 4 QA 안정화

Run 품질 게이트 다음에 진행할 실전 리스크 영역이다.

- `QA-000`이 만든 QA workspace를 `QA-001`~`QA-003`이 재사용하는 흐름을 더 강하게 검증한다.
- `run-preflight`와 fixture smoke에서 QA-000 workspace 기록이 없는 후속 QA Run을 차단한다.
- QA worker가 테스트 실행자 역할과 수정자 역할을 섞지 않게 한다.
- `qa-fix-loop`는 사용자 또는 Orchestrator 판단 후 별도 Run으로만 시작한다.
- `qa-execution` Run이 실패를 발견했을 때 즉시 수정하지 않고 원인, 재현 명령, 로그, 영향 ID, FIND/CR/ISSUE 후보를 남기는지 검사한다.
- QA 결과서와 Finding 문서가 로그, 이미지, trace, command result를 Dashboard에서 확인할 수 있게 유지한다.

### P2. Delivery Profile 구체화

프로젝트 성격에 따라 문서 깊이와 Gate 강도를 조절합니다.

- Audit/SI Profile: 감리, 인수인계, 장기 유지보수 기준
- Solution/Product Profile: 제품 로드맵, 릴리즈, 품질 기준 중심
- PoC Profile: 빠른 검증과 핵심 리스크 확인 중심
- Lite Profile: 작은 내부 도구와 단기 자동화 중심

### P2. 제출용 문서 생성

감리 제출이나 대외 공유를 위해 Markdown 원천 문서를 제출본으로 합성하는 흐름을 설계합니다.

- DOCX/XLSX/HWPX 생성 전략
- Mermaid 다이어그램 이미지화 또는 읽을 수 있는 코드블록 처리
- 원천 문서 버전과 제출본 생성 commit 기록
- 민감자료 원문 유출 방지

### P3. Dashboard 관제성 개선

Dashboard는 기능 수보다 사용자가 판단해야 할 신호를 잘 보여주는 방향으로 발전한다.
trace-context CLI가 안정된 뒤 ID 클릭/검색 기반 Trace Context 패널을 붙인다.

- 현재 Gate에서 다음에 해야 할 일
- 승인 대기와 차단 상태
- QA workspace와 최근 QA 실패 원인
- Run/Review/Worker 실행 로그와 증적
- 추적성 drill-down과 ID 기반 Trace Context
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
| Lite | 소규모 내부 도구, 단기 자동화 | 가장 낮음 |

자세한 기준 초안은 `docs/core/DELIVERY_PROFILES.md`를 따릅니다. 아직 Dashboard/CLI의 전체 profile 전환 기능으로 완성된 상태는 아닙니다.

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
| `docs/core/DELIVERY_PROFILES.md` | Delivery Profile 기준 초안 | profile별 문서/Gate 강도 구상. 전체 CLI/Dashboard 연동은 향후 보강 |
| `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md` | 회귀 하네스 fixture 전략 | 기존 샘플 프로젝트 문서를 정규화해 테스트 입력으로 사용하는 방향 |
| `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md` | 추적성 그래프 전략 | 추적표를 그래프 원장으로 사용해 Run 입력과 Dashboard ID 탐색을 자동 추천하는 방향 |
| `docs/reference/GIT-LOG-PROGRESS-HISTORY.md` | 날짜별 진행 이력 구상 | 별도 통계 저장소 없이 Git log 기반으로 파생 |
| `docs/reference/SESSION-COORDINATION-IDEAL.md` | 세션 협업 이상형 | 실시간 통신은 Core 전제 조건 아님 |
| `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md` | 제출용 문서 생성 전략 | DOCX/XLSX/HWPX 기능 구현 전 전략 기준 |
| `docs/reference/AGENT-RUNTIME-BACKEND-CANDIDATES.md` | 외부 agent runtime backend 후보 | 기본은 subprocess, AX 등은 장기 실험 후보 |
