"""Bounded, read-only Markdown lookup. Results are references, never approvals."""

import hashlib
from collections import deque
import os
from pathlib import Path, PureWindowsPath
import re
import stat
from urllib.parse import unquote, urlsplit


MAX_SECTIONS = 12
MAX_DOCUMENTS = 256
MAX_BYTES = 2_000_000
MAX_LINK_DEPTH = 2
MAX_LINK_DOCUMENTS = 16
MAX_LINKS = 64
SOURCE_ROOTS = ("docs/product", "docs/artifacts/01-requirements",
                "docs/artifacts/02-design", "docs/artifacts/03-test")
EXCLUDED_DIRS = {"templates", "runs", "reviews", "ref-docs", "private", "_exec"}
STATE = re.compile(r"^ {0,3}<!--[ \t]*vulcan:state=(current|candidate|history)[ \t]*-->[ \t]*\r?$", re.M)
SHARED = re.compile(
    r"\b(contract\s+policy|security|auth\w*|errors?|compatibility)\b|"
    r"\ubcf4\uc548|\uc778\uc99d|\uad8c\ud55c|\uc624\ub958|\ud638\ud658|\uacc4\uc57d\s*\uc815\ucc45", re.I)


def _linked(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) &
                                   getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _document(root, relative):
    """Check lexical and physical boundaries before reading any source bytes."""
    win = PureWindowsPath(relative)
    if (not relative or win.drive or win.root or Path(relative).is_absolute()
            or ".." in win.parts or ":" in relative):
        raise ValueError(f"Unsafe document path: {relative}")
    parts = relative.replace("\\", "/").split("/")
    path = root
    for part in parts:
        path = path / part
        if _linked(path):
            raise ValueError(f"Linked document path is not permitted: {relative}")
    if path.suffix.lower() != ".md" or not path.is_file():
        raise ValueError(f"Expected an existing regular Markdown file: {relative}")
    path.resolve().relative_to(root)
    return path


def _sources(root, documents, warnings):
    if documents:
        # Validate the entire explicit selection before reading any document.
        return sorted(set(_document(root, name) for name in documents))
    found = []
    for base in SOURCE_ROOTS:
        start = root
        unsafe = False
        for part in base.split("/"):
            start /= part
            if not start.exists():
                unsafe = True
                break
            if _linked(start):
                warnings.append(f"Skipped linked source directory: {base}")
                unsafe = True
                break
        if unsafe:
            continue
        for directory, dirs, files in os.walk(start, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d.lower() not in EXCLUDED_DIRS
                             and not _linked(Path(directory) / d))
            for name in sorted(files):
                if name.lower().endswith(".md"):
                    relative = (Path(directory) / name).relative_to(root).as_posix()
                    try:
                        found.append(_document(root, relative))
                    except (OSError, ValueError) as exc:
                        warnings.append(str(exc))
                    if len(found) > MAX_DOCUMENTS:
                        warnings.append("Document scan limit reached; sources omitted.")
                        return found[:MAX_DOCUMENTS]
    return sorted(set(found))


