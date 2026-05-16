# 개발표준 검토 Skill

## 사용할 때

Gate 2에서 Gate 3로 넘어가기 전, 또는 Gate 4 구현 검수 시 사용한다.

구현 전에 개발표준정의서가 확정되었는지, build persona가 일관된 방식으로 코딩할 수 있는 기준이 충분한지 검토한다.

## 필수 입력

- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/SECURITY_BASELINE.md`
- `docs/core/TECH_STACK_BASELINES.md`
- `docs/templates/DEVELOPMENT_STANDARD_TEMPLATE.md`
- 관련 개발표준정의서
- 관련 프로그램명세서
- 관련 테스트케이스

## 절차

1. 개발표준정의서 상태가 Draft 또는 템플릿 플레이스홀더 상태인지 확인한다.
2. 언어, 런타임, 프레임워크, DB, 테스트 도구, 빌드/패키지 방식이 확정되었는지 확인한다.
3. 선택한 기술스택이 `TECH_STACK_BASELINES.md`의 어떤 섹션을 따르는지 확인한다.
4. Spring Boot/Spring Security/React/Next.js/Vue/FastAPI 등 선택 스택별 패키지 구조와 계층 책임이 구현자가 바로 따를 수 있을 만큼 구체적인지 확인한다.
   - Spring Boot라면 base package, MVC 계층, feature 우선 패키지 구조, JPA Entity/DTO 분리, transaction 기준, repository/query 기준이 명시되어야 한다.
5. 메시지 리소스, 예외 처리, 로그, 설정값, 외부 의존성 규칙이 있는지 확인한다.
6. 주석 컨벤션과 추적 ID 표기 규칙이 있는지 확인한다.
7. 보안 구현 기준이 `SECURITY_BASELINE.md`의 관련 항목과 연결되어 있는지 확인한다.
8. 단위/통합/UI/성능 테스트 파일명, 함수명, 필수 검증 명령, 실행 시점, 결과 기록 위치, 증적 기준이 있는지 확인한다.
9. 베이스라인과 다른 선택이 있으면 사유가 기록되어 있는지 확인한다.
10. 누락이 기존 설계 범위 안이면 `FIND`, 기술스택 또는 범위 변경이면 `CR`로 분류한다.

## 출력

다음을 반환한다.

- 개발표준정의서 상태
- 확정된 기술스택, 적용 베이스라인, 패키지 구조
- 누락된 코딩/주석/테스트/보안 기준
- build persona가 구현 가능한지 여부
- `FIND` 또는 `CR` 권고
