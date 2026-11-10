# Vulcan-Anvil Ex Delivery Profiles

> 상태: 초안 v0.2
> 목적: 프로젝트 성격에 따라 문서 깊이, Gate 엄격도, 승인 절차, 증적 수준을 조절하는 기준을 정의한다.

## 1. 배경

Vulcan-Anvil Ex는 감리 대응형 프로젝트에서 강하게 동작하도록 설계되었다.
하지만 모든 작업이 공공/SI/감리 수준의 산출물과 검수 강도를 필요로 하지는 않는다.

내부 검증, 제품/업무 앱 개발, 개인 기능 개발에 같은 절차를 적용하면 개발보다 문서와 검수 비용이 더 커질 수 있다.
반대로 감리 대응 프로젝트에서 절차를 너무 줄이면 요구사항, 설계, 테스트, 증적, 변경관리의 추적성이 무너질 수 있다.

따라서 Vulcan-Anvil Ex는 프로젝트 성격별 기본값 묶음인 `Delivery Profile`을 둔다.

## 2. 용어

`Delivery Profile`은 프로젝트 성격에 따라 다음 항목의 기본 강도를 조절하는 실행 프로파일이다.

- 문서 깊이
- Gate 엄격도
- 사용자 승인 지점
- 테스트와 증적 수준
- 변경관리와 릴리즈 관리 방식
- 대시보드에서 강조할 상태 정보

Profile은 Core 규칙을 없애는 예외가 아니다.
공통 계약·추적성·실제 검증·승인 경계는 유지하되, 프로젝트 목적과 프로세스 모델에 맞게 산출물 깊이와 검증 범위를 조절한다. Product의 Run/Wave는 선택 사항이며 기본 운영은 세 구간 반복이다.

Profile은 별도 Core 문서 세트가 아니라 `Core + Profile Overlay`로 운영한다.
두 프로파일의 규칙을 따로 복제하지 않고, 동일한 Core 문서와 명령을 사용하되 산출물 필수 여부, 검사 엄격도, 승인 지점, 증적 수준만 Profile Overlay로 조정한다.
Profile이 달라져도 Run, ID, Traceability, Gate, Worker, QA의 기본 의미는 바뀌지 않는다.

## 3. Profile 분류

v0.6.0의 지원 프로파일은 `audit`과 `product`다. 미지원 프로파일의 프로젝트에는 `upgrade`를 실행하거나 프로파일 값을 바꿔 적용하지 않는다. 기존 문서·승인·시험 결과는 원래 프로젝트의 기록으로 보존한다.

| Profile | 대상 | 특징 | 기본 강도 |
| --- | --- | --- | --- |
| `Audit Profile` | 공공/SI/감리 대응 프로젝트 | 요구사항, 설계, 테스트, 보안, 증적, CR을 가장 엄격하게 관리 | 높음 |
| `Product Profile` | 일반 앱/제품/업무 시스템 개발 | 품질은 유지하되 감리 제출 수준의 문서/증적 밀도는 줄이고, 제품 로드맵, 릴리즈, 아키텍처 결정, 품질 기준 중심으로 운영 | 중간 |

## 4. Profile별 운영 기준

Profile Overlay는 다음 필드를 기준으로 정의한다.

| Overlay 필드 | 의미 |
| --- | --- |
| `gate_approval` | 사용자의 명시 승인 지점과 Gate 자동 진행 금지 수준 |
| `required_artifacts` | Gate별 필수 산출물 범위 |
| `traceability_level` | ID 연결과 추적표 정합성 요구 수준 |
| `program_contract_level` | Program Design, interface, public method 계약의 상세도 |
| `security_standard_level` | 보안 기준선과 외부 표준 매핑 강도 |
| `data_standard_level` | 프로젝트 단어사전, 데이터 도메인, 외부 데이터 표준 적용 강도 |
| `qa_evidence_level` | 테스트 로그, 화면 캡처, Playwright, QA Finding 증적 수준 |
| `independent_review_level` | 독립 검수 또는 교차 검증을 요구하는 시점 |
| `run_preflight_strictness` | Run 입력 계약 사전 차단/경고 기준 |
| `release_control` | 릴리즈 승인, backlog, CR, release note 관리 수준 |

