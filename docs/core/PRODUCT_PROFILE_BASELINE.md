# Product Profile Baseline

> 상태: 초안 v0.1
> 목적: `product` profile 프로젝트가 `init` 직후 설계 단계에서 바로 참조할 보안, 데이터, 릴리즈 기준선을 정의한다.

본 문서는 `vulcan.py init` 시 새 프로젝트의 `docs/core/`에 포함되는 실행 기준선이다.
긴 배경과 검토 노트는 원본 프레임워크의 `docs/reference/PRODUCT-PROFILE-BASELINE.md`를 참고하되, 프로젝트 안에서 에이전트가 우선 읽을 기준은 본 문서다.

## 1. 포지션

Product Profile은 PoC와 Audit 사이의 중간 레이어다.

| Profile | 목적 |
| --- | --- |
| `poc` | 아이디어, 기술, 화면, API 가설을 실험하고 결과를 기록 |
| `product` | 실제 사용자와 릴리즈가 있는 제품/업무 앱을 유지 가능한 수준으로 개발 |
| `audit` | 감리, 고객 검수, 공공/SI, 인수인계, 강한 QA 증적 대응 |

Product는 Audit의 축소판이 아니다.
제품 운영에 필요한 의사결정, 계약, 테스트, 릴리즈 근거를 남기는 profile이다.

## 2. 필수 관점

| 관점 | 기준 |
| --- | --- |
| Product Brief | 목표, 사용자, 핵심 시나리오, 비목표, 성공 기준 |
| Product Design | 아키텍처, 주요 컴포넌트, API/DB/UI 계약, ADR |
| Backlog/Release Scope | 이번 릴리즈 범위, 제외 범위, 다음 릴리즈 후보 |
| Test & Release Report | 핵심 회귀 테스트, 주요 화면/API 검증, known issue, release note |
| Traceability | 핵심 요구사항 -> 구현 -> 테스트 -> 릴리즈 근거 연결 |

Audit처럼 모든 ID를 촘촘하게 확장하지 않아도 되지만, 핵심 사용자 시나리오와 릴리즈 판단 근거는 끊기면 안 된다.

## 3. 보안 기준선

Product 보안은 KISA/공공 제출용 매핑을 기본 강제하지 않는다.
대신 일반 제품 개발에서 납득 가능한 보안 기준선을 둔다.

기본 기준:

- OWASP ASVS
- OWASP Top 10
- OWASP API Security Top 10
- CWE
- 프로젝트별 Security Baseline

Product에서 최소 검토할 보안 항목:

| 항목 | 확인 |
| --- | --- |
| 인증/인가 | 로그인, 세션, 토큰, 사용자별 접근통제 |
| 입력값 검증 | API body, query/path parameter, 화면 입력 |
| 오류/로그 | 내부 stack, SQL, token, 개인정보 노출 금지 |
| 데이터 보호 | 개인정보, 인증정보, 민감정보 저장/전송/마스킹 |
| Web/API 위험 | XSS, CSRF, CORS, SQL injection, command injection, SSRF 필요 여부 |
| 의존성 | 알려진 취약 버전, lockfile, upgrade 정책 |
| 파일/외부연계 | 업로드, 다운로드, webhook, 외부 URL 호출 제한 |

KISA, 공공, 고객사 보안 기준은 선택 참고로 둘 수 있다.
다만 Audit으로 전환하면 KISA/SR 또는 고객 기준과 `SEC-ID`, 테스트, 증적을 공식 매핑해야 한다.

## 4. 데이터/단어사전 기준선

Product에서도 단어사전은 필요하다.
목적은 감리 제출이 아니라 팀과 AI 에이전트가 같은 데이터 의미를 쓰게 하는 것이다.

기본 기준:

- 프로젝트 단어사전
- 화면/API/DB 항목명 매핑
- 데이터 도메인과 타입/길이/형식
- 개인정보/인증정보/민감정보/시스템정보 분류
- 필요 시 ISO/IEC 11179 metadata registry 개념 참고
- 필요 시 DAMA Dictionary/DMBOK 용어 참고

공공데이터 공통표준은 공공/SI/Audit에서는 우선 검토 대상이다.
Product에서는 조직 표준이 없거나 공공 데이터와 연계할 때 참고한다.

Product 단어사전의 최소 항목:

| 항목 | 설명 |
| --- | --- |
| TERM-ID | 프로젝트 용어 ID |
| 한글명/영문명 | 사람과 코드가 함께 이해할 수 있는 이름 |
| API 필드명 | 외부/프론트엔드 계약 |
| DB 컬럼명 | 저장소 계약 |
| 도메인 | 타입, 길이, 형식, 허용값 |
| 보안 분류 | 일반, 식별정보, 인증정보, 개인정보, 민감정보, 시스템정보 |
| 관련 ID | REQ, API, DB, PGM, SEC, TEST 중 필요한 연결 |

## 5. Gate 운영

