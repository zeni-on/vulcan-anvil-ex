# Codex/GPT Run Output Contract

> 상태: 초안 v0.1
> 목적: Codex/GPT 계열 에이전트가 작업을 마친 뒤 남겨야 하는 표준 결과보고서 형식을 정의한다.

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
| `adapter` | 예 | Adapter 이름 |
| `status` | 예 | `Completed`, `Blocked`, `Failed`, `CompletedWithIssues` 등 |
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
adapter: codex-gpt
status: Completed
summary:
  ko: "PGM-005 게시글 작성 기능을 구현하고 관련 단위/통합 테스트를 통과시켰다."
  changed_behavior:
    - "인증 사용자는 게시글을 작성할 수 있다."
    - "비로그인 사용자의 작성 요청은 차단된다."

changed_files:
  - path: docs/examples/board-with-login/sample-app/app/api/posts.py
    change_type: modified
    related_ids: [PGM-005, REQ-005, SEC-002]
  - path: docs/examples/board-with-login/sample-app/tests/unit/test_post_service.py
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
  - type: test
    command: "python -m pytest tests -p no:cacheprovider"
    result: passed
    summary: "20 passed"
  - type: lint
    command: "python -m ruff check ."
    result: passed
    summary: "All checks passed"

evidence:
  documents:
    - docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md
  files: []
  commit: null

traceability_updates:
  - document: docs/examples/board-with-login/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
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
- 구현은 완료했지만 데이터 표준 검토가 별도 Run으로 남음

### Blocked

사용자 질문이나 승인 없이는 진행할 수 없을 때 사용한다.

```yaml
status: Blocked
blocked_reason: "scope.writable 밖의 파일 수정이 필요함"
questions:
  - "DOC-DEV-G2-001 개발표준 문서를 이번 Run 범위에 포함해도 되는가?"
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

## 5. 검증 결과 작성 규칙

검증을 실행하지 못했으면 `not_run`으로 기록한다.

```yaml
verification_results:
  - type: ui_capture
    command: "browser capture"
    result: not_run
    reason: "브라우저 도구를 사용할 수 없음"
```

실패한 검증을 성공처럼 쓰지 않는다.

권장 `result` 값:

| 값 | 의미 |
| --- | --- |
| `passed` | 검증 통과 |
| `failed` | 검증 실패 |
| `not_run` | 실행하지 못함 |
| `partial` | 일부만 실행 |

## 6. 증적 작성 규칙

증적은 사람이 열어볼 수 있는 경로를 남긴다.

좋은 예:

```yaml
evidence:
  documents:
    - docs/examples/board-with-login/DOC-QA-G4-003_UI-Test-Result_v0.1.md
  files:
    - docs/examples/board-with-login/evidence/ui/SCR-003_posts/desktop.png
```

나쁜 예:

```yaml
evidence:
  files:
    - "캡처함"
```

## 7. 추적성 갱신 규칙

다음 중 하나라도 변경되면 `traceability_updates`를 작성한다.

- 요구사항추적표 상태 변경
- 테스트 결과서 갱신
- 화면 캡처 증적 추가
- 보안항목 검증 결과 변경
- 미해결 이슈 Open/Closed 변경

## 8. 사람에게 보여줄 요약

YAML 결과 뒤에는 짧은 한국어 요약을 붙일 수 있다.

```text
요약:
PGM-005 게시글 작성 기능 구현과 테스트를 완료했습니다.
관련 테스트는 모두 통과했고, DOC-QA-G4-002에 결과를 반영했습니다.
남은 이슈는 없습니다.
```

요약은 YAML과 모순되면 안 된다.
