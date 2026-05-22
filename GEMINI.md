# Gemini 에이전트 가이드 (GEMINI.md)

> 상태: v0.2 (Gemini 및 Antigravity 에이전트 전용 진입 가이드)
> 목적: Vulcan-Anvil Ex 프로젝트에서 Gemini/Antigravity 런타임이 최초 진입 시 참고할 역할, 지침 우선순위, 오케스트레이터 규칙 및 러너 실행 표준을 정의한다.

---

## 1. 역할

당신은 Vulcan-Anvil Ex 프로젝트 안에서 작업하는 Gemini 및 Antigravity 에이전트다.

이 문서를 런타임 진입 문서로 사용한다. 타 모델 전용 파일(예: Codex/GPT의 `AGENTS.md`, Claude 전용 파일)을 기본 지침으로 간주하지 않고, Gemini 전용인 이 문서를 기준으로 동작한다.

## 2. 지침 우선순위

다음 순서로 지침을 따른다.

1. 사용자 요청과 현재 대화 컨텍스트
2. 이 `GEMINI.md`
3. `docs/core/` (예: [AGENT_RUN_PROTOCOL_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/core/AGENT_RUN_PROTOCOL_GEMINI.md), [RUN_OUTPUT_CONTRACT_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/core/RUN_OUTPUT_CONTRACT_GEMINI.md))
4. `docs/adapters/gemini/`
5. `docs/` 아래의 관련 프로젝트 산출물
6. 기존 코드베이스의 관례

타 에이전트 전용 파일(예: `AGENTS.md`, `.claude/CLAUDE.md`)이 같은 저장소에 있을 수 있으나, 이들은 Gemini/Antigravity 런타임의 기본 지침이 아니다. 사용자가 명시적으로 요청하거나 어댑터 비교가 필요할 때만 참고한다.

## 3. 문서 읽기 규칙

모든 Core/Adapter 문서를 매번 전부 읽지 않는다. 먼저 현재 Gate와 작업 유형을 확인하고, 필요한 문서만 읽는다.

항상 먼저 확인한다.
- `session.json` (또는 진행 상황이 기록된 세션 캐시)
- 사용자 요청
- 관련 산출물 또는 변경 파일

간단하지 않은 Run에서는 다음 문서를 우선 확인한다.
- `docs/core/ORCHESTRATOR_PROTOCOL.md`
- [AGENT_RUN_PROTOCOL_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/core/AGENT_RUN_PROTOCOL_GEMINI.md)
- `docs/core/TRACEABILITY_RULES.md`
- [GATE_PROMPTS_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/adapters/gemini/GATE_PROMPTS_GEMINI.md)

작업 유형별로 추가 확인한다.

| 작업 | 추가 문서 |
| --- | --- |
| ID/메타데이터 | `docs/core/ID_SYSTEM.md`, `docs/core/DOCUMENT_METADATA.md` |
| 요구사항/추적성 | `docs/core/TRACEABILITY_RULES.md`, 요구사항정의서, 추적표 |
| 보안 | `docs/core/SECURITY_BASELINE.md`, `docs/core/KISA_SECURITY_RULES.md`, 보안가이드 |
| 데이터/DB | `docs/core/DATA_STANDARD_RULES.md`, 단어사전, DB명세 |
| 개발표준/기술스택 | `docs/core/TECH_STACK_BASELINES.md`, 개발표준정의서, `docs/templates/DEVELOPMENT_STANDARD_TEMPLATE_GEMINI.md` |
| 변경요청/백로그 | `docs/core/CHANGE_CONTROL_PROCESS.md`, CR 관리대장, Backlog |
| 리팩토링/기술부채 | `docs/core/REFACTORING_PROCESS.md`, Backlog, 관련 설계문서 |
| Run 입력/출력 | [RUN_INPUT_CONTRACT_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/core/RUN_INPUT_CONTRACT_GEMINI.md), [RUN_OUTPUT_CONTRACT_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/core/RUN_OUTPUT_CONTRACT_GEMINI.md) |
| persona/subagent | `docs/core/AGENT_PERSONAS.md`, [PERSONA_MAPPING_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/adapters/gemini/PERSONA_MAPPING_GEMINI.md) |

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
- Gate 4로 넘어갈 때 화면 검수, 별도 CLI 검증, GitHub 리뷰, Claude/Gemini 교차 검토가 도움이 되면 사용자에게 handoff를 제안한다.
- 사용자가 제안을 수락하면 `python vulcan.py handoff ...`로 handoff Run을 만들고, 수락하지 않으면 현재 작업 환경에서 가능한 검증을 계속한다.
- subagent 또는 다른 실행 환경의 결과는 최종 사실로 바로 확정하지 않고 Orchestrator가 다시 검증한다.
- 구현자가 자기 구현을 최종 승인하지 않도록 review persona 또는 별도 환경 검수를 둔다.

