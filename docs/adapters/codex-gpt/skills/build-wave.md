# Build Wave Skill

## 사용할 때

구현 단계에서 `implementation-plan`이 정의한 하나의 `Build Wave`를 실행할 때 사용한다.

Build Wave는 전체 구현이 아니라 하나의 검증 가능한 구현 배치다. Wave가 끝나면 코드, 테스트케이스, Orchestrator가 재실행할 검증 명령, 문서/추적표 갱신 필요 항목, 커밋 후보가 함께 남아야 한다. worker는 요구사항추적표의 `Implemented` 또는 `Verified` 상태를 직접 확정하지 않고, 갱신해야 할 ID와 증적 후보를 보고한다.

Wave/worker Run은 시간 단위가 아니라 기능/계약 단위로 나눈다. 목표 시간은 10분 내외, 최대 15분 권장이지만 보조 기준이다. 15분을 넘길 것으로 예상되면 개발을 중간에 끊지 말고 더 작은 `FUNC/PGM/API/DB/SEC/TEST` 계약 묶음으로 다시 나눈다.

## 필수 입력

- `AGENTS.md`
- `docs/core/TRACEABILITY_RULES.md`
- 현재 Build Wave Run
- Implementation Plan Run
- 현재 Wave의 `BW-ID`
- 현재 Run의 `target_contracts`
- 관련 개발표준정의서
- 관련 테스트케이스 또는 담당 테스트 파일
- 요구사항추적표. 단, 작업자 runner는 추적표를 직접 갱신하지 말고 related ID와 갱신 필요 항목을 보고한다.

관련 설계 산출물 전체를 매번 정독하지 않는다.
작업자는 현재 Build Wave Run의 `source_documents.working_documents`를 우선 읽고, API/화면/프로그램/DB/보안 설계는 related ID나 기준 충돌이 있을 때 `reference_on_demand`에서 필요한 문서만 펼친다.

## 절차

1. Orchestrator는 `vulcan.py wave-start <BW-ID>`로 현재 Wave를 active 상태로 열고, 이미 다른 active Wave가 있으면 시작하지 않는다. 작업자 runner는 `wave-start`를 직접 실행하지 않고 Orchestrator가 연 Wave와 Run 지시를 따른다.
2. Implementation Plan에서 현재 `BW-ID`의 목표, `target_contracts`, 관련 ID, 수정 범위, 테스트를 확인한다.
3. 프로그램 설계서의 관련 `PGM`, Interface Contract, Abstract Base Contract, Public Method Contract를 확인한다.
4. 개발표준정의서에서 이번 Wave에 적용되는 패키지 구조, 계층 책임, 로깅, 주석, 예외/메시지, 테스트 명령을 확인하고 Run에 준수 체크리스트를 남긴다.
5. 개발표준의 필수 기준이 비어 있거나 서로 충돌하면 코드를 작성하지 않고 `FIND` 또는 `CR` 후보로 보고한다.
6. Wave 범위 밖 요구사항, 파일, 리팩터링은 건드리지 않는다.
7. 필요한 코드, 설정, 테스트, 메시지 리소스를 구현한다.
8. 구현 또는 테스트 파일에 관련 추적 ID를 남긴다.
9. 담당 테스트케이스를 작성/갱신하고 Orchestrator가 재실행할 테스트, 빌드, 린트, Run check 명령을 Run에 남긴다.
10. 가능하면 같은 명령을 self-check로 실행하고 결과를 보고한다. self-check를 실행하지 못했으면 Not Run 사유와 Orchestrator 재실행 명령을 남긴다.
11. 요구사항추적표, session 상태, Wave 완료 상태, 전체 테스트 결과서 통합은 Orchestrator가 처리한다. 작업자 runner는 갱신 필요 항목만 보고한다.
12. 작업자 runner로 실행 중이면 `vulcan.py wave-complete <BW-ID>`, `vulcan.py sync-session`, `vulcan.py check-trace`를 직접 실행하지 않고 Orchestrator에게 실행 필요 여부를 보고한다. Orchestrator는 worker 결과를 통합하고, worker가 만든 테스트케이스를 재실행한 뒤 `wave-complete`와 `sync-session`으로 session 상태를 갱신하고 `check-trace`를 실행한다.
13. 커밋 후보 메시지를 보고한다. 사용자가 승인하거나 자동 커밋 정책이 있으면 Wave 단위로 커밋한다.

## 검증 경계

Build Wave는 전체 Gate 4 QA가 아니다.

| 구분 | 수행자 | Wave에서의 의미 |
| --- | --- | --- |
| worker self-check | worker | 자기 수정 범위의 단위 테스트, API/컴포넌트 테스트, lint/build를 가능한 만큼 실행한다. |
| Wave 종료 검증 | Orchestrator | worker 테스트를 재실행하고, 현재까지 가능한 build/run-check/회귀 검증으로 통합 깨짐을 확인한다. |
| Gate 4 QA | QA/review/evidence | 전체 사용자 시나리오, Playwright 화면 증적, Test Result, QA Finding을 확정한다. |

