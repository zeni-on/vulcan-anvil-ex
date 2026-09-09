# Codex/GPT Persona Delegation

> Codex desktop의 역할별 작업(thread)과 일시적인 subagent를 Ex의 공통 작업 계약에 연결한다. CLI에서도 사용 가능한 경로만 적용한다.

## 1. 공통 기준

역할, 문서 소유권, 짧은 전달/회수, 승인 경계는 [Role-Based Collaboration](../../core/COLLABORATION_PROTOCOL.md)을 따른다. persona는 작업 계약이며 작업창 제목이나 custom agent 이름과 같을 필요는 없다. 새 역할별 필수 문서나 별도 Gate 상태를 만들지 않는다.

## 2. 어떤 실행 공간을 쓸까

| 목적 | 권장 방식 |
| --- | --- |
| 사용자가 유지하려는 설계/경험설계/개발/품질검증 대화 | 사용자가 지정하거나 생성 요청한 역할별 작업 |
| 현재 업무 안의 짧고 독립적인 조사/구현/증적 해석 | 총괄 아래의 subagent |
| 독립 리뷰 | 부모 대화를 상속하지 않은 새 reviewer |
| 다른 모델 또는 별도 CLI 실행 증적 | 선택형 외부 runner |

사용자가 역할별 운영을 선택해도 작업 수를 고정하거나 Run마다 새 작업창을 만들지 않는다. 새 사용자 작업창은 사용자 생성 요청이 있을 때만 만든다. 현재 업무의 하위 일은 subagent를 사용한다. 이미 있는 역할 작업은 같은 프로젝트인지 확인한 뒤 재사용한다. 역할 제목만으로 읽기 전용 권한이나 model/effort가 설정되었다고 보고하지 않는다.

## 3. 기존 작업 연결

1. 현재 도구 목록에서 작업 조회, 메시지 전달, 결과 회수 기능을 확인한다. Codex 앱 도구가 제공되면 `list_threads`, `read_thread`, `send_message_to_thread`, `wait_threads`에 해당하는 기능을 사용할 수 있다. 실제 이름/인자는 노출된 schema를 따른다.
2. 사용자 지정 역할을 반환된 프로젝트/작업 ID에 연결한다. 표시 제목은 그대로 사용하되 제목만으로 식별하거나 임의 ID를 만들지 않는다. 동명이거나 위치가 불명확하면 배정 전에 확인한다.
3. 연결 정보는 기존 총괄 Plan/작업 요약에 짧게 남긴다. `session.json`에 새로운 필수 registry를 만들지 않는다. 대상 작업이 사라졌거나 접근할 수 없으면 재조회하고, 오래된 ID로 성공을 가정하지 않는다.
4. 대상의 진행 상태와 실제 작업 경로/branch/소스 기준을 확인한다. 같은 프로젝트 아래에 있어도 Local/worktree가 다를 수 있다. 별도 worktree에는 총괄의 미커밋 문서나 최신 통합 변경이 자동 반영됐다고 가정하지 않는다.
5. 업무를 전달한 뒤 도구가 제공하는 완료 알림/긴 대기를 사용한다. API의 접수/전송 성공이나 작성 중이라는 상태는 결과 완료가 아니다. 완료 응답을 회수하고 원본 파일/증적을 확인한다. 반복 전체 대화 조회나 의미 없는 재지시는 피한다.

일반 대화의 종료 후에도 총괄이 자동으로 계속 깨어난다고 가정하지 않는다. 현재 작업에서 지원되는 대기/알림을 사용하고, 그 기능이 없으면 재개 필요를 알린다. 자동화는 사용자의 별도 요청 없이 만들지 않는다.

도구가 없으면 해당 역할 작업창을 호출했다고 보고하지 않는다. 허용된 subagent나 외부 runner로 대체 가능한지 판단하고 실행 매체 변경을 알린다. 사용자가 특정 작업/새 문맥을 지정했다면 임의 대체하지 않는다. 기능 구현의 직접 수행 예외와 Gate 승인은 기존 Core 규칙을 유지한다.

