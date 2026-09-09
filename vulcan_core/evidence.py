"""Explicit, scoped verification observations; not a QA or environment attestation."""

import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import stat
import subprocess
import time
from datetime import datetime, timezone


EXCLUDED_NAMES = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__"}
LIMITATIONS = [
    "Only caller-selected scopes are observed; omitted code/tests/lockfiles are not covered.",
    "Git-ignored untracked files are not inventoried or hashed.",
    "VCS metadata, node_modules, venv/.venv, __pycache__, .env and .env.* are excluded.",
    "Without Git, ignore rules are unavailable; only the built-in exclusions apply.",
    "Snapshots are not atomic and cannot detect changes reverted between observations.",
    "HEAD and file hashes do not prove environment, dependencies, services or test coverage.",
    "Commit identity requires raw-byte index matches; filtered/CRLF checkouts may have null tested_commit.",
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


def _git(root, *args):
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS"):
        env.pop(name, None)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    # Attribute observations to the named objects, never replacement trees.
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    # check-ignore accepts literal filenames, but rejects pathspec magic itself.
    env["GIT_LITERAL_PATHSPECS"] = "0" if args[0] == "check-ignore" else "1"
    return subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false",
         "-C", str(root), *args], capture_output=True, env=env, shell=False,
    )


def _git_kind(root):
    try:
        result = _git(root, "rev-parse", "--show-toplevel")
    except OSError:
        return "unavailable"
    if result.returncode:
        return "error" if (root / ".git").exists() else "non_git"
    top = Path(os.fsdecode(result.stdout.rstrip(b"\r\n"))).resolve()
    if top != root:
        raise ValueError("project_dir must be the Git worktree root")
    return "git"


def _checked_git(root, *args):
    result = _git(root, *args)
    if result.returncode:
        raise OSError("Git observation failed")
    return result.stdout


def _head(root):
    result = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
    return result.stdout.decode("ascii").strip() if result.returncode == 0 else None


def _inventory(root, sources):
    entries = {}
    raw = _checked_git(root, "ls-files", "--stage", "-z", "--", *sources)
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, name = item.split(b"\t", 1)
        mode, blob, stage = metadata.decode("ascii").split()
        rel = os.fsdecode(name)
        entry = entries.setdefault(rel, {"tracked": True, "index": [], "status": "  "})
        entry["index"].append({"mode": mode, "blob": blob, "stage": int(stage)})
    raw = _checked_git(root, "ls-files", "--others", "--exclude-standard", "-z", "--", *sources)
    for item in raw.split(b"\0"):
        if item:
            entries[os.fsdecode(item)] = {"tracked": False, "index": [], "status": "??"}
    # No rename folding: both the removed and added paths stay in their selected scopes.
    raw = _checked_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                       "--ignored=no", "--no-renames", "--", *sources)
    for item in raw.split(b"\0"):
        if item:
            rel = os.fsdecode(item[3:])
            entry = entries.setdefault(rel, {"tracked": item[:2] != b"??", "index": []})
            entry["status"] = item[:2].decode("ascii")
    raw = _checked_git(root, "ls-files", "-v", "-z", "--", *sources)
    for item in raw.split(b"\0"):
        if item and (chr(item[0]).islower() or item[:1] == b"S"):
            entries[os.fsdecode(item[2:])]["index_visibility_limited"] = True
    return entries


def _walk(root, sources, excluded):
    entries = {}

    def visit(rel):
        if _excluded(rel):
            excluded.append({"path": rel, "reason": "built_in_exclusion"})
            return
        path = _path(root, rel)
        if path.is_dir():
            for child in sorted(path.iterdir()):
                visit(child.relative_to(root).as_posix())
        else:
            entries[rel] = {"tracked": None, "index": [], "status": None}

    for source in sources:
        visit(source)
    return entries


