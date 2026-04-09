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
| 에이전트 실행 | 한 세션에서 역할 전환 | **Subagents로 병렬 실행** |
| 스킬 | 없음 | `.claude/skills/*/skill.md` 스킬 트리거 |
| 규칙 | 없음 | `.claude/rules/*.md` 조건부 로드 |
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
│   ├── CLAUDE.md                       # 하네스 개요
│   ├── settings.json                   # hooks 설정
│   ├── agents/
│   │   ├── concierge.md                # 온보딩
│   │   ├── pm.md                       # 요구사항 (Gate 1)
│   │   ├── architect.md                # 시스템 설계 (Gate 2)
│   │   ├── ui-designer.md              # UI 설계 (Gate 2)
│   │   ├── dba.md                      # 데이터 설계 (Gate 2)
│   │   ├── frontend-dev.md             # 프론트엔드 구현
│   │   ├── backend-dev.md              # 백엔드 구현
│   │   ├── ux-reviewer.md              # UX 검수
│   │   └── qa.md                       # 테스트/리뷰 (Gate 3, 4)
│   ├── rules/
│   │   ├── core-principles.md          # 핵심 원칙 (항상 로드)
│   │   ├── gate1-requirements.md       # Gate 1 규칙
│   │   ├── gate2-design.md             # Gate 2 규칙
│   │   ├── gate3-testplan.md           # Gate 3 규칙
│   │   ├── gate4-review.md             # Gate 4 규칙
│   │   ├── implementation.md           # 구현 규칙
│   │   └── traceability.md             # 추적성 규칙
│   └── skills/
│       ├── vulcan/skill.md             # 5-Gate 오케스트레이터
│       └── security-baseline/skill.md  # OWASP 보안 체크
├── ENVIRONMENT.md                      # 빌드/실행 명령어
├── GATE_GUIDE.md                       # Gate 프로세스 가이드
├── commenting-standards.md             # 코드 주석 규칙
├── session.json                        # Gate 진행 상태
├── vulcan.py                           # CLI 도구
└── docs/
    ├── 01-requirements/REQUIREMENTS.md # Gate 1 산출물
    ├── 02-design/                      # Gate 2 산출물
    │   ├── REQ-NNN-Design.md           #   시스템 설계
    │   ├── REQ-NNN-Data-Design.md      #   데이터 설계
    │   └── UI-Design.md                #   UI 설계
    ├── 03-test-plan/Test-Plan.md       # Gate 3 산출물
    ├── 04-review/                      # Gate 4 산출물
    │   ├── REQ-NNN-Review.md           #   QA 리뷰
    │   └── UX-Review.md                #   UX 리뷰
    ├── 05-security/baseline.md         # 보안 기준선
    └── TRACEABILITY.md                 # 추적 매트릭스
```

## 5-Gate 프로세스

```
Gate 1        Gate 2              Gate 3        구현             UI검수        Gate 4       Gate 5
요구사항  →   설계          →   테스트계획 →   코딩        →   UX리뷰   →   QA리뷰  →  최종승인
 (PM)     (Arch+DBA+UI설계)   (QA)      (FE+BE-dev)   (UX-reviewer)   (QA)      (Human)
