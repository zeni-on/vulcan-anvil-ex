# Claude Run Input Contract

> 상태: v0.2.2
> 목적: Claude subagent에게 작업을 위임할 때 전달할 표준 작업지시서 형식을 정의한다.

## 1. 개념

Run Input Contract는 Orchestrator가 subagent에게 주는 작업지시서다.

Claude는 대화 컨텍스트를 유지하지만, subagent 위임 시에는 다음 구조를 명확히 전달해야 한다.

```text
누가 보아도 같은 범위 / 같은 기준 문서 / 같은 관련 ID / 같은 완료 조건 / 같은 금지사항
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
| `source_documents` | 예 | 3-tier 문서 구분 (`read_first` / `working_documents` / `reference_on_demand`) |
| `design_sequence` | G2 권장 | Gate 2 설계 순서(G2-01~G2-10)와 현재 Run 위치 |
| `scope` | 예 | 수정 가능/읽기 전용/제외 경로 |
| `completion_criteria` | 예 | 완료 판정 조건 |
| `verification` | 예 | 실행할 검증 명령 (cwd / Windows·POSIX 명령 / 성공 기준 / 증적 경로 / Not Run 기준) |
| `gate_exit_policy` | 예 | Gate 종료 시 정지/승인 질문/다음 Gate 진행 제한 |
| `ui_evidence_policy` | 화면 작업 시 | UI 증적의 상태/시나리오 단위 연결 기준 |
| `ui_implementation_contract_policy` | 화면 작업 시 | UIREF/ui-baseline을 구현 계약으로 전환·판정 기준 |
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
  ac: [AC-007, AC-008]
  func: [FUNC-005]
  scr: [SCR-005]
  pgm: [PGM-005]
  db: [DB-002]
  sec: [SEC-002, SEC-004]
  test: [UT-007, UT-008, IT-004]

source_documents:
  read_first:
    - .claude/CLAUDE.md
    - session.json
    - docs/adapters/claude/GATE_PROMPTS.md
    - docs/core/AGENT_RUN_PROTOCOL.md
  working_documents:
    - docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md
    - docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
  reference_on_demand:
    - docs/core/ID_SYSTEM.md
    - docs/core/TRACEABILITY_RULES.md
    - docs/core/SECURITY_BASELINE.md
    - docs/templates/

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
  - "검증 명령 실행 결과(cwd/exit/성공기준/로그)가 테스트 결과서에 기록된다."
  - "요구사항추적표에 증적이 연결된다."

verification:
  commands:
    - id: UT-005
      purpose: "단위 테스트"
      cwd: "repository root"
      command_windows: "py -m pytest tests -p no:cacheprovider"
      command_posix: "python -m pytest tests -p no:cacheprovider"
      required: true
      success_criteria: "exit code 0, 실패 0건"
      evidence_path: "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md"
      log_path: ".pytest_cache/output.txt"
      not_run_policy: "환경 미준비 시 Not Run 사유 + 후속 조치 기록"
    - id: LINT-001
      purpose: "정적 검사"
      cwd: "repository root"
      command_posix: "python -m ruff check ."
      required: true
      success_criteria: "exit code 0, 오류 0건"
      evidence_path: "Run 본문 verification_results"
  evidence:
    required: true
    target_documents:
      - docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md

gate_exit_policy:
  stop_required: true
  next_gate_requires_user_approval: true
  approval_evidence_required: true
  allowed_next_action: "현재 Gate 산출물 요약 + 미해결 항목 + 다음 Gate 제안 + 승인 질문을 남기고 대기한다."
  forbidden_actions:
    - "사용자의 명시 승인 없이 다음 Gate 산출물을 작성하지 않는다."
    - "사용자의 명시 승인 없이 구현·테스트 실행·QA 승인·릴리즈 승인을 선언하지 않는다."
    - "대화상 명시 승인 없이 Run 또는 릴리즈 승인서에 'User Approved'로 기록하지 않는다."

# Gate 2 Run인 경우에만 사용. docs/core/GATE2_DESIGN_SEQUENCE.md §2 참조.
design_sequence:
  current_step: "G2-05 Program / API Spec"
  recommended_order:
    - "G2-01 Kickoff / 설계 범위 고정"
    - "G2-02 SW Architecture Draft"
    - "G2-03 Screen / User Flow"
    - "G2-04 Function Spec"
    - "G2-05 Program / API Spec"
    - "G2-06 Data / DB Spec"
    - "G2-07 Security Guide"
    - "G2-08 Development Standard"
    - "G2-09 SW Architecture Baseline 보강"
    - "G2-10 Design Review / Gate 3 승인 대기"
  next_run_candidates:
    - "G2-06 Data / DB Spec"

# 화면 작업 시 사용
ui_evidence_policy:
  state_level_required: true
  id_pattern: "UI-001-01"   # SCR-단위가 아니라 SCR×상태 단위
  states_required:
    - 기본
    - 로딩
    - 오류
    - 성공
    - 전환
  minimum_fields:
    - UI-ID
    - 관련 SCR
    - 상태/시나리오
    - 기대 화면 (UIREF/ui-baseline 경로)
    - 실제 캡처 경로
    - 판정 (Pass / FIND / Not Run)
  forbidden:
    - "기대 화면과 다른 캡처를 Pass로 기록하지 않는다."
    - "캡처가 비어 있거나 누락된 상태를 묵시적으로 Pass 처리하지 않는다."

# UIREF/ui-baseline이 있는 화면 작업 시 사용
ui_implementation_contract_policy:
  required_when: "화면설계서에 UIREF, 이미지 시안, HTML/CSS/JS 화면 퍼블리싱 산출물, Figma, 기존 화면 캡처, ui-baseline 경로가 있는 경우"
  gate2_required_fields:
    - 기준 파일/CSS 경로
    - 필수 유지 요소 (레이아웃, 핵심 컴포넌트, 텍스트)
    - 변경 허용 항목
    - 변경 금지 항목
    - 비교 방식 (screenshot diff / DOM 비교 / 시각 검수)
  gate3_test_fields:
    - "UI-ID에 contract의 필수 유지/금지 항목이 기대결과로 반영"
  impl_checklist:
    - "구현 전 관련 SCR의 UI Implementation Contract 확인"
    - "화면 퍼블리싱 CSS 또는 동등한 레이아웃/class 구조 재사용 여부 기록"
    - "보안가이드로 인해 바꾼 문구/필드/흐름은 DEC/ISSUE/FIND/CR 중 하나로 기록"
    - "기본/오류/성공/전환 상태가 Gate 3 UI-ID와 연결되어 있는지 확인"
    - "구현 screenshot이 기준 UIREF와 비교 가능한 위치에 저장되는지 확인"
  gate4_required_evidence:
    - 기준 UIREF screenshot 또는 ui-baseline 경로
    - 구현 screenshot
    - 차이 판정 (Pass / FIND / CR)

output_requirements:
  format: "RUN_OUTPUT_CONTRACT.md"
  include:
    - changed_files
    - related_ids
    - verification_results   # cwd/명령/exit/성공/로그·증적 포함
    - evidence
    - open_issues
    - next_run_suggestion

question_policy:
  ask_when:
    - "요구사항과 설계문서가 충돌한다."
    - "scope.writable 밖의 파일 수정이 필요하다."
    - "보안 기준을 낮추는 선택이 필요하다."
    - "테스트 실패 원인이 요구사항 변경 없이는 해결되지 않는다."
    - "UIREF/ui-baseline은 있는데 UI Implementation Contract가 비어 있어 비교 기준을 정할 수 없다."

security_policy:
  forbidden_paths: [docs/ref-docs/]
  allowed_reference_paths: [docs/seed-docs/reference-standards/]
  forbidden_actions:
    - "민감문서 내용을 출력에 인용하지 않는다."
    - "토큰, 비밀번호, 개인식별정보를 커밋하지 않는다."
    - "승인 없이 외부 네트워크로 프로젝트 파일을 전송하지 않는다."
```

