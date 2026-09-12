# Product Process Contracts

- 상태: 2026-09-12 신규 `init --profile product`에 반복 프로세스 연결. 기존 프로젝트 이행과 자동 릴리즈 발행은 비활성화. 설치/첫 범위/호환 검증은 [일반 사용 검증](PRODUCT-NEW-PROJECT-VERIFICATION.md)을 따른다.
- 원본 설계: [3구간 운영](PRODUCT-ITERATIVE-PROCESS-DESIGN.md), [시나리오](PRODUCT-ITERATIVE-PROCESS-SCENARIOS.md)
- 구현: [product_process.py](../../vulcan_core/product_process.py), [product_readiness.py](../../vulcan_core/product_readiness.py), [product_session.py](../../vulcan_core/product_session.py), [product_consumers.py](../../vulcan_core/product_consumers.py). [상태 계약](../../scripts/regression/tests/test_product_process.py), [범위별 검사](../../scripts/regression/tests/test_product_readiness.py), [저장·CLI 반복 시험](../../scripts/regression/tests/test_product_session.py), [운영 소비자 시험](../../scripts/regression/tests/test_product_consumers.py).

이 문서는 프레임워크 개발·검토용이다. 프로젝트 에이전트의 시작 입력에 추가하지 않는다.
신규 Product 초기화만 `product-iterative-v1`로 시작한다. `upgrade`는 기존 모델, 현재 작업·승인·이력과 작성 문서를 보존한다. 표식 없는 Product와 Audit/PoC는 기존 Gate 운영을 유지한다.
새 Product에서도 상태 저장·검사·브랜치 준비·QA 전달/시험/결과 회수는 명시 작업이다. `completed`는 이번 범위 인수 완료이며, 실제 PR/merge/push/배포는 별도 승인을 확인한 Orchestrator의 Git/호스팅 도구 작업이다. 자동 발행을 활성화의 전제나 완료 의무로 추가하지 않는다.

## 1. 이번 단계의 경계

- `new_session`, `assess_transition`, `advance`, `open_work`, `describe`는 파일·Git·프로세스를 변경하지 않는다. 상태 변경 함수는 검증 후 복사본만 반환한다.
- 현재 상태는 `current_gate` 하나다. `gate_status`는 planning/impl/acceptance의 상태이며 현재 구간과 모순되면 진단한다.
- `process_model`이 없으면 Product/Audit/PoC 모두 기존 경로다. 명시된 미지원 값, 잘못된 profile이나 상태는 거부한다.
- 표식이 있는 유효한 세션의 `status --check`는 현재 범위의 문서/증적을 읽고 `scoped_check`를 반환한다. 검사 통과는 exit 0, 미완성·누락·불일치는 exit 1이다. 승인 여부는 `transition.allowed/reasons`로 별도 표시하므로 exit 0을 승인으로 해석하지 않는다.
- 알 수 없거나 잘못된 모델/상태와 새 모델의 `--trace-detail`은 exit 2다. 기존 전체 Gate 추적 검사를 새 상태에 호출하지 않는다.
- 아직 연결하지 않은 legacy 명령은 표식이 있는 세션에서 exit 2로 중단한다. 새 상태를 옛 Gate로 해석하거나 upgrade로 지우지 않는다. `load_session`/`save_session`에도 방어선을 둔다. 지원하는 조회·진단·미리보기는 4.4절을 따르며, 상태 저장은 자체 검증을 거치는 `session --process-request`, 명령 증적 수집은 허가된 구간의 `execute --verify`로 수행한다.
- `status --check`와 상태 요청 미리보기는 명령 실행·파일 변경·승인 생성·상태 전환을 하지 않는다. 단계 2b의 명시 `--apply`는 검증한 상태만 저장하며 Git commit/push, Run, branch 생성, release는 수행하지 않는다.
- Dashboard/실제 브랜치 조회·환경 진단·인수 시험·릴리즈 후보 미리보기는 4.4절까지 연결했다. 4.5절은 상태 저장과 분리한 명시 브랜치 준비, 4.6절은 Run 없는 QA 전달 후보와 결과 회수 경로다. 실제 발행과 사용자 프로젝트 이행은 후속이다. 기존 세션에 표식을 수동 추가하여 운영하지 않는다.

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
- implement에는 합의한 구현 범위의 빌드/자체 테스트와 실제 실행 기록이 포함된다. 별도 verify 결정은 인수 검증으로의 인계·실행 권한이다. `execute --verify`는 명령 실행 기록기이므로 impl에서 사용했다고 인수 검증 권한이나 Pass·수용 결정을 생성하지 않는다. 합의한 범위 밖 명령 실행은 별도 권한이 필요하다.
- 검증만 맡은 담당자에게 코드 수정 권한을 추가하지 않는다.
- accept는 실행 허가와 분리하며 해당 `verification_key`를 명시한다. 다른 결과에 대한 수용을 재사용하지 않는다.
- merge/push/deploy/release는 이 계약의 actions가 아니다. 인수가 해당 권한을 만들지 않는다.

