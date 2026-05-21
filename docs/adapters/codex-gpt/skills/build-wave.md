# Build Wave Skill

## 사용할 때

구현 단계에서 `implementation-plan`이 정의한 하나의 `Build Wave`를 실행할 때 사용한다.

Build Wave는 전체 구현이 아니라 하나의 검증 가능한 구현 배치다. Wave가 끝나면 코드, 테스트, 문서/추적표 갱신, 검증 결과, 커밋 후보가 함께 남아야 한다.

## 필수 입력

- `AGENTS.md`
- `docs/core/TRACEABILITY_RULES.md`
- 현재 Build Wave Run
- Implementation Plan Run
- 현재 Wave의 `BW-ID`
- 관련 개발표준정의서
- 관련 테스트케이스
- 요구사항추적표. 단, 작업자 runner는 추적표를 직접 갱신하지 말고 related ID와 갱신 필요 항목을 보고한다.

관련 설계 산출물 전체를 매번 정독하지 않는다.
작업자는 현재 Build Wave Run의 `source_documents.working_documents`를 우선 읽고, API/화면/프로그램/DB/보안 설계는 related ID나 기준 충돌이 있을 때 `reference_on_demand`에서 필요한 문서만 펼친다.

## 절차

1. `vulcan.py wave-start <BW-ID>`로 현재 Wave를 active 상태로 열고, 이미 다른 active Wave가 있으면 시작하지 않는다.
2. Implementation Plan에서 현재 `BW-ID`의 목표, 관련 ID, 수정 범위, 테스트를 확인한다.
3. 개발표준정의서에서 이번 Wave에 적용되는 패키지 구조, 계층 책임, 로깅, 주석, 예외/메시지, 테스트 명령을 확인하고 Run에 준수 체크리스트를 남긴다.
4. 개발표준의 필수 기준이 비어 있거나 서로 충돌하면 코드를 작성하지 않고 `FIND` 또는 `CR` 후보로 보고한다.
5. Wave 범위 밖 요구사항, 파일, 리팩터링은 건드리지 않는다.
6. 필요한 코드, 설정, 테스트, 메시지 리소스를 구현한다.
7. 구현 또는 테스트 파일에 관련 추적 ID를 남긴다.
8. Wave에 지정된 테스트와 개발표준정의서의 필수 검증 명령을 실행한다.
9. 작업자 runner는 담당 코드, 테스트, 증적, 자기 Run 기록에 구현 파일, 명령 실행 결과, 테스트 결과를 연결한다.
10. 요구사항추적표, session 상태, Wave 완료 상태, 전체 테스트 결과서 통합은 Orchestrator가 처리한다. 작업자 runner는 갱신 필요 항목만 보고한다.
11. 작업자 runner로 실행 중이면 `vulcan.py wave-complete <BW-ID>`, `vulcan.py sync-session`, `vulcan.py check-trace`를 직접 실행하지 않고 Orchestrator에게 실행 필요 여부를 보고한다. Orchestrator가 직접 수행하는 Run이면 `wave-complete`와 `sync-session`으로 session 상태를 갱신하고 `check-trace`를 실행한다.
12. 커밋 후보 메시지를 보고한다. 사용자가 승인하거나 자동 커밋 정책이 있으면 Wave 단위로 커밋한다.

## Orchestrator와 subagent 책임

- Orchestrator는 Wave 작업지시서 작성, subagent 위임, 결과 검토, 통합, 검증, 상태 갱신을 담당한다.
- 기능 구현의 주 작성자는 `build` persona 또는 subagent다.
- Orchestrator가 직접 수정할 수 있는 범위는 작은 연결 수정, 충돌 해결, 문서/추적표 갱신, 검증 보정으로 제한한다.
- 하나의 Wave 안에서는 파일 책임이 분리된 경우에만 subagent를 병렬 실행한다.
- 다른 Wave의 코드 수정은 현재 Wave가 완료될 때까지 금지한다.
- subagent, `codex-cli`, `claude-cli` 같은 작업자 runner는 Gate 전환, `session.json` Gate 상태 변경, 최종 승인 판단을 하지 않는다.
- 작업자 runner는 `wave-complete`, Gate 전환, QA Pass, PR merge가 필요하다고 판단하면 완료 보고의 Orchestrator 결정 필요 항목으로 반환한다.
- 작업자 runner의 `scope.writable`에는 담당 코드/테스트/증적/자기 Run 문서만 둔다. 추적표와 `session.json`은 Orchestrator 통합 범위로 둔다.

## 상태

| 상태 | 의미 |
| --- | --- |
| `Planned` | 계획됨 |
| `In Progress` | 구현 중 |
| `Implemented` | 코드 작성 완료 |
| `Verified` | Wave 검증 통과 |
| `Blocked` | 질문, 설계 누락, 환경 문제로 중단 |
| `Rolled Back` | 해당 Wave 변경을 되돌림 |

## 완료 조건

- Wave 관련 ID가 코드, 테스트, 작업자 Run 결과에 연결되어 있고, 추적표 갱신 필요 항목이 Orchestrator에게 전달되어 있다.
- 구현 파일의 패키지 구조, logger 선언, 주석/JavaDoc, 예외/메시지 처리가 개발표준정의서와 모순되지 않는다.
- Wave 테스트가 실행되었고 결과가 기록되어 있다.
- 실패한 테스트는 숨기지 않고 `FIND` 또는 `ISSUE`로 남긴다.
- Orchestrator가 `vulcan.py wave-complete <BW-ID>`, `vulcan.py sync-session`, `python vulcan.py check-trace`로 session/추적성을 갱신했거나, 작업자 runner가 갱신 필요 항목으로 보고했다.
- 다음 Wave 진행 가능 여부와 남은 위험을 보고한다.

## 출력

다음을 반환한다.

- `BW-ID`
- 수행한 구현 범위
- 변경 파일
- 관련 ID
- 개발표준 준수 체크리스트
- 실행한 테스트와 결과
- 갱신한 추적표/문서
- 커밋 메시지 후보
- 다음 Wave 진행 여부
- `FIND`, `ISSUE`, `CR` 후보
