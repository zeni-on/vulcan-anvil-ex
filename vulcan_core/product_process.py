"""Experimental Product state contracts. Pure functions; no CLI activation or writes.

Decisions and observations are supplied by trusted callers. This module checks
their binding, not the identity of a human or the truth/coverage of a test report.
"""

from copy import deepcopy
import hashlib
import json


MODEL = "product-iterative-v1"
STAGES = ("planning", "impl", "acceptance")
STATES = STAGES + ("completed",)
ACTIONS = {"implement", "verify", "fix", "accept"}


class ProcessContractError(ValueError):
    pass


def _require(condition, message):
    if not condition:
        raise ProcessContractError(message)


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _object(value, name):
    _require(isinstance(value, dict), name + " must be an object")
    return value


def _strings(value, name, nonempty=True):
    _require(isinstance(value, list) and (bool(value) or not nonempty)
             and all(_text(item) for item in value), name + " must be a string list")
    _require(len(value) == len(set(value)), name + " contains duplicates")
    return sorted(value)


def _reference(value):
    value = _object(value, "reference")
    _require(set(value) == {"ref", "revision"} and all(_text(v) for v in value.values()),
             "reference needs ref and immutable revision")
    _require(value["revision"].lower() not in {"head", "main", "dev", "latest", "tbd"},
             "reference revision cannot be a moving label")
    return dict(value)


def _digest(value):
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def normalize_scope(scope):
    scope = _object(scope, "scope")
    _require(set(scope) == {"work", "related_ids", "contracts", "tests", "required_checks"},
             "scope needs work, related_ids, contracts, tests and required_checks")
    result = {"work": _reference(scope["work"]),
              "related_ids": _strings(scope["related_ids"], "related_ids", False),
              "required_checks": _strings(scope["required_checks"], "required_checks", False)}
    for name in ("contracts", "tests"):
        _require(isinstance(scope[name], list), name + " must be a reference list")
        refs = [_reference(item) for item in scope[name]]
        _require(len({item["ref"] for item in refs}) == len(refs), name + " repeats a reference")
        result[name] = sorted(refs, key=lambda item: item["ref"])
    return result


def scope_key(scope):
    """No new user-assigned ID: derive identity from the existing scoped sources."""
    return _digest(normalize_scope(scope))


def process_model(session):
    session = _object(session, "session")
    if "process_model" not in session:
        return "legacy"
    _require(session["process_model"] == MODEL, "unsupported process_model")
    _require(session.get("profile") == "product", "iterative process requires Product")
    return MODEL


def require_legacy(session):
    """Stop legacy consumers before treating a new state as an old Gate."""
    model = process_model(session)
    _require(model == "legacy", "product-iterative-v1 is experimental; legacy writes/checks are disabled; use status --check for scoped diagnostics")


def new_session(scope):
    normalized = normalize_scope(scope)
    return {"profile": "product", "process_model": MODEL, "current_gate": "planning",
            "gate_status": {stage: "in-progress" if stage == "planning" else "pending" for stage in STAGES},
            "current_work": {"scope": normalized, "scope_key": scope_key(normalized), "decisions": []},
            "work_history": []}


def _validate(session):
    _require(process_model(session) == MODEL, "legacy sessions require the legacy workflow")
    _require(session.get("current_gate") in STATES, "invalid Product state")
    statuses = _object(session.get("gate_status"), "gate_status")
    stage = session["current_gate"]
    expected = {name: "done" if stage == "completed" or STAGES.index(name) < STAGES.index(stage)
                else "in-progress" if name == stage else "pending" for name in STAGES}
    _require(statuses == expected, "gate_status conflicts with current_gate")
    work = _object(session.get("current_work"), "current_work")
    _require(work.get("scope_key") == scope_key(work.get("scope")), "current scope identity mismatch")
    _require(isinstance(work.get("decisions"), list), "decisions must be a list")
    _require(isinstance(session.get("work_history"), list), "work_history must be a list")
    for item in session["work_history"]:
        item = _object(item, "history entry")
        prior = _object(item.get("work"), "historical work")
        _require(item.get("current_gate") in STATES, "invalid historical state")
        _require(prior.get("scope_key") == scope_key(prior.get("scope")), "historical scope identity mismatch")
    for decision in work["decisions"]:
        _validate_decision(decision, work["scope_key"])
    if stage in {"impl", "acceptance", "completed"}:
        _authorize(work, "implement")
    if stage in {"acceptance", "completed"}:
        _authorize(work, "verify")
    if stage == "completed":
        key = verification_key(work["scope"], work.get("verification"), work.get("basis"))
        _require(key == work.get("verification_key"), "completed result identity mismatch")
        _authorize(work, "accept", verified=key)
    return work


