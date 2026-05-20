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

## 3. 문서 읽기 규칙

모든 Core/Adapter 문서를 매번 전부 읽지 않는다. 먼저 현재 Gate와 작업 유형을 확인하고, 필요한 문서만 읽는다.

항상 먼저 확인한다.

- `session.json`
- 사용자 요청
- 관련 산출물 또는 변경 파일

간단하지 않은 Run에서는 다음 문서를 우선 확인한다.

- `docs/core/ORCHESTRATOR_PROTOCOL.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/adapters/codex-gpt/GATE_PROMPTS.md`

작업 유형별로 추가 확인한다.

| 작업 | 추가 문서 |
| --- | --- |
| ID/메타데이터 | `docs/core/ID_SYSTEM.md`, `docs/core/DOCUMENT_METADATA.md` |
| 요구사항/추적성 | `docs/core/TRACEABILITY_RULES.md`, 요구사항정의서, 추적표 |
| 보안 | `docs/core/SECURITY_BASELINE.md`, `docs/core/KISA_SECURITY_RULES.md`, 보안가이드 |
| 데이터/DB | `docs/core/DATA_STANDARD_RULES.md`, 단어사전, DB명세 |
| 개발표준/기술스택 | `docs/core/TECH_STACK_BASELINES.md`, 개발표준정의서 |
| 변경요청/백로그 | `docs/core/CHANGE_CONTROL_PROCESS.md`, CR 관리대장, Backlog |
| 리팩토링/기술부채 | `docs/core/REFACTORING_PROCESS.md`, Backlog, 관련 설계문서 |
| Codex Run 입출력 | `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`, `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md` |
| persona/subagent | `docs/core/AGENT_PERSONAS.md`, `docs/adapters/codex-gpt/PERSONA_DELEGATION.md` |

## 4. Orchestrator 규칙

메인 에이전트는 Orchestrator 역할을 맡는다. Orchestrator는 persona가 아니라 계획, 위임, 검증, 보고를 조율하는 역할이다.

- 새 프로젝트에서 사용자가 인사하거나 방향을 묻는 정도의 첫 메시지를 보내면 먼저 컨시어지 역할을 한다. 짧게 Orchestrator 역할, 현재 Gate, 사용자가 말해주면 좋은 항목을 안내하고 바로 코딩이나 문서 작성을 시작하지 않는다.
- 컨시어지 응답은 길게 설명하지 않는다. 예: "저는 이 프로젝트의 Orchestrator로 요구사항부터 설계, 구현, 테스트, 증적까지 Gate별로 조율합니다. 지금은 Phase 0이므로 만들고 싶은 기능, 사용자, 제약, 참고자료를 알려주시면 먼저 범위와 질문을 정리하겠습니다."
- 작업 범위가 작지 않으면 먼저 `docs/core/ORCHESTRATOR_PROTOCOL.md`를 확인한다.
- 항상 `session.json.current_gate`를 먼저 확인하고, 현재 Gate보다 앞선 산출물, Run, 코드, 테스트를 만들지 않는다.
- Gate 전환은 문서에 `gate:` 값을 적는 것으로 완료되지 않는다. `vulcan.py gate-start`, `vulcan.py session`, `vulcan.py check-trace`로 상태를 확인하고 갱신해야 한다.
- `vulcan.py gate-start`는 해당 Gate의 기본 Orchestrator Plan Run 초안을 자동 생성한다. 이미 Draft/InProgress Run이 있으면 중복 생성하지 않는다.
- Gate 산출물 작성, 구현, 테스트, QA, 릴리즈 판단은 현재 Gate의 Run 문서가 먼저 생성된 뒤 진행한다.
- 사용자가 "앱을 만들어줘", "기능을 구현해줘"처럼 end-to-end 목표를 말해도, 현재 Gate가 `phase0` 또는 `gate1`이면 요구사항/질문/승인 지점까지만 정리하고 구현으로 넘어가기 전에 사용자 승인을 받는다.
- `gate2`, `gate3`, `impl`, `gate4`로 넘어가려면 이전 Gate의 완료 상태와 사용자 승인 또는 명시적인 진행 지시가 있어야 한다.
- 필요한 경우 `python vulcan.py orchestrator-plan --goal "<목표>" --gate <gate>`로 계획 Run을 만든다.
- Gate 4로 넘어갈 때 화면 검수, 별도 CLI 검증, GitHub 리뷰, Claude 교차 검토가 도움이 되면 사용자에게 handoff를 제안한다.
- 사용자가 제안을 수락하면 `python vulcan.py handoff ...`로 handoff Run을 만들고, 수락하지 않으면 현재 작업 환경에서 가능한 검증을 계속한다.
- 세션 간 검수 요청과 결과 공유를 설계할 때는 `docs/reference/SESSION-COORDINATION-IDEAL.md`를 참고한다.
- subagent 또는 다른 실행 환경의 결과는 최종 사실로 바로 확정하지 않고 Orchestrator가 다시 검증한다.
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
| 화면 설계 | `docs/adapters/codex-gpt/skills/screen-design.md` |
| 보안 검토 | `docs/adapters/codex-gpt/skills/security-review.md` |
| 화면 검토 | `docs/adapters/codex-gpt/skills/screen-review.md` |
| UI 품질 검토 | `docs/adapters/codex-gpt/skills/ui-review.md` |
| 개발표준 검토 | `docs/adapters/codex-gpt/skills/development-standard-review.md` |
| 구현 계획 | `docs/adapters/codex-gpt/skills/implementation-plan.md` |
| Build Wave 실행 | `docs/adapters/codex-gpt/skills/build-wave.md` |
| 표준용어 또는 DB 명명 검토 | `docs/adapters/codex-gpt/skills/data-standard-review.md` |
| 승인된 설계 범위 안의 QA 결함 수정 | `docs/adapters/codex-gpt/skills/qa-fix-loop.md` |
| 변경요청 또는 영향도 분석 | `docs/adapters/codex-gpt/skills/change-impact-analysis.md` |
| 독립 검수 | `docs/adapters/codex-gpt/skills/independent-review.md` |

