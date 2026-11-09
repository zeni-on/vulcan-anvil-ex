# Product Verification Result

---
project: {{PROJECT_NAME}}
profile: product
status: Draft
owner_role: QA Owner
created_at: {{GENERATED_DATE}}
---

<!-- 선택 상세: docs/artifacts/04-review/<batch>/results.md. 보고서의 현재 결과 절에서 연결한다. 작성 기준: docs/core/PRODUCT_DOCUMENT_WRITING.md. 같은 실행 묶음에 한 번만 시험 범위와 테스트 정의를 연결하고 실제 실행 후 결과를 채운다. 별도 Git 증적은 요구하지 않는다. -->

## 1. Verification Scope

| 항목 | 기준 / 원본 |
| --- | --- |
| 대상 기능 / 릴리즈 / 환경 | TBD |
| 검증 경계 / 이번에 확인하지 않은 범위 | TBD |
| 시험 대상 / 확인한 동작 | TBD |
| 당시 테스트 정의 / 버전 | TBD |
| 실제 실행 명령 / cwd | TBD |

## 2. Current Execution Results

선행 행동이 실패했으면 증적 칸에 실패한 단계와 실행하지 못한 후속 단계를 나눠 적는다. 재시험이면 이전 실행을 연결하고 제품·시험·기준 중 무엇이 바뀌었는지와 이번에 다시 확인한 범위를 적는다. 예: “3개 TC를 화면 폭 2종에서 6회 실행. 다른 7개는 이전 결과 참조, 이번에는 미실행.”

| REG ID | 실행 일시 | 결과 | 실제 관측 / 로그 / 증적 | 미실행 이유 / 관련 이슈 |
| --- | --- | --- | --- | --- |
| REG-001 | TBD | Not Run | TBD | TBD |

## 3. Current Security Results

| SEC-REG ID | 실행 일시 | 결과 | 실제 관측 / 로그 / 증적 | 미실행 이유 / 관련 이슈 |
| --- | --- | --- | --- | --- |
| SEC-REG-001 | TBD | Not Run | TBD | TBD |

## 4. Remaining Obligations

미완료 시험/결함의 기존 FIND/ISSUE/CR 원본, 적용 조건, 종료에 필요한 근거: TBD

<!-- 실제 결과는 Pass / Fail / Not Run / environment_blocked 중 관측대로 기록한다. REG-API-001처럼 이름이 붙은 시험 ID도 사용할 수 있으며 한 행에 하나의 ID를 둔다. 합산 건수는 관측 칸에 쓰고 개별 시험 결과를 대신하지 않는다. Current는 현재 비교 대상이며 승인/Pass 표식이 아니다. 개발 대역 성공은 실제 외부 연계/사용자 인수/운영 성공이 아니다. 재시험 시 이전 실행 결과를 덮어쓰지 않는다. 인수·릴리즈 승인 판단은 이 실행 문서의 책임이 아니다. -->
