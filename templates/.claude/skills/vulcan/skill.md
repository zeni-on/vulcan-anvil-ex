---
name: vulcan
description: "5-Gate 개발 프로세스 오케스트레이터. 요구사항(Gate1)→설계(Gate2)→테스트계획(Gate3)→구현→QA리뷰(Gate4)→최종승인(Gate5)을 에이전트 팀이 협업하여 수행한다. 'Gate 1 시작', '프로젝트 시작', '요구사항 정의해줘', '설계 시작', '구현 시작', '리뷰 시작', 'Gate 상태 확인' 등 프로젝트 개발 프로세스 전반에 이 스킬을 사용한다. 단, 프로젝트 초기화(vulcan.py init)나 session.json 직접 수정은 이 스킬의 범위가 아니다."
---

# Vulcan — 5-Gate 개발 프로세스 오케스트레이터

에이전트 팀을 조율하여 5-Gate 프로세스에 따라 체계적으로 프로젝트를 개발한다.

## 실행 모드

두 가지 실행 모드를 지원한다. 프로젝트 상황에 맞게 선택한다.

### Subagents 모드 (기본)

오케스트레이터가 Agent 도구로 에이전트를 투입하고, SendMessage로 중계 통신한다.

- 오케스트레이터가 모든 조율을 담당
- 에이전트 간 소통은 오케스트레이터 경유
- 별도 설정 불필요, 즉시 사용 가능

### Agent Teams 모드 (실험적)

리드 세션이 팀원을 spawn하면, 팀원들이 자율적으로 태스크를 분배하고 직접 소통한다.

- 팀원 간 직접 메시징 (오케스트레이터 경유 불필요)
- 공유 태스크 리스트에서 자율적으로 태스크 claim
- tmux/iTerm2 분할 화면으로 동시 모니터링 가능
- **활성화**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수 설정
- **주의**: 실험적 기능, 토큰 사용량이 팀원 수에 비례하여 증가

**모드 선택 기준:**

| 상황 | 권장 모드 |
|------|----------|
| REQ 그룹 1~2개, 소규모 프로젝트 | Subagents |
| REQ 그룹 3개 이상, 병렬 구현 필요 | Agent Teams |
| frontend-dev ↔ backend-dev 실시간 소통 빈번 | Agent Teams |
| 토큰 비용 절약 우선 | Subagents |
| 안정성 우선 | Subagents |

**에이전트 정의 파일(`.claude/agents/*.md`)은 두 모드에서 동일하게 사용된다.**

## 에이전트 구성

| 에이전트 | 파일 | 역할 | 타입 |
|---------|------|------|------|
| pm | `.claude/agents/pm.md` | 요구사항 수집, REQ-ID 체계화, AC 작성 | general-purpose |
| architect | `.claude/agents/architect.md` | 시스템 설계, API, 모듈 구조, TST-ID 할당 | general-purpose |
| dba | `.claude/agents/dba.md` | 데이터 모델링, ERD, 마이그레이션 | general-purpose |
| frontend-dev | `.claude/agents/frontend-dev.md` | 프론트엔드 구현, UI 컴포넌트, API 연동 | general-purpose |
| backend-dev | `.claude/agents/backend-dev.md` | 백엔드 구현, API, DB 연동, 인증 | general-purpose |
| qa | `.claude/agents/qa.md` | 테스트 계획, 코드 리뷰, 판정 | general-purpose |

## 핵심 원칙

**"플래너는 코드를 쓰지 않는다. 실행자는 계획만 따른다."**

- 각 Gate는 사용자(Human)의 승인을 받아야 다음 Gate로 진행한다
- Gate 문서가 완성되지 않은 상태에서 구현을 시작하지 않는다
- session.json으로 Gate 진행 상태를 추적한다

## 워크플로우

### Phase 1: 준비 (오케스트레이터 직접 수행)

