"""Packaging regression only; does not exercise runtime role messaging."""

import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[3]
CORE = "docs/core/COLLABORATION_PROTOCOL.md"
ADAPTER = "docs/adapters/codex-gpt/PERSONA_DELEGATION.md"
BOOTSTRAP = "AGENTS.md"
SKILL = ".agents/skills/vulcan-orchestrator/SKILL.md"
ROUTING_DOCS = (CORE, ADAPTER, BOOTSTRAP, SKILL)

spec = importlib.util.spec_from_file_location("vulcan_collaboration_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
# Import without replacing the test runner's Windows stdout/stderr wrappers.
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class CollaborationDocsTests(unittest.TestCase):
    @staticmethod
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def project(self, profile):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "collaboration-fixture"
        # Only suppress init's Git side effects, never framework copying.
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(vulcan.subprocess, "run", side_effect=OSError("Git disabled in unit fixture")):
            vulcan.init(str(root), "collaboration-fixture", "Codex", profile=profile, primary="codex-cli")
        return root

    def assert_routing(self, root):
        contents = {}
        variables = vulcan.extract_variables(str(root))
        for relative in ROUTING_DOCS:
            with self.subTest(document=relative):
                self.assertTrue((ROOT / relative).is_file(), f"Pending framework source: {relative}")
                self.assertTrue((root / relative).is_file(), f"Not installed: {relative}")
                contents[relative] = (root / relative).read_text(encoding="utf-8")
                self.assertEqual(contents[relative], vulcan.render(
                    (ROOT / relative).read_text(encoding="utf-8"), variables,
                ))
        # Accept prose/code-path references as well as Markdown hyperlinks.
        for source, targets in ((BOOTSTRAP, (CORE, ADAPTER)),
                                (SKILL, (CORE, ADAPTER)), (ADAPTER, (CORE,))):
            for target in targets:
                with self.subTest(source=source, target=target):
                    self.assertTrue(Path(target).name in contents.get(source, ""),
                                    f"Missing routing reference: {source} -> {target}")

    def test_init_installs_collaboration_routing_for_all_profiles(self):
        for profile in ("poc", "product", "audit"):
            with self.subTest(profile=profile):
                self.assert_routing(self.project(profile))

    def test_upgrade_refreshes_routing_and_preserves_authored_product_state(self):
        root = self.project("product")
        authored = {
            "docs/product/PRODUCT_CONTRACTS.md": "# Authored contracts\n\nSCN-901 / REQ-901\n",
            "docs/runs/RUN-901_authored.md": "# Authored Run fixture\n\nKeep scoped evidence.\n",
            "app/service.py": "def value():\n    return 901\n",
        }
        for relative, content in authored.items():
            self.write(root / relative, content)
        expected_files = {relative: (root / relative).read_bytes() for relative in authored}
        session_path = root / "session.json"
        session = json.loads(session_path.read_text(encoding="utf-8"))
        session["current_gate"] = "impl"
        session["vulcan_version"] = "0.0.0"
        self.write(session_path, json.dumps(session))
        config_before = json.loads((root / "vulcan.config.json").read_text(encoding="utf-8"))
        for relative in ROUTING_DOCS:
            self.write(root / relative, "# Outdated framework routing\n")

        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(vulcan.subprocess, "run", side_effect=AssertionError("No external processes in upgrade fixture")):
            vulcan.cmd_upgrade(str(root))

        for relative, expected in expected_files.items():
            with self.subTest(authored=relative):
                self.assertEqual((root / relative).read_bytes(), expected)
        after = json.loads(session_path.read_text(encoding="utf-8"))
        self.assertEqual(after["current_gate"], "impl")
        self.assertEqual(after["profile"], session["profile"])
        self.assertEqual(vulcan.load_delivery_profile(str(root)), "product")
        config_after = json.loads((root / "vulcan.config.json").read_text(encoding="utf-8"))
        self.assertEqual(config_after["delivery_profile"], config_before["delivery_profile"])
        self.assertEqual(after["vulcan_version"], vulcan.read_version_from_vulcan(str(ROOT / "vulcan.py")))
        self.assert_routing(root)

    def test_installed_local_markdown_links_resolve(self):
        root = self.project("product")
        for relative in ROUTING_DOCS:
            with self.subTest(document=relative):
                document = root / relative
                self.assertTrue(document.is_file(), f"Not installed: {relative}")
                content = document.read_text(encoding="utf-8")
                # Check ordinary inline and reference-style links, not example code.
                content = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", content)
                targets = re.findall(r"\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)", content)
                targets += re.findall(r"(?m)^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)", content)
                for target in targets:
                    url = urlsplit(target.strip("<>"))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    path = unquote(url.path)
                    resolved = root / path.lstrip("/") if path.startswith("/") else document.parent / path
                    with self.subTest(document=relative, link=target):
                        self.assertTrue(resolved.exists(), f"Broken local link: {relative} -> {target}")


if __name__ == "__main__":
    unittest.main()
