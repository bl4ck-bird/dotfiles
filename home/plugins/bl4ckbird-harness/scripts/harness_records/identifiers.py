"""중단된 예약까지 보존하는 종류/부모 범위별 식별자 발급."""

from datetime import datetime
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .errors import RecordError
from .files import decode_json, json_bytes
from .schema import ID, validate

KINDS = {"work", "slice", "decision", "review", "diagnosis", "dispatch", "attempt", "disposition",
         "round", "repair", "verification", "approval", "bundle", "code_target", "host", "result"}


def existing_names(files, kind, work_id):
    if kind in {"work", "decision"}:
        return files.entries("work" if kind == "work" else "decisions")
    from .store import DIRECTORIES
    prefix = "work/" + work_id + "/"
    directory = DIRECTORIES.get(kind, {"bundle": "snapshots", "code_target": "snapshots/code",
                                      "verification": "evidence", "diagnosis": "diagnosis", "slice": "slices"}.get(kind))
    names = files.entries(prefix + directory)
    if kind == "slice" and files.exists(prefix + "state.json"):
        state = decode_json(files.read(prefix + "state.json"))
        from .schema import STATE
        validate(state, STATE)
        names.extend(item["slice_id"] for item in state["slices"])
    return names


def reserve(files, kind, description, timezone, work_id=None, now=None):
    if kind not in KINDS or not re.fullmatch(r"[a-z0-9가-힣][a-z0-9가-힣-]*", description):
        raise RecordError("Unsupported identifier kind or description")
    if kind in {"work", "decision"}:
        scope = "project"
    else:
        validate(work_id, ID, "work_id")
        scope = work_id
    try:
        zone = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise RecordError("An available explicit project/user timezone is required")
    instant = now or datetime.now(zone)
    if instant.tzinfo is None:
        raise RecordError("Clock must be timezone-aware")
    date = instant.astimezone(zone).strftime("%Y-%m-%d")
    prefix = ".reservations/" + kind + "/" + scope
    paths = files.scan(prefix) + existing_names(files, kind, work_id)
    maximum = 0
    pattern = re.compile(re.escape(date) + r"-(\d+)-")
    for path in paths:
        match = pattern.match(path.rsplit("/", 1)[-1])
        if match:
            maximum = max(maximum, int(match[1]))
    for number in range(maximum + 1, maximum + 1001):
        identifier = "%s-%03d-%s" % (date, number, description)
        reservation = {"schema_version": 1, "kind": kind, "id": identifier,
                       "scope": scope, "timezone": timezone, "reserved_at": instant.astimezone(zone).isoformat()}
        path = prefix + "/" + identifier + ".json"
        try:
            reference = files.publish(path, json_bytes(reservation))
        except RecordError:
            if files.exists(path):
                continue
            raise
        return {**reservation, "reservation_ref": reference}
    raise RecordError("Could not reserve an unused identifier")


def require_reservation(files, kind, identifier, work_id):
    validate(identifier, ID, "record_id")
    scope = "project" if kind in {"work", "decision"} else work_id
    path = ".reservations/" + kind + "/" + scope + "/" + identifier + ".json"
    from .files import decode_json
    record = decode_json(files.read(path))
    if record.get("id") != identifier or record.get("kind") != kind or record.get("scope") != scope:
        raise RecordError("Identifier reservation does not match publication")
