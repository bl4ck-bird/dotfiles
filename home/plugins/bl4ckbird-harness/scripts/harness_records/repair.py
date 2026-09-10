"""손상 원본과 메인의 복구 판단을 보존한 뒤 상태만 교체한다."""

from .errors import RecordError
from .files import decode_json, digest, json_bytes
from .identifiers import require_reservation
from .schema import STATE, schema, validate
from .state import validate_progress
from .store import stamp


def repair_state(store, replacement, record_id, expected_digest, reason, evidence_refs):
    validate(replacement, STATE)
    work_id = replacement["work_id"]
    require_reservation(store.files, "repair", record_id, work_id)
    store.check_refs(replacement, STATE, work_id)
    validate_progress(store, replacement)
    path = "work/" + work_id + "/state.json"
    original = store.files.read(path)
    if digest(original) != expected_digest:
        raise RecordError("State changed before repair; inspect the actual original")
    previous_revision = None
    try:
        previous = decode_json(original)
    except RecordError:
        previous = None
    if isinstance(previous, dict):
        if previous.get("work_id", work_id) != work_id:
            raise RecordError("Repair cannot transfer state between works")
        if previous.get("schema_version", 1) != 1:
            raise RecordError("Unsupported state version requires an explicit migration")
        revision = previous.get("revision")
        if type(revision) is int and revision >= 0:
            previous_revision = revision
    if previous_revision is not None and replacement["revision"] != previous_revision + 1:
        raise RecordError("Repair must preserve observed revision continuity")
    prefix = "work/" + work_id + "/evidence/" + record_id
    new_bytes = json_bytes(replacement)
    record = {**stamp("repair", record_id, work_id),
              "original_state_ref": {"path": prefix + "/state-before.bin", "sha256": digest(original)},
              "replacement_state_ref": {"path": prefix + "/state-after.json", "sha256": digest(new_bytes)},
              "previous_revision": previous_revision, "replacement_revision": replacement["revision"],
              "reason": reason, "evidence_refs": evidence_refs}
    validate(record, schema("repair"))
    for reference in evidence_refs:
        store.read_ref(reference)
    store.files.publish(record["original_state_ref"]["path"], original)
    store.files.publish(record["replacement_state_ref"]["path"], new_bytes)
    repair_ref = store.publish(record)
    state_ref = store.files.publish(path, new_bytes, replace=True, expected_digest=expected_digest)
    return {"repair_ref": repair_ref, "state_ref": state_ref, "automatic_actions": []}
