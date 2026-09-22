# Source product boundary and installed dogfood design

Status: P1-B design deliverable for [Issue #326](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/326), under #322. These are design boundaries, not an installed product or a completed relocation. The coordinator has adopted tracked stable core/lock/exact runtime outputs and the first copied Codex entry as target choices; P2 remains development-candidate-only. U001 selects the direction; the coordinator reconciles P1-A/P1-B before P2 implementation.

Authority: [execution plan, U001 and D01-D07](../../../assessments/ASM-20260923-00-6oq/execution-plan.md), [architecture A2/A7/A9](../../../assessments/ASM-20260923-00-6oq/architecture.md), and [issue handoff](../../../workflows/2026-09-23-framework-redesign-control/handoffs/issue-326.yaml). The inspected baseline is `53c9c8e58615e87e36f7b74ea8851fe845312daa`. The handoff's earlier `a4865f3` remains historical context; it is not this worktree's starting HEAD.

## One source and explicit consumers

`src/` is the only manually editable reusable product source after a component's cutover. The root is a project installing selected artifacts as another project would. Until cutover, existing files retain current authority; this design does not activate `src` or obsolete a root policy by itself. A component has one current owner at every transition step.

| Location after cutover | Owner and permitted change | Distribution behavior |
| --- | --- | --- |
| `src/skills/<id>/` | Capability owner; canonical `SKILL.md`, `skill-package.yaml`, owned schemas, tools, templates and references | Only explicit selected members enter skill payload |
| `src/shared/` | Small reusable primitives with demonstrated consumers | Only explicit required members; first Lesson requires no shared package |
| `src/profiles/` | Source selection owner; bundles list skills, not copies | Build input; selected identities recorded in generated metadata |
| `src/adapters/` | Runtime/provider owner; reusable projection templates or implementation | Template is build input; generated runtime members separately inventoried |
| `src/distribution/` | Product distribution owner; manifest and later consumer installer source if implemented | Manifest is build input, not project configuration; installer files require explicit selection |
| `tools/`, `.github/`, source release records | Source maintainer operations, build invocation and CI/release orchestration | Never implicit downstream payload; reusable product behavior must not be hidden in `tools/` |
| `.ai/core/` | Installer-managed selected artifacts | Generated installed bytes; change `src` and reinstall, never hand-edit a second canonical copy |
| `.ai/framework.lock` | Installer-generated identity, reviewed by project owner | Installation output, never builder input or copied from the source repository |
| `.ai/custom/`, configured artifact roots, `.dev/` | Project owner, including source repository policy and work history | Preserved; no package replacement or directory-wide cleanup authority |
| `.ai/local/` | Machine settings and disposable cache as explicitly classified | Ignored and excluded; recovery records need an explicitly durable location |
| `.agents/skills/` and other runtime surfaces | Installer owns only exact generated paths recorded in lock; project owns everything else | Generated projection, never a package input or directory-wide replacement target |
| `AGENTS.md`, `AGENTS.zh-TW.md`, `CLAUDE.md`, root README files | This project's collaboration and onboarding entries | Optional reviewed seed suggestion; updates never replace whole root documents |
| `dist/` | Rebuildable output and staging | Ignored in future implementation; never authoritative input or durable backup |

The physical `.ai` locations are this installation layout's defaults. They are not hard-coded portable skill/config/artifact contracts. A caller supplies project root and project/local config paths explicitly under P1-A. Lessons can live in `docs/lessons` or another configured filesystem root without moving into `.ai/custom` or `.dev`.

Core means framework ownership, not mandatory monolithic installation. Workflow, governance, maintenance add-ons and .NET content are absent from the initial Lesson selection. Source release/history functionality is never an implicit dependency.

## Interface with P1-A (#325)

P1-A owns `skill-package.yaml`, configuration, artifact roles, the first Lesson schema family and tool descriptions. This design consumes that contract; it introduces no competing schema or config resolver.

Coordinator read-back: package-relative metadata contains stable ID/version, entrypoint, exact required/optional dependencies, runtime, artifact roles and owned schemas/tools/templates; Lesson has `required=[]`; callers supply project/config locations; initial store is filesystem; tools remain `implementation_status=planned` until implemented.

| Interface | P1-B decision | P1-A authority retained |
| --- | --- | --- |
| Skill metadata | Installed beside entrypoint with package-relative references unchanged | ID/version, dependency and ownership field syntax |
| Dependency selection | Explicit selected IDs plus exact required closure; missing dependency/cycle is an error, not a network fetch | Declaration syntax; optional presence never becomes required |
| Config | `.ai/custom/framework.json` is this project's coordinator-selected JSON path | Precedence, meanings, locked permissions, containment, artifact bindings |
| Records | Remain in caller-selected project-owned roots | Lesson schema, writable operations, template binding and conversion |
| Runtime | Generated entry routes to installed skill | Availability/results; an entry is not evidence of tool execution |
| Lock/manifest | Installation identity and file membership, separate from record formats | Do not repeat or version P1-A schemas inside a distribution schema |

The coordinator supplied exact P1-A names: skill ID `lesson`, family `lesson.record`, schema version `1.0.0`, `schemas/lesson-record.schema.json`, `templates/lesson.md`, `references/configuration.md`, and `references/operations.md`. Tool ID `lesson.fs` is planned with `entrypoint=null`; required and optional dependencies are both empty. The source specimen belongs to `.dev/design/framework-next/portable-contracts/lesson/`. Metadata references are package-relative (`SKILL.md`, never `lesson/SKILL.md`). Cross-review read the metadata and configuration reference from P1-A commit `c3891615f97625e7c59cd871abea3c2b27b5021f` and confirmed these exact six source members. The package and installed layout both include the configuration and operations references. P1-A supports JSON project/local configuration only; this design selects the physical project path without redefining its schema. Those files are not yet integrated into this branch. A design path creates no executable. No registry, general dependency solver, schema validator or installer is implemented here.

## Allowlist and outputs

The future builder reads one immutable selected Git tree. It selects regular blobs explicitly named by one source manifest, preserving bytes and declared executable mode; checkout line-ending conversions do not define artifacts. Reject missing entries, escaping/absolute paths, symlinks, submodules, case-folded collisions and duplicate ownership before output. Build invocation is source tooling; selection/projection rules are product source in `src`.

Start with the allowlist, never a repository archive followed by exclusions. The manifest and component metadata jointly determine the closed set; each file has one component and destination. Metadata lists component members; the manifest maps selected members to installation paths. A disagreement fails, rather than automatically widening either list. New files do not ship merely because they sit below `src/skills`.

Source governance, release/workflow/assessment history, `.ai/custom`, all configured project-data roots, local settings and secrets are inadmissible inputs. The initial manifest has exact entries and no globs. Even a file copied into `src` needs content review: no source-only policies, dated history, host paths or hidden `.dev` dependencies. Unresolved references block that component's packaging; do not include all governance to satisfy a link.

| Output | Composition | Ownership boundary |
| --- | --- | --- |
| Standalone Lesson | Skill plus exact required content/tool dependencies; initial Lesson has none | No workflow store, maintenance skill or root project data |
| Optional bundle | Union of selected members and required closure from the same manifest | One release unit and component inventory initially; no auto-download solver |
| Runtime installation | Same payload plus named adapter-generated entries | Exact generated paths/digests; no editable independent runtime copy |
| Future plugin envelope | Same manifest selection plus platform metadata | Deferred until concrete need; no publication in P1-B |

The [manifest](examples/distribution-manifest.example.yaml) separates build inputs, payload and generated outputs. The [layout](examples/layout.txt) shows both sides. The [installation example](examples/installation-plan.example.yaml) has null runtime digests and no execution receipt; it is not a valid installation lock.

## Runtime projection and ownership conflicts

The first candidate uses a copied generated Codex entry at `.agents/skills/framework-lesson/SKILL.md`, routing to `.ai/core/skills/lesson/SKILL.md`. The adapter computes installed-path references; no reference back to `src`, `.ai/assets`, or the source worktree. Tools/templates remain in the installed skill and the entry explains their resolution. Additional runtimes need explicitly selected adapters; symlinks are not required.

Projection binds the installed entrypoint identity and adapter template. Generated records bind adapter identity and every generated file digest. Custom skills use a project namespace or explicitly approved binding. Name/path collision fails with both owners identified; no silent shadowing. Unknown runtime files are preserved, including files inside a formerly generated skill directory. Remove only previously owned, unchanged files no longer generated.

Before changing managed files, compare actual bytes with the old lock. Modified or unowned core/runtime content stops the affected operation and yields a reconciliation choice: preserve, adopt a reviewed source change, or move an extension to custom with explicit binding. Whole replacement and development mode do not authorize overwriting drift.

## Stable and development consumption

Stable is the default project choice: one selected released artifact, digest and exact components/adapter, never floating `latest` or a branch label. Development is selected explicitly for one worktree and records source commit, components, adapter inputs and generated digest. A candidate is never relabeled released.

After P2 source implementation and the later explicit installation cutover, a developer changing one Lesson follows this minimum sequence:

1. Edit only `src/skills/lesson/`, updating metadata when needed. Commit a coherent snapshot; the initial route builds an exact commit, not a dirty checkout.
2. Select development and Lesson from the same manifest. Build only its closure and selected adapter into disposable staging. No repository copy or version matrix.
3. Compare candidate inventory with installed lock and actual owned bytes. Preview managed additions/changes/deletions, runtime projection and independent data conversion.
4. Apply the selected candidate to this worktree with explicit project/config paths. Preserve custom and artifact roots. Activate only after required implementation-time checks succeed, then emit the actual matching lock.
5. Use the installed entry and configured Lesson store. Fix defects in `src`, rebuild and reinstall; no edit-back from `.ai/core`.
6. Return to the actual captured previous installation through the same compatibility/drift plan. Use a stable selection only when a real released installation was captured; an initial P2 candidate has no invented stable baseline. If development wrote data stable cannot read, use a supported conversion or paired data backup; changing the profile alone is insufficient.

These are future operations, not available CLI commands or executed checks. P1-B does not run them. P7 owns later validation/tooling design.

The coordinator adopted tracking stable `.ai/core`, lock and exact generated runtime files together as this repository's target dogfood layout, exposing a matching installation to a clone once a real stable artifact exists. The first selected runtime is the copied `.agents/skills/framework-lesson/SKILL.md` entry. P2 implements only the development-candidate path and must not label it published stable. Coordinator integration sequencing defers managed apply/recovery implementation to P6 and actual build/install trials to P7; the existing root runtime stays active until that explicit cutover. `.ai/custom` and durable artifacts stay tracked by project choice. Development artifacts retain development identity even if their source is integrated; default-branch integration does not make a candidate stable. `dist` and local cache are ignored. A project may later select rebuild-on-install, but lock and generated files must still describe one selection. Existing ignore rules require explicit P2/P6 owner edits; this issue makes none.

## Whole replacement, delta I/O and recovery

Whole replacement means the complete selected managed set can be reconstructed from its package. Delta is an application optimization against the old inventory; neither changes ownership.

| Case | Planned behavior |
| --- | --- |
| Same path, mode, digest | No write/timestamp churn; unchanged adapter inputs may reuse matching projection bytes |
| Added/changed member | Stage/write only it or the smallest required coherent component |
| Removed/deselected member | Delete only unchanged paths recorded as framework-owned in old lock |
| Occupied new destination or modified old member | Stop/reconcile, never adopt or delete by directory membership |
| Clean install or explicit full reinstall | Materialize selected set, protect custom/unknown files/project data |
| Same package, schema conversion needed | Separate data plan; equal package digest is not data compatibility |

No measured I/O saving is claimed. A full archive may still be acquired; drift detection reads unchanged files, and coherent staging may write more than a single modified member. Low I/O is an objective, not a benchmark.

Before mutation, capture a matching recovery set: previous core inventory/content, lock, exact owned runtime projection, selected config version/digest, and before-versions/backups of project records/indexes changed by the operation. Pin unaffected roots as unchanged; do not copy the whole project. Recovery material must survive worktree RAM-disk loss in an explicitly durable store. A Git commit retains tracked snapshots, not ignored/external records.

Sequence: resolve/detect drift -> separately plan package/data changes -> acquire/stage -> establish durable recovery -> apply supported data changes and managed outputs under a bounded operation record -> verify actual selected installation -> activate its matching lock. Withhold normal framework execution during incomplete activation. A lock is not success evidence before all selected state matches; interruption preserves last good lock and explicit recovery-needed state.

Do not claim a cross-platform atomic transaction across core, lock, runtime and project stores. Open Windows files, cross-volume moves and partial runtime writes may fail. Recovery restores the matching captured set or stops with remaining actions. Restoring core while newer data remains unreadable is not success. Expected digests/revisions protect concurrent project/external changes: do not restore an old whole backup over newer user work automatically; reconcile or stay recovery-needed.

Conversion belongs to the schema/skill owner and is separate from package version. Supported structural conversion needs its selected plan and unchanged input. Preserve recognized extensions. Unknown custom structures, unpreservable comments, ambiguous ownership or lossy conversion require a concrete reconciliation decision before mutation; `unsupported` is valid. No reverse edge means restoring matching backup; absent backup is failure. Migration notes explain changes, not executable conversion authority.

## Bounded transition and completion

The [inventory](mapping-inventory.md) separates initial Lesson work from later phases. At component cutover, extract portable meaning and references into `src`, install the candidate, and retire the former active reusable entry/reference in the same bounded integration. Retained old templates are explicitly project-owned legacy templates or frozen evidence, never second product owners. Copying mixed `.ai`/`.dev` trees into `src` is not transition.

Root policy/skills govern this project until the coordinator explicitly switches their entrypoints. Plain shell/Git can repair source without requiring a broken framework to bootstrap itself. Preserve historical records: no bulk conversion, history rewrite, arbitrary old-version upgrade guarantee, or source-release add-on in mandatory core.

P1-B delivers design, inventory, examples and issue workflow. P2/P5/P6 implementation, P7 validators/tests/CI, release/publication and adoption remain with their owners. P1-A exact names are aligned; the coordinator still owns cross-review and integration of its finalized field semantics. Tracked stable installation and the first copied Codex entry are coordinator-adopted target choices, not active runtime state. Their implementation and any future stable publication remain separate work.

Under U001, legacy validators, `check-all`/critical, suites, package builds, migration/upgrade trials, independent audit machinery and CI are `deferred-by-owner`. Only readability, JSON/YAML parsing, references/content, Git diff/status and exact commit-message format are checked here. They do not prove installation, portability or rollback behavior.

Integration sequencing authority: [P1 integration and P2 scope](../../../workflows/2026-09-23-framework-redesign-control/reports/p1-integration-and-p2-scope.md). This narrows the initial P2 activation proposal to code delivery under U001; no installed-state change is claimed.
