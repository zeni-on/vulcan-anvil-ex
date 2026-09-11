# Product Process Execution Verification

> 정책 변경 (2026-09-11): 이 문서는 당시 실제 시험과 관측을 보존한 이력이다. 아래 Git/소스 지문 신선도 차단과 시험 전 커밋 권고는 폐기된 요구이며 현재 운영에 적용하지 않는다. 현재 기준은 [CURRENT_CONTEXT_AND_EVIDENCE.md](../core/CURRENT_CONTEXT_AND_EVIDENCE.md)와 [PRODUCT-PROCESS-CONTRACTS.md](PRODUCT-PROCESS-CONTRACTS.md)를 따른다. 과거 로그·수치·결과는 재생성하지 않는다.

- 기준: 2026-09-11, main `1384c15` 이후 실행 회귀 보강.
- 범위: 별도 합성 Git 프로젝트의 실제 CLI/시험 실행, Codex native QA 위임·회수, 기존 profile 회귀.
- 상태: 실제 native QA 실패·복구·회수 및 로컬 회귀 확인. 일반 활성화/실제 발행은 보류.
- 계약 원본: [Product Process Contracts](PRODUCT-PROCESS-CONTRACTS.md), [운영 시나리오](PRODUCT-ITERATIVE-PROCESS-SCENARIOS.md).

프레임워크 검증 기록이다. 프로젝트의 필수 문서나 에이전트 시작 입력에 추가하지 않는다. PMTool/기존 샘플 이행, 일반 init 활성화, 실제 외부 릴리즈는 수행하지 않는다.

## 1. 반복 가능한 실행 시험

[fixture 생성기](../../scripts/regression/product_execution_fixture.py)와 [10개 통합 테스트](../../scripts/regression/tests/test_product_execution.py)를 추가했다. Python 표준 라이브러리와 실제 Git/CLI를 사용하며 임시 프로젝트마다 상태·소스·증적을 분리한다. 승인 actor/ref는 명시적인 합성 데이터다. 사용자 권한 인증을 시험했다고 주장하지 않는다.

| 사례 | 확인 기준 |
| --- | --- |
| 실제 실패 → 수정 → 재시험 | 요청 이력의 원문 보존 assertion을 실패시킨 후 수정한다. 실패 JSON/log는 보존하고 새 시험 결과로만 인수 요청을 평가한다. |
| worker 요약과 실제 결과 불일치 | 실패 명령을 Pass라고 제출해도 종료 코드/실행 증적에서 차단한다. |
| 승인·결과 재사용 | 과거 결과와 새 시험에 맞지 않는 수용 verification key는 차단하며 실패 요청은 session bytes를 변경하지 않는다. |
| 검증 전용 담당자의 수정 권한 | verify 허가만으로 impl 복귀를 허용하지 않는다. 해당 범위의 fix 허가가 있어야 한다. |
| 완료 후 확장 | completed에서 추가 명령 실행·직접 impl 복귀를 막고 새 범위로 열 때 과거 완료 이력을 보존한다. |
| clean Git과 최신 증적 분리 | 소스/시험/의존성/환경/문서/증적이 바뀌면 커밋해 clean이 되어도 후보를 차단한다. |
| Git 전환 실패·상태 revision | 충돌한 브랜치 생성이 미커밋 파일/상태를 훼손하지 않는지, 다른 브랜치의 옛 session에 대기 요청을 적용하면 충돌하는지 확인한다. |
| 환경 차단 | 없는 실행 파일은 exit 127/launch_error로 남으며 제품 assertion 실패나 Pass로 바꾸지 않는다. |
| 발행 방어선 | 인수 완료와 release preview 후보가 있어도 발행을 거부한다. publisher/push 대역이 호출되지 않았는지 확인한다. |
| fixture 자체의 격리 | 다른 저장소를 가리키는 Git 환경변수/설정이 자식 명령에 전달되지 않으며 외부 Git 디렉터리 포인터를 거부한다. 다른 임시 저장소의 파일·refs·index·config bytes를 비교한다. |

명시 Git 작업과 거부 경계의 검증이지 자동 `branch-start`의 구현 완료가 아니다. 발행 대역도 **호출되지 않는 것을 확인**하는 테스트이며 성공적인 PR 발행·배포 계약을 구현한 것이 아니다.

## 2. 실제 Native QA 위임

새 문맥의 Codex native `worker`(Hume)를 별도 임시 프로젝트의 `dev-test`에 배정했다. 모델 override는 생략하고 effort는 medium으로 요청했다. 런타임 모델 응답 값을 별도로 인증한 것은 아니다. 쓰기 범위는 두 증적 파일이며 코드/문서/상태/Git 변경 권한은 주지 않았다.

