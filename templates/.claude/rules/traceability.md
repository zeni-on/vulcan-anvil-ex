---
paths:
  - "docs/TRACEABILITY.md"
---

# TRACEABILITY.md 업데이트 규칙

모든 Gate에서 산출물 작성 시 **반드시** TRACEABILITY.md를 업데이트한다.

## Gate별 업데이트 항목

| Gate | 담당 | 업데이트 내용 |
|------|------|-------------|
| Gate 1 | PM | REQ-NNN-NN 행 추가 (설계/테스트/리뷰 컬럼은 `-`) |
| Gate 2 | Architect | `설계 문서` 컬럼을 실제 파일명으로 채움 |
| Gate 3 | QA | `TST-ID` 컬럼에 매핑된 TST-ID 기입 (쉼표 구분) |
| Gate 4 | QA | `리뷰 문서` 컬럼 채움 + 상태를 `구현완료` 또는 `수정예정`으로 변경 |

**미등록 시 check-trace가 실패하여 해당 Gate 완료 불가.**
