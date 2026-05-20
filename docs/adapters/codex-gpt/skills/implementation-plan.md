# 구현 계획 Skill

## 사용할 때

Gate 3 테스트 설계가 끝나고 구현 단계로 들어가기 직전에 사용한다.

구현 계획은 코드를 작성하는 Run이 아니다. Orchestrator가 승인된 요구사항, 설계, 테스트 기준을 읽고 구현을 여러 `Build Wave`로 나누는 운영 Run이다.

## 필수 입력

- `AGENTS.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- 관련 요구사항정의서
- 관련 요구사항추적표
- 관련 기능명세서
- 관련 프로그램명세서
- 관련 화면설계서
- 관련 DB명세서
- 관련 개발표준정의서
- 관련 테스트케이스 정의서

## 절차

1. 구현 대상 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`를 확인한다.
2. 구현 제외 범위와 후속 Backlog 후보를 분리한다.
3. 의존성을 기준으로 `Build Wave`를 정의한다.
4. 각 Wave에 목표, 관련 ID, 수정 파일 후보, 테스트, 추적표 갱신 항목, 커밋 후보를 연결한다.
5. subagent 또는 독립 runner 위임이 가능한 Wave와 메인 Orchestrator가 직접 통합해야 할 Wave를 구분한다.
   - Frontend Build Wave는 기본 후보 runner를 `claude-cli`로 둔다.
   - Backend Build Wave는 기본 후보 runner를 `codex-cli`로 둔다.
   - 같은 Wave 안에서 frontend/backend 파일을 동시에 수정해야 하면 runner를 하나로 합치거나 Wave를 다시 나눈다.
6. Wave 간 순서, 병렬 가능성, 중단 조건을 기록한다.
7. 구현 시작 전 필요한 사용자 승인 또는 미해결 질문을 남긴다.
8. 구현 실행 시에는 한 번에 하나의 Wave만 active 상태로 둘 것을 명시한다.

## Build Wave 작성 기준

| 항목 | 작성 기준 |
| --- | --- |
| `BW-ID` | `BW-001`, `BW-002`처럼 안정 ID를 부여한다. |
| 목표 | 하나의 검증 가능한 구현 배치로 설명한다. |
| 관련 ID | `REQ/AC/PGM/SCR/DB/SEC/UT/IT/UI` 중 해당 ID를 연결한다. |
| 수정 범위 | 예상 파일 또는 디렉터리를 적는다. |
| 테스트 | Wave 종료 시 실행할 테스트를 적는다. |
| 추적표 갱신 | 상태, 증적, 테스트 결과 갱신 항목을 적는다. |
| 커밋 후보 | Wave 완료 후 사용할 커밋 메시지 후보를 적는다. |
| 위임 | subagent/runner 위임 여부, 권장 runner, 책임 범위를 적는다. |

## 실행 운영 기준

- Implementation Plan은 전체 구현 지도이고, 실제 구현 지시는 Wave별 `build-wave` Run으로 만든다.
- Wave 수가 4개이면 보통 `implementation-plan` Run 1개와 `build-wave` Run 4개가 생긴다.
- Orchestrator는 현재 Wave의 작업지시서를 만들고, subagent에게 해당 Wave 범위만 전달한다.
- 동시에 active 상태인 Wave는 하나만 허용한다.
- 하나의 Wave 안에서는 파일 책임이 분리된 경우에만 subagent 병렬 실행을 허용한다.
- 다음 Wave의 읽기 전용 조사나 질문 정리는 가능하지만 코드 수정은 현재 Wave 완료 후 시작한다.
- Wave 상태와 구현 진행률은 `session.json`을 직접 수정하지 않고 `vulcan.py wave-start`, `vulcan.py wave-complete`, `vulcan.py sync-session`으로 갱신한다.

## 권장 Wave 예시

```text
BW-001 프로젝트 뼈대와 공통 설정
BW-002 Backend 인증/회원가입/로그인 API와 보안
BW-003 Backend TODO 데이터와 CRUD
BW-004 Frontend UI 상태와 오류/빈 상태
BW-005 Playwright 화면 증적, 테스트 결과, 추적표 정리
```

권장 runner 예:

| BW-ID | 영역 | 권장 runner |
| --- | --- | --- |
| BW-002 | Backend | codex-cli |
| BW-003 | Backend | codex-cli |
| BW-004 | Frontend | claude-cli |
| BW-005 | Evidence/QA | codex-cli 또는 claude-cli |

## 완료 조건

- 모든 구현 대상 ID가 하나 이상의 Wave에 배치되어 있다.
- Wave 간 의존성과 순서가 명확하다.
- 각 Wave에 테스트와 추적표 갱신 기준이 있다.
- subagent 위임 가능 범위와 충돌 가능 파일이 식별되어 있다.
- 사용자 승인 또는 미해결 질문이 명시되어 있다.
- Wave별 실행 Run 생성 기준과 한 번에 하나의 active Wave 원칙이 명시되어 있다.

## 출력

다음을 반환한다.

- Implementation Plan Run 요약
- `Build Wave` 목록
- Wave별 관련 ID
- Wave별 수정 파일 후보
- Wave별 테스트/검증 명령
- Wave별 권장 runner
- Wave별 커밋 메시지 후보
- subagent 위임 계획
- 중단 조건
- 다음 `build-wave` Run 제안