def _snapshot(root, sources, kind, strict_paths):
    errors, excluded, files = [], [], []
    head = None
    entries = {}
    try:
        if kind == "git":
            head = _head(root)
            if head is None:
                errors.append({"reason": "head_unavailable_or_unborn"})
            entries = _inventory(root, sources)
        elif kind == "non_git":
            entries = _walk(root, sources, excluded)
        else:
            errors.append({"reason": "git_" + kind})
    except (OSError, ValueError) as exc:
        if strict_paths and isinstance(exc, ValueError):
            raise
        errors.append({"reason": "inventory_failed", "error_type": type(exc).__name__})
    for rel, entry in sorted(entries.items()):
        if _excluded(rel):
            excluded.append({"path": rel, "reason": "built_in_exclusion"})
            continue
        item = dict(entry, path=rel, sha256=None, exists=False, raw_matches_index=False)
        status = entry["status"]
        item.update(staged=status is not None and status[0] not in " ?",
                    unstaged=status is not None and status[1] not in " ?",
                    new=status == "??" or (status is not None and "A" in status),
                    deleted=status is not None and "D" in status)
        try:
            path = _path(root, _relative(rel))
            if any(row["mode"] in {"120000", "160000"} for row in entry["index"]):
                raise ValueError("symlink/submodule sources are not supported: " + rel)
            if entry.get("index_visibility_limited"):
                errors.append({"path": rel, "reason": "assume_unchanged_or_skip_worktree"})
            if path.exists():
                before = path.stat()
                if not stat.S_ISREG(before.st_mode):
                    raise ValueError("source must be a regular file: " + rel)
                digest = hashlib.sha256()
                index = entry["index"]
                blob_digest = None
                if len(index) == 1 and index[0]["stage"] == 0:
                    blob_digest = hashlib.new("sha256" if len(index[0]["blob"]) == 64 else "sha1")
                    blob_digest.update(f"blob {before.st_size}\0".encode("ascii"))
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                        if blob_digest is not None:
                            blob_digest.update(chunk)
                after = path.stat()
                item.update(exists=True, sha256=digest.hexdigest(), size=after.st_size,
                            mode=stat.S_IMODE(after.st_mode))
                if blob_digest is not None:
                    item["raw_matches_index"] = blob_digest.hexdigest() == index[0]["blob"]
                if (before.st_size, before.st_mtime_ns, before.st_ctime_ns, before.st_ino) != (
                        after.st_size, after.st_mtime_ns, after.st_ctime_ns, after.st_ino):
                    errors.append({"path": rel, "reason": "changed_during_hash"})
            else:
                item["deleted"] = True
                if not entry["tracked"]:
                    errors.append({"path": rel, "reason": "file_disappeared"})
        except (OSError, ValueError) as exc:
            if strict_paths and isinstance(exc, ValueError):
                raise
            errors.append({"path": rel, "reason": "file_observation_failed",
                           "error_type": type(exc).__name__})
        files.append(item)
    if kind == "git":
        try:
            if _head(root) != head or _inventory(root, sources) != entries:
                errors.append({"reason": "git_changed_during_snapshot"})
        except (OSError, ValueError):
            errors.append({"reason": "git_recheck_failed"})
    if not files:
        errors.append({"reason": "no_observed_files"})
    fingerprint = hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=True,
                                            separators=(",", ":")).encode("ascii")).hexdigest()
    return {"observed_at": _now(), "git": kind, "head": head, "sources": sources,
            "files": files, "fingerprint": fingerprint, "complete": not errors,
            "errors": errors, "excluded": excluded,
            "scoped_dirty": (any(f["status"] != "  " or f["deleted"] for f in files)
                             if kind == "git" else None),
            "coverage": LIMITATIONS[:4]}


def _sources(root, sources, kind):
    if isinstance(sources, (str, bytes)) or not sources:
        raise ValueError("at least one explicit --source is required")
    sources = sorted(set(_relative(source) for source in sources))
    if not sources:
        raise ValueError("at least one explicit --source is required")
    for rel in sources:
        path = _path(root, rel)
        if _excluded(rel):
            raise ValueError("source is excluded by policy: " + rel)
        if not path.exists():
            try:
                tracked = kind == "git" and any(
                    entry["tracked"] for entry in _inventory(root, [rel]).values())
            except OSError:
                tracked = False
            if not tracked:
                raise ValueError("source does not exist and is not a tracked deletion: " + rel)
        if kind == "git":
            result = _git(root, "check-ignore", "-q", "--", rel)
            if result.returncode == 0:
                raise ValueError("source is Git-ignored: " + rel)
            if result.returncode not in (0, 1):
                raise ValueError("could not validate source ignore coverage")
    return sources


def capture_source_snapshot(project_dir, sources):
    """Observe explicit relative scopes without writing files or changing Git state.

    Invalid paths raise ValueError/OSError. Collection failures are instead reported
    in complete/errors; a partial fingerprint must not be treated as an identity.
    """
    root = _root(project_dir)
    kind = _git_kind(root)
    scopes = _sources(root, sources, kind)
    return _snapshot(root, scopes, kind, strict_paths=True)


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

    Source identity is independent of command success. Startup failure returns 127;
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
    kind = _git_kind(root)
    scopes = _sources(root, sources, kind)
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
    pre = _snapshot(root, scopes, kind, strict_paths=True)
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
    post = _snapshot(root, scopes, kind, strict_paths=False)
    changed = pre["fingerprint"] != post["fingerprint"]
    identity_complete = pre["complete"] and post["complete"]
    clean_commit = (identity_complete and not changed and pre["head"] is not None
                    and pre["head"] == post["head"] and not pre["scoped_dirty"]
                    and not post["scoped_dirty"] and not pre["excluded"] and not post["excluded"]
                    and all(f["raw_matches_index"] for f in pre["files"] + post["files"]))
    report = {"schema_version": 1, "kind": "explicit_verification", "run_id": run_id,
              "command": {"argv": list(command), "cwd": work_rel, "exit_code": exit_code,
                          "started_at": started, "finished_at": finished,
                          "duration_seconds": duration, "launch_error": launch_error},
              "source_pre": pre, "source_post": post, "source_changed": changed,
              "head_changed": pre["head"] != post["head"],
              "identity_complete": identity_complete,
              "tested_commit": pre["head"] if clean_commit else None,
              "identity": "scoped_clean_commit" if clean_commit else (
                  "incomplete" if not identity_complete else "changed" if changed else "observed_content"),
              "limitations": LIMITATIONS}
    # Revalidate after the child, then exclusive-create: never replace a prior report.
    output = _output(root, evidence, scopes)
    payload = json.dumps(report, ensure_ascii=True, indent=2) + "\n"
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
    return report, exit_code