이 모듈은 사용자 대화를 해석하거나 신원을 인증하지 않는다. ref와 actor를 적었다고 실제 동의가 증명되지는 않는다. 신뢰할 수 있는 호출자가 실제 근거·권한·철회 여부를 확인해야 하며, 프로토타입은 전달된 근거 사이의 연결을 검사한다. 운영 API를 연결할 때 이 책임을 유지한다.

## 4. 검증 기준과 반복

검증은 scope_key, basis, results를 갖는다. basis에는 환경 명세 참조를 연결하며 Git 식별자나 소스 스냅샷은 요구하지 않는다. 범위·승인·테스트 정의 revision은 유지한다. 결과별 ID, Pass, 실제 command argv, 증적 ref/revision이 필요하다.

필수 시험은 각각 한 번씩 빠짐없이 존재해야 하며 Fail/Not Run/Planned/environment_blocked는 통과가 아니다. `verification_key`는 범위·환경 명세 참조·명령·결과·증적 기준을 연결하는 수용 대상이지 소스 신선도 증명이 아니다. Git/content-source 비교로 인수를 차단하지 않는다.

수정으로 구현에 돌아가면 현재 검증을 무효화한다. 업무 변경으로 기획에 돌아가면 기존 구현 허가도 재사용하지 않는다. 이전 결과와 결정은 work_history에 보존하며, 다른 범위의 open issues나 과거 실패 기록을 지우지 않는다. 완료는 이번 범위의 완료이지 제품 개발의 종료가 아니다. 명확한 다음 국소 수정은 새 범위와 허가가 있으면 구현부터 열 수 있다.

Orchestrator는 구현·테스트·의존성·실행 환경의 변경과 실제 시험 범위를 확인해 관련 재시험을 판단한다. Git 상태나 내용 지문 비교를 필수 기제로 만들지 않는다. worker 성공 문장만으로 시험의 충분성이나 실행 환경을 확정하지 않는다. 과거 소스 관측 보고서는 재작성 없이 읽되 폐기된 검사를 현재 의무로 되살리지 않는다.

### 4.1 범위별 검사 연결 (단계 2a)

| 현재 구간 | `status --check`가 확인하는 것 | 확인하지 않는 것 |
| --- | --- | --- |
| 기획·설계 | 지정된 현재 계약의 정의 행, 필수 시험의 방법·기대 결과, 참조 원본의 고정 revision | 시험 실행 결과. `Planned`는 정상이며 미래 범위의 미완성 문서를 요구하지 않음 |
| 구현 | 위 기준 + 환경 명세 참조와 인계 준비 | 인수 Pass나 구현 품질의 자동 보증. handoff 근거·검증 허가는 별도 |
| 인수 검증 | 필수 시험별 실제 명령 실행 JSON, 성공 종료, 결과·증적 연결 | 소스/환경 신선도 자동 판정, 결과 수용·merge·배포 허가 |
| 이번 범위 완료 | 저장된 승인·결과 계약과 현재 문서/증적의 유효성 재확인 | 다른 범위의 미완료 의무 해소, 제품 전체 릴리즈 준비 |

- `local_reference(project_dir, ref, markdown=True)`가 원본 bytes의 `sha256:` revision을 계산한다. 호출자는 이 값을 범위 계약에 연결하며 사람이 SHA를 작성하지 않는다. Git 커밋을 요구하지 않으므로 미커밋 원본도 식별된다.
- Markdown anchor는 검사할 본문을 좁힌다. **revision은 문서 전체 bytes 기준**이므로 같은 파일의 다른 절만 수정해도 기준 변경을 알린다. 최초 구현은 보수적인 방식이며, 재검토 없이 자동으로 새 revision/승인을 찍지 않는다.
- 선택 절과 상위 절, 같은 문서의 공통 보안/권한/오류/호환 조건을 함께 확인하고 `common_context`에 위치를 보여준다. 본문에서 연결한 현재 Markdown 원본도 범위에 묶여 있어야 한다. 자동 전체 폴더 탐색이나 링크의 무제한 확장은 하지 않는다.
- candidate/history 본문은 현재 정의로 사용하지 않는다. 직접 지정한 anchor가 candidate/history이거나 상태 표식이 충돌하면 진단한다. 관련 ID는 본문 언급이나 링크가 아니라 표 첫 컬럼의 정의 행에서 확인한다. prose-only 정의는 추정해서 통과시키지 않는다.
- 필수 시험은 기존 Product 시험 표의 `Method/명령·방법`, `Expected/성공 기준`을 읽는다. 기존 Audit 템플릿 전체를 채우거나 기획 중 결과를 Pass로 바꾸게 하지 않는다.
- 참조는 프로젝트 내부의 정상 파일로 제한하고 symlink/junction, 경로 이탈, remote/query, 문서 32개 초과, 파일 2MB 초과를 진단한다. 원문 전체를 status 출력에 복사하지 않고 위치/이유를 반환한다.

### 4.2 실행 증적의 실제 연결

인수 수집기는 `evidence.record_verification`이 작성한 `kind: explicit_verification`, `schema_version: 2` JSON의 명시 argv, cwd, 실행 시간과 exit code를 사용한다. 기존 schema 1 관측 보고서는 읽기 호환으로 다루며 이력을 재생성하지 않는다. 모든 기존 Product에 새 로그 형식을 강제하는 변경이 아니다. [실제 위임/복구 시험](PRODUCT-PROCESS-EXECUTION-VERIFICATION.md)은 당시 관측기의 과거 기록이며 새 정책의 검증 결과로 바꾸어 읽지 않는다.

