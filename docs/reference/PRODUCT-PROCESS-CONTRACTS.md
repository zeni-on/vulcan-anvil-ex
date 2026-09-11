# Product Process Contract Prototype

- 상태: 2026-09-11 단계 1 상태 계약 + 단계 2a 범위별 검사 + 단계 2b 실험 상태 저장 CLI 구현. 일반 init/이행/Dashboard는 미연결.
- 원본 설계: [3구간 운영](PRODUCT-ITERATIVE-PROCESS-DESIGN.md), [시나리오](PRODUCT-ITERATIVE-PROCESS-SCENARIOS.md)
- 구현: [product_process.py](../../vulcan_core/product_process.py), [product_readiness.py](../../vulcan_core/product_readiness.py), [product_session.py](../../vulcan_core/product_session.py). [상태 계약](../../scripts/regression/tests/test_product_process.py), [범위별 검사](../../scripts/regression/tests/test_product_readiness.py), [저장·CLI 반복 시험](../../scripts/regression/tests/test_product_session.py).

이 문서는 프레임워크 개발·검토용이다. 프로젝트 에이전트의 시작 입력에 추가하지 않는다.
일반 init/upgrade는 새 모델을 활성화하지 않는다. 현재 Product의 기존 Gate 운영은 유지한다.
**병합과 일반 활성화는 다르다.** main에 코드를 병합해도 기존 프로젝트가 즉시 3구간으로 바뀌지는 않는다. 지금은 별도 합성 파일럿에서 CLI로 상태를 실제 저장하며 반복 흐름을 시험할 수 있다. Dashboard·branch/release 소비자·이행 검증 후 일반 적용 여부를 결정한다.

## 1. 이번 단계의 경계

- `new_session`, `assess_transition`, `advance`, `open_work`, `describe`는 파일·Git·프로세스를 변경하지 않는다. 상태 변경 함수는 검증 후 복사본만 반환한다.
- 현재 상태는 `current_gate` 하나다. `gate_status`는 planning/impl/acceptance의 상태이며 현재 구간과 모순되면 진단한다.
- `process_model`이 없으면 Product/Audit/PoC 모두 기존 경로다. 명시된 미지원 값, 잘못된 profile이나 상태는 거부한다.
- 표식이 있는 유효한 세션의 `status --check`는 현재 범위의 문서/증적을 읽고 `scoped_check`를 반환한다. 검사 통과는 exit 0, 미완성·누락·불일치는 exit 1이다. 승인 여부는 `transition.allowed/reasons`로 별도 표시하므로 exit 0을 승인으로 해석하지 않는다.
- 알 수 없거나 잘못된 모델/상태와 새 모델의 `--trace-detail`은 exit 2다. 기존 전체 Gate 추적 검사를 새 상태에 호출하지 않는다.
- 기존 CLI의 상태 변경·검사는 표식이 있는 세션에서 exit 2로 중단한다. 새 상태를 옛 Gate로 해석하거나 upgrade로 지우지 않는다. `load_session`/`save_session`에도 방어선을 둔다. 예외는 자체 검증을 거치는 `session --process-request`와 허가된 구간의 `execute --verify`뿐이다.
- `status --check`와 상태 요청 미리보기는 명령 실행·파일 변경·승인 생성·상태 전환을 하지 않는다. 단계 2b의 명시 `--apply`는 검증한 상태만 저장하며 Git commit/push, Run, branch 생성, release는 수행하지 않는다.
- 전체 QA 위임 라우팅, branch/release 소비자, Dashboard, 사용자 프로젝트 이행은 후속이다. 기존 세션에 표식을 수동 추가하여 운영하지 않는다.

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
- implement에는 합의한 구현 범위의 빌드/자체 테스트와 그 소스 관측 기록이 포함된다. 별도 verify 결정은 인수 검증으로의 인계·실행 권한이다. 명령 이름 `execute --verify`는 소스/명령 관측기이므로, impl에서 사용했다고 인수 검증 권한이나 Pass·수용 결정을 생성하지 않는다. 합의한 범위 밖 명령 실행은 별도 권한이 필요하다.
- 검증만 맡은 담당자에게 코드 수정 권한을 추가하지 않는다.
- accept는 실행 허가와 분리하며 해당 `verification_key`를 명시한다. 다른 결과에 대한 수용을 재사용하지 않는다.
- merge/push/deploy/release는 이 계약의 actions가 아니다. 인수가 해당 권한을 만들지 않는다.

