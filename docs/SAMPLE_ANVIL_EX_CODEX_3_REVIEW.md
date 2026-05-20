# sample-anvil-ex-codex-3 검토 메모

## 목적

`sample-anvil-ex-codex-3`는 Vulcan-Anvil Ex 프레임워크로 실제 생성한 예시 프로젝트이며, Codex를 메인 런타임으로 사용한 샘플이다.

이 문서는 해당 샘플 프로젝트를 훑어본 뒤, 프레임워크 실사용 예시로서의 장점, 아쉬운 점, 개선 방향을 정리한다.

검토 대상 경로:

```text
/home/zenion/projects/sample-anvil-ex-codex-3
```

---

## 한 줄 평가

`sample-anvil-ex-codex-3`는 단순히 Codex가 앱 하나를 만든 결과물이 아니라, Vulcan-Anvil Ex의 Gate, Run, Review, Traceability, QA Evidence, Approval 흐름을 실제로 한 바퀴 돌린 흔적이 강하게 남아 있는 샘플이다.

다만 현재 느낌은 "멀티에이전트 협업 샘플"이라기보다는 "Codex-main 단일 Orchestrator가 Vulcan 프로세스를 끝까지 수행한 샘플"에 가깝다.

---

## 확인한 주요 사실

### 프로젝트 상태

`session.json` 기준 전체 Gate가 완료되어 있다.

- Phase 0: done
- Gate 1: done
- Gate 2: done
- Gate 3: done
- Impl: done
- Gate 4: done
- Gate 5: done

기능 범위:

```text
로그인 회원가입 TODO 웹 애플리케이션
```

기술 스택:

- Spring Boot backend
- Vue frontend
- Spring Security
- JPA
- SQLite
- JWT cookie
- CSRF header
- Gradle
- Vitest
- Playwright

### 산출물 규모

검토 시점 기준 주요 산출물 수는 다음과 같았다.

- Run 문서: 22개
- Review 관련 Markdown: 6개
- QA 화면 증적 PNG: 20개
- Java main 파일: 29개
- Java test 파일: 12개
- Markdown 문서: 157개
- Markdown 라인 수: 약 21,756 lines
- Vue 단일 앱 파일: `frontend/src/App.vue` 1,161 lines

### 추적성 검사

다음 명령은 성공했다.

```bash
python3 vulcan.py check-trace
```

결과 요약:

```text
[check-trace] sample-anvil-ex-codex-3 - completed

Gate 진행 상태 검사: OK
문서 내용 경계 검사: OK
Phase 0 미결 항목 검사: OK

이슈 0건 - Gate 완료 가능합니다.
```

### 로컬 빌드 재현성 확인 결과

현재 검토 환경에서는 전체 빌드를 재현하지 못했다.

원인:

- `./gradlew` 실행 권한 없음
- `bash ./gradlew clean build` 실행 시 `JAVA_HOME` 또는 `java` 명령 없음
- frontend는 Node/NPM은 있으나 `node_modules`가 없어 `vitest: not found`

따라서 "현재 이 머신에서 테스트가 통과한다"까지는 확인하지 못했고, 저장소에 남은 QA 결과서, Playwright 증적, Run/Review 문서, 코드 구조를 기준으로 평가했다.

---

## 좋은 점

## 1. 프레임워크 실사용 예제로 설득력이 있다

이 샘플은 문서 템플릿만 있는 프레임워크가 아니라, 실제로 다음 흐름이 수행된 흔적을 보여준다.

1. Discovery
2. 요구사항 정의
3. 설계
4. 테스트 계획
5. Build Wave
6. 구현
7. QA
8. 독립 검수
9. 증적 보강
10. 최종 승인
11. 백로그 이월

특히 `docs/runs/`에 `RUN-001`부터 `RUN-022`까지 남아 있고, `session.json`에도 Gate별 완료 상태, 구현 Wave, 테스트 통계, 문서 통계가 기록되어 있다.

이는 "AI가 무엇을 했는지 나중에 추적할 수 있는가?"라는 질문에 대해 꽤 설득력 있는 답을 준다.

---

## 2. Codex-main 샘플이라는 점이 잘 드러난다