- 입력: 재제출 계약, 시험 정의, 명시 unittest 명령, 소스/환경 관측 경로, JSON/log 출력 위치. Run/Wave를 만들지 않았다.
- 첫 실행: 3건 중 2건 성공/1건 실패, exit 1. 수정 내용으로 반려 당시 원문을 덮어 기록하는 결함을 재현했다. 환경 차단이 아니다.
- 총괄 회수: 실제 JSON/log와 소스를 직접 읽고 결과를 대조했다. 실패 증적을 Pass라고 제출한 인수 요청이 거부되고 상태가 보존됨을 확인했다.
- 수정: 합성 fix 허가로 impl에 돌아가 원문 보존 코드를 수정·커밋한 뒤 같은 작업공간에서 다시 acceptance로 인계했다.
- 재시험: 같은 담당자에게 새 증적 위치만 바꾸어 다시 맡겼다. 실제 log는 3건 모두 성공/exit 0이며 명시 소스와 session은 QA 실행 전후 동일했다. 총괄도 원본 log와 수집기의 검사 결과를 대조했다.
- 수용: 시험 성공만 넣은 요청은 거부됐고 해당 verification key의 합성 수용 결정을 넣은 요청만 저장됐다. 이후 clean `dev-test`에서 릴리즈 후보 미리보기는 통과했지만 실제 발행은 exit 2로 거부됐다. 과거 실패 증적을 보존했고 Run/QA worktree를 생성하지 않았다.
- 실행 식별: native worker `01a08ec5-37cb-7862-acf7-7d052f03acc0`; 재시험 소스 지문 `411aa5332c2db1f9740e8c588c0cda9e62e3a6f8f196ca22f6ad65437f0f4045`. 로컬 `native-failure.json/.log`, `native-retest.json/.log`는 임시 연습 프로젝트에 남겼다. 사용자 경로나 전체 세션 로그를 공개 저장소로 복사하지 않는다.

자동 회귀는 동일한 계약을 테스트 코드로 재현한다. 모델 호출은 자동 CI에 포함하지 않는다. Agy native 런타임은 실행하지 않았으며 Gemini 문서 라우팅 검증과 구분한다.

## 3. 발견한 운영 조건

현재 소스 지문은 파일 bytes 외에 Git index/작업트리 상태도 포함한다. 따라서 시험 직후 소스를 커밋하면 내용이 같아도 이전 관측과 달라져 stale로 판정한다. 오류를 숨기려고 검사를 완화하지 않았다.

최종 인수 시험 전에 통합 소스 기준을 커밋하고 이후 상태·증적만 정리하면 불필요한 재시험을 줄일 수 있다. 시험 후 소스/index가 바뀐 경우 새 관측으로 재시험한다. 과거 성공 로그는 삭제하거나 실패로 덮어쓰지 않는다. 단순 HEAD 변경과 명시 소스 지문 변경은 다르며 소스가 동일한 문서/증적 커밋까지 무조건 새 시험을 요구하지 않는다.

Codex/Gemini bootstrap은 `process_model`이 있을 때 같은 [Core CLI 안내 4.1절](../core/ORCHESTRATOR_CLI_GUIDE.md#41-개발용-product-반복-프로세스)을 먼저 보도록 연결했다. 알려진 문구의 재발 검사는 [정책 테스트](../../scripts/regression/tests/test_product_policy.py)에 두며 모든 자연어 지침이나 런타임의 자율 준수를 보장하지 않는다.

새 문맥의 `contract-reviewer`는 fixture Git 명령의 환경변수 상속을 지적했다. 자식 Git/CLI 환경에서 기존 `GIT_*` 및 전역/시스템 Git 설정을 분리하고, 변경 명령 전에 전용 Git 디렉터리/실제 루트를 검사하도록 보강했다. 실패 수용 요청은 verification을 저장하지 않으므로 그 직후 부재 검사를 "기존 결과 삭제 검증"으로 확대하지 않았다. 실제 검증 필드의 비재사용은 completed에서 새 작업을 여는 테스트에서 과거 보존/현재 부재로 확인한다.

같은 reviewer의 재검토에서 위 지적의 수정이 확인됐으며 새 FIND/CR 후보는 없었다. 검토자가 명령을 대신 재실행한 것은 아니며, 총괄이 추가 격리 회귀를 실행해 통과를 확인했다. 문서의 테스트 수는 최종 10건으로 맞췄다.

## 4. 검증 결과와 남은 범위

- 집중 실행 회귀: 초기 8건 통과 후 환경 차단을 추가했다. 전체 회귀 실행 뒤 fixture 격리를 보강하고 추가 격리 시험 1건을 재실행해 통과했다. 최종 파일은 10건이며 모두 기존 CI discovery 대상이다.
- 정책 회귀: 6건 통과.
- 전체 Python 회귀: Git 격리 보강 전 273건 중 269건 통과/4건 환경별 skip. 격리 보강 후 추가 1건 통과. 초기 회귀 실패는 최종 QA 전에 소스/index를 확정하도록 fixture를 보정해 해소했다.
- 설치/보존 회귀: 3건 통과. Product/PoC/Audit init이 실험 표식을 추가하지 않고 테스트 fixture를 설치하지 않으며 upgrade가 기존 원본·상태를 보존하는지 확인했다.
- init smoke: 12단계 통과. fixture smoke: 84단계 통과. 변경 관련 문서의 로컬 링크 대상 19개 존재를 확인했다(모든 anchor 검사로 확대하지 않음).
- Windows/Linux Python 및 Dashboard의 최종 통합 결과는 이 변경의 PR Checks를 기준으로 확인한다. 로컬 Python 결과를 Dashboard/Agy runtime 실행 성공으로 확대하지 않는다.

실제 사용자 대화에서 범위 변경·권한 질문·다음 작업 선택이 자연스러운지는 별도 운영 확인이다. 총괄이 준비와 명령을 수행하고 사용자는 업무 판단·결과의 적합성만 확인할 수 있다. 아직 자동 브랜치/릴리즈 발행의 계약 연결, 지원 adapter 전체/선택 UI의 운영 경로, 명시 이행 보존 시험과 일반 적용 판단이 남아 있다. 이번 검증 통과를 새 프로세스 전체 활성화나 제품 전체 QA 완료로 확대하지 않는다.
