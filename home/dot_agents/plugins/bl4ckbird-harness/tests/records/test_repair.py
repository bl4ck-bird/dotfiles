from unittest.mock import patch

from support import RecordCase
from harness_records.errors import RecordError
from harness_records.files import digest, json_bytes
from harness_records.recovery import reconcile
from harness_records.repair import repair_state
from harness_records.state import update_state


class RepairTests(RecordCase):
    def damaged_state(self, data=b'{"schema_version":1,"revision":'):
        self.path = "work/" + self.work_id + "/state.json"
        self.store.files.publish(self.path, data)
        return data

    def repair(self, original, replacement=None):
        return repair_state(self.store, replacement or self.empty_state(), self.identifier("repair"),
                            digest(original), "메인이 원 배정과 관측 근거를 대조해 상태를 재구성함", [self.evidence])

    def test_explicit_repair_preserves_original_decision_and_candidate_before_replacement(self):
        original = self.damaged_state()
        self.assertEqual(reconcile(self.store, self.work_id)["status"], "needs_reconciliation")
        result = self.repair(original)
        record = self.store.read_ref(result["repair_ref"], "repair")
        self.assertEqual(self.store.read_ref(record["original_state_ref"]), original)
        self.assertEqual(self.store.read_ref(record["replacement_state_ref"]), self.store.files.read(self.path))
        self.assertIsNone(record["previous_revision"])
        self.assertEqual(result["automatic_actions"], [])
        update_state(self.store, self.empty_state(1), 0)

    def test_repair_cannot_hide_unknown_execution_or_erase_observed_revision(self):
        dispatch = self.store.publish(self.dispatch())
        malformed = {**self.empty_state(8), "unexpected": True}
        original = self.damaged_state(json_bytes(malformed))
        with self.assertRaises(RecordError):
            self.repair(original)
        candidate = self.empty_state(9)
        candidate["active_dispatch_refs"] = [dispatch]
        result = self.repair(original, candidate)
        self.assertEqual(self.store.read_ref(result["repair_ref"], "repair")["previous_revision"], 8)
        self.assertEqual(reconcile(self.store, self.work_id)["dispatches"][dispatch["path"]]["status"], "needs_reconciliation")

    def test_failed_state_replacement_keeps_both_repair_evidence_and_original(self):
        original = self.damaged_state()
        with patch("harness_records.files.os.replace", side_effect=OSError("interrupted final publication")):
            with self.assertRaises(RecordError):
                self.repair(original)
        self.assertEqual(self.store.files.read(self.path), original)
        repairs = [record for _, record in self.store.inventory(self.work_id) if record["kind"] == "repair"]
        self.assertEqual(len(repairs), 1)
        self.assertEqual(self.store.read_ref(repairs[0]["original_state_ref"]), original)
        self.assertEqual(self.store.read_ref(repairs[0]["replacement_state_ref"]), json_bytes(self.empty_state()))

    def test_stale_repair_and_unsupported_version_do_not_rewrite_original(self):
        original = self.damaged_state()
        with self.assertRaises(RecordError):
            repair_state(self.store, self.empty_state(), self.identifier("repair"), "0" * 64, "reason", [self.evidence])
        self.assertEqual(self.store.files.read(self.path), original)
        future = json_bytes({**self.empty_state(), "schema_version": 2})
        self.store.files.publish(self.path, future, replace=True, expected_digest=digest(original))
        with self.assertRaises(RecordError):
            self.repair(future)
        self.assertEqual(self.store.files.read(self.path), future)
