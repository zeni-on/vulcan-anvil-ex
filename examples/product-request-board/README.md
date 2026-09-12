# Product Request Board

Product 마무리 범위 3의 **로컬 업무 검증 샘플**입니다. [합의한 계약](docs/contracts.md)의 반려→보완→같은 요청 재제출→재검토와 이력 보존을 화면/FastAPI/SQLite에서 확인합니다. [시험 계획](docs/test-plan.md)은 실제 결과와 분리합니다.

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
python -B -m unittest discover -s tests -p test_api.py -v
npx playwright install chromium
npm run test:e2e
python -B tests/probe_history.py
```

브라우저 시험은 별도 8161 포트와 독립 SQLite를 사용하며 기존 서버를 재사용하지 않습니다. 필요 시 `REQUEST_BOARD_TEST_PORT`를 변경합니다. `@playwright/test`가 1440px/390px에서 실제 서버를 구동하고 테스트/HTML 보고서를 생성합니다. CI에서 Linux 브라우저 의존성이 없으면 `npx playwright install --with-deps chromium`으로 준비합니다.

입력/기대값은 계획에, 실제 명령·결과·한계는 [검증 보고서](docs/verification.md)에 남깁니다. HTML 보고서는 `npx playwright show-report`로 확인합니다. 생성 DB·브라우저 산출물·의존성은 Git에 포함하지 않습니다. 이 샘플은 init/upgrade로 설치되지 않으며 기존 사용자 프로젝트나 Product 일반 활성화를 변경하지 않습니다.

이전 [업무 작성 후보 예시](../../scripts/regression/fixtures/product-discovery-writing/README.md)는 당시 미정 상태를 그대로 보존합니다. 여기의 계약은 이후 사용자가 승인한 **샘플 한정** 정책이며 과거 후보를 소급해서 승인으로 고치지 않습니다.
