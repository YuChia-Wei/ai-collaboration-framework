# Installation reader and planner handoff

Issue [#354](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/354),
selected [P6 contract](../p6-selected-contract.md), and the
[maintenance formats](../installation-update/formats.md) own the scope.
This is development source, not a published engine or installation result.
U001 defers behavioral verification to program #322 coordinator / P7.

## Exact public surface

The source modules are [installation_state.py](../../../../src/distribution/installation_state.py)
and [installation_plan.py](../../../../src/distribution/installation_plan.py).
The coordinator's next single maintenance writer owns their necessary integration.
There is no CLI, bootstrap, apply, recover, lock producer, marker producer or migration here.

- `installation_state.inspect(request: dict | bytes) -> dict`
- `installation_plan.plan(request: dict | bytes) -> dict`
- `installation_state.read_candidate(candidate_root: str) -> Candidate`
- `installation_state.read_lock(project_root: str) -> InstalledLock | None`
- `installation_state.observe_installation(project_root: str, candidate: Candidate | None = None) -> Observation`
- `installation_plan.member_delta(old: InstalledLock | None, candidate: Candidate) -> list[dict]`
- `installation_plan.is_noop(observation: Observation, candidate: Candidate, mode_policy: str) -> bool`

The two operation functions are the untrusted-input/result boundary. `bytes` means
strict UTF-8 JSON with duplicate rejection; dict means an already decoded exact
built-in object with no shared/cyclic mutable containers. Unknown keys, subclasses,
bool/float versions, malformed Unicode and excess limits fail closed. Request
JSON need not be canonical. Returned plan identity uses `distribution.data.json_bytes`.

Low-level readers raise `InstallationError` or filesystem/format exceptions;
operation functions translate them into bounded diagnostics without host paths.
Private `_reader` keyword parameters share one call's budget; they are not public
API fields or policy overrides. Returned dataclasses are ephemeral observations,
not trust tokens: contained dictionaries remain mutable. Pure helpers require
unchanged reader-produced inputs and never admit mutation. A writer must reread
and recompute under its own coordination; no caller-supplied dataclass is evidence.

`Candidate` contains root, identity, selection, inventory, build, the three raw
metadata byte strings, members indexed by destination, and verified contents
indexed by destination. `InstalledLock` contains the closed document, original
raw bytes, raw SHA-256 and member map. `Observation` contains root, optional lock,
all observed old-member drift, bounded unknown entries (or null when unavailable)
and marker paths. Markers intentionally suppress inventory claims.

## Closed request and result contract

Common fields exactly: `api_version=1`, `operation`, `project_root`, `engine_root`,
`engine`. Inspect permits only optional `candidate_root`. Plan additionally
requires `candidate_root`, `candidate_identity`, `expected_lock_sha256` (null means
absent), `mode_policy`, `scratch_root`, `staging_root`, `recovery_root`, `durability`,
`protected_inputs` and `project_data_action="none"`.

Durability has exactly `declared_by`, `declaration_reference`, `failure_domain` as
nonempty strings. It is an assertion, not measured durability. Protected inputs
are a path-sorted unique finite list of `{path,sha256}`, with null SHA meaning
expected absence. Their individual bytes/absence alone are checked; no config,
record, compatibility, semantics or reference discovery is performed. Protected
paths use direct ancestor stat and exact-file reads, with no data-directory
listing. Overlap,
alias or prefix collision with managed/control paths is refused.

Inspect results have exactly `api_version`, `operation`, `outcome`, `changed=false`,
`details`, `diagnostics`. Outcomes are inspected/unsupported/blocked. Details are
exactly `managed_state`, `project_readiness="not-assessed"`, `owned`, `unknown`,
`drift`, `mode_policy`. Unavailable values are null. Present/inaccessible markers
produce recovery-needed and no fabricated inventory. Bad/unsupported lock input
blocks inspection instead of conferring ownership; absence grants none. All
observable old member mismatches are collected; an unreadable input or budget
failure returns blocked rather than a partial successful inventory.

Successful plan results contain exactly `api_version=1`, `operation="plan"`,
`outcome="planned"`, `plan`, `plan_sha256`. Failure uses the common result with
`details=null`, `changed=false`, outcome conflict/unsupported/blocked. Diagnostics
are `{code,path,reason,next_action}`; path is relative or null, never a host root.

Plan fields are exactly those selected in formats.md: `api_version`, `operation`,
`project_root`, `candidate_identity`, `engine`, `expected_lock_sha256`, `mode_policy`,
`roots`, `durability`, `project_data_action`, `protected_inputs`, `maintenance_scope`,
`delta`, `preserved_unknown`, `path_budget`, `prerequisites`. Roots has exactly
engine/candidate/scratch/staging/recovery. Arrays with defined order are sorted;
source metadata retains the actual builder's ordering (generator/dependency lists
are not arbitrarily sorted). No UUID/time enters the plan hash. A detached JSON
snapshot prevents mutation of the original request from changing the returned plan.

