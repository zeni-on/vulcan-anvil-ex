# 개발표준정의서

```yaml
---
document_id: DOC-DEV-G2-001
title: Development Standard
title_ko: 개발표준정의서
project: "{PROJECT_NAME}"
gate: G2
status: Draft
version: v0.1
owner_role: Technical Architect
author: "{AUTHOR}"
reviewer: "{REVIEWER}"
approver: "{APPROVER}"
created_at: "{YYYY-MM-DD}"
updated_at: "{YYYY-MM-DD}"
related_ids:
  - REQ-001
  - FUNC-001
  - PGM-001
  - UT-001
change_reason: 최초 초안 작성
---
```

## 1. 문서 목적

본 문서는 프로젝트의 개발 언어, 패키지 구조, 아키텍처 패턴, 코드 컨벤션, 주석 컨벤션, 빌드/실행/테스트 방법, 에이전트 작업 규칙을 정의한다.

에이전트와 개발자는 구현 전에 본 문서와 관련 요구사항/설계/테스트 산출물을 함께 확인해야 한다.

기술스택별 기본 규칙은 `docs/core/TECH_STACK_BASELINES.md`를 기준으로 한다. 본 문서는 해당 베이스라인을 프로젝트 상황에 맞게 구체화한 실행 기준이며, 구현 단계에서는 본 문서가 우선한다.

## 2. 적용 범위

| 항목 | 내용 |
| --- | --- |
| 적용 시스템 |  |
| 적용 모듈 |  |
| 적용 언어 |  |
| 적용 프레임워크 |  |
| 적용 기술스택 베이스라인 | 예: Spring Boot + Spring Security + React |
| 적용 테스트 도구 |  |
| 제외 범위 |  |

## 3. 기술 스택

| 구분 | 표준 | 버전/범위 | 선정 사유 | 비고 |
| --- | --- | --- | --- | --- |
| Language |  |  |  |  |
| Runtime |  |  |  |  |
| Web Framework |  |  |  |  |
| Database |  |  |  |  |
| ORM/Query |  |  |  |  |
| Test |  |  |  |  |
| Build/Package |  |  |  |  |
| Lint/Format |  |  |  |  |

적용 베이스라인:

| 영역 | 선택 | 참조 베이스라인 | 프로젝트 조정사항 |
| --- | --- | --- | --- |
| Backend |  | `TECH_STACK_BASELINES.md` §3 또는 §8 |  |
| Backend Security |  | `TECH_STACK_BASELINES.md` §4 |  |
| Frontend |  | `TECH_STACK_BASELINES.md` §5, §6 또는 §7 |  |
| Test/E2E |  | `TECH_STACK_BASELINES.md` 각 스택 테스트 규칙 |  |

Spring Boot를 사용하는 경우 다음 항목을 반드시 확정한다.

| 항목 | 프로젝트 기준 |
| --- | --- |
| Base Package | 예: `com.example.todo` |
| MVC 적용 방식 | 예: Controller -> Service -> Repository -> Entity |
| 패키지 구조 기준 | 예: feature 우선 `domain/{domain}/...` |
| JPA 사용 여부 | 예: Spring Data JPA + QueryDSL |
| Entity/DTO 분리 | 예: Entity 직접 응답 금지, Response DTO 사용 |
| Transaction 기준 | 예: Service 계층에서만 `@Transactional` |
| Pagination/Sort 기준 | 예: page/size/sort 허용값과 최대 size |
| Auditing 기준 | 예: createdAt/updatedAt/createdBy/updatedBy |

## 4. 아키텍처 및 패키지 구조

아키텍처 패턴:

```text
{예: Router -> Service -> Repository -> Database}
```

패키지 구조:

```text
{PROJECT_ROOT}/
  app/
    api/
    services/
    repositories/
    models/
    schemas/
    core/
    resources/
  tests/
    unit/
    integration/
  docs/
```

| 계층 | 책임 | 허용 의존성 | 금지 사항 |
| --- | --- | --- | --- |
| API/Controller | 요청/응답, 인증 확인, 입력 스키마 연결 | Service, Schema | DB 직접 접근 |
| Service | 업무 규칙, 트랜잭션 경계, 권한 판단 | Repository, Model | HTTP 객체 직접 의존 |
| Repository | 데이터 접근 | DB Session, Model | 업무 정책 판단 |
| Model/Entity | 데이터 구조 |  | 외부 API 호출 |
| Schema/DTO | 입출력 데이터 검증 |  | 업무 로직 포함 |

Spring Boot MVC/JPA 패키지 구조 예:

```text
src/main/java/{basePackage}/
  config/
  common/
    error/
    message/
    response/
  domain/{domainName}/
    controller/
    service/
    repository/
    entity/
    dto/
    mapper/
  security/
src/main/resources/
  messages_ko.properties
  application.yml
src/test/java/{basePackage}/
  domain/{domainName}/
```

JPA 기준:

