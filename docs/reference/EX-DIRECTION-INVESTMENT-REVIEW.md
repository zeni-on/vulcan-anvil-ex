# Ex Direction and Investment Review

> Status: draft v0.1  
> 작성일: 2026-06-03  
> 목적: Vulcan-Anvil Ex가 계속 투자할 가치가 있는 개발 프레임워크인지, 그리고 앞으로 어떤 방향으로 비용을 투입해야 하는지 판단 기준을 정리한다.

## 1. 질문

Vulcan-Anvil Ex는 일반적인 AI coding 도구처럼 빠르게 코드를 생성하는 것을 1차 목표로 두지 않는다.

따라서 다음 질문을 주기적으로 다시 확인해야 한다.

- Ex는 정말 효과적인 개발 프레임워크인가?
- AI agent coding을 이렇게 Gate, Run, traceability, QA evidence 중심으로 운영하는 방향이 맞는가?
- 다른 AI coding 도구들이 더 빠르게 구현하는 상황에서 Ex에 계속 비용을 투입할 이유가 있는가?
- 현재 느린 체감이 제품의 실패 신호인가, audit/profile 특성상 자연스러운 비용인가?

## 2. 현재 판단

현재 판단은 다음과 같다.

> Ex의 방향은 맞다.  
> 다만 Ex는 빠른 코딩 도구가 아니라, AI가 만든 결과를 프로젝트 산출물로 통제하는 프레임워크다.

Ex는 Codex, Claude, Antigravity/Gemini, Cursor 같은 AI coding 도구와 같은 층에서 경쟁하면 안 된다.

그 도구들은 다음에 강하다.

- 코드베이스 탐색
- 구현 계획
- 코드 작성
- 테스트 실행
- 오류 수정
- 짧은 리뷰

Ex가 겨냥해야 하는 영역은 다르다.

- 요구사항과 인수기준을 대화창 밖에 남긴다.
- 설계, API, DB, UI, Program contract를 구현과 연결한다.
- 테스트 계획과 실제 QA 증적을 분리해 관리한다.
- Gate별 승인 지점을 명확히 한다.
- worker, subagent, 외부 runner가 만든 결과를 Run 문서와 traceability로 회수한다.
- 감리, 인수인계, 장기 유지보수에서 설명 가능한 근거를 남긴다.

한 문장으로 정리하면 다음이다.

> Ex는 AI coding accelerator가 아니라 AI coding governance framework다.

또는 더 실무적으로는 다음과 같다.

> Ex는 AI가 코딩한 결과를 요구사항, 설계, 테스트, 증적, 승인 흐름으로 묶어주는 프레임워크다.

## 3. Ex가 효과적인 조건

Ex는 모든 프로젝트에 같은 효과를 주지 않는다.

효과가 큰 조건은 다음이다.

| 조건 | 이유 |
| --- | --- |
| 감리, 고객 검수, 보안 검토, 인수인계가 필요한 프로젝트 | 코드 결과뿐 아니라 산출물, 증적, 승인 이력이 필요하다. |
| PM/기획/개발/QA/리뷰어 관점이 나뉘는 프로젝트 | 각 관점의 판단을 Run과 traceability로 남길 수 있다. |
| 여러 agent 또는 여러 runtime을 섞는 프로젝트 | Codex, Claude, AGY 결과를 하나의 Core 규칙으로 회수할 수 있다. |
| 장기간 유지보수되는 SI/솔루션 프로젝트 | 변경 영향, 요구사항 연결, 테스트 증거가 시간이 지나도 남는다. |
| 사용자가 최종 판단자이고 agent가 실행자인 구조 | Gate 승인과 QA 판정을 사람이 통제할 수 있다. |

효과가 작거나 과한 조건은 다음이다.

| 조건 | 이유 |
| --- | --- |
| 하루짜리 throwaway prototype | 문서와 Gate 비용이 구현 비용보다 커질 수 있다. |
| 요구사항 추적이 필요 없는 개인 실험 | PoC profile이 아니면 절차가 무겁다. |
| 이미 조직 표준 ALM/QA/감리 도구가 강하게 자리 잡은 팀 | Ex가 중복 체계가 될 수 있다. |
| 결과 품질보다 즉시 동작하는 데모가 중요한 작업 | 일반 AI coding tool이 더 빠를 수 있다. |

## 4. 현재 위험 신호

지금까지 샘플 프로젝트에서 확인된 위험은 다음이다.

