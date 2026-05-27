#!/usr/bin/env python3
"""Minimal regression smoke harness for Vulcan-Anvil Ex.

This harness intentionally avoids model calls, npm install, Gradle, Playwright,
and full sample-project replay. It checks the framework's own init/templates and
the guardrails that should stay stable before deeper fixture-based regression
tests are added.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REQUIRED_INIT_PATHS = [
    "AGENTS.md",
    "session.json",
    "vulcan.config.json",
    "vulcan.py",
    "docs/core/RUN_INPUT_CONTRACT.md",
    "docs/core/RUN_OUTPUT_CONTRACT.md",
    "docs/core/AGENT_RUN_PROTOCOL.md",
    "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md",
    "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md",
    "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
    "docs/artifacts/02-design/architecture/DOC-ARCH-G2-001_SW-Architecture_v0.1.md",
    "docs/artifacts/02-design/architecture/DOC-ARCH-G2-002_Deployment-Infrastructure-Architecture_v0.1.md",
    "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md",
    "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md",
    "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md",
    "docs/runs",
    "docs/reviews",
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


class SmokeFailure(RuntimeError):
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
        raise SmokeFailure(
            f"{name} returned {proc.returncode}, expected {sorted(expected_returncodes)}\n"
            f"Command: {' '.join(args)}\n{output}"
        )

    missing = [text for text in required_text if text not in output]
    if missing:
        raise SmokeFailure(
            f"{name} did not include required text: {missing}\n"
            f"Command: {' '.join(args)}\n{output}"
        )

    return result


def assert_paths(project_dir: Path) -> None:
    missing = [rel for rel in REQUIRED_INIT_PATHS if not (project_dir / rel).exists()]
    if missing:
        raise SmokeFailure("init missing required paths:\n" + "\n".join(f"  - {path}" for path in missing))


def find_single_run(project_dir: Path) -> Path:
    runs = sorted((project_dir / "docs" / "runs").glob("RUN-*.md"))
    if len(runs) != 1:
        raise SmokeFailure(f"expected exactly one generated Run document, found {len(runs)}")
    return runs[0]


def run_smoke(args: argparse.Namespace) -> int:
    root = repo_root()
    vulcan_py = root / "vulcan.py"
    if not vulcan_py.exists():
        raise SmokeFailure(f"vulcan.py not found at {vulcan_py}")

    base_dir: Path
    temp_ctx: tempfile.TemporaryDirectory[str] | None = None

    if args.output_dir:
        base_dir = Path(args.output_dir).resolve()
        if base_dir.exists() and any(base_dir.iterdir()):
            raise SmokeFailure(f"output directory must be empty: {base_dir}")
        base_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_ctx = tempfile.TemporaryDirectory(prefix="vulcan-audit-smoke-")
        base_dir = Path(temp_ctx.name)

    project_dir = base_dir / "regression-smoke"
    py = sys.executable

    steps: list[StepResult] = []
    try:
        steps.append(
            run_step(
                "init",
                [py, str(vulcan_py), "init", str(project_dir), "regression-smoke"],
                cwd=root,
                timeout_seconds=args.timeout_seconds,
            )
        )
        assert_paths(project_dir)

        steps.append(run_step("version", [py, "vulcan.py", "version"], cwd=project_dir))
        steps.append(
            run_step(
                "branch-status",
                [py, "vulcan.py", "branch-status"],
                cwd=project_dir,
                required_text=["integration_branch: dev", "current_gate: phase0"],
            )
        )
        steps.append(run_step("check-contract", [py, "vulcan.py", "check-contract"], cwd=project_dir))
        steps.append(
            run_step(
                "check-architecture-baseline",
                [py, "vulcan.py", "check-architecture", "--level", "baseline"],
                cwd=project_dir,
                expected_returncodes={0, 1},
                required_text=[
                    "DOC-ARCH-G2-001_SW-Architecture_v0.1.md",
                    "DOC-ARCH-G2-002_Deployment-Infrastructure-Architecture_v0.1.md",
                ],
            )
        )
        steps.append(
            run_step(
                "gate-start-blocks-before-phase0-approval",
                [py, "vulcan.py", "gate-start", "gate1", "--feature", "Regression Smoke"],
                cwd=project_dir,
                expected_returncodes={1},
                required_text=["현재 Gate 완료와 사용자 승인 근거가 필요합니다"],
            )
        )
        steps.append(
            run_step(
                "run-new-implementation-scaffold",
                [
                    py,
                    "vulcan.py",
                    "run-new",
                    "--adapter",
                    "codex-gpt",
                    "--gate",
                    "impl",
                    "--persona",
                    "build",
                    "--skill",
                    "implementation-scaffold",
                    "--title",
                    "BW-000 Implementation Scaffold",
                    "--related-ids",
                    "BW-000,PGM-001",
                ],
                cwd=project_dir,
            )
        )
        run_file = find_single_run(project_dir)
        run_file_arg = os.path.relpath(run_file, project_dir)
        steps.append(run_step("run-check-scaffold-draft", [py, "vulcan.py", "run-check", run_file_arg], cwd=project_dir))
        steps.append(
            run_step(
                "run-preflight-blocks-unready-worker-run",
                [py, "vulcan.py", "run-preflight", run_file_arg],
                cwd=project_dir,
                expected_returncodes={1},
                required_text=["Preflight 차단", "bw_id", "TBD"],
            )
        )
        steps.append(run_step("export-snapshot", [py, "vulcan.py", "export"], cwd=project_dir))
        if not (project_dir / "snapshot.json").exists():
            raise SmokeFailure("export did not create snapshot.json")

        print("Vulcan audit smoke regression: PASS")
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
            print(f"Kept smoke project: {project_dir}")
        elif temp_ctx is not None:
            temp_ctx.cleanup()
        elif project_dir.exists():
            shutil.rmtree(project_dir)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the minimal Vulcan audit workflow smoke regression.")
    parser.add_argument("--output-dir", help="Optional empty directory where the smoke project should be created.")
    parser.add_argument("--keep", action="store_true", help="Keep the generated smoke project after the run.")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="Timeout for individual subprocess steps.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return run_smoke(parse_args(argv or sys.argv[1:]))
    except SmokeFailure as exc:
        print("Vulcan audit smoke regression: FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired as exc:
        print("Vulcan audit smoke regression: FAIL", file=sys.stderr)
        print(f"step timed out: {' '.join(exc.cmd)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