이 모듈은 사용자 대화를 해석하거나 신원을 인증하지 않는다. ref와 actor를 적었다고 실제 동의가 증명되지는 않는다. 신뢰할 수 있는 호출자가 실제 근거·권한·철회 여부를 확인해야 하며, 프로토타입은 전달된 근거 사이의 연결을 검사한다. 운영 API를 연결할 때 이 책임을 유지한다.

## 4. 검증 기준과 반복

검증은 scope_key, basis, results를 갖는다. basis는 기존 `evidence.capture_source_snapshot`의 complete/errors/fingerprint/sources와 환경 기준 ref/revision을 사용한다. 결과별 ID, Pass, 실제 command argv, 증적 ref/revision이 필요하다.

인수 시 현재 관측 basis와 시험 당시 basis가 일치해야 한다. 필수 시험은 각각 한 번씩 빠짐없이 존재해야 하며 Fail/Not Run/Planned/environment_blocked는 통과가 아니다. `verification_key`는 범위·소스·환경·명령·결과·증적 기준을 함께 묶는다. 상태에는 상세 파일 목록을 재복사하지 않고 지문과 참조만 보존한다.

수정으로 구현에 돌아가면 현재 검증을 무효화한다. 업무 변경으로 기획에 돌아가면 기존 구현 허가도 재사용하지 않는다. 이전 결과와 결정은 work_history에 보존하며, 다른 범위의 open issues나 과거 실패 기록을 지우지 않는다. 완료는 이번 범위의 완료이지 제품 개발의 종료가 아니다. 명확한 다음 국소 수정은 새 범위와 허가가 있으면 구현부터 열 수 있다.

소스 관측의 기존 한계(명시 범위, 제외 파일, 비원자 관측, Git 상태 변경 등)는 그대로다. 환경/의존성의 실제 동일성이나 시험의 진실성·충분성은 해시만으로 증명하지 않는다. 후속 수집기는 코드/시험/lockfile과 관련 환경을 빠짐없이 관측하고 근거를 확인해야 한다. 단순 HEAD 비교나 worker 성공 문장으로 대체하지 않는다.

### 4.1 범위별 검사 연결 (단계 2a)

| 현재 구간 | `status --check`가 확인하는 것 | 확인하지 않는 것 |
| --- | --- | --- |
| 기획·설계 | 지정된 현재 계약의 정의 행, 필수 시험의 방법·기대 결과, 참조 원본의 고정 revision | 시험 실행 결과. `Planned`는 정상이며 미래 범위의 미완성 문서를 요구하지 않음 |
| 구현 | 위 기준 + 명시 소스/시험/의존성 범위 및 환경 명세 파일을 실제로 관측할 수 있는지 | 인수 Pass나 구현 품질의 자동 보증. handoff 근거·검증 허가는 별도 |
| 인수 검증 | 필수 시험별 실제 명령 관측 JSON, 성공 종료, 현재 소스/환경 명세와 시험 전후 지문의 일치 | 결과 수용·merge·배포 허가 |
| 이번 범위 완료 | 저장된 승인·결과 계약과 현재 문서/증적의 유효성 재확인 | 다른 범위의 미완료 의무 해소, 제품 전체 릴리즈 준비 |

