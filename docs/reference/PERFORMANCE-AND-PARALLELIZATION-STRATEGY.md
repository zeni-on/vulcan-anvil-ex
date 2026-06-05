# Performance and Parallelization Strategy

> Status: draft v0.1
> 기준 샘플: `sample-ex-0530-1`
> 측정일: 2026-05-31

## 1. 목적

Vulcan-Anvil Ex `audit` profile은 빠른 코드 생성보다 설명 가능한 산출물, 추적성, QA 증적, 승인 경계를 우선한다.
따라서 단순 구현형 AI coding보다 시간이 더 걸리는 것은 정상이다.
다만 실제 병목이 어디에서 발생하는지 측정하고, 자동화 또는 안전한 병렬화로 줄일 수 있는 시간을 식별해야 한다.

이 문서는 샘플 프로젝트의 Run, worker summary, git log를 기준으로 현재 병목과 개선 방향을 정리한다.

## 2. 측정 데이터

측정에 사용한 데이터는 다음이다.

- `docs/runs/*.md`
- `docs/runs/_exec/*-summary.json`
- `docs/runs/_exec/*-status.json`
- `git log --date=iso`

이번 측정은 수작업 대화, 사용자 승인 대기, 야간 공백, upgrade 재실행이 섞인 샘플 로그를 기준으로 한다.
따라서 절대 시간보다 단계별 상대 비중과 병목 후보를 보는 용도로 사용한다.

## 3. 샘플 실행 요약

`sample-ex-0530-1`의 전체 git 기록 범위는 다음과 같다.

| 구간 | 시작 | 종료 | 경과 |
| --- | --- | --- | ---: |
| 전체 기록 | 2026-05-30 23:37 | 2026-05-31 12:34 | 약 12.95h |
| Phase0~Gate3 승인 흐름 | 2026-05-30 23:46 | 2026-05-31 00:38 | 약 51m |
| Impl 활성 구간 | 2026-05-31 00:38 | 2026-05-31 01:41 | 약 63m |
| 야간/대기 공백 | 2026-05-31 01:41 | 2026-05-31 09:29 | 약 7h48m |
| Gate4 QA 활성 구간 | 2026-05-31 09:30 | 2026-05-31 12:34 | 약 184m |

체감 시간이 긴 가장 큰 이유는 Gate4 QA에서 두 차례 `qa-fix-loop`가 발생했고, 각 fix 이후 재검증과 문서 정합성 정리가 반복됐기 때문이다.

## 4. Worker 실행 시간

`docs/runs/_exec/*-summary.json` 기준 worker 실행 합계는 약 96.8분이다.

| Run | 역할 | 실행 시간 | 변경 파일 수 | worktree | 관찰 |
| --- | --- | ---: | ---: | --- | --- |
| RUN-011 | BW-000 scaffold | 11.1m | 6 | No | 빌드 가능한 skeleton 생성 |
| RUN-012 | BW-001 backend | 7.3m | 18 | No | FastAPI/SQLite backend 구현 |
| RUN-013 | BW-002 frontend | 5.2m | 8 | No | UI baseline/API 연결 |
| RUN-016 | QA-000 env smoke | 12.8m | 4 | Yes | QA workspace 준비 |
| RUN-017 | QA-001 command checks | 10.6m | 4 | Yes | command 검증, contract FIND 발견 |
| RUN-018 | qa-fix-loop FIND-017-01 | 4.8m | 4 | Yes | repository contract 수정 |
| RUN-019 | QA-002 UI/E2E evidence | 20.9m | 15 | Yes | UI screenshot/log/trace 생성 |
| RUN-020 | qa-fix-loop FIND-019-01 | 11.1m | 5 | Yes | validation message 수정 |
| RUN-021 | QA-003 result summary | 13.1m | 6 | Yes | QA 결과/추적표 정리 |

단계별 worker 시간은 다음과 같다.

