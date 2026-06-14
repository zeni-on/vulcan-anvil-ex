# ORCHESTRATOR-CLI-SURFACE-STRATEGY-REVIEW-AGY

> Status: review v0.1  
> Date: 2026-06-08  
> Target Document: [ORCHESTRATOR-CLI-SURFACE-STRATEGY.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/reference/ORCHESTRATOR-CLI-SURFACE-STRATEGY.md)  
> Reviewer: Agy (Gemini Orchestrator)

---

## 1. 개요 및 총평

본 검토서는 `docs/reference/ORCHESTRATOR-CLI-SURFACE-STRATEGY.md`가 제시한 **4+1 상위 Facade 명령어 구조**로의 전환 제안에 대해, Agy(Gemini) 런타임의 최적화 모델 및 동적 서브에이전트 위임 관점에서 정합성과 효율성을 정밀 분석한 결과를 담고 있습니다.

### 핵심 결론
* **전략적 타당성 극대화**: 원자(Atomic) 단위의 명령을 삭제하지 않고 하위 호환성을 보존하면서 상위 Facade 래퍼(Wrapper) 레이어를 제공하는 방향은 **회귀 안전성과 인지적 복잡성 감소를 동시에 충족**하는 올바른 방향입니다.
* **Agy 런타임 정합성 보완**: Antigravity의 `invoke_subagent` 및 `Workspace: branch` 결합 구조와 논리적으로 완전히 합치하며, 특히 구현 전 `preflight` 강제 실행 누수를 차단하는 데 핵심적인 가교 역할을 할 것으로 기대됩니다.

---

## 2. Agy(Gemini) 관점에서의 특장점

### 2.1 TBD 설계 누수 자동 방지 (`execute --runner native`)
* **현상**: Agy native subagent 위임 시 CLI 실행기가 자동으로 기동되지 않아 `run-preflight` 검증 단계를 건너뛰고 TBD(인터페이스 미보강) 상태로 작업자가 스폰되는 누수 리스크가 존재했습니다.
* **효과**: `execute` Facade 명령어(예: `python vulcan.py execute --run-id RUN-012 --runner native`)가 내부 동작으로 `run-preflight`를 선제적으로 강제 실행하게 하면, TBD 문자열이 존재하는 시점에 위임 자체를 원천 차단할 수 있습니다.

### 2.2 비동기 통합 간소화 (`execute integrate`)
* 가상 격리 브랜치(`Workspace: branch` 모드)에서 작업한 변경 코드를 부모 워크스페이스로 병합하고, `delegation_records`와 출력 계약 스키마 정합성을 1차 자동 검증하는 과정을 단일 콘솔 명령으로 단순화할 수 있습니다.

---

## 3. 핵심 주의사항 및 리스크 진단 (Critical Warnings)

오케스트레이터의 동선 제어를 Facade로 단순화할 때, 자칫 오동작이나 정합성 훼손으로 이어질 수 있는 6가지 설계 맹점입니다.

> [!CAUTION]
> ### 1. 진단 로직의 이원화로 인한 불일치 리스크 (Single Source of Truth)
> * **위험**: `prepare-transition`과 `status --check` / `transition check`의 진단용 비즈니스 로직을 별개로 작성하거나 분리 복사할 경우, 시간이 지남에 따라 두 명령이 서로 다른 진단 결과를 출력하여 오케스트레이터의 오판을 유도할 수 있습니다.
> * **대응**: Facade 명령어는 자체 진단 로직을 격리 구현하지 말고, 기존 내부 함수(`check_trace`, `cmd_prepare_transition` 등)를 그대로 내부 래핑하여 진단 결과의 무결성을 유지해야 합니다.

> [!WARNING]
> ### 2. 암묵적 쓰기(Write) 동작으로 인한 부작용 (Side Effect)
> * **위험**: 상태를 조회하거나 단순 체크하기 위해 `transition check` 또는 `execute integrate`를 실행했을 때, 명시적 승인 없이 브랜치가 강제 전환되거나 세션 상태가 갱신되어 버리는 부작용이 발생할 수 있습니다.
> * **대응**: 상태를 직접 변경하거나 Git 상태에 영향을 주는 Facade 명령의 기본(Default) 동작은 반드시 `dry-run` 또는 `read-only`여야 하며, 실제 반영을 수반할 때는 `--apply` 플래그를 필수로 지정하게 하거나 사용자 명시 지시가 있을 때만 활성화해야 합니다.

