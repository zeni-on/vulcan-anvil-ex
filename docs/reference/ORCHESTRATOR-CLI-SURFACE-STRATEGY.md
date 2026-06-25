# Orchestrator CLI Surface Strategy

> Status: draft v0.1
> 작성일: 2026-06-08
> 목적: Vulcan-Anvil Ex를 운영하는 Orchestrator가 직접 기억하고 호출해야 하는 CLI 표면을 줄이는 전략을 정리한다.

## 1. 배경

현재 `vulcan.py`는 세밀한 원자 명령을 많이 제공한다.

예를 들면 다음 명령들은 각각 필요하다.

- `gate-start`, `session`, `sync-session`
- `branch-status`, `branch-start`
- `orchestrator-plan`, `run-new`, `wave-start`, `wave-complete`
- `run-check`, `run-preflight`, `prepare-transition`, `check-trace`, `check-contract`
- `run-exec`, `agent-run`, `agent-resume`, `run-integrate`
- `release-pr`, `upgrade`, `export`, `version`, `release`

이 구조는 안전하다.
각 명령이 좁은 책임을 가지므로 검증, 차단, 로그, 회귀 테스트를 만들기 쉽다.

하지만 Orchestrator 관점에서는 부담이 크다.
단계마다 어떤 명령을 어떤 순서로 호출해야 하는지 기억해야 하고, 하나를 빠뜨리면 `run-preflight` 누락, session 통계 미동기화, Gate 전환 전 진단 누락 같은 절차적 누수가 생긴다.

따라서 목표는 원자 명령을 삭제하는 것이 아니라, Orchestrator가 일상적으로 쓰는 상위 표면을 얇게 만드는 것이다.

## 2. 결론

권장 표면은 처음부터 여러 facade를 한꺼번에 늘리는 것이 아니라, **`status` 하나를 먼저 추가하는 단계적 구조**다.

장기적으로는 `plan`, `execute`, `transition` 같은 facade 후보가 있을 수 있다.
하지만 `prepare-transition`이 이미 전환 진단을 줄이기 위해 만들어진 macro인 만큼, 다시 `transition check` 같은 유사 진단 명령을 만들면 오히려 CLI 표면이 늘어난다.
또한 `init`, `upgrade`, `version`, `export`는 단어 자체가 충분히 직관적이므로 `project init`처럼 다시 감싸지 않는다.

따라서 1차 MVP에서 Orchestrator가 새로 기억할 명령은 다음 하나다.

```text
python vulcan.py status
```

`status --check`는 기존 `prepare-transition` 진단을 내부적으로 재사용하는 읽기 전용 요약 명령이다.
`prepare-transition`은 직접 실행 기본 명령이 아니라, `status --check` 뒤의 상세/호환 진단 명령으로 남긴다.

| 구분 | 목적 | 성격 |
| --- | --- | --- |
| `status` | 현재 상태와 다음 행동 판단 | 일상 명령 |
| `plan` | Gate/Run/Wave 작업 초안 생성 | 후속 후보 |
| `execute` | worker/subagent/thread 실행, 통합, Wave 완료 | 후속 후보 |
| `transition` | Gate 완료/승인/릴리즈 전환 | 후속 후보. `transition check`는 만들지 않음 |
| 기존 `init/upgrade/version/export` | 프로젝트 생성, 업그레이드, 버전 확인, 내보내기 | 그대로 유지 |

즉, Orchestrator가 당장 새로 떠올려야 하는 명령은 `status` 하나로 줄이고, 프로젝트 생성/업그레이드 같은 관리 명령은 기존 이름 그대로 유지한다.

이 방식이 5개 고정보다 나은 이유는 다음이다.

- `init`, `upgrade`, `version`, `export`는 Gate 운영 중 매번 쓰는 명령이 아니다.
- `check-trace`, `run-preflight`, `run-check` 같은 원자 진단은 여전히 내부적으로 필요하다.
- 상태 변경 명령을 하나로 과도하게 합치면 승인 경계가 흐려질 수 있다.
- 상위 명령은 기본적으로 `dry-run` 또는 read-only로 시작하고, 실제 변경은 명시적인 `--apply` 또는 승인 지시가 있을 때만 수행해야 한다.

