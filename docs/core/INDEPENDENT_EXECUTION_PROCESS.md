# Independent Execution Process

> 상태: v0.1
> 목적: 독립 검수, Build Wave, Evidence Run을 같은 별도 세션/worktree 실행 모델로 다루기 위한 공통 규칙을 정의한다.

## 1. 개념

Independent Execution은 Orchestrator의 현재 대화 세션과 분리된 runner가 Run 계약을 읽고 작업하는 실행 단위다.

독립 검수와 독립 구현은 본질적으로 같은 구조다.
차이는 읽기 중심인지, 쓰기 중심인지, 그리고 어떤 source document와 scope를 받는지다.

| 실행 유형 | 목적 | 권한 | 대표 출력 |
| --- | --- | --- | --- |
| `review` | 산출물, 코드, 테스트, 증적을 독립 검수 또는 교차검증한다 | 읽기 중심, result 파일 작성 | `PASS`, `FIND`, `CR`, `ISSUE` 후보 |
| `pr-cross-validation` | PR diff, CI, 리뷰 코멘트, 관련 Run을 작성 runner와 다른 runner가 교차검증한다 | 읽기 중심, PR comment 또는 result 파일 작성 | merge 가능 후보, `FIND`, `CR`, `ISSUE` 후보 |
| `build` | 승인된 Build Wave 범위 안에서 구현한다 | 쓰기 중심, scope 제한 | 코드, 테스트, Run 결과, traceability delta |
| `evidence` | 테스트 로그와 화면 증적을 수집한다 | 쓰기 중심, evidence 경로 제한 | 테스트 결과, Playwright screenshot, 로그 |
| `qa-fix` | 승인된 FIND를 기존 설계 범위 안에서 수정한다 | 쓰기 중심, FIND 범위 제한 | 수정 코드, 재검증 결과 |

Runner는 Codex인지 Claude인지가 본질이 아니다.
Codex CLI, Claude CLI, GitHub reviewer, 수동 검수자는 모두 Run 계약을 수행하는 실행기다.

## 2. 공통 원칙

- Run은 먼저 파일로 존재해야 한다.
- Runner는 Run의 `source_documents`, `scope`, `completion_criteria`, `output_requirements`를 읽고 수행한다.
- Runner는 현재 Gate보다 앞선 산출물, 구현, 테스트, 증적을 임의로 만들지 않는다.
- 쓰기 작업은 Run의 writable scope 안에서만 수행한다.
- Review runner는 본선 산출물을 직접 수정하지 않고 result 또는 review 파일에 후보 판단을 남긴다.
- Build runner가 만든 결과는 Orchestrator가 다시 검토하고 통합한다.
- Runner 완료 보고만으로 Gate를 완료 처리하지 않는다.
- Worktree를 사용한 경우 결과 수집 후 사람이 확인하고 정리한다.

## 3. Runner 구분

| Runner | 비대화형 실행 기준 | 비고 |
| --- | --- | --- |
| `codex-cli` | `codex exec` | JSONL 로그와 last message 저장 |
| `claude-cli` | `claude -p` | `--output-format json`, `--model`, `--effort` 사용 가능 |
| `manual` | 사람이 result 파일 작성 | 정책, 승인, 일정 판단에 사용 |

Claude CLI는 Codex CLI처럼 별도 대화창을 여는 것이 아니라 비대화형 실행을 만들 수 있다.
따라서 `review-run`, 향후 `run-exec`의 runner로 사용할 수 있다.

기본 Claude 설정은 `claude-opus-4-7` + `high` effort를 사용한다.
Claude Code 공식 기준으로 Opus 4.7은 `low`, `medium`, `high`, `xhigh`, `max` effort를 지원한다.
`xhigh`가 Opus 4.7의 권장 기본값에 가깝지만, Ex 기본값은 비용과 안정성을 고려해 `high`로 둔다.

## 4. Review Execution

Review Execution은 기존 `INDEPENDENT_REVIEW_PROCESS.md`의 독립 검수와 같다.
사용자-facing 용어는 `교차검증`을 우선 사용하고, 기존 `independent review`는 호환 이름으로 유지한다.

```bash
python vulcan.py review-request --gate gate2 --title "Gate 2 설계 독립 검수"
python vulcan.py review-run --review-id RV-001 --runner codex-cli
python vulcan.py review-run --review-id RV-001 --runner claude-cli
```

Review runner는 request를 읽고 result 파일만 갱신한다.
결과는 자동 승인하지 않고 Orchestrator가 `FIND`, `CR`, `ISSUE`, 승인 후보로 다시 분류한다.

## 5. PR Cross Validation

PR Cross Validation은 Build runner가 만든 변경을 merge 후보로 보기 전에 작성 runner와 다른 runner가 검증하는 절차다.

