# Run-first Multi-Agent Dispatcher 구상

> 상태: 장기 설계 메모.
> `0.4.0` 기준으로 `run-exec`, `agent-run --mode work`, `agent-run --mode review`, worktree 실행, worker 로그/증적 수집의 일부는 이미 구현되었다.
> 이 문서는 자동 큐, fan-in review, PR cross validation, lock/worktree 고도화를 검토할 때 참고한다. 현재 우선순위는 `docs/ROADMAP.md`를 따른다.

## 목적

Vulcan-Anvil Ex를 현재의 "멀티 런타임 대응 단일 오케스트레이터" 구조에서, Run을 중심으로 여러 에이전트가 독립적으로 작업하는 "멀티 에이전트 작업 운영체계"로 발전시키기 위한 설계 메모다.

이 문서는 Codex, Claude, Gemini 같은 개별 AI 런타임을 프로젝트의 주인으로 두지 않고, Vulcan의 Run Protocol과 Dispatcher를 중심에 두는 방향을 정리한다.

---

## 현재 구조 진단

현재 Vulcan-Anvil Ex는 Claude와 Codex 양쪽을 지원하지만, 실제 런타임 주도권은 사용자가 어느 세션으로 프로젝트를 열었는지에 따라 결정된다.

예:

- Claude로 프로젝트를 열면 Claude가 메인 Orchestrator가 된다.
- Codex로 프로젝트를 열면 Codex가 메인 Orchestrator가 된다.
- 두 런타임은 같은 Core 규칙과 문서를 읽을 수 있다.
- 하지만 동시에 팀처럼 병렬로 움직이는 구조는 아니다.
- 결국 현재 활성 세션 하나가 전체 작업의 왕이 된다.

따라서 현재 구조는 엄밀히 말하면 진짜 멀티에이전트 시스템이라기보다 다음에 가깝다.

> 어느 런타임으로 들어와도 같은 프로세스를 흉내 낼 수 있는 단일 Orchestrator 프레임워크

이 구조는 v0.2.x 단계에서는 현실적이고 안정적이다. 다만 사용자가 기대하는 "여러 에이전트가 각자 역할을 맡아 협업하는 느낌"은 아직 약하다.

---

## 멀티에이전트처럼 느껴지기 위한 조건

진짜 멀티에이전트 작업 흐름으로 보이려면 최소한 다음 요소가 필요하다.

### 1. 중앙 작업 큐

누가 메인 세션인지와 무관하게 작업 카드 또는 Run이 중앙 큐에 올라가야 한다.

예:

- build-backend
- build-frontend
- review
- security-review
- evidence
- ui-review

### 2. 독립 worker

각 AI 런타임은 Orchestrator의 하위 실행기로 동작해야 한다.

예:

- Codex worker
- Claude worker
- Gemini worker
- Review worker
- Evidence worker

### 3. fan-out / fan-in

Orchestrator는 일을 쪼개고, 여러 worker는 병렬로 작업한 뒤, 결과는 다시 Run/Review/Evidence로 모여야 한다.

흐름:

```text
Orchestrator
  -> 여러 Run 생성
  -> 여러 worker가 병렬 수행
  -> 결과 수집
  -> Review 또는 통합 판단
```

### 4. ownership 분리

역할별 책임이 분리되어야 한다.

- 구현자는 build만 수행한다.
- reviewer는 review만 수행한다.
- evidence worker는 증적 수집만 수행한다.
- 최종 승인 판단은 Orchestrator 또는 Human Approver가 수행한다.

### 5. session 독립성

특정 채팅창 또는 특정 AI CLI가 전체 프로젝트의 왕이 아니어야 한다.

예:

- Claude 세션에서 시작한 작업도 Codex worker가 구현할 수 있어야 한다.
- Codex 세션에서 시작한 작업도 Claude worker가 리뷰할 수 있어야 한다.
- 사용자의 진입점과 실제 실행 worker는 분리되어야 한다.

---

## 이미 존재하는 기반

Vulcan-Anvil Ex에는 멀티에이전트 구조로 확장할 수 있는 기반이 이미 있다.

현재 기반:

- `session.json`
- `docs/runs/`
- `docs/reviews/`
- `review-request`
- `review-run`
- Build Wave
- persona
- Run input/output contract
- Codex adapter
- Claude adapter

즉 멀티에이전트의 "상태판" 또는 "작업 계약 문서"는 어느 정도 준비되어 있다.

부족한 핵심은 실행 Dispatcher다.

현재 흐름:

```text
사용자
  -> Claude/Codex 세션
  -> 그 세션이 Orchestrator 역할 수행
```

목표 흐름:

```text
사용자
  -> Vulcan Orchestrator/Dispatcher
  -> Codex worker / Claude worker / Review worker / Evidence worker
```

---

## 핵심 전환: Runtime-first에서 Run-first로

현재 구조는 Runtime-first에 가깝다.