Delta rows have destination/action/before/after. Descriptors are null or exactly
sha256/size/mode/owner/kind. Actions are add/change/remove/unchanged/mode-only.
Mode-only means all descriptor fields except mode match. Windows retains declared
inventory with `mode-not-materialized` prerequisite text and no proposed member
byte rewrite. POSIX requires exact 0644/0755; cross-platform/mode-policy transitions
are unsupported. Identical unowned bytes still conflict. Unknown sibling files and
whole unknown subtrees are preserved, with no recursive removal or descent.

No-op requires a marker-free drift-free supported old lock, equal candidate identity,
unchanged inventory and equal mode policy. Build timestamps/run IDs and current
reader pin cannot churn it. Member delta can be all unchanged while candidate
identity differs: that still needs new lock publication. Prerequisite
`lock-publication` distinguishes pending from not-required; `is_noop` supplies the
precise integration helper. The planner itself never writes even for non-no-op.

Prerequisite statuses are satisfied/pending/not-required/not-applicable, each with
id/status/owner/next_action. They cover candidate provenance limits, durability,
exclusive allocation, fresh observation, lock publication, quiescence, mode
materialization, native backend, writer engine closure and guard. Pending
mechanical prerequisites must block apply. No readiness/compatibility pass is
introduced. The present reader pin can produce a useful preview, never admission
for an unimplemented mutation engine.

## Actual available evidence and parser reuse

Candidate 1 accepts only the actual assembly selection/files/build shapes and
exact emitted file closure: payload, generated runtime and three metadata files.
Canonical UTF-8 bytes, lengths, SHA-256, payload Git blob identities, destination
ownership, component/dependency closure, adapter input/output relationships and
cross-document identity are checked. Extra directories/files, aliases, links,
reparse points, hardlinked files, missing completion and unsupported formats refuse.

Actual package metadata is passed to existing `package.load_package` (versions
1/2/3) and `package.check_references`, using `git_source.Blob` only. No `GitSource`,
assembly, selection or adapter code is invoked. YAML event inspection bounds work
before the shared loader; it is not a second metadata semantic parser. Package
schemas receive bounded JSON/reference inspection through the existing owner;
no generic schema-validation registry exists. This issue adds no separate JSON
schema because the same-owner Python readers own the exact serialized shapes,
version refusal and mechanical validation. Lock 1 has no migration edge.

Manifest/profile/template/generator identities and source commit/tree are carried
as provenance and checked for available identity consistency. Those external raw
files are absent from the candidate. They are not downloaded, fully reproduced,
authenticated, or presented as complete Git source evidence. Runtime output hashes
are checked, but regeneration from an unavailable template is not claimed.

## Engine boundary and prerequisites

Before any product import, the caller must start Python with `-B` (or establish
`sys.dont_write_bytecode=True` before imports). Operation/metadata checks refuse
otherwise; an in-function guard cannot undo bytecode created by an earlier import.
Python 3.10+ and existing PyYAML 6 are explicit host prerequisites; no installation
is attempted. This source library has no selected/verified launch bootstrap.

EnginePin is exactly id=`framework-managed-installation`, version=`1.0.0`, full
lowercase 40/64-hex source_commit, sorted files `{path,sha256}`. The current exact
reader closure is exported as `READER_ENGINE_FILES`:

- src/distribution/__init__.py
- src/distribution/data.py
- src/distribution/git_source.py
- src/distribution/installation_plan.py
- src/distribution/installation_state.py
- src/distribution/package.py

Explicit engine_root must be the executing reader checkout, external to every
other selected root. The reader checks raw file hashes and origins of loaded
local modules. It observes standard files-backend Git HEAD using bounded reads
of `.git`, HEAD, commondir, exact loose branch ref or packed-refs. No Git command,
config discovery, source traversal or fetch occurs. Detached HEAD or one direct
refs/heads reference is supported; absolute worktree gitdir locators permit the
assigned RAM checkout with persistent common Git storage. Reftable, chained refs
and unknown layouts fail closed. Git metadata locators are read-only provenance,
not operation roots. HEAD observation and raw pins do not attest loaded Python
memory, Git object authenticity or byte equivalence to the entire commit tree.

