#!/usr/bin/env python3
"""Portable, opt-in routing for explicitly classified disposable test fixtures."""

from __future__ import annotations

import atexit
import ctypes
import json
import os
import platform
import re
import shutil
import stat
import tempfile as system_tempfile
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PureWindowsPath
from typing import Mapping


ENVIRONMENT_VARIABLE = "AI_CONTEXT_TEST_TMP_ROOT"
DIAGNOSTICS_VARIABLE = "AI_CONTEXT_TEST_FIXTURE_DIAGNOSTICS"
RUN_PREFIX = "ai-context-tests-run-"
MANIFEST_RELATIVE_PATH = Path(".ai/scripts/test-fixture-classifications.json")
SUMMARY_PREFIX = "AI_CONTEXT_TEST_FIXTURE_SUMMARY "


class FixtureRootError(RuntimeError):
    """Fail-closed configuration or containment error."""


class FixtureClassification(str, Enum):
    EPHEMERAL = "ephemeral-fixture-io"
    DURABILITY = "durability-storage-semantics"
    PLATFORM = "platform-filesystem-semantics"
    UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class RootPreflight:
    root: Path
    filesystem_type: str
    path_type: str
    capacity_bytes: int
    free_bytes: int

    @property
    def diagnostic_root_type(self) -> str:
        filesystem = re.sub(r"[^a-z0-9_-]+", "-", self.filesystem_type.lower())
        return f"explicit-{filesystem or 'filesystem'}"


@dataclass(frozen=True)
class FixtureRootResolution:
    route: str
    source: str
    preflight: RootPreflight | None

    def diagnostic(self, *, workspace: str | Path | None = None) -> dict[str, object]:
        platform_kind = platform_family()
        fixture_kind = self.preflight.path_type if self.preflight else "os-default"
        warning = wsl_mount_guidance(
            workspace=workspace,
            fixture_path=self.preflight.root if self.preflight else None,
            platform_kind=platform_kind,
        )
        return {
            "route": self.route,
            "root_type": (
                self.preflight.diagnostic_root_type if self.preflight else "os-default"
            ),
            "platform": platform_kind,
            "fixture_path_type": fixture_kind,
            "warning": warning,
        }


def _is_reparse_point(path: Path) -> bool:
    try:
        attributes = os.lstat(path).st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def platform_family(
    *,
    system_name: str | None = None,
    environ: Mapping[str, str] | None = None,
    release_text: str | None = None,
) -> str:
    system_name = (system_name or platform.system()).lower()
    environ = os.environ if environ is None else environ
    if system_name == "windows":
        return "windows"
    if system_name == "linux":
        release = (release_text if release_text is not None else platform.release()).lower()
        if environ.get("WSL_DISTRO_NAME") or environ.get("WSL_INTEROP") or "microsoft" in release:
            return "wsl"
        return "linux"
    return system_name or "unknown"


def path_type_for_diagnostics(value: str | Path, *, platform_kind: str | None = None) -> str:
    kind = platform_kind or platform_family()
    text = str(value).replace("\\", "/")
    if kind == "wsl":
        return (
            "wsl-mounted-windows-filesystem"
            if re.match(r"^/mnt/[a-zA-Z](?:/|$)", text)
            else "wsl-native-filesystem"
        )
    if kind == "windows":
        pure = PureWindowsPath(str(value))
        return "windows-network-filesystem" if str(pure).startswith("\\\\") else "windows-local-filesystem"
    if kind == "linux":
        return "linux-native-filesystem"
    return "other-filesystem"


def wsl_mount_guidance(
    *,
    workspace: str | Path | None,
    fixture_path: str | Path | None,
    platform_kind: str | None = None,
) -> str | None:
    kind = platform_kind or platform_family()
    if kind != "wsl":
        return None
    path_types = {
        path_type_for_diagnostics(path, platform_kind=kind)
        for path in (workspace, fixture_path)
        if path is not None
    }
    if "wsl-mounted-windows-filesystem" not in path_types:
        return None
    return (
        "non-blocking: WSL /mnt/* metadata I/O may be slow; consider a WSL-native "
        "clone or an explicitly configured disposable fixture root"
    )


