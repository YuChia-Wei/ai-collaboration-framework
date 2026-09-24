"""Generate a thin Claude entry for selected installed skill members."""

from __future__ import annotations

import json
import posixpath
import re
from hashlib import sha256
from string import Template
from urllib.parse import unquote, urlsplit

from .data import identifier, path, require, string, version


_V2_TEMPLATE_SHA256 = "11eeedac1452cc78e9ab7726791c5032b2379815ea15e8fb0f8fb11d921d032e"


def project_entry_v2(template_bytes: bytes, package_id: str, package_version: str,
                     description: str, destinations: dict[str, str],
                     *, configuration: dict | None) -> tuple[str, bytes]:
    """Render only the selected skill's rc.2 Claude projection."""
    require(type(template_bytes) is bytes
            and sha256(template_bytes).hexdigest() == _V2_TEMPLATE_SHA256,
            "Claude v2 renderer requires its exact v2 template")
    package_id = identifier(package_id, "package_id")
    package_version = version(package_version, "package_version")
    description = string(description, "description")
    require(configuration is None or type(configuration) is dict,
            "configuration must be an object or null")
    require(type(destinations) is dict
            and all(type(member) is str and type(target) is str
                    for member, target in destinations.items()),
            "destinations must map selected member paths to installed paths")
    require({"SKILL.md", "skill-package.yaml"} <= destinations.keys(),
            "selected skill must include its entrypoint and metadata")
    require(all(path(member, "member") == member
                and path(target, "destination") == target
                and target == f".ai/core/skills/{package_id}/{member}"
                for member, target in destinations.items()),
            "Claude v2 destinations must contain only the selected skill's installed members")
    require(len(set(destinations.values())) == len(destinations),
            "Claude v2 destinations must be unique")

    runtime_name = f"aicf-{package_id}"
    destination = f".claude/skills/{runtime_name}/SKILL.md"
    directory = posixpath.dirname(destination)

    def relative(member: str) -> str:
        return posixpath.relpath(destinations[member], directory)

    if configuration is None:
        configuration_guidance = (
            "This package declares `configuration: null`. It needs no framework "
            "configuration file or managed record store. Obtain only the target "
            "inputs required by the selected operation."
        )
    else:
        configuration_guidance = (
            "Obtain the caller's explicit `project_root`, configuration selection "
            "and operation. The project-owned `.ai/custom/framework.json` is not "
            "supplied by this entry. Pass the chosen configuration path explicitly "
            "under the installed skill's contract; do not infer it from the "
            "current working directory."
        )

    template = Template(template_bytes.decode("utf-8", errors="strict"))
    values = {
        "runtime_name": runtime_name,
        "description": json.dumps(description, ensure_ascii=False),
        "package_identity": f"{package_id}@{package_version}",
        "installed_entrypoint": relative("SKILL.md"),
        "installed_metadata": relative("skill-package.yaml"),
        "configuration_guidance": configuration_guidance,
        "resources": "\n".join(
            f"- [{member}]({relative(member)})" for member in sorted(destinations)
            if member not in {"SKILL.md", "skill-package.yaml"}
        ),
    }
    require(template.is_valid() and set(template.get_identifiers()) == values.keys(),
            "Claude v2 template must contain exactly the seven supported placeholders")
    rendered = template.substitute(values)
    require("src/" not in rendered and ".ai/assets/" not in rendered and ".dev/" not in rendered,
            "Claude v2 projection contains a forbidden source-checkout reference")
    require(re.search(r"[A-Za-z]:[\\/]|file://|\\\\", rendered) is None,
            "Claude v2 projection contains an absolute host path")
    for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", rendered):
        target = urlsplit(unquote(match.group(1).strip("<>")))
        resolved = posixpath.normpath(posixpath.join(directory, target.path))
        require(not target.scheme and not target.netloc and not target.query
                and not target.fragment and resolved in destinations.values(),
                "Claude v2 projection link must resolve to a selected installed member")
    return destination, rendered.encode("utf-8")
