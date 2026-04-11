# 백로그 운영 프로세스

> 본 문서는 Gate 5 완료 이후 프로젝트의 지속적 개선을 위한 백로그 관리 규칙을 정의한다.
> 설계 근거: `vulcan-anvil/docs/reference/BACKLOG-AND-INCREMENTAL-GATE.md`

## 1. 백로그란

- **정의**: Gate 5 완료 이후 발생하는 작업 큐 (미구현 요구사항, 기술부채, 개선 아이디어)
- **출처**: 사용자 피드백, QA 지적, 새 요구사항, 기술 리뷰, 보안 감사, 구현 중 발견된 deprecation/취약점
- **위치**: [`docs/06-backlog/BACKLOG.md`](BACKLOG.md)

## 2. TRACEABILITY.md vs BACKLOG.md

| 문서 | 역할 | 포함 대상 |
|------|------|----------|
| **TRACEABILITY.md** | 요구사항 전체 상태표 (정적) | 모든 REQ/NREQ의 상태 (구현완료/미구현/삭제됨) |
| **BACKLOG.md** | 작업 큐 (동적) | "할 계획이 있는" 항목만 + 기술부채 + 보안 개선 |

**원칙**: 백로그는 TRACEABILITY의 부분집합 + α (TRACEABILITY에 없는 기술부채 포함)

## 3. 항목 분류 (Triage Level)

새 항목은 다음 세 레벨 중 하나로 분류한다.

| 레벨 | 기준 | 처리 방식 |
|------|------|-----------|
| **🟢 Trivial** | **어떤 문서(REQUIREMENTS / Design / Test-Plan / Security baseline)도 수정할 필요 없음** | 바로 구현 → 커밋 (Gate rollback 불필요) |
| **🟡 Small** | 단일 REQ 범위, 기존 설계 일부 갱신 필요 | **Gate 2 부분 rollback** (scope: 영향 REQ-ID) → 설계 갱신 → 구현 → Gate 4 |
| **🔴 Major** | 새 기능, 새 REQ, 아키텍처 영향 | **Gate 1 부분 rollback** (scope: 신규 REQ-ID) → 요구사항 추가 → 해당 REQ만 Gate 1~5 재진행 |

**Trivial 판정 체크리스트** (하나라도 해당되면 🟢이 아니다):
- [ ] 입력 검증/거부 정책 추가? → 🟡 (설계 문서에 정책 명시 필요)
- [ ] API 응답 형식 변경? → 🟡 (API 계약 설계 영향)
- [ ] 새 테이블/컬럼? → 🟡 (Data-Design 영향)
- [ ] 인증/권한 범위 변경? → 🟡 (Security baseline 영향)
- [ ] UI 플로우 변경? → 🟡 (UI-Design 영향)
- [ ] 새 외부 의존성/서비스? → 🔴 (아키텍처 영향)

**예시**:
- 🟢 `datetime.utcnow()` deprecation 치환, 로그 포맷 문자열 개선, 번들 code-split(config 수정)
- 🟡 페이지네이션 정식 구현, 입력 화이트리스트 추가, 세율 해시 검증
- 🔴 외부 서비스 연동(Google Drive/OAuth), 새 대시보드 위젯, 인증 시스템 도입

## 4. 우선순위 (Priority)

| 레벨 | 기준 |
|------|------|
| **P0** | 보안 취약점, 데이터 손실 리스크, 프로덕션 장애 — 즉시 |
| **P1** | Must 요구사항 미충족, 주요 기능 결함 — 다음 배치 |
| **P2** | Should 요구사항, 기술 부채, 성능 개선 — 여유 있을 때 |
| **P3** | Could 요구사항, 아이디어, Parking Lot — 무기한 |

## 5. 상태 Lifecycle

```
Proposed → Triaged → Scheduled → In Progress → Done
                                              ↘ Rejected
```

| 상태 | 의미 |
|------|------|
| **Proposed** | 아이디어 접수, 미평가 |
| **Triaged** | 레벨(🟢/🟡/🔴) + 우선순위(P0~P3) 결정 |
| **Scheduled** | 착수 예정 (다음 세션에서 할 것) |
| **In Progress** | 작업 중 (Gate 프로세스 진입 여부 결정됨) |
| **Done** | 완료 (커밋 해시 + 완료일 기록) |
| **Rejected** | 반려 (사유 기록) — 상위 항목에 흡수된 경우도 여기 |

## 6. Gate 4 Blocker/Major는 백로그 이월 금지

백로그가 **"Gate 4 타협의 핑계"**가 되는 것을 방지하는 핵심 규칙.

| Gate 4 이슈 등급 | 백로그 이월 가능? |
|----------------|------------------|
| 🚨 Blocker (A~D 중 Fail) | **불가** — 반드시 현 Gate 내에서 해결 |
| 🔴 Major | **불가** — 반드시 현 Gate 내에서 해결 |
| 🟡 Minor | 가능 — P0/P1로 승격 시 반드시 다음 배치에서 처리 |
| 🟢 Suggestion | 가능 — P2/P3 허용 |

