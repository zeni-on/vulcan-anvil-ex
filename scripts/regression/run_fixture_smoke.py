#!/usr/bin/env python3
"""Fixture-based regression smoke harness for Vulcan-Anvil Ex.

The minimal audit smoke test checks a freshly initialized project. This script
adds a normalized completed-project fixture on top of a fresh init and verifies
that core document/check commands still accept the real artifact shape.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_FIXTURE = "simple-hello-audit"
DEFAULT_PRODUCT_FIXTURE = "simple-todo-product"

REPRESENTATIVE_RUNS = [
    "RUN-010_python-hello-api-implementation-plan_v0.1.md",
    "RUN-011_build-wave-BW-000_python-hello-api-scaffold-and-implementation_v0.1.md",
    "RUN-012_build-wave-BW-001_python-hello-api-feature-implementation_v0.1.md",
    "RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md",
    "RUN-015_qa-001-gate-4-command-validation-for-python-hello-api_v0.1.md",
    "RUN-016_qa-002-gate-4-ui-e2e-applicability-for-python-hello-api_v0.1.md",
    "RUN-017_qa-003-gate-4-result-summary-and-decision-candidate-for-python-hello-api_v0.1.md",
    "RUN-019_gate-5-release-approval-for-python-hello-api_v0.1.md",
]

PREFLIGHT_RUNS = [
    "RUN-011_build-wave-BW-000_python-hello-api-scaffold-and-implementation_v0.1.md",
    "RUN-012_build-wave-BW-001_python-hello-api-feature-implementation_v0.1.md",
]

QA_PREFLIGHT_RUNS = [
    "RUN-015_qa-001-gate-4-command-validation-for-python-hello-api_v0.1.md",
    "RUN-016_qa-002-gate-4-ui-e2e-applicability-for-python-hello-api_v0.1.md",
    "RUN-017_qa-003-gate-4-result-summary-and-decision-candidate-for-python-hello-api_v0.1.md",
]


@dataclass
class StepResult:
    name: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def combined_output(self) -> str:
        return "\n".join(part for part in [self.stdout, self.stderr] if part)


class FixtureSmokeFailure(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_step(
    name: str,
    args: list[str],
    cwd: Path,
    expected_returncodes: set[int] | None = None,
    required_text: list[str] | None = None,
    timeout_seconds: int = 120,
) -> StepResult:
    expected_returncodes = expected_returncodes or {0}
    required_text = required_text or []
    proc = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout_seconds,
    )
    result = StepResult(name=name, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    output = result.combined_output

    if proc.returncode not in expected_returncodes:
        raise FixtureSmokeFailure(
            f"{name} returned {proc.returncode}, expected {sorted(expected_returncodes)}\n"
            f"Command: {' '.join(args)}\n{output}"
        )

    missing = [text for text in required_text if text not in output]
    if missing:
        raise FixtureSmokeFailure(
            f"{name} did not include required text: {missing}\n"
            f"Command: {' '.join(args)}\n{output}"
        )

    return result


def copy_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    if src.exists():
        shutil.copytree(src, dst)


def apply_fixture(fixture_dir: Path, project_dir: Path) -> None:
    if not fixture_dir.exists():
        raise FixtureSmokeFailure(f"fixture not found: {fixture_dir}")

    for dirname in ["backend"]:
        copy_dir(fixture_dir / dirname, project_dir / dirname)

    for dirname in ["artifacts", "backlog", "runs", "reviews"]:
        copy_dir(fixture_dir / "docs" / dirname, project_dir / "docs" / dirname)

    shutil.copy2(fixture_dir / "session.fixture.json", project_dir / "session.json")
    shutil.copy2(fixture_dir / "vulcan.config.fixture.json", project_dir / "vulcan.config.json")


def apply_product_fixture(fixture_dir: Path, project_dir: Path) -> None:
    if not fixture_dir.exists():
        raise FixtureSmokeFailure(f"product fixture not found: {fixture_dir}")

    for dirname in ["app", "static", "tests"]:
        copy_dir(fixture_dir / dirname, project_dir / dirname)

    for dirname in ["product", "backlog", "runs"]:
        copy_dir(fixture_dir / "docs" / dirname, project_dir / "docs" / dirname)

    copy_dir(fixture_dir / "docs" / "artifacts" / "07-release", project_dir / "docs" / "artifacts" / "07-release")
    shutil.copy2(fixture_dir / "requirements.txt", project_dir / "requirements.txt")
    shutil.copy2(fixture_dir / "session.fixture.json", project_dir / "session.json")
    shutil.copy2(fixture_dir / "vulcan.config.fixture.json", project_dir / "vulcan.config.json")


def validate_fixture_inputs(project_dir: Path) -> None:
    missing = []
    for run_name in REPRESENTATIVE_RUNS + PREFLIGHT_RUNS + QA_PREFLIGHT_RUNS:
        path = project_dir / "docs" / "runs" / run_name
        if not path.exists():
            missing.append(str(path.relative_to(project_dir)))
    for path in [
        project_dir / "backend" / "app" / "services" / "hello_service.py",
        project_dir / "docs" / "artifacts" / "02-design" / "program" / "DOC-CORE-G2-002_Program-Design_v0.1.md",
    ]:
        if not path.exists():
            missing.append(str(path.relative_to(project_dir)))
    if missing:
        raise FixtureSmokeFailure("fixture missing required files:\n" + "\n".join(f"  - {item}" for item in missing))


def assert_qa000_doctor_evidence_policy(project_dir: Path) -> None:
    run_path = (
        project_dir
        / "docs"
        / "runs"
        / "RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md"
    )
    doctor_json_path = project_dir / "docs" / "artifacts" / "04-review" / "evidence" / "qa-000" / "QA-000-doctor.json"
    doctor_log_path = project_dir / "docs" / "artifacts" / "04-review" / "evidence" / "qa-000" / "QA-000-doctor.log"
    run_text = run_path.read_text(encoding="utf-8")
    required_text = [
        "python vulcan.py doctor --json",
        "QA-000-doctor.json",
        "qa000_doctor_evidence",
        "environment_blocked",
        "제품 결함",
    ]
    missing_text = [text for text in required_text if text not in run_text]
    if missing_text:
        raise FixtureSmokeFailure(f"QA-000 Run missing doctor evidence policy text: {missing_text}")
    if not doctor_json_path.exists():
        raise FixtureSmokeFailure(f"QA-000 fixture missing doctor JSON evidence: {doctor_json_path.relative_to(project_dir)}")
    if not doctor_log_path.exists():
        raise FixtureSmokeFailure(f"QA-000 fixture missing doctor log evidence: {doctor_log_path.relative_to(project_dir)}")
    try:
        payload = json.loads(doctor_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FixtureSmokeFailure(f"QA-000 doctor JSON evidence is invalid: {exc}") from exc
    summary = payload.get("summary") or {}
    checks = payload.get("checks") or []
    if "fail" not in summary or not isinstance(checks, list) or not checks:
        raise FixtureSmokeFailure(f"QA-000 doctor JSON evidence missing summary/checks: {payload}")


def validate_product_fixture_inputs(project_dir: Path) -> None:
    required = [
        "app/main.py",
        "static/index.html",
        "static/app.js",
        "tests/test_todos.py",
        "tests/test_ui_smoke.py",
        "requirements.txt",
        "docs/product/PRODUCT_BRIEF.md",
        "docs/product/PRODUCT_ARCHITECTURE.md",
        "docs/product/ADR_LOG.md",
        "docs/product/PRODUCT_CONTRACTS.md",
        "docs/product/PRODUCT_TRACEABILITY.md",
        "docs/product/REGRESSION_AND_RELEASE_REPORT.md",
        "docs/product/evidence/G4_status_check.log",
        "docs/product/evidence/G4_pytest.log",
        "docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md",
        "docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md",
        "docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md",
    ]
    missing = [rel for rel in required if not (project_dir / rel).exists()]
    if missing:
        raise FixtureSmokeFailure("product fixture missing required files:\n" + "\n".join(f"  - {item}" for item in missing))


def assert_trace_context_json(result: StepResult) -> None:
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise FixtureSmokeFailure(f"trace-context JSON output is invalid: {exc}\n{result.combined_output}") from exc

    related_ids = set(payload.get("related_ids") or [])
    target_contracts = payload.get("target_contracts") or {}
    nodes = payload.get("nodes") or {}
    expected_related = {"REQ-001-01", "API-001", "PGM-001", "SEC-001", "UT-001", "IT-001"}
    missing = sorted(expected_related - related_ids)
    if missing:
        raise FixtureSmokeFailure(f"trace-context JSON missing related IDs: {missing}")
    if "API-001" not in set(target_contracts.get("api") or []):
        raise FixtureSmokeFailure("trace-context JSON target_contracts.api did not include API-001")
    if "PGM-001" not in set(target_contracts.get("pgm") or []):
        raise FixtureSmokeFailure("trace-context JSON target_contracts.pgm did not include PGM-001")
    if not (nodes.get("API-001") or {}).get("label"):
        raise FixtureSmokeFailure("trace-context JSON nodes.API-001.label was empty")
    if not (nodes.get("PGM-001") or {}).get("label"):
        raise FixtureSmokeFailure("trace-context JSON nodes.PGM-001.label was empty")


def release_pr_body_path_from_output(output: str) -> Path:
    match = re.search(r"(?m)^\s*body:\s+(.+?)\s*$", output)
    if not match:
        raise FixtureSmokeFailure(f"release-pr output did not include body path\n{output}")
    return Path(match.group(1).strip())


def run_doc_path_from_output(project_dir: Path, output: str) -> Path:
    match = re.search(r"(?m)^\s*Run 문서:\s+(.+?)\s*$", output)
    if not match:
        match = re.search(r"(?m)^\s*Run 초안 생성 완료:\s+(.+?)\s*$", output)
    if not match:
        raise FixtureSmokeFailure(f"run generation output did not include Run path\n{output}")
    raw_path = match.group(1).strip()
    path = Path(raw_path)
    if not path.is_absolute():
        path = project_dir / path
    return path


def assert_trace_seed_generated_run(project_dir: Path, result: StepResult) -> None:
    run_path = run_doc_path_from_output(project_dir, result.combined_output)
    if not run_path.exists():
        raise FixtureSmokeFailure(f"trace-seed generated Run file was not found: {run_path}")
    content = run_path.read_text(encoding="utf-8")
    required = [
        "trace_context:",
        "seeds: [REQ-001-01]",
        "API-001",
        "PGM-001",
        "SEC-001",
        "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md",
    ]
    missing = [text for text in required if text not in content]
    if missing:
        raise FixtureSmokeFailure(f"trace-seed generated Run missing required text: {missing}\n{content[:2000]}")


def assert_poc_generated_run(project_dir: Path, result: StepResult) -> None:
    run_path = run_doc_path_from_output(project_dir, result.combined_output)
    if not run_path.exists():
        raise FixtureSmokeFailure(f"PoC generated Run file was not found: {run_path}")
    content = run_path.read_text(encoding="utf-8")
    required = [
        "profile: poc",
        "PoC 목표, 가설, 성공 기준",
        "python vulcan.py profile-status",
        "제품화/감리 전환",
        "docs/core/DELIVERY_PROFILES.md",
        "delegation_records",
    ]
    missing = [text for text in required if text not in content]
    if missing:
        raise FixtureSmokeFailure(f"PoC generated Run missing required text: {missing}\n{content[:2000]}")
    forbidden = [
        "worker_run_sizing_policy:",
        "docs/core/AGENT_RUN_PROTOCOL.md",
        "docs/core/RUN_INPUT_CONTRACT.md",
        "docs/core/RUN_OUTPUT_CONTRACT.md",
    ]
    present = [text for text in forbidden if text in content]
    if present:
        raise FixtureSmokeFailure(f"PoC generated Run should stay compact but included: {present}\n{content[:2000]}")


def assert_poc_trace_seed_generated_run(project_dir: Path, result: StepResult) -> None:
    run_path = run_doc_path_from_output(project_dir, result.combined_output)
    if not run_path.exists():
        raise FixtureSmokeFailure(f"PoC trace-seed generated Run file was not found: {run_path}")
    content = run_path.read_text(encoding="utf-8")
    required = [
        "profile: poc",
        "trace_context:",
        "seeds: [REQ-001-01]",
        "depth: 1",
        "API-001",
        "PGM-001",
        "delegation_records",
    ]
    missing = [text for text in required if text not in content]
    if missing:
        raise FixtureSmokeFailure(f"PoC trace-seed generated Run missing required text: {missing}\n{content[:2000]}")
    forbidden = [
        "worker_run_sizing_policy:",
        "docs/core/AGENT_RUN_PROTOCOL.md",
        "docs/core/RUN_INPUT_CONTRACT.md",
        "docs/core/RUN_OUTPUT_CONTRACT.md",
    ]
    present = [text for text in forbidden if text in content]
    if present:
        raise FixtureSmokeFailure(f"PoC trace-seed generated Run should stay compact but included: {present}\n{content[:2000]}")


def assert_release_pr_body(result: StepResult) -> None:
    body_path = release_pr_body_path_from_output(result.combined_output)
    normalized = body_path.as_posix()
    if "/.vulcan/release/release-pr-body.md" not in normalized and "\\.vulcan\\release\\release-pr-body.md" not in str(body_path):
        raise FixtureSmokeFailure(f"release-pr body path should be under .vulcan/release: {body_path}")
    if not body_path.exists():
        raise FixtureSmokeFailure(f"release-pr body file was not created: {body_path}")
    body = body_path.read_text(encoding="utf-8")
    required = [
        "## Gate 5 Evidence Documents",
        "- [OK] `docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md`",
        "- [OK] `docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md`",
        "- [OK] `docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md`",
        "Independent PR review completed or explicitly waived",
        "must not be auto-merged",
    ]
    missing = [text for text in required if text not in body]
    if missing:
        raise FixtureSmokeFailure(f"release-pr body missing required text: {missing}\n{body}")


def assert_product_completed_release_pr_body(result: StepResult) -> None:
    body_path = release_pr_body_path_from_output(result.combined_output)
    if not body_path.exists():
        raise FixtureSmokeFailure(f"Product release-pr body file was not created: {body_path}")
    body = body_path.read_text(encoding="utf-8")
    required = [
        "Profile: `product`",
        "- [OK] `docs/product/PRODUCT_BRIEF.md`",
        "- [OK] `docs/product/PRODUCT_CONTRACTS.md`",
        "- [OK] `docs/product/PRODUCT_TRACEABILITY.md`",
        "- [OK] `docs/product/REGRESSION_AND_RELEASE_REPORT.md`",
        "- [OK] `docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md`",
        "Product regression result and release scope reviewed",
    ]
    missing = [text for text in required if text not in body]
    if missing:
        raise FixtureSmokeFailure(f"Product completed release-pr body missing required text: {missing}\n{body}")
    forbidden = [
        "DOC-QA-G4-001_QA-Finding",
        "DOC-QA-G4-002_Test-Result",
        "DOC-CORE-G4-001_Traceability-Matrix",
    ]
    present = [text for text in forbidden if text in body]
    if present:
        raise FixtureSmokeFailure(f"Product completed release-pr body included audit-only evidence: {present}\n{body}")


def assert_product_completed_fixture_text(project_dir: Path) -> None:
    trace = (project_dir / "docs" / "product" / "PRODUCT_TRACEABILITY.md").read_text(encoding="utf-8")
    release = (project_dir / "docs" / "product" / "REGRESSION_AND_RELEASE_REPORT.md").read_text(encoding="utf-8")
    run = (
        project_dir
        / "docs"
        / "runs"
        / "RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
    ).read_text(encoding="utf-8")

    required_trace = ["SCN-001", "SCN-002", "SCN-003", "Verified", "REG-001", "REG-002"]
    missing_trace = [text for text in required_trace if text not in trace]
    if missing_trace:
        raise FixtureSmokeFailure(f"Product fixture traceability missing required text: {missing_trace}")

    required_release = ["REG-001", "REG-002", "Pass", "ISSUE-G4-001", "Conditional"]
    missing_release = [text for text in required_release if text not in release]
    if missing_release:
        raise FixtureSmokeFailure(f"Product fixture release report missing required text: {missing_release}")

    required_run = ["delegation_records", "status: Verified", "SCN-001", "SCN-002", "SCN-003"]
    missing_run = [text for text in required_run if text not in run]
    if missing_run:
        raise FixtureSmokeFailure(f"Product fixture Run missing required text: {missing_run}")


def assert_doctor_json(result: StepResult, project_dir: Path, expected_profile: str | None = None) -> None:
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise FixtureSmokeFailure(f"doctor JSON output is invalid: {exc}\n{result.combined_output}") from exc

    if Path(payload.get("project_dir") or "") != project_dir:
        raise FixtureSmokeFailure(f"doctor JSON project_dir mismatch: {payload.get('project_dir')} != {project_dir}")

    summary = payload.get("summary") or {}
    checks = payload.get("checks") or []
    if not isinstance(checks, list) or not checks:
        raise FixtureSmokeFailure(f"doctor JSON checks were empty\n{payload}")
    if int(summary.get("fail") or 0) != 0:
        raise FixtureSmokeFailure(f"doctor JSON reported failing environment checks\n{json.dumps(payload, ensure_ascii=False, indent=2)}")

    by_name = {check.get("name"): check for check in checks if isinstance(check, dict)}
    required_names = [
        "project_dir",
        "session.json",
        "vulcan.config.json",
        "python",
        "git",
        "node",
        "npm",
        "browser_cache",
        "npm_cache",
        "available_runners",
        "dashboard",
    ]
    missing_names = [name for name in required_names if name not in by_name]
    if missing_names:
        raise FixtureSmokeFailure(f"doctor JSON missing required checks: {missing_names}")

    for name in ["session.json", "vulcan.config.json", "python", "git"]:
        if by_name[name].get("status") != "pass":
            raise FixtureSmokeFailure(f"doctor JSON expected {name} to pass, got {by_name[name]}")

    if expected_profile:
        config_detail = by_name["vulcan.config.json"].get("detail") or ""
        if f"profile={expected_profile}" not in config_detail:
            raise FixtureSmokeFailure(f"doctor JSON did not report profile={expected_profile}: {config_detail}")


def assert_product_build_wave_related_ids(project_dir: Path, vulcan_py: Path) -> None:
    run_dir = project_dir / "docs" / "runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_path = run_dir / "RUN-001_build-wave-BW-001_product-scenario-smoke_v0.1.md"
    expected_ids = {"SCN-001", "REQ-001", "API-001", "API-002", "DATA-001", "UI-001", "REG-001"}
    run_path.write_text(
        """# Product Build Wave Smoke

