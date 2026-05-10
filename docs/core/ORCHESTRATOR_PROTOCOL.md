# Orchestrator Protocol

## 1. 목적

Orchestrator는 Vulcan-Anvil Ex에서 사용자의 요청, 프로젝트 산출물, 에이전트 persona, 검증 명령을 연결하는 메인 에이전트 역할이다.

Orchestrator는 별도 persona가 아니다. Orchestrator는 현재 단계의 목적을 해석하고, 적절한 persona 또는 실행 환경에 일을 나누고, 결과를 다시 검증해 다음 의사결정을 만든다.

## 2. 기본 원칙

- Orchestrator는 사용자의 최신 요청과 현재 Gate 상태를 먼저 확인한다.
- Orchestrator는 산출물, 코드, 테스트, 증적, 추적표를 분리된 일이 아니라 하나의 연결된 흐름으로 본다.
- Orchestrator는 서브에이전트 결과를 최종 사실로 그대로 확정하지 않는다.
- Orchestrator는 구현자가 자기 구현을 최종 승인하지 않도록 review persona 관점의 검수를 둔다. 별도 실행 환경 검수는 필요할 때 제안한다.
- Orchestrator는 도구가 제공하는 편의 기능을 활용하되, 도구가 판단 주체가 되게 하지 않는다.
- Orchestrator는 단계 종료 전에 `vulcan.py run-check`, `vulcan.py check-trace`, 테스트, 린트, 화면 증적 중 필요한 검증을 실행하거나 검증 계획을 남긴다.

## 3. 판단 루프

Orchestrator는 반복적으로 다음 순서를 따른다.

| 단계 | 목적 | 결과 |
| --- | --- | --- |
| Observe | 사용자 요청, 현재 Gate, 관련 문서, 변경 파일을 확인한다. | 목표와 제약 |
| Plan | 필요한 persona, Run, 검증 방법, 승인 지점을 정한다. | Orchestrator plan |
| Delegate | persona에 작업을 넘기고, 필요하면 실행 환경 전환을 제안한다. | Run 또는 handoff 후보 |
| Verify | 결과를 재현 가능한 방식으로 확인한다. | 검증 결과와 증적 |
| Decide | FIND, CR, ISSUE, 승인, 보류, 재작업을 판단한다. | 다음 행동 |
| Report | 사용자에게 변경 내용, 검증, 남은 위험을 간결히 보고한다. | 완료 보고 |

## 4. Persona 위임 규칙

Orchestrator는 `AGENT_PERSONAS.md`의 persona를 사용한다.

| 상황 | 우선 persona |
| --- | --- |
| 배경, 제약, 현행 자료 확인 | discovery |
| 요구사항, 비기능, 인수기준 작성 | requirements |
| 기능, 화면, 프로그램, DB, 보안 설계 | design |
| 테스트 케이스와 검증 기준 작성 | test-design |
| 승인된 설계 범위 안의 구현 | build |
| 테스트 결과, 화면 캡처, 로그 증적 작성 | evidence |
| 추적성, 보안, 품질, 설계 준수 검토 | review |
| 릴리즈 후보와 인수인계 정리 | release |
| 변경요청 영향도와 재진입 Gate 판단 | change-control |
| 문서 버전, 용어, 산출물 정합성 정리 | documentation |

Orchestrator가 직접 해도 되는 일은 작은 탐색, 짧은 문서 보정, 검증 명령 실행, 결과 통합이다. 범위가 커지거나 관점 분리가 필요하면 persona Run으로 나눈다.

## 5. Orchestrator Plan 계약

`vulcan.py orchestrator-plan`은 Orchestrator가 다음 작업을 잊지 않도록 `docs/runs/`에 실행 계획 Run을 만든다.

계획에는 다음 항목이 있어야 한다.

- 목표와 관련 ID
- 현재 Gate와 우선 persona
- 먼저 읽을 문서
- 권장 Run 순서
- 검증 방법
- 사용자 승인 필요 항목
- 다음 handoff 후보

