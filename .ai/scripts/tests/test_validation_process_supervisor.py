#!/usr/bin/env python3
"""Focused GWT tests for complete-tree validation supervision."""

from __future__ import annotations

import contextlib
import ctypes
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from collections.abc import Sequence
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / ".ai/scripts"
sys.path.insert(0, str(SCRIPTS))

import validation_process_supervisor as supervisor  # noqa: E402


UNSUPPORTED_POSIX = os.name != "nt" and not sys.platform.startswith("linux")


class ValidationProcessSupervisorGwtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="validation-supervisor-")
        self.work = Path(self.temporary.name)
        self._artifact_index = 0

    def tearDown(self) -> None:
        # cleanup() is intentionally strict: retained process handles or ACL
        # failures remain visible test failures.
        self.temporary.cleanup()

    def supervise(
        self,
        argv: list[str],
        *,
        timeout_seconds: float = 3.0,
        grace_seconds: float = 0.5,
    ) -> tuple[dict[str, object], Path, Path]:
        self._artifact_index += 1
        log_path = self.work / f"command-{self._artifact_index}.log"
        result_path = self.work / f"command-{self._artifact_index}.json"
        result = supervisor.supervise_command(
            argv,
            cwd=self.work,
            cwd_ref="fixture-repo",
            log_path=log_path,
            result_path=result_path,
            timeout_seconds=timeout_seconds,
            termination_grace_seconds=grace_seconds,
        )
        return result, log_path, result_path

    def run_linux_protocol_fault(
        self,
        *,
        argv: list[str] | None = None,
        bootstrap_code: str | None = None,
        config_write_error: BaseException | None = None,
    ) -> tuple[supervisor._RunOutcome, float]:  # noqa: SLF001
        self._artifact_index += 1
        spawned: list[subprocess.Popen[bytes]] = []
        owned_descriptors: list[int] = []
        real_popen = subprocess.Popen
        real_pipe = os.pipe

        def capture_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
            process = real_popen(*args, **kwargs)  # type: ignore[arg-type]
            spawned.append(process)
            return process

        def capture_pipe() -> tuple[int, int]:
            descriptors = real_pipe()
            owned_descriptors.extend(descriptors)
            return descriptors

        log_path = self.work / f"protocol-fault-{self._artifact_index}.log"
        started = time.monotonic()
        with log_path.open("wb", buffering=0) as log_handle:
            with contextlib.ExitStack() as stack:
                stack.enter_context(
                    mock.patch.object(
                        supervisor.subprocess,
                        "Popen",
                        side_effect=capture_popen,
                    )
                )
                stack.enter_context(
                    mock.patch.object(
                        supervisor.os,
                        "pipe",
                        side_effect=capture_pipe,
                    )
                )
                if bootstrap_code is not None:
                    stack.enter_context(
                        mock.patch.object(
                            supervisor,
                            "_LINUX_MONITOR_BOOTSTRAP_CODE",
                            bootstrap_code,
                        )
                    )
                if config_write_error is not None:
                    stack.enter_context(
                        mock.patch.object(
                            supervisor,
                            "_write_monitor_config",
                            side_effect=config_write_error,
                        )
                    )
                outcome = supervisor._run_linux_monitor(  # noqa: SLF001
                    argv or [sys.executable, "-c", "raise SystemExit(0)"],
                    cwd=self.work,
                    log_handle=log_handle,
                    timeout_seconds=0.2,
                    termination_grace_seconds=0.1,
                    cancellation=threading.Event(),
                )
        elapsed = time.monotonic() - started

        self.assertTrue(owned_descriptors)
        for descriptor in owned_descriptors:
            with self.assertRaises(OSError):
                os.fstat(descriptor)
        self.assertTrue(spawned)
        for process in spawned:
            self.assertIsNotNone(process.poll(), "helper was not reaped")
        return outcome, elapsed

    def write_tree_fixture(self) -> tuple[Path, Path, Path]:
        ready_path = self.work / "grandchild.ready"
        fire_path = self.work / "grandchild.fire"
        delayed_path = self.work / "grandchild.delayed"
        (self.work / "grandchild.py").write_text(
            """from pathlib import Path
import os
import sys
import time

ready = Path(sys.argv[1])
fire = Path(sys.argv[2])
delayed = Path(sys.argv[3])
ready.write_text(str(os.getpid()), encoding="ascii")
print("grandchild-ready", flush=True)
while not fire.exists():
    time.sleep(0.01)
delayed.write_text("descendant-survived", encoding="utf-8")
while True:
    time.sleep(0.05)
""",
            encoding="utf-8",
        )
        (self.work / "root.py").write_text(
            """from pathlib import Path
import subprocess
import sys
import time

ready = Path(sys.argv[1])
subprocess.Popen([sys.executable, "grandchild.py", *sys.argv[1:]])
deadline = time.monotonic() + 5.0
while not ready.exists():
    if time.monotonic() >= deadline:
        raise RuntimeError("grandchild did not become ready")
    time.sleep(0.01)
print("root-observed-ready", flush=True)
if sys.argv[4] == "exit":
    raise SystemExit(0)
while True:
    time.sleep(0.05)
""",
            encoding="utf-8",
        )
        return ready_path, fire_path, delayed_path

    def write_detached_tree_fixture(self) -> tuple[Path, Path, Path]:
        ready_path = self.work / "detached.ready"
        fire_path = self.work / "detached.fire"
        delayed_path = self.work / "detached.delayed"
        (self.work / "detached_writer.py").write_text(
            """from pathlib import Path
import os
import sys
import time

ready = Path(sys.argv[1])
fire = Path(sys.argv[2])
delayed = Path(sys.argv[3])
ready.write_text(str(os.getpid()), encoding="ascii")
print("detached-ready", flush=True)
while not fire.exists():
    time.sleep(0.01)
delayed.write_text("detached-survived", encoding="utf-8")
while True:
    time.sleep(0.05)
""",
            encoding="utf-8",
        )
        (self.work / "detaching_root.py").write_text(
            """from pathlib import Path
import subprocess
import sys
import time

ready = Path(sys.argv[1])
subprocess.Popen(
    [sys.executable, "detached_writer.py", *sys.argv[1:]],
    start_new_session=True,
)
deadline = time.monotonic() + 5.0
while not ready.exists():
    if time.monotonic() >= deadline:
        raise RuntimeError("detached writer did not become ready")
    time.sleep(0.01)
print("root-observed-detached", flush=True)
raise SystemExit(0)
""",
            encoding="utf-8",
        )
        return ready_path, fire_path, delayed_path

    def assert_process_stopped(self, process_id: int, timeout_seconds: float = 1.0) -> None:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if not self.process_is_active(process_id):
                return
            time.sleep(0.01)
        self.assertFalse(self.process_is_active(process_id), f"process {process_id} remains active")

    @staticmethod
    def process_is_active(process_id: int) -> bool:
        if os.name != "nt":
            try:
                os.kill(process_id, 0)
            except ProcessLookupError:
                return False
            except PermissionError:
                return True
            return True

        from ctypes import wintypes

        process_query_limited_information = 0x1000
        still_active = 259
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel32.GetExitCodeProcess.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(
            process_query_limited_information,
            False,
            process_id,
        )
        if not handle:
            return False
        try:
            exit_code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == still_active
        finally:
            kernel32.CloseHandle(handle)

    @unittest.skipIf(UNSUPPORTED_POSIX, "complete non-Linux POSIX containment unavailable")
    def test_gwt_001_given_zero_and_nonzero_commands_when_completed_then_safe_receipts_bind_exact_argv_and_sealed_logs(self) -> None:
        exit_command = self.work / "exit_command.py"
        exit_command.write_text(
            """import sys
print(f"stdout-{sys.argv[1]}", flush=True)
print(f"stderr-{sys.argv[1]}", file=sys.stderr, flush=True)
raise SystemExit(int(sys.argv[1]))
""",
            encoding="utf-8",
        )

        for exit_code in (0, 7):
            with self.subTest(exit_code=exit_code):
                argv = [sys.executable, str(exit_command.resolve()), str(exit_code)]
                receipt, log_path, result_path = self.supervise(argv)
                persisted = json.loads(result_path.read_text(encoding="utf-8"))
                log_bytes = log_path.read_bytes()

                self.assertEqual(receipt, persisted)
                self.assertEqual(supervisor.SCHEMA, receipt["schema"])
                self.assertEqual("completed", receipt["status"])
                self.assertEqual(exit_code, receipt["child_exit_code"])
                safe_argv = [
                    f"<absolute-path>/{Path(sys.executable).name}",
                    "./exit_command.py",
                    str(exit_code),
                ]
                self.assertEqual(safe_argv, receipt["argv"])
                canonical_safe_argv = json.dumps(
                    safe_argv,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
                self.assertEqual(
                    hashlib.sha256(canonical_safe_argv).hexdigest(),
                    receipt["argv_sha256"],
                )
                canonical_effective_argv = json.dumps(
                    argv,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
                self.assertEqual(
                    hashlib.sha256(canonical_effective_argv).hexdigest(),
                    receipt["effective_argv_sha256"],
                )
                self.assertEqual("fixture-repo", receipt["cwd_ref"])
                self.assertTrue(receipt["termination"]["tree_empty"])
                self.assertTrue(receipt["log"]["sealed"])
                self.assertEqual(hashlib.sha256(log_bytes).hexdigest(), receipt["log"]["sha256"])
                self.assertEqual(len(log_bytes), receipt["log"]["bytes"])
                self.assertEqual(2, receipt["log"]["lines"])
                serialized = result_path.read_text(encoding="utf-8")
                self.assertNotIn(str(self.work), serialized)
                self.assertNotIn(sys.executable, serialized)

    @unittest.skipIf(UNSUPPORTED_POSIX, "complete non-Linux POSIX containment unavailable")
    def test_gwt_002_given_child_and_grandchild_when_timeout_fires_then_tree_is_dead_before_log_is_sealed(self) -> None:
        ready_path, fire_path, delayed_path = self.write_tree_fixture()
        argv = [
            sys.executable,
            "root.py",
            ready_path.name,
            fire_path.name,
            delayed_path.name,
            "hold",
        ]

        receipt, log_path, _ = self.supervise(
            argv,
            timeout_seconds=1.0,
            grace_seconds=0.4,
        )

        self.assertEqual("timed-out", receipt["status"], receipt)
        self.assertTrue(ready_path.exists(), "fixture did not prove grandchild launch")
        grandchild_process_id = int(ready_path.read_text(encoding="ascii"))
        self.assertTrue(receipt["termination"]["tree_empty"])
        self.assertTrue(receipt["log"]["sealed"])
        sealed_bytes = log_path.read_bytes()
        sealed_digest = receipt["log"]["sha256"]

        fire_path.write_text("write-now", encoding="ascii")
        self.assert_process_stopped(grandchild_process_id)
        deadline = time.monotonic() + 0.25
        while time.monotonic() < deadline and not delayed_path.exists():
            time.sleep(0.01)

        self.assertFalse(delayed_path.exists())
        self.assertEqual(sealed_bytes, log_path.read_bytes())
        self.assertEqual(sealed_digest, hashlib.sha256(log_path.read_bytes()).hexdigest())

    @unittest.skipIf(UNSUPPORTED_POSIX, "complete non-Linux POSIX containment unavailable")
    def test_gwt_003_given_root_exits_with_background_descendant_when_supervised_then_cleanup_is_visible_and_nonpassing(self) -> None:
        ready_path, fire_path, delayed_path = self.write_tree_fixture()
        argv = [
            sys.executable,
            "root.py",
            ready_path.name,
            fire_path.name,
            delayed_path.name,
            "exit",
        ]

        receipt, log_path, _ = self.supervise(argv, grace_seconds=0.4)

        self.assertEqual("cleanup-failed", receipt["status"])
        self.assertEqual(0, receipt["child_exit_code"])
        self.assertEqual("orphan-descendant", receipt["termination"]["trigger"])
        self.assertTrue(receipt["termination"]["tree_empty"])
        self.assertTrue(receipt["log"]["sealed"])
        grandchild_process_id = int(ready_path.read_text(encoding="ascii"))
        sealed_bytes = log_path.read_bytes()

        fire_path.write_text("write-now", encoding="ascii")
        self.assert_process_stopped(grandchild_process_id)
        deadline = time.monotonic() + 0.25
        while time.monotonic() < deadline and not delayed_path.exists():
            time.sleep(0.01)
        self.assertFalse(delayed_path.exists())
        self.assertEqual(sealed_bytes, log_path.read_bytes())

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux subreaper/procfs contract")
    def test_gwt_004_given_setsid_descendant_when_root_exits_then_subreaper_finds_kills_and_reaps_it(self) -> None:
        ready_path, fire_path, delayed_path = self.write_detached_tree_fixture()
        receipt, log_path, _ = self.supervise(
            [
                sys.executable,
                "detaching_root.py",
                ready_path.name,
                fire_path.name,
                delayed_path.name,
            ],
            grace_seconds=0.5,
        )

        self.assertEqual("cleanup-failed", receipt["status"], receipt)
        self.assertEqual("orphan-descendant", receipt["termination"]["trigger"])
        self.assertTrue(receipt["termination"]["tree_empty"])
        containment = receipt["termination"]["containment"]
        self.assertTrue(containment["subreaper"])
        self.assertTrue(containment["procfs"])
        self.assertGreaterEqual(containment["observed_detached_descendants"], 1)
        self.assertGreaterEqual(containment["observed_adopted_descendants"], 1)
        self.assertEqual(0, containment["remaining_descendants"])
        self.assertTrue(receipt["log"]["sealed"])
        sealed_bytes = log_path.read_bytes()
        detached_process_id = int(ready_path.read_text(encoding="ascii"))

        fire_path.write_text("write-now", encoding="ascii")
        self.assert_process_stopped(detached_process_id)
        deadline = time.monotonic() + 0.25
        while time.monotonic() < deadline and not delayed_path.exists():
            time.sleep(0.01)
        self.assertFalse(delayed_path.exists())
        self.assertEqual(sealed_bytes, log_path.read_bytes())

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux catchable signal contract")
    def test_gwt_005_given_catchable_cancellation_when_received_then_tree_is_stopped_and_receipt_is_cancelled(self) -> None:
        ready_path = self.work / "cancel.ready"
        (self.work / "cancel_command.py").write_text(
            """from pathlib import Path
import os
import sys
import time
Path(sys.argv[1]).write_text(str(os.getpid()), encoding="ascii")
while True:
    time.sleep(0.05)
""",
            encoding="utf-8",
        )
        sender_errors: list[str] = []

        def send_cancellation_after_ready() -> None:
            deadline = time.monotonic() + 3.0
            while time.monotonic() < deadline:
                if ready_path.exists():
                    os.kill(os.getpid(), signal.SIGTERM)
                    return
                time.sleep(0.01)
            sender_errors.append("fixture never became ready")

        sender = threading.Thread(target=send_cancellation_after_ready, daemon=True)
        sender.start()
        receipt, _, _ = self.supervise(
            [sys.executable, "cancel_command.py", ready_path.name],
            timeout_seconds=5.0,
            grace_seconds=0.4,
        )
        sender.join(timeout=1.0)

        self.assertEqual([], sender_errors)
        self.assertEqual("cancelled", receipt["status"], receipt)
        self.assertEqual("cancelled", receipt["termination"]["trigger"])
        self.assertTrue(receipt["termination"]["tree_empty"])
        self.assertTrue(receipt["log"]["sealed"])

    def test_gwt_006_given_windows_blocking_bootstrap_when_released_then_assignment_precedes_argv_and_failure_never_releases(self) -> None:
        events: list[str] = []

        class FakeJob:
            def __init__(self, *, fail: bool = False) -> None:
                self.fail = fail

            def assign(self, _process_id: int) -> None:
                events.append("assign")
                if self.fail:
                    raise OSError("fixture assignment failure")

        class FakeStdin:
            def __init__(self) -> None:
                self.closed = False
                self.payloads: list[bytes] = []

            def write(self, payload: bytes) -> int:
                events.append("release")
                self.payloads.append(payload)
                return len(payload)

            def flush(self) -> None:
                events.append("flush")

            def close(self) -> None:
                self.closed = True

        class FakeProcess:
            pid = 123

            def __init__(self) -> None:
                self.stdin = FakeStdin()

        process = FakeProcess()
        gate = supervisor._WindowsBootstrapGate(process)  # type: ignore[arg-type]  # noqa: SLF001
        with self.assertRaisesRegex(RuntimeError, "not assigned"):
            gate.release(["must-not-start"])
        gate.assign(FakeJob())
        gate.release(["validator", "--exact"])
        self.assertEqual(["assign", "release", "flush"], events)
        self.assertEqual(
            {"argv": ["validator", "--exact"]},
            json.loads(process.stdin.payloads[0]),
        )

        events.clear()
        blocked_process = FakeProcess()
        blocked_gate = supervisor._WindowsBootstrapGate(  # type: ignore[arg-type]  # noqa: SLF001
            blocked_process,
        )
        with self.assertRaises(OSError):
            blocked_gate.assign(FakeJob(fail=True))
        with self.assertRaisesRegex(RuntimeError, "not assigned"):
            blocked_gate.release(["must-not-start"])
        self.assertEqual(["assign"], events)
        self.assertEqual([], blocked_process.stdin.payloads)

        marker = self.work / "bootstrap-target.marker"
        (self.work / "bootstrap_target.py").write_text(
            "from pathlib import Path; Path('bootstrap-target.marker').write_text('ran', encoding='ascii')\n",
            encoding="utf-8",
        )
        bootstrap = subprocess.Popen(
            [sys.executable, "-I", "-c", supervisor._WINDOWS_BOOTSTRAP_CODE],  # noqa: SLF001
            cwd=self.work,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        ready_lines: list[bytes] = []
        ready_seen = threading.Event()

        def read_bootstrap_ready() -> None:
            assert bootstrap.stdout is not None
            ready_lines.append(bootstrap.stdout.readline())
            ready_seen.set()

        reader = threading.Thread(target=read_bootstrap_ready, daemon=True)
        reader.start()
        try:
            self.assertTrue(ready_seen.wait(timeout=1.0), "bootstrap readiness missing")
            self.assertEqual(
                {"event": "awaiting-release"},
                json.loads(ready_lines[0]),
            )
            self.assertFalse(marker.exists(), "target ran before payload release")
            assert bootstrap.stdin is not None
            bootstrap.stdin.write(
                supervisor._windows_bootstrap_payload(  # noqa: SLF001
                    [sys.executable, "bootstrap_target.py"]
                )
            )
            bootstrap.stdin.flush()
            bootstrap.stdin.close()
            self.assertEqual(0, bootstrap.wait(timeout=3.0))
            assert bootstrap.stdout is not None
            remaining_events = [
                json.loads(line)
                for line in bootstrap.stdout.read().splitlines()
                if line
            ]
            self.assertEqual(
                ["launched", "completed"],
                [event["event"] for event in remaining_events],
            )
            self.assertTrue(marker.exists())
        finally:
            if bootstrap.poll() is None:
                bootstrap.terminate()
                try:
                    bootstrap.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    bootstrap.kill()
                    bootstrap.wait(timeout=1.0)
            reader.join(timeout=1.0)
            if bootstrap.stdin is not None and not bootstrap.stdin.closed:
                bootstrap.stdin.close()
            if bootstrap.stdout is not None:
                bootstrap.stdout.close()

    @unittest.skipUnless(os.name == "nt", "Windows Job Object cancellation contract")
    def test_gwt_007_given_injected_windows_cancellation_when_set_then_job_tree_is_terminated_and_proven_empty(self) -> None:
        ready_path = self.work / "windows-cancel.ready"
        log_path = self.work / "windows-cancel.log"
        (self.work / "windows_cancel_command.py").write_text(
            """from pathlib import Path
import os
import sys
import time
Path(sys.argv[1]).write_text(str(os.getpid()), encoding="ascii")
while True:
    time.sleep(0.05)
""",
            encoding="utf-8",
        )
        cancellation = threading.Event()
        sender_errors: list[str] = []

        def cancel_after_ready() -> None:
            deadline = time.monotonic() + 3.0
            while time.monotonic() < deadline:
                if ready_path.exists():
                    cancellation.set()
                    return
                time.sleep(0.01)
            sender_errors.append("fixture never became ready")

        sender = threading.Thread(target=cancel_after_ready, daemon=True)
        sender.start()
        with log_path.open("wb", buffering=0) as log_handle:
            outcome = supervisor._run_windows(  # noqa: SLF001
                [sys.executable, "windows_cancel_command.py", ready_path.name],
                cwd=self.work,
                log_handle=log_handle,
                timeout_seconds=5.0,
                termination_grace_seconds=0.5,
                cancellation=cancellation,
            )
        sender.join(timeout=1.0)

        self.assertEqual([], sender_errors)
        self.assertEqual("cancelled", outcome.status, outcome)
        self.assertEqual("cancelled", outcome.termination["trigger"])
        self.assertTrue(outcome.termination["tree_empty"])
        self.assertEqual(
            "job-signaled-and-active-processes-zero",
            outcome.termination["verification"],
        )
        cancelled_process_id = int(ready_path.read_text(encoding="ascii"))
        self.assert_process_stopped(cancelled_process_id)

    @unittest.skipIf(UNSUPPORTED_POSIX, "complete non-Linux POSIX containment unavailable")
    def test_gwt_008_given_invalid_receipt_invariants_when_checked_then_persistence_contract_rejects_them(self) -> None:
        (self.work / "invariant_command.py").write_text(
            "print('invariant-ok', flush=True)\n",
            encoding="utf-8",
        )
        receipt, _, _ = self.supervise(
            [sys.executable, "invariant_command.py"],
        )

        unproven = json.loads(json.dumps(receipt))
        unproven["status"] = "cleanup-failed"
        unproven["termination"]["tree_empty"] = False
        with self.assertRaisesRegex(ValueError, "unproven tree"):
            supervisor._validate_receipt_invariants(unproven)  # noqa: SLF001

        privacy_leak = json.loads(json.dumps(receipt))
        privacy_leak["argv"][0] = str(Path(sys.executable).resolve())
        with self.assertRaisesRegex(ValueError, "absolute path"):
            supervisor._validate_receipt_invariants(privacy_leak)  # noqa: SLF001

    @unittest.skipUnless(UNSUPPORTED_POSIX, "non-Linux POSIX fail-closed contract")
    def test_gwt_009_given_nonlinux_posix_when_supervision_is_requested_then_command_does_not_start(self) -> None:
        mutation_path = self.work / "must-not-run"
        receipt, _, _ = self.supervise(
            [
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(mutation_path)!r}).write_text('ran')",
            ],
        )

        self.assertEqual("launch-failed", receipt["status"])
        self.assertEqual(
            "posix-complete-containment-unavailable",
            receipt["platform"]["mechanism"],
        )
        self.assertTrue(receipt["termination"]["tree_empty"])
        self.assertFalse(mutation_path.exists())

    @unittest.skipIf(UNSUPPORTED_POSIX, "complete non-Linux POSIX containment unavailable")
    def test_gwt_010_given_attached_and_rooted_absolute_paths_when_persisted_then_all_user_path_fragments_are_redacted(self) -> None:
        (self.work / "privacy_command.py").write_text(
            "import sys; print(len(sys.argv), flush=True)\n",
            encoding="utf-8",
        )
        sensitive_arguments = [
            "-I/home/audit-user/include",
            r"-IC:\Users\audit-user\include",
            r"\Users\audit-user\secret.txt",
            "cmd</home/audit-user/tool",
        ]
        effective_argv = [
            sys.executable,
            "privacy_command.py",
            *sensitive_arguments,
        ]

        receipt, _, result_path = self.supervise(effective_argv)

        self.assertEqual("completed", receipt["status"])
        self.assertEqual(
            [
                f"<absolute-path>/{Path(sys.executable).name}",
                "privacy_command.py",
                "<argument-containing-absolute-path>",
                "<argument-containing-absolute-path>",
                "<absolute-path>/secret.txt",
                "<argument-containing-absolute-path>",
            ],
            receipt["argv"],
        )
        effective_bytes = json.dumps(
            effective_argv,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(effective_bytes).hexdigest(),
            receipt["effective_argv_sha256"],
        )
        serialized = result_path.read_text(encoding="utf-8")
        for private_fragment in ("/home/", r"C:\Users", r"\Users", "audit-user"):
            self.assertNotIn(private_fragment, serialized)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux dedicated monitor contract")
    def test_gwt_011_given_unrelated_child_starts_during_supervision_when_target_times_out_then_unrelated_child_survives(self) -> None:
        target_ready = self.work / "target.ready"
        unrelated_ready = self.work / "unrelated.ready"
        unrelated_fire = self.work / "unrelated.fire"
        unrelated_mutation = self.work / "unrelated.mutation"
        (self.work / "target_hold.py").write_text(
            """from pathlib import Path
import os
import sys
import time
Path(sys.argv[1]).write_text(str(os.getpid()), encoding="ascii")
while True:
    time.sleep(0.05)
""",
            encoding="utf-8",
        )
        (self.work / "unrelated_hold.py").write_text(
            """from pathlib import Path
import os
import sys
import time
ready = Path(sys.argv[1])
fire = Path(sys.argv[2])
mutation = Path(sys.argv[3])
ready.write_text(str(os.getpid()), encoding="ascii")
while not fire.exists():
    time.sleep(0.01)
mutation.write_text("unrelated-survived", encoding="utf-8")
while True:
    time.sleep(0.05)
""",
            encoding="utf-8",
        )
        unrelated: list[subprocess.Popen[bytes]] = []
        launcher_errors: list[str] = []

        def launch_unrelated_after_target_ready() -> None:
            deadline = time.monotonic() + 3.0
            while time.monotonic() < deadline:
                if target_ready.exists():
                    unrelated.append(
                        subprocess.Popen(
                            [
                                sys.executable,
                                "unrelated_hold.py",
                                unrelated_ready.name,
                                unrelated_fire.name,
                                unrelated_mutation.name,
                            ],
                            cwd=self.work,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    )
                    return
                time.sleep(0.01)
            launcher_errors.append("target never became ready")

        launcher = threading.Thread(
            target=launch_unrelated_after_target_ready,
            daemon=True,
        )
        launcher.start()
        try:
            receipt, _, _ = self.supervise(
                [sys.executable, "target_hold.py", target_ready.name],
                timeout_seconds=1.0,
                grace_seconds=0.4,
            )
            launcher.join(timeout=1.0)

            self.assertEqual([], launcher_errors)
            self.assertEqual(1, len(unrelated))
            self.assertEqual("timed-out", receipt["status"], receipt)
            self.assertTrue(receipt["termination"]["tree_empty"])
            self.assertTrue(receipt["termination"]["containment"]["dedicated_monitor"])
            self.assertIsNone(unrelated[0].poll(), "unrelated child was killed")
            self.assertTrue(unrelated_ready.exists())

            unrelated_fire.write_text("mutate-now", encoding="ascii")
            deadline = time.monotonic() + 1.0
            while time.monotonic() < deadline and not unrelated_mutation.exists():
                time.sleep(0.01)
            self.assertTrue(unrelated_mutation.exists())
        finally:
            for process in unrelated:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=1.0)

    @unittest.skipUnless(os.name == "nt", "Windows release-failure contract")
    def test_gwt_012_given_post_assignment_release_failures_when_supervised_then_state_is_inspected_and_never_reported_unreleased(self) -> None:
        (self.work / "release_command.py").write_text(
            "print('release-command', flush=True)\n",
            encoding="utf-8",
        )

        for stage in ("post-write", "post-flush", "post-close"):
            with self.subTest(stage=stage):
                log_path = self.work / f"release-{stage}.log"

                def fail_release(
                    gate: supervisor._WindowsBootstrapGate,  # noqa: SLF001
                    argv: Sequence[str],
                    *,
                    selected_stage: str = stage,
                ) -> None:
                    process = gate.process
                    assert process.stdin is not None
                    payload = supervisor._windows_bootstrap_payload(argv)  # noqa: SLF001
                    process.stdin.write(payload)
                    if selected_stage == "post-write":
                        raise OSError("injected post-write failure")
                    process.stdin.flush()
                    if selected_stage == "post-flush":
                        raise OSError("injected post-flush failure")
                    process.stdin.close()
                    raise OSError("injected post-close failure")

                with log_path.open("wb", buffering=0) as log_handle:
                    outcome = supervisor._run_windows(  # noqa: SLF001
                        [sys.executable, "release_command.py"],
                        cwd=self.work,
                        log_handle=log_handle,
                        timeout_seconds=3.0,
                        termination_grace_seconds=0.5,
                        cancellation=threading.Event(),
                        release_bootstrap=fail_release,
                    )

                self.assertEqual("cleanup-failed", outcome.status, outcome)
                self.assertEqual("bootstrap-release", outcome.error["stage"])
                self.assertEqual("launch-release-failure", outcome.termination["trigger"])
                self.assertTrue(outcome.termination["tree_empty"])
                self.assertNotIn("never-released", outcome.termination["verification"])
                self.assertIn("bootstrap_control_events", outcome.termination)

    @unittest.skipIf(UNSUPPORTED_POSIX, "complete non-Linux POSIX containment unavailable")
    def test_gwt_013_given_atomic_result_replace_fails_when_persisting_then_existing_receipt_is_preserved_and_no_temp_remains(self) -> None:
        log_path = self.work / "atomic-failure.log"
        result_path = self.work / "atomic-failure.json"
        preserved_receipt = b'{"existing":"preserve-exactly"}\n'
        result_path.write_bytes(preserved_receipt)
        with mock.patch.object(
            supervisor.os,
            "replace",
            side_effect=OSError("injected atomic replace failure"),
        ):
            with self.assertRaisesRegex(OSError, "atomic replace failure"):
                supervisor.supervise_command(
                    [sys.executable, "-c", "print('atomic', flush=True)"],
                    cwd=self.work,
                    cwd_ref="fixture-repo",
                    log_path=log_path,
                    result_path=result_path,
                    timeout_seconds=3.0,
                    termination_grace_seconds=0.5,
                )

        self.assertEqual(preserved_receipt, result_path.read_bytes())
        self.assertEqual([], list(self.work.glob(f".{result_path.name}.*.tmp")))

    @unittest.skipIf(UNSUPPORTED_POSIX, "complete non-Linux POSIX containment unavailable")
    def test_gwt_014_given_relative_cwd_when_supervised_then_target_runs_in_callers_resolved_directory(self) -> None:
        observed_cwd = self.work / "observed.cwd"
        (self.work / "record_cwd.py").write_text(
            "from pathlib import Path; Path('observed.cwd').write_text(str(Path.cwd().resolve()), encoding='utf-8')\n",
            encoding="utf-8",
        )
        log_path = self.work / "relative-cwd.log"
        result_path = self.work / "relative-cwd.json"

        with contextlib.chdir(self.work):
            receipt = supervisor.supervise_command(
                [sys.executable, "record_cwd.py"],
                cwd=Path("."),
                cwd_ref="relative-fixture",
                log_path=log_path,
                result_path=result_path,
                timeout_seconds=3.0,
                termination_grace_seconds=0.5,
            )

        self.assertEqual("completed", receipt["status"], receipt)
        self.assertEqual(str(self.work.resolve()), observed_cwd.read_text(encoding="utf-8"))

    def test_gwt_015_given_root_pid_is_reused_with_new_starttime_when_discovered_then_new_identity_is_not_excluded(self) -> None:
        containment = object.__new__(supervisor._LinuxContainment)  # noqa: SLF001
        containment._self_id = 10  # noqa: SLF001
        containment._root_id = 20  # noqa: SLF001
        containment._root_start_time = 100  # noqa: SLF001
        containment._root_group_id = 20  # noqa: SLF001
        containment._baseline_direct_children = set()  # noqa: SLF001
        containment._tracked = {}  # noqa: SLF001
        containment._observed = set()  # noqa: SLF001
        containment._observed_detached = set()  # noqa: SLF001
        containment._observed_adopted = set()  # noqa: SLF001
        reused_identity = supervisor._ProcEntry(  # noqa: SLF001
            process_id=20,
            parent_id=10,
            process_group_id=99,
            state="S",
            start_time=200,
        )

        containment.discover({20: reused_identity})

        self.assertEqual({20: 200}, containment._tracked)  # noqa: SLF001
        self.assertEqual({(20, 200)}, containment._observed_adopted)  # noqa: SLF001

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux monitor protocol contract")
    def test_gwt_016_given_config_write_breaks_when_monitor_waits_then_all_fds_close_and_helper_is_reaped(self) -> None:
        outcome, _ = self.run_linux_protocol_fault(
            config_write_error=BrokenPipeError("injected config pipe failure")
        )

        self.assertEqual("launch-failed", outcome.status, outcome)
        self.assertEqual("monitor-config-write", outcome.error["stage"])
        self.assertTrue(outcome.termination["tree_empty"])

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux monitor protocol contract")
    def test_gwt_017_given_helper_stalls_before_config_ack_when_supervised_then_deadline_closes_fds_and_reaps_helper(self) -> None:
        outcome, elapsed = self.run_linux_protocol_fault(
            bootstrap_code="import time; time.sleep(60)"
        )

        self.assertEqual("launch-failed", outcome.status, outcome)
        self.assertEqual("monitor-config-readiness", outcome.error["stage"])
        self.assertTrue(outcome.termination["tree_empty"])
        self.assertLess(elapsed, 5.0)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux monitor protocol contract")
    def test_gwt_018_given_helper_acks_but_never_reads_config_when_pipe_fills_then_write_deadline_reaps_helper(self) -> None:
        outcome, elapsed = self.run_linux_protocol_fault(
            argv=["x" * 1_000_000],
            bootstrap_code=(
                "import os, sys, time; "
                "os.write(int(sys.argv[3]), b'C'); "
                "time.sleep(60)"
            ),
        )

        self.assertEqual("launch-failed", outcome.status, outcome)
        self.assertEqual("monitor-config-write", outcome.error["stage"])
        self.assertEqual("TimeoutError", outcome.error["type"])
        self.assertTrue(outcome.termination["tree_empty"])
        self.assertLess(elapsed, 5.0)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux launch ACK contract")
    def test_gwt_019_given_parent_cancels_after_helper_ready_when_launch_ack_is_withheld_then_target_never_starts(self) -> None:
        target_marker = self.work / "launch-ack-target.started"
        (self.work / "launch_ack_target.py").write_text(
            "from pathlib import Path; Path('launch-ack-target.started').write_text('started', encoding='ascii')\n",
            encoding="utf-8",
        )
        cancellation = threading.Event()
        helper_ready_observed = threading.Event()

        def cancel_at_launch_ack_boundary() -> None:
            helper_ready_observed.set()
            cancellation.set()

        log_path = self.work / "launch-ack-cancel.log"
        with log_path.open("wb", buffering=0) as log_handle:
            outcome = supervisor._run_linux_monitor(  # noqa: SLF001
                [sys.executable, "launch_ack_target.py"],
                cwd=self.work,
                log_handle=log_handle,
                timeout_seconds=3.0,
                termination_grace_seconds=0.2,
                cancellation=cancellation,
                before_launch_ack=cancel_at_launch_ack_boundary,
            )

        self.assertTrue(helper_ready_observed.is_set())
        self.assertEqual("cancelled", outcome.status, outcome)
        self.assertEqual("cancelled", outcome.termination["trigger"])
        self.assertEqual(
            "launch-ack-withheld-command-not-started",
            outcome.termination["verification"],
        )
        self.assertTrue(outcome.termination["tree_empty"])
        self.assertFalse(target_marker.exists(), "target launched without parent ACK")


if __name__ == "__main__":
    unittest.main()
