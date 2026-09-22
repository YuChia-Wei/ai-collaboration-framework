"""Generate a thin Codex entry pointing only at selected installed resources."""

from __future__ import annotations

import json
import posixpath
import re
from string import Template
from urllib.parse import unquote, urlsplit

from .data import require


def project_entry(template_bytes: bytes, package_id: str, package_version: str,
                  description: str, destinations: dict[str, str]) -> tuple[str, bytes]:
    runtime_name = f"framework-{package_id}"
    destination = f".agents/skills/{runtime_name}/SKILL.md"
    directory = posixpath.dirname(destination)

    def relative(member: str) -> str:
        return posixpath.relpath(destinations[member], directory)

    template = Template(template_bytes.decode("utf-8", errors="strict"))
    values = {
        "runtime_name": runtime_name,
        "description": json.dumps(description, ensure_ascii=False),
        "package_identity": f"{package_id}@{package_version}",
        "installed_entrypoint": relative("SKILL.md"),
        "installed_metadata": relative("skill-package.yaml"),
        "resources": "\n".join(f"- [{member}]({relative(member)})" for member in sorted(destinations)
                                if member not in {"SKILL.md", "skill-package.yaml"}),
    }
    require(template.is_valid() and set(template.get_identifiers()) == values.keys(),
            "Codex template must contain exactly the supported installed-resource placeholders")
    rendered = template.substitute(values)
    require("src/" not in rendered and ".ai/assets/" not in rendered and ".dev/" not in rendered,
            "Codex projection contains a forbidden source-checkout reference; repair the adapter or description")
    require(re.search(r"[A-Za-z]:[\\/]|file://|\\\\", rendered) is None,
            "Codex projection contains an absolute host path")
    # Validate the template's literal links too, not only substituted resources.
    for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", rendered):
        target = urlsplit(unquote(match.group(1).strip("<>")))
        resolved = posixpath.normpath(posixpath.join(directory, target.path))
        require(not target.scheme and not target.netloc and not target.query
                and resolved in destinations.values(),
                "Codex projection link must resolve to a selected installed resource")
    return destination, rendered.encode("utf-8")
