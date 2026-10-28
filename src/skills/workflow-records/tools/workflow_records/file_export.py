"""Lossless current-cut file projection; not a recovery archive or import adapter."""
from __future__ import annotations

import base64
import copy
import json
import os
from pathlib import Path
import stat

import yaml

from .common import contained, mapping, relative_path
from .contracts import RecordError, digest, encoded, identifier, require, unique_object, validate_unicode

FORMAT = "workflow-records/files/1"
SELECTION = "workflow-records/file-schema-selection/1"
MANIFEST = ".workflow-records/manifest.json"
CURRENT = ".workflow-records/current-record.json"
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024
MAX_FILES = 400


def fields(value, required, optional=()):
    require(isinstance(value, dict) and set(required) <= set(value) <= set(required) | set(optional),
            "malformed_record", "File export fields are incomplete or unknown.")


def parse(raw):
    require(len(raw) <= MAX_FILE, "limit_exceeded", "Export member exceeds 32 MiB.")
    try:
        def constant(_):
            raise ValueError("Non-finite JSON")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=constant)
        validate_unicode(value)
        return value
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise RecordError("malformed_record", "Invalid export UTF-8 JSON.") from exc


def read(path):
    require(path.is_file(), "not_found", "An export resource is missing.")
    require(path.stat().st_nlink == 1, "unsafe_path", "Hard-linked export resources are unsupported.")
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE + 1)
    require(len(raw) <= MAX_FILE, "limit_exceeded", "Export member exceeds 32 MiB.")
    return raw


def resource(root, ref):
    fields(ref, {"path", "sha256"})
    relative = relative_path(ref["path"]).as_posix()
    folded = relative.casefold()
    require(not any(folded == name or folded.startswith(name + "/") for name in
                    (".ai/core", ".agents", ".claude", ".codex")),
            "unsafe_path", "Select project-owned schema/template resources, not managed runtime files.")
    raw = read(contained(root, relative))
    require(digest(raw) == ref["sha256"], "integrity_error", "Selected schema/template resource changed.")
    return raw


def schema_selection(root, selected, metadata, tasks):
    if selected is None:
        return {"profile_id": "current-record", "profile_version": "1", "selection": None}
    raw = resource(root, selected)
    selection = parse(raw)
    fields(selection, {"contract_version", "profile_id", "profile_version", "schemas"}, {"templates"})
    require(selection["contract_version"] == SELECTION, "unsupported_version", "Unknown file schema selection contract.")
    identifier(selection["profile_id"])
    require(isinstance(selection["profile_version"], str) and selection["profile_version"],
            "malformed_record", "A project profile version is required.")
    fields(selection["schemas"], {"workflow", "task"})
    templates = selection.get("templates", {})
    fields(templates, set(), {"workflow", "task"})
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError, ValidationError
        from referencing import Registry
    except ImportError as exc:
        raise RecordError("provider_unavailable", "Selected file schemas require the declared jsonschema runtime.") from exc

    def local_refs(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ("$ref", "$dynamicRef"):
                    require(isinstance(item, str) and item.startswith("#"), "unsupported_format",
                            "Project schemas support only document-local references; no resource is fetched.")
                local_refs(item)
        elif isinstance(value, list):
            for item in value:
                local_refs(item)

    for kind, values in (("workflow", [metadata]), ("task", tasks)):
        schema = parse(resource(root, selection["schemas"][kind]))
        require(not isinstance(schema, dict) or schema.get("$schema", "https://json-schema.org/draft/2020-12/schema") ==
                "https://json-schema.org/draft/2020-12/schema", "unsupported_version", "Project schemas must select Draft 2020-12.")
        local_refs(schema)
        try:
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema, registry=Registry())
            for value in values:
                validator.validate(value)
            if kind in templates:
                template = mapping(resource(root, templates[kind]), ".yaml")
                validator.validate(template)
        except (SchemaError, ValidationError, RecursionError) as exc:
            raise RecordError("schema_conflict", "Record or selected template violates the project schema.") from exc
        except RecordError:
            raise
        except Exception as exc:
            # Referencing errors must fail closed rather than trigger ambient IO.
            raise RecordError("schema_conflict", "Project schema could not be resolved locally.") from exc
    return {"profile_id": selection["profile_id"], "profile_version": selection["profile_version"],
            "selection": copy.deepcopy(selected), "definition": selection}


