"""Read-only selection 1/2 / lock 1 readers and inspection (development API 1).

No product entry point, filesystem mutation, Git subprocess or source fetch.
The executing reader closure is deliberately smaller than a future writer engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha1, sha256
import math
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

from .data import (DistributionError, Paths, _candidate_identity as _identity_text,
                   distribution_version, identifier, json_bytes, json_object, path, version)
from .git_source import Blob
from .package import check_references, load_package

__all__ = ["InstallationError", "Candidate", "InstalledLock", "Observation",
           "read_candidate", "read_lock", "observe_installation", "inspect",
           "READER_ENGINE_FILES", "ENGINE_FILES", "LIMITS"]

LIMITS = {"document_bytes": 4 * 1024 * 1024, "file_bytes": 16 * 1024 * 1024,
          "total_bytes": 128 * 1024 * 1024, "members": 4096, "components": 128,
          "entries": 20000, "nodes": 100000, "depth": 48,
          "yaml_bytes": 256 * 1024, "protected_inputs": 128,
          "path_utf16": 240, "segment_utf16": 255}
READER_ENGINE_FILES = tuple(sorted((
    "src/distribution/__init__.py", "src/distribution/data.py",
    "src/distribution/git_source.py", "src/distribution/package.py",
    "src/distribution/installation_state.py", "src/distribution/installation_plan.py",
)))
ENGINE_FILES = tuple(sorted((*READER_ENGINE_FILES,
    "src/distribution/installation.py", "src/distribution/installation_io.py",
    "src/distribution/maintenance_coordination.py", "src/tools/maintain_framework.py",
)))
METADATA = ("metadata/selection.json", "metadata/files.json", "metadata/build.json")
LOCK_PATH = ".ai/framework.lock"
MARKERS = (".ai/framework.operation", ".ai/config-transition.operation")
GUARD_PATH = ".ai/local/installation.guard"
MODES = {"100644", "100755"}
MODE_POLICIES = {"posix-permissions", "windows-inventory-only"}


class InstallationError(ValueError):
    """A bounded public diagnostic, never an underlying host exception string."""

    def __init__(self, code: str, reason: str, path: str | None = None,
                 outcome: str = "blocked", next_action: str = "Reconcile the explicit input and retry."):
        super().__init__(reason)
        self.outcome = outcome
        self.diagnostic = {"code": code, "path": path, "reason": reason, "next_action": next_action}


def _check(ok: bool, code: str, reason: str, name: str | None = None,
           outcome: str = "blocked") -> None:
    if not ok:
        raise InstallationError(code, reason, name, outcome)


def _shape(value: Any, required: set[str], optional: set[str] = frozenset()) -> dict:
    _check(type(value) is dict and all(type(k) is str for k in value),
           "invalid-shape", "Expected a closed object with string keys.")
    _check(required <= value.keys() and value.keys() <= required | optional,
           "invalid-fields", "Required fields are missing or unknown fields are present.")
    return value


def _text(value: Any) -> str:
    _check(type(value) is str and bool(value.strip()) and len(value) <= 4096,
           "invalid-text", "Expected bounded nonempty text.")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        raise InstallationError("invalid-unicode", "Unpaired Unicode surrogates are unsupported.") from None
    return value


def _array(value: Any, limit: int = LIMITS["members"]) -> list:
    _check(type(value) is list and len(value) <= limit, "array-limit", "Expected a bounded array.")
    return value


def _one(value: Any) -> None:
    _check(type(value) is int and value == 1, "unsupported-version",
           "Only exact integer version 1 is supported.", outcome="unsupported")


def _digest(value: Any, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    _check(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
           "invalid-digest", "Expected a full lowercase SHA-256 digest.")
    return value


def _oid(value: Any) -> str:
    _check(type(value) is str and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value) is not None,
           "invalid-git-identity", "Expected a full lowercase Git object identity.")
    return value


def _relative(value: Any) -> str:
    _text(value)
    _check(len(value.split("/")) <= LIMITS["depth"] and len(value.encode("utf-16-le")) // 2 <= LIMITS["path_utf16"],
           "path-limit", "Relative path exceeds the depth or UTF-16 length limit.")
    try:
        return path(value, "relative path")
    except DistributionError:
        raise InstallationError("invalid-path", "Expected an exact portable relative path.") from None


def _id(value: Any) -> str:
    _text(value)
    try:
        return identifier(value, "identifier")
    except DistributionError:
        raise InstallationError("invalid-identifier", "Unsupported capability identifier.") from None


def _version(value: Any) -> str:
    _text(value)
    try:
        return version(value, "version")
    except DistributionError:
        raise InstallationError("invalid-version", "Expected exact MAJOR.MINOR.PATCH.") from None


def _bounded(value: Any, *, allow_floats: bool = False) -> None:
    """Bound allocations and nesting before re-encoding caller-owned input."""
    stack, nodes, text_bytes = [(value, 0)], 0, 0
    seen = set()
    while stack:
        item, depth = stack.pop()
        nodes += 1
        _check(nodes + len(stack) <= LIMITS["nodes"] and depth <= LIMITS["depth"],
               "document-limit", "Input exceeds the node or nesting limit.")
        if type(item) in {dict, list}:
            _check(id(item) not in seen, "aliased-input", "Cyclic or shared mutable containers are unsupported.")
            seen.add(id(item))
            _check(nodes + len(stack) + len(item) <= LIMITS["nodes"], "document-limit", "Container exceeds node limit.")
            if type(item) is dict:
                for key, child in item.items():
                    text_bytes += len(_text(key).encode("utf-8"))
                    stack.append((child, depth + 1))
            else:
                stack.extend((child, depth + 1) for child in item)
        elif type(item) is str:
            _check(len(item) <= LIMITS["document_bytes"], "document-limit", "Text exceeds the byte budget.")
            try:
                text_bytes += len(item.encode("utf-8", errors="strict"))
            except UnicodeError:
                raise InstallationError("invalid-unicode", "Invalid Unicode text.") from None
        elif type(item) is int:
            _check(item.bit_length() <= 128, "integer-limit", "Integer exceeds the bounded representation.")
        elif type(item) is float and allow_floats:
            _check(math.isfinite(item), "invalid-scalar", "Nonfinite numbers are unsupported.")
        else:
            _check(item is None or type(item) is bool,
                   "invalid-scalar", "Unexpected scalar or inexact integer representation.")
        _check(text_bytes <= LIMITS["document_bytes"], "document-limit", "Text exceeds the aggregate byte budget.")


def _document(raw: bytes, name: str, canonical: bool = True) -> dict:
    _check(len(raw) <= LIMITS["document_bytes"], "document-limit", "Document exceeds byte limit.", name)
    try:
        value = json_object(raw, name)
        _bounded(value, allow_floats=not canonical)
        if canonical:
            _check(json_bytes(value) == raw, "noncanonical-document", "Canonical UTF-8 JSON bytes are required.", name)
        return value
    except (DistributionError, UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, InstallationError):
            raise
        raise InstallationError("invalid-json", "Invalid, duplicate-key or unbounded JSON document.", name) from None


def _plain(info: os.stat_result, name: str | None) -> None:
    _check(not stat.S_ISLNK(info.st_mode)
           and not (getattr(info, "st_file_attributes", 0) & 0x400),
           "linked-path", "Links and reparse points are unsupported.", name)


def _no_links(target: Path) -> None:
    for item in reversed((target, *target.parents)):
        info = item.lstat()
        _plain(info, None)


def _root(value: Any) -> Path:
    value = _text(value)
    normalized = value.replace("\\", "/")
    _check(not normalized.startswith("//") and not any(p in {".", ".."} for p in normalized.split("/")),
           "invalid-root", "Use a local absolute directory without traversal or network/device syntax.")
    target = Path(value)
    _check(target.is_absolute() and target != Path(target.anchor),
           "invalid-root", "Volume roots and relative roots are unsupported.")
    for part in target.parts[1:]:
        _check(not part.endswith((".", " ")) and not re.search(r'[<>:"|?*\x00-\x1f]', part)
               and re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part) is None,
               "ambiguous-root", "Ambiguous or reserved root path segment.")
    def identities():
        result = []
        for current in (target, *target.parents):
            info = current.lstat()
            _plain(info, None)
            _check(stat.S_ISDIR(info.st_mode), "invalid-root", "Every root ancestor must be a directory.")
            result.append((info.st_dev, info.st_ino))
        return result

    before = identities()
    try:
        resolved = target.resolve(strict=True)
    except OSError as exc:
        if os.name != "nt" or getattr(exc, "winerror", None) != 1:
            raise
        # ERROR_INVALID_FUNCTION: require direct stable identities and an
        # independent long-name check; abspath alone cannot reject short aliases.
        _check(all(device and inode for device, inode in before), "invalid-root",
               "Canonical fallback requires usable filesystem identities.")
        resolved = _windows_long_path(target)
    _check(identities() == before, "root-drift", "Root ancestry changed during admission.")
    _check(resolved == target, "noncanonical-root", "Root must name its direct canonical location.")
    return target


def _windows_long_path(target: Path) -> Path:
    """Query one exact name after the caller guards direct, stable ancestry."""
    import ctypes
    from ctypes import wintypes as w
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    # Long names do not expand DOS-drive aliases; require a direct local
    # device mapping as well, without selecting a different root.
    kernel.QueryDosDeviceW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
    kernel.QueryDosDeviceW.restype = w.DWORD
    device = ctypes.create_unicode_buffer(32768)
    length = kernel.QueryDosDeviceW(target.drive, device, len(device))
    kernel.GetDriveTypeW.argtypes = [w.LPCWSTR]
    kernel.GetDriveTypeW.restype = w.UINT
    _check(0 < length < len(device) and re.fullmatch(r"\\Device\\[^\\]+", device.value) is not None
           and kernel.GetDriveTypeW(target.anchor) in {2, 3, 5, 6},
           "noncanonical-root", "Direct local drive mapping is unavailable.")
    kernel.GetLongPathNameW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
    kernel.GetLongPathNameW.restype = w.DWORD
    canonical = ctypes.create_unicode_buffer(32768)
    length = kernel.GetLongPathNameW(str(target), canonical, len(canonical))
    _check(0 < length < len(canonical), "noncanonical-root", "Canonical root name is unavailable.")
    return Path(canonical.value)


class _Reader:
    """One call's bounded reads/listings. Caches are observations, not a lease."""

    def __init__(self):
        bootstrap_bytes = getattr(sys.modules.get("__main__"), "_framework_bootstrap_bytes", 0)
        _check(type(bootstrap_bytes) is int and 0 <= bootstrap_bytes <= LIMITS["total_bytes"],
               "bootstrap-read-budget", "Bootstrap read accounting is invalid.")
        self.bytes = bootstrap_bytes
        self.entries = 0
        self.listings: dict[Path, dict[str, str]] = {}
        self._listing_observations: dict[Path, tuple] = {}

    def forget_listing(self, directory: Path) -> None:
        """Own namespace mutations invalidate observations even on coarse clocks."""
        self.listings.pop(directory, None)
        self._listing_observations.pop(directory, None)

    def _directory_observation(self, directory: Path) -> tuple:
        info = directory.lstat()
        _plain(info, None)
        _check(stat.S_ISDIR(info.st_mode), "parent-collision", "Required parent is not a direct directory.")
        _check(info.st_dev and info.st_ino, "directory-identity", "Directory identity is unavailable.")
        return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
                info.st_mtime_ns, info.st_ctime_ns, getattr(info, "st_file_attributes", 0))

    def listing(self, directory: Path) -> dict[str, str]:
        # Revalidate the direct directory before reuse. This is an observation
        # under the existing quiescent-writer contract, never a filesystem lease.
        before = self._directory_observation(directory)
        if directory in self.listings and self._listing_observations.get(directory) == before:
            return self.listings[directory]
        self.forget_listing(directory)
        names = {}
        with os.scandir(directory) as rows:
            for row in rows:
                self.entries += 1
                _check(self.entries <= LIMITS["entries"], "scan-limit", "Directory entry limit exceeded; no partial inventory.")
                folded = row.name.casefold()
                _check(folded not in names, "path-alias", "Case aliases exist in a required directory.")
                names[folded] = row.name
        _check(self._directory_observation(directory) == before,
               "directory-drift", "Directory changed during listing; no partial inventory.")
        self.listings[directory] = names
        self._listing_observations[directory] = before
        return names

    def locate(self, root: Path, name: str) -> Path | None:
        _relative(name)
        current = root
        parts = name.split("/")
        for index, part in enumerate(parts):
            names = self.listing(current)
            actual = names.get(part.casefold())
            if actual is None:
                return None
            _check(actual == part, "path-alias", "Existing path uses a different case spelling.", name)
            current = current / part
            info = current.lstat()
            _plain(info, name)
            if index != len(parts) - 1:
                _check(stat.S_ISDIR(info.st_mode), "parent-collision", "A parent path is occupied by a non-directory.", name)
        return current

    def read(self, target: Path, name: str | None, limit: int = LIMITS["file_bytes"]) -> bytes:
        _no_links(target)
        before = target.lstat()
        _check(stat.S_ISREG(before.st_mode), "not-regular", "Expected a regular file.", name)
        _check(before.st_nlink == 1, "hardlinked-file", "Hardlinked input files are unsupported.", name)
        _check(before.st_size <= limit, "file-limit", "File exceeds the selected byte limit.", name)
        with target.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            _check(stat.S_ISREG(opened.st_mode) and (before.st_dev, before.st_ino) == (opened.st_dev, opened.st_ino),
                   "input-drift", "Input changed while opening.", name)
            raw = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
        self.bytes += len(raw)
        _check(len(raw) <= limit and self.bytes <= LIMITS["total_bytes"],
               "read-limit", "Read budget exceeded; no partial result.", name)
        final = target.lstat()
        _plain(final, name)
        signature = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_mode)
        _check(signature(before) == signature(after) == signature(final) and len(raw) == final.st_size,
               "input-drift", "Input changed during observation.", name)
        return raw

    def member(self, root: Path, row: dict, mode_policy: str) -> bytes:
        name = row["path"]
        target = self.locate(root, name)
        _check(target is not None, "missing-member", "Declared file is missing.", name)
        raw = self.read(target, name)
        _check(len(raw) == row["size"] and sha256(raw).hexdigest() == row["sha256"],
               "member-drift", "File length or raw SHA-256 differs.", name)
        if mode_policy == "posix-permissions":
            expected = 0o755 if row["mode"] == "100755" else 0o644
            _check(stat.S_IMODE(target.lstat().st_mode) == expected,
                   "mode-drift", "File permissions differ from the exact declared mode.", name)
        return raw


