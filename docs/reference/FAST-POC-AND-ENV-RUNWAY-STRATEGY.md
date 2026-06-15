# Fast PoC and Environment Readiness Runway Strategy

> 목적: PoC profile을 실제 빠른 실험에 맞게 줄이고, 구현 단계에서 처음 개발환경을 만드는 병목을 줄이기 위해 Environment Readiness Track을 정의한다.

## 1. 배경

`sample-ex-poc-agy-0608-1`의 PoC 실행은 Gate 4까지 약 29분이 걸렸다.
`sample-ex-poc-codex-0609-1`의 PoC 실행도 Gate 4까지 약 35분이 걸렸고, subagent 없이 Gate별 Orchestrator Plan Run 7개가 생성되었다.
반면 같은 수준의 화면 프로토타입을 프레임워크 없이 만들면 약 4~5분 수준으로 관찰되었다.

이 차이는 PoC profile이 아직 "빠른 실험"이라기보다 "경량 governance"로 동작하고 있음을 보여준다.
PoC가 유용하려면 다음 두 조건을 만족해야 한다.

- 단순 프로토타입은 5~10분 안에 동작 결과를 볼 수 있어야 한다.
- 실패, 미실행, 환경 차단은 정직하게 남기되 audit 수준 산출물과 Build Wave 절차를 강제하지 않아야 한다.
- Gate별 계획 Run을 습관적으로 만들지 않고, `docs/poc` 3종과 `status --check`를 기본 운영 표면으로 삼아야 한다.

## 2. Fast PoC 목표

Fast PoC는 결과 품질을 낮추는 모드가 아니다.
문서와 승인 비용을 줄이고, 가설 검증에 필요한 최소 기준만 유지하는 모드다.

권장 목표:

| 항목 | 목표 |
| --- | --- |
| 단순 UI/API 프로토타입 Gate 4 도달 | 5~10분 |
| PoC 전체 종료 판단 | 10~15분 |
| 필수 문서 | `docs/poc/` 3종 |
| Run 문서 | 기본 생략, 긴 위임/외부 runner/재현 필요 시만 compact Run |
| UI 증적 | smoke/demo 캡처, console log, build log |
| 공식 QA | product/audit 승격 시 보강 |

## 3. Fast PoC 흐름

```text
init --profile poc
→ POC_REQUIREMENTS: 목표, 성공 기준, HYP/REQ 최소 작성
→ POC_SYSTEM_DESIGN: 기술 선택, 화면/API/데이터 개요, Environment Readiness 결과 요약
→ 구현: subagent/native branch worker가 환경 생성과 기능 구현을 한 번에 수행
→ POC_TEST_REPORT: smoke/demo 결과, 증적, Continue/Pivot/Stop/Promote 판단
```

Fast PoC에서는 Phase 0, Gate 1, Gate 2, Gate 3 이름을 유지할 수 있지만, 각 Gate를 무거운 문서 작성 단계로 운영하지 않는다.
사용자 승인도 모든 Gate마다 길게 받기보다 다음 세 지점으로 압축한다.

| 승인 지점 | 의미 |
| --- | --- |
| Start Checkpoint | 목표와 성공 기준 확인 |
| Design Checkpoint | 기술/화면/API/데이터 방향 확인 |
| Demo Checkpoint | smoke/demo 결과와 다음 판단 확인 |

## 4. Environment Readiness Track

현재 audit/product 흐름에서는 구현 단계에 들어간 뒤 `BW-000 implementation-scaffold`로 개발환경과 skeleton을 만든다.
하지만 개발환경은 기능 구현이 아니라 작업대 준비에 가깝다.
따라서 모든 profile에서 설계가 진행되는 동안 별도 Track으로 병렬 준비할 수 있다.

### 4.1 역할

Environment Readiness Track은 SA/AA 성격의 subagent 또는 native branch agent가 담당한다.
이 worker는 설계 문서를 보며 다음을 준비한다.

- 프로젝트 폴더 구조
- package/lockfile 또는 backend dependency 파일
- lint/build/test script
- hello world 또는 health check
- 최소 import/compile/build smoke
- Playwright 또는 UI smoke 실행 가능성 확인
- 환경 차단 원인 기록

### 4.2 허용 범위

허용:

- 빈 앱 생성
- hello world, health endpoint
- 빌드/테스트 도구 설정
- 기본 폴더 구조
- 예제 smoke test
- 의존성 설치 가능성 확인

금지:

- 업무 요구사항 구현 완료 선언
- 실제 business API/DB/UI 요구사항 구현
- 테스트 Pass 또는 UI Pass 확정
- 요구사항 추적표 `Implemented`/`Verified` 반영
- Gate 상태 변경

### 4.3 브랜치 기준

Environment Readiness Track의 결과는 기능 구현이 아니므로 main 기준선에 반영될 수 있다.
다만 다음 조건을 지켜야 한다.

- main에는 문서 기준선과 개발환경 기준선만 둔다.
- 업무 기능 구현은 `workflow.integration_branch` 또는 native branch worker 결과로 분리한다.
- 환경 준비 커밋은 `env:` 또는 `scaffold:` 같은 메시지로 기능 구현 커밋과 구분한다.
- 환경 준비가 제품 코드처럼 커지면 implementation wave로 이동한다.

## 5. BW-000 재정의

`BW-000 implementation-scaffold`는 기본 구현 Wave가 아니라 예외 fallback으로 낮춘다.

| Profile | 기본 방향 |
| --- | --- |
| `poc` | BW-000 기본 생략. 첫 구현 worker가 환경 생성 + 핵심 기능 + smoke를 함께 수행한다. |
| `product` | Environment Readiness Track을 먼저 시도하고, 환경이 불완전할 때만 BW-000 사용. |
| `audit` | 설계 중 Environment Readiness Track을 허용하되, 공식 계약 skeleton이 필요한 경우 BW-000 유지. |

즉 구현 단계의 첫 질문은 "BW-000을 만들까?"가 아니라 다음이어야 한다.

```text
환경 준비 상태가 충분한가?
- 충분함: BW-001 feature 구현 시작
- 부족하지만 PoC임: 첫 구현 worker가 환경과 기능을 함께 만든다
- 부족하고 audit/product 공식 계약 필요: BW-000 또는 Environment Readiness Run으로 분리
```

## 6. Fast PoC 산출물 기준

`POC_REQUIREMENTS.md`:

- 목표
- 성공 기준
- HYP-001
- REQ-001~REQ-003 수준의 핵심 시나리오
- 제외 범위

`POC_SYSTEM_DESIGN.md`:

- 기술 선택
- 단일 Mermaid 또는 간단 구조 설명
- 주요 화면/API/데이터 개요
- Environment Readiness 결과 요약

`POC_TEST_REPORT.md`:

- 실행 명령
- build/smoke/demo 결과
- 스크린샷 또는 로그 링크
- 실패/미실행/환경 차단
- Continue/Pivot/Stop/Promote 판단

## 7. 구현 후보

1차 구현은 문서와 운영 기준을 먼저 고정한다.
그 다음 CLI와 dashboard를 최소 보강한다.

후보:

- `status`에 Environment Readiness 요약 표시
- `metrics`로 git timeline, 코드/문서/증적 라인 수, Run/위임 기록 수를 자동 산출
- `init --profile poc` 후 next action에 "목표/성공 기준 작성"만 우선 표시
- PoC에서 `gate-start`가 Gate별 Orchestrator Plan Run 자동 생성을 생략하고 `docs/poc` 작성 후보를 먼저 안내
- `wave-start BW-000`을 PoC에서 경고 또는 생략 후보로 안내
- Dashboard에 PoC 3종 문서와 Environment Readiness 상태를 별도 표시
- PoC 검사기는 `T-001`/`EV-001` 같은 특정 ID 대신 `T-*`/`EV-*` 패턴을 허용한다.
- PoC worker Run preset은 `app/`, `static/`, `tests/`, `docs/poc/evidence/` 같은 실제 PoC 경로를 기본으로 하고, audit용 `backend/`, `frontend/`, `docs/artifacts/04-review/evidence/`는 기본 주입하지 않는다.
- `delegation_records`는 단순 책임 기록을 넘어 병목 분석을 위해 `duration_seconds`, `heartbeat_count`, `status_probe_count`를 포함한다.

## 8. 성공 기준

Fast PoC 개선은 다음 조건을 만족해야 한다.

- 단순 Todo/Counter/Hello API PoC가 Gate 4 smoke까지 5~10분 목표에 가까워진다.
- audit 문서 누락 때문에 막히지 않는다.
- BW-000을 기본 생성하지 않는다.
- 환경 준비와 업무 기능 구현의 책임 경계가 문서에 남는다.
- PoC 결과를 product/audit으로 승격할 때 필요한 gap이 식별된다.
