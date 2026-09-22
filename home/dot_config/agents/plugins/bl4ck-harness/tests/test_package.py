"""소스와 버전별 설치 캐시에서 같은 패키지를 검사한다."""

from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_source_and_installed_layout_accept_same_package(self):
        manifest = json.loads((SOURCE / '.codex-plugin/plugin.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for relative in (Path(manifest['name']), Path('cache') / manifest['name'] / manifest['version']):
                with self.subTest(layout=str(relative)):
                    root = base / relative
                    shutil.copytree(SOURCE, root, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
                    result = subprocess.run([sys.executable, '-B', str(root / 'scripts/validate.py')], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    path = root / '.codex-plugin/plugin.json'
                    broken = dict(manifest, name='another-plugin')
                    path.write_text(json.dumps(broken))
                    result = subprocess.run([sys.executable, '-B', str(root / 'scripts/validate.py')], capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
