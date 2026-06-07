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

런타임의 전역 메모리, 과거 세션 요약, 다른 샘플 프로젝트 기억은 현재 프로젝트의 사실 또는 규칙으로 사용하지 않는다. 메모리가 자동으로 주입되거나 검색되더라도, 현재 작업의 근거는 반드시 이 저장소의 `session.json`, `AGENTS.md`, `docs/core/`, 현재 Gate 산출물, 현재 Run 문서, 사용자의 최신 지시에서 확인한다.

항상 먼저 확인한다.

- `session.json`
- 사용자 요청
- 관련 산출물 또는 변경 파일

간단하지 않은 Run에서는 다음 문서를 우선 확인한다.

- `docs/core/ORCHESTRATOR_PROTOCOL.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/GATE_EXECUTION_CHECKLIST.md`
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
| Run 입력/출력 | `docs/core/RUN_INPUT_CONTRACT.md`, `docs/core/RUN_OUTPUT_CONTRACT.md` |
| Codex worker model/effort 정책 | `docs/core/CODEX_MODEL_POLICY.md`, `docs/core/INDEPENDENT_EXECUTION_PROCESS.md` |
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
- 기본 audit workflow에서 Phase 0~Gate 3 문서화는 `main`에서 진행하고, `impl` 진입 후에는 `python vulcan.py branch-start impl`로 `vulcan.config.json.workflow.integration_branch`(기본 `dev`)를 시작한다.
- Build Wave, worker 구현, Gate 4 QA는 통합 브랜치에서 진행한다. `main`은 초기화와 승인된 릴리즈 기준선이며, Gate 5 승인 후 통합 브랜치를 `main`으로 반영한다.
- 현재 브랜치/정책이 헷갈리면 `python vulcan.py branch-status`로 확인한다.
- 필요한 경우 `python vulcan.py orchestrator-plan --goal "<목표>" --gate <gate>`로 계획 Run을 만든다.
- Gate 4로 넘어갈 때 화면 검수, 별도 CLI 검증, GitHub 리뷰, Claude 교차 검토가 도움이 되면 사용자에게 handoff를 제안한다.
- 사용자가 제안을 수락하면 `python vulcan.py handoff ...`로 handoff Run을 만들고, 수락하지 않으면 현재 작업 환경에서 가능한 검증을 계속한다.
- 세션 간 검수 요청과 결과 공유를 설계할 때는 `docs/reference/SESSION-COORDINATION-IDEAL.md`를 참고한다.
- subagent 또는 다른 실행 환경의 결과는 최종 사실로 바로 확정하지 않고 Orchestrator가 다시 검증한다.
- 구현자가 자기 구현을 최종 승인하지 않도록 review persona 또는 별도 환경 검수를 둔다.

## 5. Skill 카드

Codex/GPT에서 사용하는 skill은 두 층으로 나뉜다.

첫째, Codex 런타임이 발견할 수 있는 repo-local skill은 다음 위치에 둔다.

```text
.agents/skills/
```

이 skill은 항상 로드되는 지침이 아니다. 작업이 description과 맞거나 사용자가 명시적으로 호출할 때 Codex가 읽는 절차 카드다.
Vulcan Gate, Run, 구현, QA, 릴리즈 작업에서는 관련 repo-local skill을 먼저 확인한다.

| 작업 | Repo-local Skill |
| --- | --- |
| Gate/Run/worker/승인 라우팅 | `.agents/skills/vulcan-orchestrator/SKILL.md` |
| Gate 2 설계 | `.agents/skills/vulcan-design/SKILL.md` |
| 구현 Build Wave | `.agents/skills/vulcan-impl-wave/SKILL.md` |
| Gate 4 QA | `.agents/skills/vulcan-qa/SKILL.md` |
| Gate 5 릴리즈 | `.agents/skills/vulcan-release/SKILL.md` |

둘째, Codex custom agent 정의는 다음 위치에 둔다.

```text
.codex/agents/
```

