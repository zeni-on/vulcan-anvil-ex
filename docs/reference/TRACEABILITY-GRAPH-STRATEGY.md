# Traceability Graph Strategy

이 문서는 Vulcan-Anvil Ex의 요구사항 추적성을 문서별 ID 복사 방식에서 그래프 기반 조회/추천 방식으로 발전시키기 위한 구상이다.

## 문제

현재 산출물에는 요구사항, 기능, 화면, API, 프로그램, DB, 보안, 테스트, QA 이슈 ID가 여러 문서에 반복해서 들어간다.
이 방식은 문서 하나만 볼 때 관련 ID를 바로 확인할 수 있다는 장점이 있다.
하지만 AI agent가 문서를 작성하거나 수정할 때 다음 문제가 생길 수 있다.

- 같은 ID 관계를 여러 문서에 반복 입력하면서 누락이나 오기입이 생긴다.
- 요구사항 추가/수정 시 요구사항정의서, 기능명세서, 프로그램설계서, 테스트케이스, Run 문서를 모두 찾아 고쳐야 한다.
- Run 문서의 `related_ids`와 `target_contracts`가 agent의 수동 판단에 의존한다.
- parent REQ만 들어가고 상세 REQ/AC/TEST/UI ID가 빠지는 일이 생긴다.
- worker에게 실제 필요한 ID보다 너무 넓은 문서와 ID가 전달된다.

## 방향

요구사항 추적성은 트리가 아니라 그래프다.

- Node: `REQ`, `NREQ`, `AC`, `FUNC`, `SCR`, `UIREF`, `UICON`, `API`, `PGM`, `IF`, `MTH`, `DB`, `SEC`, `UT`, `IT`, `PT`, `UI`, `EV`, `FIND`, `CR`, `DEC`, `BL`, `RUN`, `RV`
- Edge: "이 ID는 저 ID를 만족한다", "이 API는 이 PGM으로 구현된다", "이 테스트는 이 요구사항을 검증한다" 같은 관계

전체 관계의 원장은 요구사항추적표가 담당한다.
개별 산출물은 자기 ID와 직접 upstream/downstream 관계만 명시한다.
전체 관계 확장, 영향도 분석, Run 입력 추천은 도구가 추적성 그래프를 파생해 수행한다.

초기 MVP에서 모든 node를 한 번에 구현하지 않는다.
1차 node는 `REQ`, `AC`, `FUNC`, `SCR`, `API`, `PGM`, `DB`, `SEC`, `UT`, `IT`, `UI`, `RUN` 정도로 제한하고, `IF`, `MTH`, `FIND`, `CR`, `RV`, `BL`, 외부 표준 ID는 2차 이후로 확장한다.

## Edge Type

그래프 관계는 단순한 "관련 있음"이 아니라 의미를 가진 edge로 구분한다.
edge type이 없으면 `trace-impact`와 Run 추천이 불필요한 ID까지 끌고 올 수 있다.

초기 edge type 후보는 다음과 같다.

| Edge type | 의미 | 예 |
| --- | --- | --- |
| `decomposes` | 상위 항목을 하위 상세 항목으로 분해 | `REQ-001 -> REQ-001-01`, `REQ-001-01 -> AC-001-01` |
| `satisfies` | 기능/설계가 요구사항 또는 AC를 만족 | `FUNC-001 -> REQ-001-01` |
| `implements` | 프로그램/API/DB/보안 설계가 기능을 구현 | `API-001 -> FUNC-001`, `PGM-001 -> API-001` |
| `verifies` | 테스트가 요구사항/AC/기능/설계를 검증 | `UT-001 -> PGM-001`, `IT-001 -> API-001`, `UI-001 -> SCR-001` |
| `evidence_of` | 증적이 테스트 또는 QA 결과를 뒷받침 | `EV-UI-001 -> UI-001` |
| `impacts` | FIND/CR/ISSUE/Backlog가 특정 ID에 영향 | `FIND-001 -> SEC-001`, `CR-001 -> API-001` |
| `documents` | Run/Review가 특정 ID를 다룸 | `RUN-014 -> PGM-001`, `RV-003 -> QA-001` |

`trace-context`는 edge type을 기준으로 결과를 필터링할 수 있어야 한다.
예를 들어 구현 Run 추천에서는 `decomposes`, `satisfies`, `implements`, `verifies`를 주로 사용하고, QA 증적 조회에서는 `verifies`, `evidence_of`, `impacts`를 우선한다.

## Node/Edge Status

각 node 또는 edge는 가능한 경우 상태를 가진다.

후보 상태:

- `Draft`
- `Designed`
- `Planned`
- `Implemented`
- `Verified`
- `Deferred`
- `Rejected`
- `Blocked`

상태는 추천 결과 필터링에 사용한다.
예를 들어 `Deferred` 또는 `Rejected` 항목은 기본 Run 추천에서 제외하고, `Verified` 항목은 재작업 대상이 아니라 영향 확인 대상으로만 표시한다.

## 원칙

1. **Traceability Matrix is the source of truth**
   - 모든 전체 관계는 요구사항추적표에 모은다.
   - 추적표는 감리/QA/릴리즈 기준의 전체 graph ledger 역할을 한다.

2. **Artifact documents keep local relationships**
   - 요구사항정의서, 기능명세서, 프로그램설계서, API 정의서, 테스트케이스 문서에는 해당 문서가 직접 책임지는 ID와 직접 관련 ID만 둔다.
   - 모든 downstream ID를 모든 문서에 복사하지 않는다.

3. **Run documents consume graph context**
   - Run의 `related_ids`, `target_contracts`, `source_documents`는 agent가 문서를 뒤져 수동 작성하기보다 trace graph query 결과를 기반으로 만든다.
   - 처음에는 추천값을 출력하고, 이후 `run-new`와 `wave-start`가 자동 반영하는 방식으로 발전시킨다.

4. **Dashboard uses the same graph**
   - Dashboard에서 ID를 클릭하면 직접 연결, 2단계 연결, 관련 문서, 관련 Run/Review/FIND/CR을 보여준다.
   - CLI와 Dashboard가 서로 다른 관계 해석을 갖지 않는다.

## CLI 후보

1차는 읽기 전용 query와 YAML 조각 출력으로 시작한다.

```powershell
python vulcan.py trace-context --id REQ-001-01 --depth 2 --direction downstream --emit yaml
```

예상 출력:

```yaml
seed_id: REQ-001-01
depth: 2
related_ids:
  - REQ-001-01
  - AC-001-01
  - FUNC-001
  - SCR-001
  - API-001
  - PGM-001
  - DB-001
  - SEC-001
  - UT-001
  - IT-001
  - UI-001
target_contracts:
  req: [REQ-001-01]
  ac: [AC-001-01]
  func: [FUNC-001]
  scr: [SCR-001]
  api: [API-001]
  pgm: [PGM-001]
  db: [DB-001]
  sec: [SEC-001]
  test: [UT-001, IT-001]
  ui: [UI-001]
source_documents:
  working_documents:
    - docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md
    - docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md
    - docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
warnings:
  - "scope.writable은 trace graph가 확정하지 않는다. Orchestrator가 Run 생성 전 직접 좁혀야 한다."
  - "interface_contract는 Program Design에서 별도 확인해야 한다."
```

`trace-context`는 처음에는 Run 문서를 직접 수정하지 않는다.
Orchestrator가 출력된 YAML 조각을 확인한 뒤 Run에 반영한다.

2차 이후에 Run 생성 명령과 연결한다.

```powershell
python vulcan.py run-new `
  --gate impl `
  --skill build-wave `
  --title "회원가입 API 구현" `
  --trace-seed REQ-001-01 `
  --trace-depth 2
