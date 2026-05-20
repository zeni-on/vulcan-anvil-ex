# Audit-first Multi-Agent SI Delivery Orchestrator

> 상태: reference draft v0.1
> 목적: Vulcan-Anvil Ex의 차별화 방향을 "감리 가능한 산출물"과 "멀티에이전트 기반 코드 생산성"의 결합 관점에서 정리한다.
> 현재 전제: 현 샘플은 멀티에이전트 구현이 완성된 상태는 아니지만, 감리 산출물/추적성/증적/코드 생성 흐름은 약 80% 수준의 가능성을 이미 보여준다. 이 문서는 그 분석을 바탕으로 Ex가 지향해야 할 제품 포지션과 로드맵을 정리한 참고 문서다.

---

## 1. 핵심 차별점

어렵지만, 사실 이 지점이 Vulcan-Anvil Ex의 진짜 차별점이 될 수 있다.

Ex가 잡아야 할 두 마리 토끼는 다음 두 가지다.

1. 감리 산출물 / 제출 문서 / 추적성 / 증적
   - 엔터프라이즈 SI에 투입되기 위한 신뢰성

2. 코드 생산성 / 모듈 병렬 구현 / 멀티에이전트 오케스트레이션
   - 기존 SI 방식보다 빨라지는 이유

둘 중 하나만 있으면 부족하다.

문서만 잘 나오면 "좋은 산출물 자동화 도구"는 되지만, 개발 생산성 혁신은 약하다.

반대로 멀티에이전트 코드만 잘 짜면 "AI 코딩 도구"는 되지만, SI 감리/검수/인수에서는 쓰기 어렵다.

따라서 Ex의 포지션은 다음처럼 잡는 것이 좋다.

```text
Vulcan-Anvil Ex =
감리 가능한 산출물을 중심으로,
멀티에이전트 구현을 통제하는 SI Delivery Orchestrator
```

핵심은 "문서 vs 코드"가 아니다.

핵심은 다음이다.

```text
코드 작업이 문서/추적성/증적을 자동으로 남기게 만드는 것.
```

즉 멀티에이전트가 빠르게 코드를 만들더라도, 각 agent의 산출물은 반드시 다음 정보를 함께 남겨야 한다.

- 어떤 요구사항을 구현했는가
- 어떤 설계를 따랐는가
- 어떤 파일을 수정했는가
- 어떤 테스트를 실행했는가
- 증적은 어디 있는가
- 추적표는 어떻게 갱신됐는가
- 미해결 FIND/CR/ISSUE는 무엇인가

그래야 "빠른 구현"이 감리 산출물과 연결된다.

---

## 2. 현재 상태에 대한 전제

현재 Ex 샘플은 멀티에이전트 구현까지 완성된 상태는 아니다.

다만 중요한 점은, 이미 다음 영역에서는 상당한 가능성을 보여준다는 것이다.

- 산출물 생성 흐름
- 요구사항/설계/테스트/QA/릴리즈 문서 흐름
- Run 기록
- 추적성 검사
- QA Evidence
- 독립 검수와 FIND 보강 루프
- 실제 코드 생성

따라서 현재 샘플에 대한 판단은 다음에 가깝다.

```text
멀티에이전트 오케스트레이션은 아직 구현 과제다.
하지만 감리형 산출물과 코드 생성이 연결되는 흐름은 이미 약 80% 수준의 가능성을 보여준다.
```

즉 지금 필요한 것은 완전히 새로운 방향 전환이 아니라, 이미 나온 산출물/코드 흐름을 더 효율적이고 반복 가능한 구조로 전환하는 것이다.

---

## 3. 두 개의 엔진

Ex는 두 개의 엔진을 가져야 한다.

### 3.1 Audit Backbone

Audit Backbone은 감리/제출/추적성 중심의 뼈대다.

역할:

- Gate
- 산출물
- 승인
- traceability
- evidence
- export package
- audit readiness dashboard

이 영역은 순차적이고 보수적이어야 한다.

Audit Backbone은 엔터프라이즈 SI에서 다음 질문에 답해야 한다.

- 요구사항이 설계/구현/테스트/증적으로 연결되는가?
- 변경 이력이 남는가?
- 미해결 이슈가 숨겨지지 않는가?
- 승인 주체가 명확한가?
- 제출 가능한 산출물이 만들어지는가?

### 3.2 Agent Execution Engine

Agent Execution Engine은 멀티에이전트 구현/검토/증적 수집 엔진이다.

역할:

- module slicing
- build wave
- subagent dispatch
- code implementation
- test execution
- review
- evidence collection
- issue classification

