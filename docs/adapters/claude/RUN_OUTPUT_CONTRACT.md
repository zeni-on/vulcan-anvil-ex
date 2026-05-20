# Claude Run Output Contract

> 상태: v0.2.2
> 목적: Claude 에이전트가 작업을 마친 뒤 남겨야 하는 표준 완료보고서 형식을 정의한다.

## 1. 개념

Run Output Contract는 에이전트의 완료보고서다.

에이전트는 단순히 "완료했습니다"라고 말하지 않고, 다음 질문에 답해야 한다.

- 무엇을 변경했는가?
- 어떤 ID와 연결되는가?
- 어떤 검증을 실행했는가?
- 어떤 증적을 남겼는가?
- 남은 이슈는 무엇인가?
- 다음 Run은 무엇이 적절한가?

## 2. 필수 필드

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `run_id` | 예 | 입력과 동일한 Run ID |
| `adapter` | 예 | `claude` |
| `status` | 예 | `Completed`, `Blocked`, `Failed`, `CompletedWithIssues`, `AwaitingApproval` 등 |
| `gate_exit_summary` | Gate 종료 Run 시 예 | 산출물 요약 / 미해결 / 다음 Gate 제안 / 다음 Run 후보 |
| `approval_request` | Gate 종료 Run 시 예 | 사용자에게 묻는 승인 질문과 승인 기록 상태 |
| `summary` | 예 | 작업 요약 |
| `changed_files` | 예 | 변경 파일 목록 |
| `related_ids` | 예 | 변경과 연결된 ID |
| `verification_results` | 예 | 테스트/린트/캡처 실행 결과 |
| `evidence` | 예 | 결과서, 캡처, 로그, 커밋 등 |
| `traceability_updates` | 예 | 추적표 또는 산출물 갱신 내용 |
| `open_issues` | 예 | 남은 이슈. 없으면 빈 배열 |
| `findings` | 선택 | QA/리뷰 중 발견한 결함과 처리 결과 |
| `change_requests` | 선택 | 설계 또는 기준선 변경이 필요한 항목 |
| `next_run_suggestion` | 선택 | 다음 실행 단위 제안 |

## 3. 권장 YAML 형식

