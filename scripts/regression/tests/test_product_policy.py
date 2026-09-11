"""Known instruction regressions, not a semantic audit of every instruction."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STAGE_SKILLS = (
    ".agents/skills/vulcan-design/SKILL.md",
    ".agents/skills/vulcan-impl-wave/SKILL.md",
    ".agents/skills/vulcan-qa/SKILL.md",
    ".agents/skills/vulcan-release/SKILL.md",
)


class ProductPolicyTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_direct_edit_restrictions_have_a_non_product_section(self):
        text = self.read("docs/core/ORCHESTRATOR_PROTOCOL.md")
        section = text.split("### Product 이외의 직접 구현 제한", 1)[1].split("### QA 실행 경로", 1)[0]
        self.assertIn("Audit/PoC에 적용", section)
        self.assertIn("30 LOC", section)
        self.assertIn("네 개의 Run 생성을 요구하지 않는다", text)

    def test_change_control_routes_product_without_mandatory_run_or_full_suite(self):
        text = self.read("docs/core/CHANGE_CONTROL_PROCESS.md")
        self.assertNotIn("Gate를 다시 진행할 때는 Run 문서가 필수다. Run은", text)
        self.assertIn("기존 CR/이슈/작업 요약을 사용하며 Run은 선택", text)
        self.assertIn("아래 실행 기준은 Audit/PoC에 적용", text)
        self.assertNotIn("| CR 승인, 즉시 반영 | 바로 Run 생성 |", text)

    def test_product_authority_and_scoped_verification_remain_canonical(self):
        text = self.read("docs/core/PRODUCT_PROFILE_BASELINE.md")
        for rule in ("Run과 Wave는 Product의 필수 산출물이 아니다", "같은 허가를 다시 요청하지 않는다",
                     "검증만 맡은 담당자는 수정 후보를 총괄에게 반환", "필수 검증 미실행은 Pass가 아니다",
                     "제품 테스트를 기계적으로 재실행하지 않음"):
            self.assertIn(rule, text)

    def test_skills_route_instead_of_requiring_product_helpers_and_fix_runs(self):
        qa = self.read(".agents/skills/vulcan-qa/SKILL.md")
        impl = self.read(".agents/skills/vulcan-impl-wave/SKILL.md")
        for text in (qa, impl):
            self.assertIn("PRODUCT_PROFILE_BASELINE.md", text)
        self.assertIn("not four mandatory Runs", qa)
        self.assertIn("same permission again", qa)
        self.assertIn("verification-only worker", qa)
        self.assertIn("consider `qa-reader`", qa)
        self.assertIn("consider `trace-scout`", impl)
        self.assertIn("consider `run-drafter`", impl)
        self.assertNotIn("Start `qa-fix-loop` only after Orchestrator/user decision.", qa)

    def test_checklist_and_bootstrap_do_not_restore_mandatory_product_wave(self):
        text = self.read("docs/core/GATE_EXECUTION_CHECKLIST.md")
        implementation = next(line for line in text.splitlines() if line.startswith("| Impl |"))
        self.assertIn("Product는 승인된 현재 작업 범위", implementation)
        self.assertIn("Audit/PoC", implementation)
        bootstrap = self.read(".agents/skills/vulcan-orchestrator/SKILL.md")
        self.assertIn("For Product execution, start with", bootstrap)
        self.assertNotIn("If the task is non-trivial, read `docs/core/ORCHESTRATOR_PROTOCOL.md`.", bootstrap)

    def test_marked_pilot_routes_before_legacy_in_codex_and_gemini(self):
        for path in ("AGENTS.md", "GEMINI.md", ".agents/skills/vulcan-orchestrator/SKILL.md"):
            with self.subTest(path=path):
                text = self.read(path)
                route = text.index("`process_model`")
                self.assertIn("ORCHESTRATOR_CLI_GUIDE.md", text[route:route + 260])
                legacy = text.find("gate-start")
                if legacy >= 0:
                    self.assertLess(route, legacy)
        guide = self.read("docs/core/ORCHESTRATOR_CLI_GUIDE.md").split("### 4.1", 1)[1].split("## 5.", 1)[0]
        self.assertIn("검증 전용 위임으로 코드나 상태를 수정하지 않는다", guide)
        self.assertIn("일반 `init`/`upgrade`는 이 모델을 활성화하지 않는다", guide)

    def test_worker_and_result_template_do_not_restore_git_evidence(self):
        worker = self.read("docs/core/PRODUCT_WORKER_GUIDE.md")
        self.assertIn("No Git evidence or pre-test commit is required", worker)
        self.assertNotIn("storage commit as the tested source commit", worker)
        template = self.read("docs/templates/product/PRODUCT_VERIFICATION_RESULT_TEMPLATE.md")
        self.assertNotIn("Git 또는 스냅샷", template)
        self.assertIn("실제 실행 명령 / cwd", template)
        output = self.read("docs/core/RUN_OUTPUT_CONTRACT.md")
        self.assertNotIn("  commit: null", output)

    def test_stage_skills_route_marked_process_before_legacy_preconditions(self):
        for path in STAGE_SKILLS:
            with self.subTest(path=path):
                text = self.read(path)
                route = text.index("`process_model`")
                self.assertIn("ORCHESTRATOR_CLI_GUIDE.md", text[route:route + 400])
                self.assertIn("unsupported", text[route:route + 500])
                self.assertLess(route, text.index("session.json"))
                self.assertIn("PRODUCT_PROFILE_BASELINE.md", text)

    def test_product_adapter_workflows_route_before_general_run_requirements(self):
        for name in ("implementation-plan", "qa-fix-loop", "change-impact-analysis", "independent-review"):
            with self.subTest(skill=name):
                text = self.read(f"docs/adapters/codex-gpt/skills/{name}.md")
                route = text.index("PRODUCT_PROFILE_BASELINE.md")
                self.assertLess(route, text.index("## 필수 입력"))
                self.assertIn("Audit/PoC", text)
        fix = self.read("docs/adapters/codex-gpt/skills/qa-fix-loop.md")
        self.assertNotIn("Orchestrator는 `qa-fix-loop` Run을 먼저 만들고", fix)
        change = self.read("docs/adapters/codex-gpt/skills/change-impact-analysis.md")
        self.assertNotIn("승인된 CR을 처리할 때는 반드시 관련 Run 문서를 만들고", change)

    def test_product_gate_prompts_and_wave_checks_are_scoped(self):
        prompt = self.read("docs/adapters/codex-gpt/GATE_PROMPTS.md")
        self.assertNotIn("필수 Core:", prompt.splitlines())
        self.assertIn("## 2. Product", prompt)
        wave = self.read("docs/adapters/codex-gpt/skills/build-wave.md")
        verification = wave.split("## 검증 경계", 1)[1].split("## Orchestrator", 1)[0]
        self.assertNotIn("worker 테스트를 재실행하고", verification)
        self.assertIn("Product", verification)
        self.assertIn("Audit/PoC", verification)

    def test_qa_skill_records_command_results_without_source_identity(self):
        qa = self.read(".agents/skills/vulcan-qa/SKILL.md")
        self.assertIn("execute --verify", qa)
        self.assertNotIn("tested-source identity", qa)
        self.assertNotIn("command success, source identity", qa)


if __name__ == "__main__":
    unittest.main()
