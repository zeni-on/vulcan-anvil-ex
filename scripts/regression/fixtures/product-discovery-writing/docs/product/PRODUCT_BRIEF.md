# Request Board Brief

가상 팀 요청의 반려 후 보완 흐름을 검토하는 작성 예시다. 승인된 제품 명세나 구현 요청이 아니다.

## Goal And Boundary

| 항목 | 내용 |
| --- | --- |
| 문제 | 요청 등록·결정 기능이 있어도 반려 후 보완 경로가 없으면 업무를 끝낼 수 없다. |
| 제품 책임 후보 | 같은 업무 건의 보완 제출과 반려 내용·사유 보존. |
| 외부 책임 | 업무 규칙·접근권한·보존 기준의 결정은 사용자에게 남는다. |
| 이번 범위 | 보완 제출과 이력 보존의 의미·관측 조건 검토. |
| 제외 | 승인된 요청 수정, 결재자 자동 배정, 실제 구현·배포. |

## Sources

[업무 흐름과 열린 결정](../artifacts/01-requirements/requests-flow.md)
[요구·인수조건 후보](../artifacts/01-requirements/requests.md)

## Core Scenarios
<!-- vulcan:state=candidate -->

| Scenario ID | 시나리오 | 사용자 가치 | 관련 REQ |
| --- | --- | --- | --- |
| SCN-001 | 반려 요청 보완·재제출 | 기존 업무를 이어가면서 이전 반려 근거를 잃지 않는다. | REQ-001 |
