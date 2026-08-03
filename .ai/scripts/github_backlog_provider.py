#!/usr/bin/env python3
"""Read-only projection of canonical backlog items into a GitHub provider plan."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml


class ProviderContractError(RuntimeError):
    """Raised when source truth cannot be projected without guessing."""


BACKLOG_ID = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]{3}$")
PR_URL = re.compile(r"https://github\.com/[^/\s]+/[^/\s]+/pull/(\d+)")
PR_NUMBER = re.compile(r"\bPR\s+#(\d+)\b", re.IGNORECASE)


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ProviderContractError(f"{path}: cannot read YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ProviderContractError(f"{path}: expected a YAML mapping")
    return value


def run_git(repo: Path, *args: str) -> str:
    command = ["git", "-C", str(repo), *args]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        raise ProviderContractError(
            f"Git command failed ({' '.join(command)}): {exc.stderr.strip()}"
        ) from exc
    return completed.stdout.strip()


def resolve_revision(repo: Path, revision: str) -> str:
    resolved = run_git(repo, "rev-parse", f"{revision}^{{commit}}")
    if not re.fullmatch(r"[0-9a-f]{40}", resolved):
        raise ProviderContractError(f"Git revision did not resolve to a commit: {revision}")
    return resolved


def revision_timestamp(repo: Path, revision: str) -> str:
    value = run_git(repo, "show", "-s", "--format=%cI", revision)
    if not value:
        raise ProviderContractError(f"Git revision has no commit timestamp: {revision}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


def repository_url(config: dict[str, Any]) -> str:
    return f"https://github.com/{config['repository']}"


def provider_link(config: dict[str, Any], revision: str, reference: str) -> str:
    if reference.startswith("https://"):
        return reference
    path, separator, fragment = reference.partition("#")
    normalized = PurePosixPath(path).as_posix()
    suffix = f"#{fragment}" if separator else ""
    return f"{repository_url(config)}/blob/{revision}/{normalized}{suffix}"


def source_reference(item_path: Path, repo: Path) -> str:
    return item_path.relative_to(repo).as_posix()


def collect_pr_numbers(item: dict[str, Any]) -> list[int]:
    numbers: set[int] = set()
    for value in walk_strings(item):
        numbers.update(int(match) for match in PR_URL.findall(value))
        numbers.update(int(match) for match in PR_NUMBER.findall(value))
    return sorted(numbers)


def evidence_projection(
    item: dict[str, Any], config: dict[str, Any], revision: str
) -> dict[str, Any]:
    prs = collect_pr_numbers(item)
    if len(prs) == 1:
        evidence_class = "exact-pr"
    elif len(prs) > 1:
        evidence_class = "multiple-prs"
    elif item.get("resolution_ref") or item.get("workflow_refs") or item.get("task_refs"):
        evidence_class = "evidence-fallback"
    else:
        evidence_class = "needs-owner-review"

    links = [
        {
            "role": (
                "Implemented" if index == 0 else "Integrated" if index == 1 else "Finalized"
            ),
            "label": f"PR #{number}",
            "url": f"{repository_url(config)}/pull/{number}",
        }
        for index, number in enumerate(prs)
    ]
    if not links:
        candidates: list[str] = []
        if isinstance(item.get("resolution_ref"), str):
            candidates.append(item["resolution_ref"])
        for key in ("workflow_refs", "task_refs"):
            values = item.get(key, [])
            if isinstance(values, list):
                candidates.extend(value for value in values if isinstance(value, str))
        for reference in candidates[:3]:
            links.append(
                {
                    "role": "Evidence",
                    "label": reference,
                    "url": provider_link(config, revision, reference),
                }
            )
    return {"class": evidence_class, "links": links}


def acceptance_lines(item: dict[str, Any]) -> list[str]:
    value = item.get("acceptance")
    if value is None:
        value = item.get("acceptance_criteria")
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(line, str) for line in value):
        raise ProviderContractError(f"{item.get('backlog_id')}: acceptance must be a string list")
    return value


def boundary_lines(item: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key in ("constraints", "compatibility_boundaries"):
        value = item.get(key, [])
        if isinstance(value, list):
            lines.extend(line for line in value if isinstance(line, str))
    return lines


def related_refs(item: dict[str, Any]) -> list[str]:
    value = item.get("related_backlog_refs", [])
    if not isinstance(value, list):
        return []
    return sorted({line for line in value if isinstance(line, str)})


def creation_attribution(config: dict[str, Any]) -> str:
    issue = config.get("issue")
    if not isinstance(issue, dict):
        raise ProviderContractError("issue configuration must be a mapping")
    attribution = issue.get("creation_attribution")
    if not isinstance(attribution, dict):
        raise ProviderContractError("issue.creation_attribution must be a mapping")
    try:
        return attribution["marker_format"].format(
            runtime=attribution["runtime"],
            model=attribution["model"],
            reasoning_effort=attribution["reasoning_effort"],
            email=attribution["email"],
        )
    except (KeyError, AttributeError, ValueError) as exc:
        raise ProviderContractError(
            "issue.creation_attribution must define a valid marker_format, runtime, model, reasoning_effort, and email"
        ) from exc


def validate_config(config: dict[str, Any], backlog_ids: set[str]) -> None:
    errors: list[str] = []
    if config.get("schema_version") != "1.0" or config.get("provider") != "github":
        errors.append("provider schema_version/provider must be 1.0/github")
    source = config.get("source")
    if not isinstance(source, dict) or source.get("expected_item_count") != len(backlog_ids):
        errors.append("source.expected_item_count must equal canonical backlog count")
    classifications = config.get("classifications")
    if not isinstance(classifications, dict):
        errors.append("classifications must be a mapping")
        classifications = {}
    if set(classifications) != backlog_ids:
        missing = sorted(backlog_ids - set(classifications))
        extra = sorted(set(classifications) - backlog_ids)
        errors.append(f"classification ID parity failed; missing={missing}, extra={extra}")
    for backlog_id, classification in classifications.items():
        if not isinstance(classification, dict):
            errors.append(f"{backlog_id}: classification must be a mapping")
            continue
        if classification.get("kind") not in {"story", "enabler"}:
            errors.append(f"{backlog_id}: kind must be story or enabler")
        if classification.get("scope") not in {"framework", "source-repo", "mixed"}:
            errors.append(f"{backlog_id}: invalid scope")
        if not classification.get("rationale"):
            errors.append(f"{backlog_id}: classification rationale is required")
    migration = config.get("migration", {})
    canaries = migration.get("canaries", []) if isinstance(migration, dict) else []
    batches = migration.get("remaining_batch_sizes", []) if isinstance(migration, dict) else []
    post_adoption = (
        migration.get("post_adoption_backlog_ids", [])
        if isinstance(migration, dict)
        else []
    )
    if (
        not isinstance(post_adoption, list)
        or len(post_adoption) != len(set(post_adoption))
        or not set(post_adoption).issubset(backlog_ids)
    ):
        errors.append("migration.post_adoption_backlog_ids must be unique canonical IDs")
        post_adoption = []
    migration_ids = backlog_ids - set(post_adoption)
    if migration.get("expected_item_count") != len(migration_ids):
        errors.append("migration.expected_item_count must equal the historical migration cohort")
    if len(canaries) != 4 or not set(canaries).issubset(migration_ids):
        errors.append("migration requires four valid canaries")
    if batches != [10, 10, 10, 7] or sum(batches) != len(migration_ids) - len(canaries):
        errors.append("remaining migration batches must be 10+10+10+7")
    labels = config.get("labels", [])
    label_names = {entry.get("name") for entry in labels if isinstance(entry, dict)}
    required_labels = {
        "kind:story",
        "kind:enabler",
        "kind:proposal",
        "scope:framework",
        "scope:source-repo",
        "scope:mixed",
        "migration:historical",
        "created-by:codex",
        "traceability:needs-review",
        "triage:needed",
    }
    if label_names != required_labels:
        errors.append("label declaration differs from the approved ten-label contract")
    issue = config.get("issue", {})
    attribution = issue.get("creation_attribution", {}) if isinstance(issue, dict) else {}
    if not isinstance(attribution, dict):
        errors.append("issue.creation_attribution must be a mapping")
    else:
        expected_attribution = {
            "required_for_formal_issue": True,
            "label": "created-by:codex",
            "marker_format": "<!-- created-by: {runtime} ({model}, {reasoning_effort}) <{email}> -->",
            "placement": "hidden marker immediately before canonical identity markers",
            "runtime": "OpenAI Codex",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "max",
            "email": "noreply@openai.com",
            "runtime_binding": "active Issue-creation execution",
            "refresh_policy": "update execution values before a creation batch when runtime provenance changes",
            "applies_to": ["formal_story", "formal_enabler"],
            "proposal_policy": {
                "ai_created": {
                    "label_required": True,
                    "hidden_marker_required": False,
                    "application": "include the attribution label in the Issue creation request",
                },
                "human_submitted": {
                    "label_required": False,
                    "hidden_marker_required": False,
                    "application": "keep the public Proposal form attribution-neutral",
                },
            },
        }
        if attribution != expected_attribution:
            errors.append("Issue creation attribution differs from the approved Codex label and marker contract")
        else:
            try:
                rendered_attribution = creation_attribution(config)
            except ProviderContractError as exc:
                errors.append(str(exc))
            else:
                if rendered_attribution != (
                    "<!-- created-by: OpenAI Codex (gpt-5.6-sol, max) <noreply@openai.com> -->"
                ):
                    errors.append("Issue creation attribution does not render the approved hidden marker")
    expected_binding = {
        "mode": "optional",
        "purposes": ["traceability", "work-authorization"],
        "authorization": {
            "requires_explicit_owner_approval": True,
            "provider_state_alone_authorizes": False,
            "missing_binding": "record explicit owner authorization in the workflow or pull request",
        },
        "merge_gate": {
            "mode": "optional",
            "reference_format": "Refs #<issue-number>",
            "missing_binding_blocks_merge": False,
        },
    }
    if config.get("work_item_binding") != expected_binding:
        errors.append(
            "work_item_binding differs from the approved optional source-repository contract"
        )
    automation = config.get("automation", {})
    allowlist = automation.get("allowlist", []) if isinstance(automation, dict) else []
    if allowlist != [
        {
            "trigger": "issue_opened_in_repository",
            "action": "auto_add_to_project_and_initialize_status_inbox",
        },
        {"trigger": "issue_closed", "action": "set_status_done"},
    ]:
        errors.append("automation allowlist differs from the approved low-risk pair")
    if errors:
        raise ProviderContractError("; ".join(errors))


def load_backlog(repo: Path, config: dict[str, Any]) -> list[tuple[Path, dict[str, Any]]]:
    pattern = config.get("source", {}).get("backlog_glob")
    if not isinstance(pattern, str):
        raise ProviderContractError("source.backlog_glob is required")
    entries: list[tuple[Path, dict[str, Any]]] = []
    seen: set[str] = set()
    for path in sorted(repo.glob(pattern)):
        item = load_yaml_mapping(path)
        backlog_id = item.get("backlog_id")
        if not isinstance(backlog_id, str) or not BACKLOG_ID.fullmatch(backlog_id):
            raise ProviderContractError(f"{path}: invalid backlog_id")
        if backlog_id in seen:
            raise ProviderContractError(f"duplicate backlog_id: {backlog_id}")
        seen.add(backlog_id)
        entries.append((path, item))
    validate_config(config, seen)
    return entries


def markdown_list(values: list[str], empty: str = "None recorded.") -> str:
    return "\n".join(f"- {value}" for value in values) if values else f"- {empty}"


def statement(item: dict[str, Any], kind: str) -> str:
    title = item["title"]
    summary = item["summary"]
    if kind == "story":
        return (
            "As a framework maintainer or downstream adopter,\n\n"
            f"I want **{title}**,\n\n"
            f"so that {summary[0].lower() + summary[1:]}"
        )
    return (
        "- Beneficiary: framework maintainers and downstream adopters\n"
        f"- Capability: **{title}**\n"
        f"- Benefit: {summary}"
    )


def project_fields(item: dict[str, Any], classification: dict[str, str], config: dict[str, Any]) -> dict[str, Any]:
    status = item["status"]
    lifecycle = config["lifecycle_mapping"][status]
    release = item["release"]
    target = "Unassigned" if release["target"] == "unassigned" else release["target"]
    published = release.get("published_in")
    if status == "declined":
        published_value = None
    elif published:
        published_value = published
    elif classification["scope"] == "source-repo":
        published_value = "Not applicable — source repository only"
    else:
        published_value = "Not yet published"
    return {
        "Status": lifecycle["status"],
        "Priority": config["priority_mapping"][item["priority"]],
        "Owner review": lifecycle["owner_review"],
        "Target release": target,
        "Published in": published_value,
    }


def render_body(
    item: dict[str, Any],
    item_path: Path,
    repo: Path,
    config: dict[str, Any],
    revision: str,
    classification: dict[str, str],
    evidence: dict[str, Any],
    fields: dict[str, Any],
) -> str:
    kind = classification["kind"]
    heading = "Story Statement" if kind == "story" else "Enabler Statement"
    acceptance = markdown_list(
        acceptance_lines(item),
        "No acceptance criteria were recorded in the canonical backlog item; follow the linked source and workflow evidence without inventing criteria.",
    )
    boundaries = markdown_list(boundary_lines(item), "No additional material constraints are recorded.")
    evidence_lines = [
        f"- {entry['role']}: [{entry['label']}]({entry['url']})"
        for entry in evidence["links"]
    ]
    if not evidence_lines:
        evidence_lines = ["- No delivery evidence is available; owner review is required before closure."]
    relations = related_refs(item)
    relation_lines = markdown_list(relations, "No explicit parent, sub-issue, or related backlog relationship is recorded.")
    release = item["release"]
    canonical_path = source_reference(item_path, repo)
    canonical_url = provider_link(config, revision, canonical_path)
    completed = release.get("completed_in") or "Not completed"
    published = release.get("published_in") or "Not recorded"
    decision = item.get("decision_needed") or "None"
    return f"""## {heading}

