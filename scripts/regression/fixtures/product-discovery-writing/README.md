# Product Discovery Writing Example

업무 분석에서 요구·AC·시험 계획으로 연결하는 작성 예시다. 완성 제품, 실행 결과, 승인된 업무 기준선이 아니다. session/code/실행 증적은 없으며 기존 completed fixture를 대체하지 않는다.

1. [Brief](docs/product/PRODUCT_BRIEF.md)에서 제품 경계와 시나리오 후보를 본다.
2. [업무 흐름](docs/artifacts/01-requirements/requests-flow.md)에서 확인된 규칙·예시와 미정 질문을 구분한다.
3. [요구·AC 후보](docs/artifacts/01-requirements/requests.md)는 같은 규칙 원본을 링크하며 정의 본문은 한 곳에 둔다.
4. [시험 계획 후보](docs/artifacts/03-test/resubmit.md)는 입력·행동·기대값과 방법을 적지만 실행/Pass를 주장하지 않는다.

가상 요청 보드 대화에서 사용자가 선택한 것은 기존 요청 보완·재제출과 반려 당시 내용·사유 보존이다. 재제출/재검토 권한, 공개 시점, 이력 조회·보존 기간은 아직 미정이다. 여기의 ID는 독립된 합성 예시 안의 번호이며 기존 예시 프로젝트의 번호를 배정/변경한 것이 아니다.

회귀 시험은 이 파일들을 임시 폴더로 복사한다. 원본 후보가 구현 대상으로 인정되지 않는지 먼저 검사하고, 별도 합성 채택 조건에서 링크·ID·Planned 계획이 읽히는지만 검사한다. 합성 채택은 사용자의 실제 업무 결정이나 구현 허가가 아니다. UI/API/DB 실제 실행은 다음 마무리 범위다.

공통 운영 기준: [Product Document Writing](../../../../docs/core/PRODUCT_DOCUMENT_WRITING.md). 대화 출처와 남은 질문: [Request Board Pilot](../../../../docs/reference/PRODUCT-DISCOVERY-PILOT-REQUEST-BOARD.md).
