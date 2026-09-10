"""원기록에서 실행 불확실성과 사용한 시도를 보고한다. 외부 작업은 실행하지 않는다."""

from datetime import datetime
from pathlib import Path

from .errors import RecordError
from .files import decode_json, relative
from .schema import STATE, validate


def observed(record):
    return datetime.fromisoformat(record.get("observed_at", record["created_at"]).replace("Z", "+00:00"))


def summarize(records):
    dispatches = {path: record for path, record in records if record["kind"] == "dispatch"}
    results = [(path, record) for path, record in records if record["kind"] == "result"]
    hosts = [(path, record) for path, record in records if record["kind"] == "host"]
    executions = {}
    for path, dispatch in dispatches.items():
        observations = [(p, r) for p, r in hosts if r["dispatch_ref"]["path"] == path]
        reports = [(p, r) for p, r in results if r["dispatch_ref"]["path"] == path]
        latest = max((observed(r) for _, r in observations), default=None)
        recent = [(p, r) for p, r in observations if observed(r) == latest]
        states = {(r["execution_state"], r["background_state"]) for _, r in recent}
        state, background = next(iter(states)) if len(states) == 1 else ("unknown", "unknown")
        confirmed = state in {"ended", "not_started"} and background in {"ended", "not_applicable"}
        status = "needs_reconciliation"
        if confirmed:
            status = "not_started" if state == "not_started" else "ended_with_result" if reports else "ended_missing_result"
        elif state == "running" or background == "running":
            status = "running"
        executions[path] = {"dispatch_id": dispatch["record_id"], "status": status,
                            "termination_confirmed": confirmed, "host_refs": [p for p, _ in recent],
                            "result_refs": [p for p, _ in reports]}
    attempts = {}
    for path, attempt in records:
        if attempt["kind"] != "attempt":
            continue
        related = [p for p, d in dispatches.items() if d["attempt_ref"] and d["attempt_ref"]["path"] == path]
        reports = [r for _, r in results if r["attempt_ref"] and r["attempt_ref"]["path"] == path]
        applied = any(r["applied"] is True for r in reports)
        never_started = bool(related) and all(executions[p]["status"] == "not_started" for p in related) and not applied
        outcome = "not_started" if never_started else "reserved"
        if applied:
            latest = max(reports, key=observed)
            outcome = latest["outcome"]
        item = attempts.setdefault(attempt["issue_id"], {"consumed": 0, "reserved": 0, "attempts": []})
        if outcome == "reserved":
            item["reserved"] += 1
        elif outcome != "not_started":
            item["consumed"] += 1
        item["attempts"].append({"path": path, "status": outcome})
    rounds, calls = {}, {}
    for path, record in records:
        if record["kind"] == "round":
            rounds.setdefault(record["slice_id"], []).append(path)
        elif record["kind"] == "dispatch":
            calls.setdefault(record["logical_dispatch_id"], []).append(path)
    return {"dispatches": executions, "issues": attempts,
            "slice_rounds": {key: {"used": len(value), "refs": value} for key, value in rounds.items()},
            "calls": {key: {"calls": len(value), "recoveries": max(0, len(value) - 1), "refs": value} for key, value in calls.items()}}


def reconcile(store, work_id):
    errors = []
    try:
        records = store.inventory(work_id)
    except RecordError as error:
        return {"status": "needs_reconciliation", "errors": [str(error)], "automatic_actions": [],
                "limitations": ["Damaged evidence prevents reliable counter reconstruction"]}
    result = summarize(records)
    path = "work/" + work_id + "/state.json"
    state = None
    if store.files.exists(path):
        try:
            state = decode_json(store.files.read(path))
            validate(state, STATE)
            store.check_refs(state, STATE, work_id)
        except RecordError as error:
            errors.append("Preserve damaged state: " + str(error))
    active = [path for path, item in result["dispatches"].items() if item["status"] in {"running", "needs_reconciliation", "ended_missing_result"}]
    if state is not None and not errors:
        missing = set(active) - {item["path"] for item in state["active_dispatch_refs"]}
        if missing:
            errors.append("State is missing unresolved dispatches: " + repr(sorted(missing)))
    result.update({"status": "needs_reconciliation" if active or errors else "records_consistent",
                  "errors": errors, "state_revision": state.get("revision") if isinstance(state, dict) else None,
                  "automatic_actions": [], "limitations": ["Host and background status are supplied observations, not a live host query",
                                                           "Result availability does not establish execution termination",
                                                           "No code, agent call, deployment or state update is replayed"]})
    return result


def overlaps(first, second):
    shared = set(first["shared_resources"]) & set(second["shared_resources"])
    if shared:
        return True
    first_root, second_root = Path(first["workspace"]).resolve(), Path(second["workspace"]).resolve()
    for left in first["write_paths"]:
        a = first_root.joinpath(*relative(left))
        for right in second["write_paths"]:
            b = second_root.joinpath(*relative(right))
            if a == b or a in b.parents or b in a.parents:
                return True
    return False


def admission(store, candidate):
    state_path = "work/" + candidate["work_id"] + "/state.json"
    if store.files.exists(state_path):
        current = decode_json(store.files.read(state_path))
        validate(current, STATE)
        store.check_refs(current, STATE, candidate["work_id"])
    records = store.inventory(candidate["work_id"])
    summary = summarize(records)
    if candidate["kind"] == "dispatch":
        for path in candidate["write_paths"]:
            relative(path)
        if candidate["role"] == "reviewer" and candidate["write_paths"]:
            raise RecordError("Reviewer dispatch must not authorize code writes")
        for path, old in records:
            if old["kind"] != "dispatch":
                continue
            same_call = old["logical_dispatch_id"] == candidate["logical_dispatch_id"]
            if same_call and old["call_index"] == candidate["call_index"]:
                raise RecordError("Call index has already been consumed")
            if not summary["dispatches"][path]["termination_confirmed"] and (same_call or overlaps(old, candidate)):
                raise RecordError("Prior execution is uncertain or running; reconcile before conflicting dispatch")
    elif candidate["kind"] == "attempt":
        issue = summary["issues"].get(candidate["issue_id"], {"consumed": 0, "reserved": 0})
        count = issue["consumed"] + issue["reserved"]
        if count >= 3:
            raise RecordError("Issue correction allowance exhausted")
        if count == 2 and (not candidate["new_evidence_refs"] or not candidate["different_approach"] or not candidate["previous_attempt_ref"]):
            raise RecordError("Third attempt requires new evidence and a different authorized approach")
        if candidate["previous_attempt_ref"]:
            previous = store.read_ref(candidate["previous_attempt_ref"], "attempt")
            if previous["issue_id"] != candidate["issue_id"]:
                raise RecordError("Attempt continuation changed issue identity")
    elif candidate["kind"] == "round":
        if summary["slice_rounds"].get(candidate["slice_id"], {}).get("used", 0) >= 5:
            raise RecordError("Slice correction round allowance exhausted")
        for reference in candidate["attempt_refs"]:
            if store.read_ref(reference, "attempt")["issue_id"] not in candidate["issue_ids"]:
                raise RecordError("Round attempt does not belong to its listed issues")