이 파일들은 메인 Orchestrator가 명시적으로 호출할 수 있는 보조 에이전트 정의다.
기본 용도는 추적성 탐색, Run 초안 검토, 계약 검토, QA 증적 해석 같은 읽기 중심 보조 작업이다.
custom agent 결과는 후보 의견이며, Gate 전환, session 갱신, 최종 승인, 공식 구현/QA 실행 판단은 메인 Orchestrator가 다시 검증한다.
Codex custom agent는 `.codex/agents/*.toml`의 `name`으로 식별된다. 메인 Orchestrator는 프롬프트에서 custom agent 이름을 명시해 Codex가 해당 agent를 선택하게 한다.
현재 surface의 내부 tool schema가 `agent_type` 같은 필드를 노출한다고 가정하지 않는다.
Codex가 custom agent name을 직접 선택하지 못하면, built-in/default subagent에 해당 TOML 내용을 운영 계약으로 주입할 수 있다.
이 fallback에서는 TOML의 model/effort가 자동 적용되었다고 보고하지 않고, 실제 적용 여부를 `explicit-tool-override`, `inherited-parent`, `unknown` 중 하나로 구분한다.

| 작업 | Codex Custom Agent |
| --- | --- |
| 관련 ID와 source document 후보 탐색 | `.codex/agents/trace-scout.toml` |
| Run 입력 계약/작업지시서 검토 | `.codex/agents/run-drafter.toml` |
| Program/API/DB/UI 계약 정합성 검토 | `.codex/agents/contract-reviewer.toml` |
| QA 로그/증적/전사 해석 | `.codex/agents/qa-reader.toml` |

셋째, Run 문서와 adapter가 참조하는 내부 작업 카드는 다음 위치에 있다.

```text
docs/adapters/codex-gpt/skills/
```

이 문서들은 Claude `.claude/skills` 플러그인이 아니며, Codex repo-local skill과도 목적이 다르다. Run 입력 계약의 `skill` 값과 adapter 문서가 참조하는 내부 절차 카드로 사용한다.

| 작업 | Skill |
| --- | --- |
| 추적성 검토 | `docs/adapters/codex-gpt/skills/traceability-review.md` |
| 화면 설계 | `docs/adapters/codex-gpt/skills/screen-design.md` |
| 보안 검토 | `docs/adapters/codex-gpt/skills/security-review.md` |
| 화면 검토 | `docs/adapters/codex-gpt/skills/screen-review.md` |
| UI 품질 검토 | `docs/adapters/codex-gpt/skills/ui-review.md` |
| 개발표준 검토 | `docs/adapters/codex-gpt/skills/development-standard-review.md` |
| 구현 계획 | `docs/adapters/codex-gpt/skills/implementation-plan.md` |
| 구현 전 계약 뼈대 생성 | `docs/adapters/codex-gpt/skills/implementation-scaffold.md` |
| Build Wave 실행 | `docs/adapters/codex-gpt/skills/build-wave.md` |
| 표준용어 또는 DB 명명 검토 | `docs/adapters/codex-gpt/skills/data-standard-review.md` |
| Gate 4 QA 실행 및 증적 수집 | `docs/adapters/codex-gpt/skills/qa-execution.md` |
| 승인된 설계 범위 안의 QA 결함 수정 | `docs/adapters/codex-gpt/skills/qa-fix-loop.md` |
| 변경요청 또는 영향도 분석 | `docs/adapters/codex-gpt/skills/change-impact-analysis.md` |
| 독립 검수 | `docs/adapters/codex-gpt/skills/independent-review.md` |

## 6. Run 규칙

