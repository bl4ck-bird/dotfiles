from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from support import RecordCase
from harness_records.capture import capture_code, capture_documents
from harness_records.errors import RecordError
from harness_records.recovery import reconcile
from harness_records.store import encode_record, location
from harness_records.state import update_state


class StateAndCliTests(RecordCase):
    def capture(self):
        return capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace, "fixture", ["app.py"], "accepted behavior")

    def verification(self, before, after, result="passed", target_match="same", task_id="behavior"):
        now = datetime.now(timezone.utc).isoformat()
        return self.record("verification", code_target_ref=before, after_target_ref=after, task_id=task_id, acceptance=["accepted result"],
                           command=["python3", "-m", "unittest"], cwd=str(self.workspace), started_at=now, ended_at=now,
                           environment=[{"name": "runtime", "identity": "fixture Python"}], result=result,
                           target_match=target_match, exit_code=0 if result == "passed" else 1, expected="accepted assertion result",
                           expectation_met=True, output_refs=[self.evidence], limitations=[])

    def state_with_task(self, completion):
        state = self.empty_state()
        slice_id = self.identifier("slice")
        state["stage"] = "execute"
        state["slices"] = [{"slice_id": slice_id, "plan_ref": self.evidence, "status": "running", "review_ref": None,
                            "review_target_ref": None, "integration_verification_ref": None, "unresolved_findings": []}]
        state["tasks"] = [{"task_id": "behavior", "slice_id": slice_id, "plan_ref": self.evidence,
                           "completion_kind": "implementation", "status": "completed", "dispatch_refs": [],
                           "completion_refs": [completion]}]
        return state

    def accepted_implementation(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verified = self.store.publish(self.verification(target, self.capture()))
        state = self.state_with_task(verified)
        dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"]))
        host = self.host(dispatch)
        result = self.store.publish(self.record("result", dispatch_ref=dispatch, host_ref=host,
                                                report_ref=self.evidence, outcome="completed", applied=True,
                                                verification_refs=[verified], observed_at=datetime.now(timezone.utc).isoformat()))
        state["tasks"][0].update(dispatch_refs=[dispatch], completion_refs=[verified, result])
        review = self.store.publish(self.record("review", stage="execute", code_target_ref=target, scope="actual behavior",
                                                evidence_refs=[verified], findings=[], verdict="Pass", limitations=[], body="independent reviewed target"))
        integration = self.store.publish(self.verification(self.capture(), self.capture(), task_id=None))
        state["slices"][0].update(status="accepted", review_ref=review, review_target_ref=target,
                                   integration_verification_ref=integration)
        return state, target

    def raw_result(self, dispatch, verification, host=None, applied=True, outcome="completed"):
        record = self.record("result", dispatch_ref=dispatch, host_ref=host, report_ref=self.evidence,
                             outcome=outcome, applied=applied, verification_refs=[verification],
                             observed_at=datetime.now(timezone.utc).isoformat())
        return self.store.files.publish(location(record), encode_record(record))

    def host_at(self, dispatch, execution_state, background_state, observed_at):
        return self.store.publish(self.record("host", dispatch_ref=dispatch, host_id="host-issued-id",
                                             observed_at=observed_at, execution_state=execution_state,
                                             background_state=background_state, evidence_refs=[self.evidence], limitations=[]))

    def test_changed_inputs_preserve_observed_pass_but_cannot_complete_task(self):
        (self.workspace / "app.py").write_text("before")
        before = self.capture()
        (self.workspace / "app.py").write_text("after")
        after = self.capture()
        record = self.verification(before, after)
        with self.assertRaises(RecordError):
            self.store.publish(record)
        record["target_match"] = "changed"
        verification = self.store.publish(record)
        self.assertEqual(self.store.read_record(verification["path"])["result"], "passed")
        with self.assertRaises(RecordError):
            update_state(self.store, self.state_with_task(verification), -1)

    def test_completed_tasks_do_not_accept_slice_without_independent_review(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verified = self.store.publish(self.verification(target, self.capture()))
        state = self.state_with_task(verified)
        dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"]))
        host = self.host(dispatch)
        result = self.store.publish(self.record("result", dispatch_ref=dispatch, host_ref=host,
                                                report_ref=self.evidence, outcome="completed", applied=True,
                                                verification_refs=[verified], observed_at=datetime.now(timezone.utc).isoformat()))
        state["tasks"][0]["dispatch_refs"] = [dispatch]
        state["tasks"][0]["completion_refs"].append(result)
        state["slices"][0]["status"] = "accepted"
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)
        review = self.store.publish(self.record("review", stage="execute", code_target_ref=target, scope="actual behavior",
                                                evidence_refs=[verified], findings=[], verdict="Pass", limitations=[], body="independent reviewed target"))
        state["slices"][0].update(review_ref=review, review_target_ref=target)
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)
        integration_target = self.capture()
        integration = self.store.publish(self.verification(integration_target, self.capture(), task_id=None))
        state["slices"][0]["integration_verification_ref"] = integration
        update_state(self.store, state, -1)

    def test_implementation_slice_rejects_task_scoped_integration_verification(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verified = self.store.publish(self.verification(target, target))
        state = self.state_with_task(verified)
        dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"]))
        host = self.host(dispatch)
        result = self.store.publish(self.record("result", dispatch_ref=dispatch, host_ref=host,
                                                report_ref=self.evidence, outcome="completed", applied=True,
                                                verification_refs=[verified], observed_at=datetime.now(timezone.utc).isoformat()))
        state["tasks"][0].update(dispatch_refs=[dispatch], completion_refs=[verified, result])
        review = self.store.publish(self.record("review", stage="execute", code_target_ref=target, scope="actual behavior",
                                                evidence_refs=[verified], findings=[], verdict="Pass", limitations=[], body="independent reviewed target"))
        invalid_integration = self.store.publish(self.verification(target, target))
        state["slices"][0].update(status="accepted", review_ref=review, review_target_ref=target,
                                   integration_verification_ref=invalid_integration)
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_implementation_slice_rejects_invalid_final_integration_outcomes(self):
        for result, target_match, expectation_met in (("assertion_failed", "same", True), ("passed", "changed", True),
                                                       ("passed", "same", False)):
            with self.subTest(result=result, target_match=target_match, expectation_met=expectation_met):
                state, target = self.accepted_implementation()
                after = target
                if target_match == "changed":
                    (self.workspace / "app.py").write_text("changed behavior")
                    after = self.capture()
                integration = self.verification(target, after, result=result, target_match=target_match, task_id=None)
                integration["expectation_met"] = expectation_met
                state["slices"][0]["integration_verification_ref"] = self.store.publish(integration)
                with self.assertRaises(RecordError):
                    update_state(self.store, state, -1)

    def test_implementation_slice_rejects_bundle_only_pass_review(self):
        state, _ = self.accepted_implementation()
        bundle = capture_documents(self.store, self.work_id, self.identifier("bundle"),
                                   [{"path": self.evidence["path"], "role": "target"}])
        review = self.store.publish(self.record("review", stage="execute", bundle_ref=bundle, code_target_ref=None,
                                                scope="documents only", evidence_refs=[self.evidence], findings=[], verdict="Pass",
                                                limitations=[], body="independent document review"))
        state["slices"][0].update(review_ref=review, review_target_ref=bundle)
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_distinct_task_captures_can_share_final_integration_target(self):
        (self.workspace / "app.py").write_text("first intermediate")
        first_target = self.capture()
        first_verification = self.store.publish(self.verification(first_target, self.capture(), task_id="first"))
        (self.workspace / "app.py").write_text("second intermediate")
        second_target = self.capture()
        second_verification = self.store.publish(self.verification(second_target, self.capture(), task_id="second"))
        state = self.empty_state()
        slice_id = self.identifier("slice")
        state["stage"] = "execute"
        tasks = []
        for task_id, verification in (("first", first_verification), ("second", second_verification)):
            dispatch = self.store.publish(self.dispatch(task_id=task_id, slice_id=slice_id, write_paths=[task_id + ".py"]))
            result = self.store.publish(self.record("result", dispatch_ref=dispatch, host_ref=self.host(dispatch),
                                                    report_ref=self.evidence, outcome="completed", applied=True,
                                                    verification_refs=[verification], observed_at=datetime.now(timezone.utc).isoformat()))
            tasks.append({"task_id": task_id, "slice_id": slice_id, "plan_ref": self.evidence,
                          "completion_kind": "implementation", "status": "completed", "dispatch_refs": [dispatch],
                          "completion_refs": [verification, result]})
        (self.workspace / "app.py").write_text("final integrated behavior")
        final_target = self.capture()
        integration = self.store.publish(self.verification(final_target, self.capture(), task_id=None))
        review = self.store.publish(self.record("review", stage="execute", code_target_ref=self.capture(), scope="final behavior",
                                                evidence_refs=[integration], findings=[], verdict="Pass", limitations=[],
                                                body="independent final code review"))
        state["slices"] = [{"slice_id": slice_id, "plan_ref": self.evidence, "status": "accepted", "review_ref": review,
                            "review_target_ref": self.store.read_record(review["path"])["code_target_ref"],
                            "integration_verification_ref": integration, "unresolved_findings": []}]
        state["tasks"] = tasks
        update_state(self.store, state, -1)

    def test_raw_result_host_contract_cannot_be_hidden_by_latest_ended_host(self):
        cases = (("missing", None, "ended", "ended"), ("other_dispatch", "other", "ended", "ended"),
                 ("unknown_background", "same", "ended", "unknown"), ("not_started", "same", "not_started", "not_applicable"))
        for name, selected, execution_state, background_state in cases:
            with self.subTest(name=name):
                (self.workspace / "app.py").write_text(name)
                target = self.capture()
                verification = self.store.publish(self.verification(target, target))
                state = self.state_with_task(verification)
                dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"],
                                                            write_paths=[name + ".py"]))
                other = self.store.publish(self.dispatch(write_paths=[name + "-other.py"])) if selected == "other" else None
                selected_dispatch = other or dispatch
                bad_host = None if selected is None else self.host_at(selected_dispatch, execution_state, background_state,
                                                                        "2026-01-01T00:00:00+00:00")
                if other:
                    self.store.publish(self.record("result", dispatch_ref=other, host_ref=bad_host,
                                                   report_ref=self.evidence, outcome="failed", applied=None,
                                                   verification_refs=[], observed_at=datetime.now(timezone.utc).isoformat()))
                self.host_at(dispatch, "ended", "ended", "2026-01-01T00:00:01+00:00")
                result = self.raw_result(dispatch, verification, bad_host)
                state["tasks"][0].update(dispatch_refs=[dispatch], completion_refs=[verification, result])
                with self.assertRaises(RecordError):
                    update_state(self.store, state, -1)

    def test_not_started_failure_then_recovery_can_complete_task(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verification = self.store.publish(self.verification(target, target))
        state = self.state_with_task(verification)
        first = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"]))
        first_host = self.host(first, "not_started", "not_applicable")
        self.store.publish(self.record("result", dispatch_ref=first, host_ref=first_host, report_ref=self.evidence,
                                       outcome="failed", applied=False, verification_refs=[], observed_at=datetime.now(timezone.utc).isoformat()))
        second = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"],
                                                  logical_dispatch_id=self.store.read_record(first["path"])["logical_dispatch_id"],
                                                  call_index=1, previous_dispatch_ref=first))
        result = self.store.publish(self.record("result", dispatch_ref=second, host_ref=self.host(second), report_ref=self.evidence,
                                                outcome="completed", applied=True, verification_refs=[verification],
                                                observed_at=datetime.now(timezone.utc).isoformat()))
        state["tasks"][0].update(dispatch_refs=[first, second], completion_refs=[verification, result])
        update_state(self.store, state, -1)

    def test_implementation_slice_rejects_review_of_different_code(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verified = self.store.publish(self.verification(target, self.capture()))
        state = self.state_with_task(verified)
        dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"]))
        host = self.host(dispatch)
        result = self.store.publish(self.record("result", dispatch_ref=dispatch, host_ref=host,
                                                report_ref=self.evidence, outcome="completed", applied=True,
                                                verification_refs=[verified], observed_at=datetime.now(timezone.utc).isoformat()))
        state["tasks"][0]["dispatch_refs"] = [dispatch]
        state["tasks"][0]["completion_refs"].append(result)
        (self.workspace / "app.py").write_text("different behavior")
        different = self.capture()
        review = self.store.publish(self.record("review", stage="execute", code_target_ref=different,
                                                scope="different behavior", evidence_refs=[self.evidence], findings=[],
                                                verdict="Pass", limitations=[], body="reviewed another code target"))
        integration = self.store.publish(self.verification(target, target, task_id=None))
        state["slices"][0].update(status="accepted", review_ref=review, review_target_ref=different,
                                   integration_verification_ref=integration)
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_later_ended_host_cannot_complete_result_linked_to_running_host(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verified = self.store.publish(self.verification(target, target))
        state = self.state_with_task(verified)
        dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"]))
        running = self.host(dispatch, "running", "running")
        result = self.store.publish(self.record("result", dispatch_ref=dispatch, host_ref=running,
                                                report_ref=self.evidence, outcome="completed", applied=True,
                                                verification_refs=[verified], observed_at=datetime.now(timezone.utc).isoformat()))
        self.host(dispatch, "ended", "ended")
        state["tasks"][0].update(dispatch_refs=[dispatch], completion_refs=[verified, result])
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_schema_valid_released_result_cannot_complete_implementation(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verified = self.store.publish(self.verification(target, target))
        state = self.state_with_task(verified)
        dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"]))
        host = self.host(dispatch)
        result = self.record("result", dispatch_ref=dispatch, host_ref=host, report_ref=self.evidence,
                             outcome="completed", applied=False, verification_refs=[verified],
                             observed_at=datetime.now(timezone.utc).isoformat())
        result_ref = self.store.files.publish(location(result), encode_record(result))
        state["tasks"][0].update(dispatch_refs=[dispatch], completion_refs=[verified, result_ref])
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_verification_only_and_documentation_slices_do_not_require_integration(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        verification = self.store.publish(self.verification(target, target))
        review = self.store.publish(self.record("review", stage="execute", code_target_ref=target, scope="checked behavior",
                                                evidence_refs=[verification], findings=[], verdict="Pass", limitations=[], body="independent reviewed target"))
        verification_state = self.state_with_task(verification)
        verification_state["tasks"][0]["completion_kind"] = "verification_only"
        verification_state["slices"][0].update(status="accepted", review_ref=review, review_target_ref=target)
        update_state(self.store, verification_state, -1)

        documentation_state = self.empty_state()
        documentation_state["revision"] = 1
        slice_id = self.identifier("slice", "documentation")
        documentation_state["slices"] = [{"slice_id": slice_id, "plan_ref": self.evidence, "status": "accepted",
                                            "review_ref": review, "review_target_ref": target,
                                            "integration_verification_ref": None, "unresolved_findings": []}]
        documentation_state["tasks"] = [{"task_id": "documentation", "slice_id": slice_id, "plan_ref": self.evidence,
                                           "completion_kind": "documentation", "status": "completed", "dispatch_refs": [],
                                           "completion_refs": [self.evidence]}]
        update_state(self.store, documentation_state, 0)

    def test_expected_reproduction_failure_is_not_implementation_completion(self):
        (self.workspace / "app.py").write_text("bug reproduction")
        target = self.capture()
        verified = self.store.publish(self.verification(target, target, result="assertion_failed"))
        state = self.state_with_task(verified)
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)
        state["tasks"][0]["completion_kind"] = "verification_only"
        update_state(self.store, state, -1)

    def test_incomplete_assertion_failures_are_preserved_but_cannot_complete_task(self):
        (self.workspace / "app.py").write_text("bug reproduction")
        target = self.capture()
        cases = {
            "missing-ended-at": {"ended_at": None},
            "missing-exit-code": {"exit_code": None},
            "zero-exit-code": {"exit_code": 0},
            "missing-output": {"output_refs": []},
        }
        for name, changes in cases.items():
            with self.subTest(name=name):
                incomplete = self.verification(target, target, result="assertion_failed")
                incomplete.update(changes)
                try:
                    reference = self.store.publish(incomplete)
                except RecordError as error:
                    self.fail("Incomplete assertion observation was not preserved: " + str(error))
                state = self.state_with_task(reference)
                state["tasks"][0]["completion_kind"] = "verification_only"
                with self.assertRaises(RecordError):
                    update_state(self.store, state, -1)

    def test_raw_unfinished_assertion_failure_cannot_complete_verification_task(self):
        (self.workspace / "app.py").write_text("bug reproduction")
        target = self.capture()
        unfinished = self.verification(target, target, result="assertion_failed")
        unfinished.update(ended_at=None, exit_code=None, output_refs=[])
        reference = self.store.files.publish(location(unfinished), encode_record(unfinished))
        state = self.state_with_task(reference)
        state["tasks"][0]["completion_kind"] = "verification_only"
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_attempt_completion_requires_applied_true_but_no_attempt_noop_may_complete(self):
        (self.workspace / "app.py").write_text("accepted behavior")
        target = self.capture()
        issue_id = self.identifier("diagnosis", "applied-unknown")
        attempt = self.store.publish(self.record("attempt", issue_id=issue_id, hypothesis="apply correction",
                                                 code_target_ref=target, previous_attempt_ref=None,
                                                 new_evidence_refs=[], different_approach=None))
        verification_record = self.verification(target, target)
        verification_record["attempt_ref"] = attempt
        verified = self.store.publish(verification_record)
        state = self.state_with_task(verified)
        dispatch = self.store.publish(self.dispatch(task_id="behavior", slice_id=state["slices"][0]["slice_id"],
                                                    attempt_ref=attempt))
        result = self.store.publish(self.record("result", dispatch_ref=dispatch, attempt_ref=attempt,
                                                host_ref=self.host(dispatch), report_ref=self.evidence,
                                                outcome="completed", applied=None, verification_refs=[verified],
                                                observed_at=datetime.now(timezone.utc).isoformat()))
        state["tasks"][0].update(dispatch_refs=[dispatch], completion_refs=[verified, result])
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)
        self.assertEqual(reconcile(self.store, self.work_id)["issues"][issue_id]["attempts"][0]["status"], "reserved")

        applied_issue = self.identifier("diagnosis", "applied")
        applied_attempt = self.store.publish(self.record("attempt", issue_id=applied_issue, hypothesis="apply correction",
                                                         code_target_ref=target, previous_attempt_ref=None,
                                                         new_evidence_refs=[], different_approach=None))
        applied_verification_record = self.verification(target, target, task_id="applied")
        applied_verification_record["attempt_ref"] = applied_attempt
        applied_verified = self.store.publish(applied_verification_record)
        applied_state = self.state_with_task(applied_verified)
        applied_state["tasks"][0]["task_id"] = "applied"
        applied_dispatch = self.store.publish(self.dispatch(task_id="applied",
                                                            slice_id=applied_state["slices"][0]["slice_id"],
                                                            attempt_ref=applied_attempt, write_paths=["applied.py"]))
        applied_result = self.store.publish(self.record("result", dispatch_ref=applied_dispatch,
                                                        attempt_ref=applied_attempt, host_ref=self.host(applied_dispatch),
                                                        report_ref=self.evidence, outcome="completed", applied=True,
                                                        verification_refs=[applied_verified],
                                                        observed_at=datetime.now(timezone.utc).isoformat()))
        applied_state["tasks"][0].update(dispatch_refs=[applied_dispatch],
                                         completion_refs=[applied_verified, applied_result])
        update_state(self.store, applied_state, -1)
        accounting = reconcile(self.store, self.work_id)["issues"][applied_issue]
        self.assertEqual((accounting["consumed"], accounting["reserved"]), (1, 0))

        noop_verified = self.store.publish(self.verification(target, target, task_id="noop"))
        noop_state = self.state_with_task(noop_verified)
        noop_state["revision"] = 1
        noop_state["tasks"][0]["task_id"] = "noop"
        noop_dispatch = self.store.publish(self.dispatch(task_id="noop", slice_id=noop_state["slices"][0]["slice_id"],
                                                         write_paths=["noop.py"]))
        noop_result = self.store.publish(self.record("result", dispatch_ref=noop_dispatch, host_ref=self.host(noop_dispatch),
                                                     report_ref=self.evidence, outcome="completed", applied=None,
                                                     verification_refs=[noop_verified],
                                                     observed_at=datetime.now(timezone.utc).isoformat()))
        noop_state["tasks"][0].update(dispatch_refs=[noop_dispatch], completion_refs=[noop_verified, noop_result])
        update_state(self.store, noop_state, 0)

    def test_generic_report_and_another_tasks_verification_cannot_complete_implementation(self):
        with self.assertRaises(RecordError):
            update_state(self.store, self.state_with_task(self.evidence), -1)
        (self.workspace / "app.py").write_text("accepted")
        target = self.capture()
        record = self.verification(target, target)
        record["task_id"] = "another-task"
        verification = self.store.publish(record)
        state = self.state_with_task(verification)
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)
        state["tasks"][0]["completion_kind"] = "verification_only"
        with self.assertRaises(RecordError):
            update_state(self.store, state, -1)

    def test_passing_verification_alone_cannot_complete_implementation(self):
        (self.workspace / "app.py").write_text("accepted")
        target = self.capture()
        verified = self.store.publish(self.verification(target, target))
        with self.assertRaises(RecordError):
            update_state(self.store, self.state_with_task(verified), -1)

    def test_interruption_while_writing_temporary_state_keeps_old_state(self):
        first = update_state(self.store, self.empty_state(), -1)
        old = self.store.files.read(first["path"])
        with patch("harness_records.files.os.fsync", side_effect=OSError("interrupted temporary write")):
            with self.assertRaises(RecordError):
                update_state(self.store, self.empty_state(1), 0)
        self.assertEqual(self.store.files.read(first["path"]), old)
        temporary = self.store.files.root / "work" / self.work_id / ".pending-interrupted"
        temporary.write_text("incomplete")
        self.assertNotIn(str(temporary.relative_to(self.store.files.root)), self.store.files.scan("work/" + self.work_id))

    def test_cli_schema_template_and_rejected_input_do_not_invoke_host(self):
        entry = Path(__file__).resolve().parents[2] / "scripts" / "records.py"
        result = subprocess.run([sys.executable, "-B", str(entry), "schema", "dispatch"], capture_output=True, check=True)
        self.assertFalse(json.loads(result.stdout)["additionalProperties"])
        result = subprocess.run([sys.executable, "-B", str(entry), "template", "state"], capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)["slices"], [])
        bad = self.root / "bad.json"
        bad.write_text('{"kind":"dispatch","schema_version":true}')
        result = subprocess.run([sys.executable, "-B", str(entry), "--root", str(self.store.files.root), "publish", "--input", str(bad)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["status"], "rejected")
