# Runtime Harness Lessons for Vulcan-Anvil Ex

> Status: draft v0.1  
> 작성일: 2026-06-24  
> 목적: 외부 runtime harness에서 Ex가 기능적으로 참고할 만한 항목을 정리하고, Ex의 고도화 후보로 변환한다.

## 1. 요약

외부 runtime harness는 Codex 안에서 project memory, planning, execution, verified completion을 제공하는 agent harness다.
외부 harness 공개 문서에서 관찰한 패턴으로는 `$init-deep`, `$ulw-plan`, `$start-work`, `$ulw-loop`를 전면에 두고, skills, hooks, model routing, diagnostics를 Codex에 설치하는 방식이다.

Ex와 외부 runtime harness는 경쟁 관계라기보다 층위가 다르다.

| 구분 | 외부 runtime harness | Vulcan-Anvil Ex |
| --- | --- | --- |
| 핵심 정체성 | Codex 실행 harness | AI 작업 결과를 회수하는 governance framework |
| 주 관심사 | 계획 실행, subagent, verified completion | Gate, 요구사항, 설계, 테스트, 증적, 승인, 추적성 |
| 주요 상태 | plan, durable progress state, harness state | `session.json`, Run, `delegation_records`, traceability, QA evidence |
| 강점 | 실행 표면이 단순하고 worker loop가 강함 | 산출물/추적성/승인/감사성이 강함 |
| Ex 관점 | 실행 backend 후보 또는 UX 참고 대상 | 상위 회수/검증/증적 레이어 유지 |

따라서 Ex는 외부 runtime harness를 그대로 복제하지 않는다.
대신 **실행성, 상태 가시성, 자동 preflight, verified completion UX**를 참고해 Ex의 native worker/subagent 흐름을 고도화한다.

## 2. 기능적으로 참고할 항목

### 2.1 Command Surface 단순화

외부 runtime harness는 사용자가 기억하는 명령을 `$init-deep`, `$ulw-plan`, `$start-work`, `$ulw-loop`처럼 몇 개의 강한 진입점으로 둔다.

Ex 적용 방향:

- 원자 명령은 유지한다.
- Orchestrator 일상 명령은 더 적게 만든다.
- `status`는 이미 MVP로 들어갔다.
- 다음 후보는 `plan`, `execute`다.
- `transition check` 같은 중복 진단 명령은 만들지 않는다. Gate 전환 진단은 `status --check`로 유지한다.

후보:

```text
python vulcan.py status
python vulcan.py plan --goal "TODO 앱 구현"
python vulcan.py execute --run-id RUN-001 --runner native
```

비목표:

- `init`, `upgrade`, `version`, `export`를 `project` 하위 명령으로 감싸지 않는다.
- 승인/전환을 자동으로 수행하는 all-in-one 명령은 만들지 않는다.

### 2.2 Durable Delegation State

외부 runtime harness의 durable progress state는 장시간 작업의 진행 상태를 durable state로 남기는 패턴이다.

Ex 문제:

- 현재 상태는 `session.json`, `docs/runs/*.md`, `_exec/*activity.json`, `_exec/*summary.json`, `delegation_records`로 흩어져 있다.
- external CLI runner는 `_exec` 로그가 있지만, native subagent/thread/Agy branch는 실시간 상태가 약하다.
- Dashboard는 완료 후 Run 문서의 `delegation_records`는 읽을 수 있지만, 실행 중 native 위임 상태는 Orchestrator가 별도 sidecar를 남기지 않으면 알기 어렵다.

Ex 적용 후보:

```text
.vulcan/delegations/RUN-014.json
```

권장 스키마 초안:

```json
{
  "run_id": "RUN-014",
  "mode": "codex-subagent",
  "delegate": "build",
  "status": "running",
  "started_at": "2026-06-24T10:00:00+09:00",
  "last_activity_at": "2026-06-24T10:03:00+09:00",
  "task": "BW-001 Todo API 구현",
  "scope": {
    "writable": ["backend/app/", "backend/tests/"]
  },
  "changed_files": [],
  "self_check": [],
  "orchestrator_verification": []
}
```

