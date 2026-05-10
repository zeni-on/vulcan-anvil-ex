# Claude Persona Mapping

> 상태: 초안 v0.1
> 목적: 기존 `.claude/agents/*.md` 파일을 Vulcan-Anvil Ex 표준 persona 체계에 매핑한다.

## 1. 기본 방향

Claude adapter는 기존 Vulcan-Anvil과의 호환성을 위해 `.claude/agents/` 파일명을 유지한다.

다만 Ex Core의 표준 역할명은 `docs/core/AGENT_PERSONAS.md`의 persona를 따른다. 따라서 Claude의 agent 이름은 실행 파일명이고, persona는 작업 계약이다.

## 2. 매핑 표

| Claude agent | Ex persona | 사용 시점 |
| --- | --- | --- |
| `concierge` | `discovery` | 프로젝트 온보딩, 초기 맥락 수집 |
| `analyst` | `discovery` | 현행 코드, API, 의존성 분석 |
| `ba` | `discovery` 또는 `requirements` | P0 분석 또는 G1 요구사항 도출 |
| `sa` | `discovery` 또는 `design` | P0 기술 방향 또는 G2 상위 설계 |
| `estimator` | `discovery` | 규모, 공수, 일정 추정 |
| `pm` | `requirements` | G1 요구사항, 비기능 요구사항, AC 작성 |
| `architect` | `design` | G2 프로그램/아키텍처/API 설계 |
| `dba` | `design` | G2 DB/데이터 설계 |
| `ui-designer` | `design` | G2 화면 흐름과 화면설계 |
| `qa` | `test-design` | G3 테스트 설계 |
| `frontend-dev` | `build` | G4 프론트엔드 구현 |
| `backend-dev` | `build` | G4 백엔드 구현 |
| `ux-reviewer` | `evidence` 또는 `review` | UI 증적 생성, UX 검수 |
| `qa` | `review` | G4 품질/보안/추적성 검토 |

## 3. Orchestrator 규칙

Claude 메인 에이전트는 사용자의 요청을 받으면 먼저 Ex persona를 판단한 뒤, 해당 persona를 수행할 Claude agent를 선택한다.

예:

```text
요청: "로그인 요구사항 정리해줘"
persona: requirements
Claude agent: pm
```

```text
요청: "게시글 작성 API 구현해줘"
persona: build
Claude agent: backend-dev
```

```text
요청: "화면 캡처 증적 만들어줘"
persona: evidence
Claude agent: ux-reviewer
```

## 4. Subagent 위임 규칙

Claude subagent에게 위임할 때는 agent 이름만 전달하지 말고 persona도 함께 전달한다.

```yaml
persona: build
claude_agent: backend-dev
run_id: RUN-003
gate: gate4
related_ids: [REQ-005, PGM-005, UT-007]
```

subagent는 다음 문서를 먼저 확인한다.

- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/adapters/claude/PERSONA_MAPPING.md`
- 해당 `.claude/agents/{agent}.md`

## 5. 이름 변경 정책

기존 `.claude/agents/pm.md`, `frontend-dev.md`, `backend-dev.md` 파일은 당장 삭제하거나 이름을 바꾸지 않는다.

이유:

- 기존 프로젝트와 프롬프트 호환성을 유지해야 한다.
- Claude runtime은 `.claude/agents/` 파일명을 기준으로 subagent를 찾을 수 있다.
- Ex Core는 이미 persona 계약을 별도로 갖고 있으므로 파일명 변경 없이 의미를 교정할 수 있다.

장기적으로는 새 프로젝트에서 다음 별칭 파일을 추가할 수 있다.

| 새 별칭 후보 | 기존 파일 |
| --- | --- |
| `requirements.md` | `pm.md` |
| `build-frontend.md` | `frontend-dev.md` |
| `build-backend.md` | `backend-dev.md` |
| `test-design.md` | `qa.md` |
| `review.md` | `qa.md`, `ux-reviewer.md` |

별칭 추가는 runtime 호환성과 중복 유지 비용을 확인한 뒤 진행한다.
