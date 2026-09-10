import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from harness_eval.cli import build_prompt, finish_suite, run_suite, trial
from harness_eval.scenarios import SCENARIOS


class SuiteLifecycleTests(unittest.TestCase):
    def test_optional_global_instructions_are_frozen_for_harness_mode_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            global_instructions = root / "global-agents.md"
            global_instructions.write_text("# Global\n\n한국어로 응답한다.\n")
            args = SimpleNamespace(output=root / ".harness" / "evaluations", codex="fake",
                                   model="test", effort="medium", judge_model="test", judge_effort="high",
                                   timeout=10, repeat=1, scenario=["mechanical-edit"], mode="harness",
                                   global_instructions=global_instructions)
            report = {"scenario": "mechanical-edit", "mode": "harness", "repetition": 1,
                      "status": "satisfied", "annotated_question_count": 0,
                      "question_annotation_coverage": "unverified",
                      "question_annotation_limitation": "모든 질문 탐지는 보장하지 않음", "elapsed_seconds": 0,
                      "agent": {"termination_confirmed": True},
                      "judge": {"run": {"termination_confirmed": True, "interrupted": False}}}
            with patch("harness_eval.cli.trial", return_value=report) as call, patch("harness_eval.cli.subprocess.run") as version:
                version.return_value = SimpleNamespace(returncode=0, stdout="fake CLI")
                self.assertEqual(run_suite(args), 0)
            source = call.call_args.args[2]
            self.assertEqual((source / "global-instructions.md").read_text(), global_instructions.read_text())
            self.assertTrue((source / "scripts" / "records.py").is_file())
            self.assertTrue((source / ".codex-plugin" / "plugin.json").is_file())
            self.assertFalse(list(source.rglob("__pycache__")))
            manifest = json.loads(next(args.output.rglob("source-manifest.json")).read_text())
            self.assertIn("scripts/records.py", manifest)
            self.assertIn(".codex-plugin/plugin.json", manifest)
            configuration = json.loads(next(args.output.rglob("configuration.json")).read_text())
            self.assertTrue(configuration["global_instructions_included"])
            self.assertIn("synthetic observation scenario", " ".join(configuration["limitations"]))
            harness_prompt = build_prompt(SCENARIOS["mechanical-edit"], source, "harness")
            baseline_prompt = build_prompt(SCENARIOS["mechanical-edit"], source, "baseline")
            self.assertIn(str(source / "global-instructions.md"), harness_prompt)
            self.assertNotIn(str(source / "global-instructions.md"), baseline_prompt)

    def test_uncertain_judge_or_user_interruption_stops_following_calls(self):
        for interrupted in (False, True):
            with self.subTest(interrupted=interrupted), tempfile.TemporaryDirectory() as temporary:
                args = SimpleNamespace(output=Path(temporary) / ".harness" / "evaluations", codex="fake",
                                       model="test", effort="medium", judge_model="test", judge_effort="high",
                                       timeout=10, repeat=2, scenario=["mechanical-edit"], mode="paired")
                report = {"scenario": "mechanical-edit", "mode": "baseline", "repetition": 1,
                          "status": "unverified", "annotated_question_count": None,
                          "question_annotation_coverage": "unverified",
                          "question_annotation_limitation": "모든 질문 탐지는 보장하지 않음", "elapsed_seconds": 0,
                          "agent": {"termination_confirmed": True},
                          "judge": {"run": {"termination_confirmed": interrupted, "interrupted": interrupted}}}
                with patch("harness_eval.cli.trial", return_value=report) as call, patch("harness_eval.cli.subprocess.run") as version:
                    version.return_value = SimpleNamespace(returncode=0, stdout="fake CLI")
                    self.assertEqual(run_suite(args), 2)
                    self.assertEqual(call.call_count, 1)
                summaries = list(args.output.rglob("summary.json"))
                self.assertEqual(len(summaries), 1)
                summary = json.loads(summaries[0].read_text())
                self.assertTrue(summary["incomplete"])
                self.assertEqual(len(summary["runs"]), 1)

    def test_summary_carries_annotation_limit_and_markdown_discloses_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            suite = Path(temporary)
            report = {"scenario": "mechanical-edit", "mode": "baseline", "repetition": 1,
                      "status": "satisfied", "annotated_question_count": 0,
                      "question_annotation_coverage": "unverified",
                      "question_annotation_limitation": "모든 질문 탐지는 보장하지 않음",
                      "elapsed_seconds": 0, "synthetic_observation": False}
            self.assertEqual(finish_suite(suite, [report], True), 0)
            summary = json.loads((suite / "summary.json").read_text())
            self.assertEqual(summary["runs"][0]["annotated_question_count"], 0)
            self.assertEqual(summary["runs"][0]["question_annotation_coverage"], "unverified")
            self.assertIn("모든 질문", summary["runs"][0]["question_annotation_limitation"])
            markdown = (suite / "summary.md").read_text()
            self.assertIn("Annotated questions", markdown)
            self.assertIn("모든 질문 탐지는 보장하지 않는다", markdown)

    def test_trial_result_carries_judge_annotation_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            suite = root / "suite"
            source = root / "source"
            (source / "skills").mkdir(parents=True)
            args = SimpleNamespace(codex="fake", model="test", effort="medium",
                                   judge_model="judge", judge_effort="high", timeout=10)

            def fake_run_codex(codex, workspace, output, prompt, model, effort, timeout, **kwargs):
                output.mkdir(parents=True, exist_ok=True)
                events = output / "events.jsonl"
                events.write_text('{"item":{"type":"agent_message","text":"수정할까요?"}}\n')
                final = output / "final.txt"
                final.write_text("수정할까요?")
                return {"status": "satisfied", "termination_confirmed": True,
                        "paths": {"events": str(events), "final": str(final)}}

            judgment = {"status": "satisfied", "checks": [], "run": {"status": "satisfied"},
                        "annotated_question_count": 0, "question_annotation_coverage": "unverified",
                        "question_annotation_limitation": "모든 질문 탐지는 보장하지 않음"}
            with patch("harness_eval.cli.preflight", return_value={"status": "satisfied"}), \
                    patch("harness_eval.cli.run_codex", side_effect=fake_run_codex), \
                    patch("harness_eval.cli.evaluate", return_value=judgment):
                report = trial(args, suite, source, "mechanical-edit", "baseline", 1)
            stored = json.loads((suite / "01-mechanical-edit-baseline" / "result.json").read_text())
            self.assertEqual(report["annotated_question_count"], 0)
            self.assertEqual(stored["judge"]["annotated_question_count"], 0)
            self.assertEqual(stored["question_annotation_coverage"], "unverified")
            self.assertIn("모든 질문", stored["question_annotation_limitation"])


if __name__ == "__main__":
    unittest.main()
