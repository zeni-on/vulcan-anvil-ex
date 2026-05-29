# 다음 세션 인수인계 메모

> 작성일: 2026-05-29
> 목적: 다른 대화나 다른 런타임에서 Vulcan-Anvil Ex 작업을 이어갈 때 현재 기준점을 빠르게 맞춘다.

## 현재 기준

Vulcan-Anvil Ex는 `0.4.0` 기준 Experimental 상태다. 현재 방향은 "문서와 Gate 중심의 audit workflow"를 유지하면서, worker 실행, staged QA, Program Design 계약 검증, trace-context 그래프, Dashboard 관제를 실제 프로젝트에서 반복 가능하게 만드는 것이다.

작업을 이어갈 때는 다음 문서를 먼저 본다.

1. `AGENTS.md`
2. `docs/ROADMAP.md`
3. `docs/CONCEPTS.md`
4. `docs/GETTING_STARTED.md`
5. `docs/core/AGENT_RUN_PROTOCOL.md`
6. `docs/core/RUN_INPUT_CONTRACT.md`
7. `docs/core/RUN_OUTPUT_CONTRACT.md`

## 중요한 운영 원칙

- Phase 0~Gate 3는 기본적으로 `main` 기준 문서화와 승인 흐름이다.
- `impl` 진입 후에는 `python vulcan.py branch-start impl`로 `vulcan.config.json.workflow.integration_branch`를 시작한다.
- Build Wave 구현과 Gate 4 QA는 통합 브랜치에서 진행한다.
- 신규 개발 또는 골격이 부족한 프로젝트는 기능 구현 전에 `BW-000 implementation-scaffold`로 빌드 가능한 skeleton을 먼저 만든다.
- Orchestrator는 구현 주 작성자가 아니다. 실제 코드, 테스트, UI, API 구현은 worker/subagent/`agent-run --mode work`로 위임하는 것이 기본값이다.
- Gate 4 QA는 한 번에 몰아서 하지 않는다. `QA-000` 환경 준비, `QA-001` 명령 검증, `QA-002` UI/E2E 증적, `QA-003` 결과 정리로 나눈다.
- `QA-001`~`QA-003`은 `QA-000`이 기록한 같은 QA workspace를 재사용한다.
- QA worker는 실패를 발견하면 즉시 수정하지 않고 원인, 재현 명령, 로그 경로, 영향 ID, 후보 FIND/CR/ISSUE를 남긴다.
- Program Design에 class/interface/public method 계약이 있으면 `python vulcan.py check-contract`로 코드 구조와 대조한다.
- 전역 memory, 과거 샘플, 다른 프로젝트 기록은 현재 프로젝트 사실의 근거가 아니다.

## 다음에 우선 볼 작업

현재 우선순위는 `docs/ROADMAP.md`를 따른다.

1. 새 `v0.4.0` 기준 샘플 프로젝트 재검증
2. trace-context 결과를 `run-new`/`wave-start` Run 초안 품질 개선으로 연결
3. Gate 4 QA worker 실패 보고와 사용자 판단 흐름 실사용 안정화
4. fixture smoke에 샘플에서 발견한 실제 회귀 케이스 추가
5. Dashboard Trace Explorer의 ID 검색, 방향 전환, 복잡도 제어 개선
6. Delivery Profile 구체화
7. 제출용 DOCX/XLSX/HWPX 생성 전략
8. Multi-Agent Dispatcher와 PR 교차검증 자동화 장기 구상

## 다음 대화에서 시작하기 좋은 문장

```text
Vulcan-Anvil Ex 작업을 이어가자. AGENTS.md, docs/ROADMAP.md, docs/CONCEPTS.md, docs/GETTING_STARTED.md를 먼저 확인하고, 현재 우선순위 기준으로 다음 보강 작업을 진행해줘.
```

## 참고

- `docs/ARTIFACT_TEMPLATE_ROADMAP.md`는 초기 산출물 템플릿 구상이다.
- `docs/RUN_FIRST_MULTI_AGENT_DISPATCHER.md`는 dispatcher 장기 구상이다.
- 최신 우선순위 판단은 `docs/ROADMAP.md`를 기준으로 한다.
