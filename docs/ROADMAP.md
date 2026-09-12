# Roadmap

이 문서는 Vulcan-Anvil Ex의 현재 상태와 다음 초점을 정리하는 기준 문서입니다.

다른 아이디어 문서나 오래된 인수인계 문서가 있더라도, 현재 우선순위는 이 문서를 먼저 기준으로 봅니다.

## 현재 상태

**Experimental - v0.4.x**

`0.4.x`는 Codex, Claude, Antigravity/Gemini runner를 실제 프로젝트 검수/구현/QA 흐름에 더 안전하게 연결하기 위해 audit workflow 브랜치 경계, worker 실행, staged Gate 4 QA, QA workspace 재사용, Program Design 계약 검증, trace-context 그래프, Dashboard 증적/추적 가시성을 보강하는 실험 라인입니다.

포함된 주요 기능은 다음과 같습니다.

- Phase 0 + 5-Gate 진행 흐름
- Codex/GPT adapter
- Claude adapter
- Dashboard A2
- SW Architecture 산출물
- API 정의서 산출물
- DBML 기반 논리/물리 ERD 초안
- 보안가이드 산출물
- Spring Boot, Spring Security, React, Next.js, Vue.js, FastAPI 기술스택 베이스라인 초안
- 리팩토링의 DEBT/FIND/CR 분류와 문서 영향 판단 기준
- 변경관리/릴리즈 산출물
- Build Wave 운영 규칙
- `workflow.integration_branch` 기반 구현 통합 브랜치 운영
- `branch-start impl`, `branch-status` 기반 구현 브랜치 운영과, 필요 시 선택하는 `run-exec`/`agent-run --mode work` 외부 CLI worker 실행
- worker progress watchdog과 hard timeout cap 기반 장시간 실행 관제
- subagent/thread/native branch agent 위임 결과를 `delegation_records`로 남기는 얇은 책임 추적 기준
- Codex runner 역할별 model/effort 정책과 실행 기록
- Codex runner 미지원 model alias compatibility fallback과 회귀 smoke
- `init --profile`과 `profile-status` 기반 Delivery Profile 선택/확인
- `BW-000 implementation-scaffold`를 통한 구현 전 빌드 가능한 skeleton 생성 기준
- Program Design 기반 `check-contract` 1차 검사(Python/Java class/interface/public method 존재 확인)
- Worker dependency cache와 worktree 실행 경계
- Gate 4 `QA-000`~`QA-003` staged QA 실행과 QA workspace 재사용 기준
- Gate 4 테스트 결과서를 실제 실행 상태 원본으로 사용하고, 요구사항추적표에 최종 검증 상태를 반영하는 기준
- Gate 전환 전 `prepare-transition` 통합 진단
- `check-trace` semantic diagnostics 보강
- 설계-코드 불일치 후보를 문서 자동 수정이 아니라 보고서로 남기는 `drift-report`
- Antigravity/Agy `Workspace: branch` native delegation과 `delegation_records.mode: agy-branch-agent` 기준 정렬
- Gate 4 QA 로그/독립검수/증적 문서 대시보드 표시
- 요구사항추적표 기반 `trace-context` CLI와 Dashboard Trace Explorer
- adapter별 Run 입력 문서 분리와 `docs/core/GATE_EXECUTION_CHECKLIST.md` 공통화
- Antigravity/Agy를 메인 Orchestrator로 사용할 때의 `GEMINI.md`, Gemini adapter, native subagent, `Workspace: branch` 활용 기준
- Gate 5 `release-pr` dry-run/body/branch guard
- fixture 기반 회귀 smoke harness
- `doctor` 환경 진단과 `doctor --json` 구조화 출력, Product fixture smoke, QA-000 `QA-000-doctor.json` 환경 증적 연결
- 샘플 프로젝트 로그 기반 성능/병렬화 병목 분석 초안
- PoC profile의 compact Run 완충과, 별도 PoC 템플릿 세트 설계 초안
- Upgrade와 Dashboard 운영 흐름
- 사용자용 profile 선택 가이드와 샘플/benchmark 요약 문서
- Dashboard 문서 코멘트와 `status.dashboard_comments` 기반 Orchestrator 가시성

아직 제품화된 안정 버전은 아니며, 실제 프로젝트 적용 결과에 따라 문서 체계와 CLI 명령은 계속 조정될 수 있습니다.

릴리즈별 변경사항은 `CHANGELOG.md`를 기준으로 확인합니다.

## 최근 완료

최근 안정화에서 완료된 항목이다. 다음 샘플/릴리즈 전에는 회귀 하네스가 이 기준을 지키는지 확인한다.

- Codex runner 미지원 model alias fallback을 `resolve_codex_model_effort()`에 고정하고, 실행 기록과 status/Dashboard에서 actual model과 fallback reason을 볼 수 있게 했다.
- Product completed fixture smoke에서 `python vulcan.py doctor --json` 구조와 기본 pass 조건을 검증한다.
- `doctor`의 환경 진단·요약·출력 로직을 `vulcan_core/doctor.py`로 분리하고, `vulcan.py`에는 기존 CLI 호환용 얇은 어댑터만 남겼다. 전용 unit test와 기존 fixture smoke가 JSON 계약을 함께 고정한다.
- Gate 4 `QA-000` Run 입력 계약에 `python vulcan.py doctor --json` 실행과 `docs/artifacts/04-review/evidence/qa-000/QA-000-doctor.json` 증적 경로를 연결했다.
- simple hello audit fixture에 `QA-000-doctor.json`/`.log` 증적을 추가했고, `scripts/regression/run_fixture_smoke.py`가 QA-000 doctor 증적 계약 누락을 감지한다.
- QA-000 workspace가 `environment_blocked`이면 QA-001 후속 Run preflight와 실행 workspace 재사용 경로가 진행을 차단하도록 fixture smoke에 고정했다.
- 차단 메시지에는 QA-000 doctor JSON/evidence 확인, 제품 결함과 환경 차단 분리, ISSUE/environment_blocked 보류, 필요 시 qa-fix-loop 생성 안내가 포함된다.
- Run 상단 metadata와 `3. Run 입력 계약`의 `gate`/`run_type` 불일치는 `run-check`와 `run-preflight`가 차단하고, fixture smoke가 이 회귀를 고정한다.
- `qa-execution` Run이 소스코드 writable scope나 긍정형 수정 지시를 포함하면 `run-check`와 `run-preflight`가 차단하고, fixture smoke가 이 회귀를 고정한다.
- 2026-06-25 Product 샘플을 Gate 5까지 완료했고, `release-pr --dry-run`이 Product evidence와 Gate 5 승인서를 기준으로 통과함을 확인했다.
- Product Gate 5에서 릴리즈 승인서가 없으면 `status --check`가 차단하도록 필수 산출물과 fixture smoke를 보강했다.
- 2026-06-25 PoC 반복형 샘플에서 `Pass`/`Smoke Pass`가 실제 evidence 파일 없이 구현 완료로 집계되던 문제를 확인했고, PoC evidence guard와 fixture smoke를 보강했다.
- Dashboard를 loopback 전용으로 바인딩하고 원격 Host/교차 출처 쓰기 차단, 선택형 토큰과 프로젝트 루트 allowlist, realpath 기반 symlink 경계 검사를 추가했다.
- Dashboard E2E의 개인 PC 절대경로 의존을 제거하고 저장소 내부 임시 fixture, production server, HTML report 기준으로 23개 시나리오를 재현 가능하게 만들었다.
- GitHub Actions에 Windows/Linux Python smoke와 Dashboard type-check, Jest, production build, high 이상 dependency audit, Playwright E2E를 연결했다.