def _linux_filesystem_type(path: Path) -> str:
    mountinfo = Path("/proc/self/mountinfo")
    try:
        lines = mountinfo.read_text(encoding="utf-8").splitlines()
    except OSError:
        return "unavailable"
    resolved = path.as_posix()
    candidates: list[tuple[int, str]] = []
    for line in lines:
        before, separator, after = line.partition(" - ")
        if not separator:
            continue
        fields = before.split()
        after_fields = after.split()
        if len(fields) < 5 or not after_fields:
            continue
        mount = fields[4].replace("\\040", " ").replace("\\011", "\t")
        if resolved == mount or resolved.startswith(mount.rstrip("/") + "/"):
            candidates.append((len(mount), after_fields[0]))
    return max(candidates, default=(0, "unavailable"))[1]


def _windows_filesystem_type(path: Path) -> str:
    try:
        filesystem = ctypes.create_unicode_buffer(64)
        root = str(path.anchor or path)
        success = ctypes.windll.kernel32.GetVolumeInformationW(  # type: ignore[attr-defined]
            ctypes.c_wchar_p(root), None, 0, None, None, None, filesystem, len(filesystem)
        )
        return filesystem.value if success and filesystem.value else "unavailable"
    except (AttributeError, OSError):
        return "unavailable"


def filesystem_type(path: Path, *, platform_kind: str | None = None) -> str:
    kind = platform_kind or platform_family()
    if kind == "windows":
        return _windows_filesystem_type(path)
    if kind in {"linux", "wsl"}:
        return _linux_filesystem_type(path)
    return "unavailable"


def preflight_fixture_root(candidate: str | Path) -> RootPreflight:
    raw = Path(candidate)
    if not raw.is_absolute():
        raise FixtureRootError("configured fixture root must be an absolute path")
    if not raw.exists():
        raise FixtureRootError("configured fixture root does not exist")
    if not raw.is_dir():
        raise FixtureRootError("configured fixture root is not a directory")
    checked_component = raw
    while checked_component.parent != checked_component:
        if checked_component.is_symlink() or _is_reparse_point(checked_component):
            raise FixtureRootError(
                "configured fixture root must not traverse a symlink or reparse point"
            )
        checked_component = checked_component.parent
    if raw.is_symlink() or _is_reparse_point(raw):
        raise FixtureRootError("configured fixture root must not be a symlink or reparse point")
    try:
        root = raw.resolve(strict=True)
    except OSError as exc:
        raise FixtureRootError("configured fixture root cannot be resolved") from exc
    if root.parent == root:
        raise FixtureRootError("configured fixture root must not be a filesystem or volume root")

    probe = root / f".ai-context-test-preflight-{uuid.uuid4().hex}"
    try:
        probe.mkdir()
        marker = probe / "write-check"
        marker.write_bytes(b"preflight\n")
        with marker.open("rb") as handle:
            if handle.read() != b"preflight\n":
                raise FixtureRootError("configured fixture root failed its read-back check")
        marker.unlink()
        probe.rmdir()
    except FixtureRootError:
        shutil.rmtree(probe, ignore_errors=True)
        raise
    except OSError as exc:
        shutil.rmtree(probe, ignore_errors=True)
        raise FixtureRootError("configured fixture root is not writable") from exc

    usage = shutil.disk_usage(root)
    kind = platform_family()
    return RootPreflight(
        root=root,
        filesystem_type=filesystem_type(root, platform_kind=kind),
        path_type=path_type_for_diagnostics(root, platform_kind=kind),
        capacity_bytes=usage.total,
        free_bytes=usage.free,
    )