1. `session.json`을 읽어 현재 Gate를 확인한다
2. 사용자 요청에서 작업 범위를 파악한다:
   - 특정 Gate 시작 요청 → 해당 Gate 에이전트 투입
   - "프로젝트 시작" → Gate 1부터 순차 진행
   - "상태 확인" → 현재 Gate 상태 보고
3. 현재 Gate에 맞는 에이전트를 구성한다

### Phase 2: Gate별 팀 구성 및 실행

| Gate | 작업 | 담당 | 의존 | 산출물 |
|------|------|------|------|--------|
| Gate 1 | 요구사항 정의 | pm | 없음 | `docs/requirements/REQUIREMENTS.md` |
| Gate 2a | 시스템 설계 | architect | Gate 1 | `docs/design/req-nnn-design.md` |
| Gate 2b | 데이터 설계 | dba | Gate 1 | `docs/design/req-nnn-data-design.md` |
| Gate 3 | 테스트 계획 | qa | Gate 2 | `docs/test-plan/TEST_PLAN.md` |
| 구현 | 프론트엔드 구현 | frontend-dev | Gate 3 | 프론트엔드 소스 코드 + 단위 테스트 |
| 구현 | 백엔드 구현 | backend-dev | Gate 3 | 백엔드 소스 코드 + 단위 테스트 |
| Gate 4 | QA 리뷰 | qa | 구현 | `docs/review/req-nnn-review.md` |
| Gate 5 | 최종 승인 | 사용자 | Gate 4 | (사용자 확인) |

**Gate 2a와 2b는 병렬 실행** — architect와 dba가 동시에 작업한다.

**구현은 다단계 병렬 실행:**
- **1차 병렬**: frontend-dev와 backend-dev가 동시에 작업한다
- **2차 병렬**: 각 에이전트 내에서도 독립적인 REQ 그룹은 병렬로 실행한다

### 구현 병렬 실행 전략

오케스트레이터는 구현 시작 시 다음 절차를 수행한다:

1. **의존성 분석** — REQUIREMENTS.md의 REQ 그룹 간 의존 관계를 파악한다
2. **실행 그래프 구성** — 독립적인 REQ 그룹은 병렬, 의존성이 있으면 순차로 배치한다
3. **에이전트 투입** — 각 병렬 단위마다 frontend-dev, backend-dev 인스턴스를 투입한다

```
예시: 3개 REQ 그룹, REQ-003이 REQ-001에 의존

[Wave 1 - 병렬]
  backend-dev  #1: REQ-001 API      ||  backend-dev  #2: REQ-002 API
  frontend-dev #1: REQ-001 UI       ||  frontend-dev #2: REQ-002 UI

[Wave 2 - Wave 1의 REQ-001 완료 후]
  backend-dev  #3: REQ-003 API
  frontend-dev #3: REQ-003 UI
```

**병렬 실행 조건:**
- 두 REQ 그룹이 동일 DB 테이블을 변경하지 않을 것
- 두 REQ 그룹 간 API 호출 의존이 없을 것
- 공유 컴포넌트/모듈이 충돌하지 않을 것

**의존성 판단 기준** (설계 문서 기반):
- 같은 엔티티/테이블을 참조 → 의존 가능성 있음 → 설계 문서에서 구체적 확인
- import/호출 관계 → 순차 실행
- 독립적인 페이지 + 독립적인 API → 병렬 실행 가능

**팀원 간 소통 흐름:**
- pm 완료 → architect에게 요구사항 전달, dba에게 데이터 요구사항 전달, qa에게 AC 전달
- architect ↔ dba: 엔티티/관계 정보 실시간 소통
- architect + dba 완료 → frontend-dev에게 UI/라우팅 설계 전달, backend-dev에게 API/DB 설계 전달
- frontend-dev ↔ backend-dev: API 스펙, 응답 형식 실시간 소통 (같은 REQ 그룹 내)
- 모든 구현 인스턴스 완료 → qa에게 구현 완료 알림 + 변경 파일 목록
- qa 리뷰 중 🔴 발견 → 해당 developer 인스턴스에게 수정 요청 → 재작업 → 재검증 (최대 2회)