**책임**: QA 에이전트는 Gate 4 리뷰에서 Blocker/Major를 발견하면 "백로그로 넘기자"는 판단을 해서는 안 된다. 반드시 Developer에게 재작업 요청.

## 7. 중복/흡수 규칙

백로그 항목이 다른 항목의 **선행/종속** 관계에 있으면 독립 항목으로 분리하지 않고 상위 항목에 흡수한다.

**판정 기준**:
- 항목 A가 항목 B의 "선행 필요"이면 → A를 B의 AC로 흡수, B를 Rejected 처리
- 항목 A와 B가 동일 REQ 그룹이고 Gate rollback 경로가 같으면 → 하나로 병합

**이유**: Backlog 항목 단위는 **PR 단위가 아니라 Gate 재진입 단위**다.

## 8. 세션 중 사용 흐름

### 8.1 백로그 조회
```
사용자: "백로그 확인" / "백로그 뭐 있어?"
Claude: BACKLOG.md의 Active 항목을 P0~P3 순으로 요약 출력
       → `python vulcan.py backlog list` 실행
```

### 8.2 항목 추가
```
사용자: "이거 백로그에 추가해줘: 차트 zoom 기능"
Claude:
  1. `python vulcan.py backlog add --title "차트 zoom 기능"` 실행 (ID 자동 할당)
  2. Triage 체크리스트(§3)로 레벨 제안
  3. 사용자 확인 → BACKLOG.md 상태 → Triaged
```

### 8.3 작업 착수
```
사용자: "백로그 BL-003 시작해줘"
Claude:
  1. 레벨 확인
  2. 🟢: 바로 구현 → 커밋
  3. 🟡: "Gate 2로 부분 rollback합니다 (scope: REQ-XXX). 진행할까요?"
         → `vulcan.py rollback --gate gate2 --scope REQ-XXX --reason "BL-003"`
  4. 🔴: "Gate 1로 부분 rollback합니다 (scope: REQ-YYY 신규). 진행할까요?"
         → `vulcan.py rollback --gate gate1 --scope REQ-YYY --reason "BL-003"`
```

### 8.4 완료 처리
```
구현 완료 후:
  1. `python vulcan.py backlog done --id BL-XXX --commit <hash>` 실행
  2. REQ 변경이 있었다면 TRACEABILITY.md 동기화
  3. session.json 갱신 (rollback_scope 해제)
```

## 9. 증분(Scoped) Gate Rollback

백로그 항목이 🟡/🔴인 경우 Gate를 되돌릴 때, **영향받는 REQ-ID 범위만** 재진행한다. 전체 Gate를 재돌릴 필요 없음.

### 🟡 Small → Gate 2 부분 Rollback
```bash
python3 vulcan.py rollback --gate gate2 --scope REQ-003 --reason "BL-003 페이지네이션 정식 구현"
# → session.json의 rollback_scope = {"gate": "gate2", "req_ids": ["REQ-003"]}
# → Gate 2, 3, 4가 pending으로 리셋되지만, check-trace는 REQ-003만 재검증 대상
# → 다른 REQ는 이미 통과된 것으로 간주
# → 다시 Gate 2 → 3 → 4 → 5 순서로 closeout (scope 내에서만)
```

### 🔴 Major → Gate 1 부분 Rollback
```bash
python3 vulcan.py rollback --gate gate1 --scope NREQ-005,NREQ-006 --reason "BL-001 Google Drive 동기화"
# → 모든 Gate pending, 하지만 scope 내 REQ만 검증
# → 요구사항 추가부터 Gate 1~5 재진행 (신규 REQ만)
```

**주의**:
- Rollback은 session.json 상태만 리셋하며, 기존 문서/코드는 보존된다.
- `--scope` 생략 시 **기존 동작(전체 rollback)** 호환 유지.
- `rollback_scope`가 있는 동안 check-trace는 scope 밖의 REQ를 "이미 통과"로 간주한다.

## 10. 회고/정리 주기

- **매 세션 종료 시**: 새 이슈/아이디어를 Proposed로 추가
- **주기적 Triage** (월 1회): Proposed 일괄 평가, Parking Lot(P3) 재검토
- **분기 정리**: Done 항목 아카이브 (BACKLOG.md의 Archived 섹션 또는 별도 파일)

## 11. ID 체계

- **BL-NNN**: 백로그 항목 ID (일련번호, 001부터, 재사용 금지)
- 백로그가 REQ/NREQ와 연관되면 `관련 REQ` 컬럼에 기록

## 12. 책임

- **사용자**: 우선순위 결정, 승인, 신규 아이디어 제안, Gate 4 Blocker 이월 거부권
- **QA 에이전트**: Gate 4에서 Blocker/Major 이슈 백로그 이월 금지
- **PM 에이전트**: 백로그 Triage 제안, 중복/흡수 판정, TRACEABILITY 동기화
- **Claude (오케스트레이터)**: `vulcan.py backlog` / `rollback --scope` 실행, 상태 갱신
