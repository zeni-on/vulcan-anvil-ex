# Product Document Writing

Product 문서를 새로 쓰거나 보완할 때 사용하는 작성 경로다. `init`의 6종 진입 원장과 Gate별 필수 목록은 유지하며, 아래 상세 파일은 필요할 때만 만든다. Audit/PoC 작성 기준을 대체하지 않는다.

## 1. 원본을 먼저 정한다

- 먼저 현재 작업의 ID/절과 연결된 공통 조건을 찾는다. 문서 전체나 과거 Run을 매번 읽지 않는다.
- 이미 원본이 있으면 그 위치에서 현행화한다. 원장에 같은 본문을 복사하거나 날짜순 Delta를 추가하지 않는다.
- 새 기능의 조건이 한 행으로 설명되지 않거나 독립 변경/검토가 필요하면 기능·도메인·서비스 단위로 분리한다. REQ마다 파일 하나를 만들거나 파일 수/분량 목표를 강제하지 않는다.
- 각 문서의 기존 제목/metadata에 범위와 책임을 명확히 하고, 현재 적용 기준과 후보/과거 기록을 구분한다. 공통 보안/오류/데이터 정책은 원본 위치와 적용 범위를 참조한다.
- ID는 기존 것을 유지한다. 색인에는 ID/제목/원본 링크만 두며 별도 수동 상태 원장을 늘리지 않는다.

### 1.1 기능이 늘어나거나 변경될 때

| 변경 | 작성 방법 |
| --- | --- |
| 같은 기능의 조건 변경 | 승인 범위의 기존 ID/원본 절을 현행화하고 영향받는 API·데이터·UI·시험 조건을 함께 확인한다. 날짜순 Delta로 현재 조건을 추론하게 하지 않는다. |
| 같은 기능의 작은 확장 | 기존 상세의 해당 절에 추가한다. 요구마다 새 파일이나 새 Run을 만들지 않는다. |
| 독립 기능 추가 | 필요한 분야의 기능별 상세와 새 ID를 추가하고 개요·계약 색인·추적·시험 진입점에서 연결한다. 관계없는 상세를 다시 쓰지 않는다. |
| 기능 폐기/대체 | 기존 ID를 재사용하지 않고 적용 종료와 대체 관계/근거를 보존한다. 미완료 의무를 파일 이동으로 닫지 않는다. |
| 새 검증/릴리즈 | 당시 기준과 실제 결과를 별도 묶음에 보존하고 원장은 적용 범위가 맞는 현재 결과를 가리킨다. 이전 Pass가 새 규격의 Pass를 대신하지 않는다. |

분리 기준은 줄 수보다 독립적인 변경·검토 책임이다. 기존 승인 원본의 이동은 5절의 별도 확인/승인을 따른다. 현재 조건의 이력은 Git/기존 CR·ADR로 찾고, 보존한 실행 결과는 수정하지 않는다. 여러 문서의 서로 다른 계약이 함께 바뀌는 것은 필요한 영향 분석이며 같은 본문을 복제하는 것과 구분한다.

## 2. 작성 위치와 템플릿

아래 템플릿 이름은 `docs/templates/product/` 기준이다. `*.md`는 기능/도메인 이름을 선택한다는 뜻이며 모든 경로를 미리 생성하지 않는다.

