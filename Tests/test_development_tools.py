"""Regression checks for the development scripts; no inference is implemented."""

import importlib.util
from pathlib import Path
import plistlib
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("baseline", ROOT / "Scripts/measure-baseline.py")
BASELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASELINE)


class DevelopmentToolsTests(unittest.TestCase):
    def test_cpu_time_formats(self):
        self.assertAlmostEqual(BASELINE.cpu_seconds("0:01.23"), 1.23)
        self.assertAlmostEqual(BASELINE.cpu_seconds("1:02:03.45"), 3723.45)
        with self.assertRaises(ValueError):
            BASELINE.cpu_seconds("invalid")

    def test_invalid_build_configuration_is_rejected(self):
        result = subprocess.run(
            ["bash", str(ROOT / "Scripts/build-app.sh"), "invalid"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)

    def test_bundle_metadata(self):
        with (ROOT / "Resources/Info.plist").open("rb") as stream:
            info = plistlib.load(stream)
        self.assertEqual(info["CFBundleExecutable"], "UniversalAIStudio")
        self.assertEqual(info["CFBundlePackageType"], "APPL")
        self.assertEqual(info["LSMinimumSystemVersion"], "14.0")

    def test_invalid_measurement_duration_is_rejected(self):
        result = subprocess.run(
            ["/usr/bin/python3", str(ROOT / "Scripts/measure-baseline.py"), "--seconds", "0"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("between 1 and 300", result.stderr)


if __name__ == "__main__":
    unittest.main()
