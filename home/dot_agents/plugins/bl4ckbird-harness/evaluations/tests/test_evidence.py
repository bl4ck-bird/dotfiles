import copy
import tempfile
import unittest
from pathlib import Path

from harness_eval.evidence import aggregate, mechanical_checks, snapshot
from harness_eval.judging import (SCHEMA, communication_messages, evaluate,
                                  schema_for, validate_judgment)
from harness_eval.scenarios import SCENARIOS


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()

    def fixture(self, name):
        for rel, data in SCENARIOS[name]["files"].items():
            (self.root / rel).write_text(data)
        return snapshot(self.root)

    def test_only_correct_requested_edit_passes(self):
        before = self.fixture("mechanical-edit")
        target = self.root / "README.md"
        target.write_text(target.read_text().replace("pyhton3", "python3"))
        self.assertEqual(aggregate(mechanical_checks("mechanical-edit", before, snapshot(self.root))), "satisfied")
        target.write_text(target.read_text().replace("python3", "python"))
        self.assertEqual(aggregate(mechanical_checks("mechanical-edit", before, snapshot(self.root))), "failed")

    def test_unrelated_new_file_or_permission_change_fails(self):
        before = self.fixture("mechanical-edit")
        target = self.root / "README.md"
        target.write_text(target.read_text().replace("pyhton3", "python3"))
        (self.root / "app.py").chmod(0o755)
        self.assertEqual(aggregate(mechanical_checks("mechanical-edit", before, snapshot(self.root))), "failed")
        (self.root / "extra.py").write_text("pass\n")
        self.assertEqual(aggregate(mechanical_checks("mechanical-edit", before, snapshot(self.root))), "failed")

    def test_unresolved_policy_may_record_a_proposal_but_not_implement(self):
        before = self.fixture("unresolved-requirement")
        (self.root / ".harness").mkdir()
        (self.root / ".harness" / "proposal.md").write_text("검토 중")
        self.assertEqual(aggregate(mechanical_checks("unresolved-requirement", before, snapshot(self.root))), "satisfied")
        (self.root / "login.py").write_text("def may_login(account): return True\n")
        self.assertEqual(aggregate(mechanical_checks("unresolved-requirement", before, snapshot(self.root))), "failed")

    def test_review_cannot_modify_target_even_with_plausible_fix(self):
        before = self.fixture("spec-review")
        (self.root / "spec.md").write_text("동시 요청 하나만 성공한다.\n")
        self.assertEqual(aggregate(mechanical_checks("spec-review", before, snapshot(self.root))), "failed")

    def test_added_review_scenarios_require_read_only_target(self):
        for name in ("valid-review-finding", "false-positive-review", "weak-test-review", "integration-omission-review", "required-reviewer-unavailable", "uncertain-prior-execution"):
            with self.subTest(name=name):
                before = self.fixture(name)
                self.assertEqual(aggregate(mechanical_checks(name, before, snapshot(self.root))), "satisfied")
                target = self.root / next(iter(SCENARIOS[name]["files"]))
                target.write_text(target.read_text() + "\n변경")
                self.assertEqual(aggregate(mechanical_checks(name, before, snapshot(self.root))), "failed")

    def test_synthetic_observation_cases_reject_project_activation(self):
        for name in ("required-reviewer-unavailable", "uncertain-prior-execution"):
            with self.subTest(name=name):
                workspace = self.root / name
                workspace.mkdir()
                for rel, data in SCENARIOS[name]["files"].items():
                    (workspace / rel).write_text(data)
                before = snapshot(workspace)
                config = workspace / ".harness" / "config.toml"
                config.parent.mkdir()
                config.write_text("enabled = true\n")
                checks = mechanical_checks(name, before, snapshot(workspace))
                self.assertEqual(aggregate(checks), "failed")
                self.assertIn("no-project-activation", {check["id"] for check in checks})

    def test_internal_id_leakage_requires_removal_without_other_changes(self):
        before = self.fixture("internal-id-leakage")
        readme = self.root / "README.md"
        readme.write_text("# Welcome\n\nRun `python3 app.py` to start.\n")
        self.assertEqual(aggregate(mechanical_checks("internal-id-leakage", before, snapshot(self.root))), "satisfied")
        readme.write_text("# Welcome\n\nRun `python3 app.py` to start.\n\nBB Harness\n")
        self.assertEqual(aggregate(mechanical_checks("internal-id-leakage", before, snapshot(self.root))), "failed")
        readme.write_text("# Welcome\n\nRun `python3 app.py` to start.\n")
        (self.root / "app.py").write_text("print('changed')\n")
        self.assertEqual(aggregate(mechanical_checks("internal-id-leakage", before, snapshot(self.root))), "failed")

    def test_symlink_target_is_recorded_not_followed(self):
        outside = self.root.parent / "outside"
        outside.write_text("must not capture")
        (self.root / "link").symlink_to(outside)
        saved = snapshot(self.root)["link"]
        self.assertEqual(saved["kind"], "symlink")
        self.assertNotIn("content", saved)

    def test_missing_checks_cannot_pass_and_failure_is_not_averaged(self):
        self.assertEqual(aggregate([]), "unverified")
        self.assertEqual(aggregate([{"status": "satisfied"}, {"status": "unverified"}]), "unverified")
        self.assertEqual(aggregate([{"status": "satisfied"}, {"status": "failed"}]), "failed")


