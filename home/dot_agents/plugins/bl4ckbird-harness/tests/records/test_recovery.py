from datetime import datetime, timezone

from support import RecordCase
from harness_records.capture import capture_code
from harness_records.errors import RecordError
from harness_records.files import json_bytes
from harness_records.recovery import reconcile
from harness_records.state import update_current, update_state


class RecoveryTests(RecordCase):
    def result(self, dispatch, host=None, applied=None, outcome="completed"):
        record = self.store.read_record(dispatch["path"])
        return self.store.publish(self.record("result", dispatch_ref=dispatch, attempt_ref=record["attempt_ref"], host_ref=host,
                                             report_ref=self.evidence, outcome=outcome, applied=applied,
                                             verification_refs=[], observed_at=datetime.now(timezone.utc).isoformat()))

    def test_dispatch_without_host_remains_uncertain_even_with_result(self):
        dispatch = self.store.publish(self.dispatch())
        self.result(dispatch)
        first = reconcile(self.store, self.work_id)
        self.assertFalse(first["dispatches"][dispatch["path"]]["termination_confirmed"])
        self.assertEqual(first["dispatches"][dispatch["path"]]["status"], "needs_reconciliation")
        self.assertEqual(first["automatic_actions"], [])
        with self.assertRaises(RecordError):
            self.store.publish(self.dispatch())
        independent = self.store.publish(self.dispatch(write_paths=["independent.py"]))
        self.assertIn(independent["path"], reconcile(self.store, self.work_id)["dispatches"])

    def test_ended_turn_with_unknown_background_is_not_terminated(self):
        dispatch = self.store.publish(self.dispatch())
        self.host(dispatch, "ended", "unknown")
        self.result(dispatch)
        self.assertFalse(reconcile(self.store, self.work_id)["dispatches"][dispatch["path"]]["termination_confirmed"])

    def test_results_before_state_and_current_failure_do_not_replay_or_recount(self):
        dispatch = self.store.publish(self.dispatch())
        self.host(dispatch)
        result = self.result(dispatch)
        before = reconcile(self.store, self.work_id)
        self.assertEqual(before["dispatches"][dispatch["path"]]["status"], "ended_with_result")
        update_state(self.store, self.empty_state(), -1)
        update_current(self.store, "Existing navigation", None)
        with self.assertRaises(RecordError):
            update_current(self.store, "New navigation", "0" * 64)
        after = reconcile(self.store, self.work_id)
        self.assertEqual(before["calls"], after["calls"])
        self.assertEqual(after["automatic_actions"], [])
        self.assertEqual(self.store.files.read("CURRENT.md"), b"Existing navigation")

    def test_missing_result_and_unresolved_dispatch_cannot_be_erased_from_state(self):
        dispatch = self.store.publish(self.dispatch())
        self.host(dispatch)
        self.assertEqual(reconcile(self.store, self.work_id)["dispatches"][dispatch["path"]]["status"], "ended_missing_result")
        with self.assertRaises(RecordError):
            update_state(self.store, self.empty_state(), -1)
        state = self.empty_state()
        state["active_dispatch_refs"] = [dispatch]
        update_state(self.store, state, -1)

    def test_finish_rejects_even_ended_dispatch_left_in_active_list(self):
        dispatch = self.store.publish(self.dispatch())
        self.result(dispatch, host=self.host(dispatch), outcome="failed")
        state = self.empty_state()
        state["active_dispatch_refs"] = [dispatch]
        state["finish_ref"] = self.evidence
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_unsupported_execution_record_version_requires_reconciliation(self):
        dispatch = self.store.publish(self.dispatch())
        path = self.store.files.root / dispatch["path"]
        record = self.store.read_record(dispatch["path"])
        record["schema_version"] = 2
        original = json_bytes(record)
        path.write_bytes(original)

        report = reconcile(self.store, self.work_id)
        self.assertEqual(report["status"], "needs_reconciliation")
        self.assertTrue(report["errors"])
        self.assertEqual(path.read_bytes(), original)

    def test_call_recovery_preserves_logical_identity_and_total_allowance(self):
        value = self.dispatch()
        first = self.store.publish(value)
        previous = first
        for index in (1, 2):
            host = self.host(previous, "not_started", "not_applicable")
            self.result(previous, host=host, applied=False, outcome="failed")
            follow = self.dispatch(logical_dispatch_id=value["record_id"], call_index=index, previous_dispatch_ref=previous)
            previous = self.store.publish(follow)
        counts = reconcile(self.store, self.work_id)["calls"][value["record_id"]]
        self.assertEqual(counts["calls"], 3)
        self.assertEqual(counts["recoveries"], 2)
        with self.assertRaises(RecordError):
            self.store.publish(self.dispatch(logical_dispatch_id=value["record_id"], call_index=3, previous_dispatch_ref=previous))

    def test_recovery_rejects_changed_assignment_identity(self):
        (self.workspace / "app.py").write_text("baseline")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace,
                              "fixture", ["app.py"], "scope")
        issue = self.identifier("diagnosis", "same-issue")
        attempt = self.store.publish(self.record("attempt", issue_id=issue, hypothesis="first hypothesis",
                                                 code_target_ref=target, previous_attempt_ref=None,
                                                 new_evidence_refs=[], different_approach=None))
        other_issue = self.identifier("diagnosis", "other-issue")
        other_attempt = self.store.publish(self.record("attempt", issue_id=other_issue, hypothesis="other hypothesis",
                                                       code_target_ref=target, previous_attempt_ref=None,
                                                       new_evidence_refs=[], different_approach=None))
        other_authority = self.store.files.publish("work/" + self.work_id + "/evidence/authority.txt", b"dummy authority")
        changes = {
            "role": "reviewer",
            "task_id": "other-task",
            "slice_id": self.identifier("slice", "other"),
            "attempt_ref": other_attempt,
            "scope": "other scope",
            "authority": "other authority",
            "authority_refs": [other_authority],
        }
        for field, changed in changes.items():
            with self.subTest(field=field):
                name = field.replace("_", "-")
                first = self.store.publish(self.dispatch(task_id="task-" + name, slice_id=self.identifier("slice", name),
                                                         attempt_ref=attempt, scope="same scope",
                                                         authority="same authority", authority_refs=[]))
                host = self.host(first, "not_started", "not_applicable")
                self.result(first, host=host, applied=False, outcome="failed")
                previous = self.store.read_record(first["path"])
                follow = self.dispatch(logical_dispatch_id=previous["logical_dispatch_id"], call_index=1,
                                       previous_dispatch_ref=first, task_id=previous["task_id"],
                                       slice_id=previous["slice_id"], attempt_ref=attempt, scope=previous["scope"],
                                       authority=previous["authority"], authority_refs=previous["authority_refs"])
                follow[field] = changed
                if field == "role":
                    follow["write_paths"] = []
                try:
                    published = self.store.publish(follow)
                except RecordError as error:
                    self.assertEqual(str(error), "Recovery dispatch changed logical assignment identity")
                    continue
                follow_host = self.host(published, "not_started", "not_applicable")
                self.result(published, host=follow_host, applied=False, outcome="failed")
                self.fail("Recovery accepted changed assignment field: " + field)

    def test_recovery_allows_execution_environment_changes(self):
        first = self.store.publish(self.dispatch(task_id="same-task", slice_id=self.identifier("slice")))
        host = self.host(first, "not_started", "not_applicable")
        self.result(first, host=host, applied=False, outcome="failed")
        other_workspace = self.root / "moved-workspace"
        other_workspace.mkdir()
        previous = self.store.read_record(first["path"])
        follow = self.dispatch(logical_dispatch_id=previous["logical_dispatch_id"], call_index=1,
                               previous_dispatch_ref=first, task_id=previous["task_id"], slice_id=previous["slice_id"],
                               workspace=str(other_workspace), model="replacement-model", effort="high",
                               report_path="work/" + self.work_id + "/evidence/recovery.md")
        self.store.publish(follow)

    def test_attempt_reservation_survives_missing_host_and_third_needs_new_evidence(self):
        (self.workspace / "app.py").write_text("baseline")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace, "fixture", ["app.py"], "scope")
        issue = self.identifier("diagnosis", "same-issue")
        first = self.store.publish(self.record("attempt", issue_id=issue, hypothesis="first hypothesis", code_target_ref=target,
                                               new_evidence_refs=[]))
        second = self.store.publish(self.record("attempt", issue_id=issue, hypothesis="second hypothesis", code_target_ref=target,
                                                previous_attempt_ref=first, new_evidence_refs=[]))
        third = self.record("attempt", issue_id=issue, hypothesis="third hypothesis", code_target_ref=target,
                            previous_attempt_ref=second, new_evidence_refs=[])
        with self.assertRaises(RecordError):
            self.store.publish(third)
        third.update(new_evidence_refs=[self.evidence], different_approach="A different in-scope approach after diagnosis")
        self.store.publish(third)
        report = reconcile(self.store, self.work_id)
        self.assertEqual(report["issues"][issue]["reserved"], 3)
        with self.assertRaises(RecordError):
            self.store.publish(self.record("attempt", issue_id=issue, hypothesis="renamed fourth", code_target_ref=target,
                                           previous_attempt_ref=second, new_evidence_refs=[self.evidence], different_approach="renamed"))
        self.assertEqual(reconcile(self.store, self.work_id)["issues"], report["issues"])

    def test_slice_round_limit_is_derived_from_unique_records(self):
        slice_id = self.identifier("slice")
        issue_id = self.identifier("diagnosis")
        for _ in range(5):
            self.store.publish(self.record("round", slice_id=slice_id, issue_ids=[issue_id], attempt_refs=[], disposition_refs=[]))
        with self.assertRaises(RecordError):
            self.store.publish(self.record("round", slice_id=slice_id, issue_ids=[issue_id], attempt_refs=[], disposition_refs=[]))
        self.assertEqual(reconcile(self.store, self.work_id)["slice_rounds"][slice_id]["used"], 5)

    def test_false_positive_disposition_does_not_consume_a_correction_attempt(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace, "fixture", ["app.py"], "scope")
        issue_id = self.identifier("diagnosis")
        finding = {"finding_id": "observed-branch", "severity": "Important", "location": "app.py:1",
                   "requirement_or_risk": "accepted branch behavior", "condition": "reported missing branch",
                   "evidence_refs": [self.evidence], "impact": "potential incorrect response", "resolution": "investigate"}
        review = self.store.publish(self.record("review", stage="execute", code_target_ref=target, scope="branch behavior",
                                                evidence_refs=[self.evidence], findings=[finding], verdict="Changes required",
                                                limitations=[], body="Reviewer's original observation"))
        before = self.store.files.read(review["path"])
        disposition = self.record("disposition", issue_id=issue_id, review_ref=review, finding_id="missing-finding",
                                  decision="false_positive", reason="Actual branch is covered by preserved evidence",
                                  evidence_refs=[self.evidence], attempt_refs=[])
        with self.assertRaises(RecordError):
            self.store.publish(disposition)
        disposition["finding_id"] = finding["finding_id"]
        self.store.publish(disposition)
        self.assertEqual(reconcile(self.store, self.work_id)["issues"], {})
        self.assertEqual(self.store.files.read(review["path"]), before)
