# Gemini Adapter (GEMINI Standard)

> 상태: v0.1 (Gemini Runner 전용 어댑터 명세)
> 목적: Gemini 및 Antigravity 환경에서 Vulcan-Anvil Ex 프레임워크의 규칙과 제약을 이행하기 위한 바인딩 가이드라인을 정의한다.

---

## 1. 연동 개념

Gemini Adapter는 Core의 공통 규약 및 Run 입력을 Gemini 모델의 API 특성에 맞게 중재하고, 출력을 정규화하는 얇은 레이어입니다.

```text
+-------------------+      +-------------------------+      +---------------------+
|    Core Rule      | ---> |     Gemini Adapter      | ---> |    Gemini Runner    |
| (Run Input YAML)  |      |  (Structured Schema)    |      |    (API Execution)  |
+-------------------+      +-------------------------+      +---------------------+
```

## 2. Gemini 특화 연동 전략

### ① Structured Outputs (JSON Schema 강제) 활용
* Gemini API가 지원하는 `responseSchema`를 활용하여 워커의 출력이 `RUN_OUTPUT_CONTRACT_GEMINI.md` 규격에 선언된 정형 JSON/YAML 스키마를 100% 무결하게 준수하도록 강제합니다.
* 워커의 응답 오류 및 포맷 정합성 오류로 인한 파싱 실패율을 0%에 수렴시킵니다.

### ② 대규모 컨텍스트 윈도우 (Long-context Window) 최적화
* Gemini의 100만 토큰 이상 대용량 컨텍스트 윈도우를 활용하여, 부분 파일 탐색 대신 **전체 코드베이스와 모든 상류 설계서(Gate 1/2/3 산출물 전체)**를 단일 컨텍스트로 주입합니다.
* 이를 통해 워커가 코드 정합성 검토 시 파일 간 의존 관계 누락으로 인한 시그니처 정합성 오류를 원천 차단합니다.

## 3. 하위 최소 산출물 구성

Gemini 어댑터는 다음 문서들로 구성되어 제어 규칙을 이행합니다.

1. **[README_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/adapters/gemini/README_GEMINI.md)**: 본 개요 및 개념 정의서
2. **[LIMITATIONS_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/adapters/gemini/LIMITATIONS_GEMINI.md)**: Gemini 엔진 고유의 한계와 극복 지침
3. **[GATE_PROMPTS_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/adapters/gemini/GATE_PROMPTS_GEMINI.md)**: 런타임 구동 엔진이 기계적으로 파싱 가능한 구조화된 게이트 프롬프트 템플릿
4. **[PERSONA_MAPPING_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/adapters/gemini/PERSONA_MAPPING_GEMINI.md)**: 코어 페르소나와 Gemini 시스템 인스트럭션 매핑 규칙
5. **[RUN_OUTPUT_CONTRACT_GEMINI.md](file:///c:/Users/user/Documents/antig-workspace/vulcan-anvil-ex/docs/adapters/gemini/RUN_OUTPUT_CONTRACT_GEMINI.md)**: 워커가 실행 완료 시 반환해야 하는 JSON/YAML 구조화 출력 정의서