def _paths(names: list[str]) -> None:
    paths = Paths()
    try:
        for name in names:
            paths.add(name, "inventory")
    except DistributionError:
        raise InstallationError("path-collision", "Inventory contains duplicate, alias or parent/child paths.") from None


def _sorted(rows: list, key) -> None:
    values = [key(row) for row in rows]
    _check(values == sorted(values) and len(values) == len(set(values)),
           "noncanonical-order", "Array must have unique entries in the specified sorted order.")


def _source(row: Any) -> dict:
    _shape(row, {"path", "git_blob", "mode", "size", "sha256"})
    _relative(row["path"])
    _check(row["path"].startswith("src/"), "source-boundary", "Source identity must be inside src.")
    _oid(row["git_blob"])
    _descriptor(row)
    return row


def _descriptor(row: dict) -> None:
    _digest(row["sha256"])
    _check(type(row["size"]) is int and 0 <= row["size"] <= LIMITS["file_bytes"],
           "invalid-size", "Expected a bounded nonnegative exact integer size.")
    _check(type(row["mode"]) is str and row["mode"] in MODES, "invalid-mode", "Unsupported Git file mode.")


def _engine_shape(engine: Any) -> dict:
    _shape(engine, {"id", "version", "source_commit", "files"})
    _check(engine["id"] == "framework-managed-installation" and engine["version"] == "1.0.0",
           "unsupported-engine", "Unsupported maintenance engine identity.", outcome="unsupported")
    _oid(engine["source_commit"])
    rows = _array(engine["files"])
    _check(bool(rows), "empty-engine", "EnginePin requires an explicit file closure.")
    for row in rows:
        _shape(row, {"path", "sha256"})
        _relative(row["path"])
        _digest(row["sha256"])
    _sorted(rows, lambda row: row["path"])
    _paths([row["path"] for row in rows])
    return engine