```text
Claude session = Orchestrator + worker
Codex session = Orchestrator + worker
```

목표 구조는 Run-first여야 한다.

```text
Run = 작업 계약
Runner = 실행기
Orchestrator = 계약 생성, 검증, 판단 역할
```

즉 Claude, Codex, Gemini는 프로젝트의 주인이 아니라 Run을 수행하는 adapter/runner 중 하나가 되어야 한다.

중요한 원칙:

> Agent Run Protocol은 특정 모델이나 제품의 사용법이 아니다.

이 원칙대로라면 Run이 중심이어야 하고, Codex/Claude/Gemini는 Run을 수행하는 실행기로 내려가야 한다.

---

## 단계별 발전 방향

## 1단계: 현재 구조 유지 + 교차 검수 강화

가장 안정적인 단기 방향이다. 현재 구조를 크게 바꾸지 않고도 멀티 런타임 효과를 낼 수 있다.

예: Claude 중심 세션

```text
Claude Orchestrator
  -> 구현 또는 Run 생성
  -> Gate 2/Gate 4 전 review-request
  -> review-run --runner codex-cli
  -> Codex 독립 검수
  -> Claude가 검수 결과를 읽고 최종 판단
```

예: Codex 중심 세션

```text
Codex Orchestrator
  -> 구현 또는 Run 생성
  -> Claude에게 handoff/review 요청
  -> Codex가 Claude 결과를 읽고 최종 판단
```

이 단계의 성격:

- 진짜 멀티에이전트보다는 "메인 1명 + 외부 검수자" 구조다.
- 구현 난이도가 낮다.
- 현재 Run/Review 문서 구조와 잘 맞는다.
- v0.2.x에서 가장 현실적인 개선이다.

---

## 2단계: `run-exec` 추가

멀티에이전트 느낌을 크게 키울 수 있는 최소 기능이다.
`review-run`은 `run-exec`의 특수한 review 실행으로 볼 수 있다.
따라서 Codex와 Claude 모두 같은 runner 추상화를 사용하고, 실행 유형만 `review`, `build`, `evidence`로 나누는 방향이 맞다.

예상 명령:

```bash
python vulcan.py run-exec --run-id RUN-004 --runner codex-cli
python vulcan.py run-exec --run-id RUN-005 --runner claude-cli
```

또는 persona 기반 실행:

```bash
python vulcan.py run-exec --persona build --runner codex-cli
python vulcan.py run-exec --persona review --runner claude-cli
```

이 기능이 들어가면 Orchestrator가 꼭 자기 런타임에서 모든 일을 직접 하지 않아도 된다.

예:

```text
RUN-010 build-backend    -> codex-cli
RUN-011 build-frontend   -> claude-cli
RUN-012 ui-review        -> claude-cli
RUN-013 security-review  -> codex-cli
RUN-014 evidence         -> codex-cli
```

핵심 원칙:

1. Run은 먼저 파일로 존재한다.
2. runner는 Run을 읽고 수행한다.
3. runner는 Run output contract에 맞춰 결과를 쓴다.
4. Orchestrator는 결과를 검증하고 다음 Run을 만든다.

이 단계부터 사용자가 Claude로 들어왔는지 Codex로 들어왔는지는 덜 중요해진다.

---

## 3단계: `dispatch` 또는 `worker` 추가

진짜 멀티에이전트 느낌은 이 단계에서 나온다.

예상 명령:

```bash
python vulcan.py dispatch
```

Dispatcher의 역할:

1. `docs/runs/`에서 status가 `Ready`인 Run을 찾는다.
2. persona와 runner 매핑을 확인한다.
3. 서로 충돌하지 않는 Run은 병렬 실행한다.
4. 완료되면 결과를 수집한다.
5. 실패, 질문, 차단 상태를 갱신한다.
6. 필요한 경우 후속 review Run 또는 fan-in Run을 생성한다.

예상 설정:

```json
{
  "runtime": {
    "available_runners": [
      {
        "name": "codex-cli",
        "model": "gpt-5.5",
        "effort": "high"
      },
      {
        "name": "claude-cli",
        "model": "claude-opus-4-7",
        "effort": "high"
      }
    ]
  },
  "concurrency": 2,
  "isolation": {
    "worktree": true,
    "readonly_review": true
  }
}
```

목표 구조:

```text
사용자
  ↓
Orchestrator
  ↓
docs/runs/RUN-xxx
  ↓
Dispatcher
  ├─ Codex worker: build-backend
  ├─ Claude worker: build-frontend
  ├─ Claude worker: ui-review
  ├─ Codex worker: test/evidence
  └─ Claude worker: final review
  ↓
Run 결과 / Review 결과 / Evidence
  ↓
Orchestrator 통합 판단
```

---

## 추천 기능 목록

멀티에이전트 구조로 발전시키기 위해 우선순위가 높은 기능은 다음과 같다.

