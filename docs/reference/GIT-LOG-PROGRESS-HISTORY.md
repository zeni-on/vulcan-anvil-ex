# Git Log 기반 날짜별 진행 이력 구상

## 1. 목적

Vulcan-Anvil Ex는 이미 `session.json.stats`로 현재 상태 통계를 가진다.

이 문서는 별도 진행률 저장소를 추가하지 않고, Git 이력을 기준으로 날짜별 진척사항을 파생해 Dashboard나 보고서에서 보여주는 방향을 정리한다.

## 2. 원칙

- 새로운 `progress-history.jsonl` 같은 이력 저장소를 기본 도입하지 않는다.
- 현재 통계는 `session.json.stats`를 기준으로 본다.
- 날짜별 진행 이력은 Git commit 날짜와 commit message에서 파생한다.
- 진행 중 통계는 일부 흔들릴 수 있음을 허용한다.
- 감리/보고 관점에서 중요한 것은 "언제 어떤 상태 변화가 있었는가"를 설명할 수 있는 것이다.
- 파생 이력은 보조 관찰 자료이며, Gate 완료/승인 사실의 최종 근거는 `session.json`, Run 문서, QA 문서, Git commit이다.

## 3. 입력 데이터

1차 구현은 다음 입력만 사용한다.

- `git log --date=iso`
- commit hash
- commit date
- commit subject
- 필요 시 현재 `session.json.stats`

Run 문서, Review 문서, QA 결과서 본문까지 파싱하는 것은 후순위로 둔다.

## 4. Commit Prefix 분류

처음에는 commit subject의 prefix만 가볍게 분류한다.

| Prefix / 패턴 | 분류 | 의미 |
| --- | --- | --- |
| `session:` | Gate / Session | Gate 시작, 승인대기, 완료, branch 시작 같은 상태 변화 |
| `wave:` 또는 `session: wave` | Build Wave | Build Wave 시작/완료/검증 |
| `review:` | Review | 독립 검수, 교차검증, 리뷰 결과 반영 |
| `feat:` | Implementation | 기능 구현 또는 실행 기능 추가 |
| `fix:` | Fix / QA Fix | 결함 수정, QA 보완, 대시보드 수정 |
| `docs:` | Documentation | 산출물, Core, Adapter, Roadmap 문서 보강 |
| `chore:` | Maintenance | 릴리즈 준비, 설정, 정리, 버전 관리 |
| `release:` 또는 tag | Release | 릴리즈, 태그, 릴리즈 노트 |
| 기타 | Other | 분류되지 않은 작업 |

분류는 완벽하지 않아도 된다. 목적은 정밀 회계가 아니라 날짜별 흐름 요약이다.

## 5. 날짜별 집계 예시

Dashboard나 CLI는 Git log를 날짜 단위로 묶어 다음처럼 표시할 수 있다.

| 날짜 | Gate/Session | Wave | Review | Impl/Fix | Docs | Release | 주요 메시지 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026-05-24 | 2 | 1 | 1 | 2 | 3 | 0 | Gate 4 QA 보강, worker 실행 정리 |
| 2026-05-25 | 1 | 0 | 0 | 1 | 4 | 1 | v0.3.0 릴리즈, Roadmap 정리 |

날짜별 상세를 펼치면 해당 날짜의 commit subject 목록을 보여준다.

```text
2026-05-25
- release: v0.3.0
- docs: clarify integration branch role
- docs: add orchestrator kickoff prompt
- fix: improve dashboard mermaid diagram contrast
```

## 6. Dashboard 표현 방향

처음에는 별도 대형 화면을 만들지 않는다.

권장 1차 UI:

- 기존 오른쪽 `커밋` 탭을 유지한다.
- 탭 내부 상단에 "날짜별 진행 요약" 작은 섹션을 추가한다.
- 최근 7일 또는 최근 10개 날짜만 표시한다.
- 각 날짜는 분류별 count와 대표 commit subject 1~2개만 보여준다.
- 날짜를 클릭하면 그 날짜 commit 목록을 펼친다.

예:

```text
진행 이력

2026-05-26
Docs 2 · Fix 1 · Session 1
Roadmap 정리, Mermaid contrast 수정

2026-05-25
Release 1 · Docs 3
v0.3.0 릴리즈
```

## 7. CLI 방향

필요하면 나중에 얇은 읽기 전용 명령을 추가한다.

```bash
python vulcan.py progress-report
```

이 명령은 파일을 생성하지 않는다.
Git log와 현재 `session.json.stats`를 읽어 콘솔에 요약만 출력한다.

옵션 후보:

```bash
python vulcan.py progress-report --since 14d
python vulcan.py progress-report --format json
```

## 8. 하지 않을 것

초기 구현에서는 다음을 하지 않는다.

- 모든 Vulcan 명령마다 progress snapshot 저장
- 별도 progress DB 또는 JSONL 파일 생성
- 커밋 메시지 본문 전체의 복잡한 자연어 파싱
- Run/Review/QA 문서 본문 전체를 매번 스캔
- 현재 진행률을 정확한 일별 회계처럼 보장

## 9. 확장 후보

나중에 필요하면 다음을 추가할 수 있다.

- tag/release와 날짜별 진행 이력 연결
- Gate 완료 커밋만 따로 필터링
- Build Wave 완료 이벤트 강조
- QA 실패/수정 반복 횟수 표시
- GitHub PR/issue 이벤트 병합
- 보고서용 Markdown export
