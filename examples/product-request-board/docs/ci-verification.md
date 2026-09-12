# 요청 보드 제품 CI 검증

- 일자: 2026-09-12
- 범위: Product 마무리 6개 중 4번. [업무 흐름 검증](verification.md)에 사용한 같은 샘플을 CI에 연결한다.
- 현재: 로컬 및 GitHub 원격 제품 CI 검증 완료, [PR #47](https://github.com/zeni-on/vulcan-anvil-ex/pull/47) 병합 대기.

## 연결과 책임

[Workflow](../../../.github/workflows/product-request-board.yml)는 PR/main push/수동 실행에 반응하며 `Request board quality` check를 만든다. Python 3.12/Node 22와 선언된 의존성/Chromium을 새 hosted runner에 준비한다. 개발자 PC의 node_modules/브라우저 캐시를 복원하지 않는다. [package scripts](../package.json)가 로컬·원격 명령의 공통 원본이다.

정적 검사는 Python compile과 JavaScript syntax 범위다. CodeQL, 포괄적 보안 분석, 정적 타입 검사를 도입했다고 표현하지 않는다. 업무 결과는 실제 API/SQLite 및 공식 Playwright assertion으로 검사한다.

필수 실행 설정은 [required.json](../ci/required.json)에 있다. API 메서드 목록, browser 태그와 desktop/mobile 실행을 결과에서 확인한다. 시험/필수 목록을 함께 임의 삭제하는 공격까지 자동 방지하는 기능은 아니다. 이 파일과 CI/시험 코드 변경은 리뷰 대상이다.

workflow를 path filter로 통째로 건너뛰지 않는다. [scope 정책](../ci/policy.py)은 코드/설정/CI 또는 샘플의 계약·시험 정의·알 수 없는 새 문서 변경을 검사 대상으로 본다. README/기존 결과 요약 등 명시된 설명 문서는 샘플 시험을 생략할 수 있다. 알 수 없는 diff는 실행 또는 차단으로 처리하며 성공으로 추정하지 않는다.

PR에서는 base와 현재 PR 전체 변경을 비교한다. 코드가 포함된 PR에서 마지막 커밋만 보고서 수정이라고 제품 검사를 생략하지 않는다. 문서-only 비적용은 PR의 비교 범위 전체가 해당할 때의 동작이다.

마지막 step은 `always()`로 각 필수 step의 실제 `outcome`과 `conclusion`을 대조한다. 실패를 `continue-on-error`로 감추거나 필요한 step을 skip/취소/누락하면 성공하지 않는다. 설치/브라우저 준비 실패는 환경 차단으로 분리한다. workflow 전체가 실행되지 않거나 job 자체가 취소된 경우에는 마지막 step도 보장되지 않으므로 예상 check의 부재/취소를 통합 시점에 확인해야 한다.

GitHub token은 contents read, checkout credential은 저장하지 않는다. 배포/secret/운영 DB, 권한 있는 후속 실행은 없다. 허용한 로그·JSON·HTML·PNG만 7일 artifact로 보존하며 `.local` DB와 node_modules는 포함하지 않는다. 저장소 보호 설정은 변경하지 않았다.

## 로컬 관측

| 검사 | 관측 |
| --- | --- |
| 정적 검사, 실제 Chromium launch | 통과 |
| API 실행/필수 메서드 대조 | 12건 통과 |
| 브라우저 실행 | desktop/mobile 합계 10건 통과, 21.3초 |
| 실제 보고서 대조 | 통과. JSON의 태그에서 `@`가 빠지는 실제 형식을 반영해 파서 수정 |
| 정책/보고서 단위 회귀 | 20건 통과. mandatory step의 skip/취소/누락/실패, 보고서 누락·중복·기대 실패·재시도와 문서 분류 포함 |

`npm run test:ci-boundaries`는 다음 7개 경계를 검사한다. 1~6은 실제 subprocess/임시 환경 실행이고, 7은 실제 정상 보고서의 사본을 바꾼 파서 시험이다.

| 의도적으로 만든 상황 | 기대한 실제 관측 |
| --- | --- |
| 이전 반려 내용을 최신 내용으로 덮어쓰는 결함 | 기존 보존 assertion 실패, child exit 1, failed |
| 필수 보존 테스트만 탐색에서 제외 | 나머지 시험이 성공해도 missing, incomplete |
| 필수 테스트 skip | skipped, incomplete |
| API 테스트 0건 | incomplete |
| 보존 assertion을 무조건 return으로 약화 | 기존 결함 probe가 검증력 상실을 감지하여 거부 |
| 빈 Chromium 캐시 | launch 준비 실패, child exit 3, environment_blocked |
| 무관한 브라우저 시험만 남기고 핵심 흐름 결과 삭제 | desktop/mobile의 필수 흐름 누락, incomplete |

이 실패를 기대대로 감지하면 검증력 시험 자체는 통과한다. 정상 제품 검사의 실패를 green으로 바꾸는 동작이 아니다. 임시 사본만 수정하며 동작 중인 로컬 샘플/사용자 데이터는 바꾸지 않는다.

Native worker Cicero가 scope/step 집계와 단위 회귀를 맡았다. 새 문맥의 native contract-reviewer Dewey는 Git rename 탐지가 원래 코드/계약 경로 삭제를 숨길 수 있다고 지적했다. 총괄은 `git diff --no-renames`로 원래 경로도 검사하도록 고치고 임시 Git 저장소의 실제 rename 회귀를 추가했다. 문서 분류/집계와 보고서 검사를 다시 실행했다. 별도 Run/외부 CLI agent나 자동 승인은 없다.

## 원격 기록

[GitHub 실행 34686757012](https://github.com/zeni-on/vulcan-anvil-ex/actions/runs/34686757012)의 `Request board quality`가 **1분 10초에 성공**했다. Ubuntu hosted runner의 Python 3.12/Node 22에서 의존성 설치, Chromium 설치/launch, 정적 검사, API, 화면, 보고서 대조, 실패 probe, artifact 보존과 최종 집계가 모두 실행되었다.

총괄이 `request-board-results-1` artifact를 회수하여 직접 확인한 내용:

- `ci-artifacts/api.json`: 12건 실행/12건 passed.
- `test-results/results.json`: 10건 expected, unexpected/skipped/flaky 각 0. 원격 Playwright 실행 시간은 12.5초.
- `ci-artifacts/reports-summary.json`: passed, 이슈 없음.
- `ci-artifacts/probes.json`: 위 7개 경계 모두 기대대로 감지. 실제 결함 failed, 누락/skip/0건 incomplete, 빈 브라우저 캐시 environment_blocked.
- `playwright-report/index.html`과 desktop/mobile PNG 존재. 최종 집계 로그는 success, issues 없음.

이것은 실제 원격 실행/리포트 확인이다. 단, 의도적 실패는 같은 job 안의 격리 subprocess에서 검사했고, 필수 step 누락/취소 집계는 단위 계약 시험이다. 전체 GitHub job을 고의로 취소하거나 보호 규칙의 강제 merge 거부를 실험했다는 뜻은 아니다.

GitHub는 기존 저장소와 같은 action 버전(checkout v4, setup-node v4, setup-python v5, upload-artifact v4)의 Node 20 런타임 deprecation 경고를 표시했다. hosted runner가 Node 24로 실행했고 실제 검사는 성공했다. 이것은 제품을 실행한 Node 22 버전과 별개이며, 경고가 없었다고 기록하지 않는다.

## 한계와 다음

이 샘플의 Linux CI 연결만 다룬다. 외부 프로젝트/Jenkins/조직망/Windows 제품 CI로 일반화하지 않는다. 실제 GitHub job 취소, workflow trigger 제거, 외부 fork 승인 정책, 브랜치 보호의 merge 차단을 실험한 것은 아니다. 누락/skip 집계는 단위 계약으로 검사하며 실패 시험은 내부 subprocess에서 관측한다. CI 성공과 사용자 인수·배포 승인은 분리되어 있다.

다음 5번은 같은 제품의 기능 확장/기록 보존과 릴리즈 권한, 6번은 신규 Product 일반 활성화다. init/upgrade/Core에 제품별 CI 스크립트를 자동 주입하거나 PMTool을 이행하지 않는다.