def _basis(value):
    """Keep the declared environment, without collecting a source identity."""
    value = _object(value, "verification basis")
    result = {"environment": _reference(value.get("environment"))}
    # Preserve the original digest of saved v1 approvals, not a freshness check.
    # New execution records and requests do not need this legacy field.
    if isinstance(value.get("source"), dict):
        source = value["source"]
        result["source"] = {key: deepcopy(source.get(key)) for key in ("fingerprint", "complete", "errors", "sources")}
        if isinstance(result["source"]["sources"], list):
            result["source"]["sources"] = _strings(result["source"]["sources"], "legacy source scopes", False)
    return result


def _validate_decision(decision, key):
    decision = _object(decision, "decision")
    _require(decision.get("scope_key") == key, "decision belongs to another scope/revision")
    actions = _strings(decision.get("actions"), "decision actions")
    _require(set(actions) <= ACTIONS, "invalid decision action; release authority is separate")
    _require(_text(decision.get("actor")), "decision actor is required")
    _require(_text(decision.get("authority")) and decision["authority"] in {"user", "delegated"},
             "decision authority is required")
    if decision["authority"] == "delegated":
        _reference(decision.get("authority_ref"))
    _reference(decision.get("evidence"))
    if "accept" in actions:
        _require(actions == ["accept"] and _text(decision.get("verification_key")),
                 "acceptance must identify a verification result, separately from execution permission")


def _authorize(work, action, decision=None, verified=None):
    candidates = work["decisions"] + ([decision] if decision is not None else [])
    if decision is not None:
        _validate_decision(decision, work["scope_key"])
    for item in candidates:
        if action in item["actions"] and (action != "accept" or item.get("verification_key") == verified):
            return
    raise ProcessContractError("missing scoped " + action + " decision")


def _ready(work, readiness, purpose):
    readiness = _object(readiness, "readiness")
    _require(readiness.get("scope_key") == work["scope_key"], "readiness belongs to another scope")
    _require(readiness.get("ready") is True, "scope is not ready")
    _require(readiness.get("purpose") == purpose, "wrong readiness purpose")
    _reference(readiness.get("evidence"))
    scope = work["scope"]
    _require(bool(scope["related_ids"] and scope["contracts"] and scope["tests"] and scope["required_checks"]),
             "implementation needs contract, related IDs, test definition and required checks")


def verification_key(scope, verification, current_basis):
    """Bind required results to the agreed scope and declared environment."""
    scope = normalize_scope(scope)
    verification = _object(verification, "verification")
    _require(verification.get("scope_key") == scope_key(scope), "verification belongs to another scope")
    tested = _basis(verification.get("basis"))
    _require(tested["environment"] == _basis(current_basis)["environment"], "stale verification environment")
    rows = verification.get("results")
    _require(isinstance(rows, list) and bool(rows), "verification results are missing")
    normalized = []
    for row in rows:
        row = _object(row, "result")
        _require(_text(row.get("id")), "result id is required")
        _require(row.get("status") == "Pass", "required result is not Pass")
        # Preserve argv order; duplicate arguments can be intentional.
        command = row.get("command")
        _require(isinstance(command, list) and bool(command) and all(_text(arg) for arg in command),
                 "executed command argv is required")
        normalized.append({"id": row["id"], "status": "Pass", "command": command,
                           "evidence": _reference(row.get("evidence"))})
    _require(sorted(row["id"] for row in normalized) == scope["required_checks"],
             "results must cover each required check exactly once")
    return _digest({"scope_key": scope_key(scope), "basis": tested,
                    "results": sorted(normalized, key=lambda row: row["id"])})


