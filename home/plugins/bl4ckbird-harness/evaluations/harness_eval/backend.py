import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
from typing import Optional
import uuid


_LIMITATIONS = [
    "Authentication environment is inherited without inspection or copying.",
    "Process-group checks cannot enumerate commands detached into another session.",
    "Requested model settings are not evidence of the model actually applied.",
]


def _paths(workspace, output_dir):
    workspace = Path(workspace).resolve(strict=True)
    output_dir = Path(output_dir).resolve()
    if not workspace.is_dir():
        raise ValueError("workspace must be a directory")
    if output_dir == workspace or workspace in output_dir.parents:
        raise ValueError("output_dir must be outside the target workspace")
    output_dir.mkdir(parents=True, exist_ok=True)
    return workspace, output_dir


def _config():
    settings = [
        'approval_policy="never"',
        'project_doc_max_bytes=0',
        'sandbox_workspace_write.writable_roots=[]',
        'sandbox_workspace_write.network_access=false',
        'sandbox_workspace_write.exclude_slash_tmp=true',
        'sandbox_workspace_write.exclude_tmpdir_env_var=true',
    ]
    return [arg for setting in settings for arg in ("-c", setting)]


def _group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _stop_group(process):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        if _group_exists(process.pid):
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 0.5
        while time.monotonic() < deadline:
            process.poll()
            if not _group_exists(process.pid):
                return True
            time.sleep(0.02)
    process.poll()
    return not _group_exists(process.pid)


def _stop_interrupted_group(process, result):
    def force_stop(signum=None, frame=None):
        result["repeated_interrupt"] = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    previous_handler = None
    installed = False
    try:
        previous_handler = signal.signal(signal.SIGINT, force_stop)
        installed = True
    except ValueError:
        pass
    try:
        try:
            return _stop_group(process)
        except KeyboardInterrupt:
            force_stop()
            try:
                process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                return False
            return not _group_exists(process.pid)
    finally:
        if installed:
            signal.signal(signal.SIGINT, previous_handler)


def _invoke(command, workspace, stdout_path, stderr_path, timeout, prompt=None):
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    started = time.time()
    monotonic_start = time.monotonic()
    result = {
        "returncode": None,
        "timed_out": False,
        "interrupted": False,
        "repeated_interrupt": False,
        "termination_confirmed": False,
        "remaining_group_detected": False,
        "errors": [],
        "started_at": started,
    }
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        if os.name != "posix" or not hasattr(os, "killpg"):
            result["errors"].append("POSIX process-group control is required")
        else:
            try:
                process = subprocess.Popen(
                    command,
                    cwd=str(workspace),
                    stdin=subprocess.PIPE if prompt is not None else subprocess.DEVNULL,
                    stdout=stdout,
                    stderr=stderr,
                    shell=False,
                    start_new_session=True,
                )
            except OSError as exc:
                result["errors"].append("CLI launch failed: " + type(exc).__name__)
            else:
                result["pid"] = process.pid
                try:
                    try:
                        process.communicate(
                            input=None if prompt is None else prompt.encode("utf-8"),
                            timeout=timeout,
                        )
                    except subprocess.TimeoutExpired:
                        result["timed_out"] = True
                        result["errors"].append("CLI timed out")
                        result["termination_confirmed"] = _stop_group(process)
                    else:
                        result["remaining_group_detected"] = _group_exists(process.pid)
                        if result["remaining_group_detected"]:
                            result["errors"].append("Processes remained in the CLI group after exit")
                            result["termination_confirmed"] = _stop_group(process)
                        else:
                            result["termination_confirmed"] = True
                except KeyboardInterrupt:
                    result["interrupted"] = True
                    result["errors"].append("CLI invocation interrupted by caller")
                    result["termination_confirmed"] = _stop_interrupted_group(process, result)
                result["returncode"] = process.poll()
    result["finished_at"] = time.time()
    result["duration_seconds"] = time.monotonic() - monotonic_start
    return result


