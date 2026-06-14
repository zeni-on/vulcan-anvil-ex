# Orchestrator CLI Guide

> 목적: Orchestrator가 매번 `python vulcan.py --help`를 탐색하지 않고, 적은 명령 표면으로 Vulcan-Anvil Ex를 운영하기 위한 Core CLI 가이드다.

이 문서는 Codex 전용 prompt가 아니다. Codex, Claude, Gemini, Antigravity 같은 adapter는 이 Core 가이드를 각 런타임 방식에 맞게 참조할 수 있다.

## 1. 기본 원칙

- 첫 명령은 가능하면 `python vulcan.py status`다.
- Gate 전환 전에는 `python vulcan.py status --check`로 전환 가능성, Run 상태, 추적성, branch 상태를 한 번에 확인한다.
- `prepare-transition`은 `status --check`가 호출하는 상세 전환 진단의 원자 명령이다. 사람이 원인 분석, 호환성 확인, 레거시 스크립트 연동을 위해 직접 실행할 수 있지만 기본 진입점은 아니다.
- `check-trace`는 추적성만 상세 디버깅하거나 trace-only 회귀 검증이 필요할 때 직접 실행한다. Gate 전환 전마다 `status --check` 뒤에 기계적으로 이어서 실행하지 않는다.
- 상세 원자 명령은 남겨둔다. 다만 Orchestrator prompt와 skill은 먼저 `status` 표면을 사용하고, 필요한 경우에만 원자 명령으로 내려간다.

## 2. 권장 명령 표면

Orchestrator가 우선 기억해야 할 명령 표면은 다음이다.

| 표면 | 용도 |
| --- | --- |
| `status` | 현재 Gate/profile/branch/Run/Wave/다음 행동 확인 |
| `profile-gap` | 현재 산출물을 목표 profile 기준으로 볼 때 부족한 문서와 내용 보완 항목 진단 |
| `metrics` | git/Run/증적 기반 진행 시간, 파일 수, 라인 수, 위임 기록 요약 |
| `gate-start`, `session`, `sync-session` | Gate 라이프사이클 갱신 |
| `orchestrator-plan`, `run-new`, `run-check`, `run-preflight` | Run 생성과 검증 |
| `branch-start`, `wave-start`, `wave-complete`, `run-integrate` | 구현/QA 통합 브랜치와 Build Wave 운영 |
| `release-pr`, `upgrade`, `version` | 릴리즈, 프레임워크 최신화, 버전 확인 |

원자 명령인 `prepare-transition`, `check-trace`, `check-contract`, `branch-status`는 상태 요약에서 더 좁은 원인 분석이 필요할 때 사용한다.

## 3. 상태 확인

| 목적 | 명령 |
| --- | --- |
| 현재 상태 요약 | `python vulcan.py status` |
| Gate 전환 진단 포함 | `python vulcan.py status --check` |
| JSON 출력 | `python vulcan.py status --json` |
| 추적성 상세 진단 포함 | `python vulcan.py status --trace-detail` |
| 브랜치만 상세 확인 | `python vulcan.py branch-status` |
| Profile 전환 gap 확인 | `python vulcan.py profile-gap --to product` 또는 `python vulcan.py profile-gap --to audit` |
| 회고/성능 통계 | `python vulcan.py metrics` 또는 `python vulcan.py metrics --json` |

`status --check`가 실패하면 바로 다음 Gate로 넘어가지 않는다. 실패 위치, 영향 ID, 해결 후보를 정리하고 필요할 때만 `prepare-transition` 또는 `check-trace`를 별도 실행한다.

`status`는 선택된 profile의 gap 요약을 함께 보여준다.
Product profile에서는 `docs/product/` 6종 문서 존재 여부와 현재 Gate의 핵심 `TBD` 항목 수를 먼저 확인한다.
상세 목록이 필요하면 `profile-gap --to product` 또는 `profile-gap --to audit`을 실행한다.

대시보드에서 문서에 남긴 코멘트는 원본 Markdown이 아니라 `.vulcan/comments/comments.jsonl`에 저장된다. `status`는 이 파일을 읽어 `dashboard_comments` 섹션에 Open 코멘트를 요약한다. Orchestrator는 Gate 판단, Run 보완, QA/FIND/CR/ISSUE 후보 정리 전에 이 섹션을 먼저 확인한다. 코멘트 상태는 단순히 `open` 또는 `closed`만 사용하며, 에이전트가 코멘트를 반영하거나 답변했으면 `closed`로 닫는다.

