# Lesson Configuration and Filesystem Binding, Version 1

Caller supplies absolute `project_root`, absolute resolved `package_root` and optional explicit `project_config` / `local_config` paths. Relative config filenames resolve against project root. No upward search, cwd inference, environment interpolation or source-repository fallback. Omitted source means absent; explicitly named missing source is an error. Local config is deliberately selected machine-local input; in a Git project it must be ignored before use. Do not edit ignore rules automatically. No secrets are expected or echoed. JSON input must reject duplicate keys and non-finite numeric values. Check the integer config version with exact type (a boolean is not version 1).

Project JSON has `config_version: 1`, optional `skills.lesson` and optional `constraints.lesson`. Local JSON has `config_version: 1` and optional `skills.lesson` only. Invocation overrides contain only the Lesson settings object. The first resolver supports only `lesson`; generalize namespace handling only with a second actual consumer.

| Setting | Type/default | Override unit |
| --- | --- | --- |
| `store.kind` | Literal `filesystem` | Fixed; another value is unsupported. |
| `store.root` | Nonempty path, `notes/lessons` | Scalar; relative to project root, not config directory. |
| `store.tracking` | `tracked` or `ignored`, default `tracked` | Scalar; diagnostics only, no Git mutation. |
| `template` | `{origin: package, path: templates/lesson.md}` | Atomic object; both keys required. Origin `package` or `project`. |

Ordinary values resolve **invocation > local > project > package defaults**. Absent fields inherit; explicit null, wrong types, unknown keys and partial template objects fail. Merge `store` by its three leaves, replace `template` atomically, never concatenate arrays.

Project constraints are separate from this override chain:

- `write_roots`: nonempty path array; relative entries resolve against project root. When omitted, allow only the store root selected by project settings plus defaults **before** local/invocation overrides. Caller authority may narrow this further. Overrides cannot expand permission.
- `locked_fields`: optional array from `store.root`, `store.tracking`, `template`; locks each effective project/default value. Differing overrides fail, not silently ignored. Same-value repetition is harmless.

Local/invocation input cannot supply constraints, replace versions or bypass actual user/runtime authority. Changing accepted constraints is a separate project edit; requesting another output location is not that edit.

Read-only `explain` returns values, winning source per field (`default`, `project`, `local`, `invocation`), normalized paths, locks, allowed roots and unsupported reasons. It creates no store and grants no writes. Static metadata cannot prove runtime capabilities.

## Filesystem roles and paths

Reference shape: `{role: lesson.record, id: lesson-<32 lowercase hex digits>}`. The caller also binds the store for this invocation. Resolve to `<store.root>/<id>.lesson.json`; identity is store-scoped, not a global registry. `lesson.view` is a rendering of the same record in the result. No record embeds the install root or source `.dev` layout.

Freeze resolved settings, template bytes and store at operation start; do not reread changed settings midway. Recheck canonical containment/permission before writing. For nonexistent paths resolve the nearest existing ancestor before appending validated segments. Symlinks/junctions/reparse points cannot escape authorized roots. Reject volume-root stores, ambiguous paths, unsafe IDs and overlap with installed package content, config files or templates. Package resources stay in package root; project templates stay in project root. External templates are unsupported initially.

An absolute/external store needs an explicit project `write_roots` entry containing it and actual caller permission. Reject relative paths escaping project root; use explicit absolute external bindings. No disk discovery or fallback. Fail unwritable stores before material output. Durable records never silently become scratch/cache. Volatile external storage requires a project durability decision; this tool does not provision backups.

Read only direct `*.lesson.json` children of the selected root. Missing store is empty for query and may be created by authorized create. Malformed/unknown-version records produce per-file diagnostics and an explicitly partial query result, never a complete empty result. No index is needed.

Changing the binding selects another collection; it does not move records, change tracking or relocate references. A durable caller persisting a logical reference must persist its store binding too. Migration is separate; an active invocation retains its original binding.

## Initial implementation limits

`scripts/lesson.py` rejects all selected symlinks, junctions and reparse points,
including links whose current target is inside a root. It rejects `..` segments,
drive-relative/device/UNC paths and ambiguous Windows filenames. Package and
project roots must already exist. Resources are checked against their declared
package root; the running executable must belong to the selected package.
Absolute project-template paths are allowed only inside the explicit project.
Package templates must identify a declared template resource.

Create can provision the missing store directory and missing parents only when
each directory lies within project write roots and any caller restriction.
With the default `notes/lessons` constraint, provision `notes` separately first;
or the project can explicitly allow `notes` to permit both directories. The tool
does not expand the default bound just because a parent is absent. Created empty
directories remain on failure and are listed in the result; cleanup never
recursively deletes them. A frozen existing store directory must retain its
filesystem identity for the operation.

Git is needed only when a selected local config belongs to a Git project. The
tool performs read-only `rev-parse --show-toplevel` and `check-ignore -q` calls,
with timeouts, to require an ignored, untracked local config inside that project.
Git-related ambient variables are excluded from these calls. A missing Git
executable yields `unavailable`; inability to establish ignored state yields
`blocked`. No local config means no Git subprocess. Files outside a Git project
do not need Git. This conditional capability is part of the filesystem/local
configuration requirement, not a mandatory skill dependency.

Explain returns `unsupported_reasons: []` only after input binding succeeds;
binding/config failures return a normal unsuccessful result with diagnostics.
`runtime_capability: not-probed` means it has not attempted publication or tested
the filesystem. It does not create a store or establish write availability.

The declaration's `implemented` state means source exists. Actual runtime,
filesystem, crash and concurrency behavior still requires execution evidence;
neither metadata nor this document supplies it.
