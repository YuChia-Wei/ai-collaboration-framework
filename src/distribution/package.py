"""Consume explicit package metadata versions 1/2/3; never resolve project settings."""

from __future__ import annotations

from dataclasses import dataclass
import posixpath
import re
from urllib.parse import unquote, urlsplit

from .data import (Paths, identifier, json_object, mapping, path, require,
                   sequence, string, version, version_one, yaml_object)
from .git_source import Blob


def text_array(value, label: str) -> list[str]:
    values = [string(item, label) for item in sequence(value, label)]
    require(len(values) == len(set(values)), f"{label}: duplicate entries")
    return values


def named(value, required: set[str], optional: set[str], label: str) -> dict[str, dict]:
    result = {}
    for item in sequence(value, label):
        item = mapping(item, required | {"id"}, optional, label)
        name = identifier(item["id"], label)
        require(name not in result, f"{label}: duplicate ID {name}")
        result[name] = item
    return result


@dataclass(frozen=True)
class Package:
    metadata: dict
    members: frozenset[str]

    @property
    def id(self) -> str:
        return self.metadata["id"]

    @property
    def version(self) -> str:
        return self.metadata["version"]


def load_package(blob: Blob) -> Package:
    label = blob.path
    data = mapping(yaml_object(blob.data, label), {
        "metadata_version", "id", "version", "delivery_status", "entrypoint",
        "dependencies", "runtime", "configuration", "artifact_roles", "resources", "operations",
    }, set(), label)
    metadata_version = data["metadata_version"]
    if type(metadata_version) is int and metadata_version == 1:
        version_one(metadata_version, label)
    else:
        require(type(metadata_version) is int and metadata_version in {2, 3},
                f"{label}: only integer metadata versions 1, 2 and 3 are supported")
    owner = identifier(data["id"], label)
    version(data["version"], label)
    require(data["delivery_status"] == "implemented", f"{owner}: design-only packages cannot be built as implemented candidates")
    require(data["entrypoint"] == "SKILL.md", f"{owner}: version {metadata_version} entrypoint must be SKILL.md")
    declared = Paths()
    members = set()

    def member(value, purpose):
        value = path(value, f"{owner} {purpose}")
        declared.add(value, f"{owner} {purpose}")
        members.add(value)
        return value

    member("SKILL.md", "entrypoint")
    member("skill-package.yaml", "metadata")
    dependencies = mapping(data["dependencies"], {"required", "optional"}, set(), label)
    required = named(dependencies["required"], {"version"}, set(), f"{owner} required dependencies")
    optional = named(dependencies["optional"], {"version", "operations", "on_missing"}, set(), f"{owner} optional dependencies")
    require(not required.keys() & optional.keys(), f"{owner}: dependency cannot be both required and optional")
    for dep in (*required.values(), *optional.values()):
        version(dep["version"], f"{owner} dependency {dep['id']}")
        require(dep["id"] != owner, f"{owner}: self dependency is forbidden")
    for dep in optional.values():
        require(bool(text_array(dep["operations"], label)), f"{owner}: optional dependency needs public operations")
        require(dep["on_missing"] in {"return-candidate", "unsupported"}, f"{owner}: unsupported optional absence behavior")

    resources = mapping(data["resources"], {"references", "schemas", "templates", "tools"}, set(), label)
    for reference in sequence(resources["references"], label):
        member(reference, "reference")
    if metadata_version == 1:
        schemas = named(resources["schemas"], {"version", "path", "owner", "migration"}, set(), label)
    else:
        # Only schemas gain pair identities. Keep named() unchanged for v1 and
        # every other resource/dependency/operation consumer.
        schemas = {}
        for schema in sequence(resources["schemas"], label):
            mapping(schema, {"id", "version", "path", "owner", "migration"}, set(), label)
            identity = (identifier(schema["id"], label), version(schema["version"], label))
            require(identity not in schemas, f"{owner}: duplicate schema identity {identity[0]}@{identity[1]}")
            schemas[identity] = schema
    templates = named(resources["templates"], {"path", "input_role", "output_role", "owner"}, set(), label)
    tools = named(resources["tools"], {"owner", "implementation_status", "entrypoint", "operation_contract", "operations"}, set(), label)
    resource_ids = [*{item["id"] for item in schemas.values()}, *templates, *tools]
    require(len(resource_ids) == len(set(resource_ids)), f"{owner}: duplicate resource identity")
    for schema in schemas.values():
        version(schema["version"], label)
        string(schema["migration"], label)
    for resource in (*schemas.values(), *templates.values(), *tools.values()):
        require(resource["owner"] == owner, f"{owner}: resource owner mismatch")
        if "path" in resource:
            member(resource["path"], "resource")
        else:
            require(resource["implementation_status"] == "implemented",
                    f"{owner}: tool {resource['id']} must name its actual implemented entrypoint")
            member(resource["entrypoint"], "tool")
            require(resource["operation_contract"] in resources["references"],
                    f"{owner}: operation contract must be a declared reference")
            require(bool(text_array(resource["operations"], label)), f"{owner}: tool needs operations")

    operation_fields = {"inputs", "outputs", "implementation_status"}
    if metadata_version == 3:
        operations = named(data["operations"], operation_fields | {"execution"},
                           {"tool", "instructions"}, label)
    else:
        operations = named(data["operations"], operation_fields | {"tool"}, set(), label)
    require(bool(operations), f"{owner}: operations cannot be empty")
    tool_operations = {}
    for operation_id, operation in operations.items():
        operation_label = f"{owner}.{operation_id}"
        text_array(operation["inputs"], label)
        text_array(operation["outputs"], label)
        require(operation["implementation_status"] == "implemented", f"{operation_label}: operation is not implemented")
        if metadata_version == 3:
            execution = string(operation["execution"], operation_label)
            require(execution in {"instruction", "tool"}, f"{operation_label}: unknown execution kind")
            arm = "instructions" if execution == "instruction" else "tool"
            mapping(operation, operation_fields | {"id", "execution", arm}, set(), operation_label)
            if execution == "instruction":
                instruction = path(operation["instructions"], operation_label)
                require(instruction in resources["references"],
                        f"{operation_label}: instructions must be a declared reference")
                continue
        tool_id = string(operation["tool"], label)
        require(tool_id in tools and operation_id in tools[tool_id]["operations"],
                f"{operation_label}: tool mapping is inconsistent")
        tool_operations[operation_id] = tool_id
    for tool_id, tool in tools.items():
        require(set(tool["operations"]) == {key for key, value in tool_operations.items() if value == tool_id},
                f"{owner}.{tool_id}: public operations and tool operations disagree")

    runtimes = named(data["runtime"], {"for_operations", "on_missing"}, {"requirement", "version", "purpose"}, label)
    for runtime in runtimes.values():
        require("requirement" in runtime or "version" in runtime, f"{owner}: runtime needs requirement or version")
        for key in ("requirement", "version", "purpose"):
            if key in runtime:
                string(runtime[key], label)
        require(runtime["on_missing"] == "unavailable", f"{owner}: unsupported runtime absence behavior")
        require(set(text_array(runtime["for_operations"], label)) <= operations.keys(),
                f"{owner}: runtime names unknown operations")

    roles = {}
    for role in sequence(data["artifact_roles"], label):
        require(type(role) is dict, f"{owner}: artifact role must be an object")
        if role.get("owner") == "project":
            role_fields = {"role", "owner", "schema", "store_binding", "identity", "filename", "read_operations", "write_operations"}
            if metadata_version in {2, 3}:
                role_fields.add("read_schemas")
            mapping(role, role_fields, set(), label)
            declared_schemas = {f"{item['id']}@{item['version']}" for item in schemas.values()}
            if metadata_version in {2, 3}:
                string(role["schema"], label)
                readable = text_array(role["read_schemas"], label)
                require(bool(readable) and set(readable) <= declared_schemas,
                        f"{owner}: read_schemas must name nonempty declared exact schema references")
                require(role["schema"] in readable, f"{owner}: read_schemas must include the writable schema")
            require(role["schema"] in declared_schemas,
                    f"{owner}: artifact role references an undeclared schema")
            for key in ("read_operations", "write_operations"):
                require(set(text_array(role[key], label)) <= operations.keys(), f"{owner}: role names unknown operations")
            for key in ("store_binding", "identity", "filename"):
                string(role[key], label)
        else:
            mapping(role, {"role", "owner", "source_role", "output", "persistence", "produce_operations"}, set(), label)
            require(role["owner"] == "derived", f"{owner}: unsupported artifact owner")
            require(set(text_array(role["produce_operations"], label)) <= operations.keys(), f"{owner}: role names unknown operations")
            for key in ("source_role", "output", "persistence"):
                string(role[key], label)
        role_id = identifier(role["role"], label)
        require(role_id not in roles, f"{owner}: duplicate artifact role")
        roles[role_id] = role
    for role in roles.values():
        if role["owner"] == "derived":
            require(role["source_role"] in roles and roles[role["source_role"]]["owner"] == "project",
                    f"{owner}: derived role must reference a declared project record")
    for template in templates.values():
        require(template["input_role"] in roles and template["output_role"] in roles,
                f"{owner}: template role binding is missing")

    if metadata_version == 3 and data["configuration"] is None:
        require(not roles and not schemas and not templates,
                f"{owner}: null configuration requires empty artifact_roles, schemas and templates")
    else:
        config = mapping(data["configuration"], {"namespace", "defaults"}, set(), label)
        require(config["namespace"] == owner, f"{owner}: configuration namespace mismatch")
        defaults = mapping(config["defaults"], {"store", "template"}, set(), label)
        store = mapping(defaults["store"], {"kind", "root", "tracking"}, set(), label)
        require(store["kind"] == "filesystem" and store["tracking"] in {"tracked", "ignored"},
                f"{owner}: unsupported default store")
        path(store["root"], f"{owner} default store")
        template = mapping(defaults["template"], {"origin", "path"}, set(), label)
        require(template["origin"] == "package" and template["path"] in {item["path"] for item in templates.values()},
                f"{owner}: default template must be a declared package resource")
    return Package(data, frozenset(members))


