"""Explicit command records, without Git or source identity collection."""

import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import time
from datetime import datetime, timezone


EXCLUDED_NAMES = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__"}
LIMITATIONS = [
    "Records command execution, not source identity, test coverage or acceptance approval.",
    "The Orchestrator reviews implementation changes and decides which checks to rerun.",
    "Optional source paths are descriptive only; their contents are not read or hashed.",
    "Explicit argv is recorded verbatim: callers must not put secrets in arguments.",
    "Child output and environment are not recorded; no timeout or process supervisor is provided.",
]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _root(project_dir):
    root = Path(project_dir).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("project_dir must be an existing directory")
    return root


def _relative(value):
    value = os.fspath(value)
    path = Path(value)
    if (not value or path.is_absolute() or PureWindowsPath(value).drive
            or any(part == ".." or ":" in part for part in path.parts)
            or (os.name == "nt" and (PureWindowsPath(value).is_reserved()
                or any(part.endswith((" ", ".")) for part in path.parts if part != ".")))
            or "\x00" in value):
        raise ValueError("paths must be nonempty relative paths without '..' or drive syntax")
    return path.as_posix()


def _path(root, relative):
    if root.is_symlink() or getattr(root, "is_junction", lambda: False)():
        raise ValueError("project_dir changed to a symlink/junction")
    path = root / relative
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise ValueError("symlink/junction paths are not supported: " + relative)
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("path escapes project_dir: " + relative)
    return resolved


def _excluded(relative):
    return any(part in EXCLUDED_NAMES or part == ".env" or part.startswith(".env.")
               for part in Path(relative).parts)


def _sources(root, sources):
    if sources is None:
        return []
    if not isinstance(sources, (list, tuple)):
        raise ValueError("sources must be a list of relative paths")
    scopes = sorted(set(_relative(source) for source in sources))
    for rel in scopes:
        _path(root, rel)
        if _excluded(rel):
            raise ValueError("source is excluded by policy: " + rel)
    return scopes


def _output(root, evidence, sources):
    rel = _relative(evidence)
    path = _path(root, rel)
    if path.suffix.lower() != ".json" or not path.parent.is_dir():
        raise ValueError("evidence must be a new .json file in an existing directory")
    if path.exists():
        raise ValueError("evidence already exists")
    for source in sources:
        scope = _path(root, source)
        if path.is_relative_to(scope) or scope.is_relative_to(path):
            raise ValueError("evidence overlaps a source scope")
    return path


def record_verification(project_dir, sources, evidence, command, cwd=".", run_id=None,
                        run_lookup=None):
    """Run explicit argv and return (report, command exit code), writing a new JSON.

    Source paths are optional context only. Startup failure returns 127;
    validation/storage errors raise ValueError/OSError. run_lookup is the existing
    framework find_run_file helper, required only when a Run label is supplied.
    No Run content is used as executable input.
    """
    root = _root(project_dir)
    if (not isinstance(command, (list, tuple)) or not command or not command[0]
            or any(not isinstance(arg, str) or "\x00" in arg for arg in command)):
        raise ValueError("command must be a nonempty explicit argv sequence")
    # Windows implicitly interprets batch files even with shell=False.
    if os.name == "nt" and Path(command[0]).suffix.lower() in {".cmd", ".bat"}:
        raise ValueError("use a real executable, not a Windows batch file")
    scopes = _sources(root, sources)
    work_rel = _relative(cwd)
    work = _path(root, work_rel)
    if not work.is_dir():
        raise ValueError("cwd must be an existing directory inside project_dir")
    if os.name == "nt":
        executable = shutil.which(command[0], path=str(work) + os.pathsep + os.environ.get("PATH", ""))
        if executable and Path(executable).suffix.lower() in {".cmd", ".bat"}:
            raise ValueError("use a real executable, not a Windows batch file")
    output = _output(root, evidence, scopes)
    if run_id is not None:
        if not isinstance(run_id, str) or not run_id.strip() or any(c in run_id for c in "/\\:\x00"):
            raise ValueError("run_id must be a Run label, not a path")
        found = run_lookup(str(root), run_id) if run_lookup else None
        if not found:
            raise ValueError("run_id does not identify an existing Run")
        try:
            run_rel = Path(os.path.abspath(found)).relative_to(root).as_posix()
        except ValueError:
            raise ValueError("Run is outside project_dir") from None
        if not _path(root, run_rel).is_file():
            raise ValueError("Run must be an existing regular file")
    _output(root, evidence, scopes)
    started = _now()
    clock = time.monotonic()
    launch_error = None
    try:
        exit_code = subprocess.run(list(command), cwd=work, shell=False).returncode
    except OSError as exc:
        exit_code = 127
        launch_error = type(exc).__name__
    duration = time.monotonic() - clock
    finished = _now()
    report = {"schema_version": 2, "kind": "explicit_verification", "run_id": run_id,
              "command": {"argv": list(command), "cwd": work_rel, "exit_code": exit_code,
                          "started_at": started, "finished_at": finished,
                          "duration_seconds": duration, "launch_error": launch_error},
              "sources": scopes,
              "limitations": LIMITATIONS}
    # Revalidate after the child, then exclusive-create: never replace a prior report.
    output = _output(root, evidence, scopes)
    payload = json.dumps(report, ensure_ascii=True, indent=2) + "\n"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    return report, exit_code
