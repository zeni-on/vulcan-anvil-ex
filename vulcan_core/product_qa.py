"""Run-free native QA handoff previews, not a dispatcher or approval service."""

from copy import deepcopy

from . import evidence, product_consumers, product_process as process, product_readiness as readiness, product_session


NATIVE_RUNNERS = {"native", "subagent", "thread", "agy-branch-agent"}


def require_acceptance_context(project_dir, session, workflow, parse_tables):
    """Recheck the current QA assignment basis before handoff or explicit execution."""
    work = process._validate(session)
    if session["current_gate"] != "acceptance":
        raise ValueError("Run-free QA handoff requires the authorized acceptance stage")
    product_session.require_verification_permission(session)
    workspace = product_consumers.require_qa_workspace(project_dir, session, workflow)
    documents = readiness.document_readiness(project_dir, work["scope"], parse_tables)
    if not documents["ready"]:
        raise product_session.BlockedError("QA contracts or test plans changed or are incomplete", documents)
    basis = readiness.observe_basis(project_dir, work.get("basis"))
    return workspace, documents, basis


def handoff(project_dir, workflow, parse_tables, *, runner="native"):
    """Read scoped sources and prepare an empty result-return request without writes.

    The Orchestrator adds explicit argv/output paths before assigning a delegate.
    Results are not inferred from Markdown or an agent completion notification.
    """
    try:
        if runner not in NATIVE_RUNNERS:
            raise ValueError("Run-free QA preview supports native/subagent/thread/agy-branch-agent only")
        root = evidence._root(project_dir)
        session, raw = product_session._load(root)
        workspace, documents, basis = require_acceptance_context(root, session, workflow, parse_tables)
        work = session["current_work"]
        _, current = product_session._load(root)
        if current != raw:
            raise product_session.ConflictError("session changed during QA preview; reload before assigning")
        return {
            "status": "candidate", "kind": "product_qa_handoff", "process_model": process.MODEL,
            "current_gate": "acceptance", "runner_mode": runner,
            "session_revision": product_session.revision(raw),
            "scope": deepcopy(work["scope"]), "scope_key": work["scope_key"],
            "workspace": workspace, "documents": documents, "basis": basis,
            "authority": "verify_only", "dispatched": False, "release_authorized": False,
            "assignment_required": ["delegate identity", "explicit command argv and cwd",
                                    "exact new evidence/log/report paths and permitted runtime outputs"],
            "return_request": {
                "process_model": process.MODEL, "expected_session_revision": product_session.revision(raw),
                "action": "advance", "target": "completed",
                "verification": {"scope_key": work["scope_key"], "basis": basis, "results": []},
            },
            "return_rules": [
                "Return the delegate, scoped check IDs, actual outcomes, command observations, logs and blockers in the existing summary.",
                "Fill verification.results from reviewed executions; the empty request is deliberately not acceptable.",
                "Preserve Fail, Not Run and environment_blocked; never turn completion or exit zero alone into QA Pass.",
                "The Orchestrator previews session --process-request without a decision, reviews the results, then supplies a separate accept decision.",
            ],
            "limitations": [
                "Preview only: no agent launch, commands, directories, Run, state writes or branch changes.",
                "verify_only is a handoff contract, not an OS sandbox; the Orchestrator restricts delegate tools and writable paths.",
                "No source freshness, live environment, test-count or semantic coverage certification. Recheck relevant changes before dispatch and acceptance.",
            ],
        }
    except product_session.ConflictError as error:
        return {"status": "conflict", "dispatched": False, "message": str(error)}
    except product_session.BlockedError as error:
        return {"status": "blocked", "dispatched": False, "message": str(error), "checks": error.checks}
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        return {"status": "blocked", "dispatched": False, "message": str(error)}


def render(result):
    if result["status"] != "candidate":
        lines = ["Product QA handoff: " + result["status"], result["message"]]
        lines.extend(f"  {item['path'] or '-'}: {item['message']}" for item in (result.get("checks") or {}).get("issues", []))
        return "\n".join(lines)
    lines = ["Product QA handoff: candidate (not dispatched)",
             "  work: " + result["scope"]["work"]["ref"],
             "  workspace: " + result["workspace"]["workspace"],
             "  authority: verify_only", "  required checks: " + ", ".join(result["scope"]["required_checks"])]
    for name in ("contracts", "tests"):
        lines.extend("  " + name + ": " + ref["ref"] for ref in result["scope"][name])
    lines.append("  Before assignment: " + "; ".join(result["assignment_required"]))
    lines.extend(result["return_rules"])
    lines.append("Use --json for the scoped payload and empty return_request. No new Run is required.")
    return "\n".join(lines)
