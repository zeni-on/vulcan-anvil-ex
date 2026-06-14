# Getting Started

Vulcan-Anvil Ex는 사용자가 명령어를 하나씩 넣어 산출물을 수동 생성하는 도구가 아닙니다. 사용자는 만들고 싶은 것과 중요한 제약을 말하고, Orchestrator가 Gate에 맞게 요구사항, 설계, 구현, 테스트, 증적을 조율합니다.

## 1. 새 프로젝트 초기화

```powershell
python vulcan.py init ../my-project "My Project"
python vulcan.py init ../my-product "My Product" --profile solution
python vulcan.py init ../my-poc "My PoC" --profile poc
```

초기화하면 Core 문서, 템플릿, adapter 문서, 공개 표준 참고자료, `AGENTS.md`, `session.json`, 프로젝트용 `vulcan.py`가 생성됩니다.

`--profile`을 지정하지 않으면 기본값은 `audit`입니다.
`solution`, `poc`는 초기화 시 선택할 수 있으며, 선택한 Profile과 Overlay 기준은 `session.json`과 `vulcan.config.json`에 기록됩니다.
Profile은 결과물의 품질 등급이 아니라 문서 깊이, 증적 밀도, 독립검수 빈도, 변경관리 형식의 차이입니다.
현재 프로젝트의 Gate/Profile/Branch/다음 행동은 다음 명령으로 먼저 확인합니다.

```powershell
python vulcan.py status
```

Profile 규칙을 더 자세히 확인해야 할 때만 `python vulcan.py profile-status`를 사용합니다.

Profile을 고르기 어렵다면 먼저 다음 기준으로 선택합니다. 자세한 설명은 [Which Profile Should I Use?](WHICH_PROFILE_SHOULD_I_USE.md)를 참고합니다.

| 원하는 것 | 선택 |
| --- | --- |
| 빠른 기술/아이디어 검증 | `--profile poc` |
| 제품/업무 앱 개발과 반복 릴리즈 | `--profile solution` |
| 감리, 고객 검수, 인수인계, 강한 QA 증적 | 기본값 `audit` |

`--remote`는 선택 옵션입니다. 넣지 않으면 로컬 폴더에 프로젝트를 만들고 Git 저장소와 초기 커밋까지 생성합니다.

```powershell
python vulcan.py init ../my-local-project "My Local Project"
```

GitHub 같은 원격 저장소와 함께 시작할 때는 `--remote`를 지정합니다.

```powershell
python vulcan.py init ../my-project "My Project" --remote https://github.com/<owner>/my-project.git
```

`--remote`를 사용하면 생성된 프로젝트에 `origin` remote를 등록하고 초기 커밋을 원격 저장소로 push합니다. 원격 저장소가 없거나 권한 문제가 있으면 로컬 초기 커밋까지만 완료하고 경고를 출력합니다.

원격 저장소를 연결하면 다음 상황에서 유용합니다.

- Dashboard에 GitHub 저장소 URL로 프로젝트를 등록해 여러 사람이 같은 상태를 볼 수 있습니다.
- 다른 PC나 다른 에이전트 세션이 clone해서 같은 문서, Run, 코드 기준으로 이어서 작업할 수 있습니다.
- 커밋 이력과 PR을 기준으로 Gate 진행, QA 검수, 변경요청 반영 과정을 추적하기 쉽습니다.

원격 저장소 등록과 push가 반드시 성공해야 한다면 `--require-remote`를 함께 사용합니다.

```powershell
python vulcan.py init ../my-project "My Project" --remote https://github.com/<owner>/my-project.git --require-remote
```

## 2. 프로젝트에서 작업 시작

```powershell
cd ../my-project
```

이후 선택한 에이전트 환경에서 프로젝트를 엽니다.

- Codex CLI: 프로젝트 폴더에서 Codex를 실행합니다.
- Codex Desktop: 프로젝트 폴더를 열고 대화를 시작합니다.
- Claude: Claude 런타임에서 프로젝트 폴더와 adapter 문서를 기준으로 작업합니다.
- Antigravity/Agy: Antigravity/Agy에서 프로젝트 폴더를 열고 Gemini adapter 문서와 `GEMINI.md`를 기준으로 작업합니다.

처음에는 가볍게 인사하거나 목표를 말하면 됩니다.

`init` 직후 새 대화나 새 세션을 시작했다면, 먼저 메인 에이전트가 Orchestrator 역할과 프로젝트 문서를 확인하도록 요청하는 것이 좋습니다.

