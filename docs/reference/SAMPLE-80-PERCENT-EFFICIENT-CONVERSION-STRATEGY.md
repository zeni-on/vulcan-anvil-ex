# Sample 80 Percent Efficient Conversion Strategy

> 상태: reference draft v0.1
> 목적: 현재 Ex 샘플이 이미 산출물과 코드 측면에서 상당한 수준의 end-to-end 가능성을 보여준다는 전제에서, 다음 단계가 "새로 만드는 것"이 아니라 "더 효율적으로 반복 가능하게 전환하는 것"임을 정리한다.
> 관련 문서: `docs/SAMPLE_ANVIL_EX_CODEX_3_REVIEW.md`, `docs/reference/SI-SEQUENTIAL-GATE-MODULE-PARALLEL-IDEAL.md`, `docs/reference/HERMES-ORCHESTRATOR-ADAPTER-IDEAL.md`, `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md`

## 1. 핵심 관점

현재 `sample-anvil-ex-codex-3`는 단순한 데모가 아니다.

이 샘플은 Vulcan-Anvil Ex가 다음을 실제로 한 바퀴 돌릴 수 있다는 증거에 가깝다.

- Phase / Gate 진행
- Run 단위 작업 기록
- 요구사항, 설계, 테스트, QA, 릴리즈 산출물 작성
- 요구사항-설계-구현-테스트-증적 추적성 관리
- 독립 검수와 FIND 보강 루프
- QA Evidence 수집
- 실제 애플리케이션 코드 생성
- Gate 5 승인/인수인계 흐름

따라서 다음 버전의 방향은 "0에서 1을 새로 만드는 것"이 아니라, 이미 80% 정도 입증된 흐름을 더 효율적이고 반복 가능한 수행 체계로 전환하는 것이다.

여기서 80%는 엄밀한 기능 커버리지 수치라기보다 전략적 판단이다.

```text
샘플은 이미 Ex가 감리형 산출물과 코드 생성 흐름을 끝까지 만들 수 있음을 보여준다.
남은 일은 그 흐름을 더 짧은 시간, 더 낮은 비용, 더 명확한 역할 분담, 더 좋은 재현성으로 반복하게 만드는 것이다.
```

## 2. 현재 샘플이 이미 증명한 것

`docs/SAMPLE_ANVIL_EX_CODEX_3_REVIEW.md` 기준 샘플은 다음 특징을 가진다.

- 전체 Gate가 완료된 end-to-end 샘플이다.
- Run 문서가 `RUN-001`부터 `RUN-022`까지 남아 있다.
- Review 관련 Markdown과 QA 증적이 존재한다.
- Java backend, Vue frontend, 테스트 코드, Playwright 증적이 함께 존재한다.
- `check-trace`가 성공한 기록이 있다.
- 독립 검수에서 FIND가 나오고, 별도 Run으로 보강된 흐름이 있다.

이는 일반적인 AI 코딩 샘플과 다르다.

일반적인 AI 코딩 샘플은 코드 결과만 남고, 다음 질문에 약하다.

- 어떤 요구사항을 구현했는가?
- 어떤 설계를 따랐는가?
- 어떤 테스트로 검증했는가?
- 화면 증적은 어디 있는가?
- 누가 검수했고 어떤 FIND가 나왔는가?
- 승인 전 미해결 항목은 무엇인가?

반면 현재 Ex 샘플은 이 질문들에 답할 수 있는 구조를 이미 상당 부분 가지고 있다.

따라서 Ex의 다음 과제는 산출물 개수를 더 늘리는 것이 아니라, 이 구조가 더 적은 마찰로 반복되게 만드는 것이다.

## 3. 현재 80%와 남은 20%의 성격

현재 80%는 다음을 의미한다.

| 영역 | 현재 샘플 상태 | 판단 |
| --- | --- | --- |
| Gate 흐름 | Phase 0부터 Gate 5까지 완료 흔적 존재 | 가능성 입증 |
| 산출물 | 요구사항, 설계, 테스트, QA, 추적성, 승인 문서 존재 | 감리 대응 뼈대 존재 |
| 코드 | Backend/Frontend/Test가 실제로 생성됨 | 코드 생산 가능성 입증 |
| Traceability | `check-trace` 성공 기록 존재 | 핵심 가치 입증 |
| Evidence | Playwright screenshot과 QA 결과서 존재 | 증적 관리 가능성 입증 |
| Review loop | FIND 발생 후 보강 Run 존재 | 프레임워크형 검수 루프 입증 |
| Multi-agent | Codex-main 중심 성격이 강함 | 다음 단계 개선 필요 |
| 재현성 | 실행 권한, Java/Node 환경, dependency 이슈 존재 | 제품화 전 보강 필요 |
| 코드 구조 | 일부 파일이 큼, 특히 `App.vue` | 샘플 품질 개선 필요 |
| 반복 효율 | 사람이/에이전트가 매번 많이 작성해야 함 | 자동화와 템플릿화 필요 |

남은 20%는 단순히 기능을 더 붙이는 일이 아니다.

남은 20%의 핵심은 다음이다.

