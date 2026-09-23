# Root bindings, configuration and Git proposal

Design for later coordinator-owned adoption; none of these root edits is applied
by #361. Relative paths below are anchored at the **later selected project_root**,
not this task's cwd. This task's `F:/framework-next/361` is not the pilot target.

## Concrete root pointer changes

| File / present meaning | Reviewable future edit | Preserved project responsibility |
| --- | --- | --- |
| `AGENTS.md` Task Routing points to `.ai/assets/skills/README.MD` for all skills | During Lesson pilot add only the bounded Lesson route below; retain other current routes. During later cutover replace each activated row with `.agents/skills/framework-<id>/SKILL.md`, whose generated links lead to `.ai/core/skills/<id>/SKILL.md` | Issue authority, branch/commit policy, source release, ownership, credentials, project tests and U001/P7 status |
| `AGENTS.md` Progressive Context / Navigation and legacy `AI-CONTEXT-BOUNDARY.md` source placement | At broader adoption state `src/` is editable reusable product source, installed paths are consumed, and list explicit source-only/remaining legacy routes | Loading an installed skill never overwrites target rules; source standards are explicit context, not hidden package dependencies |
| `AGENTS.zh-TW.md` | Translate each adopted rule and route with the same structure/scope; do not translate or duplicate generated core manually | English canonical / Taiwan Traditional Chinese parity |
| `CLAUDE.md` contains only `@AGENTS.md` | Keep the thin pointer. AGENTS states new adapter availability and withdrawn legacy capabilities for Claude | No invented Claude adapter; unsupported is visible while unaffected legacy scopes remain usable |
| `README.md`, `README.en.md` skill navigation and legacy adoption/upgrade instructions | Separate development dogfood instructions and the actual installed selection from old published-package support; link real installed routes only after they exist | Historical releases and their supported upgrade guides remain version-scoped; no new stable release claim |
| `.ai/assets/skills/README.MD` and runtime indexes | Replace current canonical claim per activated package with its installed consumer pointer and editable `src` owner; label retained legacy/source-only rows | Preserve retired identifier records and old provenance; do not turn retired IDs into aliases |
| `.dev/INDEX.md`, `.ai/INDEX.MD` | Add actual new collection/installed paths only at adoption; retain source and legacy links | Coordinator owns shared indexes; no edits here |

Proposed **pilot-only** AGENTS addition, to adopt with the config/store binding:

> Lesson development pilot: for the explicitly selected new JSON Lesson collection,
> use `.agents/skills/framework-lesson/SKILL.md` and its installed public contract.
> Select project config `.ai/custom/framework.json` explicitly. Existing Markdown
> Lessons retain their current project owner and evidence links. This is only the
> lesson-minimal / Lesson 0.2.0 / Codex pilot; other capabilities keep their named
> current routes. Edit reusable Lesson code only in `src/skills/lesson/`.

This wording does not itself prevent execution or make files available. New
sessions and the activation window in [adoption-and-recovery.md](adoption-and-recovery.md)
are required. There is no old Lesson runtime wrapper to remove; the predecessor
is the Markdown Lesson authoring/lifecycle route, not a fabricated skill ID.

For broader adoption the coordinator must reconcile source workflow policy with
new aggregate records explicitly. Proposed rule: new ordinary execution may use
`.dev/workflows-v2` under the selected package, with the same online Issue/actual
owner authority; active legacy/source-release workflows continue under their
existing contracts. Source release/Issue closure/provider rules do not disappear
because a portable workflow can run standalone. No bulk rewrite of old tasks.

## Actual profiles and proposed broader selection

Current `lesson-minimal` selects Lesson only; `knowledge` selects Lesson/ADR/
promotion; `work-management` selects PR/local backlog; `collaboration` is those
five together. All select Codex. None currently includes workflow, review,
authoring, CBF/compliance or optional context maintenance.

Propose a new shared-owner profile ID `source-repository` at
`src/profiles/source-repository.yaml`, containing exactly:

- lesson@0.2.0;
- adr, standards-promotion, pr, software-development-orchestrator,
  code-reviewer, requirement-author, spec-author, problem-frame-author,
  spec-compliance-validator, each @0.1.0;
- adapter codex; no implicit skill dependency or optional maintenance.

