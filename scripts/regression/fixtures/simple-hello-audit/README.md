# simple-hello-audit Fixture

이 fixture는 `sample-ex-branch-1`에서 추출한 공개 가능한 회귀 검증 입력이다.

## 목적

- 완료된 audit workflow 문서 세트를 기준으로 `check-trace`, `check-architecture`, `check-contract`, 대표 `run-check`, 대표 `run-preflight`가 깨지지 않는지 확인한다.
- AI runner, npm, Gradle, Playwright, 실제 worker 실행 없이 문서/계약 검사 경로만 검증한다.

## 포함

- 정규화된 `session.fixture.json`
- 정규화된 `vulcan.config.fixture.json`
- `docs/artifacts/`
- 대표 `docs/runs/*.md`
- `docs/backlog/`
- `check-contract` 검증에 필요한 최소 `backend/` 소스와 테스트

## 제외

- `.vulcan/worktrees/`
- `docs/runs/_exec/`
- `node_modules/`, `.next/`, `.pytest_cache/`, `__pycache__/`
- DB 파일, Playwright trace/video, 대형 실행 산출물
- 로컬 절대경로, runner session id, thread id, remote URL

