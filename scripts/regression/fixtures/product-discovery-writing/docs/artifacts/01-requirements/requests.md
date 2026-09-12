# Resubmission Requirements

미정 권한·상태가 있으므로 아래 요구·AC는 후보이며 구현 허가가 아니다. 사용자의 두 선택에서 도출한 기대 결과를 관측 가능하게 적는다.

## REQ-001
<!-- vulcan:state=candidate -->

| REQ ID | 요구 동작 |
| --- | --- |
| REQ-001 | 반려 요청을 보완해 같은 요청에서 재제출하고, 반려 당시 내용과 사유를 보존한다. |

### Conditions And Exceptions

업무 의미와 예시는 [규칙 원본](requests-flow.md#rules-and-examples)을 따른다. 권한·상태·보존 정책의 미정 사항은 [열린 결정](requests-flow.md#open-decisions)에서 확인한다. 이 미정 사항은 관련 요구 확정에 영향을 준다.

### Acceptance Criteria

| AC ID | 조건 / 행동 | 관측 가능한 인수조건 |
| --- | --- | --- |
| AC-001 | 반려된 '장비 필요'를 '장비 2대 필요'로 보완해 재제출 | 같은 요청에서 최신 내용을 확인한다. |
| AC-002 | 위 재제출 후 이전 내용·사유와 최신 내용을 비교 | 이전 '장비 필요', 반려 사유 '수량을 알려주세요', 최신 '장비 2대 필요'가 구별된다. |
