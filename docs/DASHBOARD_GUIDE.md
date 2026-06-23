# Dashboard Guide

Dashboard는 Vulcan-Anvil Ex 프로젝트를 사람이 읽기 쉽게 보여주는 로컬 UI입니다.
프로젝트를 대신 진행하거나 Gate를 자동 승인하는 도구가 아니라, Orchestrator와 사용자가 같은 상태를 보도록 돕는 화면입니다.

## 실행

Ex 저장소에서 Dashboard를 실행합니다.

```powershell
cd dashboard
npm install
npm run dev
```

브라우저에서 다음 주소를 엽니다.

```text
http://localhost:3001
```

그 다음 로컬 프로젝트 폴더 또는 GitHub 저장소 URL을 등록합니다.

## Dashboard가 읽는 것

Dashboard는 주로 다음 파일과 폴더를 읽습니다.

| 대상 | 의미 |
| --- | --- |
| `session.json` | 현재 Gate, profile, branch, 진행 상태 |
| `vulcan.config.json` | workflow, integration branch, runner 정책 |
| `docs/artifacts/` | 요구사항, 설계, 테스트, QA, 릴리즈 산출물 |
| `docs/product/` 또는 `docs/poc/` | Product/PoC profile의 핵심 문서 |
| `docs/runs/` | Run, Build Wave, QA Run, 위임 기록 |
| `.vulcan/comments/comments.jsonl` | Dashboard 문서 코멘트 |
| Git 커밋 | 최근 변경과 브랜치 상태 |

## 화면 읽는 법

| 영역 | 어떻게 보면 되는가 |
| --- | --- |
| Gate/Status | 현재 단계와 다음 승인 지점을 봅니다. `status --check`와 같은 판단을 화면에서 따라갈 수 있습니다. |
| 통계 | 요구사항, 테스트, 이슈, Build Wave 진행률의 빠른 요약입니다. 숫자가 이상하면 `python vulcan.py status --check`로 원인을 확인합니다. |
| 문서 목록 | 산출물이 실제로 채워졌는지 확인합니다. 긴 QA 결과서나 추적표는 요약 카드보다 Markdown 본문을 기준으로 봅니다. |
| Run/Worker | worker, subagent, native branch agent가 무엇을 했는지 봅니다. 완료 결과는 Orchestrator 재검증 전까지 후보로 봅니다. |
| Evidence | 테스트 로그, 화면 캡처, JSON/HTML report 같은 증적을 확인합니다. |
| Trace Explorer | 특정 ID를 선택해 요구사항, 설계, API, UI, 테스트, 증적의 연결을 봅니다. |
| Comments | 문서를 보다가 질문, 수정 요청, FIND 후보, CR 후보를 남깁니다. |

## Branch와 Worktree

Dashboard는 현재 등록한 물리 폴더의 Git checkout을 읽습니다.

| 표시 | 의미 |
| --- | --- |
| `branch` | Dashboard가 읽고 있는 폴더의 현재 브랜치 |
| `integration` | `vulcan.config.json.workflow.integration_branch` 값 |
| `Worktree` | `.vulcan/worktrees/` 아래 남은 worker/QA 작업공간 |
| `Runner` | 현재 감지된 Codex/Claude/Gemini runner 또는 최근 실행 정보 |

Worktree 목록은 "현재 작업 중"만 의미하지 않습니다.
worker가 끝난 뒤에도 검토, 삭제, 증적 확인을 위해 남아 있을 수 있습니다.

## 위임 기록

Dashboard는 Run 문서에 남은 `delegation_records`와 외부 CLI의 `Run Execution Record`를 읽어 위임 경로를 표시합니다.

| 표시 | 의미 |
| --- | --- |
| `Codex subagent` | Codex native subagent가 작업하고 Orchestrator가 재검증한 기록 |
| `Codex thread` | 별도 Codex thread/session에 위임한 기록 |
| `Agy branch` | Antigravity/Agy Workspace branch 또는 native branch agent 기록 |
| `External CLI` | `agent-run`/`run-exec` 같은 외부 CLI runner 실행 기록 |
| `Direct edit` | Orchestrator 직접 수정 사유가 기록된 작업 |
| `위임 경로 없음` | Run 또는 PoC 결과 문서에 실행 경로가 아직 기록되지 않은 상태 |

위임 기록이 없다고 해서 항상 오류는 아닙니다.
짧은 PoC 실험이나 사람이 직접 정리한 문서는 기록이 없을 수 있습니다.
다만 Product/Audit의 완료된 Build/QA Run에서 실행 경로가 비어 있다면, Orchestrator에게 위임 기록 또는 직접 수정 사유를 정리하도록 요청하는 것이 좋습니다.

## 문서 코멘트

Markdown 문서를 읽다가 수정 요청이나 질문이 있으면 문서 블록의 `+` 버튼으로 코멘트를 남깁니다.

코멘트는 원본 Markdown에 직접 쓰지 않고 다음 sidecar 파일에 저장됩니다.

```text
.vulcan/comments/comments.jsonl
```

Orchestrator는 작업을 시작할 때 `python vulcan.py status`의 `dashboard_comments` 요약을 보고 열려 있는 코멘트를 확인합니다.

상태는 단순하게 관리합니다.

| 상태 | 의미 |
| --- | --- |
| `open` | 아직 반영하거나 답변해야 하는 코멘트 |
| `closed` | 반영, 답변, 또는 별도 이슈화가 끝난 코멘트 |

## Evidence 확인

Gate 4 QA에서는 로그와 이미지가 특히 중요합니다.

| 증적 | 보는 방법 |
| --- | --- |
| `.log`, `.txt` | 문서 링크나 Evidence 목록에서 열어 명령 결과와 오류를 확인 |
| `.png`, `.jpg` | 화면 캡처가 실제 UI 상태를 보여주는지 확인 |
| `.json`, `.jsonl` | runner summary, transcript, structured report 확인 |
| `.html` | Playwright HTML report 같은 브라우저용 결과 확인 |

증적 링크가 깨졌다면 먼저 실제 파일이 프로젝트 안에 있는지 확인합니다.
링크 문법 문제인지, 파일 생성이 누락됐는지, Dashboard preview가 아직 지원하지 않는 형식인지 구분해야 합니다.

## 자주 생기는 상황

| 상황 | 확인할 것 |
| --- | --- |
| 통계가 맞지 않음 | 프로젝트 폴더에서 `python vulcan.py sync-session`, `python vulcan.py status --check` |
| Gate가 넘어간 것 같은데 Dashboard가 다름 | Dashboard가 읽는 폴더와 현재 Git 브랜치 확인 |
| worker가 끝났는데 화면에 남음 | Run 상태, activity summary, worktree 잔존 여부 확인 |
| 코멘트를 에이전트가 못 봄 | `.vulcan/comments/comments.jsonl` 존재 여부와 `python vulcan.py status` 출력 확인 |
| QA 증적이 안 보임 | 문서 링크 경로, 파일 확장자, 실제 파일 존재 여부 확인 |

Dashboard에서 이상해 보이는 값은 대부분 원본 문서, `session.json`, Git 상태 중 하나와 연결되어 있습니다.
화면만 고치기 전에 먼저 원본 상태를 확인하는 것이 안전합니다.