1. Run 문서가 worker에게 너무 장황하게 전달될 수 있다.
2. traceability ID가 여러 문서에 중복 기록되면서 정합성 비용이 커진다.
3. Gate 4 QA에서 테스트 실행, 원인 분석, 수정, 재검증이 섞이면 시간이 급격히 늘어난다.
4. Orchestrator가 직접 구현하거나 직접 수정하면 worker 분리의 의미가 약해진다.
5. worker timeout, 결과 회수, transcript fallback이 안정되지 않으면 장시간 대기가 생긴다.
6. Audit profile 기준을 모든 프로젝트에 적용하면 Ex가 무겁고 느린 도구로 보인다.
7. 에이전트 간 잦은 context 전환과 계약 문서 전송으로 API 비용, token 사용량, 대기 시간이 커질 수 있다.
8. LLM 또는 CLI runtime의 버전 변경으로 출력 계약, transcript 형식, permission 흐름이 바뀌면 worker 회수 로직이 깨질 수 있다.
9. 승인자가 모든 문서와 Run 결과를 계속 읽어야 한다면 review fatigue가 생기고, 결국 형식적 승인으로 흐를 수 있다.
10. Jira, GitLab, Jenkins, 사내 ALM 같은 기존 도구와 역할이 겹치면 이중 거버넌스 비용이 발생할 수 있다.

이 신호는 Ex의 방향이 틀렸다는 뜻이라기보다, 다음 방향으로 조정해야 한다는 뜻이다.

> 더 많은 규칙이 아니라, 더 적은 반복과 더 강한 자동 검증이 필요하다.

## 5. 투자 방향

앞으로의 투자는 기능 추가보다 다음에 집중한다.

### 5.1 Profile별 무게 조절

Ex는 최소 세 가지 profile을 분리해서 운영한다.

| Profile | 목적 | 운영 강도 |
| --- | --- | --- |
| `audit` | 감리, 인수인계, 장기 유지보수 | 가장 강함 |
| `solution` | 제품/솔루션 개발, 반복 릴리즈 | 중간 |
| `poc` | 가능성 검증, 기술 실험 | 낮음 |

중요한 원칙:

> PoC는 낮은 품질 모드가 아니다. 문서 깊이와 증적 밀도가 낮은 모드다.

PoC profile이 실제로 가벼워지려면 단순히 "문서를 적게 쓴다"로 끝나면 안 된다.

PoC에서는 다음 경량화 메커니즘을 우선 적용한다.

- trace depth를 기본 1로 제한한다.
- worker Run의 `source_documents`를 직접 관련 문서 중심으로 제한한다.
- Gate 4 수준의 상태별 화면 증적과 독립검수는 필요할 때만 명시한다.
- 실패한 항목을 Pass로 바꾸지 않고 PoC 판단 항목 또는 제품화 전환 보강 항목으로 남긴다.
- Audit profile의 제출/감리용 반복 설명을 worker Run에 반복하지 않는다.

### 5.2 Run 입력 계약 경량화

worker에게 주는 Run은 실행에 필요한 계약만 담아야 한다.

- 필요한 `target_contracts`
- 좁은 `scope.writable`
- 필요한 source/reference 문서
- 구현해야 할 interface/class/method/API/DTO 계약
- 실행해야 할 검증 명령
- 금지 행동

Orchestrator 운영 규칙, 전체 프로토콜, 장기 정책은 Run마다 반복하지 않는다.

### 5.3 Trace graph 기반 자동 추천

관련 ID를 사람이 여러 문서에서 긁어오지 않고, Traceability Matrix를 graph 원장으로 사용한다.

- `trace-context`
- `--trace-seed`
- `related_ids` 추천
- `target_contracts` 추천
- source document 추천

Orchestrator는 추천값을 검토하고 `scope.writable`, interface contract, 검증 명령을 확정한다.

### 5.4 QA 안정화

Gate 4는 Ex의 가치가 가장 잘 드러나는 곳이지만, 비용도 가장 크다.

따라서 다음 원칙을 유지한다.

- QA worker는 테스트 실행자다.
- QA worker는 발견 즉시 수정하지 않는다.
- 실패는 FIND, CR, ISSUE, environment_blocked 후보로 기록한다.
- 수정은 승인 후 별도 `qa-fix-loop` Run으로 진행한다.
- QA-000 workspace를 QA-001~QA-003이 재사용한다.

### 5.5 자동 측정과 성능 관리

Ex가 느린지 빠른지는 감으로 판단하지 않는다.

측정해야 할 항목:

- Gate별 wall-clock
- Run별 worker duration
- QA-Fix 왕복 횟수
- timeout/watchdog 이벤트
- Orchestrator 보정량
- `run-check`, `check-trace`, `check-contract` 실패 유형
- profile별 평균 비용
- profile 전환 시 문서량, wall-clock, worker duration 감소율
- trace graph 추천값의 수용, 수정, 기각 비율
- Gate/Run별 token 또는 API 비용을 확인할 수 있는 경우의 비용 추정
- 승인자 대기 시간과 재승인 왕복 횟수
- 산출물이 실제 감리, 인수인계, release note, QA 판단에 재사용된 횟수