```

각 Gate는 **사용자 승인** 후 다음 Gate로 진행합니다.

| Gate | 담당 에이전트 | 산출물 | 검증 |
|------|-------------|--------|------|
| 1 | pm | REQUIREMENTS.md | REQ-ID별 AC 존재 |
| 2a | architect | REQ-NNN-Design.md | REQ 그룹별 설계 파일 존재 |
| 2b | dba | REQ-NNN-Data-Design.md | DB 있는 프로젝트만 |
| 2c | ui-designer | UI-Design.md | 2a 완료 후 |
| 3 | qa | Test-Plan.md | REQ-ID별 TST-ID 매핑 |
| 구현 | frontend-dev + backend-dev | 소스 코드 + 단위 테스트 | 병렬 구현 |
| UI 검수 | ux-reviewer | UX-Review.md | 스크린샷 기반 검수 |
| 4 | qa | REQ-NNN-Review.md | Blocker 전원 Pass |
| 5 | Human | (수동) | 최종 확인 |

## 가로축 스킬 (Cross-cutting Skills)

5-Gate 프로세스에 종속되지 않는 가로축 스킬은 `.claude/skills/` 아래에 함께 포함됩니다.
일부는 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT)에서 가져왔습니다.
자세한 라이선스는 [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) 참고.
새 스킬을 작성·기여하려면 [`docs/SKILL_AUTHORING_GUIDE.md`](docs/SKILL_AUTHORING_GUIDE.md)를 먼저 읽으세요.

| 스킬 | 자동 발화 시점 | 출처 |
|------|---------------|------|
| `vulcan` | Phase 0 / Gate 1~5 진입, 상태 조회 | Vulcan |
| `security-baseline` | architect의 SEC-ID 작성, qa의 Gate 4 보안 점검 | Vulcan |
| `debugging-and-error-recovery` | 테스트 실패, 빌드 깨짐, 예외, 회귀 발생 | addyosmani/agent-skills |
| `context-engineering` | 신규 세션 시작, 컨텍스트 품질 저하, 영역 전환 | addyosmani/agent-skills |
| `git-workflow-and-versioning` | 모든 코드 변경 (커밋/브랜치/머지) | addyosmani/agent-skills |

## CLI 명령어

모든 명령어는 **프로젝트 디렉토리에서** 실행합니다 (`init` 제외).

```bash
# 프로젝트 초기화 (Vulcan-Claude-Anvil 디렉토리에서 실행)
python vulcan.py init <target-dir> <project-name>

# Gate 정합성 검사
python vulcan.py check-trace

# Gate 상태 업데이트
python vulcan.py session --gate gate1 --status done --feature "기능명"

# Gate 롤백
python vulcan.py rollback --gate gate2 --reason "요구사항 변경"

# 스냅샷 생성 (대시보드용)
python vulcan.py export

# 프레임워크 업그레이드 (프로젝트 디렉토리에서 실행)
python vulcan.py upgrade

# 버전 확인
python vulcan.py version
```

> **upgrade 참고**: 프로젝트 디렉토리의 `session.json`에 기록된 `vulcan_src` 경로에서 최신 템플릿을 가져옵니다. ENVIRONMENT.md, session.json, docs/ 산출물은 보존됩니다.

## 대시보드

프로젝트의 Gate 진행 상태, 산출물, 추적 매트릭스를 시각적으로 모니터링하는 Next.js 웹 대시보드입니다.

### 로컬 프로젝트 모드

```bash
# 대시보드 설치 (최초 1회)
cd dashboard
npm install

# 대시보드 실행
npm run dev
```

브라우저에서 `http://localhost:3001` 접속 후 로컬 프로젝트 경로를 등록합니다.

### GitHub 연동 모드

GitHub 리포지토리의 프로젝트를 대시보드에서 직접 모니터링할 수 있습니다.

#### 1. GitHub Personal Access Token 발급

1. GitHub → Settings → Developer settings → **Personal access tokens** → **Fine-grained tokens**
2. **Generate new token** 클릭
3. 설정:
   - **Token name**: `vulcan-dashboard` (임의)
   - **Expiration**: 원하는 기간
   - **Repository access**: 대상 리포지토리 선택 (또는 All repositories)
   - **Permissions** → Repository permissions:
     - **Contents**: `Read-only` (필수)
     - **Metadata**: `Read-only` (자동 선택)
4. **Generate token** 클릭 후 토큰 복사

#### 2. 환경변수 설정

```bash
# dashboard/.env.local 파일 생성
cd dashboard
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx" > .env.local
```

> **보안 주의**: `GITHUB_TOKEN`은 서버사이드에서만 사용되며, 클라이언트에 절대 노출되지 않습니다. `.env.local`은 `.gitignore`에 포함되어 있어 커밋되지 않습니다.

#### 3. 대시보드에서 GitHub 프로젝트 등록

대시보드 UI에서 프로젝트 추가 시 타입을 `GitHub`로 선택하고, `owner/repo` 형식의 리포지토리와 브랜치를 입력합니다.

## 핵심 원칙

**"플래너는 코드를 쓰지 않는다. 실행자는 계획만 따른다."**

- PM/Architect/DBA/QA는 문서를 작성하고, Frontend-dev/Backend-dev만 코드를 작성합니다
- Developer는 설계 범위 밖의 판단을 하지 않고, 필요 시 보고합니다
- 모든 Gate는 사용자 승인 없이 자동으로 넘어가지 않습니다
- QA의 Gate 4 리뷰는 긴급 상황에서도 절대 생략하지 않습니다
- check-trace 실패 상태에서 Gate 전환은 금지됩니다
