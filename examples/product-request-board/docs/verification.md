# 요청 보드 로컬 검증 결과

- 실행일: 2026-09-12
- 범위: Product 마무리 6개 중 **3번, 실제 화면/API/DB의 업무 흐름 검증**
- 기준: [합의한 샘플 계약](contracts.md), [시험 정의](test-plan.md)
- 환경: Windows, Python 3.14.3, Node.js 24.14.0, FastAPI 0.115.6, SQLite, Playwright 1.61.1/Chromium

## 합의와 검증 대상

사용자가 로컬 샘플에 한정하여 작성자 재제출, 본인 요청이 아닌 건에 대한 검토자 검토, 제출 전 보완 내용 비공개, 권한별 이력 조회와 반복 반려 이력 보존에 동의했다. [기존 대화 연습](../../../docs/reference/PRODUCT-DISCOVERY-PILOT-REQUEST-BOARD.md#9-로컬-실행-샘플의-후속-합의-2026-09-12)에 후속 합의를 연결했다.

화면에서 요청 → 사유를 넣어 반려 → 같은 요청 보완 → 재제출 → 다른 검토자 반려 → 다시 보완 → 승인 → 새로고침을 실제 실행했다. 최신 내용, 두 반려 당시 내용과 사유, 검토 회차/담당자를 각각 확인했다. 다른 브라우저에서 보완 중 내용을 읽을 수 없고 재제출 후에만 변경 내용이 보였다.

## 실제 실행

아래 명령의 작업 디렉터리는 이 샘플의 루트다. 계획의 `Planned`는 실행 상태로 덮어쓰지 않았다.

| 명령 | 최종 관측 | 실제 근거 |
| --- | --- | --- |
| `python -B -m unittest discover -s tests -p test_api.py -v` | 12건 통과 | `.local/api-tests.log`, [API 시험](../tests/test_api.py) |
| `npm run test:e2e` | 5개 시험 × desktop/mobile, 10건 통과, 23.5초 | `.local/browser-tests.log`, `test-results/results.json`, [브라우저 시험](../tests/browser/request-board.spec.js) |
| `python -B tests/probe_history.py` | 고의 결함 사본의 이력 비교 assertion 1건 실패를 올바르게 감지, probe 종료 코드 0 | `.local/history-probe.log`, [검증력 시험](../tests/probe_history.py) |

REG-001~005 및 SEC-REG-001~005의 기대 동작을 위 API/브라우저 시험에서 확인했다. 항목 ID 수와 실행 테스트 수는 서로 다른 집계다. 허용되지 않은 읽기/재제출/자기 검토, 중복·오래된 버전, 입력 오류, 동시 검토 시 데이터가 바뀌지 않는지 검사했다. SQLite 동일 파일을 새 앱 인스턴스가 읽을 때 이력이 유지되는 것도 확인했다.

Ex 루트의 `python -B -m unittest discover -s scripts/regression/tests -p test_product_discovery_writing.py -v` 11건도 통과했다. 현재 샘플 계약/Planned 시험을 기존 `document_readiness`가 읽기 전용으로 수집하는지와 문서 링크·앵커를 확인했다. 새 `session.json` 생성이나 승인·상태 전환은 하지 않았으며, 이 문서 검사를 앱 시험 통과로 대신 계산하지 않는다. `node --check static/app.js`와 `git diff --cached --check`도 통과했다.

`request-history.png`는 `test-results`의 SCN-001 desktop/mobile 결과 디렉터리에 있고 HTML 보고서에 첨부된다. 총괄이 실제 PNG를 열어 1440px/390px의 내용·이력·버튼·아이콘과 겹침을 확인했다. 긴 문자열의 가로 넘침과 사용자 콘텐츠의 HTML 비실행도 브라우저 assertion으로 검사했다. HTML은 샘플 루트에서 `npx playwright show-report`로 연다.

이 로그/HTML/JSON/PNG는 로컬 생성물이며 커밋되지 않는다. 공개 저장소에는 재현 가능한 시험 소스와 이 요약을 남긴다. 원격 산출물 보존은 다음 CI 패키지에서 연결한다.

## 시험과 리뷰에서 고친 문제

| 발견 | 보완 | 재검증 |
| --- | --- | --- |
| 새 요청을 제출해도 이전 요청이 선택됨. 최초 브라우저 실행은 1건 통과/7건 실패 | 생성 응답의 새 ID를 선택 | 연속 제출 및 전체 브라우저 10건 통과 |
| 다른 탭에서 계정 변경 시 기존 화면의 입력이 새 계정으로 제출될 수 있음 | 탭 간 변경 통지·입력 초기화, 표시 계정/세션 불일치 시 서버가 쓰기 거부 | 동일 브라우저의 두 탭 시험 + API 불일치 거부 |
| 행과 이력 사이에 commit이 발생하면 조회 응답 시점이 섞일 수 있음 | 읽기에도 명시 트랜잭션 적용 | WAL 모드에서 두 SELECT 사이 commit을 넣어 목록/상세의 일관성 검사 |
| SQLite 정수 범위 밖 ID가 내부 예외 발생 | 경로 ID 범위 검증과 공통 422 응답 | 상세/결정/재제출에 경계 밖 ID를 보내고 DB 불변 확인 |

Frontend는 native worker Bohr가 `static/` 3개 파일에 한정해 작성했다. 새 문맥의 native `contract-reviewer` Laplace는 읽기 전용으로 위 권한·조회·입력 위험 3건을 제시했다. 총괄이 수정, API/실제 브라우저 재검증 및 화면 열람을 수행했다. 별도 Run, 자동 Gate 승인, 외부 CLI runner는 사용하지 않았다.

고의 결함 probe는 임시 복사본에서만 이전 내용을 덮어쓰며 정상 소스/사용자 DB는 수정하지 않는다. 문법 검사가 아니라 **사용자가 원한 이력 보존을 깨뜨리면 기존 시험이 실패하는가**를 확인한 것이다. 남아 있는 실제 제품 결함으로 집계하지 않는다.

## 한계와 다음 경계

- 로컬 테스트 계정 선택은 실제 인증이 아니다. 운영 인증/권한 관리, 보존 기간, 배포 보안, 부하·접근성 전수 검사는 완료 범위가 아니다.
- 현재 기계의 Chromium에서 검증했다. 실제 휴대기기/Safari/Firefox와 다른 OS의 이 샘플 실행은 아직 미검증이다.
- FastAPI/Starlette의 Python 3.14 deprecation warning과 Node 색상 환경 warning은 남아 있으며 시험 실패는 아니다. 전역 라이브러리를 임의 업그레이드하지 않았다.
- 앱 재생성 및 실제 파일 저장은 확인했지만 OS 강제 종료·전원 손실 복구까지 입증한 것은 아니다.
- 이 샘플은 Ex 상태 머신을 다시 구현하거나 전체 init→수용→배포 흐름을 통과시킨 프로젝트가 아니다. 기존 상태/승인 회귀와 이번 업무 assertion은 서로 다른 검증이다.
- **제품 원격 CI는 4번**, 기능 확장과 배포 권한 경계는 5번, 신규 Product 일반 활성화는 6번에서 다룬다. PMTool/과거 후보 fixture를 변경하지 않았고 사용자 인수/배포 승인을 대행하지 않는다.
