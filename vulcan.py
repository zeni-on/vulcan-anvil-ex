#!/usr/bin/env python3
"""
Vulcan-Anvil Ex - 5-Gate AI 협업 개발 프레임워크

대장장이 신 Vulcan처럼, 에이전트 팀을 단련하여 체계적으로 프로젝트를 완성합니다.
Agent-Forge의 5-Gate 프로세스를 Claude Code 네이티브 하네스(.claude/) 구조로 재구현.

명령어:
  init         새 프로젝트 초기화
  session      Gate 상태 업데이트 + git commit 자동 생성
  check-trace  Gate별 정합성 검사
  export       snapshot.json 생성 (대시보드용)
  upgrade      프레임워크 파일을 최신 버전으로 업데이트
  version      현재 프레임워크 버전 확인

사용법:
  # 초기화 (Vulcan-Anvil 디렉토리에서 실행)
  python vulcan.py init <target-dir> <project-name> [--agent-name NAME] [--remote GIT_URL] [--require-remote]

  # 이하 명령은 프로젝트 디렉토리에서 실행
  python vulcan.py check-trace
  python vulcan.py session --gate gate1 --status done --feature "로그인 기능"
  python vulcan.py export [--output snapshot.json]
  python vulcan.py upgrade
"""

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta

# Windows 콘솔 UTF-8 출력 보장
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

VULCAN_VERSION = "0.2.2"

VULCAN_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(VULCAN_DIR, "templates")
PROJECT_DOC_SETS = [
    "docs/core",
    "docs/templates",
    "docs/adapters",
    "docs/seed-docs",
]
PROJECT_DOC_DIRS = [
    "docs/artifacts/00-discovery",
    "docs/artifacts/01-requirements",
    "docs/artifacts/02-traceability",
    "docs/artifacts/02-design/architecture",
    "docs/artifacts/02-design/function",
    "docs/artifacts/02-design/program",
    "docs/artifacts/02-design/api",
    "docs/artifacts/02-design/screen",
    "docs/artifacts/02-design/screen/images",
    "docs/artifacts/02-design/screen/ui-baseline",
    "docs/artifacts/02-design/data",
    "docs/artifacts/02-design/data/erd",
    "docs/artifacts/02-design/data/erd/logical",
    "docs/artifacts/02-design/data/erd/physical",
    "docs/artifacts/02-design/data/erd/exports",
    "docs/artifacts/02-design/security",
    "docs/artifacts/02-design/development-standard",
    "docs/artifacts/03-test",
    "docs/artifacts/04-review",
    "docs/artifacts/04-review/evidence",
    "docs/artifacts/04-review/evidence/ui",
    "docs/artifacts/05-change",
    "docs/artifacts/07-release",
    "docs/runs",
    "docs/reviews",
    "docs/ref-docs",
]
PROJECT_ARTIFACT_TEMPLATES = [
    ("docs/templates/PROJECT_BRIEF_TEMPLATE.md", "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md"),
    ("docs/templates/STAKEHOLDER_SCOPE_TEMPLATE.md", "docs/artifacts/00-discovery/DOC-CORE-P0-002_Stakeholder-And-Scope_v0.1.md"),
    ("docs/templates/AS_IS_TO_BE_TEMPLATE.md", "docs/artifacts/00-discovery/DOC-CORE-P0-003_As-Is-To-Be_v0.1.md"),
    ("docs/templates/RISK_ASSUMPTION_TEMPLATE.md", "docs/artifacts/00-discovery/DOC-CORE-P0-004_Risk-And-Assumption_v0.1.md"),
    ("docs/templates/REQUIREMENTS_SPEC_TEMPLATE.md", "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md"),
    ("docs/templates/TRACEABILITY_MATRIX_TEMPLATE.md", "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md"),
    ("docs/templates/SW_ARCHITECTURE_TEMPLATE.md", "docs/artifacts/02-design/architecture/DOC-ARCH-G2-001_SW-Architecture_v0.1.md"),
    ("docs/templates/FUNCTION_SPEC_TEMPLATE.md", "docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md"),
    ("docs/templates/PROGRAM_SPEC_TEMPLATE.md", "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md"),
    ("docs/templates/API_SPEC_TEMPLATE.md", "docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md"),
    ("docs/templates/SCREEN_SPEC_TEMPLATE.md", "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md"),
    ("docs/templates/PROJECT_GLOSSARY_TEMPLATE.md", "docs/artifacts/02-design/data/DOC-DATA-G2-001_Project-Glossary_v0.1.md"),
    ("docs/templates/DATABASE_SPEC_TEMPLATE.md", "docs/artifacts/02-design/data/DOC-DATA-G2-002_Database-Spec_v0.1.md"),
    ("docs/templates/LOGICAL_ERD_DBML_TEMPLATE.dbml", "docs/artifacts/02-design/data/erd/logical/logical-erd.dbml"),
    ("docs/templates/PHYSICAL_ERD_DBML_TEMPLATE.dbml", "docs/artifacts/02-design/data/erd/physical/physical-erd.dbml"),
    ("docs/templates/SECURITY_GUIDE_TEMPLATE.md", "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md"),
    ("docs/templates/DEVELOPMENT_STANDARD_TEMPLATE.md", "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md"),
    ("docs/templates/TEST_CASE_TEMPLATE.md", "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md"),
    ("docs/templates/QA_FINDING_TEMPLATE.md", "docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md"),
    ("docs/templates/TEST_RESULT_TEMPLATE.md", "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md"),
    ("docs/templates/CHANGE_REQUEST_TEMPLATE.md", "docs/artifacts/05-change/DOC-PM-G0-001_Change-Request_v0.1.md"),
    ("docs/templates/RELEASE_APPROVAL_TEMPLATE.md", "docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md"),
]
PROJECT_ROOT_FILES = [
    "AGENTS.md",
]
RUN_SKILLS = {
    "orchestrator-plan": "docs/core/ORCHESTRATOR_PROTOCOL.md",
    "persona-run": "docs/core/AGENT_RUN_PROTOCOL.md",
    "traceability-review": "docs/adapters/codex-gpt/skills/traceability-review.md",
    "screen-design": "docs/adapters/codex-gpt/skills/screen-design.md",
    "security-review": "docs/adapters/codex-gpt/skills/security-review.md",
    "screen-review": "docs/adapters/codex-gpt/skills/screen-review.md",
    "ui-review": "docs/adapters/codex-gpt/skills/ui-review.md",
    "development-standard-review": "docs/adapters/codex-gpt/skills/development-standard-review.md",
    "implementation-plan": "docs/adapters/codex-gpt/skills/implementation-plan.md",
    "build-wave": "docs/adapters/codex-gpt/skills/build-wave.md",
    "data-standard-review": "docs/adapters/codex-gpt/skills/data-standard-review.md",
    "qa-fix-loop": "docs/adapters/codex-gpt/skills/qa-fix-loop.md",
    "change-impact-analysis": "docs/adapters/codex-gpt/skills/change-impact-analysis.md",
    "handoff": "docs/core/ORCHESTRATOR_PROTOCOL.md",
    "independent-review": "docs/adapters/codex-gpt/skills/independent-review.md",
}
RUN_PERSONAS = {
    "discovery": "배경, 제약, 현행 자료, 질문, 위험을 정리한다.",
    "requirements": "요구사항, 비기능 요구사항, 인수기준을 정리한다.",
    "design": "기능, 화면, 프로그램, DB, 보안 설계를 작성한다.",
    "screen-design": "화면 구조, 시안, 와이어프레임, UI 기준 증적을 설계한다.",
    "security-review": "보안 요구사항, 보안설계, 시큐어코딩 기준 누락을 검토한다.",
    "screen-review": "화면 식별, 화면상태, 와이어프레임, UI 증적 기준 누락을 검토한다.",
    "ui-review": "구현자가 좋은 화면을 만들 수 있을 만큼 UI 기준선이 충분한지 검토한다.",
    "development-review": "개발표준, 패키지 구조, 코딩/주석/테스트 컨벤션 확정 여부를 검토한다.",
    "test-design": "AC, SEC, NREQ를 검증 가능한 테스트로 전개한다.",
    "build-planning": "승인된 설계와 테스트 기준을 구현 가능한 Build Wave로 나눈다.",
    "build": "승인된 설계를 코드, 설정, 테스트 코드로 구현한다.",
    "evidence": "테스트 결과, 화면 캡처, 로그 등 증적을 만든다.",
    "review": "추적성, 보안, 품질, 설계 준수 여부를 검토한다.",
    "release": "승인 후보, 릴리즈 범위, 인수인계 항목을 정리한다.",
    "change-control": "변경요청 영향도와 다시 진행할 Gate를 판단한다.",
    "documentation": "용어, 문서 버전, 산출물 일관성을 정리한다.",
}
RUN_SKILL_DEFAULT_PERSONAS = {
    "orchestrator-plan": "documentation",
    "persona-run": "",
    "traceability-review": "review",
    "screen-design": "screen-design",
    "security-review": "review",
    "screen-review": "screen-review",
    "ui-review": "ui-review",
    "development-standard-review": "development-review",
    "implementation-plan": "build-planning",
    "build-wave": "build",
    "data-standard-review": "review",
    "qa-fix-loop": "build",
    "change-impact-analysis": "change-control",
    "handoff": "review",
    "independent-review": "review",
}
GATE_DEFAULT_PERSONAS = {
    "phase0": "discovery",
    "gate1": "requirements",
    "gate2": "design",
    "gate3": "test-design",
    "impl": "build",
    "gate4": "review",
    "gate5": "release",
}
HANDOFF_TARGETS = ["cli", "desktop", "github", "codex-review", "claude", "manual"]
INDEPENDENT_REVIEW_RUNNERS = ["codex-cli", "codex", "claude-cli", "claude", "manual"]
INDEPENDENT_REVIEW_EXEC_RUNNERS = ["codex-cli", "codex", "claude-cli", "claude"]
INDEPENDENT_REVIEW_DEFAULT_GATES = ["gate2", "gate4"]
RUN_REQUIRED_KEYS = [
    "run_id",
    "adapter",
    "persona",
    "status",
    "skill",
    "related_ids",
    "verification_results",
    "evidence",
    "traceability_updates",
    "open_issues",
]

GATE_LABELS = {
    "phase0": "Phase 0 Discovery",
    "gate1": "Gate 1 요구사항",
    "gate2": "Gate 2 설계",
    "gate3": "Gate 3 테스트 플랜",
    "impl":  "구현",
    "gate4": "Gate 4 QA 검토",
    "gate5": "Gate 5 최종 승인",
}

GATE_ORDER = ["phase0", "gate1", "gate2", "gate3", "impl", "gate4", "gate5"]
DEFAULT_DELIVERY_PROFILE = "audit"

RUN_TYPES_BY_GATE = {
    "phase0": "Discovery",
    "gate1": "Requirements",
    "gate2": "Design",
    "gate3": "Test",
    "impl": "Implementation",
    "gate4": "Review",
    "gate5": "Approval",
}

AUDIT_COMMON_READ_FIRST_DOCS = [
    "AGENTS.md",
    "session.json",
    "docs/core/TRACEABILITY_RULES.md",
    "docs/adapters/codex-gpt/GATE_PROMPTS.md",
]

AUDIT_GATE_READ_FIRST_DOCS = {
    "gate2": [
        "docs/core/GATE2_DESIGN_SEQUENCE.md",
    ],
}

AUDIT_COMMON_REFERENCE_DOCS = [
    "docs/core/ID_SYSTEM.md",
    "docs/core/ORCHESTRATOR_PROTOCOL.md",
    "docs/core/AGENT_PERSONAS.md",
    "docs/core/AGENT_RUN_PROTOCOL.md",
    "docs/core/DELIVERY_PROFILES.md",
    "docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md",
    "docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md",
]

AUDIT_COMMON_READONLY_DOCS = [
    "docs/core/",
    "docs/templates/",
    "docs/seed-docs/reference-standards/",
]

AUDIT_COMMON_EXCLUDED_PATHS = [
    "docs/ref-docs/",
    "**/*.db",
    "**/__pycache__/",
    "**/.ruff_cache/",
]

AUDIT_GATE_ANCHOR_DOCS = {
    "gate1": [
        "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md",
        "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
        "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
    ],
    "gate2": [
        "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
        "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
    ],
    "gate3": [
        "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
        "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
    ],
    "impl": [
        "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
        "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
    ],
    "gate4": [
        "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
        "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md",
    ],
    "gate5": [
        "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md",
        "docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md",
    ],
}

AUDIT_FOCUSED_SOURCE_SKILLS = {
    "traceability-review",
    "independent-review",
    "change-impact-analysis",
    "handoff",
}

AUDIT_DESIGN_SEQUENCE_SKILLS = {
    "screen-design",
    "screen-review",
    "ui-review",
    "development-standard-review",
    "data-standard-review",
    "security-review",
}

AUDIT_UI_POLICY_SKILLS = {
    "screen-design",
    "screen-review",
    "ui-review",
    "implementation-plan",
    "build-wave",
    "qa-fix-loop",
}

AUDIT_GATE_EXIT_POLICY = {
    "stop_required": True,
    "next_gate_requires_user_approval": True,
    "approval_evidence_required": True,
    "allowed_next_action": "현재 Gate 산출물 요약, 미해결 항목, 다음 Gate 진행 승인 질문을 남기고 대기한다.",
    "forbidden_actions": [
        "사용자의 명시 승인 없이 다음 Gate 산출물을 작성하지 않는다.",
        "사용자의 명시 승인 없이 구현, 테스트 실행, QA 승인, 릴리즈 승인을 선언하지 않는다.",
        "대화상 승인 없이 Run 또는 릴리즈 승인서에 User Approved로 기록하지 않는다.",
    ],
}

AUDIT_UI_EVIDENCE_POLICY = {
    "state_level_required": True,
    "id_pattern": "UI-001-01",
    "capture_tool": "Playwright",
    "install_if_missing": [
        "npx playwright --version",
        "npm install -D @playwright/test",
        "npx playwright install",
    ],
    "forbidden_as_pass_evidence": [
        "CDP-only capture",
        "browser manual screenshot without Playwright run",
    ],
    "minimum_fields": [
        "UI-ID",
        "관련 SCR",
        "상태/시나리오",
        "입력값",
        "기대 화면",
        "실제 확인",
        "증적 파일",
        "결과",
    ],
    "examples": [
        "UI-001-01 회원가입 기본 화면",
        "UI-001-02 약한 비밀번호 오류",
        "UI-001-03 비밀번호 확인 불일치",
        "UI-001-04 중복 이메일 오류",
        "UI-001-05 회원가입 성공 메시지",
        "UI-001-06 성공 후 로그인 연계",
    ],
}

AUDIT_UI_IMPLEMENTATION_CONTRACT_POLICY = {
    "required_when": "화면설계서에 UIREF, 이미지 시안, HTML/CSS/JS 화면 퍼블리싱 산출물, Figma, 기존 화면 캡처, ui-baseline 경로가 있는 경우",
    "gate2_required_fields": [
        "기준 파일 또는 URL",
        "기준 CSS 또는 디자인 토큰",
        "필수 유지 요소",
        "변경 허용 항목",
        "변경 금지 항목",
        "구현 비교 방식",
        "차이 발생 시 FIND/CR 판정 기준",
    ],
    "impl_checklist": [
        "구현 전 관련 SCR의 UI Implementation Contract를 확인한다.",
        "화면 퍼블리싱 CSS 또는 동등한 레이아웃/class 구조를 재사용했는지 기록한다.",
        "보안가이드 때문에 바꾼 문구, 필드, 흐름은 DEC/ISSUE/FIND/CR 중 하나로 기록한다.",
        "기본/오류/성공/전환 상태가 Gate 3 UI-ID와 연결되어 있는지 확인한다.",
        "구현 결과 screenshot이 기준 UIREF와 비교 가능한 위치에 저장되는지 확인한다.",
    ],
    "gate4_required_evidence": [
        "기준 UIREF screenshot 또는 ui-baseline 경로",
        "구현 screenshot",
        "차이 목록",
        "허용된 차이 여부",
        "미허용 차이의 FIND 또는 CR",
    ],
}

AUDIT_WORKER_EXECUTION_POLICY = {
    "applies_when": "Run이 subagent, codex-cli, claude-cli, manual worker 등 Orchestrator와 분리된 작업자 runner에게 전달되는 경우",
    "role": "worker-runner",
    "forbidden_actions": [
        "Gate 전환을 수행하지 않는다.",
        "session.json의 current_gate, gate_status, completed를 직접 변경하지 않는다.",
        "사용자 승인, Gate 완료, QA Pass, 릴리즈 승인, merge 가능 여부를 최종 확정하지 않는다.",
        "Run의 scope.writable 밖 파일을 수정하지 않는다.",
        "Orchestrator가 요청하지 않은 신규 Run, PR, 커밋, push를 만들지 않는다.",
    ],
    "required_outputs": [
        "수행한 변경과 검증 결과를 Run 결과에 남긴다.",
        "Gate 전환, session 변경, 최종 승인 판단이 필요하면 Orchestrator 결정 필요 항목으로 반환한다.",
        "범위 밖 수정이나 기준 충돌이 필요하면 직접 처리하지 않고 open_issues 또는 findings로 남긴다.",
    ],
}

AUDIT_GATE2_DESIGN_SEQUENCE = [
    "G2-01 Kickoff / 설계 범위 고정: Gate 1 요구사항, AC, 미결 질문, 보류 항목을 확인한다.",
    "G2-02 SW Architecture Draft: 전체 구조, 주요 CNT, ADR 후보, 보안/데이터/배포 경계, Pending을 먼저 잡는다.",
    "G2-03 Screen / User Flow: SCR, UIREF, 화면 상태, 메시지 위치, 사용자 흐름을 확정한다.",
    "G2-04 Function Spec: 화면과 요구사항을 FUNC, 기능 흐름, 예외 흐름으로 전개한다.",
    "G2-05 Program / API Spec: FUNC를 PGM, API, DTO, 오류코드, 서비스 흐름으로 내린다.",
    "G2-06 Data / DB Spec: TERM, WORD, DOMAIN, DB, ERD/DBML, 제약조건을 확정한다.",
    "G2-07 Security Guide: SEC별 정책값, 적용 위치, 오류 메시지, 검증 후보를 확정한다.",
    "G2-08 Development Standard: 패키지 구조, 레이어 규칙, DTO/Entity, 빌드/테스트 명령을 확정한다.",
    "G2-09 SW Architecture Baseline 보강: 상세 설계 결정을 CMP, FLOW, 품질속성, ADR 상태로 되돌려 반영한다.",
    "G2-10 Design Review / Gate 3 승인 대기: 설계 검수 결과, FIND/ISSUE/CR, Gate 3 승인 질문을 남긴다.",
]

AUDIT_GATE_PRESETS = {
    "phase0": {
        "sample": "docs/adapters/codex-gpt/run-input-samples/phase0-discovery.sample.md",
        "required": [
            "docs/templates/PROJECT_BRIEF_TEMPLATE.md",
            "docs/templates/STAKEHOLDER_SCOPE_TEMPLATE.md",
            "docs/templates/AS_IS_TO_BE_TEMPLATE.md",
            "docs/templates/RISK_ASSUMPTION_TEMPLATE.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-002_Stakeholder-And-Scope_v0.1.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-003_As-Is-To-Be_v0.1.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-004_Risk-And-Assumption_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/00-discovery/",
            "docs/runs/",
        ],
        "completion_criteria": [
            "프로젝트 목적, 사용자, 범위, 비목표가 실제 프로젝트 값으로 정리되어 있다.",
            "이해관계자와 승인자, 주요 제약, 참고문서 출처가 식별되어 있다.",
            "As-Is/To-Be와 주요 리스크/가정이 Gate 1 질문으로 이어진다.",
            "Phase 0에서 구현, 테스트 코드, 화면 증적을 만들지 않는다.",
        ],
    },
    "gate1": {
        "sample": "docs/adapters/codex-gpt/run-input-samples/gate1-requirements-review.sample.md",
        "required": [
            "docs/templates/REQUIREMENTS_SPEC_TEMPLATE.md",
            "docs/templates/TRACEABILITY_MATRIX_TEMPLATE.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-002_Stakeholder-And-Scope_v0.1.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-003_As-Is-To-Be_v0.1.md",
            "docs/artifacts/00-discovery/DOC-CORE-P0-004_Risk-And-Assumption_v0.1.md",
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "REQ, NREQ, AC가 실제 기능/품질 요구로 작성되어 있다.",
            "각 요구사항에 출처, 우선순위, 승인 상태, 관련 리스크가 연결되어 있다.",
            "보안, 데이터, 화면, 인터페이스 후보가 Gate 2 설계 입력으로 넘어간다.",
            "요구사항과 인수기준이 추적표에 연결되어 있다.",
        ],
    },
    "gate2": {
        "sample": "docs/adapters/codex-gpt/run-input-samples/gate2-design-review.sample.md",
        "required": [
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/artifacts/02-design/architecture/DOC-ARCH-G2-001_SW-Architecture_v0.1.md",
            "docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md",
            "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md",
            "docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md",
            "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md",
            "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md",
            "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/02-design/",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "REQ/AC가 FUNC, SCR, PGM, API, DB, SEC 설계 ID로 전개되어 있다.",
            "설계 산출물 간 화면, API, 프로그램, 데이터, 보안 연결이 모순되지 않는다.",
            "Gate 2 산출 순서와 현재 Run 위치가 Run 기록에 남아 있다.",
            "SW 아키텍처 Draft/Baseline Candidate/Baseline 성숙도와 Pending/ADR 상태가 기록되어 있다.",
            "화면 퍼블리싱 산출물 또는 외부 시안이 있으면 UI Implementation Contract로 기준 파일, 필수 유지, 변경 허용/금지, 비교 방식을 확정한다.",
            "개발표준과 아키텍처 기준이 구현자가 사용할 수 있을 만큼 구체적이다.",
            "Gate 3 테스트 설계에 넘길 검증 후보가 식별되어 있다.",
        ],
        "design_sequence": AUDIT_GATE2_DESIGN_SEQUENCE,
    },
    "gate3": {
        "sample": "docs/adapters/codex-gpt/run-input-samples/gate3-test-design.sample.md",
        "required": [
            "docs/templates/TEST_CASE_TEMPLATE.md",
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md",
            "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md",
            "docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md",
            "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md",
            "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md",
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "AC, SEC, NREQ가 UT, IT, UI, PT 후보로 전개되어 있다.",
            "각 테스트케이스에 입력, 절차, 기대결과, 증적 방식이 있다.",
            "UI 테스트는 화면 단위가 아니라 상태/시나리오 단위로 UI-001-01처럼 분리되어 있다.",
            "각 UI 테스트는 기대 화면, 실제 확인 방법, 캡처 증적 파일 경로가 1:1로 연결되어 있다.",
            "화면 퍼블리싱 기반 화면은 UI Implementation Contract의 필수 유지/변경 허용/금지 항목을 테스트 기대결과에 반영한다.",
            "자동화 가능 테스트와 수동 검수 테스트가 구분되어 있다.",
            "구현 전에 필요한 테스트 데이터와 환경 제약이 식별되어 있다.",
        ],
    },
    "impl": {
        "sample": "docs/adapters/codex-gpt/run-input-samples/impl-build-wave.sample.md",
        "required": [
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md",
            "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md",
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
        ],
        "writable": [
            "docs/runs/",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/artifacts/04-review/evidence/",
        ],
        "completion_criteria": [
            "승인된 Gate 2/3 범위 안에서만 구현 또는 구현 계획을 작성한다.",
            "화면 구현은 관련 SCR의 UI Implementation Contract와 Gate 3 UI 테스트 기준을 먼저 확인한다.",
            "Build Wave 범위, 소유 파일, 관련 ID, 검증 명령이 명확하다.",
            "구현 변경은 테스트 코드, 테스트 결과, 추적표 갱신과 연결된다.",
            "동시에 active 상태인 Build Wave가 하나만 유지된다.",
        ],
        "verification_commands": [
            "python vulcan.py sync-session",
        ],
    },
    "gate4": {
        "sample": "docs/adapters/codex-gpt/run-input-samples/gate4-qa-review.sample.md",
        "required": [
            "docs/templates/QA_FINDING_TEMPLATE.md",
            "docs/templates/TEST_RESULT_TEMPLATE.md",
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
            "docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md",
            "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md",
            "docs/artifacts/04-review/evidence/",
        ],
        "writable": [
            "docs/artifacts/04-review/",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "실행한 테스트 명령과 결과가 테스트 결과서에 기록되어 있다.",
            "화면/UI 증적 또는 로그 증적이 관련 UI/UT/IT/PT ID와 1:1로 연결되어 있다.",
            "회원가입, 로그인, TODO 같은 UI 흐름은 기본/오류/성공/전환 상태별 캡처가 분리되어 있다.",
            "화면 캡처 증적은 Playwright로 생성되어 있으며, Playwright 미설치 시 설치 명령과 재실행 결과가 기록되어 있다.",
            "CDP, 브라우저 수동 캡처, 런타임 Preview 캡처만으로 UI Pass를 확정하지 않는다.",
            "화면 퍼블리싱 기반 화면은 기준 UIREF와 구현 screenshot의 차이 목록 및 허용 여부가 기록되어 있다.",
            "증적 파일이 기대 화면을 실제로 보여주지 못하면 Pass가 아니라 Fail 또는 Not Run으로 기록되어 있다.",
            "결함은 FIND로 기록하고, 범위 변경은 CR로 승격한다.",
            "수정 완료 결함은 qa-fix-loop Run과 재검증 결과가 연결되어 있다.",
        ],
        "verification_commands": [
            "python vulcan.py sync-session",
        ],
    },
    "gate5": {
        "sample": "docs/adapters/codex-gpt/run-input-samples/gate5-release-approval.sample.md",
        "required": [
            "docs/templates/RELEASE_APPROVAL_TEMPLATE.md",
            "docs/templates/CHANGE_REQUEST_TEMPLATE.md",
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md",
            "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md",
            "docs/artifacts/05-change/",
            "docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md",
            "docs/artifacts/05-change/",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "릴리즈 범위, 제외 범위, 승인자, 잔여 리스크가 명확하다.",
            "미해결 FIND/CR/ISSUE의 처리 상태와 승인 조건이 기록되어 있다.",
            "요구사항, 테스트 결과, 증적, 릴리즈 승인서가 추적표로 연결되어 있다.",
            "인수인계와 운영/롤백 고려사항이 남아 있다.",
        ],
    },
}