## 4. 전달문 예시

Run이 있는 경우 아래처럼 연결 정보와 변경점만 보낸다. 값은 실제 배정에서 확인해 채운다.

```text
이번 업무는 build 담당이다. 총괄 절차나 다른 역할의 정리를 함께 수행하지 않는다.
작업: <Run 경로 / 이번 업무>
기준: <Gate, Profile, 승인 범위, 실제 cwd, 소스 기준과 dirty 여부>
입력: <관련 ID와 원본 계약 구간, 이전 배정 이후 달라진 조건>
범위: <Run scope.writable 참조, 제외 범위, 선행 결과>
검증: <Run verification.commands/cwd 참조>
반환: 변경 파일, 실행 결과/증적, 미해결 사항과 총괄 결정 필요 항목.
읽기 시작점은 AGENTS.md와 배정 Run이며, Product build는
docs/core/PRODUCT_WORKER_GUIDE.md를 따른다. 필요한 계약과 공통 제약만 추가로 읽는다.
```

다른 persona는 해당 담당 지침으로 바꾼다. PoC에서 Run을 생략할 수 있으면 Profile에서 허용한 짧은 작업 계약을 사용한다. 담당자에게 Core 전체와 누적 session/원장을 일괄 전달하지 않는다.

## 5. 결과, 권한과 비용

- 기존 `delegation_records`에서 별도 작업 위임은 `mode: codex-thread`, subagent는 `mode: codex-subagent`로 구분한다. 실제 대상 ID/경로가 있으면 `notes` 또는 기존 실행 메타에 남긴다. 알 수 없는 시간/model/effort/식별자를 추정하지 않는다.
- `worker_completed`는 담당자 완료다. `verified`와 Gate/QA 최종 판정은 총괄 검증 후에만 기록한다. 읽기 전용 리뷰도 테스트 실행 부산물이 생겼다면 보고한다.
- 모델/effort는 [Codex Model Policy](../../core/CODEX_MODEL_POLICY.md) 3.1절을 따른다. 기존 역할 작업은 자체 설정이 있을 수 있으므로 총괄 모델 상속을 단정하거나 기본적으로 덮어쓰지 않는다.
- 독립 reviewer는 [native review 기준](../../core/AGENT_RUN_PROTOCOL.md#54-새-문맥의-native-review)을 따른다. 지원되는 subagent 호출은 `fork_context: false`를 명시한다. 기존 구현 대화를 fork한 작업이나 장기 QA 담당에게 "이전 대화를 잊어라"고 하는 것은 같은 보장이 아니다.
- Codex의 Local/worktree 전환은 Gate 전환이 아니다. 품질검증은 총괄이 지정한 안정된 QA workspace/소스에서 수행하고, 테스트 동안 해당 환경의 동시 변경을 막는다. 총괄/담당자가 서로 같은 Git index에서 커밋하지 않는다.

## 6. 작은 운영 리허설

사용자가 선택한 기존 역할 작업에 한 개 계약 구간의 읽기 전용 검토를 맡겨 다음을 확인한다.

1. 올바른 프로젝트/작업 ID와 소스 기준으로 전달되었는가?
2. 결과가 총괄에 회수되고 근거 파일/구간을 확인할 수 있는가?
3. 담당자가 Gate/session/공통 원장을 수정하지 않았는가?
4. 도구 부재/입력 불일치/질문이 있을 때 총괄로 반환하는가?

이후 승인된 개발 업무와 안정된 소스의 QA로 확장한다. 이 지침 설치만으로 실제 메시징 성공, 비용 절감 또는 자동 운영이 검증되지는 않는다. App Server 연동은 이 방식의 필수 조건이 아니다.

공식 참고: [Projects and chats](https://learn.chatgpt.com/docs/projects), [Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). 실제 제공 도구와 사용자 승인 범위가 우선이다.