```yaml
---
run_id: RUN-001
gate: impl
persona: build
skill: build-wave
bw_id: BW-001
status: Verified
related_ids: [SCN-001, REQ-001, API-001, API-002, DATA-001, UI-001, REG-001]
target_contracts:
  scenario: [SCN-001]
  req: [REQ-001]
  api: [API-001, API-002]
  data: [DATA-001]
  ui: [UI-001]
scope:
  writable:
    - "backend/"
    - "frontend/"
    - "static/"
    - "tests/"
---
```

| BW ID | Scope | Status | Related IDs |
| --- | --- | --- | --- |
| BW-001 | Product SCN-001 add/list | Verified | SCN-001, REQ-001, API-001, API-002, DATA-001, UI-001, REG-001 |
""",
        encoding="utf-8",
    )

    import importlib.util

    vulcan_root = str(vulcan_py.parent)
    if vulcan_root not in sys.path:
        sys.path.insert(0, vulcan_root)
    spec = importlib.util.spec_from_file_location("vulcan_product_wave_smoke", vulcan_py)
    if spec is None or spec.loader is None:
        raise FixtureSmokeFailure(f"could not import vulcan.py from {vulcan_py}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = module.collect_build_wave_records(str(project_dir))
    matching = [record for record in records if record.get("id") == "BW-001"]
    if not matching:
        raise FixtureSmokeFailure("Product Build Wave smoke did not find BW-001 record")
    actual_ids = set(matching[0].get("related_ids") or [])
    missing = sorted(expected_ids - actual_ids)
    if missing:
        raise FixtureSmokeFailure(
            f"Product Build Wave related IDs were not preserved: missing {missing}, actual {sorted(actual_ids)}"
        )

    inferred_role = module.infer_execution_role(
        run_path.read_text(encoding="utf-8"),
        {
            "run_id": "RUN-001",
            "persona": "build",
            "skill": "build-wave",
            "title": "Product scenario smoke",
            "bw_id": "BW-001",
        },
    )
    if inferred_role != "build":
        raise FixtureSmokeFailure(
            "Product full-stack Build Wave should infer generic build role, "
            f"got {inferred_role}"
        )


def assert_product_adr_template_policy(project_dir: Path) -> None:
    adr_path = project_dir / "docs" / "product" / "ADR_LOG.md"
    if not adr_path.exists():
        raise FixtureSmokeFailure(f"Product ADR log was not generated: {adr_path}")
    content = adr_path.read_text(encoding="utf-8")
    required = [
        "ADR-NONE",
        "현재 기록된 ADR 없음",
        "ADR-001",
        "첫 실제 의사결정",
    ]
    missing = [text for text in required if text not in content]
    if missing:
        raise FixtureSmokeFailure(f"Product ADR log missing no-decision policy text: {missing}\n{content[:2000]}")
    forbidden_patterns = [
        r"\|\s*ADR-001\s*\|\s*TBD\b",
        r"\|\s*Context\s*\|\s*TBD\s*\|",
        r"\|\s*Decision\s*\|\s*TBD\s*\|",
    ]
    matched = [pattern for pattern in forbidden_patterns if re.search(pattern, content, re.IGNORECASE)]
    if matched:
        raise FixtureSmokeFailure(f"Product ADR log still contains placeholder ADR content: {matched}\n{content[:2000]}")


def assert_product_gate4_blocks_planned_regression(project_dir: Path, vulcan_py: Path, py: str) -> None:
    script = (
        "import importlib.util, json; "
        f"spec=importlib.util.spec_from_file_location('v', r'{vulcan_py}'); "
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
        f"issues,warnings=m.collect_product_profile_findings(r'{project_dir}', gate='gate4'); "
        "print(json.dumps({'issues': issues, 'warnings': warnings}, ensure_ascii=False))"
    )
    completed = subprocess.run(
        [py, "-c", script],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=60,
    )
    if completed.returncode != 0:
        raise FixtureSmokeFailure(
            "Product Gate4 planned regression smoke failed to execute\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        raise FixtureSmokeFailure(f"could not parse Product Gate4 planned regression smoke output: {completed.stdout}") from exc
    issues = payload.get("issues") or []
    expected = "Planned/TBD 회귀 실행 결과"
    if not any(expected in issue for issue in issues):
        raise FixtureSmokeFailure(
            "Product Gate4 should block planned regression execution results, "
            f"but did not find '{expected}' in issues: {issues}"
        )


def assert_codex_model_policy_fallback(vulcan_py: Path, py: str) -> StepResult:
    script = (
        "import importlib.util, json; "
        f"spec=importlib.util.spec_from_file_location('v', r'{vulcan_py}'); "
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
        "config=m.default_vulcan_config(profile='product', primary='codex-cli'); "
        "config['runtime']['model_policy']['codex-cli']['roles']['build']['model']='gpt-5.3-codex'; "
        "policy_model, policy_effort, policy_resolution=m.resolve_codex_model_effort(config, 'build'); "
        "explicit_model, explicit_effort, explicit_resolution=m.resolve_codex_model_effort("
        "config, 'build', explicit_model='gpt-5.3-codex', explicit_effort='medium'); "
        "print(json.dumps({"
        "'policy': {'model': policy_model, 'effort': policy_effort, 'resolution': policy_resolution}, "
        "'explicit': {'model': explicit_model, 'effort': explicit_effort, 'resolution': explicit_resolution}"
        "}, ensure_ascii=False))"
    )
    completed = subprocess.run(
        [py, "-c", script],
        cwd=vulcan_py.parent,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=60,
    )
    if completed.returncode != 0:
        raise FixtureSmokeFailure(
            "Codex model policy fallback smoke failed to execute\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        raise FixtureSmokeFailure(f"could not parse Codex model fallback smoke output: {completed.stdout}") from exc

    for bucket in ["policy", "explicit"]:
        item = payload.get(bucket) or {}
        resolution = item.get("resolution") or {}
        if item.get("model") != "gpt-5.5":
            raise FixtureSmokeFailure(f"{bucket} fallback expected gpt-5.5, got {item}")
        if "compat-fallback:gpt-5.3-codex" not in (resolution.get("model_source") or ""):
            raise FixtureSmokeFailure(f"{bucket} fallback did not record compat fallback source: {item}")
        if not resolution.get("model_fallback_reason"):
            raise FixtureSmokeFailure(f"{bucket} fallback did not record fallback reason: {item}")
    if payload["explicit"].get("effort") != "medium":
        raise FixtureSmokeFailure(f"explicit effort should remain cli-argument medium: {payload['explicit']}")

    return StepResult(
        name="codex-model-policy-fallback",
        returncode=0,
        stdout=json.dumps(payload, ensure_ascii=False),
        stderr="",
    )


def assert_status_model_fallback_summary(project_dir: Path, py: str) -> StepResult:
    exec_dir = project_dir / "docs" / "runs" / "_exec"
    exec_dir.mkdir(parents=True, exist_ok=True)
    (exec_dir / "RUN-999_codex-summary.json").write_text(
        json.dumps(
            {
                "run_id": "RUN-999",
                "target_id": "RUN-999",
                "runner": "codex-cli",
                "status": "completed",
                "model": "gpt-5.5",
                "reasoning_effort": "high",
                "model_source": "codex-model-policy:build|compat-fallback:gpt-5.3-codex",
                "model_fallback_reason": "gpt-5.3-codex is not supported; using gpt-5.5",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    result = run_step(
        "status-json-model-fallback-summary",
        [py, "vulcan.py", "status", "--json"],
        cwd=project_dir,
        timeout_seconds=60,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise FixtureSmokeFailure(f"status --json output is invalid: {exc}\n{result.combined_output}") from exc

    fallbacks = payload.get("model_fallbacks") or []
    if not any(
        item.get("target_id") == "RUN-999"
        and item.get("model") == "gpt-5.5"
        and "compat-fallback:gpt-5.3-codex" in (item.get("model_source") or "")
        and item.get("model_fallback_reason")
        for item in fallbacks
    ):
        raise FixtureSmokeFailure(f"status --json did not report model fallback summary: {fallbacks}")
    return result


def assert_status_json_check(project_dir: Path, py: str) -> StepResult:
    result = run_step(
        "status-json-check",
        [py, "vulcan.py", "status", "--json", "--check"],
        cwd=project_dir,
        timeout_seconds=90,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise FixtureSmokeFailure(f"status --json --check output is invalid: {exc}\n{result.combined_output}") from exc

    transition = payload.get("transition_check") or {}
    if transition.get("command") != "python vulcan.py prepare-transition":
        raise FixtureSmokeFailure(f"status --json --check did not include prepare-transition command: {transition}")
    if transition.get("status") != "pass" or transition.get("exit_code") != 0:
        raise FixtureSmokeFailure(f"status --json --check should pass for completed fixture: {transition}")
    if not any("prepare-transition" in line for line in transition.get("stdout_lines") or []):
        raise FixtureSmokeFailure("status --json --check did not capture prepare-transition output")
    return result


def assert_execute_json_plan(project_dir: Path, py: str) -> StepResult:
    result = run_step(
        "execute-dry-run-json",
        [
            py,
            "vulcan.py",
            "execute",
            "--run-id",
            "RUN-011",
            "--runner",
            "native",
            "--dry-run",
            "--json",
        ],
        cwd=project_dir,
        timeout_seconds=90,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise FixtureSmokeFailure(f"execute --dry-run --json output is invalid: {exc}\n{result.combined_output}") from exc

    if payload.get("run_id") != "RUN-011":
        raise FixtureSmokeFailure(f"execute JSON run_id mismatch: {payload.get('run_id')}")
    if payload.get("runner_mode") != "native-delegation":
        raise FixtureSmokeFailure(f"execute JSON runner_mode mismatch: {payload.get('runner_mode')}")
    sidecar = payload.get("delegation_sidecar") or {}
    if sidecar.get("path") != ".vulcan/delegations/RUN-011.json":
        raise FixtureSmokeFailure(f"execute JSON sidecar candidate mismatch: {sidecar}")
    if sidecar.get("status") != "delegated":
        raise FixtureSmokeFailure(f"execute JSON sidecar candidate should start delegated: {sidecar}")
    if not any("run-preflight" in item for item in payload.get("planned_flow") or []):
        raise FixtureSmokeFailure(f"execute JSON planned_flow missing run-preflight: {payload.get('planned_flow')}")
    if not isinstance((payload.get("scope") or {}).get("writable"), list):
        raise FixtureSmokeFailure(f"execute JSON scope.writable should be a list: {payload.get('scope')}")
    return result


def assert_product_multi_scenario_seed_expansion(project_dir: Path, vulcan_py: Path, py: str) -> None:
    product_dir = project_dir / "docs" / "product"
    product_dir.mkdir(parents=True, exist_ok=True)
    (product_dir / "PRODUCT_BRIEF.md").write_text(
        """# Product Brief

