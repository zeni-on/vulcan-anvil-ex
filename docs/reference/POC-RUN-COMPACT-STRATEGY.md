# PoC Run Compact Strategy

> 목적: PoC profile에서 Gate와 traceability의 핵심 안전장치는 유지하면서, worker가 읽는 Run 문서의 반복 설명과 참조 문서 폭증을 줄인다.

## 1. 문제

PoC는 가설 검증과 빠른 반복이 목적이다. 하지만 audit profile 기준의 Run 문서를 그대로 쓰면 작은 실험에서도 다음 비용이 커진다.

- `source_documents`가 넓어져 worker가 불필요한 문서를 읽는다.
- `worker_run_sizing_policy`, Core protocol, Run 입출력 계약 같은 작성자/오케스트레이터용 설명이 worker Run에 반복된다.
- `--trace-seed` depth가 넓으면 직접 관련 없는 ID와 문서가 따라온다.
- QA Run마다 상세 명령 결과를 모두 길게 쓰면 최종 QA 결과서와 중복된다.

## 2. 원칙

PoC 경량화는 산출물 품질을 낮추는 것이 아니다.

- Gate 승인과 실제 실행 여부 구분은 유지한다.
- 실행하지 않은 테스트를 Pass로 바꾸지 않는다.
- `scope.writable`, `target_contracts`, 검증 명령은 여전히 명확해야 한다.
- 상세 audit 증적이 필요한 경우 `audit` profile로 전환하거나 명시적으로 `--trace-depth`와 review Run을 늘린다.
- PoC Run은 기본 필수가 아니다. 외부 CLI worker, 독립 검수, 긴 작업 위임, 재현 가능한 실험 기록이 필요할 때만 만든다.
- subagent만으로 처리한 짧은 PoC 작업은 Gate 산출물 또는 결과 요약에 기록하고, 별도 Run을 만들지 않을 수 있다.
- `TBD`, `미정`, `확정필요`는 허용하되 목표, 성공 기준, 실제 실행 결과에는 사용할 수 없다.
- 남겨 둔 `TBD`에는 사유와 후속 판단 시점을 같이 적는다.

## 3. 1차 적용 범위

1차는 Run 입력 문서의 크기와 참조 범위를 줄이는 데 집중한다.

| 항목 | audit | poc 1차 |
| --- | --- | --- |
| trace depth 기본값 | 2 | 1 |
| `source_documents.read_first` | Core/trace/run protocol 포함 가능 | `AGENTS.md`, `session.json`, `DELIVERY_PROFILES.md`, 현재 skill 중심 |
| `reference_on_demand` | trace graph 추천 전체 후보 중심 | 직접 관련 문서 우선, 최대 5개 |
| `worker_run_sizing_policy` | 필요 시 audit Run에 표시 | PoC worker Run에는 반복 표시하지 않음 |
| 개발표준 체크리스트 | 구현 Run에 상세 표시 | PoC에서는 필요 시 reference로 확인 |
| QA 상세 명령 결과 | Run과 QA 결과서에 모두 상세 가능 | 최종 `DOC-QA-G4-002_Test-Result` 중심 |
| `TBD` 처리 | 대부분 차단 | 사유/후속 판단 시점이 있으면 경고 |

## 4. 구현 규칙

- `run-new`와 `wave-start`는 profile이 `poc`이고 `--trace-depth`가 명시되지 않으면 depth 1을 사용한다.
- 사용자가 `--trace-depth 2` 이상을 명시하면 사용자의 값을 우선한다.
- PoC `reference_on_demand`는 Program, API, Data, Security, Function, Screen, Test, Requirements 순서로 직접 관련 문서를 우선한다.
- PoC worker Run에는 `AGENT_RUN_PROTOCOL`, `RUN_INPUT_CONTRACT`, `RUN_OUTPUT_CONTRACT`, `Traceability Matrix`를 반복 입력 문서로 넣지 않는다.
- Orchestrator가 필요한 운영 문서는 Run 본문 대신 현재 프로젝트의 Core 문서와 skill 문서를 필요 시 직접 확인한다.
- PoC Run이 필요한 경우에도 다음 5가지만 우선한다.
  - 목표/가설
  - 성공 기준
  - 작업 범위와 금지 범위
  - 실행 명령과 실제 결과
  - 미정 항목의 사유와 후속 판단 시점
- PoC에서 `check-trace`는 상세 ID 누락, 미실행, 환경 차단을 우선 경고로 분류한다. 제품 실패, 허위 Pass, 목표/성공 기준/결과 누락은 계속 차단한다.

## 5. 후속 작업

1차 이후 다음을 검토한다.

- Gate 2 PoC용 `design-smoke-review` 단일 검토 Run
- Gate 4 PoC QA Run compact 형식
- `ExpectedFail` / `PreFinalFail` 상태값과 Gate 5 차단 규칙
- Dashboard에서 PoC Run compact 여부와 trace depth 표시