| 단계 | Run 수 | Worker 시간 | 평균 |
| --- | ---: | ---: | ---: |
| Impl worker | 3 | 23.6m | 7.9m |
| QA execution worker | 4 | 57.3m | 14.3m |
| QA fix worker | 2 | 15.9m | 8.0m |

## 5. 병목 해석

### 5.1 Gate4 QA가 가장 비싸다

Impl worker 합계는 약 24분이지만, Gate4 QA 관련 worker와 fix는 약 73분이다.
여기에 Orchestrator 재검증, 결과 통합, 추적표 갱신, 사용자 판단 대기가 추가된다.

즉 audit profile에서 시간의 핵심 병목은 구현 자체가 아니라 다음이다.

- QA 실행 결과 해석
- FIND와 CR 분류
- 승인된 FIND에 대한 `qa-fix-loop`
- 재검증
- QA 결과서/추적표 정합성

### 5.2 정합성 정리는 필수지만 반복 비용이 크다

이번 샘플에서 실제 문제가 된 항목은 다음 유형이다.

- Gate3 테스트케이스 계획 상태와 Gate4 실행 결과 상태 혼동
- UI 그룹 ID(`UI-001`)와 실행 ID(`UI-001-05`) 혼동
- 추적표 증적 경로 구분자 문제
- Program Design contract와 실제 class/interface 불일치

이 항목들은 모두 감리형 산출물에서는 중요한 정합성이다.
다만 사람이 문서를 직접 맞추면 시간이 크므로 `check-trace`, `check-contract`, `trace-context`, `run-preflight`가 더 많이 대신해야 한다.

### 5.3 Worker 병렬화보다 전/후처리 자동화가 먼저다

Impl worker는 각각 5~11분 수준으로 비교적 짧았다.
반면 QA-Fix 왕복과 결과 정리가 긴 체감 시간을 만들었다.
따라서 당장 모든 worker를 병렬화하는 것보다 다음 자동화가 먼저 효과적이다.

- Run 생성 시 `trace-seed` 기반 ID/문서 후보 자동 보강
- Run preflight에서 scope, interface contract, QA workspace, 결과서 원본 규칙 사전 차단
- QA 결과서 -> 추적표 상태 후보 자동 생성
- QA Finding -> qa-fix-loop Run 초안 자동 생성
- `check-trace` 오류 메시지를 수정 대상 문서/컬럼까지 구체화

## 6. 병렬화 후보

Gate 전환 자체는 순차가 맞다.
하지만 Gate 내부의 일부 작업은 안전 조건을 만족하면 병렬화할 수 있다.

| 후보 | 병렬화 가능성 | 선행 조건 | 주의 |
| --- | --- | --- | --- |
| Gate2 review Run | 높음 | 설계 산출물 baseline candidate 작성 완료 | review 결과는 Orchestrator가 합성 |
| independent review | 높음 | 대상 문서가 고정됨 | result 파일 충돌 방지 |
| Impl backend/frontend | 중간 | API/DTO/interface contract 고정, 서로 다른 BW/Run | active Wave 1개 원칙과 충돌하지 않게 별도 wave 정책 필요 |
| QA-001 command groups | 중간 | QA-000 workspace 준비 완료 | 같은 workspace 동시 서버/포트 충돌 주의 |
| QA-002 viewport screenshots | 중간 | 서버 기동 완료, 테스트 데이터 격리 | 데이터 초기화 충돌 주의 |
| QA-003 결과 정리 | 낮음 | QA-001/QA-002 완료 필요 | 최종 판정 후보는 순차 합성이 안전 |
| qa-fix-loop | 낮음 | FIND별 수정 범위가 완전히 분리됨 | 동일 코드/추적표 충돌 위험 |

## 7. 개선 우선순위

### P1. 측정 자동화

현재는 사람이 git log와 summary JSON을 읽어야 한다.
`vulcan.py perf-report` 같은 명령으로 다음을 자동 산출하는 것이 좋다.

