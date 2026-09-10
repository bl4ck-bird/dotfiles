"""CLI로도 제공하는 정확한 JSON Schema와 표준 라이브러리 검증."""

import copy
from datetime import datetime
import re

from .errors import RecordError

ID_PATTERN = r"^\d{4}-\d{2}-\d{2}-\d{3,}-[a-z0-9가-힣][a-z0-9가-힣-]*$"
S = {"type": "string", "minLength": 1}
ID = {**S, "pattern": ID_PATTERN, "x-harness-id": True}
TIME = {**S, "format": "date-time"}
BOOL = {"type": "boolean"}


def obj(fields):
    return {"type": "object", "properties": fields, "required": list(fields), "additionalProperties": False}


def array(items, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum}


def nullable(value):
    return {"anyOf": [value, {"type": "null"}]}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def ref(kind=None):
    result = obj({"path": S, "sha256": {"type": "string", "pattern": r"^[0-9a-f]{64}$"}})
    if kind:
        result["x-record-kind"] = kind
    else:
        result["x-evidence-ref"] = True
    return result


REF = ref()
STRINGS = array(S)
STAGE = enum("discover", "design", "roadmap", "spec", "plan", "execute", "review", "diagnose", "finish")
COMMON = {"schema_version": {"type": "integer", "enum": [1]}, "kind": S,
          "record_id": ID, "work_id": ID, "created_at": TIME}
FINDING = obj({"finding_id": S, "severity": enum("Critical", "Important", "Minor"),
               "location": S, "requirement_or_risk": S, "condition": S,
               "evidence_refs": array(REF, 1), "impact": S, "resolution": S})
FILE = obj({"path": S, "kind": enum("file", "symlink", "deleted"),
            "mode": nullable({"type": "integer", "minimum": 0}),
            "sha256": nullable({"type": "string", "pattern": r"^[0-9a-f]{64}$"}),
            "content_ref": nullable(REF), "link_target": nullable(S),
            "git_status": S, "index_mode": nullable(S), "index_sha256": nullable(S),
            "index_content_ref": nullable(REF)})

FIELDS = {
    "repair": {"original_state_ref": REF, "replacement_state_ref": REF,
               "previous_revision": nullable({"type": "integer", "minimum": 0}),
               "replacement_revision": {"type": "integer", "minimum": 0},
               "reason": S, "evidence_refs": array(REF, 1)},
    "dispatch": {"stage": STAGE, "role": enum("implementer", "reviewer", "verifier", "diagnostician"),
                 "logical_dispatch_id": ID, "call_index": {"type": "integer", "minimum": 0, "maximum": 2},
                 "previous_dispatch_ref": nullable(ref("dispatch")), "task_id": nullable(S), "slice_id": nullable(ID),
                 "attempt_ref": nullable(ref("attempt")), "workspace": S, "scope": S,
                 "write_paths": STRINGS, "shared_resources": STRINGS,
                 "input_refs": array(REF), "authority": S, "authority_refs": array(REF),
                 "model": S, "effort": S, "report_path": S},
    "host": {"dispatch_ref": ref("dispatch"), "host_id": nullable(S), "observed_at": TIME,
             "execution_state": enum("not_started", "running", "ended", "unknown"),
             "background_state": enum("not_applicable", "running", "ended", "unknown"),
             "evidence_refs": array(REF), "limitations": STRINGS},
    "result": {"dispatch_ref": ref("dispatch"), "attempt_ref": nullable(ref("attempt")),
               "host_ref": nullable(ref("host")), "report_ref": REF,
               "outcome": enum("completed", "failed", "interrupted", "inconclusive"),
               "applied": nullable(BOOL), "verification_refs": array(ref("verification")), "observed_at": TIME},
    "attempt": {"issue_id": ID, "hypothesis": S, "code_target_ref": ref("code_target"),
                "previous_attempt_ref": nullable(ref("attempt")), "new_evidence_refs": array(REF),
                "different_approach": nullable(S)},
    "disposition": {"issue_id": ID, "review_ref": ref("review"), "finding_id": S,
                    "decision": enum("valid", "false_positive", "resolved", "unresolved"),
                    "reason": S, "evidence_refs": array(REF, 1), "attempt_refs": array(ref("attempt"))},
    "round": {"slice_id": ID, "issue_ids": array(ID, 1), "attempt_refs": array(ref("attempt")),
              "disposition_refs": array(ref("disposition"))},
    "verification": {"code_target_ref": ref("code_target"), "after_target_ref": nullable(ref("code_target")),
                     "task_id": nullable(S), "attempt_ref": nullable(ref("attempt")), "acceptance": array(S, 1),
                     "command": array(S, 1), "cwd": S, "started_at": TIME, "ended_at": nullable(TIME),
                     "environment": array(obj({"name": S, "identity": S})),
                     "result": enum("passed", "assertion_failed", "runner_failed", "no_tests", "skipped", "interrupted", "not_run"),
                     "target_match": enum("same", "changed", "unverified"),
                     "exit_code": nullable({"type": "integer"}), "expected": S, "expectation_met": nullable(BOOL),
                     "output_refs": array(REF), "limitations": STRINGS},
    "approval": {"bundle_ref": ref("bundle"), "review_refs": array(ref("review"), 1),
                 "request_text": S, "response_text": S, "response_at": nullable(TIME),
                 "session_ref": nullable(S), "message_ref": nullable(S),
                 "action": enum("grant", "amend", "withdraw"), "previous_approval_ref": nullable(ref("approval")),
                 "authority": array(enum("design", "implementation", "delivery"), 1), "scope": S,
                 "conditions": STRINGS, "body": S},
    "review": {"stage": STAGE, "bundle_ref": nullable(ref("bundle")), "code_target_ref": nullable(ref("code_target")),
               "scope": S, "evidence_refs": array(REF), "findings": array(FINDING),
               "verdict": enum("Pass", "Changes required", "Inconclusive"), "limitations": STRINGS,
               "previous_review_ref": nullable(ref("review")), "body": S},
    "bundle": {"documents": array(obj({"source_path": S, "copy_ref": REF,
                                       "role": enum("target", "basis")}), 1)},
    "code_target": {"workspace_id": S, "workspace": S, "base_commit": nullable(S), "head": nullable(S),
                    "scope": S, "inclusions": array(S, 1), "exclusions": STRINGS, "files": array(FILE, 1),
                    "external_inputs": array(obj({"role": S, "safe_identity": nullable(S), "limitation": nullable(S)})),
                    "limitations": STRINGS},
}