def _sections(text):
    lines = text.splitlines(keepends=True)
    visible = list(lines)
    fence = None
    for i, line in enumerate(lines):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            visible[i] = "\n"
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
        elif match and not (match[1][0] == "`" and "`" in match[2]):
            fence = match[1]
            visible[i] = "\n"
    headings = []
    for i, line in enumerate(visible):
        match = re.match(r"^ {0,3}(#{1,6})(?:\s+(.+?)\s*|\s*)$", line.rstrip("\r\n"))
        if match:
            headings.append((i, len(match[1]), re.sub(r"\s+#+\s*$", "", match[2] or "")))
        elif i and re.fullmatch(r" {0,3}(=+|-+)\s*", line.rstrip("\r\n")) and visible[i-1].strip():
            if not any(h[0] == i-1 for h in headings):
                headings.append((i-1, 1 if line.strip()[0] == "=" else 2, visible[i-1].strip()))
    if not headings or headings[0][0] != 0:
        headings.insert(0, (0, 0, "(document introduction)"))
    result, stack = [], []
    for n, (start, level, title) in enumerate(headings):
        end = headings[n+1][0] if n+1 < len(headings) else len(lines)
        while stack and result[stack[-1]]["level"] >= level:
            stack.pop()
        body = "".join(visible[start:end])
        markers = list(dict.fromkeys(STATE.findall(body)))
        inherited = result[stack[-1]]["state"] if stack else "unclassified"
        state = markers[0] if len(markers) == 1 else "unclassified" if markers else inherited
        result.append({"heading": title, "level": level, "start_line": start+1,
                       "end_line": end, "parents": list(stack), "state": state,
                       "state_conflict": len(markers) > 1,
                       "visible": body, "search": "".join(lines[start:end]),
                       "excerpt": "".join(lines[start:end])})
        stack.append(n)
    return result




def _reference_definitions(text):
    definitions = {}
    for label, target in re.findall(r"^ {0,3}\[([^\]\n]+)\]:\s*(<[^>]+>|\S+)", text, re.M):
        targets = definitions.setdefault(" ".join(label.lower().split()), [])
        if target not in targets:
            targets.append(target)
    return definitions


def _inline_targets(text):
    """Read bounded Markdown destinations, including balanced/escaped parens."""
    for match in re.finditer(r"(?<!!)\[[^\]\n]*\]\(\s*", text):
        start = match.end()
        if start < len(text) and text[start] == "<":
            end = text.find(">", start+1)
            if end >= 0:
                yield text[start+1:end]
            continue
        target, depth, i = [], 0, start
        while i < len(text) and not text[i].isspace():
            char = text[i]
            if char == "\\" and i+1 < len(text) and text[i+1] in r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~":
                i += 1
                target.append(text[i])
            elif char == "(":
                depth += 1
                target.append(char)
            elif char == ")":
                if not depth:
                    break
                depth -= 1
                target.append(char)
            else:
                target.append(char)
            i += 1
        yield "".join(target)


def _links(root, path, text, definitions):
    # Only actual uses of reference links count; a document-wide definition is
    # not itself a dependency of every section. Code examples are not followed.
    text = re.sub(r"(`+).*?\1", "", text, flags=re.S)
    text = re.sub(r"^ {0,3}\[[^\]\n]+\]:.*$", "", text, flags=re.M)
    targets = list(_inline_targets(text))
    unresolved = []

    def reference(label, key, notation, required=True):
        candidates = definitions.get(" ".join((key or label).lower().split()), [])
        if len(candidates) == 1:
            targets.append(candidates[0])
        elif candidates or required:
            unresolved.append({"target": notation, "path": "", "anchor": "",
                               "status": "ambiguous_definition" if candidates else "missing_definition",
                               "followed": False})

    for label, key in re.findall(r"(?<!!)\[([^\]\n]+)\]\[([^\]\n]*)\]", text):
        reference(label, key, f"[{label}][{key}]")
    for label in re.findall(r"(?<!!)(?<!\])\[([^\]\n]+)\](?![\[(])", text):
        reference(label, "", f"[{label}]", required=False)
    result = []
    # A sentinel beyond the budget lets the caller report uninspected links.
    # Filter external/non-document targets before counting that sentinel.
    for target in dict.fromkeys(targets):
        if len(result) > MAX_LINKS:
            break
        target = target.strip("<>")
        try:
            parsed = urlsplit(target)
        except ValueError:
            result.append({"target": target, "path": "", "anchor": "",
                           "status": "missing_or_unsafe", "followed": False})
            continue
        relative = unquote(parsed.path)
        if parsed.scheme or parsed.netloc or not (relative.lower().endswith(".md") or
                                                 not relative and parsed.fragment):
            continue
        # Normalize sibling references but never allow a lexical '..' hop
        # through a symlink/reparse directory before the normalization.
        normalized = os.path.normpath(str(Path(path).parent / relative)).replace("\\", "/") if relative else path
        try:
            win = PureWindowsPath(relative)
            if win.drive or win.root or ":" in relative or "\\" in relative:
                raise ValueError("Absolute or non-URL link")
            cursor = root / Path(path).parent
            for part in relative.split("/"):
                cursor = cursor / part
                cursor.resolve().relative_to(root)
                if _linked(cursor):
                    raise ValueError("Linked reference path")
            _document(root, normalized)
            status = "unsupported_query" if parsed.query else "available"
        except (ValueError, OSError):
            status = "missing_or_unsafe"
        result.append({"target": target, "path": normalized, "anchor": unquote(parsed.fragment),
                       "status": status, "followed": False})
    return (result + unresolved)[:MAX_LINKS+1]


