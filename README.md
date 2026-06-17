# Vulcan-Anvil Ex

> 사람은 목표와 승인 기준을 제시하고, AI 에이전트는 문서·Gate·검증 체계 안에서 요구사항부터 코드와 증적까지 이어간다.

Vulcan-Anvil Ex는 AI 에이전트가 장기 프로젝트에서 길을 잃지 않도록 돕는 AI 협업 개발 운영 프레임워크입니다.

한 줄로 말하면, Ex는 앱을 가장 빨리 만드는 도구가 아니라 **AI가 만든 결과를 요구사항, 설계, 테스트, 증적, 승인 흐름으로 회수하는 Trust/Governance Layer**입니다.

사용자는 "무엇을 만들고 싶은지"와 중요한 제약을 말하고, 메인 에이전트인 Orchestrator가 요구사항, 설계, 구현, 테스트, 증적 수집을 단계별로 조율합니다. `vulcan.py`는 그 과정에서 LLM이 놓치기 쉬운 ID 체계, Run 기록, 추적성, Gate 전환 규칙을 프로그램으로 점검합니다.

에이전트가 코딩하고, Vulcan-Anvil이 그 일을 설명 가능하게 만듭니다.

## 어떤 상황에 맞나

| 상황 | 추천 |
| --- | --- |
| 기능/기술 가설을 실험하고 결과를 기록하고 싶다 | `--profile poc` |
| 제품/업무 앱을 만들고 릴리즈 품질을 유지하고 싶다 | `--profile product` |
| 감리, 고객 검수, 인수인계, 보안/QA 증적이 필요하다 | 기본값 `--profile audit` |

PoC는 품질이 낮은 모드가 아니라 문서와 증적의 깊이를 줄여 핵심 가설, 반복별 기능 변화, 다음 판단을 남기는 모드입니다. Product는 일반 제품/업무 앱 개발의 중간층이고, Audit은 감리/SI/규제 대응처럼 가장 강한 추적성과 증적이 필요한 경우에 사용합니다.

Profile 선택 기준은 [Which Profile Should I Use?](docs/WHICH_PROFILE_SHOULD_I_USE.md)를 참고합니다.

## 한눈에 보기

- **사람/사용자**: 목표, 제약, 승인, 판단이 필요한 결정을 제공한다.
- **Orchestrator**: 사용자와 대화하며 계획을 세우고, 필요한 persona/subagent에 일을 나누고, 결과를 검증한다.
- **문서**: 요구사항, 기능, 화면, 프로그램, DB, 보안, 테스트, 증적을 ID로 연결한다.
- **코드**: 승인된 문서와 추적 규칙을 기준으로 에이전트가 작성한다.
- **검증**: 테스트, 화면 증적, Run 기록, 추적성 검사를 통해 다음 Gate로 넘어갈 수 있는지 확인한다.
- **Adapter**: Codex, Claude, Gemini/Antigravity 같은 런타임 차이를 흡수한다.
- **Dashboard**: Gate, 문서, Run, 통계, 최근 커밋을 한 화면에서 확인한다.

최근 `0.4.x` 라인은 Gate 전환 전 사전 진단(`prepare-transition`), 설계-코드 불일치 후보 보고(`drift-report`), adapter별 Run 입력 문서 분리, native subagent/Agy Workspace branch 위임 기록, 더 구체적인 `check-trace` 진단, Dashboard 문서 코멘트를 보강하고 있습니다. 공통 Gate 실행 기준은 `docs/core/GATE_EXECUTION_CHECKLIST.md`에 두고, Codex/Claude/Gemini 같은 runner 전용 prompt는 각 adapter 문서에서만 추가로 참조합니다.

## 왜 필요한가

AI 에이전트는 코드를 빠르게 만들 수 있지만, 긴 프로젝트에서는 다음 문제가 반복됩니다.

1. 이전 결정과 설계 근거를 잊는다.
2. 구현은 되었지만 요구사항, 테스트, 증적과 연결되지 않는다.
3. QA 중 발견한 결함과 변경요청을 구분하지 못한다.
4. Codex, Claude, GitHub Review처럼 도구가 바뀌면 작업 규칙도 흩어진다.

