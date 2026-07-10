"""Local environment diagnostics for the Vulcan-Anvil Ex CLI."""

import json
import os
import shutil
import socket
import subprocess
import sys

from .runners import detect_runtime_runners


def _add_check(checks, category, name, status, detail="", recommendation=""):
    checks.append({
        "category": category,
        "name": name,
        "status": status,
        "detail": detail,
        "recommendation": recommendation,
    })


def _command_version(command, args=None, cwd="."):
    exe = shutil.which(command)
    if not exe:
        return None, f"{command} not found"
    try:
        result = subprocess.run(
            [exe] + list(args or ["--version"]),
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return "", str(exc)
    text = (result.stdout or result.stderr or "").strip()
    if result.returncode != 0:
        return "", text or f"exit code {result.returncode}"
    return text.splitlines()[0] if text else "", ""


def _json_file(path):
    try:
        with open(path, encoding="utf-8") as file_obj:
            return json.load(file_obj)
    except (OSError, json.JSONDecodeError):
        return None


def _package_json_paths(project_dir):
    candidates = [
        "package.json",
        "frontend/package.json",
        "client/package.json",
        "web/package.json",
        "app/package.json",
        "dashboard/package.json",
    ]
    paths = []
    for rel_path in candidates:
        abs_path = os.path.join(project_dir, rel_path)
        if os.path.exists(abs_path):
            paths.append(abs_path)
    return paths


def _package_has_dependency(package_data, dependency):
    if not isinstance(package_data, dict):
        return False
    for key in ("dependencies", "devDependencies", "optionalDependencies"):
        values = package_data.get(key)
        if isinstance(values, dict) and dependency in values:
            return True
    return False


def _dir_nonempty(path):
    try:
        return os.path.isdir(path) and bool(os.listdir(path))
    except OSError:
        return False


def _local_port_open(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=0.4):
            return True
    except OSError:
        return False


def _git_text(args, project_dir):
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _git_status_porcelain(project_dir):
    try:
        result = subprocess.run(
            ["git", "-c", "core.quotePath=false", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _has_git_remote(project_dir, remote="origin"):
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote],
            cwd=project_dir,
            capture_output=True,
        )
    except OSError:
        return False
    return result.returncode == 0


def _normalize_repo_path(path):
    normalized = path.replace("\\", "/").strip().strip('"').strip("'")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def collect_doctor_checks(project_dir=".", delivery_profile="audit", runner_detector=None):
    """Collect environment checks without making a Gate or product verdict."""
    project_abs = os.path.abspath(project_dir)
    checks = []
    runner_detector = runner_detector or detect_runtime_runners

    _add_check(checks, "project", "project_dir", "pass" if os.path.isdir(project_abs) else "fail", project_abs)

    session = _json_file(os.path.join(project_abs, "session.json"))
    if session is None:
        _add_check(checks, "project", "session.json", "warn", "not found or invalid", "init된 Ex 프로젝트라면 session.json을 확인하세요.")
    else:
        _add_check(
            checks,
            "project",
            "session.json",
            "pass",
            f"project={session.get('project') or '-'}, current_gate={session.get('current_gate') or '-'}",
        )

    config = _json_file(os.path.join(project_abs, "vulcan.config.json"))
    if config is None:
        _add_check(checks, "project", "vulcan.config.json", "warn", "not found or invalid", "profile/default runner 설정이 없으면 기본값으로 동작합니다.")
    else:
        runtime_config = config.get("runtime") if isinstance(config.get("runtime"), dict) else {}
        primary = runtime_config.get("primary") or runtime_config.get("primary_runner") or "-"
        _add_check(checks, "project", "vulcan.config.json", "pass", f"profile={delivery_profile}, primary_runner={primary}")

    python_detail = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ({sys.executable})"
    _add_check(checks, "tool", "python", "pass", python_detail)

    git_version, git_error = _command_version("git", ["--version"], cwd=project_abs)
    if git_version is None:
        _add_check(checks, "tool", "git", "fail", git_error, "Git 설치 또는 PATH를 확인하세요.")
    elif git_version == "":
        _add_check(checks, "tool", "git", "warn", git_error)
    else:
        git_inside_worktree = _git_text(["rev-parse", "--is-inside-work-tree"], project_abs) == "true"
        branch = _git_text(["rev-parse", "--abbrev-ref", "HEAD"], project_abs) or "unknown"
        dirty = bool(_git_status_porcelain(project_abs))
        remote = _has_git_remote(project_abs)
        _add_check(
            checks,
            "tool",
            "git",
            "pass" if git_inside_worktree else "warn",
            f"{git_version}; git_repo={git_inside_worktree}; branch={branch}; dirty={dirty}; origin={remote}",
            "init된 Ex 프로젝트라면 git 저장소가 있어야 합니다." if not git_inside_worktree else "",
        )

    node_version, node_error = _command_version("node", ["--version"], cwd=project_abs)
    if node_version is None:
        _add_check(checks, "tool", "node", "warn", node_error, "Frontend/Dashboard/Playwright 작업 전 Node.js를 설치하세요.")
    elif node_version == "":
        _add_check(checks, "tool", "node", "warn", node_error)
    else:
        _add_check(checks, "tool", "node", "pass", node_version)

    npm_version, npm_error = _command_version("npm", ["--version"], cwd=project_abs)
    if npm_version is None:
        _add_check(checks, "tool", "npm", "warn", npm_error, "Frontend 의존성 설치와 Playwright 실행 전 npm을 확인하세요.")
    elif npm_version == "":
        _add_check(checks, "tool", "npm", "warn", npm_error)
    else:
        _add_check(checks, "tool", "npm", "pass", npm_version)

    package_paths = _package_json_paths(project_abs)
    if package_paths:
        rel_packages = [_normalize_repo_path(os.path.relpath(path, project_abs)) for path in package_paths]
        _add_check(checks, "frontend", "package.json", "pass", ", ".join(rel_packages))
    else:
        _add_check(checks, "frontend", "package.json", "info", "not found", "Frontend 없는 프로젝트라면 무시해도 됩니다.")

    playwright_packages = []
    package_with_node_modules = []
    for package_path in package_paths:
        package_data = _json_file(package_path)
        rel_package = _normalize_repo_path(os.path.relpath(package_path, project_abs))
        package_dir = os.path.dirname(package_path)
        if _package_has_dependency(package_data, "@playwright/test") or _package_has_dependency(package_data, "playwright"):
            playwright_packages.append(rel_package)
        if os.path.isdir(os.path.join(package_dir, "node_modules")):
            package_with_node_modules.append(rel_package)

    if package_paths and not package_with_node_modules:
        _add_check(checks, "frontend", "node_modules", "warn", "package.json exists but node_modules not found", "lockfile 기준 npm ci/npm install 가능 여부를 QA-000에서 확인하세요.")
    elif package_with_node_modules:
        _add_check(checks, "frontend", "node_modules", "pass", ", ".join(package_with_node_modules))

    if playwright_packages:
        _add_check(checks, "playwright", "package", "pass", ", ".join(playwright_packages))
    elif package_paths:
        _add_check(checks, "playwright", "package", "warn", "@playwright/test not found in detected package.json", "Audit/Product UI Pass에는 @playwright/test와 npx playwright test 증적이 필요합니다.")
    else:
        _add_check(checks, "playwright", "package", "info", "package.json not found")

    cache_candidates = []
    env_cache = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if env_cache:
        cache_candidates.append(env_cache)
    cache_candidates.extend([
        os.path.join(project_abs, ".vulcan", "cache", "ms-playwright"),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "ms-playwright"),
        os.path.join(os.path.expanduser("~"), ".cache", "ms-playwright"),
    ])
    existing_caches = [path for path in cache_candidates if _dir_nonempty(path)]
    if existing_caches:
        _add_check(checks, "playwright", "browser_cache", "pass", "; ".join(existing_caches[:3]))
    elif playwright_packages:
        _add_check(checks, "playwright", "browser_cache", "warn", "not found", "npx playwright install 또는 프로젝트 지정 cache를 준비하세요.")
    else:
        _add_check(checks, "playwright", "browser_cache", "info", "not checked")

    npm_cache = os.environ.get("npm_config_cache") or os.environ.get("NPM_CONFIG_CACHE") or os.path.join(project_abs, ".vulcan", "cache", "npm")
    _add_check(
        checks,
        "cache",
        "npm_cache",
        "pass" if os.path.isdir(npm_cache) else "info",
        npm_cache,
        "worker npm 설치가 막히면 npm_config_cache를 이 경로로 고정할 수 있습니다.",
    )

    runners = runner_detector()
    if runners:
        runner_details = []
        for runner in runners:
            model = runner.get("model") or "-"
            effort = runner.get("effort") or runner.get("reasoning_effort") or "-"
            runner_details.append(f"{runner.get('name')}({model}/{effort})")
        _add_check(checks, "runner", "available_runners", "pass", ", ".join(runner_details))
    else:
        _add_check(checks, "runner", "available_runners", "warn", "none detected", "codex/claude/agy CLI가 필요하면 설치와 로그인을 확인하세요.")

    dashboard_dir = os.path.join(project_abs, "dashboard")
    if os.path.exists(os.path.join(dashboard_dir, "package.json")):
        dashboard_status = "running" if _local_port_open("127.0.0.1", 3001) else "not running"
        _add_check(checks, "dashboard", "dashboard", "pass", f"package found; port 3001 {dashboard_status}")
    else:
        _add_check(checks, "dashboard", "dashboard", "info", "dashboard/package.json not found in this project", "보통 dashboard는 Ex 루트에서 실행합니다.")

    return checks