- `local_reference(project_dir, ref, markdown=True)`가 원본 bytes의 `sha256:` revision을 계산한다. 호출자는 이 값을 범위 계약에 연결하며 사람이 SHA를 작성하지 않는다. Git 커밋을 요구하지 않으므로 미커밋 원본도 식별된다.
- Markdown anchor는 검사할 본문을 좁힌다. **revision은 문서 전체 bytes 기준**이므로 같은 파일의 다른 절만 수정해도 기준 변경을 알린다. 최초 구현은 보수적인 방식이며, 재검토 없이 자동으로 새 revision/승인을 찍지 않는다.
- 선택 절과 상위 절, 같은 문서의 공통 보안/권한/오류/호환 조건을 함께 확인하고 `common_context`에 위치를 보여준다. 본문에서 연결한 현재 Markdown 원본도 범위에 묶여 있어야 한다. 자동 전체 폴더 탐색이나 링크의 무제한 확장은 하지 않는다.
- candidate/history 본문은 현재 정의로 사용하지 않는다. 직접 지정한 anchor가 candidate/history이거나 상태 표식이 충돌하면 진단한다. 관련 ID는 본문 언급이나 링크가 아니라 표 첫 컬럼의 정의 행에서 확인한다. prose-only 정의는 추정해서 통과시키지 않는다.
- 필수 시험은 기존 Product 시험 표의 `Method/명령·방법`, `Expected/성공 기준`을 읽는다. 기존 Audit 템플릿 전체를 채우거나 기획 중 결과를 Pass로 바꾸게 하지 않는다.
- 참조는 프로젝트 내부의 정상 파일로 제한하고 symlink/junction, 경로 이탈, remote/query, 문서 32개 초과, 파일 2MB 초과를 진단한다. 원문 전체를 status 출력에 복사하지 않고 위치/이유를 반환한다.

### 4.2 실행 증적의 실제 연결

합성 검증의 인수 수집기는 기존 `evidence.record_verification`이 작성한 `kind: explicit_verification`, `schema_version: 1` JSON을 사용한다. 모든 기존 Product에 새 로그 형식을 강제하는 변경이 아니다. 다른 native QA 결과를 이 계약으로 연결하는 운영 경로는 후속에서 결정한다.

- `current_work.verification`은 4절의 구조를 유지한다. 결과의 `evidence.ref/revision`은 실제 JSON 파일과 해시이며 필수 시험 여러 개를 실행한 하나의 suite 보고서를 함께 참조할 수 있다. 시험별 실행 범위·assertion의 충분성은 검토자가 확인한다.
- 구현 인계에서는 `current_work.basis`, 인수에서는 `verification.basis`의 명시 `source.sources`를 다시 관측한다. 앱 코드, 실제 테스트, lockfile/의존성 정의 등을 누락하지 않는 책임은 호출자에게 있다. 범위를 스스로 추론해 확장하지 않는다.
- 상태·잠금·생성 증적은 테스트 입력 소스 범위에서 분리한다. `--source .`로 프레임워크 상태까지 묶으면 정상 상태 저장도 소스 변경으로 잡힐 수 있으므로 실제 코드/시험/의존성/환경 명세 경로를 지정한다.
- `basis.environment`는 실제 로컬 환경 명세 파일의 고정 참조다. 이 파일도 명시 소스 스냅샷에 포함되어야 시험 당시 버전과 현재 버전을 비교할 수 있다. 런타임/서비스/브라우저 등의 관측값을 기록하는 내용은 프로젝트별로 정하며, 파일이 같다고 실행 중 환경이 같다고 인증하지 않는다.
- 명령 argv 불일치, 실패/기동 오류, 불완전 관측, 시험 중 소스 변경, 현재 소스/환경 명세 변경, 수정된 증적, 필수 결과 누락은 차단한다. `Pass` 한 줄이나 기존 Markdown 결과만으로 실제 실행을 추정하지 않는다.
- 파일/명령 기록은 서명된 감사 로그가 아니다. 조작 방지·실제 권한 인증·시험 의미 분석까지 수행한다고 주장하지 않는다. 명령과 원본의 관련성, 제외 환경/비밀 설정, 현재 운영 조건은 별도로 확인한다.
- `open_issues`는 지우지 않고 `unresolved_obligations`로 남은 수를 표시한다. 현재 범위의 검사 통과로 과거 실패를 삭제하거나 범위 밖 이슈를 완료 처리하지 않는다.