AUDIT_GATE_SKILL_PRESETS = {
    ("gate2", "data-standard-review"): {
        "sample": "docs/adapters/codex-gpt/run-input-samples/gate2-data-standard-review.sample.md",
        "required": [
            "docs/core/DATA_STANDARD_RULES.md",
            "docs/core/REFERENCE_STANDARDS.md",
            "docs/templates/PROJECT_GLOSSARY_TEMPLATE.md",
            "docs/templates/DATABASE_SPEC_TEMPLATE.md",
            "docs/artifacts/02-design/data/DOC-DATA-G2-001_Project-Glossary_v0.1.md",
            "docs/artifacts/02-design/data/DOC-DATA-G2-002_Database-Spec_v0.1.md",
            "docs/artifacts/02-design/data/erd/logical/logical-erd.dbml",
            "docs/artifacts/02-design/data/erd/physical/physical-erd.dbml",
            "docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md",
            "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/02-design/data/DOC-DATA-G2-001_Project-Glossary_v0.1.md",
            "docs/artifacts/02-design/data/DOC-DATA-G2-002_Database-Spec_v0.1.md",
            "docs/artifacts/02-design/data/erd/logical/logical-erd.dbml",
            "docs/artifacts/02-design/data/erd/physical/physical-erd.dbml",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "프로젝트 단어사전에 TERM, WORD, DOMAIN 섹션이 실제 프로젝트 값으로 채워져 있다.",
            "공공데이터 공통표준 또는 프로젝트 신규 용어 여부와 등록 사유가 기록되어 있다.",
            "화면 항목명, API 필드명, DB 컬럼명, DOMAIN-ID 매핑이 작성되어 있다.",
            "개인정보/인증정보/시스템정보 등 보안 분류와 관련 SEC-ID가 연결되어 있다.",
            "DB명세서와 논리/물리 DBML의 테이블, 컬럼, PK/FK, 코드 도메인이 일치한다.",
            "미정 또는 작성 전 상태의 placeholder가 남아 있지 않다.",
        ],
    },
    ("gate2", "development-standard-review"): {
        "sample": "docs/adapters/codex-gpt/run-input-samples/gate2-development-standard-review.sample.md",
        "required": [
            "docs/core/TECH_STACK_BASELINES.md",
            "docs/core/SECURITY_BASELINE.md",
            "docs/templates/DEVELOPMENT_STANDARD_TEMPLATE.md",
            "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md",
            "docs/artifacts/02-design/architecture/DOC-ARCH-G2-001_SW-Architecture_v0.1.md",
            "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md",
            "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md",
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "언어, 런타임, 프레임워크, DB, 빌드, 테스트 도구와 선택 근거가 작성되어 있다.",
            "TECH_STACK_BASELINES.md 중 어떤 기준을 준용하고 어떤 점을 프로젝트에 맞게 조정했는지 기록되어 있다.",
            "패키지 구조, 계층 책임, 금지 의존성, DTO/Entity 분리, 트랜잭션 기준이 구현자가 따를 수 있을 만큼 구체적이다.",
            "메시지, 예외, 로그, 설정값, 외부 의존성, 주석/추적 ID 표기 규칙이 있다.",
            "보안 구현 기준이 SECURITY_BASELINE과 SEC-ID에 연결되어 있다.",
            "필수 검증 명령과 증적 위치가 Gate 3/구현 단계로 전달 가능하다.",
        ],
    },
    ("gate2", "security-review"): {
        "required": [
            "docs/core/SECURITY_BASELINE.md",
            "docs/core/KISA_SECURITY_RULES.md",
            "docs/templates/SECURITY_GUIDE_TEMPLATE.md",
            "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md",
            "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md",
            "docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md",
            "docs/artifacts/02-design/data/DOC-DATA-G2-002_Database-Spec_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "SEC-ID별 정책값, 적용 위치, 구현 규칙, 오류 메시지, 검증 방향이 작성되어 있다.",
            "KISA/SR, OWASP, CWE 근거가 필요한 보안 항목에 연결되어 있다.",
            "비밀번호, 토큰, 접근제어, 입력검증, 정보노출 제한이 프로그램/API/DB/화면 설계와 모순되지 않는다.",
            "Gate 3에서 UT/IT/UI로 전개할 보안 검증 후보가 식별되어 있다.",
        ],
    },
    ("gate2", "screen-review"): {
        "required": [
            "docs/templates/SCREEN_SPEC_TEMPLATE.md",
            "docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md",
            "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md",
            "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "필수 화면과 상태가 SCR-ID로 식별되어 있다.",
            "각 화면에 입력 항목, 이벤트, 메시지, 호출 API/프로그램, 관련 SEC-ID가 연결되어 있다.",
            "와이어프레임, 이미지, HTML/CSS/JS 화면 퍼블리싱 산출물, 또는 동등한 화면 구조 증적이 있다.",
            "UIREF가 참고자료인지 구현 기준인지 구분되고, 구현 기준이면 필수 유지/변경 허용/금지 항목이 정의되어 있다.",
            "Gate 3 UI 테스트와 Gate 4 캡처 증적 기준이 작성되어 있다.",
        ],
    },
    ("gate2", "ui-review"): {
        "required": [
            "docs/templates/SCREEN_SPEC_TEMPLATE.md",
            "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md",
            "docs/artifacts/02-design/screen/ui-baseline/",
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
        ],
        "writable": [
            "docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md",
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
            "docs/runs/",
        ],
        "completion_criteria": [
            "구현자가 화면 밀도, 레이아웃, 상태, 메시지, 반응형 기준을 판단할 수 있다.",
            "desktop/mobile viewport와 비교 기준이 명시되어 있다.",
            "화면 퍼블리싱 산출물 또는 외부 시안이 구현 계약으로 전환되어 필수 유지 요소와 허용 차이가 명확하다.",
            "빈 상태, 오류 상태, 인증 필요 상태, 성공 상태의 UI 기준이 상태/시나리오별 UI-ID로 분리되어 있다.",
            "실제 캡처 증적 경로와 UI-ID 후보가 Gate 3/4로 1:1 전달된다.",
        ],
    },
    ("impl", "implementation-plan"): {
        "writable": [
            "docs/runs/",
            "session.json",
        ],
        "completion_criteria": [
            "Build Wave 후보와 각 Wave의 소유 파일, 관련 ID, 검증 명령이 나뉘어 있다.",
            "화면 구현 Wave는 UI Implementation Contract 준수 체크와 screenshot 비교 증적 위치가 정의되어 있다.",
            "구현 착수 전 사용자 승인 또는 명시적인 진행 지시가 필요한 항목이 식별되어 있다.",
        ],
    },
    ("impl", "build-wave"): {
        "writable": [
            "docs/runs/",
            "docs/artifacts/04-review/evidence/",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        ],
        "completion_criteria": [
            "Wave 하나의 범위만 수정하고 다른 Wave 범위는 건드리지 않는다.",
            "화면 구현은 UI Implementation Contract의 필수 유지 요소, 허용 변경, 금지 변경을 준수한다.",
            "구현 결과, 테스트 결과, 증적, 추적표 갱신이 같은 Run에 기록되어 있다.",
        ],
    },
    ("gate4", "qa-fix-loop"): {
        "required": [
            "docs/adapters/codex-gpt/skills/qa-fix-loop.md",
        ],
        "completion_criteria": [
            "승인된 설계 범위 안의 결함만 FIND로 수정한다.",
            "요구사항 또는 범위 변경이 필요한 항목은 CR로 승격한다.",
            "재검증 명령과 결과가 테스트 결과서에 반영되어 있다.",
        ],
    },
    ("gate5", "change-impact-analysis"): {
        "completion_criteria": [
            "릴리즈 전 변경요청의 영향 Gate, 영향 산출물, 승인 조건이 정리되어 있다.",
            "릴리즈 보류/승인/조건부 승인 판단 근거가 남아 있다.",
        ],
    },
}


# ── 공통 유틸 ──────────────────────────────────────────────────────────────

def render(text, variables):
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def read_template(rel_path):
    path = os.path.join(TEMPLATES_DIR, rel_path)
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_file(target_dir, rel_path, content):
    full_path = os.path.join(target_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  생성: {rel_path}")


def copy_file(target_dir, rel_path, src_rel_path=None):
    import shutil
    src = os.path.join(TEMPLATES_DIR, src_rel_path or rel_path)
    dst = os.path.join(target_dir, rel_path)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  생성: {rel_path}")


def copy_tree(src_dir, dst_dir):
    """디렉토리 트리를 재귀적으로 복사합니다."""
    import shutil
    for root, dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        for f in files:
            src = os.path.join(root, f)
            rel_path = os.path.join(rel_root, f) if rel_root != "." else f
            dst = os.path.join(dst_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def copy_source_tree(target_dir, rel_dir, variables=None, overwrite=True, source_root=None):
    """Copy a repository directory into the target project.

    Markdown and JSON files are rendered with project variables; binary files are copied as-is.
    """
    import shutil

    src_dir = os.path.join(source_root or VULCAN_DIR, rel_dir)
    if not os.path.isdir(src_dir):
        return 0

    copied = 0
    render_exts = {".md", ".json", ".txt", ".yml", ".yaml"}
    for root, dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        for f in files:
            src = os.path.join(root, f)
            child_rel = os.path.join(rel_root, f) if rel_root != "." else f
            dst_rel = os.path.join(rel_dir, child_rel)
            dst = os.path.join(target_dir, dst_rel)

            if os.path.exists(dst) and not overwrite:
                continue

            os.makedirs(os.path.dirname(dst), exist_ok=True)
            ext = os.path.splitext(f)[1].lower()
            if variables is not None and ext in render_exts:
                with open(src, encoding="utf-8") as fp:
                    content = render(fp.read(), variables)
                with open(dst, "w", encoding="utf-8") as fp:
                    fp.write(content)
            else:
                shutil.copy2(src, dst)
            copied += 1
    return copied


def install_project_doc_framework(target_dir, variables, overwrite=True, source_root=None):
    """Install audit/agent document framework files into a project."""
    source_root = source_root or VULCAN_DIR

    for rel_path in PROJECT_ROOT_FILES:
        src = os.path.join(source_root, rel_path)
        dst = os.path.join(target_dir, rel_path)
        if not os.path.isfile(src):
            continue
        if os.path.exists(dst) and not overwrite:
            continue
        with open(src, encoding="utf-8") as fp:
            content = render(fp.read(), variables)
        with open(dst, "w", encoding="utf-8") as fp:
            fp.write(content)
        print(f"  install/update: {rel_path}")

    for rel_dir in PROJECT_DOC_SETS:
        copied = copy_source_tree(
            target_dir,
            rel_dir,
            variables=variables,
            overwrite=overwrite,
            source_root=source_root,
        )
        if copied:
            print(f"  install/update: {rel_dir}/ ({copied} files)")

    for rel_dir in PROJECT_DOC_DIRS:
        write_file(target_dir, os.path.join(rel_dir, ".gitkeep"), "")


def install_project_artifacts(target_dir, variables, overwrite=False, source_root=None):
    """Install official Ex artifact working documents into docs/artifacts/."""
    source_root = source_root or VULCAN_DIR

    for src_rel, dst_rel in PROJECT_ARTIFACT_TEMPLATES:
        src = os.path.join(source_root, src_rel)
        dst = os.path.join(target_dir, dst_rel)
        if not os.path.isfile(src):
            continue
        if os.path.exists(dst) and not overwrite:
            continue
        with open(src, encoding="utf-8") as fp:
            content = render(fp.read(), variables)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as fp:
            fp.write(content)
        print(f"  install/update: {dst_rel}")


def ensure_gitignore_entry(project_dir, entry):
    path = os.path.join(project_dir, ".gitignore")
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.read()

    lines = {line.strip() for line in existing.splitlines()}
    if entry.strip() in lines:
        return

    suffix = "" if not existing or existing.endswith("\n") else "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(existing + suffix + entry.rstrip() + "\n")
    print(f"  update: .gitignore ({entry})")


def slugify(value):
    value = value.strip().lower()
    value = re.sub(r"[^0-9a-zA-Z가-힣_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "run"


def split_csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def runs_rel_dir(project_dir="."):
    docs_runs = os.path.join(project_dir, "docs", "runs")
    root_runs = os.path.join(project_dir, "runs")
    if os.path.isdir(docs_runs):
        return os.path.join("docs", "runs")
    if os.path.isdir(root_runs):
        return "runs"
    return os.path.join("docs", "runs")


def next_run_id(project_dir="."):
    runs_dir = os.path.join(project_dir, runs_rel_dir(project_dir))
    max_num = 0
    if os.path.isdir(runs_dir):
        for name in os.listdir(runs_dir):
            match = re.match(r"RUN-(\d+)", name)
            if match:
                max_num = max(max_num, int(match.group(1)))
    return f"RUN-{max_num + 1:03d}"


def reviews_rel_dir(project_dir="."):
    docs_reviews = os.path.join(project_dir, "docs", "reviews")
    if os.path.isdir(docs_reviews):
        return os.path.join("docs", "reviews")
    return os.path.join("docs", "reviews")


def next_review_id(project_dir="."):
    reviews_dir = os.path.join(project_dir, reviews_rel_dir(project_dir))
    max_num = 0
    if os.path.isdir(reviews_dir):
        for name in os.listdir(reviews_dir):
            match = re.match(r"RV-(\d+)", name)
            if match:
                max_num = max(max_num, int(match.group(1)))
    return f"RV-{max_num + 1:03d}"


def find_review_file(project_dir, review_id, suffix):
    reviews_dir = os.path.join(project_dir, reviews_rel_dir(project_dir))
    if not os.path.isdir(reviews_dir):
        return ""
    for name in sorted(os.listdir(reviews_dir)):
        if name.startswith(f"{review_id}_") and name.endswith(suffix):
            return os.path.join(reviews_rel_dir(project_dir), name)
    return ""


def find_independent_review_run_file(project_dir, review_id):
    runs_dir = os.path.join(project_dir, runs_rel_dir(project_dir))
    if not os.path.isdir(runs_dir):
        return ""
    for name in sorted(os.listdir(runs_dir)):
        if not name.endswith(".md") or "independent-review" not in name:
            continue
        path = os.path.join(runs_dir, name)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        if re.search(rf"^\s*review_id\s*:\s*{re.escape(review_id)}\s*$", content, re.MULTILINE):
            return os.path.join(runs_rel_dir(project_dir), name)
    return ""


def format_yaml_list(items):
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


def format_yaml_scalar(value):
    return json.dumps(value, ensure_ascii=False)


def file_sha256(path):
    if not os.path.exists(path):
        return ""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_yaml_sequence(items, indent=0):
    spaces = " " * indent
    if not items:
        return f"{spaces}[]"
    return "\n".join(f"{spaces}- {format_yaml_scalar(item)}" for item in items)


def merge_unique(*item_lists):
    merged = []
    seen = set()
    for items in item_lists:
        for item in items or []:
            if item not in seen:
                merged.append(item)
                seen.add(item)
    return merged


def is_working_document(path):
    normalized = path.replace("\\", "/")
    return normalized.startswith("docs/artifacts/")


def split_working_and_reference(paths):
    working = []
    reference = []
    for path in paths:
        if is_working_document(path):
            working.append(path)
        else:
            reference.append(path)
    return working, reference


def load_delivery_profile(project_dir="."):
    path = os.path.join(project_dir, "session.json")
    if not os.path.exists(path):
        return DEFAULT_DELIVERY_PROFILE

    try:
        with open(path, encoding="utf-8") as f:
            session = json.load(f)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_DELIVERY_PROFILE

    profile = session.get("profile") or session.get("delivery_profile") or DEFAULT_DELIVERY_PROFILE
    return str(profile).strip().lower() or DEFAULT_DELIVERY_PROFILE


def build_run_input_preset(profile, gate, skill, skill_path, run_rel_path):
    if profile != "audit":
        return None

    gate_preset = AUDIT_GATE_PRESETS.get(gate)
    if not gate_preset:
        return None

    skill_preset = AUDIT_GATE_SKILL_PRESETS.get((gate, skill), {})
    gate_sample = gate_preset.get("sample")
    skill_sample = skill_preset.get("sample")
    skill_required = skill_preset.get("required", [])
    skill_has_working_docs = any(is_working_document(path) for path in skill_required)
    focused_source = skill in AUDIT_FOCUSED_SOURCE_SKILLS
    if skill_has_working_docs:
        source_candidates = merge_unique(AUDIT_GATE_ANCHOR_DOCS.get(gate, []), skill_required)
    elif focused_source:
        source_candidates = merge_unique(AUDIT_GATE_ANCHOR_DOCS.get(gate, []), skill_required)
    else:
        source_candidates = merge_unique(gate_preset.get("required", []), skill_required)
    working_documents, reference_documents = split_working_and_reference(source_candidates)
    source_read_first = merge_unique(
        AUDIT_COMMON_READ_FIRST_DOCS,
        AUDIT_GATE_READ_FIRST_DOCS.get(gate, []),
        [skill_path],
    )
    source_reference = merge_unique(
        AUDIT_COMMON_REFERENCE_DOCS,
        [gate_sample] if gate_sample else [],
        [skill_sample] if skill_sample else [],
        reference_documents,
    )
    source_reference = [path for path in source_reference if path not in source_read_first]
    run_rel_path = run_rel_path.replace("\\", "/")
    verification_commands = merge_unique(
        [f"python vulcan.py run-check {run_rel_path}", "python vulcan.py check-trace"],
        gate_preset.get("verification_commands", []),
        skill_preset.get("verification_commands", []),
    )
    evidence_targets = merge_unique(
        [run_rel_path, "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md"],
        gate_preset.get("evidence_targets", []),
        skill_preset.get("evidence_targets", []),
    )
    writable_scope = skill_preset.get("writable") or gate_preset.get("writable", [])
    completion_criteria = (
        skill_preset.get("completion_criteria", [])
        if skill_has_working_docs and skill_preset.get("completion_criteria")
        else merge_unique(gate_preset.get("completion_criteria", []), skill_preset.get("completion_criteria", []))
    )
    return {
        "profile": profile,
        "run_type": RUN_TYPES_BY_GATE.get(gate, "Review"),
        "focused_source": focused_source,
        "source_documents": {
            "read_first": source_read_first,
            "working_documents": working_documents,
            "reference_on_demand": source_reference,
            "optional": merge_unique(gate_preset.get("optional", []), skill_preset.get("optional", [])),
        },
        "scope": {
            "writable": merge_unique(writable_scope),
            "readonly": merge_unique(AUDIT_COMMON_READONLY_DOCS, gate_preset.get("readonly", []), skill_preset.get("readonly", [])),
            "excluded": merge_unique(AUDIT_COMMON_EXCLUDED_PATHS, gate_preset.get("excluded", []), skill_preset.get("excluded", [])),
        },
        "completion_criteria": completion_criteria,
        "design_sequence": (
            merge_unique(gate_preset.get("design_sequence", []), skill_preset.get("design_sequence", []))
            if gate != "gate2" or skill in AUDIT_DESIGN_SEQUENCE_SKILLS
            else []
        ),
        "include_ui_policies": gate in ("gate3", "impl", "gate4") or skill in AUDIT_UI_POLICY_SKILLS,
        "verification": {
            "commands": verification_commands,
            "evidence": {
                "required": True,
                "target_documents": evidence_targets,
            },
        },
        "gate_exit_policy": AUDIT_GATE_EXIT_POLICY,
        "ui_evidence_policy": AUDIT_UI_EVIDENCE_POLICY,
        "ui_implementation_contract_policy": AUDIT_UI_IMPLEMENTATION_CONTRACT_POLICY,
        "worker_execution_policy": AUDIT_WORKER_EXECUTION_POLICY,
        "output_requirements": {
            "format": "RUN_OUTPUT_CONTRACT.md",
            "include": [
                "changed_files",
                "related_ids",
                "verification_results",
                "evidence",
                "traceability_updates",
                "gate_exit_summary",
                "approval_request",
                "open_issues",
                "next_run_suggestion",
            ],
        },
        "question_policy": {
            "ask_when": [
                "요구사항, 설계문서, 기준 문서가 서로 충돌한다.",
                "scope.writable 밖의 파일 수정이 필요하다.",
                "프로젝트 도메인 정보가 부족해 실제 값을 채울 수 없다.",
                "보안 또는 감리 기준을 낮추는 선택이 필요하다.",
            ],
        },
        "security_policy": {
            "forbidden_paths": ["docs/ref-docs/"],
            "allowed_reference_paths": ["docs/seed-docs/reference-standards/"],
            "forbidden_actions": [
                "민감문서 내용을 출력에 원문 인용하지 않는다.",
                "토큰, 비밀번호, 개인식별정보를 커밋하지 않는다.",
                "승인 없이 외부 네트워크로 프로젝트 파일을 전송하지 않는다.",
            ],
        },
    }


def render_run_input_preset(preset, ids, persona, gate):
    source = preset["source_documents"]
    scope = preset["scope"]
    verification = preset["verification"]
    evidence = verification["evidence"]
    output = preset["output_requirements"]
    question = preset["question_policy"]
    security = preset["security_policy"]
    gate_exit = preset["gate_exit_policy"]
    ui_evidence = preset["ui_evidence_policy"]
    ui_contract = preset["ui_implementation_contract_policy"]
    worker_policy = preset["worker_execution_policy"]
    design_sequence = preset.get("design_sequence", [])
    design_sequence_block = ""
    design_sequence_instruction = ""
    if design_sequence:
        design_sequence_block = f"""
design_sequence:
{format_yaml_sequence(design_sequence, 2)}"""
        design_sequence_instruction = """
   - Gate 2 Run이면 `design_sequence`에서 현재 위치를 확인하고, 필요한 이전 단계 누락과 다음 Gate 2 Run 제안을 기록한다."""
    ui_evidence_block = ""
    ui_contract_block = ""
    if preset.get("include_ui_policies", True):
        ui_evidence_block = f"""
ui_evidence_policy:
  state_level_required: {str(ui_evidence["state_level_required"]).lower()}
  id_pattern: {format_yaml_scalar(ui_evidence["id_pattern"])}
  minimum_fields:
{format_yaml_sequence(ui_evidence["minimum_fields"], 4)}
  examples:
{format_yaml_sequence(ui_evidence["examples"], 4)}"""
        ui_contract_block = f"""
ui_implementation_contract_policy:
  required_when: {format_yaml_scalar(ui_contract["required_when"])}
  gate2_required_fields:
{format_yaml_sequence(ui_contract["gate2_required_fields"], 4)}
  impl_checklist:
{format_yaml_sequence(ui_contract["impl_checklist"], 4)}
  gate4_required_evidence:
{format_yaml_sequence(ui_contract["gate4_required_evidence"], 4)}"""
        ui_instruction_block = """
8. UI 검증이 포함되면 `ui_evidence_policy`에 따라 상태/시나리오별 UI-ID와 증적 파일을 1:1로 연결한다.
9. UIREF, 화면 퍼블리싱 산출물, 외부 시안이 있으면 `ui_implementation_contract_policy`에 따라 설계-구현-증적 비교 기준을 남긴다.
10. subagent, CLI, 별도 worktree에서 작업자 runner로 실행 중이면 `worker_execution_policy`를 따른다.
11. 기준 충돌, 범위 초과, 도메인 정보 부족은 임의로 통과시키지 말고 `open_issues`에 남기거나 사용자에게 질문한다.
12. Gate 산출물 완료 후에는 다음 Gate로 진행하지 말고 사용자 승인 질문을 남긴 뒤 대기한다."""
    else:
        ui_instruction_block = """
8. subagent, CLI, 별도 worktree에서 작업자 runner로 실행 중이면 `worker_execution_policy`를 따른다.
9. 기준 충돌, 범위 초과, 도메인 정보 부족은 임의로 통과시키지 말고 `open_issues`에 남기거나 사용자에게 질문한다.
10. Gate 산출물 완료 후에는 다음 Gate로 진행하지 말고 사용자 승인 질문을 남긴 뒤 대기한다."""

    read_first_docs = source.get("read_first", [])
    working_docs = source.get("working_documents", [])
    reference_docs = source.get("reference_on_demand", [])
    optional_docs = source.get("optional", [])
    return f"""## 3. Run 입력 계약

```yaml
profile: {format_yaml_scalar(preset["profile"])}
run_type: {format_yaml_scalar(preset["run_type"])}
gate: {format_yaml_scalar(gate)}
related_ids: {format_yaml_list(ids)}
persona: {format_yaml_scalar(persona)}
source_documents:
  read_first:
{format_yaml_sequence(read_first_docs, 4)}
  working_documents:
{format_yaml_sequence(working_docs, 4)}
  reference_on_demand:
{format_yaml_sequence(reference_docs, 4)}
  optional:
{format_yaml_sequence(optional_docs, 4)}{design_sequence_block}
scope:
  writable:
{format_yaml_sequence(scope["writable"], 4)}
  readonly:
{format_yaml_sequence(scope["readonly"], 4)}
  excluded:
{format_yaml_sequence(scope["excluded"], 4)}
completion_criteria:
{format_yaml_sequence(preset["completion_criteria"], 2)}
verification:
  commands:
{format_yaml_sequence(verification["commands"], 4)}
  evidence:
    required: {str(evidence["required"]).lower()}
    target_documents:
{format_yaml_sequence(evidence["target_documents"], 6)}
gate_exit_policy:
  stop_required: {str(gate_exit["stop_required"]).lower()}
  next_gate_requires_user_approval: {str(gate_exit["next_gate_requires_user_approval"]).lower()}
  approval_evidence_required: {str(gate_exit["approval_evidence_required"]).lower()}
  allowed_next_action: {format_yaml_scalar(gate_exit["allowed_next_action"])}
  forbidden_actions:
{format_yaml_sequence(gate_exit["forbidden_actions"], 4)}{ui_evidence_block}{ui_contract_block}
worker_execution_policy:
  applies_when: {format_yaml_scalar(worker_policy["applies_when"])}
  role: {format_yaml_scalar(worker_policy["role"])}
  forbidden_actions:
{format_yaml_sequence(worker_policy["forbidden_actions"], 4)}
  required_outputs:
{format_yaml_sequence(worker_policy["required_outputs"], 4)}
output_requirements:
  format: {format_yaml_scalar(output["format"])}
  include:
{format_yaml_sequence(output["include"], 4)}
question_policy:
  ask_when:
{format_yaml_sequence(question["ask_when"], 4)}
security_policy:
  forbidden_paths:
{format_yaml_sequence(security["forbidden_paths"], 4)}
  allowed_reference_paths:
{format_yaml_sequence(security["allowed_reference_paths"], 4)}
  forbidden_actions:
{format_yaml_sequence(security["forbidden_actions"], 4)}
```

## 4. 수행 지시

1. `source_documents.read_first`만 먼저 읽고 현재 Gate, skill, 관련 ID를 확인한다.
2. `source_documents.working_documents`를 중심으로 실제 산출물을 작성하거나 검토한다.
3. `source_documents.reference_on_demand`는 기준 충돌, 작성 규칙 확인, 상세 판단이 필요할 때만 참고한다.
4. `scope.writable` 안에서만 산출물을 수정한다.{design_sequence_instruction}
5. `completion_criteria`를 모두 만족하도록 문서, 추적표, Run 기록을 갱신한다.
6. 실제 프로젝트 값으로 작성하고 placeholder를 완료 산출물에 남기지 않는다.
7. `verification.commands`를 실행하고 결과를 이 Run 기록에 남긴다.
{ui_instruction_block}

## 5. Gate 종료 및 승인 대기

Run을 완료할 때 다음 항목을 반드시 남긴다.

| 항목 | 작성 기준 |
| --- | --- |
| 현재 Gate 산출물 요약 | 이번 Gate에서 작성/수정한 산출물과 관련 ID |
| 미해결 항목 | `open_issues`, `findings`, `change_requests` |
| 다음 Gate 제안 | 다음 Gate에서 수행할 Run 후보 |
| 사용자 승인 질문 | "다음 Gate로 진행해도 되는지"를 명시적으로 질문 |
| 승인 증적 | 대화에서 사용자가 명시 승인한 문구 또는 승인 보류 사유 |

사용자 승인 전에는 다음 Gate 산출물 작성, 구현 착수, QA Pass, Gate 5 승인 선언을 하지 않는다."""


def default_persona_for_run(gate, skill):
    skill_persona = RUN_SKILL_DEFAULT_PERSONAS.get(skill)
    if skill_persona:
        return skill_persona

    return GATE_DEFAULT_PERSONAS.get(gate, "review")


def load_session(project_dir="."):
    path = os.path.join(project_dir, "session.json")
    if not os.path.exists(path):
        print("오류: session.json을 찾을 수 없습니다. 프로젝트 디렉토리에서 실행하세요.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_session(session, project_dir="."):
    path = os.path.join(project_dir, "session.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)


def git_commit(message, project_dir=".", include_source=False, paths=None):
    try:
        if paths is None:
            paths = ["session.json", "docs/"]
        for path in paths:
            subprocess.run(["git", "add", path], cwd=project_dir, check=True, capture_output=True)
        if include_source:
            # 구현/QA 이후: .gitignore가 관리하는 범위 내에서 모든 변경 포함
            subprocess.run(["git", "add", "-A"], cwd=project_dir, check=True, capture_output=True)

        staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=project_dir)
        if staged.returncode == 0:
            print(f"  커밋 생략: 변경 없음 ({message})")
            return False

        subprocess.run(["git", "commit", "-m", message], cwd=project_dir, check=True, capture_output=True)
        print(f"  커밋 완료: {message}")
        return True
    except subprocess.CalledProcessError as e:
        # git commit 실패는 경고만 출력하고 계속 진행 (git_push와 다른 동작)
        stdout = e.stdout.decode(errors="replace").strip() if e.stdout else ""
        stderr = e.stderr.decode(errors="replace").strip() if e.stderr else ""
        detail = "\n".join(part for part in [stderr, stdout] if part).strip()
        print(f"  경고: git commit 실패 - {detail or '상세 메시지 없음'}")
        return False


def git_push(project_dir="."):
    """현재 프로젝트 디렉토리에서 git push를 실행합니다.

    git commit과 달리 push 실패는 프로세스를 즉시 중단합니다 (REQ-006-02).

    Args:
        project_dir: git push를 실행할 프로젝트 디렉토리 경로.
    """
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=project_dir,
            check=True,
            capture_output=True,
        )
        print(f"  푸시 완료")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="replace").strip()
        if "has no upstream branch" in stderr:
            try:
                subprocess.run(
                    ["git", "push", "-u", "origin", "HEAD"],
                    cwd=project_dir,
                    check=True,
                    capture_output=True,
                )
                print("  푸시 완료: origin HEAD")
                return
            except subprocess.CalledProcessError as retry_error:
                stderr = retry_error.stderr.decode(errors="replace").strip()
        print(f"git push 실패: {stderr}")
        sys.exit(1)


def has_git_remote(project_dir=".", remote="origin"):
    result = subprocess.run(
        ["git", "remote", "get-url", remote],
        cwd=project_dir,
        capture_output=True,
    )
    return result.returncode == 0


def version_run_document(rel_path, message, project_dir="."):
    committed = git_commit(message, project_dir, paths=[rel_path])
    if not committed:
        return
    git_push_if_remote(project_dir)


def git_push_if_remote(project_dir="."):
    if has_git_remote(project_dir):
        git_push(project_dir)
        return True
    print("  푸시 생략: git remote origin 없음")
    return False


# ── check-trace ────────────────────────────────────────────────────────────

def count_docs(project_dir="."):
    """docs/ 하위 4개 디렉토리의 .md 파일 수를 카운트한다.

    서브디렉토리 내 .md 파일도 포함한다. 디렉토리가 없거나 권한 오류 시
    해당 카테고리를 0으로 처리하고 계속 진행한다 (graceful).

    Args:
        project_dir: 프로젝트 루트 디렉토리 경로.

    Returns:
        requirements, design, test_plan, review 카테고리별 .md 파일 수와
        total 합계를 담은 dict.
    """
    categories = {
        "discovery": [
            os.path.join(project_dir, "docs", "artifacts", "00-discovery"),
            os.path.join(project_dir, "docs", "00-discovery"),
        ],
        "requirements": [
            os.path.join(project_dir, "docs", "artifacts", "01-requirements"),
            os.path.join(project_dir, "docs", "01-requirements"),
        ],
        "design": [
            os.path.join(project_dir, "docs", "artifacts", "02-design"),
            os.path.join(project_dir, "docs", "02-design"),
        ],
        "test_plan": [
            os.path.join(project_dir, "docs", "artifacts", "03-test"),
            os.path.join(project_dir, "docs", "03-test-plan"),
        ],
        "review": [
            os.path.join(project_dir, "docs", "artifacts", "04-review"),
            os.path.join(project_dir, "docs", "04-review"),
        ],
        "release": [
            os.path.join(project_dir, "docs", "artifacts", "07-release"),
        ],
        "backlog": [
            os.path.join(project_dir, "docs", "artifacts", "05-change"),
            os.path.join(project_dir, "docs", "backlog"),
        ],
        "runs": [
            os.path.join(project_dir, "docs", "runs"),
        ],
    }
    counts = {}
    for key, dir_paths in categories.items():
        count = 0
        existing_dirs = [dir_path for dir_path in dir_paths if os.path.isdir(dir_path)]
        dirs_to_count = existing_dirs[:1]
        for dir_path in dirs_to_count:
            try:
                for root, _dirs, files in os.walk(dir_path):
                    count += sum(1 for f in files if f.endswith(".md"))
            except OSError:
                # 디렉토리 미존재 또는 권한 오류 — 0으로 처리하고 계속 진행
                continue
        counts[key] = count
    counts["total"] = sum(counts.values())
    return counts


def find_first_existing(project_dir, candidates):
    for rel_path in candidates:
        path = os.path.join(project_dir, rel_path)
        if os.path.exists(path):
            return path
    return None


def find_artifact_file(project_dir, rel_dir, name_pattern):
    base = os.path.join(project_dir, rel_dir)
    if not os.path.isdir(base):
        return None
    for root, _dirs, files in os.walk(base):
        for filename in files:
            if re.search(name_pattern, filename, re.IGNORECASE):
                return os.path.join(root, filename)
    return None


def compute_stats(project_dir="."):
    """check-trace에서 수집한 파싱 결과를 조합하여 stats 딕셔너리를 조립한다.

    parse_requirements, parse_test_plan_status, count_docs, parse_traceability를
    호출하여 요구사항/테스트/문서 통계를 단일 dict로 반환한다. 파싱 실패 시
    해당 섹션을 0 기본값으로 채우고 예외를 전파하지 않는다.

    Args:
        project_dir: 프로젝트 루트 디렉토리 경로.

    Returns:
        requirements, tests, docs 섹션과 updated_at을 포함한 stats dict.
    """
    # requirements 섹션
    try:
        group_reqs, detail_reqs, defined_acs, ac_delegates = parse_requirements(project_dir)
        traceability = parse_traceability(project_dir)
        implemented = sum(
            1 for info in traceability.values()
            if info.get("status") in ("구현완료", "완료", "Implemented", "Verified")
        )
        total_reqs = len(detail_reqs)
        # ac가 있는 REQ: defined_acs에 해당 AC-ID가 있거나 ac_delegates에 위임 참조가 있는 경우
        ac_covered = sum(
            1 for req in detail_reqs
            if req.replace("REQ-", "") in defined_acs
            or req.replace("REQ-", "") in ac_delegates
        )
        requirements_stats = {
            "groups":      len(group_reqs),
            "total":       total_reqs,
            "implemented": implemented,
            "pending":     total_reqs - implemented,
            "ac_defined":  ac_covered,
            "ac_missing":  total_reqs - ac_covered,
        }
    except Exception:
        requirements_stats = {
            "groups": 0, "total": 0, "implemented": 0,
            "pending": 0, "ac_defined": 0, "ac_missing": 0,
        }

    # tests 섹션
    try:
        tst_results = parse_test_plan_status(project_dir)
        tests_stats = {
            "total":   len(tst_results),
            "passed":  sum(1 for _, s in tst_results if s == "pass"),
            "failed":  sum(1 for _, s in tst_results if s == "fail"),
            "skipped": sum(1 for _, s in tst_results if s == "skip"),
            "pending": sum(1 for _, s in tst_results if s == "not_executed"),
        }
    except Exception:
        tests_stats = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "pending": 0}

    # docs 섹션
    try:
        docs_stats = count_docs(project_dir)
    except Exception:
        docs_stats = {"requirements": 0, "design": 0, "test_plan": 0, "review": 0, "total": 0}

    # backlog 섹션
    try:
        backlog_stats = compute_backlog_stats(project_dir)
    except Exception:
        backlog_stats = {
            "active": 0, "done": 0, "rejected": 0,
            "by_level": {"trivial": 0, "small": 0, "major": 0},
            "by_priority": {"p0": 0, "p1": 0, "p2": 0, "p3": 0},
        }

    try:
        implementation_stats = compute_implementation_progress(project_dir)
    except Exception:
        implementation_stats = {
            "requirements": {"total": 0, "implemented": 0, "pending": 0, "completed_ids": []},
            "waves": {"total": 0, "completed": 0, "current": "", "items": []},
        }

    return {
        "requirements": requirements_stats,
        "implementation": implementation_stats,
        "tests":        tests_stats,
        "docs":         docs_stats,
        "backlog":      backlog_stats,
        "updated_at":   date.today().isoformat(),
    }


WAVE_DONE_STATUSES = {"Implemented", "Verified", "Completed", "Done"}
WAVE_ACTIVE_STATUSES = {"In Progress", "Running", "Review Requested"}
WAVE_KNOWN_STATUSES = WAVE_DONE_STATUSES | WAVE_ACTIVE_STATUSES | {"Planned", "Blocked", "Rolled Back"}
WAVE_STATUS_RANK = {
    "Planned": 0,
    "In Progress": 1,
    "Running": 1,
    "Review Requested": 2,
    "Blocked": 2,
    "Implemented": 3,
    "Verified": 4,
    "Completed": 4,
    "Done": 4,
    "Rolled Back": 4,
}


def find_run_files(project_dir="."):
    runs_dir = os.path.join(project_dir, runs_rel_dir(project_dir))
    if not os.path.isdir(runs_dir):
        return []
    return [
        os.path.join(runs_dir, name)
        for name in sorted(os.listdir(runs_dir))
        if name.lower().endswith(".md")
    ]


def find_wave_run_file(project_dir, bw_id):
    pattern = re.compile(rf"\b{re.escape(bw_id)}\b", re.IGNORECASE)
    for path in find_run_files(project_dir):
        if pattern.search(os.path.basename(path)):
            return path

    for path in find_run_files(project_dir):
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue
        if pattern.search(content) or pattern.search(os.path.basename(path)):
            return path
    return None


def parse_simple_yaml_block(content):
    match = re.search(r"```yaml\s*(.*?)```", content, re.DOTALL | re.IGNORECASE)
    if not match:
        return {}
    result = {}
    for raw_line in match.group(1).splitlines():
        if raw_line.startswith((" ", "\t", "-")):
            continue
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def collect_build_wave_records(project_dir="."):
    records = {}

    for path in find_run_files(project_dir):
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except OSError:
            continue

        rel_path = os.path.relpath(path, project_dir)
        metadata = parse_simple_yaml_block(content)
        ids = set(re.findall(r"\bBW-\d{3}\b", content))
        if metadata.get("bw_id"):
            ids.add(metadata["bw_id"])

        for bw_id in sorted(ids):
            record = records.setdefault(
                bw_id,
                {"id": bw_id, "status": "Planned", "run": "", "related_ids": []},
            )
            if not record.get("run") and "build-wave" in content.lower():
                record["run"] = rel_path

            if metadata.get("bw_id") == bw_id or bw_id.lower() in os.path.basename(path).lower():
                status = metadata.get("status")
                if status in WAVE_KNOWN_STATUSES:
                    record["status"] = status
                    record["run"] = rel_path

            related = re.findall(
                r"\b(?:REQ|AC|FUNC|SCR|UIREF|UICON|PGM|DB|SEC|UT|IT|PT|UI)-\d{3}(?:-\d{2})?\b",
                content,
            )
            record["related_ids"] = sorted(set(record.get("related_ids", []) + related))

        for line in content.splitlines():
            if not line.strip().startswith("|"):
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cols or re.fullmatch(r"[-: ]+", cols[0] or ""):
                continue
            bw_cols = [c for c in cols if re.fullmatch(r"BW-\d{3}", c)]
            if not bw_cols:
                continue
            bw_id = bw_cols[0]
            record = records.setdefault(
                bw_id,
                {"id": bw_id, "status": "Planned", "run": "", "related_ids": []},
            )
            if not record.get("run"):
                record["run"] = rel_path
            for col in cols:
                if col in WAVE_KNOWN_STATUSES:
                    record["status"] = col
                    break
            related = [
                item
                for col in cols
                for item in re.findall(
                    r"\b(?:REQ|AC|FUNC|SCR|UIREF|UICON|PGM|DB|SEC|UT|IT|PT|UI)-\d{3}(?:-\d{2})?\b",
                    col,
                )
            ]
            record["related_ids"] = sorted(set(record.get("related_ids", []) + related))

    return [records[key] for key in sorted(records)]


def merge_session_wave_records(session, discovered):
    merged = {item["id"]: dict(item) for item in discovered}
    session_impl = session.get("implementation", {}) if session else {}
    session_waves = session_impl.get("waves", {}) if isinstance(session_impl, dict) else {}
    for item in session_waves.get("items", []) if isinstance(session_waves, dict) else []:
        bw_id = item.get("id")
        if not bw_id:
            continue
        base = merged.setdefault(
            bw_id,
            {"id": bw_id, "status": "Planned", "run": "", "related_ids": []},
        )
        session_status = item.get("status")
        base_status = base.get("status")
        session_rank = WAVE_STATUS_RANK.get(session_status, -1)
        base_rank = WAVE_STATUS_RANK.get(base_status, -1)
        if session_status and session_rank >= base_rank:
            base["status"] = session_status
            if item.get("run"):
                base["run"] = item["run"]
        elif not base.get("run") and item.get("run"):
            base["run"] = item["run"]
        base["related_ids"] = sorted(set(base.get("related_ids", []) + item.get("related_ids", [])))
    return [merged[key] for key in sorted(merged)]


def update_wave_run_status(project_dir, bw_id, status):
    path = find_wave_run_file(project_dir, bw_id)
    if not path:
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return ""

    def replace_status(match):
        block = match.group(1)
        if not re.search(rf"^\s*bw_id:\s*{re.escape(bw_id)}\s*$", block, re.MULTILINE):
            return match.group(0)
        if re.search(r"^\s*status:\s*.+$", block, re.MULTILINE):
            block = re.sub(r"^(\s*status:\s*).+$", rf"\1{status}", block, count=1, flags=re.MULTILINE)
        else:
            block = block.rstrip() + f"\nstatus: {status}\n"
        return f"```yaml\n{block}```"

    updated = re.sub(r"```yaml\s*(.*?)```", replace_status, content, count=1, flags=re.DOTALL | re.IGNORECASE)
    if updated != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated)
    return os.path.relpath(path, project_dir)