| 정보 / 담당 | 현재 진입점 | 필요할 때 둘 상세 원본 | 사용할 템플릿 / 적을 내용 |
| --- | --- | --- | --- |
| 목표·이번 범위 / 총괄·제품 | `PRODUCT_BRIEF.md` | 개요는 원장에 유지 | `PRODUCT_BRIEF_TEMPLATE.md`: 목표, 사용자, 성공 기준, 포함/제외 범위 |
| 요구·AC / 요구 담당 | `PRODUCT_BRIEF.md` | `docs/artifacts/01-requirements/*.md` | `PRODUCT_REQUIREMENTS_TEMPLATE.md`: 요구 동작, 조건/예외, 관측 가능한 AC, 적용 제약 |
| 아키텍처 / 설계 | `PRODUCT_ARCHITECTURE.md` | `docs/artifacts/02-design/architecture/*.md` | 기존 Architecture 양식의 필요한 절: 경계, 구성, 실행/배포 뷰, 품질과 위험 |
| API / 설계·백엔드 | `PRODUCT_CONTRACTS.md` | `docs/artifacts/02-design/api/*.md` | `PRODUCT_API_CONTRACT_TEMPLATE.md`: 권한, 입출력, 오류, 호환성, 구현 경계 |
| 데이터 / 설계·데이터 | `PRODUCT_CONTRACTS.md` | `docs/artifacts/02-design/data/*.md` | `PRODUCT_DATA_MODEL_TEMPLATE.md`: 용어, 필드 의미, ERD, 키/제약, 보존·이관 |
| UX/UI / 경험설계 | `PRODUCT_CONTRACTS.md` | `docs/artifacts/02-design/screen/*.md` | `PRODUCT_UI_CONTRACT_TEMPLATE.md`: 여정, 화면 상태, 디자인/퍼블리싱 기준, 접근성 |
| 보안 / 설계·보안 | Architecture와 Contracts의 해당 진입 절 | `docs/artifacts/02-design/security/*.md` | `PRODUCT_SECURITY_CHECKLIST_TEMPLATE.md`: 신뢰 경계, 보호 정책, SEC 계약, 검증 대상 |
| 개발 기준 / 개발 | Architecture와 Contracts의 해당 진입 절 | `docs/artifacts/02-design/development-standard/*.md` | `PRODUCT_ENGINEERING_GUIDE_TEMPLATE.md`: 도구 기준, 코드 관례, 시험/빌드/배포 절차 |
| 시험 정의 / 품질 | `REGRESSION_AND_RELEASE_REPORT.md` | `docs/artifacts/03-test/*.md` | `PRODUCT_TEST_PLAN_TEMPLATE.md`: REG/SEC-REG, 선행조건, 입력/행동/기대값, 방법 |
| 실제 실행 / 품질 | `REGRESSION_AND_RELEASE_REPORT.md` | `docs/artifacts/04-review/<batch>/*.md` | `PRODUCT_VERIFICATION_RESULT_TEMPLATE.md`: 소스·시험 정의 기준, 실행/관측, 증적, 미완료 의무 |
| 관계·현재 판단 / 총괄 | `PRODUCT_TRACEABILITY.md` | 필요 시 `docs/artifacts/02-traceability/*.md` | 기존 Traceability 양식: SCN/REQ/계약/구현/시험/증적 연결과 판단 근거 |
| 결정 / 결정 담당·총괄 | `ADR_LOG.md` | 필요 시 `docs/artifacts/02-design/architecture/*.md` | 기존 ADR 양식: 배경, 선택, 대안, 영향, 승인/대체 근거 |

복잡한 기능 흐름·공개 프로그램·서비스 간 연동은 `02-design/function/`, `program/`, `integration/`에 필요한 계약만 쓸 수 있다. 운영 절차는 `docs/operations/`, 사용자 안내는 `docs/user-guide/`, 릴리즈별 기록은 `07-release/`에 둔다. 이것들을 새 필수 파일로 만들거나 모든 private helper에 설계 ID를 붙이지 않는다. 운영/사용 안내는 현재 내용 검사 resolver가 자동으로 포함하지 않으므로 담당자가 직접 확인한다.

## 3. 원장과 상세를 연결한다

현재 도구는 원장 본문에 있는 **상대 Markdown 링크**를 따라 읽는다. 경로를 backtick이나 `related_documents`에만 적으면 검사 입력으로 따라가지 않는다. 표의 같은 첫 ID 셀을 여러 표에 정의하면 충돌할 수 있으므로 본문 정의는 한 번만 쓰고 색인/관계 참조는 링크로 쓴다.

예를 들어 `PRODUCT_CONTRACTS.md`에서 API 상세를 가리키는 색인은 아래 모양이다. 실제 파일/앵커가 생긴 뒤 연결한다.

```markdown
| 계약 | 제목 | 원본 |
| --- | --- | --- |
| [API-001](../artifacts/02-design/api/tasks.md) | 작업 등록 | 같은 링크의 상세가 원본 |
```

상세에는 `### API-001` 제목과 실제 입출력/오류 조건을 쓴다. API 템플릿의 Surface/검증/구현 경계는 형제 절이므로 진입 링크는 전체 파일을 가리킨다. 절 앵커로 좁히려면 필요한 조건이 모두 해당 절과 하위 절에 있거나 별도로 명시 연결되었는지 확인한다. 원장에 상세 정의 행을 그대로 남겨 두지 않는다. SCN 추적 행 자체는 관계 원장이므로 기존 열 구조와 실제 ID를 유지한다. 같은 API를 여러 관점의 표로 설명할 때도 첫 ID 셀은 링크 참조로 바꾸거나 항목/값 표를 사용한다.

