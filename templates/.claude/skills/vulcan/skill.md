---
name: vulcan
description: "Phase 0(Discovery)와 Gate 1~5 개발 프로세스를 오케스트레이션하는 스킬로, BA/SA/PM/Architect/DBA/QA/Frontend-dev/Backend-dev/UX-reviewer 에이전트 팀의 협업을 조율한다. Use when 사용자가 새 프로젝트를 시작하거나 '상위설계 시작', 'Discovery 시작', '프로젝트 시작'을 요청할 때. Use when '요구사항 정의', 'Gate 1 시작', 'Gate 2 시작', '설계 시작', '테스트 계획', '구현 시작', 'UX 리뷰', 'QA 리뷰', '최종 승인' 등 Phase 0 또는 Gate 진입을 요청할 때. Use when 'Gate 상태 확인', '다음 Gate로', '진행 상황' 등 프로세스 진행 상태를 묻거나 전환을 요청할 때. NOT for 프로젝트 초기화(vulcan.py init), session.json 직접 편집, 단순 코드 수정·리팩토링 요청, 단일 파일 디버깅."
---

# Vulcan — Phase 0 + 5-Gate 개발 프로세스 오케스트레이터

에이전트 팀을 조율하여 Phase 0(Discovery) + 5-Gate 프로세스에 따라 체계적으로 프로젝트를 개발한다.

## 에이전트 구성

### Phase 0 (Discovery) — 상위설계

| 에이전트 | 파일 | 역할 |
|---------|------|------|
| analyst | `.claude/agents/analyst.md` | 현행 시스템 분석, API 표면, 의존성 감사, 기술 부채 (고도화만) |
| ba | `.claude/agents/ba.md` | 법령/규정 분석, AS-IS/TO-BE 갭 분석, 요구사항 도출, 용어 정의 |
| sa | `.claude/agents/sa.md` | 인프라 설계, 기술 선택/대안 비교, 기술 검토서 |
| estimator | `.claude/agents/estimator.md` | IFPUG FP 산정, 공수/일정/인력 추정 |

### Gate 1~5 — 상세설계~개발

| 에이전트 | 파일 | 역할 |
|---------|------|------|
| concierge | `.claude/agents/concierge.md` | 온보딩, 프로젝트 개요 파악 |
| pm | `.claude/agents/pm.md` | 요구사항 수집, REQ-ID 체계화, AC 작성 |
| architect | `.claude/agents/architect.md` | 시스템 설계, API, 모듈 구조, UT-ID 할당 |
| ui-designer | `.claude/agents/ui-designer.md` | UI 설계, 와이어프레임, 디자인 토큰 |
| dba | `.claude/agents/dba.md` | 데이터 모델링, ERD, 마이그레이션 |
| frontend-dev | `.claude/agents/frontend-dev.md` | 프론트엔드 구현, UI 컴포넌트, API 연동 |
| backend-dev | `.claude/agents/backend-dev.md` | 백엔드 구현, API, DB 연동, 인증 |
| ux-reviewer | `.claude/agents/ux-reviewer.md` | UI 검수, 스크린샷 분석, 접근성 검증 |
| qa | `.claude/agents/qa.md` | 테스트 계획, 코드 리뷰, 판정 |

## 워크플로우

### Phase 0: Discovery (상위설계)

> **Phase 0은 Gate 규약이 적용되지 않는다.** rules, check-trace, session.json 없이 자유롭게 반복한다.

"상위설계 시작", "Discovery 시작", "법령 분석해줘", "인프라 설계해줘", "FP 산정해줘" 등의 요청 시:

1. `docs/00-discovery/` 폴더 존재 여부를 확인한다
2. 사용자 요청에 따라 해당 에이전트를 투입한다:
   - 현행 시스템 분석/코드 분석 관련 → `Agent(analyst)` (고도화 프로젝트)
   - 요구사항/법령/기능 관련 → `Agent(ba)`
   - 인프라/기술 선택 관련 → `Agent(sa)`
   - FP/공수 산정 관련 → `Agent(estimator)`
