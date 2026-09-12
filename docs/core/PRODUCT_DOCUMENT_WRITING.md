# Product Document Writing

Product 문서를 새로 쓰거나 보완할 때 사용하는 작성 경로다. `init`의 6종 진입 원장과 Gate별 필수 목록은 유지하며, 아래 상세 파일은 필요할 때만 만든다. Audit/PoC 작성 기준을 대체하지 않는다.

## 0. 업무에서 요구로 연결한다

새 제품/기능을 정의하거나 액터·권한, 상태 전이, 승인·반려·재시도, 외부 책임, 데이터 의미/보존, 성공 기준이 바뀔 때 사용한다. 오탈자나 동작 변화 없는 수정은 영향 절만 고친다. 이미 확인한 답은 근거를 재사용하고 모든 질문을 다시 하지 않는다.

| 진행 | 총괄이 사용자와 확인할 내용 | 남길 원본 |
| --- | --- | --- |
| 문제와 경계 | 누가 어떤 일을 끝내야 하는가, 제품과 사람/외부 시스템의 책임은 어디까지인가 | Brief의 목표/범위. 상세가 필요하면 업무 흐름 원본 |
| 대표 한 건 | 시작 사건, 액터별 행동·인계, 종료 결과와 중요한 예외를 한 건으로 재생 | 기존 기능 상세 또는 선택 `PRODUCT_BUSINESS_FLOW_TEMPLATE.md` |
| 규칙·예시·질문 | 합의한 동작에 입력/행동/관측 결과를 붙인다. 답 없는 권한·상태·보존 정책은 질문으로 구분 | 같은 흐름의 규칙/예시/열린 결정 절. 대화 전문이나 질문 원장을 추가하지 않음 |
| 요구·AC 후보 | 예시가 의도와 맞는지 되짚고 기존 REQ/AC의 변경 후보와 영향을 연결 | 요구 상세의 현재 원본. 규칙을 행마다 복제하지 않고 원본 절 링크 사용 |
| 설계·시험 연결 | 합의 범위의 API/DB/UI/보안 조건과 관측할 기대값/방법을 작성 | 해당 설계·시험 원본. 계획은 실행 결과가 아님 |

문서/템플릿의 각 절은 별도 Gate나 승인 단계가 아니다. 중요한 질문은 한두 개씩 묻고 사용자 답·기존 정책·에이전트 가정을 구분한다. **사용자 답 하나는 전체 설계 확정, 구현 허가, 인수 승인이 아니다.** 미정 항목에는 영향 범위와 다음 확인 담당/시점을 남긴다. 영향받는 계약의 확정은 보류하되 독립적으로 진행 가능한 승인 범위까지 중단하지 않는다. 승인된 조건과 충돌하면 기존 변경 절차를 따른다.

후보 REQ/AC·미합의 대안은 해당 제목 아래 기존 `<!-- vulcan:state=candidate -->` 표식으로 분리한다. Draft metadata나 '후보'라는 설명만으로 모든 소비자가 제외한다고 가정하지 않는다. 채택할 때만 실제 합의 근거와 적용 범위를 확인하고 원본 절을 현행화한다. `current` 표식도 사용자 승인 증명은 아니다. 열린 질문을 후보 절로 옮겼다는 이유로 관련 현재 계약이 구현 가능해지는 것은 아니며 총괄이 영향을 판단한다.

