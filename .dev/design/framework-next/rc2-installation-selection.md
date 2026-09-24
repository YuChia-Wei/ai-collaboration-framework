# Next RC: selectable installation, knowledge packages and runtime entries

Status: planning proposal for **0.19.0-rc.2**, program [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
Owner direction: 2026-09-24. Inspected source: `e12cf63df3c0a2102e2846ceb8d4b3171ffbfc5f`.
This document records the requested next iteration; it does not implement, install,
allocate a release, change a tag, restore CI or activate a source policy.

## Execution start: 2026-09-24

After this proposal was merged through PR #399, the owner directly instructed the
coordinator to start rc.2 and prepare a fresh task if needed. The direction and
S1-S6 sequence are now authorized to proceed. S1 fixes concrete format details
before dependent implementation; routine choices within the selected scope are
coordinator-owned. `aicf-` is the working prefix. Earlier statements that this
planning checkpoint did not dispatch work remain historical, not a current stop.
See the [continuation checkpoint](../../workflows/2026-09-23-framework-redesign-control/handoffs/rc2-coordinator-transfer.md).
Stable publication, new tags, CI and #369 native expansion remain unselected.

## Owner direction and proposal boundary

The owner considers rc.1 insufficient for stable 0.19.0 and requests further work:

1. Preserve skill IDs. Prefer `aicf-` for generated runtime entry names; discuss a
   different prefix before selecting it. `framework-` is not the desired default.
2. Restore a Claude adapter in the next RC alongside Codex.
3. Place reusable engineering knowledge and development guidance under `src/`.
4. Let downstream projects select installed items, including .NET implementation
   guidance. The framework source must consume its own product without having to
   install engineering knowledge it does not need.

These directions are recorded as selected intent. Package IDs, the configuration
shape, migration details and work units below are a concrete implementation
proposal, not already accepted executable contracts. Stable readiness remains
on hold. Existing rc.1/tag/target evidence retains its original identity.

## What exists, and what must change

- [Selection](../../../src/distribution/selection.py) accepts only a declared source
  profile, `src/skills/<id>/skill-package.yaml` and the Codex adapter. It rejects
  other component roots and adapters. Adding YAML rows alone cannot deliver this plan.
- [Codex projection](../../../src/distribution/codex.py) hardcodes `framework-`.
  Package IDs and `.ai/core/skills/<id>/` are already independent of that prefix.
- [Complete](../../../src/profiles/complete.yaml) explicitly lists 18 implemented
  skills. [Knowledge](../../../src/profiles/knowledge.yaml) selects knowledge
  management skills; [engineering](../../../src/profiles/engineering.yaml) selects
  engineering methods. Neither is an installable engineering content catalog.
- Reusable .NET guidance remains in
  [legacy technology assets](../../../.ai/assets/tech-stacks/dotnet-backend/README.MD).
  Common skill methods are in `src`, but the legacy technology knowledge has not
  been productized there. A .NET opt-in method in spec-compliance-validator does
  not amount to shipping the full engineering knowledge catalog.
- [Source adoption](source-adoption/README.md) is a prior design, not an actual
  installation. Its historical counts and Lesson-first selection do not define
  the full source installation proposed here.

## Three independent installation choices

| Choice | Proposed source | Installed ownership | Selection semantics |
| --- | --- | --- | --- |
| Skills | `src/skills/<skill-id>/` | `.ai/core/skills/<skill-id>/` | Explicit IDs; existing public IDs remain stable. |
| Engineering knowledge and rules | `src/knowledge/<package-id>/` | `.ai/core/knowledge/<package-id>/` | Optional, versioned content packages; no fake executable skill or extra skill menu entry. |
| Runtime adapters | `src/adapters/codex/`, `src/adapters/claude/` | Generated `.agents/skills/aicf-<id>/` and `.claude/skills/aicf-<id>/` | Codex, Claude, both, or core-only; identical selected core content. |

`src` is the editable product source. Installed core and wrappers are generated
consumption artifacts. Project rules, customizations, workflow data and root
instructions remain project-owned. The source repo may retain engineering
knowledge as product source while excluding it from its own installed selection.

Knowledge packages declare their ID/version, exact members, entry index,
reference closure, applicability and required/optional dependencies. They have a
content-package contract rather than mandatory skill operations/runtime tools.
Only selected installed packages enter a task's available knowledge inventory;
skills load applicable references on demand, never the entire library by default.

Start with coherent optional packages such as `engineering-common` and
`dotnet-backend` (proposed names). Organize .NET design, implementation, review and
testing material within its package and expose the applicable route. Split a
package further only for an actual independent consumer; do not create a package
per file or install every technology automatically. General skill methods must
remain useful without these packages.

## Versioned, project-owned installation selection

Propose a tracked `.ai/custom/installation.json`, separate from existing
`.ai/custom/framework.json` skill-operation settings. The former describes desired
installed items; the latter still owns stores, locations and operation settings.
The installer must not silently create or overwrite either project-owned file.
A request to save a selected installation configuration is the write instruction;
ordinary read/plan and routine skill use create no configuration or approval flow.

Illustrative desired selection for this source repository, **not a current parser input**:

```json
{
  "selection_version": 1,
  "skills": ["lesson", "adr", "pr", "software-development-orchestrator", "code-reviewer"],
  "knowledge": [],
  "adapters": ["codex", "claude"]
}
```

The skill list is illustrative, not the final source capability inventory. Source
adoption must enumerate every active capability and choose its installed successor
or explicitly retain its legacy/source-only owner. It cannot silently lose a
capability merely because the sample is short.

Existing profiles become convenient versioned presets for editing that explicit
selection. Expand and save the chosen IDs; do not resolve a floating preset on
every invocation. Users can add/remove items without modifying framework source
or maintaining their own `src/profiles` entry. `complete` remains a precisely
listed preset, never a promise to install every present or future package.

Resolve IDs against one verified immutable distribution catalog. Record exact
component versions, source/candidate identity, selection digest, adapter identity,
rendered names and managed file hashes in the installed lock. A human version
label alone is not a pin. The catalog may contain available packages that a target
does not install; distinguish artifact contents from installed selection.

The proposed delivery route is one versioned catalog with independently selectable
package content and adapter inputs. Selection derives a verifiable subset; the
lock binds both the parent artifact and that subset. A custom subset must never
masquerade as the old full-candidate identity. Downstream use must not require a
checkout of this source repository or arbitrary deletion from a built candidate.
This requires explicit candidate/lock/reader format evolution with old-format
read support and clear unsupported-write outcomes, not permissive extra fields.
The implementation design must fix exact schema versions before coding.

Required dependency omissions, unavailable versions, unknown IDs and collisions
produce an actionable plan error. Optional dependencies never install themselves.
Dependency resolution is within the selected catalog; no network package solver,
automatic technology inference or global machine setting is needed.

## Rules must be consumed, not merely copied

The reusable catalog must distinguish explanatory knowledge, examples and
normative rules. Existing rule IDs retain their meanings and identities unless a
separate semantic change is explicitly selected. File movement alone cannot change
a rule's meaning or promote a target custom rule into a global framework rule.

The target chooses applicable rule sets and technology routes. Installing knowledge
makes it available; it does not declare every rule mandatory in every directory.
Record the target's selected adoption/applicability once in its existing project
configuration/authority and have implementation, architecture, review and testing
consume the same effective choice. Do not ask for the same selection repeatedly
on each operation. Do not introduce a new mandatory approval or evidence pipeline
merely to use an installed reference package.

Missing required specialist coverage must be reported for that operation. A common
review cannot claim .NET coverage when the .NET package/target binding is absent.
For mq lab, preserve its 14 adopted rules, four customizations and domain-specific
technology choices; reconcile their selected portable sources explicitly before
retiring an old active route. Source self-adoption uses `knowledge: []` and retains
its own source development policies independently.

## Naming and Claude support

- Recommend one fixed default `aicf-` shared by both adapters for this iteration.
  Arbitrary configurable prefixes are not required to solve the owner's request.
- Example: ID `code-reviewer`, core `.ai/core/skills/code-reviewer/`, entries
  `.agents/skills/aicf-code-reviewer/SKILL.md` and
  `.claude/skills/aicf-code-reviewer/SKILL.md`.
- Adapters generate tool-appropriate thin entries from the same package metadata;
  provider-specific declarations belong to adapters, not copies of core methods.
- All entry links resolve to selected installed resources. No source checkout,
  absolute machine path or active legacy asset dependency is introduced.
- Add Claude as a new generated adapter; do not reactivate the 15 superseded old
  Claude entries. Retain their historical evidence. Reconcile root routing and
  names so there is one active entry for each selected capability per runtime.
- Test actual discovery/routing on Codex and Claude separately. Generated file
  presence, template similarity or one runtime's success does not prove the other.

## Update, deselection and recovery

Preview the exact additions, replacements, removals, naming transitions and rule
binding impacts before apply. Remove an old `framework-*` entry only when the old
lock proves ownership and its current bytes match. Unexpected or edited entries
block the affected change and remain preserved. Do not leave two autoloaded names
for one capability as an accidental compatibility strategy.

Deselecting a package removes only its unchanged managed files. Project settings,
Lessons, ADRs, workflow history, user rules and unrelated runtime entries survive.
Reject a deselection that breaks an active required dependency/rule binding until
that binding is reconciled in the same planned change. Removing an adapter does
not remove core content still selected by the project or another adapter.

Maintain existing pin, verified-byte loader, bounded reads, path/link/reparse/
alias/hardlink checks, drift detection, quiescence and recovery guarantees. Recovery
must restore the paired core/runtime/lock selection. Project-owned root/configuration
edits need corresponding before-state recovery; no whole-project-ready claim comes
from managed-byte consistency alone. Preserve rc.1 support/evidence and an explicit
rc.1-to-rc.2 path, including prefix changes and knowledge-route migration.

## Reusable content migration and completeness

Before porting, create a bounded inventory from the current reusable engineering
catalogs, `.ai/assets/tech-stacks/dotnet-backend/`, their direct reusable references
and source-rule mappings. Classify each item/rule as portable common knowledge,
portable .NET knowledge, target/source-owned policy, historical example or obsolete
content with a reason. Preserve source identities and destination IDs/paths.

For the selected reusable scope, every active portable item must have a declared
`src` destination and supported installed consumer, or a named owner disposition
visible before RC assessment. Do not call the migration complete based on directory
creation, representative examples or copying Markdown with dangling old links.
Do not let the old P5-T1 deferral silently exclude the newly requested work.
Target-specific facts and this source's execution override stay outside payloads.
Historical rules, transactions and records are not mass-converted or erased.

## Proposed implementation sequence and ownership

| Unit | Bounded result | Dependency / ownership |
| --- | --- | --- |
| S1 selection contract | Exact content-package/catalog/selection/lock format, preset expansion and minimal consumer binding; migration inventory | One shared contract owner; include reader compatibility and target examples before implementation. |
| S2 knowledge source | Selected reusable engineering and .NET content under `src/knowledge`, complete mapping and applicable references | Content owner; hand off exact members. Shared manifest/loader edits belong to S3. |
| S3 distribution and maintenance | Custom selection, content-package reader, locked subset derivation, preview/apply/deselect/recovery | One distribution writer owns loader, selection, assembly, state/plan/CLI and shared manifest/profile integration. Preserve existing safety boundaries. |
| S4 runtime entries | `aicf-` projection plus Claude adapter and exact old-entry migration | Adapter owner; coordinate shared distribution call sites serially with S3, not concurrent writers. |
| S5 installed consumption | Skills actually load selected knowledge; source installs no engineering pack; mq lab retains rules/customizations and selects .NET | Skill-consumer updates first, then separately owned source/target adoption. No direct edit to generated core. |
| S6 RC verification | Focused checks, two runtime discovery probes, source dogfood and mq lab update/recovery with exact candidate/engine identities | Select necessary new-contract checks; keep fixture, actual-target and runtime results distinct. |

This plan does not create implementation Issues/tasks or dispatch work. Keep U001:
one independently assigned Astra/ultra task per implementation Issue, RAM worktree,
local handoff before coordinator integration, no source sub-agents. Shared owners
serialize changes. #369 native driver/caller expansion stays deferred-by-owner;
this plan does not enable CI or adopt the dormant source policy.

## RC completion criteria and remaining stable work

1. Existing public skill IDs remain stable; both runtime entries use the selected
   prefix and resolve to the same installed core.
2. Source and mq lab can use different explicit selections from the same versioned
   distribution without editing source profiles. Source installs no engineering
   knowledge package; mq lab can opt into .NET. Unselected package bytes and entries
   are absent from the installed managed inventory.
3. Selected engineering knowledge is authored under `src`, installable and actually
   consumed by the relevant methods. The migration inventory exposes every excluded
   item and preserves target custom rule semantics.
4. Codex-only, Claude-only, both-runtime and deselection plans are checked; actual
   Codex and Claude discovery/routing have separate evidence. No need for a Cartesian
   matrix across every skill when representative and affected cases suffice.
5. Exact rc.1-to-rc.2 update and recovery cover name changes, old ownership/drift,
   collisions, selected dependencies and target configuration/data preservation.
6. The source repository exercises the installed product in real work, with its
   routing and retained legacy duties explicit. A successful downstream pilot or
   mere installed-file inventory is insufficient source self-adoption evidence.
7. RC status distinguishes implemented, locally checked, actual-runtime checked and
   pending outcomes. No deferred gate is relabeled passed.

Existing [R1-R7](../../workflows/2026-09-23-framework-redesign-control/reports/successor-acceptance-and-repair-scope.md#online-main-completeness-and-known-release-scope-inventory)
remain visible: new-format publication, stable-input update/recovery, cross-computer
admission and other recorded gaps do not disappear. This iteration advances R1
(source adoption) and the Claude part of R6. Add **R8** for selectable installation
and reusable engineering knowledge productization. Stable 0.19.0 remains a later
owner release decision after the selected scope and evidence are assessed.

## This planning checkpoint's evidence

Directly inspected tracked distribution selection/projection, profiles, skill
metadata, legacy content navigation, P5/P6 and source-adoption contracts. A fresh
non-persisted code graph accelerated distribution discovery; excluded roots were
not treated as absence evidence. Material conclusions were checked in tracked
source. Only document readability, links, JSON/YAML parsing, diff/scope and the
existing exact-message commit check apply to this change. No new product tests,
installation, runtime trial or independent audit is claimed; unselected legacy
verification remains deferred-by-owner under U001, owner #322 coordinator/P7.