def check_paths(paths):
    require(len(paths) <= MAX_FILES, "limit_exceeded", "Export has too many members.")
    folded, spellings = set(), {}
    for name in paths:
        relative_path(name)
        components = name.split("/")
        for index in range(1, len(components) + 1):
            prefix = "/".join(components[:index])
            require(spellings.get(prefix.casefold(), prefix) == prefix, "unsafe_path", "Export directory components collide ignoring case.")
            spellings[prefix.casefold()] = prefix
        lowered = name.casefold()
        require(lowered not in folded, "unsafe_path", "Export paths collide ignoring case.")
        folded.add(lowered)
    for name in folded:
        parts = name.split("/")
        require(not any("/".join(parts[:index]) in folded for index in range(1, len(parts))),
                "unsafe_path", "Export file and directory paths conflict.")


def source_state(source, current):
    fields(source, {"kind", "reference", "revision"}, {"configuration_revision", "authority_epoch"})
    require(isinstance(current, dict), "malformed_record", "Current record must be an object.")
    if source["kind"] == "native":
        from .contracts import WorkflowRef
        fields(source, {"kind", "reference", "revision"})
        WorkflowRef.parse(source["reference"])
        require(digest(encoded(current)) == source["revision"], "integrity_error", "Native current record differs from its revision.")
        fields(current, {"metadata", "tasks", "entrypoint", "documents", "attachments", "checkpoint", "event"})
        state = current
    elif source["kind"] == "local-group":
        from . import group_model as model
        from .source_contract import canonical
        fields(source, {"kind", "reference", "revision", "configuration_revision", "authority_epoch"})
        require(type(source["configuration_revision"]) is int and source["configuration_revision"] >= 0
                and type(source["authority_epoch"]) is int and source["authority_epoch"] >= 1,
                "malformed_record", "Invalid source configuration/authority version.")
        fields(source["reference"], {"group_id", "project_id", "workflow_id"})
        for value in source["reference"].values():
            model.identifier(value)
        require(digest(canonical(current)) == source["revision"], "integrity_error", "Group current body differs from its logical cut.")
        fields(current, {"sequence", "parent", "operation_id", "request_digest", "request", "state", "providers",
                         "targets", "configuration_revision", "authority_epoch"})
        state = current.get("state")
        model.check_state(state)
    else:
        raise RecordError("unsupported_version", "Unknown current-record source kind.")
    require(isinstance(state, dict) and isinstance(state.get("metadata"), dict)
            and isinstance(state.get("tasks"), list) and len(state["tasks"]) <= 128,
            "malformed_record", "Current workflow record is missing or invalid.")
    require(all(isinstance(task, dict) for task in state["tasks"]), "malformed_record", "Tasks must be mappings.")
    require(isinstance(state.get("documents"), dict) and isinstance(state.get("attachments"), dict)
            and isinstance(state.get("entrypoint"), str), "malformed_record", "Invalid current document collections/entrypoint.")
    return state


def yaml_bytes(value):
    # SafeDumper emits YAML scalars that round-trip JSON-like metadata, with no aliases.
    raw = yaml.safe_dump(value, allow_unicode=True, sort_keys=False).encode("utf-8")
    require(encoded(mapping(raw, ".yaml")) == encoded(value), "unsupported_format", "YAML rendering changed record values.")
    return raw


def plan(root, source, current, blobs, selection=None):
    state = source_state(source, current)
    profile = schema_selection(root, selection, state["metadata"], state["tasks"])
    files = {"workflow.yaml": yaml_bytes(state["metadata"]), CURRENT: encoded(current)}
    task_rows, blob_rows = [], {"documents": {}, "attachments": {}}
    names = []
    for task in state["tasks"]:
        if source["kind"] == "local-group":
            from .group_model import identifier as task_identifier
        else:
            task_identifier = identifier
        name = "tasks/" + task_identifier(task.get("task_id")) + ".yaml"
        names.append(name)
        task_rows.append({"task_id": task["task_id"], "path": name})
        files[name] = yaml_bytes(task)
    for kind in blob_rows:
        require(isinstance(state.get(kind), dict) and len(state[kind]) <= 128,
                "malformed_record", "Invalid document collection.")
        require(set(blobs.get(kind, {})) == set(state[kind]), "integrity_error", "Blob collection closure differs.")
        for logical, raw in blobs[kind].items():
            relative_path(logical)
            name = kind + "/" + logical
            names.append(name)
            require(isinstance(raw, bytes), "malformed_record", "Export blob must be bytes.")
            if source["kind"] == "native":
                require(digest(raw) == state[kind][logical], "integrity_error", "Native blob digest differs.")
            else:
                from .group_model import check_blob
                value = state[kind][logical]
                check_blob(value)
                require(base64.b64encode(raw).decode("ascii") == value["content"], "integrity_error", "Group blob differs.")
            files[name] = raw
            blob_rows[kind][logical] = name
    require(state.get("entrypoint") in state["documents"], "malformed_record", "Entrypoint document is missing.")
    if state.get("checkpoint") is not None:
        files[".workflow-records/checkpoint.json"] = encoded(state["checkpoint"])
    check_paths(["workflow.yaml", CURRENT, MANIFEST, *names,
                 *([".workflow-records/checkpoint.json"] if state.get("checkpoint") is not None else [])])
    require(all(len(raw) <= MAX_FILE for raw in files.values()) and sum(map(len, files.values())) <= MAX_TOTAL,
            "limit_exceeded", "Current-record export exceeds its complete byte bound.")
    manifest = {"format": FORMAT, "scope": "current-record", "source": copy.deepcopy(source),
                "schema_profile": profile, "entrypoint": state["entrypoint"], "tasks": task_rows,
                "documents": blob_rows["documents"], "attachments": blob_rows["attachments"],
                "files": {name: {"sha256": digest(raw), "size": len(raw)} for name, raw in sorted(files.items())}}
    require(len(encoded(manifest)) <= 1024 * 1024, "limit_exceeded", "Export manifest exceeds 1 MiB.")
    return manifest, files