- `current_work.verification`은 4절의 구조를 유지한다. 결과의 `evidence.ref/revision`은 실제 JSON 파일과 해시이며 필수 시험 여러 개를 실행한 하나의 suite 보고서를 함께 참조할 수 있다. 시험별 실행 범위·assertion의 충분성은 검토자가 확인한다.
- 구현 인계의 `current_work.basis`와 인수의 `verification.basis`는 환경 명세 참조를 유지한다. 소스 파일 목록이나 스냅샷을 요구하거나 재관측하지 않는다.
- `--source`는 선택적인 설명용 경로다. 상태·문서·커밋 변경을 자동으로 소스 신선도 실패로 판정하지 않는다.
- `basis.environment`는 로컬 환경 명세 파일의 참조다. 참조 파일의 revision 변경은 기존대로 진단하지만, 런타임/서비스/브라우저 등 실제 실행 환경의 동일성을 인증하지 않는다. 변경 영향과 재시험 필요성은 Orchestrator가 판단한다.
- 명령 argv 불일치, 실패/기동 오류, 수정된 증적, 필수 결과 누락은 차단한다. `Pass` 한 줄이나 기존 Markdown 결과만으로 실제 실행을 추정하지 않는다. 소스/Git 신선도 검사는 별도로 요구하지 않는다.
- 파일/명령 기록은 서명된 감사 로그가 아니다. 조작 방지·실제 권한 인증·시험 의미 분석까지 수행한다고 주장하지 않는다. 명령과 원본의 관련성, 제외 환경/비밀 설정, 현재 운영 조건은 별도로 확인한다.
- `open_issues`는 지우지 않고 `unresolved_obligations`로 남은 수를 표시한다. 현재 범위의 검사 통과로 과거 실패를 삭제하거나 범위 밖 이슈를 완료 처리하지 않는다.

### 4.3 상태 저장 CLI (단계 2b)

새 최상위 명령을 늘리지 않고 기존 `session`에 반복 Product 경로를 둔다. 아래 입력은 프레임워크/어댑터용 기계 계약이며, 사용자에게 매번 JSON이나 새 Run을 작성하라는 운영 규칙이 아니다. stdin을 쓰면 별도 요청 문서를 만들 필요가 없다.

```text
python vulcan.py session --process-request request.json --json
python vulcan.py session --process-request request.json --apply --json
python vulcan.py session --process-request - --json
```

기본 및 `--dry-run`은 미리보기다. `--apply`만 상태를 저장한다. 두 옵션을 함께 지정하거나 기존 `--gate/--status/--approved/--approval-evidence`와 섞으면 거부한다. 기존 profile의 `session --gate ... --status ...` 동작은 유지한다.

요청 공통 필드는 `process_model: product-iterative-v1`, `action`, `expected_session_revision`이다. 상태 revision은 읽기 전용 `status --json`이 현재 `session.json` bytes에서 계산해 반환한다. 사람이 Git SHA나 새 승인 ID를 만드는 방식이 아니다.

| action | 입력 | 동작 |
| --- | --- | --- |
| `start` | `scope`, `expected_session_revision: null` | session.json 없는 별도 합성 시험 폴더용. init 이후에는 이미 세션이 있으므로 사용하지 않으며 기존 프로젝트 전환에도 사용하지 않음 |
| `advance` | `target`, 해당 경계에 필요한 `decision`/`basis`/`verification`/`reason` | 현재 범위로 인접 구간 진행 또는 허가된 수정/기획 복귀 |
| `open-work` | `scope`, `target`, `reason`, 필요한 경우 `decision` | 새 범위를 열고 이전 결과/판정 보존. 기획 재정의 또는 완료 후 다음 작업 |

신규 init의 `work`는 생성된 `docs/product/PRODUCT_BRIEF.md`와 당시 내용 revision을 참조한다. 나머지 범위 목록과 결정/이력은 비어 있다. `status`는 유효한 planning, `status --check`는 `incomplete_scope`를 반환하는 것이 정상이다. Orchestrator는 실제 업무 대화와 필요한 원본 작성 후 `open-work`, `target: planning`으로 첫 범위를 미리보기/적용한다. 템플릿 생성만으로 요구/계약/시험이나 승인을 만들지 않는다.

- planning → impl은 실제 문서 준비 검사와 scoped implement 결정이 필요하다.
- impl → acceptance는 명시 `basis`의 환경 명세 참조와 verify 권한을 확인한다. 아직 실행 결과를 Pass로 만들지 않는다.
- acceptance → completed는 명시 `verification`의 실제 실행 증적 검사를 통과하고, 그 `verification_key`에 대한 별도의 accept 결정이 있어야 한다. 수용 결정이 없으면 미리보기에서 결과 키와 차단 이유를 반환하되 저장하지 않는다. 소스 스냅샷 비교는 하지 않는다.
- acceptance → impl은 사유와 fix 권한이 필요하다. 이미 허가된 fix 권한은 재사용하지만 verify만 위임된 실행자는 수정 권한을 얻지 않는다. impl/acceptance → planning은 사유를 남기고 이전 실행 허가를 초기화한다.
- `open-work`로 바로 impl에 들어가려면 이전 범위가 completed이고 새 범위의 준비 검사·구현 결정이 있어야 한다. 진행 중 작업을 새 범위로 바꿀 때에는 planning으로 돌아간다.
- 준비 결과는 저장 직전에 검사기가 생성한다. 입력의 임의 `ready: true`, `approved: true`, `readiness`나 사용하지 않는 필드는 허용하지 않는다. 승인 결정의 원본 확인·권한 철회 여부는 여전히 신뢰할 수 있는 호출자의 책임이다.

