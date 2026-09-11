# 변경 영향도 분석 Skill

## 사용할 때

요청이 요구사항, 인수기준, 아키텍처, 데이터 모델, 보안 기준선, 릴리즈 범위, 승인된 설계를 바꿀 가능성이 있을 때 사용한다.

Product의 기록과 실행자는 [PRODUCT_PROFILE_BASELINE.md](../../../core/PRODUCT_PROFILE_BASELINE.md) 7절을 따른다. 기존 CR/이슈/작업 요약을 사용하고 Run은 선택하며, 필요한 영향 계약만 읽는다. Audit/PoC는 아래 필수 입력과 Run 절차를 유지한다. 계약 변경의 승인 경계는 어느 profile에서도 생략하지 않는다.

## 필수 입력

- `docs/core/CHANGE_CONTROL_PROCESS.md`
- `docs/core/TRACEABILITY_RULES.md`
- 관련 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI` 문서
- 기존 백로그 또는 `CR` 기록이 있으면 해당 문서

## 절차

1. 요청된 변경을 한 문장으로 설명한다.
2. 현재 범위 안의 결함인지, 진짜 변경인지 판단한다.
3. 결함이면 `qa-fix-loop.md`로 전환한다.
4. 진짜 변경이면 `DOC-PM-CR-NNN_*_v0.1.md` 상세 변경요청서를 만들거나 갱신하고, `DOC-PM-G0-001_Change-Request_v0.1.md` 관리대장에 등록한다.
5. 영향받는 ID, 문서, 코드 영역, 테스트, 증적, 릴리즈 노트를 식별한다.
6. 다시 진행해야 할 최소 Gate를 결정한다.
7. 즉시 반영하지 않는 승인/보류 항목만 Backlog와 연결한다.
8. 승인된 CR의 작업 범위를 확정한다. Product는 기존 CR/이슈/작업 요약으로 실행할 수 있다. Audit/PoC 또는 Run을 선택한 Product는 CR/RUN에 같은 scope를 기록한다.

## Gate 진행 기준

| 변경 유형 | 최소 Gate |
| --- | --- |
| 요구사항 또는 인수기준 변경 | Gate 1 |
| 기능, 화면, 프로그램, DB, 아키텍처, 보안 설계 변경 | Gate 2 |
| 테스트 전략 또는 커버리지 변경만 있음 | Gate 3 |
| 승인된 구현 범위 안의 변경 | G4 QA 수정 범위 (Product Run은 선택, Audit/PoC는 QA Fix Run) |
| 릴리즈 범위 또는 승인 변경 | Gate 5 |

## 출력

다음을 반환한다.

- `CR` 또는 `FIND` 권고
- CR이면 상세 변경요청서 경로와 CR 관리대장 갱신 여부
- 영향받는 ID
- 영향받는 산출물
- 다시 진행할 Gate
- 작업 scope와 필요한 경우 Run 문서 후보
- 미해결 질문 또는 승인 필요 사항