def _read_events(path):
    events = []
    errors = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeError:
        return [], ["Events are not valid UTF-8"]
    for number, line in enumerate(lines, 1):
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            errors.append("Invalid JSONL at line %d" % number)
            continue
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            errors.append("Invalid event shape at line %d" % number)
            continue
        events.append(event)
    if not events:
        errors.append("No JSONL events")
    return events, errors


def _event_state(events):
    active = set()
    uncertain = []
    actual_model = None
    failed = False
    for event in events:
        kind = event["type"]
        item = event.get("item")
        if kind in ("error", "turn.failed"):
            failed = True
        if isinstance(event.get("model"), str):
            actual_model = event["model"]
        if isinstance(item, dict):
            identifier = item.get("id")
            if kind == "item.started":
                if not isinstance(identifier, str):
                    uncertain.append("Started item has no usable identifier")
                else:
                    active.add(identifier)
            elif kind == "item.completed" and isinstance(identifier, str):
                active.discard(identifier)
            if kind == "item.completed" and item.get("status") in ("in_progress", "running"):
                uncertain.append("Completed event reports a running item")
            if item.get("type") == "command_execution":
                command = item.get("command", "")
                if isinstance(command, str) and (
                    any(marker in command for marker in ("nohup ", "setsid ", "start_new_session", "disown"))
                    or re.search(r"(?<![&>])&(?![&>])", command)
                ):
                    uncertain.append("Command may have detached work requiring external reconciliation")
    terminal = bool(events) and events[-1]["type"] == "turn.completed"
    return {
        "terminal_event": terminal,
        "pending_items": sorted(active),
        "actual_model": actual_model,
        "event_failure": failed,
        "uncertain_execution": uncertain,
    }


