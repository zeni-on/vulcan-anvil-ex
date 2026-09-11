# Codex/GPT Gate Prompts

> 목적: Codex/GPT가 현재 작업에 필요한 Core/skill로 이동하는 짧은 안내다. 정책 원문을 이 문서에 복제하지 않는다.

## 1. 사용 방식

이 문서는 Core 규칙을 대체하지 않는다.
Codex/GPT는 `AGENTS.md`와 사용자 최신 지시, 현재 작업 범위를 확인한다. Run은 사용하는 경우에 읽는다.

`process_model`이 있으면 `docs/core/ORCHESTRATOR_CLI_GUIDE.md` 4.1절로 이동한다. 아래 기존 Gate 절차를 새 프로세스에 적용하거나 표식을 임의로 추가하지 않는다.

Run을 사용하면 출력은 `docs/core/RUN_OUTPUT_CONTRACT.md`를 따른다.

## 2. Product

Product는 [PRODUCT_PROFILE_BASELINE.md](../../core/PRODUCT_PROFILE_BASELINE.md) 7절과 현재 작업의 관련 원본부터 읽는다. Run/Wave 선택, 실행자, 수정·재시험 권한, 조건부 재검증은 7절을 따른다. Audit/PoC의 worker 필수·직접 수정 예외·QA 재승인 절차를 가져오지 않는다.

문서 위치는 [PRODUCT_DOCUMENT_WRITING.md](../../core/PRODUCT_DOCUMENT_WRITING.md)를 따른다. 6종은 진입점이며 필요한 상세의 단일 원본을 연결한다. 승인된 작업을 수행하고 현재 계약과 실제 결과를 갱신하며, 작은 변경마다 Run/상세 파일을 만들거나 기존 승인 문서를 자동 이동하지 않는다.

## 3. 기존 Gate 절차의 상세 참조

Gate의 최소 확인·승인·worker 경계는 [GATE_EXECUTION_CHECKLIST.md](../../core/GATE_EXECUTION_CHECKLIST.md), 운영은 [ORCHESTRATOR_PROTOCOL.md](../../core/ORCHESTRATOR_PROTOCOL.md)의 해당 절을 따른다. Audit/PoC의 기존 Run/worker 및 필수 검수 기준은 유지한다. 아래 문서는 현재 작업에 필요한 경우에만 추가로 읽는다.

| 필요한 판단 | 참조 |
| --- | --- |
| profile별 산출물/검사 강도 | [DELIVERY_PROFILES.md](../../core/DELIVERY_PROFILES.md) |
| 요구사항/시험/추적 연결 | [TRACEABILITY_RULES.md](../../core/TRACEABILITY_RULES.md) |
| 설계 순서와 계약 | [GATE2_DESIGN_SEQUENCE.md](../../core/GATE2_DESIGN_SEQUENCE.md) |
| Run 기반 구현 계획/실행 | [implementation-plan](skills/implementation-plan.md), [build-wave](skills/build-wave.md) |
| QA 실행/승인 범위 안의 수정 | [qa-execution](skills/qa-execution.md), [qa-fix-loop](skills/qa-fix-loop.md) |
| 계약 변경과 CR | [CHANGE_CONTROL_PROCESS.md](../../core/CHANGE_CONTROL_PROCESS.md) |
| 독립 검수 | [AGENT_RUN_PROTOCOL.md 5.4절](../../core/AGENT_RUN_PROTOCOL.md#54-새-문맥의-native-review), 공식 요청서/외부 CLI를 쓰면 [independent-review](skills/independent-review.md) |

## 4. Codex 실행과 보고

native 모델/effort는 [CODEX_MODEL_POLICY.md](../../core/CODEX_MODEL_POLICY.md) 3.1절을 따른다. 외부 CLI 설정을 native 호출에 적용하지 않는다. 역할별 기존 작업은 [PERSONA_DELEGATION.md](PERSONA_DELEGATION.md)로 연결한다.

완료 보고는 변경, 실제 검증 결과, 미해결 항목과 필요한 다음 승인만 간결하게 적는다. 실행하지 않은 검증이나 확인되지 않은 모델/effort를 사실로 기록하지 않는다.
