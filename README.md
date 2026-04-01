<p align="center">
  <img src="docs/assets/anvil.svg" width="64" height="64" alt="Anvil">
</p>

# Vulcan-Claude-Anvil

> 대장장이 신 Vulcan처럼, 에이전트 팀을 단련하여 체계적으로 프로젝트를 완성합니다.

**Agent-Forge의 5-Gate 프로세스**를 **Claude Code 네이티브 하네스**(.claude/)로 재구현한 AI 협업 개발 프레임워크.

## Agent-Forge와 무엇이 다른가

| 관점 | Agent-Forge | Vulcan-Claude-Anvil |
|------|-------------|---------------|
| 에이전트 구조 | AGENTS.md 단일 파일 (프롬프트 트릭) | `.claude/agents/*.md` 네이티브 에이전트 |
| 에이전트 실행 | 한 세션에서 역할 전환 | **Subagents 또는 Agent Teams로 병렬 실행** |
| 스킬 | 없음 | `.claude/skills/*/skill.md` 스킬 트리거 |
| 오케스트레이션 | 프롬프트 규칙 기반 | 의존성 DAG + 에러 핸들링 테이블 |
| AI 호환 | Claude + Gemini | **Claude Code 전용** (네이티브 기능 활용) |
| 5-Gate 프로세스 | O | O (동일) |
| session.json | O | O (동일) |
| check-trace | O | O (동일) |

## 빠른 시작

### 1. 프로젝트 초기화

```bash
# Vulcan-Claude-Anvil 디렉토리에서 실행
python vulcan.py init ../my-project "MyProject"
```

### 2. 프로젝트에서 Claude Code 실행

```bash
cd ../my-project
claude
```

### 3. 개발 시작

```
> Gate 1 시작해줘. 할 일 관리 웹앱을 만들려고 해.
```

또는 `/vulcan` 스킬을 트리거합니다.

## 생성되는 프로젝트 구조

```
my-project/
├── .claude/
│   ├── CLAUDE.md                    # 하네스 개요
│   ├── agents/
│   │   ├── pm.md                    # 요구사항 (Gate 1)
│   │   ├── architect.md             # 설계 (Gate 2)
│   │   ├── dba.md                   # 데이터 설계 (Gate 2)
│   │   ├── frontend-dev.md          # 프론트엔드 구현
│   │   ├── backend-dev.md           # 백엔드 구현
│   │   └── qa.md                    # 테스트/리뷰 (Gate 3, 4)
│   └── skills/
│       ├── vulcan/skill.md          # 5-Gate 오케스트레이터
│       ├── gate-transition/skill.md # Gate 전환 규칙
│       └── security-baseline/skill.md # OWASP 보안 체크
├── ENVIRONMENT.md                   # 빌드/실행 명령어
├── GATE_GUIDE.md                    # Gate 프로세스 가이드
├── commenting-standards.md          # 코드 주석 규칙
├── session.json                     # Gate 진행 상태
├── vulcan.py                        # CLI 도구
└── docs/
    ├── requirements/REQUIREMENTS.md # Gate 1 산출물
    ├── design/                      # Gate 2 산출물
    ├── test-plan/TEST_PLAN.md       # Gate 3 산출물
    ├── review/                      # Gate 4 산출물
    └── security/baseline.md         # 보안 기준선
```

## 5-Gate 프로세스

```
Gate 1        Gate 2         Gate 3           구현            Gate 4        Gate 5
요구사항  →   설계      →   테스트계획 →     코딩       →   QA 리뷰  →   최종승인
 (PM)     (Architect+DBA)    (QA)      (FE-dev+BE-dev)     (QA)       (Human)
```

각 Gate는 **사용자 승인** 후 다음 Gate로 진행합니다.

| Gate | 담당 에이전트 | 산출물 | 검증 |
|------|-------------|--------|------|
| 1 | pm | REQUIREMENTS.md | REQ-ID별 AC 존재 |
| 2 | architect + dba | design.md + data-design.md | REQ 그룹별 설계 파일 존재 |
| 3 | qa | TEST_PLAN.md | REQ-ID별 TST-ID 매핑 |
| 구현 | frontend-dev + backend-dev | 소스 코드 + 단위 테스트 | 병렬 구현 |
| 4 | qa | review.md | REQ 그룹별 리뷰 파일 + Blocker 전원 Pass |
| 5 | Human | (수동) | 최종 확인 |

## CLI 명령어

```bash
# 프로젝트 초기화
python vulcan.py init <target-dir> <project-name>

# Gate 정합성 검사
python vulcan.py check-trace

# Gate 상태 업데이트
python vulcan.py session --gate gate1 --status done --feature "기능명"

# 스냅샷 생성 (대시보드용)
python vulcan.py export

# 프레임워크 업그레이드
python vulcan.py upgrade

# 버전 확인
python vulcan.py version
```

## 실행 모드

Vulcan-Claude-Anvil는 두 가지 실행 모드를 지원합니다. 에이전트 정의 파일은 동일하게 사용됩니다.

| 모드 | 상태 | 통신 방식 | 특징 |
|------|------|----------|------|
| **Subagents** (기본) | 안정 | 오케스트레이터 경유 SendMessage | 별도 설정 불필요 |
| **Agent Teams** (실험적) | Beta | 팀원 간 직접 메시징 | 자율 태스크 분배, 대규모 병렬에 유리 |

Agent Teams 모드 활성화:
```bash
# 환경변수 설정
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

## 핵심 원칙

**"플래너는 코드를 쓰지 않는다. 실행자는 계획만 따른다."**

- PM/Architect/DBA/QA는 문서를 작성하고, Frontend-dev/Backend-dev만 코드를 작성합니다
- Developer(Frontend-dev, Backend-dev)는 설계 범위 밖의 판단을 하지 않고, 필요 시 보고합니다
- 모든 Gate는 사용자 승인 없이 자동으로 넘어가지 않습니다
- QA의 Gate 4 리뷰는 긴급 상황에서도 절대 생략하지 않습니다
