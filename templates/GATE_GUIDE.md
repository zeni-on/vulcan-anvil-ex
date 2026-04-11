# Vulcan-Claude 프로세스 가이드

## 개요

Vulcan-Claude는 **Phase 0(Discovery) + 5-Gate** 프로세스를 통해 AI 에이전트와 사람이 협업하여 프로젝트를 개발합니다.

- **Phase 0**: 탐색적 상위설계. Gate 규약 없이 자유롭게 반복하며 요구사항, 아키텍처, FP를 도출한다.
- **Gate 1~5**: 각 Gate는 산출물 작성 → 사용자 승인 → 정합성 검증 → 상태 전환의 순서로 진행된다.

## 전체 흐름도

```
[Phase 0] → 체크리스트 승인 → [Gate 1] → 승인 → [Gate 2] → 승인 → [Gate 3] → 승인 → [구현] → [Gate 4] → 승인 → [Gate 5]
 Discovery                    요구사항         설계            테스트계획        코딩       QA리뷰         최종승인
 @BA, @SA, @Estimator          @PM          @Architect       @QA        @Frontend-dev   @QA          Human
                                             @DBA(선택)                  @Backend-dev
```

---

## Phase 0: Discovery (상위설계)

**담당**: BA + SA + Estimator 에이전트
**성격**: 탐색적, 반복적. **Gate 규약/rules/skills/check-trace 없음.**

### Phase 0과 Gate 1~5의 차이

| | Phase 0 (Discovery) | Gate 1~5 |
|---|---|---|
| 규약 | 없음 (자유 반복) | 엄격한 Gate 승인 |
| 문서 버전 | 파일 버전 관리 (v1→v2→...) | Gate별 확정 |
| 에이전트 | BA, SA, Estimator | PM, Architect, DBA, ... |
| 완료 기준 | DISCOVERY-CHECKLIST | check-trace |
| 코드 작성 | 금지 | 구현 단계에서 허용 |

### 에이전트 역할

| 에이전트 | 역할 | 산출물 |
|---------|------|--------|
| **Analyst** (System Analyst) | 현행 시스템 분석, API 표면, 의존성 감사, 기술 부채 식별 | audit/ (고도화 프로젝트만) |
| **BA** (Business Analyst) | 법령/규정 분석, AS-IS/TO-BE 갭 분석, 요구사항 도출, 용어 정의 | glossary, requirements, functional-detail |
| **SA** (Solution Architect) | 인프라 설계, 기술 선택/대안 비교, 기술 검토서 | infrastructure, technical-review |
| **Estimator** | IFPUG FP 산정, 공수/일정/인력 추정 | fp-estimation |

### SA와 Gate 2 Architect(TA)의 관계

| | SA (Phase 0) | Architect/TA (Gate 2) |
|---|---|---|
| 질문 | "무엇을/왜 선택?" | "어떻게 만들까?" |
| 산출물 | 인프라 설계, 기술 검토서 | API 스펙, 모듈 구조, UT-ID |
| 결정 수준 | Zone 구성, 기술 선택 | 엔드포인트, 시그니처, 의존성 |

SA의 결정이 TA의 입력이 된다.

### 산출물 구조

```
docs/00-discovery/
├── DISCOVERY-CHECKLIST.md          # 완료 기준
├── CHANGELOG.md                    # 전체 변경 이력
├── glossary/glossary.md            # 용어집 (누적 갱신)
├── requirements/                   # 상위 요구사항 (버전별)
│   ├── requirements-v1.md
│   └── requirements-v2.md
├── functional/                     # 기능 상세 (버전별)
│   └── functional-detail-v1.md
├── infrastructure/                 # 인프라 설계 (버전별)
│   └── infrastructure-v1.md
├── technical-review/               # 기술 검토 (주제별)
│   └── [주제]-review.md
├── estimation/                     # FP 산정 (버전별)
│   └── fp-estimation-v1.md
├── audit/                          # 현행 시스템 분석 (고도화 프로젝트만)
│   ├── codebase-analysis.md
│   ├── api-surface.md
│   ├── dependency-audit.md
│   └── migration-strategy-vN.md
└── references/                     # 법령, 가이드라인 등
```

### 작업 흐름

