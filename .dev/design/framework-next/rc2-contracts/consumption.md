# Installed knowledge consumption and target applicability

Installation makes selected content available. Project adoption determines which
rules apply; the operation's subject determines which references are needed. These
are separate decisions. All four consumers—implementation, architecture, review
and testing—read the same saved binding and existing target authorities.

## Minimal binding protocol

The `bindings` array in the project's explicit installation selection uses the
closed `Binding`, `Selector` and `Authority` objects in
[the schema bundle](schemas/contracts.schema.json). A binding requires:

- A unique binding ID, installed knowledge package and exact resource IDs.
- `use_as: knowledge | example | normative-rule`. Knowledge explains; examples
  illustrate; normative rules require real target adoption/authority. A template
  or source include is used as an example until the target separately adopts it.
- Exact capability, execution-mode and operation lists, target-relative path prefixes, an explicit
  technology profile or null, and file-type IDs. `.` is the one selector-only
  token meaning the whole project; ordinary file paths still forbid dot segments.
- Existing project authority references with raw SHA-256 and a bounded selector
  (for example `rule_dispositions[rule_id=ARCH-UOW-001]`). These are interpreted by
  their current target owner, not a new universal YAML/JSON query evaluator.
- `required_rule_ids` and `required_for_coverage`. Knowledge/examples use an empty
  rule list. Normative bindings require nonempty rules and authority references.
  Loading a rule does not make its conditional applicability true.

The selection's authority hash is a drift check, not an approval token. The target
owner verifies semantic applicability and conflicting choices against the actual
files. Updated target authorities require one explicit saved binding reconciliation;
ordinary skill calls do not ask for the same adoption again. Configuration is never
created or changed implicitly. Package operation settings remain in the existing
explicitly passed `framework.json`; knowledge binding does not invent settings for
instruction-only skills whose configuration is null.

For an operation, the caller supplies installed lock/selection, project root,
operation, execution-mode and capability IDs, affected paths/file types, requested coverage and
permitted authority inputs. S5 resolves applicable binding rows, verifies selected
resource and authority identity, loads only those references, and returns a compact
consumption result:

```text
{ status: available | unavailable | blocked,
  loaded_resources: [{package, version, resource_id, member, sha256, use_as}],
  applicable_rule_ids: [...], conditional_rule_ids: [...],
  authorities: [{path, sha256, selector}],
  coverage: [{capability, operation, technology_profile, status, missing}],
  diagnostics: [{code, relative_path_or_null, reason, next_action}] }
```

This is a caller interface, not a required durable record family. `missing` names
exact package/resource/authority/rule/target predicate. A selected package with no
matching binding is available knowledge but supplies no adopted normative coverage.
Ambiguous/conflicting selectors or stale authority is blocked. A missing optional
resource is unavailable. A required specialist gap prevents claiming the requested
coverage; common analysis can continue only with that limit disclosed and without
silently substituting another specialist. No inferred technology from `.cs`, SDK
or a package name overrides the project's selection.

Package resource lookup is the only link between generic skills and optional
knowledge. Instruction-only consumers may perform this bounded protocol directly;
S3 supplies the verified index, S5 supplies semantic consumption. No new mandatory
approval pipeline, common execution engine, generic rule resolver or permanently
loaded full library is introduced. Existing target resolver/gate remains its owner.

## Source example

[Source desired selection](examples/source-installation.example.json) explicitly
lists all 18 currently delivered skill IDs with `knowledge: []`, both adapters and
no knowledge bindings. Its all-zero parent pin is intentionally unresolvable: the
example is not an admissible installation or an existing parser input. Replace it
only with a separately verified real catalog during S5 adoption.

`src/knowledge` is editable product source even when the source project's installed
selection excludes it. Source GitHub work authority, U001, source release/recovery
policy, dormant policy, CI and historical format duties stay with their current
owners. Installing local-backlog does not enable the frozen source backlog; a
separate configuration/authority is required for any use. Installing workflow,
Lesson or ADR packages does not convert existing files or replace ongoing #322
workflows. Every legacy capability has an explicit row in
[source-capabilities.json](source-capabilities.json).

## mq lab fixed read-only example

The [baseline observation](mq-lab-baseline.json) binds the selected tracked files to
`cc0e345367a1d24f49bf8fa68e0eb668df9e5e55`, tree
`1f1bac4fcc564657ae8eddb4ee1c704cc85c7284`. Each recorded authority was read from
that Git object and compared with current working bytes. This does not execute a
target gate or assert whole untracked-tree cleanliness. Git reported unreadable
ignored prerequisite-fixture directories; no target files were changed.

[The mq-lab selection example](examples/mq-lab-installation.example.json) selects
`engineering-common` and `dotnet-backend`, all 18 skills and both adapters. The
adapter choice is an rc.2 illustration, not adoption. It retains the 20 exact
`route_bindings` from the target authority and separates common/.NET rule sets.
Its actual authority hashes are fixed-target evidence; the zero parent pin is an
unresolved future catalog. No example may be applied by filling only a version label.

The 14 target rules retain these portable semantic sources:

| Rule ID | Package / canonical member | Target applicability to preserve |
| --- | --- | --- |
| AICTX-EVIDENCE-001 | engineering-common / engineering-rule-catalog.yaml | Evidence-backed AI-context and repository facts |
| ASSESSMENT-ARTIFACT-001 | engineering-common / engineering-rule-catalog.yaml | Target-governed assessment persistence; no new framework-wide artifact mandate |
| TECH-SELECT-001 | engineering-common / engineering-rule-catalog.yaml | Explicit target technology decisions |
| AGGREGATE-ES-001 | dotnet-backend / standards/BUILDING-BLOCKS-RECONSTRUCTION-CONTRACT.md | Orders-selected event sourcing; no global Apply/When rule |
| ARCH-UOW-001 | dotnet-backend / standards/coding-standards/usecase-standards.md | Explicit local aggregate/outbox transaction boundaries |
| CONTRACT-SEMANTICS-001 | dotnet-backend / standards/DESIGN-BY-CONTRACT.md | Preconditions/invariants/postconditions; no imposed helper API |
| DELETE-PURGE-001 | dotnet-backend / standards/coding-standards/archive-standards.md | Inventory physical deletion keeps purge governance relevant |
| DELETE-SOFT-001 | dotnet-backend / standards/coding-standards/aggregate-standards.md | Products' selected soft-delete marker/filter behavior |
| MAP-EVENTS-001 | dotnet-backend / standards/coding-standards/mapper-standards.md | Order reconstruction must not generate pending events |
| MESSAGING-TX-001 | dotnet-backend / standards/coding-standards/transactional-messaging-standards.md | Selected state/outgoing intent/incoming completion owner |
| PROJECT-GRAMMAR-001 | dotnet-backend / standards/project-structure.md | Target-selected slnx and bounded-context mapping |
| TEST-BDDFY-001 | dotnet-backend / standards/coding-standards/test-standards.md | Plain-xUnit branch explicitly permitted; BDDfy opt-out retained |
| TEST-GWT-001 | dotnet-backend / standards/coding-standards/test-standards.md | Observable GWT semantics regardless of runner |
| TEST-MOCK-001 | dotnet-backend / standards/coding-standards/test-standards.md | Moq/NSubstitute selected per actual target test project |

All 14 are currently recorded as `baseline-effective`; S1 reports that stored
state without re-verifying acceptance evidence. Their normative text digests and
source identities are in [migration-inventory.json](migration-inventory.json).
The target's v0.18 rule/provenance baseline is distinct from rc.1 installed lock
provenance; relocating portable sources must not relabel target historical bytes.

The four customizations remain target-owned:

| ID | Required retained meaning |
| --- | --- |
| CUST-DOTNET-MQ-GOVERNANCE | Issue-first scope, routing, repository truth, scoped runtime metadata tracking and LF policy |
| CUST-DOTNET-MQ-VALIDATION | SHA-pinned downstream-applicable gates, truthful exclusions and independent target review |
| CUST-DOTNET-MQ-REPO-TRUTH | Product/architecture decisions and inactive retired tooling/recipes |
| CUST-DOTNET-MQ-EXECUTION-PROVENANCE-ADOPTION | Prospective signature and grammar cutovers, exact historical exception; no history rewrite |

Inventory uses EF Core/Npgsql with its selected stock/reservation outbox boundaries;
Products and Orders retain Dapper paths. Orders additionally selects event sourcing.
The isolated EF Core/Wolverine sample does not replace Inventory's transaction
completion owner. SQL initialization/migrations remain schema authority. Tests use
plain xUnit v3/GWT and project-selected mocking libraries. Content examples may not
change any of these decisions or reactivate retired analyzer/provider projects.

The current gate is the target-owned
`python -I -B .dev/ai-context/tooling/validate-current-framework.py --binding-sha256 <accepted-digest> --git-range <accepted-base>..HEAD`.
It binds installed candidate/lock/engine/managed files, runtime discovery, retained
target authority/dependencies, the 20 resolver routes and target Git overlay. Its
independent target review is a separate admission gate. The old
`validate-target-ai-context.py` and target-gate manifest remain legacy support.
Source U001 does not waive target gates. S1 has read these definitions; none ran.

S5 must reconcile new installed rule/resource paths with the existing target
binding/gate owner, preserving all 20 selectors and the four customizations before
retiring a retained route. Missing target adapter support is an explicit gap; keep
the old owner active within its scope. Do not create a fake universal compatibility
adapter or consider a compact packet/generation success actual target consumption.

## Unregistered guidance and migration evidence

The profile catalog records 11 `identity-allocation-required` documents. Their
recorded `source_file_sha256` values do not match the inspected fixed source blobs
(all 11 comparisons are exposed in the inventory). S2 must use actual source
identities when preparing relocated metadata and preserve the discrepancy; S1
has not repaired the source catalog or claimed those documents are registered rules.
They remain available guidance with explicit coverage limits until a separate
rule-identity decision is made. This does not block moving their useful guidance.

Examples, fixtures and source includes carry no runtime acceptance. Old execution
manifests/fixture records stay historical in the source; current installed example
content may be read, but compilation/runtime compatibility must be separately
selected and observed. No source U001 override, target customization or target
transaction history enters a portable normative catalog.