## Core Scenarios

| Scenario ID | 시나리오 | 사용자 가치 | 우선순위 | 관련 REQ |
| --- | --- | --- | --- | --- |
| SCN-001 | Add Todo | record item | Must | REQ-001 |
| SCN-002 | Toggle Todo | update state | Must | REQ-002 |
| SCN-003 | Delete Todo | remove item | Should | REQ-003 |

## Release Scope

| 구분 | 내용 |
| --- | --- |
| 이번 릴리즈 포함 | SCN-001, SCN-002, SCN-003 |
""",
        encoding="utf-8",
    )
    (product_dir / "PRODUCT_CONTRACTS.md").write_text(
        """# Product Contracts

## API Contracts

| API ID | Method | Path / Entry | Request | Response | 관련 Scenario | 상세 문서 |
| --- | --- | --- | --- | --- | --- | --- |
| API-001 | GET | /api/todos | none | data | SCN-001, SCN-002, SCN-003 | this |
| API-002 | POST | /api/todos | text | Todo | SCN-001 | this |
| API-003 | PATCH | /api/todos/{todoId} | completed | Todo | SCN-002 | this |
| API-004 | DELETE | /api/todos/{todoId} | none | deleted | SCN-003 | this |

## Data Contracts

| DATA/DB ID | 이름 | 주요 필드 | 보안 분류 | 관련 API/Scenario | 상세 문서 |
| --- | --- | --- | --- | --- | --- |
| DATA-001 | Todo | id,text,completed | 일반 | API-001, API-002, API-003, API-004, SCN-001, SCN-002, SCN-003 | this |