def compute_implementation_progress(project_dir=".", session=None):
    try:
        _group_reqs, detail_reqs, _defined_acs, _ac_delegates = parse_requirements(project_dir)
    except Exception:
        detail_reqs = set()

    try:
        traceability = parse_traceability(project_dir)
    except Exception:
        traceability = {}

    completed_ids = {
        req_id
        for req_id, info in traceability.items()
        if re.fullmatch(r"REQ-\d{3}-\d{2}", req_id)
        and info.get("status") in ("구현완료", "완료", "Implemented", "Verified", "Done")
    }

    if session:
        session_impl = session.get("implementation", {})
        reqs = session_impl.get("requirements", {}) if isinstance(session_impl, dict) else {}
        completed_ids.update(reqs.get("completed_ids", []))

    wave_records = merge_session_wave_records(session or {}, collect_build_wave_records(project_dir))
    current = ""
    for item in wave_records:
        if item.get("status") in WAVE_ACTIVE_STATUSES:
            current = item["id"]
            break
    if session:
        session_current = (
            session.get("implementation", {})
            .get("waves", {})
            .get("current", "")
        )
        if session_current:
            current = session_current

    return {
        "requirements": {
            "total": len(detail_reqs),
            "implemented": len(completed_ids),
            "pending": max(len(detail_reqs) - len(completed_ids), 0),
            "completed_ids": sorted(completed_ids),
        },
        "waves": {
            "total": len(wave_records),
            "completed": sum(1 for item in wave_records if item.get("status") in WAVE_DONE_STATUSES),
            "current": current,
            "items": wave_records,
        },
    }


def parse_requirements(project_dir="."):
    """REQUIREMENTS.md에서 REQ-ID 및 AC 정보를 파싱합니다."""
    path = find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "01-requirements"),
        r"requirements.*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "01-requirements", "REQUIREMENTS.md"),
    ])
    if not path:
        return set(), set(), set(), {}

    with open(path, encoding="utf-8") as f:
        content = f.read()

    group_reqs = set()
    detail_reqs = set()

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cols = [c.strip() for c in stripped.strip("|").split("|")]
            if not cols or set(cols[0]) <= {"-"}:
                continue
            if re.fullmatch(r"REQ-\d{3}", cols[0]):
                name = cols[1] if len(cols) > 1 else ""
                description = cols[2] if len(cols) > 2 else ""
                if name or description:
                    group_reqs.add(cols[0])
            elif re.fullmatch(r"REQ-\d{3}-\d{2}", cols[0]):
                name = cols[1] if len(cols) > 1 else ""
                description = cols[2] if len(cols) > 2 else ""
                if name or description:
                    detail_reqs.add(cols[0])
            continue

        detail_match = re.match(r"^#{3,6}\s+(REQ-\d{3}-\d{2})\s+(.+)$", stripped)
        if detail_match and detail_match.group(2).strip():
            detail_reqs.add(detail_match.group(1))

    defined_acs = set(re.findall(r'###\s+AC-(\d{3}-\d{2})', content))
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cols = [c.strip() for c in stripped.strip("|").split("|")]
        if not cols or set(cols[0]) <= {"-"}:
            continue
        ac_match = re.fullmatch(r"AC-(\d{3}-\d{2})", cols[0])
        if ac_match:
            defined_acs.add(ac_match.group(1))

    # AC 위임 관계 파싱: REQ-XXX-XX 행에 자기 AC는 없지만 다른 AC-ID가 참조되면 위임
    ac_delegates = {}
    for line in content.splitlines():
        m_req = re.search(r'\bREQ-(\d{3}-\d{2})\b', line)
        if m_req:
            req_id = m_req.group(1)
            if req_id not in defined_acs:
                refs = re.findall(r'\bAC-(\d{3}-\d{2})\b', line)
                for ref in refs:
                    if ref != req_id:
                        ac_delegates[req_id] = ref
                        break

    return group_reqs, detail_reqs, defined_acs, ac_delegates


def parse_traceability(project_dir="."):
    """TRACEABILITY.md를 파싱하여 REQ-ID별 추적 정보를 반환합니다.
    Returns: dict[req_id] = {"design": str, "tst_ids": list, "review": str, "status": str}
    TRACEABILITY.md가 없으면 빈 dict 반환 (하위 호환성 유지).
    """
    path = find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-traceability"),
        r"traceability.*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "TRACEABILITY.md"),
    ])
    if not path:
        return {}
    result = {}
    headers = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip().startswith('|'):
                continue
            cols = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cols) < 5:
                continue
            if "REQ-ID" in cols:
                headers = cols
                continue
            if all(re.fullmatch(r"[-: ]+", c or "") for c in cols):
                continue

            header_idx = {name: idx for idx, name in enumerate(headers)}

            def cell(name, default=""):
                idx = header_idx.get(name)
                if idx is None or idx >= len(cols):
                    return default
                return cols[idx]

            req_id = cell("REQ-ID", cols[0])
            if not re.match(r'REQ-\d{3}(?:-\d{2})?$', req_id):
                continue
            ac_value = cell("AC-ID", cols[1] if len(cols) > 1 else "")
            is_ex_matrix_row = bool(headers) and re.match(r'AC-\d{3}-\d{2}$', ac_value)
            if is_ex_matrix_row:
                design = ", ".join(
                    c
                    for c in [
                        cell("FUNC-ID"),
                        cell("SCR-ID"),
                        cell("PGM-ID"),
                        cell("DB-ID"),
                        cell("IF-ID"),
                        cell("API-ID"),
                        cell("SEC-ID"),
                    ]
                    if c and c not in ("-", "미정", "해당없음")
                )
                test_columns = {
                    "UT-ID": cell("UT-ID"),
                    "IT-ID": cell("IT-ID"),
                    "PT-ID": cell("PT-ID"),
                }
                if "UI-ID" in header_idx:
                    test_columns["UI-ID"] = cell("UI-ID")
                tst_raw = ", ".join(c for c in test_columns.values() if c and c not in ("-", "미정", "해당없음"))
                review = cell("증적") or cell("검토")
                if review in ("-", "미정", "해당없음"):
                    review = ""
                status = cell("상태")
            elif req_id in result:
                continue
            else:
                design  = cols[1] if len(cols) > 1 and cols[1] != '-' else ''
                tst_raw = cols[2] if len(cols) > 2 and cols[2] != '-' else ''
                review  = cols[3] if len(cols) > 3 and cols[3] != '-' else ''
                status  = cols[4] if len(cols) > 4 else ''
                test_columns = {"TST-ID": tst_raw}
            tst_ids = [t.strip() for t in tst_raw.split(',') if t.strip() and t.strip() != '-']
            result[req_id] = {
                "design": design,
                "tst_ids": tst_ids,
                "review": review,
                "status": status,
                "test_columns": test_columns,
            }
    return result


def parse_test_plan(project_dir="."):
    """Test-Plan.md에서 TST-ID → REQ-ID 매핑을 파싱합니다."""
    path = find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "03-test"),
        r"(test.*case|test.*plan|test.*cases).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "03-test-plan", "Test-Plan.md"),
    ])
    if not path:
        return set()

    with open(path, encoding="utf-8") as f:
        content = f.read()

    return set(re.findall(r'\bREQ-\d{3}-\d{2}\b', content))


def parse_test_plan_status(project_dir="."):
    """Test-Plan.md에서 TST-ID별 실행 상태를 파싱합니다.
    테스트 케이스 목록 형식의 마크다운 테이블 행만 파싱합니다.
    보안 기준표처럼 테스트 ID를 참조만 하는 표는 집계하지 않습니다.
    Returns: list of (tst_id, status) tuples
    """
    path = find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "03-test"),
        r"(test.*case|test.*plan|test.*cases).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "03-test-plan", "Test-Plan.md"),
    ])
    if not path:
        return []

    with open(path, encoding="utf-8") as f:
        content = f.read()

    results = {}
    for line in content.splitlines():
        # 마크다운 테이블 행만 대상 (|로 시작)
        if not line.strip().startswith('|'):
            continue
        if re.search(r'\b(?:REQ|NREQ|AC|SEC|PGM|SCR)-\s*(?:/|\||$)', line):
            continue
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cols) < 9:
            continue
        # 구체적인 TST-ID만 매칭 (TST-NNN-NN 또는 TST-SEC-NN 형식)
        # TST-ID, TST-NNN-NN 같은 템플릿/플레이스홀더는 제외
        tst_match = re.search(r'\|\s*((?:TST|UT|IT|PT|UI)-(?:\d{3}(?:-\d{2})?|SEC-\d{2}))\s*\|', line)
        if not tst_match:
            continue
        tst_id = tst_match.group(1)

        # 상태 판별: Pass/Fail/Skip/미실행
        status_cell = cols[-1].lower()
        if re.search(r'\bpass\b', status_cell):
            status = 'pass'
        elif re.search(r'\bfail\b', status_cell):
            status = 'fail'
        elif re.search(r'\bskip\b', status_cell):
            status = 'skip'
        else:
            status = 'not_executed'

        results[tst_id] = status

    return list(results.items())


def find_development_standard_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-design", "development-standard"),
        r"development.*standard.*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "02-design", "development-standard.md"),
        os.path.join("docs", "02-design", "Development-Standard.md"),
    ])


def find_project_glossary_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-design", "data"),
        r"(project.*glossary|glossary|단어.*사전|용어.*사전).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "02-design", "project-glossary.md"),
        os.path.join("docs", "02-design", "Project-Glossary.md"),
        os.path.join("docs", "02-design", "glossary.md"),
    ])


def find_program_spec_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-design", "program"),
        r"(program.*spec|프로그램.*명세).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "02-design", "program-spec.md"),
        os.path.join("docs", "02-design", "Program-Spec.md"),
    ])


def find_api_spec_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-design", "api"),
        r"(api.*spec|api.*정의).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "02-design", "api-spec.md"),
        os.path.join("docs", "02-design", "API-Spec.md"),
    ])


def find_security_guide_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-design", "security"),
        r"(security.*guide|보안.*가이드).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "02-design", "security-guide.md"),
        os.path.join("docs", "02-design", "Security-Guide.md"),
    ])


def find_screen_spec_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-design", "screen"),
        r"(screen.*spec|화면.*설계).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "02-design", "screen-spec.md"),
        os.path.join("docs", "02-design", "Screen-Spec.md"),
    ])


def find_architecture_spec_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "02-design", "architecture"),
        r"(sw.*architecture|architecture|아키텍처).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "02-design", "architecture.md"),
        os.path.join("docs", "02-design", "Architecture.md"),
        os.path.join("docs", "02-design", "SW-Architecture.md"),
    ])


def find_risk_assumption_file(project_dir="."):
    return find_artifact_file(
        project_dir,
        os.path.join("docs", "artifacts", "00-discovery"),
        r"(risk.*assumption|위험.*가정).*\.md$",
    ) or find_first_existing(project_dir, [
        os.path.join("docs", "00-discovery", "risk-and-assumption.md"),
        os.path.join("docs", "00-discovery", "Risk-And-Assumption.md"),
    ])


def split_trace_values(value):
    return [
        item.strip().strip("`")
        for item in re.split(r",|\n", value or "")
        if item.strip() and item.strip() not in ("-", "미정", "해당없음")
    ]


def is_probable_source_path(value):
    normalized = value.replace("\\", "/")
    source_exts = (
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs",
        ".cs", ".php", ".rb", ".html", ".css", ".scss", ".vue", ".svelte",
    )
    if not normalized.lower().endswith(source_exts):
        return False
    return "/" in normalized or normalized.startswith(("app", "src", "tests", "test"))


def is_probable_text_file(path):
    text_exts = (
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".go", ".rs",
        ".cs", ".php", ".rb", ".html", ".css", ".scss", ".vue", ".svelte",
        ".md", ".json", ".yml", ".yaml", ".txt",
    )
    return path.lower().endswith(text_exts)


def validate_development_standard(project_dir="."):
    issues = []
    path = find_development_standard_file(project_dir)
    if not path:
        return [], ["개발표준정의서 없음"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    if re.search(r"(?m)^status:\s*Draft\s*$", content):
        issues.append(f"{rel_path} 상태가 Draft")
    if re.search(r"\{PROJECT_NAME\}|\{AUTHOR\}|\{YYYY-MM-DD\}|TBD|확정필요", content):
        issues.append(f"{rel_path}에 템플릿 플레이스홀더가 남아 있음")

    required_terms = [
        ("언어/런타임", r"Language|Runtime|적용 언어|적용 프레임워크|Java|TypeScript|Python|Node|Vue|React|Spring Boot"),
        ("패키지 구조", r"패키지 구조|app/|src/"),
        ("기술 선택 근거", r"선정 사유|선택 근거|선정 근거"),
        ("기술스택 베이스라인 조정 근거", r"TECH_STACK_BASELINES|참조 베이스라인|프로젝트 조정사항"),
        ("메시지 관리", r"메시지|message"),
        ("주석/코딩 컨벤션", r"주석|JavaDoc|Javadoc|코드 컨벤션|네이밍"),
        ("로깅 기준", r"SLF4J|Logback|Log4j2|Logger|MDC|requestId|correlationId|System\.out|printStackTrace|로그 레벨"),
        ("DB Pool 기준", r"HikariCP|DB Pool|connection pool|커넥션 풀"),
        ("Lombok 기준", r"Lombok|@Getter|@RequiredArgsConstructor|@Data|@Setter"),
        ("테스트 명령", r"python -m unittest|pytest|npm test|pnpm test|mvn test|gradle test|gradlew test|go test|cargo test|dotnet test"),
        ("검증 명령 실행 기준", r"cwd|실행 위치|성공 기준|exit code|종료 코드|Not Run|Skipped|증적|로그/증적"),
        ("보안 구현 기준", r"SECURITY_BASELINE|KISA|SR2-|SR1-|보안 구현|보안 영역|Spring Security|SEC-\d{3}|JWT"),
    ]
    for label, pattern in required_terms:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}에 {label} 기준 없음")

    critical_blank_rows = [
        ("적용 언어", r"\|\s*적용 언어\s*\|\s*\|"),
        ("적용 프레임워크", r"\|\s*적용 프레임워크\s*\|\s*\|"),
        ("Base Package", r"\|\s*Base Package\s*\|\s*(?:예:\s*)?\|"),
        ("패키지 구조 기준", r"\|\s*패키지 구조 기준\s*\|\s*(?:예:\s*)?\|"),
        ("Lombok 사용 여부", r"\|\s*사용 여부\s*\|\s*\|"),
        ("Lombok 허용 annotation", r"\|\s*허용 annotation\s*\|\s*(?:예:\s*)?\|"),
        ("로깅 API", r"\|\s*로깅 API\s*\|\s*(?:예:\s*)?\|"),
        ("로깅 구현체", r"\|\s*(?:로깅\s*)?구현체\s*\|\s*(?:예:\s*)?\|"),
        ("로그 레벨 기준", r"\|\s*로그 레벨\s*(?:기준)?\s*\|\s*(?:예:\s*)?\|"),
    ]
    for label, pattern in critical_blank_rows:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}에 {label} 값이 비어 있음")

    if re.search(r"Spring Boot|Spring Security|JPA|gradlew", content, re.IGNORECASE):
        spring_required_terms = [
            ("Spring Boot base package", r"Base Package.+`?[a-z]+(?:\.[a-z][a-z0-9_]*)+`?|base package"),
            ("feature 우선 패키지 구조", r"feature 우선|auth/|user/|\{featureName\}|domain/\{domainName\}|DDD"),
            ("domain 래퍼 선택 사유", r"domain/\{domainName\}|domain 래퍼|DDD 구조 선택 사유"),
            ("JavaDoc 적용 대상", r"JavaDoc|Javadoc|public 업무 메서드|Controller, Service, Security Config"),
            ("logger 선언 기준", r"private static final Logger|LoggerFactory|getLogger|@Slf4j|logger 선언"),
            ("System.out 금지", r"System\.out|printStackTrace"),
        ]
        for label, pattern in spring_required_terms:
            if not re.search(pattern, content, re.IGNORECASE):
                issues.append(f"{rel_path}에 {label} 기준 없음")

    return [rel_path], issues


def validate_project_glossary(project_dir="."):
    issues = []
    path = find_project_glossary_file(project_dir)
    if not path:
        return [], ["프로젝트 단어사전 없음"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    if re.search(r"(?m)^status:\s*Draft\s*$", content):
        issues.append(f"{rel_path} 상태가 Draft")
    if re.search(r"\{PROJECT_NAME\}|\{AUTHOR\}|\{YYYY-MM-DD\}|TBD|확정필요", content):
        issues.append(f"{rel_path}에 템플릿 플레이스홀더가 남아 있음")

    required_terms = [
        ("참조 표준", r"PUBLIC-DATA-STD|공공데이터 공통표준|reference-standards"),
        ("용어 ID", r"TERM-\d{3}"),
        ("단어 ID", r"WORD-\d{3}"),
        ("도메인 ID", r"DOMAIN-\d{3}"),
        ("표준 준용 상태", r"표준 준용 상태|표준 검토|표준 후보|프로젝트 신규|프로젝트 정의"),
        ("등록 사유", r"등록 사유|등록사유|사유"),
        ("화면/API/DB 항목 매핑", r"화면/API/DB|화면 항목명|API 필드명|DB 컬럼명"),
        ("보안/개인정보 분류", r"보안 분류|개인정보|인증정보|민감정보|로그 출력"),
    ]
    for label, pattern in required_terms:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}에 {label} 기준 없음")

    return [rel_path], issues


