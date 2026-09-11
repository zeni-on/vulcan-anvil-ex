# Product Process Contract Prototype

- 상태: 2026-09-11 단계 1 구현. 내부 Python 계약과 읽기 전용 진단만 제공.
- 원본 설계: [3구간 운영](PRODUCT-ITERATIVE-PROCESS-DESIGN.md), [시나리오](PRODUCT-ITERATIVE-PROCESS-SCENARIOS.md)
- 구현: [product_process.py](../../vulcan_core/product_process.py), [계약 시험](../../scripts/regression/tests/test_product_process.py)

이 문서는 프레임워크 개발·검토용이다. 프로젝트 에이전트의 시작 입력에 추가하지 않는다.
일반 init/upgrade는 새 모델을 활성화하지 않는다. 현재 Product의 기존 Gate 운영은 유지한다.

## 1. 이번 단계의 경계

- `new_session`, `assess_transition`, `advance`, `open_work`, `describe`는 파일·Git·프로세스를 변경하지 않는다. 상태 변경 함수는 검증 후 복사본만 반환한다.
- 현재 상태는 `current_gate` 하나다. `gate_status`는 planning/impl/acceptance의 상태이며 현재 구간과 모순되면 진단한다.
- `process_model`이 없으면 Product/Audit/PoC 모두 기존 경로다. 명시된 미지원 값, 잘못된 profile이나 상태는 거부한다.
- 표식이 있는 세션의 `status`는 실험 상태만 읽는다. `status --check`는 검사 소비자 미연결을 표시하고 exit 2다. 준비 완료나 인수 통과를 출력하지 않는다.
- 기존 CLI의 상태 변경·검사는 표식이 있는 세션에서 exit 2로 중단한다. 새 상태를 옛 Gate로 해석하거나 upgrade로 지우지 않는다. `load_session`/`save_session`에도 방어선을 둔다.
- 실제 상태 저장 명령, 범위별 문서 준비 검사, QA 결과 수집 연결, Dashboard, 사용자 프로젝트 이행은 단계 2 이후다. 세션에 표식을 수동 추가하여 운영하지 않는다.

## 2. 범위의 직렬화

```json
{
  "work": {"ref": "issue:request-resubmit", "revision": "snapshot:001"},
  "related_ids": ["SCN-001", "REQ-001", "SEC-001"],
  "contracts": [
    {"ref": "docs/requests.md#resubmit", "revision": "sha256:contract-content"},
    {"ref": "docs/security.md#access", "revision": "sha256:security-content"}
  ],
  "tests": [{"ref": "docs/tests.md#resubmit", "revision": "sha256:test-definition"}],
  "required_checks": ["REG-001", "SEC-REG-001"]
}
```

revision 예시는 실제 값이 아니다. 호출자는 기존 작업/결정/원본의 고정된 당시 내용을 식별하는 값을 전달한다. HEAD/main/dev/latest 같은 이동 라벨은 기준으로 쓰지 않는다. 문서나 요구사항마다 Git SHA 컬럼을 추가하지 않는다.

`scope_key`는 위 객체를 정규화해 계산한 SHA-256이다. 집합 성격 목록의 순서는 무시하고 중복은 거부한다. 작업 revision, 계약·시험 기준, 관련 ID, 필수 시험이 달라지면 다른 범위다. 별도 ITER-ID나 수동 원장을 요구하지 않는다.

기획 중 related_ids/contracts/tests/required_checks는 비어 있을 수 있다. 초기 질문을 시작하려고 미리 요구사항 ID나 시험을 지어내지 않는다. 구현 진입 때에는 관련 기준과 준비 근거가 있어야 한다. 이후 같은 작업을 수정하면 기존 작업의 revision을 갱신한다. 과거 scope_key를 새 작업에 재사용하지 않는다.

## 3. 준비와 권한

준비 자료는 `scope_key`, `purpose`(implementation/handoff), `ready`, `evidence`(ref/revision)를 갖는다. 같은 준비 자료를 기획 완료와 구현 인계에 동시에 쓰지 않는다.

결정은 `scope_key`, `actions`, `actor`, `authority`, `evidence`를 갖는다. actions는 implement/verify/fix 또는 별도의 accept다. 위임받은 결정자는 `authority_ref`로 사용자의 권한 부여 근거도 연결한다.

