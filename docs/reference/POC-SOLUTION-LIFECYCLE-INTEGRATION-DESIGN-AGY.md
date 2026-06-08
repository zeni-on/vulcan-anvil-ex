# PoC & Solution Lifecycle Integration Design (AGY-PROPOSAL)

> **상태**: v1.0 (설계 제안서)  
> **오케스트레이터**: AGY (Antigravity)  
> **목적**: Vulcan-Anvil Ex 프레임워크에 PoC 및 Solution 프로필을 유기적으로 융합하고, 아키텍처 결정 기록(ADR) 필수화 및 단계별 승격(Promotion)을 처리하기 위한 상세 스펙을 정의하여 Codex 에이전트 및 팀과의 설계를 싱크한다.

---

## 1. 개요 및 설계 이유 (Rationale)

### 1-1. 배경 및 문제 의식
현재 Vulcan-Anvil Ex 프레임워크의 기본 `audit`(감리) 프로필은 20여 종이 넘는 무거운 설계/QA 산출물과 엄격한 추적성 매트릭스(`REQ -> AC -> FUNC -> SCR -> PGM -> API -> DB -> SEC -> UT -> IT -> UI -> EV`)를 강제합니다.
이는 공공 감리나 높은 컴플라이언스가 요구되는 프로젝트에는 필수적이지만, 다음과 같은 심각한 오버헤드를 발생시킵니다.
* **개발 초기(PoC)의 병목**: 가설을 검증하고 빠른 프로토타입을 만들어야 하는 단계에서 관료적 문서 작업 때문에 AI 워커와 오케스트레이터의 동력이 상실됩니다.
* **제품화 단계(Solution)의 부적합**: 대다수의 SaaS나 상용 서비스는 감리(Audit)를 받지 않지만, 그렇다고 PoC의 불안정한 코드를 그대로 런칭할 수는 없습니다. 제품의 운영 아키텍처, 핵심 DTO/API 계약, 회귀 테스트 수준의 실질적 엔지니어링 건전성(Solution)이 필요하지만 기존 프레임워크에는 이에 맞는 적절한 타협점이 없었습니다.

### 1-2. 핵심 설계 철학
1. **감리의 본질은 존중하되, 비효율은 걷어낸다**: 감리는 프로젝트 참여자 간의 용어 불일치, 설계 오차, 테스트 누락을 기계적으로 잡아내는 훌륭한 장치입니다. 이를 포기하지 않고, 프로필 수준에 맞추어 검사 규칙을 지능적으로 완화합니다.
2. **ADR (Architecture Decision Record)의 필수화**: Solution 프로필의 정수는 쓸데없는 문서 작업의 배제가 아니라, **"왜 이 기술 스택을 선택했고, 왜 이 설계 패턴을 적용했는가"**에 대한 의사결정의 이력을 관리하는 것입니다. 이를 위해 표준 ADR 작성을 의무화합니다.
3. **가설-검증 및 승격(Promotion)의 흐름화**: PoC에서 검증된 팩트를 기반으로 자동으로 뼈대를 추출하고, Gap 분석을 통해 Solution과 Audit으로 정밀 보강 및 전환되는 순방향 흐름을 제공합니다.

---

## 2. 하려고 하는 범위 (Scope)

* **PoC 3종 통합 산출물 연동**: 가설 수립부터 최종 의사결정(Decision)까지를 3개 문서로 압축 관리.
* **Solution 5종 산출물 & ADR 의무화**: 운영 가능한 5대 영역 문서 및 `docs/adr/` 이력 관리 강제.
* **vulcan.py 검사기 개조**: `status --check`, `check-trace`, `check-contract`가 각 프로필(PoC, Solution)에서 동작할 때의 세부 검증 완화 및 분기 처리.
* **승격(Promotion) 매커니즘**: 프로필 간 전환 시 누락 요소를 진단해 주는 Gap Report 생성 및 CLI 스위칭 기능.

---

## 3. 상세 설계 (Design Details)

### 3-1. PoC 프로필 (가설-검증 중심)
* **목표**: 아이디어 검증 및 빠른 실패(Fail Fast) / Pivot 결정.
* **필수 3종 산출물**:
  1. `docs/poc/POC_REQUIREMENTS.md` (Phase 0 ~ Gate 1 통합): 핵심 가설, 검증 성공 기준(Metrics), 배제할 스코프 정의.
  2. `docs/poc/POC_SYSTEM_DESIGN.md` (Gate 2 통합): 개념 아키텍처, 기술 선택(ADR 초안), 핵심 진입점(API/Schema).
  3. `docs/poc/POC_TEST_REPORT.md` (Gate 3 ~ Gate 5 통합): 테스트 방법, 실행 로그/화면 캡처 증적, 그리고 최종 의사결정(`Continue`, `Pivot`, `Stop`, `Promote to solution/audit`).