def validate_program_spec(project_dir="."):
    issues = []
    path = find_program_spec_file(project_dir)
    if not path:
        return [], ["프로그램명세서 없음"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    if re.search(r"(?m)^status:\s*Draft\s*$", content):
        issues.append(f"{rel_path} 상태가 Draft")
    if re.search(r"\{PROJECT_NAME\}|\{AUTHOR\}|\{YYYY-MM-DD\}|TBD|확정필요", content):
        issues.append(f"{rel_path}에 템플릿 플레이스홀더가 남아 있음")

    required_terms = [
        ("PGM-ID", r"PGM-\d{3}"),
        ("인터페이스", r"호출 방식|엔드포인트|함수명|API 정의서"),
        ("입력/출력", r"입력 파라미터|출력 항목|TERM-"),
        ("처리 흐름", r"처리 흐름|처리 내용"),
        ("예외/오류", r"ERR-\d{3}|오류 ID|예외"),
        ("데이터 접근", r"DB-\d{3}|데이터 접근|트랜잭션"),
        ("보안 설계", r"SEC-\d{3}|보안 설계|KISA|SR-"),
        ("단위테스트 연결", r"UT-\d{3}|단위테스트|AC-|NREQ-"),
        ("상세 SW 설계 다이어그램 판단", r"상세 SW 설계 다이어그램|복잡도|상태 전이|생략 사유"),
    ]
    for label, pattern in required_terms:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}에 {label} 기준 없음")

    diagram_markers = [
        r"```mermaid\s*\n\s*classDiagram",
        r"```mermaid\s*\n\s*stateDiagram",
        r"```mermaid\s*\n\s*sequenceDiagram",
        r"```mermaid\s*\n\s*flowchart",
        r"```mermaid\s*\n\s*graph",
    ]
    has_detail_diagram = any(re.search(pattern, content, re.IGNORECASE) for pattern in diagram_markers)
    has_skip_reason = bool(re.search(r"생략 사유\s*\|[^\n]*\S|불필요\s*\|[^\n]*\S", content))
    has_need_marker = bool(re.search(r"\|\s*PGM-\d{3}\s*\|[^\n]*\|\s*필요\s*\|", content))
    if has_need_marker and not has_detail_diagram:
        issues.append(f"{rel_path}에 상세 SW 설계 다이어그램 필요 표시가 있으나 Mermaid 다이어그램 없음")
    if not has_detail_diagram and not has_skip_reason:
        issues.append(f"{rel_path}에 상세 SW 설계 다이어그램 또는 생략 사유 없음")

    return [rel_path], issues


def program_spec_requires_api_spec(project_dir="."):
    path = find_program_spec_file(project_dir)
    if not path:
        return False, None

    with open(path, encoding="utf-8") as f:
        content = f.read()

    effective_lines = [
        line for line in content.splitlines()
        if not re.search(r"API\s*/\s*Batch\s*/\s*Module|REST\s*/\s*GraphQL|GET\s*/\s*POST|API가 없으면|API 관련 칸", line, re.IGNORECASE)
    ]
    effective_content = "\n".join(effective_lines)

    api_patterns = [
        r"\|\s*PGM-\d{3}\s*\|[^|\n]*\|\s*(?:API|REST|GraphQL)\b",
        r"\|\s*호출 방식\s*\|\s*(?:REST|GraphQL)\s*\|",
        r"\|\s*Method\s*\|\s*(?:GET|POST|PUT|PATCH|DELETE)\s*\|",
        r"`/api/[^`]+`",
        r"\|\s*[^|\n]*/api/[^|\n]*\|",
    ]
    return any(re.search(pattern, effective_content, re.IGNORECASE) for pattern in api_patterns), path


def validate_api_spec(project_dir="."):
    issues = []
    required, program_path = program_spec_requires_api_spec(project_dir)
    if not required:
        return [], issues

    path = find_api_spec_file(project_dir)
    program_rel = os.path.relpath(program_path, project_dir) if program_path else "프로그램명세서"
    if not path:
        return [], [f"{program_rel}에 API가 정의되어 있으나 API 정의서 없음"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    if re.search(r"(?m)^status:\s*Draft\s*$", content):
        issues.append(f"{rel_path} 상태가 Draft")
    if re.search(r"\{PROJECT_NAME\}|\{AUTHOR\}|\{YYYY-MM-DD\}|TBD|확정필요", content):
        issues.append(f"{rel_path}에 템플릿 플레이스홀더가 남아 있음")

    required_terms = [
        ("API-ID", r"API-\d{3}"),
        ("Method/Path", r"\b(GET|POST|PUT|PATCH|DELETE)\b.*(/|Path)|Path.*\b(GET|POST|PUT|PATCH|DELETE)\b"),
        ("Request", r"Request|요청|Body|Query|Path|Header"),
        ("Response", r"Response|응답|상태코드|HTTP Status"),
        ("Error", r"Error|오류|error\.code|ERR-"),
        ("인증/권한", r"인증|권한|401|403|SEC-"),
        ("예시", r"요청 예시|응답 예시|```json"),
        ("테스트 연결", r"UT-|IT-|테스트 ID|검증"),
    ]
    for label, pattern in required_terms:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}에 {label} 기준 없음")

    return [rel_path], issues


def validate_architecture_spec(project_dir=".", level="baseline"):
    issues = []
    path = find_architecture_spec_file(project_dir)
    if not path:
        return [], ["SW 아키텍처 정의서 없음"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    normalized_level = (level or "baseline").lower()
    if normalized_level not in {"draft", "baseline"}:
        normalized_level = "baseline"

    if normalized_level == "baseline" and re.search(r"(?m)^status:\s*Draft\s*$", content):
        issues.append(f"{rel_path} 상태가 Draft")
    if re.search(r"\{PROJECT_NAME\}|\{AUTHOR\}|\{YYYY-MM-DD\}|TBD|확정필요", content):
        issues.append(f"{rel_path}에 템플릿 플레이스홀더가 남아 있음")

    draft_required_terms = [
        ("아키텍처 성숙도", r"성숙도|Draft|Baseline Candidate|Baseline|Pending"),
        ("아키텍처 개요", r"아키텍처 개요|시스템 목적|주요 사용자|아키텍처 범위"),
        ("논리 아키텍처", r"논리 아키텍처|프론트엔드|백엔드|인증/권한|배치/비동기"),
        ("C1/C2 구조", r"C1|C2|시스템 컨텍스트|컨테이너|CNT-\d{3}"),
        ("아키텍처 결정 후보", r"ADR-\d{3}|아키텍처 결정|ADR 후보|Architecture Decision"),
    ]
    baseline_required_terms = [
        ("물리 아키텍처", r"물리 아키텍처|PHY-\d{3}|서버|네트워크|배포 단위|런타임"),
        ("모듈/컴포넌트 구조", r"모듈/컴포넌트 구조|C3|컴포넌트|CMP-\d{3}"),
        ("데이터 흐름", r"데이터 흐름|FLOW-\d{3}|sequenceDiagram|오류 처리 흐름"),
        ("보안 아키텍처", r"SEC-\d{3}|보안 아키텍처|인증|인가|세션|암호화|KISA|OWASP|CWE"),
        ("품질속성", r"NREQ-\d{3}|QA-\d{3}|품질속성"),
        ("기술 스택 및 선택 근거", r"기술 스택|선택 근거|언어|프레임워크|DB|배포 방식"),
        ("아키텍처 결정", r"ADR-\d{3}|아키텍처 결정|Architecture Decision"),
        ("추적성 및 상세 설계 연결", r"추적성|상세 설계 연결|프로그램명세서|API정의서|DB명세서|화면설계서|추적표"),
    ]
    required_terms = draft_required_terms
    if normalized_level == "baseline":
        required_terms += baseline_required_terms
    for label, pattern in required_terms:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}에 {label} 기준 없음")

    mermaid_blocks = re.findall(r"```mermaid\s*\n(.*?)```", content, re.IGNORECASE | re.DOTALL)
    flow_blocks = [
        block for block in mermaid_blocks
        if re.search(r"^\s*(?:flowchart|graph)\s+", block, re.IGNORECASE | re.MULTILINE)
    ]
    c1_c2_blocks = flow_blocks[:2]
    missing_boundary_count = sum(
        1 for block in c1_c2_blocks
        if not re.search(r"\bsubgraph\b", block, re.IGNORECASE)
    )
    if c1_c2_blocks and missing_boundary_count:
        issues.append(f"{rel_path}의 C1/C2 아키텍처 다이어그램에 subgraph 경계 표현 없음")

    file_name_node_count = 0
    for block in flow_blocks:
        file_name_node_count += len(re.findall(r"\b[\w.-]+\.(?:py|ts|tsx|js|jsx|java|kt|go|cs|php|rb)\b", block, re.IGNORECASE))
    if file_name_node_count >= 3:
        issues.append(
            f"{rel_path}의 아키텍처 다이어그램이 파일명 나열 중심입니다 "
            "(C1/C2는 CNT/CMP/FLOW와 실행 경계 중심으로 작성)"
        )

    if normalized_level == "baseline":
        if len(flow_blocks) < 2:
            issues.append(f"{rel_path}에 C1/C2 Mermaid 경계 다이어그램이 부족함")

        required_link_targets = [
            "DOC-CORE-G2-001",
            "DOC-CORE-G2-002",
            "DOC-API-G2-001",
            "DOC-DATA-G2-002",
            "DOC-CORE-G2-003",
            "DOC-SEC-G2-001",
            "DOC-DEV-G2-001",
            "DOC-QA-G3-001",
            "DOC-CORE-G4-001",
        ]
        missing_links = [target for target in required_link_targets if target not in content]
        if missing_links:
            issues.append(f"{rel_path}의 상세 설계/추적 연결 문서 누락: {', '.join(missing_links)}")

    return [rel_path], issues


def validate_security_guide(project_dir="."):
    issues = []
    path = find_security_guide_file(project_dir)
    if not path:
        return [], ["보안가이드 없음"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    if re.search(r"(?m)^status:\s*Draft\s*$", content):
        issues.append(f"{rel_path} 상태가 Draft")
    if re.search(r"\{PROJECT_NAME\}|\{AUTHOR\}|\{YYYY-MM-DD\}|TBD|확정필요", content):
        issues.append(f"{rel_path}에 템플릿 플레이스홀더가 남아 있음")

    required_terms = [
        ("SEC-ID", r"SEC-\d{3}|SEC-[A-Z]+"),
        ("참조 표준", r"KISA|SR\d+-\d+|OWASP|CWE"),
        ("구현 규격", r"구현 규격|값 또는 규칙|적용 위치"),
        ("화면/프로그램/DB 반영 기준", r"화면설계서|프로그램명세서|DB명세서|Screen Spec|Program Spec|Database Spec"),
        ("검증 ID", r"UT-|IT-|PT-|UI-|검증 ID|테스트 ID"),
    ]
    for label, pattern in required_terms:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"{rel_path}에 {label} 기준 없음")

    return [rel_path], issues


def validate_screen_spec(project_dir="."):
    issues = []
    path = find_screen_spec_file(project_dir)
    if not path:
        return [], ["화면설계서 없음"]

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    if re.search(r"(?m)^status:\s*Draft\s*$", content):
        issues.append(f"{rel_path} 상태가 Draft")
    if re.search(r"\{PROJECT_NAME\}|\{AUTHOR\}|\{YYYY-MM-DD\}|TBD|확정필요", content):
        issues.append(f"{rel_path}에 템플릿 플레이스홀더가 남아 있음")

    has_screen = bool(re.search(r"SCR-\d{3}", content))
    has_uiref = bool(re.search(r"UIREF-\d{3}", content))
    has_ui_test = bool(re.search(r"UI-\d{3}", content))
    has_viewport = bool(re.search(r"Desktop\s+\d+x\d+|Mobile\s+\d+x\d+|viewport", content, re.IGNORECASE))
    has_visual_evidence = bool(re.search(
        r"!\[[^\]]*\]\([^)]+\)|docs/artifacts/02-design/screen/(?:images|ui-baseline)/|figma|imagegen|html\s+mockup|화면 퍼블리싱|mermaid|```(?:text|mermaid|html)",
        content,
        re.IGNORECASE,
    ))
    has_ui_baseline_or_external_design = bool(re.search(
        r"docs/artifacts/02-design/screen/(?:images|ui-baseline)/|figma|imagegen|html\s+mockup|화면 퍼블리싱|외부 시안|기존 시스템 캡처|UIREF-\d{3}",
        content,
        re.IGNORECASE,
    ))
    has_ui_contract = bool(re.search(
        r"UI Implementation Contract|구현 계약|필수 유지|변경 허용|변경 금지|허용 차이|비교 방식",
        content,
        re.IGNORECASE,
    ))

    if has_screen and not has_uiref:
        issues.append(f"{rel_path}에 UIREF 기준 시안/와이어프레임 ID 없음")
    if has_screen and not has_ui_test:
        issues.append(f"{rel_path}에 UI 테스트 ID 없음")
    if has_screen and not has_viewport:
        issues.append(f"{rel_path}에 기준 viewport 없음")
    if has_screen and not has_visual_evidence:
        issues.append(f"{rel_path}에 실제 화면 구조 증적 없음(Text Wireframe fenced block, Mermaid, 화면 퍼블리싱 산출물, 이미지/Figma 등)")
    if has_screen and has_ui_baseline_or_external_design and not has_ui_contract:
        issues.append(f"{rel_path}에 UIREF/ui-baseline을 구현 계약으로 전환한 UI Implementation Contract 없음")

    text_wireframe_rows = [
        line for line in content.splitlines()
        if "Text Wireframe" in line and re.search(r"UIREF-\d{3}", line)
    ]
    if text_wireframe_rows and not re.search(r"```(?:text|mermaid|html)", content, re.IGNORECASE):
        issues.append(f"{rel_path}에 Text Wireframe 표기는 있으나 실제 와이어프레임 코드 블록 없음")

    if re.search(r"UI 기준선 판정\s*\|\s*Minimal", content) and not has_visual_evidence:
        issues.append(f"{rel_path} UI 기준선이 Minimal인데 보강 가능한 화면 구조 증적 없음")

    return [rel_path], issues


def is_resolved_discovery_status(status):
    normalized = (status or "").strip().lower()
    return normalized in {
        "closed", "resolved", "confirmed", "accepted", "done", "n/a", "na",
        "완료", "확정", "해결", "수용", "해당없음",
    }


def detect_due_gate(text):
    value = text or ""
    if re.search(r"Gate\s*1|게이트\s*1|G1", value, re.IGNORECASE):
        return "gate1"
    if re.search(r"Gate\s*2|게이트\s*2|G2", value, re.IGNORECASE):
        return "gate2"
    if re.search(r"Gate\s*3|게이트\s*3|G3", value, re.IGNORECASE):
        return "gate3"
    if re.search(r"구현|impl|Gate\s*4|게이트\s*4|G4", value, re.IGNORECASE):
        return "impl"
    return None


def is_empty_table_value(value):
    normalized = (value or "").strip()
    return normalized in {"", "-", "미정", "확인필요", "TBD", "TODO"}


def find_header_index(headers, candidates):
    for idx, header in enumerate(headers):
        normalized = header.replace(" ", "").lower()
        for candidate in candidates:
            if candidate.replace(" ", "").lower() in normalized:
                return idx
    return None


def validate_discovery_open_items(project_dir=".", current_gate="phase0"):
    issues = []
    path = find_risk_assumption_file(project_dir)
    if not path:
        return issues

    with open(path, encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(path, project_dir)
    current_idx = GATE_ORDER.index(current_gate) if current_gate in GATE_ORDER else 0
    registry_counts = {"RISK": 0, "ASM": 0, "Q": 0}
    registry_labels = {
        "RISK": "위험 목록",
        "ASM": "가정 목록",
        "Q": "미결 질문",
    }
    registry_content_headers = {
        "RISK": ["위험 내용"],
        "ASM": ["가정 내용"],
        "Q": ["질문"],
    }

    section = ""
    headers = []
    for line in content.splitlines():
        section_match = re.match(r"^#{2,}\s*(.+?)\s*$", line.strip())
        if section_match:
            section = section_match.group(1)
            headers = []
            continue

        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cols = [c.strip() for c in stripped.strip("|").split("|")]
        if not cols:
            continue
        if cols[0] in {"---", ":---", "---:"} or all(re.match(r"^:?-{3,}:?$", col) for col in cols):
            continue
        if cols[0] in {"RISK-ID", "ASM-ID", "Q-ID"}:
            headers = cols
            continue

        item_id = cols[0]
        if not re.match(r"^(RISK|ASM|Q)-\d{3}$", item_id):
            continue

        item_type = item_id.split("-", 1)[0]
        content_idx = find_header_index(headers, registry_content_headers[item_type]) if headers else None
        content_value = cols[content_idx] if content_idx is not None and content_idx < len(cols) else ""
        status_idx = find_header_index(headers, ["상태"]) if headers else None
        status = cols[status_idx] if status_idx is not None and status_idx < len(cols) else cols[-1]

        if is_empty_table_value(content_value):
            if current_idx >= GATE_ORDER.index("gate1"):
                issues.append(
                    f"  X {rel_path}의 {item_id}는 ID만 있고 내용이 비어 있습니다 "
                    "(삭제하거나 실제 내용/해당없음 사유를 작성)"
                )
                continue
        else:
            registry_counts[item_type] += 1

        due_idx = None
        if item_id.startswith("Q-"):
            due_idx = find_header_index(headers, ["기한"]) if headers else None
        elif item_id.startswith("ASM-"):
            due_idx = find_header_index(headers, ["확인 방법", "확인방법"]) if headers else None
        elif item_id.startswith("RISK-"):
            due_idx = find_header_index(headers, ["대응 방향", "대응방향"]) if headers else None
        if due_idx is None:
            due_idx = 4 if len(cols) > 4 else None
        due_source = cols[due_idx] if due_idx is not None and due_idx < len(cols) else ""

        due_gate = detect_due_gate(due_source)
        due_idx_order = GATE_ORDER.index(due_gate) if due_gate in GATE_ORDER else None

        if is_resolved_discovery_status(status):
            if due_idx_order is None or current_idx < due_idx_order:
                continue
            result_idx = find_header_index(headers, [
                "결정/처리 결과", "확인/처리 결과", "답변/결정 내용", "처리 결과", "결정 내용",
            ]) if headers else None
            basis_idx = find_header_index(headers, ["결정 근거", "연결 ID", "연결ID"]) if headers else None
            decided_at_idx = find_header_index(headers, ["결정일시", "결정 일시", "변경일시", "변경 일시"]) if headers else None
            decider_idx = find_header_index(headers, ["결정자", "확인자"]) if headers else None
            required_resolution_fields = [
                ("결정/처리 결과", result_idx),
                ("결정 근거/연결 ID", basis_idx),
                ("결정일시", decided_at_idx),
                ("결정자", decider_idx),
            ]
            for label, idx in required_resolution_fields:
                if idx is None or idx >= len(cols) or is_empty_table_value(cols[idx]):
                    issues.append(f"  X {rel_path}의 {item_id}는 상태가 {status}이지만 {label}가 비어 있습니다")
            continue

        if due_idx_order is not None and current_idx >= due_idx_order:
            issues.append(
                f"  X {rel_path}의 {item_id}가 {due_source}까지 정리되어야 하지만 상태가 {status or '미정'}입니다"
            )

    if current_idx >= GATE_ORDER.index("gate1"):
        for item_type, count in registry_counts.items():
            if count == 0:
                issues.append(
                    f"  X {rel_path}의 {registry_labels[item_type]}에 유효한 {item_type} 행이 없습니다 "
                    f"(최소 1건 작성하거나 {item_type}-001에 해당없음 사유를 명시)"
                )

    return issues


def has_completed_run(project_dir=".", gate=None, skill=None, persona=None):
    runs_dir = os.path.join(project_dir, "docs", "runs")
    if not os.path.isdir(runs_dir):
        return False

    for root, _, files in os.walk(runs_dir):
        for filename in files:
            if not filename.lower().endswith(".md"):
                continue
            path = os.path.join(root, filename)
            with open(path, encoding="utf-8") as f:
                content = f.read()

            if gate and not re.search(rf'(?m)^gate:\s*{re.escape(gate)}\s*$', content):
                continue
            if skill and not re.search(rf'(?m)^skill:\s*{re.escape(skill)}\s*$', content):
                continue
            if persona and not re.search(rf'(?m)^persona:\s*{re.escape(persona)}\s*$', content):
                continue
            if re.search(r'(?m)^status:\s*(Completed|Verified)\s*$', content):
                run_issues, _warnings = check_run_file(path)
                if run_issues:
                    continue
                return True
    return False


def collect_run_gate_records(project_dir="."):
    runs_dir = os.path.join(project_dir, "docs", "runs")
    records = []
    if not os.path.isdir(runs_dir):
        return records

    for root, _, files in os.walk(runs_dir):
        for filename in files:
            if not filename.lower().endswith(".md"):
                continue
            if filename == ".gitkeep":
                continue
            path = os.path.join(root, filename)
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue
            gate_match = re.search(r'(?m)^gate:\s*([A-Za-z0-9_-]+)\s*$', content)
            status_match = re.search(r'(?m)^status:\s*(.+?)\s*$', content)
            records.append({
                "path": os.path.relpath(path, project_dir),
                "gate": gate_match.group(1).lower() if gate_match else "",
                "status": status_match.group(1).strip() if status_match else "",
            })
    return records


def has_open_run_for_gate(project_dir=".", gate=None):
    open_statuses = {"draft", "inprogress", "in progress", "running"}
    for record in collect_run_gate_records(project_dir):
        if gate and record["gate"] != gate:
            continue
        if record["status"].strip().lower() in open_statuses:
            return True
    return False


def detect_early_implementation_files(project_dir="."):
    candidates = [
        "app",
        "src",
        "tests",
        "test",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "pom.xml",
        "build.gradle",
    ]
    found = []
    for rel_path in candidates:
        path = os.path.join(project_dir, rel_path)
        if not os.path.exists(path):
            continue
        if os.path.isdir(path):
            has_real_file = False
            for _root, _dirs, files in os.walk(path):
                if any(filename != ".gitkeep" for filename in files):
                    has_real_file = True
                    break
            if has_real_file:
                found.append(rel_path)
        else:
            found.append(rel_path)
    return found


def validate_gate_progression(project_dir=".", current_gate="phase0"):
    issues = []
    if current_gate not in GATE_ORDER:
        return issues

    current_idx = GATE_ORDER.index(current_gate)
    run_records = collect_run_gate_records(project_dir)
    future_runs = [
        record for record in run_records
        if record["gate"] in GATE_ORDER and GATE_ORDER.index(record["gate"]) > current_idx
    ]
    for record in future_runs:
        issues.append(
            f"  X 프로세스 위반: 현재 Gate는 {current_gate}인데 앞선 Gate Run이 존재합니다 "
            f"({record['gate']}, {record['path']})"
        )

    if current_idx < GATE_ORDER.index("impl"):
        early_files = detect_early_implementation_files(project_dir)
        for rel_path in early_files:
            issues.append(
                f"  X 프로세스 위반: 현재 Gate는 {current_gate}인데 구현/테스트 파일 후보가 존재합니다 ({rel_path})"
            )

    return issues


def validate_artifact_content_boundaries(project_dir="."):
    issues = []
    artifact_dir = os.path.join(project_dir, "docs", "artifacts")
    if not os.path.isdir(artifact_dir):
        return issues

    operational_patterns = [
        r"현재\s*Gate\s*는\s*[A-Za-z0-9_-]+",
        r"현재\s*게이트\s*는\s*[A-Za-z0-9_-]+",
        r"current\s+gate\s+is\s+[A-Za-z0-9_-]+",
    ]
    target_sections = ("주요 제약", "요구사항", "성공 기준", "비목표")

    for root, _, files in os.walk(artifact_dir):
        if os.path.basename(root).lower() == "evidence":
            continue
        for filename in files:
            if not filename.lower().endswith(".md"):
                continue
            path = os.path.join(root, filename)
            try:
                with open(path, encoding="utf-8") as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                continue

            current_section = ""
            for idx, line in enumerate(lines, start=1):
                section_match = re.match(r"^#{2,}\s*(.+?)\s*$", line)
                if section_match:
                    current_section = section_match.group(1)
                if not any(section in current_section for section in target_sections):
                    continue
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in operational_patterns):
                    rel_path = os.path.relpath(path, project_dir)
                    issues.append(
                        f"  X 문서 경계 위반: {rel_path}:{idx}에 운영 상태가 업무 산출물 본문에 기록되었습니다 "
                        "(현재 Gate/Run 상태는 session.json 또는 docs/runs에 기록)"
                    )
    return issues


def is_unresolved_trace_value(value):
    normalized = value.strip().lower()
    return normalized in {"", "-", "미정", "확인필요", "tbd", "todo"}


