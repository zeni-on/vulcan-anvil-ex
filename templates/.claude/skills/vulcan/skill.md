---
name: vulcan
description: "Phase 0(Discovery)와 Gate 1~5 개발 프로세스를 오케스트레이션하는 스킬로, discovery/requirements/design/screen-design/security-review/test-design/build-planning/build-frontend/build-backend/evidence/review 에이전트 팀의 협업을 조율한다. Use when 사용자가 새 프로젝트를 시작하거나 '상위설계 시작', 'Discovery 시작', '프로젝트 시작'을 요청할 때. Use when '요구사항 정의', 'Gate 1 시작', 'Gate 2 시작', '설계 시작', '테스트 계획', '구현 시작', 'UI 증적', 'QA 리뷰', '최종 승인' 등 Phase 0 또는 Gate 진입을 요청할 때. Use when 'Gate 상태 확인', '다음 Gate로', '진행 상황' 등 프로세스 진행 상태를 묻거나 전환을 요청할 때. NOT for 프로젝트 초기화(vulcan.py init), session.json 직접 편집, 단순 코드 수정·리팩토링 요청, 단일 파일 디버깅."
---

# Vulcan — Phase 0 + 5-Gate 개발 프로세스 오케스트레이터

에이전트 팀을 조율하여 Phase 0(Discovery) + 5-Gate 프로세스에 따라 체계적으로 프로젝트를 개발한다.

## Ex Persona 원칙

Vulcan-Anvil Ex에서 표준 역할은 `.claude/agents/*.md` 파일명이 아니라 `docs/core/AGENT_PERSONAS.md`의 persona다.

Claude adapter는 기존 agent 파일명을 호환용으로 유지한다. 오케스트레이터는 먼저 persona를 판단한 뒤 `docs/adapters/claude/PERSONA_MAPPING.md`에 따라 Claude agent를 선택한다.

매핑 (파일명 = persona명, 1:1):

| Ex persona | Claude agent |
| --- | --- |
| `discovery` | discovery |
| `requirements` | requirements |
| `design` | design |
| `screen-design` | screen-design |
| `security-review` | security-review |
| `screen-review` | screen-review |
| `ui-review` | ui-review |
| `development-review` | development-review |
| `test-design` | test-design |
| `build-planning` | build-planning |
| `build` | build-frontend, build-backend |
| `evidence` | evidence |
| `review` | review |
| `release` | (Orchestrator 직접) |
| `change-control` | (Orchestrator 직접) |
| `documentation` | (Orchestrator 직접) |

subagent를 투입할 때는 agent 이름뿐 아니라 `persona`, `related_ids`, `scope`, `completion_criteria`를 함께 전달한다.

## 에이전트 구성

### Phase 0 (Discovery)

| 에이전트 | 파일 | 역할 |
|---------|------|------|
| discovery | `.claude/agents/discovery.md` | 온보딩, 현행 분석, 가정/위험 정리, 공수 산정 |

### Gate 1~2 — 요구사항·설계

| 에이전트 | 파일 | 역할 |
|---------|------|------|
| requirements | `.claude/agents/requirements.md` | G1 요구사항, AC, 기술스택 정의 |
| design | `.claude/agents/design.md` | G2 SW 아키텍처(C1/C2/C3, CNT/CMP/FLOW/ADR) + 기능/프로그램/API/DB/보안 설계, UT-ID 할당 |
| screen-design | `.claude/agents/screen-design.md` | G2 화면 구조, 와이어프레임, 디자인 토큰 |
| security-review | `.claude/agents/security-review.md` | G1/G2/G3/G4 보안 검토, FIND/CR 발행 |
| screen-review | `.claude/agents/screen-review.md` | G2/G3/G4 화면 누락/상태/증적 기준 검토 |
| ui-review | `.claude/agents/ui-review.md` | G2/G4 UI 기준선 충분성 검토 |
| development-review | `.claude/agents/development-review.md` | G2/G4 개발표준/코딩컨벤션 검토 |

### Gate 3~4 — 테스트·구현·검수

| 에이전트 | 파일 | 역할 |
|---------|------|------|
| test-design | `.claude/agents/test-design.md` | G3 테스트 케이스 설계, UT/IT/PT/UI 연결 |
| build-planning | `.claude/agents/build-planning.md` | Build Wave 분할, 위임 계획, 검증 기준 |
| build-frontend | `.claude/agents/build-frontend.md` | 프론트엔드 구현, UI 컴포넌트, API 연동 |
| build-backend | `.claude/agents/build-backend.md` | 백엔드 구현, API, DB 연동, 인증 |
| evidence | `.claude/agents/evidence.md` | 스크린샷 캡처, 테스트 실행, 증적 수집 |
| review | `.claude/agents/review.md` | G4/G5 추적성/보안/품질 검수, FIND/CR 판정 |

## 워크플로우

### Phase 0: Discovery (상위설계)

> **Phase 0은 Gate 규약이 적용되지 않는다.** rules, check-trace, session.json 없이 자유롭게 반복한다.

"상위설계 시작", "Discovery 시작", "법령 분석해줘", "인프라 설계해줘", "FP 산정해줘" 등의 요청 시:

1. `docs/artifacts/00-discovery/` 폴더 존재 여부를 확인한다
2. 사용자 요청에 따라 해당 에이전트를 투입한다:
   - 탐색, 현행 분석, 온보딩, 공수 산정 관련 → `Agent(discovery)`
