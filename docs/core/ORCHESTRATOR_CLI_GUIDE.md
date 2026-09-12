# Orchestrator CLI Guide

> 목적: Orchestrator가 매번 `python vulcan.py --help`를 탐색하지 않고, 적은 명령 표면으로 Vulcan-Anvil Ex를 운영하기 위한 Core CLI 가이드다.

이 문서는 Codex 전용 prompt가 아니다. Codex, Claude, Gemini, Antigravity 같은 adapter는 이 Core 가이드를 각 런타임 방식에 맞게 참조할 수 있다.

## 1. 기본 원칙

- 첫 명령은 가능하면 `python vulcan.py status`다.
- Gate 전환 전에는 `python vulcan.py status --check`로 전환 가능성, Run 상태, 추적성, branch 상태를 한 번에 확인한다.
- 로컬 실행 환경이 의심되면 `python vulcan.py doctor`를 먼저 실행한다. `doctor`는 Gate 상태가 아니라 Git/Node/npm/Playwright/runner/cache/Dashboard 환경을 확인한다.
- `prepare-transition`은 `status --check`가 호출하는 상세 전환 진단의 원자 명령이다. 사람이 원인 분석, 호환성 확인, 레거시 스크립트 연동을 위해 직접 실행할 수 있지만 기본 진입점은 아니다.
- `check-trace`는 추적성만 상세 디버깅하거나 trace-only 회귀 검증이 필요할 때 직접 실행한다. Gate 전환 전마다 `status --check` 뒤에 기계적으로 이어서 실행하지 않는다.
- 상세 원자 명령은 남겨둔다. 다만 Orchestrator prompt와 skill은 먼저 `status` 표면을 사용하고, 필요한 경우에만 원자 명령으로 내려간다.

## 2. 권장 명령 표면

Orchestrator가 우선 기억해야 할 명령 표면은 다음이다.

| 표면 | 용도 |
| --- | --- |
| `status` | 현재 Gate/profile/branch/Run/Wave/다음 행동 확인 |
| `doctor` | 로컬 Git/Node/npm/Playwright/runner/cache/Dashboard 환경 점검 |
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
| JSON + Gate 전환 진단 | `python vulcan.py status --json --check` |
| 추적성 상세 진단 포함 | `python vulcan.py status --trace-detail` |
| 브랜치만 상세 확인 | `python vulcan.py branch-status` |
| Profile 전환 gap 확인 | `python vulcan.py profile-gap --to product` 또는 `python vulcan.py profile-gap --to audit` |
| 회고/성능 통계 | `python vulcan.py metrics` 또는 `python vulcan.py metrics --json` |

## 3.1 로컬 환경 점검

| 목적 | 명령 |
| --- | --- |
| 환경 점검 | `python vulcan.py doctor` |
| 다른 프로젝트 점검 | `python vulcan.py doctor --project-dir <project-root>` |
| JSON 출력 | `python vulcan.py doctor --json` |

`doctor`는 `status`와 다르다. `status`는 프로젝트 진행 상태를 보고, `doctor`는 실행 환경을 본다. QA-000, Playwright, npm install, runner 실행, Dashboard 확인에서 환경 차단이 의심될 때 먼저 실행한다. `doctor`는 의존성을 설치하거나 브라우저를 다운로드하지 않는다.

권장 실행 시점:

| 시점 | 이유 | 후속 조치 |
| --- | --- | --- |
| `init`/`upgrade` 직후 새 프로젝트를 처음 맡을 때 | Python/Node/npm/Git/runner/Dashboard 기본 환경을 빨리 확인 | `fail`이면 환경 준비를 먼저 해결하고, `warn`은 Run/QA-000 입력으로 남긴다. |
| 첫 worker/subagent/thread 또는 외부 runner 실행 전 환경이 불확실할 때 | worker 실패를 제품 결함으로 오해하지 않기 위함 | runner 미감지, npm cache, Playwright cache 같은 항목을 미리 분리한다. |
| Gate 4 `QA-000` 전 또는 UI/E2E 증적 수집 전 | Playwright package/browser cache, 포트, DB, frontend/backend 실행 가능성을 빠르게 확인 | 차단 항목은 `environment_blocked` 또는 `ISSUE` 후보로 기록하고 QA-001/QA-002 강행 여부를 묻는다. |
| `npm install`, `npm run build`, `npx playwright test`, runner 실행이 실패했을 때 | 로컬 환경 문제와 제품 결함을 분리 | 같은 제품 동작 실패가 재현되기 전까지 `FIND`로 확정하지 않는다. |
| Dashboard가 뜨지 않거나 포트가 애매할 때 | Dashboard package/port 상태를 확인 | Dashboard 문제는 산출물 품질 문제가 아니라 운영 환경 문제로 분리한다. |