{statement(item, kind)}

## Outcome

{item['summary']}

## Acceptance Criteria

{acceptance}

## Boundaries

{boundaries}

## Delivery Scope

- Kind: `{kind}`
- Scope: `{classification['scope']}`
- Classification evidence: {classification['rationale']}
- Recommended owner skill: `{item.get('recommended_owner_skill') or 'not recorded'}`
- Handoff condition: {item.get('handoff_condition') or 'None recorded.'}

## Lifecycle

- Canonical state: `{item['status']}`
- Priority: `{item['priority']}` → `{fields['Priority']}`
- Target release: `{fields['Target release']}`
- Completed in: `{completed}`
- Published in: `{fields['Published in'] or 'Not applicable to declined work'}`
- Original created at: `{item['created_at']}`
- Original updated at: `{item['updated_at']}`
- Owner decision: {decision}

## Delivery Evidence

{chr(10).join(evidence_lines)}

- Evidence classification: `{evidence['class']}`

## Related Work

{relation_lines}

## Community Feedback

Comments in English or Traditional Chinese (Taiwan) are welcome. Feedback does not automatically change canonical requirements, scope, priority, owner approval, or repository workflow authorization.

## Migration Notice

This Issue is a historical projection of a canonical repository backlog item. GitHub timestamps reflect migration activity; the original lifecycle timestamps above remain authoritative. Detailed planning, execution tasks, and validation evidence stay in repository workflow artifacts.

