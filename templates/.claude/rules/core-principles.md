# Vulcan-Anvil 핵심 원칙

- 플래너는 코드를 쓰지 않는다. 실행자는 계획만 따른다.
- Gate 문서 없이 구현을 시작하지 않는다.
- 각 Gate는 사용자 승인 후 전환한다.
- session.json으로 Gate 상태를 추적한다.
- 에이전트가 명령어를 사용자에게 안내하는 것이 아니라 직접 실행한다.
- check-trace 실패 상태에서 Gate 전환 금지.
- **Gate 4 Blocker/Major 이슈는 백로그 이월 금지** — 현 Gate 내에서 해결한다 (`docs/06-backlog/PROCESS.md` §6).
- **증분 Gate Rollback을 우선** — 🟡/🔴 백로그 처리 시 `vulcan.py rollback --scope REQ-XXX`로 영향 범위를 명시한다. 전체 rollback은 scope를 특정할 수 없을 때만 사용한다.
- **Trivial 기준은 "문서 영향 없음"** — 시간이 짧아도 설계 문서에 반영할 결정을 포함하면 🟡이다.