Vulcan-Anvil Ex는 이 문제를 문서화된 Core 규칙, Adapter, Run 기록, 추적성 검사로 줄이는 것을 목표로 합니다.

## 60초 사용 흐름

1. 이 저장소에서 `vulcan.py init`으로 새 프로젝트를 만든다.
2. 생성된 프로젝트 폴더를 Codex CLI, Codex Desktop, Claude 같은 에이전트 환경에서 연다.
3. 사용자는 "로그인이 있는 게시판을 만들고 싶다"처럼 목표와 제약을 말한다.
4. Orchestrator가 `AGENTS.md`와 `docs/core/` 규칙을 읽고 필요한 질문을 한다.
5. Orchestrator가 요구사항, 설계, 테스트 기준, 구현, 증적을 단계별로 만든다.
6. `vulcan.py`는 Run, 추적성, Gate 전환 조건을 검사한다.
7. Dashboard에서 Gate, 산출물, Run, 테스트/백로그 통계, 최근 커밋을 확인한다.

## 빠른 시작

```powershell
python vulcan.py init ../my-poc "My PoC" --profile poc
cd ../my-poc
```

일반 제품/업무 앱은 `product`, 감리 대응 프로젝트는 기본값인 `audit`을 사용합니다.

```powershell
python vulcan.py init ../my-product "My Product" --profile product
python vulcan.py init ../my-audit-project "My Audit Project"
```

원격 저장소와 함께 시작하려면 `--remote`를 추가합니다.

```powershell
python vulcan.py init ../my-project "My Project" --remote https://github.com/<owner>/my-project.git
```

이후 프로젝트 폴더를 Codex, Claude, Antigravity/Agy 같은 에이전트 환경에서 열고 목표를 말합니다.

```text
로그인과 게시글 작성 기능이 있는 게시판 샘플을 만들고 싶어.
```

자세한 시작 방법은 [Getting Started](docs/GETTING_STARTED.md)를 참고합니다.

## 무엇이 남나

Ex 프로젝트가 끝나면 단순히 코드만 남지 않습니다. Profile에 따라 깊이는 다르지만 다음 정보가 함께 남습니다.

- 목표와 요구사항, 설계 판단
- 구현 코드와 테스트 코드
- 실행한 테스트 명령과 로그
- 화면 증적 또는 smoke/demo 결과
- FIND/CR/ISSUE와 남은 판단 항목
- 요구사항에서 증적까지 이어지는 추적 정보

샘플 기준의 소요 시간과 산출물 차이는 [Examples And Benchmarks](docs/EXAMPLES_AND_BENCHMARKS.md)를 참고합니다.

Product profile은 `docs/product/`에 Product Brief, Architecture, ADR Log, Contracts, Traceability, Regression/Release Report를 생성합니다.
이 문서들은 Gate별 제출 문서가 아니라 제품을 계속 개발하고 릴리즈하기 위한 운영 문서입니다.
중요한 아키텍처 의사결정이 아직 없다면 ADR Log는 `ADR-NONE`을 유지합니다.
Gate 5의 `release-pr --dry-run`도 Product profile에서는 audit 산출물 대신 `docs/product/` 원장과 backlog, Gate 5 승인서를 evidence 기준으로 사용합니다.

## Codex에서 사용할 때

Codex를 메인 Orchestrator로 사용할 때는 프로젝트 루트의 `AGENTS.md`가 진입 문서입니다.
`init`으로 생성된 프로젝트에는 Codex용 보조 지침도 함께 들어갑니다.

| 경로 | 용도 |
| --- | --- |
| `AGENTS.md` | Codex/GPT Orchestrator가 먼저 읽는 프로젝트 운영 지침 |
| `.agents/skills/` | Gate, 설계, 구현 Wave, QA, 릴리즈 작업에서 Codex가 필요할 때 읽는 repo-local skill 카드 |
| `.codex/agents/` | `trace-scout`, `run-drafter`, `contract-reviewer`, `qa-reader` 같은 읽기 중심 Codex custom agent 정의 |
| `docs/adapters/codex-gpt/` | Codex runner와 Run 계약을 연결하는 adapter 문서 |

