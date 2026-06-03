# Codex Repo-local Skill Strategy

> Status: draft v0.1  
> 작성일: 2026-06-03  
> 목적: Vulcan-Anvil Ex에서 Codex repo-local skill을 어떻게 사용하고, 전역 skill과 Core 규칙을 어떻게 분리할지 정리한다.

## 1. 배경

Codex는 `AGENTS.md`를 작업 시작 시 instruction chain에 넣는다.
반면 skill은 항상 읽는 지침이 아니라, 이름/설명으로 발견되고 task와 맞을 때 또는 명시적으로 호출될 때 읽히는 절차 카드다.

따라서 Ex는 다음을 구분해야 한다.

| 항목 | 역할 |
| --- | --- |
| `AGENTS.md` | 항상 적용되는 프로젝트 기본 지침 |
| `.agents/skills/*/SKILL.md` | Codex가 필요할 때 읽는 repo-local 절차 카드 |
| `docs/core/` | Ex의 원본 규칙 |
| `vulcan.py` | 실제 검증과 차단을 수행하는 도구 |
| `docs/adapters/codex-gpt/skills/*.md` | Run 문서와 adapter가 참조하는 내부 작업 카드 |

## 2. 원칙

1. Ex는 사용자 전역 skill을 기본으로 수정하지 않는다.
2. `init`과 `upgrade`는 프로젝트 내부 `.agents/skills`만 생성/갱신한다.
3. repo-local skill은 Core 규칙을 복제하지 않고 필요한 문서와 명령으로 안내한다.
4. skill은 행동을 유도하고, 강제력은 `vulcan.py`의 check 명령이 담당한다.
5. 같은 이름의 전역 skill이 있어도 repo-local skill이 자동 override된다고 가정하지 않는다.
6. skill description은 자동 선택의 핵심이므로 trigger 단어를 명확히 넣되, 긴 절차를 description에 넣지 않는다.
7. profile별 세부 정책은 skill에 복제하지 않고 `docs/core/DELIVERY_PROFILES.md`, `session.json`, `vulcan.config.json`, `profile-status`를 원본으로 사용한다.

## 2.1 Profile 적용 원칙

Repo-local skill은 profile별로 분리하지 않는다.

예를 들어 `vulcan-qa-audit`, `vulcan-qa-poc`처럼 skill을 나누지 않고, `vulcan-qa`가 현재 profile을 확인한 뒤 Core profile 정책을 따른다.

```text
python vulcan.py profile-status
docs/core/DELIVERY_PROFILES.md
session.json
vulcan.config.json
```

이렇게 하면 profile 정책이 바뀌어도 skill 파일을 여러 군데 수정하지 않아도 된다.
skill은 "profile을 확인하고 Core 정책을 적용하라"는 짧은 절차만 갖는다.

## 3. 1차 Skill Set

초기 repo-local skill은 다음 5개로 제한한다.

| Skill | 목적 |
| --- | --- |
| `vulcan-orchestrator` | Gate/Run/worker/approval 라우팅 진입점 |
| `vulcan-design` | Gate 2 설계와 interface/UI/API/DB/security 계약 |
| `vulcan-impl-wave` | Impl, BW-000, Build Wave, worker 실행과 통합 |
| `vulcan-qa` | Gate 4 staged QA, evidence, FIND/CR/ISSUE, qa-fix-loop |
| `vulcan-release` | Gate 5 승인, release-pr, backlog, tag/release note 준비 |

너무 많은 skill을 한 번에 만들면 자동 선택이 흔들릴 수 있다.
따라서 1차는 큰 Gate/Run 단위만 둔다.

## 4. Init/Upgrade 정책

`vulcan.py init`과 `vulcan.py upgrade`는 원본 repo의 `.agents/` 디렉터리를 프로젝트에 복사한다.

```text
project/
  .agents/
    skills/
      vulcan-orchestrator/SKILL.md
      vulcan-design/SKILL.md
      vulcan-impl-wave/SKILL.md
      vulcan-qa/SKILL.md
      vulcan-release/SKILL.md
```

전역 위치인 사용자 홈의 skill 저장소는 기본 명령으로 수정하지 않는다.
나중에 필요하면 별도 명령으로 선택 설치를 검토한다.

```text
python vulcan.py install-runtime-bootstrap --runtime codex --scope user
```

이 명령은 아직 구현 대상이 아니며, 기본 배포 경로가 아니다.

## 5. AGENTS.md와의 관계

`AGENTS.md`는 다음 역할을 한다.

- 현재 프로젝트의 Orchestrator 기본 규칙을 항상 제공한다.
- Vulcan 작업에서는 관련 repo-local skill을 먼저 확인하도록 유도한다.
- skill이 자동 선택되지 않아도 `AGENTS.md`의 Gate/Run 규칙이 기본 안전망이 된다.

Skill은 다음 역할을 한다.

- 현재 Gate와 작업 성격에 맞는 짧은 절차를 제공한다.
- 매번 `vulcan.py --help`를 넓게 탐색하는 비용을 줄인다.
- 자율운영 요청에서도 Impl, QA, Release의 반복 절차를 빠르게 떠올리게 한다.

## 6. 검증 기준

다음 항목으로 효과를 확인한다.

- 새 프로젝트 `init` 후 `.agents/skills`가 생성되는가?
- 기존 프로젝트 `upgrade` 후 `.agents/skills`가 복원/갱신되는가?
- Codex가 Vulcan 작업에서 관련 skill을 자동 또는 명시적으로 사용할 수 있는가?
- skill 사용 후 Run 생성, worker 실행, QA staged flow에서 Orchestrator 보정량이 줄어드는가?
- skill이 Core 규칙을 중복하지 않고 최신 Core 문서를 참조하는가?

## 7. 다음 단계

1차 검증 후 필요하면 Claude와 AGY도 같은 관점에서 runtime bootstrap을 정리한다.

- Claude: `.claude/CLAUDE.md`, `.claude/agents/`, `.claude/skills/`
- AGY/Gemini: `GEMINI.md`, `.antigravitycli`, CLI prompt/profile

단, Claude/AGY bootstrap은 Codex repo-local skill MVP가 실제로 도움이 되는지 확인한 뒤 진행한다.