```yaml
run_id: RUN-001
adapter: claude
status: Completed
summary:
  ko: "PGM-005 게시글 작성 기능을 구현하고 관련 단위/통합 테스트를 통과시켰다."
  changed_behavior:
    - "인증 사용자는 게시글을 작성할 수 있다."
    - "비로그인 사용자의 작성 요청은 차단된다."

changed_files:
  - path: src/api/posts.py
    change_type: modified
    related_ids: [PGM-005, REQ-005, SEC-002]
  - path: tests/unit/test_post_service.py
    change_type: modified
    related_ids: [UT-007, UT-008]

related_ids:
  req: [REQ-005]
  ac: [AC-007, AC-008]
  func: [FUNC-005]
  scr: [SCR-005]
  pgm: [PGM-005]
  db: [DB-002]
  sec: [SEC-002, SEC-004]
  test: [UT-007, UT-008, IT-004]

verification_results:
  - id: UT-005
    type: test
    cwd: "repository root"
    command: "python -m pytest tests -p no:cacheprovider"
    os: posix
    exit_code: 0
    success_criteria: "exit code 0, 실패 0건"
    result: passed
    summary: "20 passed, 0 failed"
    log_path: ".pytest_cache/v/cache/lastfailed"
    evidence_path: "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md"
  - id: LINT-001
    type: lint
    cwd: "repository root"
    command: "python -m ruff check ."
    os: posix
    exit_code: 0
    success_criteria: "exit code 0, 오류 0건"
    result: passed
    summary: "All checks passed"
    evidence_path: "Run 본문"

evidence:
  documents:
    - docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
  files: []
  commit: null
  # 상태별 UI 증적 (SCR × 상태 단위)
  ui:
    - ui_id: UI-003-01
      scr: SCR-003
      state: 기본
      expected_path: "docs/artifacts/02-design/screen/ui-baseline/scr-003-default.html"
      actual_path: "docs/artifacts/04-review/evidence/ui/UI-003-01_default.png"
      result: passed
    - ui_id: UI-003-02
      scr: SCR-003
      state: 오류
      expected_path: "docs/artifacts/02-design/screen/images/scr-003-error.png"
      actual_path: "docs/artifacts/04-review/evidence/ui/UI-003-02_error.png"
      result: not_run
      reason: "오류 상태 재현 시나리오 미구현"
  # UI Implementation Contract 차이 판정 (화면 퍼블리싱 산출물/UIREF 있는 SCR)
  ui_contract_diffs:
    - scr: SCR-003
      contract_path: "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md#SCR-003-contract"
      ref_screenshot: "docs/artifacts/02-design/screen/ui-baseline/scr-003.html"
      impl_screenshot: "docs/artifacts/04-review/evidence/ui/UI-003-01_default.png"
      verdict: Pass    # Pass / FIND / CR
      notes: "필수 유지 요소(헤더, CTA, 폼 레이아웃) 모두 일치. 변경 허용 항목(색상) 디자인 토큰 적용."

# Gate 종료 Run (Gate N → Gate N+1 진입 직전)에서만 작성
gate_exit_summary:
  gate: G2
  artifacts_completed:
    - "DOC-ARCH-G2-001_SW-Architecture (Baseline)"
    - "DOC-CORE-G2-001~003 (Function/Program/Screen)"
    - "DOC-API-G2-001, DOC-DATA-G2-001~002, DOC-SEC-G2-001, DOC-DEV-G2-001"
  open_items:
    - "FIND-003 변경 허용 항목 텍스트 wording 검토 필요"
  next_gate_proposal: gate3
  next_run_candidates:
    - "G3 Test Cases 작성 (test-design)"

approval_request:
  pending: true
  question: "Gate 2 산출물 검토 후 Gate 3 (테스트 설계)로 진행해도 될까요?"
  approval_recorded: false   # 사용자 명시 승인 후에만 true
  user_approved_at: null
  approval_evidence: null    # 승인 시 대화 인용 또는 결정 메모 경로

traceability_updates:
  - document: docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    update: "REQ-005 관련 상태와 증적을 최신 테스트 결과로 갱신"

open_issues: []

findings:
  - finding_id: FIND-001
    status: fixed
    related_ids: [REQ-005, AC-008, PGM-005, SEC-002, UT-008]
    cr_required: false
    resolution: "기존 설계 범위 내 결함으로 판단해 G4 QA Fix Loop에서 수정"

change_requests: []

next_run_suggestion:
  run_type: Evidence
  claude_agent: evidence
  goal: "SCR-005 게시글 작성 화면의 UI-005 캡처 증적을 갱신한다."
  related_ids: [SCR-005, UI-005, REQ-005]
```

## 4. 상태별 출력 규칙

### Completed

완료 조건을 모두 만족했을 때 사용한다.

필수:
- 모든 변경 파일
- 모든 검증 결과
- 증적 위치
- 미해결 이슈 없음 또는 후속 이슈가 완료 조건에 영향 없음

### CompletedWithIssues

주요 목표는 달성했지만 후속 조치가 남았을 때 사용한다.

예:
- API 테스트는 통과했지만 모바일 UI 캡처가 남음
- 구현은 완료했지만 화면 증적 수집이 별도 Run으로 남음

### Blocked

사용자 질문이나 승인 없이는 진행할 수 없을 때 사용한다.

```yaml
status: Blocked
blocked_reason: "scope.writable 밖의 파일 수정이 필요함"
questions:
  - "개발표준 문서를 이번 Run 범위에 포함해도 되는가?"
```

### Failed

시도했지만 완료 조건을 만족하지 못했을 때 사용한다.

```yaml
status: Failed
failure:
  command: "python -m pytest tests"
  observed_error: "UT-008 failed with 401 mismatch"
  affected_ids: [UT-008, SEC-002]
  retry_possible: true
```