## 3. 현재 원자 명령 분류

### 3.1 상태/진단

| 원자 명령 | 상위 표면 |
| --- | --- |
| `profile-status` | `status` |
| `branch-status` | `status` |
| `prepare-transition` | `status --check`의 내부/상세 진단. 호환 명령으로 유지 |
| `check-trace` | `status --trace-detail`, 내부 진단 |
| `check-contract` | `status --contract`, 내부 진단 |
| `check-architecture` | `status --architecture`, 내부 진단 |

### 3.2 계획/초안

| 원자 명령 | 상위 표면 |
| --- | --- |
| `orchestrator-plan` | `plan` |
| `run-new` | `plan run` |
| `wave-start` | `plan wave` 또는 `execute wave-start` |
| `trace-context` | `plan --trace-seed`, `status --trace` |
| `review-request`, `handoff` | `plan review`, `plan handoff` |

### 3.3 실행/통합

| 원자 명령 | 상위 표면 |
| --- | --- |
| `run-preflight` | `execute --preflight`, 내부 필수 단계 |
| `run-exec` | `execute --runner cli` |
| `agent-run` | `execute --runner cli-session` |
| `agent-resume` | `execute resume` |
| native subagent/thread/Agy branch 위임 | `execute --runner native` |
| `run-integrate` | `execute integrate` |
| `wave-complete` | `execute complete-wave` |
| `run-check` | `execute --verify`, 내부 필수 단계 |

### 3.4 전환/릴리즈

| 원자 명령 | 상위 표면 |
| --- | --- |
| `gate-start` | 기존 원자 명령 유지 |
| `session` | 기존 원자 명령 유지 |
| `sync-session` | 기존 원자 명령 유지 |
| `branch-start` | 기존 원자 명령 유지 |
| `release-pr` | 기존 원자 명령 유지 |

### 3.5 유지보수

| 원자 명령 | 상위 표면 |
| --- | --- |
| `init` | 기존 `init` 유지 |
| `upgrade` | 기존 `upgrade` 유지 |
| `version` | 기존 `version` 유지 |
| `export` | 기존 `export` 유지 |
| `release` | 유지보수/배포 명령 |

유지보수 명령은 `status` MVP에 억지로 넣지 않고, `project` 그룹도 만들지 않는다.

## 4. 상위 명령 설계

### 4.1 `vulcan status`

가장 먼저 구현할 MVP 후보다.

역할은 현재 프로젝트의 상태와 다음 행동 후보를 한 번에 보여주는 것이다.

기본 동작은 read-only다.

출력 후보:

- project/profile/current_gate
- Gate 상태와 승인 대기 여부
- 현재 브랜치와 `workflow.integration_branch`
- active Build Wave/Run
- 최근 worker/delegation 상태
- `prepare-transition` 필요 여부
- trace/detail 검사가 필요한 후보
- 다음 추천 명령 1~3개

권장 옵션:

```text
python vulcan.py status
python vulcan.py status --check
python vulcan.py status --trace-detail
python vulcan.py status --json
python vulcan.py status --json --check
```

`--check`는 `prepare-transition` 수준의 진단을 붙인다.
`--json --check`는 같은 진단을 `transition_check` 객체로 캡처해 자동화와 Dashboard가 재사용할 수 있게 한다.
`--trace-detail`은 추적성만 더 깊게 봐야 할 때 `check-trace`를 호출하거나 같은 내부 로직을 사용한다.

### 4.2 `vulcan plan`

역할은 현재 Gate에서 다음 작업 단위를 만드는 것이다.

기존 `orchestrator-plan`, `run-new`, `wave-start`, `trace-context`를 직접 기억하지 않아도 되게 한다.

예상 사용:

```text
python vulcan.py plan --goal "Gate 2 상세설계"
python vulcan.py plan run --skill build-wave --trace-seed REQ-001-01
python vulcan.py plan wave BW-001 --trace-seed REQ-001-01
```

주의:

- `plan`은 worker를 실행하지 않는다.
- `plan`은 초안을 만들 수 있지만, `scope.writable`, `interface_contract`, 검증 명령은 Orchestrator가 확정해야 한다.
- `plan` 결과가 바로 Gate 완료를 뜻하지 않는다.

### 4.3 `vulcan execute`

역할은 작업 단위 실행과 결과 통합이다.

기존 `run-preflight`, native subagent/thread/Agy branch 위임, 선택적 `run-exec`/`agent-run`, `run-integrate`, `wave-complete`, `run-check`를 한 흐름 안에서 다룬다.

현재 구현된 MVP는 dry-run 전용이다. 실제 worker 실행, 통합 적용, Wave 완료는 수행하지 않고 실행 전 계약/위임/검증 계획만 출력한다.

현재 사용:

```text
python vulcan.py execute --run-id RUN-012 --runner native --dry-run
python vulcan.py execute --run-id RUN-012 --runner codex-cli --dry-run
python vulcan.py execute --run-id RUN-012 --runner native --dry-run --json
```

장기 후보:

```text
python vulcan.py execute integrate --run-id RUN-012 --dry-run
python vulcan.py execute complete-wave BW-001 --status Verified
```

중요 원칙:

- native subagent/thread/Agy branch 위임 전에도 내부적으로 `run-preflight`를 먼저 수행한다.
- dry-run 단계에서는 `run-check`, `run-preflight`, `scope.writable`, 검증 명령, delegation sidecar 후보만 요약한다.
- `--json` 출력은 `delegation_sidecar`, `planned_flow`, `run_check`, `preflight`, `scope`, `verification.commands`를 같은 구조로 제공한다.
- 외부 CLI runner가 필요한 경우에만 `run-exec`/`agent-run` 경로를 선택한다.
- `execute`가 결과를 자동 승인하지 않는다.
- scope 밖 변경은 `Config Hotfix Candidate`, `qa-fix-loop`, `CR`, `reject` 중 하나로 명시 분기한다.

### 4.4 `vulcan transition` 후보

역할은 Gate 시작, 완료, 승인, 릴리즈 전환을 다루는 장기 후보다.
다만 1차 MVP에서는 구현하지 않는다.
특히 `transition check`는 만들지 않는다.
Gate 전환 진단은 `status --check` 하나로 모은다.

예상 사용:

```text
python vulcan.py transition start gate2
python vulcan.py transition complete gate2
python vulcan.py transition start impl
python vulcan.py transition release-pr --dry-run
```

중요 원칙:

- 진단은 `status --check`로 수행한다.
- Gate 완료나 다음 Gate 시작은 사용자 승인 또는 명시적인 진행 지시가 있어야 한다.
- `transition start impl`은 내부적으로 `branch-start impl` 정책과 연결한다.
- `transition release-pr`은 Gate 5 승인 흐름과 연결한다.

## 5. 효율성 관점의 방안

### 5.1 삭제보다 facade가 낫다

기존 원자 명령을 삭제하면 회귀 테스트, 문서, 샘플 프로젝트, 외부 runner 흐름이 한꺼번에 흔들린다.

따라서 다음 구조가 낫다.

```text
Orchestrator-facing facade
  status
  plan
  execute
  transition

Internal atomic commands
  run-check
  run-preflight
  prepare-transition
  check-trace
  run-integrate
  ...
```

원자 명령은 사람이 직접 쓰기보다 상위 명령의 내부 단계 또는 디버깅 도구로 남긴다.

### 5.2 상태 변경은 두 단계로 둔다

상위 명령이 편리해져도 승인 경계는 약해지면 안 된다.

따라서 상태 변경 명령은 다음 원칙을 따른다.