def _dependencies(rows: Any, optional: bool) -> list:
    rows = _array(rows, LIMITS["components"])
    identities = []
    for row in rows:
        _shape(row, {"id", "version"} | ({"operations", "on_missing"} if optional else set()))
        identities.append(_id(row["id"]))
        _version(row["version"])
        if optional:
            operations = _array(row["operations"])
            _check(bool(operations), "invalid-dependency", "Optional dependency operations cannot be empty.")
            for operation in operations:
                _id(operation)
            _check(len(operations) == len(set(operations)) and row["on_missing"] in {"return-candidate", "unsupported"},
                   "invalid-dependency", "Invalid optional dependency contract.")
    _check(len(identities) == len(set(identities)), "duplicate-dependency", "Duplicate dependency identity.")
    return rows


def _selection_inventory(selection: Any, inventory: Any) -> dict[str, dict]:
    _shape(selection, {"schema_version", "mode", "release_version", "source", "profile", "components",
                       "adapters", "build_inputs", "generator"})
    schema = selection["schema_version"]
    _check(type(schema) is int and schema in {1, 2}, "unsupported-version",
           "Only exact integer selection versions 1 and 2 are supported.", outcome="unsupported")
    if schema == 1:
        _check(selection["mode"] == "development" and selection["release_version"] is None,
               "unsupported-candidate", "Selection 1 requires development mode without a release version.", outcome="unsupported")
        generator_id = "framework-development-assembly"
    else:
        _check(selection["mode"] == "versioned", "unsupported-candidate",
               "Selection 2 requires explicit versioned mode.", outcome="unsupported")
        _text(selection["release_version"])
        try:
            distribution_version(selection["release_version"], "release_version")
        except DistributionError:
            raise InstallationError("invalid-distribution-version", "Expected canonical MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-rc.N (N > 0).") from None
        generator_id = "framework-versioned-assembly"
    _shape(selection["source"], {"commit", "tree"})
    commit = _oid(selection["source"]["commit"])
    _check(len(_oid(selection["source"]["tree"])) == len(commit), "git-format", "Mixed Git identity formats.")
    _id(selection["profile"])
    components = _array(selection["components"], LIMITS["components"])
    _check(bool(components), "empty-selection", "Select at least one actual component.")
    for item in components:
        _shape(item, {"id", "version", "metadata_version", "members", "required_dependencies", "optional_dependencies"})
        _id(item["id"])
        _version(item["version"])
        _check(type(item["metadata_version"]) is int and item["metadata_version"] in {1, 2, 3},
               "unsupported-metadata", "Only delivered metadata versions 1/2/3 are supported.", outcome="unsupported")
        names = [_relative(name) for name in _array(item["members"])]
        _sorted(names, lambda name: name)
        _check({"SKILL.md", "skill-package.yaml"} <= set(names), "package-closure", "Package entry or metadata is missing.")
        _paths(names)
        _dependencies(item["required_dependencies"], False)
        _dependencies(item["optional_dependencies"], True)
    _sorted(components, lambda item: item["id"])
    by_id = {item["id"]: item for item in components}
    for item in components:
        required = {row["id"] for row in item["required_dependencies"]}
        optional = {row["id"] for row in item["optional_dependencies"]}
        _check(not required & optional and item["id"] not in required | optional,
               "dependency-closure", "Overlapping or self dependencies are unsupported.")
        for dep in item["required_dependencies"] + item["optional_dependencies"]:
            _check(dep["id"] in by_id or dep["id"] not in required,
                   "dependency-closure", "Required dependency is not selected.")
            if dep["id"] in by_id:
                _check(by_id[dep["id"]]["version"] == dep["version"], "dependency-version", "Selected dependency version differs.")
    remaining = set(by_id)
    while remaining:
        ready = {name for name in remaining if not {r["id"] for r in by_id[name]["required_dependencies"]} & remaining}
        _check(bool(ready), "dependency-cycle", "Required dependency cycle.")
        remaining -= ready
    inputs = _array(selection["build_inputs"])
    for item in inputs:
        _source(item)
        _check(len(item["git_blob"]) == len(commit), "git-format", "Mixed Git identity formats.")
    _sorted(inputs, lambda item: item["path"])
    _paths([item["path"] for item in inputs])
    sources = {item["path"]: item for item in inputs}
    generator = _shape(selection["generator"], {"id", "implementation"})
    _check(generator["id"] == generator_id, "unsupported-generator", "Unknown candidate generator.", outcome="unsupported")
    implementation = _array(generator["implementation"])
    _check(bool(implementation), "empty-generator", "Generator provenance closure is empty.")
    seen_implementation = set()
    for item in implementation:
        _source(item)
        _check(item["path"] not in seen_implementation and sources.get(item["path"]) == item,
               "generator-binding", "Generator provenance does not match build inputs.")
        seen_implementation.add(item["path"])
    expected_inputs = seen_implementation | {"src/distribution/manifest.yaml", f"src/profiles/{selection['profile']}.yaml"}
    _shape(inventory, {"schema_version", "files"})
    _one(inventory["schema_version"])
    rows = _array(inventory["files"])
    _check(bool(rows), "empty-inventory", "Inventory is empty.")
    payload = {}
    runtime = {}
    for row in rows:
        _shape(row, {"path", "destination", "owner", "kind", "mode", "size", "sha256"}, {"source"})
        _relative(row["path"])
        _relative(row["destination"])
        _text(row["owner"])
        _text(row["kind"])
        _descriptor(row)
        _check(row["kind"] in {"payload", "runtime"} and row["path"] == f"{row['kind']}/{row['destination']}",
               "member-binding", "Candidate path and member kind disagree.")
        if row["kind"] == "payload":
            owner = row["owner"]
            _check(owner in by_id and "source" in row, "payload-owner", "Payload requires an exact selected package and source.")
            prefix = f".ai/core/skills/{owner}/"
            _check(row["destination"].startswith(prefix), "ownership-boundary", "Payload is outside its package destination.")
            member = row["destination"][len(prefix):]
            _check(member in by_id[owner]["members"], "package-closure", "Undeclared package member.")
            source = _source(row["source"])
            _check(source["path"] == f"src/skills/{owner}/{member}" and sources.get(source["path"]) == source
                   and all(source[key] == row[key] for key in ("sha256", "size", "mode")),
                   "source-binding", "Payload source identity disagrees with inventory/build inputs.")
            payload[(owner, member)] = row
            expected_inputs.add(source["path"])
        else:
            _check("source" not in row and row["mode"] == "100644", "runtime-binding", "Runtime source/mode shape is invalid.")
            runtime[row["destination"]] = row
    _sorted(rows, lambda row: row["path"])
    _paths([row["path"] for row in rows])
    _paths([row["destination"] for row in rows])
    _check(sum(row["size"] for row in rows) <= LIMITS["total_bytes"], "inventory-limit", "Inventory exceeds the total byte budget.")
    _check(set(payload) == {(item["id"], name) for item in components for name in item["members"]},
           "package-closure", "Inventory and component member closure differ.")
    adapters = _array(selection["adapters"], LIMITS["components"])
    seen_adapters, outputs = set(), set()
    for item in adapters:
        _shape(item, {"id", "package", "template", "installed_entrypoint", "entrypoint_source", "output"})
        _id(item["package"])
        _check(item["id"] == "codex" and item["package"] in by_id, "unsupported-adapter", "Unknown adapter or package.", outcome="unsupported")
        owner = item["package"]
        _check(owner not in seen_adapters, "duplicate-adapter", "Duplicate package adapter.")
        seen_adapters.add(owner)
        template = _source(item["template"])
        _check(template["path"] == "src/adapters/codex/skill-entry.md.template" and sources.get(template["path"]) == template,
               "adapter-template", "Adapter template provenance binding differs.")
        expected_inputs.add(template["path"])
        entry = payload[(owner, "SKILL.md")]
        _source(item["entrypoint_source"])
        _check(item["installed_entrypoint"] == entry["destination"] and item["entrypoint_source"] == entry["source"],
               "adapter-entry", "Adapter entry source/destination binding differs.")
        destination = f".agents/skills/framework-{owner}/SKILL.md"
        output = runtime.get(destination)
        _shape(item["output"], {"path", "destination", "owner", "kind", "mode", "size", "sha256"})
        _descriptor(item["output"])
        _check(output is not None and item["output"] == output and output["owner"] == f"codex/{owner}",
               "adapter-output", "Adapter output binding differs.")
        outputs.add(destination)
    _check(outputs == set(runtime) and (not adapters or seen_adapters == set(by_id)),
           "adapter-closure", "Runtime closure does not cover the selected adapter packages exactly.")
    _check(set(sources) == expected_inputs, "build-input-closure", "Available provenance input closure differs.")
    return {row["destination"]: row for row in rows}


