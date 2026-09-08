"""Bounded, read-only Markdown lookup. Results are references, never approvals."""

import hashlib
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import subprocess
from urllib.parse import unquote, urlsplit


MAX_SECTIONS = 12
MAX_DOCUMENTS = 256
MAX_BYTES = 2_000_000
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
    excluded = {"templates", "runs", "reviews", "ref-docs", "private", "_exec"}
    for base in ("docs/product", "docs/artifacts/02-design"):
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
            dirs[:] = sorted(d for d in dirs if d.lower() not in excluded
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


def _git(root, path):
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS", "GIT_ICASE_PATHSPECS"):
        env.pop(name, None)
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_LITERAL_PATHSPECS="1", GIT_NO_REPLACE_OBJECTS="1")

    def run(*args):
        return subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args], env=env, capture_output=True,
                              timeout=5, check=True).stdout.decode("utf-8", "replace").strip()
    try:
        if Path(run("rev-parse", "--show-toplevel")).resolve() != root:
            return {"observed_head": None, "worktree_state": "unknown"}
        head = run("rev-parse", "HEAD")
        status = run("status", "--porcelain=v1", "--untracked-files=all", "--", path)
        ignored = run("ls-files", "--cached", "--others", "--exclude-standard", "--", path)
        return {"observed_head": head, "worktree_state": "dirty" if status else "clean" if ignored else "unknown"}
    except (OSError, subprocess.SubprocessError):
        return {"observed_head": None, "worktree_state": "unknown"}


def _links(root, path, text):
    targets = re.findall(r"\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)", text)
    targets += re.findall(r"^ {0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)", text, re.M)
    result = []
    for target in dict.fromkeys(targets):
        target = target.strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path.lower().endswith(".md"):
            continue
        relative = unquote(parsed.path)
        # Links may legitimately point to a sibling via '..'; normalize only for
        # inspection, then apply the same physical boundary checks. Never fetch.
        normalized = os.path.normpath(str(Path(path).parent / relative)).replace("\\", "/")
        try:
            _document(root, normalized)
            status = "available"
        except (ValueError, OSError):
            status = "missing_or_unsafe"
        result.append({"target": target, "path": normalized, "status": status, "followed": False})
    return result


def lookup_sections(project_dir, seed_ids, documents=None, max_chars=12000):
    if not 1 <= max_chars <= 100000:
        raise ValueError("max-chars must be between 1 and 100000")
    seeds = list(dict.fromkeys(s.strip().upper() for s in seed_ids.split(",") if s.strip()))
    if not seeds or len(seeds) > 32 or any(not re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+", s) for s in seeds):
        raise ValueError("Expected 1..32 comma-separated IDs")
    patterns = {s: re.compile(r"(?<![\w-])" + re.escape(s) + r"(?![\w-])") for s in seeds}
    root = Path(project_dir).resolve(strict=True)
    warnings, all_sections = [], []
    sources = _sources(root, documents, warnings)
    if len(sources) > MAX_DOCUMENTS:
        warnings.append("Document limit reached; explicit sources omitted.")
    for source in sources[:MAX_DOCUMENTS]:
        path = source.relative_to(root).as_posix()
        try:
            with source.open("rb") as stream:
                raw = stream.read(MAX_BYTES+1)
            if len(raw) > MAX_BYTES:
                warnings.append(f"Oversized document omitted: {path}")
                continue
            sections = _sections(raw.decode("utf-8-sig"))
        except (OSError, UnicodeError) as exc:
            warnings.append(f"Document unreadable: {path}: {exc}")
            continue
        digest = hashlib.sha256(raw).hexdigest()
        for section in sections:
            section.update(path=path, document_sha256=digest)
            section["matching_ids"] = [s for s, pattern in patterns.items() if pattern.search(section["search"])]
            section["ancestry"] = [sections[i]["heading"] for i in section["parents"]]
            section["reasons"] = []
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
        all_sections.extend(sections)
    matched = {s for section in all_sections for s in section["matching_ids"]}
    for seed in seeds:
        if seed not in matched:
            warnings.append(f"No exact match: {seed}")
        current = [s for s in all_sections if seed in s["matching_ids"] and s["state"] == "current"]
        if len(current) > 1:
            warnings.append(f"Multiple current matches for {seed}; potential conflict requires Orchestrator review; no winner selected.")
    selected, omitted, used, provenance = [], [], 0, {}
    omitted_total = 0
    omitted_constraints = 0
    # Source order is only a stable tie-breaker, never a lifecycle preference.
    # Match excerpts cannot be displaced by a long global policy document.
    def priority(section):
        reasons = section["reasons"]
        return (0 if section["matching_ids"] else 1 if section["direct_ancestor"]
                else 2 if "shared" in reasons else 3)

    for section in sorted(all_sections, key=priority):
        if not section["reasons"] or not matched or not section["excerpt"]:
            continue
        item = {k: v for k, v in section.items() if k not in {"parents", "search", "visible", "level", "direct_ancestor"}}
        item["source_links"] = _links(root, item["path"], section["visible"])
        if item["matching_ids"] and item["state"] == "unclassified":
            warnings.append(f"Unclassified direct match: {item['path']}:{item['start_line']}; current applicability is uncertain; Orchestrator review required.")
        if item["state_conflict"]:
            warnings.append(f"Conflicting state markers: {item['path']}:{item['start_line']}; Orchestrator review required.")
        for link in item["source_links"]:
            if link["status"] != "available":
                warnings.append(f"Missing or unsafe source link: {item['path']}: {link['target']}")
        if len(selected) >= MAX_SECTIONS or used + len(item["excerpt"]) > max_chars:
            omitted_total += 1
            if any(r in item["reasons"] for r in ("ancestor", "shared", "direct_descendant")):
                omitted_constraints += 1
            if len(omitted) < MAX_SECTIONS:
                omitted.append({k: item[k] for k in ("path", "heading", "start_line", "end_line", "matching_ids", "reasons")})
            continue
        if item["path"] not in provenance:
            provenance[item["path"]] = _git(root, item["path"])
        item["git"] = provenance[item["path"]]
        item["truncated"] = False
        selected.append(item)
        used += len(item["excerpt"])
    if omitted_total:
        warnings.append("Whole sections omitted by output limits; contracts are incomplete. Read the referenced sources.")
    if omitted_constraints:
        warnings.append(f"Omitted {omitted_constraints} ancestor/shared/descendant constraint sections; included direct matches are not complete contracts.")
    warning_total = len(warnings)
    # Repeated ambiguity/link diagnostics must not defeat the output budget either.
    if warning_total > 48:
        warnings = warnings[:45] + warnings[-2:] + [f"Warning list bounded; {warning_total - 47} additional warnings omitted."]
    return {"schema_version": 1, "kind": "derived_reference", "authority": False,
            "notice": "Reading aid only; not authority, approval, or a complete contract. Git is observed provenance only. State is author classification. Review ambiguity with the Orchestrator.",
            "seed_ids": seeds, "limits": {"max_chars": max_chars, "max_sections": MAX_SECTIONS},
            "excerpt_chars": used, "sections": selected, "omitted_sections": omitted,
            "omitted_sections_total": omitted_total, "omitted_sections_listed": len(omitted),
            "omitted_sections_remaining": omitted_total - len(omitted),
            "warnings_total": warning_total,
            "truncated": bool(omitted_total), "incomplete": bool(warnings or omitted_total), "warnings": warnings}