진행 기법의 배경은 프레임워크의 [Discovery Guide](https://github.com/zeni-on/vulcan-anvil-ex/blob/main/docs/reference/PRODUCT-DISCOVERY-AND-VALIDATION-GUIDE.md)에 둔다. 모든 참조 표준을 읽거나 별도 방법론/도구를 설치할 필요는 없다. 이 문서가 배포되는 운영 지침이며 adapter별로 절차를 복제하지 않는다.

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
| 업무 경계·흐름 / 총괄·업무 담당 | `PRODUCT_BRIEF.md` | `docs/artifacts/01-requirements/<domain>-flow.md` | `PRODUCT_BUSINESS_FLOW_TEMPLATE.md`: 액터 책임, 시작/종료, 정상/예외 흐름, 규칙·예시·질문. 작은 기능은 기존 요구 상세에 작성 |
| 요구·AC / 요구 담당 | `PRODUCT_BRIEF.md` | `docs/artifacts/01-requirements/*.md` | `PRODUCT_REQUIREMENTS_TEMPLATE.md`: 요구 동작, 조건/예외, 관측 가능한 AC, 적용 제약 |
| 아키텍처 / 설계 | `PRODUCT_ARCHITECTURE.md` | `docs/artifacts/02-design/architecture/*.md` | 기존 Architecture 양식의 필요한 절: 경계, 구성, 실행/배포 뷰, 품질과 위험 |
| API / 설계·백엔드 | `PRODUCT_CONTRACTS.md` | `docs/artifacts/02-design/api/*.md` | `PRODUCT_API_CONTRACT_TEMPLATE.md`: 권한, 입출력, 오류, 호환성, 구현 경계 |
| 데이터 / 설계·데이터 | `PRODUCT_CONTRACTS.md` | `docs/artifacts/02-design/data/*.md` | `PRODUCT_DATA_MODEL_TEMPLATE.md`: 용어, 필드 의미, ERD, 키/제약, 보존·이관 |
| UX/UI / 경험설계 | `PRODUCT_CONTRACTS.md` | `docs/artifacts/02-design/screen/*.md` | `PRODUCT_UI_CONTRACT_TEMPLATE.md`: 여정, 화면 상태, 디자인/퍼블리싱 기준, 접근성 |
| 보안 / 설계·보안 | Architecture와 Contracts의 해당 진입 절 | `docs/artifacts/02-design/security/*.md` | `PRODUCT_SECURITY_CHECKLIST_TEMPLATE.md`: 신뢰 경계, 보호 정책, SEC 계약, 검증 대상 |
| 개발 기준 / 개발 | Architecture와 Contracts의 해당 진입 절 | `docs/artifacts/02-design/development-standard/*.md` | `PRODUCT_ENGINEERING_GUIDE_TEMPLATE.md`: 도구 기준, 코드 관례, 시험/빌드/배포 절차 |
| 시험 정의 / 품질 | `REGRESSION_AND_RELEASE_REPORT.md` | `docs/artifacts/03-test/*.md` | `PRODUCT_TEST_PLAN_TEMPLATE.md`: REG/SEC-REG, 선행조건, 입력/행동/기대값, 방법 |
| 실제 실행 / 품질 | `REGRESSION_AND_RELEASE_REPORT.md` | `docs/artifacts/04-review/<batch>/*.md` | `PRODUCT_VERIFICATION_RESULT_TEMPLATE.md`: 시험 범위·정의, 실행/관측, 증적, 미완료 의무 |
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

업무 흐름은 Brief에서, 관련 규칙/예시는 요구 상세에서 링크한다. SCN 정의는 Brief, REQ/AC 정의는 요구 원본 한 곳에 두고 업무 흐름에 ID 표를 복사하지 않는다. 시험 표는 관련 REQ/AC와 입력/행동/기대값/방법을 연결한다. 현행 내용 검사·조회가 지원하는 `01-requirements`를 사용하므로 새 소유 폴더나 `00-discovery` 자동 수집을 추가하지 않는다. 기존 프로젝트의 다른 경로는 자동 이동하지 않는다.

보안 상세는 Architecture의 보안 결정 절과 Contracts의 SEC 진입점에서 동일 원본을 가리킬 수 있다. 테스트 상세는 보고서의 계획 절, 현재 실행은 결과 절에서 연결한다. 다른 원장으로 가는 탐색 링크는 그 원장의 내용을 복제해 검사하지 않는다. 소유 경로와 입력 제한은 [Current Context And Evidence 3.2](CURRENT_CONTEXT_AND_EVIDENCE.md#32-product-내용-검사추적통계-호환)를 따른다.

## 4. 현재 계약과 실행 이력을 분리한다

- 요구/설계에는 현재 승인 범위의 조건을 적는다. 작업 일지, 로그 전문, 자기평가, 과거 Delta는 붙이지 않는다. 변경 이유는 기존 CR/ADR/Git에 연결한다.
- 테스트 정의의 기대값과 실제 결과는 별개다. 계획에 있는 `Planned`를 실행 대신 `Pass`로 고치지 않는다.
- Gate 3에서 미리 만든 결과 표의 `Not Run`은 시험 계획 완료를 단독으로 차단하지 않으며 미실행 안내로 남는다. 실제 `Fail`, `Blocked`, `environment_blocked`와 상충된 결과는 유지한다. Gate 4 이후에는 필요한 실제 실행/성공 결과를 요구한다. 이 예외는 Product Gate 3에만 적용하며 Impl self-check와 다른 profile의 기준을 완화하지 않는다.
- 실행 묶음에는 시험 대상과 당시 테스트 정의, 실제 명령·결과·로그를 연결한다. 테스트 정의의 revision은 유지하되 별도 Git 기준이나 소스 스냅샷은 요구하지 않는다. 검증 JSON은 기존 증적 칸으로 연결한다.
- 현재 실행 파일의 원본 결과는 보존한다. 재시험은 새 실행 묶음에 적고, 원장은 적용 대상/범위가 일치하는 현재 결과를 가리킨다. 과거 링크는 `history`로 표시한 절로 옮긴다. 모든 과거 실행을 현재 검사로 다시 읽게 하지 않는다.
- `current`는 현재 비교 대상으로 선택했다는 뜻이지 승인/Pass가 아니다. 현재 Fail/Not Run/환경 차단은 그대로 보고한다. 미완료 시험/결함은 기존 FIND/ISSUE/CR의 관리 원본과 연결하고 범위 축소만으로 종료하지 않는다.

## 5. Gate·인계·기존 프로젝트

표식 없는 기존 Product는 Phase 0/Gate 1에서 업무 흐름·요구/AC, Gate 2에서 설계/공통 기준, Gate 3에서 시험 정의, Gate 4에서 실제 실행, Gate 5에서 릴리즈 판단을 담당자가 갱신한다. `process_model`이 있는 실험 Product는 [CLI Guide 4.1](ORCHESTRATOR_CLI_GUIDE.md#41-개발용-product-반복-프로세스)에 따라 planning 안에서 업무·요구·설계·시험 계획을 반복한다. 템플릿의 legacy `gate_scope`를 추가 Gate 전환 지시로 해석하지 않는다. 일반 활성화는 별도이며 이 작성 지침으로 표식을 추가하지 않는다. 파일이 분리되어도 승인 시점과 책임은 바뀌지 않는다. 구현 담당자는 승인 범위의 코드/테스트와 문서 변경 후보를 반환하고 총괄이 공통 추적/승인 상태를 관리한다.

전달에는 목표/범위, **정확한 원본 경로·ID/절**, 적용 공통 조건, 검증 기준을 포함한다. 도구가 추천한 ID만 넘기거나 상세를 Run에 복사하지 않는다. Run/Wave는 기존 Product 선택 정책을 유지한다.

`upgrade`는 프레임워크 지침·템플릿을 갱신하지만 작성된 Product 원장/상세/증적을 이동하거나 재작성하지 않는다. 열린 역할 작업에도 새 작성 위치를 알려 같은 내용을 두 곳에 쓰지 않게 한다.

기존 승인 문서의 재배치는 아직 자동화하지 않는다. 승인/소스 비교, release 소비자, Dashboard 전체 호환 확인과 별도 이동 승인 후 기능 하나부터 진행한다. 현재는 기존 원본을 유지하고 새 상세가 필요한 승인 범위에 이 작성 기준을 적용한다. 링크 추가 후 `status --check`와 필요한 조회/통계를 확인하되, 검사 성공을 내용 보존이나 승인 증명으로 대신하지 않는다.