- 준비 통과만으로 구현 허가는 생기지 않는다.
- 기존 결정이 현재 범위의 verify/fix까지 포함하면 같은 허가를 다시 요구하지 않는다.
- 검증만 맡은 담당자에게 코드 수정 권한을 추가하지 않는다.
- accept는 실행 허가와 분리하며 해당 `verification_key`를 명시한다. 다른 결과에 대한 수용을 재사용하지 않는다.
- merge/push/deploy/release는 이 계약의 actions가 아니다. 인수가 해당 권한을 만들지 않는다.

이 모듈은 사용자 대화를 해석하거나 신원을 인증하지 않는다. ref와 actor를 적었다고 실제 동의가 증명되지는 않는다. 신뢰할 수 있는 호출자가 실제 근거·권한·철회 여부를 확인해야 하며, 프로토타입은 전달된 근거 사이의 연결을 검사한다. 운영 API를 연결할 때 이 책임을 유지한다.

## 4. 검증 기준과 반복

검증은 scope_key, basis, results를 갖는다. basis는 기존 `evidence.capture_source_snapshot`의 complete/errors/fingerprint/sources와 환경 기준 ref/revision을 사용한다. 결과별 ID, Pass, 실제 command argv, 증적 ref/revision이 필요하다.

인수 시 현재 관측 basis와 시험 당시 basis가 일치해야 한다. 필수 시험은 각각 한 번씩 빠짐없이 존재해야 하며 Fail/Not Run/Planned/environment_blocked는 통과가 아니다. `verification_key`는 범위·소스·환경·명령·결과·증적 기준을 함께 묶는다. 상태에는 상세 파일 목록을 재복사하지 않고 지문과 참조만 보존한다.

수정으로 구현에 돌아가면 현재 검증을 무효화한다. 업무 변경으로 기획에 돌아가면 기존 구현 허가도 재사용하지 않는다. 이전 결과와 결정은 work_history에 보존하며, 다른 범위의 open issues나 과거 실패 기록을 지우지 않는다. 완료는 이번 범위의 완료이지 제품 개발의 종료가 아니다. 명확한 다음 국소 수정은 새 범위와 허가가 있으면 구현부터 열 수 있다.

소스 관측의 기존 한계(명시 범위, 제외 파일, 비원자 관측, Git 상태 변경 등)는 그대로다. 환경/의존성의 실제 동일성이나 시험의 진실성·충분성은 해시만으로 증명하지 않는다. 후속 수집기는 코드/시험/lockfile과 관련 환경을 빠짐없이 관측하고 근거를 확인해야 한다. 단순 HEAD 비교나 worker 성공 문장으로 대체하지 않는다.

## 5. 지속 점검

Product 운영 지침을 바꿀 때 현재 범위에서 다음 사례를 함께 확인한다. 매 사용자 작업에 새 체크리스트를 채우라는 뜻이 아니다.

- Run 없는 국소 수정에 Run/worker/전체 시험을 다시 강제하지 않는가.
- 허가된 결함 수정·재시험은 이어가고, 검증 전용 담당자의 권한은 확장하지 않는가.
- 같은 원본의 문구 정리와 계약·시험·소스 변경을 구별하는가.

`test_product_policy.py`는 이번에 발견한 Core/skill 충돌의 재발을 검사한다. 모든 자연어 충돌을 자동 판정하는 검사는 아니다. 새로운 실제 사례가 나오면 관련 지침을 고치고 해당 사례의 회귀 시험을 추가한다. 설계 참고 문서를 startup 필수 입력으로 늘리거나 Product 예외를 여러 문서에 복제하지 않는다.

## 6. 이번 검증

- 새 문맥의 native contract-reviewer가 승인 authority의 잘못된 타입과 손상된 history에서 진단 대신 예외가 발생하는 두 문제를 발견했다. 두 경로를 보정하고 부정 입력 시험을 추가했으며 재검토에서 잔여 지적은 없었다.
- 최종 상태 계약 15개와 지침 회귀 5개 통과. init/upgrade 문서 라우팅·기존 산출물 보존 3개 통과.
- 전체 Python 회귀는 보정 전 203개 실행, 3개 skip으로 통과했고 이후 변경은 위 영향 시험으로 재확인했다. 초기화 smoke 12단계, 기존 Product/PoC/Audit fixture smoke 84단계 통과.
- 기존 evidence 모듈의 Python pathlib deprecation warning은 남아 있다. Windows 로컬 검증이며 운영 프로세스·Dashboard 활성화나 실제 Product 인수 시험의 증적은 아니다.