```text
안녕.. 너는 메인 오케스트레이터로써 이 프로젝트를 잘 이끌어가야해..
그에 대한 내용이 여기에 있으니 한번 전체적인 내용을 확인해줘.
```

이 요청은 구현을 바로 시작하라는 뜻이 아닙니다. 메인 에이전트가 `AGENTS.md`, `session.json`, `docs/core/`, adapter 문서, 현재 Gate 상태를 먼저 확인하고, 이후 Gate별 진행을 안정적으로 조율하도록 만드는 초기 정렬 단계입니다.

PoC Profile로 시작했다면 다음처럼 목표와 운영 강도를 함께 알려주는 것이 좋습니다.

```text
이 프로젝트는 PoC profile이야.
감리 제출 수준 문서가 아니라 목표, 가설, 성공 기준, smoke/demo 검증 결과를 중심으로 진행해줘.
실패하거나 미실행한 항목은 Pass로 기록하지 말고 PoC 결과나 다음 판단 항목으로 남겨줘.
짧은 실험은 subagent와 결과 요약 중심으로 진행하고, 외부 worker나 긴 위임이 필요한 경우에만 compact Run을 만들어줘.
TBD가 필요한 항목은 사유와 후속 판단 시점을 같이 남겨줘.
```

Solution Profile로 시작했다면 다음처럼 알려주는 것이 좋습니다.

```text
이 프로젝트는 Solution profile이야.
일반 제품/업무 앱 수준으로 요구사항, 주요 설계, API/DB/UI 계약, 릴리즈 회귀 기준을 남겨줘.
감리 제출 수준의 과도한 증적보다는 제품 품질과 유지보수성을 우선해줘.
```

Audit Profile은 기본값입니다. 감리, 고객 검수, 인수인계가 필요하다면 다음처럼 명확히 말합니다.

```text
이 프로젝트는 Audit profile이야.
요구사항, 설계, 테스트, QA 증적, 변경관리, 릴리즈 승인까지 추적 가능하게 진행해줘.
Gate 전환 전에는 status --check 결과와 남은 이슈를 보고해줘.
```

PoC Run은 기본 필수가 아닙니다. 외부 CLI worker, 독립 검수, 긴 위임, 재현 가능한 실험 기록이 필요하면 다음처럼 compact Run 초안을 생성할 수 있습니다.
짧은 subagent/thread 실험은 별도 Run 없이 결과 요약에 위임 대상, 작업 범위, 변경 파일, 결과 요약, Orchestrator 재검증 명령만 남길 수 있습니다.

```powershell
python vulcan.py run-new --gate phase0 --skill orchestrator-plan --title "PoC 가설과 성공 기준 정리" --related-ids POC-001
```

그 다음 만들고 싶은 기능이나 제약을 말합니다.

```text
로그인과 게시글 작성 기능이 있는 게시판 샘플을 만들고 싶어.
```

Orchestrator는 `AGENTS.md`, `docs/core/`, adapter 규칙을 읽고 필요한 질문을 한 뒤 현재 Gate에서 허용된 범위부터 진행합니다. Phase 0 또는 Gate 1에서는 바로 구현하지 않고 범위, 요구사항, 질문, 승인 지점을 먼저 정리합니다.

처음 실행이 끝났을 때 무엇이 남는지 감을 잡고 싶다면 [Examples And Benchmarks](EXAMPLES_AND_BENCHMARKS.md)를 먼저 읽어도 됩니다.

## 3. 기본 프로젝트 구조

```text
my-project/
├── README.md
├── AGENTS.md
├── .agents/
├── .codex/
├── .claude/
├── session.json
├── vulcan.py
├── ENVIRONMENT.md
├── GATE_GUIDE.md
└── docs/
    ├── core/
    ├── templates/
    ├── adapters/
    ├── seed-docs/
    ├── ref-docs/
    ├── artifacts/
    ├── backlog/
    └── runs/
```

`README.md`는 GitHub에서 프로젝트를 처음 보는 사람이 애플리케이션 소스와 Vulcan-Anvil Ex 운영 파일을 구분할 수 있도록 생성됩니다.

`docs/ref-docs/`는 민감한 프로젝트 참고문서를 둘 수 있는 영역이며 기본적으로 Git에서 제외됩니다.

`docs/seed-docs/`는 공개 표준 문서를 프로젝트에 주입하는 영역입니다. 현재는 공공데이터 공통표준과 소프트웨어 개발보안 관련 공개 문서를 기준 자료로 둡니다.

