# Profile Gap Check

> 상태: 초안 v0.1
> 목적: 현재 산출물을 Product 또는 Audit 기준과 비교해 부족한 계약과 증적을 찾는다.

## 1. 원칙

`profile-gap`은 목표 프로파일 기준으로 문서의 존재와 내용을 확인하는 읽기 전용 진단이다. 프로파일이나 프로세스 모델을 전환하지 않고 기존 문서·승인·증적을 이관하지 않는다. 부족한 항목은 보강 후보로 기록하고 실제 작업 범위는 별도로 합의한다.

## 2. 권장 명령

```powershell
python vulcan.py profile-gap --to product
python vulcan.py profile-gap --to audit
python vulcan.py profile-gap --to product --json
```

`profile-gap`은 읽기 전용 진단이다.
`session.json`, `vulcan.config.json`, 산출물, 코드를 수정하지 않는다.

`profile-gap`은 두 층으로 결과를 나눈다.

- `ok` / `partial` / `missing`: 목표 profile에서 기대하는 문서나 동등 산출물이 있는지
- `content_issues` / `content_warnings`: 현재 Gate에서 판단에 필요한 핵심 내용이 비어 있거나 확인이 필요한지

예를 들어 Product profile을 새로 init하면 `docs/product/` 6종 문서는 모두 있으므로 문서 세트는 `ok`가 될 수 있다.
파일이 있다는 것만으로 현재 범위가 승인되거나 인수 가능한 것은 아니다. 현재 진행 가능 여부는 `status --check`에서 따로 확인한다.

## 3. Product 기준

Product 기준으로 검토할 항목은 다음과 같다.

| 항목 | 의미 |
| --- | --- |
| Product brief | 목표, 사용자, 핵심 시나리오, 비목표, 성공 기준이 제품 관점으로 정리되어 있는가 |
| Product architecture | 주요 컴포넌트, 런타임, 배포/운영 경계, 품질속성이 있는가 |
| ADR | 중요한 기술/구조 선택 이유가 남아 있는가 |
| Product contracts | API, DB, UI, 보안, 데이터 계약의 진입점이 있는가 |
| Regression/release report | 반복 실행할 회귀 테스트와 릴리즈 판단 근거가 있는가 |
| Traceability | 핵심 시나리오 -> 계약 -> 구현 -> 테스트 -> 릴리즈 근거가 끊기지 않는가 |

## 4. Audit 기준

공식 제출이나 고객 검수를 위해 다음 항목을 확인한다.

| 항목 | 의미 |
| --- | --- |
| Requirements and AC | 요구사항, 수용기준, 비기능 요구사항이 공식 ID로 분리되어 있는가 |
| Full design artifacts | 아키텍처, 기능, 프로그램, API, 화면, DB, 보안, 개발표준이 존재하는가 |
| Security mapping | KISA/SR, 고객/공공 기준, OWASP/CWE가 SEC-ID와 테스트에 연결되어 있는가 |
| Data standard mapping | 공공데이터 공통표준 준용/변형/신규 사유가 필요한 범위에 남아 있는가 |
| Test plan and QA evidence | UT/IT/UI/PT 계획과 Gate 4 결과/증적이 분리되어 있는가 |
| Traceability matrix | REQ/AC/FUNC/SCR/PGM/API/DB/SEC/UT/IT/UI가 추적표에서 연결되어 있는가 |
| Change/release records | FIND/CR/ISSUE, 릴리즈 승인, 미해결 리스크가 정리되어 있는가 |

## 5. 결과 해석

`profile-gap` 항목은 다음 상태를 사용한다.

| 상태 | 의미 |
| --- | --- |
| `ok` | 목표 profile 기준의 직접 산출물 또는 동등한 공식 산출물이 있다 |
| `partial` | 현재 profile 산출물에 근거는 있으나 목표 profile 기준으로는 보강이 필요하다 |
| `missing` | 근거 산출물이 보이지 않는다 |
| `review` | 파일은 있으나 내용 판단이나 사용자 결정이 필요하다 |

`missing`과 `partial`은 보강 후보이며 `ok`도 승인이나 검증 완료를 뜻하지 않는다. 내용 경고와 차단 후보를 현재 범위와 대조하고, 필요한 작업과 승인 지점을 사용자에게 보고한다.