**저장과 충돌**

- 미리보기는 파일/잠금/폴더를 만들지 않는다. apply는 `.vulcan/product-process.lock`의 배타 잠금을 잡고 현재 상태·문서·증적을 다시 읽는다. 과거 미리보기 결과를 그대로 저장하지 않는다.
- `expected_session_revision`이 달라졌으면 재시도 요청을 자동 작성하지 않고 `conflict`로 반환한다. 같은 요청을 두 실행자가 동시에 적용해도 하나만 저장된다.
- 새 상태를 임시 파일에 완전히 기록·flush한 후 `session.json`을 원자 교체한다. 저장 전 상태 변경을 다시 확인하며, 교체 실패 시 이전 상태를 보존하고 임시 파일을 정리한다. 일반적인 프로세스 중단에서도 이전 또는 새 JSON 전체가 남도록 하며 전원 장애까지의 내구성을 인증하지는 않는다.
- 잠금은 이 경로를 사용하는 writer 사이의 약속이다. 별도 편집기/worker의 직접 파일 변경이나 소스 전체를 동결하는 장치가 아니다. 호출자는 작업자 변경을 회수·정리하고 영향과 필요한 관련 재시험을 확인한 뒤 전환한다.
- 남은 잠금은 PID와 활성 작업을 확인한 뒤 복구한다. 자동으로 잠금을 제거하거나 프로세스를 종료하지 않는다. 저장 후 잠금 정리에 실패하면 `applied: true`와 경고를 반환해 미저장으로 오인하지 않게 한다.
- 요청은 2MB, 세션은 8MB로 제한하고 중복 JSON 키·비유한 수·비정상 경로를 거부한다. 누적 이력이 한도에 도달하면 원본을 유지하고 저장을 거부한다. 자동 이력 삭제/분할은 제공하지 않으며 대규모 장기 운영의 알려진 제한으로 남긴다.
- 반복 Product의 `upgrade`는 같은 writer 잠금 아래 최신 세션을 다시 읽고 framework source/version만 원자 갱신한다. 동시 상태 변경을 과거 사본으로 덮어쓰지 않으며 상태/승인/원본을 재생성하지 않는다. 프레임워크 파일 복사 전체가 트랜잭션인 것은 아니므로 실행 중 worker를 정리한 뒤 업그레이드한다.

실험 세션의 `execute --verify`는 impl의 implement 권한(구현 self-check) 또는 acceptance의 verify 권한이 있을 때만 연결한다. 명시 argv와 새 증적 파일 계약을 유지하고, planning/completed 또는 잘못된 모델에서는 실행 전에 차단한다. 설명용 소스 경로는 선택 사항이다. 검증 명령 자체가 상태를 전환하거나 수용 권한을 만들지 않는다.

결과는 `ready`(미리보기 가능), `applied`(저장됨), `blocked`(현재 준비/권한/증적 부족), `conflict`(revision/잠금 충돌), `invalid`(요청·저장·상태 계약 오류)로 구분한다. CLI exit는 앞의 두 상태가 0, blocked가 1, 나머지가 2다. 미리보기의 `current_gate`/`scope_key`/`session_revision`은 저장된 현재 값이며, 후보는 `proposed_gate`/`proposed_scope_key`/`proposed_session_revision`으로 구분한다. `--apply` 요청이 실패해도 과거 승인·상태를 맞춰서 지우지 않는다.

### 4.4 운영 소비자 연결 (단계 2c)

`process_model`이 있는 세션은 소비자가 지원 모델/형태를 검증한 뒤 읽는다. 표식이 없는 기존 Product/Audit/PoC는 기존 처리 경로이며 미지원·손상 모델을 legacy로 바꿔 읽지 않는다.