### 4.3 상태 저장 CLI (단계 2b)

새 최상위 명령을 늘리지 않고 기존 `session`에 별도 실험 경로를 둔다. 아래 입력은 프레임워크/어댑터 개발용 기계 계약이며, 사용자에게 매번 JSON이나 새 Run을 작성하라는 운영 규칙이 아니다. stdin을 쓰면 별도 요청 문서를 만들 필요가 없다.

```text
python vulcan.py session --process-request request.json --json
python vulcan.py session --process-request request.json --apply --json
python vulcan.py session --process-request - --json
```

기본 및 `--dry-run`은 미리보기다. `--apply`만 상태를 저장한다. 두 옵션을 함께 지정하거나 기존 `--gate/--status/--approved/--approval-evidence`와 섞으면 거부한다. 기존 profile의 `session --gate ... --status ...` 동작은 유지한다.

요청 공통 필드는 `process_model: product-iterative-v1`, `action`, `expected_session_revision`이다. 상태 revision은 읽기 전용 `status --json`이 현재 `session.json` bytes에서 계산해 반환한다. 사람이 Git SHA나 새 승인 ID를 만드는 방식이 아니다.

| action | 입력 | 동작 |
| --- | --- | --- |
| `start` | `scope`, `expected_session_revision: null` | session.json이 없는 **별도 실험 폴더**에서 planning 세션 생성. 기존 init 프로젝트의 profile/상태를 전환하지 않음 |
| `advance` | `target`, 해당 경계에 필요한 `decision`/`basis`/`verification`/`reason` | 현재 범위로 인접 구간 진행 또는 허가된 수정/기획 복귀 |
| `open-work` | `scope`, `target`, `reason`, 필요한 경우 `decision` | 새 범위를 열고 이전 결과/판정 보존. 기획 재정의 또는 완료 후 다음 작업 |

- planning → impl은 실제 문서 준비 검사와 scoped implement 결정이 필요하다.
- impl → acceptance는 명시 `basis`를 현재 파일에서 재관측하고 verify 권한을 확인한다. 아직 실행 결과를 Pass로 만들지 않는다.
- acceptance → completed는 명시 `verification`의 실제 증적/현재 소스 검사를 통과하고, 그 `verification_key`에 대한 별도의 accept 결정이 있어야 한다. 수용 결정이 없으면 미리보기에서 결과 키와 차단 이유를 반환하되 저장하지 않는다.
- acceptance → impl은 사유와 fix 권한이 필요하다. 이미 허가된 fix 권한은 재사용하지만 verify만 위임된 실행자는 수정 권한을 얻지 않는다. impl/acceptance → planning은 사유를 남기고 이전 실행 허가를 초기화한다.
- `open-work`로 바로 impl에 들어가려면 이전 범위가 completed이고 새 범위의 준비 검사·구현 결정이 있어야 한다. 진행 중 작업을 새 범위로 바꿀 때에는 planning으로 돌아간다.
- 준비 결과는 저장 직전에 검사기가 생성한다. 입력의 임의 `ready: true`, `approved: true`, `readiness`나 사용하지 않는 필드는 허용하지 않는다. 승인 결정의 원본 확인·권한 철회 여부는 여전히 신뢰할 수 있는 호출자의 책임이다.

**저장과 충돌**