보안 상세는 Architecture의 보안 결정 절과 Contracts의 SEC 진입점에서 동일 원본을 가리킬 수 있다. 테스트 상세는 보고서의 계획 절, 현재 실행은 결과 절에서 연결한다. 다른 원장으로 가는 탐색 링크는 그 원장의 내용을 복제해 검사하지 않는다. 소유 경로와 입력 제한은 [Current Context And Evidence 3.2](CURRENT_CONTEXT_AND_EVIDENCE.md#32-product-내용-검사추적통계-호환)를 따른다.

## 4. 현재 계약과 실행 이력을 분리한다

- 요구/설계에는 현재 승인 범위의 조건을 적는다. 작업 일지, 로그 전문, 자기평가, 과거 Delta는 붙이지 않는다. 변경 이유는 기존 CR/ADR/Git에 연결한다.
- 테스트 정의의 기대값과 실제 결과는 별개다. 계획에 있는 `Planned`를 실행 대신 `Pass`로 고치지 않는다.
- Gate 3에서 미리 만든 결과 표의 `Not Run`은 시험 계획 완료를 단독으로 차단하지 않으며 미실행 안내로 남는다. 실제 `Fail`, `Blocked`, `environment_blocked`와 상충된 결과는 유지한다. Gate 4 이후에는 필요한 실제 실행/성공 결과를 요구한다. 이 예외는 Product Gate 3에만 적용하며 Impl self-check와 다른 profile의 기준을 완화하지 않는다.
- 실행 묶음에는 당시 소스와 테스트 정의의 Git 기준 또는 보존 스냅샷을 한 번 연결한다. 미커밋 변경을 포함했다면 HEAD만 검증했다고 하지 않는다. 검증 JSON은 기존 증적 칸으로 연결한다.
- 현재 실행 파일의 원본 결과는 보존한다. 재시험은 새 실행 묶음에 적고, 원장은 적용 대상/범위가 일치하는 현재 결과를 가리킨다. 과거 링크는 `history`로 표시한 절로 옮긴다. 모든 과거 실행을 현재 검사로 다시 읽게 하지 않는다.
- `current`는 현재 비교 대상으로 선택했다는 뜻이지 승인/Pass가 아니다. 현재 Fail/Not Run/환경 차단은 그대로 보고한다. 미완료 시험/결함은 기존 FIND/ISSUE/CR의 관리 원본과 연결하고 범위 축소만으로 종료하지 않는다.

## 5. Gate·인계·기존 프로젝트

Gate 1에서 요구/AC, Gate 2에서 설계/공통 기준, Gate 3에서 시험 정의, Gate 4에서 실제 실행, Gate 5에서 릴리즈 판단을 담당자가 갱신한다. 파일이 분리되어도 승인 시점과 책임은 바뀌지 않는다. 구현 담당자는 승인 범위의 코드/테스트와 문서 변경 후보를 반환하고 총괄이 공통 추적/승인 상태를 관리한다.

전달에는 목표/범위, **정확한 원본 경로·ID/절**, 적용 공통 조건, 검증 기준을 포함한다. 도구가 추천한 ID만 넘기거나 상세를 Run에 복사하지 않는다. Run/Wave는 기존 Product 선택 정책을 유지한다.

`upgrade`는 프레임워크 지침·템플릿을 갱신하지만 작성된 Product 원장/상세/증적을 이동하거나 재작성하지 않는다. 열린 역할 작업에도 새 작성 위치를 알려 같은 내용을 두 곳에 쓰지 않게 한다.

기존 승인 문서의 재배치는 아직 자동화하지 않는다. 승인/소스 비교, release 소비자, Dashboard 전체 호환 확인과 별도 이동 승인 후 기능 하나부터 진행한다. 현재는 기존 원본을 유지하고 새 상세가 필요한 승인 범위에 이 작성 기준을 적용한다. 링크 추가 후 `status --check`와 필요한 조회/통계를 확인하되, 검사 성공을 내용 보존이나 승인 증명으로 대신하지 않는다.