1. 먼저 `status --check`로 진단한다.
2. 사용자 승인 또는 명시 지시가 있을 때만 기존 `session`, `gate-start`, `branch-start`, `release-pr` 같은 상태 변경 명령을 실행한다.
3. 실패한 진단을 자동 수정하지 않는다. 수정 후보와 분기만 제시한다.

### 5.3 profile별 엄격도는 facade가 읽는다

`audit`, `product`, `poc` profile이 다르면 같은 `execute`라도 Run 문서 무게와 검사 강도가 달라진다.

예:

| Profile | `plan` | `execute` | `transition` |
| --- | --- | --- | --- |
| audit | Run/Wave/추적성 강함 | preflight/check-contract 엄격 | prepare-transition 차단 강함 |
| product | 핵심 계약 중심 | 테스트/빌드 중심 | 릴리즈 기준 중심 |
| poc | compact Run 또는 summary | subagent 중심, 외부 CLI 선택 | 최소 산출물과 실행 결과 중심 |

즉, profile별로 명령을 나누지 않고 상위 명령이 profile을 읽어 동작 강도를 조절한다.

### 5.4 Dashboard와 같은 용어를 쓴다

상위 명령 출력은 Dashboard가 보여주는 개념과 맞춰야 한다.

- current gate
- profile
- integration branch
- active wave
- running delegation
- transition readiness
- blocked/warn/pass

이렇게 해야 Orchestrator가 터미널과 Dashboard 사이에서 같은 상태를 본다.

## 6. 구현 순서

### Phase 1: `status` MVP

가장 먼저 `python vulcan.py status`를 추가한다.

범위:

- read-only
- session/profile/branch/current wave 요약
- 다음 추천 명령 출력
- `--json` 지원
- `--check`는 기존 `prepare-transition` 내부 로직 또는 원자 명령 결과를 붙이되 상태를 변경하지 않는다.
- 실패 시 원자 명령 이름, 재현 명령, 관련 문서/로그 경로를 함께 출력한다.

효과:

- Orchestrator가 매번 `branch-status`, `profile-status`, `prepare-transition`을 따로 기억하지 않아도 된다.
- 새 세션/컴팩트 이후 현재 위치를 빠르게 복구할 수 있다.

### Phase 2: `plan` 후보 검토

`orchestrator-plan`, `run-new`, `wave-start --trace-seed`, `trace-context`를 얇게 감싼다.

초기에는 기존 명령을 그대로 호출하는 alias 수준으로 시작한다.
핵심은 새 로직이 아니라 좋은 default와 안내다.
단, `status` MVP 효과를 샘플에서 확인하기 전에는 구현하지 않는다.

### Phase 3: `execute` 후보 검토

worker 실행 전후 흐름을 묶는다.

초기 범위:

- Run preflight와 run-check dry-run 자동 실행
- runner 선택 안내와 delegation sidecar 후보 출력
- native delegation이면 `delegation_records`/sidecar reminder
- external CLI runner면 기존 `run-exec`/`agent-run`으로 이어질 명령 안내
- 통합은 먼저 `run-integrate --dry-run`
- 통합 적용 전 dirty worktree와 scope violation을 확인
- ignored/cache 파일 오탐을 줄이되 공식 QA 로그와 증적은 유지

직접 자동 apply는 나중에 검토한다.
`execute`는 side effect가 크므로 `status`보다 늦게 검토한다.

### Phase 4: `transition` 후보 검토

Gate 전환과 릴리즈 흐름을 묶는다.
1차 MVP에서는 구현하지 않는다.
`transition check`는 만들지 않고, 진단은 `status --check`가 담당한다.

초기 범위:

- `transition complete <gate>`
- `transition start <gate>`
- `transition release-pr --dry-run`

승인 없는 자동 Gate 진행은 금지한다.

### Phase 5: 문서/skill 퀵맵 교체

`AGENTS.md`, repo-local skill, `GETTING_STARTED.md`의 퀵 레퍼런스는 상위 명령 중심으로 바꾼다.

단, 원자 명령은 디버깅/고급 명령으로 계속 문서화한다.

## 7. 리스크