Profile은 결과물의 품질 등급이 아니다.
모든 Profile은 정상 동작, 검증 가능한 테스트, 실패/미실행의 정직한 기록을 요구한다.
차이는 문서 깊이, 증적 밀도, 독립검수 빈도, 변경관리 형식이다.

Profile별 기본 Overlay는 다음과 같다.

| Profile | `gate_approval` | `traceability_level` | `program_contract_level` | `security_standard_level` | `data_standard_level` | `qa_evidence_level` | `independent_review_level` | `run_preflight_strictness` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `audit` | 모든 Gate 명시 승인 | 전체 REQ/AC/FUNC/SCR/PGM/API/DB/SEC/UT/IT/UI | class/interface/public method 수준 | KISA/공공/고객사 기준 + OWASP/CWE | 공공데이터 공통표준 + 프로젝트 단어사전 | QA-000~QA-003, 명령 로그, UI 증적, FIND/CR | Gate 2, Gate 4, 필요 시 PR | 강한 차단 중심 |
| `product` | 작업 범위·인수·릴리즈 승인 | 핵심 요구사항, API, DB, 보안, 회귀 테스트 | public API, service/usecase, DTO 수준 | OWASP ASVS/Top 10/API Top 10 + CWE | 프로젝트 단어사전 + ISO 11179식 metadata 요소 + 필요 시 공공표준 참고 | 릴리즈 회귀, 주요 UI/API 증적, 공식 UI runner 기본 | release candidate 또는 큰 변경 | scope/contract 차단, 나머지 경고 |

`--trace-seed`는 모든 Profile에서 사용할 수 있다.
다만 `audit`에서는 대표 상세 ID를 기준으로 Run 입력 계약을 보강하는 것을 기본값으로 보고, `product`에서는 필요한 경우 관련 ID 추천과 source document 축소 목적으로 사용한다.

### 4.1 Audit Profile

공공/SI/감리 대응 프로젝트에 사용한다.

- Phase 0부터 Gate 5까지 모든 Gate를 명시적으로 운영한다.
- 요구사항정의서, 추적표, 기능명세, 프로그램 설계, 화면설계, DB명세, 보안가이드, 개발표준, 테스트케이스, 테스트결과, QA Finding, 변경요청, 릴리즈 승인서를 관리한다.
- 보안 기준은 KISA/SR, OWASP, CWE를 근거로 연결한다.
- 데이터 설계는 공공데이터 공통표준과 프로젝트 단어사전을 확인한다.
- CR은 영향도 분석, 상세 변경요청서, 관련 Gate 진행, Run 기록을 남긴다.
- 자동화 테스트는 원칙적으로 전체 실행하고, 통합/API/UI 테스트는 영향 범위를 중심으로 증적을 남긴다.
- Build Wave Run은 가능한 한 `wave-start --trace-seed <상세 ID>`로 생성하고, worker 실행 전 `scope.writable`, `interface_contract`, `contract_skeleton`, 검증 명령을 확정한다.
- Gate 4 QA는 QA-000 환경 준비, QA-001 명령 기반 검증, QA-002 UI/E2E 증적, QA-003 결과 정리와 판정 후보로 나누어 수행한다.
- Gate 4 공식 UI Pass는 `@playwright/test` runner, `npx playwright test`, HTML report/trace/screenshot 증적을 기준으로 한다. 커스텀 Playwright script는 보조 관찰로만 남긴다.

### 4.2 Product Profile

상용 제품, 사내 업무 앱, 반복 릴리즈가 필요한 제품형 개발에 사용한다.

