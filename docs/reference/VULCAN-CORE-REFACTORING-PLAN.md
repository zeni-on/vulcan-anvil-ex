# Vulcan Core 점진 리팩터링 계획

## 1. 목적

`vulcan.py`의 공개 CLI는 유지하면서 내부 책임을 테스트 가능한 `vulcan_core/` 모듈로 점진 분리한다.

리팩터링의 성공 기준은 파일 수 증가가 아니라 다음 세 가지다.

- 기존 CLI 인자, 출력 구조, 종료 코드가 유지된다.
- 변경한 영역을 전체 fixture 실행 없이도 빠르게 단위 검증할 수 있다.
- 기능 변경과 구조 이동을 서로 다른 커밋 또는 PR로 분리할 수 있다.

## 2. 원칙

1. 한 번에 한 경계만 분리한다.
2. 각 단계는 동작 기준선 테스트를 먼저 확보한다.
3. `vulcan.py`에는 argparse 라우팅과 하위 호환 wrapper만 남긴다.
4. Gate 상태, Run 문서, 추적성 판정의 의미를 리팩터링 과정에서 바꾸지 않는다.
5. 정규식 기반 Markdown 파싱은 이동만으로 개선됐다고 보지 않는다. golden fixture를 확보한 뒤 구조화 파서 전환을 별도 기능 작업으로 수행한다.
6. init/upgrade가 새 `vulcan_core/` 파일을 대상 프로젝트에 함께 복사하는지 매 단계 검증한다.

## 3. 단계

| 단계 | 경계 | 주요 내용 | 완료 조건 |
| --- | --- | --- | --- |
| M0 | 기준선 | Python compile, core unit, audit smoke, fixture smoke 고정 | CI와 로컬에서 동일 명령 통과 |
| M1 | doctor | 환경 탐지, 결과 요약, text/JSON 렌더링 분리 | `doctor --json` 계약과 종료 코드 유지 |
| M2 | release | release readiness 수집과 PR body 생성 로직 분리 | `release-pr --dry-run` fixture 결과 유지 |
| M3 | session/status | session 로드·정규화·상태 요약 분리 | `status`, `status --check`, `sync-session` 회귀 유지 |
| M4 | run | Run 생성, 입력 계약, run-check/preflight 분리 | 기존 차단/경고 fixture 결과 유지 |
| M5 | trace/contracts | trace graph, check-trace, check-contract 판정 분리 | golden 문서 세트의 오류 위치와 판정 유지 |
| M6 | execution | runner 실행, watchdog, worktree, integration 분리 | 외부 runner dry-run과 lifecycle 기록 유지 |
| M7 | packaging | 단일 버전 원천과 설치 진입점 검토 | init/upgrade 호환 후 pipx/uvx 후보 평가 |

## 4. 현재 상태

- M0: 완료. GitHub Actions에서 compile, core unit, audit smoke, fixture smoke를 실행한다.
- M1: 완료. `vulcan_core/doctor.py`가 진단 로직을 소유하고 `vulcan.py`는 CLI wrapper만 유지한다.
- 다음 후보: M2 release 경계 조사. 코드 이동 전 `release-pr --dry-run` 출력 fixture를 먼저 고정한다.

## 5. 단계별 검증

각 모듈 분리 커밋은 최소한 다음 검증을 통과해야 한다.

```text
python -m py_compile vulcan.py vulcan_core/*.py
python -m unittest discover -s scripts/regression/tests -p "test_*.py"
python scripts/regression/run_audit_smoke.py
python scripts/regression/run_fixture_smoke.py
```

Dashboard 코드를 변경하지 않은 리팩터링 단계에서는 Dashboard 전체 E2E를 반복하지 않는다. CI 설정이나 Dashboard 계약을 함께 변경한 경우에만 타입 검사, 단위 테스트, 빌드, Playwright를 추가 수행한다.

## 6. 중단 조건

다음 중 하나가 발생하면 다음 모듈로 넘어가지 않고 현재 경계를 되돌아본다.

- CLI JSON 필드, 종료 코드 또는 사용자 메시지가 의도 없이 변경됨
- init/upgrade 대상 프로젝트에서 새 모듈 import 실패
- fixture의 기존 차단 조건이 사라지거나 새로운 오탐이 발생함
- 모듈이 `vulcan.py`를 다시 import하여 순환 의존이 생김
- 구조 이동과 정책 변경이 한 diff에서 분리되지 않음

## 7. PR 운영

- 브랜치 하나에는 원칙적으로 모듈 경계 하나만 담는다.
- 기능 추가가 필요하면 리팩터링 PR을 먼저 병합한 뒤 별도 PR로 진행한다.
- 각 PR 설명에는 유지한 CLI 계약, 이동한 책임, 실행한 회귀, 남은 결합 지점을 기록한다.
