---
paths:
  - "docs/artifacts/02-design/**"
---

# Gate 2: 설계 규칙

## 산출물 (영역별 분할)

| 영역 | 경로 | 템플릿 | 대표 ID |
| --- | --- | --- | --- |
| 기능 명세 | `docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md` | `FUNCTION_SPEC_TEMPLATE.md` | `FUNC` |
| 프로그램 명세 | `docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md` | `PROGRAM_SPEC_TEMPLATE.md` | `PGM` |
| API 명세 | `docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md` | `API_SPEC_TEMPLATE.md` | `API` |
| 화면 명세 | `docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md` | `SCREEN_SPEC_TEMPLATE.md` | `SCR` |
| 단어사전 | `docs/artifacts/02-design/data/DOC-DATA-G2-001_Project-Glossary_v0.1.md` | `PROJECT_GLOSSARY_TEMPLATE.md` | — |
| DB 명세 | `docs/artifacts/02-design/data/DOC-DATA-G2-002_Database-Spec_v0.1.md` | `DATABASE_SPEC_TEMPLATE.md` | `DB`, `IF` |
| 보안 가이드 | `docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md` | `SECURITY_GUIDE_TEMPLATE.md` | `SEC` |
| 개발 표준 | `docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md` | `DEVELOPMENT_STANDARD_TEMPLATE.md` | — |

## 원칙

- 설계 문서는 **인터페이스와 제약조건**을 정의한다. 구현 코드를 작성하지 않는다.
- 각 설계 요소에 단위테스트 `UT-NNN`을 사전 배정한다.
- 보안 통제는 `SEC-NNN`으로 식별하고 `docs/core/SECURITY_BASELINE.md` / `KISA_SECURITY_RULES.md`와 매핑한다.
- 화면 흐름은 design(라우팅/API/PGM)가 먼저, screen-design(SCR)가 그 위에 작업한다.
- 데이터 항목은 `docs/core/DATA_STANDARD_RULES.md`와 `seed-docs/`의 공공데이터 공통표준을 우선 확인한다.

## Gate 2 → Gate 3 진입 전 필수 검수 (`docs/core/AGENT_RUN_PROTOCOL.md` §5.1)

| 검수 | persona | 최소 확인 |
| --- | --- | --- |
| 요구사항 대비 설계 | review / design | 모든 REQ/AC가 FUNC/SCR/PGM/DB/SEC와 연결됨 |
| 보안 검수 | security-review | KISA/SR, OWASP, CWE 매핑 누락 없음 |
| 화면 검수 | screen-review | SCR 목록/상태/시안/메시지/UI 증적 기준 충족 |
| UI 품질 검수 | ui-review | 레이아웃 밀도/상태 표현/모바일 기준 |
| 개발표준 검수 | development-review | 언어/구조/메시지/주석/테스트/빌드 명령 충족 |

하나라도 Failed/Blocked이면 Gate 3로 넘어가지 않는다.

## 추적표

`docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md`의 `설계 문서`, `SEC`, `UT 사전배정` 컬럼을 채운다. 설계 문서 본문에는 REQ-ID를 명시해 `check-trace`가 grep할 수 있도록 한다.
