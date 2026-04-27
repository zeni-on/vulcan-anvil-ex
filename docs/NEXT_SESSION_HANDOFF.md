# 다음 세션 인수인계 메모

> 작성일: 2026-04-28
> 목적: 다른 컴퓨터나 다른 대화에서 Vulcan-Anvil Ex 작업을 이어가기 위한 맥락 요약.

## 현재 방향

Vulcan-Anvil Ex는 기존 Claude 전용 Vulcan-Anvil을 확장해, 여러 AI 도구와 사람이 함께 사용할 수 있는 개발 운영 프레임워크로 만든다.

중요한 관점:

- 특정 모델에 종속되지 않는다.
- Core와 Adapter를 분리한다.
- `.claude`는 Core가 아니라 Claude Adapter다.
- Codex, Claude, Cursor, Copilot 등은 Core를 실행하는 도구가 될 수 있다.
- Ex의 중심은 산출물, 추적성, Gate, 승인, Dashboard다.
- Phase 0와 상위 설계는 사용자와 메인 에이전트가 오래 대화하며 아이디어와 방향을 함께 만드는 단계다.
- 이후 요구사항, 설계, 구현, 테스트, 문서 갱신은 에이전트가 수행할 수 있어야 한다.
- 최종 검수와 승인은 사용자 또는 지정된 승인자가 담당한다.

## 현재까지 만든 문서

- `docs/VULCAN_ANVIL_EX_DIRECTION.md`
- `docs/ARTIFACT_TEMPLATE_ROADMAP.md`

## 다음에 이어갈 작업

1. 작년 감리 산출물 목록을 수집한다.
2. 산출물을 Phase/Gate 기준으로 분류한다.
3. 각 문서의 필수 항목, 검토 기준, 승인 메타데이터를 정의한다.
4. 에이전트가 작성할 수 있는 템플릿 구조로 바꾼다.
5. 우선 `요구사항정의서` 템플릿부터 만든다.

## 다음 대화에서 Codex에게 전달하면 좋은 문장

다음과 같이 말하면 맥락을 빠르게 이어갈 수 있다.

> Vulcan-Anvil Ex 작업을 이어가자. `docs/VULCAN_ANVIL_EX_DIRECTION.md`, `docs/ARTIFACT_TEMPLATE_ROADMAP.md`, `docs/NEXT_SESSION_HANDOFF.md`를 먼저 읽고, 감리 산출물 템플릿 설계를 계속 진행해줘.

