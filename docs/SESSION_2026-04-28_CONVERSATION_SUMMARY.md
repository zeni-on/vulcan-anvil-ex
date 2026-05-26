# 2026-04-28 대화 요약

> 목적: 현재 Codex 작업 폴더가 `VulnTrace`로 잡혀 있더라도, 실제 진행 중인 `Vulcan-Anvil-Ex` 작업 맥락을 저장소 안에 남겨 다음 환경에서 이어가기 쉽게 한다.

## 1. 현재 작업 저장소

- GitHub 저장소: `https://github.com/zeni-on/vulcan-anvil-ex`
- 작업 브랜치: `codex/bootstrap-ex`
- 최근 커밋: `da321e5 docs: define Vulcan-Anvil Ex direction`

현재 Codex 세션의 기본 작업 폴더는 다른 프로젝트로 잡혀 있었지만, 실제 Vulcan-Anvil Ex 관련 문서 작업은 `vulcan-anvil-ex` 저장소에 수행했다. 다른 컴퓨터에서는 GitHub 저장소를 clone한 뒤 `codex/bootstrap-ex` 브랜치를 기준으로 이어가면 된다.

## 2. 핵심 방향

Vulcan-Anvil Ex는 기존 Claude 전용 Vulcan-Anvil을 확장해, 특정 모델에 종속되지 않는 AI 협업 기반 개발 운영 프레임워크로 만든다.

핵심 문장:

> 모델은 자유롭게, 산출물은 추적 가능하게.

Ex는 단순한 문서 템플릿 묶음이 아니다. 사용자와 메인 에이전트가 Phase 0부터 아이디어, 문제 정의, 기술 선택, 상위 설계를 함께 탐색하고, 이후 여러 에이전트가 요구사항, 설계, 구현, 테스트, 문서 갱신을 수행할 수 있도록 돕는 프레임워크다.

사람은 모든 산출물을 직접 작성하는 역할이 아니라, 맥락과 의도를 제공하고, 중요한 판단을 승인하며, 최종 검수를 수행한다.

## 3. Core와 Adapter

Ex의 본체는 특정 도구 설정이 아니라 Core 규격이다.

- Core: Gate, 산출물, 추적성, 승인, 문서 규격, Dashboard, `check-trace`
- Adapter: 각 AI 도구에 맞춘 실행 방식

초기 Adapter 후보:

- Claude Adapter: 기존 `.claude/agents`, `.claude/rules`, `.claude/skills`
- Codex Adapter: Codex용 가이드, skill/plugin 후보, 작업 playbook

`.claude`는 Ex의 본체가 아니라 Claude용 Adapter로 본다.

## 4. 역할 용어

기존 `PM`, `QA`, `Architect` 같은 직책명 중심 표현은 Core 표준에서는 책임 기반 역할명으로 바꾼다.

예시:

- `PM` -> `Requirements Lead`
- `Architect` -> `Technical Architect`
- `DBA` -> `Data Architect`
- `QA (Gate 3)` -> `Test Designer`
- `QA (Gate 4)` -> `QA Reviewer`
- `Human` -> `Approver`
- `Frontend-dev` -> `Frontend Engineer`
- `Backend-dev` -> `Backend Engineer`
- 신규 후보: `Documentation Curator`

핵심 원칙:

> 역할명은 조직 직책이 아니라, 해당 산출물과 판단에 대한 책임을 나타낸다.

## 5. Phase 0의 의미

Phase 0는 단순한 사전 조사 단계가 아니다.

사용자가 메인 에이전트와 오래 대화하면서 다음을 함께 만드는 단계다.

- 아이디어 발굴
- 문제 재정의
- 제품 방향 설정
- 기술 검토
- 구현 전략
- 범위와 제외 범위
- 리스크 식별

이 단계의 팀워크 품질이 이후 요구사항, 설계, 구현 품질을 크게 좌우한다.

## 6. 산출물 템플릿 KPI

사용자의 올해 KPI 중 하나는 개발 프로젝트 산출물 템플릿을 구성하는 것이다.

방향:

- 작년 감리 때 사용했던 실제 문서를 기반으로 분석한다.
- 이론적인 양식이 아니라 감리 경험에서 검증된 항목을 출발점으로 삼는다.
- 감리에 필요한 항목은 유지하되, 에이전트가 작성하고 사용자가 검토하기 좋은 구조로 재설계한다.
- Strict 모드 기준 템플릿을 먼저 만들고, 이후 Standard와 Lightweight로 축약한다.

우선 분석 대상 후보:

- 요구사항정의서
- 테스트 계획서
- 테스트 결과서
- 요구사항 추적 매트릭스
- 변경 관리 대장
- 최종 승인 기록

## 7. Dashboard

Vulcan-Anvil Ex의 Dashboard는 부가 기능이 아니라 핵심 구성 요소다.

현재 Dashboard는 여러 프로젝트 등록, 로컬 프로젝트 연결, `session.json` 기반 Gate 상태 표시, 문서 트리, Markdown 문서 뷰어, 커밋 타임라인 등을 지원한다.

Ex에서 Dashboard는 에이전트가 만든 산출물을 사람이 확인하는 관제 화면이 된다.

Dashboard가 답해야 하는 질문:

> 지금 프로젝트는 어디까지 왔고, 무엇이 부족하며, 어떤 증거가 남아 있는가?

## 8. 현재 생성된 문서

- `docs/VULCAN_ANVIL_EX_DIRECTION.md`
- `docs/ARTIFACT_TEMPLATE_ROADMAP.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `docs/SESSION_2026-04-28_CONVERSATION_SUMMARY.md`

## 9. 다음에 이어갈 작업

다음 세션에서 할 일:

1. `docs/VULCAN_ANVIL_EX_DIRECTION.md`를 읽는다.
2. `docs/ARTIFACT_TEMPLATE_ROADMAP.md`를 읽는다.
3. `docs/NEXT_SESSION_HANDOFF.md`를 읽는다.
4. 작년 감리 산출물 목록을 기준으로 템플릿 후보를 분류한다.
5. 우선 `요구사항정의서` 템플릿부터 설계한다.

다음 대화에서 사용할 문장:

> Vulcan-Anvil Ex 작업을 이어가자. `docs/VULCAN_ANVIL_EX_DIRECTION.md`, `docs/ARTIFACT_TEMPLATE_ROADMAP.md`, `docs/NEXT_SESSION_HANDOFF.md`, `docs/SESSION_2026-04-28_CONVERSATION_SUMMARY.md`를 먼저 읽고, 감리 산출물 템플릿 설계를 계속 진행해줘.
