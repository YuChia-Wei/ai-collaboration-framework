# Lessons Knowledge Lifecycle

## Responsibility

A lesson is an evidence-backed, reusable, non-normative learning derived from a
workflow, assessment, incident, release, or another durable source. It explains
what was confirmed, when the conclusion applies, and where the originating
evidence remains available.

Lessons preserve reusable knowledge without converting one observation into a
rule. They do not authorize implementation, change repository behavior, or
override another document class.

## Historical Boundary

The v0.0.x `.dev/INDEX.md` advertised `lessons/` and `lessons/dotnet/`, but Git
history contains no tracked lesson directory or lesson document. Commit
`bc7094d877731ad7177899781bdea3a9f19ef5b8` removed those absent active paths on
2026-07-10, and the removal first appeared in v0.1.0. The archived
[relationship-audit task](../workflows/2026-07-ai-context-relationship-audit/tasks/fix-dev-entry-index-relationships.json)
and [review report](../workflows/2026-07-ai-context-relationship-audit/review-report.md)
retain that evidence.

This directory therefore defines the previously missing contract for an
intended knowledge area. It does not claim that a complete prior lesson system
existed.

## Boundary

| Knowledge class | Responsibility | Relationship to a lesson |
| --- | --- | --- |
| Standards and policy | Own normative behavior, constraints, and governance. | A lesson may cite them but cannot override them or become a second source of `MUST`-level behavior. |
| Implementation guides | Own maintained human procedures, setup, and troubleshooting guidance. | A reusable procedure may be promoted to a guide through separately authorized work. |
| Workflow and release evidence | Record one execution, approval, validation, or publication lifecycle. | A lesson summarizes a reusable conclusion and links back without rewriting historical evidence. |
| Assessments | Record read-only observations at a pinned subject revision. | A lesson may derive from a finding but does not replace the assessment or authorize remediation. |
| Operations runbooks | Own mandatory or repeatable operational procedures. | A mandatory operational step may be promoted to a runbook through separately authorized work. |
| Machine-local readiness state | Describes the current host, installed tools, credentials, paths, or service availability. | A lesson may preserve sanitized conditions and a host-specific remediation example, but machine-local state is not portable repository truth. |

Lesson files use descriptive conclusions and evidence. If a lesson reports a
normative requirement owned elsewhere, it cites that authority instead of
restating the requirement as lesson-owned behavior. Every lesson declares
`Normative Authority` as `none`.

## Identity And Lifecycle

Lesson identities use this stable form:

```text
LESSON-<CATEGORY-CODE>-<three-digit-sequence>
```

The identity remains stable across title, file, category-index, promotion, and
supersession updates while the learning means the same thing. The root
[lesson index](INDEX.MD) owns discovery and current lifecycle state; category
indexes are navigational projections.

| Lifecycle | Meaning | Required disposition |
| --- | --- | --- |
| `active` | The evidence-backed conclusion remains reusable in its stated conditions. | Keep origin evidence, applicability, remediation, and verification current. |
| `promoted` | Another authorized document now owns the maintained procedure, mandatory operation, or normative behavior. | Link the promotion target and retain the lesson as provenance. |
| `superseded` | Newer evidence or a successor lesson replaces the reusable conclusion. | Link the successor and retain the original lesson and historical evidence. |

Do not silently delete a promoted or superseded lesson. Update the root and
category indexes together with the lesson lifecycle fields.

## Required Lesson Packet

Each lesson contains a visible identity table rather than mandatory
frontmatter. The packet records:

- lesson ID, category, lifecycle, and `Normative Authority: none`;
- originating durable evidence and its subject or execution identity;
- context and symptom;
- confirmed conditions and root cause;
- reusable conclusion;
- non-applicable cases;
- remediation example and verification;
- promotion target, supersedes, and superseded-by fields;
- security and portability limits when host or environment evidence is involved.

Use the [lesson template](templates/lesson-template.md). Add the lesson to both
the root index and its category index in the same change.

## Promotion And Supersession

Promotion changes ownership; it does not retroactively turn the lesson into the
new authority.

| Reusable content | Promotion target | Authorization boundary |
| --- | --- | --- |
| Actionable human procedure | `.dev/guides/implementation-guides/` | Separately reviewed guide work. |
| Mandatory operational procedure | `.dev/operations/runbooks/` | Separately authorized runbook work. |
| Normative behavior or automated enforcement | The classified policy/standard owner and, when selected, its validator | Separately authorized policy or validator work. |

After promotion, retain origin evidence, set lifecycle to `promoted`, and link
the new owner. A policy, validator, guide, or runbook proposal mentioned by a
lesson remains deferred until separately authorized.

When new evidence changes the conclusion rather than promoting it, create or
identify the successor, set the older lesson to `superseded`, and record
reciprocal provenance links where applicable. Do not rewrite earlier failed or
blocked evidence as successful.

## Categories

Categories describe the reusable learning boundary, not an architecture or
technology-profile authority.

- [environment](environment/INDEX.MD) covers host, shell, process-environment,
  and runtime-availability lessons.
- [validation](validation/INDEX.MD) covers validation scheduling, immutable
  snapshots, timeout orchestration, and evidence integrity.

## Distribution Boundary

This source repository owns `.dev/lessons/` as repository knowledge derived
from source workflows, incidents, and releases. The current distribution
profile does not select this tree for the portable framework package. Adding a
lesson does not make host configuration, evidence logs, or source-repository
history downstream truth. Any future distribution or promotion decision needs
its own authorization and classification.

Do not store hostnames, credentials, secrets, private endpoints, raw home
directory contents, or mutable machine-readiness snapshots in a lesson.

## Validation

The source repository's AI-context validator checks the lesson contract only
when source-governance context is present. It verifies required entry files,
root and category index coverage, stable IDs, allowed lifecycle values,
required packet sections, lifecycle-field consistency, and exact lesson paths.
It does not decide whether prose is correct or promote a lesson automatically.