이 영역은 병렬적이고 효율적이어야 한다.

Agent Execution Engine은 다음 질문에 답해야 한다.

- 모듈별 병렬 구현이 가능한가?
- worker별 책임이 분리되는가?
- build/review/evidence 역할을 나눌 수 있는가?
- 같은 파일 충돌과 범위 오염을 막을 수 있는가?
- Wave 단위로 안전하게 통합할 수 있는가?

---

## 4. Run Protocol: 두 세계를 연결하는 핵심 계약

Audit Backbone과 Agent Execution Engine을 연결하는 핵심 계약이 Run Protocol이다.

Run 하나는 단순 작업 기록이 아니라 두 세계를 연결해야 한다.

```text
Run =
  작업 지시서
  + agent 실행 단위
  + 산출물 변경 기록
  + 코드 변경 기록
  + 테스트/증적 기록
  + traceability delta
  + audit evidence
```

이렇게 잡으면 문서와 멀티에이전트가 따로 놀지 않는다.

Ex의 이상적인 구조는 다음과 같다.

```text
[Audit Backbone]
  Gate
  Deliverables
  Traceability
  Approval
  Evidence
  Export Package

        ↑
        │ Run Protocol
        ↓

[Agent Execution Engine]
  Module Slicing
  Build Wave
  Worker / Persona
  Code / Test
  Review
  Evidence Collection
```

감리 문서가 위에서 요구하는 기준이고, 멀티에이전트는 그 기준을 만족시키기 위한 생산 라인이다.

여기서 중요한 원칙은 다음이다.

```text
멀티에이전트는 자유롭게 일하면 안 된다.
Run 계약 안에서만 일해야 한다.
```

예를 들어 build worker에게 단순히 다음처럼 지시하면 안 된다.

```text
사용자 포털 만들어줘.
```

대신 다음처럼 지시해야 한다.

```yaml
persona: build
module: MOD-USER-PORTAL
gate: impl
wave: BW-002
related_ids:
  - REQ-010
  - AC-010
  - SCR-003
  - API-005
  - PGM-012
writable_scope:
  - apps/user-portal/**
  - tests/user-portal/**
readonly_scope:
  - docs/artifacts/**
completion_required:
  - code changes
  - tests executed
  - evidence path
  - traceability update proposal
  - unresolved FIND/CR/ISSUE
```

이런 식이어야 agent가 빠르게 움직여도 감리 대응성이 깨지지 않는다.

---

## 5. 엔터프라이즈 SI 투입을 위한 세 가지 제품성

내년에 실제 엔터프라이즈 SI 투입을 목표로 한다면, Ex는 처음부터 세 가지 제품성을 가져야 한다.

### 5.1 Audit-readiness

감리자가 볼 수 있는 형태로 산출물이 나와야 한다.

확인 질문:

- 요구사항이 설계/구현/테스트/증적으로 연결되는가?
- 제출 패키지가 생성되는가?
- 변경요청과 결함 이력이 남는가?
- 누락 산출물을 Dashboard에서 볼 수 있는가?

### 5.2 Delivery acceleration

기존 SI보다 개발 속도가 빨라져야 한다.

확인 질문:

- 모듈 단위 병렬 구현이 가능한가?
- build worker, review worker, evidence worker를 분리할 수 있는가?
- Wave 단위로 안전하게 통합할 수 있는가?
- 같은 파일 충돌과 범위 오염을 막을 수 있는가?

### 5.3 Governance control

속도와 감리 기준 사이를 Orchestrator가 통제해야 한다.

확인 질문:

- Gate를 자동으로 막을 수 있는가?
- 승인 전 구현을 제한할 수 있는가?
- agent 결과를 최종 사실로 확정하지 않고 검증하는가?
- FIND/CR/ISSUE를 구분하는가?
- 사람이 승인해야 하는 지점을 숨기지 않는가?

---

## 6. v0.1의 목표: Audit-first Multi-Agent Delivery Kernel

새 0.1은 "Audit만"도 아니고 "Agent만"도 아니어야 한다.

0.1부터 둘 다의 최소 골격은 있어야 한다.

단, 구현 범위는 작게 잡아야 한다.

권장 v0.1 목표는 다음과 같다.

```text
Vulcan-Anvil Ex 0.1 =
Audit-first Multi-Agent Delivery Kernel
```

### 6.1 0.1에서 반드시 되는 것

#### 1. 감리 산출물 최소 세트 생성

- 요구사항
- 설계
- 테스트 케이스
- 테스트 결과
- 추적표
- 릴리즈 승인/인수인계
- 제출 패키지 manifest

