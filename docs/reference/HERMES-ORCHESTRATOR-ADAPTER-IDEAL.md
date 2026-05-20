# Hermes Orchestrator Adapter Ideal

> 상태: ideal draft v0.1
> 목적: Vulcan-Anvil Ex Core 규약을 Hermes Agent 기반 오케스트레이션 흐름에 연결하는 이상적 방향을 정리한다. 이 문서는 아직 공식 Adapter 규약이 아니라, 향후 Hermes Adapter/Core/Dashboard 개선을 위한 참고 설계다.

## 1. 결론

Vulcan-Anvil Ex에서 메인 에이전트의 기본 역할은 Orchestrator다.

Hermes를 사용할 때도 핵심 구조는 바뀌지 않는다.

```text
Ex Core = 프로젝트 운영 규약의 단일 진실
Hermes = 상위 Orchestrator 런타임
Codex / Claude / Gemini / 다른 Hermes worker = 실행자 또는 검토자
Dashboard = 상태 관측과 승인 보조 UI
```

따라서 Hermes Adapter는 Core 규칙을 새로 정의하지 않는다.
Hermes Adapter는 Ex Core의 Gate, Run, persona, traceability, 승인 규칙을 Hermes 기능에 어떻게 매핑할지만 정의한다.

## 2. Core는 두껍게, Adapter는 얇게

Ex에서 반드시 Core에 남아야 하는 규칙은 다음이다.

- Gate 의미와 전환 조건
- Orchestrator 판단 루프
- persona 책임과 금지사항
- Run 상태와 출력 계약
- 요구사항 추적성 규칙
- FIND / CR / ISSUE 판단 기준
- Build Wave 규칙
- 독립 검수와 승인 조건
- Dashboard가 읽는 상태 모델

Adapter가 담당해야 하는 것은 다음처럼 실행 환경별 차이에 한정한다.

- 이 도구가 처음 읽는 진입 문서는 무엇인가?
- 이 도구에서 persona를 어떻게 표현하는가?
- Run 입력을 어떻게 전달하는가?
- Run 출력을 어떻게 회수해서 Core 형식으로 정규화하는가?
- 이 도구의 컨텍스트, 권한, 세션, 자동화 한계는 무엇인가?

Codex, Claude, Hermes용 문서가 모두 같은 Gate 규칙을 다시 정의하면 규약이 갈라진다.
그러므로 도구별 Adapter는 얇은 매핑 계층으로 유지한다.

## 3. 기존 Adapter와 Hermes Adapter의 차이

| 항목 | Codex/GPT | Claude | Hermes |
| --- | --- | --- | --- |
| 기본 진입 | `AGENTS.md` | `.claude/CLAUDE.md` | Hermes session, profile, skill, workdir context |
| persona 표현 | 프롬프트 주입 또는 subagent 전달문 | `.claude/agents/*.md` | `delegate_task`, profile, kanban worker, skill |
| 실행 단위 | Run 단위 지시 | 대화/agent/subagent 단위 | 현재 세션, 동기 subtask, durable queue, scheduled job |
| 장점 | 같은 workspace에서 구현/테스트/문서 갱신이 쉽다 | Claude 전용 agent/skill 생태계 활용 | 여러 모델, 도구, profile, queue, schedule을 한 Orchestrator가 묶을 수 있다 |
| 주의 | Core 규칙을 prompt에 명시해야 한다 | Claude 전용 구조가 Core보다 앞서면 안 된다 | Hermes 기능이 Ex Core 판단을 대체하면 안 된다 |

## 4. Hermes 기능의 역할

### 4.1 `delegate_task`

`delegate_task`는 현재 Hermes 세션 안에서 짧은 하위 작업을 다른 subagent에게 맡기는 기능이다.
부모 Orchestrator는 subagent가 끝날 때까지 기다린 뒤 결과 요약을 받는다.

특징:

- 동기 실행이다. 부모 Orchestrator가 결과를 기다린다.
- subagent는 별도 대화 컨텍스트와 별도 터미널 세션을 가진다.
- 여러 작업을 병렬로 보낼 수 있다.
- 오래 지속되는 작업에는 맞지 않는다. 부모 세션이 중단되면 subagent 작업도 취소될 수 있다.
- subagent 결과는 자기 보고이므로 Orchestrator가 다시 검증해야 한다.

