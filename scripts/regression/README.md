# Regression Smoke Harness

이 폴더는 Vulcan-Anvil Ex 자체가 다시 깨지지 않는지 확인하는 최소 회귀 검증 도구를 둔다.

## 현재 제공 스크립트

문서 구간 조회와 검증 소스 식별은 합성 임시 문서/Git 저장소로 단위 회귀를 실행한다. 실제 고객/개인 프로젝트 문서를 공개 fixture로 가져오지 않는다.

```powershell
python -m unittest scripts.regression.tests.test_evidence scripts.regression.tests.test_document_context
```

`test_evidence`는 clean/dirty/새 파일/실행 중 변경, 실패 명령, 경로 및 출력 덮어쓰기 경계를 검증한다. `test_document_context`는 구간 상태/공통 조건/정확한 ID/출처/조회 제한을 검증한다. CI의 기존 `test_*.py` discovery에 포함된다. symlink 생성 권한이 없는 환경에서는 해당 실제 symlink 테스트를 skip한다.

역할별 협업 지침의 배포/보존 회귀는 `python -m unittest scripts.regression.tests.test_collaboration_docs`로 실행한다. 합성 PoC/Product/Audit 초기화, 실제 upgrade 경로의 지침 갱신과 기존 Product 문서/Run/코드/Gate/Profile 보존, 설치된 문서 링크를 검사한다. Git 초기화는 mock하며, 실제 역할 작업창의 메시징/자동 실행이나 비용 절감을 검증하는 테스트는 아니다.

Product 결과 중심 운영 회귀는 `python -m unittest scripts.regression.tests.test_product_workflow scripts.regression.tests.test_product_history scripts.regression.tests.test_status`로 실행한다. Run/Wave 선택 여부와 별개로 실제 미완료 작업, 승인/검증 경계가 보존되는지 확인한다. 현재/과거 Gate 및 실행 Wave 식별은 합성 문서/Git 이력으로 검증하며 개인 프로젝트 산출물을 fixture로 복사하지 않는다. 승인 조회는 실제 중첩 Git 프로젝트와 200건을 넘는 합성 이력으로 검사한다. Product/Core/Codex/Gemini 지침의 init/upgrade 배포도 `test_collaboration_docs`에 포함한다.

### 1. 최소 init smoke

Product 반복 프로세스의 단계 1 계약은 `python -m unittest scripts.regression.tests.test_product_process scripts.regression.tests.test_product_policy`로 검사한다. 상태/범위/승인/증적의 기계적 연결과 legacy CLI의 실험 상태 보호를 검증하며 실제 사용자 권한 인증, 문서 준비 판정, Dashboard나 프로젝트 이행은 아직 포함하지 않는다. 지침 검사는 알려진 중복·충돌의 재발 검사이며 모든 자연어를 판정하지 않는다. 새 Product 충돌 사례가 발견되면 해당 사례를 추가한다. 전체 `unittest discover`와 GitHub Actions가 이 테스트도 자동 실행한다.

```powershell
python scripts/regression/run_audit_smoke.py
```

이 스크립트는 임시 프로젝트를 만들고 다음 항목을 확인한다.

- `vulcan.py init`이 최신 템플릿과 기본 산출물을 생성한다.
- `status`와 `status --json`이 새 프로젝트의 Gate/Profile/다음 행동을 요약한다.
- `branch-status`, `check-contract`, `check-architecture --level baseline`이 crash 없이 실행된다.
- Phase 0 승인 전 `gate-start gate1`이 차단된다.
- `implementation-scaffold` Run 초안이 생성되고 `run-check`를 통과한다.
- 미구체화된 worker Run은 `run-preflight`에서 차단된다.
- `export`가 `snapshot.json`을 생성한다.

### 2. fixture smoke

```powershell
python scripts/regression/run_fixture_smoke.py
```

이 스크립트는 `scripts/regression/fixtures/simple-hello-audit/` fixture를 임시 프로젝트에 적용하고 다음 항목을 확인한다.

- `init --profile product`가 Product 문서 세트와 profile rules를 생성한다.
- `scripts/regression/fixtures/simple-todo-product/` completed Product fixture를 적용한 뒤 `status --check`와 `release-pr --dry-run`이 통과한다.
- completed Product fixture에서 `doctor --json`이 구조화된 환경 진단을 반환하고, `session.json`/`vulcan.config.json`/기본 toolchain이 pass로 해석된다.
- Product release body는 `docs/product/` 원장과 backlog/release approval을 evidence로 사용하고, audit 전용 QA Finding/Test Result/Traceability Matrix를 요구하지 않는다.
- 완료된 문서 세트에서 `check-trace`가 통과한다.
- 완료된 fixture 프로젝트에서 `status`가 Gate/Profile/브랜치 상태를 요약한다.
- 설계 산출물에서 `check-architecture --level baseline`이 통과한다.
- 최소 backend 소스와 Program Design 계약에서 `check-contract`가 실패 없이 동작한다.
- 대표 Run 문서들이 `run-check`를 통과한다.
- 대표 Build Wave Run이 `run-preflight`에서 crash 없이 검사된다.
- QA-001~QA-003 Run은 QA-000이 기록한 QA workspace가 있을 때만 `run-preflight`를 통과한다.
- QA-000 workspace 기록을 제거하면 QA-001 preflight가 차단된다.
- `trace-context`는 YAML/JSON 고정 seed에서 기대 ID와 `target_contracts`를 반환한다.
- `release-pr --dry-run`은 `.vulcan/release/release-pr-body.md`를 만들고 Gate 5 증적, 수동 merge 정책, 독립 PR review 체크리스트를 포함한다.
- `release-pr`는 잘못된 브랜치, 없는 base 브랜치, 미커밋 변경이 있을 때 차단된다.
- 공식 QA 로그는 `.gitignore`에 막히지 않고, Playwright HTML report와 `test-results/`는 보조 로컬 산출물로 ignored 처리된다.
- `run-integrate --dry-run`은 scope 밖 `playwright.config.*` 같은 변경을 `Config Hotfix Candidate`로 분류하고 Orchestrator 판단 선택지를 출력한다.
- native/Agy delegation 흔적이 있는데 `delegation_records`가 비어 있는 완료 Run은 `run-check`와 `run-preflight`에서 차단된다.
- Run 상단 metadata와 `3. Run 입력 계약`의 `gate`/`run_type`이 불일치하면 `run-check`와 `run-preflight`에서 차단된다.
- `qa-execution` Run에 소스코드 writable scope나 긍정형 소스 수정 지시가 들어가면 `run-check`와 `run-preflight`에서 차단된다.

Product fixture smoke의 평가 기준은 `docs/reference/PRODUCT-FIXTURE-SMOKE-STRATEGY.md`를 따른다.

## 범위

초기 smoke harness는 실제 AI runner, npm, Gradle, Playwright, 전체 샘플 프로젝트 재생을 실행하지 않는다.

fixture 기반 전체 회귀 검증은 `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md`를 기준으로 후속 구현한다.

## GitHub Actions

`.github/workflows/regression-smoke.yml`은 `main` push, pull request, 수동 실행에서 위 두 smoke harness를 실행한다.

CI에는 외부 AI runner, npm install, Playwright, Gradle build를 넣지 않는다. 공개 저장소에서 빠르게 반복 가능한 Python 기반 회귀 검증만 수행한다.

Dashboard Trace Context는 dashboard 빌드와 가벼운 Playwright smoke로 별도 확인한다. 이 검증은 로컬 Dashboard와 샘플 프로젝트가 필요하므로 Python fixture smoke에는 포함하지 않는다.