* **검사 완화 및 TBD 허용**:
  * PoC 진행 중 미결 사항(TBD)이 남아 있더라도 **"사유와 후속 판단 시점"**이 함께 기재되어 있으면 에러 대신 경고(Warning)만 주고 빌드/통합을 통과시킵니다.
  * Playwright E2E 검증 시 공식 `@playwright/test` 러너 대신 수동 실행 캡처나 커스텀 스크립트 로그(`smoke-demo-log`)를 정식 증적으로 인정합니다.

### 3-2. Solution 프로필 (제품화-운영 중심)
* **목표**: 감리 문서는 배제하고 실제 배포/운영 가능한 제품 수준의 베이스라인 확립.
* **필수 5종 산출물 및 ADR**:
  1. `docs/SW_ARCHITECTURE.md` & `docs/adr/`: 시스템 구조 및 주요 아키텍처 의사결정 기록(ADR) 목록.
     * `docs/adr/ADR-001-some-decision.md`와 같이 표준 ADR 양식(Status, Context, Decision, Consequences)으로 기술적 선택들을 명문화해야 합니다.
  2. `docs/API_SPEC.md`: 외부 노출 API 규격 및 요청/응답 DTO 구조 정의.
  3. `docs/DATABASE_SPEC.md`: 데이터 스키마 명세 및 인덱스 전략.
  4. `docs/SECURITY_GUIDE.md`: 암호화 기준, 인증/인가(OAuth/JWT 등) 설계.
  5. `docs/RELEASE_APPROVAL.md` (릴리즈 노트): 변경 이력 및 미해결 백로그 요약.
* **승인 지점 단축 (`major-gates-and-release`)**:
  * 모든 Gate마다 개별 승인을 받아야 하는 audit과 달리, **설계 완료(Gate 2)** 및 **릴리즈 최종 검수(Gate 4)** 지점에서만 명시적 승인을 요구하여 속도를 향상시킵니다.
* **회귀 테스트 및 주요 UI/API 검증 (`release-regression-major-ui-api`)**:
  * 개별 함수 단위의 UT/IT ID 매핑은 배제하되, 전체 API 통합 테스트 및 주요 서비스 화면의 Playwright 회귀 테스트 스위트가 100% 통과했는지 검증합니다.
* **코드 계약 검증 완화 (`public-api-service-dto`)**:
  * `check-contract` 시 private 함수는 검증하지 않으며 컨트롤러의 Public API 엔드포인트 및 서비스 인터페이스의 시그니처만 대조합니다.

---

## 4. Vulcan 연동 방법 (How to Integrate)

### 4-1. DELIVERY_PROFILE_RULES 갱신
`vulcan.py` 내의 프로필 룰에 의거해 내부 검사기들이 동작하도록 규칙 매핑을 보완합니다:
```python
DELIVERY_PROFILE_RULES = {
    "audit": {
        "gate_approval": "all-gates-explicit",
        "required_artifacts": "full-audit-set",
        "traceability_level": "full",
        "program_contract_level": "class-interface-public-method",
        "qa_evidence_level": "qa-000-to-qa-003-command-ui-log-finding",
        "independent_review_level": "gate2-gate4-pr-as-needed",
        "run_preflight_strictness": "blocking",
        "release_control": "gate5-release-approval-pr",
    },
    "solution": {
        "gate_approval": "major-gates-and-release",
        "required_artifacts": "architecture-api-db-security-release-core-and-adr",
        "traceability_level": "core-requirement-api-db-security-regression",
        "program_contract_level": "public-api-service-dto",
        "qa_evidence_level": "release-regression-major-ui-api",
        "independent_review_level": "release-candidate-or-large-change",
        "run_preflight_strictness": "scope-contract-blocking-other-warning",
        "release_control": "release-note-backlog-pr",
    },
    "poc": {
        "gate_approval": "start-checkpoint-finish",
        "required_artifacts": "goal-hypothesis-key-design-result",
        "traceability_level": "hypothesis-to-implementation-to-result",
        "program_contract_level": "main-interface-entrypoint",
        "qa_evidence_level": "smoke-demo-log",
        "independent_review_level": "optional",
        "run_preflight_strictness": "warning-first",
        "release_control": "poc-result-summary",
    },
}
```