### Phase 3: Gate 전환

1. 에이전트 작업 완료 후, 사용자에게 산출물을 보고한다
2. 사용자의 승인을 기다린다
3. 승인 확인 즉시 `python vulcan.py check-trace` 를 **직접 실행**한다
4. check-trace 이슈 0건 확인 시 `python vulcan.py session --gate gateN --status done --feature "기능명"` 을 **직접 실행**한다
5. session 명령 실행 완료 후 다음 Gate로 진행한다

> **핵심**: 에이전트가 명령어를 사용자에게 안내하는 것이 아니라 직접 실행한다.
> 사용자가 별도로 터미널 명령을 입력할 필요가 없다.

## Gate별 실행 모드

| 사용자 요청 | 실행 모드 | 투입 에이전트 |
|-----------|----------|-------------|
| "Gate 1 시작", "요구사항 정의" | Gate 1 모드 | pm |
| "Gate 2 시작", "설계 시작" | Gate 2 모드 | architect + dba (병렬) |
| "Gate 3 시작", "테스트 계획" | Gate 3 모드 | qa |
| "구현 시작", "코딩 시작" | 구현 모드 | frontend-dev + backend-dev (REQ 그룹별 다단계 병렬) |
| "Gate 4 시작", "리뷰 시작" | Gate 4 모드 | qa |
| "상태 확인", "어디까지 했어" | 상태 확인 | (오케스트레이터 직접) |

## Agent Teams 모드 실행 가이드

Teams 모드 활성화 시 (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), 오케스트레이터는 다음과 같이 동작한다.

### Teams 모드에서의 Gate별 실행

| Gate | Subagents 모드 | Teams 모드 |
|------|---------------|------------|
| Gate 1 | Agent(pm) 투입 | pm 팀원 spawn |
| Gate 2 | Agent(architect) + Agent(dba) 병렬 | architect + dba 팀원 spawn, 직접 소통 |
| Gate 3 | Agent(qa) 투입 | qa 팀원 spawn |
| 구현 | Agent(frontend-dev) + Agent(backend-dev) 다단계 병렬 | REQ 그룹별 frontend-dev + backend-dev 팀원 spawn, 자율 협업 |
| Gate 4 | Agent(qa) 투입 | qa 팀원 spawn |

### Teams 모드 구현 예시

리드 세션에서 다음과 같이 팀을 구성한다:

```
"REQ-001과 REQ-002를 병렬로 구현해줘.
 REQ-001은 frontend-dev와 backend-dev 에이전트로 팀원을 만들고,
 REQ-002도 마찬가지로 frontend-dev와 backend-dev 팀원을 만들어줘.
 REQ-003은 REQ-001에 의존하니까 REQ-001 완료 후 시작해줘."
```

팀원들은 자동으로:
- 공유 태스크 리스트에서 자기 담당 태스크를 claim
- 같은 REQ 그룹의 frontend-dev ↔ backend-dev가 직접 API 스펙 소통
- 완료 시 리드에게 자동 알림

### Teams 모드 주의사항

- Gate 전환은 여전히 사용자 승인 필요 (Teams 모드에서도 자동 전환 불가)
- session.json 관리는 리드 세션이 담당
- check-trace는 리드 세션에서 실행
- 팀원 간 파일 충돌 시 리드가 조율

## 데이터 전달 프로토콜

| 전략 | 방식 | Subagents | Teams | 용도 |
|------|------|-----------|-------|------|
| 파일 기반 | `docs/` 디렉토리 | O | O | Gate 산출물 저장 및 공유 |
| 메시지 기반 | SendMessage | 오케스트레이터 경유 | 직접 메시징 | 에이전트 간 실시간 정보 전달 |
| 태스크 기반 | TaskCreate/TaskUpdate | O | 공유 태스크 리스트 | 진행 상황 추적 |
| 상태 기반 | `session.json` | O | O (리드 관리) | Gate 전환 상태 관리 |

## 에스컬레이션 프로토콜