기대 효과:

- Dashboard가 native subagent/thread 상태를 외부 runner처럼 볼 수 있다.
- Run 문서 정규화 전에도 진행 상태를 확인할 수 있다.
- worker 완료와 Orchestrator 검증 완료를 분리해 표시할 수 있다.
- 장시간 작업 병목 분석에 도움이 된다.

주의:

- sidecar는 사실 기록이다. Gate 승인이나 테스트 Pass 확정이 아니다.
- Run 문서가 없는 짧은 PoC 작업에서는 필수로 강제하지 않는다.

### 2.3 Plan Before Work

외부 runtime harness의 `$ulw-plan`은 구현 전 의사결정과 계획을 분리한다.

Ex 적용 방향:

- Audit/Product에서는 기존 Run/Wave 계획을 유지한다.
- PoC/Product의 작은 작업은 긴 Run 문서보다 체크리스트형 plan을 허용한다.
- plan은 실행하지 않는다. 실행은 `execute` 후보나 Orchestrator 지시로 분리한다.

체크리스트형 plan 최소 구조:

```yaml
goal:
acceptance:
scope:
tasks:
verification:
handoff:
approval_required:
```

기대 효과:

- 작업지시서가 장황해지는 문제를 줄인다.
- subagent에게 줄 컨텍스트가 명확해진다.
- `run-drafter` 검토 대상도 더 작아진다.

### 2.4 Start Work / Execute Loop

외부 runtime harness의 `$start-work`는 계획을 실행하고 durable progress를 남긴다.

Ex 적용 후보:

```text
python vulcan.py execute --run-id RUN-014 --runner native --dry-run
python vulcan.py execute --run-id RUN-014 --runner native --apply
```

내부 흐름 후보:

1. `run-preflight <run-file>`
2. native subagent/thread/Agy branch 또는 external CLI runner 선택
3. `.vulcan/delegations/*.json` 시작 기록
4. worker 결과 수집
5. scope 변경 확인
6. self-check 또는 Run 지정 검증 명령 실행
7. `delegation_records` 정규화 후보 생성
8. `run-check`
9. Orchestrator 재검증 결과 보고

비목표:

- `execute`가 Gate 완료, session 갱신, release 가능 여부를 자동 확정하지 않는다.
- scope 밖 변경을 자동으로 되돌리지 않는다. Config Hotfix, QA Fix, CR, reject 후보로 분류한다.

### 2.5 Verified Completion 상태 분리

외부 runtime harness는 hopeful status update가 아니라 evidence-bound verified completion을 강조한다.

Ex 적용 방향:

- worker 완료와 Orchestrator 검증 완료를 Dashboard와 Run 기록에서 분리한다.
- "worker completed"는 후보 산출물 완료다.
- "verified"는 Orchestrator가 테스트/증적/trace를 확인한 뒤에만 사용한다.

상태 후보:

| 상태 | 의미 |
| --- | --- |
| `delegated` | worker/subagent/thread에 작업을 맡김 |
| `worker_running` | worker 실행 중 |
| `worker_completed` | worker가 결과를 반환함 |
| `orchestrator_verifying` | Orchestrator 재검증 중 |
| `verified` | 검증 통과 |
| `needs_review` | 결과는 있으나 검토/보정 필요 |
| `blocked` | 환경/계약/승인 차단 |

Dashboard 표시 후보:

```text
RUN-014 · Codex subagent · worker completed · verifying
RUN-014 · Codex subagent · verified
RUN-014 · Agy branch · needs review
```

### 2.6 Evidence Gate 정규화

외부 runtime harness의 verified loop는 evidence를 기준으로 완료를 판단한다.

Ex 적용 방향:

- Build Wave 완료 전 최소 evidence gate를 둔다.
- Gate 4 QA는 현재처럼 공식 QA 결과서와 로그/스크린샷을 원본으로 둔다.
- PoC는 smoke/demo evidence로 충분할 수 있다.

