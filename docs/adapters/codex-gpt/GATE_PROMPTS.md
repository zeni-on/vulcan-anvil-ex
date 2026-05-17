# Codex/GPT Gate Prompts

> 목적: Gate별 Codex/GPT 실행 체크리스트를 짧게 제공한다. 상세 규칙은 `docs/core/`와 관련 skill을 읽는다.

## 1. 공통 규칙

- 먼저 `session.json.current_gate`와 사용자 요청을 확인한다.
- 현재 Gate보다 앞선 산출물, 구현, 테스트, 증적을 사용자 승인 없이 만들지 않는다.
- 모든 의미 있는 변경은 관련 `REQ/AC/FUNC/SCR/PGM/API/DB/SEC/UT/IT/UI/FIND/CR/RUN`과 연결한다.
- 실행하지 않은 테스트를 통과로 보고하지 않는다.
- 각 Gate 산출물 완료 후에는 다음 Gate로 진행하지 말고 산출물 요약, 미해결 항목, 다음 Gate 제안, 사용자 승인 질문을 남기고 대기한다.
- 대화상 명시 승인 없이 Run 또는 승인 문서에 User Approved로 기록하지 않는다.
- 운영 상태를 요구사항, 제약, 성공 기준에 쓰지 않는다.
- `docs/ref-docs/`는 민감 자료일 수 있으므로 커밋하지 않는다.
- Claude 전용 `.claude/` 문서는 Codex 실행 계약으로 보지 않는다.

## 2. Phase 0 Discovery

목표: 아이디어, 문제, 범위, 질문, 위험을 정리한다.

해야 할 일:
- 프로젝트 배경과 사용자를 정리한다.
- 요구사항 후보, 질문, 위험, 가정을 구분한다.
- 확정되지 않은 항목은 Backlog 또는 질문으로 남긴다.

하지 않을 일:
- 구현, 테스트 코드, 상세 설계를 만들지 않는다.

완료 기준:
- Project Brief, Scope, As-Is/To-Be, Risk/Assumption 또는 관련 Run 갱신
- Gate 1 후보와 미결 질문 정리

## 3. Gate 1 Requirements

목표: 테스트 가능한 요구사항과 인수기준을 확정한다.

해야 할 일:
- `REQ/NREQ/AC`를 분리한다.
- 요구사항정의서와 추적표를 갱신한다.
- 보안/비기능 요구 후보를 누락하지 않는다.

주의:
- 설계와 구현 상세로 내려가지 않는다.
- `Given/When/Then`, 선행조건, 테스트 데이터는 Gate 3 테스트케이스로 넘긴다.

완료 기준:
- 모든 상세 요구사항에 AC 또는 명시적 제외 사유가 있다.
- Gate 2로 넘길 질문과 승인 필요 사항이 정리되어 있다.

## 4. Gate 2 Design

목표: 승인된 요구사항을 아키텍처, 기능, 화면, 프로그램/API, DB, 보안, 개발표준으로 전개한다.

해야 할 일:
- `docs/core/GATE2_DESIGN_SEQUENCE.md`를 읽고 이번 Run이 Gate 2 설계 순서의 어디에 있는지 기록한다.
- 권장 순서는 Kickoff/범위 고정 -> SW Architecture Draft -> 화면/사용자 흐름 -> 기능 -> 프로그램/API -> 데이터/DB -> 보안 -> 개발표준 -> SW Architecture Baseline 보강 -> 설계 검수다.
- SW 아키텍처는 큰 그림과 Pending/ADR 후보를 먼저 잡고, 상세 설계와 함께 보강한다.
- 화면이 있으면 `SCR-ID`, 화면 상태, 와이어프레임/시안, UI 증적 기준을 기록한다.
- 프로토타입, Figma, 이미지 시안, 기존 화면 캡처가 있으면 단순 참고자료인지 구현 기준인지 구분하고, 구현 기준이면 UI Implementation Contract를 작성한다.
- UI Implementation Contract에는 기준 파일/CSS, 필수 유지 요소, 변경 허용 항목, 변경 금지 항목, 비교 방식을 포함한다.
- UI 증적 기준은 화면 단위가 아니라 기본/오류/성공/전환 상태별 `UI-001-01` 형식으로 분리한다.
- 보안가이드는 구현 가능한 구체 값, 정책, 오류 메시지, 검증 ID를 가진다.
- 개발표준은 구현 전에 확정한다.
- 필요한 skill: `screen-design`, `screen-review`, `ui-review`, `security-review`, `development-standard-review`, `data-standard-review`