- 문서의 목적은 감리 제출보다 제품 의사결정, 품질 유지, 릴리즈 추적에 둔다.
- 요구사항은 제품 백로그, 사용자 시나리오, 릴리즈 범위와 연결한다.
- 설계 문서는 SW Architecture, ADR, API/DB 계약, 보안/개발표준 중심으로 유지한다.
- 보안 기준은 KISA/공공 제출 근거가 아니라 OWASP ASVS, OWASP Top 10, OWASP API Security Top 10, CWE를 기본 기준선으로 사용한다.
- 설계자가 우선 읽을 기준선은 `docs/core/PRODUCT_PROFILE_BASELINE.md`, `docs/core/SECURITY_BASELINE.md`, `docs/core/DATA_STANDARD_RULES.md`다.
- ADR은 중요한 제품/아키텍처 의사결정이 있을 때 작성한다. 아직 결정이 없다면 `docs/product/ADR_LOG.md`에 `ADR-NONE` 행을 유지하고, `ADR-001 | TBD` 같은 placeholder 행은 남기지 않는다.
- KISA, 공공, 고객사 보안 기준은 Product에서 선택 참고로 둘 수 있으며, Audit 전환 시 공식 매핑과 증적으로 보강한다.
- 데이터 표준은 프로젝트 단어사전, 화면/API/DB 항목 매핑, 데이터 도메인, 개인정보/인증정보/민감정보 분류를 기본으로 한다.
- 공공데이터 공통표준은 공공/SI/Audit에서는 우선 검토 대상이지만, Product에서는 조직/도메인 표준이 없을 때 참고 표준으로 사용할 수 있다.
- 화면설계와 증적은 주요 사용자 흐름과 회귀 테스트 기준에 집중한다.
- 변경관리는 CR보다 Issue, Feature, Release Note, ADR과 연결될 수 있다.
- Run/Wave는 선택 사항이다. 일반 변경의 실행자, 짧은 작업 전달, 사후 현행화는 `PRODUCT_PROFILE_BASELINE.md` 7절을 따르며, 외부 CLI 실행은 기존 Run 계약을 유지한다.
- `planning → impl → acceptance`로 반복한다. `completed`는 이번 범위의 인수 결과이며 별도 단계나 배포 완료가 아니다. 운영 계약은 [CLI Guide 4.1](ORCHESTRATOR_CLI_GUIDE.md#41-개발용-product-반복-프로세스)을 따른다. 표식 없는 기존 프로젝트는 호환 흐름을 유지하고 upgrade로 자동 이행하지 않는다.
- Program Design은 모든 private method까지 요구하지 않고 public API, service/usecase, DTO, persistence adapter 경계를 중심으로 작성한다.
- QA는 릴리즈 후보 기준의 회귀 테스트, 주요 화면/API 증적, release note와 backlog 연결을 우선한다.
- UI Pass는 기본적으로 `@playwright/test` runner 증적을 사용한다. 단, 프로젝트가 UI 자동화 대상이 아니거나 환경 차단이 승인되면 `Not Run`, `Skipped`, `environment_blocked`로 정직하게 기록한다.
- Product 구현 Run은 `wave-start --trace-seed SCN-001`처럼 Product Scenario ID를 seed로 만들 수 있다. Product 원장과 명시적으로 연결한 상세에서 `SCN -> REQ/API/DATA/UI/REG` 연결을 추천한다. 같은 `docs/artifacts/` 아래여도 Product 원본인지 확인하며 Audit 산출물 전체를 입력으로 가져오지 않는다. 최종 handoff에는 실제 원본 경로·ID/절을 지정한다.
- 반복 모델의 `release-pr --dry-run`은 현재 작업 범위의 인수·증적·브랜치를 진단한다. 실제 PR/릴리즈 발행은 별도 승인 후 명시적인 수동 작업이며, Audit 승인서나 옛 단계 완료를 새로 요구하지 않는다.
- Product worker 입력/역할/검증 반복은 [PRODUCT_PROFILE_BASELINE.md](PRODUCT_PROFILE_BASELINE.md) 7절과 [PRODUCT_WORKER_GUIDE.md](PRODUCT_WORKER_GUIDE.md)를 따른다. 비차단 경고 정리만을 위해 제품 테스트를 반복하지 않는다.

개발환경 준비는 두 프로파일 모두에서 앞당길 수 있다. Product 반복 모델은 planning, 기존 Gate 모델은 Phase 0~Gate 3의 승인 범위에서 의존성, 빌드 스크립트와 smoke 검증을 준비한다. 업무 기능 구현이나 QA Pass 확정은 포함하지 않는다.

## 5. Profile 선택 기준

| 질문 | 예라면 |
| --- | --- |
| 외부 감리, 고객 검수, 공식 산출물 제출이 필요한가? | `Audit Profile` |
| 일반 제품/업무 앱 개발이며 품질은 유지하되 감리 수준 산출물 밀도는 줄이고 싶은가? | `Product Profile` |
| 반복 릴리즈와 제품 로드맵, 품질 기준이 중요한가? | `Product Profile` |

## 6. 도구 적용 기준

기본 Profile은 `audit`이다.

`vulcan.py init`은 `session.json.profile`, `vulcan.config.json.delivery_profile`, `vulcan.config.json.profile_rules`에 선택한 Profile과 Overlay 기준을 기록한다.
대화형 터미널에서 Profile을 지정하지 않으면 `audit`과 `product` 중 하나를 선택할 수 있다.
기존 문서와 명령어 호환을 위해 `solution`은 `product`의 alias로 입력만 허용한다.
비대화형 자동화에서는 기존 호환성을 위해 `audit`으로 초기화한다.

사용 예:

```powershell
python vulcan.py init ../my-project "My Project" --profile audit
python vulcan.py init ../my-product "My Product" --profile product
```

현재 구현 상태는 다음과 같다.

| 항목 | 현재 상태 |
| --- | --- |
| `audit` | 기본 Profile이며 가장 강하게 문서화/검증된다. |
| `product` | 새 `init --profile product`는 `docs/product/` 6종과 Product Overlay, `product-iterative-v1` planning 세션을 생성한다. 첫 범위 합의와 승인은 [CLI Guide 4.1](ORCHESTRATOR_CLI_GUIDE.md#41-개발용-product-반복-프로세스)을 따른다. 표식 없는 기존 프로젝트/upgrade는 자동 이행하지 않는다. |
| `profile-status` | 현재 Profile, config Profile, 적용 Profile Rules를 출력한다. |
| `profile-gap` | 현재 산출물을 목표 Profile 기준으로 볼 때 부족한 항목을 읽기 전용으로 진단한다. |
| `profile_rules` | `vulcan.config.json`에 명시적으로 기록되는 Profile Overlay 기준이다. |

예상 설정 예:

```json
{
  "delivery_profile": "product",
  "profile_rules": {
    "gate_approval": "scope-acceptance-and-release",
    "traceability_level": "core",
    "program_contract_level": "public-api-and-service",
    "security_standard_level": "owasp-asvs-top10-api-top10-cwe",
    "data_standard_level": "project-glossary-field-domain-security-classification",
    "qa_evidence_level": "release-regression",
    "independent_review_level": "release-candidate",
    "run_preflight_strictness": "contract-and-scope"
  }
}
```

Product Profile의 기본 산출물 세트는 다음 6종이다.

```text
docs/product/PRODUCT_BRIEF.md
docs/product/PRODUCT_ARCHITECTURE.md
docs/product/ADR_LOG.md
docs/product/PRODUCT_CONTRACTS.md
docs/product/PRODUCT_TRACEABILITY.md
docs/product/REGRESSION_AND_RELEASE_REPORT.md
```

이 문서들은 Gate별 제출 폴더가 아니라 제품 운영 문서 세트다.
각 문서는 목표·계약·계획·실제 결과라는 목적에 따라 갱신한다. 문서별 단계 메타데이터를 두거나 문서 수를 승인 단계 수로 해석하지 않는다.
상세가 필요해지면 공통 `docs/artifacts/` 구조를 재사용하고 [PRODUCT_DOCUMENT_WRITING.md](PRODUCT_DOCUMENT_WRITING.md)의 Product 선택 템플릿을 따른다. 요구/설계/시험/실행은 원본 한 곳에 쓰고 원장은 개요, 상대 Markdown 링크와 릴리즈 판단을 유지한다.

```text
docs/product/
  PRODUCT_BRIEF.md
  PRODUCT_ARCHITECTURE.md
  ADR_LOG.md
  PRODUCT_CONTRACTS.md
  PRODUCT_TRACEABILITY.md
  REGRESSION_AND_RELEASE_REPORT.md

선택 상세 산출물:
  docs/artifacts/02-design/api/PRODUCT_API_CONTRACT.md
  docs/artifacts/02-design/data/PRODUCT_DATA_MODEL.md
  docs/artifacts/02-design/data/erd/logical/
  docs/artifacts/02-design/data/erd/physical/
  docs/artifacts/02-design/screen/PRODUCT_UI_CONTRACT.md
  docs/artifacts/02-design/screen/images/
  docs/artifacts/02-design/screen/prototypes/
  docs/artifacts/02-design/security/PRODUCT_SECURITY_CHECKLIST.md
  docs/artifacts/02-design/development-standard/PRODUCT_ENGINEERING_GUIDE.md
  docs/artifacts/03-test/PRODUCT_TEST_PLAN.md
  docs/artifacts/04-review/evidence/ui/
  docs/artifacts/04-review/evidence/logs/
  docs/artifacts/04-review/evidence/reports/
```

Product에서 위 상세 산출물은 기본 필수가 아니다.
원장 6종만으로 충분하면 상세 문서를 만들지 않는다.
요구/설계/시험/실행이 독립 변경·검토를 필요로 할 때 해당 상세를 작성한다. 요구사항 상세, 테스트 계획, 실행 결과 템플릿도 선택 제공하지만 init에서 추가 산출물을 일괄 생성하지 않는다. 기존 승인 문서는 자동 이동하지 않는다.
`profile-gap`은 다른 profile을 검토할 때 부족한 산출물을 읽기 전용으로 진단한다. 현재 Product 작업의 준비 상태와 승인 경계는 `status --check`와 CLI Guide 4.1을 기준으로 판단한다.
Product의 계획과 판단은 현재 원본 문서·작업 범위에 남기며, 시작이나 상태 전환마다 Orchestrator Plan Run을 만들지 않는다. 구현/검수 위임이나 재현 가능한 작업 기록에 유용할 때만 Run을 선택한다.

`run-new`는 Profile과 Gate, skill 조합을 보고 가능한 경우 Run 입력 계약을 자동 확장한다.

기존 Gate 모델의 Impl `check-trace`는 Gate 3 테스트케이스의 `Planned`/미실행 항목을 Gate 4 실행 대기 항목으로 취급한다. 실제 Pass/Fail/Not Run 판정은 QA 결과서와 증적으로 확인한다. Product 반복 모델도 시험 계획과 실제 결과를 분리하되, planning/impl/acceptance를 옛 Gate로 변환하지 않는다.

[Profile Gap Check](PROFILE_GAP_CHECK.md)는 목표 프로파일 기준의 부족 항목을 읽기 전용으로 확인한다. 진단 결과는 전환이나 승인이 아니다.

Audit Profile에서는 Phase 0부터 Gate 5까지 빈 Run 껍데기를 만들지 않고 다음 항목을 포함한다.

- 먼저 읽을 최소 문서, 실제 작업 산출물, 필요 시 참고 문서의 분리
- 수정 가능 경로, 읽기 전용 경로, 제외 경로
- 감리 대응 완료 기준
- 실제 검증 명령
- 출력 계약과 질문 정책
- Gate 종료 후 사용자 승인 대기 정책
- UI 테스트와 화면 증적의 상태/시나리오별 1:1 매칭 정책

기본 preset 범위:

| Gate | 기본 Run 초점 |
| --- | --- |
| `phase0` | 프로젝트 목적, 범위, 이해관계자, As-Is/To-Be, 리스크/가정 |
| `gate1` | REQ/NREQ/AC와 추적표 초기 연결 |
| `gate2` | 설계 산출물, 보안, 데이터, 화면, 개발표준 연결 및 Gate 2 설계 순서 관리 |
| `gate3` | AC/SEC/NREQ를 UT/IT/UI/PT 테스트 기준으로 전개 |
| `impl` | 승인된 설계/테스트 범위 안의 Build Wave 계획과 실행 |
| `gate4` | 테스트 결과, 화면/로그 증적, QA Finding, fix-loop |
| `gate5` | 릴리즈 승인, 미해결 FIND/CR, 잔여 리스크, 인수인계 |

Audit Profile에서는 각 Gate 완료 후 다음 Gate로 자동 진행하지 않는다.
Run은 산출물 요약, 미해결 항목, 다음 Gate 제안, 사용자 승인 질문을 남기고 멈춘다.
대화상 명시 승인 없이 승인 완료로 기록하지 않는다.

UI 테스트는 `UI-001`처럼 화면 하나로 크게 Pass 처리하지 않고 `UI-001-01`처럼 상태/시나리오 단위로 나눈다.
예를 들어 회원가입은 기본 화면, 약한 비밀번호 오류, 비밀번호 확인 불일치, 중복 이메일, 성공 메시지, 로그인 연계를 별도 테스트와 별도 캡처로 연결한다.

Run의 `source_documents`는 다음처럼 해석한다.

| 구분 | 의미 |
| --- | --- |
| `read_first` | 작업 시작 전에 먼저 읽는 최소 문서 |
| `working_documents` | 이번 Run에서 실제로 작성하거나 검토할 산출물 |
| `reference_on_demand` | 기준 충돌, 작성 규칙 확인, 상세 판단이 필요할 때만 참고하는 문서 |

Core 문서, Template, 샘플 입력 문서는 원칙적으로 `reference_on_demand`에 둔다.
에이전트는 `working_documents`를 중심으로 작업한다.
다만 Audit Profile의 Gate 2 Run은 설계 순서를 놓치지 않도록 `docs/core/GATE2_DESIGN_SEQUENCE.md`를 `read_first`에 포함한다.
Gate 2 Run 출력에는 현재 순서 위치, 누락된 이전 단계, 다음 Gate 2 Run 후보가 남아야 한다.

예:

```powershell
python vulcan.py run-new --gate phase0 --skill orchestrator-plan --title "Phase 0 Discovery" --related-ids RUN-001
python vulcan.py run-new --gate gate1 --skill traceability-review --title "요구사항 추적성 검토" --related-ids REQ-001,AC-001
python vulcan.py run-new --gate gate2 --skill data-standard-review --title "프로젝트 단어사전 검토" --related-ids DB-001,API-001,SCR-001
python vulcan.py run-new --gate gate2 --skill development-standard-review --title "개발표준 검토" --related-ids NREQ-001,SEC-001,PGM-001
python vulcan.py run-new --gate gate3 --skill traceability-review --title "테스트케이스 전개 검토" --related-ids AC-001,UT-001,IT-001
python vulcan.py run-new --gate impl --skill implementation-plan --title "Build Wave 계획" --related-ids REQ-001,PGM-001,UT-001
python vulcan.py run-new --gate gate4 --skill qa-execution --title "QA-000 Gate 4 환경 준비 및 smoke" --related-ids NREQ-002,IT-BUILD-001
python vulcan.py run-new --gate gate4 --skill qa-execution --title "QA-001 Gate 4 명령 기반 검증" --related-ids UT-001,IT-001,NREQ-001,NREQ-002
python vulcan.py run-new --gate gate4 --skill qa-execution --title "QA-002 Gate 4 UI/E2E 증적 수집" --related-ids UI-001,UI-002
python vulcan.py run-new --gate gate4 --skill qa-execution --title "QA-003 Gate 4 결과 정리 및 판정 후보" --related-ids RV-TEST-001,NREQ-001,NREQ-002
python vulcan.py run-new --gate gate4 --skill qa-fix-loop --title "QA 결함 수정 루프" --related-ids FIND-001,UI-001
python vulcan.py run-new --gate gate5 --skill traceability-review --title "릴리즈 승인 검토" --related-ids REQ-001,RUN-001,CR-001
```

향후 `check-trace`, Dashboard, template 생성 범위, Gate 완료 기준은 위 Overlay 필드에 맞춰 Profile별로 세분화한다.
Profile별 구현은 Core 규칙을 복제하지 않고, 하나의 검사기와 하나의 Run 입력 계약이 선택된 Profile의 엄격도를 참조하도록 확장한다.
