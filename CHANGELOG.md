# Changelog

## Unreleased

### Added

- `vulcan.py l2-review` 명령 추가: Gate 산출물을 별도 세션 또는 detached worktree에서 독립 검수하기 위한 review request/result 파일과 Run 초안을 생성한다.
- `vulcan.config.json` 초기 생성 추가: L2 Review runner, trigger Gate, worktree 사용 여부를 프로젝트별로 명시한다.
- `docs/core/L2_REVIEW_PROCESS.md`와 Codex `l2-review` skill 추가.

## 0.2.2 - 2026-05-18

`0.2.2`는 Codex와 Claude 양쪽 런타임의 Gate 운영 규칙, Run 계약, UI 증적, 검증 명령 기록 기준을 같은 수준으로 맞춘 패치 릴리즈다.

### Added

- Gate 완료 후 산출물 요약, 미해결 항목, 다음 Gate 제안, 사용자 승인 질문을 남기고 대기하는 Gate exit policy.
- Run 입력 계약의 `source_documents.read_first`, `working_documents`, `reference_on_demand` 3-tier 구조.
- Gate 2 설계 순서(`G2-01`~`G2-10`)와 SW Architecture 반복 보강 기준.
- UIREF/prototype 기반 UI Implementation Contract와 상태/시나리오 단위 UI 증적 기준.
- 검증 명령의 cwd, OS별 명령, 성공 기준, exit code, 로그/증적 경로, Not Run/Skipped 기록 기준.

### Changed

- Codex/GPT adapter와 Claude adapter의 Gate Prompt, Run Input/Output Contract, persona/skill 지침을 정렬.
- 개발표준, 테스트케이스, 테스트결과서 템플릿이 명령 실행 기준과 증적 기준을 더 구체적으로 요구하도록 보강.
- `gate-start`와 Run 생성 흐름이 Gate 작업 시작 전 Run 초안을 기준으로 움직이도록 정리.
- Dashboard와 문서 트리가 초기 프로젝트/프로토타입 산출물을 더 명확하게 보여주도록 보강.

### Verification

- `python -m py_compile vulcan.py`
- 임시 프로젝트 `init`으로 신규 템플릿 주입 확인
- Dashboard 테스트 실행
- PR #5 검토 및 merge 확인

## 0.2.1 - 2026-05-16

`0.2.1`은 `0.2.0` 이후 Gate 2 개발표준과 구현/QA 검증 기준을 보강한 패치 릴리즈다.

### Added

- `TECH_STACK_BASELINES.md` 추가: Spring Boot, Spring Security, React, Next.js, Vue.js, FastAPI 기술스택별 코딩/주석/테스트 기본 규칙.
- Spring Boot MVC, base package, feature-first package, JPA Entity/DTO 분리, transaction, repository/query 기준 추가.
- `REFACTORING_PROCESS.md` 추가: 리팩토링을 `DEBT/FIND/CR`로 분류하고 문서 영향, 테스트, 추적성을 기록하는 기준.

### Changed

- 개발표준정의서 템플릿에 기술스택 베이스라인, Spring Boot MVC/JPA 필수 확정 항목, 필수 검증 명령 표를 추가.
- Test Result, Build Wave, Traceability, Agent Run 규칙이 필수 검증 명령 실행 결과를 Run/Test Result에 남기도록 정리.
- README를 랜딩형으로 정리하고 Getting Started, Concepts, Upgrade/Dashboard, Roadmap 문서로 분리.
- Claude 런타임 템플릿이 기술스택 결정 시 `TECH_STACK_BASELINES.md`, 리팩토링 시 `REFACTORING_PROCESS.md`를 상황별로 참조하도록 보강.

### Verification

- `python -m py_compile vulcan.py`
- 임시 프로젝트 `init`으로 신규 Core 문서와 `AGENTS.md` 주입 확인
- `git diff --check`

## 0.2.0 - 2026-05-16

`0.2.0`은 Vulcan-Anvil Ex를 Codex 중심의 초기 골격에서 Codex와 Claude 양쪽 런타임이 실제 Gate 기반 프로젝트를 진행할 수 있는 수준으로 확장한 릴리즈다.

### Added

- Codex/GPT와 Claude adapter 문서 및 템플릿 정합성 강화.
- SW Architecture 산출물 템플릿과 Gate 2 설계 검증 기준 추가.
- 논리/물리 ERD의 DBML 원본 템플릿과 `docs/artifacts/02-design/data/erd/` 구조 추가.
- API 정의서, 보안가이드, 개발표준, 변경요청 상세서, 릴리즈 승인서 흐름 정리.
- Build Wave 기반 구현 계획, Wave 시작/완료, session 동기화 규칙 추가.
- Dashboard `LayoutA2` 추가: compact Gate 요약, 구현/Wave 진행률, 최근 Run/커밋, 통계/커밋 탭.
- 작업용 Markdown 산출물과 제출용 DOCX/XLSX/HWPX 문서의 관계를 정의하는 제출 문서 전략 추가.

### Changed

- 변경관리는 rollback 대신 승인된 CR의 필요한 Gate 진행과 Run 기록으로 처리하도록 정리.
- Dashboard 문서 목록을 1-depth 평면 표시에서 계층형 산출물 트리로 개선.
- 독립 `06-security` 산출물 버킷 대신 Gate 2 설계 하위 `security` 산출물로 정리.
- README를 `0.2.0` 기준 흐름, Dashboard, 다음 초점에 맞게 갱신.

### Verification

- `npm test -- LayoutToggle.test.tsx LayoutSwitch.test.tsx useLayoutTemplate.test.tsx DocList.test.tsx --runInBand`
- `python -m py_compile vulcan.py`

## 0.1.0 - 2026-05-11

- Vulcan-Anvil Ex 초기 Core, template, adapter, dashboard 실험 구조 정리.
- Phase 0, Gate, Run, Traceability, Backlog 기반의 기본 개발 흐름 정의.
