#!/usr/bin/env python3
"""Deterministic Git-tree-backed AI context package support."""

from __future__ import annotations

import gzip
import hashlib
import io
import os
import re
import subprocess
import tarfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable

import yaml


VERSION_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REGULAR_MODES = {"100644": 0o644, "100755": 0o755}
ZIP_MINIMUM_EPOCH = int(datetime(1980, 1, 1, tzinfo=timezone.utc).timestamp())
REPOSITORY_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\.dev|\.ai|\.agents|\.claude|\.codex|\.github)/"
    r"[A-Za-z0-9._*/{}<>-]+(?:/[A-Za-z0-9._*/{}<>-]+)*/?"
)
DEFAULT_SELECTION = {
    "release_model": "single-versioned-componentized-release",
    "mandatory_components": [
        "software-development-core",
        "ai-context-lifecycle-core",
    ],
    "profiles": ["dotnet-backend"],
    "providers": {
        "repo-backlog": {
            "enabled": False,
            "preservation": "preserve-existing-if-recorded",
        }
    },
}
DEFAULT_COMPONENT_IDS = {
    "software-development-core",
    "ai-context-lifecycle-core",
    "dotnet-backend",
    "repo-backlog",
}


class PackageError(ValueError):
    """A fail-closed package contract violation."""


@dataclass(frozen=True)
class GitEntry:
    path: str
    mode: str
    object_type: str
    object_id: str


@dataclass(frozen=True)
class PayloadFile:
    path: str
    source_path: str
    content: bytes
    mode: int
    ownership: str
    install_behavior: str
    entry_id: str
    component_id: str

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.content)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def run_git(repo: Path, *args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo, check=False, capture_output=True, text=text
    )


def resolve_commit(repo: Path, ref: str) -> str:
    result = run_git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    commit = result.stdout.strip() if result.returncode == 0 else ""
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise PackageError(f"cannot resolve immutable commit from ref {ref!r}")
    return commit


def commit_epoch(repo: Path, commit: str) -> int:
    result = run_git(repo, "show", "-s", "--format=%ct", commit)
    value = result.stdout.strip() if result.returncode == 0 else ""
    if not value.isdigit():
        raise PackageError(f"cannot read source date epoch for {commit}")
    return int(value)


def git_tree(repo: Path, commit: str) -> dict[str, GitEntry]:
    result = run_git(repo, "ls-tree", "-r", "-z", "--full-tree", commit, text=False)
    if result.returncode != 0:
        raise PackageError(result.stderr.decode(errors="replace").strip() or "git ls-tree failed")
    entries: dict[str, GitEntry] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        header, raw_path = record.split(b"\t", 1)
        mode, object_type, object_id = header.decode("ascii").split(" ")
        path = raw_path.decode("utf-8")
        entries[path] = GitEntry(path, mode, object_type, object_id)
    return entries


