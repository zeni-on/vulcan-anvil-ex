# Agy Workspace Branch Delegation Review

> 상태: 기록
> 작성일: 2026-06-07
> 목적: Antigravity/Agy Workspace: branch 방식과 Vulcan-Anvil Ex native delegation 기록 방식의 정합성 검토 결과를 보존한다.

## 검토 대상

이 문서는 다음 변경 이후 Agy 측에서 검토한 내용을 정리한다.

- Core output contract에 `delegation_records`를 추가한 native worker delegation 기준
- Gemini/Agy adapter의 `delegation_records` 및 Gemini `responseSchema` 정렬
- Agy `Workspace: branch` 기반 가상 격리 작업 방식
- `agent-run`/`run-exec` 외부 CLI runner와 Agy native branch agent 경로의 역할 분리

관련 문서:

- [RUN_OUTPUT_CONTRACT.md](../../core/RUN_OUTPUT_CONTRACT.md)
- [RUN_OUTPUT_CONTRACT_GEMINI.md](../../core/RUN_OUTPUT_CONTRACT_GEMINI.md)
- [AGENT_RUN_PROTOCOL_GEMINI.md](../../core/AGENT_RUN_PROTOCOL_GEMINI.md)
- [Gemini RUN_OUTPUT_CONTRACT_GEMINI.md](../../adapters/gemini/RUN_OUTPUT_CONTRACT_GEMINI.md)
- [Gemini Adapter README](../../adapters/gemini/README_GEMINI.md)

## 결론

Agy의 Workspace: branch 방식은 Ex의 native delegation 기록 방식과 충돌하지 않는다.

다만 이 기능은 일반 Git worktree가 아니라 Antigravity/Agy runtime 특화 기능으로 취급한다. Ex Core는 이를 범용 Git 기능으로 일반화하지 않고, Gemini/Agy adapter와 `delegation_records.mode: agy-branch-agent`로 식별한다.

## Agy 검토 요약

### 1. 상충 없음

`delegation_records.mode` 권장 값에 `agy-branch-agent`가 포함되어 있어, Agy가 가상 브랜치 worker를 띄운 실행 결과를 다른 native subagent/thread 결과와 구분해 기록할 수 있다.

Gemini `responseSchema`는 필수 필드를 다음 정도로 최소화한다.

```json
["mode", "delegate", "task", "status", "changed_files", "result_summary"]
```

`started_at`, `completed_at`, `orchestrator_verification` 같은 runtime 보조 필드는 선택값으로 두어, Agy 가상 런타임에서 일부 메타데이터가 누락되어도 Run 결과 기록 자체가 차단되지 않게 한다.

### 2. 얇은 추적 기록이 적합함

외부 CLI runner는 프로세스 로그, stderr, watchdog timeout, worktree 경로, transcript 같은 두꺼운 실행 증적이 필요하다.

반면 Agy Workspace: branch는 플랫폼 runtime이 생명주기와 격리를 관리한다. 따라서 Run 문서에는 `delegation_records` 중심으로 다음만 얇게 남기는 것이 적합하다.

- delegate와 mode
- task와 scope
- changed files
- result summary
- Orchestrator 재검증 명령 또는 필요 판단

### 3. 의존성 설치 비용을 줄일 수 있음

Agy Workspace: branch는 Copy-on-Write/가상 오버레이 방식으로 부모 workspace의 의존성 폴더를 재사용할 수 있다는 것이 Agy 측 설명이다.

따라서 일반 Git worktree처럼 `node_modules`, Python venv, Gradle cache를 작업공간마다 다시 설치하거나 링크하는 비용을 줄일 수 있다. 이 장점은 Agy runtime에 한정되며, Codex/Claude 외부 CLI runner나 일반 Git worktree에 자동 적용된다고 가정하지 않는다.

### 4. 최종 판단은 Orchestrator가 수행함

Agy worker가 반환한 변경 파일과 결과 요약은 후보 결과다. Orchestrator는 부모 workspace에서 범위와 테스트를 다시 확인해야 한다.

권장 흐름:

```text
Agy Workspace: branch worker 실행
→ delegation_records 기록
→ Orchestrator가 changed_files와 scope.writable 대조
→ 필요한 검증 명령 재실행
→ Run 결과 정규화
→ Gate/Wave/QA 판단은 Orchestrator가 수행
```

## 운영 기준

- Agy native branch worker를 사용할 때는 `delegation_records.mode: agy-branch-agent`를 사용한다.
- Agy native branch worker에게 위임하기 전에는 Orchestrator가 `python vulcan.py run-preflight <run-file>`를 직접 실행한다. Agy native branch는 외부 `run-exec` 실행 경로가 아니므로 자동 preflight가 적용되지 않는다.
- `prepare-transition`의 preflight 사후 점검은 누락을 잡는 안전망이며, 위임 전 preflight 실행을 대체하지 않는다.
- `agent-run`/`run-exec`는 Agy native branch가 아니라 외부 CLI process 실행, transcript/watchdog/evidence가 필요한 경우의 선택 경로로 둔다.
- Agy Workspace: branch의 Copy-on-Write 이점은 Gemini/Agy adapter 문서에만 runtime-specific capability로 적는다.
- Run 결과가 얇아져도 Orchestrator 재검증 명령과 변경 파일 목록은 반드시 남긴다.
- Agy 결과가 설계 문서를 자동으로 덮어쓰면 안 된다. 설계와 코드 차이는 `drift-report` 또는 CR/FIND/ISSUE 후보로 분리한다.