- Dashboard는 3구간과 현재 작업 ref/revision·관련 ID를 읽기 전용으로 표시한다. 기존 7개 Gate를 만들거나 진행 완료를 릴리즈로 해석하지 않는다. 화면은 저장 상태의 표시이며 원본 파일/시험/승인 신원을 독립 인증하는 검사기가 아니다.
- `status`/`branch-status`는 실제 Git 작업공간과 설정한 `workflow.integration_branch`를 조회한다. session의 과거 `branch_state`를 사실로 사용하지 않는다. 루트가 Git 저장소가 아니면 unmanaged로 표시하며, 상위 저장소를 상속한 하위 폴더나 Git 관측 실패는 확인 불가로 구별한다.
- `doctor`는 기존 환경 진단기를 재사용한다. 도구 설치/환경 결과와 제품 결함·수용 판단을 합치지 않으며 상태를 바꾸지 않는다.
- `execute --verify`의 구현 self-check는 구현 권한이 있을 때 worker branch에서도 가능하다. acceptance에서는 verify 권한과 설정한 통합 브랜치를 확인한다. single/disabled 정책 또는 명시적으로 해제한 branch guard는 존중한다. 독립 Git 저장소가 없는 합성 파일럿도 명시된 시험을 실행할 수 있으나, 모호한 Git 루트는 인수 실행 전에 차단한다. 새 QA worktree는 만들지 않는다.
- `release-pr --dry-run`은 이번 범위 completed, 현재 계약/증적 재검사, clean Git 작업공간, 실제 current/head/base 브랜치를 확인한다. 기존 Gate 5 승인서를 억지로 요구하지 않는다. 관련 없는 미처리 의무는 누락하지 않고 수량으로 노출하며 릴리즈 포함/제외 판단을 요청한다. 통과한 결과는 후보일 뿐 `release_authorized: false`, `publication_enabled: false`다.
- 미리보기는 PR body 파일도 쓰지 않고 `gh`/push/merge를 실행하지 않는다. 필수 실행 결과·증적과 승인 연결은 확인하되 Git/소스 신선도로 후보를 차단하지 않는다. 구현·환경 변경 영향은 Orchestrator가 판단하며 현재 범위 밖 기능·과거 수용 전체의 배포 적합성을 인증하지 않는다.

단계 2c의 **조회와 명시 시험/미리보기**에 4.5절 브랜치 준비와 4.6절 QA 전달/회수를 연결했다. 새 init은 이 경로를 사용하되 legacy save/session/gate-start/run-exec 차단은 유지한다. 기존 프로젝트와 PMTool/샘플 폴더는 자동 변환하지 않는다. 실제 발행은 별도 승인/대상 확인 후 일반 Git/호스팅 도구로 수행한다.

### 4.5 명시 브랜치 준비 (단계 2d)

`product_branch.start()`를 기존 `branch-start impl`에 연결한다. 표식이 있는 실험 Product에서만 기본이 미리보기이며, `--apply`가 있어야 Git 브랜치를 생성/전환한다. `--dry-run`은 기본과 같고 `--json`은 결과 형식만 바꾼다. 기존 profile/표식 없는 세션의 동작은 유지하고 새 옵션을 거부한다. 일반 init/upgrade 활성화는 하지 않는다.

| 조건 | 수행/차단 |
| --- | --- |
| 허가된 impl, 현재 범위의 계약·시험 계획 준비 완료 | 브랜치 준비 가능. 실행 테스트 완료나 인수 승인까지 요구하지 않음 |
| planning/acceptance/completed, 구현 권한 없음, 손상/미지원 모델 | 생성/전환 전에 거부. 과거 Gate로 변환하거나 승인을 만들지 않음 |
| 독립 Git 루트, 정상 HEAD, 설정된 main에 있고 통합 브랜치 없음 | 현재 HEAD에서 통합 브랜치 생성·전환 |
| 기존 통합 브랜치의 커밋된 파일 내용이 현재 HEAD와 같음 | 같은 작업공간에서 전환. dirty/staged/untracked `session.json` 보존 |
| 기존 통합 브랜치의 파일 내용이 다름 | 오래된 세션/계약을 덮어쓸 수 있으므로 보류. 별도 영향 검토·명시 Git 작업 필요 |
| 세션 외 미커밋 코드/문서/추적되지 않은 파일 | 전환 보류. 자동 commit/stash/discard 없음. ignored 의존성 캐시는 그대로 유지 |
| 이미 통합 브랜치 | no-op. 진행 중 코드 변경을 정리하려고 하거나 세션을 다시 저장하지 않음 |
| single/none/disabled 또는 integration branch 사용 안 함 | 별도 준비 불필요로 거부. 현재 작업공간 운영은 유지 |
| 다른 worker branch, detached/unborn HEAD, 상위 저장소를 상속한 하위 폴더 | 모호한 기준에서 생성/전환하지 않음 |

브랜치의 tree 비교는 **전환 시 파일을 바꾸지 않는다는 경계 확인**에만 사용하며 Git 증적/테스트 신선도 판정으로 저장하지 않는다. stage 전환 직후의 `session.json` 때문에 사전 커밋을 강제하지 않으며 `branch_state`, stats, 승인·이력, 문서·Run도 갱신하지 않는다. Git HEAD의 실제 브랜치는 기존 `status`/`branch-status`가 읽는다.

적용은 기존 `.vulcan/product-process.lock` 안에서 정책을 다시 읽고 세션·Git·설정·현재 문서 조건을 재관측한다. 새 브랜치는 관측한 commit에서 만들고, 기존 대상은 Git의 `update-ref --stdin` verify/prepare 트랜잭션으로 ref를 잠근 동안 전환한다. 실행 후 HEAD·세션·정책·문서를 다시 확인한다. 이 Git 트랜잭션을 지원하지 않거나 잠글 수 없는 환경은 적용을 보류한다.

Git checkout/reference-transaction hook은 일회성 빈 hooks 경로로 비활성화해 제품 코드 실행/발행 부작용을 막으며 저장소 설정은 변경하지 않는다. Git/외부 편집기 전체를 원자적으로 잠그는 기능은 아니다. 비협조적 편집/다른 Git 작업이 동시에 일어나면 최종 확인이 필요하고, 실패를 되돌리려고 reset/checkout을 수행하지 않는다.