def assess_transition(session, target, *, readiness=None, decision=None, verification=None,
                      current_basis=None, reason=None):
    """Read-only mechanical eligibility. Does not run tests or grant authority."""
    try:
        work = _validate(session)
        start = session["current_gate"]
        _require(target in STATES, "invalid target")
        if decision is not None:
            _validate_decision(decision, work["scope_key"])
        if (start, target) == ("planning", "impl"):
            _ready(work, readiness, "implementation")
            _authorize(work, "implement", decision)
        elif (start, target) == ("impl", "acceptance"):
            _ready(work, readiness, "handoff")
            _basis(current_basis)
            _authorize(work, "verify", decision)
        elif (start, target) == ("acceptance", "impl"):
            _reference(reason)
            _authorize(work, "fix", decision)
        elif start in {"impl", "acceptance"} and target == "planning":
            _reference(reason)
        elif (start, target) == ("acceptance", "completed"):
            key = verification_key(work["scope"], verification, current_basis)
            _authorize(work, "accept", decision, key)
        else:
            raise ProcessContractError("transition is not allowed; open a scoped next work item after completion")
        return {"allowed": True, "reasons": [], "scope_key": work["scope_key"], "target": target}
    except ProcessContractError as error:
        return {"allowed": False, "reasons": [str(error)], "target": target}


def _archive(session, reason):
    session["work_history"].append({"current_gate": session["current_gate"],
                                     "work": deepcopy(session["current_work"]), "reason": deepcopy(reason)})


def advance(session, target, **inputs):
    """Return a new state only after eligibility checks; caller owns persistence."""
    assessment = assess_transition(session, target, **inputs)
    _require(assessment["allowed"], "; ".join(assessment["reasons"]))
    result = deepcopy(session)
    _archive(result, inputs.get("reason"))
    work = result["current_work"]
    decision = inputs.get("decision")
    if decision is not None and decision not in work["decisions"]:
        work["decisions"].append(deepcopy(decision))
    if target == "planning":
        # Replanning invalidates prior permissions until this basis is confirmed.
        work["decisions"] = []
    elif target != "completed":
        work["decisions"] = [item for item in work["decisions"] if "accept" not in item["actions"]]
    for name in ("readiness", "verification", "verification_key", "basis"):
        work.pop(name, None)
    if inputs.get("readiness") is not None:
        work["readiness"] = deepcopy(inputs["readiness"])
    if inputs.get("current_basis") is not None:
        work["basis"] = _basis(inputs["current_basis"])
    if target == "completed":
        work["verification"] = deepcopy(inputs["verification"])
        work["verification"]["basis"] = _basis(inputs["verification"]["basis"])
        work["verification_key"] = verification_key(work["scope"], inputs["verification"], inputs["current_basis"])
    result["current_gate"] = target
    result["gate_status"] = {stage: "done" if target == "completed" or STAGES.index(stage) < STAGES.index(target)
                             else "in-progress" if stage == target else "pending" for stage in STAGES}
    return result


def open_work(session, scope, *, reason, target="planning", readiness=None, decision=None):
    """Preserve past outcomes when opening new work or revising the current scope."""
    _validate(session)
    _reference(reason)
    _require(session["current_gate"] == "completed" or target == "planning",
             "active work must return to planning before replacing its scope")
    _require(_text(target) and target in {"planning", "impl"},
             "new work starts in planning or authorized local implementation")
    used_keys = {session["current_work"]["scope_key"]}
    used_keys.update(item["work"]["scope_key"] for item in session["work_history"])
    _require(scope_key(scope) not in used_keys, "next work needs a new work/basis revision, not a recycled approval scope")
    result = deepcopy(session)
    _archive(result, reason)
    fresh = new_session(scope)
    for field in ("current_gate", "gate_status", "current_work"):
        result[field] = fresh[field]
    if target == "impl":
        result = advance(result, "impl", readiness=readiness, decision=decision)
    return result


def describe(session):
    """Diagnostic only; readiness, acceptance and release are not inferred here."""
    try:
        model = process_model(session)
        if model == "legacy":
            return {"process_model": "legacy", "use_legacy": True}
        work = _validate(session)
        return {"process_model": model, "runtime_enabled": False, "checks_enabled": True,
                "session_writes_enabled": True, "status": "experimental",
                "dashboard_read_enabled": True, "operating_preview_enabled": True,
                "publication_enabled": False,
                "current_gate": session["current_gate"], "scope_key": work["scope_key"],
                "work": deepcopy(work["scope"]["work"]), "history_count": len(session["work_history"]),
                "message": "Experimental state, scoped checks, Dashboard reads and operating previews are available; general init/migration and PR publication are not enabled."}
    except ProcessContractError as error:
        return {"status": "unsupported_or_invalid", "runtime_enabled": False, "message": str(error)}
