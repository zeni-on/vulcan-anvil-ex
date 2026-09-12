"""Explicit branch preparation for the opt-in Product process.

This changes only the Git branch, never the session, approvals or commit history.
Existing branches with different trees require a separately reviewed Git action.
"""

import os
from contextlib import contextmanager
from pathlib import Path
import queue
import subprocess
import tempfile
import threading

from . import evidence, product_process as process, product_readiness as readiness, product_session as store


def _git(root, *args, codes=(0,)):
    result = subprocess.run(["git", "-c", "core.fsmonitor=false", *args], cwd=root,
                            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, capture_output=True, timeout=30)
    if result.returncode not in codes:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise store.BlockedError("Git operation failed: " + (detail or str(result.returncode)))
    return result


def _text(root, *args):
    return _git(root, *args).stdout.decode("utf-8", errors="replace").strip()


def _branch_name(root, name):
    if not isinstance(name, str) or not name or name.startswith("-"):
        raise ValueError("workflow branches must be valid local branch names")
    _git(root, "check-ref-format", "refs/heads/" + name)
    return name


def _inspect(root, resolve_workflow, parse_tables, *, locked=False):
    config = evidence._path(root, "vulcan.config.json")
    config_before = config.read_bytes() if config.is_file() else None
    if config_before is not None:
        decoded = store.decode(config_before)
        if "workflow" in decoded and not isinstance(decoded["workflow"], dict):
            raise ValueError("workflow configuration must be an object; defaults cannot replace malformed policy")
    workflow = resolve_workflow(root)
    if not isinstance(workflow, dict):
        raise ValueError("workflow resolver must return a policy object")
    if not isinstance(workflow.get("branch_mode", "audit"), str) or type(workflow.get("impl_uses_integration_branch", True)) is not bool:
        raise ValueError("workflow branch mode/implementation policy has an invalid type")
    session, raw = store._load(root)
    work = process._validate(session)
    if session["current_gate"] != "impl":
        raise store.BlockedError("branch-start requires the authorized impl stage; no state transition is performed")
    process._authorize(work, "implement")
    if (workflow.get("branch_mode") in {"none", "single", "disabled"}
            or not workflow.get("impl_uses_integration_branch", True)):
        raise store.BlockedError("workflow uses the current workspace; no integration branch needs to be started")

    toplevel = _text(root, "rev-parse", "--show-toplevel")
    if os.path.normcase(str(Path(toplevel).resolve())) != os.path.normcase(str(root)):
        raise store.BlockedError("branch-start requires a Git repository rooted at the project workspace")
    current = _text(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    head = _text(root, "rev-parse", "--verify", "HEAD")
    main = _branch_name(root, workflow.get("main_branch") or "main")
    integration = _branch_name(root, workflow.get("integration_branch") or "dev")
    if main == integration:
        raise store.BlockedError("main and integration branches must differ")
    if current not in {main, integration}:
        raise store.BlockedError("start from the agreed main branch or current integration branch, not a worker branch")

    checks = readiness.document_readiness(root, work["scope"], parse_tables)
    if not checks["ready"]:
        raise store.BlockedError("current scoped contracts or test plans are not ready", checks)

    exists = _git(root, "show-ref", "--verify", "--quiet", "refs/heads/" + integration, codes=(0, 1))
    target = _text(root, "rev-parse", "refs/heads/" + integration) if exists.returncode == 0 else None
    operation = "none" if current == integration else "switch" if target else "create"
    if operation == "switch":
        if _text(root, "rev-parse", target + "^{tree}") != _text(root, "rev-parse", head + "^{tree}"):
            raise store.BlockedError("existing integration branch has different content; review and switch explicitly, without replacing the current session")

    dirty = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
    if operation != "none":
        # An impl transition can leave session.json dirty. Same-tree switching
        # carries it intact; no pre-test commit or auto-normalization is needed.
        allowed = {b" M session.json", b"M  session.json", b"MM session.json",
                   b"A  session.json", b"AM session.json", b"?? session.json"}
        if locked:
            allowed.add(b"?? .vulcan/product-process.lock")
        if any(entry not in allowed for entry in dirty.split(b"\0") if entry):
            raise store.BlockedError("resolve pending changes other than session.json before switching branches; no stash or discard is performed")
    config_after = config.read_bytes() if config.is_file() else None
    if config_before != config_after:
        raise store.ConflictError("workflow changed during policy resolution; reload before retrying")
    snapshot = (raw, head, target, dirty, config_after)
    result = {"status": "ready", "applied": False, "process_model": process.MODEL,
              "current_gate": session["current_gate"], "scope_key": work["scope_key"],
              "current_branch": current, "main_branch": main, "integration_branch": integration, "operation": operation,
              "session_changed": False, "release_authorized": False,
              "message": "Preview only; use --apply for this branch preparation. No session, commit or push is created."}
    return result, snapshot


@contextmanager
def _hold_target(root, name, commit, hooks):
    """Git's prepared verify transaction holds the existing target ref stable."""
    proc = subprocess.Popen(["git", "-c", "core.hooksPath=" + hooks,
                             "-c", "core.filesRefLockTimeout=1000", "update-ref", "--stdin"],
                            cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    replies = queue.Queue()

    def read_ack():
        for _ in range(2):
            replies.put(proc.stdout.readline())

    reader = threading.Thread(target=read_ack, daemon=True)
    reader.start()
    try:
        command = f"start\nverify refs/heads/{name} {commit}\nprepare\n"
        proc.stdin.write(command.encode("utf-8"))
        proc.stdin.flush()
        for expected in (b"start: ok\n", b"prepare: ok\n"):
            if replies.get(timeout=10) != expected:
                raise store.ConflictError("integration ref changed or cannot be locked; inspect Git before retrying")
        yield
    except queue.Empty:
        raise store.ConflictError("Git ref verification timed out; inspect Git locks before retrying") from None
    finally:
        try:
            proc.stdin.write(b"abort\n")
            proc.stdin.flush()
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise store.ConflictError("Git ref lock cleanup timed out; inspect Git locks before retrying") from None
        finally:
            reader.join(timeout=1)
            for stream in (proc.stdin, proc.stdout):
                try:
                    stream.close()
                except OSError:
                    pass


def start(project_dir, resolve_workflow, parse_tables, *, apply=False):
    """Preview by default; apply rechecks under the existing Product writer lock."""
    try:
        root = evidence._root(project_dir)
        if type(apply) is not bool or not callable(resolve_workflow):
            raise ValueError("apply must be a boolean and workflow must be resolved at inspection time")
        if not apply:
            return _inspect(root, resolve_workflow, parse_tables)[0]
        with store._lock(root) as warnings:
            result, observed = _inspect(root, resolve_workflow, parse_tables, locked=True)
            repeated, current = _inspect(root, resolve_workflow, parse_tables, locked=True)
            if observed != current or result != repeated:
                raise store.ConflictError("workspace changed during branch preparation; reload status before retrying")
            if result["operation"] == "none":
                result.update(status="unchanged", message="Already on the integration branch; nothing changed.")
            else:
                try:
                    # Do not run checkout hooks with product-code or publishing side effects.
                    with tempfile.TemporaryDirectory(prefix="vulcan-branch-hooks-") as hooks:
                        args = ["-c", "core.hooksPath=" + hooks, "switch", "--no-guess"]
                        if result["operation"] == "create":
                            _git(root, *args, "--create", result["integration_branch"], observed[1])
                        else:
                            with _hold_target(root, result["integration_branch"], observed[2], hooks):
                                _git(root, *args, result["integration_branch"])
                    actual_branch = _text(root, "symbolic-ref", "--quiet", "--short", "HEAD")
                    actual_head = _text(root, "rev-parse", "--verify", "HEAD")
                    _, actual_session = store._load(root)
                    verified, after = _inspect(root, resolve_workflow, parse_tables, locked=True)
                    expected_head = observed[2] or observed[1]
                    if (actual_branch != result["integration_branch"] or actual_session != observed[0]
                            or actual_head != expected_head or after[4] != observed[4]
                            or after[0] != observed[0] or after[1] != expected_head or after[2] != expected_head
                            or verified["integration_branch"] != result["integration_branch"]
                            or verified["current_branch"] != result["integration_branch"]):
                        raise store.ConflictError("branch/session changed during Git execution")
                except (OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.TimeoutExpired) as error:
                    # Git/another editor may have changed state before an error. Never
                    # roll back by checkout/reset or claim the workspace is unchanged.
                    return {"status": "conflict", "applied": None, "release_authorized": False,
                            "message": str(error) + "; inspect branch-status and session before retrying; no automatic rollback performed"}
                result.update(status="applied", applied=True, current_branch=actual_branch,
                              message="Integration branch prepared. Session, approvals, documents and commit history were not rewritten; no push performed.")
        if warnings:
            result["warnings"] = warnings
        return result
    except store.BlockedError as error:
        return {"status": "blocked", "applied": False, "message": str(error), "checks": error.checks}
    except store.ConflictError as error:
        return {"status": "conflict", "applied": False, "message": str(error)}
    except (OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.TimeoutExpired) as error:
        return {"status": "invalid", "applied": False, "message": str(error)}


def render(result):
    lines = ["Product branch preparation: " + result["status"]]
    if "operation" in result:
        lines.append(f"  {result['operation']}: {result['current_branch']} -> {result['integration_branch']}")
    lines.append("  " + result["message"])
    for issue in (result.get("checks") or {}).get("issues", []):
        lines.append(f"  {issue.get('path') or 'scope'}: {issue['message']}")
    return "\n".join(lines)
