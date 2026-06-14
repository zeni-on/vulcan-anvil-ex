# Examples And Benchmarks

이 문서는 Vulcan-Anvil Ex를 처음 보는 사람이 "실제로 무엇이 남는가"를 빠르게 이해하도록 돕는 요약입니다. 수치는 로컬 샘플 실행과 회고 문서에서 나온 관찰값이며, 하드웨어, runner, 네트워크, 사용자 승인 대기 시간에 따라 달라질 수 있습니다.

## 읽는 법

- 시간은 절대 성능 보증이 아니라 운영 강도 비교용입니다.
- PoC, Product, Audit은 품질 등급이 아니라 문서/증적/승인 깊이의 차이입니다.
- 실행하지 않은 테스트를 `Pass`로 기록하는 것은 어떤 profile에서도 허용하지 않습니다.

## 단일 TODO 앱 관찰

| 축 | PoC profile | Audit profile |
| --- | --- | --- |
| 목적 | 핵심 동작과 가설 검증 | 감리/인수인계 가능한 전체 추적성 |
| 대략 소요 | 약 10~30분대 관찰 | 약 1~2시간대 관찰 |
| 산출물 | PoC 3문서 + smoke/demo 결과 중심 | 정식 Gate 산출물, Run, QA 결과, 추적표 중심 |
| Run | 없거나 compact Run 1개 수준 | Build Wave/QA/검수 Run 여러 개 |
| 테스트 | smoke, 빠른 self-check, 필요 시 데모 캡처 | unit/integration/UI/QA 결과서와 증적 |
| 적합한 경우 | 아이디어 검증, 내부 데모, 기술 가능성 확인 | 고객 검수, 장기 유지보수, 공식 인수인계 |

## Profile별 결과물 예시

### PoC

보통 다음이 남습니다.

- `docs/poc/POC_REQUIREMENTS.md`
- `docs/poc/POC_SYSTEM_DESIGN.md`
- `docs/poc/POC_TEST_REPORT.md`
- 구현 코드와 dependency manifest
- smoke/demo 로그
- 다음 판단 항목

PoC의 목표는 "모든 공식 산출물 작성"이 아니라, 핵심 가설이 맞는지 빠르게 검증하고 다음 투자를 결정하는 것입니다.

### Product

보통 다음이 남습니다.

- 핵심 요구사항과 사용자 시나리오
- 제품/업무 아키텍처 또는 ADR
- API/DB/UI 주요 계약
- OWASP/CWE 기반 보안 기준선
- 프로젝트 단어사전과 화면/API/DB 매핑
- 구현 코드와 회귀 테스트
- 릴리즈 후보, backlog, issue, release note
- 주요 QA 로그와 화면/API 증적

Product는 PoC보다 오래가지만 Audit보다 가볍습니다. 실제 제품 또는 업무 앱을 계속 운영할 때의 기본 레이어입니다.

### Audit

보통 다음이 남습니다.

- Phase 0~Gate 5 전체 산출물
- 요구사항정의서, 기능/화면/프로그램/API/DB/보안 설계
- 테스트케이스, 테스트결과서, QA Finding
- 요구사항추적표와 증적 링크
- FIND/CR/ISSUE, release approval, 인수인계 항목

Audit은 가장 느리지만, "왜 이렇게 만들었고 무엇으로 검증했는지"를 설명할 수 있는 정보가 가장 많이 남습니다.

## 좋은 비교 기준

Ex는 Replit, Lovable, Bolt, v0 같은 빠른 앱 빌더와 같은 속도 경쟁을 하지 않습니다. 그런 도구는 빠르게 동작하는 앱을 만드는 데 강합니다. Ex는 AI가 만든 결과를 요구사항, 설계, 테스트, 증적, 승인 흐름으로 회수하는 데 초점을 둡니다.

따라서 비교할 때는 "몇 분 만에 앱이 떴는가"만 보지 말고 다음도 함께 봅니다.

- 요구사항과 구현이 연결되어 있는가?
- 실행한 테스트와 로그가 남아 있는가?
- 화면 증적 또는 smoke/demo 결과가 있는가?
- 실패나 미실행이 정직하게 기록되어 있는가?
- 다음 변경이나 인수인계 때 다시 읽을 수 있는가?

## 앞으로 보강할 것

현재는 샘플 회고 기반의 요약입니다. 향후에는 `scripts/regression` fixture와 `python vulcan.py metrics` 결과를 연결해 더 재현 가능한 benchmark summary로 정리할 예정입니다.
