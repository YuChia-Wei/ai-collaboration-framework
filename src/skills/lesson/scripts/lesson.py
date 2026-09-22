#!/usr/bin/env python3
"""Candidate-only lesson.fs 0.1.0. JSON request in, one JSON result out.

Public contract: ../references/operations.md. No source-repository imports.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import html
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from datetime import datetime, timezone
import uuid


OPERATIONS = ("explain", "create", "inspect", "query", "validate", "revise", "render")
AUTHORED = ("title", "observation", "evidence", "conclusion", "applies_when",
            "does_not_apply_when", "confidence", "follow_up")
CONTROLLED = ("schema_version", "kind", "owner", "id", "status", "created_at", "updated_at")
ID = re.compile(r"lesson-[0-9a-f]{32}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
TOKEN = re.compile(r"\{\{([a-z_]+)\}\}")
LIMIT = 4 * 1024 * 1024
MAX_FILES = 10000
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class Fault(Exception):
    def __init__(self, outcome, code, message):
        super().__init__(message)
        self.outcome, self.code, self.message = outcome, code, message

    def diagnostic(self):
        return {"code": self.code, "message": self.message}


def fail(code, message, outcome="invalid-input"):
    raise Fault(outcome, code, message)


def fields(value, required, optional=(), label="object"):
    if type(value) is not dict or not set(required) <= value.keys() or value.keys() - set(required) - set(optional):
        fail("fields", f"Invalid or unknown fields in {label}.")
    return value


def string(value, label):
    if type(value) is not str or not value or not value.strip():
        fail("type", f"{label} must be a nonempty string.")
    return value


def strings(value, label, nonempty=False):
    if type(value) is not list or (nonempty and not value):
        fail("type", f"{label} must be an array of strings.")
    for item in value:
        string(item, label)
    if len(set(value)) != len(value):
        fail("duplicate", f"{label} contains duplicates.")
    return value


def exact_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(exact_equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(exact_equal(a, b) for a, b in zip(left, right))
    return left == right


def json_values(value):
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                fail("json-key", "JSON keys must be strings.")
            json_values(key)
            json_values(child)
    elif type(value) is list:
        for child in value:
            json_values(child)
    elif type(value) is str:
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeError:
            fail("unicode", "Unpaired Unicode surrogates are unsupported.")
    elif type(value) is float:
        if not math.isfinite(value):
            fail("number", "Non-finite JSON numbers are invalid.")
    elif value is not None and type(value) not in (int, bool):
        fail("json-type", "Only JSON-compatible values are accepted.")


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("duplicate-key", "Duplicate object keys are invalid.")
        result[key] = value
    return result


def parse_json(raw):
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=unique_pairs,
                           parse_constant=lambda _: fail("number", "Non-finite JSON numbers are invalid."))
        json_values(value)
        return value
    except (UnicodeError, ValueError, RecursionError):
        fail("json", "Expected bounded strict UTF-8 JSON without a BOM.")


def encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def dependency(name, minimum, maximum):
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        fail("dependency", f"Required runtime {name} is missing.", "unavailable")
    if not re.fullmatch(r"\d+(?:\.\d+){1,3}", version):
        fail("dependency-version", f"Stable {name} runtime version required.", "unavailable")
    parts = tuple(int(p) for p in version.split("."))
    if not minimum <= parts < maximum:
        fail("dependency-version", f"Required {name} runtime range is unavailable.", "unavailable")


def parse_yaml(raw):
    dependency("PyYAML", (6, 0), (7, 0))
    try:
        import yaml
        text = raw.decode("utf-8", errors="strict")
        if text.startswith("\ufeff"):
            fail("yaml", "Metadata must be UTF-8 without a BOM.")
        for token in yaml.scan(text):
            if isinstance(token, (yaml.tokens.TagToken, yaml.tokens.AliasToken, yaml.tokens.AnchorToken)):
                fail("yaml-token", "YAML tags, aliases and anchors are forbidden.")
        node = yaml.compose(text, Loader=yaml.SafeLoader)

        def convert(item):
            if isinstance(item, yaml.MappingNode):
                pairs = []
                for key, child in item.value:
                    if key.tag != "tag:yaml.org,2002:str" or key.value == "<<":
                        fail("yaml-key", "YAML keys must be unique strings without merge keys.")
                    pairs.append((key.value, convert(child)))
                return unique_pairs(pairs)
            if isinstance(item, yaml.SequenceNode):
                return [convert(child) for child in item.value]
            if not isinstance(item, yaml.ScalarNode):
                fail("yaml", "Metadata must contain one JSON-compatible document.")
            kind = item.tag.removeprefix("tag:yaml.org,2002:")
            if kind == "str":
                return item.value
            if kind == "null" and item.value == "null":
                return None
            if kind == "bool" and item.value in ("true", "false"):
                return item.value == "true"
            if kind in ("int", "float") and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", item.value):
                return parse_json(item.value.encode("utf-8"))
            fail("yaml-type", "Metadata YAML must use JSON scalar types and spellings.")

        value = convert(node)
        json_values(value)
        return value
    except ImportError:
        fail("dependency", "PyYAML could not be imported.", "unavailable")
    except (UnicodeError, ValueError, RecursionError, yaml.YAMLError):
        fail("yaml", "Invalid bounded UTF-8 package metadata.")


def beneath(path, root):
    return path == root or root in path.parents


def overlap(left, right):
    return beneath(left, right) or beneath(right, left)


def safe_path(value, base=None, *, relative_only=False):
    string(value, "path")
    if any(ord(char) < 32 for char in value):
        fail("path", "Control characters in paths are forbidden.")
    path = Path(value)
    if relative_only and path.is_absolute():
        fail("path", "A package resource must be relative.")
    if ".." in path.parts or (path.drive and not path.is_absolute()):
        fail("path", "Parent traversal and drive-relative paths are forbidden.")
    if os.name == "nt":
        if value.startswith(("\\\\", "//")) or (path.root and not path.drive):
            fail("path", "UNC, device and root-relative paths are unsupported.", "unsupported")
        for part in path.parts[1:] if path.is_absolute() else path.parts:
            if part.endswith((" ", ".")) or re.search(r'[<>:"|?*\x00-\x1f]', part):
                fail("path", "Ambiguous Windows path segment.")
            if re.fullmatch(r"(?i:con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(?:\..*)?", part):
                fail("path", "Reserved Windows path segment.")
    if not path.is_absolute():
        if base is None:
            fail("path", "An explicit absolute root is required.")
        path = base / path
    # Refuse all links/reparse points, including contained ones; this avoids
    # mutable indirection in frozen bindings. Nonexistent tails remain lexical.
    for part in (*reversed(path.parents), path):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & REPARSE:
            fail("path-link", "Symlinks and reparse points are unsupported in selected paths.", "blocked")
    resolved = path.resolve(strict=False)
    if base is not None and not Path(value).is_absolute() and not beneath(resolved, base):
        fail("path-escape", "A relative path escapes its explicit root.", "blocked")
    return resolved


def read_bytes(path, missing="invalid-input"):
    safe_path(str(path))
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            fail("file-type", "A selected input is not a regular file.")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(path, flags), "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                fail("file-type", "A selected input is not a regular file.")
            raw = stream.read(LIMIT + 1)
            if len(raw) > LIMIT:
                fail("size-limit", "Selected file exceeds the 4 MiB limit.", "unsupported")
            if identity(path.lstat()) != identity(info):
                fail("input-drift", "Input identity changed during read.", "conflict")
            return raw
    except FileNotFoundError:
        fail("missing-file", "An explicitly selected file is missing.", missing)


def identity(info):
    return info.st_dev, info.st_ino


def resource(package, value):
    path = safe_path(value, package, relative_only=True)
    if not beneath(path, package) or not path.is_file():
        fail("resource", "Declared package resource is missing or outside the package.", "unsupported")
    return path


def load_package(package):
    metadata = parse_yaml(read_bytes(package / "skill-package.yaml", "unsupported"))
    fields(metadata, ("metadata_version", "id", "version", "delivery_status", "entrypoint",
                      "dependencies", "runtime", "configuration", "artifact_roles", "resources", "operations"), label="metadata")
    if type(metadata["metadata_version"]) is not int:
        fail("metadata-version", "metadata_version must be an integer.")
    if (metadata["metadata_version"] != 1 or metadata["id"] != "lesson" or
            metadata["version"] != "0.1.0" or metadata["delivery_status"] != "implemented"):
        fail("metadata-version", "Unsupported Lesson package identity, version or delivery state.", "unsupported")
    if metadata["entrypoint"] != "SKILL.md":
        fail("entrypoint", "Unsupported skill entrypoint.", "unsupported")
    fields(metadata["dependencies"], ("required", "optional"), label="dependencies")
    if metadata["dependencies"] != {"required": [], "optional": []}:
        fail("dependency-closure", "This Lesson version has no skill dependencies.", "unsupported")
    runtime_ids = []
    if type(metadata["runtime"]) is not list:
        fail("runtime", "runtime must be an array.")
    for item in metadata["runtime"]:
        fields(item, ("id", "for_operations", "on_missing"), ("version", "requirement", "purpose"), "runtime entry")
        runtime_ids.append(string(item["id"], "runtime id"))
        if not set(strings(item["for_operations"], "runtime operations", True)) <= set(OPERATIONS):
            fail("runtime", "Unknown runtime operation.")
        if item["on_missing"] != "unavailable" or ("version" in item) == ("requirement" in item):
            fail("runtime", "Runtime must declare one version or requirement and unavailable disposition.")
        for key in ("version", "requirement", "purpose"):
            if key in item:
                string(item[key], key)
        expected = {"python": ">=3.11,<4", "pyyaml": ">=6,<7", "jsonschema": ">=4.18,<5"}
        if item["id"] in expected and item.get("version") != expected[item["id"]]:
            fail("runtime-version", "Unsupported runtime requirement.", "unsupported")
    if sorted(runtime_ids) != sorted(("skill-instruction-reader", "python", "pyyaml", "jsonschema", "filesystem")):
        fail("runtime", "Unknown, missing or duplicate runtime identity.")
    fields(metadata["configuration"], ("namespace", "defaults"), label="configuration")
    if metadata["configuration"]["namespace"] != "lesson":
        fail("namespace", "Unsupported settings namespace.", "unsupported")
    settings(metadata["configuration"]["defaults"], complete=True)
    roles = metadata["artifact_roles"]
    if type(roles) is not list or len(roles) != 2:
        fail("roles", "Exactly the record and view roles are required.")
    by_role = {}
    for item in roles:
        if type(item) is not dict or type(item.get("role")) is not str or item["role"] in by_role:
            fail("roles", "Invalid or duplicate artifact role.")
        by_role[item.get("role")] = item
    if set(by_role) != {"lesson.record", "lesson.view"}:
        fail("roles", "Unknown artifact role.")
    fields(by_role["lesson.record"], ("role", "owner", "schema", "store_binding", "identity", "filename", "read_operations", "write_operations"))
    fields(by_role["lesson.view"], ("role", "owner", "source_role", "output", "persistence", "produce_operations"))
    record_role, view_role = by_role["lesson.record"], by_role["lesson.view"]
    if (record_role["owner"] != "project" or record_role["schema"] != "lesson.record@1.0.0" or
            record_role["store_binding"] != "lesson.store" or record_role["identity"] != "lesson-<32 lowercase hex digits>" or
            record_role["filename"] != "<id>.lesson.json" or
            record_role["read_operations"] != ["inspect", "query", "validate", "render"] or
            record_role["write_operations"] != ["create", "revise"] or view_role["owner"] != "derived" or
            view_role["source_role"] != "lesson.record" or view_role["produce_operations"] != ["render"]):
        fail("roles", "Unsupported artifact role contract.", "unsupported")
    string(view_role["output"], "view output")
    string(view_role["persistence"], "view persistence")
    resources = fields(metadata["resources"], ("references", "schemas", "templates", "tools"), label="resources")
    paths = [metadata["entrypoint"], "skill-package.yaml"]
    paths += strings(resources["references"], "references", True)
    for kind in ("schemas", "templates", "tools"):
        if type(resources[kind]) is not list or len(resources[kind]) != 1:
            fail("resources", f"Exactly one {kind} resource is required.")
    schema = fields(resources["schemas"][0], ("id", "version", "path", "owner", "migration"))
    template = fields(resources["templates"][0], ("id", "path", "input_role", "output_role", "owner"))
    tool = fields(resources["tools"][0], ("id", "owner", "implementation_status", "entrypoint", "operation_contract", "operations"))
    if (schema["id"] != "lesson.record" or schema["version"] != "1.0.0" or schema["owner"] != "lesson" or
            template["id"] != "lesson.default-view" or template["input_role"] != "lesson.record" or
            template["output_role"] != "lesson.view" or template["owner"] != "lesson" or
            tool["id"] != "lesson.fs" or tool["owner"] != "lesson" or tool["implementation_status"] != "implemented" or
            tool["entrypoint"] != "scripts/lesson.py" or tool["operations"] != list(OPERATIONS)):
        fail("resources", "Unsupported owned resource declaration.", "unsupported")
    string(schema["migration"], "migration disposition")
    if tool["operation_contract"] not in resources["references"]:
        fail("resources", "Operation contract must be a declared reference.")
    paths += [schema["path"], template["path"], tool["entrypoint"]]
    for path in paths:
        string(path, "resource path")
    if len(paths) != len(set(paths)):
        fail("resources", "Duplicate resource paths.")
    for path in paths:
        resource(package, path)
    if resource(package, tool["entrypoint"]) != Path(__file__).resolve():
        fail("package-binding", "Selected package does not own this executable.", "blocked")
    if type(metadata["operations"]) is not list:
        fail("operations", "operations must be an array.")
    operation_ids = []
    for item in metadata["operations"]:
        fields(item, ("id", "inputs", "outputs", "tool", "implementation_status"), label="operation")
        operation_ids.append(string(item["id"], "operation id"))
        strings(item["inputs"], "inputs", True)
        strings(item["outputs"], "outputs", True)
        if item["tool"] != "lesson.fs" or item["implementation_status"] != "implemented":
            fail("operation-state", "Tool operation is not implemented.", "unsupported")
    if operation_ids != list(OPERATIONS):
        fail("operations", "Unsupported operation declarations.", "unsupported")
    return metadata


def settings(value, complete=False):
    fields(value, ("store", "template") if complete else (), () if complete else ("store", "template"), "Lesson settings")
    if "store" in value:
        store = fields(value["store"], ("kind", "root", "tracking") if complete else (),
                       () if complete else ("kind", "root", "tracking"), "store settings")
        if "kind" in store and store["kind"] != "filesystem":
            fail("store-kind", "Only a filesystem store is supported.", "unsupported")
        if "root" in store:
            string(store["root"], "store.root")
        if "tracking" in store and store["tracking"] not in ("tracked", "ignored"):
            fail("tracking", "store.tracking must be tracked or ignored.")
    if "template" in value:
        template = fields(value["template"], ("origin", "path"), label="template")
        if template["origin"] not in ("package", "project"):
            fail("template-origin", "Unsupported template origin.")
        string(template["path"], "template.path")
    return value


def git_local_ignored(project, local):
    # A project without a .git marker in its ancestry needs no Git executable.
    if not any((parent / ".git").exists() for parent in (project, *project.parents)):
        return
    env = {key: val for key, val in os.environ.items() if not key.startswith("GIT_")}
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        top = subprocess.run(["git", "-C", str(project), "rev-parse", "--show-toplevel"],
                             capture_output=True, timeout=10, env=env, check=False)
        if top.returncode:
            fail("local-ignore", "Cannot establish Git ownership of local config.", "blocked")
        git_root = safe_path(top.stdout.decode("utf-8").strip())
        if not beneath(local, git_root):
            fail("local-ignore", "Local config must be an ignored file in this Git project.", "blocked")
        ignored = subprocess.run(["git", "-C", str(git_root), "check-ignore", "-q", "--", str(local)],
                                 capture_output=True, timeout=10, env=env, check=False)
        if ignored.returncode != 0:
            fail("local-ignore", "Selected local config is not ignored or is tracked.", "blocked")
    except FileNotFoundError:
        fail("git", "Git is required to prove selected local config is ignored.", "unavailable")
    except (subprocess.TimeoutExpired, UnicodeError):
        fail("local-ignore", "Could not establish the selected local config's ignored state.", "blocked")


def config(path, local=False):
    value = parse_json(read_bytes(path))
    fields(value, ("config_version",), ("skills",) if local else ("skills", "constraints"), "config")
    if type(value["config_version"]) is not int:
        fail("config-version", "config_version must have exact integer type.")
    if value["config_version"] != 1:
        fail("config-version", "Unsupported config version.", "unsupported")
    skills = fields(value.get("skills", {}), (), ("lesson",), "skills")
    lesson = settings(skills.get("lesson", {}))
    constraints = fields(value.get("constraints", {}), (), ("lesson",), "constraints")
    rules = fields(constraints.get("lesson", {}), (), ("write_roots", "locked_fields"), "Lesson constraints")
    if "write_roots" in rules:
        strings(rules["write_roots"], "write_roots", True)
    locks = strings(rules.get("locked_fields", []), "locked_fields")
    if not set(locks) <= {"store.root", "store.tracking", "template"}:
        fail("locked-fields", "Unknown locked field.")
    return lesson, rules


def merge_settings(target, layer, sources, source):
    if "store" in layer:
        for key, value in layer["store"].items():
            target["store"][key] = value
            sources["store." + key] = source
    if "template" in layer:
        target["template"] = copy.deepcopy(layer["template"])
        sources["template"] = source


def field_value(settings_value, field):
    return settings_value["template"] if field == "template" else settings_value["store"][field.split(".")[1]]


class Binding:
    def __init__(self, request):
        self.project = safe_path(request["project_root"])
        self.package = safe_path(request["package_root"])
        if not self.project.is_dir() or not self.package.is_dir():
            fail("root", "Explicit project and package roots must exist as directories.")
        self.metadata = load_package(self.package)
        self.settings = copy.deepcopy(self.metadata["configuration"]["defaults"])
        self.sources = {key: "default" for key in ("store.kind", "store.root", "store.tracking", "template")}
        self.config_paths = []
        project_layer, rules = {}, {}
        if "project_config" in request:
            project_path = safe_path(request["project_config"], self.project)
            self.config_paths.append(project_path)
            project_layer, rules = config(project_path)
        merge_settings(self.settings, project_layer, self.sources, "project")
        self.project_settings = copy.deepcopy(self.settings)
        self.locks = rules.get("locked_fields", [])
        self.allowed = [safe_path(value, self.project) for value in rules.get("write_roots", [self.settings["store"]["root"]])]
        self.caller_allowed = None
        if "write_roots" in request:
            self.caller_allowed = [safe_path(value, self.project) for value in strings(request["write_roots"], "caller write_roots", True)]
        # Absolute external stores require explicit project roots, even when
        # the root originated in project settings rather than an override.
        self.explicit_roots = "write_roots" in rules
        layers = []
        if "local_config" in request:
            local_path = safe_path(request["local_config"], self.project)
            self.config_paths.append(local_path)
            git_local_ignored(self.project, local_path)
            layers.append(("local", config(local_path, local=True)[0]))
        if "overrides" in request:
            layers.append(("invocation", settings(request["overrides"])))
        for source, layer in layers:
            merge_settings(self.settings, layer, self.sources, source)
            for locked in self.locks:
                if not exact_equal(field_value(self.settings, locked), field_value(self.project_settings, locked)):
                    fail("locked-field", f"Override changes project-locked field {locked}.", "blocked")
        self.store = safe_path(self.settings["store"]["root"], self.project)
        self.store_identity = identity(self.store.stat()) if self.store.exists() else None
        template = self.settings["template"]
        template_root = self.package if template["origin"] == "package" else self.project
        self.template_path = safe_path(template["path"], template_root)
        if not beneath(self.template_path, template_root):
            fail("template-boundary", "Template must stay within its declared root.", "blocked")
        if template["origin"] == "package" and self.template_path != resource(self.package, self.metadata["resources"]["templates"][0]["path"]):
            fail("template-resource", "A package template must be a declared template resource.")
        self.check_paths()
        try:
            self.template = read_bytes(self.template_path).decode("utf-8", errors="strict")
        except UnicodeError:
            fail("template-encoding", "Template must be UTF-8.")
        validate_template(self.template)
        self.validator = None
        if request["operation"] != "explain":
            dependency("jsonschema", (4, 18), (5, 0))
            try:
                from jsonschema import Draft202012Validator, FormatChecker
                schema = parse_json(read_bytes(resource(self.package, self.metadata["resources"]["schemas"][0]["path"])))
                # This schema family has no reference edges. Do not allow a
                # replaced schema to cause implicit network or filesystem reads.
                def no_refs(value):
                    if type(value) is dict:
                        if "$ref" in value or "$dynamicRef" in value:
                            fail("schema-ref", "References are unsupported in the initial record schema.", "unsupported")
                        for child in value.values():
                            no_refs(child)
                    elif type(value) is list:
                        for child in value:
                            no_refs(child)
                no_refs(schema)
                Draft202012Validator.check_schema(schema)
                self.validator = Draft202012Validator(schema, format_checker=FormatChecker())
            except ImportError:
                fail("dependency", "jsonschema could not be imported.", "unavailable")
            except Exception as exc:
                if isinstance(exc, Fault):
                    raise
                fail("schema", "Invalid owned record schema.")

    def check_paths(self):
        for path in (self.project, self.package, self.store, self.template_path, *self.config_paths, *self.allowed, *(self.caller_allowed or [])):
            if safe_path(str(path)) != path:
                fail("binding-drift", "Frozen path binding changed.", "conflict")
        if self.store == Path(self.store.anchor):
            fail("store-root", "Volume-root stores are forbidden.", "blocked")
        if self.store.exists() and not self.store.is_dir():
            fail("store-type", "Store must be a directory.")
        if self.store_identity is not None and (not self.store.exists() or identity(self.store.stat()) != self.store_identity):
            fail("store-drift", "Frozen store directory identity changed.", "conflict")
        if not any(beneath(self.store, root) for root in self.allowed):
            fail("write-boundary", "Selected store exceeds project write roots.", "blocked")
        if self.caller_allowed is not None and not any(beneath(self.store, root) for root in self.caller_allowed):
            fail("caller-boundary", "Selected store exceeds caller write roots.", "blocked")
        if not beneath(self.store, self.project) and not self.explicit_roots:
            fail("external-store", "An external store requires explicit project write_roots.", "blocked")
        if any(overlap(self.store, protected) for protected in (self.package, self.template_path, *self.config_paths)):
            fail("overlap", "Store overlaps installed package, config or template content.", "blocked")

    def explain(self):
        return {"settings": self.settings, "sources": self.sources, "project_root": str(self.project),
                "package_root": str(self.package), "store_root": str(self.store), "template_path": str(self.template_path),
                "locked_fields": self.locks, "write_roots": [str(p) for p in self.allowed],
                "caller_write_roots": None if self.caller_allowed is None else [str(p) for p in self.caller_allowed],
                "runtime_capability": "not-probed", "tracking": "intent-only", "unsupported_reasons": []}

    def record_path(self, ref):
        fields(ref, ("role", "id"), label="record reference")
        if ref["role"] != "lesson.record" or type(ref["id"]) is not str or not ID.fullmatch(ref["id"]):
            fail("reference", "Invalid store-scoped Lesson reference.")
        return safe_path(ref["id"] + ".lesson.json", self.store, relative_only=True)


def validate_template(template):
    found = set(TOKEN.findall(template))
    required = set(AUTHORED) | {"id", "schema_version"}
    if found - required - {"status"} or required - found:
        fail("template-token", "Template contains unknown tokens or omits required tokens.")
    remainder = TOKEN.sub("", template)
    if "{{" in remainder or "}}" in remainder:
        fail("template-token", "Malformed template token.")


def validate_record(binding, record, expected_id=None):
    fields(record, (*CONTROLLED, *AUTHORED), ("extensions",), "record")
    if type(record["schema_version"]) is not str:
        fail("record-version", "Record schema_version must be a string.")
    if record["schema_version"] != "1.0.0":
        fail("record-version", "Unsupported record schema version; original bytes preserved.", "unsupported")
    errors = sorted(binding.validator.iter_errors(record), key=lambda error: str(list(error.absolute_path)))
    if errors:
        fail("record-schema", "Record does not satisfy lesson.record@1.0.0.")
    if expected_id is not None and record["id"] != expected_id:
        fail("record-identity", "Filename and record identity differ.")
    if not ID.fullmatch(record["id"]):
        fail("record-identity", "Invalid Lesson identity.")
    if any(not re.fullmatch(r"[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+", key) for key in record.get("extensions", {})):
        fail("extension-name", "Extension keys must be exact dotted namespaces.")
    for field in ("title", "observation", "conclusion"):
        string(record[field], field)
    for field in ("applies_when", "does_not_apply_when", "follow_up"):
        for value in record[field]:
            string(value, field)
    for item in record["evidence"]:
        string(item["source"], "evidence source")
        string(item["note"], "evidence note")
    if not record["evidence"] and record["confidence"] != "tentative":
        fail("confidence", "Empty evidence requires tentative confidence.")
    try:
        created = datetime.fromisoformat(record["created_at"].upper().replace("Z", "+00:00"))
        updated = datetime.fromisoformat(record["updated_at"].upper().replace("Z", "+00:00"))
        if created.tzinfo is None or updated.tzinfo is None or updated < created:
            fail("record-time", "Record timestamps require zones and updated_at >= created_at.")
    except ValueError:
        fail("record-time", "Invalid record timestamps.")
    return record


def reference(record):
    return {"role": "lesson.record", "id": record["id"]}


def inspect_record(binding, ref):
    path = binding.record_path(ref)
    raw = read_bytes(path)
    record = validate_record(binding, parse_json(raw), ref["id"])
    return record, raw


def authored(value, extensions=False):
    return fields(value, AUTHORED, ("extensions",) if extensions else (), "authored content")


def new_record(content):
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    return {"schema_version": "1.0.0", "kind": "lesson", "owner": "project",
            "id": "lesson-" + uuid.uuid4().hex, "status": "candidate",
            "created_at": now, "updated_at": now, **copy.deepcopy(content)}


def query(binding, text):
    if type(text) is not str:
        fail("query-text", "Query text must be a string.")
    binding.check_paths()
    matches, diagnostics, inventory = [], [], []
    try:
        entries = sorted(binding.store.iterdir(), key=lambda p: p.name) if binding.store.exists() else []
    except OSError:
        fail("query-store", "Cannot enumerate the selected store.", "blocked")
    selected = [path for path in entries if path.name.endswith(".lesson.json")]
    if len(selected) > MAX_FILES:
        fail("query-limit", "Store exceeds the 10000 direct-record query limit.", "unsupported")
    for path in selected:
        item = {"filename": path.name}
        try:
            raw = read_bytes(path)
            item["sha256"] = digest(raw)
            record_id = path.name.removesuffix(".lesson.json")
            if not ID.fullmatch(record_id):
                fail("filename", "Unsafe Lesson filename.")
            record = validate_record(binding, parse_json(raw), record_id)
            if any(text.casefold() in record[key].casefold() for key in ("title", "observation", "conclusion")):
                matches.append({"reference": reference(record), "title": record["title"], "sha256": item["sha256"]})
        except (Fault, OSError) as exc:
            diagnostic = exc.diagnostic() if isinstance(exc, Fault) else {"code": "read-error", "message": "Selected record is unreadable."}
            item["error"] = diagnostic["code"]
            diagnostics.append({"filename": path.name, **diagnostic})
        inventory.append(item)
    # Includes even nonmatching/malformed raw bytes; unreadable files bind
    # filename/error only, hence partial acknowledgment is never completeness.
    subject = {"query_version": 1, "store_root": str(binding.store), "text": text,
               "record_schema": "1.0.0", "inventory": inventory}
    return {"store_root": str(binding.store), "text": text, "matches": matches,
            "partial": bool(diagnostics), "diagnostics": diagnostics,
            "query_sha256": digest(encode(subject)), "selected_count": len(selected)}


def local_write_backend(store):
    ancestor = store
    while not ancestor.exists():
        ancestor = ancestor.parent
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        root = ctypes.create_unicode_buffer(32768)
        kernel.GetVolumePathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        kernel.GetVolumePathNameW.restype = ctypes.c_int
        if not kernel.GetVolumePathNameW(str(ancestor), root, len(root)):
            fail("filesystem", "Cannot identify the local write volume.", "unsupported")
        kernel.GetDriveTypeW.argtypes = [ctypes.c_wchar_p]
        kernel.GetDriveTypeW.restype = ctypes.c_uint32
        if kernel.GetDriveTypeW(root.value) not in (3, 6):
            fail("filesystem", "Only local fixed or RAM volumes are supported for writes.", "unsupported")
        filesystem = ctypes.create_unicode_buffer(64)
        kernel.GetVolumeInformationW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32,
                                               ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                               ctypes.c_wchar_p, ctypes.c_uint32]
        kernel.GetVolumeInformationW.restype = ctypes.c_int
        if not kernel.GetVolumeInformationW(root.value, None, 0, None, None, None, filesystem, len(filesystem)) or filesystem.value != "NTFS":
            fail("filesystem", "Initial Windows writes require local NTFS.", "unsupported")
        return "local-ntfs"
    if sys.platform.startswith("linux"):
        try:
            mounts = Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines()
            candidates = []
            for line in mounts:
                left, right = line.split(" - ", 1)
                mount_path = re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), left.split()[4])
                if beneath(ancestor, Path(mount_path)):
                    candidates.append((len(Path(mount_path).parts), right.split()[0]))
            filesystem = max(candidates)[1] if candidates else ""
        except (OSError, ValueError, IndexError):
            fail("filesystem", "Cannot identify the local write mount.", "unsupported")
        if filesystem not in {"ext2", "ext3", "ext4", "xfs", "btrfs", "tmpfs", "ramfs"}:
            fail("filesystem", "Unproven, shared or network write backend is unsupported.", "unsupported")
        return "local-" + filesystem
    fail("filesystem", "Write publication semantics are unsupported on this platform.", "unsupported")


class Writer:
    """Own only an exclusive token lock and temp inode; never recover others."""
    def __init__(self, binding):
        self.binding = binding
        self.token = uuid.uuid4().hex
        self.lock = binding.store / ".lesson-write.lock"
        self.temp = binding.store / (".lesson-" + self.token + ".tmp")
        self.owned = {}
        self.mutation_state = "none"
        self.directories_created = []

    def exclusive(self, path, raw):
        self.binding.check_paths()
        safe_path(str(path))
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o600)
        # Register ownership before I/O so partial-write failures can be cleaned.
        self.owned[path] = (identity(os.fstat(fd)), raw, False)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.owned[path] = (self.owned[path][0], raw, True)

    def acquire(self, allow_create):
        self.binding.check_paths()
        local_write_backend(self.binding.store)
        if not self.binding.store.exists() and not allow_create:
            fail("missing-store", "Revise requires an existing store and candidate.")
        missing = []
        cursor = self.binding.store
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        for path in reversed(missing):
            self.binding.check_paths()
            if not any(beneath(path, root) for root in self.binding.allowed):
                fail("parent-permission", "Missing store parent is outside project write_roots; provision it separately.", "blocked")
            if self.binding.caller_allowed is not None and not any(beneath(path, root) for root in self.binding.caller_allowed):
                fail("parent-permission", "Missing store parent is outside caller write_roots.", "blocked")
            try:
                path.mkdir()
                self.directories_created.append(str(path))
            except FileExistsError:
                if not path.is_dir():
                    raise
        self.binding.store_identity = identity(self.binding.store.stat())
        try:
            self.exclusive(self.lock, (self.token + "\n").encode("ascii"))
        except FileExistsError:
            fail("writer-lock", "Store has an existing writer lock; no stale-lock recovery attempted.", "conflict")
        self.binding.check_paths()

    def publish(self, path, raw, replacing):
        if len(raw) > LIMIT:
            fail("size-limit", "Serialized record exceeds the 4 MiB limit.", "unsupported")
        self.exclusive(self.temp, raw)
        self.binding.check_paths()
        safe_path(str(path))
        self.mutation_state = "unknown"
        try:
            if replacing:
                os.replace(self.temp, path)
                del self.owned[self.temp]
            else:
                os.link(self.temp, path)  # Atomic complete-file, exclusive publish.
        except FileExistsError:
            self.mutation_state = "none"
            fail("record-collision", "Create identity already exists; no overwrite.", "conflict")
        self.mutation_state = "committed"
        if read_bytes(path) != raw:
            self.mutation_state = "unknown"
            fail("publication-readback", "Published bytes could not be confirmed; reread before retry.", "failed")

    def cleanup(self):
        failures = []
        for path in (self.temp, self.lock):
            if path not in self.owned:
                continue
            expected_identity, raw, complete = self.owned[path]
            try:
                self.binding.check_paths()
                safe_path(str(path))
                info = path.lstat()
                if identity(info) != expected_identity or not stat.S_ISREG(info.st_mode):
                    fail("cleanup-identity", "Owned transient file identity changed.", "failed")
                actual = read_bytes(path)
                # A partial lock is not a matching-token lock: preserve it for
                # explicit recovery. Temp partial bytes remain ours by inode.
                if (path == self.lock or complete) and actual != raw:
                    fail("cleanup-content", "Owned transient content changed; preserved.", "failed")
                path.unlink()
            except Exception:
                failures.append({"code": "cleanup-failed", "resource": "lock" if path == self.lock else "temporary-file",
                                 "message": "Owned transient cleanup failed; inspect before retry."})
        return failures


def write_operation(binding, request):
    operation = request["operation"]
    content = authored(request["content"], extensions=operation == "create")
    related = None
    # A generated, unpersisted validation candidate is internal only.
    candidate = new_record(content)
    validate_record(binding, candidate)
    if operation == "create":
        decision = fields(request["decision"], ("action", "query_sha256", "acknowledge_partial", "reason"), label="create decision")
        if decision["action"] != "new":
            fail("create-decision", "Choose new explicitly, or invoke revise for a selected existing reference.")
        if type(decision["query_sha256"]) is not str or not SHA256.fullmatch(decision["query_sha256"]):
            fail("query-digest", "Expected actual query SHA-256.")
        if type(decision["acknowledge_partial"]) is not bool:
            fail("decision", "acknowledge_partial must be a boolean.")
        string(decision["reason"], "decision reason")
        if type(request["text"]) is not str:
            fail("query-text", "Query text must be a string.")
    else:
        binding.record_path(request["reference"])
        if type(request["expected_sha256"]) is not str or not SHA256.fullmatch(request["expected_sha256"]):
            fail("expected-digest", "Expected a lowercase raw-byte SHA-256.")
    writer = Writer(binding)
    result = {"outcome": "failed"}
    try:
        writer.acquire(allow_create=operation == "create")
        if operation == "create":
            related = query(binding, request["text"])
            if related["query_sha256"] != decision["query_sha256"]:
                fail("query-conflict", "Collection or query changed; review the returned query and decide again.", "conflict")
            if related["partial"] and not decision["acknowledge_partial"]:
                fail("partial-query", "Explicit acknowledgment of this partial query is required.", "blocked")
            record = candidate
            path = binding.record_path(reference(record))
            raw = encode(record)
            writer.publish(path, raw, replacing=False)
            changed = True
        else:
            current, original = inspect_record(binding, request["reference"])
            if digest(original) != request["expected_sha256"]:
                fail("digest-conflict", "Record raw bytes changed; inspect before revising.", "conflict")
            if all(exact_equal(current[key], content[key]) for key in AUTHORED):
                record, raw, changed = current, original, False
            else:
                record = copy.deepcopy(current)
                record.update(copy.deepcopy(content))
                now = datetime.now(timezone.utc)
                if now < datetime.fromisoformat(current["updated_at"].upper().replace("Z", "+00:00")):
                    fail("clock-regression", "Actual clock precedes the record update time; no fabricated timestamp.", "blocked")
                record["updated_at"] = now.isoformat(timespec="microseconds")
                validate_record(binding, record, current["id"])
                path = binding.record_path(request["reference"])
                # Narrow the external-editor race; cooperating writers remain
                # mandatory because compare+replace is not filesystem CAS.
                if digest(read_bytes(path)) != request["expected_sha256"]:
                    fail("digest-conflict", "Record changed during revision; no replacement.", "conflict")
                raw = encode(record)
                writer.publish(path, raw, replacing=True)
                changed = True
        result = {"outcome": "succeeded", "reference": reference(record), "sha256": digest(raw),
                  "store_root": str(binding.store), "changed": changed}
    except Fault as exc:
        result = {"outcome": exc.outcome, "diagnostics": [exc.diagnostic()]}
    except OSError:
        result = {"outcome": "blocked" if writer.mutation_state == "none" else "failed",
                  "diagnostics": [{"code": "write-io", "message": "Write failed; no fallback storage was selected."}]}
    except (Exception, KeyboardInterrupt):
        result = {"outcome": "failed", "diagnostics": [{"code": "write-failure", "message": "Unexpected write failure; inspect before retry."}]}
    finally:
        cleanup = writer.cleanup()
        if cleanup:
            result["outcome"] = "failed"
            result.setdefault("diagnostics", []).extend(cleanup)
        result["mutation_state"] = writer.mutation_state
        result["directories_created"] = writer.directories_created
        if related is not None:
            result["related_query"] = related
    return result


def escape_markdown(text):
    escaped = html.escape(text, quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", escaped)


def render(binding, record):
    def display(value):
        if type(value) is list:
            if not value:
                return "None supplied"
            lines = []
            for item in value:
                text = item["source"] + ": " + item["note"] if type(item) is dict else item
                lines.append("- " + escape_markdown(text).replace("\n", "\n  "))
            return "\n".join(lines)
        return escape_markdown(value)
    return TOKEN.sub(lambda match: display(record[match[1]]), binding.template)


def execute(request):
    common = ("operation", "project_root", "package_root")
    optional = ("project_config", "local_config", "overrides", "write_roots")
    if type(request) is not dict or type(request.get("operation")) is not str:
        fail("request", "Request must name an operation.")
    operation = request["operation"]
    if operation not in OPERATIONS:
        fail("operation", "Unsupported operation; candidate-only operations are declared in metadata.", "unsupported")
    required = {"explain": (), "query": (), "create": ("content", "text", "decision"),
                "revise": ("reference", "expected_sha256", "content"), "inspect": ("reference",),
                "validate": ("reference",), "render": ("reference",)}[operation]
    fields(request, (*common, *required), (*optional, *(("text",) if operation == "query" else ())), "request")
    if not (3, 11) <= sys.version_info[:2] < (4, 0):
        fail("python-version", "Python >=3.11,<4 is required.", "unavailable")
    binding = Binding(request)
    if operation == "explain":
        return {"outcome": "succeeded", **binding.explain()}
    if operation == "query":
        return {"outcome": "succeeded", **query(binding, request.get("text", ""))}
    if operation in ("create", "revise"):
        return write_operation(binding, request)
    record, raw = inspect_record(binding, request["reference"])
    result = {"outcome": "succeeded", "reference": reference(record), "sha256": digest(raw), "store_root": str(binding.store)}
    if operation == "inspect":
        result["record"] = record
    elif operation == "validate":
        result.update(valid=True, diagnostics=[])
    else:
        result.update(view={"role": "lesson.view", "source": reference(record), "schema_version": record["schema_version"],
                            "markdown": render(binding, record)})
    return result


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        fail("arguments", "Use --request <explicit JSON file or ->.")


def main():
    operation = None
    try:
        parser = ArgumentParser(description=__doc__, allow_abbrev=False)
        parser.add_argument("--request", required=True, help="Absolute JSON request filename, or - for stdin")
        args = parser.parse_args()
        if args.request == "-":
            raw = sys.stdin.buffer.read(LIMIT + 1)
            if len(raw) > LIMIT:
                fail("size-limit", "Request exceeds the 4 MiB limit.", "unsupported")
        else:
            raw = read_bytes(safe_path(args.request))
        request = parse_json(raw)
        if type(request) is dict and type(request.get("operation")) is str and request["operation"] in OPERATIONS:
            operation = request["operation"]
        result = execute(request)
    except Fault as exc:
        result = {"outcome": exc.outcome, "diagnostics": [exc.diagnostic()]}
    except OSError:
        result = {"outcome": "blocked", "diagnostics": [{"code": "read-io", "message": "Selected input is inaccessible."}]}
    except Exception:
        result = {"outcome": "failed", "diagnostics": [{"code": "internal", "message": "Unexpected failure; inputs were not echoed."}]}
    result = {"operation": operation, "mutation_state": "none", **result}
    sys.stdout.buffer.write(encode(result))
    return 0 if result["outcome"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
