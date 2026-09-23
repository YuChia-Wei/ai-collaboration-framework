# Proposed formats and exact shapes

Design only. [examples.json](examples.json) uses synthetic values, not candidate evidence, runnable fixtures or installed state. No schema validator/product operation executed.

## Encoding and actual candidate 1

Use existing `distribution.data.json_bytes`: UTF-8 without BOM, ensure_ascii=False, sorted keys, indent 2, no NaN, one final LF. SHA-256 hashes raw bytes. Git OID is distinct. Future readers require closed keys, duplicate rejection, strict Unicode, bounded depth/size and exact types. Integer versions reject bool/float. Digest is not authority.

Current selection fields: `schema_version`, `mode`, `release_version`, `source:{commit,tree}`, `profile`, `components:[{id,version,metadata_version,members,required_dependencies,optional_dependencies}]`, `adapters:[{id,package,template,installed_entrypoint,entrypoint_source,output}]`, `build_inputs:[SourceIdentity]`, `generator:{id,implementation:[SourceIdentity]}`.

`SourceIdentity = {path,git_blob,mode,size,sha256}`. `Member = {path,destination,owner,kind,mode,size,sha256,source?}`. Path is `payload/<destination>` or `runtime/<destination>`; kind matches. Payload owner is package ID, source required. Runtime owner is `codex/<id>`, source omitted, mode 100644. Files document is `{schema_version:1,files:[Member]}`. Source mode is 100644 or 100755.

Build fields: `schema_version`, `outcome`, `run_id`, `completed_at`, `candidate_identity`, `candidate_sha256`, `identity_inputs`, `source_commit`, `profile`, `runtime:{python,pyyaml,os}`, `executing_implementation:[{source:SourceIdentity,execution_file_sha256}]`, `mode_materialization`, `installation`, `behavioral_validation`, `publication`. Last three are not-performed. This is build completion, not installation approval.

Identity-input keys are exactly metadata/selection.json and metadata/files.json with raw SHA-256 values. Candidate digest hashes canonical JSON of that map; identity is `development:<full-commit>:<digest>`. Revalidate all source/profile/member/adapter bindings. Require canonical metadata bytes for lossless embedding in lock. Time/run/host do not enter content identity. Consume shared loader's actual version handling; never reproduce metadata parsing in installer. Metadata-v3 support consumes #346 actual delivered loader/adapter source; no invocation launcher is part of this installation API.

## EnginePin and explicit maintenance declaration

`EnginePin` has exactly `{id,version,source_commit,files}`. ID is framework-managed-installation (or framework-config-transition for M01), version is proposed 1.0.0, source_commit is full lowercase 40/64-hex Git commit, and files is a nonempty path-sorted array `{path,sha256}` of every required implementation file. Paths are exact source-checkout-relative regular files, no traversal/glob; hashes are raw execution bytes. Actual complete dependency closure belongs to the implementation owner. No abbreviated refs, version-only substitution or file list guessed from this example.

Every operation supplies `engine_root` explicitly outside modified project and managed/recovery/candidate/disposable roots; it is not written into tracked lock. The running engine verifies fixed checkout commit and exact executing file set/hashes. Recovery pin equals the original operation's pin in full. Exact bootstrap entry/verification, interpreter dependencies and future package delivery must be selected during implementation; no product release is implied.

`MaintenanceDeclaration` has exactly `{declared_by,declaration_reference,affected_capabilities,sessions_stopped,tools_stopped,external_writers_stopped}`. Last three must be exact true; affected_capabilities is the sorted exact scope computed for this operation. Presence and scope can be checked; stopping activity cannot be proven by the engine. Declaration is the caller's assertion, not a lease or attestation. Apply/convert/recover require a fresh explicit declaration; a retained prior assertion is not reused as current permission. Plans can be produced before quiescence and are recomputed before mutation.

## Lock 1

`.ai/framework.lock` fields exactly: lock_version (integer 1), installation_id (stable 32 lowercase hex), engine (EnginePin), mode_policy (posix-permissions or windows-inventory-only), candidate_identity, selection (complete unchanged candidate selection v1 object), inventory (complete unchanged files v1 object).

Canonical re-encoding reproduces candidate digests/identity. Raw lock hash is external, not self-referential. No duplicate component/adapter/schema registry, runtime activity status, readiness/compatibility pass, timestamp, host path or config content. Inventory excludes markers/guard/project data. Actual bytes must be read back. Unknown lock version is unsupported; no v1 migration edge. A missing lock gives no existing-file ownership. Project attributes must preserve exact tracked bytes/modes across clone; drift is not normalized away.