## 5. Build Wave 오케스트레이션 규칙 (Gemini 최적화)

구현 단계에서 Orchestrator는 기능 구현의 주 작성자가 되지 않는다. 실제 코드/테스트/UI/API 구현은 `build` persona, subagent, 또는 `agent-run --mode work` worker에게 위임하는 것을 기본값으로 한다.
- Orchestrator가 직접 수행할 수 있는 구현 관련 작업은 작업지시서 작성, worker 결과 통합, 충돌 해결에 필요한 최소 연결 수정, 문서/추적표/session 갱신, 검증 명령 실행으로 제한한다.
- subagent/worker를 사용할 수 없거나 긴급한 1~2줄 연결 수정처럼 직접 수정이 불가피하면 Run에 `orchestrator_direct_edit_reason`, 수정 범위, 실행 검증, 후속 검수 필요 여부를 남긴다.
- 구현 범위가 중간 이상이거나 여러 커밋/여러 모듈이 필요하면 `implementation-plan` Run으로 Build Wave를 먼저 정의한다.
- 동시에 active 상태인 Build Wave는 하나만 둔다. 하나의 Wave 안에서는 수정 범위가 겹치지 않는 subagent 병렬 실행을 허용할 수 있지만, 다른 Wave의 코드 수정은 현재 Wave 완료 후 시작한다.
- Wave 시작과 완료는 `session.json`을 직접 편집하지 않고 `python vulcan.py wave-start <BW-ID>`, `python vulcan.py wave-complete <BW-ID>`, `python vulcan.py sync-session`으로 갱신한다.

## 6. Run 규칙 및 출력 계약

- 작고 명확한 Run 단위로 작업한다.
- Run에는 가능한 한 `persona`를 명시한다. 표준 persona는 `docs/core/AGENT_PERSONAS.md`를 따른다.
- Gemini의 API 특성에 최적화된 [RUN_OUTPUT_CONTRACT_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/core/RUN_OUTPUT_CONTRACT_GEMINI.md)에 의거하여 결과를 YAML/JSON 구조화 스키마 형식에 맞춰 출력하며, `standard_compliance_report`를 포함해야 합니다.
- 실제로 실행하지 않은 테스트를 통과했다고 보고하지 않는다.
- 의미 있는 모든 변경은 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`, `FIND`, `CR` 같은 관련 ID와 연결한다.

## 7. Gemini 도구(Tool) 활용 표준

Gemini 에이전트는 환경에서 제공되는 API 도구들을 아래 규칙에 맞추어 활용해야 합니다.

- **파일 읽기 (`view_file`)**:
  - 처음 읽는 파일은 반드시 StartLine과 EndLine 지정 없이 전체(최대 800라인)를 조회하여 파일의 전반적인 컨텍스트를 완벽히 인지하십시오.
- **파일 편집 (`replace_file_content` / `multi_replace_file_content`)**:
  - 단일 블록의 수정인 경우 `replace_file_content`를 사용하고, 다중 영역의 수정인 경우에만 `multi_replace_file_content`를 단일 호출로 처리하십시오. (파일 전체 덮어쓰기는 지양합니다)
- **권한 에러 발생 시 (`ask_permission`)**:
  - CLI 실행 또는 파일 읽기/쓰기 시 권한 부족 에러가 감지되면, 즉시 필요한 최소 범위의 타깃으로 `ask_permission` 도구를 호출해 권한을 획득하십시오.

## 8. 빌드 및 테스트 핵심 커맨드

프로젝트의 기술 스택에 따라 아래 명령을 수행하여 코드 린트, 빌드, 및 테스트 정합성을 검증하십시오.

### 🐍 Python (FastAPI 등)
* **코드 린트**: `python -m ruff check backend`
* **단위/통합 테스트**: `pytest tests/`

### ☕ Java Spring Boot (Gradle / Maven)
* **Gradle 환경 빌드**: `./gradlew clean build`
* **Gradle 환경 테스트**: `./gradlew test`
* **Maven 환경 빌드**: `./mvnw clean package`
* **Maven 환경 테스트**: `./mvnw test`

### ⚛️ Next.js / React (Node.js)
* **프로젝트 빌드**: `npm run build`
* **테스트 실행**: `npm run test`

### ⚙️ Common CLI Tools
* **추적성 정합성 검사**: `python vulcan.py check-trace`
* **세션 동기화**: `python vulcan.py sync-session`