`docs/artifacts/`는 실제 프로젝트 산출물이 작성되는 영역입니다.

`docs/runs/`는 에이전트가 수행한 작업 단위인 Run 기록을 남기는 영역입니다.

## 4. 자주 쓰는 명령

아래 명령은 사용자가 매번 직접 실행하는 절차라기보다, Orchestrator가 작업을 기록하고 검증할 때 사용하는 보조 도구입니다.

| 명령 | 설명 |
| --- | --- |
| `init` | 새 프로젝트에 Vulcan-Anvil Ex 문서와 템플릿을 주입 |
| `status` | 현재 Gate, Profile, 브랜치, active Run/Wave, 다음 행동 후보를 한 번에 요약 |
| `status --check` | `prepare-transition` 기반 Gate 전환 진단을 status 출력 뒤에 이어서 실행 |
| `orchestrator-plan` | Orchestrator 실행 계획 Run 생성 |
| `run-new` | persona/skill 기반 Run 초안 생성 |
| `run-check` | Run 문서 필수 필드와 상태 검사 |
| `prepare-transition` | 다음 Gate로 넘어가기 전 상세/호환 진단. 일반적으로는 `status --check`를 먼저 사용 |
| `trace-context` | 특정 ID 주변 추적성 그래프를 Run 입력 후보 YAML/JSON으로 출력 |
| `run-new --trace-seed <ID>` | 추적성 그래프 기반으로 Run 초안의 관련 ID와 참조 문서 후보 보강 |
| `wave-start <BW-ID> --trace-seed <ID>` | Build Wave Run 초안의 `related_ids`, `target_contracts`, 참조 문서 후보 보강 |
| `profile-status` | 현재 Delivery Profile과 `profile_rules` 상세 확인 |
| `branch-status` | 현재 브랜치, 통합 브랜치, QA workspace 상태 상세 확인 |
| `branch-start impl` | 구현 통합 브랜치(`workflow.integration_branch`) 생성 또는 전환 |
| `release-pr` | Gate 5에서 통합 브랜치 -> 기준 브랜치 Release PR 생성/갱신 |
| `agent-run --mode work` | 선택 사항. Run 문서를 codex-cli, claude-cli, antigravity-cli 같은 외부 CLI worker runner로 실행 |
| `run-exec` | 선택 사항. 특정 Run을 외부 CLI runner로 실행하고 `_exec` 로그, watchdog/timeout, worktree 증적을 남김 |
| `handoff` | 다른 실행 환경으로 넘길 검수 Run 생성 |
| `review-request` | 별도 세션/worktree 기반 독립 검수 요청 생성 |
| `review-run` | 생성된 독립 검수 요청을 codex-cli 또는 claude-cli로 실행 |
| `check-trace` | 추적성 오류 상세 진단 또는 trace-only 회귀 검사 |
| `drift-report` | 설계 산출물과 실제 코드/API/DB surface의 불일치 후보 보고서 생성 |
| `backlog` | 백로그 추가, 조회, 완료, 반려 |
| `export` | Dashboard용 snapshot 생성 |
| `upgrade` | 기존 프로젝트에 최신 framework 문서 반영 |
| `version` | 현재 Vulcan-Anvil Ex 버전 확인 |

독립 검수와 교차검증의 기본 모델과 추론 강도는 `vulcan.config.json`의 `runtime.available_runners`와 `runtime.model_policy`에서 정한다.
Codex runner는 기본적으로 역할별 model/effort 정책을 사용한다.
감리/QA 목적의 Gate 2, Gate 4 검수는 Codex 기준 `gpt-5.5` + `high`를 권장하고, QA 실행/로그 정리 같은 작업은 더 가벼운 정책을 사용할 수 있다.
자세한 기준은 `docs/core/CODEX_MODEL_POLICY.md`를 따른다.
Claude CLI를 runner로 쓸 때는 `--runner claude-cli`를 지정한다. Claude CLI는 `claude -p` 기반 비대화형 실행을 사용하며 기본값은 `claude-opus-4-7` + `high` effort다.