루트의 `AGENTS.md`가 Codex/GPT 런타임의 진입 문서로 잘 구성되어 있다.

인상적인 규칙:

- Claude 전용 파일을 기본 지침으로 보지 말라고 명시한다.
- Codex/GPT adapter 문서 우선순위가 있다.
- Run input/output contract를 따르도록 한다.
- Orchestrator가 구현 주작성자가 되지 않고 build persona/subagent를 사용하도록 한다.
- 구현자가 자기 구현을 최종 승인하지 않도록 review persona 또는 별도 환경 검수를 두라고 한다.

즉, Codex도 Vulcan-Anvil Ex의 1급 런타임으로 움직일 수 있다는 메시지가 분명하다.

---

## 3. 문서와 추적성이 강하다

요구사항추적표와 QA 문서가 상당히 촘촘하다.

연결된 ID 체계:

- REQ
- NREQ
- AC
- FUNC
- SCR
- UIREF
- UICON
- PGM
- API
- DB
- SEC
- UT
- IT
- UI

특히 `DOC-CORE-G4-001_Traceability-Matrix_v0.1.md`는 요구사항이 기능, 화면, 프로그램, API, DB, 보안, 테스트, UI 증적까지 어떻게 연결되는지 잘 보여준다.

일반적인 AI 코딩 샘플은 코드만 남기고 의사결정과 검증 근거가 사라지기 쉬운데, 이 샘플은 의사결정, 검증, 보강, 승인 흔적이 남아 있다.

---

## 4. QA Evidence가 좋다

Gate 4 QA 결과서에는 요구사항별 테스트와 증적이 연결되어 있다.

예:

- 로그인 기본 화면
- 로그인 실패
- 인증 사용자 재진입
- 로그아웃 후 보호 접근
- 회원가입 기본
- 필수값 오류
- 이메일 오류
- 비밀번호 오류
- 회원가입 성공
- TODO 목록
- TODO 빈 상태
- TODO 검색
- TODO 필터/정렬
- TODO 상세
- TODO 상세 검증 오류
- TODO 완료 토글
- 타 사용자 TODO 접근 차단
- TODO 삭제

Playwright screenshot이 UI ID와 연결되어 있어, Gate 4 QA 증적 샘플로 좋다.

---

## 5. 독립 검수에서 FIND가 나오고 보강된 점이 좋다

`RV-002` 독립 검수 결과가 무조건 PASS가 아니라 FIND로 나왔고, 이후 `RUN-021`에서 보강한 흐름이 기록되어 있다.

독립 검수에서 나온 주요 지적:

- Playwright 실행이 공식 UI 검증인지 불명확
- UI 증적 공백이 추적표 상태에 충분히 반영되지 않음
- 증적 수량 표현 불일치
- `npm run lint`가 실제로는 unit test alias였던 문제

이후 처리:

- Playwright 테스트를 공식 UI 검증으로 실행
- UI-ID 19건 screenshot 생성
- 추적표와 QA 결과서 보정
- `npm run lint`를 `vue-tsc --noEmit` 정적 타입 검사로 변경

이 흐름은 프레임워크의 장점을 잘 보여준다.

완벽한 척하는 샘플보다, 검수에서 문제가 나오고 이를 Run으로 보정하는 샘플이 훨씬 프레임워크답다.

---

## 6. 실제 앱 코드도 빈껍데기가 아니다

백엔드는 샘플치고 꽤 제대로 구성되어 있다.

확인한 구현 요소:

- BCrypt 비밀번호 저장
- JWT 기반 인증
- CSRF token header 필터
- 로그인 실패 기록
- 계정 잠금
- 사용자별 TODO ownership 체크
- 타 사용자 TODO 접근 시 404 처리
- 공통 오류 응답
- 단위/통합 테스트

예를 들어 `TodoService`는 `findByIdAndUser` 기반으로 소유권을 강제한다. 이는 단순 CRUD 예제보다 한 단계 높은 구현 판단이다.

---

## 7. UI가 생각보다 괜찮다

Playwright 증적 스크린샷 기준, TODO UI는 단순 CRUD 기본 화면이 아니라 명확한 디자인 톤이 있다.

