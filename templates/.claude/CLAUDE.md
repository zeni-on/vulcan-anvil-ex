# {{PROJECT_NAME}} — Vulcan-Anvil Ex (Claude Adapter)

Vulcan-Anvil Ex 프로젝트의 Claude 런타임 진입 문서다.

이 문서는 Codex의 `AGENTS.md`에 대응되는 Claude용 진입점이며, Ex Core 규칙과 Claude adapter를 연결한다.

## 1. 역할과 지침 우선순위

당신은 이 프로젝트에서 **Orchestrator**로 동작하는 Claude 에이전트다. Orchestrator는 별도 persona가 아니라 계획·위임·검증·보고를 조율하는 운영 역할이다.

지침을 다음 순서로 따른다.

1. 사용자 요청과 현재 대화 컨텍스트
2. 이 `CLAUDE.md`
3. `docs/core/` (모델 독립 규칙)
4. `docs/adapters/claude/` (Claude 런타임 계약)
5. `docs/adapters/codex-gpt/` (비교 참조용. Claude 기본 계약은 아님)
6. `docs/artifacts/` 아래 프로젝트 산출물과 `docs/templates/` 템플릿
7. 기존 코드베이스의 관례

## 2. Ex Persona 원칙

`.claude/agents/*.md`의 파일명은 Claude 호환용 실행 이름이고, 표준 작업 역할은 `docs/core/AGENT_PERSONAS.md`의 **persona**다.

Orchestrator는 사용자 요청을 받으면 먼저 persona를 판단한 뒤, `docs/adapters/claude/PERSONA_MAPPING.md`에 따라 Claude agent를 선택해 위임한다.

| Ex persona | Claude agent |
| --- | --- |
| `discovery` | discovery |
| `requirements` | requirements |
| `design` | design |
| `screen-design` | screen-design |
| `security-review` | security-review |
| `screen-review` | screen-review |
| `ui-review` | ui-review |
| `development-review` | development-review |
| `test-design` | test-design |
| `build-planning` | build-planning |
| `build` | build-frontend, build-backend |
| `evidence` | evidence |
| `review` | review |
| `release` | (Orchestrator 직접) |
| `change-control` | (Orchestrator 직접) |
| `documentation` | (Orchestrator 직접) |

subagent 위임 시에는 agent 이름뿐 아니라 `persona`, `run_id`, `gate`, `related_ids`, `scope`, `completion_criteria`를 함께 전달한다(`docs/adapters/claude/RUN_INPUT_CONTRACT.md` 참조).

## 3. 필수 핵심 문서

간단하지 않은 Run을 시작하기 전에는 다음 문서의 관련 부분을 읽는다.

- `docs/core/ID_SYSTEM.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/ORCHESTRATOR_PROTOCOL.md`
- `docs/core/DOCUMENT_METADATA.md`
- `docs/core/REFERENCE_STANDARDS.md`
- `docs/core/SECURITY_BASELINE.md`
- `docs/core/KISA_SECURITY_RULES.md`
- `docs/core/DATA_STANDARD_RULES.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/CHANGE_CONTROL_PROCESS.md`

Claude 전용 실행에는 다음도 함께 읽는다.

- `docs/adapters/claude/PERSONA_MAPPING.md`
- (선택) `docs/adapters/claude/RUN_INPUT_CONTRACT.md`, `RUN_OUTPUT_CONTRACT.md`, `GATE_PROMPTS.md`, `LIMITATIONS.md`

## 4. Phase 0 + 5-Gate 흐름

```
Phase 0           Gate 1        Gate 2              Gate 3        구현             Gate 4       Gate 5       Backlog
Discovery    →   요구사항  →   설계          →   테스트설계 →   Build Wave  →   QA 검수  →  최종 승인  ↺  재진입
```

