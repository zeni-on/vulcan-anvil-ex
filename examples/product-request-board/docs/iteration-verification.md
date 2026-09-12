# 동일 제품 확장과 릴리즈 경계 검증

- 일자: 2026-09-12
- 범위: Product 마무리 6개 중 5번. PR #47 병합 후 같은 요청 보드에서 진행한다.
- 현재: 로컬 검증 완료. 원격 CI 확인 후 실행 링크를 추가한다. 일반 활성화는 6번이다.

## 무엇을 확장했나

기존 반려·보완·재제출 계약과 시험 정의는 그대로 두고, [상태별 조회 계약](status-filter.md)과 [확장 시험 정의](status-filter-tests.md)를 연결했다. 목록/API는 기존 권한에 상태 조건만 추가하며 DB 스키마를 변경하지 않는다. 과거 내용을 새 결과로 덮어 쓰거나 새 필수 Run/Wave를 만들지 않는다.

## 실제 검증 경로

`npm run test:iteration`은 [실행 하네스](../ci/iteration.py)로 새 임시 프로젝트를 만들고 실제 `vulcan.py` CLI를 호출한다. 사용 중인 예제 서버/DB나 PMTool에는 상태를 쓰지 않는다.

| 순서 | 실행과 확인 |
| --- | --- |
| 기존 범위 | planning→impl→acceptance. 실제 FastAPI/SQLite에서 생성·반려·보완·재제출·재반려와 타 사용자 접근 거부를 실행하고 명령 JSON을 남긴다. |
| 기존 범위 수용 | 실행 성공만으로 completed가 되지 않는 것을 확인한 뒤 테스트용 accept 결정을 별도로 전달한다. |
| 새 확장 | 같은 세션에서 open-work. 과거 current_work 전체가 work_history에 보존되고 현재 결정/검증은 초기화된다. 새 planning에서는 릴리즈 후보 조회가 차단된다. |
| 재사용 거부 | 과거 scope의 구현 승인, 과거 범위 검증, scope key만 바꾼 이전 결과, 필수 결과 0건을 거부하며 세션 bytes가 그대로인지 확인한다. |
| 확장 검증 | 별도 프로세스로 같은 SQLite를 다시 연다. 상태별 목록·권한·invalid 입력·재제출에 따른 목록 이동·과거 두 결정 보존과 세 번째 결정 추가를 실제 assertion으로 검사한다. |
| 새 수용 | 정상 검증에도 accept가 없으면 차단한다. 과거 verification key의 수용과 preview 후 계약 변경도 거부한다. 현재 결과에 대한 별도 테스트용 수용만 적용한다. |
| 후보와 발행 구분 | 깨끗한 dev에서 release-pr --dry-run은 candidate지만 release_authorized는 False. 파일/Git refs 변경이 없고, 실제 release-pr은 exit 2로 거부된다. 이후 코드 미커밋 변경을 넣으면 dry-run도 차단된다. |

완료 후 원래 계약/시험 문서 bytes, 기존 명령 증적 bytes, 기존 수용 기록을 대조한다. SQLite는 초기화하지 않고 이어서 사용한다. 제품 작업을 planning/impl/acceptance 세 구간으로 유지하며 과거 Gate 순회나 Run 생성은 없다.

## 로컬 결과

- API 15건 통과: 기존 12건 + 상태 조회/입력/권한/이력 회귀 3건.
- Playwright 12건 통과: 기존 5개 흐름 + 상태 조회 흐름, desktop/mobile 각 실행. 29.8초, 재시도 없음. 화면 PNG에서 필터와 목록/상세 배치, 가로 넘침 없음 확인.
- compile/syntax, 필수 보고서 대조 통과. 기존 결함·누락·환경 차단 probe 7개 통과.
- CI 정책/보고서 회귀 20건 통과. iteration step도 누락/실패/skip/취소 시 최종 성공으로 집계되지 않는다.
- 두 작업 범위를 잇는 실제 CLI/SQLite 시나리오 통과. 하나의 통합 시험 안에서 위 허용·거부 경계를 모두 assert한다. 이를 수십 건의 독립 인수 시험으로 부풀리지 않는다.

결과는 `ci-artifacts/iteration/`의 test.log, commands.json, summary.json, session.json, evidence/에 생성된다. 실행 시 해당 전용 출력만 재생성하며 임시 DB는 회수하지 않는다. GitHub CI의 기존 7일 artifact 정책을 사용한다.

## 한계

- `synthetic-owner` 결정은 명시적인 시험 fixture다. 실제 사용자가 해당 기능을 수용했다거나 승인 출처를 인증했다는 뜻이 아니다.
- 현재 구현으로 두 프로세스/작업 범위를 실행한 시험이다. 구버전 바이너리를 새 바이너리로 교체하는 업그레이드, DB migration, 운영 데이터 이행 시험은 아니다.
- CLI 반복 시나리오는 API/SQLite 기반이며 화면 assertion은 별도 Playwright 시험이다. 브라우저 실행 결과까지 자동으로 사용자 수용으로 승격하지 않는다.
- 상태 계약은 소스 변경의 의미를 자동 판단하지 않는다. 이번 확장에서는 총괄이 영향 있는 기존/신규 시험을 함께 재실행했다. 별도 Git 증적/SHA 원장은 추가하지 않는다.
- scope completed는 이번 범위 수용이지 제품 전체 완료/발행 권한이 아니다. 테스트용 로컬 Git 저장소에는 remote가 없으며 push/PR/배포/보호 설정을 변경하지 않는다. 실제 발행 기능을 추가한 것이 아니다.

구현 위임은 native worker Banach(앱/API/UI/해당 시험), 총괄은 확장 문서·상태 반복 하네스·CI 연결·재검증을 맡았다. 모델 override는 사용하지 않았고 별도 Run/외부 CLI worker를 만들지 않았다.

새 문맥의 native contract-reviewer Singer가 baseline 증적의 직접 실행 범위와 음성 시험의 거부 사유를 지적했다. 총괄은 baseline에 재제출/타 사용자 재제출 거부 assertion을 넣고, 다른 범위/필수 결과 누락/계약 변경의 정확한 진단을 요구하도록 보강했다. 승인 누락만으로 시험이 우연히 통과하지 않게 확인한다.
