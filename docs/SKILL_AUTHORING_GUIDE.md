# Vulcan 스킬 작성 가이드

이 문서는 `templates/.claude/skills/` 아래에 새 스킬을 추가하거나 기존 스킬을 수정할 때 따라야 할 형식과 원칙을 정의한다. 외부 출처(예: addyosmani/agent-skills)의 스킬을 가져올 때의 절차도 포함한다.

> 본 가이드의 일부 원칙은 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)의 `docs/skill-anatomy.md`(MIT)를 참고했다.

---

## 1. 스킬은 무엇이고, 무엇이 아닌가

Vulcan 하네스에는 세 가지 종류의 동작 정의가 있다. 이들의 경계를 헷갈리면 책임이 모호해진다.

| 구분 | 위치 | 역할 | 발화 방식 |
|---|---|---|---|
| **에이전트** | `.claude/agents/*.md` | 역할/페르소나(pm, architect, qa…). Gate별 책임 주체. | 명시적 호출 또는 오케스트레이터가 위임 |
| **룰** | `.claude/rules/*.md` | 조건부로 로드되는 정책. Gate별 강제 규약. | path-specific (특정 경로 접근 시 자동) |
| **스킬** | `.claude/skills/<name>/skill.md` | 작업 워크플로우. 단계별 절차. | description의 트리거 매칭으로 자동 발화 |

스킬은 **"어떻게 일하는가"**를 정의한다. "누가 일하는가"는 에이전트, "무엇을 지켜야 하는가"는 룰이다.

### Vulcan 스킬의 두 가지 결

- **세로축 스킬**: Vulcan 5-Gate 프로세스 자체에 종속된 스킬. 현재 `vulcan`(오케스트레이터), `security-baseline`(architect/qa 보조)이 해당한다.
- **가로축 스킬**: Gate에 종속되지 않는 일반 작업 워크플로우. 현재 `debugging-and-error-recovery`, `context-engineering`, `git-workflow-and-versioning`이 해당하며, 모두 외부에서 가져왔다.

새 스킬을 추가할 때는 어느 결인지 먼저 결정하라. 세로축이면 Gate 워크플로우와의 통합 지점을 명시해야 하고, 가로축이면 Gate에 침범하지 않는 선을 지켜야 한다.

---

## 2. 파일 위치와 명명 규칙

```
templates/.claude/skills/
└── <skill-name>/                  ← 디렉토리명 = name
    ├── skill.md                   ← 필수 (Vulcan 컨벤션: 소문자)
    └── <supporting-file>.md       ← 선택 (참고 자료, 100줄 초과 시 분리)
```

규칙:
- 디렉토리명은 `lowercase-hyphen-separated`. 예: `debugging-and-error-recovery`.
- 진입 파일은 `skill.md` (소문자, Vulcan 컨벤션). addyosmani/agent-skills 원본은 `SKILL.md`(대문자)지만 Vulcan으로 가져올 때는 소문자로 변환한다.
- 보조 파일은 `lowercase-hyphen-separated.md` 형태. 예: `examples.md`, `frameworks.md`.

새 스킬 추가 시 `vulcan.py`의 `FRAMEWORK_FILES` 리스트에도 등록해야 `upgrade` 명령이 정상 동기화한다 (vulcan.py:790-822 참고).

---

## 3. Frontmatter 형식

```yaml
---
name: skill-name-with-hyphens
description: "(스킬이 제공하는 것 1줄). Use when (트리거 1). Use when (트리거 2). NOT for (제외 1), (제외 2)."
---
```

### 규칙

- **`name`**: 디렉토리명과 정확히 일치. lowercase-hyphen-separated.
- **`description`**: 1024자 이하. 다음 구조를 지킨다.
  1. **첫 문장 = what**: 스킬이 무엇을 제공하는지 1줄로. 워크플로우 단계를 요약하지 않는다.
  2. **`Use when ...` 절 다수**: 자동 발화 트리거를 카테고리별로 분리. 한 절에 여러 키워드를 묶어도 좋다.
  3. **`NOT for ...` 절**: 명시적 제외 조건. 다른 스킬과의 경계를 그어준다.

### 워크플로우 단계 요약 금지 — 왜 중요한가

