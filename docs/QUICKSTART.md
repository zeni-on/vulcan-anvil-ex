# Quickstart

Vulcan-Anvil Ex를 처음 볼 때는 모든 Gate와 문서를 한 번에 이해하려고 하지 않아도 됩니다.
먼저 다음 네 가지만 잡으면 됩니다.

1. 어떤 profile로 시작할지 고른다.
2. `init`으로 프로젝트를 만든다.
3. 메인 Orchestrator에게 프로젝트 규칙을 먼저 읽게 한다.
4. Dashboard나 `status`로 현재 위치를 확인한다.

## 1. Profile 선택

| 만들고 싶은 것 | 추천 profile | 남는 것 |
| --- | --- | --- |
| 아이디어나 기술이 되는지 확인 | `poc` | 목표, 가설, 반복 기록, smoke/demo 결과 |
| 제품/업무 앱을 계속 개발 | `product` | 제품 요구사항, 주요 설계, 계약, 회귀/릴리즈 기록 |
| 감리, 고객 검수, 인수인계 대응 | `audit` | 요구사항, 상세 설계, 테스트, QA 증적, 변경관리 |

Profile은 품질 등급이 아닙니다.
문서 깊이와 증적 밀도, 승인 절차의 차이입니다.
Product는 `docs/product/` 원장 6종으로 시작하고, API/DB/UI/보안/개발표준 상세가 필요해질 때만 `docs/artifacts/02-design/...` 아래에 Product 경량 상세 문서를 추가합니다.

## 2. 프로젝트 만들기

```powershell
python vulcan.py init ../my-poc "My PoC" --profile poc
python vulcan.py init ../my-product "My Product" --profile product
python vulcan.py init ../my-audit-project "My Audit Project"
```

기본값은 `audit`입니다.
GitHub 원격 저장소와 함께 시작하려면 `--remote`를 추가합니다.

```powershell
python vulcan.py init ../my-project "My Project" --remote https://github.com/<owner>/my-project.git
```

## 3. 메인 Orchestrator 시작

생성된 프로젝트 폴더를 Codex, Claude, Antigravity/Agy 같은 에이전트 환경에서 열고 먼저 이렇게 말합니다.

```text
안녕.. 너는 메인 오케스트레이터로써 이 프로젝트를 잘 이끌어가야해..
그에 대한 내용이 여기에 있으니 한번 전체적인 내용을 확인해줘.
```

그 다음 목표를 말합니다.

```text
단일 사용자 TODO 앱을 만들고 싶어.
```

Orchestrator는 바로 코딩하기보다 현재 Gate, profile, 필요한 질문, 승인 지점을 먼저 확인해야 합니다.

## 4. 현재 상태 확인

터미널에서는 프로젝트 폴더에서 다음 명령을 씁니다.

```powershell
python vulcan.py status
python vulcan.py status --check
```

Dashboard를 쓰면 같은 정보를 화면으로 볼 수 있습니다.

```powershell
cd dashboard
npm install
npm run dev
```

브라우저에서 `http://127.0.0.1:3001`을 열고 프로젝트 폴더를 등록합니다. Dashboard는 기본적으로 이 PC에서만 접근할 수 있습니다. 토큰과 프로젝트 경로 제한은 [Dashboard Guide](DASHBOARD_GUIDE.md)를 참고합니다.

## 5. Dashboard에서 먼저 볼 것

| 화면 | 봐야 할 것 |
| --- | --- |
| Gate/Status | 지금 어느 단계인지, 다음 승인 지점이 무엇인지 |
| Documents | 요구사항, 설계, QA 결과 문서가 실제로 채워졌는지 |
| Runs/Workers | worker나 subagent가 무엇을 했고 Orchestrator가 재검증했는지 |
| Evidence | 테스트 로그, 화면 캡처, QA 결과가 연결되어 있는지 |
| Trace Explorer | 특정 REQ/API/UI ID가 어떤 설계, 코드, 테스트와 이어지는지 |
| Comments | 문서를 보다가 남긴 질문이나 수정 요청이 열려 있는지 |

## 6. 처음에 헷갈리기 쉬운 것

- Ex는 한 번의 프롬프트로 앱을 가장 빨리 만드는 도구가 아닙니다.
- Ex는 AI가 만든 결과를 요구사항, 설계, 테스트, 증적, 승인 흐름으로 회수하는 도구입니다.
- PoC도 실패나 미실행 항목을 `Pass`로 쓰지 않습니다. 대신 결과와 다음 판단으로 남깁니다.
- Product와 Audit은 문서가 더 많지만, 그만큼 유지보수와 검수에 필요한 근거가 남습니다.
- Dashboard 코멘트는 원본 Markdown에 직접 들어가지 않고 `.vulcan/comments/comments.jsonl`에 저장됩니다.

더 자세한 절차는 [Getting Started](GETTING_STARTED.md), profile 선택은 [Which Profile Should I Use?](WHICH_PROFILE_SHOULD_I_USE.md), 실제 샘플 결과는 [Examples And Benchmarks](EXAMPLES_AND_BENCHMARKS.md)를 참고합니다.