def run_codex(codex, workspace: Path, output_dir: Path, prompt: str, model: str,
              effort: str, timeout: float, read_only=False,
              output_schema: Optional[Path] = None) -> dict:
    workspace, output_dir = _paths(workspace, output_dir)
    if not model or not effort:
        raise ValueError("model and effort must be explicit")
    final_path = output_dir / "final.txt"
    if any((output_dir / name).exists() for name in ("final.txt", "events.jsonl", "stderr.txt", "metadata.json")):
        raise ValueError("run output files must not already exist")
    command = [
        str(codex), "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral",
        "--json", "--skip-git-repo-check", "--sandbox", "read-only" if read_only else "workspace-write",
        "--model", model,
    ] + _config() + [
        "-c", "model_reasoning_effort=" + json.dumps(effort),
        "-c", 'web_search="disabled"', "-o", str(final_path),
    ]
    if output_schema is not None:
        schema = Path(output_schema).resolve(strict=True)
        if schema == workspace or workspace in schema.parents:
            raise ValueError("output schema must be outside the target workspace")
        command.extend(["--output-schema", str(schema)])
    command.append("-")
    events_path, stderr_path = output_dir / "events.jsonl", output_dir / "stderr.txt"
    result = _invoke(command, workspace, events_path, stderr_path, timeout, prompt)
    events, event_errors = _read_events(events_path)
    state = _event_state(events)
    result.update(state)
    result["process_group_terminated"] = result["termination_confirmed"]
    result["event_stream_closed"] = bool(events) and events[-1]["type"] in ("turn.completed", "turn.failed")
    result["termination_confirmed"] = bool(
        result["process_group_terminated"] and not state["pending_items"]
        and not state["uncertain_execution"] and not result["remaining_group_detected"]
        and not event_errors and result["event_stream_closed"]
    )
    result["events_valid"] = not event_errors
    result["errors"].extend(event_errors)
    if not state["terminal_event"]:
        result["errors"].append("Final turn.completed event is missing")
    if state["pending_items"]:
        result["errors"].append("Started items remain incomplete")
    result["errors"].extend(state["uncertain_execution"])
    if state["event_failure"]:
        result["errors"].append("CLI reported an error or failed turn")
    if not final_path.is_file() or not final_path.read_bytes().strip():
        result["errors"].append("Final response file is missing or empty")
    if result["returncode"] not in (None, 0):
        result["errors"].append("CLI exited unsuccessfully")
    if result["interrupted"] or not result["termination_confirmed"]:
        result["status"] = "unverified"
    elif result["timed_out"] or result["returncode"] not in (None, 0) or state["event_failure"]:
        result["status"] = "failed"
    elif result["errors"] or not result["termination_confirmed"]:
        result["status"] = "unverified"
    else:
        result["status"] = "satisfied"
    result.update({
        "command": command,
        "workspace": str(workspace),
        "requested_model": model,
        "requested_effort": effort,
        "actual_effort": None,
        "read_only": bool(read_only),
        "limitations": list(_LIMITATIONS),
        "termination_scope": "CLI process group and reported item lifecycle only",
        "paths": {"events": str(events_path), "stderr": str(stderr_path),
                  "final": str(final_path), "metadata": str(output_dir / "metadata.json")},
    })
    (output_dir / "metadata.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


_PROBE = '''import json, pathlib, sys
results = {}
for name, value in json.loads(sys.argv[1]).items():
    path = pathlib.Path(value)
    try:
        with path.open("x") as stream:
            stream.write("harness sandbox probe")
    except PermissionError:
        results[name] = {"written": False, "denied": True}
    except OSError as error:
        results[name] = {"written": False, "denied": False, "error": type(error).__name__}
    else:
        results[name] = {"written": True, "denied": False}
        try:
            path.unlink()
        except OSError as error:
            results[name]["cleanup_error"] = type(error).__name__
print(json.dumps(results))
'''


def preflight(codex, workspace: Path, output_dir: Path) -> dict:
    workspace, output_dir = _paths(workspace, output_dir)
    result = {"status": "unverified", "interrupted": False, "checks": [], "errors": [], "limitations": [
        "Probe validates filesystem write boundaries, not provider transport or all inherited environment behavior.",
        "Sandbox subcommand lacks exec's ignore-user-config and ignore-rules options; explicit sandbox overrides are probed.",
    ], "paths": {"metadata": str(output_dir / "preflight.json")}}
    if (output_dir / "preflight.json").exists():
        raise ValueError("preflight output must not already exist")
    for mode in ("workspace-write", "read-only"):
        token = ".harness-probe-" + uuid.uuid4().hex
        probes = {
            "inside": str(workspace / token),
            "outside": str(output_dir / token),
            "slash_tmp": str(Path("/tmp") / token),
            "system_tmp": str(Path(tempfile.gettempdir()) / token),
        }
        command = [str(codex), "sandbox"] + _config() + [
            "-c", "sandbox_mode=" + json.dumps(mode), "--", sys.executable, "-c", _PROBE,
            json.dumps(probes),
        ]
        stdout_path, stderr_path = output_dir / (mode + ".json"), output_dir / (mode + ".stderr.txt")
        check = _invoke(command, workspace, stdout_path, stderr_path, 20.0)
        result["interrupted"] = result["interrupted"] or check["interrupted"]
        check.update({"mode": mode, "command": command, "probe": None,
                      "stdout": str(stdout_path), "stderr": str(stderr_path)})
        try:
            probe = json.loads(stdout_path.read_text(encoding="utf-8"))
            check["probe"] = probe
        except (ValueError, UnicodeError):
            check["errors"].append("Probe did not return one valid JSON document")
        else:
            if not isinstance(probe, dict) or set(probe) != set(probes):
                check["errors"].append("Probe result keys differ from requested checks")
            else:
                for name in probes:
                    expected_write = name == "inside" and mode == "workspace-write"
                    expected = {"written": expected_write, "denied": not expected_write}
                    if probe[name] != expected:
                        check["errors"].append("Unexpected write boundary for " + name)
        check["passed"] = (check["returncode"] == 0 and check["termination_confirmed"]
                           and not check["timed_out"] and not check["errors"])
        result["checks"].append(check)
        if not check["passed"]:
            result["errors"].append(mode + " sandbox probe failed")
            break
    if result["interrupted"]:
        result["status"] = "unverified"
    elif len(result["checks"]) == 2 and not result["errors"]:
        result["status"] = "satisfied"
    else:
        result["status"] = "failed"
    (output_dir / "preflight.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