| 리스크 | 대응 |
| --- | --- |
| 상위 명령이 너무 많은 일을 자동으로 해 승인 경계를 흐림 | 기본 read-only/dry-run, 변경은 `--apply` 또는 명시 승인 필요 |
| 기존 원자 명령과 새 facade 문서가 불일치 | facade는 자체 진단 로직을 복제하지 않고 기존 내부 함수와 원자 명령을 호출하며 회귀 smoke에 포함 |
| Orchestrator가 facade만 믿고 상세 오류를 놓침 | 실패 시 원자 명령 이름과 재현 명령을 출력 |
| profile별 동작이 복잡해짐 | profile별 명령 분리 대신 profile_rules를 읽어 severity/default만 조절 |
| 외부 runner, native subagent, Agy branch가 한 명령에 섞임 | `execute`에서 runner mode를 명시하고 기록 형식을 다르게 안내 |
| ignored/cache 파일이 scope 위반으로 오탐됨 | `execute integrate`/`run-integrate`는 `.gitignore`와 빌드 캐시 제외 규칙을 적용하되 공식 QA 증적 로그는 제외하지 않음 |
| dirty worktree에서 통합 적용이 충돌을 만듦 | `--apply` 전 git status, scope violation, config hotfix 후보, 충돌 가능성을 먼저 확인하고 차단 |

## 7.1 Agy Review 반영 원칙

`ORCHESTRATOR-CLI-SURFACE-STRATEGY-REVIEW-AGY.md`의 검토 결과는 전반적으로 facade 방향과 일치한다.
다만 Agy runtime 고유 표현과 Core 공통 규칙은 분리해서 반영한다.

반영할 항목은 다음이다.

| 항목 | 반영 방식 |
| --- | --- |
| 유사 진단 명령의 난립 방지 | `transition check`를 만들지 않는다. 전환 진단은 `status --check` 하나로 모은다. |
| 기본 동작 부작용 방지 | `status` 기본은 read-only이고, 후속 `execute integrate` 후보의 기본은 dry-run이다. 상태 변경은 `--apply` 또는 명시 승인 후에만 수행한다. |
| profile별 복잡도 관리 | facade가 profile별 if-else를 많이 갖지 않고 `profile_rules`와 내부 검사 결과의 severity를 받아 출력한다. |
| ignored/cache 파일 오탐 방지 | integration 단계에서 `.gitignore`와 cache 제외 규칙을 적용한다. 단, 공식 QA 로그와 증적은 추적 대상이어야 한다. |
| 실패 디버깅 가능성 유지 | facade 실패 출력에는 실패한 원자 명령, 재현 명령, 로그/증적 경로, 차단 ID 또는 파일 경로를 포함한다. |
| 통합 race condition 방지 | `--apply` 전 현재 브랜치, dirty status, git index lock 가능성, scope violation을 확인한다. |

주의할 항목은 다음이다.

- Agy의 `Workspace: branch`, `invoke_subagent`류 동작은 adapter-specific capability다. Core facade는 이를 일반 전제로 삼지 않고 `execute --runner native`의 한 구현 후보로만 다룬다.
- `execute --runner native`가 실제로 Codex subagent, Codex thread, Agy Workspace branch, Claude native agent 중 무엇을 호출하는지는 adapter가 결정한다.
- Core가 보장해야 하는 것은 호출 방식 자체가 아니라 `run-preflight`, `delegation_records`, Orchestrator 재검증, scope 검증의 공통 계약이다.

## 8. 결정 후보

현재 기준 추천 결정은 다음이다.

1. 원자 명령은 유지한다.
2. Orchestrator-facing facade는 `status` 하나로 시작한다.
3. `init`, `upgrade`, `version`, `export`는 충분히 직관적이므로 기존 명령 그대로 유지한다.
4. 첫 구현은 `status` MVP로 시작한다.
5. `status`가 샘플 프로젝트에서 효과를 보이면 `plan`, `execute`, `transition`을 후보로 다시 검토한다. 단, `transition check`는 만들지 않는다.
