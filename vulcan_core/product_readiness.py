"""Read-only scoped checks for the iterative Product process.

Local content observations are not authorization, test-coverage certification,
or proof of the live environment. No commands from documents are executed.
"""

import hashlib
import json
import re
from urllib.parse import unquote, urlsplit

from . import evidence, product_process as process
from .document_context import MAX_BYTES, MAX_LINKS, SHARED, STATE, _anchor_indices, _document, _links, _reference_definitions, _sections
from .product_documents import active_section


MAX_REFERENCES = 32
PLACEHOLDER = re.compile(r"^(?:[-?]*|TBD|TODO|N/?A|pending|\uacb0\uc815\s*\ud544\uc694|\ud655\uc815\s*\ud544\uc694)$", re.I)
METHOD = re.compile(r"method|command|\uba85\ub839|\ubc29\ubc95", re.I)
EXPECTED = re.compile(r"expected|success|\uc131\uacf5\s*\uae30\uc900|\uae30\ub300", re.I)
STATUS = re.compile(r"^(status|result|state|\uc0c1\ud0dc|\uacb0\uacfc)$", re.I)


def _content(root, reference, markdown=False):
    if not isinstance(reference, str) or not reference or "\\" in reference:
        raise ValueError("use a project-relative URL-style reference")
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or parsed.query:
        raise ValueError("only local references without query parameters are supported")
    relative = evidence._relative(unquote(parsed.path))
    if evidence._excluded(relative):
        raise ValueError("excluded/private runtime path")
    path = _document(root, relative) if markdown else evidence._path(root, relative)
    if not path.is_file():
        raise ValueError("reference must resolve to an existing regular file")
    if not markdown and parsed.fragment:
        raise ValueError("artifact references cannot have anchors")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("reference exceeds the byte limit")
    return relative, unquote(parsed.fragment), raw


def local_reference(project_dir, reference, *, markdown=False):
    """Capture a whole-file revision, even for an anchored Markdown reference."""
    _, _, raw = _content(evidence._root(project_dir), reference, markdown)
    return {"ref": reference, "revision": "sha256:" + hashlib.sha256(raw).hexdigest()}


def _issue(code, message, path=None, line=None):
    return {"code": code, "message": message, "path": path, "line": line}


def _cell(value):
    return value.strip().strip("`*").strip()


def _without_comments(text):
    """Mask real comments, not literal comment openers in inline code spans."""
    output, kept, cursor = [], 0, 0
    token_pattern = re.compile(r"<!--|`+")
    while token := token_pattern.search(text, cursor):
        if token[0].startswith("`"):
            back = token.start()
            while back > 0 and text[back - 1] == "\\":
                back -= 1
            escaped = (token.start() - back) % 2
            closing = None if escaped else re.search(r"(?<!`)" + re.escape(token[0]) + r"(?!`)", text[token.end():])
            cursor = token.end() + closing.end() if closing else token.end()
            continue
        closing = text.find("-->", token.end())
        cursor = len(text) if closing < 0 else closing + 3
        comment = text[token.start():cursor]
        output.append(text[kept:token.start()])
        output.append(comment if STATE.fullmatch(comment) else re.sub(r"[^\r\n]", " ", comment))
        kept = cursor
    output.append(text[kept:])
    return "".join(output)


def _document_view(root, reference):
    path, anchor, raw = _content(root, reference["ref"], markdown=True)
    if reference["revision"] != "sha256:" + hashlib.sha256(raw).hexdigest():
        raise ValueError("document revision changed; review scope before renewing its reference")
    # Comments are not current definitions or dependencies; keep line positions
    # and only the explicitly supported state annotation.
    visible = "".join(section["visible"] for section in _sections(raw.decode("utf-8-sig")))
    sections = _sections(_without_comments(visible))
    start = _anchor_indices(sections).get(anchor) if anchor else None
    if anchor and start is None:
        raise ValueError("Markdown anchor does not exist")
    selected = set(range(len(sections))) if start is None else {
        i for i, section in enumerate(sections) if i == start or start in section["parents"]
    }
    selected.update(parent for i in list(selected) for parent in sections[i]["parents"])
    # Shared conditions and their children cannot disappear through a feature anchor.
    shared = {i for i, section in enumerate(sections)
              if SHARED.search(section["heading"]) and active_section(section, sections, True)}
    selected.update(i for i, section in enumerate(sections)
                    if i in shared or any(parent in shared for parent in section["parents"]))
    if start is not None and not active_section(sections[start], sections, True):
        raise ValueError("selected contract is candidate/history, not a current definition")
    return path, sections, selected


