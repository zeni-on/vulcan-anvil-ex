# Codex Model Policy

> Status: draft v0.1
> Scope: Codex native subagent policy and optional `codex-cli` runner policy

## 1. 목적

Vulcan-Anvil Ex는 초기 audit workflow에서 Codex runner를 보수적으로 `gpt-5.5` + `high` reasoning effort로 사용했다.
이 기본값은 설계 정합성, QA 판단, 릴리즈 전 검수에는 안전하지만 모든 worker 작업에 쓰기에는 시간이 오래 걸리고 비용도 커질 수 있다.

이 문서는 Codex native subagent와 외부 runner의 model/effort 선택 기준을 구분한다. native 호출은 3.1절, 외부 `codex-cli` 호출은 2절, 3절의 역할 표와 4절 이후의 설정을 따른다.
목표는 별도 벤치마크 프로젝트를 만들지 않고, 실제 Run 실행 기록을 누적해 점진적으로 정책을 조정하는 것이다.

Claude CLI와 Antigravity/Gemini runner는 이 문서의 적용 대상이 아니다.

### Astra와 native 실행

Product는 품질 profile이며 별도의 `product-astra` profile을 만들지 않는다. Astra에서도 Product 입력/검증 범위는 `PRODUCT_PROFILE_BASELINE.md` 7절을 적용한다. 모델별 지침 검토 근거는 [공식 Astra 가이드](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra)다.
아래 CLI 기본값이나 Run의 모델명은 앱의 메인 모델을 바꾸지 않는다. 메인 모델/effort는 사용자가 선택한 값을 유지한다. native subagent 모델은 사용자 설정 상속을 기본으로 하고 effort만 3.1절에 따라 작업별로 선택한다. 실제 모델/effort가 확인되지 않으면 추정해 기록하지 않는다.
입력 축소와 effort 조정의 효과는 구분해서 비교한다. 일괄 Astra 전환이나 모델 하향을 강제하지 않는다. Fast 설정은 실제 사용 여부를 확인한다. API의 `configuration_update`/비동기 도구 옵션은 문서 지시만으로 앱에 적용되지 않는다.

## 2. 외부 CLI 기본 원칙

- 명시 옵션이 항상 우선한다.
  - `--model`
  - `--reasoning-effort`
- 명시 옵션이 없으면 `vulcan.config.json.runtime.model_policy.codex-cli.roles`를 따른다.
- 역할별 정책이 없으면 `runtime.model_policy.codex-cli.fallback`을 따른다.
- fallback도 없으면 runner 기본값 `gpt-5.5` + `high`를 사용한다.
- 지원되지 않는 Codex model alias는 worker 실행 전에 compatibility fallback으로 정규화한다.
- 최종 실행 기록에는 실제 model, reasoning effort, model source, effort source, model policy role, model fallback reason을 남긴다.
- 품질 판단이 필요한 작업은 계속 강한 모델/높은 effort를 사용한다.
- 로그 요약, 증적 index, Run 초안 같은 정리 작업은 낮은 모델/effort를 우선 사용한다.

## 3. 외부 CLI 권장 역할 정책

| Role | Model | Effort | 용도 |
| --- | --- | --- | --- |
| `review` | `gpt-5.5` | `high` | 독립 검수, 설계/QA 정합성 검토 |
| `critical_judgment` | `gpt-5.5` | `high` | Gate 승인 후보, FIND/CR 분류, 릴리즈 판단 후보 |
| `build` | `gpt-5.5` | `high` | 일반 구현 worker |
| `build-backend` | `gpt-5.5` | `high` | Backend/API/DB 구현 worker |
| `build-frontend` | `gpt-5.5` | `high` | Frontend/UI 구현 worker |
| `qa-execution` | `gpt-5.4` | `medium` | QA 명령 실행, 로그 수집, 결과 정리 |
| `qa-fix-loop` | `gpt-5.5` | `high` | 승인된 FIND 범위 안의 QA 수정 worker |
| `run-draft` | `gpt-5.4-mini` | `medium` | Run 초안, trace-context 후보, 문서 정리 |
| `evidence-summary` | `gpt-5.4-mini` | `low` | 로그/증적 index, 단순 요약 |

이 표는 성능 개선을 위한 시작점이다.
정답으로 고정하지 않고 실제 sample Run에서 duration, 실패율, Orchestrator 보정량을 보고 조정한다.

## 3.1 Native 모델 상속과 작업별 effort

Ex가 배포하는 `.codex/agents/*.toml`은 역할만 정의하고 `model`, `model_reasoning_effort`를 고정하지 않는다. 일반 worker와 custom agent 모두 기본적으로 `model` override를 생략한다. 메인의 설정이나 사용자 전역 `.codex/config.toml`을 Ex가 임의로 변경하지 않는다.