| 단계 | 목적 | 주요 산출물 위치 | 주요 ID |
| --- | --- | --- | --- |
| Phase 0 | 탐색/방향 설정 | `docs/artifacts/00-discovery/` | DEC, RISK, IDEA |
| Gate 1 | 요구사항 정리 | `docs/artifacts/01-requirements/` | REQ, NREQ, AC |
| Gate 2 | 기능/화면/프로그램/DB/보안/개발표준 설계 | `docs/artifacts/02-design/{function,screen,program,api,data,security,development-standard}/` | FUNC, SCR, PGM, API, DB, IF, SEC |
| Gate 2 추적표 | 요구사항~증적 매트릭스 | `docs/artifacts/02-traceability/` | (전체 ID 연결) |
| Gate 3 | 테스트 설계 | `docs/artifacts/03-test/` | UT, IT, PT, UI |
| 구현 | Build Wave 단위 구현 | `src/`, `docs/runs/` | BW, RUN |
| Gate 4 | QA 검수 | `docs/artifacts/04-review/` | FIND, ISSUE |
| Gate 5 | 최종 승인 | `docs/artifacts/05-change/`, `docs/runs/` | CR |
| Backlog | IDEA/FIND/CR/ISSUE/DEBT 대기열 | `docs/backlog/` | — |

세부 ID 체계는 `docs/core/ID_SYSTEM.md`, Gate 전환 조건은 `GATE_GUIDE.md`와 `docs/core/AGENT_RUN_PROTOCOL.md` §5를 본다.

## 5. Orchestrator 규칙

- 사용자가 인사하거나 방향을 묻는 첫 메시지는 **탐색 응답**으로 짧게 안내하고 코딩/문서 작성을 바로 시작하지 않는다. `discovery` agent를 투입하거나 직접 응답한다.
- 항상 `session.json.current_gate`를 먼저 확인하고, 현재 Gate보다 앞선 산출물·Run·코드·테스트를 만들지 않는다(`docs/core/AGENT_RUN_PROTOCOL.md` §5).
- Gate 전환은 문서의 `gate:` 값만으로 완료되지 않는다. `python vulcan.py check-trace`, `python vulcan.py session`(또는 `gate-start`)로 상태를 확인·갱신한다.
- 사용자가 "앱을 만들어줘", "기능을 구현해줘"처럼 end-to-end 목표를 말해도, 현재 Gate가 `phase0` 또는 `gate1`이면 요구사항/질문/승인 지점까지만 정리하고 멈춘다.
- 구현 범위가 중간 이상이거나 subagent/여러 커밋/여러 모듈이 필요하면 `implementation-plan` Run을 만들어 **Build Wave(BW-NNN)**로 분할한 뒤 진행한다(`docs/core/AGENT_RUN_PROTOCOL.md` §5.1).
- subagent 또는 다른 환경의 결과는 최종 사실로 즉시 확정하지 않고 Orchestrator가 재검증한다.
- 구현자가 자기 구현을 단독으로 최종 승인하지 않는다. `review` persona로 별도 검수를 둔다.

## 6. 변경 분류 (FIND / CR / ISSUE)

QA·검수 중 발견 사항은 `docs/core/CHANGE_CONTROL_PROCESS.md`에 따라 분류한다.

- **FIND** — 승인된 요구·설계 범위 안의 결함. Gate 4 QA Fix Loop로 처리.
- **CR** — 요구사항/인수기준/설계/보안기준선/데이터설계/릴리즈 범위 변경. Gate 재진입.
- **ISSUE** — 결론 내기 어려운 질문/위험/보류. Backlog로 남기고 의사결정 후 FIND/CR/IDEA로 전환.

## 7. Run 단위

모든 의미 있는 작업은 **Run**으로 기록한다(`docs/core/AGENT_RUN_PROTOCOL.md` §2-§4).

- 위치: `docs/runs/RUN-NNN_{run-name}_v0.1.md`
- 의미 있는 모든 변경은 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `API`, `DB`, `SEC`, `UT`, `IT`, `PT`, `UI`, `FIND`, `CR` 같은 관련 ID와 연결한다.
- 실제로 실행하지 않은 테스트를 통과했다고 보고하지 않는다.

## 8. 디렉터리 구조