class GitObjectReader:
    """Read immutable Git blobs once through a single batch process."""

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self._blob_cache: dict[str, bytes] = {}
        self.batch_process_count = 0

    @staticmethod
    def _validate_entry(entry: GitEntry) -> None:
        if entry.object_type != "blob" or entry.mode not in REGULAR_MODES:
            raise PackageError(
                f"unsupported Git entry {entry.path}: mode={entry.mode} type={entry.object_type}"
            )

    def read_blobs_batch(self, entries: Iterable[GitEntry]) -> dict[str, bytes]:
        ordered_ids: list[str] = []
        for entry in entries:
            self._validate_entry(entry)
            if entry.object_id not in self._blob_cache and entry.object_id not in ordered_ids:
                ordered_ids.append(entry.object_id)
        if not ordered_ids:
            return self._blob_cache

        process = subprocess.Popen(
            ["git", "cat-file", "--batch-command", "--buffer"],
            cwd=self.repo,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.batch_process_count += 1
        assert process.stdin is not None and process.stdout is not None and process.stderr is not None
        try:
            for object_id in ordered_ids:
                process.stdin.write(f"contents {object_id}\n".encode("ascii"))
            process.stdin.write(b"flush\n")
            process.stdin.flush()

            for expected_id in ordered_ids:
                header = process.stdout.readline()
                try:
                    object_id, object_type, size_text = header.decode("ascii").strip().split(" ")
                    size = int(size_text)
                except (UnicodeDecodeError, ValueError) as exc:
                    raise PackageError(
                        f"invalid Git batch response while reading {expected_id}: {header!r}"
                    ) from exc
                if object_id != expected_id or object_type != "blob" or size < 0:
                    raise PackageError(
                        f"unexpected Git batch response for {expected_id}: {header!r}"
                    )
                content = process.stdout.read(size)
                separator = process.stdout.read(1)
                if len(content) != size or separator != b"\n":
                    raise PackageError(f"truncated Git batch payload for {expected_id}")
                self._blob_cache[expected_id] = content
        finally:
            process.stdin.close()
            returncode = process.wait()
            stderr = process.stderr.read().decode("utf-8", errors="replace").strip()
            process.stdout.close()
            process.stderr.close()
        if returncode != 0:
            raise PackageError(stderr or "git cat-file batch reader failed")
        return self._blob_cache

    def read_blob(self, entry: GitEntry) -> bytes:
        self._validate_entry(entry)
        self.read_blobs_batch((entry,))
        return self._blob_cache[entry.object_id]


@dataclass
class PackageRepositorySnapshot:
    """One immutable source snapshot shared by package construction and tests."""

    repo: Path
    commit: str
    epoch: int
    tree: dict[str, GitEntry]
    blob_reader: GitObjectReader

    @classmethod
    def from_ref(cls, repo: Path, ref: str) -> "PackageRepositorySnapshot":
        resolved_repo = repo.resolve()
        commit = resolve_commit(resolved_repo, ref)
        snapshot = cls(
            repo=resolved_repo,
            commit=commit,
            epoch=commit_epoch(resolved_repo, commit),
            tree=git_tree(resolved_repo, commit),
            blob_reader=GitObjectReader(resolved_repo),
        )
        snapshot.blob_reader.read_blobs_batch(
            entry
            for entry in snapshot.tree.values()
            if entry.object_type == "blob" and entry.mode in REGULAR_MODES
        )
        return snapshot


def git_blob(repo: Path, entry: GitEntry, reader: GitObjectReader | None = None) -> bytes:
    if entry.object_type != "blob" or entry.mode not in REGULAR_MODES:
        raise PackageError(
            f"unsupported Git entry {entry.path}: mode={entry.mode} type={entry.object_type}"
        )
    if reader is not None:
        return reader.read_blob(entry)
    result = run_git(repo, "cat-file", "blob", entry.object_id, text=False)
    if result.returncode != 0:
        raise PackageError(f"cannot read Git blob {entry.object_id} for {entry.path}")
    return result.stdout


def compile_glob(pattern: str) -> re.Pattern[str]:
    """Compile repository-relative glob syntax where * does not cross a slash."""
    expression = ""
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                index += 2
                if index < len(pattern) and pattern[index] == "/":
                    expression += "(?:.*/)?"
                    index += 1
                else:
                    expression += ".*"
                continue
            expression += "[^/]*"
        elif char == "?":
            expression += "[^/]"
        else:
            expression += re.escape(char)
        index += 1
    return re.compile(f"^{expression}$")


def patterns(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise PackageError("source or pattern field must be a string or list of strings")


def matches(path: str, pattern: str) -> bool:
    return bool(compile_glob(pattern).fullmatch(path))


def is_excluded(path: str, exclusions: list[dict]) -> bool:
    for exclusion in exclusions:
        denied = any(matches(path, item) for item in patterns(exclusion.get("patterns")))
        restored = any(matches(path, item) for item in patterns(exclusion.get("except", [])))
        if denied and not restored:
            return True
    return False


def safe_relative_path(value: str, label: str) -> str:
    if not value or "\\" in value:
        raise PackageError(f"{label} must be a non-empty POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise PackageError(f"unsafe {label}: {value!r}")
    return path.as_posix()


def static_prefix(pattern: str) -> str:
    wildcard = min((pattern.find(token) for token in ("*", "?") if token in pattern), default=-1)
    if wildcard < 0:
        return pattern.rsplit("/", 1)[0] + "/" if "/" in pattern else ""
    slash = pattern.rfind("/", 0, wildcard)
    return pattern[: slash + 1] if slash >= 0 else ""


def load_yaml_blob(
    repo: Path,
    tree: dict[str, GitEntry],
    path: str,
    reader: GitObjectReader | None = None,
) -> dict:
    entry = tree.get(path)
    if entry is None:
        raise PackageError(f"missing required Git-tree file: {path}")
    try:
        value = yaml.safe_load(git_blob(repo, entry, reader).decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise PackageError(f"cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PackageError(f"{path} root must be a mapping")
    return value


def add_payload_file(files: dict[str, PayloadFile], candidate: PayloadFile) -> None:
    target = safe_relative_path(candidate.path, "target path")
    if target in files:
        previous = files[target]
        raise PackageError(
            f"output collision at {target}: {previous.source_path} and {candidate.source_path}"
        )
    files[target] = candidate


def infer_legacy_component(entry_id: str, target_path: str | None = None) -> str:
    if entry_id == "backlog-governance" or (
        isinstance(target_path, str) and target_path.startswith(".dev/backlog/")
    ):
        return "repo-backlog"
    if entry_id == "dotnet-validation-tools":
        return "dotnet-backend"
    if entry_id in {
        "ai-entry-documents",
        "assessment-governance",
        "public-root-and-catalog-seeds",
    }:
        return "ai-context-lifecycle-core"
    return "software-development-core"


def resolve_entry_component(
    entry: dict,
    source_path: str,
    default_component: str,
    component_ids: set[str],
) -> str:
    overrides = entry.get("component_overrides", [])
    if not isinstance(overrides, list):
        raise PackageError(f"{entry.get('id')}: component_overrides must be a list")
    matched: list[str] = []
    for index, override in enumerate(overrides):
        if not isinstance(override, dict):
            raise PackageError(
                f"{entry.get('id')}: component_overrides[{index}] must be a mapping"
            )
        override_patterns = patterns(override.get("patterns"))
        component_id = override.get("component_id")
        if not isinstance(component_id, str) or component_id not in component_ids:
            raise PackageError(
                f"{entry.get('id')}: component_overrides[{index}] has unknown "
                f"component_id {component_id!r}"
            )
        if any(matches(source_path, pattern) for pattern in override_patterns):
            matched.append(component_id)
    if len(matched) > 1:
        raise PackageError(
            f"{entry.get('id')}: ambiguous component overrides for {source_path}"
        )
    return matched[0] if matched else default_component


def collect_payload(
    repo: Path,
    tree: dict[str, GitEntry],
    profile: dict,
    reader: GitObjectReader | None = None,
) -> list[PayloadFile]:
    exclusions = profile.get("exclusions")
    entries = profile.get("entries")
    if not isinstance(exclusions, list) or not isinstance(entries, list):
        raise PackageError("profile entries and exclusions must be lists")
    output: dict[str, PayloadFile] = {}
    components = profile.get("components")
    if components is None:
        component_ids = DEFAULT_COMPONENT_IDS
    else:
        if not isinstance(components, list):
            raise PackageError("profile components must be a list")
        component_ids = {
            item.get("component_id")
            for item in components
            if isinstance(item, dict) and isinstance(item.get("component_id"), str)
        }
        if len(component_ids) != len(components):
            raise PackageError("profile component IDs must be unique non-empty strings")

    for entry in entries:
        entry_id = entry.get("id")
        ownership = entry.get("ownership")
        behavior = entry.get("install_behavior")
        if not all(
            isinstance(value, str) and value
            for value in (entry_id, ownership, behavior)
        ):
            raise PackageError(
                "each profile entry requires id, ownership, and install_behavior"
            )
        component_id = entry.get("component_id") or infer_legacy_component(entry_id)
        if component_id not in component_ids:
            raise PackageError(f"{entry_id}: unknown component_id {component_id!r}")
        target_rule = entry.get("target")
        if target_rule == "mapping-declared-by-template-manifest":
            manifest_path = entry.get("template_manifest")
            if not isinstance(manifest_path, str):
                raise PackageError(f"{entry_id}: template_manifest is required")
            manifest = load_yaml_blob(repo, tree, manifest_path, reader)
            source_root = manifest.get("source_root", ".")
            if source_root != ".":
                raise PackageError(f"{manifest_path}: only manifest-relative source_root '.' is supported")
            base = PurePosixPath(manifest_path).parent
            mappings = manifest.get("mappings")
            if not isinstance(mappings, list):
                raise PackageError(f"{manifest_path}: mappings must be a list")
            for mapping in mappings:
                source_value, target_value = mapping.get("source"), mapping.get("target")
                mapping_component_id = mapping.get("component_id") or infer_legacy_component(
                    entry_id, target_value
                )
                if not isinstance(source_value, str) or not isinstance(target_value, str):
                    raise PackageError(f"{manifest_path}: mapping source and target must be strings")
                if mapping_component_id not in component_ids:
                    raise PackageError(
                        f"{manifest_path}: mapping has unknown component_id "
                        f"{mapping_component_id!r}"
                    )
                source_path = safe_relative_path((base / source_value).as_posix(), "template source")
                target_path = safe_relative_path(target_value, "template target")
                source_entry = tree.get(source_path)
                if source_entry is None:
                    raise PackageError(f"missing mapped template source: {source_path}")
                add_payload_file(
                    output,
                    PayloadFile(
                        target_path,
                        source_path,
                        git_blob(repo, source_entry, reader),
                        REGULAR_MODES[source_entry.mode],
                        ownership,
                        behavior,
                        entry_id,
                        mapping_component_id,
                    ),
                )
            continue

        matched = 0
        for source_pattern in patterns(entry.get("source")):
            prefix = static_prefix(source_pattern)
            for source_path in sorted(tree, key=lambda item: item.encode("utf-8")):
                if not matches(source_path, source_pattern) or is_excluded(source_path, exclusions):
                    continue
                source_entry = tree[source_path]
                content = git_blob(repo, source_entry, reader)
                if target_rule == "preserve-relative-path":
                    target_path = source_path
                elif isinstance(target_rule, str) and target_rule.endswith("/"):
                    relative = source_path[len(prefix) :] if prefix and source_path.startswith(prefix) else PurePosixPath(source_path).name
                    target_path = f"{target_rule}{relative}"
                elif isinstance(target_rule, str) and len(patterns(entry.get("source"))) == 1 and "*" not in source_pattern and "?" not in source_pattern:
                    target_path = target_rule
                else:
                    raise PackageError(f"{entry_id}: unsupported target mapping {target_rule!r}")
                add_payload_file(
                    output,
                    PayloadFile(
                        safe_relative_path(target_path, "target path"),
                        source_path,
                        content,
                        REGULAR_MODES[source_entry.mode],
                        ownership,
                        behavior,
                        entry_id,
                        resolve_entry_component(
                            entry,
                            source_path,
                            component_id,
                            component_ids,
                        ),
                    ),
                )
                matched += 1
        if matched == 0 and "allow_empty_until" not in entry:
            raise PackageError(f"{entry_id}: allowlist entry matched no Git-tree files")
    return sorted(output.values(), key=lambda item: item.path.encode("utf-8"))


def validate_payload_reference_integrity(files: Iterable[PayloadFile], profile: dict) -> None:
    contract = profile.get("reference_integrity")
    if not isinstance(contract, dict):
        raise PackageError("profile reference_integrity must be a mapping")
    extensions = contract.get("text_extensions")
    forbidden = contract.get("forbidden_source_lifecycle_patterns")
    if not isinstance(extensions, list) or not extensions or not all(
        isinstance(item, str) and item.startswith(".") for item in extensions
    ):
        raise PackageError("reference_integrity.text_extensions must be a non-empty extension list")
    if not isinstance(forbidden, list) or not forbidden or not all(
        isinstance(item, str) and item for item in forbidden
    ):
        raise PackageError(
            "reference_integrity.forbidden_source_lifecycle_patterns must be a non-empty list"
        )
    normalized_extensions = {item.lower() for item in extensions}
    violations: list[str] = []
    for item in files:
        if PurePosixPath(item.path).suffix.lower() not in normalized_extensions:
            continue
        try:
            text = item.content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PackageError(f"packaged text file is not UTF-8: {item.path}") from exc
        for match in REPOSITORY_PATH_RE.finditer(text):
            candidate = match.group(0)
            if any(token in candidate for token in ("*", "?", "<", ">", "{", "}")):
                continue
            values = {candidate, candidate.rstrip("/")}
            if any(matches(value, pattern) for value in values for pattern in forbidden):
                violations.append(f"{item.path} -> {candidate}")
    if violations:
        raise PackageError(
            "payload references excluded source lifecycle paths: " + "; ".join(sorted(set(violations)))
        )


def yaml_bytes(value: dict) -> bytes:
    return yaml.safe_dump(
        value, sort_keys=False, allow_unicode=True, default_flow_style=False
    ).encode("utf-8")


def payload_digest(files: Iterable[PayloadFile]) -> str:
    content = "".join(f"{item.sha256}  {item.path}\n" for item in files).encode("utf-8")
    return sha256_bytes(content)


def directory_members(paths: Iterable[str]) -> list[str]:
    directories: set[str] = set()
    for value in paths:
        path = PurePosixPath(value)
        for parent in path.parents:
            if parent.as_posix() != ".":
                directories.add(parent.as_posix() + "/")
    return sorted(directories, key=lambda item: item.encode("utf-8"))


def write_zip(path: Path, members: dict[str, tuple[bytes, int]], epoch: int) -> None:
    timestamp = datetime.fromtimestamp(max(epoch, ZIP_MINIMUM_EPOCH), tz=timezone.utc)
    date_time = (timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for directory in directory_members(members):
            info = zipfile.ZipInfo(directory, date_time)
            info.create_system = 3
            info.external_attr = (0o40755 & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, b"")
        for name in sorted(members, key=lambda item: item.encode("utf-8")):
            content, mode = members[name]
            info = zipfile.ZipInfo(name, date_time)
            info.create_system = 3
            info.external_attr = ((0o100000 | mode) & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def write_tar_gz(path: Path, members: dict[str, tuple[bytes, int]], epoch: int) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=raw, mtime=epoch) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for directory in directory_members(members):
                    info = tarfile.TarInfo(directory)
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    info.mtime = epoch
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    archive.addfile(info)
                for name in sorted(members, key=lambda item: item.encode("utf-8")):
                    content, mode = members[name]
                    info = tarfile.TarInfo(name)
                    info.size = len(content)
                    info.mode = mode
                    info.mtime = epoch
                    info.uid = info.gid = 0
                    info.uname = info.gname = "root"
                    archive.addfile(info, io.BytesIO(content))


def normalize_version(value: str) -> str:
    match = VERSION_RE.fullmatch(value)
    if match is None:
        raise PackageError("version must be MAJOR.MINOR.PATCH with optional v prefix")
    return ".".join(match.groups())


def validate_component_selection(selection: object, label: str) -> dict:
    if not isinstance(selection, dict):
        raise PackageError(f"{label} must be a mapping")
    if selection.get("release_model") != "single-versioned-componentized-release":
        raise PackageError(f"{label}.release_model is invalid")
    mandatory = selection.get("mandatory_components")
    if not isinstance(mandatory, list) or set(mandatory) != {
        "software-development-core",
        "ai-context-lifecycle-core",
    }:
        raise PackageError(f"{label} must include both mandatory cores")
    profiles = selection.get("profiles")
    if profiles != ["dotnet-backend"]:
        raise PackageError(f"{label}.profiles must select dotnet-backend")
    providers = selection.get("providers")
    backlog = providers.get("repo-backlog") if isinstance(providers, dict) else None
    if (
        not isinstance(backlog, dict)
        or not isinstance(backlog.get("enabled"), bool)
        or backlog.get("preservation") != "preserve-existing-if-recorded"
        or set(backlog) != {"enabled", "preservation"}
    ):
        raise PackageError(f"{label}.repo-backlog contract is invalid")
    return selection


def component_selection(profile: dict) -> dict:
    return validate_component_selection(
        profile.get("selection_defaults", DEFAULT_SELECTION),
        "profile selection_defaults",
    )


def inventory_document(
    payload_files: Iterable[PayloadFile],
    package_id: str,
    component_aware: bool,
) -> dict:
    records: list[dict] = []
    for item in payload_files:
        record = {
            "path": item.path,
            "source_path": item.source_path,
            "sha256": item.sha256,
            "size": len(item.content),
            "mode": f"{item.mode:04o}",
            "ownership": item.ownership,
            "install_behavior": item.install_behavior,
            "entry_id": item.entry_id,
        }
        if component_aware:
            record["component_id"] = item.component_id
        records.append(record)
    return {
        "schema_version": "2.0.0" if component_aware else "1.0.0",
        "package_id": package_id,
        "files": records,
    }


def load_previous_inventory(path: Path, expected_package_id: str) -> tuple[dict[str, dict], str]:
    try:
        content = path.read_bytes()
        document = yaml.safe_load(content)
    except (OSError, yaml.YAMLError) as exc:
        raise PackageError(f"cannot read previous files manifest: {exc}") from exc
    if (
        not isinstance(document, dict)
        or document.get("schema_version") not in {"1.0.0", "2.0.0"}
    ):
        raise PackageError("previous files manifest must use schema 1.0.0 or 2.0.0")
    if document.get("package_id") != expected_package_id:
        raise PackageError(
            "previous files manifest package_id does not match the declared previous version"
        )
    raw_records = document.get("files")
    if not isinstance(raw_records, list):
        raise PackageError("previous files manifest files must be a list")
    records: dict[str, dict] = {}
    order: list[str] = []
    for raw in raw_records:
        if not isinstance(raw, dict):
            raise PackageError("previous files manifest entries must be mappings")
        relative = safe_relative_path(raw.get("path"), "previous inventory path")
        if relative in records:
            raise PackageError(f"duplicate previous inventory path: {relative}")
        if not SHA256_RE.fullmatch(str(raw.get("sha256", ""))):
            raise PackageError(f"invalid previous inventory sha256: {relative}")
        if raw.get("mode") not in {"0644", "0755"}:
            raise PackageError(f"invalid previous inventory mode: {relative}")
        if raw.get("ownership") not in {"framework-managed", "target-template"}:
            raise PackageError(f"invalid previous inventory ownership: {relative}")
        if not isinstance(raw.get("size"), int) or raw["size"] < 0:
            raise PackageError(f"invalid previous inventory size: {relative}")
        if document.get("schema_version") == "2.0.0" and (
            not isinstance(raw.get("component_id"), str)
            or not raw["component_id"]
        ):
            raise PackageError(f"missing previous inventory component_id: {relative}")
        records[relative] = raw
        order.append(relative)
    if order != sorted(order, key=lambda item: item.encode("utf-8")):
        raise PackageError("previous inventory paths must use UTF-8 bytewise order")
    return records, sha256_bytes(content)


def migration_source_inputs(
    previous_files_path: Path | None,
    previous_version_value: str | None,
    previous_sources: Iterable[tuple[Path, str]] | None,
) -> list[tuple[str, Path]]:
    if (previous_files_path is None) != (previous_version_value is None):
        raise PackageError(
            "previous files manifest and previous version must be supplied together"
        )
    candidates: list[tuple[str, Path]] = []
    if previous_files_path is not None and previous_version_value is not None:
        candidates.append(
            (normalize_version(previous_version_value), previous_files_path.resolve())
        )
    for candidate in previous_sources or []:
        if (
            not isinstance(candidate, tuple)
            or len(candidate) != 2
            or not isinstance(candidate[0], Path)
            or not isinstance(candidate[1], str)
        ):
            raise PackageError(
                "each previous source must be a (files Path, version string) tuple"
            )
        files_path, version_value = candidate
        candidates.append((normalize_version(version_value), files_path.resolve()))
    versions: set[str] = set()
    for version, _ in candidates:
        if version in versions:
            raise PackageError(f"duplicate migration source version: {version}")
        versions.add(version)
    return sorted(
        candidates,
        key=lambda item: tuple(int(part) for part in item[0].split(".")),
    )


def migration_operations(
    previous: dict[str, dict],
    incoming_files: Iterable[PayloadFile],
) -> list[dict]:
    incoming = {
        item.path: {
            "sha256": item.sha256,
            "mode": f"{item.mode:04o}",
            "ownership": item.ownership,
            "component_id": item.component_id,
        }
        for item in incoming_files
    }
    removed = set(previous) - set(incoming)
    added = set(incoming) - set(previous)

    previous_signatures: dict[tuple[str, str, str], list[str]] = {}
    incoming_signatures: dict[tuple[str, str, str], list[str]] = {}
    for path in removed:
        record = previous[path]
        if record.get("ownership") == "framework-managed":
            signature = (record["sha256"], record["mode"], record["ownership"])
            previous_signatures.setdefault(signature, []).append(path)
    for path in added:
        record = incoming[path]
        if record["ownership"] == "framework-managed":
            signature = (record["sha256"], record["mode"], record["ownership"])
            incoming_signatures.setdefault(signature, []).append(path)

    renamed_sources: set[str] = set()
    renamed_destinations: set[str] = set()
    operations: list[dict] = []
    for signature in sorted(set(previous_signatures) & set(incoming_signatures)):
        sources = sorted(previous_signatures[signature], key=lambda item: item.encode("utf-8"))
        destinations = sorted(incoming_signatures[signature], key=lambda item: item.encode("utf-8"))
        if len(sources) != 1 or len(destinations) != 1:
            continue
        source, destination = sources[0], destinations[0]
        renamed_sources.add(source)
        renamed_destinations.add(destination)
        operations.append(
            {
                "kind": "rename",
                "path": destination,
                "from_path": source,
                "ownership": "framework-managed",
                "component_id": incoming[destination]["component_id"],
                "preconditions": [
                    "source_sha256_equals_previous_release",
                    "destination_absent",
                ],
            }
        )

    for path in sorted(set(previous) & set(incoming), key=lambda item: item.encode("utf-8")):
        before, after = previous[path], incoming[path]
        if all(before.get(key) == after.get(key) for key in ("sha256", "mode", "ownership")):
            continue
        if before.get("ownership") == after.get("ownership") == "framework-managed":
            operations.append(
                {
                    "kind": "replace",
                    "path": path,
                    "ownership": "framework-managed",
                    "component_id": after["component_id"],
                    "preconditions": ["current_sha256_equals_previous_release"],
                }
            )
        else:
            ownership = (
                "target-template"
                if "target-template" in {before.get("ownership"), after.get("ownership")}
                else str(after.get("ownership"))
            )
            operations.append(
                {
                    "kind": "reconcile",
                    "path": path,
                    "ownership": ownership,
                    "component_id": after["component_id"],
                    "preconditions": ["human_acknowledgement"],
                }
            )

    for path in sorted(added - renamed_destinations, key=lambda item: item.encode("utf-8")):
        operations.append(
            {
                "kind": "add",
                "path": path,
                "ownership": incoming[path]["ownership"],
                "component_id": incoming[path]["component_id"],
                "preconditions": ["destination_absent"],
            }
        )
    for path in sorted(removed - renamed_sources, key=lambda item: item.encode("utf-8")):
        ownership = previous[path].get("ownership")
        operations.append(
            {
                "kind": "remove" if ownership == "framework-managed" else "reconcile",
                "path": path,
                "ownership": ownership,
                "component_id": previous[path].get(
                    "component_id",
                    "repo-backlog"
                    if path.startswith(".dev/backlog/")
                    else "software-development-core",
                ),
                "preconditions": [
                    "current_sha256_equals_previous_release"
                    if ownership == "framework-managed"
                    else "human_acknowledgement"
                ],
            }
        )

    operations.sort(
        key=lambda item: (
            item["path"].encode("utf-8"),
            item["kind"],
            str(item.get("from_path", "")).encode("utf-8"),
        )
    )
    return [
        {"id": f"migration-{index:04d}", **operation}
        for index, operation in enumerate(operations, 1)
    ]


def build_package(
    repo: Path,
    ref: str,
    version_value: str,
    output_dir: Path,
    profile_path: str = ".ai/distribution/profiles/dotnet-backend.yaml",
    previous_files_path: Path | None = None,
    previous_version_value: str | None = None,
    previous_sources: Iterable[tuple[Path, str]] | None = None,
) -> dict[str, Path | str]:
    snapshot = PackageRepositorySnapshot.from_ref(repo, ref)
    repo = snapshot.repo
    commit = snapshot.commit
    epoch = snapshot.epoch
    tree = snapshot.tree
    profile = load_yaml_blob(repo, tree, profile_path, snapshot.blob_reader)
    version = normalize_version(version_value)
    profile_id = profile.get("profile", {}).get("id")
    name_template = profile.get("package", {}).get("name_template")
    source_repository = profile.get("package", {}).get("source_repository")
    if not all(isinstance(item, str) and item for item in (profile_id, name_template, source_repository)):
        raise PackageError("profile package identity is incomplete")
    package_id = name_template.format(version=version)
    source_inputs = migration_source_inputs(
        previous_files_path,
        previous_version_value,
        previous_sources,
    )
    release_path = f".dev/releases/v{version}/release.yaml"
    release = load_yaml_blob(repo, tree, release_path, snapshot.blob_reader)
    if release.get("version") != f"v{version}":
        raise PackageError(f"{release_path}: version must equal v{version}")
    distribution = release.get("distribution")
    if not isinstance(distribution, dict):
        raise PackageError(f"{release_path}: distribution must be a mapping")
    if distribution.get("profile_id") != profile_id:
        raise PackageError(
            f"{release_path}: distribution.profile_id must equal {profile_id}"
        )
    if distribution.get("package_id") != package_id:
        raise PackageError(
            f"{release_path}: distribution.package_id must equal {package_id}"
        )
    compatibility = release.get("compatibility")
    if not isinstance(compatibility, dict):
        raise PackageError(f"{release_path}: compatibility must be a mapping")
    minimum_source = compatibility.get("minimum_source_version")
    if not isinstance(minimum_source, str):
        raise PackageError(
            f"{release_path}: compatibility.minimum_source_version must be a version"
        )
    try:
        minimum_source = f"v{normalize_version(minimum_source)}"
    except ValueError as exc:
        raise PackageError(
            f"{release_path}: compatibility.minimum_source_version is invalid"
        ) from exc
    breaking_changes = compatibility.get("breaking_changes")
    if not isinstance(breaking_changes, bool):
        raise PackageError(
            f"{release_path}: compatibility.breaking_changes must be boolean"
        )
    automatic_sources = compatibility.get("automatic_upgrade_sources")
    if not isinstance(automatic_sources, list) or not all(
        isinstance(item, str) for item in automatic_sources
    ):
        raise PackageError(
            f"{release_path}: compatibility.automatic_upgrade_sources must be a list"
        )
    try:
        automatic_sources = [f"v{normalize_version(item)}" for item in automatic_sources]
    except ValueError as exc:
        raise PackageError(
            f"{release_path}: compatibility.automatic_upgrade_sources is invalid"
        ) from exc
    expected_sources = [f"v{source_version}" for source_version, _ in source_inputs]
    if automatic_sources != expected_sources:
        raise PackageError(
            f"{release_path}: automatic upgrade sources {automatic_sources} do not "
            f"match package migration sources {expected_sources}"
        )
    payload_files = collect_payload(repo, tree, profile, snapshot.blob_reader)
    if not payload_files:
        raise PackageError("package payload is empty")
    validate_payload_reference_integrity(payload_files, profile)
    selection = component_selection(profile)
    component_aware = profile.get("schema_version") == "2.0.0"

    file_document = inventory_document(payload_files, package_id, component_aware)
    files_content = yaml_bytes(file_document)
    files_sha = sha256_bytes(files_content)
    created_at = datetime.fromtimestamp(epoch, timezone.utc).isoformat().replace("+00:00", "Z")
    package_document = {
        "schema_version": "2.0.0" if component_aware else "1.0.0",
        "package_id": package_id,
        "profile_id": profile_id,
        "version": version,
        "release_id": f"REL-v{version}",
        "source": {"repository": source_repository, "ref": commit, "commit": commit},
        "created_at": created_at,
        "source_date_epoch": epoch,
        "payload": {
            "root": "payload",
            "file_count": len(payload_files),
            "sha256": payload_digest(payload_files),
        },
        "compatibility": {
            "minimum_governed_source": minimum_source,
            "breaking_changes": breaking_changes,
            "automatic_upgrade_sources": automatic_sources,
        },
    }
    if component_aware:
        package_document["selection"] = selection
    clean_install_operations = []
    for index, item in enumerate(payload_files, 1):
        operation = {
            "id": f"clean-install-{index:04d}",
            "kind": "add",
            "path": item.path,
            "ownership": item.ownership,
            "preconditions": ["destination_absent"],
        }
        if component_aware:
            operation["component_id"] = item.component_id
        clean_install_operations.append(operation)
    migration_sources: list[dict] = []
    for previous_version, source_path in source_inputs:
        previous_package_id = name_template.format(version=previous_version)
        previous, previous_sha = load_previous_inventory(
            source_path, previous_package_id
        )
        migration_sources.append(
            {
                "version": previous_version,
                "manifest_sha256": previous_sha,
                "operations": migration_operations(previous, payload_files),
            }
        )
    migration_document = {
        "schema_version": "3.0.0" if component_aware else "2.0.0",
        "package_id": package_id,
        "to": {"version": version, "manifest_sha256": files_sha},
        "clean_install": {"operations": clean_install_operations},
        "sources": migration_sources,
        "safety": {
            "dry_run_default": True,
            "clean_worktree_required": True,
            "starting_commit_required": True,
            "abort_on_unacknowledged_reconciliation": True,
        },
    }
    if component_aware:
        migration_document["selection"] = selection
    install_entry = tree.get(".ai/distribution/templates/INSTALL.md")
    if install_entry is None:
        raise PackageError("missing package INSTALL.md template")
    requirements_entry = tree.get(".ai/distribution/templates/requirements.txt")
    if requirements_entry is None:
        raise PackageError("missing package requirements.txt template")

    relative_members: dict[str, tuple[bytes, int]] = {
        "INSTALL.md": (git_blob(repo, install_entry, snapshot.blob_reader), 0o644),
        "requirements.txt": (git_blob(repo, requirements_entry, snapshot.blob_reader), 0o644),
        "metadata/package.yaml": (yaml_bytes(package_document), 0o644),
        "metadata/files.yaml": (files_content, 0o644),
        "metadata/migration.yaml": (yaml_bytes(migration_document), 0o644),
    }
    for item in payload_files:
        relative_members[f"payload/{item.path}"] = (item.content, item.mode)
    checksum_lines = "".join(
        f"{sha256_bytes(relative_members[name][0])}  {name}\n"
        for name in sorted(relative_members, key=lambda item: item.encode("utf-8"))
    ).encode("utf-8")
    relative_members["metadata/SHA256SUMS.txt"] = (checksum_lines, 0o644)
    members = {f"{package_id}/{name}": value for name, value in relative_members.items()}

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{package_id}.zip"
    tar_path = output_dir / f"{package_id}.tar.gz"
    for candidate in (zip_path, tar_path, Path(f"{zip_path}.sha256"), Path(f"{tar_path}.sha256")):
        if candidate.exists():
            raise PackageError(f"refusing to overwrite existing output: {candidate}")
    write_zip(zip_path, members, epoch)
    write_tar_gz(tar_path, members, epoch)
    for archive_path in (zip_path, tar_path):
        digest = sha256_bytes(archive_path.read_bytes())
        Path(f"{archive_path}.sha256").write_text(
            f"{digest}  {archive_path.name}\n", encoding="utf-8", newline="\n"
        )
    return {
        "package_id": package_id,
        "commit": commit,
        "zip": zip_path,
        "tar_gz": tar_path,
    }


def archive_files(path: Path) -> dict[str, tuple[bytes, int]]:
    files: dict[str, tuple[bytes, int]] = {}
    if path.name.endswith(".zip"):
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                safe_relative_path(info.filename, "archive member")
                files[info.filename] = (archive.read(info), (info.external_attr >> 16) & 0o777)
    elif path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            for info in archive.getmembers():
                if info.isdir():
                    continue
                if not info.isfile():
                    raise PackageError(f"unsupported tar member type: {info.name}")
                safe_relative_path(info.name, "archive member")
                stream = archive.extractfile(info)
                if stream is None:
                    raise PackageError(f"cannot read tar member: {info.name}")
                files[info.name] = (stream.read(), info.mode & 0o777)
    else:
        raise PackageError(f"unsupported archive: {path}")
    return files


def validate_migration_metadata(migration: dict, files_sha: str) -> None:
    to_data = migration.get("to")
    if (
        not isinstance(to_data, dict)
        or normalize_version(str(to_data.get("version", "")))
        != str(to_data.get("version", ""))
        or to_data.get("manifest_sha256") != files_sha
    ):
        raise PackageError("migration target identity does not match files.yaml")
    schema_version = migration.get("schema_version")
    if schema_version == "1.0.0":
        if not isinstance(migration.get("from"), dict) or not isinstance(
            migration.get("operations"), list
        ):
            raise PackageError("migration schema 1.0.0 requires from and operations")
        return
    if schema_version not in {"2.0.0", "3.0.0"}:
        raise PackageError(f"unsupported migration schema version: {schema_version!r}")
    if schema_version == "3.0.0":
        validate_component_selection(migration.get("selection"), "migration selection")
    clean_install = migration.get("clean_install")
    sources = migration.get("sources")
    if not isinstance(clean_install, dict) or not isinstance(
        clean_install.get("operations"), list
    ):
        raise PackageError("migration clean_install.operations must be a list")
    if not isinstance(sources, list):
        raise PackageError("migration sources must be a list")
    operation_lists = [clean_install["operations"]]
    identities: set[tuple[str, str]] = set()
    versions: set[str] = set()
    source_order: list[tuple[int, int, int]] = []
    for source in sources:
        if not isinstance(source, dict):
            raise PackageError("migration sources must be mappings")
        version = normalize_version(str(source.get("version", "")))
        digest = source.get("manifest_sha256")
        if source.get("version") != version:
            raise PackageError("migration source version must omit the v prefix")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise PackageError("migration source manifest_sha256 must be lowercase SHA-256")
        if not isinstance(source.get("operations"), list):
            raise PackageError("migration source operations must be a list")
        operation_lists.append(source["operations"])
        identity = (version, digest)
        if version in versions or identity in identities:
            raise PackageError(f"duplicate or ambiguous migration source: {version}")
        versions.add(version)
        identities.add(identity)
        source_order.append(tuple(int(part) for part in version.split(".")))
    if source_order != sorted(source_order):
        raise PackageError("migration sources must use semantic-version order")
    if schema_version == "3.0.0":
        for operations in operation_lists:
            for operation in operations:
                if (
                    not isinstance(operation, dict)
                    or not isinstance(operation.get("component_id"), str)
                    or not operation["component_id"]
                ):
                    raise PackageError(
                        "migration schema 3 operations require component_id"
                    )


def validate_archive(path: Path) -> dict[str, tuple[bytes, int]]:
    members = archive_files(path)
    roots = {PurePosixPath(name).parts[0] for name in members}
    if len(roots) != 1:
        raise PackageError("archive must contain exactly one envelope root")
    root = next(iter(roots))
    prefix = f"{root}/"
    required = {
        f"{prefix}INSTALL.md",
        f"{prefix}requirements.txt",
        f"{prefix}metadata/package.yaml",
        f"{prefix}metadata/files.yaml",
        f"{prefix}metadata/migration.yaml",
        f"{prefix}metadata/SHA256SUMS.txt",
    }
    missing = required - members.keys()
    if missing:
        raise PackageError(f"archive missing required members: {sorted(missing)}")
    checksums = members[f"{prefix}metadata/SHA256SUMS.txt"][0].decode("utf-8").splitlines()
    expected: dict[str, str] = {}
    for line in checksums:
        digest, relative = line.split("  ", 1)
        if not SHA256_RE.fullmatch(digest) or relative in expected:
            raise PackageError("invalid or duplicate SHA256SUMS entry")
        expected[relative] = digest
    checksum_relative = "metadata/SHA256SUMS.txt"
    actual_relative = {
        name[len(prefix) :]: sha256_bytes(content)
        for name, (content, _) in members.items()
        if name != f"{prefix}{checksum_relative}"
    }
    if expected != actual_relative:
        raise PackageError("SHA256SUMS does not exactly cover all other envelope files")
    package = yaml.safe_load(members[f"{prefix}metadata/package.yaml"][0])
    inventory = yaml.safe_load(members[f"{prefix}metadata/files.yaml"][0])
    migration = yaml.safe_load(members[f"{prefix}metadata/migration.yaml"][0])
    if not all(isinstance(item, dict) for item in (package, inventory, migration)):
        raise PackageError("package metadata roots must be mappings")
    if package.get("package_id") != root or inventory.get("package_id") != root or migration.get("package_id") != root:
        raise PackageError("package identity mismatch")
    package_schema = package.get("schema_version")
    if package_schema not in {"1.0.0", "2.0.0"}:
        raise PackageError(f"unsupported package schema version: {package_schema!r}")
    if package_schema == "2.0.0":
        validate_component_selection(package.get("selection"), "package selection")
    inventory_schema = inventory.get("schema_version")
    if inventory_schema not in {"1.0.0", "2.0.0"}:
        raise PackageError(f"unsupported files schema version: {inventory_schema!r}")
    validate_migration_metadata(
        migration,
        sha256_bytes(members[f"{prefix}metadata/files.yaml"][0]),
    )
    records = inventory.get("files")
    if not isinstance(records, list):
        raise PackageError("files.yaml files must be a list")
    inventory_paths: set[str] = set()
    payload_items: list[PayloadFile] = []
    for record in records:
        if (
            inventory_schema == "2.0.0"
            and (
                not isinstance(record.get("component_id"), str)
                or not record["component_id"]
            )
        ):
            raise PackageError("files schema 2 entries require component_id")
        target = safe_relative_path(record.get("path"), "inventory path")
        if target in inventory_paths:
            raise PackageError(f"duplicate inventory path: {target}")
        inventory_paths.add(target)
        member_name = f"{prefix}payload/{target}"
        if member_name not in members:
            raise PackageError(f"inventory path missing from payload: {target}")
        content, mode = members[member_name]
        if record.get("sha256") != sha256_bytes(content) or record.get("size") != len(content):
            raise PackageError(f"inventory hash or size mismatch: {target}")
        if record.get("mode") != f"{mode:04o}":
            raise PackageError(f"inventory mode mismatch: {target}")
        payload_items.append(
            PayloadFile(
                target,
                str(record.get("source_path")),
                content,
                mode,
                str(record.get("ownership")),
                str(record.get("install_behavior")),
                str(record.get("entry_id")),
                str(record.get("component_id", "legacy-unclassified")),
            )
        )
    archive_payload_paths = {
        name[len(f"{prefix}payload/") :]
        for name in members
        if name.startswith(f"{prefix}payload/")
    }
    if inventory_paths != archive_payload_paths:
        raise PackageError("payload and files.yaml path sets differ")
    payload_meta = package.get("payload", {})
    if payload_meta.get("file_count") != len(records) or payload_meta.get("sha256") != payload_digest(payload_items):
        raise PackageError("package payload count or digest mismatch")
    return members


def validate_sidecar(path: Path) -> None:
    sidecar = Path(f"{path}.sha256")
    if not sidecar.is_file():
        raise PackageError(f"missing archive checksum sidecar: {sidecar}")
    line = sidecar.read_text(encoding="utf-8").strip()
    digest, filename = line.split("  ", 1)
    if filename != path.name or digest != sha256_bytes(path.read_bytes()):
        raise PackageError(f"archive checksum sidecar mismatch: {sidecar}")