- 미리보기는 파일/잠금/폴더를 만들지 않는다. apply는 `.vulcan/product-process.lock`의 배타 잠금을 잡고 현재 상태·문서·증적을 다시 읽는다. 과거 미리보기 결과를 그대로 저장하지 않는다.
- `expected_session_revision`이 달라졌으면 재시도 요청을 자동 작성하지 않고 `conflict`로 반환한다. 같은 요청을 두 실행자가 동시에 적용해도 하나만 저장된다.
- 새 상태를 임시 파일에 완전히 기록·flush한 후 `session.json`을 원자 교체한다. 저장 전 상태 변경을 다시 확인하며, 교체 실패 시 이전 상태를 보존하고 임시 파일을 정리한다. 일반적인 프로세스 중단에서도 이전 또는 새 JSON 전체가 남도록 하며 전원 장애까지의 내구성을 인증하지는 않는다.
- 잠금은 이 경로를 사용하는 writer 사이의 약속이다. 별도 편집기/worker의 직접 파일 변경이나 소스 전체를 동결하는 장치가 아니다. 호출자는 작업자 변경을 회수·정리한 뒤 전환하며, 소스 관측의 비원자적 한계는 유지한다.
- 남은 잠금은 PID와 활성 작업을 확인한 뒤 복구한다. 자동으로 잠금을 제거하거나 프로세스를 종료하지 않는다. 저장 후 잠금 정리에 실패하면 `applied: true`와 경고를 반환해 미저장으로 오인하지 않게 한다.
- 요청은 2MB, 세션은 8MB로 제한하고 중복 JSON 키·비유한 수·비정상 경로를 거부한다. 한도를 넘는 누적 이력의 별도 보존/정리는 일반 활성화 전 후속 검토 대상이며 과거 결과를 자동 삭제하지 않는다.

실험 세션의 `execute --verify`는 impl의 implement 권한(구현 self-check) 또는 acceptance의 verify 권한이 있을 때만 연결한다. 기존 명시 argv/소스/새 증적 파일 계약을 유지하고, planning/completed 또는 잘못된 모델에서는 실행 전에 차단한다. 검증 명령 자체가 상태를 전환하거나 수용 권한을 만들지 않는다.

결과는 `ready`(미리보기 가능), `applied`(저장됨), `blocked`(현재 준비/권한/증적 부족), `conflict`(revision/잠금 충돌), `invalid`(요청·저장·상태 계약 오류)로 구분한다. CLI exit는 앞의 두 상태가 0, blocked가 1, 나머지가 2다. 미리보기의 `current_gate`/`scope_key`/`session_revision`은 저장된 현재 값이며, 후보는 `proposed_gate`/`proposed_scope_key`/`proposed_session_revision`으로 구분한다. `--apply` 요청이 실패해도 과거 승인·상태를 맞춰서 지우지 않는다.

### 4.4 운영 소비자 연결 (단계 2c)

`process_model`이 있는 세션은 소비자가 지원 모델/형태를 검증한 뒤 읽는다. 표식이 없는 기존 Product/Audit/PoC는 기존 처리 경로이며 미지원·손상 모델을 legacy로 바꿔 읽지 않는다.

- Dashboard는 3구간과 현재 작업 ref/revision·관련 ID를 읽기 전용으로 표시한다. 기존 7개 Gate를 만들거나 진행 완료를 릴리즈로 해석하지 않는다. 화면은 저장 상태의 표시이며 원본 파일/시험/승인 신원을 독립 인증하는 검사기가 아니다.
- `status`/`branch-status`는 실제 Git 작업공간과 설정한 `workflow.integration_branch`를 조회한다. session의 과거 `branch_state`를 사실로 사용하지 않는다. 루트가 Git 저장소가 아니면 unmanaged로 표시하며, 상위 저장소를 상속한 하위 폴더나 Git 관측 실패는 확인 불가로 구별한다.
- `doctor`는 기존 환경 진단기를 재사용한다. 도구 설치/환경 결과와 제품 결함·수용 판단을 합치지 않으며 상태를 바꾸지 않는다.
- `execute --verify`의 구현 self-check는 구현 권한이 있을 때 worker branch에서도 가능하다. acceptance에서는 verify 권한과 설정한 통합 브랜치를 확인한다. single/disabled 정책 또는 명시적으로 해제한 branch guard는 존중한다. 독립 Git 저장소가 없는 합성 파일럿도 명시된 시험을 실행할 수 있으나, 모호한 Git 루트는 인수 실행 전에 차단한다. 새 QA worktree는 만들지 않는다.
- `release-pr --dry-run`은 이번 범위 completed, 현재 계약/증적 재검사, clean Git 작업공간, 실제 current/head/base 브랜치를 확인한다. 기존 Gate 5 승인서를 억지로 요구하지 않는다. 관련 없는 미처리 의무는 누락하지 않고 수량으로 노출하며 릴리즈 포함/제외 판단을 요청한다. 통과한 결과는 후보일 뿐 `release_authorized: false`, `publication_enabled: false`다.
- 미리보기는 PR body 파일도 쓰지 않고 `gh`/push/merge를 실행하지 않는다. 인수 당시 증적이 stale이면 후보를 차단한다. 현재 범위 밖 기능·과거 수용 전체의 배포 적합성을 인증하지 않는다.