## 다음 초점

`0.4.x`에서는 기능을 더 많이 넣기보다, 실제 샘플 프로젝트에서 반복 검증 가능한 운영 체계를 단단하게 만드는 데 집중한다.
세부 아이디어는 reference 문서로 넘기고, 이 문서는 "지금 무엇을 먼저 볼지"를 정하는 큐로 사용한다.

### Now: testing-first stabilization

#### 이번 Product 마무리 범위 (2026-09-12, 6개로 한정)

아래 6개를 이번 목표의 완료 기준으로 삼는다. 각 항목은 작은 branch/PR로 검증하며 새로운 아이디어는 후속으로 둔다. 기존 프로젝트/PMTool의 명시 전환, Audit 재설계, 자동 dispatcher 등은 이 완료 조건에 추가하지 않는다.

| 순서 | 작업 | 현재 상태 / 완료 기준 |
| --- | --- | --- |
| 1 | QA 결과 회수 간소화 | [PR #44](https://github.com/zeni-on/vulcan-anvil-ex/pull/44) 병합, Linux/Windows Python 및 Dashboard CI 통과. [검증과 한계](reference/PRODUCT-PROCESS-CONTRACTS.md#67-마무리-범위-1-qa-결과-입력-축소-2026-09-12): 기존 요청에서 ID·판정·증적 경로를 받고 실행 argv/참조를 보완. 별도 수용 결정과 변경/실패 차단 유지 |
| 2 | 업무 분석을 작성 흐름에 연결 | [PR #45](https://github.com/zeni-on/vulcan-anvil-ex/pull/45) 병합, CI 3종 통과. [Core 작성 경로](core/PRODUCT_DOCUMENT_WRITING.md#0-업무에서-요구로-연결한다), 선택 업무 양식과 [후보 연결 예시](../scripts/regression/fixtures/product-discovery-writing/README.md). [검증/한계](reference/PRODUCT-DISCOVERY-AND-VALIDATION-GUIDE.md#7-작성-연결-검증-2026-09-12): 원본→REQ/AC→시험, 미정 결정·일반 활성화 경계와 설치/조회 호환 확인 |
| 3 | 실제 요청 보드 한 흐름 검증 | [PR #46](https://github.com/zeni-on/vulcan-anvil-ex/pull/46) 병합, CI 3종 통과. [실행 샘플/결과](../examples/product-request-board/docs/verification.md): 후속 업무 합의, 실제 UI/API/SQLite에서 반복 반려·재제출·권한·이력 보존. API 12건, desktop/mobile 10건 통과 및 고의 이력 파괴 감지. 운영 인증/인수 승인은 아님 |
| 4 | 제품 CI 연결·실행 | [PR #47](https://github.com/zeni-on/vulcan-anvil-ex/pull/47) 병합, CI 4종 통과. [요청 보드 CI 결과](../examples/product-request-board/docs/ci-verification.md): 실제 GitHub 실행 1분 10초 성공, API 12건/UI 10건 및 7개 차단 probe 확인·artifact 회수. 자동 merge·배포·보호 설정은 변경하지 않음 |
| 5 | 반복 운영·릴리즈 경계 마무리 | 로컬 검증 완료, 별도 PR/원격 CI 확인 중. [같은 제품의 확장·결과](../examples/product-request-board/docs/iteration-verification.md): 상태 조회 확장, 과거 계약/수용/SQLite 이력 보존, 이전 승인·증적 재사용 거부, 릴리즈 후보와 실제 발행 분리. API 15건/UI 12건, 실제 CLI 반복 시험. 자동 발행/기존 프로젝트 이행은 추가하지 않음 |
| 6 | 신규 Product 일반 사용 마무리 | 미활성화. init/지원 adapter/Core/Dashboard의 같은 흐름과 호환 회귀를 확인한 뒤 적용 판단 |

6번 이후에는 실제 사용으로 전환한다. 아래 완료 이력과 장기 후보를 모두 구현해야 이 목표가 완료되는 것은 아니다.

#### Product 3구간 반복 프로세스 (2026-09-12, 운영 관측/일반 활성화 전)

- 최우선 방향은 **기획·설계 ↔ 구현 ↔ 인수 검증**이다. [운영 설계](reference/PRODUCT-ITERATIVE-PROCESS-DESIGN.md)에 사용자 결정/자율 진행, 범위별 문서 책임, 반복·수용·배포 경계와 현재 코드의 결합 지점을 정리했다. 화면만 묶거나 내부에서 기존 7단계를 자동 순회하는 접근은 제외한다.
- [운영 시나리오와 후속 회귀 기준](reference/PRODUCT-ITERATIVE-PROCESS-SCENARIOS.md)은 신규/확장, 인수 중 결함·업무 변경·환경 차단, 병렬 기획, 완료 후 재진입 등을 다룬다. 아직 runtime 실행 시험이 아니라 설계 검토용 기대 행동이다.
- 새 문맥의 native contract reviewer가 범위/상태, 승인·증적 재사용, legacy 호환과 숨은 Gate 반복 여부를 읽기 전용 검토했고 지적은 없었다. 총괄은 로컬 문서 링크와 변경 범위를 확인했다. 이는 새 프로세스의 실행 검증이나 사용자 최종 승인이 아니다.
- Product 지침의 Run 필수/직접 수정 제한/QA 재승인 충돌을 적용 profile별로 정리했다. `test_product_policy`로 발견한 재발 패턴을 고정하며, 후속 Product 변경에서도 실제 충돌 사례를 계속 보강한다. 모든 자연어 지침의 정합성이 자동 보장된다는 뜻은 아니다.
- Codex 세부 skill의 잔존 Run/worker 강제, 무조건 재시험, 제거된 Git 증적 안내를 정리했다. Gate Prompts의 중복 규칙은 Core 참조로 줄이고, 설계/구현/QA/릴리즈 skill은 `process_model`이 있으면 기존 Gate 절차보다 개발용 모델 경로를 먼저 따른다. 지침 회귀와 init/upgrade 설치·원본 보존을 검사하며, 일반 활성화·모델 기본값·Audit/PoC 실행 정책은 변경하지 않는다.
- [단계 1 상태·작업 범위·승인 계약](reference/PRODUCT-PROCESS-CONTRACTS.md)을 내부 API와 합성 계약 테스트로 구현했다. 범위 revision/승인/실제 증적의 분리, 읽기 전용 진단, 미지원·실험 모델의 legacy 쓰기 차단을 포함한다. 일반 init/upgrade 활성화나 실제 프로젝트 이행은 하지 않는다.
- 단계 2a: [범위별 준비·인수 검사](reference/PRODUCT-PROCESS-CONTRACTS.md#41-범위별-검사-연결-단계-2a)를 실험 세션의 `status --check`에 연결했다. 현재 계약·시험 원본, 공통 조건과 실제 명령 증적을 확인한다. 별도 Git/소스 신선도 검사는 폐기하고 환경 명세 참조와 Orchestrator의 변경 영향·재시험 판단을 유지한다. 기획 중 Planned는 허용하며 검사 통과와 승인·릴리즈를 구분한다. SHA나 새 Run을 수동 작성하는 절차는 추가하지 않는다.
- 단계 2b: [실험 상태 저장 CLI](reference/PRODUCT-PROCESS-CONTRACTS.md#43-상태-저장-cli-단계-2b)를 기존 `session`에 연결했다. 기본 미리보기, 명시 apply, scoped 검사/승인·실행 근거, 상태 revision 충돌·배타 잠금·원자 저장을 포함한다. 별도 임시 프로젝트에서 실제 CLI 상태 반복과 `execute --verify` 연결을 시험하며 기존 프로젝트를 이행하지 않는다.
- 단계 2c: [PR #36](https://github.com/zeni-on/vulcan-anvil-ex/pull/36)을 머지했다. 지원 Dashboard의 3구간/현재 범위 읽기, `status`/`branch-status`의 실제 브랜치 조회, `doctor` 환경 진단, 합의한 통합 작업공간의 인수 시험과 무부작용 `release-pr --dry-run`을 연결했다. 범위 수용과 제품 전체 릴리즈 권한은 분리한다. 상세 제한과 [검증 결과](reference/PRODUCT-PROCESS-CONTRACTS.md#64-단계-2c)는 [운영 소비자 계약](reference/PRODUCT-PROCESS-CONTRACTS.md#44-운영-소비자-연결-단계-2c)에 둔다.
- 실행 회귀 보강: [임시 Git/실제 native QA 검증](reference/PRODUCT-PROCESS-EXECUTION-VERIFICATION.md)을 진행했다. 실제 실패→허가된 수정→재시험, 과거 증적/승인 재사용 차단, 완료 후 재진입, 환경 차단, 발행 거부와 fixture Git 격리를 자동 회귀로 고정한다. Codex/Gemini 시작점은 실험 표식이 있을 때 같은 Core 안내로 먼저 라우팅한다. 실제 Codex QA 위임·회수는 확인했으며 Agy runtime, 자동 dispatcher/branch-start/성공적인 발행은 검증 완료로 보지 않는다.
- Git 증적 제거: 검증·문서 조회의 Git/소스 지문 수집과 그에 따른 인수 차단을 제거했다. 테스트 후 staging/커밋은 결과를 무효화하지 않으며, 실제 실패·필수 시험 누락·범위/승인 연결 검사는 유지한다. 구현 변경의 재시험 판단은 총괄이 맡는다. 기존 로그는 보존하고 새 기록은 명령·시간·종료 코드만 남긴다.
- 단계 2d: [명시 브랜치 준비](reference/PRODUCT-PROCESS-CONTRACTS.md#45-명시-브랜치-준비-단계-2d)를 실험 모델의 `branch-start impl`에 연결했다. 기본 미리보기/명시 apply, 현재 범위·권한·계약 확인, 세션을 그대로 가져가는 동일 내용 브랜치 생성/전환과 충돌 보존을 실제 Git 시험 25건으로 검증했다. 세션 저장/사전 커밋/자동 push를 묶지 않는다. 기존 통합 브랜치 내용이 다르면 별도 Git 판단 대상으로 남긴다. 일반 활성화·발행·제품 CI 완료는 아니다.
- 단계 2e: [Run 없는 QA 전달/회수](reference/PRODUCT-PROCESS-CONTRACTS.md#46-run-없는-qa-전달과-결과-회수-단계-2e)를 `execute --dry-run`과 기존 상태 요청에 연결했다. 현재 범위의 계약/시험/환경 참조와 빈 결과 요청을 제공하며, 실제 결과 회수·수용 판단은 총괄이 맡는다. acceptance 실행 직전 기준 재검사, 실패/누락/중복/오래된 요청의 완료 거부를 회귀로 확인한다. 자동 dispatcher/QA 승인 기능은 아니다.
- [PR #42](https://github.com/zeni-on/vulcan-anvil-ex/pull/42)를 CI 3종 통과 후 병합하고 [실제 운영 관측](reference/PRODUCT-OPERATION-TRIAL-2026-09-12.md)을 진행했다. 같은 요청 재제출의 독립 함수 fixture에서 native QA 실패→한 줄 수정→재시험 3건 Pass→합성 수용을 확인했다. 새 Run/QA worktree/문서 수정에 따른 전체 재시험은 없었다. 운영 CLI 10회의 실행 합계는 9.823초였지만 결과 조립에 별도 로컬 helper를 썼으므로 기본 CLI만의 사용성·비용 절감 입증이나 실제 제품 인수로 확대하지 않는다.
- 현재 마무리 순서와 완료 여부는 위 6개 표를 따른다. #44~#47에서 QA 결과 입력·업무 작성·실제 앱·제품 CI를 병합했다. 5번은 같은 제품의 확장/이력/릴리즈 경계 검증이며, 다음 6번이 신규 Product 일반 활성화다. 새 CLI/Gate/필수 문서를 늘리는 방식은 우선하지 않는다. main 병합은 기본 활성화를 뜻하지 않으며 기존 프로젝트 상태를 먼저 바꾸지 않는다.
- Audit/PoC는 이번 설계 대상이 아니며 기존 동작을 유지한다. 단계 축소와 문서 축소는 별개다. 아래 업무 분석 파일럿과 기능별 원본 구조를 활용하고, 전체 AC/REQ 조회는 별도 후속으로 유지한다.

#### Product 업무·시나리오 합의 파일럿 (2026-09-10, 진행 중)

- [진행 가이드와 표준 연결](reference/PRODUCT-DISCOVERY-AND-VALIDATION-GUIDE.md), [요청 보드 대화 연습](reference/PRODUCT-DISCOVERY-PILOT-REQUEST-BOARD.md)을 추가했다. IIBA/IREB의 업무·요구 분석 관점과 Example Mapping을 참고하여 문제/경계, 액터·흐름, 규칙·예시·질문, REQ/AC로 연결하는 절차를 제안한다. 표준 준수 인증이나 새로운 필수 Gate/Run은 아니다.
- 합성 예시에서 반려 후 재신청이 정의되지 않은 점을 확인했고, 사용자는 기존 요청에서 재제출하며 반려 당시 내용·사유도 보존하는 방향을 선택했다. 여기서 인수조건 후보 두 개를 도출했으며, 남은 권한·상태·이력 정책 질문과 구분한다. 실제 프로젝트 원본·승인·구현·QA는 변경하지 않았다.
- 2026-09-12 작성 연결: Core 작성 0절과 선택 업무 흐름 양식을 기존 `01-requirements` 경로에 연결했다. init/upgrade는 지침·양식만 갱신하며 필수 6종, 작성된 원본과 기존 상태를 보존한다. Codex/Gemini는 같은 Core 경로를 사용한다. 기획 활동별 Gate/승인을 추가하지 않는다.
- 다음 업무 검증은 남은 사용자 합의 후 같은 흐름의 실제 UI/API/DB에서 진행한다. 원본의 AC/REQ 전체 조회는 별도 후속이며 새 필수 원장을 만들지 않는다. 작성 예시/파서 회귀의 성공을 업무 합의·QA·일반 활성화로 확대하지 않는다.

#### Product 제품별 CI와 업무 검증 연결 (2026-09-12, 설계 / 선행 작업 후 샘플 적용)

- [설계·판정 기준·적용 순서](reference/PRODUCT-CI-AND-QUALITY-LOOP.md)를 추가했다. Ex 자체의 CI와 생성된 제품의 CI를 구분하며, 합의한 업무 예시를 실제 assertion과 반복 검증으로 연결한다. 정적 분석·빌드 성공만으로 업무 문제 해결이나 사용자 수용을 대신하지 않는다.
- 순서는 **위 Product 운영 연결과 업무 합의 → 같은 합성 제품의 로컬 시험/실제 GitHub Actions 실행 → 실패·테스트 0건/필수 skip·환경 차단 검증 → Product 기준 채택**이다. 일반 활성화보다 먼저 샘플에서 관측하며, 전체 AC 조회나 운영 지표 자동화까지 선행 조건으로 늘리지 않는다.
- 자동 검증 능력을 필수화할 방향이며 공급자는 GitHub Actions에 한정하지 않는다. 기존 Jenkins 등은 재사용한다. 새 Gate/Run/Git 증적 필드나 CLI를 만들지 않고 개발 가이드·프로젝트 스크립트·기존 시험 결과와 연결한다.
- 이번에는 설계만 추가한다. init/upgrade의 CI 자동 생성, 기존 프로젝트 검사 강도/승인 문서 변경, 저장소 보호 규칙 설정은 하지 않았다. 샘플 실행과 관리자 동의 없이 CI 통과·merge 차단·일반 배포 완료로 보고하지 않는다.

#### Product 문서 구조와 작성 책임 (2026-09-11, 작성 경로/확장 회귀 정리)

- [문서 지도와 점진 이행](reference/PRODUCT-DOCUMENT-ARCHITECTURE-STRATEGY.md), [문서별 작성 계약](reference/PRODUCT-DOCUMENT-WRITING-CONTRACTS.md), [파일럿 결과/한계](reference/PRODUCT-DOCUMENT-ARCHITECTURE-PILOT.md)를 정리했다. 6개 파일 제한 대신 필요한 문서의 원본 위치/책임을 정하고 기능별 분할, 공통 기준 참조, 현재 명세/결정/실행 기록 분리를 제안한다.
- 원본 밖 기능 파일럿에서 요구/AC 7쌍, 공통 조건 본문 16줄, Pending 9개 행을 보존했고 23개 탐색 링크를 대조했다. 미수집 참조 3개와 기존 조회의 공통 조건 누락을 드러냈다. 속도/토큰 절감 또는 제품 QA 통과를 입증한 것은 아니다.
- 설계 #27에 이어 [조회 #28](https://github.com/zeni-on/vulcan-anvil-ex/pull/28), [내용 검사·추적·통계 #29](https://github.com/zeni-on/vulcan-anvil-ex/pull/29)를 Windows/Linux Python 및 Dashboard CI 통과 후 머지했다. 명시적 상세 링크, legacy/split/mixed 호환, 중복/충돌·누락 진단과 계획/현재 결과 분리를 검증했다. [조회 범위](core/CURRENT_CONTEXT_AND_EVIDENCE.md#31-분리-문서-조회-호환-mvp), [검사 범위](core/CURRENT_CONTEXT_AND_EVIDENCE.md#32-product-내용-검사추적통계-호환)를 따른다.
- [작성 경로 #30](https://github.com/zeni-on/vulcan-anvil-ex/pull/30)을 머지했다. [Product 문서 작성 경로](core/PRODUCT_DOCUMENT_WRITING.md)를 Core/Codex/Gemini에 연결하고 선택형 요구 상세·시험 계획·실행 결과 템플릿을 추가했다. 기존 설계 템플릿의 중복 정의/실행 결과 혼합을 정리하며, init의 필수 6종과 upgrade의 기존 원본 보존을 회귀 검증했다.
- [PR #31](https://github.com/zeni-on/vulcan-anvil-ex/pull/31)의 **Product Gate 3 선작성 Not Run 오탐 수정과 문서 기능 확장 회귀**를 PR #36 이후 main 기준으로 통합했다. 3개 시나리오→댓글 추가→기존 제목 제한 변경을 합성 예시와 자동 테스트로 확인한다. 원장 6종은 유지하고 현재 원본/과거 결과/당시 시험 정의를 분리한다. 실제 실패·환경 차단·상충 결과와 Gate 4 이후의 필수 실행 판정은 유지한다. [확장 검증 결과와 한계](reference/PRODUCT-DOCUMENT-GROWTH-REGRESSION.md)를 따른다.
- 다음 순서는 위 6개 마무리 표로 관리한다. 기존 상태·승인·문서 참조 검사와 Dashboard 읽기/릴리즈 미리보기를 전체 운영 완료로 확대하지 않는다. 실제 기능 원본 이동은 별도 승인 대상으로 두고 기존 승인 문서를 자동 이동하거나 6종 진입점을 삭제하지 않는다.
- 실행 정책/필수 6종/Dashboard와 사용자 프로젝트 원본은 유지한다. Audit/PoC 검사 기준도 바꾸지 않는다.

#### Product 결과 중심 실행 정리 (2026-09-09, main 반영 완료)

- [Product 기준 7절](core/PRODUCT_PROFILE_BASELINE.md#7-product-실행과-검증-범위)을 일반 작업/이슈 요약 기반으로 정리했다. Run/Wave와 새 worker는 선택하고, 승인 범위·보안·실제 검증·현재 계약 현행화는 유지한다. 외부 CLI는 기존 Run/preflight 계약을 유지한다.
- `status`의 새 Wave 생성 강제 안내, 과거 완료 Run의 입력 사전검사 반복, 계획 문장 속 BW 번호의 실행 Wave 오인을 보정했다. Git 승인 조회는 변경 후보를 찾아 일괄 읽으며, 실제 미완료 작업과 근거 없는 미래 Gate 산출물은 계속 진단한다.
- Codex/Core/Gemini/사용자 안내를 같은 기준에 맞췄다. unit 130건 중 127건 통과/Windows symlink 권한 관련 3건 skip, init smoke 12단계와 fixture smoke 84단계가 통과했다. 새 문맥 리뷰에서 과거/현재 결과 혼합, 승인 조회 비용, 결과 컬럼 충돌과 손상된 승인 기록을 보정했고 재검토에서 남은 지적은 없었다.
- 기존 프로젝트의 읽기 전용 관찰에서 계획 참조와 실행 Wave를 구분하고 승인된 과거 Run을 재검사에서 제외함을 확인했다. 실제 미완료 작업/승인 근거가 불명확한 기록은 유지한다. 기존 산출물 자동 삭제·재작성, 사용자 프로젝트 upgrade, Dashboard 재구성은 이번 변경에 포함하지 않는다.
- [PR #26](https://github.com/zeni-on/vulcan-anvil-ex/pull/26)을 Windows/Linux Python 및 Dashboard CI 통과 후 main으로 머지했다. 후속은 작은 실제 변경 한 건의 문서 생성 수, 재검사 횟수, 입력 범위와 누락/보정량 비교다. 속도나 크레딧 절감은 실측 전 보장하지 않는다.

#### 역할별 작업 협업 정책 (2026-09-09)

- [PR #25](https://github.com/zeni-on/vulcan-anvil-ex/pull/25)를 CI 통과 후 main으로 머지했다.
- [공통 협업 규칙](core/COLLABORATION_PROTOCOL.md)과 [Codex 작업 연결](adapters/codex-gpt/PERSONA_DELEGATION.md)을 추가/정리했다. 역할별 문서 소유권, 개별 업무 전달/회수, 실제 작업공간/소스 확인, 총괄의 단일 상태 관리와 새 문맥 review를 기존 Run/Profile/Gate 체계에 연결한다.
- Codex의 오래된 전체 Core 일괄 입력 예시와 병렬 구현 안내를 현재 Product worker 입력 및 단일 active Wave 규칙에 맞췄다. 역할 수 고정, 새 필수 registry/Run 필드, 자동 dispatcher/App Server 또는 다중 Wave는 추가하지 않는다.
- 검증 완료: 합성 프로젝트 init/upgrade 지침 설치·기존 산출물 보존·문서 링크 3건, 전체 unit 95건 중 92건 통과/Windows symlink 권한에 따른 3건 skip, init smoke 12단계, fixture smoke 84단계. 새 문맥 리뷰에서 차단 지적은 없었다.
- 다음 운영 확인은 사용자가 선택한 기존 역할 작업에서 읽기 전용 업무 한 건의 전달/회수다. 실제 메시징/비용 절감 검증과 문서 설치 검증은 구분한다. 실제 사용자 프로젝트와 역할 작업창 설정은 변경하지 않았다.

#### 현재 계약 조회와 검증 명령 기록 (2026-09-08)

기준: [Current Context And Evidence](core/CURRENT_CONTEXT_AND_EVIDENCE.md). [PR #24](https://github.com/zeni-on/vulcan-anvil-ex/pull/24)를 2026-09-09에 main으로 머지했다.

2026-09-11 정책 변경: 별도 Git 증적·소스 지문 수집과 신선도 차단 요구는 폐기한다. 현재 `execute --verify`는 명시 argv/cwd/시간/exit code를 기록하며 `--source`는 선택적 설명용 경로다. 아래 완료 항목과 시험 수치는 당시 사실이며 새 정책의 검증으로 재작성하지 않는다.

1. 완료: PR #23 머지. Dashboard high production advisory 수정과 Windows/Linux Python, Dashboard/E2E CI를 확인했다. 당시 남았던 moderate production advisory 2건도 2026-09-11 PR #36에서 해소했으며, 개발 의존성을 포함한 전체 npm audit 결과는 0건이었다.
2. 당시 완료: 현재 계약/후보/이력/미분류와 커밋별 의미를 정의했다. 커밋 증적 요구는 이후 폐기했다.
3. 당시 완료: 선택형 `execute --verify`가 소스 범위의 Git 기준, 파일 해시와 명령 exit code를 기록했다. 전용/기존 worker 테스트 47건 중 45건 통과, Windows symlink 권한에 따른 2건 skip을 확인했다. 소스 관측 방식은 현재 운영 지침이 아니다.
4. 완료: 선택형 `trace-context --sections`가 정확한 ID, 출처/줄 범위/해시, 적용 상태와 공통 제약을 반환한다. Run에는 짧은 `section_lookup`만 추가한다. 기존 그래프/원장을 자동 수정하지 않는다.
5. 완료: 로컬 unit 92건 중 89건 통과/Windows symlink 권한에 따른 3건 skip, init smoke 12단계, fixture smoke 84단계를 확인했다. 새 문맥 review의 Git 식별/Markdown 표식 지적 3건을 보정했고 reviewer 재검사 9건도 통과했다. [파일럿 관찰과 한계](core/CURRENT_CONTEXT_AND_EVIDENCE.md#61-로컬-조회-파일럿-2026-09-08)를 남겼으며 원본 프로젝트 변경이나 사적 문서 공개는 하지 않았다. [PR #24](https://github.com/zeni-on/vulcan-anvil-ex/pull/24)의 Windows/Linux Python 및 Dashboard 회귀 CI 통과 후 머지했다.

#### Product 입력/검증 비용 정리 (2026-09-08)

- PR #23으로 main에 반영했다. Product 원장/승인/보안 수준을 유지하며 worker 입력, 수정 경로와 실제 검증 명령을 좁히고, 증적 확인과 재실행 조건을 구분한다. 실행 기준은 [Product Profile Baseline 7절](core/PRODUCT_PROFILE_BASELINE.md#7-product-실행과-검증-범위), worker 입력은 [Product Worker Guide](core/PRODUCT_WORKER_GUIDE.md)다.
- Product Run 생성/사전검사 단위 회귀, Audit 초기화 smoke, Product/PoC/Audit fixture smoke를 확인했다. 다음은 실제 작업에서 같은 모델/effort로 입력량, 재검사, 위임 왕복, 결함/보정량을 비교하는 것이다. 실행 시간이나 크레딧 감소는 아직 입증하지 않았다.
- 계약 구간 추출은 PR #24로 반영했다. 다음은 역할별 위임에서 이 조회 결과를 사용해 입력/회수 범위를 확인하는 것이다. 다중 active Wave, App Server 연동, 외부 CLI 모델 기본값 변경은 이번 범위에 포함하지 않는다.
- 후속 정책: Codex custom agent의 모델/effort 고정을 제거하고 사용자 모델 설정 상속과 작업별 effort 선택을 분리했다. [native review 기준](core/AGENT_RUN_PROTOCOL.md#54-새-문맥의-native-review)은 위험도에 따른 호출 판단과 부모 대화 비상속을 명시한다. 자동 리뷰 호출/새 mandatory checker는 추가하지 않았고, 외부 CLI 기본값/사용자 전역 설정도 변경하지 않는다.

지금은 새 기능을 늘리기보다, 이미 얻은 운영 규칙이 실제 샘플과 fixture에서 반복 검증되는지 확인하는 구간이다.
새 CLI나 자동화 후보는 먼저 테스트/샘플에서 효과를 확인하고, 효과가 분명할 때만 main으로 승격한다.

1. **Fixture smoke를 기준선으로 유지**
   - 샘플 프로젝트를 매번 처음부터 재실행하는 대신, 반복 발견된 회귀를 `scripts/regression/run_fixture_smoke.py`에 고정한다.
   - 공식 QA 로그 누락, Playwright 보조 report 오인, Config Hotfix scope 후보, native/Agy `delegation_records` 누락, Run 입력 계약 metadata 불일치, QA worker 수정 지시 오염, `status --json --check`, `execute --dry-run --json`은 fixture smoke에 고정했다.
   - 다음 fixture 추가는 실제 샘플에서 두 번 이상 반복되거나, Gate 전환/QA/릴리즈를 실제로 막은 회귀만 대상으로 한다.
   - 회귀 하네스 기준은 `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md`를 따른다.

2. **Gate 4 QA 흐름 재검증**
   - Audit/Product의 공식 UI Pass는 `@playwright/test`와 `npx playwright test` 실행 결과를 기준으로 한다.
   - 커스텀 Playwright script는 PoC smoke/demo 또는 보조 증적으로만 쓴다.
   - QA-000은 `doctor --json` 환경 증적을 남기고, 제품 결함과 `environment_blocked`를 분리한다.
   - QA worker가 테스트 실행자와 수정자 역할을 섞지 않는지, 수정이 승인된 `qa-fix-loop` 또는 Config Hotfix 후보로 분리되는지 샘플에서 확인한다.
   - 2026-06-25 Product sample Gate 4에서 `doctor`, compileall, pytest, npm test/build, `npx playwright test`와 screenshot 증적까지 확인했다. 동시에 Product 기본 문구 `Not run yet | Planned`가 Gate 4 전환을 막지 못하던 readiness 버그를 fixture에 고정했다.
   - 다음 보강은 새 기능 구현이 아니라 "차단 후 사용자 협의 안내와 qa-fix-loop/ISSUE 후보 분기가 자연스럽게 보이는지"를 확인하는 것이다.

3. **Profile별 실제 샘플 재실행**
   - Product profile은 fixture smoke만으로 끝내지 않고, 실제 Product 샘플 1회를 재실행해 운영 마찰을 확인한다.
   - 2026-06-25 Product sample rerun에서 Phase 0~Gate 5, Impl handoff, native worker 구현, `BW-001` Verified, Gate 4 QA evidence, Gate 5 release approval, `release-pr --dry-run`까지 확인했다. full-stack Product Build Wave가 `build-frontend`로 잘못 추론되던 문제를 `build`로 보정했고, Product trace 원장 기반 구현 통계가 `3/3`으로 잡히도록 fixture에 고정했다. Gate 5 승인서 누락을 `status --check`가 놓치던 문제도 fixture에 고정했다. 결과는 `docs/reference/PRODUCT-PROFILE-SAMPLE-RERUN-2026-06-25.md`에 남겼다.
   - PoC profile은 빠른 시간보다 실험 기록 복원성을 기준으로 본다. 2026-06-25 반복형 PoC 샘플에서 `Fix Log / Experiment Iterations`가 REQ/테스트/증적과 연결되면 복원이 가능함을 확인했고, evidence 없는 `Smoke Pass`가 완료로 집계되지 않도록 fixture에 고정했다. 결과는 `docs/reference/POC-ITERATION-SAMPLE-RERUN-2026-06-25.md`에 남겼다.
   - Audit profile은 Gate 4/5 전환과 release-pr dry-run까지 큰 흐름이 깨지지 않는지 릴리즈 전 smoke 성격으로만 재실행한다.
   - Product 기준은 `docs/reference/PRODUCT-FIXTURE-SMOKE-STRATEGY.md`, PoC 기준은 `docs/reference/POC-PROFILE-TEMPLATE-SET-STRATEGY.md`를 따른다.

4. **Run/위임 품질 게이트는 샘플 기반으로만 보강**
   - `run-check`, `run-preflight`, `trace-context`, `--trace-seed`, native 위임용 `delegation_records`의 MVP는 이미 들어갔다.
   - 추가 규칙은 이론적으로 만들지 않고, 실제 Run/QA/worker 기록에서 반복된 누락만 반영한다.
   - 외부 CLI runner는 `_exec` 로그와 Run Execution Record를 유지하되, subagent/thread/Agy Workspace branch는 얇은 `delegation_records`를 기본 기록으로 정리한다.
   - 추적성 그래프 기준은 `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md`를 따른다.

5. **문서/대시보드 사용자 경로 점검**
   - README, profile 선택 가이드, 샘플/benchmark 문서는 "빠른 앱 빌더"가 아니라 AI-generated work Trust/Governance Layer 관점으로 유지한다.
   - Dashboard 문서 코멘트, Trace Explorer, QA evidence 표시가 실제 오케스트레이터 판단에 도움이 되는지 샘플에서 확인한다.
   - 새 UI 기능은 문서나 CLI가 안정된 뒤에만 추가한다.

### Next: 0.5 후보

`0.4.x` 안정화 뒤 제품성이나 생산성을 키우는 항목이다.

1. **Spec-to-Scaffold MVP 실험 보류**
   - Gate 2 Program Design에서 class/component, public method, DTO/entity, test mapping을 읽어 skeleton 후보를 만든다.
   - 자동 반영이 아니라 `scaffold-plan`, `scaffold-generate --dry-run`, Orchestrator 확인 순서로 둔다.
   - 코드에서 설계로 역투영하는 기능은 자동 수정이 아니라 `drift-report` 후보로 남긴다.
   - PR #15는 CI 통과 상태지만, 실제 Gate 2 Program Design과 BW-000/Run 작성 시간을 줄이는지 확인하기 전에는 main으로 승격하지 않는다.
   - 효과가 불분명하면 PR을 닫거나 reference 아이디어로만 남긴다.

2. **Performance & Parallelization**
   - `perf-report`류 CLI로 Gate별 wall-clock, Run별 worker duration, QA-Fix 왕복, timeout/watchdog 이벤트를 산출한다.
   - 병렬화는 review, 독립검수, QA command group, UI viewport 증적부터 제한적으로 검토한다.
   - 구현 병렬화는 API/DTO/interface contract와 merge 전략이 충분히 안정된 뒤 검토한다.
   - 상세 기준은 `docs/reference/PERFORMANCE-AND-PARALLELIZATION-STRATEGY.md`를 따른다.

3. **Delivery Profile 구체화**
   - Audit/SI, Product, PoC profile의 Run preset, 검사 엄격도, Dashboard 표시를 더 분명하게 나눈다.
   - Product profile은 OWASP/CWE 기반 보안 기준선과 프로젝트 단어사전/데이터 매핑을 기본으로 삼고, KISA/공공데이터 공통표준은 Audit 전환 gap으로 정리한다.
   - Product profile은 현재 문서 세트, Gate별 필수 산출물, trace 검사, `release-pr --dry-run` evidence 기준이 1차 구현되어 있다.
   - Product fixture smoke 기준은 `docs/reference/PRODUCT-FIXTURE-SMOKE-STRATEGY.md`에 고정했다. 다음 작업은 실제 Product 샘플 재실행으로 fixture가 놓치는 운영 마찰을 확인하는 것이다.
   - PoC compact Run 기준은 `docs/reference/POC-RUN-COMPACT-STRATEGY.md`를 따른다.
   - PoC 산출물 세트 분리 기준은 `docs/reference/POC-PROFILE-TEMPLATE-SET-STRATEGY.md`를 따른다.
   - Product 기준은 `docs/core/PRODUCT_PROFILE_BASELINE.md`를 따른다.

4. **Dashboard 증적/추적 polish**
   - Trace Explorer는 MVP가 들어갔으므로, 샘플 사용 결과를 보고 ID 검색, upstream/downstream 전환, 그래프 복잡도 제어를 보강한다.
   - QA evidence 확대 보기, UIREF와 screenshot side-by-side 비교는 실제 Gate 4 사용감 확인 뒤 진행한다.

5. **Orchestrator CLI facade 검증**
   - `status` MVP부터 시작해 `branch-status`, `profile-status`, `prepare-transition` 진단을 한 화면으로 요약한다.
   - `transition check` 같은 유사 진단 명령은 만들지 않는다. 진단 표면은 `status --check`로 모은다.
   - `status --json --check`는 전환 진단을 `transition_check` 객체로 제공한다.
   - `execute --dry-run` MVP는 Run 실행 전 `run-check`, `run-preflight`, sidecar 후보, scope, 검증 명령을 한 번에 확인하는 수준으로 들어갔다.
   - `execute --dry-run --json`은 같은 계획을 `delegation_sidecar`, `planned_flow`, `run_check`, `preflight`, `scope`, `verification` 구조로 제공한다.
   - 다음 작업은 새 명령 추가가 아니라 샘플에서 Orchestrator가 `status`와 `execute --dry-run`을 자연스럽게 쓰는지 확인하는 것이다.
   - 이후 필요성이 샘플로 검증되면 `plan`, 실제 `execute`, `transition`은 후보로 다시 검토한다.
   - 상세 설계는 `docs/reference/ORCHESTRATOR-CLI-SURFACE-STRATEGY.md`를 따른다.

6. **Delegation sidecar와 worker completion state 검증**
   - native subagent/thread/Agy branch 진행 상태를 `.vulcan/delegations/*.json` sidecar로 읽어 Dashboard에 표시하는 MVP가 들어갔다.
   - worker 완료와 Orchestrator 검증 완료를 Dashboard와 Run 기록에서 분리한다.
   - `execute --dry-run --json`은 native 위임 시작 전에 만들 sidecar 후보를 구조화해 보여준다.
   - `run-check`/`run-preflight`는 완료된 worker Run에 worker 완료 상태만 있고 Orchestrator 재검증 기록이 없으면 경고한다.
   - 다음 작업은 sidecar 스키마 확장이 아니라 샘플에서 실제 위임 기록이 Dashboard/Run/최종 보고에 일관되게 보이는지 확인하는 것이다.
   - 외부 runtime harness에서 참고한 durable progress state와 verified completion 패턴은 `docs/reference/RUNTIME-HARNESS-LESSONS.md`를 따른다.

7. **CLI 유지보수 경계와 배포 방식 정리**
   - `vulcan.py`를 한 번에 재작성하지 않고 session/trace/run/execution/release/doctor 경계부터 테스트 가능한 모듈로 점진 분리한다.
   - 단계별 경계, 검증, 중단 조건은 [`VULCAN-CORE-REFACTORING-PLAN.md`](reference/VULCAN-CORE-REFACTORING-PLAN.md)를 따른다.
   - `doctor`, release 정책/PR body, status 조회 경계를 분리했다. 다음 후보는 session 저장 경계이며, 기능 추가와 구조 이동은 같은 PR에 섞지 않는다.
   - Markdown/YAML 입력 계약은 정규식만 늘리지 않고 구조화 파서와 schema 검증을 우선 적용할 후보를 선정한다.
   - 단일 버전 원천, 문서 링크 검사, migration/golden test를 먼저 넣은 뒤 `pipx`/`uvx` 설치 경로를 검토한다.

8. **외부 효과 검증**
   - 같은 과제를 profile별 또는 무프레임워크 기준과 비교하되 시간만 보지 않고 누락 AC, 재작업, 검토시간, 증적률, 토큰 비용을 함께 측정한다.
   - 공개 end-to-end 샘플 하나를 재현 가능한 fixture와 Dashboard 화면으로 연결한다.
   - 외부 사용자 사례가 생기기 전까지 품질 향상이나 감리 준수를 보장한다고 표현하지 않는다.

### Later: 장기 확장 후보

우선순위는 낮지만 방향성은 유지하는 항목이다.

- **Agent-aware output checker**: 테스트 ID 누락, 공식 로그 미추적, 완료 문서의 `TBD`, 부적절한 `N/A`, 얇은 `delegation_records` 같은 반복 실수를 가볍게 검사한다.
- **Multi-Agent Dispatcher / PR 교차검증**: Ready Run 자동 실행, worker lock, fan-in review, PR cross validation은 현재 실행 흐름이 더 안정된 뒤 검토한다.
- **제출용 문서 생성**: Markdown 원천 문서를 DOCX/XLSX/HWPX 제출본으로 합성하는 전략은 `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md`를 기준으로 한다.
- **Git log 기반 진행 이력**: 별도 통계 저장소를 만들기보다 Git commit 날짜와 메시지에서 파생하는 방향을 검토한다.
- **Canary deployment verification**: Gate 5 이후 preview/staging/canary 검증은 GitHub Actions, secret 관리, 외부 URL 보안 정책이 안정된 뒤 검토한다.
- **외부 runtime backend 후보**: Google AX 같은 event log/resume/trace 지향 runtime은 장기 실험 후보로만 추적한다.

### Parking Lot

현재는 하지 않는 항목이다.

- 파일 watcher 기반 Reactive Session Stream: 문서 임시 저장 중 불완전 상태를 읽거나 승인 전 통계가 완료처럼 보이는 위험이 있어 보류한다.
- 구현 산출물에서 설계 문서를 자동 덮어쓰기: 설계와 코드의 주종 관계가 뒤집힐 수 있으므로 `drift-report` 후보 생성까지만 허용한다.
- 대규모 병렬 구현 자동화: 계약/merge/검증 전략이 더 안정될 때까지 보류한다.

## Delivery Profile 방향

Vulcan-Anvil Ex는 모든 프로젝트에 같은 무게의 절차를 강제하지 않는 방향으로 발전합니다.

| Profile | 목적 | 문서/Gate 강도 |
| --- | --- | --- |
| Audit/SI | 감리, 인수인계, 장기 유지보수 대응 | 가장 강함 |
| Product | 제품 로드맵, 릴리즈, 품질 기준 중심 | 중간 |
| PoC | 기능/기술 가설 실험과 반복 기록 | 낮음 |
자세한 기준 초안은 `docs/core/DELIVERY_PROFILES.md`를 따릅니다.
현재 CLI는 `init --profile`과 `profile-status`를 제공하며, 검사 엄격도와 Dashboard 표시는 후속 단계에서 Profile Overlay와 연결합니다.

## 제출용 문서 전략

작업 중에는 Markdown 원천 문서를 나누어 관리합니다. 제출 시점에는 DOCX/XLSX/HWPX 템플릿과 생성 코드를 통해 필요한 내용을 합성하는 방향을 둡니다.

상세 전략은 `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md`를 기준으로 합니다. 아직 제출본 생성 기능으로 완성된 상태는 아니며, 구현 전 전략 문서로 관리합니다.

## 세션 협업 모델

세션 간 실시간 통신은 Core 전제 조건이 아닙니다.

대신 다음 파일을 공유 상태로 사용합니다.

- `session.json`
- `docs/runs/`
- 증적 파일
- 백로그 문서
- Git 커밋

이상적인 세션 협업 모델은 `docs/reference/SESSION-COORDINATION-IDEAL.md`에 정리되어 있습니다. 실시간 브로드캐스트나 watcher는 향후 확장 옵션입니다.

## 관련 문서의 상태

| 문서 | 현재 용도 | 비고 |
| --- | --- | --- |
| `docs/ROADMAP.md` | 현재 기준 로드맵 | 우선순위 판단 기준 |
| `docs/NEXT_SESSION_HANDOFF.md` | 다음 세션 시작용 요약 | 최신 상태로 유지 |
| `docs/ARTIFACT_TEMPLATE_ROADMAP.md` | 초기 산출물 템플릿 구상 | 참고 문서. 최신 우선순위는 이 문서가 아니라 `ROADMAP.md` |
| `docs/RUN_FIRST_MULTI_AGENT_DISPATCHER.md` | dispatcher 장기 구상 | 일부는 이미 구현됨. 자동 큐/PR 교차검증 검토 시 참고 |
| `docs/core/REFACTORING_PROCESS.md` | 리팩토링 분류 기준 초안 | DEBT/FIND/CR 판단과 문서 영향 분석 기준. 자동화는 향후 보강 |
| `docs/core/DELIVERY_PROFILES.md` | Delivery Profile 기준 | `init --profile`, `profile-status`, profile_rules 기반 Overlay. 검사 엄격도/Dashboard 연동은 후속 보강 |
| `docs/WHICH_PROFILE_SHOULD_I_USE.md` | 사용자용 Profile 선택 가이드 | PoC/Product/Audit을 처음 고르는 기준과 시작 메시지 예시 |
| `docs/EXAMPLES_AND_BENCHMARKS.md` | 샘플/benchmark 요약 | 샘플 실행 결과, profile별 산출물과 시간 차이를 사용자 관점으로 요약 |
| `docs/core/PRODUCT_PROFILE_BASELINE.md` | Product Profile 기준 | 제품/업무 앱 기본 레이어의 보안, 데이터, Gate, Audit 전환 gap 기준 |
| `docs/core/CODEX_MODEL_POLICY.md` | Codex model/effort 정책 | Codex runner의 역할별 모델 선택, 실행 기록, 성능 측정 기준 |
| `docs/reference/REGRESSION-HARNESS-FIXTURE-STRATEGY.md` | 회귀 하네스 fixture 전략 | 기존 샘플 프로젝트 문서를 정규화해 테스트 입력으로 사용하는 방향 |
| `docs/reference/TRACEABILITY-GRAPH-STRATEGY.md` | 추적성 그래프 전략 | 추적표를 그래프 원장으로 사용해 Run 입력과 Dashboard ID 탐색을 자동 추천하는 방향 |
| `docs/reference/PERFORMANCE-AND-PARALLELIZATION-STRATEGY.md` | 성능/병렬화 전략 | 샘플 프로젝트 로그 기준 병목 분석과 perf-report, QA 정합성 자동화, 제한적 병렬화 방향 |
| `docs/reference/FAST-POC-AND-ENV-RUNWAY-STRATEGY.md` | PoC와 개발환경 runway 전략 | PoC 실험 기록, Environment Readiness Track, BW-000 재정의 방향 |
| `docs/reference/POC-PROFILE-TEMPLATE-SET-STRATEGY.md` | PoC 전용 템플릿 세트 전략 | PoC를 audit 템플릿 완충이 아니라 3개 통합 산출물 세트로 검증하는 방향 |
| `docs/reference/PRODUCT-FIXTURE-SMOKE-STRATEGY.md` | Product fixture smoke 전략 | Product profile 회귀 fixture와 실제 샘플 재실행의 합격 기준 |
| `docs/reference/EX-DIRECTION-INVESTMENT-REVIEW.md` | Ex 방향성/투자 판단 기준 | 빠른 AI coding tool이 아니라 AI coding governance framework로 투자할 조건과 축소 신호를 정리 |
| `docs/reference/CODEX-REPO-LOCAL-SKILL-STRATEGY.md` | Codex repo-local skill 전략 | 전역 skill을 건드리지 않고 `.agents/skills`로 Vulcan 절차 카드를 제공하는 기준 |
| `docs/reference/CODEX-CUSTOM-AGENT-STRATEGY.md` | Codex custom agent 전략 | `.codex/agents`로 메인 Orchestrator의 읽기 중심 보조 에이전트를 정의하는 기준 |
| `docs/reference/ORCHESTRATOR-CLI-SURFACE-STRATEGY.md` | Orchestrator CLI 표면 축소 전략 | 원자 명령은 유지하고 `status` MVP부터 운영 표면을 줄이는 방향 |
| `docs/reference/RUNTIME-HARNESS-LESSONS.md` | 외부 runtime harness 참고 기능 정리 | delegation sidecar, execute facade, verified completion, doctor, model routing 등 Ex 고도화 후보 |
| `docs/reference/GIT-LOG-PROGRESS-HISTORY.md` | 날짜별 진행 이력 구상 | 별도 통계 저장소 없이 Git log 기반으로 파생 |
| `docs/reference/SESSION-COORDINATION-IDEAL.md` | 세션 협업 이상형 | 실시간 통신은 Core 전제 조건 아님 |
| `docs/reference/SUBMISSION-DOCUMENT-STRATEGY.md` | 제출용 문서 생성 전략 | DOCX/XLSX/HWPX 기능 구현 전 전략 기준 |
| `docs/reference/AGENT-RUNTIME-BACKEND-CANDIDATES.md` | 외부 agent runtime backend 후보 | 기본은 subprocess, AX 등은 장기 실험 후보 |
