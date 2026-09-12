# New Product Activation Verification

- 일자: 2026-09-12
- 범위: [Product 마무리 6번](../ROADMAP.md#이번-product-마무리-범위-2026-09-12-6개로-한정), 신규 초기화와 기존 모델 호환
- 운영 원본: [Core CLI 4.1](../core/ORCHESTRATOR_CLI_GUIDE.md#41-개발용-product-반복-프로세스), [상태/승인 계약](PRODUCT-PROCESS-CONTRACTS.md)

## 적용 범위

`init --profile product`는 `product-iterative-v1`의 planning으로 시작한다. 기획·설계, 구현, 인수 검증 세 구간과 이번 범위 인수 완료를 사용한다. 새 profile이나 최상위 CLI는 추가하지 않는다.

첫 scope는 생성된 PRODUCT_BRIEF의 참조만 가진다. 관련 ID, 계약, 시험, 필수 검사와 승인은 비어 있다. 초기 `status --check`의 incomplete_scope는 정상이며, 합의 전 구현이나 가짜 Pass를 만들지 않는다. 총괄이 실제 대화/원본에 기반한 첫 범위를 기존 open-work 요청으로 미리보고 적용한 다음, 준비 검사와 별도 구현 허가를 확인한다.

표식 없는 기존 Product/Audit/PoC는 그대로 유지한다. upgrade는 기존 문서·현재 범위·승인·이력을 이행하거나 초기화하지 않는다. marked Product에서는 복사 전 writer 잠금을 잡고, 최신 session의 source/version만 원자 갱신한다. 이미 초기화된 프로젝트에 init을 다시 실행하면 파일을 변경하기 전에 거부한다.

## 검증

| 대상 | 확인 내용 | 결과 |
| --- | --- | --- |
| 초기화/실제 CLI 회귀 | Codex/Agy/Claude primary별 planning, 빈 범위/무승인 차단, open-work preview/apply, 별도 구현 승인, version/profile-status/잠금 충돌, 기존 모델 upgrade 보존 | 집중 8건 통과. Python 전체 354건 중 351건 통과, Windows symlink 제약 3건 skip |
| Audit init smoke | 기존 Gate 진입 차단과 Run/추적/환경 초기 경로 | 12단계 통과 |
| 기존 profile fixture | 과거 Product/Audit/PoC Gate 계약 회귀. 새 init 기본값과 혼동하지 않도록 임시 legacy fixture를 명시 | 84단계 통과 |
| 같은 제품 반복 | 요청 보드 실제 CLI 반복, 상태 조회 확장, SQLite 반려 이력/기존 수용 보존, 발행 미수행 | 통과 |
| Dashboard | 신규 빈 범위, legacy/잘못된 모델, 3구간/수용 표시. desktop 1440px/mobile 390px | Jest 전체 310건, Product E2E 25건 및 fixture 보정 후 신규 화면 2건 통과. 화면 직접 확인. typecheck/production build 통과, production advisory 0건 |
| 원격 CI | Windows/Linux Python, Dashboard, 제품별 요청 보드 CI | 최종 head의 PR Checks가 원본. 아래 로컬 결과와 원격 완료 시점을 구분 |

실행 경로는 [초기화 시험](../../scripts/regression/tests/test_product_activation.py), [legacy smoke](../../scripts/regression/run_fixture_smoke.py), [화면 시험](../../dashboard/src/__tests__/e2e/product-process.spec.ts), [요청 보드 반복 시험](../../examples/product-request-board/ci/iteration.py)에 있다. 전체 회귀의 첫 실행에서 과거 `init Product = phase0`를 전제한 fixture가 실패했고, 실제 제품 정책을 느슨하게 하지 않고 legacy fixture와 신규 초기화 기대값을 분리했다.

최초 원격 실행에서는 Linux/제품 CI/Dashboard가 통과했고 Windows 잠금 시험 2건이 짧은 임시 경로를 내부 함수에 직접 전달해 실패했다. fixture root를 정규 경로로 만들어 실제 CLI와 같은 입력 계약을 사용하도록 보정했다. 제품의 경로 이탈 방어는 완화하지 않는다. 최종 재실행은 [PR #49 Checks](https://github.com/zeni-on/vulcan-anvil-ex/pull/49/checks)를 기준으로 본다.

## 독립 검토

새 문맥의 native contract reviewer가 version의 legacy 읽기와 upgrade의 늦은 잠금 충돌 처리를 발견했다. marked 읽기 연결, 파일 복사 전 잠금, 명시 오류 처리와 전체 파일 무변경 CLI 시험으로 보정했다. 해당 수정 재검토와 집중 3건에서 추가 지적은 없었다. Dashboard/adapter 담당과 Python 담당의 변경 영역을 분리했고 총괄이 변경과 결과를 재확인했다.

## 한계

- 초기화의 primary 설치 라우팅을 확인한 것이지 Agy/Claude 런타임의 실제 모델 호출을 모두 실행한 것은 아니다.
- Dashboard는 저장 상태 표시다. 테스트/승인 신원을 인증하거나 버튼으로 인수·배포하지 않는다.
- upgrade의 framework 파일 복사 전체는 원자적 트랜잭션이 아니다. 실행 중 worker를 정리한 뒤 수행하고 중간 IO 실패는 상태/원본 확인 후 재시도한다.
- 누적 session은 기존 8MB 한도를 유지한다. 무한 이력, 자동 분할/삭제, 기존 프로젝트 자동 이행은 제공하지 않는다.
- 로컬 Python의 기존 pathlib deprecation warning과 개발 서버의 일시적인 webpack 경고는 남았다. 해당 시험은 통과했으며 원격 production E2E는 PR Checks에서 별도로 확인한다.
- 계약/명령 결과 검사는 업무 의미·실제 권한·테스트 충분성을 대신하지 않는다. 실제 발행은 별도 승인 후 Git/호스팅 도구로 수행하며 자동 dispatcher/배포를 추가하지 않았다.
- PMTool과 사용자 샘플 원본은 변경하지 않았다. 이 여섯 항목 이후에는 추가 기능 묶음을 시작하지 않고 실제 사용 관찰로 전환한다.