### 1. `run-exec`

단일 Run을 특정 runner로 실행한다.

```bash
python vulcan.py run-exec --run-id RUN-001 --runner codex-cli
```

### 2. runner selection

persona 또는 Run type의 runner는 `runtime.available_runners`에서 자동 선택한다.
프로젝트 설정에는 가능한 runner 목록만 둔다.

예:

```json
{
  "runtime": {
    "available_runners": [
      {
        "name": "codex-cli",
        "model": "gpt-5.5",
        "effort": "high"
      },
      {
        "name": "claude-cli",
        "model": "claude-opus-4-7",
        "effort": "high"
      }
    ]
  }
}
```

선택 규칙:

```text
runner 0개 -> manual
runner 1개 -> 모든 실행을 해당 runner로 수행
codex-cli + claude-cli ->
  build-backend/evidence = codex-cli 우선
  build-frontend/review/pr-cross-validation = claude-cli 우선
  PR/Gate 교차검증 = 작성 runner와 다른 runner 우선
```

### 3. `dispatch`

Ready 상태의 Run을 자동으로 실행한다.

```bash
python vulcan.py dispatch
```

### 4. run status

Run lifecycle을 명시한다.

추천 상태:

- Draft
- Ready
- Running
- Blocked
- Completed
- Failed
- Cancelled

### 5. lock/worktree

동시에 실행되는 Run 간 파일 충돌을 막는다.

옵션:

- Run별 git worktree 생성
- writable path 제한
- review 계열 Run은 readonly 모드
- 동일 파일 수정 Run은 병렬 실행 금지
- build 계열 Run은 브랜치 worktree를 사용한다.
- review 계열 Run은 detached/readonly worktree를 사용하고 PR을 만들지 않는다.
- build worktree 결과는 Orchestrator 검증 후 draft PR로 만든다.
- PR은 작성 runner와 다른 runner가 교차검토한다.

권장 PR 흐름:

```text
RUN-010 build-backend / codex-cli
  -> branch worktree
  -> Orchestrator 검증
  -> draft PR
  -> claude-cli 교차검토

RUN-011 build-frontend / claude-cli
  -> backend API 계약 반영
  -> branch worktree
  -> Orchestrator 검증
  -> draft PR
  -> codex-cli 교차검토
```

### 6. fan-in review

여러 Run이 완료된 뒤 통합 Review Run을 자동 생성한다.

예:

```text
RUN-010 build-backend 완료
RUN-011 build-frontend 완료
  -> RUN-012 integration-review 자동 생성
```

### 7. PR cross validation

Build Run이 PR을 만들면 PR 자체도 교차검증 대상이 된다.

```text
RUN-010 build-backend 완료
  -> draft PR 생성
  -> RUN-012 pr-cross-validation / claude-cli

RUN-011 build-frontend 완료
  -> draft PR 생성
  -> RUN-013 pr-cross-validation / codex-cli
```

PR 교차검증은 다음을 입력으로 본다.

- PR diff
- 관련 Build Wave Run
- CI 결과
- 테스트 결과서
- Playwright 증적
- 추적표 delta
- unresolved review thread

PR 교차검증 결과는 merge가 아니라 Orchestrator 판단 후보로 남긴다.

- merge 후보
- `FIND`
- `CR`
- `ISSUE`

---

## 설계상 주의할 점

### Orchestrator는 모델이 아니라 역할이어야 한다

Claude와 Codex는 Orchestrator 역할을 수행할 수 있지만, 프레임워크 관점에서는 특정 모델이 Orchestrator에 고정되어서는 안 된다.

권장 개념:

```text
Orchestrator Role
Runner Adapter
Human Approver
```

### Runner는 계약을 수행해야 한다

Runner가 자유롭게 프로젝트를 해석해서 일하면 안 된다. 반드시 Run 문서를 입력 계약으로 읽고, output contract에 맞춰 결과를 남겨야 한다.

### Review와 Build는 분리해야 한다

Build worker가 자기 작업을 최종 승인하면 멀티에이전트 구조의 의미가 약해진다. 최소한 중요한 Gate에서는 독립 review worker가 필요하다.

### 병렬성보다 충돌 방지가 먼저다

초기에는 과도한 병렬 실행보다 안전한 직렬 실행이 낫다. Dispatcher v1은 concurrency 1 또는 2로 시작하고, 파일 충돌 감지와 worktree 격리가 안정화된 뒤 확장하는 편이 좋다.

---

## 한 줄 결론

현재 Vulcan-Anvil Ex는 멀티에이전트라기보다 "멀티 런타임 대응 단일 오케스트레이터"에 가깝다.

하지만 이미 Run, Review, persona, adapter, session 상태판의 기반이 있으므로, `Run Queue + Dispatcher + Runner mapping`을 추가하면 Run-first 멀티에이전트 구조로 자연스럽게 발전할 수 있다.