해석 규칙:

- `pass`: 해당 환경 항목은 현재 확인 기준에서 사용 가능하다.
- `warn`: 지금 당장 차단은 아닐 수 있지만 Run/QA-000/ISSUE 후보에 남긴다.
- `fail`: 해당 작업은 환경 준비 없이는 신뢰 있게 실행하기 어렵다. 제품 결함이 아니라 환경 차단으로 먼저 분류한다.
- `info`: 판정 근거로 쓰기보다 실행 환경 설명에 사용한다.

`doctor` 결과만으로 테스트를 `Pass` 또는 `Fail`로 기록하지 않는다. 실제 테스트/빌드/QA 판정은 해당 명령의 실행 결과와 증적으로 남긴다. 자동화나 대시보드가 필요하면 `python vulcan.py doctor --json`을 사용한다.

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

### 4.1 개발용 Product 반복 프로세스

`process_model: product-iterative-v1`을 사용하는 별도 실험 파일럿에서는 `status --check`와 `session --process-request`를 사용한다. 기존 Gate 명령을 새 구간 이름으로 호출하지 않는다. 상태 요청은 기본 미리보기이고 `--apply`일 때만 범위/권한/증적과 상태 revision을 검사해 저장한다. 상세 기계 계약과 제한은 프레임워크 저장소의 [Product Process Contracts](https://github.com/zeni-on/vulcan-anvil-ex/blob/main/docs/reference/PRODUCT-PROCESS-CONTRACTS.md#43-상태-저장-cli-단계-2b)를 따른다.

일반 `init`/`upgrade`는 이 모델을 활성화하지 않는다. 기존 Product/Audit/PoC 세션에 표식을 수동 추가하거나 이 명령으로 이행하지 않는다. 실험 모델도 Run/자동 Git commit/릴리즈를 추가로 강제하지 않으며, 기존 프로젝트에는 위의 Gate 라이프사이클이 그대로 적용된다.

| 실험 모델의 운영 작업 | 연결된 경로와 경계 |
| --- | --- |
| 현재 위치/범위/작업공간 | `status`, `branch-status`. `planning`/`impl`/`acceptance`를 그대로 읽으며 과거 Gate 키로 바꾸지 않는다. |
| 구현 통합 브랜치 준비 | `branch-start impl` 또는 `branch-start impl --dry-run`으로 미리보고, `--apply`로 적용한다. `--json`으로 결과를 읽을 수 있다. 허가된 impl 범위와 현재 계약을 확인하며 세션·승인·commit/push는 만들지 않는다. |
| QA 전달/인수 시험 | acceptance에서 `execute --dry-run --json`으로 Run 없는 전달 후보를 읽는다. 환경이 불확실하면 `doctor`로 확인하고 필요한 명시 명령만 `execute --verify`로 실행한다. 합의한 통합 작업공간을 사용하고 QA worktree를 새로 만들지 않는다. |
| 릴리즈 후보 확인 | `release-pr --dry-run`은 현재 범위 인수/증적/브랜치를 재확인하며 미처리 의무를 표시한다. 파일·PR·push를 만들지 않으며 후보가 나와도 발행 권한은 없다. |
| 화면 확인 | 지원 Dashboard는 저장된 3구간과 이번 작업 범위를 읽기 전용으로 표시한다. `completed`는 이번 범위 인수이며 제품 전체 완료나 배포 완료가 아니다. |

실험 모델의 브랜치 준비는 설정된 main에서 통합 브랜치를 새로 만들거나, 현재 HEAD와 커밋된 파일 내용이 같은 기존 통합 브랜치로 전환하는 범위다. `session.json`만 미커밋이면 그대로 가져가며, 다른 변경이 섞이면 먼저 정리한다. 이미 통합 브랜치면 그대로 둔다. 기존 통합 브랜치 내용이 다르면 자동 전환/세션 덮어쓰기 없이 차단하므로 영향 검토 후 별도 Git 작업으로 처리한다. 단일 브랜치 정책에서는 이 준비 명령이 필요하지 않다.

`--apply`는 현재 조건을 다시 검사하고 기존 Product 쓰기 잠금을 사용한다. Git 실패·timeout 또는 동시 변경으로 결과가 불명확하면 `branch-status`와 세션을 확인하고 재시도한다. 자동 stash/reset/rollback은 하지 않고 checkout hook도 실행하지 않는다. 이 명령을 세션 상태 변경이나 제품 구현/인수/발행 승인으로 사용하지 않는다.

기존 Gate/QA Run 자동화와 실제 `release-pr` 발행은 아직 지원하지 않는다. `session --process-request`로 상태를 저장해도 브랜치는 자동 전환되지 않는다. 표식이 없는 기존 모델의 `branch-start impl` 동작은 유지하며 새 `--apply`/`--dry-run`/`--json` 옵션은 실험 모델 전용이다.

native QA는 다음 순서로 연결한다. 새 문서를 추가로 채우라는 뜻이 아니라 현재 작업 요약과 기존 상태 요청을 재사용하는 경로다.

1. acceptance에서 `python vulcan.py execute --dry-run --json`을 실행한다. `--run-id` 없이 현재 scope, 계약/시험 참조, 통합 작업공간, 환경 명세와 빈 `return_request`를 받는다. `--runner subagent`, `thread`, `agy-branch-agent`는 전달 방식의 표시이며 실제 호출이나 격리 보장이 아니다.
2. 총괄이 기존 작업 요약에 담당자, 정확한 argv/cwd, 새 JSON/log/report 경로와 필요한 런타임 출력 경로를 붙여 전달한다. 문서에서 명령을 자동 추출·실행하지 않는다. 담당자는 검증 전용 위임으로 코드나 상태를 수정하지 않는다. `verify_only`는 역할 계약이며 CLI가 임의 테스트 프로세스를 OS sandbox로 격리한다는 뜻은 아니다.
3. 담당자는 명시 명령을 실행하고 ID별 실제 결과, 명령 JSON과 원본 로그, 실패 원인/미실행 항목을 반환한다. `execute --verify`는 acceptance의 현재 계약·시험 계획·환경 명세·작업공간을 실행 전에 재확인한다. 환경 명세가 정상이어도 실제 서비스/브라우저가 준비됐다는 뜻은 아니다.
4. 총괄이 실제 명령 종료·로그·현재 소스/환경 변경을 확인하고 `return_request.verification.results`를 채운다. ID마다 `id`, `status`, 실제 `command` argv, `evidence` 참조를 사용한다. 빈 results를 채우기 위해 Pass를 만들지 않으며 실패/누락/`environment_blocked`를 보존한다. delegate/검증 범위/결과는 기존 요약에 남긴다.
5. 결과 요청을 `session --process-request <request.json> --json`으로 미리본다. 실제 증적이 통과해도 accept 결정이 없으면 차단되며 `checks.verification_key`만 확인할 수 있다. 총괄은 실제 수용 권한을 확인한 뒤 별도 accept 결정을 연결하고 `--apply`한다. 오래된 session revision이면 현재 상태를 먼저 확인하며 자동으로 새 revision을 끼워 넣어 재적용하지 않는다.

실패한 결과 요청은 상태를 바꾸거나 실패 기록을 저장하지 않는다. 원본 증적과 기존 결과 요약에 실패를 남기고, 허가된 수정은 impl로 돌아가 처리한 뒤 새 증적을 수집한다. 서브에이전트의 완료 알림이나 exit 0은 테스트 건수/업무 결과/인수 승인을 인증하지 않는다. 이 경로는 새 Run/자동 dispatcher/릴리즈 권한을 만들지 않는다.

## 5. Run 생성과 검증

| 목적 | 명령 |
| --- | --- |
| Orchestrator Plan 생성 | `python vulcan.py orchestrator-plan --goal "<goal>" --gate <gate>` |
| 새 Run 생성 | `python vulcan.py run-new --skill <skill> --title "<title>" --related-ids "<ids>"` |
| trace seed 기반 Run 생성 | `python vulcan.py run-new --skill <skill> --title "<title>" --trace-seed <ID>` |
| Run 실행 계획 dry-run | `python vulcan.py execute --run-id <RUN-ID> --runner native --dry-run` |
| Run 실행 계획 JSON | `python vulcan.py execute --run-id <RUN-ID> --runner native --dry-run --json` |
| worker handoff 전 사전검사 | `python vulcan.py run-preflight <run-file>` |
| Run 완료/형식 검사 | `python vulcan.py run-check <run-file>` |

Run을 사용하는 native subagent/thread/branch agent에게 넘기기 전에는 `run-preflight` 또는 이를 포함한 `execute --dry-run` 통과를 확인한다. Product의 일반 작업은 기존 요구사항/이슈/작업 요약의 목표, 수정 범위, 계약, 검증 기준으로 진행할 수 있으며 Run 생성이 선행 조건이 아니다. 외부 `run-exec`/`agent-run --mode work`의 Run과 자동 preflight는 유지한다.

`execute --dry-run`은 실제 worker를 실행하지 않는다. Run 문서를 기준으로 `run-check`, `run-preflight`, 위임 sidecar 후보, `scope.writable`, 검증 명령, 외부 runner 연결 명령을 한 번에 요약한다. native subagent/thread/Agy branch agent에게 일을 넘기기 전에는 이 출력으로 누락된 handoff 조건을 먼저 확인한다.
이 호출에서 preflight가 통과했고 이후 Run/계약/범위/프로젝트 상태가 바뀌지 않았다면 동일 사전검사를 별도 명령으로 반복할 필요는 없다. 변경이 생기면 위임 전에 다시 검사한다.

자동화나 Dashboard 연동처럼 기계가 읽어야 하는 경우에는 `--json`을 붙인다. 이 JSON에는 `delegation_sidecar` 후보, `planned_flow`, `run_check`, `preflight`, `scope`, `verification.commands`가 포함된다. 이 출력도 dry-run 계획일 뿐이며 worker 실행, Gate 승인, Wave 완료를 수행하지 않는다.

### 5.1 명시 검증 명령 기록

이미 승인된 검증 명령의 실행 기록을 남기려면 `execute --verify`를 사용한다. `execute --dry-run`의 worker 계획과는 별개이며 worker 호출, Run 자동 실행, Gate 전환을 하지 않는다.

```text
python vulcan.py execute --verify --evidence docs/product/evidence/REG-001-command.json -- python -m pytest tests -q
```

경로는 실제 프로젝트에 맞게 선택한다. `--source`는 선택적인 설명용 경로이며 소스 스냅샷이나 Git 식별자를 수집하지 않는다. `--cwd`와 `--project-dir`는 필요한 경우만 지정한다. 기존 Run에 연결하려면 `--run-id`를 추가한다. `--evidence`는 이미 존재하는 폴더 안의 새 JSON 경로이며 기존 파일을 덮어쓸 수 없다.

명령은 `--` 뒤의 명시 argv로 실행한다. shell 문자열이나 Run 본문에서 명령을 자동 추출하지 않는다. Windows에서는 `.cmd`/`.bat` 대신 실제 실행 파일/인터프리터를 사용한다. 명령 출력은 터미널로 전달되며 상세 테스트 로그/HTML은 기존 테스트 도구에서 별도로 남긴다. schema 2 JSON은 argv, cwd, 실행 시간과 exit code를 담는 실행 기록이지 로그를 대체하는 QA 결과서가 아니다.

별도 Git 증적이나 소스 신선도 검사는 하지 않는다. 과거 관측 JSON은 재작성하지 않고 읽을 수 있다. Orchestrator가 구현·환경 변경과 시험 범위를 확인해 관련 재시험을 판단하며, exit code 0만으로 QA 승인을 대신하지 않는다. 전체 기준은 [CURRENT_CONTEXT_AND_EVIDENCE.md](CURRENT_CONTEXT_AND_EVIDENCE.md)를 따른다.

## 6. 구현과 Build Wave

| 목적 | 명령 |
| --- | --- |
| impl 통합 브랜치 시작 | `python vulcan.py branch-start impl` |
| Build Wave 시작 | `python vulcan.py wave-start <BW-ID> --trace-seed <seed-id>` |
| Build Wave 완료 | `python vulcan.py wave-complete <BW-ID> --status Verified` |
| worker 결과 통합 검토 | `python vulcan.py run-integrate <run-file>` |

구현은 기본적으로 통합 브랜치에서 수행한다. Product의 실행자 선택은 `PRODUCT_PROFILE_BASELINE.md` 7절을 따른다. 일반 수정마다 새 worker/Run을 만들지 않는다. `status`는 Product에서 승인된 변경의 구현/검증을 안내하며 `wave-start`를 필수 다음 행동으로 추천하지 않는다. Wave를 선택하면 기존 시작/완료 명령을 사용하며 미완료 Wave를 자동 완료하지 않는다. Audit/PoC의 위임 방식은 유지한다.

Product profile에서 `wave-start --trace-seed SCN-001`을 사용하면 Product 원장에서 관련 `REQ/API/DATA/UI/REG`를 추천한다. 원장 전체 정독 대신 worker guide와 대상 계약 ID/섹션을 입력으로 사용한다. 생성된 Run의 수정 경로와 검증 명령 TBD는 실제 프로젝트 기준으로 확정한 뒤 preflight를 통과시킨다. 원장만으로 계약이 부족하면 `docs/templates/product/PRODUCT_*_TEMPLATE.md`의 경량 상세 문서를 `docs/artifacts/02-design/...`에 둔다. 추적표/최종 결과 정리는 Orchestrator가 맡으며, 증적 재사용과 재실행 조건은 `PRODUCT_PROFILE_BASELINE.md` 7절을 따른다.

`BW-000 implementation-scaffold`는 skeleton/build smoke만 검증한다. 업무 요구사항, 테스트, UI 상태를 `Implemented`, `Verified`, `Pass`로 확정하지 않는다.

### 6.1 누적 문서의 계약 구간 조회

```text
python vulcan.py trace-context --id API-001,PGM-001 --sections --emit json
python vulcan.py trace-context --id API-001 --sections --document docs/product/PRODUCT_CONTRACTS.md --max-chars 12000 --emit yaml
```

기존 그래프 조회는 `--sections` 없이 사용한다. 구간 조회는 `docs/product/`, `docs/artifacts/01-requirements/`, `02-design/`, `03-test/`의 Markdown을 기본 탐색한다. `--document`는 이 자동 탐색을 명시한 상대경로 목록으로 대체한다. 선택한 절에 실제로 연결된 공통 문서는 아래 범위에서 추가 조회하지만, 링크가 없는 필요한 계약은 함께 지정해야 한다.

결과의 경로/제목/줄 범위/문서 해시를 기준으로 필요한 원문을 읽는다. 현재/후보/이력 표식이 없는 절은 `unclassified`이고, 여러 현재 일치 구간은 단순 참조인지 실제 충돌인지 Orchestrator가 판단한다. 원본/참조의 의미 판정이나 Gate 내용 검사를 대신하지 않는다.

- 선택된 절의 명시적 Markdown 링크를 최대 2단계, 64개까지 따라 읽는다. 기본 탐색 범위 밖 문서는 `--document`로 직접 지정한 경우에만 연결 조회한다. 네트워크 요청, 프로젝트 밖 경로, symlink/junction 우회는 허용하지 않는다.
- `문서.md#앵커`는 대상 절/하위 절/상위 조건을, 앵커 없는 문서 링크는 해당 문서의 절들을 조회 후보로 삼는다. 공통 보안/오류 제목 기반 조회도 유지하되, 제목 키워드를 새 작성 의무로 만들지는 않는다.
- 추가로 읽는 링크 문서는 최대 16개, 최초 탐색을 포함한 전체 문서는 최대 256개다. 본문은 최대 12절/기본 12,000자이며 절을 중간에서 자르지 않는다. 많이 연결된 색인은 예산을 소모하므로 필요한 문서/앵커로 좁힌다.
- `references`와 각 절의 `source_links`에서 미수집 원인을 확인한다. `followed: true`는 대상 구간이 출력에 모두 포함됐다는 뜻일 뿐 승인/완전한 계약이라는 뜻이 아니다. 앵커 오류, 범위/깊이/출력 제한 등은 `incomplete`와 경고로 남긴다. 부족한 구간은 원문을 읽거나 문서를 좁혀 다시 조회한다.

의미상 연결되지 않은 조건이나 Markdown 파서가 지원하지 않는 링크까지 자동 발견한다고 가정하지 않는다. 생성된 Run의 `section_lookup`은 읽기 안내이지 계약 확정이나 원문 복사본이 아니다. Product 6종 원장과 Gate/통계/작성 경로를 새 분할 구조로 옮기는 작업은 별도다.

구간 모드의 `--emit yaml`은 추가 라이브러리 없이 읽을 수 있는 JSON 호환 YAML 1.2 형식으로 출력한다. `--max-chars`는 본문 문자 수 제한이며 출처/경고 metadata를 포함한 전체 JSON 바이트나 모델 토큰 수 제한이 아니다.

### 6.2 Product 분리 문서의 검사와 통계

새 명령은 추가하지 않는다. `status --check`/`check-trace`는 기존 Product 원장에서 명시적으로 연결된 소유 상세 문서를 함께 검사한다. 기존 원장/혼합/분리 형식 모두 원본 표의 SCN/REQ/계약/REG 연결을 유지해야 한다. 상세 파일을 만들기만 하고 원장에서 연결하지 않으면 현재 검사 원본으로 자동 채택하지 않는다.

`sync-session`의 Product 통계와 Product seed 추천도 같은 원본을 참조한다. 계획/결과 중복, SEC-REG를 REG로 잘못 세는 경우, 상세 REQ를 부모로 잘라 세는 경우를 방지한다. 누락·상충 여부는 `product.document_diagnostics`와 Gate 진단에서 확인한다. `trace-context`의 기존 그래프 모드나 Dashboard 문서 구조 전체를 새 체계로 바꾼 것은 아니다. 소유 범위/미수집 처리 기준은 [Current Context And Evidence 3.2](CURRENT_CONTEXT_AND_EVIDENCE.md#32-product-내용-검사추적통계-호환)를 따른다.

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
`product` profile의 release PR body는 audit 제출 산출물이 아니라
`docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md`,
`docs/product/PRODUCT_TRACEABILITY.md`,
`docs/product/REGRESSION_AND_RELEASE_REPORT.md`,
`docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md`를 중심으로 evidence를 표시한다.

## 8. 직접 실행보다 상태 표면을 우선하는 이유

Orchestrator가 원자 명령을 모두 기억하고 매번 순서대로 조합하면 안전하지만 느리고 누락이 생긴다. `status`는 다음을 줄이기 위한 얇은 상위 표면이다.

- 현재 Gate와 branch 확인 누락
- `sync-session` 누락으로 인한 dashboard 통계 불일치
- `prepare-transition`과 `check-trace`의 기계적 중복 실행
- worker Run preflight 누락
- 다음 행동 판단을 위해 `--help`를 반복 조회하는 비용

따라서 adapter prompt, repo-local skill, 사용자 안내 문서에서는 `status`를 기본 진입점으로 두고, 상세 분석이 필요할 때 원자 명령으로 내려간다.
