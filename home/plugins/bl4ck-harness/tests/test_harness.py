"""기록 도구가 사용자 자료를 보존하고 잘못된 참조를 거부하는지 확인한다."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/harness.py'


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, command, *args):
        return subprocess.run([sys.executable, str(SCRIPT), command, '--root', str(self.root), *args], capture_output=True, text=True)

    def initialize(self):
        result = self.run_tool('init')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_initialize_preserves_ignore_and_current(self):
        (self.root / '.gitignore').write_text('node_modules/', encoding='utf-8')
        self.initialize()
        self.assertEqual((self.root / '.gitignore').read_text(), 'node_modules/\n/.harness/\n')
        current = self.root / '.harness/CURRENT.md'
        current.write_text('# 현재 상태\n\n사용자가 남긴 재개 위치\n', encoding='utf-8')
        self.initialize()
        self.assertIn('사용자가 남긴 재개 위치', current.read_text())
        self.assertEqual((self.root / '.gitignore').read_text().count('/.harness/'), 1)
        self.assertFalse((self.root / '.harness/ROADMAP.md').exists())
        self.assertEqual(self.run_tool('check').returncode, 0)

    def test_foreign_records_are_not_overwritten(self):
        record = self.root / '.harness'
        record.mkdir()
        previous = record / 'CURRENT.md'
        previous.write_text('이전 하네스 기록', encoding='utf-8')
        result = self.run_tool('init')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(previous.read_text(), '이전 하네스 기록')
        self.assertFalse((self.root / '.gitignore').exists())

    def test_disabled_or_invalid_config_is_not_overwritten(self):
        self.initialize()
        path = self.root / '.harness/config.json'
        cases = [dict(plugin='bl4ck-harness', schema_version=1, enabled=False), dict(plugin='bl4ck-harness', schema_version=True, enabled=True), dict(plugin='other', schema_version=1, enabled=True)]
        for value in cases:
            original = json.dumps(value)
            path.write_text(original)
            self.assertNotEqual(self.run_tool('init').returncode, 0)
            self.assertEqual(path.read_text(), original)

    def test_symlink_records_do_not_touch_external_directory(self):
        with tempfile.TemporaryDirectory() as external:
            (self.root / '.harness').symlink_to(external, target_is_directory=True)
            result = self.run_tool('init')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(Path(external).iterdir()), [])
            self.assertFalse((self.root / '.gitignore').exists())

    def test_snapshot_preserves_target_after_edit_and_does_not_replace_previous(self):
        self.initialize()
        change = self.root / '.harness/changes/folder-import'
        change.mkdir(parents=True)
        spec = change / 'spec.md'
        spec.write_text('# 명세\n\n중복 가져오기는 한 번만 반영한다.\n', encoding='utf-8')
        original = spec.read_bytes()
        result = self.run_tool('snapshot', '--change', 'folder-import', '--files', 'changes/folder-import/spec.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        first = next((change / 'snapshots').iterdir())
        saved = first / 'files/changes/folder-import/spec.md'
        spec.write_text('# 변경된 명세\n', encoding='utf-8')
        self.assertEqual(saved.read_bytes(), original)
        metadata = json.loads((first / 'manifest.json').read_text())
        self.assertEqual(metadata['files'][0]['sha256'], hashlib.sha256(original).hexdigest())
        second = self.run_tool('snapshot', '--change', 'folder-import', '--files', 'changes/folder-import/spec.md')
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(len(list((change / 'snapshots').iterdir())), 2)

    def test_snapshot_rejects_traversal_and_symlink(self):
        self.initialize()
        change = self.root / '.harness/changes/example'
        change.mkdir(parents=True)
        outside = self.root / 'private.md'
        outside.write_text('읽지 않아야 하는 내용', encoding='utf-8')
        (change / 'linked.md').symlink_to(outside)
        for value in ['../private.md', 'changes/example/linked.md', str(outside)]:
            result = self.run_tool('snapshot', '--change', 'example', '--files', value)
            self.assertNotEqual(result.returncode, 0)
        self.assertFalse((change / 'snapshots').exists())

    def test_check_finds_missing_document_reference(self):
        self.initialize()
        current = self.root / '.harness/CURRENT.md'
        current.write_text('# 현재 상태\n\n[현재 명세](changes/missing/spec.md)\n', encoding='utf-8')
        self.assertNotEqual(self.run_tool('check').returncode, 0)
        target = self.root / '.harness/changes/missing/spec.md'
        target.parent.mkdir(parents=True)
        target.write_text('# 명세\n', encoding='utf-8')
        self.assertEqual(self.run_tool('check').returncode, 0)

    def test_snapshot_refuses_records_without_ignore_rule(self):
        self.initialize()
        change = self.root / '.harness/changes/example'
        change.mkdir(parents=True)
        (change / 'spec.md').write_text('# 명세\n', encoding='utf-8')
        (self.root / '.gitignore').write_text('node_modules/\n')
        result = self.run_tool('snapshot', '--change', 'example', '--files', 'changes/example/spec.md')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((change / 'snapshots').exists())

    @unittest.skipUnless(shutil.which('git'), 'Git이 설치되지 않았습니다.')
    def test_snapshot_refuses_force_tracked_records(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.initialize()
        change = self.root / '.harness/changes/example'
        change.mkdir(parents=True)
        (change / 'spec.md').write_text('# 명세\n', encoding='utf-8')
        subprocess.run(['git', '-C', str(self.root), 'add', '-f', '.harness/changes/example/spec.md'], check=True)
        result = self.run_tool('snapshot', '--change', 'example', '--files', 'changes/example/spec.md')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((change / 'snapshots').exists())

    @unittest.skipUnless(shutil.which('git'), 'Git이 설치되지 않았습니다.')
    def test_negated_ignore_is_repaired_before_writing_and_rejected_afterward(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        ignore = self.root / '.gitignore'
        original = '/.harness/\n!/.harness/\n'
        ignore.write_text(original)
        self.initialize()
        self.assertEqual(ignore.read_text(), original + '/.harness/\n')
        actual = subprocess.run(['git', '-C', str(self.root), 'check-ignore', '--quiet', '.harness/config.json'])
        self.assertEqual(actual.returncode, 0)
        self.assertEqual(self.run_tool('check').returncode, 0)
        ignore.write_text(original)
        self.assertNotEqual(self.run_tool('check').returncode, 0)

    @unittest.skipUnless(shutil.which('git'), 'Git이 설치되지 않았습니다.')
    def test_tracked_records_are_preserved_and_rejected(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        record = self.root / '.harness'
        record.mkdir()
        tracked = record / 'previous.md'
        tracked.write_text('추적 중인 자료', encoding='utf-8')
        subprocess.run(['git', '-C', str(self.root), 'add', '.harness/previous.md'], check=True)
        self.assertNotEqual(self.run_tool('init').returncode, 0)
        self.assertEqual(tracked.read_text(), '추적 중인 자료')
        self.assertFalse((self.root / '.harness/config.json').exists())


if __name__ == '__main__':
    unittest.main()