TASK = obj({"task_id": S, "slice_id": ID, "plan_ref": REF,
            "completion_kind": enum("implementation", "verification_only", "documentation"),
            "status": enum("pending", "running", "needs_reconciliation", "blocked", "completed"),
            "dispatch_refs": array(ref("dispatch")), "completion_refs": array(REF)})
SLICE = obj({"slice_id": ID, "plan_ref": REF, "status": enum("pending", "running", "blocked", "accepted"),
             "review_ref": nullable(ref("review")), "review_target_ref": nullable(REF),
             "integration_verification_ref": nullable(ref("verification")),
             "unresolved_findings": array(obj({"review_ref": ref("review"), "finding_id": S}))})
STATE = obj({"schema_version": {"type": "integer", "enum": [1]}, "work_id": ID,
             "revision": {"type": "integer", "minimum": 0}, "stage": STAGE,
             "approval_refs": array(ref("approval")), "slices": array(SLICE), "tasks": array(TASK),
             "active_dispatch_refs": array(ref("dispatch")),
             "blockers": array(obj({"scope": S, "reason": S, "resolution": S, "evidence_refs": array(REF)})),
             "finish_ref": nullable(REF)})


def schema(kind):
    if kind == "state":
        return copy.deepcopy(STATE)
    if kind not in FIELDS:
        raise RecordError("Unknown record kind: " + repr(kind))
    return obj({**copy.deepcopy(COMMON), "kind": enum(kind), **copy.deepcopy(FIELDS[kind])})


def validate(value, definition, location="record"):
    if "anyOf" in definition:
        for choice in definition["anyOf"]:
            try:
                validate(value, choice, location)
                return
            except RecordError:
                pass
        raise RecordError(location + ": no allowed type matches")
    kind = definition["type"]
    matches = {"object": lambda: type(value) is dict, "array": lambda: type(value) is list,
               "string": lambda: type(value) is str, "integer": lambda: type(value) is int,
               "number": lambda: type(value) in (int, float), "boolean": lambda: type(value) is bool,
               "null": lambda: value is None}
    if not matches[kind]():
        raise RecordError(location + ": expected " + kind)
    if "enum" in definition and value not in definition["enum"]:
        raise RecordError(location + ": unsupported value")
    if kind == "object":
        fields = definition["properties"]
        if set(value) != set(fields):
            raise RecordError(location + ": missing or unknown fields: " + repr(sorted(set(value) ^ set(fields))))
        for key in fields:
            validate(value[key], fields[key], location + "." + key)
    elif kind == "array":
        if len(value) < definition.get("minItems", 0):
            raise RecordError(location + ": too few items")
        for index, item in enumerate(value):
            validate(item, definition["items"], location + "[" + str(index) + "]")
    elif kind == "string":
        if len(value) < definition.get("minLength", 0) or ("pattern" in definition and not re.fullmatch(definition["pattern"], value)):
            raise RecordError(location + ": invalid string")
        if definition.get("format") == "date-time":
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError()
            except ValueError:
                raise RecordError(location + ": timezone-aware timestamp required")
        if definition.get("x-harness-id"):
            try:
                datetime.strptime(value[:10], "%Y-%m-%d")
            except ValueError:
                raise RecordError(location + ": invalid identifier date")
    elif kind in ("integer", "number"):
        import math
        if not math.isfinite(value) or value < definition.get("minimum", float("-inf")) or value > definition.get("maximum", float("inf")):
            raise RecordError(location + ": invalid number")


def template(definition):
    if "anyOf" in definition:
        return None
    kind = definition["type"]
    if "enum" in definition:
        return definition["enum"][0]
    if kind == "object":
        return {key: template(item) for key, item in definition["properties"].items()}
    return {"array": [], "string": "", "integer": 0, "number": 0, "boolean": False, "null": None}[kind]