| 단계 | Product 기준 |
| --- | --- |
| Phase 0 | 제품 목표, 사용자, 문제, 범위 후보 |
| Gate 1 | 핵심 요구사항/시나리오와 release scope |
| Gate 2 | Product Design, API/DB/UI 계약, 보안/데이터 기준선 |
| Gate 3 | 핵심 회귀 테스트와 릴리즈 판단 기준 |
| Impl | 기능 단위 worker/subagent 구현과 self-check |
| Gate 4 | 릴리즈 후보 검증, 주요 UI/API/E2E, known issue |
| Gate 5 | release note, backlog, risk, merge/release 판단 |

## 6. Audit 전환 Gap

Product에서 Audit으로 전환할 때 보강할 수 있는 항목:

- 공공데이터 공통표준 준용/변형/신규 사유
- KISA/SR 또는 고객사 보안 기준 공식 매핑
- 상세 요구사항추적표 확장
- SEC-ID별 테스트/증적 1:1 연결
- 화면 상태별 UI 증적 확대
- FIND/CR/ISSUE와 승인 이력 정규화

전환은 단순 profile 값 변경이 아니라 gap을 확인하고 필요한 산출물을 추가하는 작업이다.

## 7. Product 실행과 검증 범위

이 절은 Product의 worker 입력과 검증 반복 기준이다. 다른 Core/adapter 문서의 일반적인 "worker 테스트 재실행"은 Product에서 아래 조건으로 해석한다. 품질/보안 계약, 사전검사, Gate 승인 조건은 완화하지 않는다.

- 원장 6종은 유지한다. worker에게는 현재 Run, 직접 관련 계약 ID/섹션과 공통 보안/데이터 제약을 전달한다. 전체 원장/과거 Run은 필요할 때만 읽는다. 상세 계약이 부족하면 먼저 보완하며, 분량을 줄이려고 필수 조건을 생략하지 않는다.
- worker 입력은 [PRODUCT_WORKER_GUIDE.md](PRODUCT_WORKER_GUIDE.md)를 사용한다. Orchestrator용 skill의 계획/위임/Gate 절차를 worker에게 수행시키지 않는다.
- 생성된 수정 경로와 검증 명령의 TBD는 Orchestrator가 실제 코드 구조와 프로젝트 명령으로 확정한다. Python/Node/Java 도구가 설치되어 있다는 이유만으로 모든 스택의 검증을 추가하지 않는다.
- worker는 코드/담당 테스트와 결과를 반환한다. 추적표, 최종 보고서, session, 선택적 위임 메타데이터 정규화는 Orchestrator가 맡는다. 비차단 경고는 보고 후 판단하며, 경고 0개를 구현 완료 조건으로 삼지 않는다.

| 상황 | 필요한 검증 |
| --- | --- |
| 설명/링크/선택 메타데이터만 수정 | 관련 문서 검사. 제품 테스트를 기계적으로 재실행하지 않음 |
| 국소 기능 변경 | 담당 단위/통합 테스트와 필요한 빌드 |
| API/DB/권한/공유 코드 또는 실행 설정 변경 | 영향 계약, 보안 경계와 관련 회귀 검증 확대 |
| 통합/충돌 해결로 검증 대상 코드가 변경됨 | 통합 결과에서 관련 테스트 재실행 |
| 증적 불확실, 새 실패/의심 또는 환경/의존성 변경 | 영향 검증 재실행 |
| Gate 4 릴리즈 후보 | 승인된 회귀/UI/API/E2E 검증 수행. Impl self-check만으로 대체하지 않음 |

Orchestrator는 실제 diff/scope와 명령/결과/증적을 확인한다. 검증 대상 소스(미커밋 변경 포함), 테스트, 의존성, 환경과 명령이 현재 대상에 일치하고 결과가 확인될 때만 기존 결과를 사용할 수 있다. 동일 브랜치명이나 worker의 성공 요약만으로 재사용하지 않는다. 확인한 근거와 재실행 여부/이유는 기존 `orchestrator_verification`에 기록한다. 필수 검증 미실행은 Pass가 아니다.

승인된 범위의 조사/구현/검증은 이어서 수행한다. 계약 변경, 차단 조건, 다음 Gate/릴리즈 승인에서는 기존 절차를 따른다. 규칙 때문에 중단하면 적용 문서와 조건을 밝힌다.
active 구현 Wave 하나 원칙은 유지한다. 독립적인 읽기 전용 검토를 겹칠 수 있지만, 원장/코드 동시 편집이나 재귀 위임은 추가하지 않는다. native 완료 알림/긴 대기가 제공되면 이를 사용하고, 새 근거 없는 짧은 조회나 "계속해" 메시지를 반복하지 않는다.

리뷰 호출은 [AGENT_RUN_PROTOCOL.md](AGENT_RUN_PROTOCOL.md) 5.4절의 위험도 판단을 따른다. 모든 Wave에서 일괄 실행하지 않으며, 호출한 독립 reviewer는 부모 대화를 상속하지 않는다. Codex native 모델 상속과 작업별 effort는 [CODEX_MODEL_POLICY.md](CODEX_MODEL_POLICY.md) 3.1절을 따른다. 사용자/고객이 명시한 검수는 이 기준으로 생략하지 않는다.