느낌:

- 손글씨/노트/스티커 스타일
- 왼쪽 사이드바
- 중앙 TODO 목록
- 오른쪽 캘린더/진행도 패널
- 한국어 UX 문구
- 상태별 Playwright 증적 생성에 적합한 화면 구조

프레임워크 데모 목적에는 충분히 좋은 UI다.

다만 제품 코드라기보다는 "프로토타입 기반 UI를 실제 앱으로 옮긴 증적 샘플"에 가깝다.

---

## 아쉬운 점

## 1. 멀티에이전트 협업 느낌은 아직 약하다

`vulcan.config.json` 기준 independent runner가 `codex-cli`다.

즉 Codex가 메인으로 만들고, 독립 검수도 Codex CLI로 수행한 구조에 가깝다.

물론 독립 세션으로 실행되었다면 절차적 독립성은 어느 정도 있다. 하지만 외부에서 볼 때는 다음처럼 느껴질 수 있다.

> Codex가 만들고 Codex가 검수한 것 아닌가?

따라서 이 샘플은 다음을 보여주기에는 좋다.

- Codex-main으로 Vulcan 프로세스를 끝까지 수행 가능
- Run/Review 구조 작동 가능
- 독립 검수와 FIND 보강 루프 가능

하지만 다음을 보여주기에는 아직 약하다.

- 여러 AI 런타임이 역할 분담
- Codex build + Claude review
- Claude design + Codex implementation
- Gemini check 또는 별도 reviewer
- Dispatcher 기반 fan-out/fan-in

즉 Run-first 멀티에이전트 구조의 기반은 보이지만, 실제 멀티 런타임 협업 느낌은 아직 약하다.

---

## 2. `README.md`에 템플릿 흔적이 남아 있다

루트 `README.md` 첫 줄이 다음처럼 남아 있다.

```markdown
# {PROJECT_NAME}
```

작은 문제지만 샘플 프로젝트의 첫인상에는 꽤 크게 보인다.

추천 수정:

```markdown
# sample-anvil-ex-codex-3
```

또는:

```markdown
# Sample Anvil Ex Codex 3 - Login Signup TODO App
```

추가하면 좋은 내용:

- 이 샘플의 목적
- Codex-main으로 진행했다는 설명
- Gate 진행 요약
- 실행 방법
- 테스트 방법
- 산출물 보는 법
- 주요 증적 위치
- 알려진 백로그

---

## 3. `App.vue`가 너무 크다

`frontend/src/App.vue`가 1,161 lines로 크다.

데모/증적 생성용으로는 괜찮지만, 프레임워크가 만든 결과물이 유지보수 가능하다는 인상을 주려면 분리하는 편이 좋다.

추천 분리 예:

```text
frontend/src/components/AuthForm.vue
frontend/src/components/TodoList.vue
frontend/src/components/TodoDetail.vue
frontend/src/components/SidebarPanel.vue
frontend/src/components/CalendarPanel.vue
frontend/src/composables/useAuth.ts
frontend/src/composables/useTodos.ts
frontend/src/types/todo.ts
```

이 리팩토링은 기능 추가보다 "샘플 품질 개선" 성격이 강하다.

---

## 4. 빌드 재현성이 약하다

검토 환경에서 다음 문제가 있었다.

- `gradlew` 실행 권한 없음
- Java/JAVA_HOME 없음
- frontend dependencies 미설치

샘플을 외부에 보여줄 경우, 재현성을 높이기 위해 다음을 권장한다.

```bash
chmod +x gradlew
```

README에 다음을 명시한다.

```bash
# prerequisites
java -version
node --version
npm --version

# install frontend deps
cd frontend
npm install

# backend/frontend build
cd ..
bash ./gradlew clean build

# frontend checks
cd frontend
npm run test:unit
npm run lint
npm run build
npm run test:e2e
```

Docker 또는 devcontainer를 제공하면 더 좋다.

---

## 5. Windows path가 남아 있다

`session.json`에 다음과 같은 Windows 경로가 남아 있다.

```json
"vulcan_src": "C:\\Users\\user\\Documents\\antig-workspace\\vulcan-anvil-ex"
```