```

이 경우 `related_ids`, `target_contracts`, 일부 `source_documents`를 trace graph에서 자동 추천한다.
다만 `target_contracts`, `interface_contract`, `scope.writable`은 자동 확정하지 않는다.
그래프는 추천만 하고, Orchestrator가 확인한 뒤 확정한다.

## MVP 단계

### MVP 1. CLI trace-context

목표:

- 요구사항추적표와 주요 산출물에서 ID와 관계를 파싱한다.
- `trace-context --id <ID> --depth <N> --emit yaml`로 Run 입력에 붙일 수 있는 추천 YAML을 출력한다.
- 출력은 읽기 전용이며 문서를 수정하지 않는다.

포함:

- `related_ids` 추천
- `target_contracts` 후보 분류
- 관련 문서 후보
- edge type과 direction 기준 필터
- status 기반 기본 제외(`Deferred`, `Rejected`)

제외:

- `run-new` 자동 주입
- Dashboard 그래프 시각화
- DB 저장

### MVP 2. Dashboard ID Trace Context

목표:

- Dashboard 문서 화면에서 ID를 클릭하면 Trace Context 패널을 연다.
- 직접 연결과 2단계 연결을 텍스트 목록으로 보여준다.
- 관련 문서와 관련 Run/Review/FIND/CR 후보를 표시한다.

포함:

- ID 검색
- 직접 연결/2단계 연결 구분
- 관련 문서 목록

제외:

- 복잡한 node-link 그래프 시각화
- Run 자동 생성 버튼

### MVP 3. Run 생성 추천 연동

목표:

- `run-new --trace-seed`, `wave-start --trace-seed`에서 trace graph 추천을 사용할 수 있게 한다.
- 자동 확정이 아니라 Orchestrator 확인을 전제로 한다.

원칙:

- `related_ids`는 자동 추천 가능
- `target_contracts`는 추천값으로 표시하되 Orchestrator 확정 필요
- `interface_contract`가 없으면 preflight warning 또는 blocker
- `scope.writable`은 graph가 확정하지 않으며 사람이 좁혀야 함
- QA Run에는 1차 적용하지 않는다. QA-000 workspace 같은 운영 상태는 trace graph 밖의 정보다.

### MVP 4. Graph Consistency Check

목표:

- `check-trace` 또는 별도 `trace-check`에서 추적표와 개별 문서의 관계 차이를 reconciliation report로 보여준다.

보고 유형:

- 추적표에만 존재하는 관계
- 개별 문서에만 존재하는 관계
- parent REQ만 있고 상세 REQ/AC가 빠진 관계
- 테스트 ID가 요구사항/AC와 연결되지 않은 상태
- Run의 `related_ids`가 trace graph 추천 범위와 크게 다른 상태

처음에는 warning으로 시작하고, Audit profile에서 단계적으로 차단 기준을 강화한다.

## Dashboard 후보

1차 Dashboard 기능:

- 문서 안의 ID를 클릭 가능하게 만든다.
- 클릭 시 Trace Context 패널을 연다.
- 직접 연결과 2단계 연결을 구분한다.
- 해당 ID가 등장하는 문서 목록을 보여준다.

예:

```text
Trace Context

REQ-001-01 회원가입

직접 연결:
- AC-001-01
- FUNC-001
- SCR-001

2단계 연결:
- API-001
- PGM-001
- DB-001
- SEC-001
- UT-001
- IT-001
- UI-001

관련 문서:
- Requirements Spec
- Function Spec
- API Spec
- Program Design
- Test Cases
```

2차 Dashboard 기능:

- ID 검색창
- 관련 FIND/CR/RUN/RV 표시
- "이 ID로 Run 만들기" 버튼은 MVP 3 이후에 검토한다.

3차 Dashboard 기능:

- depth 1~2 미니 그래프 시각화
- 큰 그래프는 전체 표시하지 않고 선택 ID 중심으로 잘라서 표시한다.

그래프 시각화는 유지보수 비용이 크므로 MVP 1~2에서는 제외한다.
초기에는 텍스트 목록 기반 Trace Context가 더 실용적이다.

## DB 필요 여부

당장 DB는 필수로 보지 않는다.

초기 구현은 다음 방식이 더 적절하다.

- 요구사항추적표 Markdown 파싱
- 주요 산출물의 ID 패턴 파싱
- 메모리 내 graph 구성
- `snapshot.json` 또는 Dashboard API 응답에 trace context 포함

DB가 필요한 시점은 다음과 같다.

- 프로젝트 문서가 커져서 매번 Markdown 파싱 비용이 커진다.
- Dashboard에서 ID 검색/그래프 탐색을 자주 수행한다.
- 여러 사용자가 동시에 trace graph를 조회하고 캐시가 필요하다.
- graph 변경 이력, edge confidence, source line reference를 별도 저장해야 한다.

그 전까지는 별도 DB보다 "파싱 가능한 Markdown + 파생 graph cache"가 단순하고 안전하다.

가능한 중간 단계는 하나로 통일한다.

- `snapshot.json.trace_graph`

추가 cache를 여러 개 두면 invalidation 정책이 복잡해지므로 초기에는 `snapshot.json`에 포함하는 방향을 우선 검토한다.
DB가 필요해지더라도 바로 graph DB로 가지 않고 SQLite의 `nodes`, `edges` 테이블 정도에서 시작한다.

## 검증 후보

향후 `check-trace`는 다음을 추가로 검사할 수 있다.

- 추적표에는 있는데 개별 문서에는 없는 직접 관계
- 개별 문서에는 있는데 추적표에는 없는 관계
- parent REQ만 있고 상세 REQ/AC가 빠진 관계
- 테스트 ID가 요구사항 또는 AC와 연결되지 않은 상태
- Run의 `related_ids`가 trace graph 추천 범위와 크게 다른 상태

이 검증은 처음부터 차단으로 두지 않고 warning으로 시작한 뒤, Audit profile에서만 점진적으로 강화한다.
