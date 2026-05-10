# 보안 검토 Skill

## 사용할 때

보안 요구사항, 보안 설계, 보안 구현, 보안 테스트 증적을 검토할 때 사용한다.

## 필수 입력

- `docs/core/REFERENCE_STANDARDS.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/templates/PROGRAM_SPEC_TEMPLATE.md`
- `docs/templates/SCREEN_SPEC_TEMPLATE.md`
- 관련 `SEC` 항목
- 필요한 경우 `docs/seed-docs/reference-standards/` 아래 공개 보안 표준 문서

## 절차

1. 관련 `REQ`, `NREQ`, `SCR`, `PGM`, `SEC` ID를 식별한다.
2. 설계 문서에 보안 통제가 반영되어 있는지 확인한다.
3. 구현이 승인된 보안 설계를 따르는지 확인한다.
4. 테스트가 보안 통제를 증명하는지 확인한다.
5. 승인된 범위 안의 미해결 보안 이슈는 `FIND`로 기록한다.
6. 보안 기준선, 인수기준, 설계 범위가 바뀌어야 하면 `CR`로 승격한다.

## 출력

다음을 반환한다.

- 검토한 보안 ID
- 사용한 보안 가이드 참조
- 누락되었거나 약한 통제 항목
- 테스트 커버리지 상태
- `FIND` 또는 `CR` 권고