Build Wave 최소 gate 후보:

1. Run/plan reread
2. scope check
3. automated test 또는 build smoke
4. evidence/log attached
5. Orchestrator verification

PoC 최소 gate 후보:

1. smoke 실행
2. demo evidence 또는 실행 로그
3. 남은 판단/제약 기록

### 2.7 Parallel Explore Subagents

외부 runtime harness는 구현 전에 repository exploration을 subagent로 분산하는 패턴을 가진다.

Ex 적용 방향:

- 무조건 병렬화하지 않는다.
- 다음 상황에서만 보조 agent를 쓴다.

| 상황 | 후보 agent |
| --- | --- |
| 관련 ID/source document가 넓음 | `trace-scout` |
| Run 작업지시서 품질이 불안함 | `run-drafter` |
| 설계-코드 계약 정합성이 위험함 | `contract-reviewer` |
| QA 로그/증적 해석이 복잡함 | `qa-reader` |
| 기존 큰 repo를 처음 도입함 | future `codebase-scout` |

Dashboard에는 helper agent 결과를 "검토 보조 의견"으로 표시하되, 승인/Pass로 간주하지 않는다.

### 2.8 Specialist Skill 확장

외부 runtime harness는 specialized skills를 command layer 주변에 둔다.

Ex 후보 skill:

| Skill 후보 | 목적 |
| --- | --- |
| `vulcan-code-review` | 코드 품질, FIND 후보, 설계 위반 후보 |
| `vulcan-ui-evidence` | Playwright 캡처, UIREF 비교, screenshot evidence 정리 |
| `vulcan-contract-drift` | 설계-코드/API/DB surface 불일치 분석 |
| `vulcan-cleanup` | 과한 README/주석/AI 냄새 제거 후보 제안 |
| `vulcan-lsp-check` | 타입, 심볼, 참조, public API surface 검사 |

우선순위는 낮다.
먼저 `delegation sidecar`와 `execute facade`가 안정되어야 한다.

### 2.9 Hook / Lifecycle 자동화

외부 runtime harness는 hooks를 적극적으로 활용한다.

Ex 적용 후보:

| 시점 | 자동/반자동 작업 |
| --- | --- |
| worker 위임 전 | `run-preflight` |
| worker 시작 | `.vulcan/delegations/*.json` 생성 |
| worker 완료 | 변경 파일/scope 수집 |
| Run 완료 전 | `run-check` |
| Gate 전환 전 | `status --check` |
| Dashboard refresh | sidecar/activity 상태 읽기 |

주의:

- 자동 진단과 자동 차단은 좋다.
- 자동 승인과 자동 산출물 덮어쓰기는 위험하다.
- 설계 문서 자동 갱신은 여전히 `drift-report` 후보 생성까지만 허용한다.

### 2.10 Model Routing

외부 runtime harness는 task category별 model routing을 강조한다.

Ex 적용 방향:

- 정책은 두 층으로 둔다.
  - recommended model policy
  - actual available model fallback
- 모델이 계정/CLI에서 지원되지 않으면 실패가 아니라 fallback 후보를 출력해야 한다.

역할별 후보:

| 역할 | 기본 방향 |
| --- | --- |
| `trace-scout` | 빠른 모델 / medium |
| `run-drafter` | 중간 모델 / medium |
| `contract-reviewer` | 강한 모델 / high |
| `qa-reader` | 중간 모델 / medium |
| `build worker` | 작업 위험도에 따라 medium~high |

### 2.11 Doctor / Health Check

외부 runtime harness에는 diagnostics 성격이 있다.

Ex 후보:

```text
python vulcan.py doctor
```

확인 항목:

- Python/Node/Git 설치
- Dashboard dependency 상태
- Codex/Claude/Agy runner 감지
- Playwright browser cache
- Git branch/worktree 상태
- `.vulcan/comments` 접근 가능 여부
- `docs/core`, templates, profile overlay 누락
- `vulcan.config.json` workflow/runtime 설정 이상

