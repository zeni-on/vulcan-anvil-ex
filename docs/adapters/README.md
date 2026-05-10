# Vulcan-Anvil Ex Adapters

이 디렉토리는 Vulcan-Anvil Ex Core 규약을 실제 에이전트 도구에 연결하기 위한 Adapter 문서를 둔다.

Core는 모델 독립 규칙을 정의하고, Adapter는 이를 Codex/GPT, Claude, Cursor, Copilot 같은 실행 환경에 맞게 변환한다.

## 1. Adapter의 위치

Adapter는 다음 질문에 답한다.

- 이 에이전트에게 어떤 문서를 어떤 순서로 제공할 것인가?
- Gate별 프롬프트 또는 실행 명령은 어떻게 구성할 것인가?
- 에이전트가 만든 결과를 Core 산출물 형식으로 어떻게 되돌릴 것인가?
- 실패, 질문, 승인요청을 어떻게 기록할 것인가?
- 컨텍스트 한계가 있을 때 어떤 문서를 우선 제공할 것인가?

## 2. 공통 전제

모든 Adapter는 다음 Core 문서를 준수한다.

- `docs/core/ID_SYSTEM.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/DOCUMENT_METADATA.md`
- `docs/core/REFERENCE_STANDARDS.md`
- `docs/core/DATA_STANDARD_RULES.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`

## 3. 우선 구현 순서

권장 순서:

1. `codex-gpt`: 현재 샘플 개발 흐름을 기준으로 첫 Adapter를 만든다.
2. `claude`: 같은 Run Protocol과 persona 체계를 Claude 실행 방식에 매핑한다.
3. `dashboard`: Run 상태, 산출물 상태, 추적표 상태를 시각화한다.

## 4. Adapter 산출물

Adapter는 최소 다음 산출물을 가진다.

| 문서 | 목적 |
| --- | --- |
| `README.md` | Adapter의 범위와 사용 방식 |
| `RUN_INPUT_CONTRACT.md` | 해당 에이전트에 전달할 입력 형식 |
| `RUN_OUTPUT_CONTRACT.md` | 해당 에이전트 결과를 정규화하는 형식 |
| `GATE_PROMPTS.md` | Gate별 기본 프롬프트 또는 실행 지침 |
| `PERSONA_MAPPING.md` | Core persona와 도구별 agent/subagent 이름의 매핑 |
| `LIMITATIONS.md` | 모델/도구 한계, 보안 주의사항 |

## 5. 다음 작업

다음 단계에서는 `codex-gpt` Adapter를 만든다.

첫 목표는 로그인 게시판 샘플을 대상으로 다음 흐름을 재현하는 것이다.

```text
Run 입력 생성
-> Codex/GPT 실행 지침 구성
-> 구현/테스트/증적 수행
-> Run 결과 정규화
-> 추적표 갱신
```