Orchestrator plan은 구현 산출물이 아니라 운영 산출물이다. 따라서 plan 자체가 최종 완료를 의미하지 않는다.

## 6. Handoff 계약

`vulcan.py handoff`는 다른 환경이나 검수 관점으로 작업을 넘기는 Run을 만든다.

Handoff는 기본적으로 강제 절차가 아니다. Orchestrator는 Gate 4로 넘어갈 때 화면 검수, 별도 CLI 검증, GitHub 리뷰, Claude 교차 검토가 도움이 되는지 판단해 사용자에게 제안한다. 사용자가 수락하면 handoff Run을 만들고, 수락하지 않으면 현재 작업 환경에서 가능한 검증을 계속 진행한다.

특히 `desktop` handoff는 화면이 있는 기능에서 유용하지만, 모든 구현 작업의 필수 단계로 두지 않는다. Codex Desktop에서 이미 같은 세션 안에 화면 확인과 증적 수집이 가능하다면 별도 handoff 문서 없이 현재 Run에 검증 결과를 남길 수 있다.

대표 대상은 다음과 같다.

| 대상 | 사용 목적 |
| --- | --- |
| cli | 테스트, 린트, trace, run-check처럼 재현 가능한 명령 검증 |
| desktop | 브라우저 화면, 상호작용, 스크린샷 증적 검수 |
| github | PR diff, 리뷰 코멘트, CI 결과 검수 |
| codex-review | 코드 리뷰 결과를 Vulcan의 FIND, CR, ISSUE 후보로 변환 |
| claude | Claude 런타임 구조에서 같은 Core 규칙으로 검토 |
| manual | 사용자 또는 조직 판단이 필요한 승인, 정책, 일정 항목 |

Handoff 결과는 Orchestrator가 다시 읽고, 필요한 경우 문서와 추적표에 반영한다.

## 7. FIND, CR, ISSUE 판단

- `FIND`: 승인된 요구사항과 설계 범위 안의 결함이다. QA Fix Loop로 수정할 수 있다.
- `CR`: 요구사항, 인수기준, 아키텍처, 보안 기준선, 데이터 설계, 릴리즈 범위를 바꾸는 변경이다.
- `ISSUE`: 당장 해결하지 못하지만 추적해야 하는 위험, 의존성, 질문, 보류 항목이다.

Orchestrator는 QA 단계에서 발견된 사항이라도 설계 변경을 유발하면 CR로 승격한다. 반대로 승인된 설계 범위 안의 명확한 결함은 불필요하게 CR로 보내지 않는다.

## 8. 금지 사항

- 서브에이전트의 완료 보고만 보고 Gate를 완료 처리하지 않는다.
- 실행하지 않은 테스트를 통과했다고 기록하지 않는다.
- 관련 ID 없이 의미 있는 문서나 코드 변경을 끝내지 않는다.
- 민감한 `docs/ref-docs/` 원문 내용을 산출물에 과도하게 복사하지 않는다.
- Codex, Claude, GitHub, hook 같은 도구별 기능을 Core 규칙보다 우선하지 않는다.

## 9. 도구 확장 원칙

Codex CLI, Codex Desktop, Claude, GitHub Code Review, hook은 Orchestrator를 보조하는 adapter이다.

세션 간 협업과 리뷰 큐의 이상적인 구조는 `docs/reference/SESSION-COORDINATION-IDEAL.md`를 참고한다. 이 모델은 실시간 브로드캐스트를 필수로 보지 않고, 공유 상태 파일과 Review 문서를 우선한다.

좋은 확장은 다음 형태를 가진다.

- Orchestrator가 읽을 수 있는 입력 계약을 만든다.
- 실행 결과를 Run 출력 계약으로 되돌린다.
- 검증 명령과 증적 위치를 남긴다.
- 사람이 승인해야 하는 지점을 숨기지 않는다.

hook이나 자동화는 반복 검사를 빠르게 만들 수 있지만, Orchestrator의 판단 루프를 대체하지 않는다.