결과는 `ready`(미리보기), `applied`(준비 완료), `unchanged`(이미 대상), `blocked`(조건 부족), `conflict`(잠금/동시 변경/불명확한 Git 실행), `invalid`(모델/입력/관측 오류)다. 앞 세 상태는 exit 0, blocked는 1, 나머지는 2다. Git 실행 도중 실패·timeout 또는 사후 상태 불일치는 `applied: null`로 반환한다. 실제 상태가 바뀌지 않았다고 단정하지 않고 `branch-status`/세션 확인을 요청한다. 어떠한 결과도 push/merge/release 권한이 아니다.

일반 Git 전환·worktree 관리 도구를 재구현하는 단계가 아니다. 서로 다른 기존 브랜치의 자동 병합, 상태 이행, native dispatcher, 실제 PR 발행·CI 적용은 이 변경에 포함하지 않는다.

### 4.6 Run 없는 QA 전달과 결과 회수 (단계 2e)

`execute --dry-run [--json]`에서 Run을 생략하면 실험 Product의 현재 acceptance 범위로 `product_qa.handoff()`를 호출한다. 기존 Run planner, 외부 CLI 실행과 섞지 않으며 새 명령/Run/위임 sidecar를 만들지 않는다. 실제 운영 순서는 [Core CLI 4.1절](../core/ORCHESTRATOR_CLI_GUIDE.md#41-개발용-product-반복-프로세스)에 한 번만 정의한다. Codex QA skill과 Gemini bootstrap은 같은 Core 경로를 참조한다.

| 계약 | 동작 |
| --- | --- |
| 현재 acceptance + verify 권한 + 현재 계약/시험/환경 명세 + 합의한 작업공간 | `candidate`/exit 0. 현재 scope/참조/basis를 읽고 `verify_only` 전달 후보를 반환 |
| planning/impl/completed, 권한/계약/환경/작업공간 불일치 | 후보를 만들지 않고 차단. impl self-check의 기존 `execute --verify` 권한은 유지 |
| `native`, `subagent`, `thread`, `agy-branch-agent` | 사용자/총괄이 선택한 실행 방식의 표기. 실제 spawn/send/격리/모델 설정 없음 |
| 담당자와 argv/cwd/출력 경로 | 총괄이 할당 전에 확정할 항목. 현재 문서에서 명령 자동 추출·전체 본문 복제 없음 |
| `return_request` | 기존 상태 요청의 action/target/session revision/scope/basis를 제공하되 results는 빈 배열, decision은 없음. 그대로는 완료할 수 없음 |
| 경로만 있는 결과 행 | 기존 session preview에서 `{id, status, evidence: "relative.json"}`을 받는다. ID별 판정은 입력 그대로 두고 실행 JSON의 argv와 해당 bytes의 참조만 보완한 `prepared_request`를 반환. 기존 전체 행과 혼합 사용 가능 |
| 준비된 결과 요청 | 수용 결정은 만들지 않는다. 경로만 있는 요청은 직접 apply/decision 포함 preview 불가. 반환된 전체 요청을 검토한 뒤 별도 accept 결정으로 기존 apply 사용. preview 이후 증적 bytes 변경·오래된 세션 요청은 재사용 차단 |
| 실패·미실행·환경 차단·누락·중복 결과 또는 실제 명령 실패를 감춘 Pass | 기존 결과/실행 관측 검사에서 거부. 실패 보고는 원본 증적/요약에 보존하고 세션 저장 실패를 결과 저장으로 오인하지 않음 |
| 실제 결과 성공, accept 결정 없음 | 인수 요청 미리보기는 blocked. 검증된 결과 키만 반환하며 별도 실제 수용 판단 후 apply |
| 전달 이후 session revision 변경 | 기존 optimistic concurrency 검사로 conflict. 현재 범위 확인 없이 새 revision으로 치환하지 않음 |

후보 조회는 session bytes를 다시 대조하며 변경 감지 시 conflict를 반환한다. 이 조회는 예약이나 파일시스템 잠금이 아니다. 실제 `execute --verify`는 acceptance에서 계약/시험/환경 참조를 재확인하지만 소스 변경·실제 서비스·시험 수·업무 커버리지를 인증하지 않는다. 테스트 도구의 결과와 현재 소스/환경 영향은 총괄이 확인한다. Git 증적/사전 commit을 추가하지 않는다.

`verify_only`는 위임 계약이며 외부 명령의 쓰기를 기술적으로 막는 sandbox가 아니다. 총괄이 도구 권한과 정확한 출력 범위를 제한한다. 결과 회수도 agent 메시지를 파싱해 자동 Pass/승인으로 바꾸는 기능이 아니며, 새로운 dispatcher나 실제 release 발행은 포함하지 않는다.

## 5. 지속 점검

[실행 회귀 기록](PRODUCT-PROCESS-EXECUTION-VERIFICATION.md)은 실제 Git/명령 실패와 native QA 회수에 대한 후속 검증이다. 범위 수용 이후 발행 거부를 확인한 것이며 실제 발행 계약이나 일반 활성화 완료로 해석하지 않는다.

Product 운영 지침을 바꿀 때 현재 범위에서 다음 사례를 함께 확인한다. 매 사용자 작업에 새 체크리스트를 채우라는 뜻이 아니다.

- Run 없는 국소 수정에 Run/worker/전체 시험을 다시 강제하지 않는가.
- 허가된 결함 수정·재시험은 이어가고, 검증 전용 담당자의 권한은 확장하지 않는가.
- 같은 원본의 문구 정리와 계약·시험·소스 변경을 구별하는가.

`test_product_policy.py`는 이번에 발견한 Core/skill 충돌의 재발을 검사한다. 모든 자연어 충돌을 자동 판정하는 검사는 아니다. 새로운 실제 사례가 나오면 관련 지침을 고치고 해당 사례의 회귀 시험을 추가한다. 설계 참고 문서를 startup 필수 입력으로 늘리거나 Product 예외를 여러 문서에 복제하지 않는다.

## 6. 단계별 검증

아래는 당시 구현의 실제 실행 기록이다. Git/소스 지문 비교 요구는 이후 폐기되었으며 아래 시험 수치나 관측 결과를 새 정책의 검증으로 재작성하지 않는다. 문서·환경 명세의 revision 확인은 유지한다.

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
- 초기 production dependency audit에 남았던 moderate 2건은 병합 전 Mermaid `11.16.0 -> 11.16.1`, DOMPurify `3.4.11 -> 3.4.15` 갱신으로 해소했다. 개발 의존성에서 추가 확인한 5개 패키지의 advisory도 기존 의존성 범위 안에서 갱신했으며, 잠금 파일 기준 전체 `npm audit` 결과는 0건이다. Next/React의 주요 버전과 기존 audit 차단 기준은 변경하지 않았다.
- 갱신 후 `npm ci`, typecheck, production build, Jest 300개, 전체 E2E 45개가 통과했다. 애니메이션 완료 대기를 보강한 최종 Mermaid E2E 2개도 통과했고 390px/1440px 캡처에서 노드·연결·글자를 확인했다. 설치된 의존성 전체 `npm audit --audit-level=low`도 0건이다.
- 남은 관찰: Python의 기존 pathlib 경고는 별도이다. Mermaid 캡처 과정에서 기존 DocDrawer의 `min-w-[480px]` 때문에 390px 화면에서는 문서 패널 왼쪽이 잘리는 현상도 확인했다. 다이어그램 자체는 표시되며 이 의존성 보강에서는 기존 패널 레이아웃을 변경하지 않는다.

### 6.5 단계 2d

- 임시 Git 저장소에서 최종 브랜치 시험 25건을 통과했다. preview 무변경, 미커밋/staged/untracked 세션·ignored 캐시 보존, 기존 브랜치의 다른 내용 거부, 이미 통합 브랜치인 경우 no-op, 단계·권한·설정 오류, Git root/worker branch 경계와 legacy 경로를 확인했다.
- 새 문맥의 native contract-reviewer가 대상 ref 이동과 잠금 이전의 오래된 workflow 정책 사용을 발견했다. Git verify/prepare ref 잠금, 관측한 commit에서 생성, 잠금 안의 정책 해석과 실행 후 재검사로 보정했다. 추가로 최종 관측 중 HEAD·세션·브랜치 변경을 놓치는 경로를 수정했다. 해당 경로 재검토에서 남은 지적은 없으며 총괄이 변경 전/중/후의 실제 Git·설정·세션 변화 회귀를 실행했다.
- Git ref 잠금 종료의 stdin EOF 누락은 실제 시험에서 발견해 보정했다. 실패/timeout의 상태 불확실성을 숨기거나 자동 rollback하지 않으며, 설정된 checkout hook을 실행하지 않는 것도 시험했다.
- 전체 Python 회귀 284건 실행에서 281건 통과, 로컬 symlink 생성 제약 3건 skip을 확인했다. 그 실행 이후 추가한 최종 관측 비교/예외 분류 보강은 브랜치 관련 25건으로 재검증했다. 전체 회귀와 마지막 영향 시험의 실행 시점을 구분한다.
- 초기화 smoke 12단계, 기존 Product/PoC/Audit fixture smoke 84단계, 관련 문서의 로컬 링크 42개가 통과했다. 기존 pathlib deprecation warning은 남아 있다. GUI 변경이 없어 Dashboard 로컬 빌드/브라우저 시험은 이번에 반복하지 않았다.
- 합성 프로세스·Git 연결 시험이지 요청 보드 업무 앱의 QA나 미정 업무 권한의 승인 결과가 아니다. 일반 Product 활성화, 기존 사용자 프로젝트 변경, 실제 릴리즈 발행과 제품별 CI 연결은 수행하지 않았다.

### 6.6 단계 2e

- [QA 전달 모듈](../../vulcan_core/product_qa.py)과 [QA 회귀](../../scripts/regression/tests/test_product_qa.py)를 추가했다. 집중 시험 11건에서 실제 Git 통합 작업공간의 전달 후보 → 실제 실패 → 허가된 수정 → 새 결과 회수 → 별도 수용을 확인했다. 빈/실패/미실행/환경 차단/누락/중복 결과, 실제 명령 실패를 가린 Pass, 오래된 결과 요청은 완료되지 않는다.
- Product 회귀 207건 중 206건 통과/1건 skip, 나머지 Python 회귀 92건 중 90건 통과/2건 skip으로 기존 전체 discovery 대상을 나누어 실행했다. 합계 299건 중 296건 통과이며 3건은 로컬 symlink 생성 제약이다. 초기 집중 시험 이후 추가한 Core 라우팅 정책 회귀도 포함한다.
- 초기화 smoke 12단계와 기존 Product/PoC/Audit fixture smoke 84단계를 통과했다. 관련 문서의 로컬 링크 대상 46개와 diff-check를 확인했다. 기존 pathlib deprecation warning은 남아 있으며 GUI 변경이 없어 Dashboard 로컬 빌드/브라우저 시험은 반복하지 않았다.
- 새 문맥의 native contract-reviewer는 현재 구현/테스트의 실행·권한·legacy 경계를 읽기 전용으로 검토했고 추가 지적은 없었다. 실제 테스트는 총괄이 실행했다. 이번 시험에서 실제 QA 에이전트를 새로 호출한 것은 아니며, 자동 회귀가 native 호출의 후보 입력/반환 형태를 검증한 것이다. Agy 런타임 동작이나 자동 dispatcher 성공으로 확대하지 않는다.
- QA skill의 frontmatter 검증을 통과했다. Codex skill과 Gemini bootstrap은 같은 Core CLI 4.1절을 참조하므로 adapter별 절차를 복제하지 않는다. 일반 init/upgrade 활성화, 사용자 프로젝트 변경, 업무 정책 승인, 실제 릴리즈 발행/제품별 CI 설정은 하지 않았다.

### 6.7 마무리 범위 1: QA 결과 입력 축소 (2026-09-12)

- [결과 요청 회귀](../../scripts/regression/tests/test_product_qa_return.py) 16건을 추가했다. 기존 `session --process-request`의 preview에서 경로만 있는 결과를 준비하며 별도 CLI/Run/승인 정책을 만들지 않는다. 경로·JSON 형식, 판정 보존, 실패 명령을 가린 Pass, 잘못된 ID/중복/누락, scope/session/환경/문서 변경과 preview 이후 증적 변경, 직접 apply/결정 주입 거부, 기존 전체/혼합 결과 호환과 보완된 요청의 기존 크기 제한을 확인한다.
- 크기 제한 보강 전 Product 회귀 222건 중 221건 통과/1건 skip, 나머지 Python 회귀 92건 중 90건 통과/2건 skip을 확인했다. 당시 전체 discovery 대상 합계 314건 중 311건 통과이며 skip 3건은 로컬 symlink 생성 제약이다. 마지막 크기 제한 사례를 포함한 결과 반환/QA/세션 영향 시험 44건도 모두 통과했다. 기존 pathlib deprecation warning은 이번 범위에서 수정하지 않았다.
- 초기화 smoke 12단계, 기존 Product/PoC/Audit fixture smoke 84단계와 관련 문서의 로컬 링크 대상 18개, diff-check를 확인했다. GUI 변경이 없어 Dashboard 로컬 빌드/브라우저 시험은 반복하지 않았으며 최종 CI 결과와 구분한다.
- 새 독립 로컬 예시에서 별도 Python 결과 조립 helper 없이 PowerShell의 JSON 변환과 기존 CLI로 실패→수정→재시험→합성 수용을 수행했다. 최초 3건 중 1건 실패를 보존하고 원문 이력 코드 한 줄 수정 뒤 3건 모두 통과했다. 성공 결과만으로는 수용되지 않으며 최종 scoped check ready/이슈 0건, 발행 비활성화를 확인했다. 사용자 프로젝트/실제 업무 정책의 승인이나 UI·DB 시험은 아니다.
- 이 예시의 운영 CLI는 13회였다(독립 fixture 준비 제외). 수정 후 현재 basis가 비워지는 것을 놓쳐 null 환경 기준의 재시험 인계가 한 번 거부됐고, 보존된 이전 기준을 확인·명시하여 다시 인계했다. 잘못된 요청으로 상태/테스트가 진행되지는 않았다. 이는 결과 행 축약과 별개인 총괄의 상태 인계 실수이며 운영 전체가 자동화됐다고 보고하지 않는다.
- 이번에 제거한 수동 입력은 결과 행마다 복사하던 argv와 증적 revision이다. 범위/환경/세션은 기존 전달 요청을 재사용한다. 상태 전환·결과 검토·수용 결정은 남아 있으며 명령 수나 소요시간/크레딧 감소를 입증하지 않았다. 원본 성공/실패 JSON과 로그는 로컬 예시에 보존하고 공개 저장소로 복사하지 않았다.
- 새 문맥의 native contract-reviewer가 상태/판정/참조/권한 경계를 읽기 전용 검토했고 추가 지적은 없었다. 이후 추가한 크기 제한 보강은 총괄이 해당 부정 시험과 위 44건으로 재검증했다. 테스트 실행은 총괄이 맡았다. Core CLI 4.1절과 handoff 안내만 현행화하며 Codex/Gemini에 별도 운영 방법을 복제하지 않는다.