- 작고 명확한 Run 단위로 작업한다.
- PoC profile에서는 Run 문서를 기본 필수 산출물로 보지 않는다. 외부 CLI worker, 독립 검수, 긴 작업 위임, 재현 가능한 실험 기록이 필요한 경우에만 compact Run을 만든다.
- PoC profile에서 subagent만으로 처리한 짧은 실험은 Gate 산출물 또는 결과 요약에 남기고 별도 Run을 생략할 수 있다.
- PoC profile의 `TBD`, `미정`, `확정필요`는 사유와 후속 판단 시점이 있으면 경고/판단 항목으로 남길 수 있다. 단, 목표, 성공 기준, 실제 실행 결과, 실행하지 않은 테스트의 Pass는 `TBD` 또는 추정으로 대체하지 않는다.
- Run에는 가능한 한 `persona`를 명시한다. 표준 persona는 `docs/core/AGENT_PERSONAS.md`를 따른다.
- Codex subagent를 사용할 수 있으면 persona 단위로 위임하되, 최종 결과는 메인 에이전트가 Run 출력 계약으로 정규화한다.
- subagent/thread/native branch agent를 사용했으면 외부 CLI runner 수준의 `Run Execution Record`가 없더라도 현재 Run 또는 결과 요약에 `delegation_records`를 남긴다. 최소 항목은 위임 대상, 작업 범위, 변경 파일, 결과 요약, Orchestrator 재검증 명령이다.
- 외부 CLI runner(`agent-run`, `run-exec`)를 사용한 경우에는 기존처럼 `Run Execution Record`, `_exec` 로그, timeout/watchdog, worktree/branch 정보를 남긴다.
- 의미 있는 모든 변경은 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`, `FIND`, `CR` 같은 관련 ID와 연결한다.
- QA 이슈가 승인된 설계 범위 안의 결함이면 `FIND`로 기록하고 G4 QA Fix Loop로 처리한다.
- 이슈가 요구사항, 인수기준, 아키텍처, 보안 기준선, 데이터 설계, 릴리즈 범위를 바꾸면 `CR`로 승격한다.
- 실제로 실행하지 않은 테스트를 통과했다고 보고하지 않는다.
- 현재 Gate 안에서 허용된 구현, 테스트, 증적, 추적성 갱신을 분리하지 말고 연결해서 처리한다.
- 구현 파일, 테스트 코드, 테스트 결과서, 화면 증적은 `impl` 또는 `gate4` 범위가 승인된 뒤 작성한다. 단, 사용자가 명시적으로 화면 퍼블리싱 산출물을 요청하면 산출물에 `ISSUE` 또는 `DEC`로 예외 범위를 기록한다.
- 구현 단계에서 Orchestrator는 기능 구현의 주 작성자가 되지 않는다. 작은 기능, 단일 파일, 단일 테스트 변경이라도 실제 코드/테스트/UI/API 구현은 `build` persona의 native worker(subagent/thread/native branch agent)에게 위임하는 것을 기본값으로 한다.
- `agent-run --mode work`와 `run-exec`는 기본 구현 경로가 아니다. 별도 CLI 프로세스, worktree 격리, watchdog/timeout 증적, cross-runner 실행이 필요할 때 선택하는 옵션이다.
- Orchestrator가 직접 수행할 수 있는 구현 관련 작업은 작업지시서 작성, worker 결과 통합, 충돌 해결에 필요한 최소 연결 수정, 문서/추적표/session 갱신, 검증 명령 실행으로 제한한다.
- subagent/worker를 사용할 수 없거나 긴급한 1~2줄 연결 수정처럼 직접 수정이 불가피하면 Run에 `orchestrator_direct_edit_reason`, 수정 범위, 실행 검증, 후속 검수 필요 여부를 남긴다.
- 사용자가 "worker를 사용하라"고 명시하지 않았다는 점은 Orchestrator 직접 구현 사유가 아니다. 사용자가 구현 진행을 승인하면 Orchestrator는 별도 요청이 없어도 native worker 위임을 기본 절차로 적용한다.
- Orchestrator 직접 구현 예외는 worker/subagent/thread 실행 불가, worker 결과 통합 중 충돌 해결에 필요한 최소 수정, 긴급한 1~2줄 연결 수정, 사용자의 명시적 직접 구현 승인에 한해 허용한다.
- 구현 범위가 중간 이상이거나 subagent/thread/여러 커밋/여러 모듈이 필요하면 `implementation-plan` Run으로 Build Wave를 먼저 정의한다. 작은 단일 구현은 Implementation Plan Wave 분할을 생략할 수 있지만, 구현 자체는 native worker에게 위임하고 생략 이유와 검증 범위를 남긴다. 외부 CLI runner가 필요할 때만 `agent-run`/`run-exec`를 선택한다.
- 신규 개발이거나 빌드 가능한 프로젝트 골격/class/interface/method/DTO skeleton이 없으면 feature 구현 Build Wave 전에 `BW-000 implementation-scaffold` Run을 먼저 만든다. 이미 골격이 충분하면 `contract_skeleton.mode: not-required`와 생략 근거를 Implementation Plan 또는 Run에 남긴다.
- 동시에 active 상태인 Build Wave는 하나만 둔다. 한 Wave를 여러 runner에게 나누어 동시에 구현시키지 않는다. backend/frontend처럼 작업지시서가 분리되어야 하면 서로 다른 `build-wave` Run, 보통 서로 다른 `BW-ID`로 나눈 뒤 순차 실행한다.
- Build Wave 수만큼 `build-wave` Run을 만든다. 각 Run은 해당 Wave의 작업지시서이자 결과보고서이며, subagent/worker에게 전달할 최소 입력 계약이 된다.
- Build Wave Run을 만들 때는 관련 ID를 수동으로 넓게 나열하는 대신 가능한 한 상세 `REQ-NNN-NN`, `AC-NNN-NN`, `FUNC`, `PGM`, `API`, `SCR`, `DB`, `SEC`, `UT/IT/UI` 중 대표 seed를 정하고 `python vulcan.py wave-start <BW-ID> --trace-seed <ID>` 또는 `python vulcan.py run-new ... --trace-seed <ID>`를 우선 사용한다.
- `--trace-seed`는 `related_ids`, `target_contracts`, `source_documents.reference_on_demand`를 추적성 그래프에서 추천하는 기능이다. 추천값은 자동 확정이 아니므로 Orchestrator가 `scope.writable`, `target_contracts.interface_contract`, `contract_skeleton`, 검증 명령을 Program Design과 실제 작업 범위 기준으로 확정한 뒤 worker에게 넘긴다.
- Wave 시작과 완료는 `session.json`을 직접 편집하지 않고 `python vulcan.py wave-start <BW-ID>`, `python vulcan.py wave-complete <BW-ID>`, `python vulcan.py sync-session`으로 갱신한다.
- Wave 완료 검증은 해당 Wave의 `target_contracts`와 Gate 3 테스트 설계에 매핑된 테스트까지만 완료 판정한다.
- 전체 사용자 시나리오 E2E, 상태별 화면 증적, QA Pass 판정은 Gate 4에서 수행한다. Wave 완료 보고를 전체 통합 테스트 완료처럼 표현하지 않는다.
- Gate 4에서 Orchestrator는 테스트 실행자와 수정자를 겸하지 않는다. 가능하면 `qa-execution` worker Run으로 테스트 실행, 로그, Playwright 증적, 후보 FIND/CR/ISSUE를 수집하고, 실패가 나오면 즉시 수정하지 않고 사용자와 처리 방향을 협의한다.
- Gate 4 QA는 한 번에 전부 수행하지 않는다. `QA-000` 환경 준비/스모크, `QA-001` 명령 기반 검증, `QA-002` UI/E2E 증적, `QA-003` 결과 정리/판정 후보 순서로 나누며, `QA-000`이 차단되면 후속 QA를 진행하지 않고 사유를 보고한다.
- `QA-000`은 기본적으로 `workflow.integration_branch`의 현재 작업공간을 Gate 4 전체에서 재사용할 QA workspace로 기록한다. QA worktree는 명시적으로 활성화한 경우에만 사용한다. `QA-001`, `QA-002`, `QA-003`은 새 작업공간을 임의로 만들지 않고 `QA-000`이 기록한 같은 공간에서 실행한다.
- QA에서 승인된 설계 범위 안의 결함을 고치기로 결정한 뒤에만 별도 `qa-fix-loop` Run을 만든다. 새 API, 새 메소드, 요구사항/설계 변경이 필요하면 `CR` 후보로 승격한다.
- `qa-fix-loop` Run 파일명에는 `qa-fix-loop`와 대상 `FIND-ID`를 포함하고 `run_type: QAFix`로 작성한다. Orchestrator는 수정 범위, 금지 범위, `scope.writable`, 검증 명령을 확정한 뒤 native worker(subagent/thread/native branch agent)에게 구현 수정을 맡기며, 직접 구현하지 않는다. 외부 CLI 실행 증적이 필요할 때만 `agent-run`/`run-exec`를 선택한다.
- `session.json.current_gate`, Run 상태, 에이전트 작업 제한 같은 운영 상태를 프로젝트 제약, 요구사항, 성공 기준, 비목표로 쓰지 않는다. 운영 상태는 `session.json`, `docs/runs/`, 완료 보고에만 남긴다.

## 7. 참고문서 경계

- `MEMORY.md`, 전역 memory, 과거 rollout summary, 다른 프로젝트의 sample 기록은 보조 힌트일 뿐이다. 요구사항, 범위, Gate 상태, 승인 여부, 구현 대상, 테스트 통과 여부의 근거로 삼지 않는다.
- 메모리 내용과 현재 프로젝트 문서가 다르면 현재 프로젝트 문서를 우선한다. 충돌이 있으면 메모리를 적용하지 말고 `open_issues` 또는 질문으로 남긴다.
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
docs/core/RUN_OUTPUT_CONTRACT.md
```

