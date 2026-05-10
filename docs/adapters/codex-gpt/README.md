# Codex/GPT Adapter

> 상태: 계획 v0.1
> 목적: Vulcan-Anvil Ex Core 산출물과 Agent Run Protocol을 Codex/GPT 기반 개발 실행 흐름에 연결한다.

## 1. 범위

Codex/GPT Adapter는 사람이 Codex 또는 GPT 계열 에이전트와 함께 개발할 때 필요한 입력, 실행 지침, 출력 정규화 방식을 정의한다.

이 Adapter는 다음 작업을 우선 지원한다.

- 요구사항/설계 문서 읽기
- Gate별 작업 범위 선정
- 구현 및 테스트 실행
- 화면 캡처와 결과 증적 생성
- 요구사항추적표 갱신
- 다음 Run 제안

## 2. 초기 대상

초기 검증 대상은 다음 샘플이다.

```text
docs/examples/board-with-login/
```

이 샘플은 요구사항, 기능명세, 프로그램명세, DB명세, 화면명세, 개발표준, 테스트케이스, 테스트 결과, UI 증적을 모두 가지고 있으므로 Adapter 검증에 적합하다.

## 3. Codex/GPT 실행 특징

Codex/GPT Adapter는 다음 특징을 고려한다.

- Codex/GPT 런타임의 기본 진입 문서는 루트 `AGENTS.md`다.
- `AGENTS.md`는 세부 규칙을 중복하지 않고 `docs/core/`와 `docs/adapters/codex-gpt/`를 참조한다.
- Claude 전용 `.claude/CLAUDE.md`, `.claude/agents/`, `.claude/skills/`는 같은 저장소에 공존할 수 있으나 Codex/GPT의 기본 실행 계약은 아니다.
- 파일 읽기와 수정, 테스트 실행을 한 흐름에서 처리할 수 있다.
- 산출물과 코드가 같은 워크스페이스에 있을 때 추적표 갱신까지 이어가기 좋다.
- 컨텍스트가 길어지면 Run Scope를 좁혀야 한다.
- 프로젝트 주입 표준(`docs/seed-docs/reference-standards/`)은 읽기 전용 기준 문서로 사용할 수 있다.
- 민감 참고문서(`docs/ref-docs/`)는 기본적으로 제외해야 한다.
- 테스트와 캡처는 결과 문서 및 증적 경로로 남겨야 한다.

## 4. 기본 실행 순서

```text
1. Run 입력 확인
2. 관련 문서 읽기
3. 추적표에서 관련 ID 확인
4. 구현 또는 문서 수정
5. 테스트 실행
6. 증적 생성
7. 추적표와 결과서 갱신
8. Run 출력 정리
```

## 5. 다음 작성 대상

본 Adapter는 다음 문서를 기준으로 구체화한다.

- `RUN_INPUT_CONTRACT.md`
- `RUN_OUTPUT_CONTRACT.md`
- `GATE_PROMPTS.md`
- `LIMITATIONS.md`

## 6. 현재 사용 가능한 문서

| 문서 | 용도 |
| --- | --- |
| `RUN_INPUT_CONTRACT.md` | Codex/GPT에게 전달할 표준 작업지시서 형식 |
| `RUN_OUTPUT_CONTRACT.md` | Codex/GPT가 반환해야 하는 표준 완료보고서 형식 |
| `PERSONA_DELEGATION.md` | Codex/GPT subagent 위임과 persona 적용 규칙 |
| `GATE_PROMPTS.md` | Gate별 기본 프롬프트 |
| `LIMITATIONS.md` | Codex/GPT Adapter 한계와 승인 필요 상황 |
| `skills/` | Codex/GPT가 상황별로 명시적으로 읽는 작업 절차 카드 |

## 7. Skill 카드

Codex/GPT Adapter의 skill은 Claude `.claude/skills`와 다르다.
런타임 플러그인이 아니라 `AGENTS.md`가 상황별로 참조하는 절차 카드다.

| 상황 | Skill |
| --- | --- |
| 추적성 검토 | `skills/traceability-review.md` |
| 보안 검토 | `skills/security-review.md` |
| 표준용어/DB명세 검토 | `skills/data-standard-review.md` |
| QA 결함 수정 루프 | `skills/qa-fix-loop.md` |
| 변경요청 영향도 분석 | `skills/change-impact-analysis.md` |

## 8. 다음 검증 작업

다음 단계에서는 로그인 게시판 샘플을 기준으로 실제 Run 입력 파일을 작성한다.

권장 위치:

```text
docs/examples/board-with-login/runs/
```

권장 첫 Run:

```text
RUN-001_review-traceability_v0.1.md
```

목표:

```text
샘플 산출물과 구현 결과를 Codex/GPT Adapter 입력/출력 계약으로 재검증한다.
```
