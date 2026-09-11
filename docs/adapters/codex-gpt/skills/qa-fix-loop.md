# QA 수정 루프 Skill

## 사용할 때

QA, 테스트, 리뷰, 증적 확인 중 발견한 결함이 승인된 설계 범위 안에서 수정 가능해 보일 때 사용한다.

Product는 [PRODUCT_PROFILE_BASELINE.md](../../../core/PRODUCT_PROFILE_BASELINE.md) 7절에 따라 기존 FIND/이슈/작업 요약의 수정 범위와 재시험 기준을 사용한다. 이미 수정·재시험까지 맡았다면 같은 허가를 다시 요청하지 않는다. 검증 전용 담당자는 수정 후보를 총괄에게 반환한다. Run과 새 worker는 선택이며, 실행자와 결과 확인은 7절을 따른다. Audit/PoC는 아래 Run/worker 절차를 유지한다.

## 필수 입력

- `docs/core/CHANGE_CONTROL_PROCESS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- 관련 `FIND` 기록 또는 실패 설명
- 관련 설계, 구현, 테스트 산출물

## 절차

1. 이슈가 승인된 설계 범위 안에 있는지 확인한다.
2. 범위 안의 결함이면 `FIND`를 생성하거나 갱신한다.
3. 관련 `REQ`, `AC`, `PGM`, `SEC`, `UT`, `IT`, `UI` ID를 식별한다.
4. Product는 기존 작업 요약에 수정 범위, 금지 범위와 검증 명령을 확정한다. Run을 선택했거나 Audit/PoC라면 `qa-fix-loop` Run에 `scope.writable`과 같은 기준을 기록한다.
5. Product 실행자는 7절로 정한다. Audit/PoC에서는 native worker가 수정하고 Orchestrator는 통합과 재검증을 담당한다. 외부 CLI가 필요할 때만 `agent-run`/`run-exec`와 해당 Run 계약을 사용한다.
6. 발견사항을 해결하는 최소 구현 또는 문서 수정을 수행한다.
7. 관련 검증을 다시 실행한다.
8. 검증 결과에는 실행 위치(cwd), 명령, 성공 기준, exit code, 결과, 로그/증적 경로를 기록한다.
9. 필수 검증을 실행하지 못했으면 `Pass`가 아니라 `Not Run`으로 남기고 사유, 영향 범위, 후속 조치를 기록한다.
10. 증적과 추적성 갱신 필요 항목을 남긴다. 추적표와 session 상태 확정은 Orchestrator가 재검증 후 수행한다.
11. 수정에 요구사항, 인수기준, 설계, 보안 기준선, 릴리즈 범위 변경이 필요하면 중단하고 `CR`로 승격한다.
12. subagent/thread로 수정했다면 기존 결과 요약에 위임 대상, 수정 범위, 변경 파일, 실제 검증 결과를 남긴다. Run이 있으면 `delegation_records`를, 외부 CLI runner라면 기존 `Run Execution Record`도 사용한다.

## Run을 사용하는 경우의 작성 기준

- 파일명에는 `qa-fix-loop`와 대상 `FIND-ID`를 포함한다.
  - 예: `RUN-018_qa-fix-loop-FIND-017-01-todorepository-contract-fix_v0.1.md`
- 메타데이터는 다음 성격을 가진다.

```yaml
gate: gate4
persona: build
skill: qa-fix-loop
run_type: QAFix
related_ids: [FIND-017-01, IF-003, PGM-003, UT-001, IT-001]
```

- `qa-fix-loop`는 QA 실행 Run이 아니다. QA 실행은 `qa-execution`, 승인된 설계 범위 안의 결함 수정은 `qa-fix-loop`, 계약 변경이 필요한 경우는 `change-impact-analysis` 또는 CR로 분리한다.
- 새 요구사항, 새 API, 새 화면 상태, DB 계약 변경이 필요하면 구현하지 않고 Orchestrator 결정 필요 항목으로 반환한다.
- native 위임의 기록을 위해 Product Run을 새로 만들지 않는다. Run을 사용한 위임은 현재 Run의 `delegation_records`에 남긴다.

## 출력

다음을 반환한다.

- `FIND` ID
- 원인
- 변경 파일
- 검증 명령과 결과
- 실행 위치(cwd), exit code, 로그/증적 경로
- 갱신한 증적
- `CR` 승격 필요 여부