def resolve_fixture_root(
    explicit_root: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> FixtureRootResolution:
    environ = os.environ if environ is None else environ
    if explicit_root is not None and str(explicit_root).strip():
        return FixtureRootResolution("accelerated", "runner-parameter", preflight_fixture_root(explicit_root))
    configured = environ.get(ENVIRONMENT_VARIABLE, "").strip()
    if configured:
        return FixtureRootResolution("accelerated", "repository-environment", preflight_fixture_root(configured))
    return FixtureRootResolution("default", "os-default", None)


def is_contained_run_directory(root: Path, run_directory: Path) -> bool:
    try:
        resolved_root = root.resolve(strict=True)
        resolved_run = run_directory.resolve(strict=True)
    except OSError:
        return False
    return (
        resolved_run.parent == resolved_root
        and resolved_run.name.startswith(RUN_PREFIX)
        and resolved_run != resolved_root
        and not run_directory.is_symlink()
        and not _is_reparse_point(run_directory)
    )


def cleanup_run_directory(root: Path, run_directory: Path) -> None:
    if not run_directory.exists():
        return
    if not is_contained_run_directory(root, run_directory):
        raise FixtureRootError("cleanup refused a path outside the verified run directory")
    try:
        shutil.rmtree(run_directory, onerror=_remove_readonly)
    except OSError as exc:
        raise FixtureRootError("verified run directory cleanup failed") from exc


def _remove_readonly(function: object, path: str, _: object) -> None:
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    function(path)  # type: ignore[operator]


def _create_inherited_acl_directory(root: Path, *, prefix: str, suffix: str = "") -> Path:
    for _ in range(100):
        candidate = root / f"{prefix}{uuid.uuid4().hex}{suffix}"
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
        except OSError as exc:
            raise FixtureRootError("unable to create a contained fixture directory") from exc
    raise FixtureRootError("unable to allocate a unique contained fixture directory")


class InheritedAclTemporaryDirectory:
    """TemporaryDirectory-compatible child that retains its parent's Windows ACL."""

    def __init__(self, root: Path, *, suffix: str = "", prefix: str = "tmp") -> None:
        self.path = _create_inherited_acl_directory(root, prefix=prefix, suffix=suffix)
        self.name = str(self.path)

    def cleanup(self) -> None:
        if self.path.exists():
            try:
                shutil.rmtree(self.path, onerror=_remove_readonly)
            except OSError as exc:
                raise FixtureRootError("classified fixture cleanup failed") from exc

    def __enter__(self) -> str:
        return self.name

    def __exit__(self, *_: object) -> None:
        self.cleanup()


class FixtureRunSession:
    def __init__(self, resolution: FixtureRootResolution) -> None:
        if resolution.preflight is None or resolution.route != "accelerated":
            raise FixtureRootError("accelerated fixture session requires a preflighted root")
        self.resolution = resolution
        started = time.perf_counter()
        self.run_directory = _create_inherited_acl_directory(
            resolution.preflight.root, prefix=RUN_PREFIX
        )
        if not is_contained_run_directory(resolution.preflight.root, self.run_directory):
            shutil.rmtree(self.run_directory, ignore_errors=True)
            raise FixtureRootError("created run directory failed containment validation")
        self.fixture_count = 0
        self.fixture_creation_seconds = time.perf_counter() - started
        self._closed = False

    def temporary_directory(self, *args: object, **kwargs: object) -> InheritedAclTemporaryDirectory:
        if len(args) > 2:
            raise FixtureRootError("classified fixture supports only suffix and prefix positional arguments")
        kwargs = dict(kwargs)
        if kwargs.get("dir") is not None:
            raise FixtureRootError("classified fixture callers must not override the verified run directory")
        kwargs.pop("dir", None)
        if "ignore_cleanup_errors" in kwargs:
            kwargs.pop("ignore_cleanup_errors")
        suffix = str(args[0]) if args else str(kwargs.pop("suffix", ""))
        prefix = str(args[1]) if len(args) > 1 else str(kwargs.pop("prefix", "tmp"))
        if kwargs:
            raise FixtureRootError(f"unsupported classified fixture options: {sorted(kwargs)}")
        started = time.perf_counter()
        temporary = InheritedAclTemporaryDirectory(
            self.run_directory, suffix=suffix, prefix=prefix
        )
        self.fixture_creation_seconds += time.perf_counter() - started
        self.fixture_count += 1
        if Path(temporary.name).resolve().parent != self.run_directory.resolve():
            temporary.cleanup()
            raise FixtureRootError("fixture directory escaped the verified run directory")
        return temporary

    def close(self) -> None:
        if self._closed:
            return
        cleanup_run_directory(self.resolution.preflight.root, self.run_directory)  # type: ignore[union-attr]
        self._closed = True


_PROCESS_SESSION: FixtureRunSession | None = None
_PROCESS_ROOT: Path | None = None
_DEFAULT_FIXTURE_COUNT = 0
_DEFAULT_FIXTURE_SECONDS = 0.0


def _process_session() -> FixtureRunSession | None:
    global _PROCESS_ROOT, _PROCESS_SESSION
    configured = os.environ.get(ENVIRONMENT_VARIABLE, "").strip()
    if _PROCESS_SESSION is not None and configured:
        try:
            if Path(configured).resolve(strict=True) == _PROCESS_ROOT:
                return _PROCESS_SESSION
        except OSError as exc:
            raise FixtureRootError("configured fixture root cannot be resolved") from exc
    resolution = resolve_fixture_root()
    if resolution.route == "default":
        return None
    assert resolution.preflight is not None
    if _PROCESS_SESSION is not None:
        if _PROCESS_ROOT != resolution.preflight.root:
            raise FixtureRootError("fixture root changed after the process run directory was created")
        return _PROCESS_SESSION
    _PROCESS_ROOT = resolution.preflight.root
    _PROCESS_SESSION = FixtureRunSession(resolution)
    return _PROCESS_SESSION


def TemporaryDirectory(  # noqa: N802 - compatibility with tempfile call sites
    *args: object,
    classification: FixtureClassification | str = FixtureClassification.EPHEMERAL,
    **kwargs: object,
) -> system_tempfile.TemporaryDirectory[str] | InheritedAclTemporaryDirectory:
    global _DEFAULT_FIXTURE_COUNT, _DEFAULT_FIXTURE_SECONDS
    try:
        selected = FixtureClassification(classification)
    except ValueError as exc:
        raise FixtureRootError(f"unknown fixture classification: {classification}") from exc
    if selected is not FixtureClassification.EPHEMERAL:
        return system_tempfile.TemporaryDirectory(*args, **kwargs)
    session = _process_session()
    if session:
        return session.temporary_directory(*args, **kwargs)
    started = time.perf_counter()
    temporary = system_tempfile.TemporaryDirectory(*args, **kwargs)
    _DEFAULT_FIXTURE_SECONDS += time.perf_counter() - started
    _DEFAULT_FIXTURE_COUNT += 1
    return temporary


def load_classification_manifest(repository_root: Path) -> dict[str, object]:
    path = repository_root / MANIFEST_RELATIVE_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureRootError("classification manifest cannot be read") from exc
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise FixtureRootError("classification manifest schema_version must be 1.0")
    if data.get("environment_variable") != ENVIRONMENT_VARIABLE:
        raise FixtureRootError("classification manifest environment variable is inconsistent")
    tests = data.get("tests")
    if not isinstance(tests, list) or not tests:
        raise FixtureRootError("classification manifest tests must be a non-empty list")
    observed: set[str] = set()
    for index, entry in enumerate(tests):
        if not isinstance(entry, dict):
            raise FixtureRootError(f"classification manifest test {index} must be an object")
        relative = entry.get("path")
        classification = entry.get("classification")
        if not isinstance(relative, str) or not relative.startswith(".ai/scripts/tests/"):
            raise FixtureRootError(f"classification manifest test {index} has an unsafe path")
        if relative in observed:
            raise FixtureRootError(f"classification manifest duplicates {relative}")
        observed.add(relative)
        try:
            selected = FixtureClassification(classification)
        except ValueError as exc:
            raise FixtureRootError(f"classification manifest test {relative} has an unknown classification") from exc
        if selected is not FixtureClassification.EPHEMERAL:
            raise FixtureRootError(f"accelerated profile may contain only ephemeral fixtures: {relative}")
        if not (repository_root / relative).is_file():
            raise FixtureRootError(f"classified test does not exist: {relative}")
    return data


def _emit_process_summary() -> None:
    if os.environ.get(DIAGNOSTICS_VARIABLE) != "1":
        return
    resolution = resolve_fixture_root()
    session = _PROCESS_SESSION
    payload = resolution.diagnostic(workspace=Path.cwd())
    payload.update(
        {
            "event": "fixture-summary",
            "fixture_classification": FixtureClassification.EPHEMERAL.value,
            "fixture_count": session.fixture_count if session else _DEFAULT_FIXTURE_COUNT,
            "fixture_creation_seconds": round(
                session.fixture_creation_seconds if session else _DEFAULT_FIXTURE_SECONDS, 6
            ),
        }
    )
    print(SUMMARY_PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")))


def close_process_session() -> None:
    global _DEFAULT_FIXTURE_COUNT, _DEFAULT_FIXTURE_SECONDS, _PROCESS_ROOT, _PROCESS_SESSION
    if _PROCESS_SESSION is not None:
        _PROCESS_SESSION.close()
    _PROCESS_SESSION = None
    _PROCESS_ROOT = None
    _DEFAULT_FIXTURE_COUNT = 0
    _DEFAULT_FIXTURE_SECONDS = 0.0


atexit.register(close_process_session)
atexit.register(_emit_process_summary)
