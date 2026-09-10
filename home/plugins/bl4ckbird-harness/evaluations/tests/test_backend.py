import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness_eval.backend import preflight, run_codex


_FAKE = '''import json, os, pathlib, signal, sys, time
config = json.loads(pathlib.Path(__file__).with_suffix(".json").read_text())
args = sys.argv[1:]
def interrupt_caller():
    if config.get("second_interrupt"):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    print(json.dumps({"type": "thread.started"}), flush=True)
    os.kill(os.getppid(), signal.SIGINT)
    if config.get("second_interrupt"):
        time.sleep(0.4)
        os.kill(os.getppid(), signal.SIGINT)
    time.sleep(10)
if args[0] == "sandbox":
    if config.get("probe_interrupt"):
        interrupt_caller()
    if config.get("probe_passthrough"):
        command = args[args.index("--") + 1:]
        os.execv(command[0], command)
    mode = "read-only" if "sandbox_mode=" + json.dumps("read-only") in args else "workspace-write"
    if config.get("probe_malformed"):
        print("invalid probe output")
    else:
        result = {name: {"written": name == "inside" and mode == "workspace-write", "denied": name != "inside" or mode == "read-only"} for name in ("inside", "outside", "slash_tmp", "system_tmp")}
        if config.get("probe_escape"):
            result[config["probe_escape"]] = {"written": True, "denied": False}
        print(json.dumps(result))
    sys.exit(config.get("probe_exit", 0))
prompt = sys.stdin.read()
pathlib.Path("captured.json").write_text(json.dumps({"args": args, "prompt": prompt}))
if config.get("ignore_term"):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
if config.get("interrupt"):
    interrupt_caller()
if config.get("sleep"):
    time.sleep(config["sleep"])
if config.get("linger"):
    if os.fork() == 0:
        time.sleep(10)
        os._exit(0)
if not config.get("no_final"):
    pathlib.Path(args[args.index("-o") + 1]).write_text(config.get("final", "Completed fixture"))
for event in config.get("events", [{"type": "turn.completed", "usage": {"input_tokens": 12, "output_tokens": 3}}]):
    print(json.dumps(event), flush=True)
if config.get("invalid_line"):
    print("unframed text", flush=True)
sys.exit(config.get("exit", 0))
'''


