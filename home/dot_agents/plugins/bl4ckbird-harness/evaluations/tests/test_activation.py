import tempfile
import unittest
from pathlib import Path

from harness_eval.evidence import mechanical_checks, snapshot
from harness_eval.scenarios import SCENARIOS


class ActivationTests(unittest.TestCase):
    def test_config_only_activation_cannot_hide_among_work_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, data in SCENARIOS['unresolved-requirement']['files'].items():
                (root / name).write_text(data)
            before = snapshot(root)
            (root / '.harness').mkdir()
            (root / '.harness' / 'proposal.md').write_text('휴면 계정 정책 검토 중')
            proposal = mechanical_checks('unresolved-requirement', before, snapshot(root))
            self.assertTrue(all(check['status'] == 'satisfied' for check in proposal))
            (root / '.harness' / 'config.toml').write_text('schema_version = 1\nenabled = true\n')
            checks = {check['id']: check['status'] for check in mechanical_checks('unresolved-requirement', before, snapshot(root))}
            self.assertEqual(checks['no-dependent-implementation'], 'satisfied')
            self.assertEqual(checks['no-project-activation'], 'failed')


if __name__ == '__main__':
    unittest.main()
