# Vulcan-Anvil 컨텍스트 관리 전략 (레퍼런스)

> **이 문서는 참고용 레퍼런스**이다. 필수 적용 사항이 아니며, 컨텍스트 문제가 실제로 발생했을 때 꺼내 쓸 수 있는 도구 상자이다.
> Claude Code 공식 문서의 Best Practices를 Vulcan-Anvil 워크플로우에 맞춰 정리한다.
>
> **현재 적용된 것:**
> - skill.md 슬림화 (453줄 → 162줄) + `.claude/rules/` path-specific 분리 (전략 4)
> - Hooks: Stop 시 check-trace 자동 실행 (전략 3)
>
> **현재 미적용 (필요 시 도입):**
> - `/clear` 자동 실행은 불가능 — `/clear`는 CLI 내부 명령으로, hooks나 AI가 직접 트리거할 수 없다
> - Agent Teams (전략 2) — 실험적 기능, 안정화 후 재평가
> - 자기 개선 패턴 (전략 5) — Auto Memory는 기본 활성화, 나머지는 선택적 도입

---

## 문제 정의

Vulcan-Anvil의 5-Gate 프로세스를 한 세션에서 Gate 1→5까지 진행하면:

1. **컨텍스트 윈도우 포화** — skill.md(~450줄) + 에이전트 조율 + 산출물 검증 + 사용자 대화가 누적되어 초반 규약이 압축/희석됨
2. **서브에이전트 콜드 스타트** — 매번 새 컨텍스트에서 시작하므로, 오케스트레이터가 프롬프트에 규약을 충분히 전달하지 못하면 agent.md만 보고 동작
3. **후반 Gate 품질 저하** — Gate 4~5에서 초반 Gate 규칙(트레이서빌리티, 산출물 포맷 등)을 잊음

### 근거 (Claude Code 공식 문서)