Ex에서의 권장 용도:

- `review` persona로 특정 설계 문서나 diff를 읽기 중심 검토
- `security-review`, `ui-review`, `development-review`처럼 관점이 분리된 검토
- 서로 파일 범위가 겹치지 않는 작은 Build Run
- 요구사항 초안과 질문 후보를 병렬로 뽑는 탐색 작업
- 독립 검수 전 예비 검토

Ex에서의 금지 또는 주의:

- Gate 승인을 subagent 완료 보고만으로 확정하지 않는다.
- 같은 파일을 여러 subagent가 동시에 수정하게 하지 않는다.
- 구현자가 자기 구현을 최종 승인하게 하지 않는다.
- 실행하지 않은 테스트를 subagent 보고만 보고 통과로 기록하지 않는다.

Ex 매핑 예시:

```text
Orchestrator
-> delegate_task(review persona): Gate 2 산출물 누락 검토
-> delegate_task(security-review persona): 보안 기준선 검토
-> Orchestrator가 결과 재검증
-> FIND / CR / ISSUE 후보 분류
-> Run 결과와 traceability 갱신
```

### 4.2 `profile`

`profile`은 독립된 Hermes 실행 환경이다.
각 profile은 별도 config, 세션, memory, skills, tool 설정을 가질 수 있다.

특징:

- 같은 Hermes라도 profile마다 모델, provider, toolset, memory, skill 구성을 다르게 둘 수 있다.
- profile은 persona 그 자체가 아니라, persona를 안정적으로 수행하기 위한 실행 환경이다.
- 장기적으로 반복되는 역할에 적합하다.
- kanban dispatcher나 cron job이 특정 profile로 실행되도록 할 수 있다.

Ex에서의 권장 profile 예시:

| Profile | 역할 | 권장 성격 |
| --- | --- | --- |
| `ex-orchestrator` | 메인 진행자 | Core 규약, Gate 판단, Run 통합, 사용자 보고 |
| `ex-builder` | 구현자 | 코드/테스트 수정 중심, 승인된 설계 범위만 수행 |
| `ex-reviewer` | 독립 검토자 | 읽기 중심, traceability/FIND/CR/ISSUE 판정 후보 생성 |
| `ex-security` | 보안 검토자 | 보안 기준선, KISA, secure coding 검토 |
| `ex-evidence` | 증적 수집자 | 테스트 결과, 화면 캡처, 로그 정리 |
| `ex-docs` | 문서 정합성 | 메타데이터, 용어, 문서 버전, 링크 정리 |

중요한 점:

```text
profile != Core persona
```

Core persona는 작업 책임이다.
Hermes profile은 그 책임을 수행하도록 설정된 실행 환경이다.

예를 들어 `review` persona는 `ex-reviewer` profile에서 자주 수행할 수 있지만, 둘은 같은 개념이 아니다.

### 4.3 `kanban`

`kanban`은 Hermes의 durable multi-agent work queue다.
SQLite board에 task를 만들고, profile별 worker가 task를 claim해서 수행한다.

특징:

- 현재 대화 턴이 끝나도 task 상태가 보존된다.
- dispatcher가 task를 profile에 배정하고 worker를 실행할 수 있다.
- task 사이에 dependency/link/comment/block/complete 같은 상태를 둘 수 있다.
- 여러 profile이 같은 board를 보며 협업할 수 있다.
- worker는 `kanban_show`, `kanban_complete`, `kanban_block`, `kanban_comment` 같은 제한된 도구로 작업 상태를 갱신한다.

Ex에서의 권장 용도:

- Build Wave를 여러 worker task로 나누기
- Gate 2 또는 Gate 4 독립 검수 queue 만들기
- `review`, `security-review`, `ui-review`, `development-review`를 분리된 profile에 배정하기
- 긴 작업을 현재 채팅 턴에 묶지 않고 durable queue로 운영하기
- Dashboard가 읽을 수 있는 Ex Run 상태와 Hermes task 상태를 연결하기

Ex Core와의 관계:

```text
Ex docs/runs/ = 공식 Run 기록
Hermes kanban = worker 실행 queue
```

kanban task가 완료됐다고 Ex Run이 자동 완료되는 것은 아니다.
Orchestrator는 worker 결과를 읽고, 필요한 검증을 실행한 뒤, Ex Run 문서와 traceability를 갱신해야 한다.

권장 매핑:

```text
Implementation Plan Run
-> Build Wave 정의
-> kanban task 생성: BW-001 backend, BW-001 frontend, BW-001 tests
-> profile별 worker가 task 수행
-> Orchestrator가 결과 수집/검증
-> vulcan.py wave-complete
-> Run 결과 정리
```

### 4.4 `cron`

`cron`은 예약 실행 기능이다.
사용자가 이미 이해한 기능에 가깝지만, Ex에서는 다음처럼 쓰기 좋다.

권장 용도:

- 매일 또는 매 Run 종료 후 문서 링크/메타데이터 점검
- traceability 누락 점검
- stale Run, 오래 열린 FIND/ISSUE 요약
- CI 결과나 GitHub PR 상태 주기 확인
- Dashboard에 표시할 요약 리포트 생성

주의:

- cron은 사용자가 없는 상태에서 실행될 수 있으므로 질문을 던지는 작업에는 맞지 않는다.
- 승인이나 범위 변경 판단을 자동 확정하지 않는다.
- cron 결과는 Orchestrator가 다음 세션에서 판단 재료로 사용한다.

## 5. Hermes를 Ex 상위 Orchestrator로 쓸 때의 권장 흐름

### 5.1 짧은 작업

```text
사용자 요청
-> Hermes Orchestrator가 current_gate와 관련 문서 확인
-> 필요한 경우 delegate_task로 persona 검토 수행
-> Orchestrator가 결과 검증
-> Run 문서와 traceability 갱신
-> 사용자에게 완료 보고
```

### 5.2 여러 worker가 필요한 작업

```text
사용자 요청
-> Orchestrator Plan Run 생성
-> Build Wave 또는 Review Queue 정의
-> Hermes kanban task 생성
-> profile별 worker 실행
-> Orchestrator가 결과 수집
-> 테스트/trace/run-check 검증
-> FIND / CR / ISSUE 분류
-> Run 결과 갱신
```

### 5.3 반복 점검 작업

```text
cron job
-> 정해진 주기로 traceability, Run 상태, CI, 문서 상태 확인
-> 요약 리포트 생성
-> Orchestrator가 다음 세션에서 판단 재료로 사용
```

## 6. 권장 원칙

1. Hermes 기능은 Ex Core를 대체하지 않는다.
2. Gate 판단과 최종 승인 흐름은 항상 Ex Core 규칙을 따른다.
3. Adapter는 실행 방식만 얇게 매핑한다.
4. `delegate_task`는 짧고 명확한 subtask에 사용한다.
5. `profile`은 장기 역할별 실행 환경에 사용한다.
6. `kanban`은 durable multi-worker queue에 사용한다.
7. `cron`은 반복 점검과 알림에 사용한다.
8. 모든 subagent, profile, kanban worker, cron 결과는 Orchestrator가 다시 검증한다.
9. Dashboard는 관측자와 승인 보조 UI이며, Core 규칙의 주체가 아니다.

## 7. 다음 정리 후보

Hermes Adapter를 실제 운영 문서로 확장하려면 다음 문서를 추가할 수 있다.

| 문서 | 목적 |
| --- | --- |
| `RUN_INPUT_CONTRACT.md` | Hermes subagent/profile/kanban worker에게 넘길 Run 입력 형식 |
| `RUN_OUTPUT_CONTRACT.md` | Hermes worker 결과를 Ex Run 출력으로 정규화하는 형식 |
| `PERSONA_MAPPING.md` | Core persona와 Hermes profile/toolset/skill 매핑 |
| `GATE_PROMPTS.md` | Hermes Orchestrator가 Gate별로 읽고 위임할 얇은 prompt 템플릿 |
| `LIMITATIONS.md` | Hermes delegation, profile, kanban, cron 사용 한계와 승인 필요 상황 |
