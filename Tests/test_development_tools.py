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
VERIFY_SPEC = importlib.util.spec_from_file_location("verify_app", ROOT / "Scripts/verify-app.py")
VERIFY = importlib.util.module_from_spec(VERIFY_SPEC)
VERIFY_SPEC.loader.exec_module(VERIFY)


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
        self.assertEqual(info["LSMinimumSystemVersion"], "26.2")

    def test_invalid_measurement_duration_is_rejected(self):
        result = subprocess.run(
            ["/usr/bin/python3", str(ROOT / "Scripts/measure-baseline.py"), "--seconds", "0"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("between 1 and 300", result.stderr)

    def test_deployment_contract_accepts_matching_artifacts(self):
        info = {"LSMinimumSystemVersion": "26.2", "CFBundleExecutable": "UniversalAIStudio", "CFBundlePackageType": "APPL"}
        manifest = {"platforms": [{"platformName": "macos", "version": "26.2"}]}
        VERIFY.validate_metadata(info, manifest, "arm64", "    platform MACOS\n    minos 26.2.0\n")

    def test_deployment_contract_rejects_incompatible_artifacts(self):
        valid = {"LSMinimumSystemVersion": "26.2", "CFBundleExecutable": "UniversalAIStudio", "CFBundlePackageType": "APPL"}
        manifest = {"platforms": [{"platformName": "macos", "version": "26.2"}]}
        for minimum in ("14.0", "15.0", "26.0", "26.1", "27.0"):
            with self.subTest(manifest=minimum), self.assertRaises(ValueError):
                VERIFY.validate_metadata(valid, {"platforms": [{"platformName": "macos", "version": minimum}]}, "arm64", "platform MACOS\nminos 26.2\n")
            with self.subTest(minimum=minimum), self.assertRaises(ValueError):
                VERIFY.validate_metadata(dict(valid, LSMinimumSystemVersion=minimum), manifest, "arm64", "platform MACOS\nminos 26.2\n")
            with self.subTest(mach_o=minimum), self.assertRaises(ValueError):
                VERIFY.validate_metadata(valid, manifest, "arm64", "platform MACOS\nminos " + minimum + "\n")
        for architectures in ("x86_64", "arm64 x86_64"):
            with self.subTest(architectures=architectures), self.assertRaises(ValueError):
                VERIFY.validate_metadata(valid, manifest, architectures, "platform MACOS\nminos 26.2\n")
        with self.assertRaises(ValueError):
            VERIFY.validate_metadata(valid, manifest, "arm64", "platform IOS\nminos 26.2\n")
        with self.assertRaises(ValueError):
            VERIFY.validate_metadata(valid, {"platforms": []}, "arm64", "platform MACOS\nminos 26.2\n")


if __name__ == "__main__":
    unittest.main()