@unittest.skipUnless(os.name == "posix", "POSIX sandbox process groups")
class BackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.output = self.root / "output"
        self.codex = self.root / "fake-codex"
        self.codex.write_text("#!" + sys.executable + "\n" + _FAKE)
        self.codex.chmod(0o700)
        self.configure()

    def configure(self, **config):
        self.codex.with_suffix(".json").write_text(json.dumps(config))

    def run_cli(self, **kwargs):
        return run_codex(str(self.codex), self.workspace, self.output,
                         "Fix the literal $(do-not-execute) `payload`", "fixture-model",
                         "high", kwargs.pop("timeout", 3), **kwargs)

    def test_success_preserves_explicit_configuration_and_terminal_evidence(self):
        result = self.run_cli()
        self.assertEqual(result["status"], "satisfied")
        self.assertTrue(result["termination_confirmed"])
        self.assertNotIn("usage", result)
        self.assertIn("turn.completed", (self.output / "events.jsonl").read_text())
        self.assertIsNone(result["actual_model"])
        captured = json.loads((self.workspace / "captured.json").read_text())
        self.assertIn("$(do-not-execute)", captured["prompt"])
        args = captured["args"]
        for option in ("--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
                       "--skip-git-repo-check", 'approval_policy="never"',
                       "project_doc_max_bytes=0", "sandbox_workspace_write.writable_roots=[]",
                       "sandbox_workspace_write.network_access=false",
                       "sandbox_workspace_write.exclude_slash_tmp=true",
                       "sandbox_workspace_write.exclude_tmpdir_env_var=true"):
            self.assertIn(option, args)
        self.assertEqual(args[args.index("--model") + 1], "fixture-model")
        self.assertIn('model_reasoning_effort="high"', args)
        self.assertNotIn("env", json.loads((self.output / "metadata.json").read_text()))

    def test_read_only_and_output_schema(self):
        schema = self.root / "schema.json"
        schema.write_text('{"type":"object"}')
        result = self.run_cli(read_only=True, output_schema=schema)
        self.assertEqual(result["command"][result["command"].index("--sandbox") + 1], "read-only")
        self.assertEqual(result["command"][result["command"].index("--output-schema") + 1], str(schema.resolve()))

    def test_nonzero_exit_is_not_success_even_with_terminal_event(self):
        self.configure(exit=2)
        result = self.run_cli()
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["returncode"], 2)

    def test_failed_turn_is_not_success(self):
        self.configure(events=[{"type": "turn.failed", "error": {"message": "denied"}}])
        self.assertEqual(self.run_cli()["status"], "failed")

    def test_empty_and_malformed_events_are_unverified(self):
        cases = [{"events": []}, {"invalid_line": True}, {"events": ["not an object"]},
                 {"events": [{"type": "thread.started"}]}]
        for index, config in enumerate(cases):
            with self.subTest(config=config):
                self.configure(**config)
                self.output = self.root / ("output-%d" % index)
                result = self.run_cli()
                self.assertEqual(result["status"], "unverified")
                self.assertTrue(result["process_group_terminated"])
                self.assertFalse(result["termination_confirmed"])
                metadata = json.loads((self.output / "metadata.json").read_text())
                self.assertFalse(metadata["termination_confirmed"])

    def test_malformed_line_cannot_be_hidden_by_valid_completion(self):
        self.configure(events=[
            {"type": "item.started", "item": {"id": "cmd-1", "type": "command_execution"}},
            "lost tool completion",
            {"type": "item.completed", "item": {"id": "cmd-1", "type": "command_execution"}},
            {"type": "turn.completed"},
        ])
        result = self.run_cli()
        self.assertTrue(result["process_group_terminated"])
        self.assertTrue(result["terminal_event"])
        self.assertEqual(result["pending_items"], [])
        self.assertFalse(result["events_valid"])
        self.assertFalse(result["termination_confirmed"])
        self.assertEqual(result["status"], "unverified")

    def test_missing_final_response_is_unverified(self):
        self.configure(no_final=True)
        self.assertEqual(self.run_cli()["status"], "unverified")

    def test_incomplete_tool_is_unverified(self):
        self.configure(events=[
            {"type": "item.started", "item": {"id": "cmd-1", "type": "command_execution"}},
            {"type": "turn.completed"},
        ])
        result = self.run_cli()
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(result["pending_items"], ["cmd-1"])

    def test_detached_command_signal_requires_reconciliation(self):
        self.configure(events=[
            {"type": "item.completed", "item": {"id": "cmd-1", "type": "command_execution", "command": "nohup worker &"}},
            {"type": "turn.completed"},
        ])
        self.assertEqual(self.run_cli()["status"], "unverified")

    def test_completed_failed_command_does_not_hide_a_later_successful_turn(self):
        self.configure(events=[
            {"type": "item.started", "item": {"id": "cmd-1", "type": "command_execution"}},
            {"type": "item.completed", "item": {"id": "cmd-1", "type": "command_execution", "status": "failed", "exit_code": 1}},
            {"type": "turn.completed"},
        ])
        self.assertEqual(self.run_cli()["status"], "satisfied")

    def test_shell_conjunction_and_redirection_are_not_background_launches(self):
        self.configure(events=[
            {"type": "item.completed", "item": {"id": "cmd-1", "type": "command_execution", "command": "check && report 2>&1"}},
            {"type": "turn.completed"},
        ])
        self.assertEqual(self.run_cli()["status"], "satisfied")

    def test_remaining_process_group_blocks_stable_completion(self):
        self.configure(linger=True)
        result = self.run_cli()
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(result["remaining_group_detected"])
        self.assertFalse(result["termination_confirmed"])

    def test_timeout_kills_process_group_even_when_term_is_ignored(self):
        self.configure(sleep=10, ignore_term=True)
        result = self.run_cli(timeout=1)
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(result["timed_out"])
        self.assertTrue(result["process_group_terminated"])
        self.assertFalse(result["termination_confirmed"])
        self.assertEqual(result["returncode"], -signal.SIGKILL)

    def test_missing_cli_returns_preserved_unverified_result(self):
        self.codex = self.root / "nonexistent"
        result = self.run_cli()
        self.assertEqual(result["status"], "unverified")
        self.assertTrue((self.output / "metadata.json").is_file())

    def test_keyboard_interrupt_stops_group_and_preserves_metadata(self):
        previous = signal.getsignal(signal.SIGINT)
        self.configure(interrupt=True)
        result = self.run_cli()
        self.assertTrue(result["interrupted"])
        self.assertFalse(result["timed_out"])
        self.assertTrue(result["process_group_terminated"])
        self.assertFalse(result["termination_confirmed"])
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(result["returncode"], -signal.SIGTERM)
        self.assertEqual(signal.getsignal(signal.SIGINT), previous)
        metadata = json.loads((self.output / "metadata.json").read_text())
        self.assertTrue(metadata["interrupted"])
        self.assertTrue((self.output / "events.jsonl").read_text().strip())

    def test_second_interrupt_forces_kill_without_losing_metadata(self):
        previous = signal.getsignal(signal.SIGINT)
        self.configure(interrupt=True, second_interrupt=True)
        result = self.run_cli()
        self.assertTrue(result["interrupted"])
        self.assertTrue(result["repeated_interrupt"])
        self.assertTrue(result["process_group_terminated"])
        self.assertEqual(result["returncode"], -signal.SIGKILL)
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(signal.getsignal(signal.SIGINT), previous)
        metadata = json.loads((self.output / "metadata.json").read_text())
        self.assertTrue(metadata["repeated_interrupt"])

    def test_preflight_interrupt_stops_before_next_probe(self):
        self.configure(probe_interrupt=True)
        result = preflight(str(self.codex), self.workspace, self.output)
        self.assertTrue(result["interrupted"])
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(len(result["checks"]), 1)
        self.assertTrue(result["checks"][0]["termination_confirmed"])
        self.assertTrue((self.output / "preflight.json").is_file())

    def test_output_and_schema_must_be_outside_workspace(self):
        self.output = self.workspace / "output"
        with self.assertRaises(ValueError):
            self.run_cli()
        self.output = self.root / "output"
        schema = self.workspace / "schema.json"
        schema.write_text("{}")
        with self.assertRaises(ValueError):
            self.run_cli(output_schema=schema)

    def test_existing_run_evidence_is_not_overwritten(self):
        self.run_cli()
        before = (self.output / "events.jsonl").read_bytes()
        with self.assertRaises(ValueError):
            self.run_cli()
        self.assertEqual((self.output / "events.jsonl").read_bytes(), before)

    def test_preflight_checks_workspace_read_only_and_shared_tmp(self):
        result = preflight(str(self.codex), self.workspace, self.output)
        self.assertEqual(result["status"], "satisfied")
        self.assertEqual(len(result["checks"]), 2)
        self.assertFalse(result["checks"][1]["probe"]["inside"]["written"])
        self.assertNotIn("-C", result["checks"][0]["command"])
        self.assertTrue(result["checks"][0]["probe"]["slash_tmp"]["denied"])

    def test_preflight_rejects_writable_external_or_shared_paths(self):
        for name in ("outside", "slash_tmp", "system_tmp"):
            with self.subTest(name=name):
                self.configure(probe_escape=name)
                self.output = self.root / name
                result = preflight(str(self.codex), self.workspace, self.output)
                self.assertEqual(result["status"], "failed")
                self.assertEqual(len(result["checks"]), 1)

    def test_preflight_rejects_malformed_json_and_nonzero_exit(self):
        for index, config in enumerate(({"probe_malformed": True}, {"probe_exit": 4})):
            with self.subTest(config=config):
                self.configure(**config)
                self.output = self.root / ("probe-%d" % index)
                self.assertEqual(preflight(str(self.codex), self.workspace, self.output)["status"], "failed")

    def test_real_probe_detects_cli_that_does_not_enforce_sandbox(self):
        self.configure(probe_passthrough=True)
        result = preflight(str(self.codex), self.workspace, self.output)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["checks"][0]["probe"]["inside"]["written"])
        self.assertTrue(result["checks"][0]["probe"]["outside"]["written"])
        self.assertFalse(list(self.workspace.glob(".harness-probe-*")))
        self.assertFalse(list(self.output.glob(".harness-probe-*")))


if __name__ == "__main__":
    unittest.main()
