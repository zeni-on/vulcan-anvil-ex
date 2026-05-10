# Codex/GPT Skill

> 목적: Codex/GPT skill은 `AGENTS.md`가 참조하는 가벼운 작업 절차 카드다.

이 파일들은 Claude Code의 `.claude/skills`가 아니며 런타임 플러그인으로 취급하지 않는다.
Vulcan-Anvil Ex Run을 수행하기 전에 어떤 절차를 읽어야 하는지 정의한다.

## Skill 목록

| Skill | 사용할 때 |
| --- | --- |
| `traceability-review.md` | 산출물, 코드, 테스트, 증적이 ID로 연결되어 있는지 검토할 때 |
| `security-review.md` | 보안 설계, 보안 구현, 보안 테스트 커버리지를 검토할 때 |
| `data-standard-review.md` | 프로젝트 용어집, DB 명세, 데이터 명명, 공공데이터 표준 준수 여부를 검토할 때 |
| `qa-fix-loop.md` | 승인된 설계 범위 안에서 QA 발견사항을 수정할 때 |
| `change-impact-analysis.md` | 변경요청을 분석하거나 이슈를 CR로 승격해야 하는지 판단할 때 |

## 규칙

- skill 수행 결과는 `REQ`, `AC`, `FUNC`, `SCR`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`, `FIND`, `CR` 중 관련 ID와 연결한다.
- skill 수행 중 범위 누락이나 결함을 발견하면 `docs/core/CHANGE_CONTROL_PROCESS.md`에 따라 `ISSUE`, `FIND`, `CR`로 분류한다.
- 핵심 규칙을 이 디렉터리에 중복하지 않는다. 세부 기준은 `docs/core/`와 adapter 계약 문서를 참조한다.