def build_doctor_report(project_dir=".", delivery_profile="audit", runner_detector=None):
    project_abs = os.path.abspath(project_dir)
    checks = collect_doctor_checks(
        project_abs,
        delivery_profile=delivery_profile,
        runner_detector=runner_detector,
    )
    counts = {"pass": 0, "warn": 0, "fail": 0, "info": 0}
    for check in checks:
        status = check.get("status") or "info"
        counts[status] = counts.get(status, 0) + 1
    return {
        "project_dir": project_abs,
        "summary": counts,
        "checks": checks,
    }


def render_doctor_report(report, emit_json=False):
    if emit_json:
        return json.dumps(report, ensure_ascii=False, indent=2)

    counts = report["summary"]
    lines = [
        "==================================================",
        " [doctor] Vulcan local environment check",
        "==================================================",
        f" project_dir: {report['project_dir']}",
    ]
    for check in report["checks"]:
        status = (check.get("status") or "info").upper()
        lines.append(f" [{status}] {check.get('category')}.{check.get('name')}: {check.get('detail') or '-'}")
        if check.get("recommendation") and check.get("status") in {"warn", "fail"}:
            lines.append(f"        -> {check.get('recommendation')}")
    lines.extend([
        "--------------------------------------------------",
        f" summary: pass {counts.get('pass', 0)}, warn {counts.get('warn', 0)}, fail {counts.get('fail', 0)}, info {counts.get('info', 0)}",
        "==================================================",
    ])
    return "\n".join(lines)


def run_doctor(project_dir=".", delivery_profile="audit", emit_json=False, runner_detector=None):
    report = build_doctor_report(
        project_dir,
        delivery_profile=delivery_profile,
        runner_detector=runner_detector,
    )
    print(render_doctor_report(report, emit_json=emit_json))
    return 1 if report["summary"].get("fail", 0) else 0
