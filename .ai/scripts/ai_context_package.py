#!/usr/bin/env python3
"""Deterministic Git-tree-backed AI context package support."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import posixpath
import re
import subprocess
import tarfile
import urllib.parse
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
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
MARKDOWN_REFERENCE_DEFINITION_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(\S+)")
MARKDOWN_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
MARKDOWN_SETEXT_RE = re.compile(r"^\s{0,3}(?:=+|-+)\s*$")
MARKDOWN_HTML_ID_RE = re.compile(r"\bid=[\"']([^\"']+)[\"']", re.IGNORECASE)
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
ACTIONABLE_COMMAND_RE = re.compile(
    r"^\s*(?:(?:[-*+]|\d+[.)])\s+|>\s*)*(?:\$\s*)?"
    r"(?:python(?:3)?|bash|sh|pwsh|powershell(?:\.exe)?)\b",
    re.IGNORECASE,
)
REPOSITORY_ROOT_PREFIXES = (".ai/", ".dev/", ".agents/", ".claude/", ".codex/", ".github/")
PLACEHOLDER_TOKENS = ("*", "?", "<", ">", "{", "}")
COMPONENT_PACKAGE_SCHEMAS = {"2.0.0", "2.1.0", "2.2.0"}
IDENTITY_PACKAGE_SCHEMAS = {"1.1.0", "2.1.0", "2.2.0"}
PAYLOAD_USER_VIEW_CLASSIFICATIONS = {
    "markdown_local_links": "required-local-navigation",
    "markdown_anchors": "required-local-anchor",
    "component_cross_links": "navigation-only-not-activation",
    "fenced_code": "non-actionable-example-unless-command",
    "inline_code": "non-actionable-reference-unless-command",
    "templates_and_placeholders": "non-actionable-template",
    "external_urls": "external-not-validated",
    "actionable_local_commands": "required-local-target",
}
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


def commit_tree_sha(repo: Path, commit: str) -> str:
    result = run_git(repo, "rev-parse", "--verify", f"{commit}^{{tree}}")
    tree_sha = result.stdout.strip() if result.returncode == 0 else ""
    if not re.fullmatch(r"[0-9a-f]{40}", tree_sha):
        raise PackageError(f"cannot read tree identity for {commit}")
    return tree_sha


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

    def list_tree(self, commit: str) -> dict[str, GitEntry]:
        """Read one commit tree through the same repository boundary."""
        return git_tree(self.repo, commit)

    def read_commit_metadata(self, commit: str) -> dict[str, int | str]:
        """Return immutable commit facts used by package identity."""
        return {
            "commit_sha": commit,
            "tree_sha": commit_tree_sha(self.repo, commit),
            "source_date_epoch": commit_epoch(self.repo, commit),
        }


@dataclass
class PackageRepositorySnapshot:
    """One immutable source snapshot shared by package construction and tests."""

    repo: Path
    commit: str
    tree_sha: str
    epoch: int
    tree: dict[str, GitEntry]
    blob_reader: GitObjectReader

    @classmethod
    def from_ref(cls, repo: Path, ref: str) -> "PackageRepositorySnapshot":
        resolved_repo = repo.resolve()
        commit = resolve_commit(resolved_repo, ref)
        reader = GitObjectReader(resolved_repo)
        metadata = reader.read_commit_metadata(commit)
        snapshot = cls(
            repo=resolved_repo,
            commit=commit,
            tree_sha=str(metadata["tree_sha"]),
            epoch=int(metadata["source_date_epoch"]),
            tree=reader.list_tree(commit),
            blob_reader=reader,
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


def _is_placeholder(value: str) -> bool:
    return any(token in value for token in PLACEHOLDER_TOKENS)


def _decode_payload_text(item: PayloadFile) -> str:
    try:
        return item.content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackageError(f"packaged text file is not UTF-8: {item.path}") from exc


def _visible_markdown_lines(text: str) -> list[tuple[int, str]]:
    visible: list[tuple[int, str]] = []
    fence_character: str | None = None
    fence_length = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        marker = MARKDOWN_FENCE_RE.match(line)
        if marker is not None:
            token = marker.group(1)
            if fence_character is None:
                fence_character = token[0]
                fence_length = len(token)
            elif token[0] == fence_character and len(token) >= fence_length:
                fence_character = None
                fence_length = 0
            continue
        if fence_character is None:
            visible.append((line_number, line))
    return visible


def _strip_inline_code(line: str) -> str:
    return INLINE_CODE_RE.sub("", line)


def _markdown_destination(value: str) -> str:
    destination = value.strip()
    if destination.startswith("<") and ">" in destination:
        destination = destination[1 : destination.index(">")]
    elif destination:
        destination = destination.split()[0]
    return urllib.parse.unquote(destination)


def _resolve_markdown_target(source_path: str, raw_destination: str) -> tuple[str | None, str]:
    destination = _markdown_destination(raw_destination)
    if not destination:
        return source_path, ""
    if destination.startswith("//") or re.match(
        r"^[A-Za-z][A-Za-z0-9+.-]*:", destination
    ):
        return None, ""
    path_and_query, separator, fragment = destination.partition("#")
    path_value = path_and_query.split("?", 1)[0]
    if not separator:
        fragment = ""
    if not path_value:
        target = source_path
    elif path_value.startswith("/") or "\\" in path_value:
        return "..", fragment
    elif path_value.startswith(REPOSITORY_ROOT_PREFIXES):
        target = posixpath.normpath(path_value)
    else:
        target = posixpath.normpath(
            posixpath.join(posixpath.dirname(source_path), path_value)
        )
    if target == ".." or target.startswith("../"):
        return "..", fragment
    return target, fragment


def _target_payload_items(
    files_by_path: dict[str, PayloadFile], target: str
) -> list[PayloadFile]:
    exact = files_by_path.get(target.rstrip("/"))
    if exact is not None:
        return [exact]
    prefix = target.rstrip("/") + "/"
    return [item for path, item in files_by_path.items() if path.startswith(prefix)]


def _github_heading_slug(value: str) -> str:
    value = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(
        r"</?(?:a|span|br|code|kbd|em|strong|sup|sub|details|summary)\b[^>]*>",
        "",
        value,
        flags=re.IGNORECASE,
    )
    value = value.replace("`", "").replace("*", "").replace("~", "")
    normalized = "".join(
        character
        for character in value.casefold()
        if character.isalnum() or character.isspace() or character in {"-", "_"}
    )
    return re.sub(r"\s+", "-", normalized)


def _markdown_anchors(text: str) -> set[str]:
    visible = _visible_markdown_lines(text)
    anchors: set[str] = set()
    counts: dict[str, int] = {}

    def add_heading(value: str) -> None:
        base = _github_heading_slug(value)
        if not base:
            return
        occurrence = counts.get(base, 0)
        counts[base] = occurrence + 1
        anchors.add(base if occurrence == 0 else f"{base}-{occurrence}")

    previous_line = ""
    for _, line in visible:
        anchors.update(MARKDOWN_HTML_ID_RE.findall(line))
        heading = MARKDOWN_HEADING_RE.match(line)
        if heading is not None:
            add_heading(heading.group(1))
        elif MARKDOWN_SETEXT_RE.match(line) and previous_line.strip():
            add_heading(previous_line.strip())
        previous_line = line
    return anchors


def _normalized_components(profile: dict) -> list[dict]:
    raw_components = profile.get("components")
    if not isinstance(raw_components, list) or not raw_components:
        raise PackageError("profile components must be a non-empty list")
    normalized: list[dict] = []
    for index, component in enumerate(raw_components):
        if not isinstance(component, dict):
            raise PackageError(f"profile components[{index}] must be a mapping")
        normalized.append(
            {
                "component_id": component.get("component_id"),
                "classification": component.get("classification"),
                "required": component.get("required"),
                "requires": component.get("requires"),
            }
        )
    return normalized


def payload_user_view_contract(profile: dict) -> dict:
    reference_integrity = profile.get("reference_integrity")
    user_view = profile.get("payload_user_view")
    if not isinstance(reference_integrity, dict):
        raise PackageError("profile reference_integrity must be a mapping")
    if not isinstance(user_view, dict):
        raise PackageError("profile payload_user_view must be a mapping")
    return {
        "schema_version": user_view.get("schema_version"),
        "classifications": user_view.get("classifications"),
        "reference_integrity": {
            "text_extensions": reference_integrity.get("text_extensions"),
            "forbidden_source_lifecycle_patterns": reference_integrity.get(
                "forbidden_source_lifecycle_patterns"
            ),
        },
        "components": _normalized_components(profile),
        "supported_selections": user_view.get("supported_selections"),
        "capabilities": user_view.get("capabilities"),
    }


def _validate_user_view_structure(contract: object) -> tuple[dict[str, dict], dict[str, set[str]], list[dict]]:
    if not isinstance(contract, dict) or contract.get("schema_version") != "1.0.0":
        raise PackageError("payload user_view must use schema 1.0.0")
    if contract.get("classifications") != PAYLOAD_USER_VIEW_CLASSIFICATIONS:
        raise PackageError("payload user_view classifications are missing or weakened")
    reference = contract.get("reference_integrity")
    if not isinstance(reference, dict):
        raise PackageError("payload user_view reference_integrity must be a mapping")
    extensions = reference.get("text_extensions")
    forbidden = reference.get("forbidden_source_lifecycle_patterns")
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

    raw_components = contract.get("components")
    if not isinstance(raw_components, list) or not raw_components:
        raise PackageError("payload user_view components must be a non-empty list")
    components: dict[str, dict] = {}
    for component in raw_components:
        if not isinstance(component, dict):
            raise PackageError("payload user_view component entries must be mappings")
        component_id = component.get("component_id")
        requires = component.get("requires")
        if (
            not isinstance(component_id, str)
            or not component_id
            or component_id in components
            or not isinstance(component.get("classification"), str)
            or not isinstance(component.get("required"), bool)
            or not isinstance(requires, list)
            or len(requires) != len(set(requires))
            or not all(isinstance(item, str) and item for item in requires)
        ):
            raise PackageError("payload user_view component contract is invalid or ambiguous")
        components[component_id] = component
    for component_id, component in components.items():
        for dependency in component["requires"]:
            if dependency == component_id or dependency not in components:
                raise PackageError(
                    f"component {component_id} has invalid dependency {dependency!r}"
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(component_id: str) -> None:
        if component_id in visiting:
            raise PackageError(f"component dependency cycle includes {component_id}")
        if component_id in visited:
            return
        visiting.add(component_id)
        for dependency in components[component_id]["requires"]:
            visit(dependency)
        visiting.remove(component_id)
        visited.add(component_id)

    for component_id in components:
        visit(component_id)

    raw_selections = contract.get("supported_selections")
    if not isinstance(raw_selections, list) or not raw_selections:
        raise PackageError("payload user_view supported_selections must be a non-empty list")
    required_components = {
        component_id
        for component_id, component in components.items()
        if component["required"]
    }
    selections: dict[str, set[str]] = {}
    for selection in raw_selections:
        if not isinstance(selection, dict):
            raise PackageError("payload user_view selection entries must be mappings")
        selection_id = selection.get("selection_id")
        selected = selection.get("components")
        if (
            not isinstance(selection_id, str)
            or not selection_id
            or selection_id in selections
            or not isinstance(selected, list)
            or len(selected) != len(set(selected))
            or not all(isinstance(item, str) and item in components for item in selected)
        ):
            raise PackageError("payload user_view supported selection is invalid or ambiguous")
        selected_set = set(selected)
        if not required_components.issubset(selected_set):
            raise PackageError(f"selection {selection_id} omits a required component")
        for component_id in selected_set:
            if not set(components[component_id]["requires"]).issubset(selected_set):
                raise PackageError(
                    f"selection {selection_id} is not closed under {component_id} dependencies"
                )
        selections[selection_id] = selected_set

    capabilities = contract.get("capabilities")
    if not isinstance(capabilities, list):
        raise PackageError("payload user_view capabilities must be a list")
    capability_ids: set[str] = set()
    for capability in capabilities:
        if not isinstance(capability, dict):
            raise PackageError("payload user_view capability entries must be mappings")
        capability_id = capability.get("capability_id")
        owner_component = capability.get("owner_component")
        path_patterns = capability.get("path_patterns")
        availability = capability.get("availability")
        if (
            not isinstance(capability_id, str)
            or not capability_id
            or capability_id in capability_ids
            or owner_component not in components
            or not isinstance(path_patterns, list)
            or not path_patterns
            or not all(isinstance(item, str) and item for item in path_patterns)
            or not isinstance(availability, dict)
            or set(availability) != set(selections)
        ):
            raise PackageError("payload user_view capability contract is invalid or ambiguous")
        for selection_id, selected in selections.items():
            expected = "available" if owner_component in selected else "unavailable-not-selected"
            if availability.get(selection_id) != expected:
                raise PackageError(
                    f"capability {capability_id} availability is invalid for {selection_id}"
                )
        capability_ids.add(capability_id)
    return components, selections, capabilities


def _validate_markdown_navigation(
    files: list[PayloadFile], files_by_path: dict[str, PayloadFile]
) -> None:
    anchors = {
        item.path: _markdown_anchors(_decode_payload_text(item))
        for item in files
        if PurePosixPath(item.path).suffix.lower() == ".md"
    }
    missing: list[str] = []
    invalid_anchors: list[str] = []
    unsafe: list[str] = []
    for item in files:
        if PurePosixPath(item.path).suffix.lower() != ".md":
            continue
        text = _decode_payload_text(item)
        for line_number, line in _visible_markdown_lines(text):
            visible_line = _strip_inline_code(line)
            destinations = [
                match.group(1) for match in MARKDOWN_LINK_RE.finditer(visible_line)
            ]
            definition = MARKDOWN_REFERENCE_DEFINITION_RE.match(visible_line)
            if definition is not None:
                destinations.append(definition.group(1))
            for destination in destinations:
                if _is_placeholder(destination):
                    continue
                target, fragment = _resolve_markdown_target(item.path, destination)
                if target is None:
                    continue
                evidence = f"{item.path}:{line_number} -> {destination}"
                if target == "..":
                    unsafe.append(evidence)
                    continue
                targets = _target_payload_items(files_by_path, target)
                if not targets:
                    missing.append(evidence)
                    continue
                if fragment:
                    exact = files_by_path.get(target)
                    if (
                        exact is None
                        or PurePosixPath(exact.path).suffix.lower() != ".md"
                        or fragment not in anchors.get(exact.path, set())
                    ):
                        invalid_anchors.append(evidence)
    if unsafe:
        raise PackageError(
            "payload Markdown navigation escapes the payload root: "
            + "; ".join(sorted(set(unsafe)))
        )
    if missing:
        raise PackageError(
            "payload Markdown navigation targets are missing: "
            + "; ".join(sorted(set(missing)))
        )
    if invalid_anchors:
        raise PackageError(
            "payload Markdown anchors are missing: "
            + "; ".join(sorted(set(invalid_anchors)))
        )


def _validate_actionable_markdown_commands(
    files: list[PayloadFile], files_by_path: dict[str, PayloadFile]
) -> None:
    missing: list[str] = []
    for item in files:
        if PurePosixPath(item.path).suffix.lower() != ".md":
            continue
        for line_number, line in enumerate(_decode_payload_text(item).splitlines(), 1):
            probes = [line, *(match.group(2) for match in INLINE_CODE_RE.finditer(line))]
            for probe in probes:
                if ACTIONABLE_COMMAND_RE.match(probe) is None:
                    continue
                for match in REPOSITORY_PATH_RE.finditer(probe):
                    candidate = match.group(0)
                    if _is_placeholder(candidate):
                        continue
                    if not _target_payload_items(files_by_path, candidate):
                        missing.append(f"{item.path}:{line_number} -> {candidate}")
    if missing:
        raise PackageError(
            "payload actionable command targets are missing: "
            + "; ".join(sorted(set(missing)))
        )


def _validate_component_capabilities(
    files: list[PayloadFile],
    files_by_path: dict[str, PayloadFile],
    components: dict[str, dict],
    selections: dict[str, set[str]],
    capabilities: list[dict],
) -> None:
    unknown = sorted({item.component_id for item in files} - set(components))
    if unknown:
        raise PackageError(f"payload files use unknown components: {unknown}")
    for capability in capabilities:
        capability_id = capability["capability_id"]
        owner_component = capability["owner_component"]
        matched = [
            item
            for item in files
            if any(matches(item.path, pattern) for pattern in capability["path_patterns"])
        ]
        if not matched:
            raise PackageError(f"capability {capability_id} path patterns matched no payload files")
        wrong_component = sorted(
            item.path for item in matched if item.component_id != owner_component
        )
        if wrong_component:
            raise PackageError(
                f"capability {capability_id} is not owned entirely by {owner_component}: "
                + "; ".join(wrong_component)
            )
        references: list[tuple[str, str, list[PayloadFile]]] = []
        for item in matched:
            if PurePosixPath(item.path).suffix.lower() not in {
                ".md",
                ".yaml",
                ".yml",
                ".json",
                ".toml",
                ".txt",
                ".sh",
                ".ps1",
            }:
                continue
            for match in REPOSITORY_PATH_RE.finditer(_decode_payload_text(item)):
                candidate = match.group(0)
                if _is_placeholder(candidate):
                    continue
                targets = _target_payload_items(files_by_path, candidate)
                if not targets:
                    raise PackageError(
                        f"capability {capability_id} reference is missing: "
                        f"{item.path} -> {candidate}"
                    )
                references.append((item.path, candidate, targets))
        for selection_id, selected in selections.items():
            selected_paths = {
                item.path for item in files if item.component_id in selected
            }
            expected = capability["availability"][selection_id]
            selected_capability_paths = {item.path for item in matched} & selected_paths
            if expected == "unavailable-not-selected":
                if selected_capability_paths:
                    raise PackageError(
                        f"capability {capability_id} leaks into unavailable selection {selection_id}"
                    )
                continue
            if selected_capability_paths != {item.path for item in matched}:
                raise PackageError(
                    f"capability {capability_id} is incomplete in selection {selection_id}"
                )
            unresolved = sorted(
                f"{source} -> {candidate}"
                for source, candidate, targets in references
                if not any(target.path in selected_paths for target in targets)
            )
            if unresolved:
                raise PackageError(
                    f"capability {capability_id} references are not closed in {selection_id}: "
                    + "; ".join(unresolved)
                )


def validate_payload_user_view(files: Iterable[PayloadFile], contract: object) -> None:
    payload_files = list(files)
    files_by_path = {item.path: item for item in payload_files}
    if len(files_by_path) != len(payload_files):
        raise PackageError("payload user_view received duplicate target paths")
    components, selections, capabilities = _validate_user_view_structure(contract)
    reference = contract["reference_integrity"]
    normalized_extensions = {
        item.lower() for item in reference["text_extensions"]
    }
    forbidden = reference["forbidden_source_lifecycle_patterns"]
    lifecycle_violations: list[str] = []
    for item in payload_files:
        if PurePosixPath(item.path).suffix.lower() not in normalized_extensions:
            continue
        for match in REPOSITORY_PATH_RE.finditer(_decode_payload_text(item)):
            candidate = match.group(0)
            if _is_placeholder(candidate):
                continue
            values = {candidate, candidate.rstrip("/")}
            if any(matches(value, pattern) for value in values for pattern in forbidden):
                lifecycle_violations.append(f"{item.path} -> {candidate}")
    if lifecycle_violations:
        raise PackageError(
            "payload references excluded source lifecycle paths: "
            + "; ".join(sorted(set(lifecycle_violations)))
        )
    _validate_markdown_navigation(payload_files, files_by_path)
    _validate_actionable_markdown_commands(payload_files, files_by_path)
    _validate_component_capabilities(
        payload_files, files_by_path, components, selections, capabilities
    )


def _validate_legacy_payload_reference_integrity(
    files: Iterable[PayloadFile], profile: dict
) -> None:
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
        for match in REPOSITORY_PATH_RE.finditer(_decode_payload_text(item)):
            candidate = match.group(0)
            if _is_placeholder(candidate):
                continue
            values = {candidate, candidate.rstrip("/")}
            if any(matches(value, pattern) for value in values for pattern in forbidden):
                violations.append(f"{item.path} -> {candidate}")
    if violations:
        raise PackageError(
            "payload references excluded source lifecycle paths: "
            + "; ".join(sorted(set(violations)))
        )


def validate_payload_reference_integrity(files: Iterable[PayloadFile], profile: dict) -> None:
    if isinstance(profile.get("payload_user_view"), dict):
        validate_payload_user_view(files, payload_user_view_contract(profile))
        return
    _validate_legacy_payload_reference_integrity(files, profile)


def yaml_bytes(value: dict) -> bytes:
    return yaml.safe_dump(
        value, sort_keys=False, allow_unicode=True, default_flow_style=False
    ).encode("utf-8")


def payload_digest(files: Iterable[PayloadFile]) -> str:
    content = "".join(f"{item.sha256}  {item.path}\n" for item in files).encode("utf-8")
    return sha256_bytes(content)


def identity_fingerprint(document: dict) -> str:
    """Hash canonical, typed identity inputs without serializing YAML formatting."""
    return sha256_bytes(
        json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )


def selected_input_fingerprint(
    source_inputs: dict[str, bytes],
    payload_files: Iterable[PayloadFile],
    migration_sources: Iterable[dict],
) -> str:
    """Fingerprint only bytes/configuration that can affect package output."""
    return identity_fingerprint(
        {
            "schema_version": "package-selected-input/v1",
            "source_inputs": [
                {"path": path, "sha256": sha256_bytes(content)}
                for path, content in sorted(
                    source_inputs.items(), key=lambda item: item[0].encode("utf-8")
                )
            ],
            "payload": [
                {
                    "path": item.path,
                    "sha256": item.sha256,
                    "mode": f"{item.mode:04o}",
                    "ownership": item.ownership,
                    "install_behavior": item.install_behavior,
                    "component_id": item.component_id,
                }
                for item in sorted(payload_files, key=lambda item: item.path.encode("utf-8"))
            ],
            "migration_sources": [
                {
                    "version": item["version"],
                    "manifest_sha256": item["manifest_sha256"],
                }
                for item in sorted(
                    migration_sources,
                    key=lambda item: str(item["version"]),
                )
            ],
        }
    )


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
    component_aware = profile.get("schema_version") == "2.0.0"
    user_view_contract = (
        payload_user_view_contract(profile)
        if isinstance(profile.get("payload_user_view"), dict)
        else None
    )
    validate_payload_reference_integrity(payload_files, profile)
    selection = component_selection(profile)

    file_document = inventory_document(payload_files, package_id, component_aware)
    files_content = yaml_bytes(file_document)
    files_sha = sha256_bytes(files_content)
    created_at = datetime.fromtimestamp(epoch, timezone.utc).isoformat().replace("+00:00", "Z")
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
    migration_content = yaml_bytes(migration_document)
    install_entry = tree.get(".ai/distribution/templates/INSTALL.md")
    if install_entry is None:
        raise PackageError("missing package INSTALL.md template")
    requirements_entry = tree.get(".ai/distribution/templates/requirements.txt")
    if requirements_entry is None:
        raise PackageError("missing package requirements.txt template")
    profile_entry = tree.get(profile_path)
    release_entry = tree.get(release_path)
    if profile_entry is None or release_entry is None:
        raise PackageError("package identity inputs are missing from the source tree")
    source_input_bytes = {
        profile_path: git_blob(repo, profile_entry, snapshot.blob_reader),
        release_path: git_blob(repo, release_entry, snapshot.blob_reader),
        ".ai/distribution/templates/INSTALL.md": git_blob(
            repo, install_entry, snapshot.blob_reader
        ),
        ".ai/distribution/templates/requirements.txt": git_blob(
            repo, requirements_entry, snapshot.blob_reader
        ),
    }
    payload_sha = payload_digest(payload_files)
    selected_inputs_sha = selected_input_fingerprint(
        source_input_bytes,
        payload_files,
        migration_sources,
    )
    package_document = {
        "schema_version": (
            "2.2.0"
            if component_aware and user_view_contract is not None
            else "2.1.0" if component_aware else "1.1.0"
        ),
        "package_id": package_id,
        "profile_id": profile_id,
        "version": version,
        "release_id": f"REL-v{version}",
        "source": {
            "repository": source_repository,
            "ref": commit,
            "commit": commit,
            "tree": snapshot.tree_sha,
        },
        "created_at": created_at,
        "source_date_epoch": epoch,
        "identity": {
            "schema_version": "1.0.0",
            "selected_input_fingerprint": selected_inputs_sha,
            "payload_fingerprint": payload_sha,
            "files_manifest_digest": files_sha,
            "migration_digest": sha256_bytes(migration_content),
        },
        "payload": {
            "root": "payload",
            "file_count": len(payload_files),
            "sha256": payload_sha,
        },
        "compatibility": {
            "minimum_governed_source": minimum_source,
            "breaking_changes": breaking_changes,
            "automatic_upgrade_sources": automatic_sources,
        },
    }
    if component_aware:
        package_document["selection"] = selection
    if user_view_contract is not None:
        package_document["user_view"] = user_view_contract

    relative_members: dict[str, tuple[bytes, int]] = {
        "INSTALL.md": (source_input_bytes[".ai/distribution/templates/INSTALL.md"], 0o644),
        "requirements.txt": (source_input_bytes[".ai/distribution/templates/requirements.txt"], 0o644),
        "metadata/package.yaml": (yaml_bytes(package_document), 0o644),
        "metadata/files.yaml": (files_content, 0o644),
        "metadata/migration.yaml": (migration_content, 0o644),
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
    archive_digests: dict[str, str] = {}
    for archive_path in (zip_path, tar_path):
        digest = sha256_bytes(archive_path.read_bytes())
        archive_digests[archive_path.name] = digest
        Path(f"{archive_path}.sha256").write_text(
            f"{digest}  {archive_path.name}\n", encoding="utf-8", newline="\n"
        )
    return {
        "package_id": package_id,
        "commit": commit,
        "tree": snapshot.tree_sha,
        "selected_input_fingerprint": selected_inputs_sha,
        "payload_fingerprint": payload_sha,
        "files_manifest_digest": files_sha,
        "migration_digest": sha256_bytes(migration_content),
        "zip": zip_path,
        "tar_gz": tar_path,
        "zip_digest": archive_digests[zip_path.name],
        "tar_digest": archive_digests[tar_path.name],
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
    if package_schema not in {"1.0.0", "1.1.0", *COMPONENT_PACKAGE_SCHEMAS}:
        raise PackageError(f"unsupported package schema version: {package_schema!r}")
    if package_schema in COMPONENT_PACKAGE_SCHEMAS:
        validate_component_selection(package.get("selection"), "package selection")
    identity = package.get("identity")
    if package_schema in IDENTITY_PACKAGE_SCHEMAS:
        source = package.get("source")
        if not isinstance(source, dict) or not all(
            isinstance(source.get(key), str) and re.fullmatch(r"[0-9a-f]{40}", source[key])
            for key in ("commit", "tree")
        ):
            raise PackageError("package source identity requires commit and tree SHA")
        if not isinstance(identity, dict) or identity.get("schema_version") != "1.0.0":
            raise PackageError("package identity schema is missing or unsupported")
        for key in (
            "selected_input_fingerprint",
            "payload_fingerprint",
            "files_manifest_digest",
            "migration_digest",
        ):
            if not isinstance(identity.get(key), str) or not SHA256_RE.fullmatch(identity[key]):
                raise PackageError(f"package identity has invalid {key}")
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
    if package_schema == "2.2.0":
        validate_payload_user_view(payload_items, package.get("user_view"))
    if package_schema in IDENTITY_PACKAGE_SCHEMAS and identity is not None:
        expected_identity = {
            "payload_fingerprint": payload_digest(payload_items),
            "files_manifest_digest": sha256_bytes(
                members[f"{prefix}metadata/files.yaml"][0]
            ),
            "migration_digest": sha256_bytes(
                members[f"{prefix}metadata/migration.yaml"][0]
            ),
        }
        for key, value in expected_identity.items():
            if identity.get(key) != value:
                raise PackageError(f"package identity {key} does not match archive bytes")
    return members


def validate_sidecar(path: Path) -> None:
    sidecar = Path(f"{path}.sha256")
    if not sidecar.is_file():
        raise PackageError(f"missing archive checksum sidecar: {sidecar}")
    line = sidecar.read_text(encoding="utf-8").strip()
    digest, filename = line.split("  ", 1)
    if filename != path.name or digest != sha256_bytes(path.read_bytes()):
        raise PackageError(f"archive checksum sidecar mismatch: {sidecar}")