## 4. Gate 라이프사이클

| 목적 | 명령 |
| --- | --- |
| Gate 시작 | `python vulcan.py gate-start <gate>` |
| Gate 완료 기록 | `python vulcan.py session --gate <gate> --status done` |
| 상태 재계산/동기화 | `python vulcan.py sync-session` |

`gate-start`는 해당 Gate의 기본 Orchestrator Plan Run 초안을 자동 생성할 수 있다. 이미 Draft 또는 InProgress Run이 있으면 중복 생성하지 않는다.
PoC와 Product profile에서는 Gate별 Orchestrator Plan Run 자동 생성을 생략한다.
이 두 profile은 각각 `docs/poc/`, `docs/product/` 원장과 `status --check`를 우선 사용하고, 위임/재현/검수 기록이 필요할 때만 Run을 만든다.

Gate 완료는 사용자 승인 또는 명시적인 진행 지시가 있을 때만 수행한다.

Product profile은 Gate별 폴더를 늘리기보다 `docs/product/` 문서 세트의 `gate_scope`와 본문 섹션을 갱신한다.
Audit profile처럼 모든 `docs/artifacts/` 산출물을 처음부터 생성하지 않는다.

## 5. Run 생성과 검증

| 목적 | 명령 |
| --- | --- |
| Orchestrator Plan 생성 | `python vulcan.py orchestrator-plan --goal "<goal>" --gate <gate>` |
| 새 Run 생성 | `python vulcan.py run-new --skill <skill> --title "<title>" --related-ids "<ids>"` |
| trace seed 기반 Run 생성 | `python vulcan.py run-new --skill <skill> --title "<title>" --trace-seed <ID>` |
| worker handoff 전 사전검사 | `python vulcan.py run-preflight <run-file>` |
| Run 완료/형식 검사 | `python vulcan.py run-check <run-file>` |

native subagent, thread, native branch agent에게 넘기기 전에는 Orchestrator가 `run-preflight`를 직접 실행한다. `run-exec`와 `agent-run --mode work`는 preflight 자동 실행 경로가 있지만, native 위임은 자동 차단되지 않는다.

## 6. 구현과 Build Wave

| 목적 | 명령 |
| --- | --- |
| impl 통합 브랜치 시작 | `python vulcan.py branch-start impl` |
| Build Wave 시작 | `python vulcan.py wave-start <BW-ID> --trace-seed <seed-id>` |
| Build Wave 완료 | `python vulcan.py wave-complete <BW-ID> --status Verified` |
| worker 결과 통합 검토 | `python vulcan.py run-integrate <run-file>` |

구현은 기본적으로 통합 브랜치에서 수행한다. Orchestrator는 기능 구현의 주 작성자가 아니라 worker 결과를 통합하고 검증하는 역할이다.

`BW-000 implementation-scaffold`는 skeleton/build smoke만 검증한다. 업무 요구사항, 테스트, UI 상태를 `Implemented`, `Verified`, `Pass`로 확정하지 않는다.

## 7. QA와 릴리즈

Gate 4 QA는 한 번에 모두 수행하지 않고 다음 흐름으로 나눈다.

| 단계 | 목적 |
| --- | --- |
| `QA-000` | 환경 준비와 smoke |
| `QA-001` | 명령 기반 검증 |
| `QA-002` | UI/E2E 증적 |
| `QA-003` | 결과 정리와 판정 후보 |

결함 수정은 승인된 설계 범위 안에서만 `qa-fix-loop` Run으로 진행한다. 새 API, 새 메소드, 요구사항/설계 변경이 필요하면 `CR` 후보로 승격한다.

릴리즈 준비는 `python vulcan.py release-pr --dry-run`으로 먼저 확인한다.

## 8. 직접 실행보다 상태 표면을 우선하는 이유

Orchestrator가 원자 명령을 모두 기억하고 매번 순서대로 조합하면 안전하지만 느리고 누락이 생긴다. `status`는 다음을 줄이기 위한 얇은 상위 표면이다.

- 현재 Gate와 branch 확인 누락
- `sync-session` 누락으로 인한 dashboard 통계 불일치
- `prepare-transition`과 `check-trace`의 기계적 중복 실행
- worker Run preflight 누락
- 다음 행동 판단을 위해 `--help`를 반복 조회하는 비용

따라서 adapter prompt, repo-local skill, 사용자 안내 문서에서는 `status`를 기본 진입점으로 두고, 상세 분석이 필요할 때 원자 명령으로 내려간다.
