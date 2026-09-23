"""Read explicit immutable Git blobs, bypassing checkout conversions and replace refs."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import re
import stat
import subprocess

from .data import DistributionError, path, require


@dataclass(frozen=True)
class Blob:
    path: str
    oid: str
    mode: str
    data: bytes

    def identity(self) -> dict:
        return {"path": self.path, "git_blob": self.oid, "mode": self.mode,
                "size": len(self.data), "sha256": sha256(self.data).hexdigest()}


def _require_windows_direct_drive(target: Path, label: str) -> None:
    """Refuse directory-drive aliases when the final-path API is unavailable."""
    import ctypes
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.QueryDosDeviceW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
    kernel.QueryDosDeviceW.restype = w.DWORD
    device = ctypes.create_unicode_buffer(32768)
    length = kernel.QueryDosDeviceW(target.drive, device, len(device))
    kernel.GetDriveTypeW.argtypes = [w.LPCWSTR]
    kernel.GetDriveTypeW.restype = w.UINT
    require(0 < length < len(device) and re.fullmatch(r"\\Device\\[^\\]+", device.value) is not None
            and kernel.GetDriveTypeW(target.anchor) in {2, 3, 5, 6},
            f"{label}: final-path fallback requires a direct local drive mapping")


def direct_directory(value: Path, label: str) -> Path:
    """Admit a direct directory when Windows lacks the final-path API.

    Only ERROR_INVALID_FUNCTION (1) may use the already checked absolute path.
    The drive mapping must be direct and local; every ancestor must exist,
    be a plain directory and retain its identity.
    This is bounded path admission, not a concurrent-filesystem/durability claim.
    """
    require(value.is_absolute() and ".." not in value.parts,
            f"{label}: use an absolute directory without traversal")
    require(not str(value).startswith(("\\\\", "//")), f"{label}: network/device roots are unsupported")
    if os.name == "nt":
        for part in value.parts[1:]:
            require(not part.endswith((".", " ")) and not re.search(r'[<>:"|?*~\x00-\x1f]', part)
                    and re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part) is None,
                    f"{label}: ambiguous or aliased directory segment")

    def identities():
        result = []
        for current in (value, *value.parents):
            info = current.lstat()
            require(stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
                    and not getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
                    f"{label}: every ancestor must be a direct directory without links/reparse points")
            result.append((info.st_dev, info.st_ino))
        return result

    before = identities()
    try:
        resolved = value.resolve(strict=True)
    except OSError as exc:
        if os.name != "nt" or getattr(exc, "winerror", None) != 1:
            raise
        require(all(device and inode for device, inode in before),
                f"{label}: final-path fallback requires usable filesystem identities")
        resolved = Path(os.path.abspath(value))
        _require_windows_direct_drive(resolved, label)
    require(identities() == before, f"{label}: directory identity changed during admission")
    return resolved


class GitSource:
    def __init__(self, repository: Path, commit: str):
        require(repository.is_absolute(), "repository must be an explicit absolute worktree root")
        self.repository = direct_directory(repository, "repository")
        root_info = self.repository.lstat()
        self.repository_identity = (root_info.st_dev, root_info.st_ino)
        require(re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit) is not None,
                "commit must be one full lowercase Git object ID, never a branch, tag or abbreviation")
        self.commit = commit
        self.blobs: dict[str, Blob] = {}
        actual_root = direct_directory(Path(self._git("rev-parse", "--show-toplevel").decode().strip()), "Git worktree root")
        root_info = actual_root.lstat()
        require(actual_root == self.repository and (root_info.st_dev, root_info.st_ino) == self.repository_identity,
                "repository must name its unchanged worktree root")
        promisor_keys = self._git("config", "--name-only", "--get-regexp",
                                  r"^(extensions\.partialclone|remote\..*\.promisor)$", allow_absent=True)
        require(not promisor_keys.strip(),
                "partial/promisor clones are unsupported; provide a complete local repository before assembly")
        require(self._git("cat-file", "-t", commit).strip() == b"commit",
                "selected object must be a commit, not an annotated tag or tree")
        self.tree = self._git("rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()

    def _git(self, *arguments: str, allow_absent: bool = False) -> bytes:
        environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
        environment.update(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
                           GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        try:
            result = subprocess.run(["git", "--no-replace-objects", "-C", str(self.repository), *arguments],
                                    env=environment, capture_output=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DistributionError(f"Git read {arguments[0]!r} failed or timed out; provide a local complete object database") from exc
        require(result.returncode == 0 or (allow_absent and result.returncode == 1),
                f"Git read {arguments[0]!r} failed; verify the explicit repository, commit and local objects (no fetch is performed)")
        return result.stdout

    def read(self, source_path: str) -> Blob:
        path(source_path, "Git input")
        require(source_path.startswith("src/"), f"build input outside src is forbidden: {source_path}")
        if source_path in self.blobs:
            return self.blobs[source_path]
        rows = self._git("ls-tree", "--full-tree", "-z", self.commit, "--", source_path).split(b"\0")
        entries = []
        for row in rows:
            if row:
                header, name = row.split(b"\t", 1)
                if name.decode("utf-8") == source_path:
                    entries.append(header.decode("ascii").split())
        require(len(entries) == 1, f"missing exact Git member: {source_path}; add it and commit the complete declared package")
        mode, kind, oid = entries[0]
        require(kind == "blob" and mode in {"100644", "100755"},
                f"{source_path}: only regular Git blobs are supported; symlinks, trees and submodules are forbidden")
        blob = Blob(source_path, oid, mode, self._git("cat-file", "blob", oid))
        self.blobs[source_path] = blob
        return blob
