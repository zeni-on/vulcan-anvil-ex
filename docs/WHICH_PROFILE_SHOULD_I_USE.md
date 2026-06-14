# Which Profile Should I Use?

Vulcan-Anvil Ex는 프로젝트마다 같은 무게의 문서와 검증을 강제하지 않습니다. `profile`은 결과물의 품질 등급이 아니라 **문서 깊이, 증적 밀도, 승인 지점, 변경관리 방식의 기본값**입니다.

## 빠른 선택

| 질문 | 추천 profile |
| --- | --- |
| "일단 되는지 빨리 보고 싶다" | `poc` |
| "업무 앱/솔루션을 제품처럼 만들고 릴리즈 품질을 유지하고 싶다" | `solution` |
| "감리, 고객 검수, 인수인계, 보안/QA 증적이 필요하다" | `audit` |

## Profile별 의도

### PoC

PoC는 가능성 검증입니다. 목표, 가설, 성공 기준, 핵심 설계, smoke/demo 결과만 빠르게 남깁니다.

```powershell
python vulcan.py init ../my-poc "My PoC" --profile poc
```

PoC에서 중요한 것은 "완벽한 산출물"이 아니라 다음 질문에 답하는 것입니다.

- 이 아이디어가 실제로 동작하는가?
- 핵심 기술/화면/API 가설이 맞는가?
- 계속 투자할 가치가 있는가?
- 제품화 또는 Audit 전환 시 무엇을 보강해야 하는가?

PoC에서도 실행하지 않은 테스트를 `Pass`로 쓰지 않습니다. 실패, 미실행, 환경 차단은 다음 판단 항목으로 남깁니다.

### Solution

Solution은 일반 제품, 사내 업무 앱, 반복 릴리즈가 필요한 솔루션 개발의 기본값입니다. 감리 제출 수준의 모든 문서가 필요하지는 않지만, API/DB/UI/보안/릴리즈 품질은 유지해야 할 때 사용합니다.

```powershell
python vulcan.py init ../my-product "My Product" --profile solution
```

Solution에서 중요한 것은 다음입니다.

- 핵심 요구사항과 사용자 시나리오
- 제품/업무 아키텍처와 ADR
- API, DB, DTO, 주요 UI 계약
- OWASP/CWE 기반 보안 기준선
- 프로젝트 단어사전, 화면/API/DB 항목 매핑, 데이터 보안 분류
- 릴리즈 회귀 테스트와 주요 화면/API 증적
- backlog, issue, release note 연결

Solution은 "가벼운 Audit"이 아니라 제품 운영에 필요한 중간 레이어입니다. 자세한 기준은 [Solution Profile Baseline](reference/SOLUTION-PROFILE-BASELINE.md)을 참고합니다.

### Audit

Audit은 기본 profile입니다. 감리, 고객 검수, 장기 유지보수, 인수인계, 보안/QA 증적이 중요한 경우에 사용합니다.

```powershell
python vulcan.py init ../my-audit-project "My Audit Project"
```

Audit에서 중요한 것은 다음입니다.

- 요구사항에서 설계, 테스트, 증적까지의 전체 추적성
- Gate별 승인과 변경관리
- Program/API/DB/UI/Security 계약
- QA 결과서, 화면 증적, FIND/CR/ISSUE 분류
- 릴리즈 승인과 인수인계 근거

## 시작 메시지 예시

### PoC

```text
이 프로젝트는 PoC profile이야.
핵심 가설과 성공 기준을 먼저 잡고, smoke/demo로 동작 여부를 확인해줘.
감리 제출 수준 문서는 만들지 말고, 실패나 미실행은 다음 판단 항목으로 남겨줘.
```

### Solution

```text
이 프로젝트는 Solution profile이야.
일반 제품/업무 앱 수준으로 요구사항, 주요 설계, API/DB/UI 계약, 릴리즈 회귀 기준을 남겨줘.
감리 제출 수준의 과도한 증적보다는 제품 품질과 유지보수성을 우선해줘.
```

### Audit

```text
이 프로젝트는 Audit profile이야.
요구사항, 설계, 테스트, QA 증적, 변경관리, 릴리즈 승인까지 추적 가능하게 진행해줘.
Gate 전환 전에는 status --check 결과와 남은 이슈를 보고해줘.
```

## 전환 기준

PoC로 시작해도 결과가 의미 있으면 Solution 또는 Audit으로 승격할 수 있습니다.

| 현재 | 전환 후보 | 조건 |
| --- | --- | --- |
| `poc` | `solution` | 실제 사용자/릴리즈 계획이 생겼고 API/DB/UI 계약을 유지해야 함 |
| `poc` | `audit` | 고객 검수, 감리, 보안/인수인계 증적이 필요해짐 |
| `solution` | `audit` | 공식 산출물, 변경관리, QA 증적, 승인 절차가 강해짐 |

전환은 단순 설정 변경이 아니라 부족한 산출물과 추적성을 보강하는 작업입니다.