이번에는 **조회와 명시 시험/미리보기**까지만 연결한다. `branch-start`의 상태/Git 복합 변경, native QA 위임·결과 회수, 실제 릴리즈 발행의 별도 승인/대상 revision 계약, 이행/기본 init 전환은 후속이다. 단순 조회를 가능하게 하려고 legacy save/session/gate-start/run-exec 차단을 해제하지 않는다. 기존 프로젝트와 PMTool/샘플 폴더는 자동 변환하지 않는다.

## 5. 지속 점검

Product 운영 지침을 바꿀 때 현재 범위에서 다음 사례를 함께 확인한다. 매 사용자 작업에 새 체크리스트를 채우라는 뜻이 아니다.

- Run 없는 국소 수정에 Run/worker/전체 시험을 다시 강제하지 않는가.
- 허가된 결함 수정·재시험은 이어가고, 검증 전용 담당자의 권한은 확장하지 않는가.
- 같은 원본의 문구 정리와 계약·시험·소스 변경을 구별하는가.

`test_product_policy.py`는 이번에 발견한 Core/skill 충돌의 재발을 검사한다. 모든 자연어 충돌을 자동 판정하는 검사는 아니다. 새로운 실제 사례가 나오면 관련 지침을 고치고 해당 사례의 회귀 시험을 추가한다. 설계 참고 문서를 startup 필수 입력으로 늘리거나 Product 예외를 여러 문서에 복제하지 않는다.

## 6. 단계별 검증

### 6.1 단계 1

- 새 문맥의 native contract-reviewer가 승인 authority의 잘못된 타입과 손상된 history에서 진단 대신 예외가 발생하는 두 문제를 발견했다. 두 경로를 보정하고 부정 입력 시험을 추가했으며 재검토에서 잔여 지적은 없었다.
- 최종 상태 계약 15개와 지침 회귀 5개 통과. init/upgrade 문서 라우팅·기존 산출물 보존 3개 통과.
- 전체 Python 회귀는 보정 전 203개 실행, 3개 skip으로 통과했고 이후 변경은 위 영향 시험으로 재확인했다. 초기화 smoke 12단계, 기존 Product/PoC/Audit fixture smoke 84단계 통과.
- 기존 evidence 모듈의 Python pathlib deprecation warning은 남아 있다. Windows 로컬 검증이며 운영 프로세스·Dashboard 활성화나 실제 Product 인수 시험의 증적은 아니다.

### 6.2 단계 2a

- 합성 임시 프로젝트에서 요청 보드의 기존 요청 보완/재제출, 이전 반려 내용·사유 보존, 소유자 권한 계약을 사용했다. 실제 Python assertion 명령으로 기록·지문 연결을 시험했으며 요청 보드 업무 기능 자체의 QA는 아니다. 사용자 프로젝트나 환경은 변경하지 않았다.
- 전체 Python 회귀 222개 실행, 4개 skip으로 통과했다. 이후 독립 리뷰 보정과 부정 시험을 추가한 최종 Product 관련 회귀는 118개 실행, 1개 skip으로 통과했다. 새 범위별 테스트는 21개이며 Windows에서 symlink 생성 권한이 없는 1개는 skip한다.
- 초기화 smoke 12단계, 기존 Product/PoC/Audit fixture smoke 84단계 통과. 변경은 Python 검사/문서에 한정되며 Dashboard 로컬 실행 검증은 하지 않았다.
- 새 문맥의 native contract-reviewer가 주석 내부 표의 잘못된 정의 인정과 링크 검사 한도 초과의 무진단 누락을 발견했다. 주석 보정의 후속 검토에서는 inline code의 주석 예시가 공통 보안 조건을 가리는 경우도 찾아 수정했다. 주석/코드 예시/링크 한도 회귀를 추가했고 최종 해당 경로 재검토에서 잔여 지적은 없었다. Orchestrator는 영향 시험으로 재검증했다.
- 증적은 source/환경 명세의 관측 일치를 확인할 뿐 실제 서비스 환경·시험 의미·사용자 신원을 인증하지 않는다. 모든 기획 의미나 보안 의무를 자동 판정하는 검사로 확대 해석하지 않는다.