3. 에이전트는 `docs/artifacts/00-discovery/` 하위에 산출물을 작성한다
4. 문서 변경 시 새 버전 파일(vN+1)로 작성하고 `CHANGELOG.md`에 기록한다
5. **사용자가 반복을 원하면 자유롭게 반복한다** — 승인 절차 없음

### Phase 0 → Gate 1 전환

사용자가 "Gate 1 시작", "상위설계 끝", "Discovery 완료" 등을 요청하면:

1. `docs/artifacts/00-discovery/DISCOVERY-CHECKLIST.md`의 필수 항목을 검토한다
2. 미충족 항목이 있으면 사용자에게 보고한다
3. 사용자 승인 후, `requirements` persona로 `Agent(requirements)`를 투입하여 Phase 0 산출물을 REQ-NNN/AC-NNN 형식으로 변환한다
4. 이후 기존 Gate 1~5 프로세스를 따른다

### Phase 1: 준비 (오케스트레이터 직접 수행)

1. `session.json`을 읽어 현재 Gate를 확인한다
2. 사용자 요청에서 작업 범위를 파악한다:
   - Phase 0 관련 요청 → Phase 0 에이전트 투입 (위 참조)
   - 특정 Gate 시작 요청 → 해당 Gate 에이전트 투입
   - "프로젝트 시작", 자연어 요청 → **Discovery 온보딩 후** Gate 1 진행
   - "상태 확인" → 현재 Gate 상태 보고
3. 온보딩 필요 여부 판단:
   - gate1이 pending + 사용자가 구체적 Gate를 지정하지 않음 → `Agent(discovery)` 투입
   - 명시적 Gate 지정 또는 이미 진행 중인 프로젝트 → discovery 스킵

### Phase 1.5: 온보딩 (Discovery → Requirements 연계)

"프로젝트 시작" 또는 자연어 요청 시:
1. `Agent(discovery)` 투입 — 사용자와 대화로 프로젝트 개요 수집
2. Discovery가 **프로젝트 온보딩 요약**을 반환
3. 오케스트레이터가 온보딩 요약을 컨텍스트에 포함하여 `requirements` persona로 `Agent(requirements)` 투입

### Phase 2: Gate별 팀 구성 및 실행

> 산출물 경로는 CLAUDE.md의 "Gate 산출물" 테이블 참조.

| Gate | 담당 | 비고 |
|------|------|------|
| Gate 1 | requirements | |
| Gate 2a | design (SW 아키텍처 Draft) | C1/C2 + 주요 CNT/ADR 후보, Pending 명시. `check-architecture --level draft` 통과 |
| Gate 2b | design (상세 설계) | 기능/프로그램/API/DB/보안. 아키텍처 결정과 일관 |
| Gate 2c | screen-design | design 완료 후 |
| Gate 2d | design (SW 아키텍처 Baseline 보강) | CMP/FLOW/품질/보안/추적 링크 마무리. `check-architecture --level baseline` 통과 |
| Gate 2 검수 | security-review, screen-review, ui-review, development-review | 병렬 가능 |
| Gate 3 | test-design | |
| 구현 계획 | build-planning | |
| 구현 | build-frontend + build-backend | Wave별 병렬 |
| UI 증적 | evidence | |
| Gate 4 | review | |
| Gate 5 | release (Orchestrator 직접) | |

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

### Gate 전환 조건 (`docs/core/AGENT_RUN_PROTOCOL.md` §5)

| Gate | 완료 조건 |
|------|----------|
| Phase 0 | 배경/제약/참조문서 파악, 질문·가정·위험 기록 (`docs/artifacts/00-discovery/`) |
| Gate 1 | 모든 `REQ-NNN`과 `NREQ-NNN`에 `AC-NNN` 매핑, 추적표 반영 |
| Gate 2 | SW 아키텍처가 `Baseline`(`check-architecture --level baseline` 통과)이고 `CNT/CMP/FLOW/ADR`, `FUNC/SCR/PGM/API/DB/IF/SEC`, 개발표준이 정의되며, 보안/화면/UI 품질/개발표준 검수가 Failed 없이 통과 |
| Gate 3 | 모든 `AC`와 보안항목이 `UT/IT/PT/UI` 중 하나 이상에 연결 |
| 구현 | Build Wave별 코드+테스트+추적표+증적이 갱신되고 단위 테스트 Pass |
| Gate 4 | Blocker(A~D) 전원 Pass, FIND/CR/ISSUE가 명시적으로 처리됨 |
| Gate 5 | 승인본/변경이력/릴리즈 증적 정리, 사용자 최종 승인 |

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
| "상위설계 시작", "Discovery 시작", "프로젝트 시작" | discovery |
| "Gate 1 시작", "요구사항 정의" | requirements |
| "Gate 2 시작", "설계 시작" | design(SW 아키텍처 → 상세 설계) → screen-design (순차), security-review/ui-review/development-review (병렬 검수) |
| "Gate 3 시작", "테스트 계획" | test-design |
| "구현 계획", "Build Wave 분할" | build-planning |
| "구현 시작", "코딩 시작" | build-frontend + build-backend (Wave별) |
| "UI 증적", "화면 캡처" | evidence |
| "Gate 4 시작", "리뷰 시작" | review |
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
| `security-baseline` | design, security-review, review | OWASP Top 10 체크리스트 |