#### 2. Module Slicing 가능

- MOD-ID 정의
- 모듈 책임
- API/DB/화면/배치 연결
- 병렬 가능 여부
- 선행 의존성

#### 3. Build Wave 가능

- Wave 계획
- Wave별 Run
- worker에게 넘길 작업 계약
- Wave 완료 검증

#### 4. Run Protocol이 양쪽을 연결

- agent 작업 결과가 산출물/코드/테스트/증적으로 연결됨

#### 5. CLI 중심 최소 실행

- init
- gate-start
- run-new
- run-check
- check-trace
- check-deliverables
- wave-start
- wave-complete
- export-package

### 6.2 0.1에서 굳이 하지 않아도 되는 것

- 완성형 Dashboard
- 완전 자동 DOCX/HWPX 생성
- Claude/Codex/Hermes 완전 동등 지원
- 대규모 kanban dispatcher
- 모든 산출물 템플릿 완성
- 복잡한 UI evidence 자동화

즉 0.1은 "작지만 끝까지 흐르는 샘플"이 핵심이다.

작은 예제 프로젝트 하나를 대상으로 다음 흐름을 끝까지 보여줘야 한다.

```text
요구사항 작성
-> 설계 작성
-> 모듈 분리
-> 테스트 설계
-> Build Wave 구현
-> 테스트/증적
-> 추적표
-> 제출 패키지 manifest
```

이게 되면 0.2부터 멀티에이전트 효율화를 붙이면 된다.

---

## 7. 추천 로드맵

### v0.1: Audit-first Delivery Kernel

- Gate
- Run
- Traceability
- Deliverables
- Module Slicing
- Build Wave
- Export Package Manifest
- 작은 샘플 end-to-end

### v0.2: Codex Execution Adapter

- AGENTS.md
- Codex Run 실행
- build/review/evidence worker 계약
- 코드 변경 + 테스트 + 산출물 갱신 연결

### v0.3: Multi-Agent Execution

- 병렬 Build Wave
- worker isolation
- review worker
- evidence worker
- conflict detection
- wave-level integration

### v0.4: Dashboard

- 감리 준비도
- Gate 상태
- 산출물 completeness
- traceability coverage
- module/wave 상태
- FIND/CR/ISSUE 상태

### v0.5: Submission Export

- DOCX/XLSX/HWPX/PDF 생성
- audit package
- export manifest
- 제출 이력

### v0.6: Hermes/Claude/Gemini Orchestration

- Hermes profile
- delegate_task
- kanban
- Claude/Codex 교차검토
- 장기 multi-agent 운영

---

## 8. 제품 철학 / Ex 헌장 후보

제품 철학은 v0.1부터 고정해야 한다.

영문 버전:

```text
Every code change must become audit evidence.
Every agent task must become a Run.
Every Run must connect to traceability.
Every Gate must produce reviewable deliverables.
Every deliverable must be exportable for audit.
```

한국어 버전:

```text
모든 코드 변경은 감리 증적이 되어야 한다.
모든 에이전트 작업은 Run으로 남아야 한다.
모든 Run은 추적성에 연결되어야 한다.
모든 Gate는 검토 가능한 산출물을 만들어야 한다.
모든 산출물은 제출 패키지로 export 가능해야 한다.
```

이 문장을 Ex의 헌장처럼 둘 수 있다.

---

## 9. 결론

어렵지만 방향은 명확하다.

Ex는 "문서 자동화 도구"도 아니고, "AI 코딩 에이전트 프레임워크"만도 아니다.

Ex는 둘을 묶은 다음 형태가 되어야 한다.

```text
감리 가능한 멀티에이전트 SI 수행 프레임워크
```

내년에 엔터프라이즈 SI에 넣으려면, Ex의 가치는 다음 문장으로 설명되어야 한다.

```text
AI 에이전트로 개발 속도를 높이되,
감리 산출물·추적성·증적·승인 흐름이 무너지지 않게 하는 SI Delivery Orchestrator.
```

현재 샘플은 멀티에이전트 구현까지 완성한 것은 아니지만, 감리 산출물과 코드 생성 흐름이 연결될 수 있다는 가능성을 이미 상당 부분 보여준다.

따라서 다음 단계는 다음이다.

```text
이미 나온 산출물 중심 흐름을 기반으로,
Run Protocol, Module Slicing, Build Wave, Adapter, Dashboard, Export를 단계적으로 붙여
반복 가능한 엔터프라이즈 SI Delivery Orchestrator로 발전시키는 것.
```
