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

### 5.1 검증 대상 Git 기록

이미 승인된 검증 명령의 소스 기준을 남기려면 `execute --verify`를 사용한다. `execute --dry-run`의 worker 계획과는 별개이며 worker 호출, Run 자동 실행, Gate 전환을 하지 않는다.

```text
python vulcan.py execute --verify --source app --source tests --source requirements.txt --evidence docs/product/evidence/REG-001-source.json -- python -m pytest tests -q
```

경로는 실제 프로젝트에 맞게 선택한다. `--source`에는 코드/테스트/lockfile 등 실제 검증 입력을 반복 지정하고, `--cwd`와 `--project-dir`는 필요한 경우만 지정한다. 기존 Run에 연결하려면 `--run-id`를 추가한다. `--evidence`는 이미 존재하는 폴더 안의 새 JSON 경로이며, 소스 범위와 겹치거나 기존 파일을 덮어쓸 수 없다.

명령은 `--` 뒤의 명시 argv로 실행한다. shell 문자열이나 Run 본문에서 명령을 자동 추출하지 않는다. Windows에서는 `.cmd`/`.bat` 대신 실제 실행 파일/인터프리터를 사용한다. 명령 출력은 터미널로 전달되며 상세 테스트 로그/HTML은 기존 테스트 도구에서 별도로 남긴다. JSON은 로그를 대체하는 QA 결과서가 아니라 소스 식별 증적이다.

`tested_commit`은 지정 소스가 Git 기준과 일치하고 실행 전후 안정적으로 식별된 경우에만 채워진다. 미커밋/새 파일을 포함하면 실제 내용 fingerprint와 범위를 확인한다. Git clean이어도 필터/줄바꿈 변환으로 실제 바이트가 index와 다르면 커밋 대신 관측한 내용을 기준으로 남긴다. exit code 0만으로 `identity_complete`, `source_changed`, 환경/테스트 범위 또는 QA 승인을 생략하지 않는다. 수집은 관측 전후 비교이며 실행 중 잠깐 바뀌었다 복원된 모든 변경을 감시하는 장치는 아니다. 전체 기준은 [CURRENT_CONTEXT_AND_EVIDENCE.md](CURRENT_CONTEXT_AND_EVIDENCE.md)를 따른다.

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