---

## 9. Vulcan CLI 워크플로우 퀵 레퍼런스 (CLI 실행 전 즉시 참고)

> [!IMPORTANT]
> 에이전트는 명령어를 찾기 위해 `python vulcan.py --help`를 매번 실행하는 탐색 비효율을 줄여야 합니다. 아래의 정해진 표준 명령어 퀵 맵을 즉시 활용하십시오.

### ① Gate 라이프사이클 제어
| 목적 | 실행할 명령어 |
| --- | --- |
| **Gate 시작** | `python vulcan.py gate-start <gate>` (e.g. `phase0`, `gate1`, `gate2`, `gate3`, `impl`, `gate4`, `gate5`) |
| **Gate 완료** | `python vulcan.py session --gate <gate> --status done` (필요 시 `--feature <이름>` 추가) |
| **상태 동기화** | `python vulcan.py sync-session` (Gate 전환 또는 변경 발생 시 원격 push 및 로컬 동기화) |

### ② 에이전트 Run 생성 및 검증
| 목적 | 실행할 명령어 |
| --- | --- |
| **Orchestrator Plan 생성** | `python vulcan.py orchestrator-plan --goal "<목표>" --gate <gate>` |
| **새 작업 Run 생성** | `python vulcan.py run-new --skill <skill> --title "<제목>" --related-ids "<ID들>"` <br>※ *주요 skill: `traceability-review`, `screen-design`, `security-review`, `development-standard-review`, `implementation-plan`, `build-wave`, `qa-execution`, `qa-fix-loop`* |
| **Run 사전검사 (preflight)** | `python vulcan.py run-preflight <run_file_path>` |
| **Run 완료검사 (check)** | `python vulcan.py run-check <run_file_path>` |
| **전체 추적성/정합성 정적 검사** | `python vulcan.py check-trace` |

### ③ 구현 Build Wave 및 QA
| 목적 | 실행할 명령어 |
| --- | --- |
| **통합/작업 브랜치 상태 확인** | `python vulcan.py branch-status` |
| **통합 브랜치 기동 (impl 진입 시)** | `python vulcan.py branch-start impl` |
| **Build Wave 시작** | `python vulcan.py wave-start <BW-ID> --trace-seed <대표ID>` |
| **Build Wave 완료** | `python vulcan.py wave-complete <BW-ID> --status Verified` |
| **결과 통합 및 병합 (Review 후)** | `python vulcan.py run-integrate <run_file_path>` |

### ④ 릴리즈 및 프레임워크 최신화
| 목적 | 실행할 명령어 |
| --- | --- |
| **Release PR 생성 테스트** | `python vulcan.py release-pr --dry-run` |
| **프레임워크 최신화 (도구/템플릿)** | `python vulcan.py upgrade` |