Custom agent는 자동 승인자가 아닙니다. 메인 Orchestrator가 관련 ID 탐색, Run 초안 검토, 계약 정합성 검토, QA 로그 해석 같은 보조 작업을 맡길 때 사용하고, 최종 Gate 전환과 승인 판단은 다시 Orchestrator가 검증합니다.

## Antigravity/Agy에서 사용할 때

Antigravity/Agy도 메인 Orchestrator가 될 수 있습니다. 이 경우 Gemini/Antigravity adapter 문서를 기준으로 Core Gate 규칙을 읽고, Agy 플랫폼의 native subagent와 `Workspace: branch` 기능을 활용해 worker를 격리 실행합니다.

| 경로 | 용도 |
| --- | --- |
| `GEMINI.md` | Gemini/Antigravity Orchestrator가 읽는 프로젝트 운영 지침 |
| `docs/adapters/gemini/` | Agy/Gemini prompt, persona mapping, structured output, native branch delegation 기준 |
| `docs/core/AGENT_RUN_PROTOCOL_GEMINI.md` | Agy native subagent/branch 실행 프로토콜 |
| `docs/reference/_reviews/AGY-WORKSPACE-BRANCH-DELEGATION-REVIEW.md` | Agy Workspace branch 방식과 Ex 위임 기록 정합성 검토 |

Agy `Workspace: branch`는 일반 Git worktree와 다르게 플랫폼이 가상 격리 작업공간을 제공하는 경로로 취급합니다. 외부 CLI runner처럼 `_exec` 로그를 두껍게 남기기보다, Run 문서의 `delegation_records.mode: agy-branch-agent`에 위임 대상, 범위, 변경 파일, 결과 요약, Orchestrator 재검증 명령을 남깁니다.

주의할 점도 있습니다. Agy native branch 위임은 `run-exec` 경로가 아니므로 자동 preflight가 걸리지 않습니다. Orchestrator는 worker를 부르기 전에 직접 `python vulcan.py run-preflight <run-file>`를 실행해 `TBD`, scope, Run metadata 불일치를 먼저 막아야 합니다.

## Dashboard

```powershell
cd dashboard
npm install
npm run dev
```

브라우저에서 `http://localhost:3001`로 접속한 뒤 로컬 프로젝트 경로 또는 GitHub 저장소 URL을 등록합니다.

Dashboard는 `session.json`, `docs/artifacts/`, `docs/runs/`, Git 커밋을 읽어 프로젝트 상태를 보여줍니다.

업그레이드와 Dashboard 운영 방법은 [Upgrade And Dashboard](docs/UPGRADE_AND_DASHBOARD.md)를 참고합니다.

## 핵심 흐름

Vulcan-Anvil Ex는 Phase 0과 5-Gate 흐름으로 작업을 나눕니다.

| 단계 | 목적 | 주요 산출물 |
| --- | --- | --- |
| Phase 0 | 탐색과 방향 설정 | 목표 초안, 질문 목록, 범위 후보, 제약/위험 |
| Gate 1 | 요구사항 정리 | 요구사항정의서, 요구사항추적표 초안 |
| Gate 2 | 설계 | 아키텍처, 기능, 프로그램, API, 화면, DB, 보안 설계 |
| Gate 3 | 테스트 설계 | 단위/기능 테스트 케이스, 통합 테스트 기준 |
| 구현 | 승인된 설계 구현 | 코드, 설정, 메시지 리소스, 테스트 코드 |
| Gate 4 | QA 검수 | 테스트 결과, 화면 증적, FIND/CR/ISSUE 분류 |
| Gate 5 | 최종 승인 | 릴리즈 후보, 인수인계 항목, 잔여 리스크 |

Gate 3 테스트케이스는 실행 계획과 기대 기준을 정의합니다. 실제 Pass/Fail/Not Run 결과는 Gate 4 테스트 결과서에 기록하고, 요구사항 관점의 최종 검증 상태는 요구사항추적표에 반영합니다.

개념 설명은 [Concepts](docs/CONCEPTS.md)를 참고합니다.

## 현재 상태

**Experimental - v0.4.8**

`0.4.8`은 Product profile 안정화 패치입니다. Product Build Wave의 `SCN/API/DATA/UI/REG` 관련 ID를 보존하고, Product Gate 5 release PR body가 `docs/product/` 원장 문서를 evidence로 표시하며, ADR이 없을 때는 `ADR-NONE` empty-state를 사용합니다.