## UI Contracts

| UI/SCR ID | 화면/상호작용 | 주요 상태 | 관련 Scenario | 검증 |
| --- | --- | --- | --- | --- |
| UI-001 | Todo screen | Empty/List/Error | SCN-001, SCN-002, SCN-003 | REG-001 |
""",
        encoding="utf-8",
    )
    (product_dir / "PRODUCT_TRACEABILITY.md").write_text(
        """# Product Traceability

| Scenario ID | 관련 REQ | 시나리오 | Contract | Implementation | Regression | Release Evidence | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-001 | REQ-001 | Add Todo | API-001, API-002, DATA-001, UI-001 | TBD | REG-001, REG-002 | EV-001 | Planned |
| SCN-002 | REQ-002 | Toggle Todo | API-001, API-003, DATA-001, UI-001 | TBD | REG-001, REG-002 | EV-002 | Planned |
| SCN-003 | REQ-003 | Delete Todo | API-001, API-004, DATA-001, UI-001 | TBD | REG-001, REG-002 | EV-003 | Planned |
""",
        encoding="utf-8",
    )
    (product_dir / "REGRESSION_AND_RELEASE_REPORT.md").write_text(
        """# Regression And Release Report

| REG ID | 검증 대상 | 명령/방법 | 성공 기준 | 관련 Scenario |
| --- | --- | --- | --- | --- |
| REG-001 | API CRUD | pytest | pass | SCN-001, SCN-002, SCN-003 |
| REG-002 | UI smoke | browser | pass | SCN-001, SCN-002, SCN-003 |
""",
        encoding="utf-8",
    )

    script = (
        "import importlib.util, json; "
        f"spec=importlib.util.spec_from_file_location('v', r'{vulcan_py}'); "
        "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
        f"ids=m.product_related_ids_for_seeds(r'{project_dir}', ['SCN-001'], ['SCN-001']); "
        "print(json.dumps(ids, ensure_ascii=False))"
    )
    completed = subprocess.run(
        [py, "-c", script],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=60,
    )
    if completed.returncode != 0:
        raise FixtureSmokeFailure(
            "Product multi-scenario seed expansion smoke failed to execute\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        actual_ids = set(json.loads(completed.stdout.strip().splitlines()[-1]))
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        raise FixtureSmokeFailure(f"could not parse Product multi-scenario expansion output: {completed.stdout}") from exc
    expected_ids = {
        "SCN-001",
        "SCN-002",
        "SCN-003",
        "REQ-001",
        "REQ-002",
        "REQ-003",
        "API-001",
        "API-002",
        "API-003",
        "API-004",
        "DATA-001",
        "UI-001",
        "REG-001",
        "REG-002",
        "EV-001",
        "EV-002",
        "EV-003",
    }
    missing = sorted(expected_ids - actual_ids)
    if missing:
        raise FixtureSmokeFailure(
            "Product multi-scenario seed expansion missed related IDs: "
            f"missing {missing}, actual {sorted(actual_ids)}"
        )


def assert_gitignore_evidence_policy(project_dir: Path, py: str, steps: list[StepResult]) -> None:
    official_log = project_dir / "docs" / "artifacts" / "04-review" / "evidence" / "logs" / "QA-CMD-999_fixture.log"
    official_log.parent.mkdir(parents=True, exist_ok=True)
    official_log.write_text("fixture official QA log\n", encoding="utf-8")
    steps.append(
        run_step(
            "gitignore-allows-official-qa-log",
            ["git", "check-ignore", str(official_log.relative_to(project_dir))],
            cwd=project_dir,
            expected_returncodes={1},
        )
    )

    playwright_report = project_dir / "playwright-report" / "index.html"
    playwright_report.parent.mkdir(parents=True, exist_ok=True)
    playwright_report.write_text("<!doctype html><title>debug report</title>\n", encoding="utf-8")
    steps.append(
        run_step(
            "gitignore-ignores-playwright-report",
            ["git", "check-ignore", str(playwright_report.relative_to(project_dir))],
            cwd=project_dir,
            required_text=["playwright-report", "index.html"],
        )
    )

    test_result = project_dir / "test-results" / "fixture.txt"
    test_result.parent.mkdir(parents=True, exist_ok=True)
    test_result.write_text("debug artifact\n", encoding="utf-8")
    steps.append(
        run_step(
            "gitignore-ignores-test-results",
            ["git", "check-ignore", str(test_result.relative_to(project_dir))],
            cwd=project_dir,
            required_text=["test-results", "fixture.txt"],
        )
    )


def write_bad_native_delegation_run(project_dir: Path, source_run_name: str, target_run_name: str) -> Path:
    source = project_dir / "docs" / "runs" / source_run_name
    target = project_dir / "docs" / "runs" / target_run_name
    content = source.read_text(encoding="utf-8")
    content = re.sub(r"run_id:\s*RUN-\d+", "run_id: RUN-999", content, count=1)
    content += (
        "\n\n## Native Delegation Regression Fixture\n\n"
        "Agy Workspace: branch worker completed this Run, but this fixture intentionally "
        "omits delegation_records so run-check/run-preflight must block it.\n"
    )
    target.write_text(content, encoding="utf-8")
    return target


def assert_native_delegation_guardrails(project_dir: Path, py: str, steps: list[StepResult]) -> None:
    bad_build_run = write_bad_native_delegation_run(
        project_dir,
        "RUN-012_build-wave-BW-001_python-hello-api-feature-implementation_v0.1.md",
        "RUN-999_native-delegation-missing-records-build_v0.1.md",
    )
    build_arg = str(bad_build_run.relative_to(project_dir))
    steps.append(
        run_step(
            "run-check-blocks-native-build-without-delegation-records",
            [py, "vulcan.py", "run-check", build_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=["native/Agy worker 사용 흔적", "delegation_records"],
        )
    )
    steps.append(
        run_step(
            "run-preflight-blocks-native-build-without-delegation-records",
            [py, "vulcan.py", "run-preflight", build_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=["native/Agy worker 사용 흔적", "delegation_records"],
        )
    )

    bad_qa_run = write_bad_native_delegation_run(
        project_dir,
        "RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md",
        "RUN-998_native-delegation-missing-records-qa_v0.1.md",
    )
    qa_arg = str(bad_qa_run.relative_to(project_dir))
    steps.append(
        run_step(
            "run-check-blocks-native-qa-without-delegation-records",
            [py, "vulcan.py", "run-check", qa_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=["native/Agy", "delegation_records"],
        )
    )
    steps.append(
        run_step(
            "run-preflight-blocks-native-qa-without-delegation-records",
            [py, "vulcan.py", "run-preflight", qa_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=["native/Agy", "delegation_records"],
        )
    )


def write_mismatched_run_input_contract_run(project_dir: Path) -> Path:
    source = project_dir / "docs" / "runs" / "RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md"
    target = project_dir / "docs" / "runs" / "RUN-997_run-input-contract-metadata-mismatch_v0.1.md"
    content = source.read_text(encoding="utf-8")

    def replace_contract(match: re.Match[str]) -> str:
        prefix, block, suffix = match.groups()
        block = re.sub(r'(?m)^gate:\s*["\']?gate4["\']?\s*$', 'gate: "gate1"', block, count=1)
        block = re.sub(r'(?m)^run_type:\s*["\']?Evidence["\']?\s*$', 'run_type: "Requirements"', block, count=1)
        return f"{prefix}{block}{suffix}"

    content = re.sub(
        r"(?s)(##\s*3\.\s*Run\s+입력\s+계약.*?```yaml\s*\n)(.*?)(```)",
        replace_contract,
        content,
        count=1,
    )
    content += (
        "\n\n## Run Input Contract Metadata Regression Fixture\n\n"
        "This fixture intentionally leaves the top metadata as gate4/Evidence while changing "
        "the embedded Run input contract to gate1/Requirements. run-check and run-preflight "
        "must block this mismatch.\n"
    )
    target.write_text(content, encoding="utf-8")
    return target


def assert_run_input_contract_metadata_guardrails(project_dir: Path, py: str, steps: list[StepResult]) -> None:
    mismatched_run = write_mismatched_run_input_contract_run(project_dir)
    run_arg = str(mismatched_run.relative_to(project_dir))
    required_text = [
        "Run 상단 metadata와 3. Run 입력 계약의 gate 값이 다릅니다",
        "Run 상단 metadata와 3. Run 입력 계약의 run_type 값이 다릅니다",
    ]
    steps.append(
        run_step(
            "run-check-blocks-run-input-contract-metadata-mismatch",
            [py, "vulcan.py", "run-check", run_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=required_text,
        )
    )
    steps.append(
        run_step(
            "run-preflight-blocks-run-input-contract-metadata-mismatch",
            [py, "vulcan.py", "run-preflight", run_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=required_text,
        )
    )


def write_mutating_qa_execution_run(project_dir: Path) -> Path:
    source = project_dir / "docs" / "runs" / "RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md"
    target = project_dir / "docs" / "runs" / "RUN-996_qa-execution-source-mutation-pollution_v0.1.md"
    content = source.read_text(encoding="utf-8")
    content = re.sub(r"run_id:\s*RUN-\d+", "run_id: RUN-996", content, count=1)
    content = content.replace(
        '    - "docs/artifacts/04-review/evidence/"',
        '    - "docs/artifacts/04-review/evidence/"\n    - "backend/app/main.py"',
        1,
    )
    content += (
        "\n\n## QA Worker Mutation Pollution Regression Fixture\n\n"
        "QA worker instruction: modify backend/app/main.py and add a new API method while collecting QA evidence.\n"
        "run-check and run-preflight must block this and require a separate approved qa-fix-loop or CR candidate.\n"
    )
    target.write_text(content, encoding="utf-8")
    return target


def assert_qa_execution_mutation_guardrails(project_dir: Path, py: str, steps: list[StepResult]) -> None:
    bad_qa_run = write_mutating_qa_execution_run(project_dir)
    run_arg = str(bad_qa_run.relative_to(project_dir))
    required_text = [
        "qa-execution Run writable scope에는 소스코드 경로를 포함하지 않습니다",
        "qa-execution Run이 소스 수정 지시처럼 보입니다",
        "qa-fix-loop",
    ]
    steps.append(
        run_step(
            "run-check-blocks-qa-execution-source-mutation",
            [py, "vulcan.py", "run-check", run_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=required_text,
        )
    )
    steps.append(
        run_step(
            "run-preflight-blocks-qa-execution-source-mutation",
            [py, "vulcan.py", "run-preflight", run_arg],
            cwd=project_dir,
            expected_returncodes={1},
            required_text=required_text,
        )
    )


def assert_run_integrate_config_hotfix_candidate(project_dir: Path, py: str, steps: list[StepResult]) -> None:
    session_path = project_dir / "session.json"
    session_before = json.loads(session_path.read_text(encoding="utf-8"))
    session_for_integrate = json.loads(json.dumps(session_before))
    session_for_integrate["current_gate"] = "impl"
    session_path.write_text(
        json.dumps(session_for_integrate, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    worker_dir = project_dir.parent / "config-hotfix-worker"
    try:
        steps.append(
            run_step(
                "worktree-add-config-hotfix-worker",
                ["git", "worktree", "add", "-b", "codex/config-hotfix-fixture", str(worker_dir), "HEAD"],
                cwd=project_dir,
            )
        )
        (worker_dir / "playwright.config.ts").write_text(
            "export default { testDir: './frontend/e2e' };\n",
            encoding="utf-8",
        )
        steps.append(
            run_step(
                "run-integrate-detects-config-hotfix-candidate",
                [
                    py,
                    "vulcan.py",
                    "run-integrate",
                    "--run-id",
                    "RUN-012",
                    "--worktree-dir",
                    str(worker_dir),
                    "--dry-run",
                ],
                cwd=project_dir,
                required_text=[
                    "blocked_scope_violation",
                    "config_hotfix_candidates",
                    "playwright.config.ts",
                    "required_decision",
                    "accept_config_hotfix",
                    "do not revert automatically",
                ],
            )
        )
    finally:
        session_path.write_text(
            json.dumps(session_before, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if worker_dir.exists():
            steps.append(
                run_step(
                    "worktree-remove-config-hotfix-worker",
                    ["git", "worktree", "remove", "--force", str(worker_dir)],
                    cwd=project_dir,
                    expected_returncodes={0, 1},
                )
            )


def run_fixture_smoke(args: argparse.Namespace) -> int:
    root = repo_root()
    fixture_dir = root / "scripts" / "regression" / "fixtures" / args.fixture
    product_fixture_dir = root / "scripts" / "regression" / "fixtures" / args.product_fixture
    vulcan_py = root / "vulcan.py"
    if not vulcan_py.exists():
        raise FixtureSmokeFailure(f"vulcan.py not found at {vulcan_py}")

    temp_ctx: tempfile.TemporaryDirectory[str] | None = None
    if args.output_dir:
        base_dir = Path(args.output_dir).resolve()
        if base_dir.exists() and any(base_dir.iterdir()):
            raise FixtureSmokeFailure(f"output directory must be empty: {base_dir}")
        base_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_ctx = tempfile.TemporaryDirectory(prefix="vulcan-fixture-smoke-")
        base_dir = Path(temp_ctx.name)

    project_dir = base_dir / "regression-simple-hello"
    profile_solution_dir = base_dir / "profile-solution-smoke"
    profile_product_dir = base_dir / "profile-product-smoke"
    profile_product_completed_dir = base_dir / "profile-product-completed-fixture-smoke"
    profile_poc_dir = base_dir / "profile-poc-smoke"
    py = sys.executable
    steps: list[StepResult] = []

    try:
        steps.append(assert_codex_model_policy_fallback(vulcan_py, py))
        steps.append(
            run_step(
                "init-profile-solution",
                [py, str(vulcan_py), "init", str(profile_solution_dir), "profile-solution-smoke", "--profile", "solution"],
                cwd=root,
                timeout_seconds=args.timeout_seconds,
            )
        )
        steps.append(
            run_step(
                "profile-status-solution",
                [py, "vulcan.py", "profile-status"],
                cwd=profile_solution_dir,
                required_text=[
                    "effective_profile: product",
                    "run_preflight_strictness: scope-contract-blocking-other-warning",
                ],
            )
        )
        steps.append(
            run_step(
                "init-profile-product",
                [py, str(vulcan_py), "init", str(profile_product_dir), "profile-product-smoke", "--profile", "product"],
                cwd=root,
                timeout_seconds=args.timeout_seconds,
            )
        )
        steps.append(assert_status_model_fallback_summary(profile_product_dir, py))
        assert_product_adr_template_policy(profile_product_dir)
        steps.append(
            StepResult(
                name="product-adr-template-policy",
                returncode=0,
                stdout="Product ADR template uses ADR-NONE instead of placeholder ADR-001",
                stderr="",
            )
        )
        assert_product_gate4_blocks_planned_regression(profile_product_dir, vulcan_py, py)
        steps.append(
            StepResult(
                name="product-gate4-blocks-planned-regression",
                returncode=0,
                stdout="Product Gate4 blocks Planned/TBD regression execution results",
                stderr="",
            )
        )
        assert_product_multi_scenario_seed_expansion(profile_product_dir, vulcan_py, py)
        steps.append(
            StepResult(
                name="product-multi-scenario-seed-expansion",
                returncode=0,
                stdout="Product SCN-001 seed expands to sibling scenarios and their contracts",
                stderr="",
            )
        )
        release_dir = profile_product_dir / "docs" / "artifacts" / "07-release"
        release_dir.mkdir(parents=True, exist_ok=True)
        (release_dir / "DOC-PM-G5-001_Release-Approval_v0.1.md").write_text(
            "# 릴리즈 승인서\n\nProduct release smoke approval.\n",
            encoding="utf-8",
        )
        product_release_body = run_step(
            "product-release-body-profile-aware",
            [
                py,
                "-c",
                (
                    "import importlib.util, pathlib; "
                    f"spec=importlib.util.spec_from_file_location('v', r'{vulcan_py}'); "
                    "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
                    f"print(m.release_pr_body(r'{profile_product_dir}', 'main', 'dev', 'Product smoke release'))"
                ),
            ],
            cwd=root,
            required_text=[
                "Profile: `product`",
                "docs/product/PRODUCT_TRACEABILITY.md",
                "docs/product/REGRESSION_AND_RELEASE_REPORT.md",
                "docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md",
            ],
            timeout_seconds=args.timeout_seconds,
        )
        if "DOC-QA-G4-001_QA-Finding" in product_release_body.combined_output or "DOC-QA-G4-002_Test-Result" in product_release_body.combined_output:
            raise FixtureSmokeFailure("Product release body included audit QA artifact requirements")
        steps.append(product_release_body)
        assert_product_build_wave_related_ids(profile_product_dir, vulcan_py)
        steps.append(
            StepResult(
                name="product-build-wave-related-ids",
                returncode=0,
                stdout="Product Build Wave related IDs preserved",
                stderr="",
            )
        )
        steps.append(
            run_step(
                "init-profile-product-completed-fixture",
                [
                    py,
                    str(vulcan_py),
                    "init",
                    str(profile_product_completed_dir),
                    "profile-product-completed-fixture-smoke",
                    "--profile",
                    "product",
                ],
                cwd=root,
                timeout_seconds=args.timeout_seconds,
            )
        )
        apply_product_fixture(product_fixture_dir, profile_product_completed_dir)
        validate_product_fixture_inputs(profile_product_completed_dir)
        assert_product_completed_fixture_text(profile_product_completed_dir)
        steps.append(
            StepResult(
                name="product-completed-fixture-files",
                returncode=0,
                stdout="Product completed fixture files and trace text validated",
                stderr="",
            )
        )
        steps.append(
            run_step(
                "product-completed-fixture:compileall",
                [py, "-m", "compileall", "app"],
                cwd=profile_product_completed_dir,
                timeout_seconds=args.timeout_seconds,
            )
        )
        steps.append(
            run_step(
                "product-completed-fixture:configure-git-user-email",
                ["git", "config", "user.email", "vulcan-regression@example.invalid"],
                cwd=profile_product_completed_dir,
            )
        )
        steps.append(
            run_step(
                "product-completed-fixture:configure-git-user-name",
                ["git", "config", "user.name", "Vulcan Regression"],
                cwd=profile_product_completed_dir,
            )
        )
        steps.append(run_step("product-completed-fixture:add", ["git", "add", "-A"], cwd=profile_product_completed_dir))
        steps.append(
            run_step(
                "product-completed-fixture:commit",
                ["git", "commit", "-m", "test: apply completed product fixture"],
                cwd=profile_product_completed_dir,
            )
        )
        steps.append(run_step("product-completed-fixture:checkout-dev", ["git", "checkout", "-B", "dev"], cwd=profile_product_completed_dir))
        product_doctor_json = run_step(
            "product-completed-fixture:doctor-json",
            [py, "vulcan.py", "doctor", "--json"],
            cwd=profile_product_completed_dir,
        )
        assert_doctor_json(product_doctor_json, profile_product_completed_dir, expected_profile="product")
        steps.append(product_doctor_json)
        steps.append(
            run_step(
                "product-completed-fixture:status-check",
                [py, "vulcan.py", "status", "--check"],
                cwd=profile_product_completed_dir,
                required_text=[
                    "현재 프로젝트는 모든 Gate를 마쳤습니다",
                    "Completed",
                ],
            )
        )
        completed_release_pr = run_step(
            "product-completed-fixture:release-pr-dry-run",
            [py, "vulcan.py", "release-pr", "--dry-run"],
            cwd=profile_product_completed_dir,
            required_text=[
                "Profile: `product`",
                "docs/product/PRODUCT_TRACEABILITY.md",
                "docs/product/REGRESSION_AND_RELEASE_REPORT.md",
            ],
        )
        assert_product_completed_release_pr_body(completed_release_pr)
        steps.append(completed_release_pr)
        steps.append(
            run_step(
                "init-profile-poc",
                [py, str(vulcan_py), "init", str(profile_poc_dir), "profile-poc-smoke", "--profile", "poc"],
                cwd=root,
                timeout_seconds=args.timeout_seconds,
            )
        )
        steps.append(
            run_step(
                "profile-status-poc",
                [py, "vulcan.py", "profile-status"],
                cwd=profile_poc_dir,
                required_text=[
                    "effective_profile: poc",
                    "run_preflight_strictness: warning-first",
                ],
            )
        )
        poc_run_new = run_step(
            "run-new-profile-poc",
            [
                py,
                "vulcan.py",
                "run-new",
                "--gate",
                "phase0",
                "--skill",
                "orchestrator-plan",
                "--title",
                "PoC Hypothesis Smoke",
                "--related-ids",
                "POC-001",
            ],
            cwd=profile_poc_dir,
            required_text=["Run 초안 생성 완료"],
        )
        assert_poc_generated_run(profile_poc_dir, poc_run_new)
        steps.append(poc_run_new)
        steps.append(
            run_step(
                "init",
                [py, str(vulcan_py), "init", str(project_dir), "regression-simple-hello"],
                cwd=root,
                timeout_seconds=args.timeout_seconds,
            )
        )
        steps.append(
            run_step(
                "profile-status-audit",
                [py, "vulcan.py", "profile-status"],
                cwd=project_dir,
                required_text=[
                    "effective_profile: audit",
                    "run_preflight_strictness: blocking",
                ],
            )
        )
        apply_fixture(fixture_dir, project_dir)
        validate_fixture_inputs(project_dir)
        assert_qa000_doctor_evidence_policy(project_dir)
        steps.append(
            StepResult(
                name="qa000-doctor-evidence-policy",
                returncode=0,
                stdout="QA-000 Run records doctor --json as environment evidence",
                stderr="",
            )
        )
        steps.append(run_step("configure-git-user-email", ["git", "config", "user.email", "vulcan-regression@example.invalid"], cwd=project_dir))
        steps.append(run_step("configure-git-user-name", ["git", "config", "user.name", "Vulcan Regression"], cwd=project_dir))
        steps.append(run_step("commit-fixture-state:add", ["git", "add", "-A"], cwd=project_dir))
        steps.append(run_step("commit-fixture-state:commit", ["git", "commit", "-m", "test: apply completed fixture"], cwd=project_dir))
        steps.append(run_step("checkout-integration-branch", ["git", "checkout", "-B", "dev"], cwd=project_dir))
        assert_run_integrate_config_hotfix_candidate(project_dir, py, steps)

        steps.append(
            run_step(
                "status-fixture",
                [py, "vulcan.py", "status"],
                cwd=project_dir,
                required_text=[
                    "[status] Vulcan Orchestrator status",
                    "current_gate: completed",
                    "profile: audit",
                    "current_branch: dev",
                ],
            )
        )
        steps.append(run_step("branch-status", [py, "vulcan.py", "branch-status"], cwd=project_dir))
        steps.append(
            run_step(
                "trace-context:req-001-01",
                [py, "vulcan.py", "trace-context", "--id", "REQ-001-01", "--depth", "2", "--emit", "yaml"],
                cwd=project_dir,
                required_text=[
                    "seed_id: REQ-001-01",
                    "target_contracts:",
                    "API-001",
                    "scope.writable은 trace graph가 확정하지 않는다",
                ],
            )
        )
        trace_json = run_step(
            "trace-context:api-001-json",
            [py, "vulcan.py", "trace-context", "--id", "API-001", "--depth", "2", "--direction", "both", "--emit", "json"],
            cwd=project_dir,
        )
        assert_trace_context_json(trace_json)
        steps.append(trace_json)

        release_pr_dry_run = run_step(
                "release-pr-dry-run",
                [py, "vulcan.py", "release-pr", "--dry-run"],
                cwd=project_dir,
                required_text=["Vulcan release PR", "Merge policy: manual only after Gate 5 approval"],
        )
        assert_release_pr_body(release_pr_dry_run)
        steps.append(release_pr_dry_run)
        steps.append(
            run_step(
                "release-pr-blocks-missing-base",
                [py, "vulcan.py", "release-pr", "--dry-run", "--base", "missing-release-base"],
                cwd=project_dir,
                expected_returncodes={1},
                required_text=["release-pr base 브랜치를 찾을 수 없습니다"],
            )
        )
        steps.append(run_step("checkout-main-for-release-pr-guard", ["git", "checkout", "main"], cwd=project_dir))
        try:
            steps.append(
                run_step(
                    "release-pr-blocks-wrong-branch",
                    [py, "vulcan.py", "release-pr", "--dry-run"],
                    cwd=project_dir,
                    expected_returncodes={1},
                    required_text=["release-pr은 통합 브랜치 `dev`에서 실행합니다"],
                )
            )
        finally:
            steps.append(run_step("checkout-dev-after-release-pr-guard", ["git", "checkout", "dev"], cwd=project_dir))
        dirty_guard = project_dir / "docs" / "runs" / "_release_dirty_guard.md"
        dirty_guard.write_text("dirty guard\n", encoding="utf-8")
        try:
            steps.append(
                run_step(
                    "release-pr-blocks-dirty-worktree",
                    [py, "vulcan.py", "release-pr", "--dry-run"],
                    cwd=project_dir,
                    expected_returncodes={1},
                    required_text=["release-pr 생성 전 미커밋 변경이 있습니다"],
                )
            )
        finally:
            dirty_guard.unlink(missing_ok=True)
        steps.append(
            run_step(
                "check-trace",
                [py, "vulcan.py", "check-trace"],
                cwd=project_dir,
                required_text=["이슈 0건"],
            )
        )
        steps.append(
            run_step(
                "check-architecture-baseline",
                [py, "vulcan.py", "check-architecture", "--level", "baseline"],
                cwd=project_dir,
                required_text=["이슈 0건"],
            )
        )
        steps.append(
            run_step(
                "check-contract",
                [py, "vulcan.py", "check-contract"],
                cwd=project_dir,
                required_text=["FAIL 0"],
            )
        )
        steps.append(assert_status_json_check(project_dir, py))
        steps.append(assert_execute_json_plan(project_dir, py))

        for run_name in REPRESENTATIVE_RUNS:
            steps.append(
                run_step(
                    f"run-check:{run_name}",
                    [py, "vulcan.py", "run-check", str(Path("docs") / "runs" / run_name)],
                    cwd=project_dir,
                )
            )

        for run_name in PREFLIGHT_RUNS:
            steps.append(
                run_step(
                    f"run-preflight:{run_name}",
                    [py, "vulcan.py", "run-preflight", str(Path("docs") / "runs" / run_name)],
                    cwd=project_dir,
                    expected_returncodes={0, 1},
                )
            )

        for run_name in QA_PREFLIGHT_RUNS:
            steps.append(
                run_step(
                    f"run-preflight:{run_name}",
                    [py, "vulcan.py", "run-preflight", str(Path("docs") / "runs" / run_name)],
                    cwd=project_dir,
                )
            )

        session_path = project_dir / "session.json"
        session_before_qa_guard = json.loads(session_path.read_text(encoding="utf-8"))
        session_missing_qa_workspace = json.loads(json.dumps(session_before_qa_guard))
        session_missing_qa_workspace.pop("qa_execution", None)
        session_path.write_text(
            json.dumps(session_missing_qa_workspace, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        try:
            steps.append(
                run_step(
                    "run-preflight-blocks-qa001-without-qa000-workspace",
                    [
                        py,
                        "vulcan.py",
                        "run-preflight",
                        str(Path("docs") / "runs" / QA_PREFLIGHT_RUNS[0]),
                    ],
                    cwd=project_dir,
                    expected_returncodes={1},
                    required_text=["qa_execution.gate4_workspace.path"],
                )
            )
        finally:
            session_path.write_text(
                json.dumps(session_before_qa_guard, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        session_blocked_qa_workspace = json.loads(json.dumps(session_before_qa_guard))
        session_blocked_qa_workspace.setdefault("qa_execution", {}).setdefault("gate4_workspace", {})["status"] = "environment_blocked"
        session_path.write_text(
            json.dumps(session_blocked_qa_workspace, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        try:
            steps.append(
                run_step(
                    "run-preflight-blocks-qa001-after-qa000-environment-blocked",
                    [
                        py,
                        "vulcan.py",
                        "run-preflight",
                        str(Path("docs") / "runs" / QA_PREFLIGHT_RUNS[0]),
                    ],
                    cwd=project_dir,
                    expected_returncodes={1},
                    required_text=[
                        "workspace 상태가 environment_blocked",
                        "doctor JSON",
                        "ISSUE/environment_blocked",
                        "qa-fix-loop",
                    ],
                )
            )
            steps.append(
                run_step(
                    "status-json-surfaces-qa-workspace-followup",
                    [py, "vulcan.py", "status", "--json"],
                    cwd=project_dir,
                    required_text=[
                        "qa_workspace_followup",
                        "doctor JSON",
                        "ISSUE/environment_blocked",
                        "qa-fix-loop",
                    ],
                )
            )
        finally:
            session_path.write_text(
                json.dumps(session_before_qa_guard, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        steps.append(run_step("export-snapshot", [py, "vulcan.py", "export"], cwd=project_dir))
        if not (project_dir / "snapshot.json").exists():
            raise FixtureSmokeFailure("export did not create snapshot.json")

        trace_seed_run_new = run_step(
            "run-new-trace-seed",
            [
                py,
                "vulcan.py",
                "run-new",
                "--gate",
                "impl",
                "--skill",
                "build-wave",
                "--title",
                "Trace Seed Run New Smoke",
                "--trace-seed",
                "REQ-001-01",
            ],
            cwd=project_dir,
            required_text=["trace-context 보강", "related_ids"],
        )
        assert_trace_seed_generated_run(project_dir, trace_seed_run_new)
        steps.append(trace_seed_run_new)

        session_path = project_dir / "session.json"
        session_before_trace_seed_wave = json.loads(session_path.read_text(encoding="utf-8"))
        session_for_trace_seed_wave = json.loads(json.dumps(session_before_trace_seed_wave))
        session_for_trace_seed_wave["current_gate"] = "impl"
        impl = session_for_trace_seed_wave.setdefault("implementation", {})
        waves = impl.setdefault("waves", {})
        waves["current"] = ""
        waves.setdefault("items", [])
        session_path.write_text(
            json.dumps(session_for_trace_seed_wave, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        trace_seed_wave = run_step(
            "wave-start-trace-seed",
            [
                py,
                "vulcan.py",
                "wave-start",
                "BW-099",
                "--title",
                "Trace Seed Run Generation Smoke",
                "--trace-seed",
                "REQ-001-01",
            ],
            cwd=project_dir,
            required_text=["trace-context 보강", "related_ids"],
        )
        assert_trace_seed_generated_run(project_dir, trace_seed_wave)
        steps.append(trace_seed_wave)

        session_poc_trace_seed = json.loads(session_path.read_text(encoding="utf-8"))
        session_poc_trace_seed["profile"] = "poc"
        session_poc_trace_seed["delivery_profile"] = "poc"
        session_poc_trace_seed["current_gate"] = "impl"
        session_path.write_text(
            json.dumps(session_poc_trace_seed, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        config_path = project_dir / "vulcan.config.json"
        config_poc_trace_seed = json.loads(config_path.read_text(encoding="utf-8"))
        config_poc_trace_seed["delivery_profile"] = "poc"
        config_path.write_text(
            json.dumps(config_poc_trace_seed, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        poc_trace_seed_run_new = run_step(
            "run-new-poc-trace-depth-default",
            [
                py,
                "vulcan.py",
                "run-new",
                "--gate",
                "impl",
                "--skill",
                "build-wave",
                "--title",
                "PoC Trace Depth Default Smoke",
                "--trace-seed",
                "REQ-001-01",
            ],
            cwd=project_dir,
            required_text=["trace-context 보강", "related_ids"],
        )
        assert_poc_trace_seed_generated_run(project_dir, poc_trace_seed_run_new)
        steps.append(poc_trace_seed_run_new)

        assert_gitignore_evidence_policy(project_dir, py, steps)
        assert_native_delegation_guardrails(project_dir, py, steps)
        assert_run_input_contract_metadata_guardrails(project_dir, py, steps)
        assert_qa_execution_mutation_guardrails(project_dir, py, steps)

        print("Vulcan fixture smoke regression: PASS")
        print(f"  fixture: {args.fixture}")
        if args.keep:
            print(f"  project_dir: {project_dir}")
        else:
            print(f"  project_dir: {project_dir} (temporary)")
        print(f"  steps: {len(steps)}")
        for step in steps:
            print(f"  - {step.name}: exit {step.returncode}")
        return 0
    finally:
        if args.keep:
            print(f"Kept fixture smoke project: {project_dir}")
        elif temp_ctx is not None:
            temp_ctx.cleanup()
        elif project_dir.exists():
            shutil.rmtree(project_dir)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fixture-based Vulcan regression smoke checks.")
    parser.add_argument("--fixture", default=DEFAULT_FIXTURE, help=f"Fixture name under scripts/regression/fixtures (default: {DEFAULT_FIXTURE}).")
    parser.add_argument(
        "--product-fixture",
        default=DEFAULT_PRODUCT_FIXTURE,
        help=f"Completed Product fixture name under scripts/regression/fixtures (default: {DEFAULT_PRODUCT_FIXTURE}).",
    )
    parser.add_argument("--output-dir", help="Optional empty directory where the smoke project should be created.")
    parser.add_argument("--keep", action="store_true", help="Keep the generated fixture smoke project after the run.")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="Timeout for individual subprocess steps.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return run_fixture_smoke(parse_args(argv or sys.argv[1:]))
    except FixtureSmokeFailure as exc:
        print("Vulcan fixture smoke regression: FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired as exc:
        print("Vulcan fixture smoke regression: FAIL", file=sys.stderr)
        print(f"step timed out: {' '.join(exc.cmd)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