> "Most best practices are based on one constraint: Claude's context window fills up fast, and performance degrades as it fills."
> — [Best Practices](https://code.claude.com/docs/en/best-practices)

> "CLAUDE.md fully survives compaction. After `/compact`, Claude re-reads your CLAUDE.md from disk and re-injects it fresh into the session."
> — [Memory](https://code.claude.com/docs/en/memory)

> "If you've corrected Claude more than twice on the same issue in one session, the context is cluttered with failed approaches. Run `/clear` and start fresh."
> — [Best Practices](https://code.claude.com/docs/en/best-practices)

---

## 전략 1: Gate 완료 시 `/clear` 자동 실행 (권장)

### 핵심 아이디어

Gate 완료 → session.json 업데이트 → **`/clear` 실행** → session.json 재로드 → 다음 Gate 자동 진행.

### `/compact` vs `/clear` — 왜 `/clear`인가

| | `/compact` | `/clear` |
|---|---|---|
| 동작 | 대화 히스토리를 **요약**하여 압축 | 대화 히스토리를 **완전 삭제** |
| CLAUDE.md | 디스크에서 다시 로드 ✅ | 디스크에서 다시 로드 ✅ |
| 이전 요약 | **누적됨** — 반복할수록 요약이 쌓임 | **없음** — 완전 초기화 |
| 한계 | Gate 1→5 반복 compact 시 요약 자체가 컨텍스트 포화 유발 | 이전 Gate 대화 내용 완전 유실 |

**`/compact`의 함정**: compact를 반복하면 이전 compact 요약이 계속 누적된다. Gate 5개 + 구현 + 리뷰를 한 세션에서 compact만으로 진행하면, 결국 요약들이 컨텍스트를 상당 부분 차지하여 같은 문제에 도달한다.

**`/clear`가 근본 해결**: 대화를 완전 리셋하되, 상태는 파일(session.json, docs/)로 보존되므로 정보 손실이 없다.

### `/clear` 후 오케스트레이터가 뭘 해야 하는지 아는가?

**안다.** 이유:
- `/clear` 후에도 **CLAUDE.md + skill.md가 다시 로드**됨
- skill.md의 Phase 1에 "session.json 읽어서 현재 Gate 확인" 규칙이 이미 있음
- 단, `/clear` 후 **자동으로 다음 작업을 시작하는 트리거**가 필요 → 이것은 skill.md 규칙으로 해결

### skill.md 수정 사항

Phase 3 (Gate 완료 후)의 step 6 뒤에 추가:

```markdown
### Phase 3.5: 컨텍스트 리셋 (Gate 전환 시)

Gate 전환이 필요할 때 다음 절차를 **반드시** 수행한다:

1. session.json 업데이트 완료 확인
2. 다음 Gate 정보를 한 줄로 정리한다 (예: "다음: Gate 2 설계, REQ 3개 그룹")
3. `/clear` 실행 — 컨텍스트 완전 초기화
4. `/clear` 직후 즉시 Phase 1(상태 복구 프로토콜)을 수행한다

**⚠️ `/compact`가 아니라 `/clear`를 사용한다.**
`/compact`는 요약이 누적되어 장기 세션에서 컨텍스트 포화를 유발한다.
`/clear`는 완전 리셋이지만, 모든 상태가 파일(session.json, docs/)에 보존되므로 정보 손실이 없다.
```

Phase 1 (준비) 강화:

```markdown
### Phase 1 보강: 상태 복구 프로토콜

세션 시작 또는 `/clear` 직후에는 **반드시** 다음을 수행한다:

1. `session.json` 읽기 — 현재 Gate, 완료된 Gate 확인
2. 다음 Gate의 pending 상태 확인
3. 최근 Gate 산출물 파일 존재 확인 (빈 파일 여부 포함)
4. 현재 Gate에 해당하는 에이전트와 작업 범위 결정
5. 다음 Gate 에이전트를 **즉시 투입**한다 (사용자 대기 불필요 — 이전 Gate에서 이미 승인됨)
```

### `/compact`를 쓰는 경우

`/compact`는 **Gate 내부**에서 대화가 길어질 때 사용한다 (예: 구현 단계에서 여러 REQ 그룹을 순차 처리할 때). Gate **전환** 시에는 반드시 `/clear`를 사용한다.

| 상황 | 사용 명령 |
|------|----------|
| Gate 전환 (Gate 1→2, 2→3 등) | `/clear` |
| Gate 내부에서 대화가 길어질 때 | `/compact` |
| 구현 Wave 간 전환 (Wave 1→2) | `/compact` (같은 Gate 내이므로) |

### 장점

- **주의: `/clear`는 자동 실행 불가** — CLI 내부 명령이므로 사용자가 수동으로 입력해야 한다
- CLAUDE.md 규약이 매 Gate마다 완전히 신선하게 로드됨
- 이전 요약 누적 문제 없음 — 매번 깨끗한 컨텍스트
- session.json이 이미 상태를 추적하므로 추가 인프라 불필요

### 단점

- 이전 Gate 대화의 세부 내용에 접근 불가 (하지만 산출물 파일로 보존됨)
- `/clear` 직후 session.json을 읽고 자동 진행하려면 skill.md 규칙이 정확해야 함

---

## 전략 2: Agent Teams (실험적)

### 핵심 아이디어

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수를 설정하면, 리드 세션이 팀원을 spawn하고 팀원들이 자율적으로 태스크를 분배/소통한다.

### 근거

> "Agent teams let you coordinate multiple Claude Code instances working together. One session acts as the team lead, coordinating work."
> — [Agent Teams](https://code.claude.com/docs/en/agent-teams)

> "Unlike subagents, which run within a single session and can only report back to the main agent, you can also interact with individual teammates directly."
> — [Agent Teams](https://code.claude.com/docs/en/agent-teams)

### Vulcan-Anvil과의 적합성

| 장점 | 단점 |
|------|------|
| 팀원 간 직접 메시징 (architect ↔ dba) | 실험적 기능, 안정성 미보장 |
| 공유 태스크 리스트로 자율 분배 | 토큰 비용 팀원 수 비례 증가 |
| 각 팀원이 독립 컨텍스트 보유 | 세션 재개(resume) 미지원 |
| subagent 정의 파일 재사용 가능 | 한 세션당 하나의 팀만 가능 |

### 현시점 권장 여부: **비추천** (실험적)

Agent Teams는 컨셉은 Vulcan-Anvil의 에이전트 팀 구조와 잘 맞지만, 현재 제한사항이 많다:
- 세션 재개 불가
- 태스크 상태가 지연될 수 있음
- 중첩 팀 불가 (팀원이 자기 팀을 만들 수 없음)
- 리드 교체 불가

안정화된 후 도입을 검토한다.

---

## 전략 3: Hooks로 규약 강제 (보완책)

### 핵심 아이디어

`settings.json`에 hook을 설정하여, 에이전트가 규약을 잊더라도 자동으로 검증/강제한다.

### 근거

> "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens."
> — [Best Practices](https://code.claude.com/docs/en/best-practices)

### 예시

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "python vulcan.py check-trace --quick 2>/dev/null || echo 'WARN: check-trace 이슈 발견'"
      }
    ],
    "Stop": [
      {
        "command": "python vulcan.py check-trace"
      }
    ]
  }
}
```

### 활용 시나리오

| Hook 시점 | 검증 내용 |
|-----------|----------|
| PostToolUse (Write/Edit) | 구현 중 설계 범위 밖 파일 수정 감지 |
| Stop (에이전트 종료 시) | check-trace 실행하여 산출물 정합성 확인 |
| TaskCompleted (Teams 모드) | 팀원이 태스크 완료 시 품질 게이트 검증 |

---

## 전략 4: CLAUDE.md / skill.md 최적화

### 핵심 아이디어

CLAUDE.md와 skill.md의 크기를 줄여 컨텍스트 소모를 최소화한다.

### 근거

> "Size: target under 200 lines per CLAUDE.md file."
> — [Memory](https://code.claude.com/docs/en/memory)

> "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost."
> — [Best Practices](https://code.claude.com/docs/en/best-practices)

### 구체적 방법

### 방법 A: skill.md 분리

Gate별 세부 규칙을 별도 파일로 분리하고, 메인 skill.md는 핵심 원칙 + 워크플로우 개요만 유지한다.

```
.claude/skills/
├── vulcan/
│   ├── skill.md              — 핵심 원칙 + 워크플로우 개요 (200줄 이하)
│   ├── gate1-details.md      — Gate 1 세부 규칙 (필요 시 참조)
│   ├── gate2-details.md      — Gate 2 세부 규칙
│   └── impl-details.md       — 구현 단계 세부 규칙
```

단, skills는 `/vulcan` 호출 시 또는 Claude가 관련성을 판단했을 때 로드된다.
skills 내의 추가 파일은 에이전트가 직접 읽어야 한다 (자동 로드 아님).

### 방법 B: `.claude/rules/` 활용 (핵심 — 컨텍스트 효율 극대화)

#### rules란?

CLAUDE.md를 **주제별, 경로별로 쪼개서 관리**하는 공식 기능이다.

#### 로드 시점 — 2가지 모드

| 모드 | frontmatter | 로드 시점 | 컨텍스트 소모 |
|------|-------------|----------|-------------|
| **무조건 로드** | `paths` 없음 | 매 세션 시작 | 항상 (CLAUDE.md와 동일) |
| **조건부 로드** | `paths` 있음 | **해당 경로 파일을 Claude가 읽을 때만** | 필요할 때만 |

> "Rules without paths frontmatter are loaded at launch. Rules with a paths field trigger when Claude reads files matching the pattern."
> — [Memory](https://code.claude.com/docs/en/memory)

#### Vulcan-Anvil에 적용: Gate별 path-specific rules

```
.claude/rules/
├── core-principles.md          ← paths 없음: 항상 로드 (핵심 원칙만, 짧게)
├── gate1-requirements.md       ← paths: ["docs/01-requirements/**"]
├── gate2-design.md             ← paths: ["docs/02-design/**"]
├── gate3-testplan.md           ← paths: ["docs/03-test-plan/**"]
├── gate4-review.md             ← paths: ["docs/04-review/**"]
├── implementation-frontend.md  ← paths: ["src/components/**", "src/app/**"]
├── implementation-backend.md   ← paths: ["src/api/**", "src/lib/**"]
└── security.md                 ← paths: ["docs/05-security/**"]
```

#### 각 rules 파일 예시

**core-principles.md** (항상 로드, 짧게 유지):
```markdown
# Vulcan-Anvil 핵심 원칙

- 플래너는 코드를 쓰지 않는다. 실행자는 계획만 따른다.
- Gate 문서 없이 구현을 시작하지 않는다.
- 각 Gate는 사용자 승인 후 전환한다.
- session.json으로 Gate 상태를 추적한다.
- Gate 전환 시 `/clear`로 컨텍스트를 리셋한다.
```

**gate1-requirements.md** (docs/01-requirements/ 접근 시만 로드):
```markdown
---
paths:
  - "docs/01-requirements/**"
---

# Gate 1: 요구사항 정의 규칙

- REQ-NNN-NN 형식의 ID를 사용한다
- 각 REQ에 AC-NNN-NN 수락 기준을 매핑한다
- REQ 그룹은 REQ-NNN, 상세 요구사항은 REQ-NNN-NN
- TRACEABILITY.md의 REQ 컬럼을 업데이트한다
- 기술 스택과 제약조건을 명시한다
```

**gate2-design.md** (docs/02-design/ 접근 시만 로드):
```markdown
---
paths:
  - "docs/02-design/**"
---

# Gate 2: 설계 규칙

- 설계 문서는 인터페이스와 제약조건을 정의한다. 구현 코드를 작성하지 않는다.
- 각 설계 요소에 UT-ID를 사전 배정한다
- SEC-ID로 보안 고려사항을 식별한다
- TRACEABILITY.md의 설계 문서 컬럼을 업데이트한다
- 파일명: req-nnn-design.md, req-nnn-data-design.md
```

**gate4-review.md** (docs/04-review/ 접근 시만 로드):
```markdown
---
paths:
  - "docs/04-review/**"
---

# Gate 4: QA 리뷰 규칙

- 코드 리뷰 → 테스트 실행 → 최종 판정 3단계로 분리 투입
- 🔴 필수 수정 발견 시 Developer 재투입 → 재검증
- QA가 Blocker 항목 무시하고 Pass 판정 금지
- check-trace 실패 상태에서 Gate 전환 금지
```

#### 이 구조의 효과

```
[Gate 1 진행 중]
  컨텍스트에 로드된 것:
  ✅ CLAUDE.md (항상)
  ✅ core-principles.md (항상)
  ✅ gate1-requirements.md (docs/01-requirements/ 접근했으므로)
  ❌ gate2-design.md (아직 접근 안 함)
  ❌ gate4-review.md (아직 접근 안 함)
  ❌ implementation-frontend.md (아직 접근 안 함)
  → 불필요한 규칙이 컨텍스트를 차지하지 않음!

[Gate 2 진행 중] (/clear 후)
  ✅ CLAUDE.md
  ✅ core-principles.md
  ✅ gate2-design.md (docs/02-design/ 접근했으므로)
  ❌ gate1-requirements.md (이 Gate에서 접근 안 함)
  → Gate 2에 필요한 규칙만 로드됨!
```

**현재 (skill.md 450줄 한 번에 로드)** vs **rules 분리 후**:

| | 현재 | rules 분리 후 |
|---|---|---|
| 항상 로드되는 양 | ~450줄 (skill.md 전체) | ~30줄 (core-principles.md) |
| Gate별 규칙 | 전부 섞여있음 | 해당 Gate 진입 시만 로드 |
| 규칙 무시 확률 | 높음 (길어서 묻힘) | 낮음 (필요한 것만 짧게) |

### 방법 C: `@import` 활용

CLAUDE.md에서 참조 문서를 import하여 세션 시작 시 함께 로드한다.

```markdown
# CLAUDE.md
@ENVIRONMENT.md
@commenting-standards.md
```

`@import`는 **항상 로드**되므로, 모든 세션에서 필요한 공통 참조에만 사용한다.
Gate별 규칙은 `@import`보다 **path-specific rules가 더 효율적**이다.

---

## 전략 5: 자기 개선 패턴 (Self-Improving Patterns)

AI가 스스로 규칙/스킬을 개선하는 패턴들이 커뮤니티에서 실험되고 있다. 아래는 실제 사례와 한계를 정리한 것이다.

### 패턴 A: Auto Memory (공식 기능)

Claude가 세션 중 자동으로 메모를 저장하고, 다음 세션에서 로드하는 공식 기능.

**동작 방식:**
```
세션 중 사용자 교정: "npm 말고 pnpm 써"
  → Claude가 ~/.claude/projects/<project>/memory/에 자동 저장
  → 다음 세션 시작 시 MEMORY.md (200줄 / 25KB) 자동 로드
```

**실제 사용 후기:**
- 초기 효과는 좋음 — 빌드 명령, 코드 스타일, 디버깅 패턴 등을 기억
- **20~30 세션 후 품질 저하** — 모순된 항목 공존, 상대적 날짜("어제") 의미 상실, 삭제된 파일 참조, 200줄 초과 시 오래된 노트 미로드
- "도움이 되어야 할 노트북이 Claude를 혼란시키는 노이즈가 된다"

> 참고: [Automatic Memory Is Not Learning](https://medium.com/@brentwpeterson/automatic-memory-is-not-learning-4191f548df4c)
> — "auto memory captures the 'what' but not the 'why' or context"

**Auto Dream (메모리 정리 기능):**

Auto Memory 품질 저하 문제를 해결하기 위해 Anthropic이 추가한 기능. 백그라운드 서브에이전트가 메모리 파일을 리뷰하고 정리한다.

- 상대 날짜 → 절대 날짜 변환
- 모순된 항목 제거
- 중복 병합
- 200줄 제한 내로 유지

트리거 조건: 마지막 정리 후 24시간 이상 + 5세션 이상 경과 시 자동 실행.
실제 사례: 913개 세션의 메모리를 8~9분에 280줄→142줄로 정리한 케이스 보고됨.

> 참고: [Auto Dream 상세](https://antoniocortes.com/en/2026/03/30/auto-memory-and-auto-dream-how-claude-code-learns-and-consolidates-its-memory/)

### 패턴 B: "실수 → 반성 → 규칙 추가" 프롬프트

사용자가 실수 발생 시 한 문장으로 자기 개선을 트리거하는 패턴.

**매직 프롬프트:**
> "Reflect on this mistake. Abstract and generalize the learning. Write it to CLAUDE.md."

**동작 단계:**
1. Claude가 실수함 (예: 설계 문서에 구현 코드 작성)
2. 사용자가 교정 후 위 프롬프트 실행
3. Claude가: 무엇이 잘못됐는지 반성 → 일반화 → CLAUDE.md에 규칙 추가

**보고된 결과:**
- 세션 1: 실수 3개 → 규칙 3개 추가 (각 5초)
- 세션 2: 기본 실수 제거됨, 더 고급 오류 발견
- 세션 3: 논의가 아키텍처 트레이드오프 수준으로 상승

**핵심 조건 — Meta-Rules:**

CLAUDE.md에 "규칙을 어떻게 작성할지"에 대한 메타 규칙이 있어야 한다:
```markdown
# Meta-Rules (규칙 작성 규칙)
- NEVER 또는 ALWAYS로 시작하는 절대적 지시문 사용
- 왜(why)를 먼저 설명하고 해결책을 제시
- 한 줄로 표현 가능한 규칙만 추가 (장황한 설명 금지)
- 기존 규칙과 모순되면 기존 규칙을 수정하거나 삭제
```

> 참고: [Self-Improving AI: One Prompt](https://dev.to/aviad_rozenhek_cba37e0660/self-improving-ai-one-prompt-that-makes-claude-learn-from-every-mistake-16ek)

### 패턴 C: Learnings.md 자기 학습 스킬

프로젝트에 `Learnings.md` 파일을 두고, Claude가 매 세션마다 읽고 → 작업 → 새로운 관찰 추가하는 패턴.

**구조:**
```markdown
# Learnings.md

## What Has Worked
- [2026-03-15] REQ 그룹별 청크 분리 시 2개 이하가 품질 유지에 효과적 (confidence: high)

## What Has Failed
- [2026-03-14] 5개 REQ를 한 번에 설계 투입 → 후반 REQ 품질 급락 (confidence: high)

## Patterns and Preferences
- architect에게 보안 고려사항 누락 빈번 → SEC-ID 체크리스트 반드시 포함 (confidence: medium)

## Open Questions
- Gate 2에서 ui-designer의 투입 타이밍 최적화 필요
```

**CLAUDE.md에 추가할 지시:**
```markdown
# Self-Learning Protocol
- 세션 시작 시 Learnings.md를 읽고 핵심 사항을 인지한다
- 작업 완료 후 새로운 관찰/실수/패턴을 Learnings.md에 추가한다
- 각 항목에 날짜, 태스크 유형, confidence 레벨(high/medium/low)을 포함한다
- 80줄을 초과하면 오래되거나 낮은 confidence 항목을 정리한다
```

**보고된 한계:**
- 읽기 단계를 건너뛰면 패턴 전체가 무효화됨
- 80~100줄 초과 시 고가치 항목이 오래된 관찰에 묻힘
- 관련 없는 워크플로우를 섞으면 혼란 유발
- CLAUDE.md 대체물로 취급하면 안 됨 — 보완 관계

> 참고: [Self-Learning Claude Code Skill](https://www.mindstudio.ai/blog/self-learning-claude-code-skill-learnings-md)

### 패턴 D: Bootstrap Seed Prompt (자기 진화 시스템)

~1400 토큰의 시드 프롬프트를 CLAUDE.md에 넣으면, Claude가 스스로 설정을 진화시키는 패턴.

**핵심 루프:** Reflect(반성) → Triage(분류) → Cascade(적용)

**진화 과정:**
- 세션 1~3: 기본 인프라 구축 (learnings.md 생성 등)
- 세션 8: 반복 패턴이 rules로 승격
- 세션 15+: 문서 구조가 자연스럽게 분화 (rule/process/requirements/reference)

**주의사항:**
- 원 저자가 **"아직 검증되지 않은 가설"**이라고 명시
- 50줄 초과 시 자동 분리 규칙이 있으나, 실제로 잘 작동하는지 미확인
- 사용자 승인 없이 진화하면 위험 → `AskUserQuestion`으로 제어

> 참고: [Self-Improving Claude Code Gist](https://gist.github.com/ChristopherA/fd2985551e765a86f4fbb24080263a2f)

### 현실적 평가 및 Vulcan-Anvil 적용

| 패턴 | 성숙도 | 실제 검증 | Vulcan-Anvil 적합성 |
|------|--------|----------|-------------------|
| Auto Memory | ✅ 공식 기능 | 20~30 세션 후 품질 저하, Auto Dream으로 보완 | 기본 활성화, 별도 작업 불필요 |
| 실수→반성→규칙 추가 | ⚠️ 커뮤니티 패턴 | 초기 효과 좋음, 장기 검증 부족 | **Gate 리뷰 후 적용 권장** |
| Learnings.md | ⚠️ 커뮤니티 패턴 | 80줄 이하 유지 시 효과적 | **오케스트레이터에 적용 가능** |
| Bootstrap Seed | ❌ 미검증 가설 | 저자 본인이 미검증 인정 | 당장은 비추천 |

### Vulcan-Anvil 권장 적용 방법

**1단계 (즉시):** Auto Memory 활성화 확인 — 이미 기본 활성화되어 있음

**2단계 (Gate 리뷰 후 자기 개선):** QA가 Gate 4에서 🔴 발견 시:
```
사용자: "이 실수를 반성하고, 일반화해서 rules에 추가해"
→ Claude가 .claude/rules/gate2-design.md에 규칙 추가
→ 다음 프로젝트에서 같은 실수 방지
```

**3단계 (Learnings.md 도입):** 오케스트레이터가 프로젝트별 학습 내용을 축적:
```
프로젝트 루트에 .claude/learnings.md 생성
→ 오케스트레이터가 Gate 완료 시 관찰 사항 기록
→ 다음 세션에서 참고
→ 80줄 초과 시 정리
```

**핵심 원칙:** 자기 개선은 **보완책**이다. 1차 방어선은 여전히 `/clear` + 잘 구조화된 rules + hooks이다. 자기 개선이 잘 안 되더라도 프로세스가 무너지지 않도록 설계해야 한다.

---

## 권장 조합

| 우선순위 | 전략 | 효과 |
|---------|------|------|
| **1 (필수)** | Gate 전환 시 `/clear` 자동 실행 | 사용자 개입 없이 컨텍스트 완전 초기화 (요약 누적 없음) |
| **2 (필수)** | CLAUDE.md / skill.md 최적화 + rules 분리 | 컨텍스트 소모 최소화, 규약 준수율 향상 |
| **3 (권장)** | Hooks로 규약 강제 | 잊더라도 자동 검증으로 안전망 확보 |
| **4 (권장)** | 자기 개선 (Auto Memory + 실수→규칙 패턴) | 세션 간 학습 축적, 반복 실수 방지 |
| **5 (대기)** | Agent Teams | 안정화 후 도입 검토 |

---

## 참고 자료 (Claude Code 공식 문서)

| 문서 | URL | 핵심 내용 |
|------|-----|----------|
| Best Practices | https://code.claude.com/docs/en/best-practices | 컨텍스트 관리, /compact, 세션 분리, 서브에이전트 패턴 |
| Memory (CLAUDE.md) | https://code.claude.com/docs/en/memory | CLAUDE.md 작성법, 200줄 제한, auto memory, /compact 후 CLAUDE.md 재로드 |
| Sub-agents | https://code.claude.com/docs/en/sub-agents | 서브에이전트 정의, persistent memory, 컨텍스트 분리 |
| Agent Teams | https://code.claude.com/docs/en/agent-teams | 실험적 팀 기능, 공유 태스크, 팀원 간 직접 메시징 |
| Hooks | https://code.claude.com/docs/en/hooks | PostToolUse, Stop, TaskCompleted 등 자동 검증 |
| Skills | https://code.claude.com/docs/en/skills | 온디맨드 로드, disable-model-invocation |
| Context Window | https://code.claude.com/docs/en/context-window | 컨텍스트 시각화, 토큰 소비 분석 |
| Sessions | https://code.claude.com/docs/en/sessions | --continue, --resume, /rename, 세션 관리 |

### 커뮤니티 자료 (자기 개선 패턴)

| 자료 | URL | 핵심 내용 |
|------|-----|----------|
| Self-Improving AI (DEV.to) | https://dev.to/aviad_rozenhek_cba37e0660/self-improving-ai-one-prompt-that-makes-claude-learn-from-every-mistake-16ek | "실수→반성→규칙 추가" 매직 프롬프트 패턴 |
| Self-Learning Skill (MindStudio) | https://www.mindstudio.ai/blog/self-learning-claude-code-skill-learnings-md | Learnings.md 자기 학습 스킬 패턴, 한계 분석 |
| Bootstrap Seed (GitHub Gist) | https://gist.github.com/ChristopherA/fd2985551e765a86f4fbb24080263a2f | ~1400 토큰 시드 프롬프트로 자기 진화 시스템 (미검증) |
| Auto Dream (AntonioCortes) | https://antoniocortes.com/en/2026/03/30/auto-memory-and-auto-dream-how-claude-code-learns-and-consolidates-its-memory/ | Auto Memory 품질 저하 문제와 Auto Dream 해결책 |
| Auto Memory Is Not Learning (Medium) | https://medium.com/@brentwpeterson/automatic-memory-is-not-learning-4191f548df4c | auto memory의 한계 — "what"은 기억하지만 "why"는 못함 |
| Recursive Self-Improvement (Medium) | https://medium.com/@davidroliver/recursive-self-improvement-building-a-self-improving-agent-with-claude-code-d2d2ae941282 | 신뢰도 점수 기반 자율 개선 패턴 (시리즈 연재 중) |

---

## 다음 단계

1. [ ] skill.md에 Phase 3.5 (컨텍스트 리셋) 규칙 추가
2. [ ] skill.md를 200줄 이하로 리팩토링 (Gate별 세부 규칙 분리)
3. [ ] `.claude/rules/` 도입 (path-specific 규칙)
4. [ ] hooks 설정 (check-trace 자동 실행)
5. [ ] CLAUDE.md에 Meta-Rules 추가 (규칙 작성 규칙)
6. [ ] "실수→반성→규칙 추가" 프롬프트를 QA 리뷰 프로세스에 통합
7. [ ] Learnings.md 도입 검토 (오케스트레이터용, 80줄 이하 유지)
8. [ ] Auto Memory + Auto Dream 동작 확인
9. [ ] Agent Teams 안정화 후 재평가
