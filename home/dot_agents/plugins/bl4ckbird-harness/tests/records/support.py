from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from harness_records.identifiers import reserve
from harness_records.schema import schema, template
from harness_records.store import Store, stamp


class RecordCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = Store(self.root / ".harness")
        self.workspace = self.root / "code"
        self.workspace.mkdir()
        self.work_id = self.identifier("work", "example")
        self.evidence = self.store.files.publish("work/" + self.work_id + "/evidence/source.txt", b"Observed fixture result")

    def identifier(self, kind, name="example"):
        return reserve(self.store.files, kind, name, "UTC", getattr(self, "work_id", None))["id"]

    def record(self, kind, **fields):
        identifier = self.identifier(kind)
        return {**template(schema(kind)), **stamp(kind, identifier, self.work_id), **fields}

    def dispatch(self, **fields):
        value = self.record("dispatch", workspace=str(self.workspace), scope="fixture behavior", write_paths=["app.py"],
                            shared_resources=[], input_refs=[self.evidence], authority="current explicit request",
                            authority_refs=[], model="observed-test-model", effort="medium", report_path=self.evidence["path"])
        value["logical_dispatch_id"] = value["record_id"]
        value.update(fields)
        return value

    def host(self, dispatch, state="ended", background="ended"):
        return self.store.publish(self.record("host", dispatch_ref=dispatch, host_id="host-issued-id",
                                             observed_at=datetime.now(timezone.utc).isoformat(), execution_state=state,
                                             background_state=background, evidence_refs=[self.evidence], limitations=[]))

    def empty_state(self, revision=0):
        return {**template(schema("state")), "work_id": self.work_id, "revision": revision}
