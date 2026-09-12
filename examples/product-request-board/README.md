# Product Request Board

Product 마무리 범위 3의 **로컬 업무 검증 샘플**입니다. [합의한 계약](docs/contracts.md)의 반려→보완→같은 요청 재제출→재검토와 이력 보존을 화면/FastAPI/SQLite에서 확인합니다. [시험 계획](docs/test-plan.md)은 실제 결과와 분리합니다.

범위 5에서는 같은 제품에 [상태별 조회](docs/status-filter.md)를 추가했습니다. 원래 계약을 누적 설명으로 덮지 않고, [확장 시험 계획](docs/status-filter-tests.md)과 [반복·릴리즈 검증 결과](docs/iteration-verification.md)를 별도로 연결합니다. 화면의 상태 선택으로 전체/검토 대기/반려/승인 요청을 조회할 수 있습니다.

## 실행

Python 3.12 이상과 Node.js 22 이상을 사용합니다. 이 디렉터리에서 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm ci
python app.py --demo
```

주소는 `http://127.0.0.1:8157`입니다. 포트가 사용 중이면 `--port`로 변경합니다. SQLite는 `.local/requests.sqlite3`에 저장되며 `--db`로 위치를 지정할 수 있습니다. 앱을 재시작해도 요청과 결정 이력은 유지됩니다. 세션은 메모리이므로 테스트 계정을 다시 선택합니다.

**`--demo`는 실제 로그인이 아닙니다.** 로컬 사용자가 고정 테스트 계정으로 바꿔 역할별 업무 흐름을 확인하는 기능입니다. 서버는 loopback에만 바인딩합니다. 인터넷/사내망에 공개하거나 고객·개인정보를 넣지 마세요. 실제 인증, 운영 보안 및 데이터 보존 정책의 검증을 완료한 샘플이 아닙니다.

## 검증

```powershell
npx playwright install chromium
npm run check:browser
npm run check:static
npm run test:api
npm run test:e2e
npm run check:reports
npm run test:ci-boundaries
npm run test:iteration
```

브라우저 시험은 별도 8161 포트와 독립 SQLite를 사용하며 기존 서버를 재사용하지 않습니다. 필요 시 `REQUEST_BOARD_TEST_PORT`를 변경합니다. `@playwright/test`가 1440px/390px에서 실제 서버를 구동하고 테스트/HTML 보고서를 생성합니다. CI에서 Linux 브라우저 의존성이 없으면 `npx playwright install --with-deps chromium`으로 준비합니다.

입력/기대값은 계획에, 실제 명령·결과·한계는 [검증 보고서](docs/verification.md)에 남깁니다. HTML 보고서는 `npx playwright show-report`로 확인합니다. 생성 DB·브라우저 산출물·의존성은 Git에 포함하지 않습니다. 이 샘플은 init/upgrade로 설치되지 않으며 기존 사용자 프로젝트나 Product 일반 활성화를 변경하지 않습니다.

## PR 자동 검증

[Product Request Board workflow](../../.github/workflows/product-request-board.yml)는 같은 명령을 GitHub Actions에서 실행합니다. PR의 **Checks → Request board quality**를 확인하세요. 실행 화면의 **Artifacts**에서 `request-board-results`로 시작하는 파일을 받으면 API 결과, Playwright HTML/PNG와 실패 원인을 볼 수 있습니다. 보관 기간은 7일입니다.

[필수 검사 목록](ci/required.json)은 API 메서드와 브라우저 태그/viewport를 대조하기 위한 실행 설정입니다. 요구사항/시험 본문을 대신하지 않습니다. 새 필수 동작을 추가하면 시험과 이 목록을 함께 검토합니다. 테스트 0건, 필수 항목 누락/skip, 예상 실패 처리, 재시도 후 성공도 그대로 Pass로 바꾸지 않습니다.

검사 실패는 `failed`, 필수 실행 누락은 `incomplete`, 설치/브라우저 준비 실패는 `environment_blocked`로 보고합니다. 알려진 결함·누락을 임시 사본에 넣는 **검증력 시험**은 해당 실패를 올바르게 감지했을 때 성공합니다. 실제 코드 실패를 무시하는 옵션은 아닙니다.

보고서/README만 바뀌면 샘플 시험은 비적용 처리할 수 있습니다. 샘플의 계약/시험 정의/새 문서, 코드, 설정, CI 변경은 생략하지 않습니다. workflow 자체는 PR마다 시작하여 비적용 이유나 결과를 남깁니다. CI가 아예 시작되지 않았거나 취소되었다면 성공이 아닙니다.

**이 check를 만들었다고 merge가 기술적으로 금지되는 것은 아닙니다.** Required check 지정은 저장소 관리자의 별도 설정이며 이번 변경은 보호 설정, 자동 merge·배포나 고객 프로젝트의 CI를 바꾸지 않습니다. 다른 제품은 자기 스택/필수 시나리오에 맞는 명령을 연결하며, 이 샘플 목록을 일괄 복제하지 않습니다. [CI 검증 결과와 한계](docs/ci-verification.md)를 참고하세요.

`test:iteration`은 새 임시 프로젝트에서 기존 범위 수용→확장→새 검증/수용을 실제 CLI로 시험합니다. 이전 승인 재사용·증적 누락·계약 변경은 거부되어야 하며, 최종 후보에서도 실제 `release-pr` 발행은 허용되지 않습니다. 임시 승인 입력은 테스트용이며 사용자 승인으로 기록하지 않습니다. `.local`의 사용 중인 DB나 기존 고객 프로젝트를 이행하지 않습니다.

이전 [업무 작성 후보 예시](../../scripts/regression/fixtures/product-discovery-writing/README.md)는 당시 미정 상태를 그대로 보존합니다. 여기의 계약은 이후 사용자가 승인한 **샘플 한정** 정책이며 과거 후보를 소급해서 승인으로 고치지 않습니다.
