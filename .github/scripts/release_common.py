"""Source-only release transport contracts; never part of the installation engine."""
from __future__ import annotations
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from string import Template
import zipfile

WORKFLOW = ".github/workflows/publish-release.yml"
SCHEMA = "framework-release-assets/2"
LEGACY_SCHEMA = "framework-release-assets/1"
README_SOURCE_PATH = "src/distribution/templates/release-readme.md"
README_FIELDS = frozenset({"label", "source_commit", "catalog_identity", "release_version"})
README_LIMIT = 1024 * 1024
LIMIT = 256 * 1024 * 1024
ENGINE_DECLARATIONS = ("src/tools/maintain_framework.py", "src/distribution/installation_state.py")


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


def engine_files(read):
    """Read, never execute, the two selected product closure declarations."""
    declarations = []
    for name in ENGINE_DECLARATIONS:
        try:
            tree = ast.parse(read(name))
        except (SyntaxError, UnicodeError) as exc:
            raise ValueError("invalid Engine declaration source") from exc
        values = [node.value for node in tree.body if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "ENGINE_FILES" for t in node.targets)]
        require(len(values) == 1 and isinstance(values[0], ast.Tuple), "literal ENGINE_FILES tuple required")
        members = ast.literal_eval(values[0])
        require(members and all(type(n) is str and safe_name(n).startswith("src/") for n in members),
                "nonempty product-only Engine 2 closure required")
        require(tuple(sorted(set(members))) == members and len({n.casefold() for n in members}) == len(members),
                "sorted unique Engine 2 closure required")
        require(set(ENGINE_DECLARATIONS) <= set(members), "Engine declaration owners missing from closure")
        declarations.append(members)
    require(declarations[0] == declarations[1], "ENGINE_FILES declarations disagree")
    return declarations[0]


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


def render_readme(template_utf8, source, catalog_identity, release_version):
    """Render only the four selected values; never evaluate template code."""
    require(type(template_utf8) is str, "README template must be UTF-8 text")
    raw = template_utf8.encode("utf-8", errors="strict")
    require(len(raw) <= README_LIMIT, "README template budget")
    template = Template(template_utf8)
    require(template.is_valid(), "invalid README template placeholder")
    require(set(template.get_identifiers()) == README_FIELDS, "README template fields must match fixed fields")
    return template.substitute(label=source["tag"] or "snapshot", source_commit=source["commit"],
                               catalog_identity=catalog_identity, release_version=release_version).encode("utf-8")


def verify_readme_source(record, source, catalog_identity, release_version, rendered):
    fields = {"path", "commit", "git_blob", "sha256", "size", "template_utf8"}
    require(type(record) is dict and set(record) == fields, "README source fields")
    require(record["path"] == README_SOURCE_PATH, "README source path")
    require(oid(record["commit"]) == source["commit"], "README source commit")
    require(type(record["template_utf8"]) is str, "README template must be UTF-8 text")
    raw = record["template_utf8"].encode("utf-8", errors="strict")
    require(len(raw) <= README_LIMIT and type(record["size"]) is int and record["size"] == len(raw), "README source size")
    require(record["sha256"] == sha(raw), "README source hash")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(oid(record["git_blob"]) == blob, "README source Git blob")
    expected = render_readme(record["template_utf8"], source, catalog_identity, release_version)
    require(rendered == expected, "README rendered bytes differ from selected source template")


def verify_bundle(directory, expected_source=None):
    manifest_file = directory / "release-manifest.json"
    plain(manifest_file)
    manifest = document(manifest_file.read_bytes())
    require(manifest["schema"] in (LEGACY_SCHEMA, SCHEMA), "manifest schema")
    current = manifest["schema"] == SCHEMA
    # A successful /1 read proves only the retained legacy envelope. It carries
    # no README source evidence and never establishes the /2 source-only rule.
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
    require(all("engine/" + n in payload for n in ENGINE_DECLARATIONS), "Engine declaration sources missing")
    declared = engine_files(lambda n: payload["engine/" + n])
    require(tuple(pin_names) == declared, "engine pin closure differs from product declarations")
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
        if current:
            require(safe_name(row["source"]["path"]).startswith("src/"), "catalog product source must originate under src/")
        data = payload["catalog/" + safe_name(row["path"])]
        require(len(data) == row["source"]["size"] and sha(data) == row["source"]["sha256"], "catalog member mismatch")
    inputs = {n: sha(payload["catalog/" + n]) for n in ("metadata/catalog.json", "metadata/catalog-files.json")}
    # Match the public product's sorted, indented, newline-terminated identity serialization.
    identity_raw = (json.dumps(inputs, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    ident = f"catalog:1:{manifest['version']}:{source['commit']}:{sha(identity_raw)}"
    require(ident == manifest["catalog_identity"], "catalog identity mismatch")
    build = document(payload["catalog/metadata/build.json"])
    require(build["identity"] == ident and build["identity_inputs"] == inputs and build["artifact_kind"] == "catalog", "catalog build receipt")
    if current:
        verify_readme_source(manifest["provenance"].get("readme_source"), source,
                             manifest["catalog_identity"], manifest["version"], payload["README.md"])
    require(set(names) == expected | {"engine/" + n for n in pin_names} |
            {"engine/engine.json", "engine-pin.json", "README.md", "content-hashes.json"}, "release payload closure")
    hashes = document(payload["content-hashes.json"])
    require(hashes == [r for r in rows if r["path"] != "content-hashes.json"], "content hash inventory")
    checksum = directory / (name + ".sha256")
    plain(checksum)
    require(checksum.read_bytes() == f"{archive['sha256']}  {name}\n".encode(), "archive checksum mismatch")
    return manifest
