"""Execute known-bad cases in disposable copies; the real sample stays intact."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from checks import ROOT, OUTPUT, browser_issues, required, write_json

sys.path.insert(0, str(ROOT / "tests"))
from probe_history import mutated_source

METHOD = "test_reg_001_preserves_original_content_and_reason_after_resubmit"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def command(argv, cwd, env=ENV):
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", timeout=90)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUTPUT.mkdir(exist_ok=True)
    results = []
    baseline = command([sys.executable, "-B", "tests/probe_history.py"], ROOT)
    (OUTPUT / "preservation-probe.log").write_text(baseline.stdout + baseline.stderr, encoding="utf-8")
    if baseline.returncode != 0:
        raise RuntimeError("Preservation probe no longer detects the intended assertion failure")
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests/test_api.py").read_text(encoding="utf-8")
    needle = f"    def {METHOD}(self):"
    if tests.count(needle) != 1:
        raise RuntimeError("Review the required preservation method before updating probes")
    cases = {
        "history_corruption": (mutated_source(source), tests, "failed"),
        "missing_required": (source, tests.replace(needle, "    def not_collected(self):"), "incomplete"),
        "skipped_required": (source, tests.replace(needle, "    @unittest.skip('negative probe')\n" + needle), "incomplete"),
        "zero_tests": (source, "# Disposable empty discovery target\n", "incomplete"),
    }
    for name, (app_text, test_text, expected) in cases.items():
        with tempfile.TemporaryDirectory(prefix="request-board-ci-") as folder:
            temp = Path(folder)
            (temp / "tests").mkdir()
            (temp / "ci").mkdir()
            (temp / "app.py").write_text(app_text, encoding="utf-8")
            (temp / "tests/test_api.py").write_text(test_text, encoding="utf-8")
            for file in ("checks.py", "required.json"):
                shutil.copyfile(ROOT / "ci" / file, temp / "ci" / file)
            run = command([sys.executable, "-B", "ci/checks.py", "api"], temp)
            report = json.loads((temp / "ci-artifacts/api-summary.json").read_text(encoding="utf-8"))
            if run.returncode != 1 or report["status"] != expected:
                raise RuntimeError(f"{name}: expected {expected}, got {report}")
            if name == "history_corruption" and "AssertionError" not in run.stdout:
                raise RuntimeError("Corruption must fail an assertion, not environment/import setup")
            (OUTPUT / f"probe-{name}.log").write_text(run.stdout + run.stderr, encoding="utf-8")
            results.append({"case": name, "observed": report["status"], "child_exit": run.returncode})

    with tempfile.TemporaryDirectory(prefix="request-board-weakened-") as folder:
        temp = Path(folder)
        (temp / "tests").mkdir()
        (temp / "app.py").write_text(source, encoding="utf-8")
        (temp / "tests/test_api.py").write_text(tests.replace(needle, needle + "\n        return  # Deliberately weakened assertion"), encoding="utf-8")
        shutil.copyfile(ROOT / "tests/probe_history.py", temp / "tests/probe_history.py")
        run = command([sys.executable, "-B", "tests/probe_history.py"], temp)
        if run.returncode != 1 or "Expected the history-preservation assertion to fail" not in run.stderr:
            raise RuntimeError("Assertion weakening was not detected by the preservation probe")
        (OUTPUT / "probe-weakened.log").write_text(run.stdout + run.stderr, encoding="utf-8")
        results.append({"case": "weakened_assertion", "observed": "rejected", "child_exit": 1})

    # Use an actual empty browser cache without downloading or deleting any installed browser.
    with tempfile.TemporaryDirectory(prefix="request-board-empty-browser-") as folder:
        run = command(["node", "ci/browser-ready.cjs"], ROOT, {**ENV, "PLAYWRIGHT_BROWSERS_PATH": folder})
        report = json.loads(run.stderr)
        if run.returncode != 3 or report["status"] != "environment_blocked":
            raise RuntimeError("Empty browser cache was not classified as environment_blocked")
        (OUTPUT / "probe-environment.log").write_text(run.stdout + run.stderr, encoding="utf-8")
        results.append({"case": "missing_browser_cache", "observed": report["status"], "child_exit": 3})

    browser = json.loads((ROOT / "test-results/results.json").read_text(encoding="utf-8"))
    if browser_issues(browser, required()):
        raise RuntimeError("Run a successful, complete browser suite before the report omission probe")

    def remove_flow(suites):
        for suite in suites:
            suite["specs"] = [s for s in suite.get("specs", [])
                              if "resubmission" not in {tag.removeprefix("@") for tag in s.get("tags", [])}]
            remove_flow(suite.get("suites", []))

    omitted = copy.deepcopy(browser)
    remove_flow(omitted["suites"])
    issues = browser_issues(omitted, required())
    if not any(i.startswith("missing:browser:") for i in issues):
        raise RuntimeError("Unrelated green browser cases concealed a missing required flow")
    results.append({"case": "browser_report_missing_required_flow", "observed": "incomplete", "method": "copy of actual report", "issues": issues})
    write_json("probes.json", {"status": "passed", "cases": results})
    print(json.dumps({"status": "passed", "cases": results}, indent=2))


if __name__ == "__main__":
    main()
