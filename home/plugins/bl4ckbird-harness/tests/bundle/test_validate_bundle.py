import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest


BUNDLE_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = BUNDLE_ROOT / "scripts" / "validate_bundle.py"
SPEC = importlib.util.spec_from_file_location("validate_bundle", VALIDATOR_PATH)
validate_bundle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_bundle)


class BundleRuntimeValidationTests(unittest.TestCase):
    def copy_bundle(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        bundle = Path(directory.name) / "bl4ckbird-harness"
        shutil.copytree(BUNDLE_ROOT, bundle)
        return bundle

    def test_accepts_complete_bundle(self):
        self.assertEqual(validate_bundle.validate(BUNDLE_ROOT), [])

    def test_normal_bundle_validation_does_not_write_files(self):
        before = self.file_bytes(BUNDLE_ROOT)
        self.assertEqual(validate_bundle.validate(BUNDLE_ROOT), [])
        self.assertEqual(self.file_bytes(BUNDLE_ROOT), before)

    def test_rejects_missing_records_entrypoint(self):
        bundle = self.copy_bundle()
        (bundle / "scripts" / "records.py").unlink()
        self.assertTrue(any("records.py" in error for error in validate_bundle.validate(bundle)))

    def test_rejects_missing_runtime_module(self):
        bundle = self.copy_bundle()
        (bundle / "scripts" / "harness_records" / "recovery.py").unlink()
        self.assertTrue(any("scripts/harness_records/recovery.py" in error
                            for error in validate_bundle.validate(bundle)))

    def test_rejects_missing_runtime_package_initializer(self):
        bundle = self.copy_bundle()
        (bundle / "scripts" / "harness_records" / "__init__.py").unlink()
        self.assertTrue(any("harness_records/__init__.py" in error for error in validate_bundle.validate(bundle)))

    def test_rejects_unloadable_runtime_module(self):
        bundle = self.copy_bundle()
        (bundle / "scripts" / "harness_records" / "errors.py").write_text("not valid python +\n")
        self.assertTrue(any("Cannot load runtime modules" in error for error in validate_bundle.validate(bundle)))

    def test_rejects_runtime_import_timeout(self):
        bundle = self.copy_bundle()
        (bundle / "scripts" / "harness_records" / "errors.py").write_text("while True:\n    pass\n")
        self.assertTrue(any("Timed out loading runtime modules" == error
                            for error in validate_bundle.validate(bundle)))

    def test_ignores_ambient_pythonpath_import_fallback(self):
        bundle = self.copy_bundle()
        errors = bundle / "scripts" / "harness_records" / "errors.py"
        errors.write_text(errors.read_text() + "\nimport ambient_only\n")
        ambient = bundle.parent / "ambient"
        ambient.mkdir()
        (ambient / "ambient_only.py").write_text("VALUE = 'ambient'\n")
        previous = os.environ.get("PYTHONPATH")
        os.environ["PYTHONPATH"] = str(ambient)
        self.addCleanup(self.restore_pythonpath, previous)
        self.assertTrue(any("Cannot load runtime modules" in error
                            for error in validate_bundle.validate(bundle)))
        unisolated = self.load_validator_without_isolation(bundle.parent)
        self.assertEqual(unisolated.validate(bundle), [])

    @staticmethod
    def file_bytes(root):
        return {
            path.relative_to(root): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    @staticmethod
    def load_validator_without_isolation(directory):
        path = directory / "validate_bundle_without_isolation.py"
        source = VALIDATOR_PATH.read_text().replace(
            '[sys.executable, "-B", "-I", "-c"',
            '[sys.executable, "-B", "-c"',
        )
        path.write_text(source)
        spec = importlib.util.spec_from_file_location("validate_bundle_without_isolation", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def restore_pythonpath(previous):
        if previous is None:
            os.environ.pop("PYTHONPATH", None)
        else:
            os.environ["PYTHONPATH"] = previous


if __name__ == "__main__":
    unittest.main()