새 프로젝트는 `independent_enabled: true`가 기본값이다. 이는 Gate 2/Gate 4 종료 전 교차검증을 기본 권장 절차로 둔다는 뜻이며, `review-run`을 자동 실행한다는 뜻은 아니다.
독립 검수와 독립 구현은 장기적으로 `Independent Execution` 공통 모델로 수렴한다. 사용자-facing 용어는 `교차검증`을 우선 사용한다. `review-run`은 그중 읽기 중심 review 실행이고, 향후 `run-exec`는 Build Wave, Evidence Run, PR 교차검증까지 같은 runner 방식으로 실행하는 방향이다.
`init`은 현재 PC의 `codex`와 `claude` CLI 설치 여부를 감지해 `vulcan.config.json.runtime.available_runners`에 기록한다. Codex만 있으면 같은 runner 기반 독립검수/동시 worktree 작업으로 운영하고, Codex와 Claude가 모두 있으면 Gate/PR/QA 교차검증과 cross-runner 작업을 기본 후보로 둔다.

### 4.1 Codex repo-local skill과 custom agent

Codex를 메인 Orchestrator로 사용할 때는 다음 세 계층을 구분합니다.

| 계층 | 위치 | 역할 |
| --- | --- | --- |
| 진입 지침 | `AGENTS.md` | Codex/GPT가 현재 프로젝트에서 가장 먼저 따르는 Orchestrator 지침 |
| repo-local skill | `.agents/skills/` | Gate/설계/구현/QA/릴리즈 작업에서 필요할 때 읽는 절차 카드 |
| custom agent | `.codex/agents/` | Orchestrator가 명시적으로 호출하는 읽기 중심 보조 에이전트 정의 |

기본 custom agent는 다음과 같습니다.

| Agent | 용도 |
| --- | --- |
| `trace-scout` | 특정 REQ/API/PGM 주변 관련 ID와 source document 후보 탐색 |
| `run-drafter` | worker에게 넘길 Run 입력 계약이 충분한지 검토 |
| `contract-reviewer` | Program/API/DB/UI 계약과 구현 정합성 검토 |
| `qa-reader` | QA 로그, 스크린샷, transcript, stale evidence 해석 |

custom agent 결과는 후보 의견입니다. Gate 전환, session 갱신, QA Pass, release/merge 가능 판단은 메인 Orchestrator가 다시 검증합니다.
현재 Codex surface가 native custom agent 선택을 직접 노출하지 않는 경우도 있으므로, Orchestrator는 실제 실행 방식을 `native_custom_agent`, `prompt_contract_fallback`, `unknown` 중 하나로 보고해야 합니다.

### 4.2 Antigravity/Agy main Orchestrator

Agy를 메인 Orchestrator로 사용할 수도 있습니다. 이 경우 Agy는 `GEMINI.md`, `docs/core/`, `docs/adapters/gemini/`를 기준으로 Gate를 조율하고, 플랫폼의 native subagent와 `Workspace: branch` 기능을 활용해 worker를 분리 실행할 수 있습니다.

```text
안녕.. 너는 Agy 기반 메인 오케스트레이터로써 이 프로젝트를 잘 이끌어가야해.
GEMINI.md, session.json, docs/core, docs/adapters/gemini 내용을 확인하고 현재 Gate부터 조율해줘.
```

Agy `Workspace: branch`는 Ex에서 native branch agent 경로로 취급합니다. 일반 Git worktree나 `agy.exe` 외부 CLI runner와 다르게 플랫폼이 가상 격리 작업공간을 관리하므로, Run 문서에는 `delegation_records.mode: agy-branch-agent`로 얇은 위임 기록을 남깁니다.

중요한 차이가 하나 있습니다. `agent-run --mode work`나 `run-exec`는 worker 실행 전 `run-preflight`를 자동 호출하지만, Agy native subagent/branch 위임은 그 CLI 경로를 타지 않습니다. 따라서 Orchestrator는 worker를 부르기 전에 직접 다음 명령을 실행해야 합니다.

```powershell
python vulcan.py run-preflight <run-file>
```

`run-preflight`가 `TBD`, scope, Run metadata/Input 계약 불일치, BW-000 상태 확정 오염을 차단하면 worker를 실행하지 말고 Run 문서를 먼저 보정합니다.

### 4.3 Gate 전환 전 사전 진단

Gate 산출물 작성이 끝났다고 바로 다음 Gate로 넘어가지 않습니다. Orchestrator는 먼저 현재 Gate 상태와 Run 완료 여부, 추적성 이슈를 한 번에 확인합니다.

```powershell
python vulcan.py status --check
```

`status --check`는 `prepare-transition` 진단을 status 흐름 안에서 보여주는 기본 진입점입니다. 실패하면 다음 Gate로 넘어가지 말고, 출력된 산출물/ID/Run 기준으로 원인을 정리한 뒤 사용자에게 승인 또는 보완 방향을 묻습니다.

