# Getting Started

Vulcan-Anvil Ex는 사용자가 명령어를 하나씩 넣어 산출물을 수동 생성하는 도구가 아닙니다. 사용자는 만들고 싶은 것과 중요한 제약을 말하고, Orchestrator가 Gate에 맞게 요구사항, 설계, 구현, 테스트, 증적을 조율합니다.

## 1. 새 프로젝트 초기화

```powershell
python vulcan.py init ../my-project "My Project"
```

초기화하면 Core 문서, 템플릿, adapter 문서, 공개 표준 참고자료, `AGENTS.md`, `session.json`, 프로젝트용 `vulcan.py`가 생성됩니다.

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

처음에는 가볍게 인사하거나 목표를 말하면 됩니다.

`init` 직후 새 대화나 새 세션을 시작했다면, 먼저 메인 에이전트가 Orchestrator 역할과 프로젝트 문서를 확인하도록 요청하는 것이 좋습니다.

```text
안녕.. 너는 메인 오케스트레이터로써 이 프로젝트를 잘 이끌어가야해..
그에 대한 내용이 여기에 있으니 한번 전체적인 내용을 확인해줘.
```

이 요청은 구현을 바로 시작하라는 뜻이 아닙니다. 메인 에이전트가 `AGENTS.md`, `session.json`, `docs/core/`, adapter 문서, 현재 Gate 상태를 먼저 확인하고, 이후 Gate별 진행을 안정적으로 조율하도록 만드는 초기 정렬 단계입니다.

그 다음 만들고 싶은 기능이나 제약을 말합니다.

```text
로그인과 게시글 작성 기능이 있는 게시판 샘플을 만들고 싶어.
```

Orchestrator는 `AGENTS.md`, `docs/core/`, adapter 규칙을 읽고 필요한 질문을 한 뒤 현재 Gate에서 허용된 범위부터 진행합니다. Phase 0 또는 Gate 1에서는 바로 구현하지 않고 범위, 요구사항, 질문, 승인 지점을 먼저 정리합니다.

## 3. 기본 프로젝트 구조

```text
my-project/
├── README.md
├── AGENTS.md
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
| `orchestrator-plan` | Orchestrator 실행 계획 Run 생성 |
| `run-new` | persona/skill 기반 Run 초안 생성 |
| `run-check` | Run 문서 필수 필드와 상태 검사 |
| `branch-status` | 현재 브랜치, 통합 브랜치, QA workspace 상태 확인 |
| `branch-start impl` | 구현 통합 브랜치(`workflow.integration_branch`) 생성 또는 전환 |
| `agent-run --mode work` | Run 문서를 worker runner로 실행 |
| `run-exec` | 특정 Run을 codex-cli, claude-cli, antigravity-cli 같은 runner로 실행 |
| `handoff` | 다른 실행 환경으로 넘길 검수 Run 생성 |
| `review-request` | 별도 세션/worktree 기반 독립 검수 요청 생성 |
| `review-run` | 생성된 독립 검수 요청을 codex-cli 또는 claude-cli로 실행 |
| `check-trace` | Gate별 추적성 검사 |
| `backlog` | 백로그 추가, 조회, 완료, 반려 |
| `export` | Dashboard용 snapshot 생성 |
| `upgrade` | 기존 프로젝트에 최신 framework 문서 반영 |
| `version` | 현재 Vulcan-Anvil Ex 버전 확인 |

독립 검수와 교차검증의 기본 모델과 추론 강도는 `vulcan.config.json`의 `runtime.available_runners`에서 정한다. 감리/QA 목적의 Gate 2, Gate 4 검수는 Codex 기준 `gpt-5.5` + `high`를 권장한다.
Claude CLI를 runner로 쓸 때는 `--runner claude-cli`를 지정한다. Claude CLI는 `claude -p` 기반 비대화형 실행을 사용하며 기본값은 `claude-opus-4-7` + `high` effort다.

새 프로젝트는 `independent_enabled: true`가 기본값이다. 이는 Gate 2/Gate 4 종료 전 교차검증을 기본 권장 절차로 둔다는 뜻이며, `review-run`을 자동 실행한다는 뜻은 아니다.
독립 검수와 독립 구현은 장기적으로 `Independent Execution` 공통 모델로 수렴한다. 사용자-facing 용어는 `교차검증`을 우선 사용한다. `review-run`은 그중 읽기 중심 review 실행이고, 향후 `run-exec`는 Build Wave, Evidence Run, PR 교차검증까지 같은 runner 방식으로 실행하는 방향이다.
`init`은 현재 PC의 `codex`와 `claude` CLI 설치 여부를 감지해 `vulcan.config.json.runtime.available_runners`에 기록한다. Codex만 있으면 같은 runner 기반 독립검수/동시 worktree 작업으로 운영하고, Codex와 Claude가 모두 있으면 Gate/PR/QA 교차검증과 cross-runner 작업을 기본 후보로 둔다.

## 5. 0.3 구현/QA 흐름

`0.3.x` audit workflow에서는 구현과 QA를 `main`에 바로 누적하지 않습니다. `impl`에 진입하면 Orchestrator는 먼저 통합 브랜치를 시작합니다.

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
→ agent-run --mode work 또는 run-exec로 worker 실행
→ Orchestrator가 worker 결과 검토/통합/재검증
→ wave-complete
```

신규 개발이거나 빌드 가능한 코드 골격이 없으면 `BW-000 implementation-scaffold`를 먼저 둡니다. 이 단계는 업무 로직을 완성하는 것이 아니라, 빌드 설정, entrypoint, public class/interface/method signature, DTO/schema, 테스트 skeleton을 고정하는 단계입니다.

Gate 4 QA는 한 번에 몰아서 하지 않고 다음 단계로 나눕니다.

| QA Run | 목적 |
| --- | --- |
| `QA-000` | QA workspace 준비, 의존성/포트/DB/Playwright 가능성 확인 |
| `QA-001` | backend/frontend test, lint, build, `check-contract`, `check-trace`, `run-check` 같은 명령 검증 |
| `QA-002` | Playwright UI/E2E screenshot/log/trace 증적 수집 |
| `QA-003` | QA Finding, Test Result, FIND/CR/ISSUE, Gate 4 판단 후보 정리 |

`QA-001`~`QA-003`은 `QA-000`이 기록한 같은 QA workspace에서 실행합니다. QA worker는 실패를 발견해도 소스코드를 바로 수정하지 않고 원인, 재현 명령, 로그 경로, 영향 ID, 후보 FIND/CR/ISSUE를 남깁니다. 수정이 필요하면 Orchestrator가 사용자와 결정한 뒤 별도 `qa-fix-loop` Run으로 처리합니다.

### Run 생성 예시

```powershell
python vulcan.py run-new ^
  --gate gate4 ^
  --persona review ^
  --skill traceability-review ^
  --title "로그인 게시판 추적성 검토" ^
  --related-ids REQ-001,REQ-002
```

### 추적성 검사 예시

```powershell
python vulcan.py check-trace
```
