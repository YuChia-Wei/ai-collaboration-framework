#!/usr/bin/env python3
"""GWT contracts for the WSL-native v0.15 validation launcher."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
LAUNCHER_PATH = ROOT / ".ai/scripts/run-v015-package-validation-wsl.py"
TEST_TEMP_ROOT = ROOT / ".dev/ai-context/local/validation/test-v015-wsl-native-launcher"
TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
SPEC = importlib.util.spec_from_file_location("v015_wsl_native_launcher", LAUNCHER_PATH)
assert SPEC and SPEC.loader
LAUNCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAUNCHER)


def result_payload(*, subject: str = "a" * 40, lane: str = "long", filesystem: str = "ext2/ext3") -> bytes:
    buffer = io.BytesIO()
    files = {
        "output/terminal.json": b"{}\n",
        "lane.stdout": b'{"outcome":"passed"}\n',
        "lane.stderr": b"",
        "launcher.json": json.dumps(
            {
                "cleanup": "trap-confirmed",
                "filesystem": filesystem,
                "lane": lane,
                "lane_exit": 0,
                "subject_sha": subject,
                "workspace": "linux-native-temp",
            }
        ).encode(),
    }
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        output_directory = tarfile.TarInfo("output")
        output_directory.type = tarfile.DIRTYPE
        archive.addfile(output_directory)
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


class V015WslNativeLauncherGwtTests(unittest.TestCase):
    def test_gwt_001_given_launcher_command_when_rendered_then_no_shared_mount_path_is_used(self) -> None:
        command = LAUNCHER.wsl_command("Ubuntu-24.04", "a" * 40, "long", False, ["--trusted-reference"])

        self.assertEqual("wsl.exe", command[0])
        self.assertNotIn("/mnt/", "\n".join(command))
        self.assertIn('mktemp -d "/tmp/', LAUNCHER.WSL_BOOTSTRAP)
        self.assertNotIn("TMPDIR", LAUNCHER.WSL_BOOTSTRAP)
        self.assertLess(
            LAUNCHER.WSL_BOOTSTRAP.index("stat -f -c %T /tmp"),
            LAUNCHER.WSL_BOOTSTRAP.index("tar -xf -"),
        )
        self.assertIn("git clone --no-checkout", LAUNCHER.WSL_BOOTSTRAP)
        self.assertIn("9p|drvfs", LAUNCHER.WSL_BOOTSTRAP)
        self.assertIn("env -u AI_CONTEXT_TEST_TMP_ROOT", LAUNCHER.WSL_BOOTSTRAP)

    def test_gwt_002_given_result_from_native_temp_when_extracted_then_terminal_and_receipt_are_persisted(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT) as temporary:
            destination = Path(temporary) / "evidence"

            exit_code, stdout, stderr = LAUNCHER.extract_result(
                result_payload(), destination, "a" * 40, "long"
            )

            self.assertEqual(0, exit_code)
            self.assertIn('"outcome":"passed"', stdout)
            self.assertEqual("", stderr)
            self.assertTrue((destination / "terminal.json").is_file())
            receipt = json.loads((destination / "wsl-native-launcher.json").read_text())
            self.assertEqual("linux-native-temp", receipt["workspace"])

    def test_gwt_003_given_shared_filesystem_receipt_when_extracted_then_it_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT) as temporary:
            with self.assertRaisesRegex(LAUNCHER.LauncherError, "result-shared-filesystem"):
                LAUNCHER.extract_result(
                    result_payload(filesystem="9p"), Path(temporary) / "evidence", "a" * 40, "long"
                )

    def test_gwt_004_given_path_traversal_member_when_extracted_then_it_fails_before_write(self) -> None:
        for unsafe_name in ("../escape", "output/..\\..\\escape", "output/file:stream"):
            with self.subTest(unsafe_name=unsafe_name):
                buffer = io.BytesIO()
                with tarfile.open(fileobj=buffer, mode="w") as archive:
                    info = tarfile.TarInfo(unsafe_name)
                    info.size = 1
                    archive.addfile(info, io.BytesIO(b"x"))
                with tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT) as temporary:
                    with self.assertRaisesRegex(LAUNCHER.LauncherError, "unsafe-result-member"):
                        LAUNCHER.extract_result(
                            buffer.getvalue(), Path(temporary) / "evidence", "a" * 40, "long"
                        )

    def test_gwt_005_given_existing_output_when_validated_then_it_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory(dir=TEST_TEMP_ROOT) as temporary:
            root = Path(temporary)
            output = root / ".dev/ai-context/local/validation/run"
            output.mkdir(parents=True)
            with self.assertRaisesRegex(LAUNCHER.LauncherError, "output-already-exists"):
                with mock.patch.object(LAUNCHER, "run_git") as run_git:
                    run_git.return_value.returncode = 0
                    LAUNCHER.validate_output(root, output)


if __name__ == "__main__":
    unittest.main()