- Canonical source: [`{canonical_path}` at `{revision[:12]}`]({canonical_url})

{creation_attribution(config)}

<!-- canonical-backlog-id: {item['backlog_id']} -->
<!-- migration-id: {config['migration']['id']} -->
"""


def closing_comment(item: dict[str, Any], evidence: dict[str, Any], fields: dict[str, Any]) -> str | None:
    if item["status"] not in {"resolved", "declined"}:
        return None
    evidence_text = ", ".join(
        f"[{entry['label']}]({entry['url']})" for entry in evidence["links"]
    ) or "no verified delivery link"
    if item["status"] == "declined":
        return (
            "Historical migration note: this canonical backlog item was declined by the owner. "
            f"Decision: {item.get('decision_needed') or 'see canonical source'}. Evidence: {evidence_text}. "
            "Closing as not planned; this does not claim acceptance completion."
        )
    completed = item["release"].get("completed_in") or "not recorded"
    published = fields["Published in"] or "not recorded"
    return (
        "Historical migration note: the canonical backlog records this outcome as resolved. "
        f"Completed in: {completed}. Published in: {published}. Delivery evidence: {evidence_text}. "
        "Closing as completed while preserving the repository as the detailed evidence authority."
    )


def project_item(
    item_path: Path,
    item: dict[str, Any],
    repo: Path,
    config: dict[str, Any],
    revision: str,
) -> dict[str, Any]:
    backlog_id = item["backlog_id"]
    classification = config["classifications"][backlog_id]
    evidence = evidence_projection(item, config, revision)
    fields = project_fields(item, classification, config)
    warnings: list[str] = []
    if classification["scope"] == "source-repo" and item["release"].get("published_in"):
        warnings.append("source-repo scope conflicts with a non-null canonical published_in value")
    if item["status"] in {"resolved", "declined"} and evidence["class"] == "needs-owner-review":
        warnings.append("closed canonical item has insufficient delivery or decision evidence")
    blocked = bool(warnings)
    lifecycle = config["lifecycle_mapping"][item["status"]]
    labels = [
        f"kind:{classification['kind']}",
        f"scope:{classification['scope']}",
        "migration:historical",
        config["issue"]["creation_attribution"]["label"],
    ]
    if blocked:
        labels.append("traceability:needs-review")
        fields["Owner review"] = "Pending"
    desired_state = "open" if blocked else lifecycle["issue_state"]
    close_reason = None if blocked else lifecycle["close_reason"]
    comment = None if blocked else closing_comment(item, evidence, fields)
    source_path = source_reference(item_path, repo)
    return {
        "backlog_id": backlog_id,
        "source": {
            "path": source_path,
            "sha256": sha256_bytes(item_path.read_bytes()),
            "permalink": provider_link(config, revision, source_path),
        },
        "classification": classification,
        "issue": {
            "title": f"[{backlog_id}] {item['title']}",
            "body": render_body(
                item, item_path, repo, config, revision, classification, evidence, fields
            ),
            "labels": labels,
            "assignees": [],
            "desired_state": desired_state,
            "close_reason": close_reason,
            "closing_comment": comment,
        },
        "project_fields": fields,
        "evidence": evidence,
        "relationships": related_refs(item),
        "action": "blocked-owner-review" if blocked else "create-and-close" if desired_state == "closed" else "create-open",
        "warnings": warnings,
    }


def build_plan(repo: Path, config_path: Path, revision: str = "HEAD") -> dict[str, Any]:
    config = load_yaml_mapping(config_path)
    resolved_revision = resolve_revision(repo, revision)
    entries = load_backlog(repo, config)
    items = [
        project_item(path, item, repo, config, resolved_revision)
        for path, item in entries
    ]
    canaries = config["migration"]["canaries"]
    post_adoption = config["migration"].get("post_adoption_backlog_ids", [])
    remaining = [
        item["backlog_id"]
        for item in items
        if item["backlog_id"] not in canaries
        and item["backlog_id"] not in post_adoption
    ]
    sizes = config["migration"]["remaining_batch_sizes"]
    batches: list[list[str]] = []
    cursor = 0
    for size in sizes:
        batches.append(remaining[cursor : cursor + size])
        cursor += size
    if cursor != len(remaining):
        raise ProviderContractError("migration batches do not cover all non-canary items")
    counts = {
        "total": len(items),
        "open": sum(item["issue"]["desired_state"] == "open" for item in items),
        "closed": sum(item["issue"]["desired_state"] == "closed" for item in items),
        "blocked": sum(item["action"] == "blocked-owner-review" for item in items),
        "stories": sum(item["classification"]["kind"] == "story" for item in items),
        "enablers": sum(item["classification"]["kind"] == "enabler" for item in items),
    }
    return {
        "schema_version": "1.0",
        "provider": "github",
        "mode": "read-only-dry-run",
        "migration_id": config["migration"]["id"],
        "repository": config["repository"],
        "source_revision": resolved_revision,
        "generated_at": revision_timestamp(repo, resolved_revision),
        "online_writes_performed": False,
        "stage_b_authorized": False,
        "counts": counts,
        "canaries": canaries,
        "remaining_batches": batches,
        "post_adoption_items": post_adoption,
        "items": items,
    }


def render_plan_markdown(plan: dict[str, Any]) -> str:
    counts = plan["counts"]
    rows = []
    for item in plan["items"]:
        fields = item["project_fields"]
        rows.append(
            "| {id} | {kind} | {scope} | {state} | {reason} | {status} | {priority} | {target} | {published} | {evidence} | {action} |".format(
                id=item["backlog_id"],
                kind=item["classification"]["kind"],
                scope=item["classification"]["scope"],
                state=item["issue"]["desired_state"],
                reason=item["issue"]["close_reason"] or "—",
                status=fields["Status"],
                priority=fields["Priority"],
                target=fields["Target release"],
                published=fields["Published in"] or "—",
                evidence=item["evidence"]["class"],
                action=item["action"],
            )
        )
    batches = "\n".join(
        f"- Batch {index}: {', '.join(batch)}"
        for index, batch in enumerate(plan["remaining_batches"], 1)
    )
    return f"""# GitHub Backlog Migration Dry-Run

This is a read-only Stage A projection. It performed no GitHub write and does
not authorize Stage B.

## Snapshot

- Migration: `{plan['migration_id']}`
- Repository: `{plan['repository']}`
- Canonical revision: `{plan['source_revision']}`
- Deterministic generated-at source: `{plan['generated_at']}`
- Total: `{counts['total']}`
- Desired open / closed: `{counts['open']} / {counts['closed']}`
- Story / Enabler: `{counts['stories']} / {counts['enablers']}`
- Blocked for owner review: `{counts['blocked']}`
- Online writes performed: `false`

## Canary And Batch Order

- Canaries: {', '.join(plan['canaries'])}
{batches}

## Complete Preview

Full Issue bodies, labels, comments, source digests, and warnings are preserved
in the adjacent YAML evidence file.

| Backlog | Kind | Scope | Issue state | Close reason | Project status | Priority | Target | Published | Evidence | Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Stage B Gate

After this contract PR is merged, regenerate from fresh `main` and obtain
explicit owner approval for that exact revision and preview before any online
label, Issue, Project, view, field, or automation mutation.
"""


def dump_plan_yaml(plan: dict[str, Any]) -> str:
    return yaml.safe_dump(
        plan,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
