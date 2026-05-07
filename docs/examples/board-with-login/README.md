# 로그인 게시판 샘플

이 예제는 Vulcan-Anvil Ex의 Core 규칙과 템플릿이 실제 개발 시나리오에 맞는지 검증하기 위한 최소 샘플이다.

샘플 범위:

- 회원가입
- 로그인/로그아웃
- 게시글 목록 조회
- 게시글 상세 조회
- 게시글 작성
- 본인 게시글 수정
- 본인 게시글 삭제

샘플 목적:

- 요구사항정의서가 실제 기능을 충분히 표현하는지 확인한다.
- 요구사항추적표가 요구사항, 기능, 화면, 프로그램, DB, 보안, 테스트를 연결할 수 있는지 확인한다.
- 기능명세서가 구현 상세로 너무 빨리 내려가지 않으면서도 설계와 테스트로 이어질 만큼 충분한지 확인한다.

현재 샘플 산출물:

- `DOC-CORE-G1-001_Requirements-Spec_v0.1.md`
- `DOC-CORE-G4-001_Traceability-Matrix_v0.1.md`
- `DOC-CORE-G2-001_Function-Spec_v0.1.md`
- `DOC-DATA-G2-001_Project-Glossary_v0.1.md`
- `DOC-DATA-G2-002_Database-Spec_v0.1.md`
- `DOC-CORE-G2-002_Program-Spec_v0.1.md`
- `DOC-CORE-G2-003_Screen-Spec_v0.1.md`
- `DOC-QA-G3-001_Test-Cases_v0.1.md`
- `DOC-DEV-G2-001_Development-Standard_v0.1.md`
- `DOC-QA-G4-002_Test-Result_v0.1.md`
- `DOC-QA-G4-003_UI-Test-Result_v0.1.md`
- `evidence/ui/`: 화면별 브라우저 캡처 증적
- `sample-app/`: 문서 기반 FastAPI 샘플 구현

다음 검증 후보:

- 각 산출물이 너무 길어지는 지점을 확인하고 ID 단위 분리 구조를 설계한다.
- 단계별 에이전트 실행 프로토콜을 작성하고, 다음 에이전트가 산출물만 보고 이어받을 수 있는지 검증한다.
- 샘플 구현에서 발견된 `bcrypt`, pytest 임시 디렉터리, 메시지 리소스 규칙을 개발표준에 반영할지 검토한다.