def _anchor_indices(sections):
    anchors = {}
    for i, section in enumerate(sections):
        if not section["level"]:
            continue
        base = re.sub(r"[^\w\- ]", "", section["heading"].lower()).replace(" ", "-")
        anchor, suffix = base, 0
        while anchor in anchors:
            suffix += 1
            anchor = f"{base}-{suffix}"
        anchors[anchor] = i
    return anchors


def _reference_allowed(path, explicit):
    if path in explicit:
        return True
    return (not EXCLUDED_DIRS.intersection(part.lower() for part in Path(path).parts)
            and any(path.startswith(base + "/") for base in SOURCE_ROOTS))


def _load_sections(source, root, patterns, warnings):
    path = source.relative_to(root).as_posix()
    try:
        with source.open("rb") as stream:
            raw = stream.read(MAX_BYTES+1)
        if len(raw) > MAX_BYTES:
            warnings.append(f"Oversized document omitted: {path}")
            return None
        sections = _sections(raw.decode("utf-8-sig"))
    except (OSError, UnicodeError) as exc:
        warnings.append(f"Document unreadable: {path}: {exc}")
        return None
    digest = hashlib.sha256(raw).hexdigest()
    for section in sections:
        section.update(path=path, document_sha256=digest, reasons=[], direct_ancestor=False)
        section["matching_ids"] = [s for s, pattern in patterns.items() if pattern.search(section["search"])]
        section["ancestry"] = [sections[i]["heading"] for i in section["parents"]]
    return sections


def _follow_references(root, cache, patterns, explicit, warnings):
    initial = [(path, i, 0) for path, sections in cache.items() if sections is not None
               for i, s in enumerate(sections) if s["reasons"]]
    queue = deque(sorted(initial, key=lambda entry: _priority(cache[entry[0]][entry[1]])))
    visited, references, linked_documents = set(), [], 0
    limited = False
    definitions = {}
    for path, sections in cache.items():
        if sections is not None:
            definitions[path] = _reference_definitions("".join(s["visible"] for s in sections))
    while queue:
        path, i, depth = queue.popleft()
        if (path, i) in visited:
            continue
        visited.add((path, i))
        section = cache[path][i]
        section["source_links"] = []
        for link in _links(root, path, section["visible"], definitions[path]):
            if len(references) >= MAX_LINKS:
                limited = True
                break
            link.update(source_path=path, source_line=section["start_line"], depth=depth+1)
            references.append(link)
            section["source_links"].append(link)
            if link["status"] != "available":
                continue
            target = link["path"]
            if not _reference_allowed(target, explicit):
                link["status"] = "outside_lookup_scope"
                continue
            if target not in cache:
                if depth >= MAX_LINK_DEPTH:
                    link["status"] = "depth_limit"
                    continue
                if linked_documents >= MAX_LINK_DOCUMENTS or len(cache) >= MAX_DOCUMENTS:
                    link["status"] = "document_limit"
                    continue
                linked_documents += 1
                try:
                    cache[target] = _load_sections(_document(root, target), root, patterns, warnings)
                except (OSError, ValueError):
                    cache[target] = None
                if cache[target] is not None:
                    definitions[target] = _reference_definitions("".join(s["visible"] for s in cache[target]))
            sections = cache[target]
            if sections is None:
                link["status"] = "unreadable"
                continue
            anchor = link["anchor"]
            if anchor:
                start = _anchor_indices(sections).get(anchor)
                if start is None:
                    link["status"] = "missing_anchor"
                    continue
                wanted = {j for j, s in enumerate(sections) if j == start or start in s["parents"]}
                parents = set(sections[start]["parents"])
            else:
                wanted, parents = set(range(len(sections))), set()
            shared = {j for j, s in enumerate(sections) if SHARED.search(s["heading"])}
            wanted |= {j for j, s in enumerate(sections) if j in shared or shared.intersection(s["parents"])}
            parents |= {parent for j in wanted for parent in sections[j]["parents"]}
            indices = sorted(wanted | parents)
            already = all(sections[j]["reasons"] for j in indices)
            if depth >= MAX_LINK_DEPTH and not already:
                link["status"] = "depth_limit"
                continue
            link["status"] = "already_selected" if already else "read"
            link["target_lines"] = [sections[j]["start_line"] for j in indices]
            for j in indices:
                reason = "linked" if j in wanted else "linked_ancestor"
                if reason not in sections[j]["reasons"]:
                    sections[j]["reasons"].append(reason)
                queue.append((target, j, depth+1))
    if limited:
        warnings.append("Reference link limit reached; additional links were not inspected. Contracts are incomplete.")
    return references