3. 에이전트는 `docs/00-discovery/` 하위에 산출물을 작성한다
4. 문서 변경 시 새 버전 파일(vN+1)로 작성하고 `CHANGELOG.md`에 기록한다
5. **사용자가 반복을 원하면 자유롭게 반복한다** — 승인 절차 없음

### Phase 0 → Gate 1 전환

사용자가 "Gate 1 시작", "상위설계 끝", "Discovery 완료" 등을 요청하면:

1. `docs/00-discovery/DISCOVERY-CHECKLIST.md`의 필수 항목을 검토한다
2. 미충족 항목이 있으면 사용자에게 보고한다
3. 사용자 승인 후, `Agent(pm)`을 투입하여 Phase 0 산출물을 REQ-NNN/AC-NNN 형식으로 변환한다
4. 이후 기존 Gate 1~5 프로세스를 따른다

### Phase 1: 준비 (오케스트레이터 직접 수행)

1. `session.json`을 읽어 현재 Gate를 확인한다
2. 사용자 요청에서 작업 범위를 파악한다:
   - Phase 0 관련 요청 → Phase 0 에이전트 투입 (위 참조)
   - 특정 Gate 시작 요청 → 해당 Gate 에이전트 투입
   - "프로젝트 시작", 자연어 요청 → **Concierge 온보딩 후** Gate 1 진행
   - "상태 확인" → 현재 Gate 상태 보고
3. 온보딩 필요 여부 판단:
   - gate1이 pending + 사용자가 구체적 Gate를 지정하지 않음 → `Agent(concierge)` 투입
   - 명시적 Gate 지정 또는 이미 진행 중인 프로젝트 → concierge 스킵

### Phase 1.5: 온보딩 (Concierge → PM 연계)

"프로젝트 시작" 또는 자연어 요청 시:
1. `Agent(concierge)` 투입 — 사용자와 대화로 프로젝트 개요 수집
2. Concierge가 **프로젝트 온보딩 요약**을 반환
3. 오케스트레이터가 온보딩 요약을 컨텍스트에 포함하여 `Agent(pm)` 투입

### Phase 2: Gate별 팀 구성 및 실행

> 산출물 경로는 CLAUDE.md의 "Gate 산출물" 테이블 참조.

| Gate | 담당 | 비고 |
|------|------|------|
| Gate 1 | pm | |
| Gate 2a | architect | Gate 2a/2b 병렬 |
| Gate 2b | dba | DB 있는 프로젝트만 |
| Gate 2c | ui-designer | 2a 완료 후 |
| Gate 3 | qa | |
| 구현 | frontend-dev + backend-dev | |
| UI 검수 | ux-reviewer | |
| Gate 4 | qa | |
| Gate 5 | 사용자 | |

### 작업 분할 전략 (컨텍스트 보호)

> **⚠️ 서브에이전트에 한 번에 모든 REQ를 주지 않는다.**

오케���트레이터가 REQ 그룹별 복잡도를 평가하여 청크 단위로 나눠 투입한다:

| REQ 그룹 복잡도 | 기준 | 청크 크기 |
|---------------|------|----------|
| 경량 | 상세 REQ 1~3개, API 1~2개 | 3~4개 그룹 묶음 |
| 보통 | 상세 REQ 4~6개, API 3~5개 | 2개 그룹 묶음 |
| 복잡 | 상세 REQ 7개+, API 6개+ | 1개 그룹 단독 |

REQ 그룹 1~2개면 분할 없이 한 번에 투입한다.

**서브에이전트 투입 시 프롬프트 규칙:**
- 해당 청크의 REQ 범위를 명시한다
- 참조할 **문서 경로만** 알려준다 (설계 내용을 프롬프트에 옮기지 않는다)
- 범위 밖 REQ는 언급하지 않는다

### Phase 3: 산출물 검증 및 Gate 전환

