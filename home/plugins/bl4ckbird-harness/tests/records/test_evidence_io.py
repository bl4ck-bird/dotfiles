from contextlib import redirect_stderr, redirect_stdout
import io
import os
from unittest.mock import patch

from support import RecordCase
from harness_records.cli import main
from harness_records.files import MAX_BYTES


class EvidenceIoTests(RecordCase):
    def put(self, source):
        destination = "work/" + self.work_id + "/evidence/imported.txt"
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = main(["--root", str(self.store.files.root), "put-evidence", "--source", str(source), "--path", destination])
        return code, destination

    def test_static_symlink_and_overlarge_file_are_not_published(self):
        source = self.root / "source.txt"
        source.symlink_to(self.root / "outside.txt")
        (self.root / "outside.txt").write_text("dummy outside content")
        code, destination = self.put(source)
        self.assertEqual(code, 2)
        self.assertFalse(self.store.files.exists(destination))
        source.unlink()
        with source.open("wb") as stream:
            stream.truncate(MAX_BYTES + 1)
        code, destination = self.put(source)
        self.assertEqual(code, 2)
        self.assertFalse(self.store.files.exists(destination))

    def test_source_replaced_by_symlink_before_open_does_not_follow_target(self):
        source = self.root / "source.txt"
        source.write_text("selected content")
        outside = self.root / "outside.txt"
        outside.write_text("dummy unselected content")
        original_open = os.open

        def exchange_before_open(path, flags, *args, **kwargs):
            if path == source.name and not flags & os.O_DIRECTORY:
                source.unlink()
                source.symlink_to(outside)
            return original_open(path, flags, *args, **kwargs)

        with patch("harness_records.capture.os.open", side_effect=exchange_before_open):
            code, destination = self.put(source)
        self.assertEqual(code, 2)
        self.assertFalse(self.store.files.exists(destination))

    def test_explicit_regular_evidence_is_preserved_exactly(self):
        source = self.root / "source.txt"
        source.write_bytes(b"actual observed output\n")
        code, destination = self.put(source)
        self.assertEqual(code, 0)
        self.assertEqual(self.store.files.read(destination), b"actual observed output\n")

    def test_secret_candidate_in_absolute_or_resolved_parent_is_rejected(self):
        candidate = self.root / "credentials"
        candidate.mkdir()
        source = candidate / "settings.txt"
        source.write_text("dummy fixture content")
        code, destination = self.put(source)
        self.assertEqual(code, 2)
        self.assertFalse(self.store.files.exists(destination))

        alias = self.root / "ordinary-parent"
        alias.symlink_to(candidate, target_is_directory=True)
        code, destination = self.put(alias / "settings.txt")
        self.assertEqual(code, 2)
        self.assertFalse(self.store.files.exists(destination))

    def test_relative_regular_evidence_is_preserved(self):
        source = self.root / "relative-source.txt"
        source.write_bytes(b"relative observed output\n")
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)
        code, destination = self.put(source.name)
        self.assertEqual(code, 0)
        self.assertEqual(self.store.files.read(destination), b"relative observed output\n")