Wave가 전체 사용자 시나리오를 완성하지 않았다면 전체 E2E나 최종 화면 증적을 Wave 완료 조건으로 요구하지 않는다.
Gate 3 테스트 설계에서 이 Wave의 `target_contracts`에 매핑된 `UT/IT/UI`와 필요한 smoke 기준만 Wave 검증으로 수행한다.
Wave가 vertical slice를 완성한 경우에는 제한된 smoke/E2E를 실행할 수 있지만, 최종 QA Pass는 Gate 4에서만 판정한다.
완료 보고에는 "전체 통합 테스트 완료" 대신 "Wave 범위 계약 테스트와 가능한 회귀 검증 완료"처럼 범위를 명확히 쓴다.

## Orchestrator와 subagent 책임

- Orchestrator는 Wave 작업지시서 작성, subagent/worker 위임, 결과 검토, 통합, worker 테스트케이스 재실행, 상태 갱신을 담당한다.
- 기능 구현의 주 작성자는 `build` persona, subagent, 또는 `agent-run --mode work` worker다.
- 작은 기능, 단일 파일, 단일 테스트 변경이라도 Orchestrator가 바로 구현 완료 처리하지 않는다. 단일 worker Run으로 위임하거나 직접 수정 예외를 기록한다.
- Orchestrator가 직접 수정할 수 있는 범위는 작은 연결 수정, 충돌 해결, 문서/추적표/session 갱신, 검증 보정으로 제한한다.
- 사용자가 worker 사용을 명시하지 않았다는 점은 직접 수정 예외 사유가 아니다. 구현 승인이 있으면 worker/subagent/agent-run 위임을 기본값으로 둔다.
- 직접 수정 예외는 worker/subagent/agent-run 실행 불가, worker 결과 통합 중 충돌 해결에 필요한 최소 수정, 긴급한 1~2줄 연결 수정, 사용자의 명시적 직접 구현 승인에 한해 허용한다.
- 직접 수정 예외가 필요하면 `orchestrator_direct_edit_reason`, 수정 파일, 실행 검증, 후속 검수 필요 여부를 Run에 남긴다.
- 하나의 Wave 안에서는 파일 책임이 분리된 경우에만 subagent를 병렬 실행한다.
- 다른 Wave의 코드 수정은 현재 Wave가 완료될 때까지 금지한다.
- subagent, `codex-cli`, `claude-cli` 같은 작업자 runner는 Gate 전환, `session.json` Gate 상태 변경, 최종 승인 판단을 하지 않는다.
- 작업자 runner는 `wave-complete`, Gate 전환, QA Pass, PR merge가 필요하다고 판단하면 완료 보고의 Orchestrator 결정 필요 항목으로 반환한다.
- 작업자 runner의 `scope.writable`에는 담당 코드/테스트/자기 Run 문서만 둔다. 화면 증적처럼 직접 산출해야 하는 파일이 있을 때만 담당 증적 경로를 추가한다. 추적표, 테스트 결과서, `session.json`은 Orchestrator 통합 범위로 둔다.
- 시간이 부족하다는 이유로 빌드/테스트가 깨진 중간 구현을 완료 처리하지 않는다.

## 상태

| 상태 | 의미 |
| --- | --- |
| `Planned` | 계획됨 |
| `In Progress` | 구현 중 |
| `Implemented` | Wave 범위 코드 작성 완료. 추적표 최종 상태가 아니라 Orchestrator 재검증 전 후보 상태 |
| `Verified` | Orchestrator가 Wave 범위 테스트를 재실행해 통과 확인. Gate 4 QA Pass와는 다름 |
| `Blocked` | 질문, 설계 누락, 환경 문제로 중단 |
| `Rolled Back` | 해당 Wave 변경을 되돌림 |

## 완료 조건

- Wave 관련 ID가 코드, 테스트, 작업자 Run 결과에 연결되어 있고, 추적표 갱신 필요 항목이 Orchestrator에게 전달되어 있다.
- Wave의 target_contracts가 기능/계약 단위의 완결 조각으로 닫혀 있다.
- 구현 파일의 패키지 구조, logger 선언, 주석/JavaDoc, 예외/메시지 처리가 개발표준정의서와 모순되지 않는다.
- 담당 테스트케이스와 Orchestrator 재실행 명령이 남아 있으며, worker self-check 결과 또는 Not Run 사유가 기록되어 있다.
- 실패한 테스트는 숨기지 않고 `FIND` 또는 `ISSUE`로 남긴다.
- 작업자 runner는 추적표 갱신 필요 항목을 보고하고, Orchestrator가 worker 테스트케이스와 현재 Wave 범위에서 가능한 회귀 검증을 재실행한 뒤 `vulcan.py wave-complete <BW-ID>`, `vulcan.py sync-session`, `python vulcan.py check-trace`로 session/추적성을 반영한다.
- Wave 완료를 Gate 4 QA Pass나 전체 E2E 완료로 표현하지 않는다.
- 다음 Wave 진행 가능 여부와 남은 위험을 보고한다.

## 출력

다음을 반환한다.

- `BW-ID`
- 수행한 구현 범위
- 변경 파일
- 관련 ID
- 개발표준 준수 체크리스트
- 작성/갱신한 테스트케이스
- Orchestrator 재실행 명령
- worker self-check 결과 또는 Not Run 사유
- 추적표/문서 갱신 필요 항목
- 커밋 메시지 후보
- 다음 Wave 진행 여부
- `FIND`, `ISSUE`, `CR` 후보