`status`는 프로젝트 진행 상태이고, `doctor`는 로컬 실행 환경 건강검진이다.
두 명령은 역할이 다르다.

### 2.12 Existing Codebase Adoption

외부 runtime harness의 `$init-deep`은 큰 repo에 계층적 `AGENTS.md` context를 생성하는 패턴이다.

Ex 후보:

```text
python vulcan.py adopt-existing --profile product
python vulcan.py map-codebase
```

산출 후보:

- 폴더별 역할 요약
- 기존 API/DB/UI 목록
- 테스트 명령 후보
- 위험 영역
- Gate 1/2 역방향 초안
- local `AGENTS.md` guidance 후보

주의:

- 기존 코드에서 설계를 자동 확정하지 않는다.
- 기존 코드 기반 분석은 "현행 분석/후보"이지 승인된 요구사항/설계가 아니다.

### 2.13 Cleanup / AI-slop 제거

외부 runtime harness는 AI-looking code cleanup을 기능으로 둔다.

Ex에서 관찰된 문제:

- worker가 구현 외 README/증적/Run self-check까지 한 번에 처리해 시간이 늘어남
- 과한 주석 또는 부족한 테스트 설명
- 샘플에서 문서 정합성 맞추느라 구현 시간이 늘어남

Ex 적용 방향:

- Build worker는 코드와 테스트에 집중한다.
- Evidence/Normalization worker는 문서/증적 정리를 맡는다.
- Cleanup reviewer는 과한 문서/주석/불필요 파일 제거 후보를 제안한다.

## 3. 우선순위

### P0. Delegation Sidecar MVP

목표:

- native subagent/thread/Agy branch 진행 상태를 Dashboard가 실시간 또는 준실시간으로 읽을 수 있게 한다.

현재 상태:

- Dashboard local datasource가 `.vulcan/delegations/*.json`을 읽어 `runtime.delegations`와 병합한다.
- sidecar와 Run 문서 기록이 같은 `run_id/mode/delegate`를 가리키면 sidecar를 먼저 표시한다.
- sidecar가 없어도 기존 Run 문서의 `delegation_records`, `Run Execution Record`, direct edit reason 표시는 유지된다.

작업:

- `.vulcan/delegations/*.json` 스키마 정의
- Orchestrator 지침에 "native 위임 시작/완료 시 sidecar 갱신" 추가
- Dashboard runtime API가 sidecar를 읽어 `runtime.delegations`와 병합
- Run 문서 `delegation_records`와 sidecar의 관계 정의

성공 기준:

- Run 문서 정규화 전에도 Dashboard에서 `worker_running`, `worker_completed`, `verified/needs_review` 후보를 볼 수 있다.
- sidecar가 없어도 기존 프로젝트는 깨지지 않는다.

sidecar는 Gate 승인, 테스트 Pass, release 가능 여부를 확정하지 않는다.
최종 판단은 여전히 Orchestrator 재검증과 Run/QA/Release 산출물에 기록한다.

### P1. Execute Facade 설계와 Dry-run

목표:

- `run-preflight`, native 위임, scope check, run-check, delegation 정규화 후보를 하나의 흐름으로 묶는다.

현재 상태:

- `python vulcan.py execute --run-id <RUN> --runner native --dry-run` MVP가 들어갔다.
- 실제 worker를 호출하지 않고 `run-check`, `run-preflight`, 위임 sidecar 후보, scope, 검증 명령, Orchestrator 재검증 흐름을 출력한다.
- run-check issue 또는 preflight blocker가 있으면 dry-run도 실패 코드로 종료한다.

작업:

- external CLI 실행과 `run-integrate --dry-run`까지 자동 연결할지 검토
- native sidecar 초안 생성/갱신은 실제 샘플 검증 뒤 검토
- 실제 worker 호출은 초기에는 안내/체크리스트 출력까지만 허용한다.

성공 기준:

- Orchestrator가 worker 실행 전후에 빠뜨리는 명령이 줄어든다.
- 자동 승인 없이 실행 준비/검증 흐름만 단순화한다.

### P2. Worker Completion State 분리

목표:

- worker 완료와 Orchestrator 검증 완료를 명확히 나눈다.

현재 상태:

- Dashboard 위임 기록은 raw `status` 대신 해석된 상태 배지를 표시한다.
- `worker_completed`/`completed`는 `worker 완료`로 표시하고, `verified`만 `검증 완료`로 표시한다.
- `orchestrator_verifying`, `needs_review`, `blocked`/`failed`/`timeout`/`environment_blocked`를 별도 의미로 분리한다.

작업:

- sidecar/Run/Dashboard 상태명 정리
- Dashboard badge 업데이트
- `run-check` 또는 `prepare-transition`에서 미검증 worker 결과를 더 명확히 안내

성공 기준:

- `completed_no_result_change`, `worker completed`, `verified`, `needs review`가 사용자에게 덜 헷갈린다.

남은 후보:

- `run-check` 또는 `prepare-transition`에서 완료된 Build/QA Run에 `worker_completed`만 있고 `verified` 또는 Orchestrator 검증 기록이 없으면 안내한다.
- Run 문서 생성 지침에서 `completed` 대신 `worker_completed`/`verified`를 명시적으로 쓰게 유도한다.

### P3. Doctor Command

목표:

- 새 사용자와 샘플 테스트에서 환경 차단을 빨리 식별한다.

작업:

- `python vulcan.py doctor` 명령 추가
- Node/npm/Playwright/Git/runner/Dashboard/cache 점검
- profile별 최소 환경 점검

성공 기준:

- Gate 4에서 Playwright browser cache, npm install, runner 미감지 같은 문제를 늦게 발견하지 않는다.

### P4. Role-based Model Routing Fallback

목표:

- 모델 미지원 오류를 작업 실패가 아니라 정책 fallback으로 처리한다.

작업:

- `runtime.model_policy`에 recommended/fallback 분리
- 실행 기록에 `model_source`, fallback reason 기록
- Dashboard 또는 `status`에 실제 사용 모델 표시

성공 기준:

- `gpt-5.3-codex` 미지원 같은 문제가 worker 실행 시간을 낭비하지 않는다.

### P5. Existing Codebase Adoption

목표:

- 신규 프로젝트뿐 아니라 기존 repo에 Ex를 얹는 흐름을 만든다.

작업:

- `map-codebase`/`adopt-existing` 전략 문서화
- 기존 API/DB/UI/test command 후보 추출
- Gate 0/1/2 후보 문서 생성은 dry-run으로 제한

성공 기준:

- 기존 코드베이스에서도 Ex를 "처음부터 새로 만드는 도구"가 아니라 "운영/증적 레이어"로 도입할 수 있다.

## 4. 당장 하지 않을 것

- 외부 runtime harness를 Ex 기본 dependency로 포함하지 않는다.
- Ex 명령을 특정 harness의 command naming과 1:1로 맞추지 않는다.
- 자동 approval, 자동 Gate transition, 자동 설계 문서 덮어쓰기는 하지 않는다.
- 대규모 병렬 구현 자동화는 계약/merge/검증 전략이 더 안정된 뒤 검토한다.

## 5. 결론

외부 runtime harness는 Ex가 부족했던 "실행 하네스 UX"를 잘 보여준다.
하지만 Ex의 핵심 가치는 빠른 실행이 아니라, 실행 결과를 요구사항-설계-테스트-증적-승인 흐름으로 회수하는 것이다.

따라서 Ex의 다음 고도화는 다음 순서가 가장 자연스럽다.

1. `delegation sidecar`
2. `execute` facade dry-run
3. worker completion state 분리
4. `doctor`
5. role-based model fallback
6. existing codebase adoption

이 순서는 외부 runtime harness의 장점을 흡수하되, Ex를 Codex 전용 harness가 아니라 runtime-agnostic governance layer로 유지한다.
