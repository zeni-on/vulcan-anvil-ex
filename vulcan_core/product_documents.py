"""Read Product ledgers and explicitly linked detail without relocating sources.

Unlike excerpt lookup, incomplete input is a validation issue, not a usable
truncated contract. This module never infers approval or executes references.
"""

from collections import deque
import re
from pathlib import Path

from .document_context import (
    _anchor_indices, _document, _links, _reference_definitions, _sections,
    EXCLUDED_DIRS, MAX_BYTES, MAX_LINKS,
)

ROOTS = {
    "PRODUCT_BRIEF.md": ("docs/artifacts/01-requirements/",),
    "PRODUCT_ARCHITECTURE.md": ("docs/artifacts/02-design/",),
    "ADR_LOG.md": ("docs/artifacts/02-design/architecture/",),
    "PRODUCT_CONTRACTS.md": ("docs/artifacts/02-design/",),
    "PRODUCT_TRACEABILITY.md": ("docs/artifacts/02-traceability/",),
    "REGRESSION_AND_RELEASE_REPORT.md": ("docs/artifacts/03-test/", "docs/artifacts/04-review/", "docs/artifacts/07-release/"),
}
MAX_DOCUMENTS = 128
MAX_DEPTH = 4
MAX_REFERENCES = 512
HISTORY = re.compile(r"\bhistory\b|\bhistorical\b|\barchive\w*\b|\bprevious\b|\bpast\b|\bsuperseded\b|\uacfc\uac70|\uc774\ub825|\uc774\uc804", re.I)


def active_section(section, sections, historical_titles=False):
    if section["state"] in {"candidate", "history"}:
        return False
    titles = [section["heading"]] + [sections[i]["heading"] for i in section["parents"]]
    return not historical_titles or section["state"] == "current" or not any(HISTORY.search(t) for t in titles)


