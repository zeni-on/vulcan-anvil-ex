"""Explicit, session-only legacy Product migration and guarded restoration.

Preservation is not an implementation decision. No legacy trace scan, Git,
document rewriting, runtime invocation or project-wide backup occurs here.
"""

import base64
from copy import deepcopy
import json
import os

from . import evidence, product_process as process, product_readiness as readiness
from . import product_session as store


GATES = {"phase0", "gate1", "gate2", "gate3", "impl", "gate4", "gate5"}
GATE_STATUSES = {"pending", "in-progress", "awaiting-approval", "done", "blocked"}
LEGACY_FIELDS = {"current_gate", "gate_status", "completed", "pending", "blocked", "approvals",
                 "implementation", "qa_execution", "stats", "feature"}
BACKUP_DIR = ".vulcan/product-migrations"
MAX_BACKUP_BYTES = store.MAX_SESSION_BYTES * 2


def _json(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("ascii")


def _legacy(session):
    if (not isinstance(session, dict) or session.get("profile") != "product"
            or "process_model" in session):
        raise ValueError("migration requires an unmarked legacy Product session")
    if session.get("current_gate") not in GATES | {"completed"}:
        raise ValueError("invalid legacy current_gate")
    statuses = session.get("gate_status")
    if (not isinstance(statuses, dict) or set(statuses) != GATES
            or any(not isinstance(v, str) or v not in GATE_STATUSES for v in statuses.values())):
        raise ValueError("legacy gate_status must contain the seven known Gate states")
    if {"current_work", "work_history", "migration"} & session.keys():
        raise ValueError("legacy session contains conflicting iterative state fields")


def _observe(root, reference, inputs):
    reference = process._reference(reference)
    # Whole-file fingerprints bind the preview, not acceptance. Anchors are not
    # resolved here; their meaning and candidate/current scope remain reviewed.
    _, _, raw = readiness._content(root, reference["ref"], markdown=True)
    if store.revision(raw) != reference["revision"]:
        raise store.ConflictError("migration input changed: " + reference["ref"])
    inputs[reference["ref"]] = reference["revision"]
    return reference


def _check_inputs(root, inputs):
    for ref, rev in inputs.items():
        _observe(root, {"ref": ref, "revision": rev}, {})


def _backup_path(root, relative):
    relative = evidence._relative(relative)
    name = relative.removeprefix(BACKUP_DIR + "/")
    if (relative != BACKUP_DIR + "/" + name or len(name) != 69 or not name.endswith(".json")
            or any(c not in "0123456789abcdef" for c in name[:-5])):
        raise ValueError("backup must be a generated session migration record")
    return evidence._path(root, relative)


def _read_backup(root, relative):
    raw = _backup_bytes(root, relative)
    record = store.decode(raw)
    if (record.get("kind") != "legacy-product-session" or type(record.get("schema_version")) is not int
            or record["schema_version"] != 1):
        raise ValueError("invalid migration backup")
    original = base64.b64decode(record["original_base64"], validate=True)
    if len(original) > store.MAX_SESSION_BYTES or store.revision(original) != record["previous_revision"]:
        raise ValueError("migration backup integrity mismatch")
    _legacy(store.decode(original))
    return record, original, raw


def _backup_bytes(root, relative):
    with _backup_path(root, relative).open("rb") as stream:
        raw = stream.read(MAX_BACKUP_BYTES + 1)
    if len(raw) > MAX_BACKUP_BYTES:
        raise ValueError("migration backup exceeds size limit")
    return raw


def _preserve(root, relative, raw):
    """Never overwrite a record, including an incomplete record after a crash."""
    path = _backup_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if _backup_bytes(root, relative) != raw:
            raise store.ConflictError("existing migration backup differs; preserve and inspect it before retrying")
        return
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    if _backup_bytes(root, relative) != raw:
        raise ValueError("migration backup verification failed")


def _migration(root, session, previous, request):
    _legacy(session)
    if request.get("target") != "planning":
        raise ValueError("legacy migration only enters planning")
    if not {"scope", "reason", "obligations", "obligation_review"} <= request.keys():
        raise ValueError("migration needs scope, reason, obligations and obligation_review")
    if request["obligation_review"] not in {"pending", "reviewed"}:
        raise ValueError("obligation_review must be pending or reviewed, not a completion verdict")
    obligations = request["obligations"]
    if not isinstance(obligations, list) or len(obligations) > 256:
        raise ValueError("obligations must be a bounded list of handover records")
    inputs = {}
    reason = _observe(root, request["reason"], inputs)
    scope = process.normalize_scope(request["scope"])
    for ref in [scope["work"], *scope["contracts"], *scope["tests"]]:
        _observe(root, ref, inputs)
    for row in obligations:
        if (not isinstance(row, dict) or set(row) != {"source", "description", "owner", "scope", "status"}
                or not process._text(row["description"]) or not process._text(row["owner"])
                or row["scope"] not in {"current", "followup", "undetermined"}
                or row["status"] not in {"open", "undetermined"}):
            raise ValueError("obligations need source, description, owner, scope and open/undetermined status")
        _observe(root, row["source"], inputs)
    plan = {"previous_revision": store.revision(previous), "scope": scope, "reason": reason,
            "obligations": obligations, "obligation_review": request["obligation_review"]}
    key = "sha256:" + process._digest(plan)
    relative = BACKUP_DIR + "/" + key[7:] + ".json"
    _backup_path(root, relative)
    candidate = {k: deepcopy(v) for k, v in session.items() if k not in LEGACY_FIELDS}
    candidate.update(process.new_session(scope))
    candidate["migration"] = {"backup": relative, "previous_revision": store.revision(previous),
        "preview_key": key, "legacy_current_gate": session["current_gate"],
        "legacy_gate_status": deepcopy(session["gate_status"]),
        "archived_fields": sorted(LEGACY_FIELDS & session.keys()),
        "obligation_review": request["obligation_review"], "obligations": deepcopy(obligations),
        "reason": reason}
    process._validate(candidate)
    raw = _json(candidate)
    if len(raw) > store.MAX_SESSION_BYTES:
        raise ValueError("migrated session exceeds size limit")
    backup = _json({"kind": "legacy-product-session", "schema_version": 1,
        "original_base64": base64.b64encode(previous).decode("ascii"),
        "previous_revision": store.revision(previous), "migrated_revision": store.revision(raw),
        "preview_key": key})
    return candidate, raw, key, inputs, relative, backup


def _restore(root, session, previous, request):
    process._validate(session)
    relative = request.get("backup")
    record, original, backup_raw = _read_backup(root, relative)
    migration = session.get("migration", {})
    if (migration.get("backup") != relative or migration.get("preview_key") != record["preview_key"]
            or migration.get("previous_revision") != record["previous_revision"]
            or record["migrated_revision"] != store.revision(previous)):
        raise store.ConflictError("restoration requires the exact migration postimage; subsequent changes must be reviewed separately")
    key = "sha256:" + process._digest({"action": "restore-migration", "backup": relative,
        "backup_revision": store.revision(backup_raw), "session_revision": store.revision(previous)})
    return store.decode(original), original, key, {}, relative, backup_raw


def transact(root, request, *, apply):
    """Called through the common request validator and error/lock conventions."""
    token = request.get("preview_key")
    if token is not None and (not isinstance(token, str) or not store._is_revision(token)):
        raise ValueError("preview_key must be an observed SHA-256")
    if apply and (request["expected_session_revision"] is None or token is None):
        raise ValueError("apply requires the reviewed prepared_request, including preview_key and session revision")

    def perform():
        session, previous = store._load(root)
        expected = request["expected_session_revision"]
        if expected is not None and expected != store.revision(previous):
            raise store.ConflictError("session changed since migration preview")
        operation = _migration if request["action"] == "migrate" else _restore
        candidate, raw, key, inputs, relative, backup = operation(root, session, previous, request)
        if "preview_key" in request and request["preview_key"] != key:
            raise store.ConflictError("migration plan changed; review a new preview")
        if store._load(root)[1] != previous:
            raise store.ConflictError("session changed during migration preview")
        _check_inputs(root, inputs)
        prepared = deepcopy(request)
        prepared.update(expected_session_revision=store.revision(previous), preview_key=key)
        if apply:
            if request["action"] == "migrate":
                _preserve(root, relative, backup)
            def before_replace():
                if _read_backup(root, relative)[2] != backup:
                    raise store.ConflictError("migration backup changed before session replacement")
                _check_inputs(root, inputs)
                if store._load(root)[1] != previous:
                    raise store.ConflictError("session changed before migration replacement")
            store._save(root, raw, store.revision(previous), before_replace=before_replace)
        result = {"status": "applied" if apply else "ready", "applied": apply,
            "action": request["action"], "previous_session_revision": store.revision(previous),
            "session_revision": store.revision(raw) if apply else store.revision(previous),
            "proposed_session_revision": store.revision(raw),
            "current_gate": candidate["current_gate"] if apply else session["current_gate"],
            "proposed_gate": candidate["current_gate"], "prepared_request": prepared,
            "backup": relative, "backup_scope": ["session.json"],
            "release_authorized": False, "implementation_authorized": False,
            "obligations": candidate.get("migration", {}).get("obligations", []),
            "limitations": ["Session-only preservation; not a backup of documents, code, secrets or databases.",
                "Backup contains original session values; it is not encrypted or automatically Git-ignored. Protect it before sharing.",
                "Handover records are reviewed input, not a complete inventory or resolved obligations.",
                "Legacy approvals and test outcomes do not authorize this planning scope.",
                "Cooperating writer lock only; stop other editors before applying or restoring.",
                "Restoration refuses any subsequent session change and never restores other files."]}
        if request["action"] == "migrate":
            result["migration"] = candidate["migration"]
            result["proposed_scope"] = candidate["current_work"]["scope"]
        return result

    if apply:
        with store._lock(root) as warnings:
            result = perform()
        if warnings:
            result["warnings"] = warnings
        return result
    return perform()