def _priority(section):
    reasons = section["reasons"]
    return (0 if section["matching_ids"] else 1 if section["direct_ancestor"]
            else 2 if "linked" in reasons or "linked_ancestor" in reasons
            else 3 if "shared" in reasons else 4)


def lookup_sections(project_dir, seed_ids, documents=None, max_chars=12000):
    if not 1 <= max_chars <= 100000:
        raise ValueError("max-chars must be between 1 and 100000")
    seeds = list(dict.fromkeys(s.strip().upper() for s in seed_ids.split(",") if s.strip()))
    if not seeds or len(seeds) > 32 or any(not re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+", s) for s in seeds):
        raise ValueError("Expected 1..32 comma-separated IDs")
    patterns = {s: re.compile(r"(?<![\w-])" + re.escape(s) + r"(?![\w-])") for s in seeds}
    root = Path(project_dir).resolve(strict=True)
    warnings, cache = [], {}
    sources = _sources(root, documents, warnings)
    explicit = {p.relative_to(root).as_posix() for p in sources} if documents else set()
    if len(sources) > MAX_DOCUMENTS:
        warnings.append("Document limit reached; explicit sources omitted.")
    for source in sources[:MAX_DOCUMENTS]:
        path = source.relative_to(root).as_posix()
        sections = _load_sections(source, root, patterns, warnings)
        cache[path] = sections
        if sections is None:
            continue
        direct = {i for i, s in enumerate(sections) if s["matching_ids"]}
        shared = {i for i, s in enumerate(sections) if SHARED.search(s["heading"])}
        for i, section in enumerate(sections):
            section["direct_ancestor"] = any(i in sections[j]["parents"] for j in direct)
            if i in direct or direct.intersection(section["parents"]):
                section["reasons"].append("direct" if i in direct else "direct_descendant")
            if any(i in sections[j]["parents"] for j in direct | shared):
                section["reasons"].append("ancestor")
            if i in shared or shared.intersection(section["parents"]):
                section["reasons"].append("shared")
    matched = {seed for sections in cache.values() if sections is not None
               for section in sections for seed in section["matching_ids"]}
    references = _follow_references(root, cache, patterns, explicit, warnings) if matched else []
    all_sections = [s for sections in cache.values() if sections is not None for s in sections]
    matched = {seed for s in all_sections if s["reasons"] for seed in s["matching_ids"]}
    for seed in seeds:
        if seed not in matched:
            warnings.append(f"No exact match: {seed}")
        current = [s for s in all_sections if s["reasons"] and seed in s["matching_ids"] and s["state"] == "current"]
        if len(current) > 1:
            warnings.append(f"Multiple current matches for {seed}; potential conflict requires Orchestrator review; no winner selected.")
    selected, omitted, used = [], [], 0
    omitted_total = 0
    omitted_constraints = 0
    # Source order is only a stable tie-breaker, never a lifecycle preference.
    # Match excerpts cannot be displaced by a long global policy document.
    for section in sorted(all_sections, key=_priority):
        if not section["reasons"] or not matched or not section["excerpt"]:
            continue
        item = {k: v for k, v in section.items() if k not in {"parents", "search", "visible", "level", "direct_ancestor"}}
        item.setdefault("source_links", [])
        if item["matching_ids"] and item["state"] == "unclassified":
            warnings.append(f"Unclassified direct match: {item['path']}:{item['start_line']}; current applicability is uncertain; Orchestrator review required.")
        elif any(r.startswith("linked") for r in item["reasons"]) and item["state"] == "unclassified":
            warnings.append(f"Unclassified linked context: {item['path']}:{item['start_line']}; source state is not inherited across documents.")
        if item["state_conflict"]:
            warnings.append(f"Conflicting state markers: {item['path']}:{item['start_line']}; Orchestrator review required.")
        if len(selected) >= MAX_SECTIONS or used + len(item["excerpt"]) > max_chars:
            omitted_total += 1
            if any(r in item["reasons"] for r in ("ancestor", "shared", "direct_descendant", "linked", "linked_ancestor")):
                omitted_constraints += 1
            if len(omitted) < MAX_SECTIONS:
                omitted.append({k: item[k] for k in ("path", "heading", "start_line", "end_line", "matching_ids", "reasons")})
            continue
        item["truncated"] = False
        selected.append(item)
        used += len(item["excerpt"])
    included = {(s["path"], s["start_line"]) for s in selected}
    for link in references:
        target_lines = link.pop("target_lines", None)
        if target_lines is not None:
            count = sum((link["path"], line) in included for line in target_lines)
            link.update(target_sections_total=len(target_lines), included_sections=count)
            link["followed"] = bool(target_lines) and count == len(target_lines)
            if not link["followed"]:
                link["status"] = "output_limit"
        if not link["followed"]:
            warnings.append(f"Source reference not fully included ({link['status']}): {link['source_path']}:{link['source_line']} -> {link['target']}")
    if omitted_total:
        warnings.append("Whole sections omitted by output limits; contracts are incomplete. Read the referenced sources.")
    if omitted_constraints:
        warnings.append(f"Omitted {omitted_constraints} ancestor/shared/descendant/linked constraint sections; included direct matches are not complete contracts.")
    warning_total = len(warnings)
    # Repeated ambiguity/link diagnostics must not defeat the output budget either.
    if warning_total > 48:
        warnings = warnings[:45] + warnings[-2:] + [f"Warning list bounded; {warning_total - 47} additional warnings omitted."]
    return {"schema_version": 1, "kind": "derived_reference", "authority": False,
            "notice": "Reading aid only; not authority, approval, or a complete contract. State is author classification. Review ambiguity with the Orchestrator.",
            "seed_ids": seeds, "limits": {"max_chars": max_chars, "max_sections": MAX_SECTIONS,
                                          "max_documents": MAX_DOCUMENTS, "max_link_documents": MAX_LINK_DOCUMENTS,
                                          "max_link_depth": MAX_LINK_DEPTH, "max_links": MAX_LINKS},
            "references": references,
            "excerpt_chars": used, "sections": selected, "omitted_sections": omitted,
            "omitted_sections_total": omitted_total, "omitted_sections_listed": len(omitted),
            "omitted_sections_remaining": omitted_total - len(omitted),
            "warnings_total": warning_total,
            "truncated": bool(omitted_total), "incomplete": bool(warnings or omitted_total), "warnings": warnings}
