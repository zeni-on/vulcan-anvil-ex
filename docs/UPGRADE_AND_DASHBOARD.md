# Upgrade And Dashboard

이 문서는 기존 Vulcan-Anvil Ex 프로젝트를 최신 규칙으로 갱신하는 방법과 Dashboard를 통해 진행 상태를 확인하는 방법을 정리합니다.

## 기존 프로젝트 업그레이드

이미 `init`으로 만든 프로젝트에 최신 Ex 규칙과 템플릿을 반영하려면 해당 프로젝트 폴더에서 `upgrade`를 실행합니다.

```powershell
cd ../my-project
python vulcan.py upgrade
```

`init`으로 만든 프로젝트는 `session.json`에 원본 Ex 저장소 경로를 기록하므로, 보통은 `upgrade` 명령에 Ex 폴더 경로를 따로 넘기지 않아도 됩니다.

Ex 저장소 위치를 옮겼거나 `session.json`의 `vulcan_src`가 더 이상 유효하지 않으면, 먼저 해당 값을 현재 Ex 저장소 경로로 맞춘 뒤 실행합니다.

## upgrade가 갱신하는 것

`upgrade`는 프로젝트를 새로 만드는 명령이 아닙니다. 목적은 기존 프로젝트의 작업 결과를 보존하면서, Ex 본체에서 개선된 운영 규칙을 반영하는 것입니다.

업데이트되는 항목은 다음과 같습니다.

- `vulcan.py`
- `AGENTS.md`
- `docs/core/`
- `docs/templates/`
- `docs/adapters/`
- `docs/seed-docs/`
- `.claude/` 런타임 규칙, agent, skill 파일
- `GATE_GUIDE.md`
- `docs/backlog/PROCESS.md`

보존되는 항목은 다음과 같습니다.

- `docs/artifacts/` 아래 실제 프로젝트 산출물
- `docs/runs/` Run 기록
- 프로젝트 코드와 테스트 코드
- `docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md`
- `docs/ref-docs/` 아래 민감 참고자료

`upgrade`는 없는 공식 산출물 템플릿은 새로 만들 수 있지만, 이미 작성된 산출물은 기본적으로 덮어쓰지 않습니다.

## Dashboard 실행

Dashboard는 Gate 진행 상태, 산출문서, Run, 구현 진행률, 테스트/백로그 통계, 최근 커밋을 한 화면에서 확인하기 위한 보조 UI입니다.

```powershell
cd dashboard
npm install
npm run dev
```

실행 후 브라우저에서 다음 주소로 접속합니다.

```text
http://localhost:3001
```

## 프로젝트 등록 방식

Dashboard에는 두 가지 방식으로 프로젝트를 등록할 수 있습니다.

| 방식 | 용도 |
| --- | --- |
| 로컬 경로 | 현재 PC의 프로젝트 폴더를 직접 확인 |
| GitHub URL | 원격 저장소의 문서와 커밋을 기준으로 여러 사람이 같은 상태 확인 |

로컬 경로는 개발 중인 PC에서 빠르게 확인할 때 편합니다. GitHub URL은 PL, 개발자, 검수자가 같은 프로젝트 상태를 공유할 때 유용합니다.

원격 저장소를 쓰려면 `init --remote`로 시작하거나, 프로젝트를 GitHub에 push한 뒤 Dashboard에서 저장소 URL을 등록합니다.

## Dashboard 통계 기준

Dashboard 통계는 다음 정보를 읽어서 표시합니다.

- `session.json`
- `docs/artifacts/`
- `docs/runs/`
- Git 커밋

진행률이 맞지 않을 때는 먼저 Orchestrator가 다음 명령을 제대로 실행했는지 확인합니다.

```powershell
python vulcan.py sync-session
python vulcan.py check-trace
```

Build Wave를 사용하는 구현 단계라면 `wave-start`, `wave-complete`, `sync-session` 흐름도 확인합니다.
