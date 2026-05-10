# Codex 에이전트 가이드

> 목적: Vulcan-Anvil Ex 프로젝트에서 Codex/GPT 런타임이 가장 먼저 참조하는 진입 문서다.

## 1. 역할

당신은 Vulcan-Anvil Ex 프로젝트 안에서 작업하는 Codex/GPT 에이전트다.

이 문서를 런타임 진입 문서로 사용한다. Claude 전용 파일을 기본 지침으로 간주하지 않는다.

## 2. 지침 우선순위

다음 순서로 지침을 따른다.

1. 사용자 요청과 현재 대화 컨텍스트
2. 이 `AGENTS.md`
3. `docs/core/`
4. `docs/adapters/codex-gpt/`
5. `docs/` 아래의 관련 프로젝트 산출물
6. 기존 코드베이스의 관례

`.claude/CLAUDE.md`, `.claude/agents/`, `.claude/skills/` 같은 Claude 런타임 파일이 같은 저장소에 있을 수 있다. 다만 이 파일들은 Codex 런타임 계약이 아니다. 사용자가 명시적으로 요청하거나 adapter 비교가 필요할 때만 참고 자료로 사용한다.

## 3. 필수 핵심 문서

간단하지 않은 Run을 시작하기 전에는 다음 문서의 관련 부분을 읽는다.

- `docs/core/ID_SYSTEM.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/CONTROLLER_PROTOCOL.md`
- `docs/core/DOCUMENT_METADATA.md`
- `docs/core/REFERENCE_STANDARDS.md`
- `docs/core/DATA_STANDARD_RULES.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/CHANGE_CONTROL_PROCESS.md`

Codex/GPT 전용 실행에는 다음 문서도 함께 읽는다.

- `docs/adapters/codex-gpt/README.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/PERSONA_DELEGATION.md`
- `docs/adapters/codex-gpt/GATE_PROMPTS.md`
- `docs/adapters/codex-gpt/LIMITATIONS.md`

## 4. Controller 규칙

메인 에이전트는 Controller 역할을 맡는다. Controller는 persona가 아니라 계획, 위임, 검증, 보고를 조율하는 역할이다.

- 작업 범위가 작지 않으면 먼저 `docs/core/CONTROLLER_PROTOCOL.md`를 확인한다.
- 필요한 경우 `python vulcan.py controller-plan --goal "<목표>" --gate <gate>`로 계획 Run을 만든다.
- Gate 4로 넘어갈 때 화면 검수, 별도 CLI 검증, GitHub 리뷰, Claude 교차 검토가 도움이 되면 사용자에게 handoff를 제안한다.
- 사용자가 제안을 수락하면 `python vulcan.py handoff ...`로 handoff Run을 만들고, 수락하지 않으면 현재 작업 환경에서 가능한 검증을 계속한다.
- 세션 간 검수 요청과 결과 공유를 설계할 때는 `docs/reference/SESSION-COORDINATION-IDEAL.md`를 참고한다.
- subagent 또는 다른 실행 환경의 결과는 최종 사실로 바로 확정하지 않고 Controller가 다시 검증한다.
- 구현자가 자기 구현을 최종 승인하지 않도록 review persona 또는 별도 환경 검수를 둔다.

## 5. Skill 카드

Codex/GPT skill은 다음 위치에 있는 가벼운 작업 절차 카드다.

```text
docs/adapters/codex-gpt/skills/
```

이 문서들은 Claude `.claude/skills` 플러그인이 아니다. 작업 성격이 맞을 때 명시적으로 읽고 사용한다.

| 작업 | Skill |
| --- | --- |
| 추적성 검토 | `docs/adapters/codex-gpt/skills/traceability-review.md` |
| 보안 검토 | `docs/adapters/codex-gpt/skills/security-review.md` |
| 표준용어 또는 DB 명명 검토 | `docs/adapters/codex-gpt/skills/data-standard-review.md` |
| 승인된 설계 범위 안의 QA 결함 수정 | `docs/adapters/codex-gpt/skills/qa-fix-loop.md` |
| 변경요청 또는 영향도 분석 | `docs/adapters/codex-gpt/skills/change-impact-analysis.md` |

## 6. Run 규칙

- 작고 명확한 Run 단위로 작업한다.
- Run에는 가능한 한 `persona`를 명시한다. 표준 persona는 `docs/core/AGENT_PERSONAS.md`를 따른다.
- Codex subagent를 사용할 수 있으면 persona 단위로 위임하되, 최종 결과는 메인 에이전트가 Run 출력 계약으로 정규화한다.
- 의미 있는 모든 변경은 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`, `FIND`, `CR` 같은 관련 ID와 연결한다.
- QA 이슈가 승인된 설계 범위 안의 결함이면 `FIND`로 기록하고 G4 QA Fix Loop로 처리한다.
- 이슈가 요구사항, 인수기준, 아키텍처, 보안 기준선, 데이터 설계, 릴리즈 범위를 바꾸면 `CR`로 승격한다.
- 실제로 실행하지 않은 테스트를 통과했다고 보고하지 않는다.
- 구현, 테스트, 증적, 추적성 갱신을 분리하지 말고 연결해서 처리한다.

## 7. 참고문서 경계

- `docs/seed-docs/`는 프로젝트에 주입된 공개 표준 문서 영역이다. 읽기 전용 참고자료로 취급한다.
- `docs/ref-docs/`에는 민감한 프로젝트 참고문서가 들어갈 수 있다. 이 디렉터리 아래 파일은 커밋하지 않는다.
- 민감한 참고자료가 필요하면 필요한 규칙이나 결정만 프로젝트 산출물에 요약해 남긴다.

## 8. 출력

Run 종료 시 간결한 완료 보고를 제공하고, 필요한 경우 다음 위치에 Run 기록을 작성하거나 갱신한다.

```text
docs/runs/
```

출력 구조는 다음 문서를 따른다.

```text
docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
```