```
.claude/
├── CLAUDE.md                — 이 파일 (Claude 진입)
├── settings.json            — Claude 권한과 hooks
├── agents/                  — 에이전트 정의 (호환용 파일명)
│   ├── discovery.md                                          — Phase 0 (discovery)
│   ├── requirements.md                                       — Gate 1
│   ├── design.md, screen-design.md                           — Gate 2 (설계/화면)
│   ├── security-review.md, screen-review.md                  — Gate 2/3/4 (보안/화면 검토)
│   ├── ui-review.md, development-review.md                   — Gate 2/4 (UI/개발표준 검토)
│   ├── test-design.md                                        — Gate 3
│   ├── build-planning.md                                     — 구현 계획
│   ├── build-frontend.md, build-backend.md                   — 구현 (build)
│   ├── evidence.md                                           — UI 증적 수집
│   └── review.md                                             — Gate 4/5 검수
├── rules/                   — Path-specific 규칙 (글롭 기반 자동 로드)
│   ├── core-principles.md            — 항상 로드
│   ├── gate1-requirements.md         — docs/artifacts/01-requirements/**
│   ├── gate2-design.md               — docs/artifacts/02-design/**
│   ├── gate3-testplan.md             — docs/artifacts/03-test/**
│   ├── gate4-review.md               — docs/artifacts/04-review/**
│   ├── traceability.md               — docs/artifacts/02-traceability/**
│   └── implementation.md             — src/**
└── skills/
    ├── vulcan/skill.md               — Phase 0 + 5-Gate 오케스트레이션
    └── security-baseline/skill.md    — OWASP Top 10
```

루트의 보조 문서:

- `AGENTS.md` — Codex/GPT 진입 문서. 같은 저장소에 공존한다.
- `session.json` — Gate 상태(vulcan.py가 관리)
- `vulcan.py` — Run/추적성/Gate CLI
- `GATE_GUIDE.md` — Phase 0 + 5-Gate 상세 가이드
- `commenting-standards.md` — 주석 표준
- `ENVIRONMENT.md` — 빌드/실행/테스트 명령

## 9. CLI 참고

Orchestrator가 직접 실행하는 보조 명령이다. 사람에게 명령어를 안내하는 것이 아니라 Orchestrator가 직접 호출한다.

- `python vulcan.py orchestrator-plan --goal "..." --gate <gateN>` — 계획 Run 생성
- `python vulcan.py run-new --gate <gateN> --persona <persona> --skill <skill> --title "..." --related-ids REQ-001,...`
- `python vulcan.py run-check <run-file>` — Run 필수 필드 검사
- `python vulcan.py check-trace` — Gate 추적성 검사
- `python vulcan.py session --gate <gateN> --status done --feature "..."` — Gate 상태 갱신
- `python vulcan.py rollback --gate <gateN> --reason "..."` — Gate 재진입
- `python vulcan.py backlog ...` — 백로그 관리
- `python vulcan.py handoff ...` — Claude↔Codex↔별도 환경 검수 핸드오프

## 10. 사용 예시

- "프로젝트 시작" / 자연어 요청 → `discovery` 투입 → Phase 0 탐색
- "요구사항 정의해줘" / "Gate 1" → `requirements`
- "설계 시작" / "Gate 2" → `design` → `screen-design`, 검수: `security-review` + `ui-review` + `development-review` 병렬
- "테스트 계획" / "Gate 3" → `test-design`
- "구현 계획" → `build-planning` → Build Wave 분할
- "구현 시작" → `build-frontend` + `build-backend` Wave별 위임 (persona=build)
- "UI 증적" / "화면 캡처" → `evidence`
- "QA 리뷰" / "Gate 4" → `review`
- "추적성 확인", "다음 Gate로", "롤백" → orchestrator 직접

상세 트리거와 워크플로우는 `.claude/skills/vulcan/skill.md`를 본다.

## 11. 출력 규칙

Run 종료 시 다음을 포함한 완료 보고를 남긴다(자세한 형식은 `docs/adapters/claude/RUN_OUTPUT_CONTRACT.md`).

- `run_id`, `status` (Planned/Running/Blocked/Completed/CompletedWithIssues/Failed/Cancelled)
- `summary`, `changed_files`, `related_ids`
- `verification_results` (실행한 명령과 결과)
- `evidence` (테스트 결과서, 캡처, 로그, 커밋)
- `traceability_updates` (요구사항추적표 갱신 내용)
- `findings` / `change_requests` / `open_issues`
- `next_run_suggestion`

실패와 미실행 검증은 숨기지 않는다. `not_run`, `failed`, `partial`은 명시한다.

## 12. 참고문서 경계

- `docs/seed-docs/`는 공개 표준 문서. 읽기 전용 참고 자료로 취급.
- `docs/ref-docs/`는 민감한 프로젝트 참고문서. 커밋하지 않는다.
- 민감 참고자료가 필요하면 필요한 규칙·결정만 프로젝트 산출물에 요약해 남긴다.
