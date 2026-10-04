"""Source-only release transport contracts; never part of the installation engine."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import zipfile

WORKFLOW = ".github/workflows/publish-release.yml"
SCHEMA = "framework-release-assets/1"
LIMIT = 256 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def document(raw):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def oid(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value), "full Git SHA required")
    return value


def version(value):
    require(isinstance(value, str) and len(value) <= 100, "version length")
    require(re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?", value), "SemVer required")
    prerelease = value.split("+")[0].partition("-")[2]
    require(all(not (x.isdigit() and len(x) > 1 and x[0] == "0") for x in prerelease.split(".")), "SemVer leading zero")
    return value


def tag_name(value):
    require(isinstance(value, str) and value.startswith("v"), "existing v-prefixed tag required")
    version(value[1:])
    return value


def safe_name(value):
    require(isinstance(value, str) and value and "\\" not in value and ":" not in value, "unsafe archive path")
    require(not value.startswith("/") and all(x not in ("", ".", "..") for x in value.split("/")), "unsafe archive path")
    require(not re.search(r"[\x00-\x1f<>|?*]", value), "unsafe archive path")
    for part in PurePosixPath(value).parts:
        require(not part.endswith((" ", ".")) and not re.fullmatch(r"(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?", part), "unsafe portable path")
    return value


def git(repository, *args):
    environment = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    environment.update(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    return subprocess.check_output(["git", "--no-replace-objects", "-C", str(repository), *args],
                                   env=environment, stderr=subprocess.PIPE, timeout=90)


def identity(repository, source_commit=None, tag=None):
    if tag:
        tag_name(tag)
        ref = "refs/tags/" + tag
        require(git(repository, "cat-file", "-t", ref).strip() == b"tag", "annotated existing tag required")
        tag_object = oid(git(repository, "rev-parse", ref).decode().strip())
        raw = git(repository, "cat-file", "tag", tag_object).decode()
        header = raw.split("\n\n", 1)[0].splitlines()
        require(len(header) >= 3 and header[1] == "type commit" and header[2] == "tag " + tag, "tag must directly name its exact commit and tag")
        commit = oid(header[0].removeprefix("object "))
        if source_commit:
            require(commit == source_commit, "source/tag commit mismatch")
        return {"tag": tag, "tag_object": tag_object, "commit": commit}
    commit = oid(source_commit)
    require(git(repository, "cat-file", "-t", commit).strip() == b"commit", "source is not a commit")
    return {"tag": None, "tag_object": None, "commit": commit}


def plain(path):
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and not path.is_symlink() and info.st_nlink == 1
            and not getattr(info, "st_file_attributes", 0) & 0x400, "plain file required")
    return info


def entry(name, raw, mode=0o644):
    return {"path": safe_name(name), "size": len(raw), "sha256": sha(raw), "mode": mode}


def verify_bundle(directory, expected_source=None):
    manifest_file = directory / "release-manifest.json"
    plain(manifest_file)
    manifest = document(manifest_file.read_bytes())
    require(manifest["schema"] == SCHEMA, "manifest schema")
    source = manifest["source"]
    oid(source["commit"])
    if expected_source is not None:
        require(source == expected_source, "source/manifest mismatch")
    if source["tag"]:
        tag_name(source["tag"])
        oid(source["tag_object"])
        require(manifest["version"] == source["tag"][1:], "version/tag mismatch")
    else:
        require(source["tag_object"] is None, "snapshot tag object")
    version(manifest["version"])
    for key in ("tooling_commit", "workflow_commit"):
        oid(manifest["provenance"][key])
    require(manifest["provenance"]["workflow"] in (WORKFLOW, ".github/workflows/package-candidate.yml"), "workflow identity")
    archive = manifest["archive"]
    name = safe_name(archive["name"])
    require("/" not in name and name.endswith(".zip"), "archive filename")
    path = directory / name
    plain(path)
    raw = path.read_bytes()
    require(len(raw) <= LIMIT and len(raw) == archive["size"] and sha(raw) == archive["sha256"], "archive size/hash mismatch")
    rows = manifest["entries"]
    names = [r["path"] for r in rows]
    require(names == sorted(set(names)) and len(names) <= 4096 and len({x.casefold() for x in names}) == len(names), "entry order/uniqueness")
    require(sum(r["size"] for r in rows) <= LIMIT, "archive expanded budget")
    payload = {}
    with zipfile.ZipFile(path) as zip_file:
        require(zip_file.namelist() == names, "archive entry closure/order")
        for info, row in zip(zip_file.infolist(), rows):
            safe_name(info.filename)
            require(not info.is_dir() and info.file_size == row["size"] and row["size"] <= LIMIT, "archive member size/type")
            require((info.external_attr >> 16) == (stat.S_IFREG | row["mode"]) and row["mode"] in (0o644, 0o755), "archive mode")
            data = zip_file.read(info)
            require(sha(data) == row["sha256"], "archive raw content mismatch")
            payload[row["path"]] = data
    require(sum(r["size"] for r in rows) <= LIMIT, "archive expanded budget")
    pin_raw = payload["engine-pin.json"]
    pin = document(pin_raw)
    require(sha(pin_raw) == manifest["engine_pin_sha256"] and pin["source_commit"] == source["commit"], "engine pin/source mismatch")
    require(pin["id"] == "framework-managed-installation" and pin["version"] == "2.0.0", "engine version")
    pin_names = [r["path"] for r in pin["files"]]
    require(len(pin_names) == 23 and pin_names == sorted(set(pin_names)) and all(n.startswith("src/") for n in pin_names), "engine pin closure")
    require(document(payload["engine/engine.json"]) == {"engine": pin, "engine_package_version": 1}, "engine descriptor mismatch")
    require({x[7:] for x in names if x.startswith("engine/")} == set(pin_names) | {"engine.json"}, "engine archive closure")
    for row in pin["files"]:
        require(sha(payload["engine/" + safe_name(row["path"])]) == row["sha256"], "engine raw content mismatch")
    catalog = document(payload["catalog/metadata/catalog.json"])
    require(catalog["source"]["commit"] == source["commit"] and catalog["release_version"] == manifest["version"], "catalog/source mismatch")
    catalog_files = document(payload["catalog/metadata/catalog-files.json"])
    expected = {"catalog/" + r["path"] for r in catalog_files["files"]} | {
        "catalog/metadata/catalog.json", "catalog/metadata/catalog-files.json", "catalog/metadata/build.json"}
    require({x for x in names if x.startswith("catalog/")} == expected, "catalog archive closure")
    for row in catalog_files["files"]:
        data = payload["catalog/" + safe_name(row["path"])]
        require(len(data) == row["source"]["size"] and sha(data) == row["source"]["sha256"], "catalog member mismatch")
    inputs = {n: sha(payload["catalog/" + n]) for n in ("metadata/catalog.json", "metadata/catalog-files.json")}
    # Match the public product's sorted, indented, newline-terminated identity serialization.
    identity_raw = (json.dumps(inputs, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    ident = f"catalog:1:{manifest['version']}:{source['commit']}:{sha(identity_raw)}"
    require(ident == manifest["catalog_identity"], "catalog identity mismatch")
    build = document(payload["catalog/metadata/build.json"])
    require(build["identity"] == ident and build["identity_inputs"] == inputs and build["artifact_kind"] == "catalog", "catalog build receipt")
    require(set(names) == expected | {"engine/" + n for n in pin_names} |
            {"engine/engine.json", "engine-pin.json", "README.md", "content-hashes.json"}, "release payload closure")
    hashes = document(payload["content-hashes.json"])
    require(hashes == [r for r in rows if r["path"] != "content-hashes.json"], "content hash inventory")
    checksum = directory / (name + ".sha256")
    plain(checksum)
    require(checksum.read_bytes() == f"{archive['sha256']}  {name}\n".encode(), "archive checksum mismatch")
    return manifest