## 4. Claude 전용 추가 필드

```yaml
skills: [vulcan, security-baseline]   # 자동 로드 — 명시는 선택
allow_bash: true                       # Bash tool 실행 허용
allow_browser_capture: true            # Playwright/Chrome MCP UI 캡처 허용
```

## 5. 필드 작성 규칙

- **`goal`**: 한 문장. 예 `"SCR-003 게시글 목록 화면을 구현하고 UI-003 캡처 증적을 생성한다."` (나쁜 예: `"화면 좀 정리"`)
- **`related_ids`**: 비워두지 않는다. 불명확하면 Run 시작 전 discovery/review Run으로 전환.
- **`source_documents` 3-tier**:
  - `read_first`: 작업 시작 전 반드시 읽는 문서 (CLAUDE.md, session.json, 관련 GATE_PROMPTS, AGENT_RUN_PROTOCOL 등 운영 문서)
  - `working_documents`: 이번 Run에서 작성/갱신할 대상 문서
  - `reference_on_demand`: 필요할 때만 보는 표준/템플릿/Core 규칙
- **`scope.writable`**: 밖의 파일 수정은 원칙적으로 금지. 필요 시 `Blocked` 또는 `question_policy`.
- **`verification.commands`**: 명령 문자열만으로 불충분. **cwd / Windows·POSIX / 필수 여부 / 성공 기준 / 증적 경로 / Not Run 기준**까지 모두 있어야 Gate 4에서 에이전트별 해석 차이를 제거할 수 있다.
- **`design_sequence`** (Gate 2): `docs/core/GATE2_DESIGN_SEQUENCE.md` §2를 따른다. 한 Run이 여러 단계를 다루면 모두 명시.
- **`ui_implementation_contract_policy`**: 화면 퍼블리싱 산출물 또는 외부 시안이 있는 화면 작업에서 사용. Gate 2에서 시안을 참고자료 vs 구현 계약으로 분류하고, 구현 계약이면 필수 유지/변경 허용/금지/비교 방식 작성. Gate 3에서 UI 테스트 기대결과 반영. Impl 체크리스트로 확인. Gate 4에서 기준 UIREF와 구현 screenshot 차이를 `Pass`, `FIND`, `CR`로 판정.

## 6. 입력 검증 체크리스트

Run 시작 전 Orchestrator는 다음을 확인한다.

| 체크 | 기준 |
| --- | --- |
| 관련 ID 존재 | 추적표 또는 산출물에 관련 ID가 존재한다 |
| 먼저 읽을 문서 존재 | `source_documents.read_first` 파일이 존재한다 |
| 작업 대상 문서 존재 | `source_documents.working_documents`가 비어 있지 않다 |
| 수정 범위 명확 | `scope.writable`이 비어 있지 않다 |
| 제외 경로 포함 | `docs/ref-docs/`가 제외되어 있다 |
| 검증 명령 완전성 | 각 명령에 cwd/성공 기준/증적 경로/Not Run 기준이 있다 |
| Gate 일치 | `session.json.current_gate`와 `gate` 필드가 일치한다 |
| Gate 정지 정책 | `gate_exit_policy.stop_required=true`이고 승인 질문 형식이 명시되어 있다 |
| UI 정책 (화면 시) | `ui_evidence_policy`와 (필요 시) `ui_implementation_contract_policy`가 채워져 있다 |