`description`은 모델의 시스템 프롬프트에 주입되어 *항상* 보인다. 만약 description에 워크플로우 단계 요약(예: "Discovery → Gate1 → Gate2 → ...")이 들어가 있으면, 모델은 본문 `skill.md`를 읽지 않고 그 요약만 보고 동작할 위험이 있다. description은 **"무엇 + 언제"**만 담고, **"어떻게"**는 본문에 둔다.

### 한국어 / 영어 선택 기준

- **세로축 스킬** (Vulcan 프로세스 직결, 사용자 자연어로 호출): **한국어**
  - 예: `vulcan/skill.md`의 description은 한국어. 사용자가 "Gate 1 시작", "보안 점검" 같은 한국어로 말할 때 매칭률이 높다.
- **가로축 스킬** (일반 기술 워크플로우, 외부 출처): **영어**
  - 예: `debugging-and-error-recovery/skill.md`의 description은 영어. 유지보수 비용을 낮추고, 모델의 영문 매칭률을 활용한다.

### 실제 예시

**세로축 스킬 (`templates/.claude/skills/security-baseline/skill.md`):**

```yaml
description: "OWASP Top 10 기반 보안 체크리스트와 SEC-ID 작성·검증 기준을 제공하는 스킬. Use when architect가 Gate 2 설계 산출물에 보안 요건(SEC-ID)을 정의·문서화할 때. Use when qa가 Gate 4 리뷰의 Blocker 항목 D(보안 점검)를 수행할 때. Use when 사용자가 '보안 점검', 'OWASP', '취약점 체크', '보안 설계 검토', 'SEC-ID 작성'을 요청할 때. Use when 인증/인가/암호화/입력 검증/세션 관리 등 보안 민감 영역을 설계하거나 리뷰할 때. NOT for 침투 테스트(pentest) 실행, 외부 보안 인증 심사(ISMS·SOC2 등), 보안 사고 대응(인시던트 핸들링), 위협 모델링 워크숍 진행."
```

(383자, 1024 한도 내)

**가로축 스킬 (`templates/.claude/skills/debugging-and-error-recovery/skill.md`):**

```yaml
description: Guides systematic root-cause debugging. Use when tests fail, builds break, behavior doesn't match expectations, or you encounter any unexpected error. Use when you need a systematic approach to finding and fixing the root cause rather than guessing.
```

---

## 4. 본문 표준 섹션

`skill.md`의 본문은 다음 표준 섹션을 따른다. 모든 섹션이 필수는 아니지만, 빠진 섹션은 이유가 있어야 한다.

```markdown
# Skill Title

## Overview
1~2문장. 이 스킬이 무엇을 하고, 왜 중요한가.

## When to Use
- 트리거 조건 (positive)
- NOT for: 제외 조건 (negative)
- (가로축 스킬인 경우) **Vulcan integration**: ...

## Core Process / Workflow
주요 워크플로우. 번호 매긴 단계, 의사결정 분기 ASCII 다이어그램, 코드 예시.

## (스킬별 특화 섹션)
- 패턴 / 예시 / 안티패턴 등 스킬 성격에 맞게.

## Common Rationalizations
| 합리화 | 현실 |
|---|---|
| 에이전트가 단계를 건너뛸 핑계 | 그 핑계가 왜 틀렸는가 |

## Red Flags
- 스킬이 위반되고 있다는 관찰 가능한 신호
- 코드 리뷰 시 체크할 항목

## Verification
완료 후 확인할 체크박스. 모든 항목은 증거(테스트 출력, 빌드 결과, 스크린샷)로 검증 가능해야 한다.

- [ ] ...
- [ ] ...
```

### 섹션별 작성 팁

- **Overview**: "엘리베이터 피치". 길어지면 잘못 쓰고 있다.
- **When to Use**: positive와 negative를 모두 둔다. negative가 다른 스킬과의 경계를 만든다.
- **Core Process**: *구체적*이어야 한다. "테스트가 통과하는지 확인하라"가 아니라 "`npm test`를 실행하고 모든 테스트가 통과하는지 확인하라".
- **Common Rationalizations**: 잘 만들어진 스킬의 가장 큰 차별점. 에이전트가 단계를 건너뛸 만한 모든 핑계에 미리 반박을 적어둔다. *"이건 간단하니까 스펙은 생략해도 돼"* 같은 말이 안 나오게 한다.
- **Red Flags**: Common Rationalizations와 짝이다. 핑계가 사고라면 Red Flag는 증상이다.
- **Verification**: 체크박스마다 *증거*가 있어야 한다. "코드가 깨끗한가" (X) → "`npm run lint`가 0 에러로 종료한다" (O).