def _same_document_schema_reference(document: dict, reference: str, label: str) -> None:
    """Inspect one finite JSON pointer; never expand refs or invoke a resolver.

    The selected document is the only lookup root. A target containing another
    reference is not followed, so chained/cyclic refs cannot trigger unbounded
    resolution. Schema validation remains the package owner's responsibility.
    """
    require(reference.startswith("#/$defs/"),
            f"{label}: metadata v2/v3 schema references must use same-document #/$defs/ pointers")
    require(re.search(r"%(?![0-9a-fA-F]{2})", reference) is None,
            f"{label}: malformed schema reference escape")
    pointer = unquote(reference[1:], encoding="utf-8", errors="strict")
    target = document
    for token in pointer[1:].split("/"):
        require(re.search(r"~(?![01])", token) is None, f"{label}: malformed JSON pointer escape")
        token = token.replace("~1", "/").replace("~0", "~")
        if type(target) is dict:
            require(token in target, f"{label}: schema reference target is missing")
            target = target[token]
        elif type(target) is list:
            require(re.fullmatch(r"0|[1-9][0-9]*", token) is not None
                    and len(token) <= len(str(len(target))), f"{label}: invalid schema reference index")
            index = int(token)
            require(index < len(target), f"{label}: schema reference target is missing")
            target = target[index]
        else:
            require(False, f"{label}: schema reference traverses a scalar")
    require(type(target) in {dict, bool}, f"{label}: schema reference must select an object or boolean schema")