def check_trace(project_dir="."):
    session = load_session(project_dir)
    current_gate = session.get("current_gate", "phase0")
    issues = []

    print(f"\n[check-trace] {session.get('project', '프로젝트')} - {GATE_LABELS.get(current_gate, current_gate)}\n")

    progression_issues = validate_gate_progression(project_dir, current_gate)
    if progression_issues:
        print("  Gate 진행 상태 검사: 위반 감지")
        issues.extend(progression_issues)
    else:
        print("  Gate 진행 상태 검사: OK")

    boundary_issues = validate_artifact_content_boundaries(project_dir)
    if boundary_issues:
        print("  문서 내용 경계 검사: 위반 감지")
        issues.extend(boundary_issues)
    else:
        print("  문서 내용 경계 검사: OK")

    discovery_validation_gate = "gate1" if current_gate == "phase0" else current_gate
    discovery_issues = validate_discovery_open_items(project_dir, discovery_validation_gate)
    if discovery_issues:
        print("  Phase 0 미결 항목 검사: 위반 감지")
        issues.extend(discovery_issues)
    else:
        print("  Phase 0 미결 항목 검사: OK")

    if current_gate in ("gate3", "impl", "gate4", "gate5"):
        print("  Gate 2 산출물 유지 검사")
        prior_design_checks = [
            ("SW 아키텍처 정의서", validate_architecture_spec),
            ("프로그램명세서", validate_program_spec),
            ("보안가이드", validate_security_guide),
            ("화면설계서", validate_screen_spec),
            ("API 정의서", validate_api_spec),
            ("개발표준정의서", validate_development_standard),
            ("프로젝트 단어사전", validate_project_glossary),
        ]
        for label, validator in prior_design_checks:
            _files, prior_issues = validator(project_dir)
            if prior_issues:
                issues.extend(f"  X {issue}" for issue in prior_issues)
            else:
                print(f"  O {label} 확인")

    group_reqs, detail_reqs, defined_acs, ac_delegates = parse_requirements(project_dir)

    # ── Gate 1: REQ-ID별 AC 존재 여부 + TRACEABILITY.md 행 등록 여부
    if current_gate == "gate1":
        print("  Gate 1 검사 (1): 인수 기준(AC) 정의 여부")
        if not detail_reqs:
            issues.append("REQUIREMENTS.md에 REQ-NNN-NN 형식의 요구사항이 없습니다.")
        for req in sorted(detail_reqs):
            ac_id = req.replace("REQ-", "")
            if ac_id in defined_acs:
                print(f"  O {req} - AC 확인")
            elif ac_id in ac_delegates and ac_delegates[ac_id] in defined_acs:
                print(f"  O {req} - AC-{ac_delegates[ac_id]} 위임 확인")
            else:
                issues.append(f"  X {req} - AC 미정의")

        print("\n  Gate 1 검사 (2): TRACEABILITY.md 행 등록 여부")
        traceability = parse_traceability(project_dir)
        if not traceability:
            issues.append("  X TRACEABILITY.md 없음 — PM이 작성해야 합니다")
        else:
            for req in sorted(detail_reqs):
                if req in traceability:
                    print(f"  O {req} - TRACEABILITY.md 행 확인")
                else:
                    issues.append(f"  X {req} - TRACEABILITY.md에 행 미등록")

    # ── Gate 2: 설계 파일 내 REQ-ID 포함 여부 (TRACEABILITY.md 우선, 없으면 그룹 파일 fallback)
    if current_gate == "gate2":
        design_dir = find_first_existing(project_dir, [
            os.path.join("docs", "artifacts", "02-design"),
            os.path.join("docs", "02-design"),
        ])
        traceability = parse_traceability(project_dir)

        if traceability:
            print("  Gate 2 검사: TRACEABILITY.md 기반 설계 파일 내 REQ-ID 포함 확인")
            design_docs = []
            if design_dir and os.path.isdir(design_dir):
                for root, _dirs, files in os.walk(design_dir):
                    for file_name in files:
                        if file_name.endswith(".md"):
                            design_docs.append(os.path.join(root, file_name))
            for req in sorted(detail_reqs):
                info = traceability.get(req)
                if info and re.search(r'통합|삭제됨', info.get("status", "")):
                    print(f"  - {req} - {info['status']} (검사 제외)")
                    continue
                if not info or not info["design"]:
                    issues.append(f"  X {req} - TRACEABILITY.md에 설계 문서 미등록")
                    continue
                # 쉼표 구분된 복수 설계 파일 지원
                design_files = [f.strip() for f in info["design"].split(',') if f.strip()]
                found_in_any = False
                missing_files = []
                for df in design_files:
                    if not df.endswith(".md"):
                        continue
                    filepath = os.path.join(design_dir or "", df)
                    if not os.path.exists(filepath):
                        missing_files.append(df)
                        continue
                    with open(filepath, encoding="utf-8") as f:
                        content = f.read()
                    if req in content:
                        found_in_any = True
                        break
                if not found_in_any and design_docs:
                    for filepath in design_docs:
                        with open(filepath, encoding="utf-8") as f:
                            content = f.read()
                        if req in content:
                            found_in_any = True
                            break
                if missing_files and not found_in_any:
                    issues.append(f"  X {req} - {', '.join(missing_files)} 파일 없음")
                elif found_in_any:
                    print(f"  O {req} - 설계 산출물 내 ID 확인")
                else:
                    issues.append(f"  X {req} - 설계 산출물 안에 {req} 없음")
        else:
            print("  Gate 2 검사: REQ 그룹별 설계 파일 존재 여부 (TRACEABILITY.md 없음 — fallback)")
            for group in sorted(group_reqs):
                filename = f"{group.lower()}-design.md"
                filepath = os.path.join(design_dir or "", filename)
                if os.path.exists(filepath):
                    print(f"  O {group} - {filename} 확인")
                else:
                    issues.append(f"  X {group} - docs/02-design/{filename} 없음")

        print("\n  Gate 2 검사: SW 아키텍처 정의서 확정 여부")
        architecture_files, architecture_issues = validate_architecture_spec(project_dir)
        if architecture_files and not architecture_issues:
            print(f"  O SW 아키텍처 정의서 확인 ({', '.join(architecture_files)})")
        for issue in architecture_issues:
            issues.append(f"  X {issue}")

        print("\n  Gate 2 검사: 보안가이드 확정 여부")
        security_guide_files, security_guide_issues = validate_security_guide(project_dir)
        if security_guide_files and not security_guide_issues:
            print(f"  O 보안가이드 확인 ({', '.join(security_guide_files)})")
        for issue in security_guide_issues:
            issues.append(f"  X {issue}")

        print("\n  Gate 2 검사: 프로그램명세서 상세 SW 설계 여부")
        program_spec_files, program_spec_issues = validate_program_spec(project_dir)
        if program_spec_files and not program_spec_issues:
            print(f"  O 프로그램명세서 확인 ({', '.join(program_spec_files)})")
        for issue in program_spec_issues:
            issues.append(f"  X {issue}")

        print("\n  Gate 2 검사: 화면설계 기준 증적 여부")
        screen_spec_files, screen_spec_issues = validate_screen_spec(project_dir)
        if screen_spec_files and not screen_spec_issues:
            print(f"  O 화면설계서 기준 증적 확인 ({', '.join(screen_spec_files)})")
        for issue in screen_spec_issues:
            issues.append(f"  X {issue}")

        print("\n  Gate 2 검사: API 정의서 상세 여부")
        api_spec_files, api_spec_issues = validate_api_spec(project_dir)
        if api_spec_files and not api_spec_issues:
            print(f"  O API 정의서 확인 ({', '.join(api_spec_files)})")
        elif not api_spec_files and not api_spec_issues:
            print("  - API 정의서 검사 제외 (프로그램명세서에 API 없음)")
        for issue in api_spec_issues:
            issues.append(f"  X {issue}")

        print("\n  Gate 2 검사: 개발표준정의서 근거 여부")
        dev_standard_files, dev_standard_issues = validate_development_standard(project_dir)
        if dev_standard_files and not dev_standard_issues:
            print(f"  O 개발표준정의서 확인 ({', '.join(dev_standard_files)})")
        for issue in dev_standard_issues:
            issues.append(f"  X {issue}")

        print("\n  Gate 2 검사: 프로젝트 단어사전/도메인 여부")
        glossary_files, glossary_issues = validate_project_glossary(project_dir)
        if glossary_files and not glossary_issues:
            print(f"  O 프로젝트 단어사전 확인 ({', '.join(glossary_files)})")
        for issue in glossary_issues:
            issues.append(f"  X {issue}")

        print("\n  Gate 2 검사: Gate 3 진입 전 설계 검수 Run 완료 여부")
        required_review_runs = [
            ("security-review", "보안 검토"),
            ("screen-review", "화면 검토"),
            ("ui-review", "UI 품질 검토"),
            ("development-standard-review", "개발표준 검토"),
        ]
        for skill_name, label in required_review_runs:
            if has_completed_run(project_dir, gate="gate2", skill=skill_name):
                print(f"  O {label} Run 완료 확인 ({skill_name})")
            else:
                issues.append(f"  X {label} Run 미완료 - Gate 3 진입 전 {skill_name} 완료 필요")

    # ── Gate 3: 모든 REQ-NNN-NN에 TST-ID 매핑 여부 + TRACEABILITY.md tst_ids 등록 여부
    if current_gate == "gate3":
        print("  Gate 3 검사 (1): REQ-ID별 TST-ID 커버리지")
        covered = parse_test_plan(project_dir)
        traceability = parse_traceability(project_dir)
        for req in sorted(detail_reqs):
            req_status = traceability.get(req, {}).get("status", "")
            if req_status == "삭제됨" or re.search(r'통합', req_status):
                print(f"  - {req} - {req_status} (검사 제외)")
                continue
            if req in covered:
                print(f"  O {req} - TST 매핑 확인")
            else:
                issues.append(f"  X {req} - Test-Plan.md에 TST 매핑 없음")

        print("\n  Gate 3 검사 (2): TRACEABILITY.md tst_ids 컬럼 등록 여부")
        for req in sorted(detail_reqs):
            info = traceability.get(req, {})
            req_status2 = info.get("status", "")
            if req_status2 == "삭제됨" or re.search(r'통합', req_status2):
                continue
            unresolved_columns = [
                label for label, value in info.get("test_columns", {}).items()
                if is_unresolved_trace_value(value)
            ]
            if unresolved_columns:
                issues.append(
                    f"  X {req} - TRACEABILITY.md 테스트 컬럼 미정: {', '.join(unresolved_columns)} "
                    "(테스트가 불필요하면 '해당없음', 통합/UI 테스트로 대체하면 해당 IT/UI ID를 명시)"
                )
                continue
            tst_ids = info.get("tst_ids", [])
            if tst_ids:
                print(f"  O {req} - TST-ID {', '.join(tst_ids)} 등록 확인")
            else:
                issues.append(f"  X {req} - TRACEABILITY.md에 tst_ids 미등록")

    # ── Impl: 개발표준 확정 + 구현 파일/테스트 연결 확인
    if current_gate == "impl":
        print("  Impl 검사 (0): Implementation Plan Run 여부")
        if has_completed_run(project_dir, gate="impl", skill="implementation-plan"):
            print("  O Implementation Plan Run 완료 확인")
        else:
            print("  ! Implementation Plan Run 없음 - 작은 단일 Run 구현이면 생략 가능, 중간 이상 작업은 Build Wave 계획 권장")

        print("\n  Impl 검사 (1): 개발표준정의서 확정 여부")
        dev_standard_files, dev_standard_issues = validate_development_standard(project_dir)
        if dev_standard_files and not dev_standard_issues:
            print(f"  O 개발표준정의서 확인 ({dev_standard_files[0]})")
        for issue in dev_standard_issues:
            issues.append(f"  X {issue}")

        print("\n  Impl 검사 (2): TRACEABILITY.md 구현 증적 파일 존재 및 ID 포함 여부")
        traceability = parse_traceability(project_dir)
        if not traceability:
            issues.append("  X TRACEABILITY.md 없음 - 구현 파일 연결 확인 불가")
        for req in sorted(detail_reqs):
            info = traceability.get(req, {})
            req_status = info.get("status", "")
            if req_status == "삭제됨" or re.search(r'통합', req_status):
                continue

            evidence_paths = [
                item for item in split_trace_values(info.get("review", ""))
                if is_probable_source_path(item)
            ]
            if not evidence_paths:
                issues.append(f"  X {req} - 추적표 증적에 구현 파일 경로 없음")
                continue

            existing_paths = []
            id_found = False
            related_ids = [req] + info.get("tst_ids", [])
            for evidence_path in evidence_paths:
                full_path = os.path.join(project_dir, evidence_path)
                if not os.path.exists(full_path):
                    issues.append(f"  X {req} - 구현 증적 파일 없음: {evidence_path}")
                    continue
                existing_paths.append(evidence_path)
                if is_probable_text_file(full_path):
                    try:
                        with open(full_path, encoding="utf-8") as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        content = ""
                    if any(related_id and related_id in content for related_id in related_ids):
                        id_found = True

            if existing_paths:
                print(f"  O {req} - 구현 파일 존재 확인 ({', '.join(existing_paths[:3])})")
                if id_found:
                    print(f"  O {req} - 구현/테스트 파일 내 관련 ID 확인")
                else:
                    issues.append(f"  X {req} - 구현/테스트 파일 안에 관련 REQ 또는 TEST ID 없음")

        print("\n  Impl 검사 (3): 테스트케이스 실행 상태")
        tst_results = parse_test_plan_status(project_dir)
        if not tst_results:
            issues.append("  X 테스트케이스 실행 상태 없음")
        else:
            not_passed = [(tid, status) for tid, status in tst_results if status != "pass"]
            passed = [(tid, status) for tid, status in tst_results if status == "pass"]
            print(f"  총 {len(tst_results)}건: Pass {len(passed)}, 미통과 {len(not_passed)}")
            for tid, _ in passed:
                print(f"  O {tid} - Pass")
            for tid, status in not_passed:
                issues.append(f"  X {tid} - {status}")

    # ── Gate 4: 리뷰 파일 내 REQ-ID 포함 여부 + TST-ID 실행 상태
    if current_gate == "gate4":
        review_dirs = [
            os.path.join(project_dir, "docs", "artifacts", "04-review"),
            os.path.join(project_dir, "docs", "04-review"),
        ]
        review_files = []
        for review_dir in review_dirs:
            if os.path.isdir(review_dir):
                for root, _, files in os.walk(review_dir):
                    if os.path.basename(root).lower() == "evidence":
                        continue
                    for filename in files:
                        if filename.lower().endswith(".md"):
                            review_files.append(os.path.join(root, filename))
        traceability = parse_traceability(project_dir)

        if traceability:
            print("  Gate 4 검사 (1): TRACEABILITY.md 기반 리뷰 파일 내 REQ-ID 포함 확인")
            file_contents = {}
            for filepath in review_files:
                with open(filepath, encoding="utf-8") as f:
                    file_contents[filepath] = f.read()
            for req in sorted(detail_reqs):
                info = traceability.get(req, {})
                status = info.get("status", "")
                if status in ("미구현", "삭제됨"):
                    print(f"  - {req} - {status} (리뷰 검사 제외)")
                    continue
                matched = [
                    os.path.relpath(path, project_dir)
                    for path, content in file_contents.items()
                    if req in content
                ]
                if matched:
                    print(f"  O {req} - 리뷰 문서 내 ID 확인 ({matched[0]})")
                else:
                    issues.append(f"  X {req} - docs/artifacts/04-review 리뷰 문서 안에 {req} 없음")
        else:
            print("  Gate 4 검사 (1): REQ 그룹별 리뷰 파일 존재 여부 (TRACEABILITY.md 없음 — fallback)")
            if not review_files:
                for group in sorted(group_reqs):
                    issues.append(f"  X {group} - docs/artifacts/04-review 리뷰 문서 없음")
                    continue
            file_contents = {}
            for filepath in review_files:
                if filepath not in file_contents:
                    with open(filepath, encoding="utf-8") as f:
                        file_contents[filepath] = f.read()
            for group in sorted(group_reqs):
                if any(group in content for content in file_contents.values()):
                    print(f"  O {group} - 리뷰 문서 내 ID 확인")
                else:
                    issues.append(f"  X {group} - docs/artifacts/04-review 리뷰 문서 안에 {group} 없음")

        print("\n  Gate 4 검사 (2): TST-ID 실행 상태")
        tst_results = parse_test_plan_status(project_dir)
        if not tst_results:
            issues.append("Test-Plan.md에 TST-ID가 없거나 파일이 존재하지 않습니다.")
        else:
            not_executed = [(tid, s) for tid, s in tst_results if s == 'not_executed']
            failed = [(tid, s) for tid, s in tst_results if s == 'fail']
            passed = [(tid, s) for tid, s in tst_results if s == 'pass']
            skipped = [(tid, s) for tid, s in tst_results if s == 'skip']

            print(f"  총 {len(tst_results)}건: Pass {len(passed)}, Fail {len(failed)}, Skip {len(skipped)}, 미실행 {len(not_executed)}")

            for tid, _ in passed:
                print(f"  O {tid} - Pass")
            for tid, _ in skipped:
                print(f"  - {tid} - Skip")
            for tid, _ in failed:
                issues.append(f"  X {tid} - Fail")
                print(f"  X {tid} - Fail")
            for tid, _ in not_executed:
                issues.append(f"  X {tid} - 미실행")
                print(f"  X {tid} - 미실행")

    # stats 계산 및 session.json 업데이트 — 이슈 유무와 무관하게 항상 실행
    try:
        stats = compute_stats(project_dir)
        session["stats"] = stats
        save_session(session, project_dir)
    except Exception as e:
        print(f"  [경고] stats 계산 실패: {e}")

    print()
    if issues:
        print(f"이슈 {len(issues)}건 발견 - Gate 완료 불가:\n")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("이슈 0건 - Gate 완료 가능합니다.")


# ── architecture check ─────────────────────────────────────────────────────

def cmd_check_architecture(level="baseline", project_dir="."):
    files, issues = validate_architecture_spec(project_dir, level=level)
    label = "Draft" if level == "draft" else "Baseline"

    print(f"\n[check-architecture] SW 아키텍처 {label} 검사\n")
    if files:
        for rel_path in files:
            print(f"  대상: {rel_path}")
    else:
        print("  대상: 없음")

    if issues:
        print(f"\n이슈 {len(issues)}건 발견:\n")
        for issue in issues:
            print(f"  X {issue}")
        sys.exit(1)

    print("\n이슈 0건 - SW 아키텍처 기준을 만족합니다.")


# ── gate preflight ─────────────────────────────────────────────────────────

def validate_gate_start_prerequisites(project_dir=".", target_gate="phase0"):
    """Gate 전환 직전에 이전 단계의 완료 조건만 검사한다."""
    if target_gate not in GATE_ORDER:
        return []

    issues = []
    target_idx = GATE_ORDER.index(target_gate)
    if target_idx >= GATE_ORDER.index("gate1"):
        issues.extend(validate_discovery_open_items(project_dir, current_gate="gate1"))
    return issues


def require_gate_start_prerequisites(project_dir=".", target_gate="phase0"):
    issues = validate_gate_start_prerequisites(project_dir, target_gate)
    if not issues:
        return

    print(f"\n[gate-start] {target_gate} 진입 전 완료 조건 위반:\n")
    for issue in issues:
        print(f"  {issue}")
    print("\n이슈를 정리한 뒤 다시 Gate 전환을 실행하세요.")
    sys.exit(1)


# ── backlog ────────────────────────────────────────────────────────────────

BACKLOG_PATH = "docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md"
LEGACY_BACKLOG_PATH = "docs/backlog/BACKLOG.md"


def get_backlog_path(project_dir="."):
    path = os.path.join(project_dir, BACKLOG_PATH)
    if os.path.exists(path):
        return path
    legacy_path = os.path.join(project_dir, LEGACY_BACKLOG_PATH)
    if os.path.exists(legacy_path):
        return legacy_path
    return path


def _parse_backlog_items(content):
    """BACKLOG.md Active 섹션의 마크다운 테이블에서 BL-NNN 항목을 파싱한다.

    Returns: list of dict{id, title, type, level, priority, status, req, gate, run, source, note}
    """
    items = []
    in_active = False
    for line in content.splitlines():
        if line.startswith("## Active"):
            in_active = True
            continue
        if in_active and line.startswith("## ") and not line.startswith("## Active"):
            break
        if not in_active:
            continue
        m = re.match(r'^\|\s*(BL-\d{3})\s*\|', line)
        if not m:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8:
            continue
        if len(cols) >= 11:
            items.append({
                "id": cols[0], "title": cols[1], "type": cols[2],
                "level": cols[3], "priority": cols[4], "status": cols[5],
                "req": cols[6], "gate": cols[7], "run": cols[8],
                "source": cols[9], "note": cols[10],
            })
        else:
            items.append({
                "id": cols[0], "title": cols[1], "type": "-",
                "level": cols[2], "priority": cols[3], "status": cols[4],
                "req": cols[5], "gate": "-", "run": "-",
                "source": cols[6], "note": cols[7],
            })
    return items


def compute_backlog_stats(project_dir="."):
    """BACKLOG.md에서 Active/Done/Rejected 건수와 레벨·우선순위별 카운트를 계산한다."""
    path = get_backlog_path(project_dir)
    if not os.path.exists(path):
        return {
            "active": 0, "done": 0, "rejected": 0,
            "by_type": {"idea": 0, "find": 0, "cr": 0, "issue": 0, "debt": 0},
            "by_level": {"trivial": 0, "small": 0, "major": 0},
            "by_priority": {"p0": 0, "p1": 0, "p2": 0, "p3": 0},
        }

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Active 항목 파싱 (레벨·우선순위 포함)
    active_items = _parse_backlog_items(content)

    # Done / Rejected 건수: BL-NNN 행만 카운트 (헤더·빈행 제외)
    def _count_section(section_header):
        count = 0
        in_section = False
        for line in content.splitlines():
            if line.startswith(f"## {section_header}"):
                in_section = True
                continue
            if in_section and line.startswith("## ") and not line.startswith(f"## {section_header}"):
                break
            if in_section and re.match(r'^\|\s*BL-\d{3}\s*\|', line):
                count += 1
        return count

    level_map = {
        "Trivial": "trivial", "Small": "small", "Major": "major",
        "🟢": "trivial", "🟡": "small", "🔴": "major",
    }
    by_level = {"trivial": 0, "small": 0, "major": 0}
    by_priority = {"p0": 0, "p1": 0, "p2": 0, "p3": 0}
    by_type = {"idea": 0, "find": 0, "cr": 0, "issue": 0, "debt": 0}
    for item in active_items:
        typ = item.get("type", "").lower()
        if typ in by_type:
            by_type[typ] += 1
        lv = level_map.get(item["level"])
        if lv:
            by_level[lv] += 1
        pr = item["priority"].lower()
        if pr in by_priority:
            by_priority[pr] += 1

    return {
        "active":       len(active_items),
        "done":         _count_section("Done"),
        "rejected":     _count_section("Rejected"),
        "by_type":      by_type,
        "by_level":     by_level,
        "by_priority":  by_priority,
    }


def _count_backlog_section(content, section_header):
    count = 0
    in_section = False
    for line in content.splitlines():
        if line.startswith(f"## {section_header}"):
            in_section = True
            continue
        if in_section and line.startswith("## ") and not line.startswith(f"## {section_header}"):
            break
        if in_section and re.match(r"^\|\s*BL-\d{3}\s*\|", line):
            count += 1
    return count


def _refresh_backlog_summary(content):
    stats = {
        "Active": len(_parse_backlog_items(content)),
        "Done": _count_backlog_section(content, "Done"),
        "Rejected": _count_backlog_section(content, "Rejected"),
        "Deferred": _count_backlog_section(content, "Deferred"),
    }
    lines = content.splitlines()
    out = []
    in_stats = False
    wrote = False
    for line in lines:
        if line.startswith("## 통계"):
            in_stats = True
            wrote = True
            out.append(line)
            out.append("")
            for key, value in stats.items():
                out.append(f"- **{key}**: {value}건")
            continue
        if in_stats and line.startswith("## "):
            in_stats = False
            out.append(line)
            continue
        if in_stats:
            continue
        out.append(line)

    if not wrote:
        if out and out[-1].strip():
            out.append("")
        out.extend([
            "## 통계",
            "",
            f"- **Active**: {stats['Active']}건",
            f"- **Done**: {stats['Done']}건",
            f"- **Rejected**: {stats['Rejected']}건",
            f"- **Deferred**: {stats['Deferred']}건",
        ])

    return "\n".join(out) + ("\n" if content.endswith("\n") else "")


def _next_backlog_id(content):
    ids = re.findall(r'\bBL-(\d{3})\b', content)
    next_num = max([int(i) for i in ids], default=0) + 1
    return f"BL-{next_num:03d}"


def cmd_backlog_list(project_dir="."):
    path = get_backlog_path(project_dir)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음. 프로젝트가 Vulcan-Anvil Ex 구조인지 확인하세요.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    items = _parse_backlog_items(content)
    if not items:
        print("  백로그 Active 항목이 없습니다.")
        return

    # 우선순위 순 정렬: P0 > P1 > P2 > P3 > 기타
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    items.sort(key=lambda x: order.get(x["priority"], 9))

    print(f"\n  백로그 Active {len(items)}건:\n")
    for it in items:
        item_type = "" if it.get("type") in ("", "-") else f"{it['type']}/"
        print(f"  {it['id']} [{it['priority']}/{item_type}{it['level']}] {it['status']:10s} {it['title']}")
        if it["req"] and it["req"] != "-":
            print(f"         ↳ {it['req']}  ({it['source']})")
        if it.get("gate") and it["gate"] != "-":
            print(f"         ↳ gate: {it['gate']}  run: {it.get('run') or '-'}")
    print()


def cmd_backlog_add(
    title,
    level="",
    priority="P2",
    req="",
    source="",
    note="",
    item_type="IDEA",
    gate="phase0",
    run="",
    project_dir=".",
):
    path = get_backlog_path(project_dir)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    new_id = _next_backlog_id(content)
    new_row = (
        f"| {new_id} | {title} | {item_type or 'IDEA'} | {level or '-'} | {priority} | Proposed | "
        f"{req or '-'} | {gate or '-'} | {run or '-'} | {source or '-'} | {note or '-'} |"
    )

    # Active 테이블의 placeholder 행이 있으면 대체, 아니면 마지막 BL 행 뒤에 삽입
    lines = content.splitlines()
    out = []
    inserted = False
    in_active = False
    for i, line in enumerate(lines):
        if line.startswith("## Active"):
            in_active = True
            out.append(line)
            continue
        if in_active and line.startswith("## ") and not line.startswith("## Active"):
            if not inserted:
                # Active 섹션이 끝나기 전에 새 행 삽입 (빈 줄 앞)
                # 직전 빈 줄들 건너뛰고 테이블 끝 찾기
                j = len(out) - 1
                while j > 0 and out[j].strip() == "":
                    j -= 1
                out.insert(j + 1, new_row)
                inserted = True
            in_active = False
            out.append(line)
            continue
        if in_active and "(아직 없음)" in line:
            out.append(new_row)
            inserted = True
            continue
        out.append(line)

    if not inserted:
        print("오류: BACKLOG.md Active 섹션을 찾지 못했습니다.")
        sys.exit(1)

    updated = _refresh_backlog_summary("\n".join(out) + ("\n" if content.endswith("\n") else ""))
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"  추가: {new_id} - {title}")
    print(f"  다음 단계: Triage (레벨/우선순위 결정) 후 상태 → Triaged")


def cmd_backlog_done(bl_id, commit_hash="", project_dir="."):
    """BL 항목을 Done으로 이동시킨다. Active에서 제거 후 Done 섹션에 기록."""
    path = get_backlog_path(project_dir)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    items = _parse_backlog_items(content)
    target = next((i for i in items if i["id"] == bl_id), None)
    if not target:
        print(f"오류: {bl_id}를 Active 섹션에서 찾지 못했습니다.")
        sys.exit(1)

    done_row = (
        f"| {target['id']} | {target['title']} | {date.today().isoformat()} | "
        f"{commit_hash or '-'} | {target.get('type', '-')} | {target['level']} | "
        f"{target['req']} | {target.get('run', '-')} |"
    )

    lines = content.splitlines()
    out = []
    in_done = False
    removed = False
    done_inserted = False
    for line in lines:
        # Active에서 대상 행 제거
        if not removed and re.match(r'^\|\s*' + re.escape(bl_id) + r'\s*\|', line):
            removed = True
            continue
        if line.startswith("## Done"):
            in_done = True
            out.append(line)
            continue
        if in_done and line.startswith("## ") and not line.startswith("## Done"):
            in_done = False
        if in_done and "(아직 없음)" in line and not done_inserted:
            out.append(done_row)
            done_inserted = True
            continue
        if in_done and re.match(r'^\|\s*\|', line) and not done_inserted:
            pass  # skip accidentally
        out.append(line)

    if in_done and not done_inserted:
        pass

    # 만약 placeholder가 없었다면 Done 섹션 마지막 행 다음에 추가
    if not done_inserted:
        new_out = []
        in_done2 = False
        appended = False
        for line in out:
            if line.startswith("## Done"):
                in_done2 = True
                new_out.append(line)
                continue
            if in_done2 and line.startswith("## ") and not line.startswith("## Done") and not appended:
                # 섹션 종료 직전에 삽입
                j = len(new_out) - 1
                while j > 0 and new_out[j].strip() == "":
                    j -= 1
                new_out.insert(j + 1, done_row)
                appended = True
                in_done2 = False
            new_out.append(line)
        out = new_out
        done_inserted = appended

    updated = _refresh_backlog_summary("\n".join(out) + ("\n" if content.endswith("\n") else ""))
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"  완료: {bl_id} → Done ({commit_hash or 'commit 미지정'})")


def cmd_backlog_reject(bl_id, reason="", project_dir="."):
    path = get_backlog_path(project_dir)
    if not os.path.exists(path):
        print(f"오류: {BACKLOG_PATH} 없음.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    items = _parse_backlog_items(content)
    target = next((i for i in items if i["id"] == bl_id), None)
    if not target:
        print(f"오류: {bl_id}를 Active 섹션에서 찾지 못했습니다.")
        sys.exit(1)

    rej_row = f"| {target['id']} | {target['title']} | {date.today().isoformat()} | {reason or '-'} |"

    lines = content.splitlines()
    out = []
    in_rej = False
    removed = False
    rej_inserted = False
    for line in lines:
        if not removed and re.match(r'^\|\s*' + re.escape(bl_id) + r'\s*\|', line):
            removed = True
            continue
        if line.startswith("## Rejected"):
            in_rej = True
            out.append(line)
            continue
        if in_rej and line.startswith("## ") and not line.startswith("## Rejected"):
            in_rej = False
        if in_rej and "(아직 없음)" in line and not rej_inserted:
            out.append(rej_row)
            rej_inserted = True
            continue
        out.append(line)

    if not rej_inserted:
        # fallback: append before next section
        new_out = []
        in_rej2 = False
        appended = False
        for line in out:
            if line.startswith("## Rejected"):
                in_rej2 = True
                new_out.append(line)
                continue
            if in_rej2 and line.startswith("## ") and not line.startswith("## Rejected") and not appended:
                j = len(new_out) - 1
                while j > 0 and new_out[j].strip() == "":
                    j -= 1
                new_out.insert(j + 1, rej_row)
                appended = True
                in_rej2 = False
            new_out.append(line)
        out = new_out

    updated = _refresh_backlog_summary("\n".join(out) + ("\n" if content.endswith("\n") else ""))
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"  반려: {bl_id} → Rejected ({reason or '사유 미지정'})")


# ── session ────────────────────────────────────────────────────────────────

def cmd_session(gate, status, feature, project_dir="."):
    session = load_session(project_dir)

    if gate not in GATE_LABELS:
        print(f"오류: 유효하지 않은 gate - {gate}")
        print(f"  사용 가능: {', '.join(GATE_LABELS.keys())}")
        sys.exit(1)

    if feature:
        session["feature"] = feature

    gate_order = ["phase0", "gate1", "gate2", "gate3", "impl", "gate4", "gate5"]
    next_gate = None
    if status == "done":
        current_idx = gate_order.index(gate)
        if current_idx + 1 < len(gate_order):
            next_gate = gate_order[current_idx + 1]
        else:
            next_gate = "completed"
        if next_gate != "completed":
            require_gate_start_prerequisites(project_dir, next_gate)

    session["gate_status"][gate] = status

    if status == "done":
        session["current_gate"] = next_gate

        entry = f"{GATE_LABELS[gate]} - {session.get('feature', '')}"
        if entry not in session.get("completed", []):
            session.setdefault("completed", []).append(entry)

    save_session(session, project_dir)
    print(f"  session.json 업데이트: {gate} → {status}")

    feature_label = session.get("feature", "")
    commit_msg = f"session: {gate} done - {GATE_LABELS[gate]}"
    if feature_label:
        commit_msg += f" ({feature_label})"
    # 구현(impl), Gate 4(QA리뷰), Gate 5(최종승인): 소스코드 포함 커밋
    include_source = gate in ("impl", "gate4", "gate5")
    committed = git_commit(commit_msg, project_dir, include_source=include_source)
    if committed:
        git_push_if_remote(project_dir)