---

## 5. Vulcan 5-Gate와의 통합 검증

새 스킬을 추가하기 전에 다음 항목을 확인하라. **하나라도 위반되면 스킬을 다시 설계하라.**

- [ ] **"플래너는 코드를 쓰지 않는다" 원칙을 침해하지 않는가?** PM/Architect/QA 같은 플래너 에이전트가 이 스킬 때문에 코드를 직접 쓰게 되면 안 된다.
- [ ] **`check-trace`를 우회하도록 권장하지 않는가?** "급할 때는 추적성 검증을 건너뛰어라" 같은 안내는 금지.
- [ ] **Gate 승인 절차를 건너뛰지 않는가?** "구현이 끝났으면 자동으로 다음 Gate로 전환하라"는 금지. 모든 Gate 전환은 사용자 승인이 필요하다.
- [ ] **기존 에이전트의 책임과 중복되지 않는가?** 중복이면 새 스킬보다는 기존 에이전트 정의 보강이 더 적절할 수 있다.
- [ ] **(가로축 스킬인 경우)** `When to Use` 섹션에 **Vulcan integration** 한 줄을 추가했는가? 예: "구현 단계(frontend-dev/backend-dev)에서 발생한 오류는 이 스킬을 따른다."

### Vulcan integration 한 줄 작성 예시

가로축 스킬은 본문은 그대로 두고 `When to Use` 섹션 마지막에 한 줄만 추가한다.

```markdown
- **Vulcan integration**: 구현 단계(frontend-dev / backend-dev)에서 발생한 오류는 이 스킬을 따른다. Gate 4(QA 리뷰) 도중 발견된 결함도 동일.
```

이 패턴은 외부 스킬의 가치를 손상시키지 않으면서 Vulcan 사용자에게 즉시 의미 있는 진입점을 준다.

---

## 6. 작성 원칙 6가지

1. **Process over knowledge**. 스킬은 워크플로우다. 지식 카탈로그가 아니다. 사실보다 단계를 적어라.
2. **Specific over general**. "테스트를 실행하라"가 아니라 "`npm test -- --coverage`를 실행하라". 명령어는 풀 형태로.
3. **Evidence over assumption**. Verification 체크박스는 모두 증거(테스트 출력, 빌드 결과, 파일 존재 여부)로 검증 가능해야 한다.
4. **Anti-rationalization**. 건너뛸 만한 단계마다 핑계와 반박 표를 추가하라. 이게 스킬의 가장 큰 가치다.
5. **Progressive disclosure**. `skill.md`는 진입점이다. 보조 파일은 필요할 때만 로드되도록 분리한다.
6. **Token-conscious**. 제거해도 에이전트의 행동이 변하지 않는 섹션은 제거하라. 모든 섹션은 자기 토큰 비용을 정당화해야 한다.

---

## 7. 외부 출처 스킬을 가져올 때

외부 레포의 스킬을 Vulcan에 포함하려면 다음 절차를 따른다.

### Step 1. 라이선스 확인

- **권장 라이선스**: MIT, Apache 2.0, BSD-2/3
- 거부: GPL/AGPL (Vulcan과 호환되지 않는 copyleft)
- 라이선스가 명시되지 않은 경우 사용 금지.

### Step 2. 파일 복사 + 명명 변환

원본의 `SKILL.md`(대문자)를 Vulcan 컨벤션의 `skill.md`(소문자)로 변환한다. 디렉토리명은 그대로 유지.

```
원본:   skills/<name>/SKILL.md
Vulcan: templates/.claude/skills/<name>/skill.md
```

### Step 3. 출처 코멘트 삽입

frontmatter `---` 닫는 줄 바로 다음에 한 줄 코멘트를 추가한다.

```markdown
---
name: ...
description: ...
---

<!-- Source: https://github.com/<owner>/<repo> (MIT License, © YYYY <Author>). See THIRD_PARTY_LICENSES.md. -->

# Skill Title
...
```

### Step 4. Vulcan integration 한 줄 추가