The later sole writer must integrate installation state/plan with its final
entrypoint, verification bootstrap, local import/resource closure, interpreter /
PyYAML provisioning and native backend. Extend the explicit closure coherently;
do not claim these six files describe the final apply/recover engine. Unknown
engine members/versions fail unsupported now. No provider/model substitution is
hidden in this source-only boundary.

## Bounded reads, roots and path budget

Per public operation: at most 128 MiB aggregate file reads (including engine,
metadata, candidate, old inventory and protected inputs); 16 MiB per regular file;
4 MiB per JSON document/request/lock/serialized plan; 256 KiB per YAML/frontmatter;
4096 members/source identities/engine files; 128 components/adapters/dependencies;
128 protected paths; 20,000 enumerated entries; 100,000 JSON/YAML nodes/events;
48 nesting levels/path segments; integer magnitude at most 128 bits. Limits are
fixed source constants, not caller knobs. Over-limit operations never partial-pass.
Finite schema resource numbers are allowed; version/size fields remain exact ints.

Only declared candidate closure is fully enumerated. On the project side, listings
follow exact requested/owned ancestor paths and their immediate entries; sibling
reporting descends only known parents inside selected package/runtime directories.
Unknown subtrees are listed once and never opened. With no lock/candidate there is
no guessed ownership inventory. No repository, data store or recovery store scan.

Every selected root must already exist, be absolute/direct/local and outside the
other roots, with no symlink/reparse ancestors, traversal, device/UNC/drive-relative
spelling, reserved Windows names or volume-root stores. Scratch and staging may
be exactly equal; other overlap is refused. Hardlinked regular inputs are refused.
Filesystem observations/hash checks do not remove TOCTOU; external concurrent
writers remain unsupported and the writer must demand quiescence.

Path budget is a conservative refusal policy on every supported host: 240 UTF-16
units for full paths, 255 per segment. It includes candidate/engine inputs, managed
and protected project destinations, controls, derived fixed-width sibling temp
names and scratch/staging/recovery paths. `path_budget` has policy,
full_path_utf16_limit, segment_utf16_limit, maximum_full_path_utf16,
maximum_segment_utf16, checked_paths, backend_certification=`not-assessed`.
No OS certification or speed measurement is implied.

Future writer layout assumptions: scratch `i-<32hex>/{metadata/*,plan.json,.ai/framework.lock}`;
staging `i-<32hex>/<destination>` for added/changed bytes and the next lock;
recovery `i-<32hex>/{operation.json,objects/<64hex>}`; project sibling `.fi-<12hex>`.
Placeholders calculate lengths only and allocate nothing. The writer must bind
real names, exclusive absence, hash-prefix collision handling and any extra
backend paths before mutation. Any layout extension needs its own path budget.

## P7 cases and uncompleted work

No cases below have been executed. All behavioral evidence is `deferred-by-owner`,
authority U001, owner program #322 coordinator / P7, next action select focused
new checks before any pilot/root use.

1. Real builder candidates for metadata 1/2/3, including null-config instructions;
   matching old lock and clean install; approved candidate identity selection.
2. Duplicate keys, bool/float versions, unpaired Unicode, canonical-byte drift,
   member/source/adapter mismatch, required/optional dependency and closure errors.
3. Every-old-member drift (including unchanged ones), mode drift, expected-lock
   mismatch, identical unowned files, parent/child and case collisions.
4. Removed owned member beside unknown files/directories/links; no unknown descent;
   no-op across build time/run changes; same bytes with changed declared mode.
5. Missing/corrupt/unsupported lock, present/unreadable/malformed package or M01
   marker, unknown control occupation and absent no-op coordination resource.
6. Protected raw bytes/null absence, duplicate/overlapping paths, large inputs,
   depth/entry/node/read limits and inaccessible inputs; no partial successful result.
7. Engine raw drift, wrong HEAD/root/module origin, packed/detached/worktree refs,
   unavailable dependency, bytecode policy, unknown pin/closure and Git layouts.
8. Path length boundaries, root overlap, reparse/symlink/hardlink occupation,
   actual Windows filesystem behavior and writer's real operation/temp names.
9. Follow-on writer only: OS writer lock, exact apply, full durable before/after
   closure, interruption/recovery, original pin binding and RAM managed reconstruction.

Project config/data interpretation, M01 conversion, activation decisions, full
source reproduction, publication and downstream adoption remain separate work.
