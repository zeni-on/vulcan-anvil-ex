# Build Wave Skill

## 사용할 때

구현 단계에서 `implementation-plan`이 정의한 하나의 `Build Wave`를 실행할 때 사용한다.

Build Wave는 전체 구현이 아니라 하나의 검증 가능한 구현 배치다. Wave가 끝나면 코드, 테스트, 문서/추적표 갱신, 검증 결과, 커밋 후보가 함께 남아야 한다.

## 필수 입력

- `AGENTS.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`
- Implementation Plan Run
- 현재 Wave의 `BW-ID`
- 관련 설계 산출물
- 관련 테스트케이스

## 절차

1. Implementation Plan에서 현재 `BW-ID`의 목표, 관련 ID, 수정 범위, 테스트를 확인한다.
2. Wave 범위 밖 요구사항, 파일, 리팩터링은 건드리지 않는다.
3. 필요한 코드, 설정, 테스트, 메시지 리소스를 구현한다.
4. 구현 또는 테스트 파일에 관련 추적 ID를 남긴다.
5. Wave에 지정된 테스트와 최소 검증 명령을 실행한다.
6. 요구사항추적표, 테스트 결과서, Run 기록에 구현 파일과 테스트 결과를 연결한다.
7. Wave 완료 후 커밋 후보 메시지를 보고한다. 사용자가 승인하거나 자동 커밋 정책이 있으면 Wave 단위로 커밋한다.

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

- Wave 관련 ID가 코드, 테스트, 추적표에 연결되어 있다.
- Wave 테스트가 실행되었고 결과가 기록되어 있다.
- 실패한 테스트는 숨기지 않고 `FIND` 또는 `ISSUE`로 남긴다.
- 다음 Wave 진행 가능 여부와 남은 위험을 보고한다.

## 출력

다음을 반환한다.

- `BW-ID`
- 수행한 구현 범위
- 변경 파일
- 관련 ID
- 실행한 테스트와 결과
- 갱신한 추적표/문서
- 커밋 메시지 후보
- 다음 Wave 진행 여부
- `FIND`, `ISSUE`, `CR` 후보