PR 교차검증은 일반 Gate 산출물 검수와 다르게 다음 입력을 함께 본다.

- PR diff
- 관련 Build Wave Run
- 관련 요구사항, 설계, 테스트케이스, 개발표준
- CI 결과와 실패 로그
- 테스트 결과서와 Playwright 증적
- 추적표 delta
- PR 리뷰 코멘트와 unresolved thread

권장 분담:

| PR 작성 runner | 교차검증 runner | 중점 |
| --- | --- | --- |
| `codex-cli` Backend PR | `claude-cli` | API 계약, 보안 흐름, 예외/메시지, 테스트 누락 |
| `claude-cli` Frontend PR | `codex-cli` | UI Implementation Contract, 상태별 UI 테스트, 추적성, Playwright 증적 |
| Evidence/QA PR | 작성 runner가 아닌 review runner | 증적-테스트-추적표 1:1 연결, 미실행 테스트 Pass 여부 |

PR 교차검증 결과는 자동 merge 승인이 아니다.
Orchestrator가 결과를 다시 확인하고 다음 중 하나로 확정한다.

- merge 후보
- 수정 요청 `FIND`
- 기준선 변경 `CR`
- 사용자 판단 `ISSUE`

PR 교차검증 최소 체크:

- PR scope가 Run의 writable scope와 맞는가
- 관련 ID가 변경 파일, 테스트, 증적, 추적표에 연결되어 있는가
- 필수 검증 명령과 CI가 실행되었고 exit code가 기록되어 있는가
- 화면 변경은 Playwright 증적과 UI Implementation Contract 비교가 있는가
- 설계, 보안, 데이터, 개발표준 기준을 낮추는 변경이 숨어 있지 않은가
- 리뷰 코멘트나 CI 실패가 unresolved 상태로 남아 있지 않은가

## 6. Build Execution

Build Execution은 같은 독립 실행 모델을 구현에 적용한 것이다.
프론트엔드와 백엔드는 같은 `build` persona에 속하지만, 실제 실행에서는 서로 다른 Build Wave와 runner로 나누는 것이 권장된다.

권장 기본 분담:

| 영역 | 권장 runner | 이유 |
| --- | --- | --- |
| Frontend Build Wave | `claude-cli` | 화면설계서, UI Implementation Contract, 상태별 UI 테스트를 기준으로 화면/상태 구현에 집중한다 |
| Backend Build Wave | `codex-cli` | 개발표준, 패키지 구조, API/DB/보안/테스트 계약을 기준으로 서버 구현에 집중한다 |
| Evidence / Playwright QA | `codex-cli` 또는 `claude-cli` | 프로젝트 환경에서 Playwright 실행이 안정적인 runner를 선택한다 |

중요한 점은 runner 선호가 품질 보증을 대체하지 않는다는 것이다.
프론트엔드가 Claude에서 작성되어도 Playwright 증적과 UI Contract 검수는 필요하고, 백엔드가 Codex에서 작성되어도 개발표준/보안/테스트 검수는 필요하다.

권장 흐름:

1. Orchestrator가 `implementation-plan` Run을 만든다.
2. Build Wave별 Run을 만든다.
3. 각 Build Wave에 runner, writable scope, 관련 ID, 검증 명령을 부여한다.
4. runner가 별도 세션/worktree에서 수행한다.
5. Orchestrator가 변경 파일, 테스트 결과, traceability delta, FIND/ISSUE를 회수한다.
6. 필요한 경우 review/evidence Run을 만든다.

Worktree와 PR은 같은 것이 아니다.

- Review Execution은 보통 detached/readonly worktree에서 result 파일만 만들며 PR을 만들지 않는다.
- Build Execution은 브랜치 worktree에서 수행하는 것을 권장한다.
- Build runner 완료 후 Orchestrator가 변경 범위와 테스트를 확인한 뒤 draft PR을 만든다.
- PR이 만들어지면 작성 runner와 다른 runner가 교차검토한다.
- 예: `claude-cli`가 Frontend PR을 만들면 `codex-cli`가 설계, 테스트, traceability 관점에서 리뷰한다.
- 예: `codex-cli`가 Backend PR을 만들면 `claude-cli` 또는 별도 review runner가 API 계약, 보안, 테스트 증적 관점에서 리뷰한다.

초기 운영은 직렬 실행이 기본이다.
Backend Wave를 먼저 끝내고 API 계약을 고정한 뒤 Frontend Wave가 그 계약을 따라가는 방식이 충돌을 줄인다.
병렬 실행은 writable scope가 분리되고 fan-in review가 준비된 뒤 허용한다.

향후 명령 형태:

```bash
python vulcan.py run-exec --run-id RUN-010 --runner codex-cli
python vulcan.py run-exec --run-id RUN-011 --runner claude-cli
```