`prepare-transition`은 여전히 사용할 수 있지만, 일반적인 첫 명령이 아니라 상세/호환 진단 명령으로 둡니다. 추적성 문제만 더 깊게 봐야 할 때만 `check-trace`를 별도로 실행합니다.

### 4.4 설계-구현 Drift 확인

구현이나 QA 수정 후에는 설계 문서를 바로 코드 기준으로 덮어쓰지 않습니다. 먼저 drift 후보 보고서를 만들어, 설계가 바뀌어야 하는지 구현이 계약을 어긴 것인지 구분합니다.

```powershell
python vulcan.py drift-report --output docs/artifacts/04-review/evidence/contract/contract-drift-report.md
```

`drift-report`는 후보 보고서입니다. Orchestrator는 결과를 FIND, CR, ISSUE 후보로 분류하고, 승인된 경우에만 설계 문서 또는 코드 수정을 별도 Run으로 진행합니다.

### 4.5 Adapter별 Run 입력 문서

Run 입력 계약의 형식은 모든 runner가 `docs/core/RUN_INPUT_CONTRACT.md`를 공유합니다. 다만 `source_documents.read_first`에는 runner별 prompt를 섞지 않습니다.

| Runner | 공통으로 먼저 읽는 문서 | 추가 adapter 문서 |
| --- | --- | --- |
| Codex/GPT | `docs/core/GATE_EXECUTION_CHECKLIST.md` | `docs/adapters/codex-gpt/GATE_PROMPTS.md` |
| Claude | `docs/core/GATE_EXECUTION_CHECKLIST.md` | `docs/adapters/claude/GATE_PROMPTS.md` |
| Gemini/Antigravity | `docs/core/GATE_EXECUTION_CHECKLIST.md` | `docs/adapters/gemini/GATE_PROMPTS_GEMINI.md` |

따라서 Gemini나 Claude Run 문서에 Codex 전용 `docs/adapters/codex-gpt/GATE_PROMPTS.md`가 들어가 있다면 최신 규칙 기준으로는 정리 대상입니다.

## 5. 0.4 구현/QA 흐름

`0.4.x` audit workflow에서는 구현과 QA를 `main`에 바로 누적하지 않습니다. `impl`에 진입하면 Orchestrator는 먼저 통합 브랜치를 시작합니다.

```powershell
python vulcan.py branch-status
python vulcan.py branch-start impl
```

통합 브랜치 이름은 `vulcan.config.json`의 `workflow.integration_branch`가 결정합니다. 기본값은 `dev`지만, 프로젝트에서 `dev-happy`, `develop`, `integration/todo`처럼 바꿔도 됩니다.

```json
{
  "workflow": {
    "integration_branch": "dev-happy"
  }
}
```

이후 구현은 보통 다음 순서로 진행합니다.

```text
Gate 3 승인
→ branch-start impl
→ implementation-plan Run
→ BW-000 implementation-scaffold 필요 여부 판단
→ build-wave Run 생성
→ native worker(subagent/thread/native branch agent)에게 위임
→ 필요 시 agent-run --mode work 또는 run-exec로 외부 CLI runner 실행
→ Orchestrator가 worker 결과 검토/통합/재검증
→ wave-complete
```

신규 개발이거나 빌드 가능한 코드 골격이 없으면 `BW-000 implementation-scaffold`를 먼저 둡니다. 이 단계는 업무 로직을 완성하는 것이 아니라, 빌드 설정, entrypoint, public class/interface/method signature, DTO/schema, 테스트 skeleton을 고정하는 단계입니다.

Codex subagent, Codex thread, Claude subagent, Agy workspace branch agent처럼 native 위임을 사용한 경우에는 외부 CLI runner 수준의 stderr/jsonl/timeout 로그가 없을 수 있습니다. 이때는 현재 Run의 `delegation_records`에 위임 대상, scope, 변경 파일, 결과 요약, Orchestrator 재검증 명령을 남깁니다. `agent-run`/`run-exec` 같은 외부 CLI runner는 기존처럼 `Run Execution Record`, `_exec` 로그, watchdog/timeout 정보를 남깁니다.