하지 않을 일:
- 사용자 승인 없이 구현으로 넘어가지 않는다.
- 보안 정책값을 코드나 테스트에서 임의로 만들지 않는다.

완료 기준:
- 설계 산출물과 추적표가 연결되어 있다.
- SW 아키텍처의 Draft/Baseline Candidate/Baseline 성숙도와 Pending/ADR 상태가 기록되어 있다.
- 이번 Run의 Gate 2 순서 위치와 다음 Gate 2 Run 후보가 남아 있다.
- UIREF/prototype이 구현 계약으로 전환되었고 Gate 3/Impl/Gate 4에서 검증 가능한 비교 기준이 있다.
- Gate 3 테스트 설계로 넘길 AC/SEC/NREQ가 식별되어 있다.

## 5. Gate 3 Test Planning

목표: 요구사항, 보안가이드, 화면 기준을 검증 가능한 테스트로 전개한다.

해야 할 일:
- `UT/IT/PT/UI` ID를 정의한다.
- UI 테스트는 상태/시나리오 단위로 작성하고 각 UI-ID에 기대 화면과 캡처 경로를 1:1로 둔다.
- prototype 기반 화면 테스트는 UI Implementation Contract의 필수 유지/변경 허용/금지 항목을 기대결과와 비교 방식에 반영한다.
- 테스트는 `AC/SEC/NREQ/SCR` 중 하나 이상과 연결한다.
- 화면 테스트는 viewport, 기준 시안, 캡처 경로, 비교 기준을 가진다.

주의:
- 보안가이드에 없는 정책값을 테스트가 새로 만들지 않는다.
- 추적표의 테스트 컬럼에 `미정`을 남기지 않는다. 불필요하면 `해당없음`과 사유를 쓴다.

완료 기준:
- 테스트케이스 정의서와 추적표가 갱신되어 있다.
- 구현자가 실행할 검증 명령과 기준이 분명하다.

## 6. Impl / Gate 4 Build And QA

목표: 승인된 설계를 구현하고 테스트, 증적, 추적표를 함께 갱신한다.

해야 할 일:
- 구현 전 `implementation-plan` 또는 단일 구현 Run의 생략 사유를 확인한다.
- 화면 구현 전 관련 SCR의 UI Implementation Contract와 Gate 3 UI 테스트 기준을 확인한다.
- Build Wave가 있으면 현재 `BW-ID` 범위만 수행한다.
- 구현, 테스트, 증적, 추적표, Run 결과를 분리하지 않는다.
- 화면이 있으면 실제 화면을 확인하고 필요한 캡처 증적을 남긴다.
- prototype 기반 화면은 기준 UIREF screenshot과 구현 screenshot의 차이를 기록하고 허용 여부를 판정한다.
- 캡처가 기대 화면을 보여주지 못하면 Pass로 기록하지 않고 FIND 또는 Not Run으로 남긴다.

주의:
- Orchestrator는 구현 주 작성자가 아니다. 구현은 `build` persona/subagent가 맡고 Orchestrator는 검토와 통합을 책임진다.
- 개발표준/보안가이드/테스트케이스가 비어 있으면 구현 완료로 선언하지 않는다.

완료 기준:
- 관련 테스트와 린트 결과가 기록되어 있다.
- 구현 파일, 테스트 파일, 증적 경로가 추적표와 결과서에 연결되어 있다.

## 7. Change Control

목표: 변경 후보를 FIND, CR, ISSUE, Backlog로 분류하고 승인된 변경만 필요한 Gate로 다시 진행한다.

해야 할 일:
- 기준선 변경이면 `DOC-PM-CR-NNN_*` 상세서와 CR 관리대장을 갱신한다.
- 승인된 CR을 처리할 때는 `gate-start` 후 관련 Run 문서를 반드시 만든다.
- scope는 CR 상세서와 Run 문서에 기록한다.
- 문서/설계 검토는 scope 중심으로 하되, 자동화된 단위테스트는 원칙적으로 전체 실행한다.

하지 않을 일:
- 별도 되돌림 흐름을 사용하지 않는다.
- Gate 통과를 막는 Blocker/Major FIND를 Backlog로 미루지 않는다.

## 8. Gate 5 Approval

목표: 산출물, 테스트 결과, 미해결 항목, 승인 조건을 정리한다.

해야 할 일:
- Release Approval 문서를 갱신한다.
- Open FIND/CR/ISSUE/Backlog가 승인 가능한 상태인지 확인한다.
- 릴리즈 또는 인수인계 증적을 연결한다.

완료 기준:
- 승인 여부, 승인 조건, 잔여 위험 수용 여부가 기록되어 있다.