특히 `trace-context`와 `--trace-seed`는 추천 기능이므로, 추천이 맞았는지도 측정해야 한다.
추천 정확도가 낮으면 자동화가 오히려 Orchestrator 보정량을 늘릴 수 있다.

### 5.6 Adapter-agnostic Core 유지

AI coding 도구는 빠르게 발전한다.
Codex, Claude, Cursor, Antigravity/Gemini가 traceability, evidence, review 기능을 자체적으로 흡수할 가능성도 있다.

따라서 Ex는 특정 runtime의 부속 기능이 되면 안 된다.

방어 전략은 다음이다.

- Gate, Run, traceability, QA evidence, release approval은 Core 규칙으로 둔다.
- Codex, Claude, AGY, 향후 runtime은 adapter로만 붙인다.
- runtime별 skill/agent/prompt는 Core 규칙을 복제하지 않고 얇은 bootstrap으로 유지한다.
- 같은 Core Run을 서로 다른 runner가 수행해도 결과가 같은 산출물 계약으로 회수되는지 확인한다.
- adapter별 중복 규칙이 Core보다 커지면 구조를 다시 정리한다.

## 6. 계속 투자할 기준

다음 조건이 만족되면 계속 투자할 가치가 있다.

1. 샘플 프로젝트에서 Gate 완료 후 산출물, 코드, 테스트, 증적이 서로 추적된다.
2. 사용자가 Dashboard에서 현재 상태와 누락 항목을 이해할 수 있다.
3. Run 생성 시간이 줄고, worker가 작업지시서를 더 잘 이해한다.
4. QA 실패가 즉시 임의 수정으로 이어지지 않고, FIND/CR/ISSUE로 분류된다.
5. PoC profile에서는 일반 AI coding tool에 가까운 속도로 작은 실험을 진행할 수 있다.
6. Audit profile에서는 느리더라도 감리/인수인계에 설명 가능한 결과를 만든다.
7. 최소 3개 이상의 서로 다른 샘플 유형에서 같은 기준으로 완료/보류/실패 판단을 재현할 수 있다.
8. 사용자가 직접 읽어야 하는 문서량보다 Dashboard와 check 명령이 알려주는 판단 신호가 늘어난다.

## 7. 축소 또는 중단 신호

다음 신호가 2개 이상의 샘플 프로젝트에서 반복되거나, 한 프로젝트 안에서 같은 유형으로 3회 이상 반복되면 방향을 축소해야 한다.

1. 사용자가 산출물보다 절차 보정에 더 많은 시간을 쓴다.
2. worker가 Run 문서를 반복적으로 오해하고, Orchestrator가 대부분 직접 수정한다.
3. traceability 정합성 비용이 구현/QA 가치를 계속 압도한다.
4. PoC profile도 충분히 가벼워지지 않는다.
5. Dashboard가 판단을 돕기보다 정보만 많이 보여준다.
6. Core 규칙보다 adapter별 중복 규칙이 더 많아진다.
7. 기존 ALM/CI/CD 도구와 동기화하는 비용이 Ex가 제공하는 추적성과 증적 가치보다 커진다.
8. 승인자가 Run과 QA 결과를 형식적으로 승인하게 되어, 실제 거버넌스 효과가 사라진다.

이 경우 Ex는 전체 개발 프레임워크가 아니라 다음 중 하나로 축소할 수 있다.

- audit evidence generator
- traceability assistant
- Gate/Run documentation toolkit
- QA evidence manager

## 8. 결론

Ex는 일반 AI coding tool을 대체하려는 방향으로 가면 경쟁력이 약하다.

Ex가 가져야 할 정체성은 다음이다.

> AI가 빠르게 만든 코드를 프로젝트가 신뢰할 수 있는 산출물로 바꾸는 운영 프레임워크.

따라서 앞으로의 핵심 방향은 다음이다.

1. Audit profile은 설명 가능성을 유지한다.
2. PoC/Solution profile은 더 가볍게 만든다.
3. 규칙 추가보다 자동 추천과 자동 검증을 늘린다.
4. worker와 Orchestrator 역할을 분리한다.
5. Dashboard는 많은 정보보다 판단 가능한 신호를 보여준다.
6. 성능은 profile별로 측정하고 관리한다.

현재 결론:

> 계속 투자할 가치는 있다.  
> 다만 "더 단단하게"보다 "더 가볍고 자동으로"가 다음 투자 방향이다.