> **⛔ 반드시 step 6까지 완료해야 한다.**

1. 모든 에이전트/청크 완료 시 산출물 파일 존재 및 내용을 검증한다
   - 산출물 누락 또는 빈 파일 → 해당 에이전트 재투입
2. 사용자에게 보고: 산출물 목록 + 요약 + "Gate N으로 진행할까요?"
3. **⛔ 사용자의 명시적 승인을 기다린다** — 승인 없이 다음 Gate 진행 금지
4. 승인 후 `python vulcan.py check-trace` 직접 실행
5. 이슈 0건 확인 시 `python vulcan.py session --gate gateN --status done --feature "기능명"` 직접 실행
6. session 명령 완료 후 다음 Gate 진행

### Gate 전환 조건

| Gate | 완료 조건 |
|------|----------|
| Gate 1 | 모든 REQ-NNN-NN에 AC-NNN-NN 존재 |
| Gate 2 | 모든 REQ 그룹에 Design.md 존재 |
| Gate 3 | 모든 REQ-NNN-NN이 Test-Plan.md에 TST-ID 매핑 |
| Gate 4 | 모든 REQ 그룹에 Review.md 존재 + Blocker 전원 Pass |
| Gate 5 | 사용자 최종 확인 |

### 긴급 절차 (Hotfix)

1. REQUIREMENTS.md에 최소 요구사항 작성
2. 설계 문서는 생략 가능 (사용자 명시적 허용 시)
3. **Gate 4 QA 리뷰는 절대 생략 불가**

### 롤백

사용자가 "요구사항 추가", "Gate N부터 다시", "롤백" 요청 시:
1. `python vulcan.py rollback --gate gateN --reason "사유"` 직접 실행
2. 해당 Gate 에이전트 즉시 투입 (롤백 요청 = 승인)

## Gate별 실행 모드

| 사용자 요청 | 투입 에이전트 |
|-----------|-------------|
| "상위설계 시작", "Discovery 시작" | analyst, ba, sa, estimator (요청에 따라) |
| "프로젝트 시작", 자연어 요청 | concierge → pm |
| "Gate 1 시작", "요구사항 정의" | pm |
| "Gate 2 시작", "설계 시작" | architect + dba (병렬) → ui-designer |
| "Gate 3 시작", "테스트 계획" | qa |
| "구현 시작", "코딩 시작" | frontend-dev + backend-dev |
| "UI 검수", "UX 리뷰" | ux-reviewer |
| "Gate 4 시작", "리뷰 시작" | qa |
| "상태 확인" | (오케스트레이터 직접) |
| "롤백해줘" | (오케스트레이터 직접) |

## 에스컬레이션 프로토콜

다음 상황에서는 즉시 사용자에게 보고한다:

| 트리거 | 이유 |
|--------|------|
| 요구사항 범위 변경 | 설계/테스트 재작업 필요 |
| QA 2회 연속 Fail | 설계 수준 문제 가능성 |
| 설계에 없는 외부 서비스 필요 | 아키텍처 변경 |
| 보안 취약점 발견 | 즉시 대응 |
| 병렬 인스턴스 간 파일 충돌 | 실행 순서 재조정 |

보고 형식: "에스컬레이션: [트리거] — [현재 상황] — [선택지 1 / 선택��� 2]"

## 에러 핸들링

| 에러 유형 | 전략 |
|----------|------|
| session.json 없음 | "vulcan.py init을 먼저 실행하세요" 안내 |
| Gate 순서 이탈 | 현재 Gate 안내, 순서대로 진행 유도 |
| 에이전트 실패 | 1회 재시도 → 실패 시 사용자 보고 |
| ��출물 누락 | check-trace 실행 → 누락 식별 |
| 산출물 품질 저하 | 청크를 더 작게 쪼개서 재투입 |

## 확장 스킬

| 스킬 | 대상 | 역할 |
|------|------|------|
| `security-baseline` | qa, architect | OWASP Top 10 체크리스트 |