| 항목 | 규칙 | 예외 |
| --- | --- | --- |
| Entity 응답 노출 | 금지, Response DTO로 변환 | 내부 배치/테스트 전용은 사유 기록 |
| Fetch 전략 | 기본 LAZY, 필요한 조회는 fetch join/EntityGraph/projection 사용 |  |
| Cascade/orphanRemoval | 생명주기 종속 시에만 사용 | 사유 기록 |
| Query 방식 | Spring Data JPA, JPQL, QueryDSL, native query 선택 기준 명시 | native query는 DB 종속성 기록 |
| 트랜잭션 | Service 계층에서 관리 | Repository 직접 트랜잭션은 사유 기록 |
| Auditing | 생성/수정 일시와 사용자 기준 명시 |  |

## 5. 코드 컨벤션

| 항목 | 규칙 | 예외 |
| --- | --- | --- |
| 네이밍 |  |  |
| 함수/메서드 크기 |  |  |
| 모듈 분리 |  |  |
| 예외 처리 |  |  |
| 로그 |  |  |
| 설정값 |  |  |
| 외부 의존성 |  |  |

언어/프레임워크별 상세 기준:

| 스택 | 적용 규칙 | 예외/조정 사유 |
| --- | --- | --- |
| Spring Boot |  |  |
| Spring Security |  |  |
| React/Next.js/Vue |  |  |
| Python/FastAPI |  |  |

## 6. 주석 컨벤션

기본 원칙:

- 코드가 그대로 설명하는 내용은 주석으로 반복하지 않는다.
- 요구사항, 보안 기준, 성능 제약, 추적 ID, 복잡한 의사결정은 주석 또는 docstring에 남길 수 있다.
- 임시 우회 처리는 `ISSUE-ID` 또는 `DEC-ID`와 함께 남긴다.

추적 ID 표기 예:

```text
REQ: REQ-001
PGM: PGM-001
SEC: SEC-001
TEST: UT-001
```

스택별 주석 기준:

| 스택 | 기준 |
| --- | --- |
| Java/Spring | 보안 판단, 트랜잭션 경계, 복잡한 도메인 규칙에는 관련 `REQ/SEC/PGM`을 남길 수 있다. 단순 getter/setter, 단순 CRUD 위임에는 주석을 쓰지 않는다. |
| TypeScript/React/Next/Vue | 복잡한 상태 전이, 권한 가드, API 오류 변환, 접근성 예외에는 관련 `REQ/SCR/SEC`을 남길 수 있다. JSX/Template이 그대로 설명하는 내용은 주석으로 반복하지 않는다. |
| Python/FastAPI | 보안 dependency, 권한 판단, repository transaction, 복잡한 validation에는 관련 `REQ/SEC/PGM`을 남길 수 있다. |

## 7. API 및 오류 응답 규칙

성공 응답 표준:

```json
{
  "data": {},
  "message": "OK"
}
```

오류 응답 표준:

```json
{
  "error": {
    "code": "ERR-001",
    "message": "요청을 처리할 수 없습니다."
  }
}
```

| 오류 코드 | 의미 | HTTP 상태 | 관련 보안 기준 |
| --- | --- | ---: | --- |
| ERR-001 |  |  |  |

## 8. 메시지 관리 규칙

기본 원칙:

- 사용자에게 노출되는 메시지는 코드에 직접 하드코딩하지 않는다.
- 사용자 노출 메시지는 메시지 리소스 파일에서 관리한다.
- API 응답은 메시지 코드와 메시지 본문을 함께 반환한다.
- 테스트는 원칙적으로 메시지 본문보다 메시지 코드를 검증한다.
- 인증/권한/보안 오류 메시지는 계정 존재 여부, 내부 구조, 권한 판단 상세를 노출하지 않는다.
- 문구 변경은 코드 변경 없이 메시지 리소스 수정으로 처리할 수 있어야 한다.

메시지 리소스 예:

```text
app/resources/messages.ko.yml
app/resources/messages.en.yml
```

메시지 코드 예:

```yaml
MSG-001: 정상 처리되었습니다.
ERR-001: 요청을 처리할 수 없습니다.
```

| 구분 | 하드코딩 허용 여부 | 관리 방식 | 비고 |
| --- | --- | --- | --- |
| 사용자 오류 메시지 | 금지 | 메시지 리소스 | API `error.message` |
| 사용자 성공/안내 메시지 | 금지 | 메시지 리소스 | API `message` |
| 입력값 검증 메시지 | 금지 | 메시지 리소스 | Validation 응답 |
| 보안 관련 메시지 | 금지 | 메시지 리소스 | 노출 정보 최소화 |
| 로그 내부 메시지 | 허용 | 코드 또는 상수 | 민감정보 출력 금지 |
| 테스트 설명 문자열 | 허용 | 테스트 코드 | 메시지 본문 검증 지양 |
| 개발자 전용 assertion | 허용 | 코드 | 사용자 노출 금지 |

## 9. DB 접근 및 데이터 표준 규칙

- DB 객체와 컬럼은 DB명세서의 `DB-ID`와 연결한다.
- 용어/단어/도메인은 프로젝트 단어사전과 공공데이터 공통표준 검토 상태를 따른다.
- 개인정보 또는 중요정보는 저장/전송/로그 출력 전에 보안항목을 확인한다.

