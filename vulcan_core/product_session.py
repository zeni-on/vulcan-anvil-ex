"""Iterative Product session transactions, separate from legacy Gate writers.

The invoking Orchestrator owns real authority/provenance checks. Requests are
data, never executable instructions. Locking coordinates cooperating writers;
it cannot serialize an unrelated editor that ignores the protocol.
"""

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
import tempfile

from . import evidence, product_process as process, product_readiness as readiness


MAX_REQUEST_BYTES = 2_000_000
MAX_SESSION_BYTES = 8_000_000


class ConflictError(ValueError):
    pass


class BlockedError(ValueError):
    def __init__(self, message, checks=None):
        super().__init__(message)
        self.checks = checks


def revision(raw):
    return None if raw is None else "sha256:" + hashlib.sha256(raw).hexdigest()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("non-finite JSON number: " + value)

    try:
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=pairs, parse_constant=invalid_constant)
    except RecursionError:
        raise ValueError("JSON nesting exceeds the supported depth") from None
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value


def read_request(project_dir, reference, stdin):
    if reference == "-":
        raw = stdin.read(MAX_REQUEST_BYTES + 1)
    else:
        root = evidence._root(project_dir)
        path = evidence._path(root, evidence._relative(reference))
        if not path.is_file():
            raise ValueError("request must be a regular file")
        with path.open("rb") as stream:
            raw = stream.read(MAX_REQUEST_BYTES + 1)
    if len(raw) > MAX_REQUEST_BYTES:
        raise ValueError("process request exceeds size limit")
    return decode(raw)


def _load(root):
    path = evidence._path(root, "session.json")
    if not path.exists():
        return None, None
    if not path.is_file():
        raise ValueError("session must be a regular file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_SESSION_BYTES + 1)
    if len(raw) > MAX_SESSION_BYTES:
        raise ValueError("session exceeds size limit")
    return decode(raw), raw


def _validated_request(request):
    if not isinstance(request, dict) or request.get("process_model") != process.MODEL:
        raise ValueError("request requires explicit product-iterative-v1 process_model")
    action = request.get("action")
    fields = {"start": {"scope"}, "advance": {"target", "decision", "basis", "verification", "reason"},
              "open-work": {"scope", "target", "reason", "decision"}}
    if not isinstance(action, str) or action not in fields:
        raise ValueError("action must be start, advance or open-work")
    common = {"process_model", "expected_session_revision", "action"}
    if not common <= request.keys() or request.keys() - common - fields[action]:
        raise ValueError("missing request fields or unsupported fields")
    if action == "start":
        if "scope" not in request or request["expected_session_revision"] is not None:
            raise ValueError("start requires scope and null expected_session_revision")
    else:
        expected = request["expected_session_revision"]
        if not isinstance(expected, str) or not _is_revision(expected):
            raise ValueError("expected_session_revision must be the observed session SHA-256")
        if not isinstance(request.get("target"), str) or request["target"] not in process.STATES:
            raise ValueError("target must be a Product state, never a Gate/release operation")
        if action == "open-work" and not {"scope", "reason"} <= request.keys():
            raise ValueError("open-work requires scope and reason")
    return action


def _is_revision(value):
    return value.startswith("sha256:") and len(value) == 71 and all(c in "0123456789abcdef" for c in value[7:])


def _forward(root, session, request, parse_tables):
    staged = deepcopy(session)
    work = staged["current_work"]
    if "decision" in request:
        process._validate_decision(request["decision"], work["scope_key"])
        work["decisions"].append(deepcopy(request["decision"]))
    if "basis" in request:
        work["basis"] = deepcopy(request["basis"])
    if "verification" in request:
        work["verification"] = deepcopy(request["verification"])
    checked = readiness.collect(root, staged, parse_tables)
    if checked["status"] != "ready" or not checked["transition"]["allowed"]:
        raise BlockedError("scoped readiness, execution or authority is incomplete", checked)
    return checked


def _evaluate(root, session, request, parse_tables):
    action = request["action"]
    checked = None
    if action == "start":
        if session is not None:
            raise ValueError("start cannot replace an existing session; legacy migration is not supported")
        candidate = process.new_session(request["scope"])
    else:
        if session is None:
            raise ValueError("session does not exist; initialize a new Product project first")
        process._validate(session)
        target = request["target"]
        if action == "open-work":
            if target == "impl":
                fresh = process.new_session(request["scope"])
                checked = _forward(root, fresh, request, parse_tables)
            elif "decision" in request:
                raise ValueError("planning does not consume an implementation decision")
            candidate = process.open_work(session, request["scope"], target=target, reason=request["reason"],
                readiness=checked["readiness"] if checked else None, decision=request.get("decision"))
        else:
            start = session["current_gate"]
            if (start, target) in {("planning", "impl"), ("impl", "acceptance"), ("acceptance", "completed")}:
                allowed = {"planning": {"decision"}, "impl": {"decision", "basis"},
                           "acceptance": {"decision", "verification"}}[start]
                if (request.keys() & {"decision", "basis", "verification", "reason"}) - allowed:
                    raise ValueError("request includes inputs not consumed at this boundary")
                required = {"impl": "basis", "acceptance": "verification"}.get(start)
                if required and required not in request:
                    raise ValueError("this boundary requires explicit " + required)
                checked = _forward(root, session, request, parse_tables)
                candidate = process.advance(session, target, readiness=checked["readiness"],
                    current_basis=checked["current_basis"], verification=request.get("verification"),
                    decision=request.get("decision"))
            else:
                if "basis" in request or "verification" in request or (target == "planning" and "decision" in request):
                    raise ValueError("backward transition cannot consume forward evidence/authority")
                candidate = process.advance(session, target, reason=request.get("reason"), decision=request.get("decision"))
    process._validate(candidate)
    return candidate, checked


@contextmanager
def _lock(root):
    folder = evidence._path(root, ".vulcan")
    folder.mkdir(exist_ok=True)
    path = evidence._path(root, ".vulcan/product-process.lock")
    try:
        stream = path.open("x", encoding="ascii")
    except FileExistsError:
        raise ConflictError("process writer lock exists; check its owner before recovering a stale lock") from None
    warnings = []
    try:
        with stream:
            stream.write(str(os.getpid()))
            stream.flush()
            yield warnings
    finally:
        try:
            path.unlink()
        except OSError:
            warnings.append("writer lock cleanup failed; verify owner before removing the stale lock")


def _save(root, raw, expected):
    path = evidence._path(root, "session.json")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=root, prefix=".product-session-", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        _, current = _load(root)
        if revision(current) != expected:
            raise ConflictError("session changed during validation; reload status and prepare a new request")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)