```text
End-to-end 가능성을 repeatable delivery system으로 바꾸는 것.
```

즉 한 번 성공한 샘플을 다음 프로젝트에서도 빠르고 안정적으로 재현할 수 있어야 한다.

## 4. "새로 만들기"가 아니라 "효율 전환"이다

앞으로의 작업을 다음처럼 이해하면 좋다.

```text
Before:
  에이전트가 긴 대화와 많은 문서 작성을 통해 샘플을 끝까지 만든다.

After:
  Ex가 Gate, Run, 산출물, 추적성, 증적, Build Wave의 기본 뼈대를 제공하고,
  에이전트는 승인된 Run 계약 안에서 필요한 부분만 빠르게 채운다.
```

즉 목표는 더 많은 문서를 손으로 쓰게 하는 것이 아니다.

목표는 다음이다.

- 반복되는 산출물 구조는 템플릿과 생성기로 만든다.
- 에이전트는 판단과 구체화가 필요한 부분에 집중한다.
- 모든 코드 변경은 자동으로 Run, test, evidence, traceability와 연결된다.
- Orchestrator는 전체 흐름과 승인 조건을 통제한다.
- Dashboard와 export는 사람이 볼 수 있는 상태를 빠르게 제공한다.

핵심 전환 문장:

```text
Ex는 산출물을 많이 쓰게 하는 도구가 아니라,
코드 생산 과정이 자연스럽게 감리 가능한 산출물과 증적으로 남게 하는 도구여야 한다.
```

## 5. 두 개의 엔진으로 나누어 보기

Ex의 효율 전환은 두 엔진을 분리해서 보면 명확하다.

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

### 5.1 Audit Backbone

Audit Backbone은 보수적이어야 한다.

담당:

- Gate 의미와 전환 조건
- 산출물 최소 세트
- 문서 메타데이터와 버전
- Traceability Matrix
- Evidence 목록
- FIND / CR / ISSUE 분류
- 승인/보류/이월 판단
- 제출 패키지 manifest

이 영역은 빠르게 바뀌면 안 된다.
엔터프라이즈 SI와 감리 대응의 신뢰성이 여기에 달려 있다.

### 5.2 Agent Execution Engine

Agent Execution Engine은 효율적이고 병렬화 가능해야 한다.

담당:

- 모듈 분해
- Build Wave 계획
- worker/persona 배정
- 코드 구현
- 테스트 실행
- 독립 검수
- 화면/로그/테스트 증적 수집
- 산출물 갱신 제안

이 영역은 runtime별로 달라질 수 있다.
Codex, Claude, Gemini, Hermes profile, kanban worker는 이 계층에 붙는다.

중요한 것은 Agent Execution Engine이 Audit Backbone을 우회하지 않는 것이다.

## 6. Run Protocol이 두 세계를 연결한다

Run은 단순 작업 메모가 아니라, Audit Backbone과 Agent Execution Engine을 연결하는 계약이어야 한다.

권장 정의:

```text
Run =
  작업 지시서
  + agent 실행 단위
  + 산출물 변경 기록
  + 코드 변경 기록
  + 테스트/증적 기록
  + traceability delta
  + audit evidence
  + 미해결 FIND/CR/ISSUE
```

앞으로의 효율화는 Run을 중심으로 해야 한다.

안 좋은 방향:

```text
에이전트에게 "기능 만들어줘"라고 지시한다.
완료 후 사람이 문서와 증적을 나중에 맞춘다.
```

좋은 방향:

```text
Run 계약 안에 관련 ID, 수정 범위, 테스트 기준, 증적 요구, traceability 갱신 요구를 넣는다.
에이전트는 그 계약 안에서 구현하고, 결과를 Run output으로 남긴다.
Orchestrator가 검증 후 Gate/산출물/추적성에 반영한다.
```

예시:

```yaml
run_id: RUN-0XX
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

이 구조가 잡히면 문서와 코드가 따로 놀지 않는다.

## 7. 효율 전환의 우선순위

### P0. 대표 샘플 품질 정리

목표: 현재 샘플을 Ex의 "Golden Sample" 후보로 만든다.

작업:

1. 샘플 README 정리
   - 샘플 목적
   - Gate 진행 요약
   - 실행 방법
   - 테스트 방법
   - 산출물 보는 법
   - 증적 위치
   - 알려진 백로그
2. 빌드 재현성 보강
   - `gradlew` 실행 권한
   - Java/Node prerequisite
   - frontend dependency 설치 절차
   - 검증 명령 묶음
   - 가능하면 Docker/devcontainer
3. 환경 의존 경로 정리
   - Windows 절대 경로 제거 또는 마스킹
   - export 가능한 샘플 상태 구성
4. 코드 첫인상 개선
   - 큰 Vue 파일 분리
   - composable/type/component 분리
   - 테스트 의도 주석 보강

### P1. 산출물 생성/검증 자동화

목표: 사람이 반복 작성하는 부분을 줄인다.

작업:

1. `init` 시 최소 산출물 tree와 manifest 생성
2. Gate별 required deliverables 검사 강화
3. Run 생성 시 관련 ID와 산출물 위치 자동 제안
4. `check-trace`, `run-check`, `check-deliverables`를 Gate exit 조건과 연결
5. export manifest를 통해 제출 패키지 생성 가능성 확보

### P2. Run-first 실행 효율화

목표: 에이전트가 매번 긴 설명 없이 표준 Run 계약으로 움직이게 한다.

작업:

1. Run input/output schema 정리
2. persona별 completion checklist 정리
3. Build Wave Run template 추가
4. Review Run template 추가
5. Evidence Run template 추가
6. Run 결과에서 traceability delta를 추출하는 규칙 추가

### P3. Multi-runtime 역할 분담

목표: Codex-main 샘플을 넘어 runtime별 강점을 보여준다.

예시:

- Codex: build / code modification
- Claude: design review / independent review
- Gemini: broad consistency check 또는 alternative review
- Hermes: top-level orchestration, profile/kanban/cron coordination

중요 원칙:

```text
런타임이 많아지는 것이 목적이 아니다.
Run 계약을 통해 역할 분담이 명확해지고, 독립 검수와 병렬 구현의 신뢰성이 높아져야 한다.
```

### P4. Dashboard와 Export는 상태 관측/제출 보조로 붙인다

Dashboard는 Core 판단을 대신하지 않는다.
Dashboard는 사람이 다음을 빠르게 보게 해주는 관측 계층이다.

- 현재 Gate
- 산출물 completeness
- traceability coverage
- Run 상태
- Build Wave 상태
- FIND / CR / ISSUE 상태
- Evidence coverage
- 제출 패키지 준비도

Export는 원천 Markdown을 대체하지 않는다.
Export는 고객/감리 제출용 합본을 생성하는 단계다.

## 8. 0.1 재정의: Audit-first Multi-Agent Delivery Kernel

현 시점에서 Ex의 v0.1 방향은 다음처럼 정의하는 것이 좋다.

```text
Vulcan-Anvil Ex 0.1 = Audit-first Multi-Agent Delivery Kernel
```

0.1에서 중요한 것은 거대한 자동화가 아니다.
중요한 것은 작은 샘플 하나가 끝까지 흐르는 것이다.

필수:

1. 감리 산출물 최소 세트
   - 요구사항
   - 설계
   - 테스트 케이스
   - 테스트 결과
   - 추적표
   - 릴리즈 승인/인수인계
   - 제출 패키지 manifest
2. Module Slicing
   - MOD-ID
   - 책임 범위
   - API/DB/화면/배치 연결
   - 병렬 가능 여부
   - 선행 의존성
3. Build Wave
   - Wave 계획
   - Wave별 Run
   - worker에게 넘길 작업 계약
   - Wave 완료 검증
4. Run Protocol
   - agent 작업 결과가 산출물/코드/테스트/증적으로 연결됨
5. CLI 중심 최소 실행
   - init
   - gate-start
   - run-new
   - run-check
   - check-trace
   - check-deliverables
   - wave-start
   - wave-complete
   - export-package

0.1에서 굳이 완성하지 않아도 되는 것:

- 완성형 Dashboard
- 완전 자동 DOCX/HWPX 생성
- 모든 runtime의 완전 동등 지원
- 대규모 kanban dispatcher
- 모든 산출물 템플릿의 완성도 100%
- 복잡한 UI evidence 자동화

## 9. Ex 헌장 후보

Ex의 제품 철학은 다음 문장으로 고정할 수 있다.

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

## 10. 제품 메시지

Ex는 단순한 문서 자동화 도구가 아니다.
Ex는 단순한 AI 코딩 에이전트 프레임워크도 아니다.

Ex의 위치는 다음에 가깝다.

```text
감리 가능한 멀티에이전트 SI 수행 프레임워크
```

또는:

```text
AI 에이전트로 개발 속도를 높이되,
감리 산출물, 추적성, 증적, 승인 흐름이 무너지지 않게 하는 SI Delivery Orchestrator.
```

현재 샘플은 이 메시지의 80%를 이미 보여준다.
다음 단계는 이 메시지가 매번 더 빠르고 안정적으로 재현되게 만드는 것이다.

## 11. 다음 작업 후보

가장 실용적인 다음 작업은 다음 순서가 좋다.

1. `sample-anvil-ex-codex-3`를 Golden Sample 후보로 정리한다.
2. 샘플 README, 실행 방법, 검증 명령, 증적 위치를 보강한다.
3. 샘플에서 반복 패턴을 추출해 Ex template/generator로 되돌린다.
4. Run input/output 계약을 더 엄격하게 만든다.
5. Build Wave와 Module Slicing을 CLI와 template에 연결한다.
6. Dashboard는 감리 준비도와 Run/Wave 상태를 보여주는 관측 계층으로 붙인다.
7. Codex-main + Claude-review 또는 Hermes-orchestrated sample로 멀티 런타임 설득력을 보강한다.

결론:

```text
Ex의 다음 버전은 더 많은 것을 새로 붙이는 버전이 아니라,
이미 성공한 샘플 흐름을 제품화 가능한 반복 시스템으로 압축하는 버전이어야 한다.
```
