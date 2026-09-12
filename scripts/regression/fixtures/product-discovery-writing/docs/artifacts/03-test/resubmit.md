# Resubmission Test Plan

가설·업무 예시를 시험 계획으로 연결한 후보이며 실행한 결과가 아니다. 실제 명령과 테스트 파일은 업무 합의/구현 허가 이후 구체화한다.

## Regression Plan
<!-- vulcan:state=candidate -->

요구/인수조건 원본: [REQ-001과 AC](../01-requirements/requests.md#req-001).

| REG ID | 관련 REQ / AC | 입력 / 행동 | Expected | Method | Status |
| --- | --- | --- | --- | --- | --- |
| REG-001 | REQ-001, AC-001 | 반려된 설명을 '장비 2대 필요'로 바꾸어 같은 요청에서 재제출 | 동일 요청의 최신 내용이 변경된다. | 실제 흐름에서 재제출 후 동일 요청 식별자와 최신 내용을 비교한다. | Planned |
| REG-002 | REQ-001, AC-002 | 위 재제출 후 이전 기록과 최신 기록을 비교 | 이전 내용·사유와 최신 내용이 서로 구별되어 남는다. | 이전 내용 '장비 필요'와 사유 '수량을 알려주세요'를 최신 내용과 assertion으로 비교한다. | Planned |

## Open Decisions
<!-- vulcan:state=candidate -->

권한·재검토 시점·보존 정책이 합의되면 그 영향에 맞춰 보안/예외 시험을 보완한다. 아직 전체 필수 시험이 확정되었거나 Pass라는 의미가 아니다.
