# Vulcan-Anvil Ex

> AI 에이전트가 요구사항, 설계, 구현, 테스트, 증적을 연결해서 작업하도록 돕는 감리 대응형 개발 프레임워크.

Vulcan-Anvil Ex는 기존 Vulcan-Anvil의 5-Gate 사고방식을 바탕으로, 공공/SI 프로젝트에서 필요한 산출물과 추적성을 에이전트 개발 흐름에 붙이는 실험적 프레임워크입니다.

핵심은 단순합니다.

- 요구사항, 기능, 화면, 프로그램, DB, 보안, 테스트, 증적을 ID로 연결한다.
- Codex, Claude 같은 런타임 차이는 adapter로 흡수한다.
- 메인 에이전트는 Controller 역할을 맡아 계획, 위임, 검증, 보고를 조율한다.
- `vulcan.py`는 LLM이 놓치기 쉬운 규칙을 프로그램으로 점검하고 Run 기록을 만든다.

## Status

**Experimental - v1.6.0**

아직 제품화된 안정 버전이 아니라, 실제 프로젝트 적용을 전제로 빠르게 검증 중인 Ex 버전입니다. 문서 체계와 CLI 명령은 실전 검증 결과에 따라 바뀔 수 있습니다.

## 왜 필요한가

AI 에이전트는 코드를 빠르게 만들 수 있지만, 긴 프로젝트에서는 다음 문제가 반복됩니다.

1. 이전 결정과 설계 근거를 잊는다.
2. 구현은 되었지만 요구사항, 테스트, 증적과 연결되지 않는다.
3. QA 중 발견한 결함과 변경요청을 구분하지 못한다.
4. Codex, Claude, GitHub Review처럼 도구가 바뀌면 작업 규칙도 흩어진다.

Vulcan-Anvil Ex는 이 문제를 문서화된 Core 규칙, Adapter, Run 기록, 추적성 검사로 줄이는 것을 목표로 합니다.

## 핵심 개념

### Core

`docs/core/`는 런타임과 무관한 공통 규칙입니다.

- `ID_SYSTEM.md`: 요구사항, 설계, 테스트, 증적 ID 체계
- `TRACEABILITY_RULES.md`: 요구사항에서 증적까지의 연결 규칙
- `CONTROLLER_PROTOCOL.md`: 메인 에이전트의 계획, 위임, 검증 규칙
- `AGENT_PERSONAS.md`: 단계별 persona와 subagent 위임 기준
- `AGENT_RUN_PROTOCOL.md`: 에이전트 실행 단위인 Run 규칙
- `CHANGE_CONTROL_PROCESS.md`: FIND, CR, ISSUE, 백로그, Gate 재진입 기준
- `REFERENCE_STANDARDS.md`: 보안/데이터 표준 참조 규칙
- `DATA_STANDARD_RULES.md`: 프로젝트 단어사전과 데이터 표준화 규칙

### Controller

Controller는 별도 persona가 아니라 메인 에이전트의 운영 역할입니다.

Controller는 사용자의 요청과 현재 Gate를 보고 다음을 결정합니다.

- 어떤 persona에게 위임할지
- 어떤 Run을 만들지
- 어떤 문서와 코드를 확인할지
- 어떤 검증을 실행할지
- FIND, CR, ISSUE 중 무엇으로 분류할지
- Gate 4에서 별도 handoff를 제안할지

Gate 4에서 `desktop handoff`는 강제하지 않습니다. 화면 검수나 별도 환경 검증이 도움이 될 때 Controller가 사용자에게 제안하고, 사용자가 수락하면 `vulcan.py handoff`로 별도 Run을 만듭니다.

### Adapter

`docs/adapters/`는 런타임별 작업 방식을 담습니다.

- `codex-gpt/`: Codex/GPT용 AGENTS, Run 계약, skill 카드, persona 위임 규칙
- `claude/`: Claude 런타임의 agent/skill 구조와 Core persona 매핑

Codex는 `AGENTS.md`를 진입 문서로 사용하고, Claude는 `CLAUDE.md` 계열 문서를 읽는 구조를 전제로 합니다. Core 규칙은 양쪽 모두에서 공유합니다.

### Run

Run은 에이전트가 수행한 작업 단위입니다.

일반 프로젝트에서는 `docs/runs/`, 샘플처럼 독립 폴더 안에서 관리되는 경우에는 `runs/`에 기록할 수 있습니다. `vulcan.py`는 두 위치를 자동 감지합니다.

Run 문서는 다음을 남깁니다.

- `run_id`
- `adapter`
- `gate`
- `persona`
- `skill`
- `related_ids`
- `verification_results`
- `evidence`
- `traceability_updates`
- `findings`
- `change_requests`
- `open_issues`

## 빠른 시작

### 1. 새 프로젝트 초기화

```powershell
python vulcan.py init ../my-project "My Project"
```

초기화하면 Core 문서, 템플릿, adapter 문서, 공개 표준 참고자료, `AGENTS.md`가 프로젝트에 복사됩니다.

### 2. 프로젝트에서 작업

```powershell
cd ../my-project
```

Codex를 사용한다면 `AGENTS.md`를 기준으로 작업합니다. Claude를 사용한다면 Claude adapter 문서와 Core 규칙을 함께 참조합니다.

