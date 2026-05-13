# Claude Run Input Contract

> 상태: v0.1
> 목적: Claude subagent에게 작업을 위임할 때 전달할 표준 작업지시서 형식을 정의한다.

## 1. 개념

Run Input Contract는 Orchestrator가 subagent에게 주는 작업지시서다.

Claude는 대화 컨텍스트를 유지하지만, subagent 위임 시에는 다음 구조를 명확히 전달해야 한다.

```text
누가 보아도 같은 범위
같은 기준 문서
같은 관련 ID
같은 완료 조건
같은 금지사항
```

이 계약은 subagent가 임의로 범위를 넓히거나, 문서를 건너뛰거나, 테스트 없이 완료를 선언하는 일을 줄이기 위한 것이다.

## 2. 필수 필드

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `run_id` | 예 | 실행 단위 ID. 예: `RUN-001` |
| `adapter` | 예 | `claude` |
| `persona` | 예 | 표준 작업 persona. 예: `requirements`, `design`, `build`, `review` |
| `claude_agent` | 예 | `.claude/agents/` 파일명. 예: `build-backend`, `review` |
| `run_type` | 예 | `Discovery`, `Design`, `Implementation`, `Test`, `Evidence`, `Review` |
| `gate` | 예 | 현재 Gate. 예: `G2`, `G4` |
| `goal` | 예 | 이번 Run에서 달성할 구체 목표 |
| `related_ids` | 예 | 요구사항, 설계, 보안, 테스트 ID |
| `source_documents` | 예 | 반드시 읽어야 하는 문서 |
| `scope` | 예 | 수정 가능/읽기 전용/제외 경로 |
| `completion_criteria` | 예 | 완료 판정 조건 |
| `verification` | 예 | 실행해야 할 테스트, 린트, 캡처 |
| `output_requirements` | 예 | 결과 보고 형식과 갱신할 산출물 |
| `question_policy` | 예 | 질문해야 하는 조건 |
| `security_policy` | 예 | 민감문서, 비밀, 외부전송 제한 |

## 3. 권장 YAML 형식

```yaml
run_id: RUN-001
adapter: claude
persona: build
claude_agent: build-backend
run_type: Implementation
gate: G4
goal: "PGM-005 게시글 작성 기능을 구현하고 관련 테스트를 통과시킨다."

related_ids:
  req: [REQ-005]
  nreq: [NREQ-001]
  ac: [AC-007, AC-008]
  func: [FUNC-005]
  scr: [SCR-005]
  pgm: [PGM-005]
  db: [DB-002]
  sec: [SEC-002, SEC-004]
  test: [UT-007, UT-008, IT-004]

source_documents:
  required:
    - docs/core/ID_SYSTEM.md
    - docs/core/TRACEABILITY_RULES.md
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    - docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md
    - docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
  optional:
    - docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md
    - docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md

scope:
  writable:
    - src/api/posts.py
    - src/services/post_service.py
    - tests/
    - docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
  readonly:
    - docs/core/
    - docs/templates/
    - docs/seed-docs/reference-standards/
  excluded:
    - docs/ref-docs/
    - "**/*.db"
    - "**/__pycache__/"

completion_criteria:
  - "관련 구현이 개발표준의 구조를 따른다."
  - "UT-007, UT-008, IT-004가 통과한다."
  - "실행 결과가 테스트 결과서에 반영된다."
  - "요구사항추적표에 증적이 연결된다."

verification:
  commands:
    - "python -m pytest tests -p no:cacheprovider"
    - "python -m ruff check ."
  evidence:
    required: true
    target_documents:
      - docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md

output_requirements:
  format: "RUN_OUTPUT_CONTRACT.md"
  include:
    - changed_files
    - related_ids
    - verification_results
    - evidence
    - open_issues
    - next_run_suggestion

question_policy:
  ask_when:
    - "요구사항과 설계문서가 충돌한다."
    - "scope.writable 밖의 파일 수정이 필요하다."
    - "보안 기준을 낮추는 선택이 필요하다."
    - "테스트 실패 원인이 요구사항 변경 없이는 해결되지 않는다."

security_policy:
  forbidden_paths:
    - docs/ref-docs/
  allowed_reference_paths:
    - docs/seed-docs/reference-standards/
  forbidden_actions:
    - "민감문서 내용을 출력에 인용하지 않는다."
    - "토큰, 비밀번호, 개인식별정보를 커밋하지 않는다."
    - "승인 없이 외부 네트워크로 프로젝트 파일을 전송하지 않는다."
```

## 4. Claude 전용 추가 필드

Claude subagent는 다음을 추가로 활용할 수 있다.

```yaml
# .claude/skills/ 자동 로드됨 — 명시 선택 사항
skills:
  - vulcan
  - security-baseline

# Bash tool 실행 허용 여부
allow_bash: true

# 브라우저 캡처 허용 여부 (Playwright/Chrome MCP)
allow_browser_capture: true
```

## 5. 필드 작성 규칙

`goal`은 한 문장으로 쓴다.

좋은 예:
```text
SCR-003 게시글 목록 화면을 구현하고 UI-003 캡처 증적을 생성한다.
```

나쁜 예:
```text
화면 좀 정리
```

`related_ids`는 가능한 한 비워두지 않는다. 관련 ID가 불명확하면 Run을 시작하기 전에 discovery 또는 review Run으로 전환한다.

`scope.writable` 밖의 파일 수정은 원칙적으로 금지한다.

## 6. 입력 검증 체크리스트

Run 시작 전 Orchestrator는 다음을 확인한다.

| 체크 | 기준 |
| --- | --- |
| 관련 ID 존재 | 추적표 또는 산출물에 관련 ID가 존재한다 |
| 기준 문서 존재 | `source_documents.required` 파일이 존재한다 |
| 수정 범위 명확 | `scope.writable`이 비어 있지 않다 |
| 제외 경로 포함 | `docs/ref-docs/`가 제외되어 있다 |
| 완료 조건 명확 | 테스트 또는 증적 기준이 하나 이상 있다 |
| Gate 일치 | `session.json.current_gate`와 `gate` 필드가 일치한다 |