def cmd_gate_start(gate, feature=None, project_dir="."):
    """현재 진행 Gate를 명시적으로 전환한다.

    Gate 시작은 원격 대시보드/다른 세션이 현재 단계를 알 수 있도록
    session.json만 커밋하고 push한다.
    """
    session = load_session(project_dir)

    if gate not in GATE_LABELS:
        print(f"오류: 유효하지 않은 gate - {gate}")
        print(f"  사용 가능: {', '.join(GATE_LABELS.keys())}")
        sys.exit(1)

    if feature:
        session["feature"] = feature

    require_gate_start_prerequisites(project_dir, gate)

    session["current_gate"] = gate
    session.setdefault("gate_status", {})[gate] = "pending"
    save_session(session, project_dir)
    print(f"  Gate 시작: {gate} - {GATE_LABELS[gate]}")

    feature_label = session.get("feature", "")
    commit_msg = f"session: {gate} start - {GATE_LABELS[gate]}"
    if feature_label:
        commit_msg += f" ({feature_label})"
    committed = git_commit(commit_msg, project_dir, paths=["session.json"])
    if committed:
        git_push_if_remote(project_dir)

    if has_open_run_for_gate(project_dir, gate):
        print(f"  Run 초안 생략: {gate}에 진행 중인 Run이 이미 있습니다.")
        return

    goal = f"{GATE_LABELS[gate]} 시작 계획"
    if feature_label:
        goal = f"{feature_label} - {goal}"
    print(f"  Run 초안 자동 생성: {gate} Orchestrator Plan")
    cmd_orchestrator_plan(goal=goal, gate=gate, related_ids="", project_dir=project_dir)


def sync_session(project_dir="."):
    session = load_session(project_dir)
    session["implementation"] = compute_implementation_progress(project_dir, session=session)
    session["stats"] = compute_stats(project_dir)
    session["stats"]["implementation"] = session["implementation"]
    save_session(session, project_dir)
    return session


def cmd_sync_session(project_dir="."):
    session = sync_session(project_dir)
    impl = session.get("implementation", {})
    reqs = impl.get("requirements", {})
    waves = impl.get("waves", {})
    print("  session.json 동기화 완료")
    print(f"  요구사항 구현률: {reqs.get('implemented', 0)}/{reqs.get('total', 0)}")
    print(f"  Build Wave: {waves.get('completed', 0)}/{waves.get('total', 0)} 완료")
    if waves.get("current"):
        print(f"  현재 Wave: {waves.get('current')}")


def cmd_wave_start(bw_id, title="", related_ids="", project_dir="."):
    if not re.fullmatch(r"BW-\d{3}", bw_id):
        print(f"오류: BW-ID 형식이 아닙니다: {bw_id}")
        print("  예: BW-001")
        sys.exit(1)

    session = sync_session(project_dir)
    current_gate = session.get("current_gate")
    if current_gate != "impl":
        print(f"오류: Build Wave는 impl 단계에서만 시작할 수 있습니다. 현재 Gate: {current_gate}")
        sys.exit(1)

    impl = session.setdefault("implementation", {})
    waves = impl.setdefault("waves", {})
    current = waves.get("current")
    items = waves.setdefault("items", [])
    if current and current != bw_id:
        current_item = next((item for item in items if item.get("id") == current), {})
        if current_item.get("status") not in WAVE_DONE_STATUSES:
            print(f"오류: 이미 active Build Wave가 있습니다: {current}")
            print("  먼저 wave-complete 또는 sync-session으로 현재 Wave를 정리하세요.")
            sys.exit(1)

    existing = next((item for item in items if item.get("id") == bw_id), None)
    ids = split_csv(related_ids)
    run_path = find_wave_run_file(project_dir, bw_id)
    if not run_path:
        run_id = next_run_id(project_dir)
        run_title = title or f"Build Wave {bw_id}"
        rel_path = os.path.join(runs_rel_dir(project_dir), f"{run_id}_build-wave-{bw_id}_{slugify(run_title)}_v0.1.md")
        skill_path = RUN_SKILLS["build-wave"]
        wave_read_first = [
            "AGENTS.md",
            "session.json",
            "docs/core/TRACEABILITY_RULES.md",
            skill_path,
        ]
        wave_working_documents = [
            rel_path.replace("\\", "/"),
            "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md",
            "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        ]
        wave_reference_documents = [
            "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
            "docs/artifacts/02-design/",
            "docs/core/AGENT_RUN_PROTOCOL.md",
            "docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md",
            "docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md",
        ]
        wave_writable = [
            rel_path.replace("\\", "/"),
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
            "docs/artifacts/04-review/evidence/",
            "TBD: 이 Wave의 코드/테스트 수정 경로를 Orchestrator가 구체화",
        ]
        content = f"""# {run_id} Build Wave {bw_id} - {run_title}

```yaml
run_id: {run_id}
adapter: codex-gpt
gate: impl
persona: build
skill: build-wave
skill_path: {skill_path}
bw_id: {bw_id}
status: In Progress
created_at: {date.today()}
related_ids: {format_yaml_list(ids)}
runner_role: worker-runner
source_documents:
  read_first:
{format_yaml_sequence(wave_read_first, 4)}
  working_documents:
{format_yaml_sequence(wave_working_documents, 4)}
  reference_on_demand:
{format_yaml_sequence(wave_reference_documents, 4)}
scope:
  writable:
{format_yaml_sequence(wave_writable, 4)}
  readonly:
    - "docs/core/"
    - "docs/templates/"
    - "docs/seed-docs/reference-standards/"
  excluded:
    - "docs/ref-docs/"
    - "**/*.db"
    - "**/__pycache__/"
    - "**/.ruff_cache/"
worker_execution_policy:
  forbidden_actions:
    - "Gate 전환을 수행하지 않는다."
    - "session.json의 current_gate, gate_status, completed를 직접 변경하지 않는다."
    - "사용자 승인, QA Pass, 릴리즈 승인, merge 가능 여부를 최종 확정하지 않는다."
    - "scope.writable 밖 파일을 수정하지 않는다."
  required_outputs:
    - "수행한 변경과 검증 결과를 Run 결과에 남긴다."
    - "wave-complete, Gate 전환, session 변경, 최종 승인 판단이 필요하면 Orchestrator 결정 필요 항목으로 반환한다."
verification_results: []
evidence: []
traceability_updates: []
findings: []
change_requests: []
open_issues: []
```

## 1. Wave 작업지시

{run_title}

## 2. 관련 ID

{format_yaml_list(ids)}

## 3. 작업자 입력 계약

- 먼저 `source_documents.read_first`만 읽고 `{bw_id}` 범위와 관련 ID를 확인한다.
- `source_documents.working_documents`는 이번 Wave의 필수 작업 문서다.
- `source_documents.reference_on_demand`는 설계 충돌, 기준 확인, 세부 판단이 필요할 때만 참고한다.
- `scope.writable`에 `TBD`가 남아 있으면 코드 수정 전에 Orchestrator에게 수정 허용 경로를 요청한다.

## 4. Orchestrator 지시

- 이 Run은 `{bw_id}` 하나만 수행한다.
- 다른 Build Wave의 코드 수정은 하지 않는다.
- subagent를 병렬 실행하더라도 이 Wave의 수정 허용 범위 안에서만 작업한다.
- 구현 결과는 Orchestrator가 검토하고 통합한다.
- 작업자 runner는 Gate 전환, session 상태 변경, 최종 승인 판단을 하지 않는다.
- `session.json`의 `current_gate`, `gate_status`, `completed`는 직접 변경하지 않는다.
- 완료 시 테스트, 추적표, Run 기록을 갱신하고 Orchestrator에게 `wave-complete {bw_id}` 실행 필요 여부를 보고한다.

## 5. 수정 범위

| 항목 | 내용 |
| --- | --- |
| 수정 허용 | TBD |
| 읽기 전용 | 요구사항, 설계, 테스트케이스, 개발표준 |
| 제외 | 다른 Wave 범위, 승인되지 않은 리팩터링, `docs/ref-docs/` |

## 6. 검증 계획

TBD

## 7. 결과 기록

### 변경 파일

TBD

### 검증 결과

TBD

### 추적표 갱신

TBD

### 후속 조치

TBD
"""
        write_file(project_dir, rel_path, content)
        run_path = os.path.join(project_dir, rel_path)

    rel_run = os.path.relpath(run_path, project_dir)
    if existing:
        existing["status"] = "In Progress"
        existing["run"] = rel_run
        existing["related_ids"] = sorted(set(existing.get("related_ids", []) + ids))
    else:
        items.append({"id": bw_id, "status": "In Progress", "run": rel_run, "related_ids": ids})

    waves["current"] = bw_id
    session["implementation"] = compute_implementation_progress(project_dir, session=session)
    session["implementation"]["waves"]["current"] = bw_id
    save_session(session, project_dir)
    print(f"  Build Wave 시작: {bw_id}")
    print(f"  Run 문서: {rel_run}")


def cmd_wave_complete(bw_id, status="Verified", req_ids="", project_dir="."):
    if not re.fullmatch(r"BW-\d{3}", bw_id):
        print(f"오류: BW-ID 형식이 아닙니다: {bw_id}")
        sys.exit(1)
    if status not in WAVE_KNOWN_STATUSES:
        print(f"오류: 지원하지 않는 Wave 상태입니다: {status}")
        print(f"  사용 가능: {', '.join(sorted(WAVE_KNOWN_STATUSES))}")
        sys.exit(1)

    session = sync_session(project_dir)
    impl = session.setdefault("implementation", {})
    waves = impl.setdefault("waves", {})
    items = waves.setdefault("items", [])
    item = next((entry for entry in items if entry.get("id") == bw_id), None)
    if not item:
        item = {"id": bw_id, "status": status, "run": "", "related_ids": []}
        items.append(item)
    item["status"] = status

    completed_reqs = split_csv(req_ids)
    if completed_reqs:
        reqs = impl.setdefault("requirements", {})
        current_ids = set(reqs.get("completed_ids", []))
        current_ids.update(completed_reqs)
        reqs["completed_ids"] = sorted(current_ids)
        item["related_ids"] = sorted(set(item.get("related_ids", []) + completed_reqs))

    if waves.get("current") == bw_id and status in WAVE_DONE_STATUSES:
        waves["current"] = ""

    rel_run = update_wave_run_status(project_dir, bw_id, status)
    if rel_run:
        item["run"] = rel_run

    session["implementation"] = compute_implementation_progress(project_dir, session=session)
    if waves.get("current") and status not in WAVE_DONE_STATUSES:
        session["implementation"]["waves"]["current"] = waves.get("current")
    session["stats"] = compute_stats(project_dir)
    session["stats"]["implementation"] = session["implementation"]
    save_session(session, project_dir)

    impl = session.get("implementation", {})
    req_stats = impl.get("requirements", {})
    wave_stats = impl.get("waves", {})
    print(f"  Build Wave 갱신: {bw_id} → {status}")
    print(f"  요구사항 구현률: {req_stats.get('implemented', 0)}/{req_stats.get('total', 0)}")
    print(f"  Build Wave: {wave_stats.get('completed', 0)}/{wave_stats.get('total', 0)} 완료")


# ── export ────────────────────────────────────────────────────────────────

def git_log_timeline(project_dir="."):
    try:
        result = subprocess.run(
            ["git", "log", "--grep=^session:", "--date=short",
             "--pretty=format:%H|%ad|%s", "--", "session.json"],
            cwd=project_dir, capture_output=True, text=True, check=True
        )
        timeline = []
        for line in result.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) < 3:
                continue
            commit, date_str, message = parts
            timeline.append({"commit": commit[:7], "date": date_str, "message": message})
        return list(reversed(timeline))
    except subprocess.CalledProcessError:
        return []


def collect_documents(project_dir="."):
    docs = {"requirements": None, "design": [], "test_plan": None, "review": []}

    req = os.path.join(project_dir, "docs", "01-requirements", "REQUIREMENTS.md")
    if os.path.exists(req):
        docs["requirements"] = "docs/01-requirements/REQUIREMENTS.md"

    design_dir = os.path.join(project_dir, "docs", "02-design")
    if os.path.isdir(design_dir):
        docs["design"] = sorted([
            f"docs/02-design/{f}" for f in os.listdir(design_dir) if f.endswith(".md")
        ])

    tp = os.path.join(project_dir, "docs", "03-test-plan", "Test-Plan.md")
    if os.path.exists(tp):
        docs["test_plan"] = "docs/03-test-plan/Test-Plan.md"

    review_dir = os.path.join(project_dir, "docs", "04-review")
    if os.path.isdir(review_dir):
        docs["review"] = sorted([
            f"docs/04-review/{f}" for f in os.listdir(review_dir) if f.endswith(".md")
        ])

    return docs