`run-exec`가 도입되기 전에는 Orchestrator가 Build Wave Run을 작업지시서로 만들고, Codex/Claude 세션 또는 CLI에 수동으로 전달할 수 있다.

## 7. 설정 방향

새 프로젝트의 `vulcan.config.json`은 독립 실행 기본값을 둘 수 있다.
`vulcan.py init`은 현재 PC에서 `codex`와 `claude` CLI 설치 여부를 확인하고, 사용 가능한 runner 목록을 설정에 기록한다.
절대 경로는 기록하지 않는다.
교차검증 가능 여부, 동시 worktree 가능 여부, persona별 runner 선택은 이 목록에서 Vulcan이 계산한다.

```json
{
  "runtime": {
    "primary": null,
    "available_runners": [
      {
        "name": "codex-cli",
        "model": "gpt-5.5",
        "effort": "high",
        "sandbox": "workspace-write",
        "version": "codex-cli 0.130.0"
      },
      {
        "name": "claude-cli",
        "model": "claude-opus-4-7",
        "effort": "high",
        "version": "2.1.142 (Claude Code)"
      }
    ]
  },
  "execution": {
    "independent_enabled": true,
    "default_worktree": true,
    "default_timeout_seconds": 2400
  }
}
```

기존 `review.independent_*` 설정은 호환을 위해 유지하되, 장기적으로는 `execution` 아래 공통 설정으로 수렴한다.

Runner 목록 해석:

| 조건 | 운영 방식 |
| --- | --- |
| runner 0개 | 자동 독립 실행 없이 manual 검수 중심으로 운영한다 |
| runner 1개 | 같은 runner의 별도 세션/worktree로 독립검수와 동시 작업을 수행한다 |
| runner 2개 이상 | 작성 runner와 검증 runner를 분리해 Gate, PR, QA 교차검증을 수행한다 |
| `codex-cli` + `claude-cli` | Backend는 Codex, Frontend는 Claude, 검증은 작성 runner와 다른 runner를 우선한다 |

예를 들어 Codex만 설치되어 있으면 교차검증은 아니지만 Codex CLI를 별도 세션/worktree로 실행해 독립검수와 동시 Build Wave를 수행할 수 있다.
Codex와 Claude가 모두 설치되어 있으면 Gate 2, PR, Gate 4에서 교차검증을 기본 운영 후보로 둔다.

## 8. Timeout과 runner 상태

Runner 실행은 timeout과 종료 상태를 반드시 기록한다.

기본값:

- review 실행: `review.independent_exec_timeout_seconds`, 기본 1800초
- build/evidence/qa-fix 실행: `execution.default_timeout_seconds`, 기본 2400초

실행 기록에는 다음 필드를 남긴다.

```yaml
executed_at: "2026-05-20T22:50:00"
deadline_at: "2026-05-20T23:30:00"
completed_at: "2026-05-20T23:12:10"
duration_seconds: 1330
timeout_seconds: 2400
timed_out: false
status: completed
exit_code: 0
result_file_changed: true
```

상태 해석:

| 상태 | 의미 | Orchestrator 조치 |
| --- | --- | --- |
| `completed` | runner가 정상 종료했고 결과 파일이 변경됐다 | 결과를 검토하고 반영 후보로 분류 |
| `completed_no_result_change` | runner는 정상 종료했지만 결과 파일을 쓰지 않았다 | 출력 로그를 확인하고 재실행 또는 수동 정리 |
| `failed` | timeout 전 비정상 종료했다 | stderr/stdout에서 인증, 토큰, 권한, 실행 오류 확인 |
| `timeout` | 지정된 timeout을 넘겨 프로세스가 중단됐다 | 부분 로그를 확인하고 Run을 쪼개거나 timeout을 조정 |

토큰 소진 여부는 모든 runner가 표준화해서 알려주지 않는다.
따라서 Vulcan은 토큰 소진을 직접 판정하지 않고, exit code, stderr/stdout, 마지막 응답, 결과 파일 변경 여부로 비정상 종료를 판단한다.
runner가 토큰 또는 사용량 한도 때문에 종료하면 보통 `failed`나 `completed_no_result_change`로 남고, Orchestrator가 로그에서 원인을 확인한다.

장시간 build/evidence 실행은 향후 `run-exec`에서 heartbeat 또는 streaming log의 `last_output_at`을 추가해 멈춤 상태를 더 빨리 감지할 수 있다.

## 9. Orchestrator 책임

Orchestrator는 runner보다 상위에 있다.

- Run 생성
- runner 선택
- worktree 생성 여부 결정
- 결과 회수
- 테스트/증적 재검증
- FIND/CR/ISSUE 분류
- 본선 산출물 반영 판단
- 사용자 승인 질문

Runner가 아무리 강해도 Orchestrator의 Gate 판단과 Human approval을 대체하지 않는다.