This is **ten actual packages / 76 source members**, a proposal rather than an
existing profile/build result. Choose one coherent complete selection; sequentially
applying two independent profiles is not assumed to union installations. A smaller
profile can deselect earlier managed members. Add the five #347 engineering skills
only after their actual delivery/mapping and coordinator selection; without their
replacement or an explicit owner decision that they are unneeded, full adoption
remains pending. Do not claim the ten-package source selection covers them.

Optional maintenance can use a separately selected `context-maintenance` convenience
profile or a deliberate combined profile if the source owner supplies it. Neither
exists at this checkpoint. Selecting it must not accidentally remove ordinary
skills or silently add it to ordinary profiles. `local-backlog` remains optional
and off for this source repository's default GitHub work-management choice.

## Configuration, templates and collections

The [pilot JSON proposal](pilot-framework.proposal.json) is a literal future
`.ai/custom/framework.json` body, stored only under this design. It is new config 2,
not a migration input/output and not read by any tool here. The caller must supply
actual absolute project_root/package_root and explicitly select project_config;
there is no discovery by filename or cwd. No local config is selected initially.

The pilot locks `store.root`, `store.tracking`, `template`, and grants only the
new `.dev/lessons/records` write root. Provision that directory separately in the
later authorized window; no parent-creation permission is implied. `tracked` is
intent, not a Git operation. No acceptance adapter is configured: candidate
creation/read operations can be selected later, but `accept` is not thereby enabled.

The following concrete broader settings are proposed for later **selected** namespaces
only. For each, use `store.kind=filesystem`, `store.tracking=tracked`, the listed
root, `template={origin:package,path:<listed>}`, project `write_roots=[<root>]`,
and locks on `store.root`, `store.tracking`, `template` under that same namespace.
Do not copy these into null-config instruction namespaces.

| Namespace | New project store | Package-relative template | Preserved predecessor / extra required input |
| --- | --- | --- | --- |
| lesson | `.dev/lessons/records` | `templates/lesson.md` | Existing `.dev/lessons/{environment,validation}` Markdown and indexes; real decision-source bindings required before accept |
| adr | `.dev/adr/records` | `templates/adr.md` | Existing ADR Markdown; decide requires actual project-selected evidence binding and actor/decision provenance |
| standards-promotion | `.dev/knowledge/promotions` | `templates/promotion.md` | Existing standards remain normative owners; propose/reconcile require explicit `source_read_roots`, exact targets and adoption/effect mappings; no fabricated generic adapter |
| pr | `.dev/pull-requests` | `templates/pr.md` | Actual repository/base/head, validation dispositions and task authority; provider operation remains explicit and separate |
| software-development-orchestrator | `.dev/workflows-v2` | `templates/workflow.md` | Existing `.dev/workflows/` remains; select `retention={compact_after_days:30,archive_after_days:90,purge_after_days:null}`, `resume_budget_chars=12000`; previews only, no scheduler/deletion |
| problem-frame-author | `.dev/problem-frames/records` | `templates/cbf.md` | Existing CBF/SWF files preserved; all store/write roots/ancestors must already exist |
| local-backlog (only if later selected) | `.dev/local-work-items` | `templates/work-item.md` | Never `.dev/backlog/items`; no provider sync or replacement of online Issue authority |

The first six proposed collection paths were directly checked absent in this
checkout. That is not a claim about the later target or ignored/external data.
All supplied bindings require fresh collision, ownership and containment checks
there. The optional local-backlog path is only a future proposal, not inspected.
Prepare project-owned ancestors explicitly, without granting write scope to all
`.dev`. Persistent bindings accompany store-relative IDs in handoffs.

Default package templates avoid copying incompatible historical Markdown templates.
If a project template is later needed, propose a separate
`.ai/custom/templates/<id>.md`, `origin=project`, explicit path and owner-reviewed
supported tokens. Keep old `.dev/lessons/templates/lesson-template.md` and
`.dev/adr/ADR-TEMPLATE.md` as legacy history/templates, never silently render them
with a new tool. No custom template currently exists at these proposed locations.

Instruction packages `code-reviewer`, `requirement-author`, `spec-author`,
`spec-compliance-validator`, `ai-context-auditor`, `ai-context-governance` have null
configuration: give them explicit task scope, target files, formats and permitted
destinations; no settings/store/schema provisioning. Requirement/spec output may
stay in current `.dev/requirement/` and `.dev/specs/` under their project owners.

