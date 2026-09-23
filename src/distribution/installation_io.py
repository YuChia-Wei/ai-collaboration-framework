"""Native, bounded file operations for quiescent managed maintenance.

Only single-file publication is atomic. File/namespace flushes are ordered;
power loss, hardware failure, remote filesystems and external writers are outside
this backend's selected failure domains. No cleanup or path discovery service.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import ctypes
from hashlib import sha256
import os
from pathlib import Path
import stat
import sys

from . import installation_state as state


@dataclass
class Changes:
    """Actual successful namespace/content changes, including preparation residue."""
    changed: bool = False
    counts: dict = field(default_factory=lambda: dict(added=0, changed=0, removed=0, unchanged=0))
    operation_root: str | None = None
    lock_sha256: str | None = None
    protected: str = "unresolved"
    marker_admitted: bool = False
    residues: list[dict] = field(default_factory=list)

    def record(self, role: str, name: str) -> None:
        self.changed = True
        # Bounded structural residue locators; no per-step persisted journal.
        if role != "project" or name in {state.GUARD_PATH, ".ai", ".ai/local"} or "/.fi-" in name:
            if len(self.residues) < 24:
                self.residues.append({"role": role, "path": name})


def budget(paths: list[tuple[str, Path, str]]) -> None:
    """Check every actual name (and its ancestors) before any allocation."""
    for role, root, name in paths:
        state._relative(name)
        target = root.joinpath(*name.split("/"))
        state._check(target.is_relative_to(root), "path-containment", "Derived path escapes its selected root.", name)
        lengths = [len(str(target).encode("utf-16-le")) // 2]
        segments = [len(part.encode("utf-16-le")) // 2 for part in target.parts]
        state._check(lengths[0] <= state.LIMITS["path_utf16"] and max(segments) <= state.LIMITS["segment_utf16"],
                     "path-budget", f"Actual {role} path exceeds the 240/255 UTF-16 refusal budget.", name, "unsupported")


def sibling(operation_id: str, destination: str) -> str:
    suffix = sha256((operation_id + "\0" + destination).encode("utf-8")).hexdigest()[:12]
    return destination.rsplit("/", 1)[0] + "/.fi-" + suffix


class Backend:
    """Windows NTFS/ReFS or Linux selected local filesystems; no fallback."""

    def __init__(self, roots: dict[str, Path], durability: dict):
        state._shape(durability, {"declared_by", "declaration_reference", "failure_domain"})
        for value in durability.values():
            state._text(value)
        domain = durability["failure_domain"]
        state._check(domain in {"process-termination", "project-volume-loss"}, "failure-domain",
                     "Supported domains are process-termination and project-volume-loss with surviving recovery storage; power loss is unsupported.", outcome="unsupported")
        self.windows = os.name == "nt"
        state._check(self.windows or (os.name == "posix" and sys.platform == "linux" and ctypes.sizeof(ctypes.c_void_p) == 8),
                     "native-platform", "Only Windows and 64-bit Linux native maintenance are supported.", outcome="unsupported")
        if self.windows:
            from ctypes import wintypes as w
            self.native = ctypes.WinDLL("kernel32", use_last_error=True)
            self.native.MoveFileExW.argtypes = [w.LPCWSTR, w.LPCWSTR, w.DWORD]
            self.native.MoveFileExW.restype = w.BOOL
            self.native.GetVolumePathNameW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
            self.native.GetVolumePathNameW.restype = w.BOOL
            self.native.GetDriveTypeW.argtypes = [w.LPCWSTR]
            self.native.GetDriveTypeW.restype = w.UINT
            self.native.GetVolumeInformationW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD, ctypes.POINTER(w.DWORD),
                                                          ctypes.POINTER(w.DWORD), ctypes.POINTER(w.DWORD), w.LPWSTR, w.DWORD]
            self.native.GetVolumeInformationW.restype = w.BOOL
        else:
            self.native = ctypes.CDLL(None, use_errno=True)
            state._check(hasattr(self.native, "renameat2"), "native-primitive",
                         "Linux libc renameat2 is required for non-replacing publication.", outcome="unsupported")
            self.native.renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
            self.native.renameat2.restype = ctypes.c_int
            self.native.statfs.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
            self.native.statfs.restype = ctypes.c_int
        observed = {role: self._volume(root) for role, root in roots.items()}
        if domain == "project-volume-loss":
            state._check(observed["project"][0] != observed["recovery"][0] and not observed["recovery"][1],
                         "recovery-failure-domain", "Project-volume loss needs a distinct non-RAM recovery volume; survival remains the caller's assertion.", outcome="unsupported")

    def _volume(self, root: Path) -> tuple:
        if self.windows:
            from ctypes import wintypes as w
            volume, filesystem = ctypes.create_unicode_buffer(260), ctypes.create_unicode_buffer(64)
            if not self.native.GetVolumePathNameW(str(root), volume, len(volume)):
                raise OSError("native volume observation failed")
            kind = self.native.GetDriveTypeW(volume.value)
            serial, maximum, flags = w.DWORD(), w.DWORD(), w.DWORD()
            if not self.native.GetVolumeInformationW(volume.value, None, 0, ctypes.byref(serial), ctypes.byref(maximum),
                                                     ctypes.byref(flags), filesystem, len(filesystem)):
                raise OSError("native filesystem observation failed")
            state._check(kind in {3, 6} and filesystem.value.upper() in {"NTFS", "REFS"}, "native-filesystem",
                         "Windows backend requires a local fixed/RAM NTFS or ReFS volume.", outcome="unsupported")
            return (root.stat().st_dev, kind == 6)
        buffer = ctypes.create_string_buffer(256)
        if self.native.statfs(os.fsencode(root), buffer) != 0:
            raise OSError("native filesystem observation failed")
        kind = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_long))[0] & 0xffffffff
        state._check(kind in {0xef53, 0x58465342, 0x9123683e, 0x01021994, 0x858458f6}, "native-filesystem",
                     "Linux backend requires ext4-family, XFS, Btrfs, tmpfs or ramfs; network/unknown filesystems are unsupported.", outcome="unsupported")
        return (root.stat().st_dev, kind in {0x01021994, 0x858458f6})

    def flush_directory(self, directory: Path) -> None:
        state._no_links(directory)
        if not self.windows:
            descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        # Windows has no portable directory fsync here. MoveFileExW uses
        # WRITE_THROUGH; selected domains keep the OS/recovery volume alive.

    def move(self, source: Path, target: Path, replace: bool) -> None:
        state._check(source.parent == target.parent, "publication-volume", "Publication must use a same-directory sibling.")
        if self.windows:
            if not self.native.MoveFileExW(str(source), str(target), 8 | (1 if replace else 0)):
                raise OSError("native publication failed")
        else:
            if self.native.renameat2(-100, os.fsencode(source), -100, os.fsencode(target), 0 if replace else 1) != 0:
                raise OSError("native publication failed")


class IO:
    """One operation's bounded reader, native backend and actual mutation tally."""

    def __init__(self, backend: Backend, reader: state._Reader, changes: Changes):
        self.backend, self.reader, self.changes = backend, reader, changes

    def locate(self, root: Path, name: str) -> Path | None:
        state._root(str(root))
        self.contained_volume(root, name)
        self.reader.listings.clear()
        return self.reader.locate(root, name)

    def contained_volume(self, root: Path, name: str) -> None:
        state._relative(name)
        device = root.stat().st_dev
        current = root
        for part in name.split("/"):
            current = current / part
            try:
                info = current.lstat()
            except FileNotFoundError:
                break
            state._plain(info, name)
            state._check(info.st_dev == device and not (current.is_dir() and os.path.ismount(current)),
                         "nested-mount", "Operation paths cannot cross a nested mount or volume boundary.", name, "unsupported")

    def raw(self, root: Path, name: str, limit: int = state.LIMITS["file_bytes"]) -> bytes | None:
        target = self.locate(root, name)
        return None if target is None else self.reader.read(target, name, limit)

    def parents(self, root: Path, name: str, role: str) -> None:
        parts = name.split("/")[:-1]
        for index in range(1, len(parts) + 1):
            relative = "/".join(parts[:index])
            target = self.locate(root, relative)
            if target is None:
                target = root.joinpath(*parts[:index])
                target.mkdir(mode=0o700)
                self.changes.record(role, relative)
                self.backend.flush_directory(target.parent)
            state._plain(target.lstat(), relative)
            state._check(stat.S_ISDIR(target.lstat().st_mode), "parent-collision", "Required parent is not a direct directory.", relative, "conflict")

    def directory(self, root: Path, name: str, role: str) -> Path:
        state._check(self.locate(root, name) is None, "operation-collision", "Exclusive operation path already exists.", name, "conflict")
        target = root / name
        target.mkdir(mode=0o700)
        self.changes.record(role, name)
        self.backend.flush_directory(root)
        return target

    def create(self, root: Path, name: str, raw: bytes, role: str, mode: str = "100644") -> None:
        self.parents(root, name, role)
        state._check(self.locate(root, name) is None, "exclusive-file", "Exclusive file path is occupied.", name, "conflict")
        target = root / name
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0), 0o600)
        self.changes.record(role, name)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as stream:
                stream.write(raw)
                stream.flush()
                if not self.backend.windows:
                    os.fchmod(descriptor, 0o755 if mode == "100755" else 0o644)
                os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.backend.flush_directory(target.parent)
        state._check(self.raw(root, name) == raw, "write-readback", "Written bytes did not read back exactly.", name)

    def expect(self, root: Path, name: str, raw: bytes | None, mode: str | None = None) -> None:
        state._check(self.raw(root, name) == raw, "current-drift", "Current bytes/absence differ from the admitted state.", name, "conflict")
        if raw is not None and mode is not None and not self.backend.windows:
            state._check(stat.S_IMODE((root / name).lstat().st_mode) == (0o755 if mode == "100755" else 0o644),
                         "current-mode-drift", "Current mode differs from the admitted state.", name, "conflict")

    def publish(self, root: Path, name: str, raw: bytes, before: bytes | None, operation_id: str,
                mode: str = "100644", before_mode: str | None = None, category: str | None = None) -> None:
        temporary = sibling(operation_id, name)
        self.expect(root, name, before, before_mode)
        state._check(self.locate(root, temporary) is None, "sibling-collision", "Publication sibling must be absent.", temporary, "conflict")
        self.create(root, temporary, raw, "project", mode)
        self.expect(root, name, before, before_mode)
        self.backend.move(root / temporary, root / name, replace=before is not None)
        self.changes.record("project", name)
        if name == state.MARKERS[0]:
            self.changes.marker_admitted = True
        if category:
            self.changes.counts[category] += 1
        self.backend.flush_directory((root / name).parent)
        self.expect(root, name, raw, mode)

    def remove(self, root: Path, name: str, before: bytes, mode: str | None = None,
               category: str | None = None) -> None:
        self.expect(root, name, before, mode)
        (root / name).unlink()
        self.changes.record("project", name)
        if category:
            self.changes.counts[category] += 1
        self.backend.flush_directory((root / name).parent)
        self.expect(root, name, None)

    def mode(self, root: Path, name: str, raw: bytes, before_mode: str, after_mode: str) -> None:
        self.expect(root, name, raw, before_mode)
        if not self.backend.windows:
            descriptor = os.open(root / name, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                opened, current = os.fstat(descriptor), (root / name).lstat()
                state._check((opened.st_dev, opened.st_ino) == (current.st_dev, current.st_ino),
                             "mode-open-drift", "Mode target changed while opening.", name, "conflict")
                os.fchmod(descriptor, 0o755 if after_mode == "100755" else 0o644)
                self.changes.record("project", name)
                self.changes.counts["changed"] += 1
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            self.expect(root, name, raw, after_mode)
        else:
            self.changes.counts["unchanged"] += 1