def _prepare_result_request(root, session, request, *, apply):
    """Expand reviewed path-only rows in previews, pinning the bytes actually read."""
    verification = request.get("verification")
    rows = verification.get("results") if isinstance(verification, dict) else None
    if not isinstance(rows, list) or not any(isinstance(row, dict) and isinstance(row.get("evidence"), str) for row in rows):
        return None
    if apply or "decision" in request:
        raise ValueError("path-only results require a preview without decision; review prepared_request before applying acceptance")
    if session is None or session.get("current_gate") != "acceptance" or request["action"] != "advance" or request.get("target") != "completed":
        raise ValueError("path-only results are only supported for acceptance completion previews")
    work = process._validate(session)
    if verification.get("scope_key") != work["scope_key"]:
        raise ValueError("verification belongs to another scope")
    ids = [row.get("id") if isinstance(row, dict) else None for row in rows]
    if any(not isinstance(identifier, str) for identifier in ids) or sorted(ids) != work["scope"]["required_checks"]:
        raise ValueError("results must cover each required check exactly once")
    prepared = deepcopy(request)
    size = len(json.dumps(prepared, ensure_ascii=True, allow_nan=False))
    reports = {}
    for row in prepared["verification"]["results"]:
        reference = row.get("evidence")
        if not isinstance(reference, str):
            continue
        if set(row) != {"id", "status", "evidence"}:
            raise ValueError("path-only results accept only id, status and evidence; command comes from the report")
        if not isinstance(row["status"], str) or row["status"] not in {"Pass", "Fail", "Not Run", "environment_blocked", "Skipped"}:
            raise ValueError("result status must be an explicit reviewed outcome")
        if reference not in reports:
            _, _, raw = readiness._content(root, reference)
            report = decode(raw)
            command = report.get("command")
            if (report.get("kind") != "explicit_verification" or type(report.get("schema_version")) is not int
                    or report["schema_version"] not in {1, 2} or not isinstance(command, dict)):
                raise ValueError("expected an explicit_verification JSON report: " + reference)
            argv = command.get("argv")
            if (not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or "\x00" in arg for arg in argv)
                    or not argv[0] or type(command.get("exit_code")) is not int
                    or not isinstance(command.get("started_at"), str) or not command["started_at"]
                    or not isinstance(command.get("finished_at"), str) or not command["finished_at"]
                    or (command.get("launch_error") is not None and not isinstance(command["launch_error"], str))):
                raise ValueError("incomplete command observation: " + reference)
            reports[reference] = (argv, {"ref": reference, "revision": revision(raw)})
        argv, observed = reports[reference]
        expanded = {"id": row["id"], "status": row["status"], "command": argv, "evidence": observed}
        size += len(json.dumps(expanded, ensure_ascii=True)) - len(json.dumps(row, ensure_ascii=True))
        if size > MAX_REQUEST_BYTES:
            raise ValueError("prepared result request exceeds size limit")
        row["command"] = deepcopy(argv)
        row["evidence"] = deepcopy(observed)
    return prepared


