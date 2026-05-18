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

```text
로그인과 게시글 작성 기능이 있는 게시판 샘플을 만들고 싶어.
감리 대응 문서와 테스트 증적까지 같이 만들어줘.
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
├── commenting-standards.md
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
| `handoff` | 다른 실행 환경으로 넘길 검수 Run 생성 |
| `check-trace` | Gate별 추적성 검사 |
| `backlog` | 백로그 추가, 조회, 완료, 반려 |
| `export` | Dashboard용 snapshot 생성 |
| `upgrade` | 기존 프로젝트에 최신 framework 문서 반영 |
| `version` | 현재 Vulcan-Anvil Ex 버전 확인 |

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