Antigravity/Agy의 `Workspace: branch`는 native branch agent 경로로 취급합니다. Agy가 가상 브랜치에서 작업하면 `delegation_records.mode: agy-branch-agent`로 얇게 기록하고, Orchestrator가 변경 파일과 검증 명령을 다시 확인합니다. `agy.exe`를 외부 CLI runner로 호출해 transcript/watchdog 증적을 남기는 경로는 선택 사항입니다. Agy 검토 기록은 [Agy Workspace Branch Delegation Review](reference/_reviews/AGY-WORKSPACE-BRANCH-DELEGATION-REVIEW.md)를 참고합니다.

worker 실행은 즉시 kill 기준이 아니라 progress watchdog 기준입니다. `execution.progress_probe_seconds`마다 status 변화, worktree diff, 변경 파일 수, runner 로그 진척을 확인하고, `execution.no_progress_timeout_seconds` 동안 의미 있는 진척이 없으면 `stalled` timeout 후보로 종료합니다. `execution.hard_timeout_seconds`는 진척 여부와 무관한 절대 상한입니다.

```json
{
  "execution": {
    "default_timeout_seconds": 2400,
    "hard_timeout_seconds": 5400,
    "extension_seconds": 600,
    "max_extensions": 3,
    "progress_probe_seconds": 300,
    "no_progress_timeout_seconds": 900,
    "min_runtime_seconds": 120
  }
}
```

watchdog 상태, 마지막 진척 시각, 무진척 시간, 종료 사유는 `docs/runs/_exec/*-summary.json`, `activity.json`, Run Execution Record에 기록됩니다. 기존 `default_timeout_seconds`와 extension 필드는 호환을 위해 남아 있으며, watchdog 설정이 없을 때의 fallback으로 사용할 수 있습니다. Orchestrator는 timeout이 발생하면 즉시 실패로 단정하지 않고, 남은 diff와 로그를 보고 Run 분리, resume, 재실행, 사용자 협의 중 하나를 선택합니다.

Gate 4 QA는 한 번에 몰아서 하지 않고 다음 단계로 나눕니다.

| QA Run | 목적 |
| --- | --- |
| `QA-000` | integration branch QA workspace 기록, 의존성/포트/DB/Playwright 가능성 확인 |
| `QA-001` | backend/frontend test, lint, build, `check-contract`, `run-check` 같은 명령 검증. 추적성 오류가 있으면 `check-trace` 상세 진단 |
| `QA-002` | Playwright UI/E2E screenshot/log/trace 증적 수집 |
| `QA-003` | QA Finding, Test Result, FIND/CR/ISSUE, Gate 4 판단 후보 정리 |

`QA-001`~`QA-003`은 `QA-000`이 기록한 같은 QA workspace에서 실행합니다. 기본 workspace는 `workflow.integration_branch`의 현재 작업공간입니다. QA worktree는 명시적으로 활성화한 경우에만 사용합니다. QA worker는 실패를 발견해도 소스코드를 바로 수정하지 않고 원인, 재현 명령, 로그 경로, 영향 ID, 후보 FIND/CR/ISSUE를 남깁니다. 수정이 필요하면 Orchestrator가 사용자와 결정한 뒤 별도 `qa-fix-loop` Run으로 처리합니다.

테스트 문서의 역할은 분리합니다. Gate 3 테스트케이스 문서는 “무엇을 어떻게 검증할지”를 담는 계획 문서이므로 `Planned`를 `Pass`로 덮어쓰지 않습니다. Gate 4에서 실제 실행한 결과는 `DOC-QA-G4-002_Test-Result_v0.1.md`에 `Pass / Fail / Not Run / Skipped / environment_blocked`로 기록하고, QA-003에서 이 결과와 증적을 근거로 요구사항추적표의 `상태`, `증적`, `요구사항별 검증 요약`을 갱신합니다.

### Run 생성 예시

```powershell
python vulcan.py run-new ^
  --gate gate4 ^
  --persona review ^
  --skill traceability-review ^
  --title "로그인 게시판 추적성 검토" ^
  --related-ids REQ-001,REQ-002
```

추적성 그래프에서 Run 입력 후보를 보강하려면 `--trace-seed`를 사용합니다.

```powershell
python vulcan.py wave-start BW-001 ^
  --title "회원가입 API 구현" ^
  --trace-seed REQ-001-01
```

이 옵션은 `related_ids`, `target_contracts`, `source_documents.reference_on_demand`를 추천값으로 보강합니다.
`interface_contract`와 `scope.writable`은 Program Design과 실제 작업 범위를 확인한 뒤 Orchestrator가 확정해야 합니다.

### 추적성 검사 예시

```powershell
python vulcan.py check-trace
```