def refresh_framework_metadata(project_dir, *, source, version):
    """Upgrade framework metadata without replacing concurrently updated work."""
    root = evidence._root(project_dir)
    with _lock(root) as warnings:
        _refresh_framework_metadata(root, source=source, version=version)
    return warnings


def _refresh_framework_metadata(root, *, source, version):
    """Caller holds the process writer lock, including during framework copying."""
    session, previous = _load(root)
    process._validate(session)
    session.update(vulcan_src=source, vulcan_version=version)
    raw = (json.dumps(session, ensure_ascii=True, indent=2, allow_nan=False) + "\n").encode("ascii")
    if len(raw) > MAX_SESSION_BYTES:
        raise ValueError("upgraded session exceeds size limit")
    _save(root, raw, revision(previous))


def transact(project_dir, request, parse_tables, *, apply=False):
    """Default preview; apply re-evaluates under a writer lock and atomically saves."""
    try:
        root = evidence._root(project_dir)
        if type(apply) is not bool:
            raise ValueError("apply must be a boolean")
        action = _validated_request(request)

        def perform():
            session, previous = _load(root)
            if session is not None and process.process_model(session) != process.MODEL:
                raise ValueError("existing legacy sessions are not migrated by this command")
            if revision(previous) != request["expected_session_revision"]:
                raise ConflictError("stale expected_session_revision; reload status before retrying")
            prepared = _prepare_result_request(root, session, request, apply=apply)

            def with_prepared(result):
                if prepared is not None:
                    _, current = _load(root)
                    if current != previous:
                        raise ConflictError("session changed during result preview; reload before preparing another request")
                    result["prepared_request"] = prepared
                return result

            try:
                candidate, checked = _evaluate(root, session, prepared or request, parse_tables)
            except BlockedError as error:
                return with_prepared({"status": "blocked", "applied": False,
                                      "message": str(error), "checks": error.checks})
            raw = (json.dumps(candidate, ensure_ascii=True, indent=2, allow_nan=False) + "\n").encode("ascii")
            if len(raw) > MAX_SESSION_BYTES:
                raise ValueError("proposed session exceeds size limit")
            if apply:
                _save(root, raw, request["expected_session_revision"])
            current = candidate if apply else session
            return with_prepared({"status": "applied" if apply else "ready", "applied": apply, "action": action,
                    "current_gate": current["current_gate"] if current else None,
                    "scope_key": current["current_work"]["scope_key"] if current else None,
                    "proposed_gate": candidate["current_gate"], "proposed_scope_key": candidate["current_work"]["scope_key"],
                    "previous_session_revision": revision(previous), "session_revision": revision(raw) if apply else revision(previous),
                    "proposed_session_revision": revision(raw), "checks": checked, "release_authorized": False})

        if apply:
            with _lock(root) as warnings:
                result = perform()
            if warnings:
                result["warnings"] = warnings
            return result
        return perform()
    except BlockedError as error:
        return {"status": "blocked", "applied": False, "message": str(error), "checks": error.checks}
    except ConflictError as error:
        return {"status": "conflict", "applied": False, "message": str(error)}
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        return {"status": "invalid", "applied": False, "message": str(error)}


def require_verification_permission(session):
    """Authorize source recording for impl self-check or acceptance execution.

    The recorder's --verify flag is not an acceptance transition or verdict.
    Handoff still requires a separate verify decision in the process engine.
    """
    work = process._validate(session)
    stage = session["current_gate"]
    if stage not in {"impl", "acceptance"}:
        raise ValueError("explicit verification requires impl or acceptance in this pilot")
    process._authorize(work, "implement" if stage == "impl" else "verify")