`0.4.7`은 Dashboard 문서 코멘트와 Orchestrator 가시성을 보강한 패치였습니다. Dashboard에서 Markdown 산출물에 코멘트를 남기면 원본 문서를 수정하지 않고 `.vulcan/comments/comments.jsonl`에 sidecar로 저장하며, Orchestrator는 `python vulcan.py status`의 `dashboard_comments` 요약을 통해 코멘트와 사용자 판단 요청을 먼저 확인할 수 있습니다.

`0.4.6`은 Codex custom agent, PoC profile 완충, Agy native main orchestration, `Workspace: branch` 위임 기록, Run preflight guard, `prepare-transition` 완성도 검사를 묶은 패치였습니다.

아직 제품화된 안정 버전은 아니며, 실제 프로젝트 적용 결과에 따라 문서 체계와 CLI 명령은 계속 조정될 수 있습니다.

릴리즈별 변경사항은 [CHANGELOG.md](CHANGELOG.md)를 기준으로 확인합니다.

## 문서

| 문서 | 내용 |
| --- | --- |
| [Getting Started](docs/GETTING_STARTED.md) | 초기화, 원격 저장소, 프로젝트 시작, 주요 명령 |
| [Which Profile Should I Use?](docs/WHICH_PROFILE_SHOULD_I_USE.md) | PoC, Product, Audit 선택 기준 |
| [Examples And Benchmarks](docs/EXAMPLES_AND_BENCHMARKS.md) | 샘플 실행 결과, 산출물, 소요 시간 요약 |
| [Concepts](docs/CONCEPTS.md) | 이름의 의미, Orchestrator, Gate, Backlog, Build Wave, Adapter |
| [Product Profile Baseline](docs/core/PRODUCT_PROFILE_BASELINE.md) | 일반 제품/업무 앱 레이어의 보안, 데이터, 릴리즈 기준 |
| [Profile Gap Check](docs/core/PROFILE_GAP_CHECK.md) | PoC -> Product -> Audit 전환 전 부족 항목 진단 기준 |
| [Upgrade And Dashboard](docs/UPGRADE_AND_DASHBOARD.md) | 기존 프로젝트 업그레이드와 Dashboard 운영 |
| [Roadmap](docs/ROADMAP.md) | 현재 상태, 다음 초점, Delivery Profile 방향 |
| [Codex/GPT Adapter](docs/adapters/codex-gpt/README.md) | Codex용 AGENTS, repo-local skill, custom agent, runner 연결 기준 |
| [Gemini/Antigravity Adapter](docs/adapters/gemini/README_GEMINI.md) | Agy/Gemini Orchestrator, Workspace branch, structured output, native delegation 기준 |
| [Gate Execution Checklist](docs/core/GATE_EXECUTION_CHECKLIST.md) | 모든 runner가 공통으로 따르는 Gate 실행/승인/위임 경계 |
| [Codex Custom Agent Strategy](docs/reference/CODEX-CUSTOM-AGENT-STRATEGY.md) | `.codex/agents` 기반 보조 에이전트 정의와 native/fallback 보고 기준 |
| [Tech Stack Baselines](docs/core/TECH_STACK_BASELINES.md) | Spring Boot, Spring Security, React, Next.js, Vue.js, FastAPI 기본 개발 규칙 |
| [Contributing](CONTRIBUTING.md) | 공개 기여 시 권리, 회사/고객 정보 제외, PR 기준 |

## 주의

이 프로젝트는 아직 실험적입니다. 모든 프로젝트에 맞는 무거운 프로세스를 강제하려는 도구가 아니라, 감리와 장기 유지보수가 필요한 프로젝트에서 AI 에이전트가 길을 잃지 않게 만드는 작업대에 가깝습니다.

Vulcan-Anvil Ex는 개인이 시작하고 운영하는 오픈소스 프로젝트이며, 특정 회사·고객·조직의 공식 산출물이 아닙니다.
이 저장소에는 회사 또는 고객의 비공개 코드, 문서, 정보가 포함되어 있지 않습니다.