def _candidate_identity(selection: dict, inventory: dict) -> tuple[str, dict[str, str]]:
    hashes = {METADATA[0]: sha256(json_bytes(selection)).hexdigest(), METADATA[1]: sha256(json_bytes(inventory)).hexdigest()}
    digest = sha256(json_bytes(hashes)).hexdigest()
    return _identity_text(selection["source"]["commit"], digest, selection["release_version"]), hashes


def _yaml_bound(raw: bytes, name: str) -> None:
    """Resource preflight only; the existing loader remains the metadata parser."""
    _check(len(raw) <= LIMITS["yaml_bytes"], "yaml-limit", "YAML input exceeds the byte limit.", name)
    _check(sys.dont_write_bytecode, "bytecode-policy", "Start the host with -B before imports; the reader cannot create dependency bytecode.", outcome="unsupported")
    try:
        import yaml
    except ImportError:
        raise InstallationError("missing-pyyaml", "PyYAML 6 is required; provision it explicitly.", outcome="unsupported") from None
    _check(yaml.__version__.split(".")[0] == "6", "unsupported-pyyaml", "Only PyYAML 6 is supported.", outcome="unsupported")
    try:
        depth, count = 0, 0
        for event in yaml.parse(raw.decode("utf-8", errors="strict"), Loader=yaml.SafeLoader):
            count += 1
            if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)):
                depth += 1
            if isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)):
                depth -= 1
            _check(count <= LIMITS["nodes"] and depth <= LIMITS["depth"], "yaml-limit", "YAML exceeds structural limits.", name)
            _check(not isinstance(event, yaml.events.AliasEvent) and getattr(event, "anchor", None) is None,
                   "yaml-alias", "YAML aliases and anchors are unsupported.", name)
    except (UnicodeError, yaml.YAMLError, RecursionError):
        raise InstallationError("invalid-yaml", "Invalid bounded UTF-8 YAML.", name) from None


