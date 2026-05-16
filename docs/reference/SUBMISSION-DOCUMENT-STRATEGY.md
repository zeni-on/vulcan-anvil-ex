# 제출용 문서 생성 전략

> 목적: Vulcan-Anvil Ex의 작업용 Markdown 산출물과 감리/고객 제출용 Word, Excel, HWPX 문서의 관계를 정의한다.

## 1. 기본 원칙

Vulcan-Anvil Ex는 작업 중에는 문서를 작게 나누어 관리한다.

작업용 문서는 에이전트가 읽고 갱신하기 쉽고, 추적성 검사를 수행하기 쉬워야 한다. 따라서 요구사항, 아키텍처, 프로그램, API, DB, 화면, 보안, 테스트, QA 문서는 각각 독립된 Markdown 산출물로 유지한다.

반면 제출용 문서는 고객, 감리, 검토자가 읽기 쉬운 일반 문서 형식이어야 한다. 제출 시점에는 여러 작업용 원천 문서를 하나의 제출본으로 합성할 수 있다.

핵심 원칙은 다음과 같다.

- 작업용 원천 문서는 Markdown으로 관리한다.
- 제출용 문서는 원천 문서에서 생성한다.
- 제출용 문서를 원천으로 삼아 다시 수작업 갱신하지 않는다.
- 제출용 문서의 수동 보정이 필요하면 보정 사유를 남기고 가능한 한 원천 문서에 되돌려 반영한다.
- 제출용 문서 생성 규칙은 템플릿과 코드로 재현 가능해야 한다.

## 2. 작업용 문서와 제출용 문서의 역할

| 구분 | 목적 | 형식 | 사용 시점 | 주 사용자 |
| --- | --- | --- | --- | --- |
| 작업용 원천 문서 | 에이전트 작성, 단계별 검증, 추적성 관리 | Markdown | Phase/Gate 진행 중 | Orchestrator, persona, PL, 개발자 |
| 제출용 합본 문서 | 고객/감리/내부 승인 제출 | DOCX / XLSX / HWPX / PDF | Gate 완료, 중간보고, 최종 제출 | 고객, 감리자, 승인자 |
| 증적 패키지 | 실행 결과, 화면 캡처, 로그, 테스트 결과 보존 | 이미지 / 로그 / XLSX / PDF | Gate 4, Gate 5 | QA, 감리자, 운영/인수 담당 |

## 3. 원천 문서 구성

대표적인 작업용 원천 문서는 다음과 같다.

```text
docs/artifacts/00-discovery/
  DOC-CORE-P0-001_Project-Brief_v0.1.md
  DOC-CORE-P0-002_Stakeholder-And-Scope_v0.1.md
  DOC-CORE-P0-003_As-Is-To-Be_v0.1.md
  DOC-CORE-P0-004_Risk-And-Assumption_v0.1.md

docs/artifacts/01-requirements/
  DOC-CORE-G1-001_Requirements-Spec_v0.1.md

docs/artifacts/02-design/
  architecture/DOC-ARCH-G2-001_SW-Architecture_v0.1.md
  function/DOC-CORE-G2-001_Function-Spec_v0.1.md
  program/DOC-CORE-G2-002_Program-Spec_v0.1.md
  api/DOC-API-G2-001_API-Spec_v0.1.md
  data/DOC-DATA-G2-001_Project-Glossary_v0.1.md
  data/DOC-DATA-G2-002_Database-Spec_v0.1.md
  screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md
  security/DOC-SEC-G2-001_Security-Guide_v0.1.md
  development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md

docs/artifacts/03-test/
  DOC-QA-G3-001_Test-Cases_v0.1.md

docs/artifacts/04-review/
  DOC-QA-G4-001_QA-Finding_v0.1.md
  DOC-QA-G4-002_Test-Result_v0.1.md

docs/artifacts/02-traceability/
  DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
```

## 4. 제출용 SW 아키텍처 문서

제출용 SW 아키텍처 정의서는 내부 작업용 SW 아키텍처 문서 하나만 그대로 변환하지 않는다. 필요하면 상위설계, 요구사항, 보안, API, DB, 화면, 추적표의 내용을 합성한다.

제출용 SW 아키텍처 정의서의 권장 구성은 다음과 같다.

| 제출 섹션 | 주요 원천 문서 | 설명 |
| --- | --- | --- |
| 문서 개요 | SW Architecture, Document Metadata | 문서 목적, 버전, 승인 정보 |
| 사업/시스템 개요 | Project Brief, Stakeholder/Scope, As-Is/To-Be | 상위설계 요약 |
| 요구사항 및 품질속성 요약 | Requirements Spec, Traceability Matrix | 기능/비기능 요구사항 요약 |
| 시스템 구성 | SW Architecture | C1/C2, 시스템 경계, 컨테이너 구조 |
| 논리 아키텍처 | SW Architecture, Function Spec, Program Spec | 주요 논리 영역과 책임 |
| 물리 아키텍처 | SW Architecture, Development Standard | 서버, 네트워크, 배포 단위, 런타임 |
| 보안 아키텍처 | Security Guide, SW Architecture | 인증, 인가, 세션/토큰, 암호화, 로그/감사 |
| 데이터 및 인터페이스 구조 | DB Spec, API Spec, SW Architecture | 데이터 저장소, API, 외부 연계 |
| 주요 설계 결정 | SW Architecture, ADR | 기술 선택, 대안, 영향 범위 |
| 테스트/검증 연결 | Test Cases, Traceability Matrix | 주요 검증 기준과 테스트 연결 |
| 추적성 요약 | Traceability Matrix | REQ/NREQ/SEC와 설계/테스트 연결 |

