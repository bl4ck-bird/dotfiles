import copy
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from support import RecordCase
from harness_records.capture import capture_code, capture_documents, compare_target
from harness_records.errors import RecordError


class CaptureTests(RecordCase):
    def document_bundle(self):
        path = "work/" + self.work_id + "/spec.md"
        self.store.files.publish(path, b"Accepted behavior")
        return capture_documents(self.store, self.work_id, self.identifier("bundle"), [{"path": path, "role": "target"}])

    def test_document_approval_preserves_exact_response_and_detects_copy_tampering(self):
        bundle = self.document_bundle()
        review = self.store.publish(self.record("review", stage="spec", bundle_ref=bundle, scope="behavior",
                                                evidence_refs=[self.evidence], findings=[], verdict="Pass", limitations=[], body="검토 통과"))
        approval = self.record("approval", bundle_ref=bundle, review_refs=[review], request_text="이 명세대로 진행할까요?",
                               response_text="응", authority=["design"], scope="specified behavior", conditions=[], body="현재 요청과 응답 보존")
        published = self.store.publish(approval)
        self.assertEqual(self.store.read_record(published["path"])["response_text"], "응")
        self.assertIsNone(self.store.read_record(published["path"])["message_ref"])
        content = self.store.read_record(bundle["path"])["documents"][0]["copy_ref"]
        (self.store.files.root / content["path"]).write_bytes(b"changed accepted behavior")
        with self.assertRaises(RecordError):
            compare_target(self.store, bundle)
        with self.assertRaises(RecordError):
            self.store.publish({**approval, "record_id": self.identifier("approval")})

    def test_review_for_another_bundle_cannot_approve_current_bundle(self):
        first = self.document_bundle()
        second = capture_documents(self.store, self.work_id, self.identifier("bundle"),
                                   [{"path": "work/" + self.work_id + "/spec.md", "role": "target"}])
        review = self.store.publish(self.record("review", stage="spec", bundle_ref=first, scope="behavior",
                                                evidence_refs=[], findings=[], verdict="Pass", limitations=[], body="reviewed first target"))
        approval = self.record("approval", bundle_ref=second, review_refs=[review], request_text="Approve?", response_text="yes",
                               authority=["design"], scope="behavior", conditions=[], body="response preserved")
        with self.assertRaises(RecordError):
            self.store.publish(approval)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.workspace), *args], check=True, capture_output=True).stdout

    def test_code_capture_distinguishes_index_worktree_deletion_modes_and_head(self):
        self.git("init", "--template=", "--quiet")
        (self.workspace / "app.py").write_text("baseline\n")
        (self.workspace / "deleted.py").write_text("preserve deletion\n")
        self.git("add", "--", "app.py", "deleted.py")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                 "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Fixture")
        head = self.git("rev-parse", "HEAD").decode().strip()
        (self.workspace / "app.py").write_text("staged\n")
        self.git("add", "--", "app.py")
        (self.workspace / "app.py").write_text("working tree\n")
        (self.workspace / "app.py").chmod(0o755)
        (self.workspace / "deleted.py").unlink()
        (self.workspace / "new.py").write_text("new file\n")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace,
                              "fixture-workspace", ["app.py", "deleted.py", "new.py"], "three explicit inputs", head)
        record = self.store.read_record(target["path"])
        files = {item["path"]: item for item in record["files"]}
        self.assertEqual(record["head"], head)
        self.assertEqual(record["base_commit"], head)
        self.assertNotEqual(files["app.py"]["sha256"], files["app.py"]["index_sha256"])
        self.assertEqual(self.store.files.read(files["app.py"]["index_content_ref"]["path"]), b"staged\n")
        self.assertEqual(files["app.py"]["mode"], 0o755)
        self.assertEqual(files["deleted.py"]["kind"], "deleted")
        self.assertEqual(files["new.py"]["git_status"], "??")
        self.assertTrue(compare_target(self.store, target)["matches"])
        (self.workspace / "app.py").chmod(0o644)
        self.assertEqual(compare_target(self.store, target)["changed_inputs"], ["app.py"])

    def test_non_git_capture_preserves_contents_without_inventing_base(self):
        (self.workspace / "app.py").write_bytes(b"actual code")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace,
                              "fixture", ["app.py"], "explicit scope")
        record = self.store.read_record(target["path"])
        self.assertIsNone(record["base_commit"])
        self.assertIsNone(record["head"])
        self.assertEqual(self.store.files.read(record["files"][0]["content_ref"]["path"]), b"actual code")

    def test_secret_candidates_and_symlink_directory_are_not_captured(self):
        (self.workspace / ".env").write_text("not copied")
        with self.assertRaises(RecordError):
            capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace, "fixture", [".env"], "scope")
        external = self.root / "external"
        external.mkdir()
        (external / "data.txt").write_text("not copied")
        (self.workspace / "link").symlink_to(external, target_is_directory=True)
        with self.assertRaises(RecordError):
            capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace, "fixture", ["link/data.txt"], "scope")

    def test_manifest_cannot_claim_content_hash_other_than_preserved_bytes(self):
        (self.workspace / "app.py").write_text("actual")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace, "fixture", ["app.py"], "scope")
        record = self.store.read_record(target["path"])
        record["record_id"] = self.identifier("code_target")
        record["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(RecordError):
            self.store.publish(record)

    def test_git_pathspec_magic_cannot_capture_a_secret_candidate(self):
        self.git("init", "--template=", "--quiet")
        dummy = b"dummy-secret-fixture-not-real"
        (self.workspace / ".env").write_bytes(dummy)
        self.git("add", "--force", "--", ".env")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace,
                              "fixture", [":(literal).env"], "literal path only")
        item = self.store.read_record(target["path"])["files"][0]
        self.assertEqual(item["kind"], "deleted")
        self.assertIsNone(item["index_content_ref"])
        for path in self.store.files.scan("work/" + self.work_id + "/snapshots"):
            self.assertNotIn(dummy, self.store.files.read(path))

    def test_literal_wildcard_filename_does_not_expand(self):
        self.git("init", "--template=", "--quiet")
        (self.workspace / "*.txt").write_text("literal wildcard file")
        (self.workspace / "other.txt").write_text("unselected file")
        self.git("add", "--", "*.txt", "other.txt")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace,
                              "fixture", ["*.txt"], "literal path only")
        item = self.store.read_record(target["path"])["files"][0]
        self.assertEqual(item["path"], "*.txt")
        self.assertEqual(self.store.files.read(item["index_content_ref"]["path"]), b"literal wildcard file")

    def test_git_capture_does_not_execute_repository_fsmonitor_hook(self):
        self.git("init", "--template=", "--quiet")
        (self.workspace / "app.py").write_text("fixture")
        self.git("add", "--", "app.py")
        hook = self.workspace / "monitor.sh"
        hook.write_text("#!/bin/sh\n: > monitor-was-run\n")
        hook.chmod(0o755)
        self.git("config", "core.fsmonitor", "./monitor.sh")
        target = capture_code(self.store, self.work_id, self.identifier("code_target"), self.workspace,
                              "fixture", ["app.py"], "explicit code")
        self.assertTrue(compare_target(self.store, target)["matches"])
        self.assertFalse((self.workspace / "monitor-was-run").exists())
