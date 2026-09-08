import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("vulcan_product_worker_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
# Import without replacing the test runner's Windows stdout/stderr wrappers.
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class ProductWorkerTests(unittest.TestCase):
    def project(self, profile="product", stack="skeleton", gate="impl"):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.write(root / "session.json", json.dumps({
            "project": "worker-fixture", "profile": profile, "current_gate": gate,
            "implementation": {"waves": {"current": "", "items": []}}, "stats": {},
        }))
        self.write(root / "vulcan.config.json", json.dumps({
            "delivery_profile": profile, "workflow": {"enabled": False},
            "runtime": {"gemini_long_context_mode": True},
        }))
        self.write(root / "AGENTS.md", "# Fixture worker rules\n")
        self.write(root / vulcan.PRODUCT_WORKER_GUIDE, "# Neutral worker guide\n")
        self.write(root / "docs/product/PRODUCT_CONTRACTS.md", (
            "| Scenario | Requirement | API | Data | UI | Regression |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| SCN-001 | REQ-001 | API-001 | DATA-001 | UI-001 | REG-001 |\n"
        ))
        self.write(root / "docs/artifacts/02-design/unrelated.md", "# Unrelated design\n")
        if stack == "python":
            self.write(root / "pyproject.toml", "[project]\nname = 'fixture'\nversion = '0.1'\n")
            self.write(root / "app/service.py", "def value():\n    return 1\n")
            self.write(root / "tests/test_service.py", "def test_value():\n    assert True\n")
        elif stack == "node":
            self.write(root / "package.json", json.dumps({"scripts": {"test:unit": "node --test"}}))
            self.write(root / "src/service.js", "export const value = 1;\n")
        return root

    @staticmethod
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def draft(self, root, entry="wave-start", scaffold=False, seed="SCN-001"):
        session = json.loads((root / "session.json").read_text(encoding="utf-8"))
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(vulcan, "sync_session", return_value=session), \
                mock.patch.object(vulcan, "refresh_session_stats"), \
                mock.patch.object(vulcan, "workflow_branch_guard"), \
                mock.patch.object(vulcan, "version_run_document"):
            if entry == "wave-start":
                vulcan.cmd_wave_start(
                    "BW-000" if scaffold else "BW-001", title="Bounded worker",
                    trace_seed=seed, related_ids="SEC-001", project_dir=str(root),
                )
            else:
                vulcan.cmd_run_new(
                    "codex-gpt", "impl", "implementation-scaffold" if scaffold else "build-wave",
                    "Bounded worker", "SEC-001", trace_seed=seed, project_dir=str(root),
                )
        return sorted((root / "docs/runs").glob("*.md"))[-1]

    def ready(self, path, commands=None, cwd="."):
        content = path.read_text(encoding="utf-8")
        if not vulcan.parse_simple_yaml_block(content).get("bw_id"):
            content = content.replace("status: Draft", "bw_id: BW-001\nstatus: Draft", 1)
        content = re.sub(
            r'    - "TBD: Orchestrator must assign exact code/test paths[^\n]*',
            '    - "app/service.py"\n    - "tests/test_service.py"', content,
        )
        content = re.sub(r'^  cwd: .+$', "  cwd: " + json.dumps(cwd), content, flags=re.MULTILINE)
        commands = commands if commands is not None else ["python -m pytest tests/test_service.py"]
        command_lines = "\n".join("    - " + json.dumps(command) for command in commands)
        content = re.sub(r'  commands:\n.*?\n  evidence:', "  commands:\n" + command_lines + "\n  evidence:", content, flags=re.DOTALL)
        self.write(path, content)
        return content

    def test_both_generators_are_stack_neutral_and_bounded(self):
        for entry in ("wave-start", "run-new"):
            for stack in ("python", "node", "skeleton"):
                for scaffold in (False, True):
                    with self.subTest(entry=entry, stack=stack, scaffold=scaffold):
                        root = self.project(stack=stack)
                        path = self.draft(root, entry, scaffold)
                        content = path.read_text(encoding="utf-8")
                        meta = vulcan.parse_simple_yaml_block(content)
                        contract = vulcan.parse_run_input_contract_yaml(content)
                        self.assertEqual(meta["skill_path"], vulcan.PRODUCT_WORKER_GUIDE)
                        self.assertEqual(meta["skill"], "implementation-scaffold" if scaffold else "build-wave")
                        for key in ("profile", "adapter", "skill", "run_type", "gate", "persona"):
                            self.assertEqual(meta[key], contract[key])
                        rel_path = path.relative_to(root).as_posix()
                        self.assertEqual(vulcan.extract_nested_yaml_list(content, "source_documents", "read_first"), [rel_path, "AGENTS.md", vulcan.PRODUCT_WORKER_GUIDE])
                        self.assertEqual(vulcan.extract_nested_yaml_list(content, "source_documents", "working_documents"), [rel_path])
                        refs = vulcan.extract_nested_yaml_list(content, "source_documents", "reference_on_demand")
                        self.assertIn("docs/product/PRODUCT_CONTRACTS.md", refs)
                        self.assertIn("docs/product/PRODUCT_ARCHITECTURE.md", refs)
                        self.assertFalse(any("TRACEABILITY" in item or "REPORT" in item or "unrelated" in item for item in refs))
                        writable = vulcan.extract_nested_yaml_list(content, "scope", "writable")
                        self.assertEqual(len(writable), 2)
                        self.assertEqual(writable[0], rel_path)
                        self.assertTrue(writable[1].startswith("TBD:"))
                        commands = vulcan.extract_nested_yaml_list(content, "verification", "commands")
                        self.assertEqual(len(commands), 1)
                        self.assertTrue(commands[0].startswith("TBD:"))
                        for guessed in ("npm test", "npm run build", "python -m", "gradle", "npx playwright", "python vulcan.py run-"):
                            self.assertNotIn(guessed, content)
                        blockers, _ = vulcan.run_preflight_file(str(path))
                        self.assertTrue(any("writable scope" in item for item in blockers))
                        self.assertTrue(any("verification.commands" in item for item in blockers))
                        self.assertTrue(any("verification.cwd" in item for item in blockers))
                        self.assertEqual(vulcan.check_run_file(str(path))[0], [])

    def test_source_ids_and_security_apply_without_sec_seed(self):
        for entry in ("wave-start", "run-new"):
            with self.subTest(entry=entry):
                root = self.project()
                path = self.draft(root, entry)
                content = path.read_text(encoding="utf-8")
                targets = vulcan._extract_yaml_block_text(content, "target_contracts")
                for source_id in ("SCN-001", "REQ-001", "API-001", "DATA-001", "UI-001", "REG-001", "SEC-001"):
                    self.assertIn(source_id, targets)
                self.assertIn("seeds: [SCN-001]", content)
                self.assertIn("even when no SEC-ID is assigned", content)
                self.assertIn("authentication/authorization", content)
                self.assertIn("public contract conflicts", content)
                self.assertIn("PRODUCT_TRACEABILITY and report normalization are Orchestrator-owned", content)
                preset = vulcan.build_run_input_preset("product", "impl", "build-wave", "unused", "docs/runs/RUN-002.md")
                without_sec = vulcan.render_run_input_preset(preset, ["SCN-001"], "build", "impl")
                self.assertIn("These shared constraints apply to every Product Build Run", without_sec)
                self.assertIn("security_policy:", without_sec)

    def test_missing_placeholder_and_run_only_commands_block(self):
        root = self.project(stack="python")
        path = self.draft(root)
        original = path.read_text(encoding="utf-8")
        for commands in ([], ["TBD"], ["tbd: select tests"], ["TODO select tests"], ["TBC: tests"],
                         ["none"], ["NULL"], ["pending"], ["<test command>"], [""],
                         ["python -m pytest tests/test_service.py", "TBD"],
                         ["python vulcan.py run-check docs/runs/RUN-001.md"],
                         ["python vulcan.py run-preflight docs/runs/RUN-001.md"]):
            with self.subTest(commands=commands):
                self.write(path, original)
                self.ready(path, commands)
                self.assertTrue(any("verification.commands" in item for item in vulcan.run_preflight_file(str(path))[0]))
        self.write(path, original)
        content = self.ready(path)
        self.write(path, re.sub(r'\nverification:\n.*?\n```', '\n```', content, flags=re.DOTALL))
        self.assertTrue(any("verification.commands" in item for item in vulcan.run_preflight_file(str(path))[0]))

    def test_missing_or_placeholder_cwd_blocks(self):
        root = self.project(stack="python")
        path = self.draft(root)
        for cwd in ("", "TBD", "tbd: directory", "TODO directory", "TBC: directory",
                    "none", "NULL", "pending", "<cwd>", "does-not-exist"):
            with self.subTest(cwd=cwd):
                self.ready(path, cwd=cwd)
                self.assertTrue(any("verification.cwd" in item for item in vulcan.run_preflight_file(str(path))[0]))
        content = self.ready(path)
        self.write(path, re.sub(r'^  cwd:.*\n', '', content, flags=re.MULTILINE))
        self.assertTrue(any("verification.cwd" in item for item in vulcan.run_preflight_file(str(path))[0]))

    def test_concrete_commands_and_cwd_pass_for_both_generators(self):
        for entry in ("wave-start", "run-new"):
            for stack, command, cwd in (("python", "python -m pytest tests/test_service.py", "."), ("node", "node --test service.test.js", "src")):
                with self.subTest(entry=entry, stack=stack):
                    root = self.project(stack=stack)
                    path = self.draft(root, entry)
                    self.ready(path, [command], cwd)
                    self.assertEqual(vulcan.run_preflight_file(str(path))[0], [])

    def test_placeholder_words_inside_real_commands_and_paths_pass(self):
        for entry in ("wave-start", "run-new"):
            root = self.project(stack="python")
            path = self.draft(root, entry)
            for cwd in ("pending", "none", "null", "checks/pending", "checks/TODO"):
                (root / cwd).mkdir(parents=True, exist_ok=True)
                for command in (
                    'python -c "value = 1; assert value is not None"',
                    "python -m unittest tests.test_pending",
                    'python -c "assert len(\'TBD\') == 3"',
                    'python -c "assert len(\'<placeholder>\') == 13"',
                ):
                    with self.subTest(entry=entry, cwd=cwd, command=command):
                        self.ready(path, [command], cwd)
                        self.assertEqual(vulcan.run_preflight_file(str(path))[0], [])
            (root / "TBD").mkdir()
            self.ready(path, cwd="TBD")
            self.assertTrue(any("verification.cwd" in item for item in vulcan.run_preflight_file(str(path))[0]))

    def test_run_new_summary_uses_worker_guide_only_for_product_builds(self):
        for profile in ("product", "audit", "poc"):
            for scaffold in (False, True):
                with self.subTest(profile=profile, scaffold=scaffold):
                    path = self.draft(self.project(profile=profile), "run-new", scaffold)
                    content = path.read_text(encoding="utf-8")
                    summary = content.rsplit("### 요약", 1)[1].split("###", 1)[0]
                    if profile == "product":
                        self.assertIn(vulcan.PRODUCT_WORKER_GUIDE, summary)
                        self.assertIn("scoped changes, actual verification results and remaining issues", summary)
                        self.assertIn("Orchestrator owns output normalization", summary)
                        self.assertNotIn("RUN_OUTPUT_CONTRACT.md", summary)
                    else:
                        self.assertEqual(summary.strip(), "Draft 상태. 작업 완료 후 `RUN_OUTPUT_CONTRACT.md`에 맞춰 요약한다.")

    def test_scope_contract_and_metadata_guards_still_block(self):
        root = self.project(stack="python")
        path = self.draft(root)
        ready = self.ready(path)
        for needle, replacement, message in (
            ('    - "app/service.py"', '    - "session.json"', "session.json"),
            ('    - "app/service.py"', '    - "TBD: narrow scope"', "writable scope"),
            ('language: "Use the approved Product architecture/runtime for this Run."', 'language: "TBD: runtime"', "target_contracts"),
            ('bw_id: BW-001\n', '', "bw_id"),
            ('persona: build', 'persona: review', "persona"),
        ):
            with self.subTest(message=message):
                self.write(path, ready.replace(needle, replacement, 1))
                self.assertTrue(any(message in item for item in vulcan.run_preflight_file(str(path))[0]))

    def test_scaffold_contract_must_be_resolved_before_handoff(self):
        for entry in ("wave-start", "run-new"):
            with self.subTest(entry=entry):
                root = self.project(stack="python")
                path = self.draft(root, entry, scaffold=True)
                content = self.ready(path, ["python -m compileall app/service.py"])
                self.assertTrue(any("target_contracts" in item for item in vulcan.run_preflight_file(str(path))[0]))
                content = content.replace("TBD: Orchestrator must assign the skeleton file", "app/service.py")
                content = content.replace("TBD: approved interface/schema to scaffold", "value() -> int")
                content = content.replace("TBD: select the scoped skeleton smoke command and align it with verification.commands", "python -m compileall app/service.py")
                self.write(path, content)
                self.assertEqual(vulcan.run_preflight_file(str(path))[0], [])
                self.write(path, content.replace("contract_skeleton:", "omitted_skeleton:"))
                self.assertTrue(any("contract_skeleton" in item for item in vulcan.run_preflight_file(str(path))[0]))

    def test_gate_and_single_active_wave_guards_are_unchanged(self):
        root = self.project(gate="gate2")
        with self.assertRaises(SystemExit):
            self.draft(root)
        root = self.project()
        session = json.loads((root / "session.json").read_text(encoding="utf-8"))
        session["implementation"]["waves"] = {"current": "BW-002", "items": [{"id": "BW-002", "status": "In Progress"}]}
        self.write(root / "session.json", json.dumps(session))
        with self.assertRaises(SystemExit):
            self.draft(root)
        self.assertFalse((root / "docs/runs").exists())

    def test_execute_product_conditional_validation_and_audit_poc_unchanged(self):
        for profile in ("product", "audit", "poc"):
            with self.subTest(profile=profile):
                root = self.project(profile=profile, stack="python")
                path = self.draft(root)
                if profile == "product":
                    self.ready(path)
                with mock.patch.object(vulcan, "workflow_branch_guard"), \
                        mock.patch.object(vulcan, "run_preflight_file", wraps=vulcan.run_preflight_file) as preflight:
                    plan = vulcan._execute_plan("RUN-001", project_dir=str(root))
                self.assertEqual(preflight.call_count, 1)
                flow = "\n".join(plan["planned_flow"])
                if profile == "product":
                    self.assertEqual(plan["exit_code"], 0)
                    self.assertIn("already computed", flow)
                    self.assertNotIn("python vulcan.py run-preflight", flow)
                    self.assertIn("actual command/cwd/evidence/source/environment matching", flow)
                    self.assertIn("after code integration or change, new failures, or uncertain evidence", flow)
                    self.assertIn("Gate 4 required release validation remains mandatory", flow)
                    self.assertNotIn("Orchestrator reruns the Run-specific verification commands", flow)
                else:
                    self.assertIn("python vulcan.py run-preflight", flow)
                    self.assertIn("Orchestrator reruns the Run-specific verification commands", flow)
                    self.assertNotIn("Matching unchanged evidence", flow)

    def test_worker_returns_warnings_without_operational_check_loop(self):
        path = self.draft(self.project())
        content = path.read_text(encoding="utf-8")
        self.assertIn("Workers need not execute run-check or run-preflight", content)
        self.assertIn("do not chase timing metadata or warning cleanup", content)
        self.assertIn("broken required tests or unresolved scope/contract/security blockers are not completion", content)
        self.assertIn("Write evidence logs only to explicitly assigned file paths", content)
        self.assertNotIn("docs/product/evidence/", content)

    def test_completed_runs_keep_readiness_as_warnings_only(self):
        root = self.project(stack="python")
        path = self.draft(root)
        ready = self.ready(path)
        for status in ("Completed", "Verified", "CompletedWithIssues"):
            for missing in (True, False):
                with self.subTest(status=status, missing=missing):
                    content = ready.replace("status: InProgress", "status: " + status, 1)
                    if missing:
                        content = re.sub(r'\nverification:\n.*?\n```', '\n```', content, flags=re.DOTALL)
                    else:
                        content = content.replace("python -m pytest tests/test_service.py", "TBD: historical command")
                        content = content.replace('cwd: "."', 'cwd: "removed-worktree"')
                    self.write(path, content)
                    blockers, warnings = vulcan.run_preflight_file(str(path))
                    self.assertEqual(blockers, [])
                    self.assertTrue(any("verification.commands" in item for item in warnings))
                    self.assertTrue(any("verification.cwd" in item for item in warnings))
                    self.write(path, content.replace('    - "app/service.py"', '    - "session.json"'))
                    self.assertTrue(any("session.json" in item for item in vulcan.run_preflight_file(str(path))[0]))

    def test_historical_product_fixture_is_still_evaluable(self):
        root = self.project()
        fixture = next((ROOT / "scripts/regression/fixtures/simple-todo-product/docs/runs").glob("RUN-001_*.md"))
        path = root / "docs/runs" / fixture.name
        self.write(path, fixture.read_text(encoding="utf-8"))
        blockers, warnings = vulcan.run_preflight_file(str(path))
        self.assertEqual(blockers, [])
        self.assertTrue(any("Historical Product Build readiness" in item for item in warnings))

    def test_qa_fix_loop_is_not_routed_or_subject_to_build_readiness(self):
        root = self.project()
        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(vulcan, "version_run_document"):
            vulcan.cmd_run_new("codex-gpt", "gate4", "qa-fix-loop", "Bounded fix", "FIND-001", project_dir=str(root))
        path = next((root / "docs/runs").glob("*.md"))
        content = path.read_text(encoding="utf-8")
        self.assertNotIn(vulcan.PRODUCT_WORKER_GUIDE, content)
        self.assertEqual(vulcan.parse_simple_yaml_block(content)["skill_path"], vulcan.RUN_SKILLS["qa-fix-loop"])
        blockers, warnings = vulcan.run_preflight_file(str(path))
        self.assertTrue(any("target_contracts" in item for item in blockers))
        self.assertFalse(any("Product Build verification" in item for item in blockers + warnings))

    def test_execute_json_reports_blocked_draft_then_ready_handoff(self):
        root = self.project(stack="python")
        path = self.draft(root)
        for ready in (False, True):
            with self.subTest(ready=ready):
                if ready:
                    self.ready(path)
                output = io.StringIO()
                with contextlib.redirect_stdout(output), mock.patch.object(vulcan, "workflow_branch_guard"):
                    if ready:
                        vulcan.cmd_execute("RUN-001", dry_run=True, project_dir=str(root), emit_json=True)
                    else:
                        with self.assertRaises(SystemExit) as error:
                            vulcan.cmd_execute("RUN-001", dry_run=True, project_dir=str(root), emit_json=True)
                        self.assertEqual(error.exception.code, 1)
                plan = json.loads(output.getvalue())
                self.assertEqual(plan["preflight"]["status"], "pass" if ready else "block")
                self.assertIn("Run/contracts/scope/project state changes", plan["planned_flow"][0])
                self.assertEqual(plan["runner"]["model"], "")
                self.assertFalse((root / plan["delegation_sidecar"]["path"]).exists())

    def test_custom_agents_leave_model_and_effort_to_runtime(self):
        names = {"trace-scout", "run-drafter", "contract-reviewer", "qa-reader"}
        for name in names:
            with self.subTest(agent=name):
                config = tomllib.loads((ROOT / f".codex/agents/{name}.toml").read_text(encoding="utf-8"))
                self.assertEqual(config["name"], name)
                self.assertTrue(config["description"])
                self.assertTrue(config["developer_instructions"])
                self.assertNotIn("model", config)
                self.assertNotIn("model_reasoning_effort", config)

    def test_init_and_upgrade_install_worker_guide(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "product-fixture"
        expected = (ROOT / vulcan.PRODUCT_WORKER_GUIDE).read_text(encoding="utf-8")
        agents = {p.relative_to(ROOT): p.read_text(encoding="utf-8") for p in (ROOT / ".codex/agents").glob("*.toml")}
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(vulcan.subprocess, "run", side_effect=OSError("Git disabled in unit fixture")):
            vulcan.init(str(root), "worker-fixture", "Codex", profile="product", primary="codex-cli")
        guide = root / vulcan.PRODUCT_WORKER_GUIDE
        self.assertEqual(guide.read_text(encoding="utf-8"), expected)
        for rel_path, source in agents.items():
            self.assertEqual((root / rel_path).read_text(encoding="utf-8"), source)
            self.write(root / rel_path, 'model = "previous-fixed-model"\nmodel_reasoning_effort = "high"\n')
        user_config = "[agents]\ndefault_subagent_model = 'user-choice'\ndefault_subagent_reasoning_effort = 'high'\n"
        self.write(root / ".codex/config.toml", user_config)
        self.write(guide, "# Old worker guide\n")
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(vulcan.subprocess, "run", side_effect=AssertionError("No external processes in upgrade fixture")):
            vulcan.cmd_upgrade(str(root))
        self.assertEqual(guide.read_text(encoding="utf-8"), expected)
        for rel_path, source in agents.items():
            self.assertEqual((root / rel_path).read_text(encoding="utf-8"), source)
        self.assertEqual((root / ".codex/config.toml").read_text(encoding="utf-8"), user_config)
        self.assertEqual(json.loads((root / "session.json").read_text(encoding="utf-8"))["current_gate"], "phase0")


if __name__ == "__main__":
    unittest.main()