작업용 SW 아키텍처 문서는 상위설계를 재작성하지 않고 참조한다. 제출용 SW 아키텍처 정의서에서는 독자가 별도 원천 문서를 열지 않아도 이해할 수 있도록 필요한 범위만 요약해 합성한다.

## 5. 제출용 산출물 생성 위치

제출용 문서는 원천 문서와 분리해 생성한다.

```text
docs/exports/
  architecture/
    SW-Architecture-Submission_v1.0.docx
    SW-Architecture-Submission_v1.0.pdf
  requirements/
    Requirements-Submission_v1.0.docx
  traceability/
    Traceability-Matrix_v1.0.xlsx
  evidence/
    QA-Evidence-Package_v1.0.zip
```

`docs/exports/`는 프로젝트 정책에 따라 커밋 대상이 될 수도 있고, 빌드 산출물로 제외될 수도 있다. 고객/감리 제출 이력 보존이 중요하면 제출본을 릴리즈 태그 또는 별도 저장소에 보존한다.

## 6. DOCX 템플릿 전략

향후 DOCX 제출본 생성을 위해 다음 구조를 사용한다.

```text
docs/export-templates/
  docx/
    sw-architecture/
      template.docx
      manifest.json
    requirements/
      template.docx
      manifest.json
```

`template.docx`는 회사/프로젝트 표지, 머리말, 꼬리말, 목차, 스타일, 표 서식을 포함한다.

`manifest.json`은 원천 문서와 제출 섹션의 매핑을 정의한다.

예시:

```json
{
  "document_type": "sw-architecture-submission",
  "output": "docs/exports/architecture/SW-Architecture-Submission_v1.0.docx",
  "sections": [
    {
      "title": "사업/시스템 개요",
      "sources": [
        "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md",
        "docs/artifacts/00-discovery/DOC-CORE-P0-002_Stakeholder-And-Scope_v0.1.md"
      ],
      "mode": "summarize"
    },
    {
      "title": "시스템 구성",
      "sources": [
        "docs/artifacts/02-design/architecture/DOC-ARCH-G2-001_SW-Architecture_v0.1.md"
      ],
      "mode": "extract",
      "sections": ["논리 아키텍처", "물리 아키텍처"]
    }
  ]
}
```

## 7. 생성 코드 방향

향후 `vulcan.py` 또는 별도 모듈에 제출용 문서 생성 명령을 추가한다.

예상 명령:

```bash
python vulcan.py export-doc sw-architecture --format docx
python vulcan.py export-doc requirements --format docx
python vulcan.py export-doc traceability --format xlsx
```

생성기는 다음 단계를 수행한다.

1. `manifest.json`을 읽는다.
2. 원천 Markdown 문서를 파싱한다.
3. 필요한 섹션을 추출하거나 요약한다.
4. Mermaid 다이어그램은 이미지 또는 원문 코드블록으로 변환한다.
5. 표는 DOCX/XLSX 표로 변환한다.
6. 원천 문서 ID, 버전, Git commit SHA를 제출본 메타데이터에 기록한다.
7. 생성 결과를 `docs/exports/`에 저장한다.
8. 제출본 생성 로그를 `docs/runs/` 또는 별도 export log에 남긴다.

## 8. 검증 기준

제출용 문서는 생성 후 다음을 검증한다.

| 검증 항목 | 기준 |
| --- | --- |
| 원천 문서 연결 | 제출본에 사용된 원천 문서 목록과 버전이 기록되어야 한다 |
| 추적성 | REQ/NREQ/SEC와 설계/테스트 연결이 누락되지 않아야 한다 |
| 표 렌더링 | Markdown 표가 DOCX/XLSX에서 깨지지 않아야 한다 |
| 다이어그램 | Mermaid 다이어그램이 이미지 또는 읽을 수 있는 코드블록으로 포함되어야 한다 |
| 민감정보 | `docs/ref-docs/`의 민감 자료 원문이 제출본에 그대로 포함되지 않아야 한다 |
| 재현성 | 같은 commit에서 같은 명령을 실행하면 동일한 제출본을 생성할 수 있어야 한다 |

## 9. 운영 원칙

- 제출본은 원천 문서를 대체하지 않는다.
- 제출본에서 발견된 오류는 가능하면 원천 문서를 수정한 뒤 재생성한다.
- 수동 보정이 필요한 경우 보정 내역, 보정자, 보정 일시, 사유를 기록한다.
- 제출본 생성 전 `check-trace`, `check-architecture --level baseline`, 관련 테스트 검증을 먼저 통과한다.
- 최종 제출본은 Git tag, release, 또는 별도 제출 패키지로 보존한다.