### 6.3 단계 2b

- 임시 합성 프로젝트에서 CLI로 planning → impl → acceptance → completed → 다음 planning을 실제 저장했다. 실제 Python assertion의 소스 관측 JSON도 `execute --verify`로 수집했다. 요청 보드 업무 앱 자체의 QA나 PMTool 이행 시험은 아니다.
- 전체 Python 회귀는 보정 전 241개 실행, 4개 skip으로 통과했다. 깊은 JSON과 권한 구분 회귀를 추가한 Product 회귀는 135개 실행, 1개 skip으로 통과했다. 상태 저장/CLI 시험은 17개이며 초기화 smoke 12단계와 기존 profile fixture smoke 84단계도 통과했다.
- 새 문맥의 native contract-reviewer가 깊은 JSON의 traceback을 발견해 구조화된 invalid 응답으로 보정했다. 구현 self-check 관측과 인수 verify 권한의 구분도 계약·시험에 명시했다. 해당 경로 재검토에서 잔여 지적과 verify/accept 우회 사례는 없었다.
- Orchestrator는 최종 미리보기의 현재/제안 상태 구분, 승인 없는 인계 차단, revision 충돌, 동시 적용 1건만 저장, 쓰기 실패·잠금 정리 경고, 기존 profile 보존을 확인했다. 기존 pathlib deprecation warning은 남아 있다. Dashboard 로컬 실행과 일반 이행은 이번 검증 범위가 아니다.

### 6.4 단계 2c

- 전체 Python 회귀 254개 실행, 4개 skip으로 통과했다. 독립 리뷰 보정/호환 시험 추가 후 최종 소비자 시험 14개를 통과했다. 초기화 smoke 12단계와 기존 profile fixture smoke 84단계도 통과했다.
- 새 문맥의 native contract-reviewer가 다른 `--project-dir`을 지정할 때 호출 위치의 branch 정책을 검사하던 오류와 `main~1` 같은 revision을 branch로 인정하던 문제를 찾았다. 대상 workspace/config와 정확한 Git ref 확인으로 보정하고 실제 Git/CLI 재현 시험을 추가했다. 재검토에서 잔여 지적은 없었다.
- Dashboard 담당 native worker는 schema/loader/화면/시험을 변경했고, Orchestrator는 diff와 저장 상태 표시·미지원 모델 차단을 확인했다. 최종 typecheck/production build와 Jest 300개가 통과했다. 전체 E2E 41개 통과 후 캡처에서 모바일 높이 제한을 발견해 보정했으며, A/A2/B 모바일 확인을 포함한 최종 Product E2E 20개도 통과했다. 390px/1440px 캡처를 직접 확인했다.
- UI fixture는 저장 상태 표시 시험이며, 실행 권한/실제 증적의 유효성은 Python 계약/명령 시험이 검증한다. 화면 자체가 사용자 승인이나 전체 제품 릴리즈를 인증하지 않는다. 실제 PMTool/샘플 프로젝트는 변경하지 않았다.
- 기존 pathlib/caniuse-lite 경고가 남았다. production dependency audit의 high 이상 기준은 통과했지만 DOMPurify/Mermaid의 moderate advisory 2건은 별도 의존성 보강 대상으로 남긴다. 이번 PR은 의존성 버전을 바꾸지 않는다.
