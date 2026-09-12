"""Fail-closed, stdlib-only policy for the Product request board CI."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ENVIRONMENT_STEPS = ("python", "node", "install", "browsers")
VERIFICATION_STEPS = ("static", "api", "browser", "reports", "probe", "iteration")
MANDATORY_STEPS = ENVIRONMENT_STEPS + VERIFICATION_STEPS
EXAMPLE_PREFIX = "examples/product-request-board/"
EXAMPLE_REPORTS = {
    EXAMPLE_PREFIX + "README.md",
    EXAMPLE_PREFIX + "docs/verification.md",
    EXAMPLE_PREFIX + "docs/ci-verification.md",
}
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def requires_tests(paths: list[str]) -> bool:
    """Only unambiguously documentation-only changes may skip verification."""
    if not isinstance(paths, list) or not paths:
        return True
    for path in paths:
        if not isinstance(path, str) or not path:
            return True
        path = path.replace("\\", "/")
        parts = path.split("/")
        if any(part in ("", ".", "..") for part in parts):
            return True
        if ":" in path or any(ord(char) < 32 for char in path):
            return True
        if (parts[0] == ".github" or (path.startswith(EXAMPLE_PREFIX) and path not in EXAMPLE_REPORTS)
                or not path.endswith(".md")):
            return True
    return False


def _step_state(step):
    if not isinstance(step, dict):
        return "invalid"
    outcome, conclusion = step.get("outcome"), step.get("conclusion")
    # An actual failure remains a failure even with continue-on-error enabled.
    if outcome == "failure" or conclusion == "failure":
        return "failure"
    if outcome == conclusion and outcome in ("success", "skipped", "cancelled"):
        return outcome
    return "invalid"


def assess_steps(steps: dict, required: bool) -> dict:
    """Summarize steps; environment failures outrank failures and incompleteness."""
    if not isinstance(steps, dict) or type(required) is not bool:
        return {"status": "incomplete", "issues": ["Invalid steps or required value"]}
    issues = []
    statuses = []
    if _step_state(steps.get("scope")) != "success":
        issues.append("scope: must succeed")
        statuses.append("incomplete")
    expected = "success" if required else "skipped"
    for step_id in MANDATORY_STEPS:
        state = _step_state(steps.get(step_id))
        if state == expected:
            continue
        issues.append(f"{step_id}: expected {expected}, got {state}")
        if state == "failure":
            statuses.append("environment_blocked" if step_id in ENVIRONMENT_STEPS else "failed")
        else:
            statuses.append("incomplete")
    for status in ("environment_blocked", "failed", "incomplete"):
        if status in statuses:
            return {"status": status, "issues": issues}
    return {"status": "success" if required else "not_applicable", "issues": []}


def _scope():
    base = os.environ.get("BASE_SHA", "")
    paths = []
    if (os.environ.get("EVENT_NAME") in ("pull_request", "push")
            and re.fullmatch(r"[0-9a-fA-F]{40}", base)):
        result = subprocess.run(
            ["git", "diff", "--no-renames", "--name-only", "-z", base, "HEAD"],
            cwd=REPOSITORY_ROOT, check=True, capture_output=True,
        )
        raw = result.stdout
        if raw and not raw.endswith(b"\0"):
            raise ValueError("git diff output is not NUL-terminated")
        paths = raw[:-1].decode("utf-8").split("\0") if raw else []
    required = requires_tests(paths)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"required={str(required).lower()}\n")
    print(json.dumps({"required": required, "changed_paths": len(paths)}))
    return 0


def _gate():
    value = os.environ.get("REQUIRED")
    if value not in ("true", "false"):
        raise ValueError("REQUIRED must be exactly true or false")
    steps = json.loads(os.environ["STEPS_JSON"])
    if not isinstance(steps, dict):
        raise ValueError("STEPS_JSON must be an object")
    result = assess_steps(steps, value == "true")
    print(json.dumps(result))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(f"## Product CI: {result['status']}\n")
            for issue in result["issues"]:
                stream.write(f"- {issue}\n")
    return 0 if result["status"] in ("success", "not_applicable") else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scope", action="store_true")
    mode.add_argument("--gate", action="store_true")
    args = parser.parse_args(argv)
    try:
        return _scope() if args.scope else _gate()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"CI policy error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
