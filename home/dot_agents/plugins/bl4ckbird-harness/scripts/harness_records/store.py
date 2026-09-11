"""기록 종류별 위치·필드·참조를 확인하고 불변 근거를 게시한다."""

from datetime import datetime, timezone

from .errors import RecordError
from .files import Files, decode_json, digest, json_bytes, relative
from .identifiers import require_reservation
from .schema import schema, validate

DIRECTORIES = {"dispatch": "execution/dispatches", "host": "execution/hosts", "result": "execution/results",
               "attempt": "execution/attempts", "disposition": "execution/dispositions", "round": "execution/rounds",
               "repair": "execution/repairs", "approval": "approvals", "review": "reviews"}


def stamp(kind, record_id, work_id):
    return {"schema_version": 1, "kind": kind, "record_id": record_id, "work_id": work_id,
            "created_at": datetime.now(timezone.utc).isoformat()}


def location(record):
    kind, identifier = record["kind"], record["record_id"]
    prefix = "work/" + record["work_id"] + "/"
    if kind == "bundle":
        return prefix + "snapshots/" + identifier + "/manifest.json"
    if kind == "code_target":
        return prefix + "snapshots/code/" + identifier + "/manifest.json"
    if kind == "verification":
        return prefix + "evidence/" + identifier + "/verification.json"
    extension = ".md" if kind in {"approval", "review"} else ".json"
    return prefix + DIRECTORIES[kind] + "/" + identifier + extension


def encode_record(record):
    if record["kind"] not in {"approval", "review"}:
        return json_bytes(record)
    header = {key: value for key, value in record.items() if key != "body"}
    return b"---\n" + json_bytes(header) + b"---\n" + record["body"].encode()


def decode_record(data):
    if data.startswith(b"---\n"):
        pieces = data[4:].split(b"\n---\n", 1)
        if len(pieces) != 2:
            raise RecordError("Invalid JSON frontmatter")
        record = decode_json(pieces[0])
        if "body" in record:
            raise RecordError("Body must not appear in frontmatter")
        record["body"] = pieces[1].decode("utf-8")
        return record
    return decode_json(data)


def is_canonical_record_path(work_id, path):
    parts = list(relative(path))
    if parts[:2] != ["work", work_id]:
        return False
    tail = parts[2:]
    for directory in DIRECTORIES.values():
        if tail[:len(directory.split("/"))] == directory.split("/") and len(tail) == len(directory.split("/")) + 1:
            return tail[-1].endswith(".md" if directory in {"approvals", "reviews"} else ".json")
    return ((len(tail) == 3 and tail[0] == "snapshots" and tail[2] == "manifest.json")
            or (len(tail) == 4 and tail[:2] == ["snapshots", "code"] and tail[3] == "manifest.json")
            or (len(tail) == 3 and tail[0] == "evidence" and tail[2] == "verification.json"))