def check_references(package: Package, blobs: dict[str, Blob]) -> dict:
    """Check portable document/schema file references without executing package tools."""
    def local_reference(source_name: str, target: str, allow_web: bool = False):
        target = unquote(target.strip("<>"))
        parsed = urlsplit(target)
        if parsed.scheme in {"https", "http", "mailto"} and allow_web:
            return  # Citation, not a build input or fetched resource.
        require(not parsed.scheme and not parsed.netloc and not parsed.query,
                f"{package.id}/{source_name}: non-portable resource reference {target!r}")
        if not parsed.path:
            return
        require(not parsed.path.startswith(("/", "\\")) and "\\" not in parsed.path,
                f"{package.id}/{source_name}: absolute resource reference {target!r}")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source_name), parsed.path))
        require(resolved in package.members,
                f"{package.id}/{source_name}: reference {target!r} is outside the selected package closure")

    if package.metadata["metadata_version"] == 3:
        for operation in package.metadata["operations"]:
            if operation["execution"] == "instruction":
                name = operation["instructions"]
                require(name in blobs, f"{package.id}: instruction reference is missing: {name}")
                # Instructions are UTF-8 text even when their extension is not .md.
                # Reading source establishes presence, never invocation or approval.
                blobs[name].data.decode("utf-8", errors="strict")

    for name, blob in blobs.items():
        if name.endswith(".md"):
            text = blob.data.decode("utf-8", errors="strict")
            # Standard inline links/images and reference definitions. Arbitrary prose
            # and dynamic Python access remain content-review/P7 responsibilities.
            for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", text):
                local_reference(name, match.group(1), allow_web=True)
            for match in re.finditer(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)", text, re.MULTILINE):
                local_reference(name, match.group(1), allow_web=True)
    for item in package.metadata["resources"]["schemas"]:
        name = item["path"]
        schema = json_object(blobs[name].data, name)
        require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
                f"{package.id}/{name}: only Draft 2020-12 schemas are supported")

        def walk(value):
            if type(value) is dict:
                for key, child in value.items():
                    if key in {"$ref", "$dynamicRef"}:
                        if package.metadata["metadata_version"] == 1:
                            local_reference(name, string(child, name))
                        else:
                            _same_document_schema_reference(schema, string(child, name), f"{package.id}/{name}")
                    walk(child)
            elif type(value) is list:
                for child in value:
                    walk(child)
        walk(schema)
    entry = blobs[package.metadata["entrypoint"]].data.decode("utf-8", errors="strict")
    frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", entry, re.DOTALL)
    require(frontmatter is not None, f"{package.id}: SKILL.md needs name/description frontmatter")
    fields = mapping(yaml_object(frontmatter.group(1).encode("utf-8"), f"{package.id} frontmatter"),
                     {"name", "description"}, set(), f"{package.id} frontmatter")
    require(fields["name"] == package.id, f"{package.id}: SKILL.md name mismatch")
    string(fields["description"], f"{package.id} description")
    return fields