def cmd_export(output="snapshot.json", project_dir="."):
    from datetime import datetime
    session = load_session(project_dir)

    snapshot = {
        "schema_version": "1.0",
        "framework": "vulcan-anvil",
        "project": session.get("project", ""),
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "current_gate": session.get("current_gate", "phase0"),
        "gate_status": session.get("gate_status", {}),
        "feature": session.get("feature", ""),
        "started": session.get("started", ""),
        "completed": session.get("completed", []),
        "blocked": session.get("blocked", []),
        "timeline": git_log_timeline(project_dir),
        "documents": collect_documents(project_dir),
        "stats": session.get("stats"),
    }

    out_path = os.path.join(project_dir, output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  snapshot 생성: {output}")
    print(f"  프로젝트: {snapshot['project']} | Gate: {snapshot['current_gate']}")


# ── release ───────────────────────────────────────────────────────────────

# dashboard/ 복사 시 제외할 디렉토리/파일 이름 목록 (REQ-008-03, SEC-002-03)
_DASHBOARD_EXCLUDES = {"node_modules", ".next", ".env.local"}


def _copy_tree_filtered(src_dir, dst_dir, excludes):
    """excludes에 포함된 이름을 건너뛰며 디렉토리 트리를 복사합니다.

    Args:
        src_dir: 복사 원본 디렉토리 절대 경로.
        dst_dir: 복사 대상 디렉토리 절대 경로.
        excludes: 건너뛸 파일/디렉토리 이름 집합.
    """
    import shutil
    for root, dirs, files in os.walk(src_dir):
        # 제외 디렉토리는 재귀 탐색에서도 제외 (os.walk in-place 수정)
        dirs[:] = [d for d in dirs if d not in excludes]
        rel_root = os.path.relpath(root, src_dir)
        for f in files:
            if f in excludes:
                continue
            src = os.path.join(root, f)
            rel_path = os.path.join(rel_root, f) if rel_root != "." else f
            dst = os.path.join(dst_dir, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def cmd_release(target):
    """Vulcan-Dev에서 Vulcan-Anvil 경로로 배포 대상 파일을 복사합니다.

    배포 대상: vulcan.py, templates/, dashboard/, README.md
    배포 제외: docs/, session.json, .claude/, node_modules/, .env.local, .git/

    Args:
        target: 배포 대상 디렉토리 경로 (절대 또는 상대). (REQ-008-01)
    """
    import shutil

    target_abs = os.path.abspath(target)

    # 자기 자신 덮어쓰기 방지 (REQ-008-01)
    if os.path.abspath(VULCAN_DIR) == target_abs:
        print(f"오류: 대상 경로가 현재 Vulcan-Dev 디렉토리와 동일합니다. 자기 자신 덮어쓰기는 허용되지 않습니다.")
        sys.exit(1)

    # 대상 경로 존재 확인
    if not os.path.isdir(target_abs):
        print(f"오류: 대상 경로가 존재하지 않습니다 — {target_abs}")
        sys.exit(1)

    print(f"\nVulcan-Anvil release")
    print(f"  소스: {VULCAN_DIR}")
    print(f"  대상: {target_abs}\n")

    # vulcan.py 복사
    src_vulcan = os.path.join(VULCAN_DIR, "vulcan.py")
    if os.path.isfile(src_vulcan):
        shutil.copy2(src_vulcan, os.path.join(target_abs, "vulcan.py"))
        print(f"  생성/업데이트: vulcan.py")

    # templates/ 복사
    src_templates = os.path.join(VULCAN_DIR, "templates")
    if os.path.isdir(src_templates):
        dst_templates = os.path.join(target_abs, "templates")
        _copy_tree_filtered(src_templates, dst_templates, excludes=set())
        print(f"  생성/업데이트: templates/")

    # dashboard/ 복사 (node_modules/, .next/, .env.local 제외)
    src_dashboard = os.path.join(VULCAN_DIR, "dashboard")
    if os.path.isdir(src_dashboard):
        dst_dashboard = os.path.join(target_abs, "dashboard")
        _copy_tree_filtered(src_dashboard, dst_dashboard, excludes=_DASHBOARD_EXCLUDES)
        print(f"  생성/업데이트: dashboard/")

    # README.md 복사
    src_readme = os.path.join(VULCAN_DIR, "README.md")
    if os.path.isfile(src_readme):
        shutil.copy2(src_readme, os.path.join(target_abs, "README.md"))
        print(f"  생성/업데이트: README.md")

    print(f"\n완료! {target_abs} 에 배포되었습니다.")


# ── upgrade ────────────────────────────────────────────────────────────────

# upgrade 시 타겟에서 삭제할 파일 (이전 버전에서 제거된 파일)
DEPRECATED_FILES = [
    ".claude/skills/gate-transition/skill.md",
    "docs/CHANGE_PROCESS.md",
    "commenting-standards.md",
]

FRAMEWORK_FILES = [
    # CLAUDE.md & settings
    ".claude/CLAUDE.md",
    ".claude/settings.json",
    # agents
    ".claude/agents/discovery.md",
    ".claude/agents/requirements.md",
    ".claude/agents/design.md",
    ".claude/agents/screen-design.md",
    ".claude/agents/security-review.md",
    ".claude/agents/screen-review.md",
    ".claude/agents/ui-review.md",
    ".claude/agents/development-review.md",
    ".claude/agents/test-design.md",
    ".claude/agents/build-planning.md",
    ".claude/agents/build-frontend.md",
    ".claude/agents/build-backend.md",
    ".claude/agents/evidence.md",
    ".claude/agents/review.md",
    # rules
    ".claude/rules/core-principles.md",
    ".claude/rules/gate1-requirements.md",
    ".claude/rules/gate2-design.md",
    ".claude/rules/gate3-testplan.md",
    ".claude/rules/gate4-review.md",
    ".claude/rules/implementation.md",
    ".claude/rules/traceability.md",
    # skills
    ".claude/skills/vulcan/skill.md",
    ".claude/skills/security-baseline/skill.md",
    ".claude/skills/debugging-and-error-recovery/skill.md",
    ".claude/skills/context-engineering/skill.md",
    ".claude/skills/git-workflow-and-versioning/skill.md",
    # docs & guides
    "GATE_GUIDE.md",
    # backlog (v1.1+): PROCESS.md는 upgrade 시 덮어쓰기, BACKLOG.md는 보존
    "docs/backlog/PROCESS.md",
]


def read_version_from_vulcan(vulcan_py_path):
    try:
        with open(vulcan_py_path, encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'^VULCAN_VERSION\s*=\s*["\'](.+?)["\']', content, re.MULTILINE)
        return match.group(1) if match else "unknown"
    except OSError:
        return "unknown"


def extract_variables(project_dir="."):
    """CLAUDE.md에서 프로젝트 변수 추출."""
    claude_path = os.path.join(project_dir, ".claude", "CLAUDE.md")
    if not os.path.exists(claude_path):
        print("오류: .claude/CLAUDE.md를 찾을 수 없습니다.")
        sys.exit(1)

    with open(claude_path, encoding="utf-8") as f:
        content = f.read()

    project = re.search(r'^# (.+?)(?:\s+-|\s+Harness)', content, re.MULTILINE)
    generated = re.search(r'생성일: (.+)', content)

    session = load_session(project_dir)

    return {
        "PROJECT_NAME": project.group(1).strip() if project else session.get("project", "Unknown"),
        "GENERATED_DATE": generated.group(1).strip() if generated else str(date.today()),
    }


def cmd_upgrade(project_dir="."):
    import shutil

    session = load_session(project_dir)
    vulcan_src = session.get("vulcan_src") or VULCAN_DIR
    src_templates = os.path.join(vulcan_src, "templates")

    if not os.path.isdir(src_templates):
        print("오류: Vulcan-Anvil 원본 경로를 찾을 수 없습니다.")
        print(f"  templates 디렉터리가 없습니다: {src_templates}")
        sys.exit(1)

    current_ver = session.get("vulcan_version", "unknown")
    src_vulcan = os.path.join(vulcan_src, "vulcan.py")
    new_ver = read_version_from_vulcan(src_vulcan)

    variables = extract_variables(project_dir)
    print(f"\nVulcan-Anvil upgrade")
    print(f"  프로젝트: {variables['PROJECT_NAME']}")
    print(f"  버전: {current_ver} → {new_ver}")
    print(f"  소스: {vulcan_src}\n")

    for rel_path in FRAMEWORK_FILES:
        tpl_path = os.path.join(src_templates, rel_path)
        if not os.path.exists(tpl_path):
            print(f"  건너뜀 (템플릿 없음): {rel_path}")
            continue
        with open(tpl_path, encoding="utf-8") as f:
            content = render(f.read(), variables)
        dst = os.path.join(project_dir, rel_path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  업데이트: {rel_path}")

    for rel_path in DEPRECATED_FILES:
        dst = os.path.join(project_dir, rel_path)
        if os.path.exists(dst):
            os.remove(dst)
            parent = os.path.dirname(dst)
            if os.path.isdir(parent) and not os.listdir(parent):
                os.rmdir(parent)
            print(f"  삭제 (deprecated): {rel_path}")

    if os.path.exists(src_vulcan):
        shutil.copy2(src_vulcan, os.path.join(project_dir, "vulcan.py"))
        print(f"  업데이트: vulcan.py")

    # v1.1+: Backlog 공식 문서가 없으면 생성하고, legacy BACKLOG.md는 보존한다.
    backlog_dst = os.path.join(project_dir, BACKLOG_PATH)
    if not os.path.exists(backlog_dst):
        legacy_backlog = os.path.join(project_dir, LEGACY_BACKLOG_PATH)
        if os.path.exists(legacy_backlog):
            os.makedirs(os.path.dirname(backlog_dst), exist_ok=True)
            shutil.copy2(legacy_backlog, backlog_dst)
            print(f"  마이그레이션: {LEGACY_BACKLOG_PATH} → {BACKLOG_PATH}")
        else:
            tpl = os.path.join(src_templates, "docs/backlog/BACKLOG.md")
            if os.path.exists(tpl):
                with open(tpl, encoding="utf-8") as f:
                    content = render(f.read(), variables)
                os.makedirs(os.path.dirname(backlog_dst), exist_ok=True)
                with open(backlog_dst, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  생성 (Ex 신규): {BACKLOG_PATH}")

    install_project_doc_framework(project_dir, variables, overwrite=True, source_root=vulcan_src)
    install_project_artifacts(project_dir, variables, overwrite=False, source_root=vulcan_src)
    ensure_gitignore_entry(project_dir, "docs/ref-docs/")
    create_vulcan_config(project_dir)

    session["vulcan_version"] = new_ver
    session["vulcan_src"] = vulcan_src
    save_session(session, project_dir)

    print(f"\n완료! v{current_ver} → v{new_ver}")
    print(f"보존된 파일: ENVIRONMENT.md, session.json, docs/")


# ── version ───────────────────────────────────────────────────────────────

def cmd_version(project_dir="."):
    print(f"Vulcan-Anvil Ex v{VULCAN_VERSION}")
    session_path = os.path.join(project_dir, "session.json")
    if os.path.exists(session_path):
        session = load_session(project_dir)
        project_ver = session.get("vulcan_version", "unknown")
        print(f"  프로젝트: {session.get('project', '-')} (설치 버전: {project_ver})")


# ── init ───────────────────────────────────────────────────────────────────

def cmd_run_new(adapter, gate, skill, title, related_ids, persona=None, project_dir="."):
    if skill not in RUN_SKILLS:
        print(f"오류: 알 수 없는 skill입니다: {skill}")
        print("사용 가능 skill:")
        for name in RUN_SKILLS:
            print(f"  - {name}")
        sys.exit(1)

    persona = persona or default_persona_for_run(gate, skill)
    if persona not in RUN_PERSONAS:
        print(f"오류: 알 수 없는 persona입니다: {persona}")
        print("사용 가능 persona:")
        for name in RUN_PERSONAS:
            print(f"  - {name}")
        sys.exit(1)

    run_id = next_run_id(project_dir)
    rel_path = os.path.join(runs_rel_dir(project_dir), f"{run_id}_{slugify(title)}_v0.1.md")
    ids = split_csv(related_ids)
    skill_path = RUN_SKILLS[skill]
    profile = load_delivery_profile(project_dir)
    preset = build_run_input_preset(profile, gate, skill, skill_path, rel_path)
    run_type = preset["run_type"] if preset else RUN_TYPES_BY_GATE.get(gate, "Review")
    completion_section_number = "6" if preset else "5"
    first_read_docs = preset["source_documents"]["read_first"] if preset else [
        "AGENTS.md",
        "session.json",
        "docs/core/TRACEABILITY_RULES.md",
        skill_path,
    ]
    first_read_section = "\n".join(f"- `{path}`" for path in first_read_docs)
    input_sections = render_run_input_preset(preset, ids, persona, gate) if preset else f"""## 3. 입력 범위

| 항목 | 내용 |
| --- | --- |
| 관련 ID | `{format_yaml_list(ids)}` |
| Persona | `{persona}` |
| 대상 문서 | 실행 전 Run 작성자가 구체 경로를 기입 |
| 대상 코드 | 실행 전 Run 작성자가 구체 경로를 기입 |
| 제외 범위 | `docs/ref-docs/`, 비밀/토큰/개인정보, 관련 없는 리팩터링 |

## 4. 수행 지시

1. 관련 문서와 코드를 확인한다.
2. `{persona}` persona의 책임과 금지사항을 확인한다.
3. skill 절차에 따라 누락, 결함, 변경 필요 여부를 판단한다.
4. 필요한 경우 문서, 코드, 테스트, 증적을 갱신한다.
5. 검증 명령을 실행하고 결과를 기록한다.
6. `RUN_OUTPUT_CONTRACT.md` 형식에 맞게 이 Run 기록을 갱신한다."""

    content = f"""# {run_id} {title}

```yaml
run_id: {run_id}
adapter: {adapter}
gate: {gate}
persona: {persona}
skill: {skill}
skill_path: {skill_path}
profile: {profile}
run_type: {run_type}
status: Draft
created_at: {date.today()}
related_ids: {format_yaml_list(ids)}
verification_results: []
evidence: []
traceability_updates: []
findings: []
change_requests: []
open_issues: []
```

## 1. Run 목표

{title}

## 2. 에이전트가 먼저 읽을 문서

{first_read_section}

나머지 기준 문서는 `source_documents.reference_on_demand`에 있을 때만 필요 시 참고한다.

{input_sections}

## {completion_section_number}. 완료 보고

### 요약

Draft 상태. 작업 완료 후 `RUN_OUTPUT_CONTRACT.md`에 맞춰 요약한다.

### 변경 파일

Draft 상태. 작업 완료 후 변경 파일을 기록한다.

### 검증 결과

Draft 상태. 작업 완료 후 실제 실행한 검증 명령과 결과를 기록한다.

### 후속 조치

Draft 상태. 작업 완료 후 후속 조치나 다음 Run 제안을 기록한다.
"""
    write_file(project_dir, rel_path, content)
    print(f"\nRun 초안 생성 완료: {rel_path}")
    version_run_document(rel_path, f"run: create {run_id} - {title}", project_dir)
    print(f"다음 단계: 에이전트는 Run 파일과 `{skill_path}`를 기준으로 작업합니다.")


def cmd_orchestrator_plan(goal, gate, related_ids, persona=None, adapter="codex-gpt", project_dir="."):
    persona = persona or GATE_DEFAULT_PERSONAS.get(gate, "review")
    if persona not in RUN_PERSONAS:
        print(f"오류: 알 수 없는 persona입니다: {persona}")
        sys.exit(1)

    run_id = next_run_id(project_dir)
    title = f"Orchestrator Plan - {goal}"
    rel_path = os.path.join(runs_rel_dir(project_dir), f"{run_id}_{slugify(title)}_v0.1.md")
    ids = split_csv(related_ids)
    skill = "orchestrator-plan"
    skill_path = RUN_SKILLS[skill]

    content = f"""# {run_id} {title}

```yaml
run_id: {run_id}
adapter: {adapter}
gate: {gate}
persona: {persona}
skill: {skill}
skill_path: {skill_path}
status: Draft
created_at: {date.today()}
related_ids: {format_yaml_list(ids)}
verification_results: []
evidence: []
traceability_updates: []
findings: []
change_requests: []
open_issues: []
```

## 1. Orchestrator 목표

{goal}

## 2. 먼저 읽을 문서

- `AGENTS.md`
- `docs/core/ORCHESTRATOR_PROTOCOL.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/CHANGE_CONTROL_PROCESS.md`
- `docs/adapters/codex-gpt/PERSONA_DELEGATION.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`

## 3. 판단 범위

| 항목 | 내용 |
| --- | --- |
| Gate | `{gate}` |
| 우선 persona | `{persona}` |
| 관련 ID | `{format_yaml_list(ids)}` |
| 목표 산출물 | TBD |
| 제외 범위 | TBD |
| 사용자 승인 필요 항목 | TBD |

## 4. 권장 Run 순서

| 순서 | persona | 목적 | 산출물 | 검증 |
| --- | --- | --- | --- | --- |
| 1 | `{persona}` | 현재 목표와 관련 산출물 확인 | 영향 범위와 누락 항목 | 문서 존재 여부 |
| 2 | TBD | 필요한 구현 또는 문서 수정 | 변경 파일 | 테스트/정적검사 |
| 3 | `review` | 산출물, 추적성, 증적 검수 | FIND/CR/ISSUE 판단 | `vulcan.py run-check` |

## 5. Orchestrator 체크리스트

- [ ] 목표와 관련 ID가 연결되어 있다.
- [ ] 위임할 persona와 직접 수행할 일을 구분했다.
- [ ] 서브에이전트 결과를 최종 사실로 확정하기 전에 Orchestrator가 재검증한다.
- [ ] 구현자가 스스로 최종 검수를 끝내지 않도록 `review` 관점의 검수를 둔다.
- [ ] Gate 4 진입 시 별도 handoff가 도움이 되는지 사용자에게 제안한다.
- [ ] 사용자가 handoff를 수락하지 않으면 현재 작업 환경에서 가능한 검증을 계속한다.
- [ ] `FIND`, `CR`, `ISSUE` 분류 기준을 적용한다.
- [ ] 다음 단계로 넘기기 전에 필요한 사용자 승인을 받는다.

## 6. 완료 보고

### 요약

TBD

### 위임 결과

TBD

### 검증 결과

TBD

### 다음 핸드오프

TBD
"""
    write_file(project_dir, rel_path, content)
    print(f"\nOrchestrator 계획 생성 완료: {rel_path}")
    version_run_document(rel_path, f"run: create {run_id} - orchestrator plan", project_dir)
    print("다음 단계: 계획을 검토한 뒤 필요한 persona Run 또는 handoff를 생성합니다.")


def cmd_handoff(target, title, from_run, gate, related_ids, persona="review", adapter="codex-gpt", project_dir="."):
    if target not in HANDOFF_TARGETS:
        print(f"오류: 알 수 없는 handoff 대상입니다: {target}")
        print("사용 가능 대상:")
        for name in HANDOFF_TARGETS:
            print(f"  - {name}")
        sys.exit(1)
    if persona not in RUN_PERSONAS:
        print(f"오류: 알 수 없는 persona입니다: {persona}")
        sys.exit(1)

    run_id = next_run_id(project_dir)
    full_title = f"Handoff to {target} - {title}"
    rel_path = os.path.join(runs_rel_dir(project_dir), f"{run_id}_{slugify(full_title)}_v0.1.md")
    ids = split_csv(related_ids)
    skill = "handoff"
    skill_path = RUN_SKILLS[skill]
    source_run = from_run or "TBD"

    content = f"""# {run_id} {full_title}

```yaml
run_id: {run_id}
adapter: {adapter}
gate: {gate}
persona: {persona}
skill: {skill}
skill_path: {skill_path}
status: Draft
created_at: {date.today()}
handoff_to: {target}
from_run: {source_run}
related_ids: {format_yaml_list(ids)}
verification_results: []
evidence: []
traceability_updates: []
findings: []
change_requests: []
open_issues: []
```

## 1. Handoff 목표

{title}

## 2. 이전 맥락

| 항목 | 내용 |
| --- | --- |
| 이전 Run | `{source_run}` |
| 대상 환경 | `{target}` |
| 요청 persona | `{persona}` |
| 관련 ID | `{format_yaml_list(ids)}` |

## 3. 대상 환경 지시

- `desktop`: 구현 결과를 브라우저로 열고 화면, 상호작용, 스크린샷 증적을 확인한다.
- `cli`: 테스트, 린트, `vulcan.py run-check`, `vulcan.py check-trace`처럼 재현 가능한 명령을 우선 실행한다.
- `github`: PR diff, 리뷰 코멘트, CI 결과를 기준으로 코드 변경 위험을 검수한다.
- `codex-review`: GitHub 코드 리뷰 결과를 Vulcan 산출물의 `FIND`, `CR`, `ISSUE` 후보로 변환한다.
- `claude`: `CLAUDE.md`와 Claude agent/skill 구조를 참고하되 Core 규약과 추적성 규칙을 우선한다.
- `manual`: 사람이 확인해야 하는 승인, 정책, 일정, 대외 커뮤니케이션 항목을 정리한다.

## 4. 먼저 읽을 문서

- `AGENTS.md`
- `docs/core/ORCHESTRATOR_PROTOCOL.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/CHANGE_CONTROL_PROCESS.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`

## 5. 완료 조건

- [ ] 이전 Run의 결론을 그대로 믿지 않고 대상 환경에서 재검증했다.
- [ ] 검증 명령, 화면 캡처, PR 리뷰, 수동 확인 중 하나 이상의 증적을 남겼다.
- [ ] 발견사항을 `FIND`, `CR`, `ISSUE` 중 하나로 분류했다.
- [ ] 필요한 문서 또는 추적표 갱신 대상을 기록했다.
- [ ] Orchestrator에게 다음 의사결정 항목을 반환했다.

## 6. 완료 보고

### 요약

TBD

### 검증 결과

TBD

### 증적

TBD

### Orchestrator 결정 필요 항목

TBD
"""
    write_file(project_dir, rel_path, content)
    print(f"\nHandoff 문서 생성 완료: {rel_path}")
    version_run_document(rel_path, f"run: create {run_id} - handoff {target}", project_dir)
    print("다음 단계: 대상 환경에서 검증한 뒤 이 Run 파일을 갱신합니다.")


def git_status_porcelain(project_dir="."):
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def review_config_get(review_config, key, default=None):
    new_key = f"independent_{key}"
    if new_key in review_config:
        return review_config.get(new_key)
    return default


def create_review_worktree(project_dir, review_id, worktree_dir=None):
    project_abs = os.path.abspath(project_dir)
    if worktree_dir:
        target = os.path.abspath(worktree_dir)
    else:
        parent = os.path.dirname(project_abs)
        target = os.path.join(parent, f"{os.path.basename(project_abs)}-review-{review_id.lower()}")

    if os.path.exists(target):
        print(f"오류: 독립 검수 worktree 경로가 이미 존재합니다: {target}")
        sys.exit(1)

    try:
        subprocess.run(
            ["git", "worktree", "add", "--detach", target, "HEAD"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as e:
        detail = (e.stderr or e.stdout or str(e)).strip()
        print(f"오류: 독립 검수 worktree 생성 실패 - {detail}")
        sys.exit(1)

    return target


def cmd_review_request(title, gate, related_ids, from_run="", runner=None, create_worktree=None, worktree_dir="", project_dir="."):
    config = load_vulcan_config(project_dir)
    review_config = config.get("review", {}) if isinstance(config.get("review"), dict) else {}
    runner = runner or review_config_get(review_config, "runner", "codex-cli")
    if runner not in INDEPENDENT_REVIEW_RUNNERS:
        print(f"오류: 알 수 없는 독립 검수 runner입니다: {runner}")
        print("사용 가능 runner:")
        for name in INDEPENDENT_REVIEW_RUNNERS:
            print(f"  - {name}")
        sys.exit(1)

    if create_worktree is None:
        create_worktree = bool(review_config_get(review_config, "worktree", True))

    ids = split_csv(related_ids)
    review_id = next_review_id(project_dir)
    review_slug = slugify(f"review {gate} {title}")
    review_rel_dir = reviews_rel_dir(project_dir)
    request_rel_path = os.path.join(review_rel_dir, f"{review_id}_{review_slug}_request.md")
    result_rel_path = os.path.join(review_rel_dir, f"{review_id}_{review_slug}_result.md")
    run_id = next_run_id(project_dir)
    run_rel_path = os.path.join(runs_rel_dir(project_dir), f"{run_id}_independent-review-{review_slug}_v0.1.md")
    source_run = from_run or "TBD"
    dirty_status = git_status_porcelain(project_dir)
    worktree_path = "TBD"

    if create_worktree:
        worktree_path = create_review_worktree(project_dir, review_id, worktree_dir or None)

    gate_focus = {
        "gate2": [
            "Gate 2만 보지 말고 Phase 0 -> Gate 1 -> Gate 2 순서로 상류 정합성을 먼저 확인한다.",
            "Phase 0의 목표, 제약, 가정, 질문, DEC/RISK/ASM이 Gate 1 요구사항/범위에 반영되었는지 확인한다.",
            "Gate 1의 REQ/NREQ/AC, 포함/제외 범위, DEC/ISSUE가 Gate 2 설계 전제와 모순되지 않는지 확인한다.",
            "Gate 2 설계가 승인된 Gate 1 범위를 임의로 축소하거나 확장하지 않았는지 확인한다.",
            "Gate 2 설계 순서(G2-01~G2-10)가 지켜졌는지 확인한다.",
            "REQ/AC가 FUNC, SCR, PGM, API, DB, SEC, DEV 기준으로 빠짐없이 전개되었는지 확인한다.",
            "SW Architecture가 Draft에서 Baseline 후보로 충분히 보강되었는지 확인한다.",
            "UIREF/ui-baseline이 있으면 UI Implementation Contract와 상태별 UI 증적 기준이 있는지 확인한다.",
            "Gate 3 테스트 설계로 넘길 검증 후보와 미해결 질문이 분리되었는지 확인한다.",
        ],
        "gate4": [
            "테스트 결과가 개발표준과 테스트케이스의 필수 명령을 모두 실행했는지 확인한다.",
            "각 검증 결과에 cwd, 명령, exit code, 성공 기준, 로그/증적 경로가 있는지 확인한다.",
            "UI 증적이 상태/시나리오별 UI-ID와 1:1로 연결되었는지 확인한다.",
            "기준 UIREF와 구현 screenshot 차이가 Pass/FIND/CR로 판정되었는지 확인한다.",
            "미실행 검증이나 기대 화면과 다른 캡처가 Pass로 기록되지 않았는지 확인한다.",
        ],
    }.get(gate, [
        "현재 Gate 산출물, Run 결과, 추적표의 일관성을 확인한다.",
        "완료 선언 전에 사용자 승인 대기와 미해결 항목이 분리되었는지 확인한다.",
        "발견사항을 PASS, FIND, CR, ISSUE 중 하나로 분류한다.",
    ])

    upstream_review_content = ""
    upstream_result_content = ""
    if gate == "gate2":
        upstream_review_content = """
## 4.1 Gate 2 상류 정합성 필수 검토

Gate 2 독립 검수는 Gate 2 산출물만 보는 검수가 아니다.
반드시 다음 순서로 앞단부터 확인한 뒤 설계 산출물을 판정한다.

| 순서 | 확인 범위 | 확인 기준 |
| --- | --- | --- |
| 1 | Phase 0 | 프로젝트 목표, 사용자, 제약, 가정, 질문, 리스크, 의사결정이 기록되어 있는가 |
| 2 | Phase 0 -> Gate 1 | Phase 0의 목표/제약/가정/질문이 Gate 1 요구사항, 범위, DEC/ISSUE로 내려왔는가 |
| 3 | Gate 1 | REQ/NREQ/AC, 포함/제외 범위, DEC/ISSUE가 명확한가 |
| 4 | Gate 1 -> Gate 2 | REQ/NREQ/AC가 FUNC, SCR, PGM, API, DB, SEC, DEV 설계로 누락 없이 전개됐는가 |
| 5 | Scope Drift | Gate 2가 승인된 Gate 1 범위를 임의 확장/축소하지 않았는가 |
| 6 | Open Decisions | 미해결 DEC/ISSUE/RISK/ASM이 닫혔거나 Gate 3 입력/Orchestrator 판단 항목으로 분리됐는가 |
| 7 | Design Internal Consistency | 아키텍처, 화면, 기능, API, 프로그램, DB, 보안, 개발표준이 서로 모순되지 않는가 |

상류 정합성에서 누락이나 모순이 있으면 Gate 2 문서 내부가 잘 작성되어 있어도 `PASS`로 판정하지 않는다.
승인된 범위 안에서 보완 가능한 결함은 `FIND`, 요구사항/범위/기준선 변경이 필요하면 `CR`, 사용자 판단이 필요하면 `ISSUE`로 남긴다.
"""
        upstream_result_content = """
## 2.1 Gate 2 상류 정합성 판정

| 판정 항목 | 결과 | 근거 | FIND/CR/ISSUE 후보 |
| --- | --- | --- | --- |
| Phase0 -> Gate1 | TBD |  |  |
| Gate1 -> Gate2 | TBD |  |  |
| Scope Drift | TBD |  |  |
| Open Decisions | TBD |  |  |
| Design Internal Consistency | TBD |  |  |
"""

    request_content = f"""# {review_id} Independent Review Request - {title}

```yaml
review_id: {review_id}
review_type: independent
status: Requested
runner: {runner}
gate: {gate}
upstream_review_required: {"true" if gate == "gate2" else "false"}
source_run: {source_run}
request_file: {request_rel_path}
result_file: {result_rel_path}
worktree_path: {worktree_path}
independent_session_required: true
readonly_review: true
related_ids: {format_yaml_list(ids)}
created_at: {date.today()}
```

## 1. 리뷰 목적

{title}

독립 검수는 작성 세션과 분리된 검수다. 리뷰어는 산출물을 직접 수정하지 않고, 결과 파일에 `PASS`, `FIND`, `CR`, `ISSUE` 후보를 남긴다.

## 2. 먼저 읽을 문서

- `AGENTS.md`
- `session.json`
- `vulcan.config.json`
- `docs/core/INDEPENDENT_REVIEW_PROCESS.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/skills/independent-review.md`

## 3. 리뷰 대상

| 항목 | 내용 |
| --- | --- |
| Gate | `{gate}` |
| 원본 Run | `{source_run}` |
| 관련 ID | `{format_yaml_list(ids)}` |
| 결과 파일 | `{result_rel_path}` |

## 4. 중점 검토 항목

{chr(10).join(f"- {item}" for item in gate_focus)}
{upstream_review_content}

## 5. 범위

### Readonly

- `docs/artifacts/`
- `docs/runs/`
- `docs/core/`
- `docs/adapters/`
- `session.json`
- `vulcan.config.json`

### Writable

- `{result_rel_path}`

## 6. 판정 규칙

| 판정 | 기준 |
| --- | --- |
| PASS | Gate 산출물과 증적이 다음 Gate 진행에 충분하다 |
| FIND | 승인된 범위 안의 결함이며 Gate 안에서 수정 가능하다 |
| CR | 요구사항, 설계, 보안, 데이터, 릴리즈 범위 변경이 필요하다 |
| ISSUE | 결론을 내리려면 추가 질문 또는 사용자 판단이 필요하다 |

## 7. 주의

- 리뷰어는 작성자의 의도를 추측하지 않는다.
- 리뷰어는 Gate 전환, session 상태 변경, 최종 승인 판단을 하지 않는다.
- 대화상 사용자 승인 없이 `User Approved`로 기록하지 않는다.
- 실행하지 않은 테스트나 확인하지 않은 화면을 Pass로 판정하지 않는다.
- 산출물을 수정해야 한다면 직접 수정하지 말고 결과 파일에 `FIND` 또는 `CR`로 남긴다.
"""

    result_content = f"""# {review_id} Independent Review Result - {title}

```yaml
review_id: {review_id}
review_type: independent
status: Draft
runner: {runner}
gate: {gate}
source_run: {source_run}
reviewed_by: TBD
environment: independent-session
result_verdict: Pending
related_ids: {format_yaml_list(ids)}
verification_results: []
evidence: []
findings: []
change_requests: []
issues: []
orchestrator_decision_needed: []
```

## 1. 요약

TBD

## 2. 실행/확인 증적

| 항목 | 결과 | 근거 |
| --- | --- | --- |
| 문서 검토 | TBD |  |
| 추적성 검토 | TBD |  |
| 검증 명령 확인 | TBD |  |
| UI/증적 확인 | TBD |  |
{upstream_result_content}

## 3. Findings

| ID | 심각도 | 관련 ID | 내용 | 권고 처리 |
| --- | --- | --- | --- | --- |
| FIND- | Blocker/Major/Minor |  |  |  |

## 4. CR 후보

| ID | 관련 ID | 변경 필요 범위 | 사유 |
| --- | --- | --- | --- |
| CR- |  |  |  |

## 5. ISSUE 후보

| ID | 질문/위험 | 필요한 결정 |
| --- | --- | --- |
| ISSUE- |  |  |

## 6. Orchestrator 결정 필요 항목

TBD
"""

    run_content = f"""# {run_id} Independent Review - {title}

```yaml
run_id: {run_id}
adapter: codex-gpt
gate: {gate}
persona: review
skill: independent-review
skill_path: docs/adapters/codex-gpt/skills/independent-review.md
status: Draft
created_at: {date.today()}
review_id: {review_id}
review_type: independent
runner: {runner}
from_run: {source_run}
request_file: {request_rel_path}
result_file: {result_rel_path}
worktree_path: {worktree_path}
related_ids: {format_yaml_list(ids)}
verification_results: []
evidence: []
traceability_updates: []
findings: []
change_requests: []
open_issues: []
```

## 1. 목적

{title}

## 2. 독립 검수 요청

- 요청 파일: `{request_rel_path}`
- 결과 파일: `{result_rel_path}`
- 독립 세션/worktree: `{worktree_path}`

## 3. Orchestrator 처리 원칙

- 독립 검수 결과를 최종 사실로 바로 확정하지 않는다.
- 결과 파일의 `FIND`, `CR`, `ISSUE` 후보를 본선 산출물과 대조한다.
- 반영이 필요하면 별도 Run 또는 QA Fix Loop로 처리한다.
- 독립 검수 runner는 Gate 전환, session 상태 변경, 최종 승인 판단을 하지 않는다.
- 리뷰 worktree는 결과 수집 후 사용자가 확인한 뒤 정리한다.

## 4. 완료 보고

TBD
"""

    write_file(project_dir, request_rel_path, request_content)
    write_file(project_dir, result_rel_path, result_content)
    write_file(project_dir, run_rel_path, run_content)

    if create_worktree and worktree_path != "TBD":
        for rel_path in (request_rel_path, result_rel_path, run_rel_path):
            src = os.path.join(project_dir, rel_path)
            dst = os.path.join(worktree_path, rel_path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, encoding="utf-8") as f:
                content = f.read()
            with open(dst, "w", encoding="utf-8") as f:
                f.write(content)

    print(f"\n독립 검수 요청 생성 완료: {request_rel_path}")
    print(f"독립 검수 결과 초안 생성 완료: {result_rel_path}")
    print(f"독립 검수 Run 생성 완료: {run_rel_path}")
    if create_worktree:
        print(f"독립 검수 worktree 생성 완료: {worktree_path}")
    if dirty_status and create_worktree:
        print("\n주의: 본 작업공간에 커밋되지 않은 변경이 있습니다.")
        print("  worktree는 HEAD 기준으로 생성되므로 미커밋 변경은 포함되지 않을 수 있습니다.")
    print("\n다음 단계: 새 Codex/Claude 세션에서 request 파일을 열고 result 파일을 작성합니다.")


def cmd_review_run(
    review_id,
    runner=None,
    model=None,
    reasoning_effort=None,
    timeout_seconds=None,
    sandbox=None,
    dry_run=False,
    project_dir=".",
):
    config = load_vulcan_config(project_dir)
    review_config = config.get("review", {}) if isinstance(config.get("review"), dict) else {}
    runner = runner or review_config_get(review_config, "runner", "") or runtime_role_runner(config, "review")
    runner_normalized = {
        "codex": "codex-cli",
        "claude": "claude-cli",
    }.get(runner, runner)
    if runner_normalized not in INDEPENDENT_REVIEW_EXEC_RUNNERS:
        print(f"오류: review-run에서 아직 지원하지 않는 runner입니다: {runner}")
        print("현재 지원 runner: codex-cli, claude-cli")
        sys.exit(1)

    project_abs = os.path.abspath(project_dir)
    request_rel_path = find_review_file(project_abs, review_id, "_request.md")
    result_rel_path = find_review_file(project_abs, review_id, "_result.md")
    run_rel_path = find_independent_review_run_file(project_abs, review_id)
    if not request_rel_path or not result_rel_path:
        print(f"오류: {review_id}에 해당하는 독립 검수 request/result 파일을 찾을 수 없습니다.")
        sys.exit(1)

    request_abs = os.path.abspath(os.path.join(project_abs, request_rel_path))
    result_abs = os.path.abspath(os.path.join(project_abs, result_rel_path))
    run_abs = os.path.abspath(os.path.join(project_abs, run_rel_path)) if run_rel_path else ""
    with open(request_abs, encoding="utf-8") as f:
        request_content = f.read()
    request_meta = parse_simple_yaml_block(request_content)

    worktree_path = request_meta.get("worktree_path", "TBD")
    exec_dir = os.path.abspath(worktree_path) if worktree_path and worktree_path != "TBD" and os.path.isdir(worktree_path) else project_abs
    exec_result_abs = os.path.abspath(os.path.join(exec_dir, result_rel_path))
    exec_request_abs = os.path.abspath(os.path.join(exec_dir, request_rel_path))
    if not os.path.exists(exec_request_abs):
        exec_request_abs = request_abs
    if not os.path.exists(exec_result_abs):
        exec_result_abs = result_abs

    runner_config = runtime_runner_config(config, runner_normalized)
    if runner_normalized == "codex-cli":
        model = model or review_config_get(review_config, "model", "") or runner_config.get("model") or "gpt-5.5"
        reasoning_effort = (
            reasoning_effort
            or review_config_get(review_config, "reasoning_effort", "")
            or runner_config.get("reasoning_effort")
            or runner_config.get("effort")
            or "high"
        )
    else:
        model = model or review_config_get(review_config, "claude_model", "") or runner_config.get("model") or "claude-opus-4-7"
        reasoning_effort = (
            reasoning_effort
            or review_config_get(review_config, "claude_effort", "")
            or runner_config.get("effort")
            or runner_config.get("reasoning_effort")
            or "high"
        )
    sandbox = sandbox or review_config_get(review_config, "sandbox", "") or runner_config.get("sandbox") or "workspace-write"
    timeout_seconds = int(timeout_seconds or review_config_get(review_config, "exec_timeout_seconds", 1800))

    review_rel_dir = reviews_rel_dir(project_dir)
    runner_log_slug = "codex" if runner_normalized == "codex-cli" else "claude"
    log_ext = "jsonl" if runner_normalized == "codex-cli" else "json"
    log_rel_path = os.path.join(review_rel_dir, f"{review_id}_{runner_log_slug}-exec.{log_ext}")
    stderr_rel_path = os.path.join(review_rel_dir, f"{review_id}_{runner_log_slug}-exec.stderr.txt")
    last_message_rel_path = os.path.join(review_rel_dir, f"{review_id}_{runner_log_slug}-last-message.md")
    log_abs = os.path.abspath(os.path.join(project_abs, log_rel_path))
    stderr_abs = os.path.abspath(os.path.join(project_abs, stderr_rel_path))
    last_message_abs = os.path.abspath(os.path.join(project_abs, last_message_rel_path))
    os.makedirs(os.path.dirname(log_abs), exist_ok=True)

    prompt = f"""You are an independent reviewer for Vulcan-Anvil Ex.

Working directory:
{exec_dir}

Read this independent review request:
{request_rel_path}

Write your review result only to:
{result_rel_path}

Rules:
- Treat this as a new independent review session.
- Do not modify project artifacts, source code, requirements, design documents, test results, or traceability documents.
- You may read files and run safe verification commands if needed.
- You must update the result file with status, reviewed_by, result_verdict, reviewed documents, findings, CR candidates, ISSUE candidates, and evidence.
- Use PASS, FIND, CR, or ISSUE as the result verdict.
- Do not perform Gate transitions, edit session state, or make final approval/merge/release decisions.
- Do not mark user approval unless the request/result contains explicit user approval evidence.
- In your final response, summarize what you wrote to the result file and mention the result verdict.
"""

    if runner_normalized == "codex-cli":
        runner_exe = shutil.which("codex")
        if not runner_exe:
            print("오류: codex CLI를 찾을 수 없습니다. `codex --version`이 실행되는지 확인하세요.")
            sys.exit(1)
        cmd = [
            runner_exe,
            "-a",
            "never",
            "exec",
            "--cd",
            exec_dir,
            "-m",
            model,
            "-c",
            f"model_reasoning_effort={format_yaml_scalar(reasoning_effort)}",
            "--sandbox",
            sandbox,
            "--json",
            "--output-last-message",
            last_message_abs,
            prompt,
        ]
    else:
        runner_exe = shutil.which("claude")
        if not runner_exe:
            print("오류: Claude CLI를 찾을 수 없습니다. `claude --version`이 실행되는지 확인하세요.")
            sys.exit(1)
        cmd = [
            runner_exe,
            "-p",
            prompt,
            "--output-format",
            "json",
            "--effort",
            reasoning_effort,
            "--permission-mode",
            "acceptEdits",
        ]
        if model:
            cmd.extend(["--model", model])

    printable_cmd = " ".join(f'"{part}"' if " " in part else part for part in cmd)
    if dry_run:
        print("Independent review run dry-run")
        print(f"  review_id: {review_id}")
        print(f"  runner: {runner_normalized}")
        print(f"  model: {model or '(runner default)'}")
        print(f"  reasoning_effort: {reasoning_effort}")
        print(f"  exec_dir: {exec_dir}")
        print(f"  command: {printable_cmd}")
        return

    before_hash = file_sha256(exec_result_abs)
    started_dt = datetime.now()
    deadline_dt = started_dt + timedelta(seconds=timeout_seconds)
    started_at = started_dt.isoformat(timespec="seconds")
    deadline_at = deadline_dt.isoformat(timespec="seconds")
    timed_out = False
    try:
        result = subprocess.run(
            cmd,
            cwd=exec_dir,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        exit_code = result.returncode
        stdout = result.stdout or ""
        stderr = result.stderr or ""
    except subprocess.TimeoutExpired as e:
        timed_out = True
        exit_code = 124
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + f"\nTIMEOUT after {timeout_seconds} seconds"
    completed_dt = datetime.now()
    completed_at = completed_dt.isoformat(timespec="seconds")
    duration_seconds = int((completed_dt - started_dt).total_seconds())

    with open(log_abs, "w", encoding="utf-8") as f:
        f.write(stdout)
    with open(stderr_abs, "w", encoding="utf-8") as f:
        f.write(stderr)
    if runner_normalized == "claude-cli":
        with open(last_message_abs, "w", encoding="utf-8") as f:
            try:
                parsed_stdout = json.loads(stdout) if stdout.strip() else {}
                message = (
                    parsed_stdout.get("result")
                    or parsed_stdout.get("text")
                    or parsed_stdout.get("message")
                    or stdout
                )
            except json.JSONDecodeError:
                message = stdout
            f.write(message if isinstance(message, str) else json.dumps(message, ensure_ascii=False, indent=2))

    after_hash = file_sha256(exec_result_abs)
    result_changed = bool(before_hash and after_hash and before_hash != after_hash)
    if timed_out:
        run_status = "timeout"
    elif exit_code != 0:
        run_status = "failed"
    elif not result_changed:
        run_status = "completed_no_result_change"
    else:
        run_status = "completed"
    if os.path.normcase(exec_result_abs) != os.path.normcase(result_abs) and os.path.exists(exec_result_abs):
        os.makedirs(os.path.dirname(result_abs), exist_ok=True)
        shutil.copy2(exec_result_abs, result_abs)

    if run_abs and os.path.exists(run_abs):
        execution_note = f"""

## 5. 독립 검수 실행 기록

```yaml
executed_at: {started_at}
deadline_at: {deadline_at}
completed_at: {completed_at}
duration_seconds: {duration_seconds}
timeout_seconds: {timeout_seconds}
timed_out: {str(timed_out).lower()}
status: {run_status}
runner: {runner_normalized}
model: {model or "(runner default)"}
reasoning_effort: {reasoning_effort}
sandbox: {sandbox}
exec_dir: {exec_dir}
exit_code: {exit_code}
json_log: {log_rel_path}
stderr_log: {stderr_rel_path}
last_message: {last_message_rel_path}
result_file_changed: {str(result_changed).lower()}
```
"""
        with open(run_abs, "a", encoding="utf-8") as f:
            f.write(execution_note)

    print("\n독립 검수 실행 완료")
    print(f"  review_id: {review_id}")
    print(f"  runner: {runner_normalized}")
    print(f"  model: {model or '(runner default)'}")
    print(f"  reasoning_effort: {reasoning_effort}")
    print(f"  status: {run_status}")
    print(f"  duration_seconds: {duration_seconds}")
    print(f"  exit_code: {exit_code}")
    print(f"  result_changed: {str(result_changed).lower()}")
    print(f"  json_log: {log_rel_path}")
    print(f"  last_message: {last_message_rel_path}")
    if exit_code != 0:
        print(f"오류: {runner_normalized} 실행이 비정상 종료되었습니다. stderr 로그를 확인하세요: {stderr_rel_path}")
        sys.exit(exit_code)
    if not result_changed:
        print("경고: result 파일 변경이 감지되지 않았습니다. 독립 검수 결과를 확인하세요.")


def check_run_file(path):
    issues = []
    warnings = []
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"오류: Run 파일을 읽을 수 없습니다: {e}")
        sys.exit(1)

    for key in RUN_REQUIRED_KEYS:
        if not re.search(rf"^\s*{re.escape(key)}\s*:", content, re.MULTILINE):
            issues.append(f"필수 필드 누락: {key}")

    if not re.search(r"\b(REQ|NREQ|AC|FUNC|SCR|UIREF|UICON|PGM|DB|IF|SEC|UT|IT|PT|UI|FIND|CR|ISSUE|RUN)-\d+\b", content):
        issues.append("관련 추적 ID가 없습니다.")

    status = ""
    status_match = re.search(r"^\s*status\s*:\s*(.+)$", content, re.MULTILINE)
    if status_match:
        status = status_match.group(1).strip()
        if status not in {"Draft", "Requested", "InProgress", "Completed", "Verified", "Blocked", "Failed", "CompletedWithIssues", "AwaitingApproval"}:
            issues.append(f"허용되지 않은 status 값: {status}")

    skill_match = re.search(r"^\s*skill\s*:\s*(.+)$", content, re.MULTILINE)
    if skill_match:
        skill = skill_match.group(1).strip()
        if skill not in RUN_SKILLS:
            issues.append(f"알 수 없는 skill 값: {skill}")

    persona_match = re.search(r"^\s*persona\s*:\s*(.+)$", content, re.MULTILINE)
    if persona_match:
        persona = persona_match.group(1).strip()
        if persona not in RUN_PERSONAS:
            issues.append(f"알 수 없는 persona 값: {persona}")

    if re.search(r"result\s*:\s*passed", content, re.IGNORECASE) and not re.search(r"command\s*:", content):
        issues.append("passed 결과가 있지만 검증 command가 없습니다.")

    if re.search(r"status\s*:\s*Completed", content) and re.search(r"verification_results\s*:\s*\[\]", content):
        warnings.append("Completed 상태이지만 verification_results가 비어 있습니다.")

    if re.search(r"status\s*:\s*Completed", content) and re.search(r"traceability_updates\s*:\s*\[\]", content):
        warnings.append("Completed 상태이지만 traceability_updates가 비어 있습니다.")

    if status in {"Completed", "Verified", "CompletedWithIssues"}:
        body_without_yaml = re.sub(r"```yaml.*?```", "", content, flags=re.IGNORECASE | re.DOTALL)
        if re.search(r"(?im)(^|\|)\s*(TBD|확정필요|작성필요)\s*(\||$)", body_without_yaml):
            issues.append("Completed 상태이지만 본문에 TBD/확정필요/작성필요 placeholder가 남아 있습니다.")

        is_audit_run = bool(re.search(r"^\s*profile\s*:\s*audit\s*$", content, re.MULTILINE))
        if is_audit_run:
            if not re.search(r"gate_exit_summary\s*:", content):
                issues.append("Audit Run 완료 상태이지만 gate_exit_summary가 없습니다.")
            if not re.search(r"approval_request\s*:", content):
                issues.append("Audit Run 완료 상태이지만 다음 Gate 승인 질문(approval_request)이 없습니다.")

        has_ui_reference = bool(re.search(r"\bUI-\d{3}\b", content))
        has_state_level_ui = bool(re.search(r"\bUI-\d{3}-\d{2}\b", content))
        if has_ui_reference and not has_state_level_ui and re.search(r"ui|화면|캡처|증적", content, re.IGNORECASE):
            issues.append("UI 증적이 포함된 완료 Run이지만 상태/시나리오 단위 UI-ID(UI-001-01)가 없습니다.")
        has_ui_pass_evidence = (
            has_ui_reference
            and re.search(r"result\s*:\s*(passed|Pass)|\|\s*Pass\s*\|", content, re.IGNORECASE)
            and re.search(r"캡처|screenshot|UI Evidence|증적|actual_path|file\s*:", content, re.IGNORECASE)
        )
        has_playwright_evidence = bool(re.search(
            r"capture_tool\s*:\s*Playwright|npx\s+playwright\s+test|playwright\s+test|Playwright.+exit code",
            content,
            re.IGNORECASE,
        ))
        if has_ui_pass_evidence and not has_playwright_evidence:
            issues.append("UI Pass 증적이 있지만 Playwright 실행 결과 또는 capture_tool: Playwright 기록이 없습니다.")

    return issues, warnings


def cmd_run_check(run_file):
    issues, warnings = check_run_file(run_file)
    if warnings:
        print("경고:")
        for warning in warnings:
            print(f"  - {warning}")

    if issues:
        print("Run 검증 실패:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    print("Run 검증 통과")


def create_session_json(target_dir, project_name, profile=DEFAULT_DELIVERY_PROFILE):
    session = {
        "project": project_name,
        "vulcan_src": VULCAN_DIR,
        "vulcan_version": VULCAN_VERSION,
        "profile": profile,
        "current_gate": "phase0",
        "gate_status": {
            "phase0": "pending",
            "gate1": "pending",
            "gate2": "pending",
            "gate3": "pending",
            "impl":  "pending",
            "gate4": "pending",
            "gate5": "pending"
        },
        "feature": "",
        "started": str(date.today()),
        "completed": [],
        "pending": [],
        "blocked": []
    }
    write_file(target_dir, "session.json", json.dumps(session, ensure_ascii=False, indent=2))


def command_version(command, timeout_seconds=10):
    exe = shutil.which(command)
    if not exe:
        return None
    try:
        result = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return (result.stdout or result.stderr or "").strip()


def runner_default_config(name, version=None):
    if name == "codex-cli":
        return {
            "name": "codex-cli",
            "model": "gpt-5.5",
            "effort": "high",
            "sandbox": "workspace-write",
            "version": version
        }
    if name == "claude-cli":
        return {
            "name": "claude-cli",
            "model": "claude-opus-4-7",
            "effort": "high",
            "version": version
        }
    return {
        "name": name,
        "model": None,
        "effort": "high",
        "version": version
    }


def detect_runtime_runners():
    runners = []
    codex_version = command_version("codex")
    claude_version = command_version("claude")
    if codex_version is not None:
        runners.append(runner_default_config("codex-cli", codex_version or None))
    if claude_version is not None:
        runners.append(runner_default_config("claude-cli", claude_version or None))
    return runners


def normalize_runtime_runners(runtime_config):
    available = runtime_config.get("available_runners", [])
    if isinstance(available, list):
        return [runner for runner in available if isinstance(runner, dict) and runner.get("name")]
    if isinstance(available, dict):
        normalized = []
        for name, values in available.items():
            if not isinstance(values, dict) or not values.get("available"):
                continue
            runner = runner_default_config(name, values.get("version"))
            for key in ("model", "effort", "reasoning_effort", "sandbox"):
                if key in values:
                    runner[key] = values[key]
            normalized.append(runner)
        return normalized
    return []


def runtime_runner_names(config):
    return [runner["name"] for runner in normalize_runtime_runners(config.get("runtime", {}))]


def runtime_runner_config(config, runner_name):
    for runner in normalize_runtime_runners(config.get("runtime", {})):
        if runner.get("name") == runner_name:
            return runner
    return runner_default_config(runner_name)


def runtime_default_runner(config):
    names = runtime_runner_names(config)
    if "codex-cli" in names:
        return "codex-cli"
    if names:
        return names[0]
    return "manual"


def runtime_role_runner(config, role):
    names = runtime_runner_names(config)
    default_runner = runtime_default_runner(config)
    if default_runner == "manual":
        return "manual"
    if role in ("build-backend", "build", "evidence") and "codex-cli" in names:
        return "codex-cli"
    if role in ("build-frontend", "review", "pr-cross-validation") and "claude-cli" in names:
        return "claude-cli"
    return default_runner


def runtime_capability(config, capability):
    names = runtime_runner_names(config)
    if capability == "same_runner_independent_review":
        return bool(names)
    if capability == "cross_model_validation":
        return "codex-cli" in names and "claude-cli" in names
    if capability == "parallel_worktrees":
        return bool(names)
    if capability == "parallel_cross_runner_work":
        return "codex-cli" in names and "claude-cli" in names
    return False


def deep_merge_dict(base, updates):
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            deep_merge_dict(base[key], value)
        else:
            base[key] = value
    return base


def default_vulcan_config(available_runners=None):
    has_runner = bool(available_runners) if available_runners is not None else True
    config = {
        "version": VULCAN_VERSION,
        "runtime": {
            "primary": None,
            "available_runners": available_runners or []
        },
        "review": {
            "independent_enabled": has_runner,
            "independent_sandbox": "workspace-write",
            "independent_exec_timeout_seconds": 1800,
            "independent_triggers": INDEPENDENT_REVIEW_DEFAULT_GATES,
            "independent_worktree": True,
            "independent_readonly": True
        },
        "execution": {
            "independent_enabled": has_runner,
            "default_worktree": True,
            "default_timeout_seconds": 2400
        }
    }
    return config


def create_vulcan_config(target_dir):
    rel_path = "vulcan.config.json"
    path = os.path.join(target_dir, rel_path)
    if os.path.exists(path):
        return
    available_runners = detect_runtime_runners()
    write_file(target_dir, rel_path, json.dumps(default_vulcan_config(available_runners), ensure_ascii=False, indent=2))


def load_vulcan_config(project_dir="."):
    path = os.path.join(project_dir, "vulcan.config.json")
    config = default_vulcan_config()
    if not os.path.exists(path):
        return config
    try:
        with open(path, encoding="utf-8") as f:
            user_config = json.load(f)
    except (OSError, json.JSONDecodeError):
        return config
    if isinstance(user_config, dict):
        deep_merge_dict(config, user_config)
    return config


def init(target_dir, project_name, agent_name, remote_url=None, require_remote=False, profile=DEFAULT_DELIVERY_PROFILE):
    import shutil
    print(f"\nVulcan-Anvil 초기화")
    print(f"  프로젝트: {project_name}")
    print(f"  대상 폴더: {target_dir}")
    print(f"  Delivery Profile: {profile}\n")

    if require_remote and not remote_url:
        print("오류: --require-remote가 지정되었지만 --remote가 없습니다.")
        print("  예: python vulcan.py init <dir> <name> --remote <git-url> --require-remote")
        sys.exit(1)

    if os.path.exists(target_dir):
        files = os.listdir(target_dir)
        if files:
            print(f"경고: {target_dir} 폴더가 비어있지 않습니다.")
            answer = input("계속 진행할까요? (y/N): ").strip().lower()
            if answer != "y":
                print("취소됨.")
                sys.exit(0)
    else:
        os.makedirs(target_dir)

    variables = {
        "PROJECT_NAME": project_name,
        "GENERATED_DATE": str(date.today()),
    }

    # .claude/ 디렉토리 전체 복사 후 변수 치환
    src_claude = os.path.join(TEMPLATES_DIR, ".claude")
    dst_claude = os.path.join(target_dir, ".claude")
    copy_tree(src_claude, dst_claude)
    print(f"  생성: .claude/ (agents 13, skills 5, rules 7)")

    # .claude/ 내 모든 .md 파일에 변수 치환 적용
    for root, dirs, files in os.walk(dst_claude):
        for f in files:
            if f.endswith(".md"):
                fpath = os.path.join(root, f)
                with open(fpath, encoding="utf-8") as fp:
                    content = render(fp.read(), variables)
                with open(fpath, "w", encoding="utf-8") as fp:
                    fp.write(content)

    # ENVIRONMENT.md
    content = render(read_template("ENVIRONMENT.md"), variables)
    write_file(target_dir, "ENVIRONMENT.md", content)

    # GATE_GUIDE.md
    copy_file(target_dir, "GATE_GUIDE.md")

    # README.md
    content = render(read_template("PROJECT_README.md"), variables)
    write_file(target_dir, "README.md", content)

    # docs/backlog/
    content = render(read_template("docs/backlog/BACKLOG.md"), variables)
    write_file(target_dir, BACKLOG_PATH, content)
    copy_file(target_dir, "docs/backlog/PROCESS.md", "docs/backlog/PROCESS.md")

    # audit and agent coding document framework
    install_project_doc_framework(target_dir, variables, overwrite=True)
    install_project_artifacts(target_dir, variables, overwrite=False)

    # session.json
    create_session_json(target_dir, project_name, profile)
    create_vulcan_config(target_dir)

    # vulcan.py 자신을 프로젝트에 복사
    shutil.copy2(__file__, os.path.join(target_dir, "vulcan.py"))
    print(f"  생성: vulcan.py")

    # .gitignore
    gitignore = "node_modules/\n.env\n.env.local\ndashboard/.next/\ndashboard/node_modules/\ndocs/ref-docs/\n"
    write_file(target_dir, ".gitignore", gitignore)

    # git init + 초기 커밋
    # 참고: dashboard/는 Vulcan-Anvil 루트에 단일 설치하여 재사용합니다 (REQ-007-01)
    try:
        try:
            subprocess.run(["git", "init", "-b", "main"], cwd=target_dir, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        except subprocess.CalledProcessError:
            subprocess.run(["git", "init"], cwd=target_dir, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
            subprocess.run(["git", "branch", "-M", "main"], cwd=target_dir, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        subprocess.run(["git", "add", "-A"], cwd=target_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"init: {project_name} 프로젝트 초기화"],
            cwd=target_dir, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        print(f"  생성: git 저장소 초기화 + 초기 커밋")
        print(f"  생성: git 기본 브랜치 main")

        if remote_url:
            try:
                subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=target_dir, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
                print(f"  생성: git remote origin")
                subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=target_dir, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
                print(f"  푸시 완료: origin HEAD")
            except subprocess.CalledProcessError as e:
                detail = (e.stderr or e.stdout or str(e)).strip()
                message = f"git remote 등록 또는 push 실패 - {detail}"
                if require_remote:
                    print(f"  오류: {message}")
                    sys.exit(1)
                print(f"  경고: {message}")
                print("  안내: 로컬 초기 커밋은 완료되었습니다. 원격 저장소를 만든 뒤 직접 push할 수 있습니다.")
        else:
            print("  안내: remote가 설정되지 않았습니다. Gate 시작/완료 push를 사용하려면 remote를 설정하세요.")
    except Exception as e:
        if require_remote:
            print(f"  오류: git 초기화 또는 remote push 실패 - {e}")
            sys.exit(1)
        print(f"  경고: git 초기화 실패 - {e}")

    print(f"\n완료! {project_name} 프로젝트가 초기화되었습니다.")
    print(f"\n다음 단계:")
    print(f"  1. cd {target_dir}")
    print(f"  2. Codex 또는 Claude 런타임 실행")
    print(f"  3. Orchestrator에게 '무엇을 만들지' 설명하고 Phase 0부터 시작")
    if not remote_url:
        print(f"  4. 협업/GitHub 대시보드를 쓰려면 git remote를 설정하세요.")
    print(f"\n대시보드 실행:")
    print(f"  cd <Vulcan-Anvil 경로>/dashboard && npm run dev")
    print(f"  브라우저: http://localhost:3001")
    print(f"\nGate 완료 시:")
    print(f"  python vulcan.py check-trace")
    print(f"  python vulcan.py session --gate gate1 --status done --feature '기능명'")


# ── main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Vulcan-Anvil Ex - 5-Gate AI 협업 개발 프레임워크",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
명령어:
  init         새 프로젝트 초기화 (Vulcan-Anvil 디렉토리에서 실행)
  check-trace  현재 Gate 정합성 검사 (프로젝트 디렉토리에서 실행)
  gate-start   현재 진행 Gate 전환 (프로젝트 디렉토리에서 실행)
  session      Gate 상태 업데이트 + git commit (프로젝트 디렉토리에서 실행)
  sync-session session.json 대시보드 상태 캐시 동기화
  wave-start   Build Wave 시작 및 작업지시 Run 생성
  wave-complete Build Wave 완료/상태 갱신
  export       snapshot.json 생성 (프로젝트 디렉토리에서 실행)
  upgrade      프레임워크 파일 최신화 (프로젝트 디렉토리에서 실행)
  version      현재 프레임워크 버전 확인

예시:
  python vulcan.py init ../my-app "MyApp"
  python vulcan.py init ../my-app "MyApp" --remote https://github.com/me/my-app.git
  python vulcan.py init ../my-app "MyApp" --remote https://github.com/me/my-app.git --require-remote
  python vulcan.py check-trace
  python vulcan.py gate-start gate1 --feature "로그인 기능"
  python vulcan.py session --gate gate1 --status done --feature "로그인 기능"
  python vulcan.py sync-session
  python vulcan.py wave-start BW-001 --title "인증 기반 구현" --related-ids REQ-001-01,PGM-001
  python vulcan.py wave-complete BW-001 --status Verified --req REQ-001-01,REQ-002-01
  python vulcan.py export
  python vulcan.py upgrade
        """
    )
    subparsers = parser.add_subparsers(dest="command")

    p_init = subparsers.add_parser("init", help="새 프로젝트 초기화")
    p_init.add_argument("target_dir", help="초기화할 프로젝트 폴더 경로")
    p_init.add_argument("project_name", help="프로젝트 이름")
    p_init.add_argument("--agent-name", default="VULCAN", help="메인 에이전트 이름 (기본값: VULCAN)")
    p_init.add_argument("--remote", default="", help="초기화 후 origin으로 등록할 Git remote URL")
    p_init.add_argument("--require-remote", action="store_true", help="remote 등록/초기 push 실패 시 init 실패 처리")
    p_init.add_argument("--profile", default=DEFAULT_DELIVERY_PROFILE, choices=["audit", "solution", "poc", "lite"], help="Delivery Profile")

    subparsers.add_parser("check-trace", help="현재 Gate 정합성 검사")

    p_check_architecture = subparsers.add_parser("check-architecture", help="SW 아키텍처 성숙도 검사")
    p_check_architecture.add_argument("--level", default="baseline", choices=["draft", "baseline"], help="검사 수준")

    p_gate_start = subparsers.add_parser("gate-start", help="현재 진행 Gate 전환")
    p_gate_start.add_argument("gate", choices=list(GATE_LABELS.keys()), help="시작할 Gate 이름")
    p_gate_start.add_argument("--feature", default="", help="작업 기능명")

    p_session = subparsers.add_parser("session", help="Gate 상태 업데이트 + git commit")
    p_session.add_argument("--gate", required=True, choices=list(GATE_LABELS.keys()), help="Gate 이름")
    p_session.add_argument("--status", required=True, choices=["done", "pending"], help="상태")
    p_session.add_argument("--feature", default="", help="작업 기능명")

    subparsers.add_parser("sync-session", help="session.json 대시보드 상태 캐시 동기화")

    p_wave_start = subparsers.add_parser("wave-start", help="Build Wave 시작 및 작업지시 Run 생성")
    p_wave_start.add_argument("bw_id", help="Build Wave ID (예: BW-001)")
    p_wave_start.add_argument("--title", default="", help="Wave 제목")
    p_wave_start.add_argument("--related-ids", default="", help="관련 ID 콤마 구분")

    p_wave_complete = subparsers.add_parser("wave-complete", help="Build Wave 완료/상태 갱신")
    p_wave_complete.add_argument("bw_id", help="Build Wave ID (예: BW-001)")
    p_wave_complete.add_argument("--status", default="Verified", choices=sorted(WAVE_KNOWN_STATUSES), help="Wave 상태")
    p_wave_complete.add_argument("--req", default="", help="구현 완료 처리할 REQ-ID 콤마 구분")

    p_run_new = subparsers.add_parser("run-new", help="Codex/GPT Run 초안 생성")
    p_run_new.add_argument("--adapter", default="codex-gpt", help="Adapter 이름")
    p_run_new.add_argument("--gate", default="gate1", choices=list(GATE_LABELS.keys()), help="Gate 이름")
    p_run_new.add_argument("--persona", default="", choices=[""] + sorted(RUN_PERSONAS.keys()), help="Run persona")
    p_run_new.add_argument("--skill", required=True, choices=sorted(RUN_SKILLS.keys()), help="Run skill")
    p_run_new.add_argument("--title", required=True, help="Run 제목")
    p_run_new.add_argument("--related-ids", default="", help="관련 ID 콤마 구분")

    p_run_check = subparsers.add_parser("run-check", help="Run 결과 문서 검사")
    p_run_check.add_argument("run_file", help="검사할 Run 문서 경로")

    p_backlog = subparsers.add_parser("backlog", help="백로그 관리 (list/add/done/reject)")
    p_orchestrator_plan = subparsers.add_parser("orchestrator-plan", help="Orchestrator 실행 계획 Run 생성")
    p_orchestrator_plan.add_argument("--goal", required=True, help="Orchestrator가 수립할 목표")
    p_orchestrator_plan.add_argument("--adapter", default="codex-gpt", help="Adapter 이름")
    p_orchestrator_plan.add_argument("--gate", default="gate1", choices=list(GATE_LABELS.keys()), help="Gate 이름")
    p_orchestrator_plan.add_argument("--persona", default="", choices=[""] + sorted(RUN_PERSONAS.keys()), help="우선 적용 persona")
    p_orchestrator_plan.add_argument("--related-ids", default="", help="관련 ID 콤마 구분")

    p_handoff = subparsers.add_parser("handoff", help="다른 환경/에이전트로 넘길 검수 Run 생성")
    p_handoff.add_argument("--to", required=True, choices=sorted(HANDOFF_TARGETS), help="handoff 대상")
    p_handoff.add_argument("--title", required=True, help="handoff 목표")
    p_handoff.add_argument("--from-run", default="", help="이전 Run ID 또는 파일명")
    p_handoff.add_argument("--adapter", default="codex-gpt", help="Adapter 이름")
    p_handoff.add_argument("--gate", default="gate4", choices=list(GATE_LABELS.keys()), help="Gate 이름")
    p_handoff.add_argument("--persona", default="review", choices=sorted(RUN_PERSONAS.keys()), help="handoff persona")
    p_handoff.add_argument("--related-ids", default="", help="관련 ID 콤마 구분")

    p_review_request = subparsers.add_parser("review-request", help="독립 세션/워크트리 기반 검수 요청 생성")
    p_review_request.add_argument("--title", required=True, help="독립 검수 목표")
    p_review_request.add_argument("--gate", required=True, choices=list(GATE_LABELS.keys()), help="검수 대상 Gate")
    p_review_request.add_argument("--related-ids", default="", help="관련 ID 콤마 구분")
    p_review_request.add_argument("--from-run", default="", help="검수 대상 Run ID 또는 파일명")
    p_review_request.add_argument("--runner", choices=INDEPENDENT_REVIEW_RUNNERS, help="독립 검수 실행 런타임")
    p_review_request.add_argument("--worktree", dest="worktree", action="store_true", help="격리 worktree 생성")
    p_review_request.add_argument("--no-worktree", dest="worktree", action="store_false", help="worktree를 생성하지 않음")
    p_review_request.set_defaults(worktree=None)
    p_review_request.add_argument("--worktree-dir", default="", help="worktree 생성 경로")

    p_review_run = subparsers.add_parser("review-run", help="독립 검수 요청을 codex-cli 또는 claude-cli로 실행")
    p_review_run.add_argument("--review-id", required=True, help="실행할 리뷰 ID (예: RV-001)")
    p_review_run.add_argument("--runner", choices=INDEPENDENT_REVIEW_RUNNERS, help="독립 검수 실행 런타임")
    p_review_run.add_argument("--model", default="", help="runner 모델")
    p_review_run.add_argument("--reasoning-effort", default="", choices=["", "low", "medium", "high", "xhigh"], help="추론 강도")
    p_review_run.add_argument("--timeout-seconds", type=int, default=0, help="runner timeout seconds")
    p_review_run.add_argument("--sandbox", default="", choices=["", "read-only", "workspace-write", "danger-full-access"], help="codex-cli sandbox")
    p_review_run.add_argument("--dry-run", action="store_true", help="실행하지 않고 명령만 출력")

    backlog_sub = p_backlog.add_subparsers(dest="backlog_cmd")
    backlog_sub.add_parser("list", help="백로그 Active 항목 나열")
    bl_add = backlog_sub.add_parser("add", help="새 백로그 항목 추가")
    bl_add.add_argument("--title", required=True)
    bl_add.add_argument("--level", default="", help="🟢/🟡/🔴 (선택, 나중에 Triage)")
    bl_add.add_argument("--priority", default="P2", choices=["P0", "P1", "P2", "P3"])
    bl_add.add_argument("--req", default="")
    bl_add.add_argument("--source", default="")
    bl_add.add_argument("--note", default="")
    bl_add.add_argument("--type", dest="item_type", default="IDEA", choices=["IDEA", "FIND", "CR", "ISSUE", "DEBT"])
    bl_add.add_argument("--backlog-gate", dest="backlog_gate", default="phase0", help="다시 진행할 Gate 후보")
    bl_add.add_argument("--run", default="", help="관련 Run ID 또는 파일")
    bl_done = backlog_sub.add_parser("done", help="백로그 항목 완료 처리")
    bl_done.add_argument("--id", dest="bl_id", required=True)
    bl_done.add_argument("--commit", dest="commit_hash", default="")
    bl_rej = backlog_sub.add_parser("reject", help="백로그 항목 반려")
    bl_rej.add_argument("--id", dest="bl_id", required=True)
    bl_rej.add_argument("--reason", default="")

    p_export = subparsers.add_parser("export", help="snapshot.json 생성")
    p_export.add_argument("--output", default="snapshot.json", help="출력 파일명")

    subparsers.add_parser("upgrade", help="프레임워크 파일 최신화")
    subparsers.add_parser("version", help="현재 프레임워크 버전 확인")

    p_release = subparsers.add_parser("release", help="Vulcan-Anvil로 코드 배포")
    p_release.add_argument("--target", required=True, help="배포 대상 경로 (예: ../Vulcan-Anvil)")

    args = parser.parse_args()

    if args.command == "init":
        init(
            target_dir=os.path.abspath(args.target_dir),
            project_name=args.project_name,
            agent_name=args.agent_name,
            remote_url=args.remote or None,
            require_remote=args.require_remote,
            profile=args.profile,
        )
    elif args.command == "check-trace":
        check_trace()
    elif args.command == "check-architecture":
        cmd_check_architecture(level=args.level)
    elif args.command == "gate-start":
        cmd_gate_start(gate=args.gate, feature=args.feature)
    elif args.command == "session":
        cmd_session(gate=args.gate, status=args.status, feature=args.feature)
    elif args.command == "sync-session":
        cmd_sync_session()
    elif args.command == "wave-start":
        cmd_wave_start(bw_id=args.bw_id, title=args.title, related_ids=args.related_ids)
    elif args.command == "wave-complete":
        cmd_wave_complete(bw_id=args.bw_id, status=args.status, req_ids=args.req)
    elif args.command == "run-new":
        cmd_run_new(
            adapter=args.adapter,
            gate=args.gate,
            skill=args.skill,
            title=args.title,
            related_ids=args.related_ids,
            persona=args.persona or None,
        )
    elif args.command == "run-check":
        cmd_run_check(args.run_file)
    elif args.command == "orchestrator-plan":
        cmd_orchestrator_plan(
            goal=args.goal,
            gate=args.gate,
            related_ids=args.related_ids,
            persona=args.persona or None,
            adapter=args.adapter,
        )
    elif args.command == "handoff":
        cmd_handoff(
            target=args.to,
            title=args.title,
            from_run=args.from_run,
            gate=args.gate,
            related_ids=args.related_ids,
            persona=args.persona,
            adapter=args.adapter,
        )
    elif args.command == "review-request":
        cmd_review_request(
            title=args.title,
            gate=args.gate,
            related_ids=args.related_ids,
            from_run=args.from_run,
            runner=args.runner,
            create_worktree=args.worktree,
            worktree_dir=args.worktree_dir,
        )
    elif args.command == "review-run":
        cmd_review_run(
            review_id=args.review_id,
            runner=args.runner,
            model=args.model or None,
            reasoning_effort=args.reasoning_effort or None,
            timeout_seconds=args.timeout_seconds or None,
            sandbox=args.sandbox or None,
            dry_run=args.dry_run,
        )
    elif args.command == "backlog":
        if args.backlog_cmd == "list":
            cmd_backlog_list()
        elif args.backlog_cmd == "add":
            cmd_backlog_add(
                title=args.title, level=args.level, priority=args.priority,
                req=args.req, source=args.source, note=args.note,
                item_type=args.item_type, gate=args.backlog_gate, run=args.run,
            )
        elif args.backlog_cmd == "done":
            cmd_backlog_done(bl_id=args.bl_id, commit_hash=args.commit_hash)
        elif args.backlog_cmd == "reject":
            cmd_backlog_reject(bl_id=args.bl_id, reason=args.reason)
        else:
            p_backlog.print_help()
    elif args.command == "export":
        cmd_export(output=args.output)
    elif args.command == "upgrade":
        cmd_upgrade()
    elif args.command == "version":
        cmd_version()
    elif args.command == "release":
        cmd_release(target=args.target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

