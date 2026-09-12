"""Sample-only command and report checks; no Ex state/approval changes."""

from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "ci-artifacts"


def required():
    data = json.loads((ROOT / "ci/required.json").read_text(encoding="utf-8"))
    for key in ("api", "browser", "projects"):
        values = data[key]
        if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values) or len(set(values)) != len(values):
            raise ValueError("Invalid required inventory: " + key)
    return data


def api_issues(report, inventory):
    cases = report["cases"]
    counts = Counter(row["id"] for row in cases)
    issues = ["missing:api:" + name for name in inventory["api"] if counts[name] == 0]
    issues += ["duplicate:api:" + name for name, count in counts.items() if count != 1]
    for row in cases:
        if row["status"] != "passed":
            code = "failed" if row["status"] in {"failed", "error", "unexpected_success"} else "incomplete"
            issues.append(f"{code}:api:{row['id']}:{row['status']}")
    if report["executed"] != len(cases):
        issues.append("incomplete:api:execution count mismatch")
    return issues


def browser_issues(report, inventory):
    issues, found = [], Counter()
    if report.get("errors"):
        issues.append("failed:browser:runner errors")

    def visit(suites):
        for suite in suites:
            for spec in suite.get("specs", []):
                # Playwright JSON omits the @ prefix used by test declarations.
                tags = {"@" + tag.removeprefix("@") for tag in spec.get("tags", [])} & set(inventory["browser"])
                for case in spec["tests"]:
                    project = case["projectName"]
                    results = case["results"]
                    if (case["expectedStatus"] != "passed" or case["status"] != "expected"
                            or len(results) != 1 or results[0]["status"] != "passed"
                            or results[0].get("retry", 0) != 0 or results[0].get("errors")):
                        code = "failed" if any(r["status"] in {"failed", "timedOut"} for r in results) else "incomplete"
                        issues.append(f"{code}:browser:{project}:{spec['title']}")
                    if len(tags) > 1:
                        issues.append("incomplete:browser:one test cannot stand in for multiple required cases")
                    for tag in tags:
                        found[(project, tag)] += 1
            visit(suite.get("suites", []))

    visit(report["suites"])
    for project in inventory["projects"]:
        for tag in inventory["browser"]:
            count = found[(project, tag)]
            if count != 1:
                issues.append(f"{'missing' if count == 0 else 'duplicate'}:browser:{project}:{tag}")
    return issues


def write_json(name, value):
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []
        self.current = None

    def startTest(self, test):
        super().startTest(test)
        self.current = {"id": test.id(), "status": "incomplete"}
        self.cases.append(self.current)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.current["status"] = "passed"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.current["status"] = "failed"

    def addError(self, test, err):
        super().addError(test, err)
        self.current["status"] = "error"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.current["status"] = "skipped"

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.current["status"] = "expected_failure"

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.current["status"] = "unexpected_success"

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err:
            self.current["status"] = "failed"


def run_api():
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_api.py")
    OUTPUT.mkdir(exist_ok=True)
    with (OUTPUT / "api.log").open("w", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordedResult).run(suite)
    print((OUTPUT / "api.log").read_text(encoding="utf-8"))
    report = {"cases": result.cases, "executed": result.testsRun}
    write_json("api.json", report)
    return api_issues(report, required())


def run_static():
    commands = [[sys.executable, "-m", "py_compile", "app.py", "tests/test_api.py", "ci/iteration.py", "ci/iteration_assertions.py"],
                ["node", "--check", "static/app.js"], ["node", "--check", "playwright.config.js"],
                ["node", "--check", "tests/browser/request-board.spec.js"],
                ["node", "--check", "ci/browser-ready.cjs"]]
    errors = []
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        print(json.dumps({"argv": command, "exit_code": result.returncode}))
        print(result.stdout + result.stderr)
        if result.returncode:
            errors.append("failed:static:" + command[-1])
    required()
    return errors


def check_reports():
    inventory = required()
    api = json.loads((OUTPUT / "api.json").read_text(encoding="utf-8"))
    browser = json.loads((ROOT / "test-results/results.json").read_text(encoding="utf-8"))
    return api_issues(api, inventory) + browser_issues(browser, inventory)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    commands = {"api": run_api, "static": run_static, "reports": check_reports}
    name = sys.argv[1] if len(sys.argv) == 2 else ""
    if name not in commands:
        raise SystemExit("Usage: python ci/checks.py static|api|reports")
    try:
        issues = commands[name]()
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as error:
        issues = ["incomplete:" + str(error)]
    status = "failed" if any(i.startswith("failed:") for i in issues) else "incomplete" if issues else "passed"
    summary = {"status": status, "issues": issues}
    write_json(name + "-summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