class Store:
    def __init__(self, root):
        self.files = Files(root)

    def read_record(self, path):
        record = decode_record(self.files.read(path))
        if not isinstance(record, dict) or "kind" not in record:
            raise RecordError("Not a typed record: " + path)
        validate(record, schema(record["kind"]))
        if location(record) != path:
            raise RecordError("Record identity differs from its canonical path")
        return record

    def read_ref(self, reference, expected_kind=None):
        data = self.files.read(reference["path"])
        if digest(data) != reference["sha256"]:
            raise RecordError("Evidence changed: " + reference["path"])
        if not expected_kind:
            return data
        record = self.read_record(reference["path"])
        if record["kind"] != expected_kind:
            raise RecordError("Wrong referenced record kind: " + expected_kind)
        if expected_kind in {"bundle", "code_target"}:
            self.check_refs(record, schema(expected_kind))
        return record

    def check_refs(self, value, definition, work_id=None):
        if value is None:
            return
        if "anyOf" in definition:
            return self.check_refs(value, definition["anyOf"][0], work_id)
        if definition.get("x-record-kind") or definition.get("x-evidence-ref"):
            target = self.read_ref(value, definition.get("x-record-kind"))
            if isinstance(target, dict) and work_id and target["work_id"] != work_id:
                raise RecordError("Typed execution evidence belongs to another work")
            return
        if definition["type"] == "object":
            for key, item in definition["properties"].items():
                self.check_refs(value[key], item, work_id)
        elif definition["type"] == "array":
            for item in value:
                self.check_refs(item, definition["items"], work_id)

    def inventory(self, work_id):
        from .schema import ID
        validate(work_id, ID, "work_id")
        found = []
        for path in self.files.scan("work/" + work_id):
            if not is_canonical_record_path(work_id, path):
                continue
            if path.endswith(".md"):
                kind = next((kind for kind in ("approval", "review") if "/" + DIRECTORIES[kind] + "/" in path), None)
                identifier = path.rsplit("/", 1)[-1][:-3]
                reserved = kind and self.files.exists(".reservations/" + kind + "/" + work_id + "/" + identifier + ".json")
                if not reserved and not self.files.read(path).startswith(b"---\n"):
                    continue
            record = self.read_record(path)
            self.check_refs(record, schema(record["kind"]), work_id)
            found.append((path, record))
        return found

    def publish(self, record):
        definition = schema(record.get("kind"))
        validate(record, definition)
        require_reservation(self.files, record["kind"], record["record_id"], record["work_id"])
        self.check_refs(record, definition, record["work_id"])
        self.check_record(record)
        return self.files.publish(location(record), encode_record(record))

    def check_record(self, record):
        kind = record["kind"]
        if kind in {"bundle", "code_target"}:
            from .capture import safe_name
            prefix = location(record).rsplit("/", 1)[0] + "/"
            items = record["documents"] if kind == "bundle" else record["files"]
            names = [item["source_path"] if kind == "bundle" else item["path"] for item in items]
            if len(set(names)) != len(names):
                raise RecordError("Duplicate captured input")
            for name, item in zip(names, items):
                safe_name(name)
                references = [item["copy_ref"]] if kind == "bundle" else [item["content_ref"], item["index_content_ref"]]
                if any(reference and not reference["path"].startswith(prefix) for reference in references):
                    raise RecordError("Snapshot copies must remain within their target snapshot")
                if kind == "code_target":
                    for hash_key, ref_key in (("sha256", "content_ref"), ("index_sha256", "index_content_ref")):
                        expected = item[ref_key]["sha256"] if item[ref_key] else None
                        if item[hash_key] != expected:
                            raise RecordError("Manifest hash differs from preserved content")
                    if (item["kind"] == "deleted") != (item["content_ref"] is None):
                        raise RecordError("Deletion and preserved content disagree")
        elif kind == "dispatch":
            relative(record["report_path"])
            if not record["report_path"].startswith("work/" + record["work_id"] + "/"):
                raise RecordError("Planned report must be in its work directory")
            from pathlib import Path
            if not Path(record["workspace"]).is_absolute() or not Path(record["workspace"]).is_dir():
                raise RecordError("Dispatch workspace must exist at an absolute path")
            previous = record["previous_dispatch_ref"]
            if record["call_index"] == 0:
                if previous or record["logical_dispatch_id"] != record["record_id"]:
                    raise RecordError("Initial dispatch must own its logical identity")
            else:
                if previous is None:
                    raise RecordError("Recovery dispatch requires its preceding call")
                old = self.read_ref(previous, "dispatch")
                if old["logical_dispatch_id"] != record["logical_dispatch_id"] or old["call_index"] + 1 != record["call_index"]:
                    raise RecordError("Recovery dispatch breaks call continuity")
                identity = ("role", "task_id", "slice_id", "attempt_ref", "scope", "authority", "authority_refs")
                if any(old[field] != record[field] for field in identity):
                    raise RecordError("Recovery dispatch changed logical assignment identity")
            from .recovery import admission
            admission(self, record)
        elif kind in {"attempt", "round"}:
            from .recovery import admission
            admission(self, record)
        elif kind == "host":
            if record["execution_state"] != "unknown" and not record["evidence_refs"]:
                raise RecordError("Execution observations require evidence")
            if record["execution_state"] == "not_started" and record["background_state"] not in {"not_applicable", "ended"}:
                raise RecordError("Not-started observation conflicts with background state")
        elif kind == "result":
            dispatch = self.read_ref(record["dispatch_ref"], "dispatch")
            if dispatch["attempt_ref"] != record["attempt_ref"]:
                raise RecordError("Result must retain its dispatch's attempt")
            if record["host_ref"]:
                host = self.read_ref(record["host_ref"], "host")
                if host["dispatch_ref"] != record["dispatch_ref"]:
                    raise RecordError("Host observation belongs to another dispatch")
                inconsistent = record["applied"] is True or record["outcome"] == "completed"
                if host["execution_state"] == "not_started" and inconsistent:
                    raise RecordError("Not-started execution cannot report applied or completed work")
            if record["applied"] is False:
                if not record["host_ref"] or host["execution_state"] != "not_started":
                    raise RecordError("Releasing an attempt requires evidence that execution did not start")
        elif kind == "approval":
            if (record["action"] == "grant") != (record["previous_approval_ref"] is None):
                raise RecordError("Approval changes must link the original approval")
            for reference in record["review_refs"]:
                review = self.read_ref(reference, "review")
                if review["bundle_ref"] != record["bundle_ref"] or review["verdict"] != "Pass":
                    raise RecordError("Approval requires passing review of the same preserved bundle")
        elif kind == "review":
            if not record["bundle_ref"] and not record["code_target_ref"]:
                raise RecordError("Review requires an identified document or code target")
            if len({item["finding_id"] for item in record["findings"]}) != len(record["findings"]):
                raise RecordError("Duplicate finding identity")
            if record["verdict"] == "Pass" and any(item["severity"] != "Minor" for item in record["findings"]):
                raise RecordError("Unresolved blocking findings cannot accompany Pass")
        elif kind == "disposition":
            review = self.read_ref(record["review_ref"], "review")
            if not any(item["finding_id"] == record["finding_id"] for item in review["findings"]):
                raise RecordError("Disposition refers to an unknown finding")
        elif kind == "verification":
            from .capture import same_code_target
            if record["ended_at"] and datetime.fromisoformat(record["ended_at"].replace("Z", "+00:00")) < datetime.fromisoformat(record["started_at"].replace("Z", "+00:00")):
                raise RecordError("Verification end precedes start")
            match = "unverified"
            if record["after_target_ref"]:
                first = self.read_ref(record["code_target_ref"], "code_target")
                second = self.read_ref(record["after_target_ref"], "code_target")
                match = "same" if same_code_target(first, second) else "changed"
            if record["target_match"] != match:
                raise RecordError("Verification target-match claim conflicts with captured inputs")
            if record["result"] == "passed" and (record["exit_code"] != 0 or record["ended_at"] is None or not record["output_refs"]):
                raise RecordError("Passed verification requires actual ended execution and output")