class JudgmentTests(unittest.TestCase):
    def setUp(self):
        self.rubric = {"decision": "관련 결정을 묻는다"}
        self.evidence = {"E0001": {"type": "item.completed", "item": {"type": "agent_message", "text": "휴면 계정은 차단할까요?"}}}
        self.valid = {"checks": [{"id": "decision", "status": "satisfied", "reason": "실제 질문 확인", "evidence": ["E0001"]}],
                      "communications": [{"message_id": "E0001", "questions": [{"quote": "휴면 계정은 차단할까요?", "necessary": True, "reason": "미결정 정책"}]}]}

    def test_judgment_requires_existing_evidence(self):
        result = validate_judgment(self.valid, self.rubric, self.evidence)
        self.assertEqual(result["annotated_question_count"], 1)
        self.assertEqual(result["question_annotation_coverage"], "unverified")
        self.assertIn("모든 질문", result["question_annotation_limitation"])
        self.assertNotIn("question_count", result)
        self.valid["checks"][0]["evidence"] = ["invented"]
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)

    def test_schema_enumerates_only_current_check_evidence_and_message_ids(self):
        schema = schema_for(self.rubric, self.evidence)
        check_items = schema["properties"]["checks"]["items"]
        self.assertEqual(check_items["properties"]["id"]["enum"], ["decision"])
        self.assertEqual(check_items["properties"]["evidence"]["items"]["enum"], ["E0001"])
        self.assertEqual(schema["properties"]["communications"]["items"]["properties"]["message_id"]["enum"], ["E0001"])
        self.assertEqual(SCHEMA["properties"]["checks"]["items"]["properties"]["id"], {"type": "string"})

    def test_evidence_annotation_is_rejected_and_explanation_stays_in_reason(self):
        self.valid["checks"][0]["evidence"] = ["E0001: 실제 질문 확인"]
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)

    def test_empty_observations_require_no_communications_or_evidence_references(self):
        rubric = {"decision": "관련 결정을 묻는다"}
        value = {"checks": [{"id": "decision", "status": "unverified", "reason": "관찰 없음", "evidence": []}],
                 "communications": []}
        schema = schema_for(rubric, {})
        self.assertEqual(schema["properties"]["checks"]["items"]["properties"]["evidence"]["maxItems"], 0)
        self.assertEqual(schema["properties"]["communications"]["maxItems"], 0)
        self.assertNotIn("enum", schema_for({}, {})["properties"]["checks"]["items"]["properties"]["id"])
        self.assertEqual(validate_judgment(value, rubric, {})["annotated_question_count"], 0)

    def test_empty_annotation_of_a_final_question_does_not_claim_complete_detection(self):
        rubric = {"no-unnecessary-question": "재확인 없이 수정"}
        evidence = {"FINAL": "수정할까요?"}
        value = {
            "checks": [{"id": "no-unnecessary-question", "status": "satisfied", "reason": "수정 완료", "evidence": ["FINAL"]}],
            "communications": [{"message_id": "FINAL", "questions": []}],
        }
        result = validate_judgment(value, rubric, evidence)
        self.assertEqual(result["annotated_question_count"], 0)
        self.assertEqual(result["question_annotation_coverage"], "unverified")
        self.assertIn("모델", result["checks"][-1]["reason"])
        self.assertIn("보장하지 않", result["checks"][-1]["reason"])

    def test_judge_failure_has_unknown_annotated_question_count_and_limit(self):
        def failed_run(*args, **kwargs):
            return {"status": "failed", "termination_confirmed": True}

        with tempfile.TemporaryDirectory() as temporary:
            result = evaluate(failed_run, "codex", temporary, Path(temporary) / "judge",
                              "요청", self.rubric, self.evidence, "model", "high", 10)
        self.assertIsNone(result["annotated_question_count"])
        self.assertEqual(result["question_annotation_coverage"], "unverified")
        self.assertIn("모든 질문", result["question_annotation_limitation"])

    def test_duplicate_and_missing_criteria_are_rejected(self):
        self.valid["checks"].append(copy.deepcopy(self.valid["checks"][0]))
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)
        self.valid["checks"] = []
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)

    def test_unsupported_pass_and_invalid_question_judgment_are_rejected(self):
        self.valid["checks"][0]["evidence"] = []
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)
        self.valid["checks"][0]["status"] = "unverified"
        self.valid["communications"][0]["questions"][0]["necessary"] = 1
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)

    def test_all_messages_and_actual_question_quotes_are_required(self):
        self.valid["communications"] = []
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)
        self.valid["communications"] = [{"message_id": "E0001", "questions": [{"quote": "없는 질문?", "necessary": True, "reason": "미결정"}]}]
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, self.rubric, self.evidence)

    def test_distinct_final_response_is_a_required_communication(self):
        rubric = {"no-unnecessary-question": "재확인 없이 수정"}
        evidence = {
            "E0001": {"type": "item.completed", "item": {"type": "agent_message", "text": "파일을 확인 중입니다."}},
            "FINAL": "이대로 진행할까요?",
        }
        self.assertEqual(communication_messages(evidence), {
            "E0001": "파일을 확인 중입니다.", "FINAL": "이대로 진행할까요?"
        })
        value = {
            "checks": [{"id": "no-unnecessary-question", "status": "satisfied", "reason": "변경 완료", "evidence": ["E0001"]}],
            "communications": [
                {"message_id": "E0001", "questions": []},
                {"message_id": "FINAL", "questions": [{"quote": "이대로 진행할까요?", "necessary": False, "reason": "기계적 수정"}]},
            ],
        }
        old_false_pass = copy.deepcopy(value)
        old_false_pass["communications"].pop()
        with self.assertRaises(ValueError):
            validate_judgment(old_false_pass, rubric, evidence)
        result = validate_judgment(value, rubric, evidence)
        self.assertEqual(aggregate(result["checks"]), "failed")

    def test_only_duplicate_of_last_agent_message_is_removed(self):
        duplicate = {"E0001": {"type": "item.completed", "item": {"type": "agent_message", "text": "완료했습니다."}},
                     "FINAL": "완료했습니다."}
        self.assertEqual(communication_messages(duplicate), {"E0001": "완료했습니다."})

        repeated_earlier_message = {
            "E0001": {"type": "item.completed", "item": {"type": "agent_message", "text": "처음 결과"}},
            "E0002": {"type": "item.completed", "item": {"type": "agent_message", "text": "마지막 진행 보고"}},
            "FINAL": "처음 결과",
        }
        self.assertEqual(communication_messages(repeated_earlier_message), {
            "E0001": "처음 결과", "E0002": "마지막 진행 보고", "FINAL": "처음 결과"
        })

    def test_question_constraints_override_a_contradictory_pass(self):
        rubric = {"no-unnecessary-question": "재확인 없이 수정"}
        self.valid["checks"][0]["id"] = "no-unnecessary-question"
        result = validate_judgment(self.valid, rubric, self.evidence)
        self.assertEqual(aggregate(result["checks"]), "failed")

    def test_unnecessary_confirmation_fails_even_when_decision_is_asked(self):
        rubric = {"relevant-decision": "필요한 결정 질문"}
        self.valid["checks"][0]["id"] = "relevant-decision"
        self.valid["communications"][0]["questions"][0]["necessary"] = False
        result = validate_judgment(self.valid, rubric, self.evidence)
        self.assertEqual(aggregate(result["checks"]), "failed")

    def test_prompt_self_report_does_not_prove_actual_read(self):
        rubric = {"stage-prompt-used": "시점별 프롬프트 실제 읽기"}
        self.valid["checks"][0]["id"] = "stage-prompt-used"
        with self.assertRaises(ValueError):
            validate_judgment(self.valid, rubric, self.evidence, "# Specification Review")
        self.evidence["E0002"] = {"type": "item.completed", "item": {"type": "command_execution", "exit_code": 0, "aggregated_output": "# Specification Review"}}
        self.valid["checks"][0]["evidence"] = ["E0002"]
        self.assertEqual(validate_judgment(self.valid, rubric, self.evidence, "# Specification Review")["checks"][0]["status"], "satisfied")


if __name__ == "__main__":
    unittest.main()