## 4.1 Gate 종료 / 승인 요청 규칙

Gate N의 마지막 Run(다음 Gate 진입 직전)은 다음 두 필드를 **반드시** 채운다.

- **`gate_exit_summary`**: 산출물 목록 / 미해결 항목 / 다음 Gate 제안 / 다음 Run 후보
- **`approval_request`**: 사용자에게 묻는 명시적 승인 질문 + 승인 기록 상태

승인 흐름:
1. Run 종료 시 `status: AwaitingApproval` + `approval_request.pending=true` + 질문 문장
2. 사용자가 명시 승인하면 다음 Run(또는 `session --status done` 처리 Run)에서 `approval_recorded=true`, `user_approved_at`, `approval_evidence` 채움
3. **명시 승인 없이는 `approval_recorded=true` 기록 금지** (대화상 승인 없는 상태에서 Run 또는 Release Approval 산출물에 "User Approved" 자동 기록 불가)

## 4.2 UI 증적 / Contract diff 작성 규칙

화면 작업 Run은 `evidence.ui`와 (UIREF/ui-baseline 있는 SCR이면) `evidence.ui_contract_diffs`를 **반드시** 채운다.

- **`evidence.ui[]`**: SCR×상태 단위(`UI-NNN-NN`). 기본/로딩/오류/성공/전환 상태별 1행. 각 행에 `expected_path`(UIREF/ui-baseline) + `actual_path`(실제 캡처) + `result`(passed/failed/not_run) + (실패/미실행 시) `reason`
- **`evidence.ui_contract_diffs[]`**: 화면 퍼블리싱 산출물/UIREF가 있는 SCR마다 1행. `verdict`는 `Pass` / `FIND` / `CR` 중 하나. 차이 무시 또는 묵시적 Pass 금지

## 5. 검증 결과 작성 규칙

각 검증 결과는 **id / type / cwd / command / os / exit_code / success_criteria / result / summary / log_path / evidence_path** 필드를 가진다. 명령 문자열만으로는 불충분 — cwd와 성공 기준, exit code, 로그/증적 경로까지 기록해야 Gate 4에서 에이전트별 해석 차이를 제거할 수 있다.

검증을 실행하지 못했으면 `not_run`으로 기록한다.

```yaml
verification_results:
  - id: UI-003-01
    type: ui_capture
    cwd: "repository root"
    command: "playwright screenshot --target SCR-003"
    os: posix
    result: not_run
    reason: "브라우저 MCP를 사용할 수 없음"
    followup: "evidence persona가 환경 복구 후 재실행"
```

실패한 검증을 성공처럼 쓰지 않는다. 누락 필드 + Pass 기록은 **Gate 4 검수에서 FIND로 처리**된다.

권장 `result` 값:

| 값 | 의미 |
| --- | --- |
| `passed` | 검증 통과 |
| `failed` | 검증 실패 |
| `not_run` | 실행하지 못함 (reason 필수) |
| `partial` | 일부만 실행 |

## 6. Claude 전용 증적 필드

Claude는 Bash tool로 직접 명령을 실행하므로 실제 출력을 포함한다.

```yaml
evidence:
  documents:
    - docs/artifacts/04-review/DOC-QA-G4-003_UI-Test-Result_v0.1.md
  files:
    - docs/artifacts/04-review/screenshots/SCR-003-posts-desktop-initial.png
  bash_outputs:
    - command: "python -m pytest tests"
      output: "20 passed in 1.23s"
```

## 7. 사람에게 보여줄 요약

YAML 결과 뒤에는 짧은 한국어 요약을 붙인다.

```text
요약:
PGM-005 게시글 작성 기능 구현과 테스트를 완료했습니다.
관련 테스트는 모두 통과했고, DOC-QA-G4-002에 결과를 반영했습니다.
남은 이슈는 없습니다.
```

요약은 YAML과 모순되면 안 된다.
