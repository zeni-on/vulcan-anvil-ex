# Cross Validation: Ex Direction and Investment Review

> 대상 문서: `docs/reference/EX-DIRECTION-INVESTMENT-REVIEW.md`  
> 검증일: 2026-06-03  
> 검증 runner: Claude CLI, Antigravity/Gemini CLI

## 1. 실행 방식

Claude는 `claude --print`로 파일 수정 없이 문서 검토만 수행했다.

AGY는 Windows CLI에서 stdin만으로 `--print`를 실행할 수 없어 `--print <prompt>` 인자로 재실행했다.
stdout 결과 파일은 생성되지 않았지만, 로컬 AGY session transcript jsonl에서 최종 모델 응답을 회수했다.

```text
%USERPROFILE%/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript_full.jsonl
```

raw transcript와 CLI log에는 로컬 계정, 경로, runtime metadata가 포함될 수 있으므로 repository에는 보관하지 않는다.
검증 의견만 `EX-DIRECTION-INVESTMENT-REVIEW.agy.md`로 추출해 남긴다.

## 2. Claude 검증 요약

Claude의 결론은 다음이다.

- Ex를 빠른 coding accelerator가 아니라 AI coding governance framework로 포지셔닝한 것은 일관되고 설득력 있다.
- 적용 조건과 부적합 조건을 함께 명시한 점이 좋다.
- PoC profile의 경량화가 실제로 달성 가능한지, governance 가치가 측정 가능한지 보강이 필요하다.
- 경쟁 도구가 trace/evidence 기능을 흡수할 가능성에 대한 방어 전략이 필요하다.
- trace graph 추천 정확도와 Orchestrator 보정량을 측정해야 한다.

## 3. AGY 검증 요약

AGY의 결론은 다음이다.

- Ex를 생산성 도구가 아닌 AI coding governance framework로 정의한 것은 타당하다.
- 다중 runtime을 Core Gate/Run 규칙으로 회수하려는 방향은 차별성이 있다.
- PoC profile은 문서 깊이만 줄이는 것으로 충분하지 않고, 실제 실행 오버헤드도 측정해야 한다.
- review fatigue, LLM 버전 변경, 기존 ALM/CI 도구와의 중복 위험을 추가해야 한다.
- token/API 비용, human approval latency, runtime 출력 계약 변경 위험을 측정 항목에 포함하는 것이 좋다.

## 4. 반영한 변경

다음 항목을 본문에 반영했다.

- API 비용, context 전환, LLM/CLI runtime 변경 위험
- review fatigue와 기존 ALM/CI 도구 중복 위험
- PoC profile의 구체적 경량화 메커니즘
- trace graph 추천 정확도, profile 전환 비용 감소율, 승인자 대기 시간, 산출물 재사용 횟수 측정
- adapter-agnostic Core 유지 전략
- 축소 또는 중단 신호의 반복 기준

AGY가 제안한 "PoC 자동 패스" 성격의 표현은 그대로 반영하지 않았다.
PoC에서도 실패나 미실행 항목을 Pass로 바꾸면 Ex의 기본 신뢰성이 약해지기 때문이다.