- Gate별 wall-clock
- worker execution time
- Orchestrator/대기/문서 정합성 추정 시간
- Run별 duration, changed files, timeout/watchdog state
- QA-Fix 왕복 횟수
- 가장 오래 걸린 Run top N
- role/model/effort별 duration과 timeout 경향

### P1. QA 결과서 -> 추적표 후보 자동화

Gate4에서 가장 많이 반복되는 정합성 작업이다.
QA Test Result의 `결과`, `증적`, `관련 테스트`를 읽어 요구사항추적표의 다음 후보를 생성한다.

- `상태`
- `증적`
- `요구사항별 검증 요약`
- 미해결 FIND/CR/ISSUE

최종 반영은 Orchestrator가 하되, 후보 생성은 도구가 담당한다.

### P1. Run 품질 자동 보강

`run-new --trace-seed`와 `wave-start --trace-seed`는 시작점이다.
다음은 Run 초안의 부족한 부분을 도구가 더 구체적으로 알려주는 것이다.

- `scope.writable`이 넓은지
- `interface_contract`가 비어 있는지
- worker가 읽을 문서가 과한지
- QA Run이 `QA-000`이 기록한 integration workspace를 참조하는지
- 결과서/추적표/session을 worker가 직접 확정하려는지

PoC profile의 성능 개선은 먼저 Run 입력 계약의 밀도를 줄이는 방식으로 진행한다.
1차 기준은 `docs/reference/POC-RUN-COMPACT-STRATEGY.md`를 따른다.

### P1. Codex model/effort routing

별도 벤치마크 프로젝트를 크게 돌리기보다, 실제 Run 실행 기록에 model/effort/source를 남기고 점진적으로 조정한다.
Codex 기준 초기 정책은 `docs/core/CODEX_MODEL_POLICY.md`를 따른다.

- 중요한 판단, 설계 검수, FIND/CR 분류는 `gpt-5.5` + `high`를 유지한다.
- 일반 구현과 QA fix는 `gpt-5.5` + `high`를 우선 사용한다.
- QA 실행/로그 수집은 `gpt-5.4` + `medium`으로 시작한다.
- Run 초안, trace 후보, evidence summary는 `gpt-5.4-mini` + `medium/low`를 후보로 둔다.

이 정책의 효과는 `duration_seconds`, `timed_out`, `changed_files`, `run-check/check-trace/check-contract` 결과, Orchestrator 보정량으로 판단한다.

### P2. 안전 병렬화

병렬화는 성능 개선 효과가 있지만, audit profile에서는 정합성 충돌 비용이 크다.
따라서 다음 순서가 좋다.

1. review Run 병렬화
2. 독립검수 병렬화
3. QA command group 병렬화
4. UI viewport 병렬화
5. 구현 병렬화는 계약과 merge 전략이 충분히 안정된 뒤 검토

## 8. Dashboard 후보

Dashboard에는 다음을 추가할 수 있다.

- Gate별 소요시간 막대
- Run별 worker duration과 status
- QA-Fix 왕복 횟수
- Worker 시간 vs Orchestrator/정합성 시간 추정
- 가장 오래 걸린 Run과 timeout/watchdog 이벤트
- `audit`, `solution`, `poc` profile별 예상 비용 비교

단, Dashboard는 먼저 `perf-report` 같은 CLI 출력이 안정된 뒤 붙이는 것이 좋다.

## 9. 결론

현재 병목은 worker가 느려서라기보다 audit profile의 정합성 비용에서 나온다.
샘플 기준 worker 실행 합계는 약 97분이고, 그중 Gate4 QA와 QA-Fix가 약 73분을 차지했다.

따라서 다음 성능 개선의 핵심은 다음이다.

1. 측정 자동화
2. QA 결과서와 추적표 정합성 자동 후보 생성
3. Run 생성 품질 자동 보강
4. review/QA 중심의 제한적 병렬화

이 방향이면 audit profile의 설명 가능성은 유지하면서 체감 시간을 줄일 수 있다.
