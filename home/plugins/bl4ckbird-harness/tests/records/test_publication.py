from datetime import datetime, timezone
import os
from pathlib import Path
from unittest.mock import patch

from support import RecordCase
from harness_records.errors import RecordError
from harness_records.files import decode_json, json_bytes
from harness_records.identifiers import reserve
from harness_records.schema import schema, validate
from harness_records.state import update_state


class PublicationTests(RecordCase):
    def test_identifiers_preserve_abandoned_reservations_and_scopes(self):
        moment = datetime(2026, 9, 10, 23, 30, tzinfo=timezone.utc)
        first = reserve(self.store.files, "dispatch", "first", "Asia/Seoul", self.work_id, moment)
        second = reserve(self.store.files, "dispatch", "second", "Asia/Seoul", self.work_id, moment)
        independent = reserve(self.store.files, "review", "first", "Asia/Seoul", self.work_id, moment)
        self.assertTrue(first["id"].startswith("2026-09-11-001-"))
        self.assertTrue(second["id"].startswith("2026-09-11-002-"))
        self.assertTrue(independent["id"].startswith("2026-09-11-001-"))
        self.assertEqual(decode_json(self.store.files.read(first["reservation_ref"]["path"]))["id"], first["id"])

    def test_pre_tool_identifiers_and_plain_reviews_remain_intact(self):
        moment = datetime(2026, 9, 10, tzinfo=timezone.utc)
        (self.store.files.root / "work" / "2026-09-10-019-existing").mkdir()
        allocated = reserve(self.store.files, "work", "next", "UTC", now=moment)
        self.assertTrue(allocated["id"].startswith("2026-09-10-020-"))
        path = "work/" + self.work_id + "/reviews/2026-09-10-007-historical.md"
        old = self.store.files.publish(path, "# Historical Review\n\n과거 판단 원문\n".encode())
        allocated = reserve(self.store.files, "review", "next", "UTC", self.work_id, moment)
        self.assertTrue(allocated["id"].startswith("2026-09-10-008-"))
        self.assertEqual(self.store.inventory(self.work_id), [])
        self.assertEqual(self.store.files.reference(path), old)

    def test_reserved_review_corruption_is_not_treated_as_historical_markdown(self):
        identifier = self.identifier("review")
        path = "work/" + self.work_id + "/reviews/" + identifier + ".md"
        self.store.files.publish(path, b"damaged typed record")
        with self.assertRaises(RecordError):
            self.store.inventory(self.work_id)

    def test_nested_evidence_project_records_are_inert_to_current_inventory(self):
        dispatch = self.store.publish(self.dispatch())
        before = self.store.inventory(self.work_id)
        nested = ("work/" + self.work_id + "/evidence/fixture/project/.harness/work/foreign/"
                  "execution/dispatches/" + dispatch["path"].rsplit("/", 1)[-1])
        self.store.files.publish(nested, self.store.files.read(dispatch["path"]))
        after = self.store.inventory(self.work_id)
        self.assertEqual(after, before)

    def test_malformed_canonical_execution_record_blocks_inventory(self):
        identifier = self.identifier("dispatch")
        path = "work/" + self.work_id + "/execution/dispatches/" + identifier + ".json"
        self.store.files.publish(path, b'{"schema_version":')
        with self.assertRaises(RecordError):
            self.store.inventory(self.work_id)

    def test_immutable_publication_and_tampered_reference_rejection(self):
        record = self.dispatch()
        reference = self.store.publish(record)
        before = self.store.files.read(reference["path"])
        record["scope"] = "another scope"
        with self.assertRaises(RecordError):
            self.store.publish(record)
        self.assertEqual(self.store.files.read(reference["path"]), before)
        (self.store.files.root / self.evidence["path"]).write_bytes(b"changed observation")
        with self.assertRaises(RecordError):
            self.store.publish(self.dispatch(write_paths=["separate.py"]))

    def test_path_traversal_symlinks_and_nonregular_files_are_refused(self):
        for name in ("../escape", "/tmp/escape", "work/../escape", "work//escape"):
            with self.subTest(name=name), self.assertRaises(RecordError):
                self.store.files.publish(name, b"bad")
        (self.store.files.root / "escape").symlink_to(self.workspace, target_is_directory=True)
        with self.assertRaises(RecordError):
            self.store.files.publish("escape/unexpected", b"bad")
        os.mkfifo(self.store.files.root / "fifo")
        with self.assertRaises(RecordError):
            self.store.files.read("fifo")
        self.assertFalse((self.workspace / "unexpected").exists())

    def test_exact_schema_rejects_bool_revision_unknown_fields_and_bad_time(self):
        state = self.empty_state()
        state["revision"] = True
        with self.assertRaises(RecordError):
            validate(state, schema("state"))
        state = self.empty_state()
        state["counter"] = 0
        with self.assertRaises(RecordError):
            validate(state, schema("state"))
        record = self.dispatch(created_at="2026-09-10T12:00:00")
        with self.assertRaises(RecordError):
            self.store.publish(record)

    def test_stale_revision_and_interrupted_replace_preserve_previous_state(self):
        first = update_state(self.store, self.empty_state(), -1)
        old = self.store.files.read(first["path"])
        with self.assertRaises(RecordError):
            update_state(self.store, self.empty_state(1), -1)
        with patch("harness_records.files.os.replace", side_effect=OSError("simulated interrupted publication")):
            with self.assertRaises(RecordError):
                update_state(self.store, self.empty_state(1), 0)
        self.assertEqual(self.store.files.read(first["path"]), old)
        self.assertEqual(update_state(self.store, self.empty_state(1), 0)["path"], first["path"])

    def test_corrupt_state_is_preserved_and_blocks_new_dispatch(self):
        path = "work/" + self.work_id + "/state.json"
        self.store.files.publish(path, b'{"schema_version":')
        with self.assertRaises(RecordError):
            self.store.publish(self.dispatch())
        self.assertEqual(self.store.files.read(path), b'{"schema_version":')

    def test_planned_report_may_be_absent_but_evidence_must_exist(self):
        record = self.dispatch(report_path="work/" + self.work_id + "/evidence/later.txt")
        self.store.publish(record)
        bad = self.dispatch(write_paths=["other.py"])
        bad["input_refs"] = [{"path": "missing.txt", "sha256": "0" * 64}]
        with self.assertRaises(RecordError):
            self.store.publish(bad)

    def test_not_started_host_cannot_publish_completed_applied_result(self):
        cases = ((True, "failed"), (None, "completed"))
        for applied, outcome in cases:
            with self.subTest(applied=applied, outcome=outcome):
                dispatch = self.store.publish(self.dispatch(write_paths=["app-" + outcome + ".py"]))
                host = self.host(dispatch, "not_started", "not_applicable")
                result = self.record("result", dispatch_ref=dispatch, host_ref=host, report_ref=self.evidence,
                                     outcome=outcome, applied=applied, verification_refs=[],
                                     observed_at=datetime.now(timezone.utc).isoformat())
                with self.assertRaises(RecordError):
                    self.store.publish(result)
