# 화면설계서

```yaml
---
document_id: DOC-CORE-G2-003
title: Screen Specification
title_ko: 화면설계서
project: 프로젝트명
gate: G2
status: Draft
version: v0.1
owner_role: UX/UI Designer
author: 작성자 또는 에이전트
reviewer: Requirements Lead
approver: Approver
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
related_ids:
  - SCR-001
change_reason: 최초 초안 작성
---
```

## 1. 문서 목적

본 문서는 화면, 페이지, 팝업, 다이얼로그, 보고서 UI의 구성과 동작을 정의한다.

화면설계서는 기능명세서와 프로그램명세서를 연결하며, 입력값 검증, 권한, 보안항목, 테스트 기준을 화면 관점에서 표현한다.

## 2. 작성 기준

- 화면은 `SCR-001` 형식으로 부여한다.
- 화면은 하나 이상의 `REQ`, `AC`, `FUNC`와 연결한다.
- 화면 입력/출력 항목은 프로젝트 단어사전 `TERM`과 연결한다.
- 화면 이벤트는 관련 프로그램 `PGM`과 연결한다.
- 보안 민감 화면은 `SEC`와 외부 보안 기준 `SR`을 함께 기록한다.
- 외부 시안, Figma 캡처, 이미지 생성 시안, 손그림, 기존 화면 캡처는 출처와 파일 경로를 기록하고 `SCR-ID`와 연결한다.
- 외부 시안이 없더라도 `Text Wireframe`, `HTML Mockup`, `Mermaid`, 이미지 중 하나 이상의 화면 구조 증적을 작성한다.
- `Text Wireframe`을 사용하는 경우 `UIREF-ID`별로 별도 절과 fenced code block을 작성한다. 단순 화면 구성 표만으로는 와이어프레임으로 보지 않는다.
- 구현 후 비교가 가능하도록 기준 viewport와 주요 비교 항목을 작성한다.

## 3. 화면 목록

| SCR-ID | 화면명 | 유형 | 관련 FUNC | 관련 PGM | 관련 SEC | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| SCR-001 |  | Page / Popup / Dialog / Report | FUNC- | PGM- | SEC- | Draft |

## 4. 화면 시안 및 기준 증적

| SCR-ID | 시안/와이어프레임 ID | 출처 | 파일/URL | 기준 Viewport | 비교 기준 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| SCR-001 | UIREF-001 | Figma / imagegen / 외부 이미지 / 손그림 / 기존 시스템 캡처 | docs/artifacts/02-design/screen/images/UIREF-001_example.png | Desktop 1280x720, Mobile 390x844 | 레이아웃, 입력항목, 메시지 위치, 버튼 상태 | Draft |

### 4.1 UIREF-001 Text Wireframe

`출처`가 `Text Wireframe`이면 아래처럼 실제 배치 기준을 작성한다.
외부 이미지나 HTML mockup을 사용하는 경우에는 파일/URL과 viewport, 비교 기준을 표에 명시한다.

```text
[Header: 서비스명 / 사용자 상태]

[Main]
  [Field: 입력항목]
  [Field: 입력항목]
  [Error Message Area]
  [Primary Button]

[Footer or Help Area]
```

## 5. 화면 상세

### SCR-001 화면명

| 항목 | 내용 |
| --- | --- |
| SCR-ID | SCR-001 |
| 화면명 |  |
| 화면 유형 | Page / Popup / Dialog / Report |
| 설명 |  |
| 관련 요구사항 | REQ- |
| 관련 인수기준 | AC- |
| 관련 기능 | FUNC- |
| 관련 프로그램 | PGM- |
| 관련 보안항목 | SEC- |
| 접근 권한 | 전체 / 로그인 사용자 / 특정 역할 |
| 기준 시안 | UIREF-001 |
| 기준 Viewport | Desktop 1280x720 / Mobile 390x844 |

#### 5.1 화면 상태

| 상태 ID | 상태명 | 발생 조건 | 표시/동작 | 관련 AC/SEC |
| --- | --- | --- | --- | --- |
| STATE-001 | 기본 상태 | 최초 진입 |  | AC- |
| STATE-002 | 오류 상태 | 입력값 오류 또는 처리 실패 |  | AC-/SEC- |
| STATE-003 | 빈 상태 | 표시할 데이터 없음 |  | AC- |
| STATE-004 | 권한 제한 상태 | 권한 없음 또는 비로그인 |  | SEC- |

#### 5.2 화면 구성

| 영역 | 구성요소 | 설명 | 표시 조건 | 비고 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

#### 5.3 입력 항목

| 순번 | TERM-ID | 화면 항목명 | API 필드명 | 필수 | 형식/도메인 | 검증 기준 | 관련 SEC/SR |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | TERM-001 |  |  | Y/N | DOMAIN- |  | SEC- / KISA-SD-2021 SR- |

#### 5.4 출력 항목

| 순번 | TERM-ID | 화면 항목명 | API 필드명 | 형식/도메인 | 표시 조건 | 보안 분류 |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | TERM-001 |  |  | DOMAIN- |  | 일반 |

#### 5.5 화면 이벤트

| 이벤트 ID | 이벤트 | 발생 조건 | 호출 프로그램 | 처리 결과 | 관련 AC/SEC |
| --- | --- | --- | --- | --- | --- |
| EVT-001 |  |  | PGM- |  | AC-/SEC- |

#### 5.6 권한 및 보안

| SEC-ID | 참조 표준 | 보안 고려사항 | 화면 적용 방식 | 검증 테스트 |
| --- | --- | --- | --- | --- |
| SEC-001 | KISA-SD-2021 SR- |  |  | UT-/IT- |

#### 5.7 오류/검증 메시지

| 메시지 ID | 발생 조건 | 메시지 | 표시 위치 | 관련 AC/SEC |
| --- | --- | --- | --- | --- |
| MSG-001 |  |  |  | AC-/SEC- |

#### 5.8 UI 테스트 및 증적 기준

| UI-ID | 대상 SCR | 사용자 흐름 | 기준 시안 | Viewport | 캡처 경로 | 비교 기준 | 관련 AC/SEC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UI-001 | SCR-001 |  | UIREF-001 | Desktop 1280x720 / Mobile 390x844 | docs/artifacts/04-review/evidence/ui/UI-001_desktop.png | 레이아웃, 메시지, 주요 상태 | AC-/SEC- |

#### 5.9 테스트 연결

| 테스트 ID | 테스트명 | 검증 내용 | 관련 AC/SEC/NREQ |
| --- | --- | --- | --- |
| IT-001 |  |  | AC- |

## 5. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | YYYY-MM-DD | 최초 초안 작성 |  |  |  |

## 6. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 모든 화면에 `SCR-ID`가 부여되었는가 |  |
| 화면이 `REQ`, `AC`, `FUNC`와 연결되었는가 |  |
| 화면 이벤트가 관련 `PGM`과 연결되었는가 |  |
| 입력/출력 항목이 프로젝트 단어사전과 연결되었는가 |  |
| 입력값 검증과 오류 메시지가 작성되었는가 |  |
| 보안 고려사항에 `SEC-ID`와 `SR-ID`가 연결되었는가 |  |
| 외부/생성 시안이 `SCR-ID`, 출처, 파일/URL, viewport와 연결되었는가 |  |
| 기본/오류/빈/권한 제한 상태가 필요한 경우 작성되었는가 |  |
| UI 테스트와 캡처 증적 기준이 작성되었는가 |  |
| 테스트 연결이 작성되었는가 |  |
