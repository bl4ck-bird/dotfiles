"""메인이 판단한 단일 상태를 낡은 입력 검사 후 게시한다."""

from .errors import RecordError
from .capture import same_code_target
from .files import decode_json, digest, json_bytes
from .recovery import summarize
from .schema import STATE, validate


def is_final_integration(verification):
    return (verification["task_id"] is None and verification["result"] == "passed"
            and verification["target_match"] == "same" and verification["expectation_met"] is True)


def completed_result_has_ended_host(store, result):
    if result["applied"] is False or not result["host_ref"]:
        return False
    dispatch = store.read_ref(result["dispatch_ref"], "dispatch")
    if dispatch["attempt_ref"] and result["applied"] is not True:
        return False
    host = store.read_ref(result["host_ref"], "host")
    return (host["dispatch_ref"] == result["dispatch_ref"] and host["execution_state"] == "ended"
            and host["background_state"] in {"ended", "not_applicable"})


def update_state(store, state, expected_revision):
    validate(state, STATE)
    work_id = state["work_id"]
    store.check_refs(state, STATE, work_id)
    path = "work/" + work_id + "/state.json"
    exists = store.files.exists(path)
    old_digest = None
    if exists:
        old_data = store.files.read(path)
        old = decode_json(old_data)
        validate(old, STATE)
        store.check_refs(old, STATE, work_id)
        if old["work_id"] != work_id or expected_revision != old["revision"]:
            raise RecordError("Stale or mismatched state; reconcile before replacement")
        old_digest = digest(old_data)
    elif expected_revision != -1:
        raise RecordError("Initial state requires expected revision -1")
    if state["revision"] != expected_revision + 1:
        raise RecordError("State revision must increase exactly once")
    validate_progress(store, state)
    return store.files.publish(path, json_bytes(state), replace=exists, expected_digest=old_digest)


def validate_progress(store, state):
    work_id = state["work_id"]
    slices = {item["slice_id"]: item for item in state["slices"]}
    tasks = {item["task_id"]: item for item in state["tasks"]}
    if len(slices) != len(state["slices"]) or len(tasks) != len(state["tasks"]):
        raise RecordError("Duplicate slice/task identity")
    records = store.inventory(work_id)
    execution = summarize(records)["dispatches"]
    required_active = {path for path, entry in execution.items() if entry["status"] in {"running", "needs_reconciliation", "ended_missing_result"}}
    if not required_active <= {item["path"] for item in state["active_dispatch_refs"]}:
        raise RecordError("State cannot discard unresolved execution")
    for task in tasks.values():
        if task["slice_id"] not in slices:
            raise RecordError("Task has no owning slice")
        if task["status"] == "completed":
            if not task["completion_refs"]:
                raise RecordError("Completed task requires checked evidence")
            verified = []
            for reference in task["completion_refs"]:
                if reference["path"].endswith("/verification.json"):
                    verification = store.read_ref(reference, "verification")
                    allowed = {"passed", "assertion_failed"} if task["completion_kind"] == "verification_only" else {"passed"}
                    if (verification["result"] not in allowed or verification["target_match"] != "same"
                            or verification["expectation_met"] is not True or verification["task_id"] != task["task_id"]):
                        raise RecordError("Incomplete/changed-target verification cannot establish task completion")
                    valid_exit = (verification["exit_code"] == 0 if verification["result"] == "passed"
                                  else verification["exit_code"] not in {None, 0})
                    if not valid_exit or verification["ended_at"] is None or not verification["output_refs"]:
                        raise RecordError("Unfinished verification cannot establish task completion")
                    verified.append((reference, verification))
            if task["completion_kind"] in {"implementation", "verification_only"} and not verified:
                raise RecordError("Code/verification completion requires typed evidence for the same task")
            for reference in task["dispatch_refs"]:
                if execution[reference["path"]]["status"] not in {"ended_with_result", "not_started"}:
                    raise RecordError("Task execution has not ended with usable result evidence")
                dispatch = store.read_ref(reference, "dispatch")
                if dispatch["task_id"] != task["task_id"] or dispatch["slice_id"] != task["slice_id"]:
                    raise RecordError("Task completion links another task's dispatch")
            if task["completion_kind"] == "implementation":
                linked = False
                for reference in task["completion_refs"]:
                    if "/execution/results/" not in reference["path"]:
                        continue
                    result = store.read_ref(reference, "result")
                    if (result["dispatch_ref"] not in task["dispatch_refs"] or result["outcome"] != "completed"
                            or not completed_result_has_ended_host(store, result)):
                        continue
                    linked = linked or any(ref in result["verification_refs"] and result["attempt_ref"] == verification["attempt_ref"]
                                           for ref, verification in verified)
                if not linked:
                    raise RecordError("Implementation completion requires linked dispatch, result and passing verification")
    for item in slices.values():
        if item["status"] != "accepted":
            continue
        owned = [task for task in tasks.values() if task["slice_id"] == item["slice_id"]]
        if not owned or any(task["status"] != "completed" for task in owned) or item["unresolved_findings"]:
            raise RecordError("Slice acceptance requires completed tasks and resolved findings")
        if not item["review_ref"] or not item["review_target_ref"]:
            raise RecordError("Slice acceptance requires independent review and its target")
        review = store.read_ref(item["review_ref"], "review")
        if review["verdict"] != "Pass" or item["review_target_ref"] not in (review["bundle_ref"], review["code_target_ref"]):
            raise RecordError("Slice review and reviewed target do not establish acceptance")
        if any(task["completion_kind"] == "implementation" for task in owned):
            if not item["integration_verification_ref"]:
                raise RecordError("Implementation slice acceptance requires final integration verification")
            integration = store.read_ref(item["integration_verification_ref"], "verification")
            if not is_final_integration(integration):
                raise RecordError("Implementation slice requires passing final integration verification")
            if not review["code_target_ref"]:
                raise RecordError("Implementation slice requires review of code target")
            reviewed = store.read_ref(review["code_target_ref"], "code_target")
            verified = store.read_ref(integration["code_target_ref"], "code_target")
            if not same_code_target(reviewed, verified):
                raise RecordError("Implementation review and final integration target differ")
    if state["finish_ref"] and (state["active_dispatch_refs"] or required_active
                                or any(item["status"] != "accepted" for item in slices.values()) or state["blockers"]):
        raise RecordError("Finish cannot hide active work, unaccepted slices or blockers")


def update_current(store, text, expected_digest):
    if not isinstance(text, str) or not text.strip():
        raise RecordError("CURRENT content must be explicitly supplied")
    exists = store.files.exists("CURRENT.md")
    if exists and expected_digest is None:
        raise RecordError("Replacing CURRENT requires its expected digest")
    if not exists and expected_digest is not None:
        raise RecordError("CURRENT does not exist")
    return store.files.publish("CURRENT.md", text.encode(), replace=exists, expected_digest=expected_digest)
