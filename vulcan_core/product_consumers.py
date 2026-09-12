"""Read-only operating views for the iterative Product process.

Persisted acceptance is not release authority. These consumers never checkout,
write session state, run QA from document text, or publish a PR.
"""

import os
import json
from pathlib import Path
import subprocess

from . import evidence, product_process as process, product_readiness as readiness, product_session


def load(project_dir):
    """Return a validated iterative session, or None for legacy/missing sessions."""
    path = Path(project_dir) / "session.json"
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as stream:
        session = json.load(stream)
    if not isinstance(session, dict) or "process_model" not in session:
        return None
    session, _ = product_session._load(evidence._root(project_dir))
    process._validate(session)
    return session


def _git(root, *args):
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=10)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def branch_context(project_dir, session, workflow):
    work = process._validate(session)
    root = evidence._root(project_dir)
    toplevel = _git(root, "rev-parse", "--show-toplevel")
    repository = bool(toplevel and os.path.normcase(str(Path(toplevel).resolve())) == os.path.normcase(str(root)))
    current = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD") if repository else None
    head = _git(root, "rev-parse", "--verify", "HEAD") if repository else None
    integration = workflow.get("integration_branch") or "dev"
    branch_mode = workflow.get("branch_mode", "audit")
    required = (branch_mode not in {"none", "single", "disabled"}
                and workflow.get("impl_uses_integration_branch", True)
                and session["current_gate"] in {"impl", "acceptance", "completed"})
    ambiguous = not repository and (bool(toplevel) or (root / ".git").exists())
    status = ("unavailable" if ambiguous else "unmanaged" if not repository else "not_required" if not required
              else "matched" if current == integration else "mismatch")
    return {"process_model": process.MODEL, "current_gate": session["current_gate"],
            "scope_key": work["scope_key"], "workspace": str(root),
            "repository": repository, "current_branch": current, "head_commit": head,
            "main_branch": workflow.get("main_branch") or "main", "integration_branch": integration,
            "integration_required": bool(required), "branch_status": status,
            "qa_workspace": "current_integration_workspace" if required else "current_workspace",
            "qa_worktree_created": False, "release_authorized": False}


def require_qa_workspace(project_dir, session, workflow):
    """Acceptance execution uses the agreed integration workspace, not a new QA tree."""
    context = branch_context(project_dir, session, workflow)
    if session["current_gate"] == "acceptance" and context["branch_status"] == "unavailable":
        raise ValueError("cannot verify the Git workspace root; resolve branch-status before acceptance execution")
    if (session["current_gate"] == "acceptance" and context["branch_status"] == "mismatch"
            and workflow.get("enforce_branch_guard", True)):
        raise ValueError("acceptance verification requires the agreed integration branch "
                         + str(context["integration_branch"]) + "; inspect branch-status and switch explicitly")
    # A synthetic non-Git pilot can still execute its explicitly authorized tests.
    return context


def release_preview(project_dir, session, workflow, parse_tables, *, base="", head="", title=""):
    """Recheck a scoped candidate without creating a body file or invoking gh."""
    context = branch_context(project_dir, session, workflow)
    checked = readiness.collect(project_dir, session, parse_tables)
    work = session["current_work"]
    base = base or workflow.get("release_merge_to") or context["main_branch"]
    head = head or context["integration_branch"]
    blockers = []
    if session["current_gate"] != "completed":
        blockers.append("current scope has not been accepted")
    if checked["status"] != "ready":
        blockers.append("current scoped documents or execution evidence are missing, changed or failed")
    if not context["repository"]:
        blockers.append("no Git repository rooted at this workspace")
    else:
        dirty = _git(project_dir, "status", "--porcelain", "--untracked-files=normal")
        if dirty is None or dirty:
            blockers.append("candidate workspace must be clean; commit or resolve pending changes explicitly")
        if context["branch_status"] == "mismatch" or context["current_branch"] != head:
            blockers.append("candidate head must be the current agreed integration branch")
        if base == head:
            blockers.append("release base and head must differ")
        for name in (base, head):
            # Explicit branch refs avoid interpreting command options/revisions as branches.
            if (not isinstance(name, str)
                    or _git(project_dir, "check-ref-format", "refs/heads/" + name) is None
                    or not _git(project_dir, "show-ref", "--verify", "--hash", "refs/heads/" + name)):
                blockers.append("local branch not found: " + str(name))
    obligations = checked.get("unresolved_obligations", "unknown")
    return {"status": "candidate" if not blockers else "blocked", "process_model": process.MODEL,
            "title": title or "Product release candidate", "base": base, "head": head,
            "current_gate": session["current_gate"], "work": work["scope"]["work"],
            "scope_key": work["scope_key"], "verification_key": checked.get("verification_key"),
            "branch": context, "checks": checked, "blockers": blockers,
            "unresolved_obligations": obligations, "release_authorized": False,
            "publication_enabled": False,
            "message": "Preview only. Review release scope, unresolved obligations and independent approval before publication. No PR, push or deployment is performed."}


def render_branch(context):
    return "\n".join(f"{key}: {value}" for key, value in context.items())


def render_release(result):
    lines = ["Product release preview: " + result["status"],
             f"  work: {result['work']['ref']} ({result['work']['revision']})",
             f"  branch: {result['head']} -> {result['base']}",
             f"  current scoped checks: {result['checks']['status']}",
             f"  unresolved obligations: {result['unresolved_obligations']}"]
    lines.extend("  blocked: " + item for item in result["blockers"])
    lines.append(readiness.render(result["checks"]))
    lines.extend(["  release_authorized: False", result["message"]])
    return "\n".join(lines)