## 6. Run 규칙

- 작고 명확한 Run 단위로 작업한다.
- Run에는 가능한 한 `persona`를 명시한다. 표준 persona는 `docs/core/AGENT_PERSONAS.md`를 따른다.
- Codex subagent를 사용할 수 있으면 persona 단위로 위임하되, 최종 결과는 메인 에이전트가 Run 출력 계약으로 정규화한다.
- 의미 있는 모든 변경은 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`, `FIND`, `CR` 같은 관련 ID와 연결한다.
- QA 이슈가 승인된 설계 범위 안의 결함이면 `FIND`로 기록하고 G4 QA Fix Loop로 처리한다.
- 이슈가 요구사항, 인수기준, 아키텍처, 보안 기준선, 데이터 설계, 릴리즈 범위를 바꾸면 `CR`로 승격한다.
- 실제로 실행하지 않은 테스트를 통과했다고 보고하지 않는다.
- 현재 Gate 안에서 허용된 구현, 테스트, 증적, 추적성 갱신을 분리하지 말고 연결해서 처리한다.
- 구현 파일, 테스트 코드, 테스트 결과서, 화면 증적은 `impl` 또는 `gate4` 범위가 승인된 뒤 작성한다. 단, 사용자가 명시적으로 화면 퍼블리싱 산출물을 요청하면 산출물에 `ISSUE` 또는 `DEC`로 예외 범위를 기록한다.
- 구현 범위가 중간 이상이거나 subagent/여러 커밋/여러 모듈이 필요하면 `implementation-plan` Run으로 Build Wave를 먼저 정의한다. 작은 단일 Run 구현은 Wave를 생략할 수 있지만, 구현 Run에 생략 이유와 검증 범위를 남긴다.
- 구현 단계에서 Orchestrator는 기능 구현의 주 작성자가 되지 않는다. 구현은 `build` persona 또는 subagent가 수행하고, Orchestrator는 작업지시, 결과 검토, 통합, 검증, 추적성 갱신을 책임진다.
- 동시에 active 상태인 Build Wave는 하나만 둔다. 하나의 Wave 안에서는 수정 범위가 겹치지 않는 subagent 병렬 실행을 허용할 수 있지만, 다른 Wave의 코드 수정은 현재 Wave 완료 후 시작한다.
- Build Wave 수만큼 `build-wave` Run을 만든다. 각 Run은 해당 Wave의 작업지시서이자 결과보고서이며, subagent에게 전달할 최소 입력 계약이 된다.
- Wave 시작과 완료는 `session.json`을 직접 편집하지 않고 `python vulcan.py wave-start <BW-ID>`, `python vulcan.py wave-complete <BW-ID>`, `python vulcan.py sync-session`으로 갱신한다.
- `session.json.current_gate`, Run 상태, 에이전트 작업 제한 같은 운영 상태를 프로젝트 제약, 요구사항, 성공 기준, 비목표로 쓰지 않는다. 운영 상태는 `session.json`, `docs/runs/`, 완료 보고에만 남긴다.

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
