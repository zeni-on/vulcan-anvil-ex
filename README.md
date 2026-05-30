# Vulcan-Anvil Ex

> 사람은 목표와 승인 기준을 제시하고, AI 에이전트는 문서·Gate·검증 체계 안에서 요구사항부터 코드와 증적까지 이어간다.

Vulcan-Anvil Ex는 AI 에이전트가 장기 프로젝트에서 길을 잃지 않도록 돕는 AI 협업 개발 운영 프레임워크입니다.

사용자는 "무엇을 만들고 싶은지"와 중요한 제약을 말하고, 메인 에이전트인 Orchestrator가 요구사항, 설계, 구현, 테스트, 증적 수집을 단계별로 조율합니다. `vulcan.py`는 그 과정에서 LLM이 놓치기 쉬운 ID 체계, Run 기록, 추적성, Gate 전환 규칙을 프로그램으로 점검합니다.

에이전트가 코딩하고, Vulcan-Anvil이 그 일을 설명 가능하게 만듭니다.

## 한눈에 보기

- **사람/사용자**: 목표, 제약, 승인, 판단이 필요한 결정을 제공한다.
- **Orchestrator**: 사용자와 대화하며 계획을 세우고, 필요한 persona/subagent에 일을 나누고, 결과를 검증한다.
- **문서**: 요구사항, 기능, 화면, 프로그램, DB, 보안, 테스트, 증적을 ID로 연결한다.
- **코드**: 승인된 문서와 추적 규칙을 기준으로 에이전트가 작성한다.
- **검증**: 테스트, 화면 증적, Run 기록, 추적성 검사를 통해 다음 Gate로 넘어갈 수 있는지 확인한다.
- **Adapter**: Codex, Claude 같은 런타임 차이를 흡수한다.
- **Dashboard**: Gate, 문서, Run, 통계, 최근 커밋을 한 화면에서 확인한다.

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
python vulcan.py init ../my-project "My Project"
cd ../my-project
```

원격 저장소와 함께 시작하려면 `--remote`를 추가합니다.

```powershell
python vulcan.py init ../my-project "My Project" --remote https://github.com/<owner>/my-project.git
```

이후 프로젝트 폴더를 Codex 또는 Claude에서 열고 목표를 말합니다.

```text
로그인과 게시글 작성 기능이 있는 게시판 샘플을 만들고 싶어.
```

자세한 시작 방법은 [Getting Started](docs/GETTING_STARTED.md)를 참고합니다.

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

개념 설명은 [Concepts](docs/CONCEPTS.md)를 참고합니다.

## 현재 상태

**Experimental - v0.4.1**

`0.4.1`은 `0.4.0`의 trace-context, staged QA, release-pr 흐름을 유지하면서 worker soft timeout, Agy transcript fallback, Run/Wave 이슈 가드를 보강한 안정화 패치입니다. 구현은 `workflow.integration_branch` 통합 브랜치(기본값 `dev`)에서 진행하고, Gate 4는 `QA-000`이 준비한 QA workspace를 `QA-001`~`QA-003`이 재사용하는 흐름을 기준으로 합니다.

아직 제품화된 안정 버전은 아니며, 실제 프로젝트 적용 결과에 따라 문서 체계와 CLI 명령은 계속 조정될 수 있습니다.

릴리즈별 변경사항은 [CHANGELOG.md](CHANGELOG.md)를 기준으로 확인합니다.

## 문서

| 문서 | 내용 |
| --- | --- |
| [Getting Started](docs/GETTING_STARTED.md) | 초기화, 원격 저장소, 프로젝트 시작, 주요 명령 |
| [Concepts](docs/CONCEPTS.md) | 이름의 의미, Orchestrator, Gate, Backlog, Build Wave, Adapter |
| [Upgrade And Dashboard](docs/UPGRADE_AND_DASHBOARD.md) | 기존 프로젝트 업그레이드와 Dashboard 운영 |
| [Roadmap](docs/ROADMAP.md) | 현재 상태, 다음 초점, Delivery Profile 방향 |
| [Tech Stack Baselines](docs/core/TECH_STACK_BASELINES.md) | Spring Boot, Spring Security, React, Next.js, Vue.js, FastAPI 기본 개발 규칙 |
| [Contributing](CONTRIBUTING.md) | 공개 기여 시 권리, 회사/고객 정보 제외, PR 기준 |

## 주의

이 프로젝트는 아직 실험적입니다. 모든 프로젝트에 맞는 무거운 프로세스를 강제하려는 도구가 아니라, 감리와 장기 유지보수가 필요한 프로젝트에서 AI 에이전트가 길을 잃지 않게 만드는 작업대에 가깝습니다.

Vulcan-Anvil Ex는 개인이 시작하고 운영하는 오픈소스 프로젝트이며, 특정 회사·고객·조직의 공식 산출물이 아닙니다.
이 저장소에는 회사 또는 고객의 비공개 코드, 문서, 정보가 포함되어 있지 않습니다.
