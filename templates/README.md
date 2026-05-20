# Project Seed Templates

이 디렉터리는 `vulcan.py init`이 새 프로젝트 루트에 복사하는 시드 파일을 보관한다.

## `docs/templates/`와의 차이

| 위치 | 역할 | 예 |
| --- | --- | --- |
| `templates/` | 새 프로젝트의 루트 파일과 기본 작업 폴더를 만드는 초기 시드 | `PROJECT_README.md`, `ENVIRONMENT.md`, `GATE_GUIDE.md`, `docs/backlog/PROCESS.md` |
| `docs/templates/` | Gate 산출물 문서의 공식 양식 | 요구사항정의서, 화면설계서, 개발표준정의서, 테스트결과서 |

`templates/`는 프로젝트 골격을 만들기 위한 재료이고, `docs/templates/`는 프로젝트 안에서 작성될 공식 산출물의 양식이다.

## 변경 기준

- 새 프로젝트가 처음 생성될 때 필요한 루트 안내 파일은 이 디렉터리에 둔다.
- Gate 산출물의 본문 구조, 메타데이터, 추적성 필드는 `docs/templates/`에 둔다.
- Core 규칙은 이 디렉터리에 복사하지 않고 `docs/core/`를 참조한다.
- Adapter별 실행 지침은 이 디렉터리에 두지 않고 `docs/adapters/`를 참조한다.