def substantive(text):
    text = re.sub(r"(?ms)^---\s*\n.*?^---\s*$", "", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = []
    source_lines = text.splitlines()
    for i, line in enumerate(source_lines):
        line = line.strip()
        if not line or line.startswith("#") or re.fullmatch(r"[-=| :]+", line):
            continue
        if re.search(r"\[[^\]]*\]\([^)]*\)", line):
            continue
        if i+1 < len(source_lines) and "|" in line and re.fullmatch(r"[| :\-]+", source_lines[i+1].strip()):
            continue
        lines.append(line)
    return bool(lines)


class ProductDocuments:
    def __init__(self, project_dir, names=None):
        self.root = Path(project_dir).resolve()
        self.issues = []
        self.warnings = []
        self.cache = {}
        self.groups = {}
        self.linked = set()
        self.reference_count = 0
        for name in names if names is not None else [n for n in ROOTS if (self.root / "docs/product" / n).exists()]:
            name = Path(name).name
            if name in ROOTS:
                self.groups[name] = self._collect(name)

    def _read(self, relative):
        if relative in self.cache:
            return self.cache[relative]
        if len(self.cache) >= MAX_DOCUMENTS:
            self.issues.append(f"Product document limit ({MAX_DOCUMENTS}): {relative}; input incomplete.")
            return None
        try:
            path = _document(self.root, relative)
            with path.open("rb") as stream:
                raw = stream.read(MAX_BYTES+1)
            if len(raw) > MAX_BYTES:
                raise ValueError("document exceeds size limit")
            sections = _sections(raw.decode("utf-8-sig"))
        except (OSError, ValueError, UnicodeError) as exc:
            self.issues.append(f"Product source unreadable: {relative}: {exc}")
            sections = None
        self.cache[relative] = sections
        return sections

    def _collect(self, name):
        root = f"docs/product/{name}"
        queue = deque([(root, "", 0)])
        selected, visited = {}, set()
        while queue:
            path, anchor, depth = queue.popleft()
            if (path, anchor) in visited:
                continue
            visited.add((path, anchor))
            sections = self._read(path)
            if sections is None:
                continue
            if anchor:
                start = _anchor_indices(sections).get(anchor)
                if start is None:
                    self.issues.append(f"Product source anchor missing: {path}#{anchor}")
                    continue
                indices = {j for j, s in enumerate(sections) if j == start or start in s["parents"]}
                indices.update(sections[start]["parents"])
            else:
                indices = set(range(len(sections)))
            definitions = _reference_definitions("".join(s["visible"] for s in sections))
            for i in sorted(indices):
                section = sections[i]
                if not active_section(section, sections, historical_titles=name == "REGRESSION_AND_RELEASE_REPORT.md"):
                    continue
                if section["state_conflict"]:
                    self.issues.append(f"Product source state conflict: {path}:{section['start_line']}")
                    continue
                indices_seen = selected.setdefault(path, set())
                if i in indices_seen:
                    continue
                indices_seen.add(i)
                links = _links(self.root, path, section["visible"], definitions)
                if len(links) > MAX_LINKS:
                    self.issues.append(f"Product section reference limit: {path}:{section['start_line']}; input incomplete.")
                for link in links[:MAX_LINKS]:
                    self.reference_count += 1
                    if self.reference_count > MAX_REFERENCES:
                        if self.reference_count == MAX_REFERENCES+1:
                            self.issues.append("Product reference limit: input incomplete.")
                        break
                    target = link["path"]
                    # Other ledgers and folders are navigation/evidence links,
                    # not definitions owned by this logical document.
                    other_ledger = target.startswith("docs/product/") and Path(target).name in ROOTS and target != root
                    owned = (target.startswith("docs/product/") or any(target.startswith(p) for p in ROOTS[name]))
                    if other_ledger or target and not owned:
                        if link["status"] != "available":
                            self.warnings.append(f"Product reference unavailable: {path}:{section['start_line']} -> {link['target']}")
                        elif not other_ledger:
                            self.warnings.append(f"Product reference outside document ownership (not included): {path}:{section['start_line']} -> {link['target']}")
                        continue
                    self.linked.add(name)
                    if link["status"] != "available" or EXCLUDED_DIRS.intersection(p.lower() for p in Path(target).parts):
                        self.issues.append(f"Product source reference {link['status']}: {path}:{section['start_line']} -> {link['target']}")
                        continue
                    if depth >= MAX_DEPTH and (target, link["anchor"]) not in visited:
                        self.issues.append(f"Product source depth limit: {path}:{section['start_line']} -> {link['target']}")
                        continue
                    queue.append((target, link["anchor"], depth+1))
        return [
            {"path": path, "sections": [self.cache[path][i] for i in sorted(indices)],
             "content": "".join(self.cache[path][i]["excerpt"] for i in sorted(indices))}
            for path, indices in selected.items()
        ]

    def documents(self, name):
        return self.groups.get(Path(name).name, [])

    def texts(self, name):
        return [d["content"] for d in self.documents(name)]

    def text(self, name):
        return "\n".join(self.texts(name))

    def records(self, name, pattern, parse_tables):
        """Primary IDs define rows; mentions and linked index cells do not."""
        rows, seen = [], {}
        for document in self.documents(name):
            for section in document["sections"]:
                for headers, table in parse_tables(section["visible"]):
                    for row in table:
                        if not headers:
                            continue
                        primary = row.get(headers[0], "").strip().strip("`")
                        if not re.fullmatch(pattern, primary):
                            continue
                        values = [row.get(header, "").strip() for header in headers]
                        key = tuple(re.sub(r"\s+", " ", v) for v in values)
                        source = f"{document['path']}:{section['start_line']}"
                        previous = seen.setdefault(primary, {})
                        if key in previous:
                            continue
                        if previous:
                            self.issues.append(f"Product conflicting definitions {primary}: {next(iter(previous.values()))}; {source}. No winner selected.")
                        previous[key] = source
                        rows.append({"id": primary, "cells": values, "row": row, "headers": headers, "source": source})
        return rows

    def diagnostics(self):
        return {"incomplete": bool(self.issues or self.warnings), "issues": list(dict.fromkeys(self.issues)),
                "warnings": list(dict.fromkeys(self.warnings)), "sources": sorted(self.cache)}