다음 상황에서는 즉시 사용자에게 보고한다:

| 트리거 | 이유 |
|--------|------|
| 요구사항 범위 변경 | 설계/테스트 재작업 필요 여부 판단 |
| QA 2회 연속 Fail | 설계 수준의 문제 가능성 |
| 설계에 없는 외부 서비스/라이브러리 필요 | 아키텍처 변경 |
| Breaking 스키마 변경 | 마이그레이션 전략 승인 필요 |
| 보안 취약점 발견 | 즉시 대응 필요 |
| 병렬 인스턴스 간 파일 충돌 | 실행 순서 재조정 필요 |

보고 형식: "에스컬레이션: [트리거] — [현재 상황] — [선택지 1 / 선택지 2]"

## 금지 사항

- Gate 문서 없이 구현 시작
- Frontend-dev/Backend-dev가 설계 범위 밖에서 자율적 판단
- Gate 완료 선언 없이 session.json 수동 수정
- QA가 Blocker 항목 무시하고 Pass 판정
- check-trace 실패 상태에서 Gate 전환

## 에러 핸들링

| 에러 유형 | 전략 |
|----------|------|
| session.json 없음 | "vulcan.py init을 먼저 실행하세요" 안내 |
| Gate 순서 이탈 | 현재 Gate를 안내하고 순서대로 진행 유도 |
| 에이전트 실패 | 1회 재시도 → 실패 시 사용자에게 보고 |
| 산출물 누락 | check-trace 실행 안내 → 누락 항목 식별 |

## 테스트 시나리오

### 정상 흐름
**프롬프트**: "Gate 1 시작해줘. 할 일 관리 웹앱을 만들려고 해."
**기대 결과**:
- pm 에이전트 투입, 비전 질문 시작
- REQUIREMENTS.md 작성 (REQ-001 ~ REQ-NNN)
- 각 REQ-NNN-NN에 AC-NNN-NN 매핑
- 사용자 확인 요청 → check-trace 안내

### Gate 2 병렬 흐름
**프롬프트**: "Gate 2 시작"
**기대 결과**:
- architect + dba 병렬 투입
- architect: req-nnn-design.md 작성
- dba: req-nnn-data-design.md 작성
- 상호 엔티티 정보 SendMessage로 교환

### 구현 병렬 흐름 (단일 REQ 그룹)
**프롬프트**: "구현 시작" (REQ 그룹 1개)
**기대 결과**:
- frontend-dev + backend-dev 병렬 투입
- frontend-dev: UI 컴포넌트, 페이지, 라우팅 구현
- backend-dev: API 엔드포인트, 비즈니스 로직, DB 연동 구현
- 상호 API 스펙 SendMessage로 교환
- 양쪽 완료 후 qa에게 구현 완료 알림

### 구현 다단계 병렬 흐름 (다중 REQ 그룹)
**프롬프트**: "구현 시작" (독립적인 REQ 그룹 여러 개)
**기대 결과**:
- 오케스트레이터가 REQ 그룹 간 의존성 분석
- 독립적인 REQ 그룹별로 frontend-dev + backend-dev 인스턴스 병렬 투입
- 의존성 있는 REQ 그룹은 선행 그룹 완료 후 순차 투입
- 각 인스턴스 내에서 frontend-dev ↔ backend-dev API 스펙 소통
- 전체 완료 후 qa에게 통합 구현 완료 알림

### 에러 흐름
**프롬프트**: "구현 시작해줘" (Gate 1 미완료 상태)
**기대 결과**:
- session.json 확인 → current_gate가 gate1
- "Gate 1(요구사항)을 먼저 완료해야 합니다" 안내

## 에이전트별 확장 스킬

| 스킬 | 대상 에이전트 | 역할 |
|------|-------------|------|
| `gate-transition` | (오케스트레이터) | Gate 전환 규칙, check-trace 통합, session 관리 |
| `security-baseline` | qa, architect | OWASP Top 10 체크리스트, 보안 평가 기준 |