샘플 프로젝트를 여러 환경에서 보여줄 경우, 절대 경로보다는 상대 경로나 설명용 필드로 정리하는 편이 좋다.

예:

```json
"vulcan_src": "../vulcan-anvil-ex"
```

또는 샘플 export 시 해당 필드를 제거/마스킹하는 것도 고려할 수 있다.

---

## 6. `runtime.primary`가 null이다

`vulcan.config.json`에는 다음처럼 되어 있다.

```json
"runtime": {
  "primary": null
}
```

이 샘플이 Codex-main 샘플이라면 config 레벨에서도 명확히 표현하는 편이 좋다.

예:

```json
"runtime": {
  "primary": "codex-cli"
}
```

또는 향후 Run-first 구조를 고려하면 다음처럼 확장할 수 있다.

```json
"runtime": {
  "primary": "codex-cli",
  "orchestrator": "codex-cli",
  "runner_map": {
    "build": "codex-cli",
    "review": "codex-cli"
  }
}
```

다만 장기적으로는 특정 모델이 Orchestrator에 고정되는 구조보다 Run-first runner mapping으로 가는 것이 바람직하다.

---

## 개선 우선순위

## P0: 샘플 첫인상 개선

1. 루트 `README.md`의 `{PROJECT_NAME}` 수정
2. README에 샘플 목적, 실행 방법, Gate 결과 요약 추가
3. `gradlew` 실행 권한 부여
4. `session.json`의 Windows 절대 경로 정리

## P1: 재현성 개선

1. Java/Node prerequisite 명시
2. frontend dependency 설치 절차 명시
3. 전체 검증 명령 묶음 제공
4. 가능하면 Docker/devcontainer 제공

## P2: 코드 품질 개선

1. `App.vue` 컴포넌트 분리
2. auth/todo 상태 로직 composable 분리
3. frontend type 정의 분리
4. Playwright evidence helper 유지하되 테스트 의도 주석 보강

## P3: 멀티 런타임 샘플 강화

1. Codex-main + Claude-review 샘플로 확장
2. `vulcan.config.json`에 runner mapping 추가
3. Gate 2 또는 Gate 4 독립 검수를 다른 런타임으로 수행한 예시 추가
4. 향후 Dispatcher 기반 fan-out/fan-in 샘플로 발전

---

## 프레임워크 관점의 의미

이 샘플은 Vulcan-Anvil Ex의 핵심 가치 중 다음을 잘 보여준다.

- Gate 기반 진행
- Run 단위 작업 기록
- 요구사항-설계-테스트-증적 추적성
- 독립 검수와 FIND 보강
- QA Evidence 관리
- 릴리즈 승인 기록
- 후속 백로그 이월

특히 좋았던 점은 "문제가 없었다"가 아니라 "문제가 발견되고, Run으로 보강되고, 다시 승인되었다"는 흐름이 남아 있다는 것이다.

이것은 프레임워크형 개발 프로세스에서 매우 중요한 장점이다.

---

## 최종 평가

`sample-anvil-ex-codex-3`는 Vulcan-Anvil Ex가 실제 end-to-end 개발 프로세스를 굴릴 수 있다는 증거 샘플로는 꽤 성공적이다.

Codex-main으로도 Gate, Run, Review, Traceability, QA, Evidence, Approval 흐름이 돌아간다는 점을 보여준다.

다만 앱 코드 품질 샘플이라기보다는 프레임워크 운영 샘플에 가깝고, 멀티에이전트 협업 샘플보다는 Codex 중심 단일 Orchestrator 샘플에 가깝다.

대표 샘플로 더 설득력을 높이려면 다음을 우선 보강하는 것이 좋다.

1. README 정리
2. 빌드 재현성 보강
3. `App.vue` 분리
4. Codex-main + 다른 런타임 review 예시 추가
5. 향후 Run Queue + Dispatcher + Runner mapping 샘플로 확장

요약하면:

> 프레임워크의 가능성은 잘 보인다. 다음 버전에서는 README, 재현성, frontend 구조, runner 다양화를 보강하면 훨씬 설득력 있는 대표 샘플이 될 수 있다.