`When to Use` 섹션 끝에 Vulcan 통합 한 줄을 추가한다 (5절 참고). 이 외 본문은 원본 그대로 둔다 — 패치를 늘릴수록 upstream 변경 사항을 따라가기 어려워진다.

### Step 5. `THIRD_PARTY_LICENSES.md` 등록

레포 루트 `THIRD_PARTY_LICENSES.md`에 출처 항목을 추가한다. 형식은 기존 항목 참고.

### Step 6. `vulcan.py` `FRAMEWORK_FILES` 등록

`vulcan.py`의 `FRAMEWORK_FILES` 리스트(현재 vulcan.py:790-822)에 새 스킬 경로를 추가하고, init 시 출력하는 카운트(`skills N`)도 함께 갱신한다.

### Step 7. README의 가로축 스킬 표 갱신

`README.md`의 "가로축 스킬" 표에 한 행 추가. 자동 발화 시점과 출처를 명시한다.

---

## 8. 등록과 검증 체크리스트

새 스킬을 추가한 후 다음을 모두 통과해야 머지한다.

- [ ] 임시 디렉토리에 `python vulcan.py init <tmp> Test`를 실행해 `.claude/skills/<name>/skill.md`가 정상 복사되는지 확인
- [ ] 임시 디렉토리에서 `.claude/skills/<name>/`을 삭제 후 `python vulcan.py upgrade`를 실행해 복원되는지 확인 (FRAMEWORK_FILES 등록 검증)
- [ ] 새 Claude Code 세션에서 description의 주요 트리거 키워드를 입력해 자동 발화 여부 확인
- [ ] 기존 스킬과 트리거 충돌이 없는지 확인. 충돌이 있으면 양쪽 description의 `NOT for` 절로 경계를 명시한다.
- [ ] (외부 출처) `THIRD_PARTY_LICENSES.md`에 항목 추가
- [ ] `README.md`의 가로축 스킬 표 갱신
- [ ] 5절 Vulcan 5-Gate 통합 검증 5개 항목 모두 통과

---

## 9. 자주 묻는 질문

**Q. 새 도메인 지식을 추가하고 싶다. 스킬과 룰 중 어느 것을 만들어야 하나?**
A. *워크플로우*면 스킬, *강제 규약*이면 룰이다. "이렇게 디버깅해라"는 스킬, "Gate 1 산출물에는 REQ-ID가 반드시 있어야 한다"는 룰.

**Q. 새 역할이 필요하면 에이전트를 추가해야 하나, 스킬을 추가해야 하나?**
A. *주체*가 필요하면 에이전트, *절차*가 필요하면 스킬. 보통 새 에이전트는 5-Gate 책임 분배를 다시 그리는 큰 변경이다. 가능하면 기존 에이전트가 새 스킬을 호출하도록 설계하라.

**Q. description이 1024자를 넘으면?**
A. 제외 조건(`NOT for`)을 더 압축하거나, 트리거 키워드를 카테고리로 묶어라. 그래도 안 되면 스킬이 너무 광범위한 것이다 — 분할을 검토하라.

**Q. 한국어 트리거가 잘 안 걸린다.**
A. (1) description의 "Use when" 절을 사용자의 *실제 발화*에 가깝게 다시 써라. 추상화하지 말고 그대로. (2) 동의어를 한 절에 묶어라. 예: "'Gate 1 시작', '요구사항 정의', '스펙 작성'을 요청할 때". (3) 명령형보다 명사형이 더 잘 매칭된다.

**Q. 가로축 스킬 본문을 한국어로 번역해도 되나?**
A. 권장하지 않는다. 유지보수 비용이 두 배가 되고, upstream 업데이트를 따라가기 어려워진다. description만 한국어가 필요하다면 description은 한국어, 본문은 영어로 두는 분리도 가능하다.

---

## 부록: 참고 자료

- 외부 참고: [addyosmani/agent-skills `docs/skill-anatomy.md`](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md) (MIT)
- Vulcan 내부 참고:
  - 세로축 예시: `templates/.claude/skills/vulcan/skill.md`, `templates/.claude/skills/security-baseline/skill.md`
  - 가로축 예시: `templates/.claude/skills/debugging-and-error-recovery/skill.md`
  - 라이선스 관리: `THIRD_PARTY_LICENSES.md`
  - 업그레이드 동기화 로직: `vulcan.py` `FRAMEWORK_FILES` (vulcan.py:790-822)
