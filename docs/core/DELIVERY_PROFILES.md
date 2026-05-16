# Vulcan-Anvil Ex Delivery Profiles

> 상태: 초안 v0.1
> 목적: 프로젝트 성격에 따라 문서 깊이, Gate 엄격도, 승인 절차, 증적 수준을 조절하는 기준을 정의한다.

## 1. 배경

Vulcan-Anvil Ex는 감리 대응형 프로젝트에서 강하게 동작하도록 설계되었다.
하지만 모든 작업이 공공/SI/감리 수준의 산출물과 검수 강도를 필요로 하지는 않는다.

작은 PoC, 내부 검증, 솔루션 제품 개발, 개인 기능 개발에 같은 절차를 적용하면 개발보다 문서와 검수 비용이 더 커질 수 있다.
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
Core의 ID, Run, Traceability, Gate 원칙은 유지하되, 프로젝트 목적에 맞게 산출물 깊이와 검증 범위를 조절한다.

## 3. Profile 분류

| Profile | 대상 | 특징 | 기본 강도 |
| --- | --- | --- | --- |
| `Audit Profile` | 공공/SI/감리 대응 프로젝트 | 요구사항, 설계, 테스트, 보안, 증적, CR을 가장 엄격하게 관리 | 높음 |
| `Solution Profile` | 제품/솔루션 개발 | 감리 제출보다 제품 로드맵, 릴리즈, 아키텍처 결정, 품질 기준 중심 | 중간 |
| `PoC Profile` | 실험/검증/프로토타입 | Phase 0, Gate 1, Gate 2를 가볍게 묶고 핵심 가설 검증에 집중 | 낮음~중간 |
| `Lite Profile` | 개인/소규모 기능 개발 | 문서보다 Run 기록, 요구사항 요약, 테스트 결과 중심 | 낮음 |

## 4. Profile별 운영 기준

### 4.1 Audit Profile

공공/SI/감리 대응 프로젝트에 사용한다.

- Phase 0부터 Gate 5까지 모든 Gate를 명시적으로 운영한다.
- 요구사항정의서, 추적표, 기능명세, 프로그램명세, 화면설계, DB명세, 보안가이드, 개발표준, 테스트케이스, 테스트결과, QA Finding, 변경요청, 릴리즈 승인서를 관리한다.
- 보안 기준은 KISA/SR, OWASP, CWE를 근거로 연결한다.
- 데이터 설계는 공공데이터 공통표준과 프로젝트 단어사전을 확인한다.
- CR은 영향도 분석, 상세 변경요청서, 관련 Gate 진행, Run 기록을 남긴다.
- 자동화 테스트는 원칙적으로 전체 실행하고, 통합/API/UI 테스트는 영향 범위를 중심으로 증적을 남긴다.

### 4.2 Solution Profile

상용 제품, 사내 솔루션, 반복 릴리즈가 필요한 제품형 개발에 사용한다.

- 문서의 목적은 감리 제출보다 제품 의사결정, 품질 유지, 릴리즈 추적에 둔다.
- 요구사항은 제품 백로그, 사용자 시나리오, 릴리즈 범위와 연결한다.
- 설계 문서는 SW Architecture, ADR, API/DB 계약, 보안/개발표준 중심으로 유지한다.
- 화면설계와 증적은 주요 사용자 흐름과 회귀 테스트 기준에 집중한다.
- 변경관리는 CR보다 Issue, Feature, Release Note, ADR과 연결될 수 있다.
- Gate는 유지하되 승인 절차를 가볍게 운영할 수 있다.

### 4.3 PoC Profile

기술 검증, 고객 데모, 빠른 가능성 확인에 사용한다.

- Phase 0, Gate 1, Gate 2를 짧게 묶어 목표, 가설, 성공 기준, 주요 제약을 먼저 정한다.
- 모든 산출물을 완성하려고 하지 않고 핵심 요구사항, 핵심 설계, 핵심 테스트만 작성한다.
- 추적성은 최소한 `가설/요구사항 -> 구현 -> 검증 결과`를 연결하는 수준으로 유지한다.
- 보안/데이터/운영 기준은 실제 배포가 아니라 위험 식별과 향후 전환 조건 중심으로 작성한다.
- PoC 결과가 제품화 또는 SI 프로젝트로 전환되면 Audit 또는 Solution Profile로 승격한다.

### 4.4 Lite Profile

개인 프로젝트, 작은 기능, 빠른 내부 자동화에 사용한다.

- Run 문서와 요구사항 요약을 중심으로 운영한다.
- Gate는 단계명보다 체크리스트처럼 가볍게 사용할 수 있다.
- 추적성은 주요 요구사항, 구현 파일, 테스트 결과 연결만 남긴다.
- 화면 증적과 상세 산출물은 필요한 경우에만 작성한다.
- 장기 유지보수나 외부 제출이 필요해지면 Solution 또는 Audit Profile로 승격한다.

## 5. Profile 선택 기준

| 질문 | 예라면 |
| --- | --- |
| 외부 감리, 고객 검수, 공식 산출물 제출이 필요한가? | `Audit Profile` |
| 반복 릴리즈와 제품 로드맵, 품질 기준이 중요한가? | `Solution Profile` |
| 핵심 가설이나 기술 가능성을 빠르게 검증하려는가? | `PoC Profile` |
| 개인/소규모 기능이며 문서 비용을 최소화해야 하는가? | `Lite Profile` |

## 6. 향후 적용 방향

`0.2.0` 기준 Delivery Profile은 문서화된 방향이다.
향후 `vulcan.py init` 또는 `session.json`에서 Profile을 선택할 수 있게 확장한다.

예상 옵션:

```powershell
python vulcan.py init ../my-project "My Project" --profile audit
python vulcan.py init ../my-product "My Product" --profile solution
python vulcan.py init ../my-poc "My PoC" --profile poc
python vulcan.py init ../my-tool "My Tool" --profile lite
```

Profile이 도입되면 `check-trace`, Dashboard, template 생성 범위, Gate 완료 기준도 Profile별로 조절한다.