def safe_absolute(value):
    require(isinstance(value, str) and Path(value).is_absolute(), "unsafe_path", "Select an absolute local path.")
    path = Path(value)
    relative_path("/".join(path.parts[1:]))
    require(not str(path).startswith(("\\\\", "//")), "unsupported_topology", "Network paths are unsupported.")
    for candidate in [*reversed(path.parents), path]:
        if candidate.exists() or candidate.is_symlink():
            info = candidate.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "unsafe_path", "Links and reparse points are unsupported.")
    if os.name == "nt":
        import ctypes
        require(ctypes.windll.kernel32.GetDriveTypeW(str(path.anchor)) != 4,
                "unsupported_topology", "Mapped network paths are unsupported.")
    return path.resolve()


def destination_path(destination, protected):
    target = safe_absolute(destination)
    require(target.parent.is_dir(), "not_found", "Export parent must already exist.")
    folded = str(target).casefold()
    for original in protected:
        value = str(original).casefold()
        require(folded != value and not folded.startswith(value + os.sep) and not value.startswith(folded + os.sep),
                "unsafe_path", "Export must not overlap live carrier/control storage.")
    require(not target.exists(), "already_exists", "Export requires a fresh directory.")
    return target


def publish(target, files):
    # mkdir is a portable no-replace reservation. Manifest is written last.
    try:
        target.mkdir()
    except FileExistsError as exc:
        raise RecordError("already_exists", "Another exporter reserved the destination.") from exc
    created_files, created_dirs = [], [target]
    try:
        for name, raw in files.items():
            path = contained(target, name)
            missing = []
            parent = path.parent
            while parent != target and not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                created_dirs.append(directory)
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                created_files.append(path)
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
    except BaseException:
        for path in reversed(created_files):
            path.unlink(missing_ok=True)
        for path in reversed(created_dirs):
            try:
                path.rmdir()
            except OSError:
                pass  # Never remove another writer's files.
        raise


def export(root, request, source, current, blobs, protected):
    target = destination_path(request.get("destination"), protected)
    manifest, files = plan(root, source, current, blobs, request.get("schema_selection"))
    raw = encoded(manifest)
    publish(target, {**files, MANIFEST: raw})
    return {"state": "exported", "scope": "current-record", "format": FORMAT,
            "destination": str(target), "manifest_digest": digest(raw), "source": source,
            "file_count": len(files) + 1, "git_import": "not-established", "restore": "unsupported"}


def native(store, ref, request):
    with store.transaction() as (connection, _):
        current, revision = store._state(connection, ref)
        require(isinstance(request.get("expected_revision"), str) and request["expected_revision"] == revision,
                "revision_conflict", "Current native revision differs from expected_revision.")
        blobs = {kind: {name: store.blob(connection, key) for name, key in current[kind].items()}
                 for kind in ("documents", "attachments")}
        return export(store.root, request, {"kind": "native", "reference": ref.as_dict(), "revision": revision},
                      current, blobs, sqlite_paths(store.database))


def sqlite_paths(database):
    return [Path(str(database) + suffix) for suffix in ("", "-journal", "-wal", "-shm")]


def group(group, control, envelope, request):
    from . import group_model as model
    group.cas(control, envelope, request)
    current = model.current(envelope)
    state = current.get("state")
    require(state is not None, "not_found", "Workflow has not been created.")
    blobs = {kind: {name: base64.b64decode(value["content"], validate=True) for name, value in state[kind].items()}
             for kind in ("documents", "attachments")}
    source = {"kind": "local-group", "reference": group.identity, "revision": model.head(envelope),
              "configuration_revision": control["configuration_revision"], "authority_epoch": control["authority_epoch"]}
    protected = [group.directory]
    for member in control["members"].values():
        protected.extend(sqlite_paths(member["path"]) if member["kind"] == "sqlite" else [Path(member["path"])])
    return export(group.root, request, source, current, blobs, protected)


