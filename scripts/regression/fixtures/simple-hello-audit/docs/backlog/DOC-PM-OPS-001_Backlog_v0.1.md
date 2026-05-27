# regression-simple-hello 백로그

> 운영 규칙: [`PROCESS.md`](PROCESS.md) 참조
> 최종 갱신: 2026-05-24

## 범례

- **유형**: IDEA / FIND / CR / ISSUE / DEBT
- **레벨**: Trivial / Small / Major
- **우선순위**: P0 / P1 / P2 / P3
- **상태**: Proposed / Triaged / Scheduled / In Progress / Done / Rejected / Deferred
- **다시 진행할 Gate**: phase0 / gate1 / gate2 / gate3 / impl / gate4 / gate5 / none

---

## Active

| ID | 제목 | 유형 | 레벨 | 우선순위 | 상태 | 관련 ID | 다시 진행할 Gate | 관련 Run | 출처 | 비고 |
|----|------|------|------|---------|------|---------|-------------|----------|------|------|
| BL-001 | 선택 ruff E402 import order 정리 | ISSUE | Trivial | P3 | Proposed | ISSUE-QA-001,IT-001 | gate4 | RUN-019 | Gate 5 user approval: backlog ISSUE-QA-001 and approve release | backend/tests/test_hello_api.py에서 pytest.importorskip 이후 module import가 있어 ruff E402 4건 발생. 필수 QA 통과로 릴리즈 차단은 아니며 후속 QA Fix Loop 또는 정리 Run에서 처리. |

---

## Done

| ID | 제목 | 완료일 | 커밋 | 유형 | 레벨 | 관련 ID | 관련 Run |
|----|------|--------|------|------|------|---------|----------|
| — | (아직 없음) | — | — | — | — | — | — |

---

## Rejected

| ID | 제목 | 반려일 | 사유 |
|----|------|--------|------|
| — | (아직 없음) | — | — |

---

## Deferred

| ID | 제목 | 보류일 | 보류 사유 | 재검토 조건 |
|----|------|--------|-----------|-------------|
| — | (아직 없음) | — | — | — |

---

## 통계

- **Active**: 1건
- **Done**: 0건
- **Rejected**: 0건
- **Deferred**: 0건