def document_readiness(project_dir, scope, parse_tables):
    """Check declared definitions and test plans, not execution during planning."""
    root = evidence._root(project_dir)
    scope = process.normalize_scope(scope)
    issues, sources, views, common = [], [], [], []
    for key in ("related_ids", "contracts", "tests", "required_checks"):
        if not scope[key]:
            issues.append(_issue("incomplete_scope", key + " is not defined yet"))
    references = [(kind, ref) for kind in ("contracts", "tests") for ref in scope[kind]]
    if len(references) > MAX_REFERENCES:
        return {"ready": False, "issues": [_issue("reference_limit", "scope exceeds 32 document references")], "sources": [], "common_context": []}
    for kind, reference in references:
        try:
            path, sections, selected = _document_view(root, reference)
            views.append((kind, path, sections, selected))
            sources.append(dict(reference))
        except (OSError, ValueError, UnicodeError) as error:
            issues.append(_issue("invalid_reference", str(error), reference["ref"]))

    covered = {(path, i) for _, path, _, selected in views for i in selected}
    definitions = {"contracts": {}, "tests": {}}
    for kind, path, sections, selected in views:
        labels = _reference_definitions("".join(s["visible"] for s in sections))
        wanted = set(scope["related_ids"] if kind == "contracts" else scope["required_checks"])
        for i in sorted(selected):
            section = sections[i]
            if section["state_conflict"]:
                issues.append(_issue("conflicting_state", "resolve conflicting document state markers", path, section["start_line"]))
            if not active_section(section, sections, True):
                continue
            shared = any(SHARED.search(sections[n]["heading"]) for n in [i, *section["parents"]])
            if shared:
                common.append({"path": path, "line": section["start_line"], "heading": section["heading"]})
            links = _links(root, path, section["visible"], labels)
            if len(links) > MAX_LINKS:
                issues.append(_issue("link_limit", "section exceeds the link inspection budget; scope cannot be fully checked", path, section["start_line"]))
            for link in links[:MAX_LINKS]:
                target_views = [view for view in views if view[1] == link["path"]]
                bound = link["status"] == "available" and bool(target_views)
                if bound:
                    target_sections = target_views[0][2]
                    target = _anchor_indices(target_sections).get(link["anchor"]) if link["anchor"] else None
                    required = {n for n, s in enumerate(target_sections)
                                if active_section(s, target_sections, True) and
                                (not link["anchor"] or n == target or target in s["parents"])}
                    bound = bool(required) and all((link["path"], n) in covered for n in required)
                if not bound:
                    issues.append(_issue("unbound_reference", "bind the referenced current contract/test in scope: " + link["target"], path, section["start_line"]))
            for headers, rows in parse_tables(section["visible"], section["start_line"] - 1):
                for row in rows:
                    identifier = _cell(row.get(headers[0], ""))
                    if identifier not in wanted and not (shared and kind == "contracts" and re.fullmatch(r"SEC-\d+(?:-\w+)*", identifier)):
                        continue
                    line = int(row["__line_num__"])
                    values = {h: _cell(row.get(h, "")) for h in headers[1:] if not STATUS.fullmatch(h.strip())}
                    meaningful = [v for v in values.values() if not PLACEHOLDER.fullmatch(v)]
                    if not meaningful:
                        issues.append(_issue("empty_definition", identifier + " needs a substantive definition", path, line))
                    if kind == "tests":
                        for pattern, name in ((METHOD, "method"), (EXPECTED, "expected outcome")):
                            if not any(pattern.search(h) and not PLACEHOLDER.fullmatch(v) for h, v in values.items()):
                                issues.append(_issue("incomplete_test_plan", identifier + " needs " + name, path, line))
                    signature = tuple(sorted(values.items()))
                    previous = definitions[kind].get(identifier)
                    if previous is not None and previous != signature:
                        issues.append(_issue("conflicting_definition", identifier + " has different current definitions", path, line))
                    definitions[kind][identifier] = signature
    for kind, ids in (("contracts", scope["related_ids"]), ("tests", scope["required_checks"])):
        for identifier in sorted(set(ids) - definitions[kind].keys()):
            issues.append(_issue("missing_definition", identifier + " needs a primary-ID table row in scoped " + kind))
    return {"ready": not issues, "issues": issues, "sources": sources, "common_context": common}


def observe_basis(project_dir, basis):
    """Check the declared environment reference, not Git or source freshness."""
    declared = process._basis(basis)
    root = evidence._root(project_dir)
    environment = local_reference(root, declared["environment"]["ref"])
    if environment != declared["environment"]:
        raise ValueError("environment manifest revision changed")
    return declared


