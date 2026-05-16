# Agent Run Protocol

> 상태: 초안 v0.1
> 목적: Vulcan-Anvil Ex에서 Codex, GPT, Claude 등 서로 다른 에이전트가 동일한 산출물과 Gate 규칙을 기준으로 작업하도록 공통 실행 규약을 정의한다.

## 1. 기본 원칙

Agent Run Protocol은 특정 모델이나 제품의 사용법이 아니다.

이 문서는 에이전트가 프로젝트 산출물을 읽고, 작업을 수행하고, 결과와 증적을 남기는 공통 계약을 정의한다. Adapter는 이 계약을 각 도구의 명령, 프롬프트, API, 세션 방식에 맞게 변환한다.

Core 원칙:

- 에이전트는 항상 승인된 문서와 추적표를 먼저 읽고 작업한다.
- 에이전트의 모든 작업은 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `PT`, `UI` 중 하나 이상과 연결되어야 한다.
- 에이전트가 임의로 범위를 확장하지 않도록 Run Scope를 명시한다.
- Gate 완료 전에는 산출물, 구현, 테스트, 증적, 미해결 이슈를 함께 남긴다.
- 모델별 차이는 Adapter에서 흡수하고 Core 산출물 형식은 유지한다.

## 2. Run 단위

하나의 Run은 에이전트에게 위임 가능한 최소 작업 단위다.

Run은 다음 중 하나의 목적을 가진다.

| Run 유형 | 목적 | 대표 산출물 |
| --- | --- | --- |
| Discovery Run | 요구사항, 참조문서, 현행 코드 분석 | 분석 메모, 질문 목록, `DEC`, `RISK` |
| Design Run | 요구사항을 설계 산출물로 전개 | SW 아키텍처 정의서, 기능명세, 화면명세, 프로그램명세, DB명세 |
| Screen Design Run | 화면 구조와 시안을 `SCR-ID`에 연결 | 화면설계서, 와이어프레임, 시안 이미지, 기준 viewport |
| Design Review Run | Gate 3 진입 전 설계 완성도를 검수 | 보안 검토, 화면 검토, 개발표준 검토 |
| Implementation Run | 승인된 설계를 코드로 구현 | 소스 코드, 설정, 리소스, 마이그레이션 |
| Test Run | 테스트 코드와 실행 결과 작성 | `UT`, `IT`, `PT`, `UI`, 결과서 |
| Evidence Run | 화면 캡처, 로그, 결과 파일 정리 | 증적 파일, 결과 문서 |
| Review Run | 추적성, 보안, 품질 점검 | 이슈, 변경요청, 리뷰 결과 |
| QA Fix Run | G4에서 발견된 기존 설계 범위 내 결함 수정 | `FIND`, 수정 코드, 재검증 결과 |
| Change Impact Run | 변경요청 영향도 분석과 다시 진행할 Gate 판단 | `CR`, 영향받는 ID, scope, 승인 판단 |

Run은 너무 크게 만들지 않는다.

좋은 Run 예시:

```text
REQ-005 게시글 작성 기능의 PGM-005 구현 및 UT-007/UT-008 통과
SCR-003 게시글 목록 화면 구현 및 UI-003 캡처 증적 생성
SCR-001 로그인 화면 시안을 외부 Figma 캡처와 연결하고 UI-001 비교 기준 작성
SEC-003 작성자 권한 검증 누락 여부 리뷰
FIND-001 비로그인 게시글 작성 실패 결함 수정 및 UT-008 재실행
CR-001 게시글 첨부파일 요청 영향도 분석
```

나쁜 Run 예시:

```text
게시판 전체 개발
문서 전부 정리
테스트 적당히 추가
```

## 3. Run 입력 계약

Adapter는 에이전트를 실행하기 전에 다음 입력을 구성해야 한다.