**신규 개발:**
1. **BA**: 법령/규정 분석 → 용어 정의 → 상위 요구사항 초안 → 기능 상세
2. **SA**: 요구사항 기반 인프라 설계 → 기술 검토 → 보안 아키텍처
3. **Estimator**: 기능 상세 + 기술 검토 결과 → FP 산정 → 공수/일정 추정
4. **반복**: 요구사항 변경 → 인프라 재설계 → FP 재산정 (자유롭게 반복)
5. **완료 판단**: DISCOVERY-CHECKLIST 필수 항목 충족 → 사용자 승인

**고도화 프로젝트:**
1. **Analyst**: 현행 코드/API/의존성 분석 → BA·SA에 입력 제공
2. **BA**: Analyst 결과 + 법령/규정 → AS-IS/TO-BE 갭 분석 → 요구사항
3. **SA**: Analyst 결과 + 요구사항 → 기술 선택, 마이그레이션 전략
4. **Estimator**: 변경 영향 범위 기반 FP 산정
5. **반복 + 완료 판단**: 위와 동일

### Phase 0 → Gate 1 전환

1. `DISCOVERY-CHECKLIST.md`의 필수 항목을 검토한다
2. 사용자의 승인을 받는다
3. Phase 0의 상위 요구사항을 Gate 1의 REQ-NNN/AC-NNN 형식으로 변환한다
   - PM 에이전트가 `docs/00-discovery/requirements/` 최신 버전을 읽고 정규화
4. 이후 Gate 1~5 프로세스를 따른다

---

## Gate 1: 요구사항 정의

**담당**: PM 에이전트
**산출물**: `docs/01-requirements/REQUIREMENTS.md`

### 수행 내용
1. 비전 질문 (배경, 대상, 가치, 성공기준)
2. 요구사항 구조화 (REQ-NNN / REQ-NNN-NN)
3. 인수 기준 작성 (AC-NNN-NN)
4. 기술 스택 협의

### 완료 조건
- 모든 REQ-NNN-NN에 AC-NNN-NN이 정의됨
- `python vulcan.py check-trace` 이슈 0건

### 전환 명령
```bash
python vulcan.py check-trace
python vulcan.py session --gate gate1 --status done --feature "기능명"
```

## Gate 2: 설계

**담당**: Architect + DBA(DB 있을 때) + UI-Designer 에이전트
**산출물**: `docs/02-design/REQ-NNN-Design.md`, `docs/02-design/REQ-NNN-Data-Design.md`, `docs/02-design/UI-Design.md`

### 수행 내용
1. 시스템 아키텍처 설계
2. API 설계 (엔드포인트, 스키마)
3. 디렉토리 구조 정의
4. 테스트 ID 사전 할당 (TST-ID)
5. 보안 고려사항 식별 (SEC-ID)
6. 데이터 모델링 (DBA — ERD, 스키마, 마이그레이션)
7. UI 설계 (UI-Designer — 와이어프레임, 디자인 토큰, 컴포넌트 명세)

### 완료 조건
- 모든 REQ 그룹에 Design.md 존재
- `python vulcan.py check-trace` 이슈 0건

## Gate 3: 테스트 계획

**담당**: QA 에이전트
**산출물**: `docs/03-test-plan/Test-Plan.md`

### 수행 내용
1. 테스트 전략 수립 (Unit, Integration, E2E)
2. TST-ID ↔ REQ-ID 매핑 확인
3. 테스트 케이스 작성
4. 커버리지 목표 설정

### 완료 조건
- 모든 REQ-NNN-NN이 Test-Plan.md에 매핑됨
- `python vulcan.py check-trace` 이슈 0건

## 구현 (Gate 3과 Gate 4 사이)

**담당**: Frontend-dev + Backend-dev 에이전트 (REQ 그룹별 다단계 병렬 실행)

### 병렬 실행 전략

오케스트레이터가 구현 시작 시 REQ 그룹 간 의존성을 분석하여 실행 순서를 결정한다.

```
[Wave 1 - 독립적인 REQ 그룹 병렬]
  REQ-001: frontend-dev #1 || backend-dev #1
  REQ-002: frontend-dev #2 || backend-dev #2

[Wave 2 - 의존성 있는 REQ 그룹, 선행 완료 후]
  REQ-003 (REQ-001 의존): frontend-dev #3 || backend-dev #3
```

