# Codex/GPT Run Input Contract

> 상태: 초안 v0.1
> 목적: Codex/GPT 계열 에이전트에게 작업을 맡길 때 전달할 표준 작업지시서 형식을 정의한다.

## 1. 개념

Run Input Contract는 에이전트에게 주는 작업지시서다.

사람이 자연어로 요청하더라도 Adapter는 이를 다음 구조로 바꿔 에이전트에게 전달해야 한다.

```text
누가 보아도 같은 범위
같은 기준 문서
같은 관련 ID
같은 완료 조건
같은 금지사항
```

이 계약은 Codex/GPT가 임의로 범위를 넓히거나, 문서를 건너뛰거나, 테스트 없이 완료를 선언하는 일을 줄이기 위한 것이다.

## 2. 필수 필드

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `run_id` | 예 | 실행 단위 ID. 예: `RUN-001` |
| `adapter` | 예 | Adapter 이름. 예: `codex-gpt` |
| `persona` | 예 | 표준 작업 persona. 예: `requirements`, `design`, `build`, `review` |
| `agent_role` | 아니오 | adapter 호환용 보조 역할명. 예: `implementation-agent`, `review-agent` |
| `run_type` | 예 | `Discovery`, `Design`, `Implementation`, `Test`, `Evidence`, `Review` |
| `gate` | 예 | 현재 Gate. 예: `G2`, `G4` |
| `project` | 예 | 대상 프로젝트 또는 샘플 이름 |
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
adapter: codex-gpt
persona: build
agent_role: implementation-agent
run_type: Implementation
gate: G4
project:
  name: Board With Login Sample
  root: docs/examples/board-with-login
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
    - docs/examples/board-with-login/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G2-002_Program-Spec_v0.1.md
    - docs/examples/board-with-login/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/examples/board-with-login/DOC-QA-G3-001_Test-Cases_v0.1.md
  optional:
    - docs/examples/board-with-login/DOC-CORE-G2-001_Function-Spec_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G2-003_Screen-Spec_v0.1.md

scope:
  writable:
    - docs/examples/board-with-login/sample-app/app/api/posts.py
    - docs/examples/board-with-login/sample-app/app/services/post_service.py
    - docs/examples/board-with-login/sample-app/tests/
    - docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
  readonly:
    - docs/core/
    - docs/templates/
    - docs/seed-docs/reference-standards/
  excluded:
    - docs/ref-docs/
    - "**/*.db"
    - "**/__pycache__/"
    - "**/.ruff_cache/"

completion_criteria:
  - "관련 구현이 개발표준의 Router-Service-Repository 구조를 따른다."
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
      - docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md

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

## 4. 필드 작성 규칙

`goal`은 한 문장으로 쓴다.

좋은 예:

```text
SCR-003 게시글 목록 화면을 구현하고 UI-003 캡처 증적을 생성한다.
```

나쁜 예:

```text
화면 좀 정리
```

`related_ids`는 가능한 한 비워두지 않는다. 관련 ID가 불명확하면 Run을 시작하기 전에 Discovery 또는 Review Run으로 전환한다.

`source_documents.required`는 에이전트가 반드시 읽어야 하는 문서다. 컨텍스트가 부족하면 Adapter는 이 문서들을 요약해서라도 제공해야 한다.

`scope.writable` 밖의 파일 수정은 원칙적으로 금지한다. 단, 테스트 실행 중 생성물 제외를 위한 `.gitignore` 보정처럼 좁고 명백한 보정은 출력에 이유를 남긴다.

## 5. Codex/GPT 전달 프롬프트 기본형

Adapter는 YAML 입력 뒤에 다음 실행 지침을 붙인다.

```text
너는 Vulcan-Anvil Ex Codex/GPT Adapter를 통해 실행되는 에이전트다.
아래 Run 입력 계약을 기준으로만 작업한다.

작업 순서:
1. source_documents.required를 먼저 읽고 관련 ID를 확인한다.
2. scope.writable 안에서만 수정한다.
3. completion_criteria를 모두 만족하도록 구현/문서/테스트를 갱신한다.
4. verification.commands를 실행한다.
5. RUN_OUTPUT_CONTRACT 형식으로 결과를 보고한다.

금지:
- docs/ref-docs/를 읽거나 커밋하지 않는다.
- 관련 없는 리팩터링을 하지 않는다.
- 테스트를 실행하지 못했으면 통과로 보고하지 않는다.
- 추적표/결과서 갱신이 필요하면 누락하지 않는다.
```

## 6. 최소 입력과 완전 입력

초기 대화에서는 사람이 최소 입력만 줄 수 있다.

```yaml
goal: "게시글 작성 기능 구현"
related_ids: [REQ-005]
```

이 경우 Adapter는 추적표와 문서를 읽어 완전 입력으로 확장해야 한다.

완전 입력을 만들 수 없으면 `Blocked` 상태로 질문한다.

## 7. 입력 검증 체크리스트

Run 시작 전 Adapter는 다음을 확인한다.

| 체크 | 기준 |
| --- | --- |
| 관련 ID 존재 | 추적표 또는 산출물에 관련 ID가 존재한다 |
| 기준 문서 존재 | `source_documents.required` 파일이 존재한다 |
| 수정 범위 명확 | `scope.writable`이 비어 있지 않다 |
| 제외 경로 포함 | `docs/ref-docs/`가 제외되어 있다 |
| 완료 조건 명확 | 테스트 또는 증적 기준이 하나 이상 있다 |
| 출력 형식 지정 | `RUN_OUTPUT_CONTRACT.md`를 참조한다 |
