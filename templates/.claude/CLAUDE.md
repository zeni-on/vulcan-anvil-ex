# {{PROJECT_NAME}} — Vulcan-Claude Harness

Phase 0(Discovery) + 5-Gate 프로세스에 따라 에이전트 팀이 협업하여 체계적으로 개발하는 하네스.

**핵심 원칙**: 플래너는 코드를 쓰지 않는다. 실행자는 계획만 따른다.

## 구조

```
.claude/
├── agents/                  — 에이전트 정의
│   ├── ba.md, sa.md, estimator.md, analyst.md — Phase 0 (Discovery)
│   ├── concierge.md, pm.md, architect.md   — Gate 1~2
│   ├── ui-designer.md, dba.md              — Gate 2
│   ├── frontend-dev.md, backend-dev.md     — 구현
│   ├── ux-reviewer.md, qa.md               — Gate 3~4
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

## 전체 프로세스

```
Phase 0           Gate 1        Gate 2              Gate 3        구현             UI검수        Gate 4       Gate 5       Backlog
Discovery    →   요구사항  →   설계          →   테스트계획 →   코딩        →   UX리뷰   →   QA리뷰  →  최종승인   ↺  지속 반복
(BA+SA+Est)       (PM)     (Arch+DBA+UI설계)   (QA)      (FE+BE-dev)   (UX-reviewer)   (QA)      (Human)    (PM+QA)
  자유반복→       승인→       승인→             승인→      완료→          승인→        승인→      완료→       증분 rollback
```

- **Phase 0**: 탐색적 단계. Gate 규약/rules/skills 없음. 자유롭게 버전 반복.
- **Gate 1~5**: 각 Gate는 사용자 승인 후 `check-trace` → `session` 명령으로 전환한다.
- **Backlog (Gate 5 이후)**: Gate 5 완료 이후 새 요구사항/기술부채/개선은 `docs/06-backlog/BACKLOG.md`로 접수되고, Triage Level에 따라 해당 Gate로 **증분 rollback**하여 scope 내 REQ만 재진행한다.

## 사용법

- Phase 0: "상위설계 시작", "Discovery 시작" 등 자연어로 BA/SA/Estimator 투입
- Gate 1~5: `/vulcan` 스킬을 트리거하거나, "Gate 1 시작해줘" 같은 자연어로 요청

## 산출물

### Phase 0 (Discovery) — 규약 없음, 자유 반복

| 산출물 | 경로 | 담당 |
|--------|------|------|
| 용어집 | `docs/00-discovery/glossary/glossary.md` | BA |
| 상위 요구사항 | `docs/00-discovery/requirements/requirements-vN.md` | BA |
| 기능 상세 | `docs/00-discovery/functional/functional-detail-vN.md` | BA |
| 인프라 설계 | `docs/00-discovery/infrastructure/infrastructure-vN.md` | SA |
| 기술 검토서 | `docs/00-discovery/technical-review/[주제]-review.md` | SA |
| FP 산정서 | `docs/00-discovery/estimation/fp-estimation-vN.md` | Estimator |
| 완료 체크리스트 | `docs/00-discovery/DISCOVERY-CHECKLIST.md` | 공통 |
| 코드베이스 분석 | `docs/00-discovery/audit/codebase-analysis.md` | Analyst |
| API 표면 분석 | `docs/00-discovery/audit/api-surface.md` | Analyst |
| 의존성 감사 | `docs/00-discovery/audit/dependency-audit.md` | Analyst |
| 마이그레이션 전략 | `docs/00-discovery/audit/migration-strategy-vN.md` | Analyst |
| 변경 이력 | `docs/00-discovery/CHANGELOG.md` | 공통 |

### Gate 1~5 — 엄격한 Gate 규약 적용

| Gate | 산출물 | 경로 |
|------|--------|------|
| Gate 1 | 요구사항 정의서 | `docs/01-requirements/REQUIREMENTS.md` |
| Gate 2 | 설계 문서 | `docs/02-design/REQ-NNN-Design.md` |
| Gate 2 | 데이터 설계 | `docs/02-design/REQ-NNN-Data-Design.md` |
| Gate 2 | UI 설계 | `docs/02-design/UI-Design.md` |
| Gate 3 | 테스트 계획서 | `docs/03-test-plan/Test-Plan.md` |
| UI 검수 | UX 리뷰 보고서 | `docs/04-review/UX-Review.md` |
| Gate 4 | QA 리뷰 보고서 | `docs/04-review/REQ-NNN-Review.md` |
| Backlog | 백로그 | `docs/06-backlog/BACKLOG.md` |
| Backlog | 운영 프로세스 | `docs/06-backlog/PROCESS.md` |

## 참조 파일

- `session.json` — Gate 진행 상태 (vulcan.py가 관리)
- `ENVIRONMENT.md` — 빌드/실행/테스트 명령어
- `commenting-standards.md` — 코드 주석 규칙
- `GATE_GUIDE.md` — Phase 0 + Gate 프로세스 상세 가이드
- `docs/05-security/baseline.md` — 보안 기준선