**병렬 실행 조건:**
- 동일 DB 테이블 변경이 없을 것
- REQ 그룹 간 API 호출 의존이 없을 것
- 공유 컴포넌트/모듈 충돌이 없을 것

### 수행 내용

**Frontend-dev (각 인스턴스):**
1. 프론트엔드 프로젝트 초기화, UI 컴포넌트 개발
2. 페이지/라우팅 구현, 상태관리 설정
3. API 연동 (백엔드 미완성 시 목업 데이터로 우선 개발)
4. 프론트엔드 단위 테스트 작성 (TST-ID 기반)

**Backend-dev (각 인스턴스):**
1. 백엔드 프로젝트 초기화, API 엔드포인트 구현
2. 비즈니스 로직, DB 연동, 인증/인가 구현
3. DB 마이그레이션 적용
4. 백엔드 단위 테스트 작성 (TST-ID 기반)

**공통:**
- ENVIRONMENT.md를 실제 명령어로 업데이트
- commenting-standards.md 준수
- 같은 REQ 그룹 내 Frontend-dev ↔ Backend-dev 간 API 스펙 실시간 소통

### 주의사항
- 설계 범위 밖의 판단은 하지 않는다 — 보고한다
- 설계에 없는 외부 라이브러리가 필요하면 에스컬레이션
- 병렬 인스턴스 간 파일 충돌 주의 — 공유 파일 수정 시 오케스트레이터에게 보고

## Gate 4: QA 리뷰

**담당**: QA 에이전트
**산출물**: `docs/04-review/REQ-NNN-Review.md`

### 수행 내용
1. 6개 항목 평가 (A~F)
2. Blocker 항목 (A~D): 1개라도 Fail → 전체 Fail
3. Improvement 항목 (E~F): 개선 권고
4. 테스트 실행 및 결과 기록

### Blocker 항목
| 항목 | 기준 |
|------|------|
| A. 요구사항 충족 | 모든 REQ-NNN-NN 구현 여부 |
| B. 설계 준수 | 아키텍처/API 설계 준수 여부 |
| C. 테스트 결과 | 단위 테스트 전원 통과 |
| D. 보안 점검 | SEC-ID 대응 구현 여부 |

### Fail 시 재작업
1. QA가 해당 Developer(Frontend-dev/Backend-dev)에게 🔴 필수 수정 사항 전달
2. 해당 Developer 수정 후 재제출
3. QA 재검증 (최대 2회)
4. 2회 실패 시 에스컬레이션

## Gate 5: 최종 승인

**담당**: 사용자 (Human)

### 수행 내용
1. docs/04-review/ 의 모든 리뷰 보고서 확인
2. (선택) 코드 직접 검토
3. 최종 승인

### 전환 명령
```bash
python vulcan.py session --gate gate5 --status done --feature "기능명"
```

## Backlog (Gate 5 이후 지속 반복)

**담당**: PM (Triage) + QA (Gate 4 Blocker 방어) + 사용자 (우선순위 결정)
**산출물**: `docs/06-backlog/BACKLOG.md`, `docs/06-backlog/PROCESS.md`
**설계 근거**: `vulcan-anvil/docs/reference/BACKLOG-AND-INCREMENTAL-GATE.md`

Gate 5는 선을 긋지만 소프트웨어는 "완성"되지 않는다. Gate 5 이후 발생하는 새 요구사항, 기술부채, 개선 아이디어는 백로그로 관리되며, 항목의 성격에 따라 **증분 Gate Rollback**으로 해당 Gate에 재진입한다.

### Triage Level → Gate 재진입 경로

| 레벨 | 기준 | 처리 |
|------|------|------|
| 🟢 Trivial | **어떤 문서도 수정할 필요 없음** | 바로 구현 → 커밋 |
| 🟡 Small | 단일 REQ 범위, 설계 일부 갱신 | `rollback --gate gate2 --scope REQ-XXX` |
| 🔴 Major | 새 기능, 새 REQ, 아키텍처 영향 | `rollback --gate gate1 --scope REQ-YYY` |