## Package operation 1

Durable `<recovery_root>/i-<id>/operation.json` and `.ai/framework.operation` are identical immutable bytes. Marker means incomplete maintenance and no owner activation; it cannot block arbitrary readers. Removing it completes only the managed operation.

| Field | Meaning |
| --- | --- |
| operation_version, operation_id | Integer 1; exclusive 32-hex directory ID. |
| engine, installation_id | Exact EnginePin and old/new installation ID. |
| project_root, operation_root | Explicit canonical absolute project/durable directory, local locators. |
| durability | `{declared_by,declaration_reference,failure_domain}`; caller assertion, not inferred durability. |
| maintenance | Original MaintenanceDeclaration for this operation; recover requires a fresh one too. |
| plan_sha256 | Accepted exact transient plan hash. |
| before_lock_sha256, after_lock_sha256 | Raw durable lock hashes; before may be null for clean install. |
| candidate_metadata | Exactly metadata/selection.json, files.json, build.json names -> raw hashes. |
| protected_inputs | Finite caller-selected `{path,sha256}` rows; null sha explicitly means absent. No semantics, directory inventory or implicit config discovery. |
| project_data_action | Exactly none. |

Required `objects/<sha256>` closure: old/new locks, every old/new managed file, all three candidate metadata documents. Deduplicate inside operation, preserve exact bytes; modes come from lock, not backup filesystem. No project config/records copied. Complete read-back precedes marker. Missing objects/state correspondence blocks managed recovery. No duplicated inventory, mutable phase counter or log/receipt.

Local locators need project-owned ignore/access treatment; diagnostics avoid leaking absolute paths. Malformed durable record never authorizes recovery. Supplied hash does not authorize overwriting an unrelated valid marker/installation. Unavailable original EnginePin blocks recovery, even if a newer engine has the same advertised version.

## Conditional M01 state 1

Only actual-needed separate config conversion creates this record. Sole producer/reader/validator: assigned P6 config-transition implementer in agreement with Lesson/v2 config owners. Durable `<recovery_root>/m01-<id>/operation.json` and `.ai/config-transition.operation` are identical. Objects contain only explicit config before/after bytes. Fields exactly:

- transition_version 1, operation_id, engine (framework-config-transition EnginePin).
- edge p2-json-config-1-to-2, project_root, operation_root, durability, maintenance.
- plan_sha256; targets array `{role,path,before_sha256,after_sha256}`, one project and optional one local row, distinct explicit authorized paths.
- consumer_selection `{reference,sha256}`: project-selected actual need/consumers, not compatibility result or registry.

Config owner validates the closed P2 semantics and output integer 2 preserving all other values/absence. Pair is not atomic. Native maintenance lock excludes participating package/config writers; caller stops readers/writers. Marker records incompleteness, not reader enforcement. Complete pair/raw hash/selected conversion invariants precede marker removal; mechanical outcome does not establish project readiness. External concurrent writers unsupported; hash checks do not remove TOCTOU.

Separate API 1 plan/convert/recover. Plan requires exact files/hashes, actual consumer need, EnginePin/engine_root, explicit scratch/durable roots and intent convert|restore-snapshot. Convert consumes accepted plan plus fresh maintenance declaration. Recovery requires exact record/hash, same engine pin/root, current expected file/marker hashes, fresh declaration and finish/restore direction. After completion, later snapshot restore requires a NEW plan and exact after bytes; never integer-reverse modified v2 content. Project separately checks reader/data suitability before activation. Exact facade/detail variants remain implementation selection; no generic schema/conversion plugin framework.

## Package API 1 request and transient plan

Common request fields: api_version 1, operation, project_root, engine_root, engine (EnginePin). Four operations only:

| Operation | Other closed request fields |
| --- | --- |
| inspect | Optional candidate_root. |
| plan | candidate_root, candidate_identity, expected_lock_sha256 (null absent), mode_policy, scratch_root, staging_root, recovery_root (parent), durability, protected_inputs (empty allowed), project_data_action none. |
| apply | All plan fields, expected_plan_sha256, maintenance. |
| recover | operation_root, operation_sha256, direction finish|restore, expected_lock_sha256, expected_marker_sha256 (null absent), reconstruct_missing_managed (default false), maintenance. |