def _packages(selection: dict, members: dict[str, dict], contents: dict[str, bytes]) -> None:
    packages = {}
    for component in selection["components"]:
        owner = component["id"]
        prefix = f".ai/core/skills/{owner}/"
        blobs = {}
        for member in component["members"]:
            row = members[prefix + member]
            raw = contents[prefix + member]
            source = row["source"]
            hashed = (sha1 if len(source["git_blob"]) == 40 else sha256)(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
            _check(hashed == source["git_blob"], "git-blob-binding", "Available payload bytes differ from declared Git blob.", row["destination"])
            blobs[member] = Blob(source["path"], source["git_blob"], row["mode"], raw)
        metadata = blobs["skill-package.yaml"]
        _yaml_bound(metadata.data, prefix + "skill-package.yaml")
        try:
            package = load_package(metadata)
            _bounded(package.metadata)
            _check(package.id == owner and package.version == component["version"]
                   and type(package.metadata["metadata_version"]) is int
                   and package.metadata["metadata_version"] == component["metadata_version"]
                   and package.members == frozenset(component["members"])
                   and package.metadata["dependencies"]["required"] == component["required_dependencies"]
                   and package.metadata["dependencies"]["optional"] == component["optional_dependencies"],
                   "metadata-binding", "Actual package metadata differs from selection/closure.", prefix + "skill-package.yaml")
            for schema in package.metadata["resources"]["schemas"]:
                _document(blobs[schema["path"]].data, prefix + schema["path"], canonical=False)
            entry = blobs["SKILL.md"].data.decode("utf-8", errors="strict")
            frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", entry, re.DOTALL)
            _check(frontmatter is not None, "entry-frontmatter", "Package entry lacks frontmatter.", prefix + "SKILL.md")
            _yaml_bound(frontmatter.group(1).encode("utf-8"), prefix + "SKILL.md")
            check_references(package, blobs)
        except (DistributionError, UnicodeError, RecursionError):
            raise InstallationError("package-contract", "Shared package loader/reference checks rejected this package.", prefix + "skill-package.yaml") from None
        packages[owner] = package
    for package in packages.values():
        for dep in package.metadata["dependencies"]["optional"]:
            if dep["id"] in packages:
                available = {row["id"] for row in packages[dep["id"]].metadata["operations"]}
                _check(set(dep["operations"]) <= available, "dependency-operations", "Selected optional dependency lacks operations.")


@dataclass(frozen=True)
class Candidate:
    root: Path
    identity: str
    selection: dict
    inventory: dict
    build: dict
    metadata_bytes: dict[str, bytes]
    members: dict[str, dict]
    contents: dict[str, bytes]


def _candidate_documents(raw: dict[str, bytes]) -> tuple:
    """Shared candidate semantics for filesystem input and durable recovery objects."""
    _shape(raw, set(METADATA))
    docs = {name: _document(raw[name], name) for name in METADATA}
    selection, inventory, build = (docs[name] for name in METADATA)
    members = _selection_inventory(selection, inventory)
    identity, identity_inputs = _candidate_identity(selection, inventory)
    _shape(build, {"schema_version", "outcome", "run_id", "completed_at", "candidate_identity", "candidate_sha256",
                   "identity_inputs", "source_commit", "profile", "runtime", "executing_implementation",
                   "mode_materialization", "installation", "behavioral_validation", "publication"})
    _one(build["schema_version"])
    _check(build["outcome"] == "assembled" and all(build[key] == "not-performed" for key in ("installation", "behavioral_validation", "publication")),
           "build-state", "Completion metadata does not describe an uninstalled assembled candidate.")
    _check(type(build["run_id"]) is str and re.fullmatch(r"[0-9a-f]{32}", build["run_id"]) is not None,
           "build-run", "Invalid build run identity.")
    try:
        stamp = datetime.fromisoformat(_text(build["completed_at"]))
        _check(stamp.utcoffset() is not None, "build-time", "Build timestamp needs an explicit offset.")
    except ValueError as exc:
        if isinstance(exc, InstallationError):
            raise
        raise InstallationError("build-time", "Invalid completion timestamp.") from None
    _check(build["candidate_identity"] == identity and build["candidate_sha256"] == identity.rsplit(":", 1)[1]
           and build["identity_inputs"] == identity_inputs and build["source_commit"] == selection["source"]["commit"]
           and build["profile"] == selection["profile"], "candidate-identity", "Candidate completion identity bindings disagree.")
    runtime = _shape(build["runtime"], {"python", "pyyaml", "os"})
    for value in runtime.values():
        _text(value)
    _check(runtime["os"] in {"posix", "nt"} and build["mode_materialization"] == ("posix-permissions" if runtime["os"] == "posix" else "inventory-only"),
           "build-mode", "Unsupported build platform/mode declaration.", outcome="unsupported")
    executing = _array(build["executing_implementation"])
    for item in executing:
        _shape(item, {"source", "execution_file_sha256"})
        _source(item["source"])
        _digest(item["execution_file_sha256"])
    _check([item["source"] for item in executing] == selection["generator"]["implementation"],
           "generator-binding", "Build execution provenance differs from selection.")
    return selection, inventory, build, members, identity


def read_candidate(candidate_root: str, *, _reader: _Reader | None = None) -> Candidate:
    """Read exact emitted candidate closure; no external source reproduction.

    Source/profile/generator identities are provenance. Public operation
    boundaries translate filesystem/format exceptions into safe diagnostics.
    """
    _check(sys.dont_write_bytecode, "bytecode-policy", "Start the host with -B before importing the reader; implicit bytecode writes are unsupported.", outcome="unsupported")
    reader = _reader or _Reader()
    root = _root(candidate_root)
    raw = {}
    for name in METADATA:
        target = reader.locate(root, name)
        _check(target is not None, "incomplete-candidate", "Candidate metadata document is missing.", name)
        raw[name] = reader.read(target, name, LIMITS["document_bytes"])
    selection, inventory, build, members, identity = _candidate_documents(raw)
    expected = set(METADATA) | {row["path"] for row in members.values()}
    directories = {"/".join(name.split("/")[:i]) for name in expected for i in range(1, len(name.split("/")))}
    pending, found = [(root, "")], set()
    while pending:
        directory, prefix = pending.pop()
        for entry in reader.listing(directory).values():
            name = prefix + entry
            _relative(name)
            info = (directory / entry).lstat()
            _plain(info, name)
            if stat.S_ISDIR(info.st_mode):
                _check(name in directories, "extra-candidate-directory", "Unexpected candidate directory.", name)
                pending.append((directory / entry, name + "/"))
            else:
                _check(name in expected and stat.S_ISREG(info.st_mode), "extra-candidate-file", "Unexpected/nonregular candidate member.", name)
                found.add(name)
    _check(found == expected, "candidate-closure", "Candidate file closure is incomplete.")
    policy = "posix-permissions" if os.name == "posix" else "windows-inventory-only"
    _check(os.name in {"posix", "nt"}, "unsupported-platform", "Reader platform is unsupported.", outcome="unsupported")
    contents = {destination: reader.member(root, row, policy) for destination, row in members.items()}
    _packages(selection, members, contents)
    return Candidate(root, identity, selection, inventory, build, raw, members, contents)


@dataclass(frozen=True)
class InstalledLock:
    document: dict
    raw: bytes
    sha256: str
    members: dict[str, dict]


def _lock_bytes(raw: bytes) -> InstalledLock:
    """One lock parser shared by live observation and durable operations."""
    document = _document(raw, LOCK_PATH)
    _shape(document, {"lock_version", "installation_id", "engine", "mode_policy", "candidate_identity", "selection", "inventory"})
    _one(document["lock_version"])
    _check(type(document["installation_id"]) is str and re.fullmatch(r"[0-9a-f]{32}", document["installation_id"]) is not None,
           "installation-identity", "Invalid stable installation identity.", LOCK_PATH)
    _engine_shape(document["engine"])
    _text(document["mode_policy"])
    _check(document["mode_policy"] in MODE_POLICIES, "mode-policy", "Unsupported installed mode policy.", LOCK_PATH, "unsupported")
    members = _selection_inventory(document["selection"], document["inventory"])
    identity, _ = _candidate_identity(document["selection"], document["inventory"])
    _check(document["candidate_identity"] == identity, "lock-identity", "Embedded candidate identity disagrees.", LOCK_PATH)
    return InstalledLock(document, raw, sha256(raw).hexdigest(), members)


def read_lock(project_root: str, *, _reader: _Reader | None = None) -> InstalledLock | None:
    """Read lock 1; absence confers no ownership. Does not establish file state."""
    reader = _reader or _Reader()
    root = _root(project_root)
    target = reader.locate(root, LOCK_PATH)
    if target is None:
        return None
    raw = reader.read(target, LOCK_PATH, LIMITS["document_bytes"])
    return _lock_bytes(raw)


@dataclass(frozen=True)
class Observation:
    root: Path
    lock: InstalledLock | None
    drift: list[dict]
    unknown: list[str] | None
    markers: list[str]


def _unknown(reader: _Reader, root: Path, names: set[str], owned: set[str]) -> list[str]:
    """Descend only declared parent paths inside selected managed package roots."""
    scopes = set()
    for name in names:
        parts = name.split("/")
        scopes.add("/".join(parts[:4] if name.startswith(".ai/core/skills/") else parts[:3]))
    parents = {"/".join(name.split("/")[:i]) for name in names for i in range(1, len(name.split("/")))}
    unknown = set()
    for scope in sorted(scopes):
        target = reader.locate(root, scope)
        if target is None:
            continue
        if not stat.S_ISDIR(target.lstat().st_mode):
            unknown.add(scope)
            continue
        pending = [(target, scope)]
        while pending:
            directory, prefix = pending.pop()
            for entry in reader.listing(directory).values():
                name = prefix + "/" + entry
                if name in names:
                    if name not in owned:
                        unknown.add(name)
                    continue
                info = (directory / entry).lstat()
                if name in parents:
                    _plain(info, name)
                    _check(stat.S_ISDIR(info.st_mode), "parent-collision", "Required parent is occupied.", name)
                    pending.append((directory / entry, name))
                else:
                    # Preserve unknown directories/links without opening or following them.
                    unknown.add(name + ("/" if stat.S_ISDIR(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400 else ""))
    return sorted(unknown)


def observe_installation(project_root: str, candidate: Candidate | None = None,
                         *, _reader: _Reader | None = None) -> Observation:
    """Observe every old member, including unchanged ones, and bounded siblings."""
    reader = _reader or _Reader()
    root = _root(project_root)
    markers = []
    for name in MARKERS:
        try:
            if reader.locate(root, name) is not None:
                markers.append(name)
        except InstallationError as exc:
            if exc.diagnostic["code"] in {"scan-limit", "read-limit"}:
                raise
            markers.append(name)
        except OSError:
            # Inaccessible control paths never look like absent maintenance.
            markers.append(name)
    if markers:
        return Observation(root, None, [], None, sorted(markers))
    lock = read_lock(project_root, _reader=reader)
    old = lock.members if lock else {}
    names = set(old) | (set(candidate.members) if candidate else set())
    drift, contents = [], {}
    if lock:
        policy = lock.document["mode_policy"]
        _check((os.name, policy) in {("posix", "posix-permissions"), ("nt", "windows-inventory-only")},
               "mode-platform", "Installed mode policy cannot be established on this platform.", outcome="unsupported")
        for name, row in sorted(old.items()):
            try:
                contents[name] = reader.member(root, {**row, "path": name}, policy)
            except InstallationError as exc:
                if exc.diagnostic["code"] not in {"missing-member", "member-drift", "mode-drift", "linked-path", "hardlinked-file", "not-regular", "parent-collision", "path-alias", "input-drift"}:
                    raise
                drift.append({"path": name, "reason": exc.diagnostic["code"]})
        if not drift:
            _packages(lock.document["selection"], old, contents)
    unknown = _unknown(reader, root, names, set(old)) if not drift else None
    return Observation(root, lock, drift, unknown, [])


def _head(reader: _Reader, root: Path) -> str:
    """Read standard files-backend Git HEAD without tools or a repository scan.

    Reftable, chained symrefs and custom layouts are explicitly unsupported.
    This observes checkout provenance, not object authenticity or loaded memory.
    """
    git_path = root / ".git"
    _no_links(git_path)
    if stat.S_ISREG(git_path.lstat().st_mode):
        declaration = reader.read(git_path, None, 4096).decode("utf-8", errors="strict").strip()
        _check(declaration.startswith("gitdir: "), "unsupported-git-layout", "Unknown Git worktree declaration.", outcome="unsupported")
        locator = Path(declaration[8:])
        _check(locator.is_absolute(), "unsupported-git-layout", "Only absolute worktree Git directory locators are supported.", outcome="unsupported")
        git_path = _root(str(locator))
    _check(stat.S_ISDIR(git_path.lstat().st_mode), "unsupported-git-layout", "Git directory is unavailable.", outcome="unsupported")
    common = git_path
    common_file = git_path / "commondir"
    if common_file.exists():
        locator = reader.read(common_file, None, 4096).decode("utf-8", errors="strict").strip()
        # Git commondir may contain '..'; check ancestors before resolving.
        common = git_path / locator
        _no_links(common)
        common = _root(str(common.resolve(strict=True)))
    _check(not (common / "reftable").exists(), "unsupported-git-layout", "Reftable checkout identity is unsupported.", outcome="unsupported")
    head = reader.read(git_path / "HEAD", None, 4096).decode("ascii", errors="strict").strip()
    if not head.startswith("ref: "):
        return _oid(head)
    reference = head[5:]
    _relative(reference)
    _check(reference.startswith("refs/heads/"), "unsupported-git-layout", "HEAD must be detached or a direct local branch.", outcome="unsupported")
    for directory in (git_path, common):
        file_path = directory.joinpath(*reference.split("/"))
        if file_path.exists():
            return _oid(reader.read(file_path, None, 4096).decode("ascii", errors="strict").strip())
    packed = common / "packed-refs"
    _check(packed.exists(), "engine-head", "Engine branch identity is unavailable.")
    result = []
    for line in reader.read(packed, None, LIMITS["document_bytes"]).decode("ascii", errors="strict").splitlines():
        if line and not line.startswith(("#", "^")):
            fields = line.split(" ")
            if len(fields) == 2 and fields[1] == reference:
                result.append(_oid(fields[0]))
    _check(len(result) == 1, "engine-head", "Engine branch identity is missing or ambiguous.")
    return result[0]


def _engine(reader: _Reader, root: Path, pin: dict) -> None:
    _check(os.name in {"posix", "nt"}, "unsupported-platform", "Reader platform is unsupported.", outcome="unsupported")
    _check(sys.dont_write_bytecode, "bytecode-policy", "Start the host with -B before importing product/dependency modules.", outcome="unsupported")
    _engine_shape(pin)
    _check(tuple(row["path"] for row in pin["files"]) == ENGINE_FILES,
           "unsupported-engine-closure", "Pin must name the complete source maintenance engine closure exactly.", outcome="unsupported")
    _check(Path(__file__).resolve().parents[2] == root, "executing-engine-root", "Explicit engine root differs from executing reader checkout.")
    bootstrap = sys.modules.get("__main__")
    _check(getattr(bootstrap, "_framework_bootstrap", None) == (str(root), pin)
           and Path(getattr(bootstrap, "__file__", "")).resolve() == root / "src/tools/maintain_framework.py",
           "engine-bootstrap", "Use the fixed isolated source entry; caller imports alone do not establish bootstrap.", outcome="unsupported")
    _check(_head(reader, root) == pin["source_commit"], "engine-head", "Engine checkout HEAD differs from the explicit pin.")
    for row in pin["files"]:
        target = reader.locate(root, row["path"])
        _check(target is not None, "engine-file", "Pinned engine file is missing.", row["path"])
        _check(sha256(reader.read(target, row["path"])).hexdigest() == row["sha256"], "engine-drift", "Engine execution bytes differ from pin.", row["path"])
        module_name = ("__main__" if row["path"] == "src/tools/maintain_framework.py" else
                       __package__ if row["path"].endswith("/__init__.py") else
                       __package__ + "." + Path(row["path"]).stem)
        module = sys.modules.get(module_name)
        if module is not None:
            _check(getattr(module, "__file__", None) is not None and Path(module.__file__).resolve() == target,
                   "engine-module-origin", "Loaded module originates outside the pinned checkout.", row["path"])

    expected_modules = {__package__} | {__package__ + "." + Path(name).stem
                       for name in ENGINE_FILES if name.startswith("src/distribution/") and not name.endswith("/__init__.py")}
    actual_modules = {name for name in sys.modules if name == __package__ or name.startswith(__package__ + ".")}
    _check(actual_modules == expected_modules, "engine-import-closure",
           "Loaded local package modules differ from the closed maintenance engine.", outcome="unsupported")


def _roots_disjoint(roots: dict[str, Path]) -> None:
    for name, root in roots.items():
        for other_name, other in roots.items():
            if name >= other_name:
                continue
            if {name, other_name} == {"scratch", "staging"} and root == other:
                continue
            left, right = root.stat(), other.stat()
            _check(not root.is_relative_to(other) and not other.is_relative_to(root)
                   and (left.st_dev, left.st_ino) != (right.st_dev, right.st_ino),
                   "root-overlap", "Selected roots overlap or alias; only identical scratch/staging parents may be shared.")


def _request(request: Any, operation: str, extra: set[str], optional: set[str] = frozenset()) -> dict:
    if type(request) is bytes:
        request = _document(request, "request.json", canonical=False)
    _bounded(request)
    raw = json_bytes(request)
    _check(len(raw) <= LIMITS["document_bytes"], "request-limit", "Request exceeds byte limit.")
    request = _document(raw, "request.json")
    _shape(request, {"api_version", "operation", "project_root", "engine_root", "engine"} | extra, optional)
    _one(request["api_version"])
    _check(request["operation"] == operation, "unsupported-operation", "Request operation is unsupported by this function.", outcome="unsupported")
    return request


def _failure(operation: str, exc: Exception, details: dict | None = None) -> dict:
    if isinstance(exc, InstallationError):
        outcome, diagnostic = exc.outcome, exc.diagnostic
    else:
        outcome = "blocked"
        diagnostic = {"code": "unreadable-input", "path": None,
                      "reason": "Input is inaccessible, malformed or changed during observation.",
                      "next_action": "Reconcile explicit inputs and runtime prerequisites; no partial result was accepted."}
    return {"api_version": 1, "operation": operation, "outcome": outcome,
            "changed": False, "details": details, "diagnostics": [diagnostic]}


def inspect(request: dict | bytes) -> dict:
    """Closed API 1 inspect request/result; always read-only and not-assessed."""
    empty = {"managed_state": "blocked", "project_readiness": "not-assessed", "owned": None,
             "unknown": None, "drift": None, "mode_policy": None}
    try:
        request = _request(request, "inspect", set(), {"candidate_root"})
        reader = _Reader()
        roots = {"project": _root(request["project_root"]), "engine": _root(request["engine_root"])}
        if "candidate_root" in request:
            roots["candidate"] = _root(request["candidate_root"])
        _roots_disjoint(roots)
        _engine(reader, roots["engine"], request["engine"])
        candidate = read_candidate(request["candidate_root"], _reader=reader) if "candidate" in roots else None
        observation = observe_installation(request["project_root"], candidate, _reader=reader)
        if observation.markers:
            return {"api_version": 1, "operation": "inspect", "outcome": "inspected", "changed": False,
                    "details": {**empty, "managed_state": "recovery-needed"},
                    "diagnostics": [{"code": "maintenance-marker", "path": name, "reason": "Maintenance marker is present or inaccessible.",
                                     "next_action": "Keep affected capabilities inactive and use the assigned recovery owner."} for name in observation.markers]}
        lock = observation.lock
        details = {"managed_state": "drift" if observation.drift else ("managed-bytes-consistent" if lock else "uninstalled"),
                   "project_readiness": "not-assessed", "owned": lock.document["inventory"]["files"] if lock else [],
                   "unknown": observation.unknown, "drift": observation.drift,
                   "mode_policy": lock.document["mode_policy"] if lock else None}
        return {"api_version": 1, "operation": "inspect", "outcome": "inspected", "changed": False,
                "details": details, "diagnostics": []}
    except (InstallationError, OSError, UnicodeError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        result = _failure("inspect", exc, empty)
        result["details"]["managed_state"] = result["outcome"]
        return result