| 입력 | 필수 여부 | 설명 |
| --- | --- | --- |
| Run ID | 필수 | 에이전트 실행 단위 ID. 예: `RUN-001` |
| Persona | 필수 | 작업 persona. 예: `requirements`, `design`, `build`, `review`. 상세는 `AGENT_PERSONAS.md`를 따른다. |
| Run 유형 | 필수 | Discovery, Design, Implementation, Test, Evidence, Review |
| 목표 | 필수 | 이번 Run에서 완료할 구체적 목표 |
| 범위 | 필수 | 수정 가능 파일, 읽기 전용 파일, 제외 파일 |
| 기준 문서 | 필수 | 요구사항, 추적표, 관련 설계문서, 개발표준 |
| 관련 ID | 필수 | `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, 테스트 ID |
| Gate | 필수 | 현재 Gate와 완료 조건 |
| 금지사항 | 필수 | 민감문서, 임의 리팩터링, 승인 없는 범위 변경 등 |
| 완료 조건 | 필수 | 테스트, 캡처, 문서 갱신, 리뷰 기준 |
| 질문 정책 | 필수 | 막혔을 때 질문할 조건 |

입력 예시:

```yaml
run_id: RUN-001
persona: build
run_type: Implementation
goal: PGM-005 게시글 작성 API 구현
gate: G2
scope:
  writable:
    - docs/examples/board-with-login/sample-app/app/api/posts.py
    - docs/examples/board-with-login/sample-app/app/services/post_service.py
  readonly:
    - docs/examples/board-with-login/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    - docs/examples/board-with-login/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/seed-docs/reference-standards/
  excluded:
    - docs/ref-docs/
related_ids:
  req: [REQ-005]
  ac: [AC-007, AC-008]
  func: [FUNC-005]
  pgm: [PGM-005]
  sec: [SEC-002, SEC-004]
completion:
  - 구현 파일 작성
  - UT-007, UT-008 통과
  - 추적표 증적 갱신
```

## 4. Run 출력 계약

에이전트는 작업 완료 시 다음 결과를 남겨야 한다.

| 출력 | 필수 여부 | 설명 |
| --- | --- | --- |
| 변경 요약 | 필수 | 무엇을 왜 바꿨는지 |
| 변경 파일 | 필수 | 파일 경로 목록 |
| 관련 ID | 필수 | 변경과 연결된 추적 ID |
| 검증 결과 | 필수 | 실행한 테스트/명령/캡처 결과 |
| 증적 | 해당 시 필수 | 테스트 결과서, 스크린샷, 로그, 커밋 |
| 미해결 이슈 | 필수 | 남은 질문, 위험, 후속 작업 |
| 다음 Run 제안 | 선택 | 이어서 진행할 수 있는 구체 작업 |

출력은 사람에게 설명 가능한 문장과 기계가 읽을 수 있는 구조를 함께 갖는 것이 좋다.

권장 출력 형식:

```yaml
run_id: RUN-001
status: Completed
changed_files:
  - docs/examples/board-with-login/sample-app/app/api/posts.py
related_ids:
  - REQ-005
  - AC-007
  - PGM-005
verification:
  - command: python -m pytest tests
    result: passed
evidence:
  - DOC-QA-G4-002_Test-Result_v0.1.md