A later local override may be explicitly selected at `.ai/local/framework.json`,
config 2 with `skills` only, after ignored/untracked status is proven. It cannot
carry project constraints or widen permissions. Preserve existing
`.dev/ai-context/local/` state; no implicit relocation of CLI routing or credentials.

## M01 decision and bounded observation

At this fixed checkout the exact paths `.ai/custom/framework.json`,
`.ai/local/framework.json`, `.dev/project-config.yaml`,
`.dev/ai-context/provenance.yaml`, `.dev/ai-context/customizations.yaml`,
`.ai/core`, `.ai/framework.lock` were absent. `.ai/custom` and `.ai/local` were also
absent. These observations cover neither other checkouts nor arbitrary project/
local paths, backups, historical examples or external stores. Historical examples
with config 1 are not an actual selected target input.

M01 remains **unassigned**. If the later target supplies a real closed P2 Lesson
JSON config 1 and v2 is actually needed, identify exact project/local pair, bytes,
owner, locks, bounds and new capability need; then request the already selected
bounded 1->2 work through the coordinator. Lesson 0.2 can still read the closed v1
shape; version 2 is needed for the other selected configured packages/new adapters.
No YAML, provenance, customization ledger, old workflow or Lesson Markdown
conversion belongs to M01. No required Lesson-record migration: v1 JSON is read-only
in Lesson 0.2; explicit derive creates a new v2 identity and decision state.

## Byte-preserving Git and tracking proposal

Observed root attributes apply `text=auto eol=lf` to future core, lock, runtime and
config paths. No `.ai/local/` or `dist/` ignore exists in the inspected root file;
`.dev/ai-context/local/` and `*.tmp` are already ignored. Source text normalization
may continue, but installed exact bytes must survive staging/checkout.

For the pilot, propose these later root attribute entries, after general text rules:

```gitattributes
.ai/core/skills/lesson/** -text -eol -filter -ident -working-tree-encoding -merge
.ai/framework.lock -text -eol -filter -ident -working-tree-encoding -merge
.agents/skills/framework-lesson/SKILL.md -text -eol -filter -ident -working-tree-encoding -merge
```

Extend only to exact selected package subtrees and exact generated entry files as
selection grows; no `.agents/**` or `.dev/**` blanket rule. Keep normal readable
diffs by not disabling `diff`; `-merge` makes concurrent managed edits require
explicit reconciliation/rebuild. No hand resolution that creates bytes inconsistent
with the lock. `-text` disables line-ending conversion; unsetting transforms avoids
selected filter/ident/encoding conversion. Higher-priority or deeper attributes
can override root policy, so actual effective attributes and raw blob/checkout
identities must be observed. This proposal follows [Git's attribute contract](https://git-scm.com/docs/gitattributes),
not a performed round-trip test.

Track one coherent candidate's exact core inventory, generated Codex entries and
actual `.ai/framework.lock` together. Track accepted `.ai/custom/framework.json`
and project records/templates separately as project-owned files. Do not stage a
whole runtime/core directory blindly or infer ownership from Git tracking. Project
config remains ordinary LF UTF-8; any selected digest is taken from the actual
bytes after materialization. Raw evidence originals keep their existing binary
exceptions; no mass `git add --renormalize`.

Proposed new ignore lines, if these locations are adopted:

```gitignore
/.ai/local/
/dist/
```

Do not ignore `.ai/core`, the lock, selected generated entries, `.ai/custom`, all
of `.dev`, or project collections. Do not stage secrets, machine config, candidate
scratch or operation/recovery snapshots. #359 must supply actual guard/marker
paths and lifecycle before exact transient exclusions are adopted; never guess
those names or ignore a recovery-needed marker as proof it is safe to proceed.
Durable managed recovery remains an explicitly selected external store.

Tracking a development candidate keeps its development identity and null release
version. A stable tracked installation is a later option only when a real released
artifact exists. P7 must compare candidate raw bytes, staged Git blobs and fresh
checkout bytes/modes, including clone behavior; Windows mode remains inventory-only
unless the actual backend says otherwise. No round-trip or native guarantee is
claimed by this design.