**Trivial 판정 체크리스트** (하나라도 해당되면 🟢이 아니다):
- 입력 검증/거부 정책 추가? → 🟡
- API 응답 형식 변경? → 🟡
- 새 테이블/컬럼? → 🟡
- 인증/권한 범위 변경? → 🟡
- 새 외부 의존성? → 🔴

### 증분 Gate Rollback

`--scope` 옵션을 사용하면 session.json에 `rollback_scope`가 기록되고, 이후 `check-trace`는 scope 내 REQ-ID만 재검증 대상으로 삼는다. 기존 문서/코드는 보존된다.

```bash
# 🟡 Small 예시: REQ-003 페이지네이션 정식 구현
python vulcan.py rollback --gate gate2 --scope REQ-003 --reason "BL-003"
# → Gate 2, 3, 4가 pending으로 리셋되지만 REQ-003만 재검증 대상
# → 다른 REQ는 이미 통과로 간주

# 🔴 Major 예시: NREQ-005/006 Google Drive 동기화 (새 NREQ)
python vulcan.py rollback --gate gate1 --scope NREQ-005,NREQ-006 --reason "BL-001"
```

### Gate 4 Blocker 방어 규칙

Gate 4 QA 리뷰에서 Blocker(A~D Fail) 또는 Major 이슈를 발견하면 **백로그 이월은 금지**된다. 반드시 현 Gate 내에서 Developer에게 재작업 요청. Minor/Suggestion 이슈만 백로그 이월 허용. 자세한 내용은 `docs/06-backlog/PROCESS.md` §6 참조.

### 백로그 명령어

```bash
python vulcan.py backlog list                                   # Active 항목 나열
python vulcan.py backlog add --title "차트 zoom" --priority P2   # 새 항목 추가 (ID 자동 할당)
python vulcan.py backlog done --id BL-003 --commit <hash>        # 완료 처리
python vulcan.py backlog reject --id BL-002 --reason "상위 흡수"  # 반려
```

## 에스컬레이션

다음 상황에서는 즉시 사용자에게 보고합니다:

1. **요구사항 범위 변경** — 설계/테스트 재작업 필요
2. **QA 2회 연속 Fail** — 설계 수준 문제 가능성
3. **설계에 없는 외부 서비스/라이브러리 필요** — 아키텍처 변경
4. **Breaking 스키마 변경** — 마이그레이션 전략 승인 필요
5. **보안 취약점 발견** — 즉시 대응

## 긴급 절차 (Hotfix)

1. REQUIREMENTS.md에 최소 요구사항 작성 (1~3줄)
2. 설계 문서 생략 가능 (사용자 허용 시)
3. **Gate 4 QA 리뷰는 절대 생략 불가**

## 변경 관리

요구사항 추가/수정/삭제 시 문서 수정 순서.

### 신규 REQ 추가

```
REQUIREMENTS.md (REQ + AC 추가)
  → TRACEABILITY.md (행 추가)
  → REQ-NNN-Design.md (설계)
  → TRACEABILITY.md (설계 컬럼)
  → Test-Plan.md (TST-ID 추가)
  → TRACEABILITY.md (테스트 컬럼)
  → 소스 코드 (구현)
  → REQ-NNN-Review.md (리뷰)
  → TRACEABILITY.md (리뷰 컬럼 + 상태 → 구현완료)
```

### 기존 REQ 수정

1. REQUIREMENTS.md에서 해당 REQ 수정, 상태 → `수정예정`
2. TRACEABILITY.md 상태 → `수정예정`
3. `REQ-NNN-Design-vN.md` 새 버전 파일로 변경분 작성 (기존 파일 보존)
4. Test-Plan.md에서 해당 TST-ID를 현재 요구사항 기준으로 덮어쓰기
5. 구현 → 리뷰 → TRACEABILITY 업데이트

### REQ 삭제

1. REQUIREMENTS.md에서 상태 → `삭제됨` (행 유지, 번호 재사용 금지)
2. TRACEABILITY.md 상태 → `삭제됨`
3. Test-Plan.md에서 해당 TST-ID 제거
4. 소스 코드에서 관련 코드 제거
5. 설계/리뷰 문서는 삭제하지 않고 보존 (히스토리)
