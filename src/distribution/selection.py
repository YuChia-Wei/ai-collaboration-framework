"""Exact allowlist and required-closure selection from one immutable Git tree."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .codex import project_entry
from .data import Paths, identifier, mapping, path, require, sequence, version, version_one, yaml_object
from .git_source import Blob, GitSource
from .package import Package, check_references, load_package, named, text_array


@dataclass(frozen=True)
class Member:
    envelope: str
    destination: str
    owner: str
    mode: str
    data: bytes
    source: Blob | None = None

    @property
    def candidate_path(self) -> str:
        return f"{self.envelope}/{self.destination}"

    def identity(self) -> dict:
        value = {"path": self.candidate_path, "destination": self.destination,
                 "owner": self.owner, "kind": self.envelope, "mode": self.mode,
                 "size": len(self.data), "sha256": sha256(self.data).hexdigest()}
        if self.source:
            value["source"] = self.source.identity()
        return value


@dataclass(frozen=True)
class Selection:
    profile: str
    packages: tuple[Package, ...]
    members: tuple[Member, ...]
    adapters: tuple[dict, ...]


def select(source: GitSource, profile_id: str) -> Selection:
    identifier(profile_id, "profile")
    manifest_path = "src/distribution/manifest.yaml"
    manifest = mapping(yaml_object(source.read(manifest_path).data, manifest_path),
                       {"manifest_version", "profiles", "components", "adapters"}, set(), manifest_path)
    version_one(manifest["manifest_version"], manifest_path)
    profiles = named(manifest["profiles"], {"path"}, set(), "manifest profiles")
    components = named(manifest["components"], {"source", "metadata", "members"}, set(), "manifest components")
    adapters = named(manifest["adapters"], {"template"}, set(), "manifest adapters")
    require(profile_id in profiles, f"unknown profile {profile_id!r}; choose an explicitly declared profile")

    # Validate all manifest mappings for ownership/collisions, but read only the
    # selected blobs. Unselected components never enter the payload or closure.
    input_paths, output_paths = Paths(), Paths()
    input_paths.add(manifest_path, "manifest")
    for key, item in profiles.items():
        require(path(item["path"], key) == f"src/profiles/{key}.yaml", f"{key}: profile input must stay in src/profiles")
        input_paths.add(item["path"], key)
    for key, item in adapters.items():
        require(key == "codex" and item["template"] == "src/adapters/codex/skill-entry.md.template",
                f"{key}: only the explicit Codex adapter is implemented")
        input_paths.add(item["template"], key)
    maps = {}
    for key, component in components.items():
        require(component["source"] == f"src/skills/{key}" and component["metadata"] == "skill-package.yaml",
                f"{key}: component must use its own src/skills directory and skill-package.yaml")
        members = {}
        for row in sequence(component["members"], f"{key} members"):
            mapping(row, {"source", "destination"}, set(), f"{key} member")
            member_path = path(row["source"], f"{key} source")
            destination = path(row["destination"], f"{key} destination")
            require(destination == f".ai/core/skills/{key}/{member_path}",
                    f"{key}/{member_path}: destination must preserve the package-relative path in managed core")
            input_paths.add(f"{component['source']}/{member_path}", key)
            output_paths.add(destination, key)
            members[member_path] = destination
        require(bool(members), f"{key}: empty component allowlist")
        maps[key] = members

    profile_path = profiles[profile_id]["path"]
    profile = mapping(yaml_object(source.read(profile_path).data, profile_path),
                      {"profile_version", "id", "skills", "adapters"}, set(), profile_path)
    version_one(profile["profile_version"], profile_path)
    require(profile["id"] == profile_id, "profile ID does not match its manifest binding")
    requested = named(profile["skills"], {"version"}, set(), f"{profile_id} skills")
    require(bool(requested), "profile must explicitly select at least one skill")
    selected_adapters = text_array(profile["adapters"], "profile adapters")
    require(set(selected_adapters) <= adapters.keys(), "profile selects an undeclared adapter")

    packages: dict[str, Package] = {}
    contents: dict[str, dict[str, Blob]] = {}
    for key, request in requested.items():
        version(request["version"], f"{key} selected version")
        require(key in components, f"{key}: selected component missing from manifest")
        component = components[key]
        package = load_package(source.read(f"{component['source']}/{component['metadata']}"))
        require(package.id == key and package.version == request["version"],
                f"{key}: metadata identity disagrees with exact profile selection")
        manifest_members = set(maps[key])
        require(manifest_members == package.members,
                f"{key}: metadata/manifest closure mismatch; missing from manifest {sorted(package.members - manifest_members)}; "
                f"undeclared manifest members {sorted(manifest_members - package.members)}; reconcile both explicitly")
        packages[key] = package
        contents[key] = {member: source.read(f"{component['source']}/{member}") for member in sorted(package.members)}

    visiting, visited = set(), set()

    def visit(key: str):
        require(key not in visiting, f"required dependency cycle includes {key}")
        if key in visited:
            return
        visiting.add(key)
        package = packages[key]
        for dependency in package.metadata["dependencies"]["required"]:
            target = dependency["id"]
            require(target in packages, f"{key} requires unselected {target}@{dependency['version']}; explicitly select it, no fetch is performed")
            require(packages[target].version == dependency["version"], f"{key}: incompatible required version for {target}")
            visit(target)
        for dependency in package.metadata["dependencies"]["optional"]:
            target = dependency["id"]
            if target in packages:
                require(packages[target].version == dependency["version"], f"{key}: incompatible explicitly selected optional {target}")
                operations = {item["id"] for item in packages[target].metadata["operations"]}
                require(set(dependency["operations"]) <= operations, f"{key}: optional {target} lacks a declared public operation")
        visiting.remove(key)
        visited.add(key)

    for key in sorted(packages):
        visit(key)
    members = []
    adapter_records = []
    for key in sorted(packages):
        package = packages[key]
        frontmatter = check_references(package, contents[key])
        for name, blob in sorted(contents[key].items()):
            members.append(Member("payload", maps[key][name], key, blob.mode, blob.data, blob))
        for adapter_id in sorted(selected_adapters):
            template = source.read(adapters[adapter_id]["template"])
            destination, data = project_entry(template.data, key, package.version, frontmatter["description"], maps[key])
            output_paths.add(destination, f"{adapter_id}/{key}")
            member = Member("runtime", destination, f"{adapter_id}/{key}", "100644", data)
            members.append(member)
            adapter_records.append({"id": adapter_id, "package": key, "template": template.identity(),
                                    "installed_entrypoint": maps[key]["SKILL.md"],
                                    "entrypoint_source": contents[key]["SKILL.md"].identity(),
                                    "output": member.identity()})
    return Selection(profile_id, tuple(packages[key] for key in sorted(packages)),
                     tuple(sorted(members, key=lambda item: item.candidate_path)), tuple(adapter_records))
