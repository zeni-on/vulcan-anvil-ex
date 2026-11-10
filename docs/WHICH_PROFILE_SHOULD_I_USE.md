# Which Profile Should I Use?

Vulcan-Anvil Ex는 프로젝트마다 같은 무게의 문서와 검증을 강제하지 않습니다. `profile`은 결과물의 품질 등급이 아니라 **문서 깊이, 증적 밀도, 승인 지점, 변경관리 방식의 기본값**입니다.

## 빠른 선택

| 질문 | 추천 profile |
| --- | --- |
| "제품/업무 앱을 만들고 릴리즈 품질을 유지하고 싶다" | `product` |
| "감리, 고객 검수, 인수인계, 보안/QA 증적이 필요하다" | `audit` |

작은 기능 실험도 새 Product에서 시나리오 하나로 범위를 좁혀 진행할 수 있습니다. 이는 기존 프로젝트나 과거 시험 결과가 Product로 전환된다는 뜻이 아닙니다.

## Profile별 의도

### Product

Product는 일반 제품, 사내 업무 앱, 반복 릴리즈가 필요한 개발의 기본값입니다. 감리 제출 수준의 모든 문서가 필요하지는 않지만, API/DB/UI/보안/릴리즈 품질은 유지해야 할 때 사용합니다.

```powershell
python vulcan.py init ../my-product "My Product" --profile product
```

Product에서 중요한 것은 다음입니다.

- 핵심 요구사항과 사용자 시나리오
- 제품/업무 아키텍처와 ADR
- API, DB, DTO, 주요 UI 계약
- OWASP/CWE 기반 보안 기준선
- 프로젝트 단어사전, 화면/API/DB 항목 매핑, 데이터 보안 분류
- 릴리즈 회귀 테스트와 주요 화면/API 증적
- backlog, issue, release note 연결

Product는 "가벼운 Audit"이 아니라 제품 운영을 위한 프로파일입니다. 자세한 기준은 [Product Profile Baseline](core/PRODUCT_PROFILE_BASELINE.md)을 참고합니다.

일반 변경은 기존 작업/이슈의 목표, 범위, 관련 계약, 검증 기준으로 진행할 수 있습니다. Run/Wave와 새 worker는 필요할 때 선택하며, 매 수정마다 새 문서를 만들지는 않습니다. 승인 경계, 보안, 실제 테스트 결과와 현재 계약의 현행화는 유지합니다.

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

### Product

```text
이 프로젝트는 Product profile이야.
일반 제품/업무 앱 수준으로 요구사항, 주요 설계, API/DB/UI 계약, 릴리즈 회귀 기준을 남겨줘.
감리 제출 수준의 과도한 증적보다는 제품 품질과 유지보수성을 우선해줘.
```

### Audit

```text
이 프로젝트는 Audit profile이야.
요구사항, 설계, 테스트, QA 증적, 변경관리, 릴리즈 승인까지 추적 가능하게 진행해줘.
Gate 전환 전에는 status --check 결과와 남은 이슈를 보고해줘.
```

## 기준이 달라졌을 때

고객 검수나 공식 제출이 필요해지면 [Profile Gap Check](core/PROFILE_GAP_CHECK.md)로 Audit 기준에서 부족한 문서와 증적을 확인합니다. 진단은 프로파일을 바꾸거나 기존 승인을 승계하지 않습니다.
