# 회귀 검증 하네스 Fixture 전략

## 1. 목적

이 문서는 Vulcan-Anvil Ex의 P0 회귀 검증 하네스를 구현하기 전에, 하네스가 사용할 fixture를 어떻게 준비할지 정리한다.

목표는 실제 AI worker를 매번 호출하지 않고도 `init`, Gate 전환, Run 생성, Build Wave, QA 단계, check 명령이 다시 깨지지 않는지 검증하는 것이다.

## 2. 핵심 방향

회귀 검증 하네스는 새 문서를 매번 생성하지 않는다.

대신 지금까지 실제 테스트에 사용한 샘플 프로젝트에서 완결된 산출물 문서 세트를 추출해, Ex 저장소 안에 고정 fixture로 둔다.

이 fixture는 사용자 예제 프로젝트가 아니라 자동 검증 입력값이다.

## 3. Ex 안에 가져올 것

샘플 프로젝트 전체를 가져오지 않는다.

가져오는 것은 문서와 최소 상태 파일 중심이다.

권장 위치:

```text
scripts/regression/
  run_audit_smoke.py
  fixtures/
    simple-todo-audit/
      docs/
        artifacts/
          00-discovery/
          01-requirements/
          02-traceability/
          02-design/
          03-test/
          04-review/
        runs/
        reviews/
      session.fixture.json
      vulcan.config.fixture.json
```

## 4. 후보 샘플

초기 fixture 후보는 이미 실제 Gate 진행과 QA 문제를 겪은 프로젝트에서 고른다.

| 후보 | 장점 | 주의 |
| --- | --- | --- |
| `sample-ex-branch-1` | integration branch, QA-000~QA-003, Gate 5, backlog carryover 흐름까지 최신 규칙과 가깝다 | 범위가 hello API라 UI/E2E fixture는 약할 수 있다 |
| `sample-ex-0524-1` | Gate 4 QA worker, 화면/로그 증적, 환경 blocker 사례가 있다 | 특정 Vue/Spring/SQLite 구현 흔적과 로컬 실행 부산물 정리가 필요하다 |
| `sample-ex-0523-1` | local-only simple todo lifecycle과 Gate 4/Gate 5 흐름이 있다 | 최신 integration branch/QA workspace 규칙과 차이가 있을 수 있다 |

처음에는 하나만 고른다.
추천 시작점은 `sample-ex-branch-1` 또는 최신 규칙으로 다시 진행한 simple-todo 샘플이다.

## 5. 포함 대상

fixture에 포함할 수 있는 항목:

- `docs/artifacts/00-discovery/`
- `docs/artifacts/01-requirements/`
- `docs/artifacts/02-traceability/`
- `docs/artifacts/02-design/`
- `docs/artifacts/03-test/`
- `docs/artifacts/04-review/` 중 작은 Markdown 결과 문서
- 대표 `docs/runs/` 문서
- 대표 `docs/reviews/` 문서
- 정규화된 `session.fixture.json`
- 정규화된 `vulcan.config.fixture.json`

필요하면 실패용 fixture를 별도 폴더로 둔다.

```text
fixtures/
  simple-todo-audit-pass/
  bad-run-preflight/
  bad-qa-workspace/
  bad-infra-tbd/
```

## 6. 제외 대상

fixture에 넣지 않는다.

- `backend/`, `frontend/` 전체 구현 소스
- `node_modules/`
- `.next/`
- `.vulcan/worktrees/`
- `.pytest_cache/`, `__pycache__/`
- DB 파일
- Playwright trace zip, video, 대형 screenshot
- 실제 worker execution log 전체
- 로컬 절대경로
- 개인 토큰, secret, remote URL
- 특정 runner session id, thread id

필요한 증적은 작은 Markdown, 작은 log sample, 또는 파일명만 남긴다.

## 7. 정규화 규칙

샘플 프로젝트에서 가져온 문서는 공개 저장소에 들어갈 수 있도록 정규화한다.

정규화 대상:

| 항목 | 처리 |
| --- | --- |
| 프로젝트명 | `regression-simple-todo` 같은 fixture 전용 이름으로 통일 |
| 로컬 절대경로 | `<PROJECT_ROOT>` 또는 상대경로로 치환 |
| Git remote | 제거 또는 `example.invalid`로 치환 |
| commit hash | 필요 없으면 제거. 필요한 경우 `fixture-commit` 같은 값 사용 |
| worker/session id | 제거 |
| 날짜 | 테스트가 날짜에 의존하지 않게 고정 또는 유지 |
| runner/model | 필요하면 `codex-cli`, `claude-cli`, `antigravity-cli` 같은 일반 이름만 유지 |
| status | 하네스 목적에 맞게 `Draft`, `InProgress`, `Verified`, `CompletedWithIssues` 등 정리 |

## 8. 하네스 흐름

1차 하네스는 모델을 호출하지 않는다.

최소 smoke harness는 다음 명령으로 실행한다.

```powershell
python scripts/regression/run_audit_smoke.py
```

현재 최소판은 fixture를 사용하지 않고 임시 프로젝트를 생성해 `init`, 핵심 check 명령, Gate 차단, Run 생성/검사, preflight 차단을 확인한다.
fixture 기반 검증은 이 smoke harness 위에 후속으로 추가한다.

첫 fixture smoke는 다음 명령으로 실행한다.

```powershell
python scripts/regression/run_fixture_smoke.py
```

현재 fixture는 `scripts/regression/fixtures/simple-hello-audit/`이며, `sample-ex-branch-1`에서 정규화한 공개 가능한 문서 세트와 `check-contract`용 최소 backend 소스를 포함한다.

권장 흐름:

```text
1. 임시 디렉터리 생성
2. python vulcan.py init <tmp> regression-simple-todo
3. fixture 문서를 tmp 프로젝트에 복사
4. 필요한 시점의 session.fixture.json / config.fixture.json 적용
5. python vulcan.py check-trace
6. python vulcan.py check-architecture --level baseline
7. python vulcan.py check-contract
8. 대표 Run 문서 run-check
9. 대표 Build Wave Run run-preflight
10. agent-run/run-exec는 --dry-run으로 명령 구성과 guard만 확인
11. QA-001~QA-003은 QA-000 workspace 없을 때 차단되는지 확인
```

## 9. 확인할 회귀 포인트

최소 assertion 후보:

- init이 최신 템플릿과 `DOC-ARCH-G2-002`를 생성한다.
- gate-start가 기본 Orchestrator Plan Run 초안을 만든다.
- 승인대기 상태는 다음 Gate로 넘어가지 않는다.
- 승인 완료만 다음 Gate 전환을 허용한다.
- branch-start impl이 `workflow.integration_branch`를 사용한다.
- 통합 브랜치가 아니면 Build Wave / run-exec가 차단된다.
- BW-000은 `implementation-scaffold` 성격으로 생성된다.
- Build Wave Run에 부적절한 `TBD` 또는 과다 writable scope가 있으면 run-preflight가 차단한다.
- worker 미명시는 Orchestrator 직접 구현 사유가 아니다.
- QA-001~QA-003은 QA-000 workspace 없이 진행되지 않는다.
- check-architecture가 SW Architecture와 Deployment Infrastructure Architecture를 혼동하지 않는다.
- check-contract가 Python/Java/TS 계약 검사에서 crash 없이 종료한다.

## 10. 하지 않을 것

초기 하네스에서는 다음을 하지 않는다.

- 실제 Codex/Claude/Gemini 모델 호출
- 실제 frontend/backend 전체 구현 실행
- npm install, Gradle build, Playwright browser install을 기본 회귀 검증에 포함
- 샘플 프로젝트 전체를 Ex repo에 복사
- 매번 AI가 문서를 새로 작성하게 하기

## 11. 판단

이 방식은 예전 샘플 프로젝트를 Ex에 포함하는 것과 다르다.

예제 프로젝트를 넣는 것이 아니라, 프레임워크 회귀 검증을 위한 작고 정규화된 입력 fixture만 넣는다.
따라서 public repo에 포함해도 목적이 명확하고, 향후 Ex의 안정성을 높이는 테스트 자산으로 사용할 수 있다.
