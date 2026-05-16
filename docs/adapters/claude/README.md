# Claude Adapter

> 상태: v0.2.1
> 목적: Vulcan-Anvil Ex Core 산출물과 Agent Run Protocol을 Claude Code 기반 개발 실행 흐름에 연결한다.

## 1. 범위

Claude Adapter는 사람이 Claude Code CLI 또는 IDE 확장과 함께 개발할 때 필요한 입력 계약, 실행 지침, 출력 정규화 방식을 정의한다.

`0.2.1` 기준 Claude Adapter는 Core persona, Build Wave, SW Architecture, DBML ERD, 변경관리/릴리즈 산출물, 기술스택 베이스라인, 리팩토링 프로세스 흐름을 Claude의 `.claude/agents`와 `.claude/skills` 구조에 연결한다.

이 Adapter는 다음 작업을 지원한다.

- 요구사항/설계 문서 읽기
- Gate별 작업 범위 선정
- 구현 및 테스트 실행
- 화면 캡처와 결과 증적 생성
- 요구사항추적표 갱신
- subagent 위임 및 조율

## 2. Claude 실행 특징

Claude Adapter는 다음 Claude 고유 특징을 고려한다.

- **진입점**: 루트 `.claude/CLAUDE.md`가 Claude의 기본 진입 문서다
- **subagent**: `.claude/agents/*.md` 파일명으로 subagent를 위임할 수 있다. 파일명 = persona명 (1:1)
- **skills**: `.claude/skills/*/skill.md`가 런타임 플러그인으로 자동 로드된다
- **tools**: Bash, Read, Write, Edit, Grep, Glob 등 내장 도구를 직접 실행할 수 있다
- **브라우저**: Playwright 또는 Claude-in-Chrome MCP로 UI 캡처가 가능하다
- **대화 컨텍스트**: 이전 대화 내용을 Orchestrator가 유지한다

## 3. Codex/GPT Adapter와의 차이

| 항목 | Codex/GPT | Claude |
| --- | --- | --- |
| 진입 문서 | `AGENTS.md` | `.claude/CLAUDE.md` |
| subagent 위임 | 프롬프트 주입 | `.claude/agents/*.md` |
| 스킬 | `docs/adapters/codex-gpt/skills/` 수동 참조 | `.claude/skills/` 자동 로드 |
| 도구 실행 | 텍스트 명령 출력 | Bash tool 직접 실행 |
| 컨텍스트 | Run 단위 주입 | 대화 누적 |
| UI 캡처 | 명령 출력 | Playwright MCP / Claude-in-Chrome |

## 4. 기본 실행 순서

```text
1. CLAUDE.md → session.json 확인
2. persona 판단 → PERSONA_MAPPING.md에서 agent 선택
3. Run 입력 계약(RUN_INPUT_CONTRACT.md) 구성
4. subagent 위임 또는 Orchestrator 직접 실행
5. 테스트/린트/캡처 실행
6. 추적표와 결과서 갱신
7. Run 출력 계약(RUN_OUTPUT_CONTRACT.md) 형식으로 완료 보고
```

## 5. 현재 사용 가능한 문서

| 문서 | 용도 |
| --- | --- |
| `PERSONA_MAPPING.md` | Claude agent 파일명과 Ex persona 1:1 매핑 |
| `RUN_INPUT_CONTRACT.md` | Claude subagent에게 전달할 표준 작업지시서 형식 |
| `RUN_OUTPUT_CONTRACT.md` | Claude 에이전트가 반환해야 하는 표준 완료보고서 형식 |
| `GATE_PROMPTS.md` | Gate별 기본 지침 |
| `LIMITATIONS.md` | Claude Adapter 한계와 승인 필요 상황 |

## 6. 관련 Core 문서

- `docs/core/AGENT_PERSONAS.md` — 표준 persona 정의
- `docs/core/AGENT_RUN_PROTOCOL.md` — Run 단위 실행 규칙
- `docs/core/TRACEABILITY_RULES.md` — 추적성 갱신 규칙
- `docs/core/ORCHESTRATOR_PROTOCOL.md` — Orchestrator 운영 규칙