## 10. 보안 구현 규칙

| 보안 영역 | 구현 규칙 | 참조 기준 | 검증 테스트 |
| --- | --- | --- | --- |
| 입력값 검증 |  | KISA-SD-2021 SR1-1, SR1-9 |  |
| 인증 |  | KISA-SD-2021 SR2-1 |  |
| 권한 |  | KISA-SD-2021 SR2-4 |  |
| 비밀번호/암호 |  | KISA-SD-2021 SR2-3, SR2-6, SR2-7 |  |
| 중요정보 전송 |  | KISA-SD-2021 SR2-8 |  |
| 예외처리 |  | KISA-SD-2021 SR3-1 |  |
| 세션통제 |  | KISA-SD-2021 SR4-1 |  |

## 11. 테스트 컨벤션

| 항목 | 규칙 |
| --- | --- |
| 테스트 파일명 |  |
| 테스트 함수명 |  |
| 단위테스트 기준 |  |
| 통합테스트 기준 |  |
| 성능테스트 기준 |  |
| 테스트 데이터 |  |
| 테스트 증적 |  |

테스트 함수명 예:

```text
test_UT_001_signup_success()
test_IT_001_signup_then_login()
```

## 12. 빌드, 실행, 테스트 명령

구현 및 QA 단계에서 실행해야 하는 명령을 정의한다. 에이전트는 필수 명령을 실행한 뒤 `docs/runs/`의 Run 문서와 `DOC-QA-G4-002_Test-Result_v0.1.md`에 결과를 기록한다.

| 목적 | 명령 | 필수 여부 | 실행 시점 | 결과 기록 위치 | 비고 |
| --- | --- | --- | --- | --- | --- |
| 의존성 설치 |  | 필수/선택 | 최초 구현 또는 환경 갱신 | Run |  |
| 개발 서버 실행 |  | 선택 | 화면 확인 또는 수동 QA | Run / Test Result |  |
| 단위 테스트 |  | 필수 | Build Wave 완료 시, Gate 4 전 | Run / Test Result |  |
| 통합 테스트 |  | 필수/선택 | Gate 4 전 또는 영향 범위 검증 | Run / Test Result |  |
| E2E/UI 테스트 |  | 필수/선택 | 화면 기능 구현 후, Gate 4 | Run / Test Result / UI Evidence |  |
| 정적 검사 |  | 필수/선택 | Build Wave 완료 시, Gate 4 전 | Run |  |
| 빌드 |  | 필수/선택 | Gate 4 전, 릴리즈 후보 전 | Run / Test Result |  |
| 포맷 |  | 선택 | 구현 중 또는 커밋 전 | Run |  |

기술스택별 명령 예:

| 스택 | 단위 테스트 | 정적 검사 | 빌드 | 비고 |
| --- | --- | --- | --- | --- |
| Spring Boot/Gradle | `./gradlew test` | `./gradlew check` | `./gradlew build` | Windows에서는 `.\gradlew.bat test` 형식 사용 가능 |
| Spring Boot/Maven | `./mvnw test` | `./mvnw verify` | `./mvnw package` | Windows에서는 `.\mvnw.cmd test` 형식 사용 가능 |
| React/Next.js | `npm test` | `npm run lint` | `npm run build` | 프로젝트 스크립트명에 맞게 조정 |
| Vue.js | `npm run test:unit` | `npm run lint` | `npm run build` | Vitest/ESLint 기준 |
| Python/FastAPI | `pytest` | `ruff check .` | 해당 시 작성 | 프로젝트 도구에 맞게 조정 |

필수 명령을 실행하지 못한 경우에는 `Not Run` 또는 `Skipped`로 기록하고 사유, 영향 범위, 후속 조치를 남긴다. 실행하지 않은 명령을 `Pass`로 기록하지 않는다.

## 13. 에이전트 작업 규칙

에이전트는 다음 순서를 따른다.

1. 관련 요구사항정의서, 기능명세서, 프로그램명세서, 화면설계서, DB명세서, 테스트케이스를 확인한다.
2. 구현 대상의 `REQ/FUNC/PGM/SCR/DB/SEC/UT/IT/PT` ID를 확인한다.
3. 사용자가 선택한 기술스택에 맞는 `docs/core/TECH_STACK_BASELINES.md` 섹션과 본 개발표준정의서의 패키지 구조, 코드 컨벤션을 따른다.
4. 문서에 없는 기능, API, DB 컬럼, 테스트를 임의로 추가하지 않는다.
5. 필요한 변경이 있으면 먼저 `ISSUE` 또는 `CR` 후보로 기록한다.
6. 사용자 노출 메시지를 코드에 직접 하드코딩하지 않고 메시지 리소스를 사용한다.
7. 구현 후 테스트 결과와 증적을 추적표에 연결할 수 있게 남긴다.

## 14. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | {YYYY-MM-DD} | 최초 초안 작성 |  |  |  |