[OpenAI 공식 subagent 문서](https://developers.openai.com/codex/subagents)에 따르면 custom TOML 값이 있으면 우선하며, 그 외에는 명시적 spawn 값, 사용자 `[agents]` 기본값, 부모 설정 순으로 결정된다. 따라서 Ex의 고정값을 제거해도 사용자의 `agents.default_subagent_model` 설정이 있으면 부모와 다를 수 있다. 부모 모델 상속 의도와 충돌하면 그 사실을 알리고 사용자 설정을 확인한다. 실제 적용값을 확인하지 못했으면 `unknown`으로 보고한다.

사용자가 특정 subagent effort를 지시했다면 우선한다. 그 외에는 Orchestrator가 생성 전에 아래 기준으로 선택하고, 현재 도구가 지원하면 `reasoning_effort` 인자로 전달한다. 메인의 effort는 바꾸지 않는다.

| effort | 선택 기준 |
| --- | --- |
| `low` | 판단 범위가 좁은 파일/ID 탐색, 확정된 형식의 결과 정리, 기계적 수정 |
| `medium` | 기본값. 계약이 명확한 일반 구현, 담당 테스트 작성, 국소 검토/증적 해석 |
| `high` | 보안/권한, 데이터 마이그레이션, 여러 모듈의 계약 변경, 모호한 설계나 어려운 원인 분석 |

역할 이름만으로 effort를 고정하지 않는다. 중요한 검토를 무조건 low로 시작했다가 반복 재시도하지 않고, 위험을 알면 처음부터 high를 선택한다. `xhigh` 이상은 자동 기본값으로 쓰지 않는다. 사용자가 명시했거나 별도 합의된 정책이 있을 때만 사용한다.

현재 모델/도구가 선택값을 지원하지 않거나 세션에 이전 custom agent 고정값이 로드돼 있으면, 프롬프트에 effort를 적는 것으로 적용됐다고 주장하지 않는다. 지원되는 설정/역할로 재시작하거나, 상속값과 한계를 알린 뒤 기존 권한 안에서 진행한다. fresh-context 요구는 별도로 [AGENT_RUN_PROTOCOL.md](AGENT_RUN_PROTOCOL.md) 5.4절을 따른다.

호출 시 선택한 effort와 간단한 이유는 기존 위임 요약에 남길 수 있다. 런타임이 응답하지 않은 실제 값/토큰/비용은 만들지 않으며, 이를 위해 새 필수 Run 필드나 경고 0개 정리 루프를 추가하지 않는다. effort는 사고량 조정이지 테스트/보안/승인 기준 완화가 아니다. 비용 절감은 입력량, 재시도, 유효 결함과 보정량을 함께 보고 판단한다.

## 4. 설정 예시

```json
{
  "runtime": {
    "model_policy": {
      "codex-cli": {
        "enabled": true,
        "fallback": {
          "model": "gpt-5.5",
          "effort": "high"
        },
        "roles": {
          "review": {
            "model": "gpt-5.5",
            "effort": "high"
          },
          "build": {
            "model": "gpt-5.5",
            "effort": "high"
          },
          "qa-execution": {
            "model": "gpt-5.4",
            "effort": "medium"
          },
          "evidence-summary": {
            "model": "gpt-5.4-mini",
            "effort": "low"
          }
        }
      }
    }
  }
}
```

## 5. 실행 기록

`agent-run --mode work`, `run-exec`, `review-run`은 Codex runner 실행 기록에 다음 값을 남긴다.

```yaml
model: gpt-5.5
reasoning_effort: high
model_source: codex-model-policy:build-backend
effort_source: codex-model-policy:build-backend
model_policy_role: build-backend
model_fallback_reason: ""
```

명시 옵션을 사용하면 source는 `cli-argument`가 된다.

```powershell
python vulcan.py agent-run --mode work --run-id RUN-012 --runner codex-cli --model gpt-5.5 --reasoning-effort high
```

## 5.1 Compatibility fallback

역할 정책이나 CLI 명시 옵션이 현재 Codex CLI 계정에서 지원되지 않는 model alias를 가리키면, Ex는 실행 전에 지원되는 fallback model로 바꾼다.

현재 compatibility fallback:

| Requested model | Actual model | 사유 |
| --- | --- | --- |
| `gpt-5.3-codex` | `gpt-5.5` | 현재 Codex CLI 계정에서 지원되지 않는 경우가 있어 실행 전 호환 모델로 정규화 |

fallback이 발생하면 실행 기록의 `model_source`에는 `compat-fallback:<requested-model>`이 붙고, `model_fallback_reason`에 사람이 읽을 수 있는 이유가 남는다.

예:

```yaml
model: gpt-5.5
reasoning_effort: high
model_source: codex-model-policy:build|compat-fallback:gpt-5.3-codex
effort_source: codex-model-policy:build
model_policy_role: build
model_fallback_reason: gpt-5.3-codex is not supported by the current Codex CLI account; using gpt-5.5
```

이 fallback은 품질 downgrade 정책이 아니라 실행 호환성 회복 장치다.
모델 정책 자체를 조정하려면 `vulcan.config.json.runtime.model_policy` 또는 이 문서의 권장 역할 정책을 변경한다.

## 6. 성능 측정 방향

모델별 성능을 별도 실험으로 크게 돌리지 않는다.
실제 Run 실행 기록을 누적해 다음 항목을 비교한다.

- role
- model
- reasoning_effort
- duration_seconds
- exit_code
- timed_out
- run_file_changed 또는 result_file_changed
- changed_files
- run-check/check-trace/check-contract 결과
- Orchestrator 보정 필요 여부

향후 `perf-report`가 안정되면 role/model/effort별 평균 실행 시간과 실패 경향을 집계한다.

## 7. 주의사항

- `qa-execution`은 실패를 수정하지 않는다. 낮춘 effort로 실행하더라도 FIND/CR 최종 분류는 Orchestrator 또는 강한 review가 확인한다.
- `build`와 `qa-fix-loop`는 코드 변경을 만들 수 있으므로 `mini` 계열을 기본값으로 두지 않는다.
- `critical_judgment`는 자동 실행 role이라기보다 Orchestrator가 중요한 판단을 별도 runner에게 맡길 때 사용하는 정책 이름이다.
- 프로젝트가 감리 또는 보안 민감도가 높으면 모든 role을 일시적으로 `gpt-5.5` + `high`로 되돌릴 수 있다.
