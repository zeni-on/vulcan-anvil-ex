#!/usr/bin/env python3
"""Fixture-based regression smoke harness for Vulcan-Anvil Ex.

The minimal audit smoke test checks a freshly initialized project. This script
adds a normalized completed-project fixture on top of a fresh init and verifies
that core document/check commands still accept the real artifact shape.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_FIXTURE = "simple-hello-audit"

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


def assert_trace_context_json(result: StepResult) -> None:
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise FixtureSmokeFailure(f"trace-context JSON output is invalid: {exc}\n{result.combined_output}") from exc

    related_ids = set(payload.get("related_ids") or [])
    target_contracts = payload.get("target_contracts") or {}
    expected_related = {"REQ-001-01", "API-001", "PGM-001", "SEC-001", "UT-001", "IT-001"}
    missing = sorted(expected_related - related_ids)
    if missing:
        raise FixtureSmokeFailure(f"trace-context JSON missing related IDs: {missing}")
    if "API-001" not in set(target_contracts.get("api") or []):
        raise FixtureSmokeFailure("trace-context JSON target_contracts.api did not include API-001")
    if "PGM-001" not in set(target_contracts.get("pgm") or []):
        raise FixtureSmokeFailure("trace-context JSON target_contracts.pgm did not include PGM-001")


def release_pr_body_path_from_output(output: str) -> Path:
    match = re.search(r"(?m)^\s*body:\s+(.+?)\s*$", output)
    if not match:
        raise FixtureSmokeFailure(f"release-pr output did not include body path\n{output}")
    return Path(match.group(1).strip())


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


def run_fixture_smoke(args: argparse.Namespace) -> int:
    root = repo_root()
    fixture_dir = root / "scripts" / "regression" / "fixtures" / args.fixture
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
    py = sys.executable
    steps: list[StepResult] = []

    try:
        steps.append(
            run_step(
                "init",
                [py, str(vulcan_py), "init", str(project_dir), "regression-simple-hello"],
                cwd=root,
                timeout_seconds=args.timeout_seconds,
            )
        )
        apply_fixture(fixture_dir, project_dir)
        validate_fixture_inputs(project_dir)
        steps.append(run_step("commit-fixture-state:add", ["git", "add", "-A"], cwd=project_dir))
        steps.append(run_step("commit-fixture-state:commit", ["git", "commit", "-m", "test: apply completed fixture"], cwd=project_dir))
        steps.append(run_step("checkout-integration-branch", ["git", "checkout", "-B", "dev"], cwd=project_dir))

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

        steps.append(run_step("export-snapshot", [py, "vulcan.py", "export"], cwd=project_dir))
        if not (project_dir / "snapshot.json").exists():
            raise FixtureSmokeFailure("export did not create snapshot.json")

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