def preflight(root, request, kind, reference):
    directory = safe_absolute(request.get("directory"))
    require(directory.is_dir(), "not_found", "Export directory is missing.")
    raw = read(contained(directory, MANIFEST))
    require(len(raw) <= 1024 * 1024, "limit_exceeded", "Export manifest exceeds 1 MiB.")
    require(digest(raw) == request.get("manifest_digest"), "integrity_error", "Manifest differs from the observed digest.")
    manifest = parse(raw)
    fields(manifest, {"format", "scope", "source", "schema_profile", "entrypoint", "tasks", "documents", "attachments", "files"})
    require(manifest["format"] == FORMAT and manifest["scope"] == "current-record", "unsupported_version", "Unknown file export format/scope.")
    fields(manifest["source"], {"kind", "reference", "revision"}, {"configuration_revision", "authority_epoch"})
    require(manifest["source"].get("kind") == kind and manifest["source"].get("reference") == reference,
            "binding_mismatch", "File export identity differs from the explicit selection.")
    require(isinstance(manifest["files"], dict), "malformed_record", "Manifest file map is required.")
    check_paths([*manifest["files"], MANIFEST])
    expected = set(manifest["files"]) | {MANIFEST}
    actual, dirs = set(), []
    total = 0
    for parent, directories, names in os.walk(directory, followlinks=False):
        for name in directories:
            item = Path(parent) / name
            relative = item.relative_to(directory).as_posix()
            contained(directory, relative)
            dirs.append(relative)
            require(len(dirs) <= 4096, "limit_exceeded", "Too many export directories.")
        for name in names:
            item = Path(parent) / name
            relative = item.relative_to(directory).as_posix()
            contained(directory, relative)
            actual.add(relative)
            require(relative in expected, "integrity_error", "Export contains an unmanifested file.")
    require(actual == expected and all(any(name.startswith(path + "/") for name in expected) for path in dirs),
            "integrity_error", "Export file/directory closure differs.")
    files = {}
    for name, details in manifest["files"].items():
        fields(details, {"sha256", "size"})
        value = read(contained(directory, name))
        total += len(value)
        require(total <= MAX_TOTAL, "limit_exceeded", "Export exceeds 64 MiB.")
        require(type(details["size"]) is int and len(value) == details["size"] and digest(value) == details["sha256"],
                "integrity_error", "An export member differs from its manifest.")
        files[name] = value
    require(CURRENT in files, "integrity_error", "Current-record sidecar is missing.")
    current = parse(files[CURRENT])
    state = source_state(manifest["source"], current)
    # Rebuild from YAML and raw blobs, then compare the complete plan. This
    # checks semantic closure even when an attacker recomputes all file hashes.
    rebuilt = copy.deepcopy(current)
    projected = rebuilt if kind == "native" else rebuilt["state"]
    require("workflow.yaml" in files and isinstance(manifest["tasks"], list), "integrity_error", "Metadata/task projection is missing.")
    projected["metadata"] = mapping(files["workflow.yaml"], ".yaml")
    projected["tasks"] = []
    for row in manifest["tasks"]:
        fields(row, {"task_id", "path"})
        require(isinstance(row["path"], str) and row["path"] in files, "integrity_error", "Projected task is missing.")
        task = mapping(files[row["path"]], ".yaml")
        require(task.get("task_id") == row["task_id"], "integrity_error", "Projected task identity differs.")
        projected["tasks"].append(task)
    require(encoded(rebuilt) == encoded(current), "integrity_error", "YAML projection differs from the complete current record.")
    blobs = {}
    for collection in ("documents", "attachments"):
        require(isinstance(manifest[collection], dict), "malformed_record", "Invalid blob map.")
        require(all(isinstance(name, str) and name in files for name in manifest[collection].values()), "integrity_error", "Projected blob is missing.")
        blobs[collection] = {logical: files[name] for logical, name in manifest[collection].items()}
    planned, rendered = plan(root, manifest["source"], current, blobs, request.get("schema_selection"))
    require(encoded(planned) == encoded(manifest) and set(rendered) == set(files),
            "integrity_error", "Export plan/schema/record closure differs.")
    return {"valid": True, "scope": "current-record", "format": FORMAT, "manifest_digest": digest(raw),
            "source": manifest["source"], "file_count": len(expected), "reassembly": "exact", "restore": "unsupported"}