def check_execution(project_dir, scope, verification, current_basis):
    """Check existing explicit_verification reports; never execute or invent a Pass."""
    key = process.verification_key(scope, verification, current_basis)
    root = evidence._root(project_dir)
    for row in verification["results"]:
        ref = row["evidence"]
        _, _, raw = _content(root, ref["ref"])
        if "sha256:" + hashlib.sha256(raw).hexdigest() != ref["revision"]:
            raise ValueError(row["id"] + ": execution artifact revision changed")
        report = json.loads(raw)
        if (not isinstance(report, dict) or report.get("kind") != "explicit_verification"
                or type(report.get("schema_version")) is not int or report["schema_version"] not in {1, 2}):
            raise ValueError(row["id"] + ": expected an explicit_verification JSON report")
        command = report.get("command")
        if (not isinstance(command, dict) or command.get("argv") != row["command"]
                or type(command.get("exit_code")) is not int or command["exit_code"] != 0
                or command.get("launch_error") is not None
                or not command.get("started_at") or not command.get("finished_at")):
            raise ValueError(row["id"] + ": unsuccessful, incomplete or mismatched command observation")
    return key


def collect(project_dir, session, parse_tables):
    """Next-boundary diagnosis; checks passing never grant approval or release."""
    summary = process.describe(session)
    if summary.get("status") != "active":
        return {"status": "invalid", "issues": [_issue("invalid_session", summary.get("message", "requires iterative Product"))]}
    work = session["current_work"]
    docs = document_readiness(project_dir, work["scope"], parse_tables)
    stage = session["current_gate"]
    result = {"status": "ready" if docs["ready"] else "blocked", "purpose": {
        "planning": "implementation_readiness", "impl": "acceptance_handoff",
        "acceptance": "acceptance_evidence", "completed": "completed_scope_evidence"}[stage],
        "scope_key": work["scope_key"], "documents": docs["sources"], "common_context": docs["common_context"], "issues": docs["issues"],
        "execution": "not_required_at_this_stage", "release_authorized": False,
        "limitations": ["Scoped mechanical checks do not prove semantic completeness or review quality.",
                        "Approval provenance and revocation require the trusted Orchestrator.",
                        "Source changes are not detected here; the Orchestrator decides relevant retests.",
                        "Environment manifests describe the environment; they do not observe live services."],
        "unresolved_obligations": len(session.get("open_issues", [])) if isinstance(session.get("open_issues", []), (list, dict)) else "unknown"}
    readiness = {"scope_key": work["scope_key"], "ready": docs["ready"],
                 "purpose": "implementation" if stage == "planning" else "handoff",
                 "evidence": {"ref": "status:scoped-readiness", "revision": "sha256:" + process._digest(docs)}}
    current = None
    if stage != "planning":
        try:
            basis = work.get("verification", {}).get("basis") if stage in {"acceptance", "completed"} else work.get("basis")
            current = observe_basis(project_dir, basis)
            if stage in {"acceptance", "completed"}:
                verified = check_execution(project_dir, work["scope"], work.get("verification"), current)
                result.update(execution="verified_observations", verification_key=verified)
        except (OSError, ValueError, UnicodeError, AttributeError) as error:
            result["issues"].append(_issue("invalid_execution_basis", str(error)))
            result["execution"] = "missing_stale_or_failed"
    if result["issues"]:
        result["status"] = "blocked"
    result["readiness"] = readiness
    result["current_basis"] = current
    target = {"planning": "impl", "impl": "acceptance", "acceptance": "completed"}.get(stage)
    result["transition"] = process.assess_transition(session, target, readiness=readiness,
        current_basis=current, verification=work.get("verification")) if target else None
    if result["transition"] and result["status"] != "ready":
        result["transition"]["allowed"] = False
        result["transition"]["reasons"].append("scoped document/execution checks are blocked")
    return result


def render(result):
    lines = [f"scoped_check: {result['status']} ({result['purpose']})",
             f"  documents: {len(result['documents'])}; execution: {result['execution']}",
             f"  unresolved obligations outside this decision: {result['unresolved_obligations']}"]
    for issue in result["issues"]:
        location = issue["path"] or "scope"
        if issue["line"] is not None:
            location += ":" + str(issue["line"])
        lines.append(f"  [{issue['code']}] {location}: {issue['message']}")
    transition = result["transition"]
    if transition:
        lines.append(f"  transition eligibility: {transition['allowed']} -> {transition['target']}")
        lines.extend("  " + reason for reason in transition["reasons"])
    lines.append("  Read-only diagnostics; no approval, state change or release permission is created.")
    return "\n".join(lines)
