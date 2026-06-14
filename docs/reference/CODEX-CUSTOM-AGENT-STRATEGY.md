# Codex Custom Agent Strategy

> Status: draft v0.1  
> 작성일: 2026-06-04  
> 목적: Vulcan-Anvil Ex에서 Codex custom agent를 "메인 Orchestrator의 보조 에이전트"로 사용하는 기준을 정리한다.

## 1. 배경

Ex는 이미 다음 실행 계층을 갖고 있다.

| 계층 | 위치 | 목적 |
| --- | --- | --- |
| Core 규칙 | `docs/core/` | Gate, Run, traceability, QA, release의 원본 규칙 |
| Repo-local skill | `.agents/skills/` | Codex가 필요할 때 읽는 절차 카드 |
| External worker | `python vulcan.py agent-run/run-exec` | worktree, 로그, Run 증적을 남기는 공식 실행 |
| Codex custom agent | `.codex/agents/*.toml` | 메인 Orchestrator가 호출할 수 있는 정의된 보조 에이전트 |

Codex custom agent는 Ex의 공식 worker 실행을 대체하지 않는다.
주 용도는 메인 Orchestrator가 혼자 수행하던 읽기, 추적, 초안 검토, 원인 분석을 분리해 컨텍스트 오염과 반복 탐색 비용을 줄이는 것이다.

## 2. 원칙

1. custom agent는 먼저 read-heavy 보조 역할에 사용한다.
2. 파일 수정, Gate 전환, session 갱신, 최종 승인 판단은 custom agent에게 맡기지 않는다.
3. 공식 구현, QA 실행, 증적 생성은 기본적으로 Run 문서와 `agent-run/run-exec` 경로를 우선한다.
4. custom agent 결과는 후보 의견이며 Orchestrator가 다시 검증한다.
5. delivery profile(`audit`, `product`, `poc`)은 agent 이름으로 만들지 않는다. agent는 역할 중심으로 정의하고, 현재 profile은 `session.json` 또는 `python vulcan.py profile-status`로 확인한다.
6. agent 수는 작게 시작한다. 너무 많은 역할을 만들면 선택 비용과 결과 통합 비용이 커진다.

## 3. 1차 Agent Set

초기 정의는 다음 4개로 제한한다.

| Agent | 용도 | 기본 성격 | Model | Effort |
| --- | --- | --- | --- | --- |
| `trace-scout` | 관련 ID, 누락 trace, source document 후보 탐색 | read-only | `gpt-5.5` | `medium` |
| `run-drafter` | Run 문서가 worker 작업지시서로 충분한지 검토 | read-only/draft | `gpt-5.5` | `medium` |
| `contract-reviewer` | Program/API/DB/UI 계약과 구현 또는 Run 범위 정합성 검토 | read-only | `gpt-5.5` | `high` |
| `qa-reader` | QA 로그, 스크린샷, transcript, result 문서 해석 | read-only | `gpt-5.5` | `medium` |

Build worker 역할은 1차 custom agent에 넣지 않는다.
구현은 worktree, 로그, Run Execution Record가 중요한 영역이므로 `agent-run --mode work` 또는 `run-exec`를 우선한다.

## 3.1 Model/Effort 기준

custom agent의 model/effort는 역할 성격에 맞춰 낮추거나 높인다.
무조건 `gpt-5.5` + `high`로 고정하지 않는다.

| 성격 | 기준 |
| --- | --- |
| 빠른 탐색/정리 | `gpt-5.5` + `medium` |
| 단순 로그 index/요약 | `gpt-5.4-mini` + `low`도 가능하나, 1차 agent에는 두지 않는다 |
| Run 작업지시서 품질 검토 | `gpt-5.5` + `medium` |
| 설계/구현 계약 정합성 판단 | `gpt-5.5` + `high` |
| QA 원인 분류와 FIND/CR/ISSUE 후보 판단 | `gpt-5.5` + `medium` |

`contract-reviewer`는 잘못 낮추면 설계 계약 누락을 놓칠 수 있으므로 강한 모델을 쓴다.
`qa-reader`는 로그 요약만 하는 agent가 아니라 결함/환경 차단/도구 문제를 분리해야 하므로 강한 모델을 쓴다.
첫 샘플 테스트에서 `gpt-5.5` + `medium`이 `gpt-5.4-mini`보다 전체 판단 시간을 줄일 가능성이 확인되어, 1차 custom agent는 대부분 `gpt-5.5` + `medium`을 기본으로 둔다.
`contract-reviewer`만 설계/구현 계약 누락과 CR 후보 판단을 더 깊게 보기 위해 `high`를 유지한다.

## 4. 파일 위치

프로젝트 전용 custom agent는 다음 위치에 둔다.

```text
.codex/agents/
  trace-scout.toml
  run-drafter.toml
  contract-reviewer.toml
  qa-reader.toml
```

`vulcan.py init`과 `vulcan.py upgrade`는 `.codex/agents/`만 복사한다.
`.codex/config.toml`은 사용자 또는 프로젝트별 설정일 수 있으므로 기본 복사 대상에 포함하지 않는다.

## 5. 호출 패턴

custom agent는 자동으로 계속 실행되는 직원이 아니다.
메인 Orchestrator가 필요할 때 명시적으로 호출한다.

