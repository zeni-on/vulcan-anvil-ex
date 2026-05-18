# Gate 4 QA 테스트 결과서

```yaml
---
document_id: DOC-QA-G4-002
title: QA Test Result
title_ko: QA 테스트 결과서
project:
gate: G4
status: Draft
version: v0.1
owner_role: QA Reviewer
author:
reviewer:
approver:
created_at:
updated_at:
related_ids:
  - REQ-
change_reason: 최초 초안 작성
---
```

## 1. QA 범위

| 구분 | 범위 |
| --- | --- |
| 대상 기능 |  |
| 대상 요구사항 | REQ- |
| 대상 화면 | SCR- |
| 기준 시안 | UIREF- |
| UI 구현 계약 | UICON- |
| QA 방식 | 단위/통합 테스트, 추적성 검사, 브라우저 확인, 화면 캡처 증적 |

## 2. 요구사항 검증 요약

> 대시보드는 이 표를 테스트 실행 목록이 아니라 요구사항별 검증 요약으로 렌더링한다. 헤더명은 유지한다.

| REQ-ID | 검증 항목 | 관련 테스트 | 결과 | 증적 |
| --- | --- | --- | --- | --- |
| REQ- |  | UT- / IT- / UI-001-01 | Pass / Fail / Not Run / Skipped | EV- / UI- / LOG- 또는 경로 |

## 3. 실행 검증

> 명령, 브라우저 수동 확인, Playwright, 보안 점검 등 실제 실행한 검증만 작성한다.
> 개발표준정의서의 "빌드, 실행, 테스트 명령" 표에서 필수로 지정한 명령은 실행 결과를 모두 기록한다.
> `Pass`는 성공 기준, exit code, 로그/증적이 모두 확인될 때만 기록한다.

| 검증 ID | 목적 | 실행 위치(cwd) | 명령/방법 | OS | 필수 여부 | 성공 기준 | Exit Code | 결과 | 로그/증적 | 요약 | 관련 Run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA-CMD-001 | 단위 테스트 | repository root | `./gradlew test` | Windows / POSIX | 필수/선택 | exit code 0, 실패 0건 | 0 / 1 / N/A | Pass / Fail / Not Run / Skipped | `build/reports/tests/test/` |  | RUN- |

실행 검증 기록 기준:

- 필수 명령을 실행하지 못한 경우 결과를 `Not Run`으로 기록하고 사유, 영향 범위, 후속 조치를 요약에 남긴다.
- 프로젝트 범위상 적용하지 않는 명령은 `Skipped`로 기록하고 승인 근거 또는 적용 제외 사유를 남긴다.
- `Exit Code`를 확인할 수 없는 수동 검증은 `N/A`로 적고, 대신 관찰 증적 파일을 연결한다.

## 4. 화면 증적

> 대시보드는 이 표의 헤더를 기준으로 이미지 썸네일과 미리보기를 렌더링한다. 파일은 프로젝트 기준 상대 경로를 쓴다.
> 화면 증적은 화면 단위가 아니라 상태/시나리오 단위로 기록한다. 기대 화면과 다른 캡처를 Pass 증적으로 연결하지 않는다.

| 증적 ID | 관련 UI | 관련 SCR | 상태/시나리오 | 기대 화면 | 실제 확인 | 파일 | 결과 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-UI-001-01 | UI-001-01 | SCR-001 | 회원가입 기본 화면 | 이메일/비밀번호/비밀번호 확인/가입 버튼이 보인다 |  | docs/artifacts/04-review/evidence/ui/UI-001-01_signup_default_desktop.png | Pass / Fail / Not Run |
| EV-UI-001-02 | UI-001-02 | SCR-001 | 약한 비밀번호 오류 | 오류 메시지가 보이고 가입이 차단된다 |  | docs/artifacts/04-review/evidence/ui/UI-001-02_signup_weak_password_desktop.png | Pass / Fail / Not Run |
| EV-UI-001-05 | UI-001-05 | SCR-001 | 회원가입 성공 | 가입 완료 메시지와 로그인 안내가 보인다 |  | docs/artifacts/04-review/evidence/ui/UI-001-05_signup_success_desktop.png | Pass / Fail / Not Run |

### 4.1 UI 증적 판정 규칙

| 항목 | 기준 |
| --- | --- |
| Pass | 기대 화면, 메시지, 상태 전환이 증적 파일에서 확인된다 |
| Fail | 화면은 확인했지만 기대 화면과 다르다 |
| Not Run | 캡처 또는 브라우저 검증을 수행하지 못했다 |
| FIND 등록 | 테스트 항목과 증적 파일이 맞지 않거나, 기대 화면을 보여주지 못하는 캡처가 Pass로 기록된 경우 |

### 4.2 UIREF 구현 계약 비교

프로토타입이나 외부 시안이 UI Implementation Contract로 지정된 경우, 기준 UIREF와 구현 화면을 비교한다.
허용된 차이는 근거를 남기고, 허용되지 않은 차이는 `FIND`로 등록한다.
요구사항, 보안 정책, 화면 설계 자체를 바꿔야 하는 차이는 `CR`로 승격한다.

| 비교 ID | 관련 UI | 관련 Contract | 기준 UIREF/파일 | 구현 증적 | 차이 | 허용 여부 | 처리 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UICMP-001 | UI-001-01 | UICON-001 | UIREF-001 / docs/artifacts/02-design/screen/prototypes/UIREF-001/index.html | docs/artifacts/04-review/evidence/ui/UI-001-01_signup_default_desktop.png |  | 허용 / 미허용 | Pass / FIND- / CR- |

## 5. QA 발견사항과 재귀 수정 방침

| 항목 | 내용 |
| --- | --- |
| 현재 Open FIND | 없음 / FIND- |
| QA 중 발견된 결함 처리 | 기존 설계 범위 안의 결함은 FIND 등록 후 G4 QA Fix Loop에서 수정, 테스트 재실행, 증적 갱신 |
| CR 승격 기준 | 요구사항, AC, 화면/프로그램/API/DB 설계, 보안 기준 변경이 필요한 경우 CR로 승격 |
| 이번 QA 판단 |  |

## 6. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 |  | 최초 작성 |  |  |  |