### 3. Controller 계획 생성

```powershell
python vulcan.py controller-plan ^
  --goal "로그인 게시판 Gate 4 검수 계획" ^
  --gate gate4 ^
  --persona review ^
  --related-ids REQ-001,UI-001
```

### 4. Run 생성

```powershell
python vulcan.py run-new ^
  --gate gate4 ^
  --persona review ^
  --skill traceability-review ^
  --title "로그인 게시판 추적성 검토" ^
  --related-ids REQ-001,REQ-002
```

### 5. Run 검사

```powershell
python vulcan.py run-check docs/runs/RUN-001_login-traceability_v0.1.md
```

### 6. Gate 추적성 검사

```powershell
python vulcan.py check-trace
```

## 주요 CLI 명령

| 명령 | 설명 |
| --- | --- |
| `init` | 새 프로젝트에 Vulcan-Anvil Ex 문서와 템플릿을 주입 |
| `controller-plan` | Controller 실행 계획 Run 생성 |
| `run-new` | persona/skill 기반 Run 초안 생성 |
| `run-check` | Run 문서 필수 필드와 상태 검사 |
| `handoff` | 다른 실행 환경으로 넘길 검수 Run 생성 |
| `check-trace` | Gate별 추적성 검사 |
| `rollback` | 특정 Gate부터 재진입 |
| `backlog` | 백로그 추가, 조회, 완료, 반려 |
| `export` | 대시보드용 snapshot 생성 |
| `upgrade` | 기존 프로젝트에 최신 framework 문서 반영 |
| `version` | 현재 Vulcan-Anvil Ex 버전 확인 |

## 생성되는 주요 구조

```text
my-project/
├── AGENTS.md
├── session.json
├── vulcan.py
└── docs/
    ├── core/
    ├── templates/
    ├── adapters/
    ├── seed-docs/
    ├── ref-docs/
    └── runs/
```

`docs/ref-docs/`는 민감한 프로젝트 참고문서를 둘 수 있는 영역이며 기본적으로 Git에서 제외됩니다.

`docs/seed-docs/`는 공개 표준 문서를 프로젝트에 주입하는 영역입니다. 현재는 공공데이터 공통표준과 소프트웨어 개발보안 관련 공개 문서를 기준 자료로 둡니다.

## 문서 템플릿

`docs/templates/`에는 다음 산출물 템플릿이 있습니다.

- 요구사항정의서
- 요구사항추적표
- 기능명세서
- 프로그램명세서
- 화면설계서
- DB명세서
- 개발표준서
- 테스트케이스
- QA Finding
- 변경요청
- 프로젝트 단어사전

템플릿은 Markdown으로 관리하지만, 향후 감리 제출용으로 Excel, Word, HWPX 등 일반 문서 형식으로 변환하는 흐름을 붙일 수 있도록 설계합니다.

## 샘플 프로젝트

`docs/examples/board-with-login/`에는 로그인 기능이 있는 게시판 샘플이 들어 있습니다.

샘플에는 다음이 포함됩니다.

- 요구사항, 기능, 프로그램, 화면, DB, 테스트, UI 증적 문서
- FastAPI 기반 샘플 앱
- 단위/통합/UI 라우트 테스트
- Controller 기반 Gate 4 검수 Run 예시

검증 예시:

```powershell
cd docs/examples/board-with-login/sample-app
python -m pytest -p no:cacheprovider tests
```

## 보안과 데이터 표준

설계와 구현 단계에서는 다음을 함께 봅니다.

- 소프트웨어 개발보안 가이드
- 소프트웨어 보안약점 진단가이드
- 공공데이터 공통표준
- 프로젝트 단어사전

보안 항목은 `SEC-ID`로 요구사항, 프로그램, 화면, 테스트와 연결합니다. 데이터 항목은 공공데이터 공통표준을 먼저 확인하고, 없으면 프로젝트 단어사전에 추가하는 흐름을 기본으로 합니다.

## 세션 협업 모델

세션 간 실시간 통신은 Core 전제 조건이 아닙니다.

대신 다음 파일을 공유 상태로 사용합니다.

- `session.json`
- `docs/runs/`
- 향후 `docs/reviews/`
- 증적 파일
- 백로그 문서

이상적인 세션 협업 모델은 `docs/reference/SESSION-COORDINATION-IDEAL.md`에 정리되어 있습니다. 실시간 브로드캐스트나 watcher는 향후 확장 옵션입니다.

## 현재 방향

Vulcan-Anvil Ex의 다음 초점은 다음입니다.

- 실제 프로젝트 생성 후 Core/Adapter 문서 적용성 검증
- Review Queue 도입 여부 판단
- Codex와 Claude adapter의 실행 흐름 정교화
- Dashboard가 Run, 추적표, 문서 상태를 읽도록 확장
- 감리 제출용 문서 변환 흐름 검토

## 주의

이 프로젝트는 아직 실험적입니다. 모든 프로젝트에 맞는 무거운 프로세스를 강제하려는 도구가 아니라, 감리와 장기 유지보수가 필요한 프로젝트에서 AI 에이전트가 길을 잃지 않게 만드는 작업대에 가깝습니다.