No skill/tool invocation, project_config_paths, compatibility object, generic scanner or plugin selection in these requests. Protected-input paths are individually caller-selected; values/hash/null checked only, never read as config/record meaning. Apply requires current matches; explicit whole-loss managed reconstruction may disclose missing protected inputs while restoring managed bytes only.

Plan fields exactly: api_version, operation=plan, project_root, candidate_identity, engine, expected_lock_sha256, mode_policy, roots (engine/candidate/scratch/staging/recovery), durability, project_data_action, protected_inputs, maintenance_scope, delta, preserved_unknown, path_budget, prerequisites. Maintenance_scope is sorted union of old/new selected capability IDs. Delta `{destination,action,before,after}`; descriptors null or `{sha256,size,mode,owner,kind}`. Stable sorted arrays; no UUID/time in plan hash. Prerequisites `{id,status,owner,next_action}` refer only to maintenance mechanics/input/durability prerequisites, never data compatibility. Pending mechanical prerequisites block apply. Path budget describes refusal limits, not OS certification.

Successful plan result exactly `{api_version:1,operation:"plan",outcome:"planned",plan,plan_sha256}`. Outcome sets are closed: inspect inspected|unsupported|blocked; plan planned|conflict|unsupported|blocked; apply applied|unchanged|conflict|unsupported|blocked|recovery-needed; recover recovered|already-matching|conflict|unsupported|blocked|recovery-needed. Common other result `{api_version,operation,outcome,changed,details,diagnostics}`. Diagnostic `{code,path,reason,next_action}` uses relative path/null. A failed plan uses the common result with details=null. Each other details variant is closed:

- Inspect: `{managed_state,project_readiness,owned,unknown,drift,mode_policy}`; project_readiness always not-assessed. Owned uses candidate Member shape; unknown is relative paths; drift rows `{path,reason}`. Unavailable values use null rather than fabricated inventory.
- Apply/recover: `{managed_state,project_readiness,lock_sha256,operation_root,counts,protected_input_state}`. Project_readiness always not-assessed; counts `{added,changed,removed,unchanged}` are actual and may be null when not established. Protected_input_state matches|unresolved|conflict|not-selected, a byte observation only. Managed_state uninstalled|managed-bytes-consistent|drift|recovery-needed|unsupported|blocked. On error, retain truthful partial changed/counts and locators.

Applied/unchanged/recovered do not authorize enabling a capability. Missing project data after RAM loss can coexist with managed-bytes-consistent but never whole-project-ready. Project chooses its public reader checks separately; unknown compatibility remains unknown, not a passed field. No persisted pass receipt or stateful readiness plugin is introduced.

Synthetic examples have artificial hashes/source/declarations and incomplete illustrative candidate membership. They are not runnable fixtures or real admission evidence. Direct JSON parsing proves syntax only. Historical checkpoint examples used a different proposal; only this revised shape is current and none has been implemented/published.

## Accountability

| Format | Producer | Reader/validator owner | Version/migration owner |
| --- | --- | --- | --- |
| Manifest/profile 1 | Source selection owner | Existing distribution selection | Coordinator; no installer rewrite. |
| Package metadata 1/2, selected future 3 | Capability owner | #346/shared loader | P5/coordinator, v1/v2 preserved. |
| Candidate documents 1 | Existing assembly | Distribution candidate reader | Distribution, actual versions only. |
| EnginePin / maintenance assertion | Explicit caller/implementation owner | Maintenance facade verifies identity/scope, not stopped activity | Same maintenance owner; embedded shapes, no separate files. |
| Lock 1 | Installer after actual publication | Installation-state reader + actual file checks | Distribution; no migration edge. |
| Package operation 1 / marker | Apply | Recovery/state reader + durable/current checks | Distribution, same complete engine pin. |
| M01 state 1 / marker | Separate converter | Its state and actual selected config readers | Config-transition owner, sole 1->2 edge. |
| API 1 | Caller/facade | Operation-specific facade | Corresponding maintenance owner; transient. |
| SHA objects / guard file | Maintenance writer / native backend | Hash/containment / OS-held writer lock | No extra record schema/lease. |
| Project config/records and activation decision | Project/capability owners | Separately selected public readers | Those owners, not package installer. |

No schema/source implementation here. Later state schemas belong beside their owners; no global registry, ordinary-invocation runtime or generic compatibility system. Source workflow JSON/YAML remains proportionately adapted existing workflow state.
