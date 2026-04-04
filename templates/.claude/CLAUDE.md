# {{PROJECT_NAME}} — Vulcan-Claude Harness

5-Gate 프로세스에 따라 에이전트 팀이 협업하여 체계적으로 개발하는 하네스.

**핵심 원칙**: 플래너는 코드를 쓰지 않는다. 실행자는 계획만 따른다.

## 구조

```
.claude/
├── agents/                  — 에이전트 정의
│   ├── concierge.md, pm.md, architect.md, ui-designer.md
│   ├── dba.md, frontend-dev.md, backend-dev.md
│   ├── ux-reviewer.md, qa.md
├── rules/                   — Gate별 규칙 (path-specific 조건부 로드)
│   ├── core-principles.md   — 항상 로드 (핵심 원칙)
│   ├── gate1-requirements.md — docs/01-requirements/** 접근 시
│   ├── gate2-design.md      — docs/02-design/** 접근 시
│   ├── gate3-testplan.md    — docs/03-test-plan/** 접근 시
│   ├── gate4-review.md      — docs/04-review/** 접근 시
│   └── implementation.md    — src/** 접근 시
├── skills/
│   ├── vulcan/skill.md      — 5-Gate 오케스트레이터 (Gate 전환 규칙 포함)
│   └── security-baseline/skill.md — OWASP Top 10
└── CLAUDE.md                — 이 파일
```

## 5-Gate 프로세스

```
Gate 1        Gate 2              Gate 3        구현             UI검수        Gate 4       Gate 5
요구사항  →   설계          →   테스트계획 →   코딩        →   UX리뷰   →   QA리뷰  →  최종승인
 (PM)     (Arch+DBA+UI설계)   (QA)      (FE+BE-dev)   (UX-reviewer)   (QA)      (Human)
   ↓           ↓                 ↓          ↓              ↓            ↓          ↓
 승인→       승인→             승인→      완료→          승인→        승인→      완료
```

각 Gate는 사용자 승인 후 `check-trace` → `session` 명령으로 전환한다.

## 사용법

`/vulcan` 스킬을 트리거하거나, "Gate 1 시작해줘" 같은 자연어로 요청한다.

## Gate 산출물

| Gate | 산출물 | 경로 |
|------|--------|------|
| Gate 1 | 요구사항 정의서 | `docs/01-requirements/REQUIREMENTS.md` |
| Gate 2 | 설계 문서 | `docs/02-design/REQ-NNN-Design.md` |
| Gate 2 | 데이터 설계 | `docs/02-design/REQ-NNN-Data-Design.md` |
| Gate 2 | UI 설계 | `docs/02-design/UI-Design.md` |
| Gate 3 | 테스트 계획서 | `docs/03-test-plan/Test-Plan.md` |
| UI 검수 | UX 리뷰 보고서 | `docs/04-review/UX-Review.md` |
| Gate 4 | QA 리뷰 보고서 | `docs/04-review/REQ-NNN-Review.md` |

## 참조 파일

- `session.json` — Gate 진행 상태 (vulcan.py가 관리)
- `ENVIRONMENT.md` — 빌드/실행/테스트 명령어
- `commenting-standards.md` — 코드 주석 규칙
- `GATE_GUIDE.md` — Gate 프로세스 상세 가이드
- `docs/05-security/baseline.md` — 보안 기준선