> [!IMPORTANT]
> ### 3. Profile별 엄격도 분기 설계의 과도한 복잡화
> * **위험**: `audit`, `product`, `poc` 등 프로필에 따른 검사 강도 및 차단/경고 필터링을 Facade 내부의 IF-ELSE 분기로 관리하면 코드 유지보수성이 급격히 저하됩니다.
> * **대응**: Facade는 최대한 얇게(Thin) 유지하고, 검사 엄격도 판정은 `vulcan.config.json`의 `profile_rules` 정책이나 각 내부 검사 서브루틴(`run_preflight_file`) 내부로 격리하여 Facade에는 결과(`Pass`, `Warning`, `Block`)만 리턴해 주어야 합니다.

> [!NOTE]
> ### 4. 서브에이전트 통합 시 임시/무시 파일에 의한 오차단
> * **위험**: 워커가 가상 브랜치 내에서 빌드/테스트를 수행할 때 발생하는 린트 캐시, 컴파일 임시 파일(예: `__pycache__`, `.DS_Store`)이 변경 파일 목록에 묻어들어가 `scope.writable` 위반 차단(outside_writable_scope)이 걸리는 비효율이 존재합니다.
> * **대응**: `execute integrate`가 Git 상태를 분석할 때, `.gitignore`에 등록된 항목 및 불필요한 빌드 임시 파일들을 자동으로 제외(Sanitization)하는 규칙을 포함시켜야 합니다.

> [!NOTE]
> ### 5. 에러 추적성 상실로 인한 디버깅 맹점 (Black Box 현상)
> * **위험**: CLI 출력을 지나치게 축약하여 "통합 실패(Failed)"와 같은 상위 요약만 보여주면, 에이전트가 구체적인 컴파일 에러나 린트 경고의 내용을 인지하지 못해 후속 조치나 디버깅에 실패하게 됩니다.
> * **대응**: Facade 명령어 실행이 실패했을 때는 반드시 **실제 에러가 발생한 원자 명령의 CLI 커맨드라인과 상세 로그/증적 경로**를 콘솔에 함께 선명하게 출력해 주어야 합니다.

> [!WARNING]
> ### 6. 다중 작업 시의 레이스 컨디션 (Race Condition)
> * **위험**: 통합 브랜치(`dev`)가 깨끗하지 않거나(dirty) 다른 병렬 프로세스가 git index를 물고 있는 상황에서 `execute integrate --apply`가 무작위로 호출되면 파일 충돌이나 이력 유실이 발생할 수 있습니다.
> * **대응**: 통합 적용 전 항상 `git status`를 사전 확인하고, 충돌 가능성이 있는 경우 롤백을 보장하며 강제 중단되는 안전장치(Safety Guard)를 탑재해야 합니다.

---

## 4. Agy 기반 구현 가이드라인 제안

Facade 명령어가 개발되어 반영될 때, `agy` 오케스트레이터의 기본 호출 흐름은 다음과 같아야 합니다.

### ① 상태 진단 흐름
```text
오케스트레이터
  └─> python vulcan.py status --check
        ├─> [내부] prepare-transition 호출 및 차단 항목 수집
        └─> 통과 시: [추천] python vulcan.py transition start impl
            실패 시: [출력] 구체적 미통과 항목 (예: "TBD:signatures 가 docs/... 에 잔존")
```

### ② 작업 위임 및 preflight 연동 흐름
```text
오케스트레이터
  ├─> python vulcan.py plan run --skill build-wave ... (Run 초안 생성)
  ├─> [수동/스크립트] Program-Design 코드를 interface_contract에 주입
  └─> python vulcan.py execute --run-id RUN-012 --runner native
        ├─> [내부] run-preflight 자동 실행
        ├─> 차단 발견 시: 기동 중지 및 에러 출력 (TBD 누수 원천 차단)
        └─> 통과 시: invoke_subagent (Workspace: branch) API 호출 및 비동기 대기
```

---

## 5. 결론 및 향후 조치 사항

본 `ORCHESTRATOR-CLI-SURFACE-STRATEGY.md`에서 제시한 **Phase 1: `status` MVP 개발**은 즉시 착수하기에 충분한 타당성을 가지고 있습니다. 

위 6가지 주의사항(진단 함수 재사용, 기본값 dry-run, 예외 파일 필터링 등)을 설계 지침으로 유지하여 구현을 개시할 것을 권장합니다.