### 4-2. validate_artifacts_presence() 수정
현재 프로젝트의 프로필을 로드하고 필수 문서가 존재하는지 판단할 때, 아래 분기 처리를 구현합니다:
* `poc` 프로필: `docs/poc/` 폴더 내 3종 통합 문서 존재 여부만 체크.
* `solution` 프로필: 5종 필수 문서 및 `docs/adr/` 폴더가 존재하고 그 하위에 최소 1개 이상의 `ADR-*.md` 파일이 존재하는지 체크.

### 4-3. check_trace() 및 check_contract() 분기 처리
* **check_trace**:
  * `poc`: 기존 풀 체인 검증을 건너뛰고, 가설에서 테스트 결과 및 최종 의사결정으로의 단선 링크 정합성만 검증.
  * `solution`: `REQ -> API -> DB -> SEC -> Regression Test` 핵심 운영 맵핑 매트릭스만 추출 및 누락 체크.
* **check_contract**:
  * `poc`: 주 진입점의 존재 여부만 검증.
  * `solution`: Public API 및 Service DTO 수준까지만 컴파일 시그니처 대조 검사 적용.

---

## 5. 단계별 승격 방안 (Promotion Strategy)

승격은 이전 단계의 산출물 및 코드를 입력 재료(Seed)로 삼아, 다음 단계의 필수 문서 뼈대를 자동 생성(Scaffolding)하고 누락된 요소를 채우도록 유도하는 **Gap-driven** 방식으로 수행합니다.

### 5-1. PoC -> Solution 승격
1. **의사결정 확인**: `POC_TEST_REPORT.md` 내 `Decision` 항목이 `Promote to solution/audit`인지 검사.
2. **뼈대 역생성 (Scaffolding)**:
   * `POC_SYSTEM_DESIGN.md`에 정의된 핵심 API와 스키마 정보를 파싱하여 `API_SPEC.md`와 `DATABASE_SPEC.md` 초안을 자동 생성.
   * `docs/adr/` 폴더를 생성하고 PoC 기술 스택 선택 내용을 바탕으로 `ADR-001-stack-selection.md` 초안을 배치.
3. **Gap 분석 및 리포팅**: Solution에 필요한 아키텍처(SW_ARCHITECTURE.md) 및 보안(SECURITY_GUIDE.md) 등 누락 사항을 콘솔과 마크다운 Gap Report로 요약 안내.
4. **프로필 스위칭**: 사용자가 수긍하면 `vulcan.config.json` 및 `session.json`을 `solution` 프로필로 전환하고 커밋 유도.

### 5-2. Solution -> Audit 승격
1. **뼈대 정밀 역생성**:
   * 실제 동작하는 코드의 라우터와 데이터 모델을 정적 분석하여 감리용 `PROGRAM_SPEC.md` 및 상세 `DATABASE_SPEC.md`에 들어갈 클래스/메서드/테이블 목록 테이블을 역으로 채워 넣음.
2. **추적성 복원 (Reverse Traceability)**:
   * 기존의 기능 명세와 코드 진입점 관계를 기반으로 `TRACEABILITY_MATRIX_TEMPLATE.md`에 맵핑을 채우고, 끊어지는 연결 고리(Gap)를 찾아내어 오케스트레이터 및 워커에게 보강을 지시.
3. **공식 증적 취합**:
   * Playwright 테스트 스위트를 정식 구동하여 QA-000부터 QA-003에 이르는 공식 증적 문서로 이전하고, 발견된 미해결 이슈를 `QA_FINDING_TEMPLATE.md`로 변환.
4. **프로필 스위칭**: `audit` 프로필로 전환하여 최종 컴플라이언스 검증 가동.

---

## 6. 결론 및 향후 계획

본 설계 제안은 Vulcan-Anvil Ex 프레임워크가 실무적인 속도(PoC)와 엔지니어링 안정성(Solution), 그리고 엄격한 절차(Audit)를 모두 충족하도록 돕는 유연한 진화 체계를 제공합니다.

* **1단계**: PoC 3종 통합 템플릿 제작 및 `docs/templates/poc/` 배치.
* **2단계**: `vulcan.py` 내 프로필 규칙에 따른 `status --check`, `check-trace` 등 우회/필터링 코드 작성.
* **3단계**: `promote-profile` CLI 추가 및 Gap 분석 리포터 구현.
* **4단계**: PoC 및 Solution 통합 리그레션 테스트를 통한 무결성 입증.
