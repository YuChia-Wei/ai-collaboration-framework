"""Source-only admission and publication identity for exact release asset bytes."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path, PurePosixPath

import yaml

from ai_context_package import (
    PackageError, PackageRepositorySnapshot, canonical_json_bytes, collect_payload,
    git_blob, load_yaml_blob, selected_input_document, sha256_bytes,
    validate_archive, validate_sidecar,
)
from ai_context_package_identity import expected_rule

SCHEMA = "release-asset-admission/v1"
PROVIDER_SCHEMA = "release-asset-publication/v1"
PROFILE = ".ai/distribution/profiles/dotnet-backend.yaml"
SHA = re.compile(r"[0-9a-f]{64}\Z")


def governed(version: str) -> bool:
    if not re.fullmatch(r"v\d+\.\d+\.\d+", version):
        raise PackageError("release version must be vMAJOR.MINOR.PATCH")
    return tuple(map(int, version[1:].split("."))) >= (0, 16, 0)


def strict_json(raw: bytes) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise PackageError("duplicate JSON key")
            result[key] = value
        return result

    value = json.loads(raw, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise PackageError("identity record must be an object")
    return value


def contained(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise PackageError("asset path must be a contained POSIX relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or pure.as_posix() != value or any(p in {".", ".."} for p in pure.parts):
        raise PackageError("unsafe asset path")
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink() or getattr(current.lstat(), "st_file_attributes", 0) & 0x400:
            raise PackageError("asset path crosses a reparse point")
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise PackageError("asset is not a contained regular file")
    return current


def asset_names(version: str) -> list[str]:
    package_id = expected_rule(version[1:])["package_id"]
    return [package_id + suffix for suffix in (".zip", ".zip.sha256", ".tar.gz", ".tar.gz.sha256")]


def describe_assets(root: Path, directory: Path, version: str) -> tuple[list[dict], dict, dict]:
    records = []
    members = []
    for name in asset_names(version):
        path = contained(root, (directory / name).relative_to(root).as_posix())
        content = path.read_bytes()
        records.append({"name": name, "path": path.relative_to(root).as_posix(),
                        "size": len(content), "sha256": sha256_bytes(content)})
        if not name.endswith(".sha256"):
            validate_sidecar(path)
            members.append(validate_archive(path))
    if members[0] != members[1]:
        raise PackageError("admitted ZIP and tar members differ")
    package_id = expected_rule(version[1:])["package_id"]
    prefix = package_id + "/metadata/"
    metadata = yaml.safe_load(members[0][prefix + "package.yaml"][0])
    if metadata["version"] != version[1:] or metadata["release_id"] != "REL-" + version:
        raise PackageError("archive release identity disagrees with admission")
    selected = strict_json(members[0][prefix + "selected-inputs.json"][0])
    return records, metadata, selected


def make_admission(root: Path, directory: Path, version: str) -> dict:
    governed(version)
    records, metadata, _ = describe_assets(root, directory, version)
    identity = metadata["identity"]
    return {"schema_version": SCHEMA, "state": "admitted-candidate", "version": version,
            "package_id": metadata["package_id"], "release_id": metadata["release_id"],
            "build_commit": metadata["source"]["commit"],
            "payload_fingerprint": identity["payload_fingerprint"],
            "selected_input_fingerprint": identity["selected_input_fingerprint"],
            "artifact_set_id": "sha256:" + sha256_bytes(canonical_json_bytes([
                {k: item[k] for k in ("name", "size", "sha256")} for item in records])),
            "assets": records}


def check_admission(value: dict, version: str) -> None:
    keys = {"schema_version", "state", "version", "package_id", "release_id", "build_commit",
            "payload_fingerprint", "selected_input_fingerprint", "artifact_set_id", "assets"}
    if set(value) != keys or value.get("schema_version") != SCHEMA or value.get("state") != "admitted-candidate":
        raise PackageError("unsupported or incomplete asset admission")
    if (value["version"] != version or value["release_id"] != "REL-" + version
            or value["package_id"] != expected_rule(version[1:])["package_id"]):
        raise PackageError("admission logical identity mismatch")
    if not re.fullmatch(r"[0-9a-f]{40}", str(value["build_commit"])):
        raise PackageError("admission build provenance is missing")
    for key in ("payload_fingerprint", "selected_input_fingerprint"):
        if not isinstance(value[key], str) or not SHA.fullmatch(value[key]):
            raise PackageError("admission content fingerprint is invalid")
    assets = value["assets"]
    if not isinstance(assets, list) or [a.get("name") for a in assets if isinstance(a, dict)] != asset_names(version):
        raise PackageError("admission must identify exactly four ordered release assets")
    for asset in assets:
        if (set(asset) != {"name", "path", "size", "sha256"}
                or type(asset["size"]) is not int or asset["size"] <= 0
                or not isinstance(asset["sha256"], str) or not SHA.fullmatch(asset["sha256"])):
            raise PackageError("admission asset identity is invalid")
        if PurePosixPath(asset["path"]).name != asset["name"]:
            raise PackageError("admission asset name/path mismatch")
    expected = "sha256:" + sha256_bytes(canonical_json_bytes([
        {k: item[k] for k in ("name", "size", "sha256")} for item in assets]))
    if value["artifact_set_id"] != expected:
        raise PackageError("admission artifact set identity mismatch")


def verify_source(root: Path, version: str, ref: str, admission: dict, selected: dict) -> None:
    """Rebind selected bytes to a new commit without rebuilding the archive."""
    snapshot = PackageRepositorySnapshot.from_ref(root, ref)
    profile = load_yaml_blob(root, snapshot.tree, PROFILE, snapshot.blob_reader)
    paths = {PROFILE, f".dev/releases/{version}/release.yaml",
             ".ai/distribution/templates/INSTALL.md", ".ai/distribution/templates/requirements.txt",
             profile["package"]["identity_registry"]}
    inputs = {path: git_blob(root, snapshot.tree[path], snapshot.blob_reader) for path in paths}
    payload = collect_payload(root, snapshot.tree, profile, snapshot.blob_reader)
    current = selected_input_document(inputs, payload, selected["migration_sources"])
    if current != selected or sha256_bytes(canonical_json_bytes(current)) != admission["selected_input_fingerprint"]:
        raise PackageError("admitted selected inputs differ from the source ref; prepare a new candidate")


def verify_route_binding(matrix: dict, admission: dict) -> None:
    """The matrix and the publication transport must select one archive subject."""
    version = admission["version"]
    identity = {k: admission[k] for k in ("package_id", "release_id", "payload_fingerprint")}
    if not isinstance(matrix, dict) or matrix.get("target", {}).get("package_identity") != identity:
        raise PackageError("route target differs from admitted package identity")
    zip_digest = admission["assets"][0]["sha256"]
    matching = 0
    for route in matrix.get("routes", []):
        if route.get("target") != version:
            raise PackageError("route target version differs from admission")
        for edge in route.get("edges", []):
            if edge.get("to_version") == version:
                matching += 1
                if (edge.get("package_identity") != identity
                        or edge.get("artifacts", {}).get("archive", {}).get("sha256") != zip_digest):
                    raise PackageError("route archive differs from admitted publication bytes")
    if matching == 0:
        raise PackageError("admission has no bound incoming route")


def load_admission(root: Path, version: str, ref: str = "HEAD", *, verify_projection: bool = True) -> dict:
    governed(version)
    path = f".dev/releases/{version}/artifact-admission.json"
    snapshot = PackageRepositorySnapshot.from_ref(root, ref)
    if path not in snapshot.tree:
        raise PackageError("tracked exact-byte asset admission is missing")
    admission = strict_json(git_blob(root, snapshot.tree[path], snapshot.blob_reader))
    check_admission(admission, version)
    for asset in admission["assets"]:
        entry = snapshot.tree.get(asset["path"])
        if entry is None or sha256_bytes(git_blob(root, entry, snapshot.blob_reader)) != asset["sha256"]:
            raise PackageError("admitted asset is absent or different in the source ref")
    if governed(version):
        matrix_path = f".dev/releases/{version}/support-matrix.yaml"
        if matrix_path not in snapshot.tree:
            raise PackageError("admitted route matrix is missing")
        verify_route_binding(yaml.safe_load(git_blob(root, snapshot.tree[matrix_path], snapshot.blob_reader)), admission)
    directories = {str(PurePosixPath(asset["path"]).parent) for asset in admission["assets"]}
    if len(directories) != 1:
        raise PackageError("admitted assets must share one directory")
    directory = root / directories.pop()
    actual = make_admission(root, directory, version)
    if actual != admission:
        raise PackageError("local asset bytes or package identity differ from admission")
    if verify_projection:
        _, _, selected = describe_assets(root, directory, version)
        verify_source(root, version, ref, admission, selected)
    return admission


def verify_transported(root: Path, admission: dict, directory: Path) -> None:
    """Bind downloaded/uploaded bytes to the admission, including sidecars."""
    check_admission(admission, admission["version"])
    for asset in admission["assets"]:
        path = contained(directory, asset["name"])
        content = path.read_bytes()
        if len(content) != asset["size"] or sha256_bytes(content) != asset["sha256"]:
            raise PackageError("transported release asset differs from admitted bytes")


def stage(root: Path, admission: dict, output: Path) -> None:
    paths = [(contained(root, asset["path"]), output / asset["name"]) for asset in admission["assets"]]
    if any(target.exists() for _, target in paths):
        raise PackageError("refusing to overwrite staged release assets")
    output.mkdir(parents=True, exist_ok=True)
    for source, target in paths:
        shutil.copyfile(source, target)
    verify_transported(root, admission, output)


def verify_provider(admission: dict, release: dict, repository: str, *, allow_draft: bool = False) -> dict:
    """Pure comparison. Callers must supply fresh authenticated provider read-back."""
    check_admission(admission, admission["version"])
    version = admission["version"]
    expected_page = f"https://github.com/{repository}/releases/tag/{version}"
    page = release.get("html_url")
    draft_page = bool(release.get("draft") is True and isinstance(page, str)
                      and re.fullmatch(re.escape(f"https://github.com/{repository}/releases/tag/untagged-") + r"[0-9a-f]+", page))
    if (release.get("tag_name") != version or release.get("prerelease") is not False
            or type(release.get("draft")) is not bool or (release["draft"] and not allow_draft)
            or type(release.get("id")) is not int or release["id"] <= 0
            or (page != expected_page and not draft_page)):
        raise PackageError("provider release identity or lifecycle mismatch")
    if not release["draft"] and not release.get("published_at"):
        raise PackageError("provider publication time is missing")
    assets = release.get("assets")
    if not isinstance(assets, list) or len(assets) != len(admission["assets"]):
        raise PackageError("provider asset set is incomplete")
    by_name = {a.get("name"): a for a in assets if isinstance(a, dict)}
    if len(by_name) != len(assets) or set(by_name) != set(asset_names(version)):
        raise PackageError("provider asset names disagree or repeat")
    observed = []
    ids = set()
    for expected in admission["assets"]:
        actual = by_name[expected["name"]]
        url = f"https://github.com/{repository}/releases/download/{version}/{expected['name']}"
        if (type(actual.get("id")) is not int or actual["id"] <= 0 or actual["id"] in ids
                or actual.get("state") != "uploaded" or actual.get("browser_download_url") != url
                or type(actual.get("size")) is not int or actual["size"] != expected["size"]
                or actual.get("digest") != "sha256:" + expected["sha256"]):
            raise PackageError("provider asset name/size/digest/identity disagrees with admitted bytes")
        ids.add(actual["id"])
        observed.append({k: actual[k] for k in ("id", "name", "size", "digest", "browser_download_url")})
    return {"schema_version": PROVIDER_SCHEMA, "state": "uploaded-draft" if release["draft"] else "published",
            "version": version, "package_id": admission["package_id"], "release_id": admission["release_id"],
            "artifact_set_id": admission["artifact_set_id"], "payload_fingerprint": admission["payload_fingerprint"],
            "provider_release_id": release["id"], "published_at": release.get("published_at"),
            "assets": observed}
