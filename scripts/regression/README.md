# Regression Smoke Harness

이 폴더는 Vulcan-Anvil Ex 자체가 다시 깨지지 않는지 확인하는 최소 회귀 검증 도구를 둔다.

## 현재 제공 스크립트

### 1. 최소 init smoke

```powershell
python scripts/regression/run_audit_smoke.py
```

이 스크립트는 임시 프로젝트를 만들고 다음 항목을 확인한다.

- `vulcan.py init`이 최신 템플릿과 기본 산출물을 생성한다.
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

- 완료된 문서 세트에서 `check-trace`가 통과한다.
- 설계 산출물에서 `check-architecture --level baseline`이 통과한다.
- 최소 backend 소스와 Program Design 계약에서 `check-contract`가 실패 없이 동작한다.
- 대표 Run 문서들이 `run-check`를 통과한다.
- 대표 Build Wave Run이 `run-preflight`에서 crash 없이 검사된다.
- QA-001~QA-003 Run은 QA-000이 기록한 QA workspace가 있을 때만 `run-preflight`를 통과한다.
- QA-000 workspace 기록을 제거하면 QA-001 preflight가 차단된다.
- `trace-context`는 YAML/JSON 고정 seed에서 기대 ID와 `target_contracts`를 반환한다.
- `release-pr --dry-run`은 `.vulcan/release/release-pr-body.md`를 만들고 Gate 5 증적, 수동 merge 정책, 독립 PR review 체크리스트를 포함한다.
- `release-pr`는 잘못된 브랜치, 없는 base 브랜치, 미커밋 변경이 있을 때 차단된다.

## 범위

초기 smoke harness는 실제 AI runner, npm, Gradle, Playwright, 전체 샘플 프로젝트 재생을 실행하지 않는다.

fixture 기반 전체 회귀 검증은 `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md`를 기준으로 후속 구현한다.

## GitHub Actions

`.github/workflows/regression-smoke.yml`은 `main` push, pull request, 수동 실행에서 위 두 smoke harness를 실행한다.

CI에는 외부 AI runner, npm install, Playwright, Gradle build를 넣지 않는다. 공개 저장소에서 빠르게 반복 가능한 Python 기반 회귀 검증만 수행한다.

Dashboard Trace Context는 dashboard 빌드와 가벼운 Playwright smoke로 별도 확인한다. 이 검증은 로컬 Dashboard와 샘플 프로젝트가 필요하므로 Python fixture smoke에는 포함하지 않는다.