open_issues: []
```

## 5. Gate별 실행 규칙

| Gate | 에이전트 역할 | 완료 조건 |
| --- | --- | --- |
| P0 | 배경, 제약, 참조문서 파악 | 질문/가정/위험이 기록됨 |
| G1 | 요구사항과 인수기준 정리 | `REQ`, `NREQ`, `AC`가 추적표에 반영됨 |
| G2 | SW 아키텍처, 기능, 화면, 프로그램, DB, 보안 설계 및 설계 검수 | `CNT`, `CMP`, `FLOW`, `ADR`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, 개발표준 연결과 보안/화면/개발표준 검수 완료 |
| G3 | 테스트 계획 작성 | `UT`, `IT`, `PT`, `UI`가 `AC`/`SEC`와 연결됨 |
| G4 | 구현, 테스트, 증적 생성 | 테스트 결과와 화면/로그 증적이 추적표에 연결됨 |
| G5 | 승인, 릴리즈, 인수인계 | 승인본, 변경이력, 릴리즈 증적 정리 |

에이전트는 현재 Gate의 완료 조건을 만족하지 못하면 다음 Gate로 넘어갔다고 선언하지 않는다.

에이전트는 `session.json.current_gate`보다 앞선 Gate의 작업을 임의로 수행하지 않는다. Run 문서의 `gate:` 값은 실제 진행 상태를 바꾸지 않는다. Gate 진행 상태는 `vulcan.py gate-start`, `vulcan.py session`, `vulcan.py check-trace`를 통해 확인하고 갱신한다.

현재 Gate별 금지 예시는 다음과 같다.

| 현재 Gate | 사용자 추가 승인 없이 금지되는 작업 |
| --- | --- |
| `phase0` | 확정 요구사항 작성, 설계 확정, 구현 파일/테스트 코드 생성 |
| `gate1` | 기능/화면/프로그램/DB 설계 확정, 구현 파일/테스트 코드 생성 |
| `gate2` | 테스트 결과서 작성, 구현 파일 생성, 완료된 QA 증적 선언 |
| `gate3` | 구현 파일 생성, 실제 테스트 결과를 완료 증적으로 확정 |
| `impl` | QA 승인, 릴리즈 승인 선언 |
| `gate4` | 미해결 FIND/CR/ISSUE를 숨기고 최종 승인 선언 |

사용자가 완성된 앱이나 기능을 요청해도, 현재 Gate가 앞 단계라면 에이전트는 먼저 현재 Gate 산출물과 다음 Gate 승인 질문을 만들고 멈춘다. 예외적으로 프로토타입 구현이 필요한 경우에는 사용자에게 명시적으로 확인하고, 예외 범위와 후속 정리 항목을 Run의 `open_issues` 또는 `change_requests`에 기록한다.

Gate 1의 인수기준은 요구사항 충족 여부를 판단하는 검증 가능한 문장과 검증 방식까지만 작성한다. `Given/When/Then`, 선행조건, 예외조건, 검증 데이터, 테스트 절차, 자동화 파일명은 Gate 3 테스트케이스 문서에 작성한다.

## 5.1 Implementation Plan과 Build Wave

구현 단계는 작업 규모에 따라 운영 강도를 조절한다. 구현 범위가 중간 이상이거나 subagent, 여러 커밋, 여러 모듈, UI 증적이 함께 필요한 경우에는 `implementation-plan` Run을 만들고 승인된 범위를 여러 `Build Wave`로 나눈다. 작은 단일 Run 구현은 Build Wave를 생략할 수 있다.

| 개념 | 의미 | 산출물 |
| --- | --- | --- |
| Implementation Plan Run | 전체 구현을 Wave로 나누는 운영 Run | `BW-ID`, 의존성, 위임 계획, 테스트/커밋 계획 |
| Build Wave Run | 하나의 검증 가능한 구현 배치 | 코드, 테스트, 추적표 갱신, 검증 결과, 커밋 후보 |

`Build Wave`는 다음 기준을 만족해야 한다.

- 하나의 Wave는 관련 `REQ/AC/PGM/SCR/DB/SEC/UT/IT/UI`를 가진다.
- 하나의 Wave는 독립적으로 검증 가능한 테스트 또는 확인 기준을 가진다.
- 하나의 Wave가 끝나면 요구사항추적표와 Run 기록이 갱신된다.
- 하나의 Wave는 기본적으로 하나의 커밋 후보가 된다.
- Wave 간 의존성이 있으면 Implementation Plan에 순서를 명시한다.
- 구현 중 active Wave는 하나만 둔다. 여러 Wave를 동시에 코드 수정 상태로 진행하지 않는다.
- 하나의 Wave 내부에서는 수정 범위가 겹치지 않는 subagent 병렬 작업을 허용할 수 있다.
- Orchestrator는 기능 구현의 주 작성자가 아니라 작업지시, 검토, 통합, 검증, 상태 갱신 책임자다.
- Wave 시작과 완료는 `session.json` 수동 편집이 아니라 `vulcan.py wave-start`, `vulcan.py wave-complete`, `vulcan.py sync-session`으로 처리한다.

Implementation Plan이 Wave 4개를 정의했다면, 실행 기록은 보통 다음처럼 1:N 구조가 된다.

```text
RUN-010_implementation-plan-...md
RUN-011_build-wave-BW-001_...md
RUN-012_build-wave-BW-002_...md
RUN-013_build-wave-BW-003_...md
RUN-014_build-wave-BW-004_...md
```

`Implementation Plan Run`은 전체 지도이고, `Build Wave Run`은 해당 Wave의 작업지시서이자 결과보고서다. subagent에게는 전체 프로젝트 맥락을 과도하게 넘기기보다 해당 Wave Run의 목표, 관련 ID, 수정 허용 범위, 테스트, 완료 조건을 전달한다.

Build Wave를 생략하는 경우 구현 Run은 다음을 남긴다.

- 생략 이유
- 단일 Run으로 처리할 구현 범위
- 관련 ID
- 실행할 테스트와 검증 명령
- 추적표 갱신 기준
- 커밋 메시지 후보

권장 상태값:

| 상태 | 의미 |
| --- | --- |
| `Planned` | 계획됨 |
| `In Progress` | 구현 중 |
| `Implemented` | 코드 작성 완료 |
| `Verified` | Wave 검증 통과 |
| `Blocked` | 질문, 설계 누락, 환경 문제로 중단 |
| `Rolled Back` | 해당 Wave 변경을 되돌림 |

Gate 2에서 Gate 3로 넘어가기 전에는 다음 검수가 완료되어야 한다.

SW 아키텍처는 Gate 2 안에서 점진적으로 성숙시킨다.

| 시점 | Orchestrator 책임 | 권장 검증 |
| --- | --- | --- |
| Gate 2 시작 | Architecture Draft를 만들고 C1/C2, 주요 CNT, 주요 ADR 후보, Pending 항목을 드러낸다 | `python vulcan.py check-architecture --level draft` |
| 상세 설계 작성 후 | 기능/프로그램/API/DB/화면/보안가이드 내용을 아키텍처의 CMP/FLOW/품질속성/상세 설계 연결로 되돌려 반영한다 | `python vulcan.py check-architecture --level baseline` |
| Gate 3 진입 전 | Gate 3 테스트 설계에 영향을 주는 Pending을 닫거나 RISK/ASM/Q/ISSUE/CR로 분류한다 | `python vulcan.py check-trace` |

| 검수 | 책임 Persona | 최소 확인 |
| --- | --- | --- |
| 요구사항 대비 설계 검수 | `review` 또는 `design` | 모든 `REQ/AC`가 `FUNC/SCR/PGM/DB/SEC` 중 필요한 산출물과 연결됨 |
| 보안 검수 | `security-review` | `SECURITY_BASELINE.md` 기준 보안항목 누락 여부, `KISA/SR`, `OWASP`, `CWE` 매핑 |
| 화면 검수 | `screen-review` | 화면 목록, 화면 상태, 와이어프레임/시안, 메시지, UI 증적 기준 |
| UI 품질 검수 | `ui-review` | 구현자가 임의 해석하지 않도록 UI 기준선 유형, 레이아웃 밀도, 상태 표현, 모바일 기준이 충분한지 확인 |
| 개발표준 검수 | `development-review` | 언어/프레임워크, 기술스택 베이스라인, 패키지 구조, 메시지 관리, 주석/코딩/테스트 컨벤션, 빌드/실행 명령 |

위 검수 중 하나라도 `Failed` 또는 `Blocked`이면 Gate 3 테스트 설계로 넘어가지 않는다.

화면이 있는 기능은 다음 흐름을 가진다.

| 단계 | 책임 Persona | 최소 산출물 |
| --- | --- | --- |
| Gate 2 | `screen-design` | `SCR-ID`, 화면 상태, 시안/와이어프레임 경로, 기준 viewport, 비교 기준 |
| Gate 2 Review | `screen-review`, `ui-review` | 화면 누락, 상태 누락, 시안 연결, 증적 가능 여부와 UI 품질 기준선 검토 |
| Gate 3 | `test-design` | `UI-ID`, viewport, 사용자 흐름, 기대 화면, 캡처/비교 기준 |
| Impl | `build` | 시안을 실제 UI 코드로 구현하고 desktop/mobile에서 확인 |
| Gate 4 | `evidence`, `screen-review` | Playwright 스크린샷, 시안 대비 차이, UI Finding 또는 승인 |

외부에서 가져온 시안도 Anvil 산출물이다. 외부 Figma, 이미지, PPT, 손그림, 기존 시스템 캡처는 화면설계서에 출처와 경로를 기록하고 `SCR-ID`와 연결해야 한다.

Implementation Run은 다음 조건을 만족해야 완료할 수 있다.

| 조건 | 최소 확인 |
| --- | --- |
| 개발표준 준수 | 개발표준정의서가 Draft가 아니고 언어, 기술스택 베이스라인, 구조, 메시지, 주석, 테스트, 보안 기준, 필수 검증 명령을 가진다. |
| 구현 파일 연결 | 요구사항추적표의 증적에 실제 구현 파일 경로가 연결된다. |
| 추적 ID 표시 | 구현 또는 테스트 파일 안에 관련 `REQ`, `PGM`, `SCR`, `SEC`, `UT`, `IT` 중 하나 이상의 ID가 남는다. |
| 테스트 실행 | Gate 3에서 정의한 테스트와 개발표준정의서의 필수 검증 명령이 실행되고 Pass/Fail/Skip/Not Run 상태가 기록된다. |
| 화면 구현 검증 | 화면이 있으면 기준 시안 또는 화면설계서와 실제 구현 화면을 desktop/mobile에서 확인한다. |
| 문서 갱신 | 구현 결과가 테스트케이스, 추적표, Run 기록에 반영된다. |

## 6. 승인과 질문 규칙

에이전트는 다음 상황에서 작업을 멈추고 질문해야 한다.

- 요구사항이 서로 충돌한다.
- 승인된 ID를 변경해야 한다.
- 현재 Gate보다 앞선 산출물, 구현, 테스트, 증적을 생성해야 한다.
- Run Scope 밖의 파일을 수정해야 한다.
- 민감문서 또는 제외 경로를 읽거나 포함해야 한다.
- 보안 기준을 낮추는 선택이 필요하다.
- 테스트 결과를 통과로 볼 수 없는 애매한 상태가 발생한다.
- 개발표준정의서의 필수 검증 명령을 실행하지 못했거나 실행 결과를 남기지 못했다.

다음 상황에서는 에이전트가 합리적으로 판단하고 진행할 수 있다.

- 문서의 기존 패턴과 일치하는 필드 추가
- 명백한 오탈자 수정
- 테스트 통과를 위한 좁은 범위의 구현 보정
- `.gitignore`에 생성물 제외 규칙 추가
- 추적표에 이미 존재하는 ID의 증적 경로 추가

## 7. 산출물 갱신 규칙

에이전트가 코드를 변경하면 최소한 다음 항목을 점검한다.

- 관련 프로그램명세의 `PGM` 설명과 실제 구현이 맞는가
- 관련 화면명세의 `SCR` 설명과 실제 화면이 맞는가
- 관련 테스트케이스의 `UT`, `IT`, `PT`, `UI`가 존재하는가
- 테스트 결과서가 최신 실행 결과를 반영하는가
- 요구사항추적표의 상태와 증적이 갱신되었는가

문서 갱신이 이번 Run 범위 밖이면 `ISSUE` 또는 다음 Run 제안으로 남긴다.

## 8. Adapter 책임

Adapter는 Core 규약을 특정 에이전트 실행 방식으로 변환한다.

Adapter가 책임지는 것:

- Core 입력 계약을 모델별 프롬프트나 명령으로 변환
- 세션 컨텍스트 길이에 맞춰 문서 요약/선별
- 도구 사용 가능 여부 확인
- 실행 결과를 Core 출력 계약으로 정규화
- 실패, 중단, 사용자 질문을 일관된 상태로 기록

Adapter가 책임지지 않는 것:

- Core ID 체계 임의 변경
- 프로젝트 산출물 종류 임의 축소
- 승인 없이 Gate 완료 기준 완화
- 민감문서 커밋 또는 외부 전송

## 9. 상태 값

Run 상태는 다음 값을 사용한다.

| 상태 | 의미 |
| --- | --- |
| Planned | 실행 전 |
| Running | 실행 중 |
| Blocked | 질문, 승인, 환경 문제로 중단 |
| Completed | 완료 조건 충족 |
| CompletedWithIssues | 주요 결과는 있으나 후속 이슈 존재 |
| Failed | 완료 조건 미충족 |
| Cancelled | 사용자 또는 상위 계획에 의해 취소 |

## 10. 실패 기록 규칙

실패는 숨기지 않는다.

실패한 Run은 다음을 남긴다.

- 실패한 명령 또는 작업
- 관찰된 오류
- 영향받는 ID
- 재시도 여부
- 후속 조치 제안

예시:

```yaml
run_id: RUN-004
status: Blocked
blocked_reason: "브라우저 캡처 도구가 networkidle 대기 옵션을 지원하지 않음"
affected_ids:
  - UI-003
resolution: "load 상태 대기와 명시적 안정화 대기로 캡처 재시도"
```

## 11. 최소 파일 구조

프로젝트는 에이전트 실행 기록을 다음 위치 중 하나에 둘 수 있다.

```text
docs/runs/
docs/examples/{sample}/runs/
```

권장 파일명:

```text
RUN-001_{run-name}_v0.1.md
```

Adapter별 내부 로그는 필요하면 다음 위치를 사용한다.

```text
docs/adapters/{adapter-name}/
```

단, 모델별 내부 로그에는 민감정보, 토큰, 외부 비공개 데이터가 포함되지 않아야 한다.