Codex 공식 문서 기준으로 custom agent는 `.codex/agents/*.toml`의 `name`으로 식별된다.
메인 Orchestrator는 프롬프트에서 해당 이름을 명시해 Codex가 그 agent를 선택하게 한다.
현재 surface의 내부 tool schema가 `agent_type` 같은 필드를 노출한다고 가정하지 않는다.

Codex surface와 세션 상태에 따라 실제 실행은 두 가지 모드로 나뉜다.

| Mode | 의미 | model/effort 적용 |
| --- | --- | --- |
| `native_custom_agent` | Codex가 프롬프트에 명시된 `.codex/agents/*.toml`의 `name`을 실제 custom agent로 선택해 호출한다 | custom agent TOML 값이 적용된 것으로 볼 수 있다 |
| `prompt_contract_fallback` | built-in/default subagent를 띄우고 `.codex/agents/*.toml` 내용을 prompt에 운영 계약으로 주입한다 | TOML의 model/effort가 자동 적용된다고 보지 않는다. tool parameter override가 가능할 때만 적용한다 |

Orchestrator는 custom agent 실행 보고에 반드시 다음을 남긴다.

```yaml
custom_agent_requested: qa-reader
custom_agent_invocation_mode: native_custom_agent | prompt_contract_fallback
spawned_agent_name_or_type: qa-reader | default | explorer | worker | unknown
model_effort_source: toml-applied | explicit-tool-override | inherited-parent | unknown
files_changed: true | false
```

`prompt_contract_fallback`도 유효한 운영 방식이다.
다만 이 경우 "custom agent model/effort가 적용되었다"고 보고하지 않고, "custom agent 계약을 prompt로 주입했다"고 표현한다.

예시:

```text
trace-scout custom agent를 사용해서 REQ-005-01 기준 관련 ID와 필요한 source document 후보를 정리해줘.
결과를 받은 뒤 메인 Orchestrator가 Run 문서를 확정해줘.
```

```text
run-drafter와 contract-reviewer custom agent를 병렬로 사용해서 RUN-014가 worker에게 충분한 작업지시서인지 검토해줘.
두 결과를 받은 뒤 메인 Orchestrator가 blocker와 보완안을 정리해줘.
```

```text
qa-reader custom agent를 사용해서 QA-002 Playwright 로그와 스크린샷 증적을 읽고 FIND/CR/ISSUE 후보로 분류해줘.
파일은 수정하지 말고 결과만 요약해줘.
```

## 6. 사용 권장 지점

| 단계 | 권장 agent | 이유 |
| --- | --- | --- |
| Gate 2 종료 전 | `contract-reviewer` | 설계 계약 누락을 Gate 3 전에 찾는다 |
| Build Wave Run 작성 전 | `trace-scout`, `run-drafter` | related IDs와 Run scope를 좁힌다 |
| worker timeout 또는 no-result-change 후 | `qa-reader` | 로그와 transcript에서 상태를 해석한다 |
| Gate 4 QA 실패 후 | `qa-reader`, `contract-reviewer` | 결함, 환경 차단, 설계 변경 후보를 분리한다 |
| Gate 5 승인 전 | `contract-reviewer` | 미해결 FIND/CR/ISSUE와 release blocker를 다시 확인한다 |

## 7. 성공 기준

효과는 다음 기준으로 확인한다.

- 메인 Orchestrator 단독보다 누락을 더 빨리 찾는가?
- 결과가 짧고 구조화되어 바로 판단에 쓸 수 있는가?
- 잘못 짚은 문제나 일반론이 적은가?
- Orchestrator가 다시 읽어야 하는 문서 양이 줄었는가?
- Run 보정량, QA 원인 분석 시간, check 실패 반복이 줄었는가?

효과가 확인되지 않으면 agent를 늘리지 않는다.
custom agent는 복잡도를 줄일 때만 유지한다.

## 8. Ex Worker와의 경계

| 항목 | Codex custom agent | `vulcan.py agent-run/run-exec` |
| --- | --- | --- |
| 주 용도 | 조사, 초안, 검토, 로그 해석 | 공식 worker 실행, 구현, QA 실행 |
| 증적 | agent 요약 중심 | Run Execution Record, 로그, worktree diff |
| 파일 수정 | 기본 금지 | Run scope 안에서 허용 |
| 병렬성 | 읽기 중심 병렬에 적합 | 하나의 Run/worker 실행 단위에 적합 |
| 최종 판단 | 불가 | 불가, Orchestrator가 판단 |

따라서 Ex의 기본 책임 구조는 다음과 같다.

```text
가벼운 보조 판단 = Codex custom agent
공식 구현/QA 실행 = vulcan.py worker
최종 판단/승인/Gate 전환 = Main Orchestrator
```

## 9. 검증 계획

1. 완료된 샘플 프로젝트에서 Run 문서 1개, Program Design 1개, QA 결과서 1개를 고른다.
2. 메인 Orchestrator 단독 검토 결과를 기록한다.
3. custom agent 1~2개를 호출한 검토 결과를 기록한다.
4. 발견 이슈 수, 유효 이슈 수, 잘못 짚은 이슈 수, 소요 시간, Orchestrator 보정량을 비교한다.
5. 효과가 큰 agent만 유지하고, 중복 agent는 제거한다.
