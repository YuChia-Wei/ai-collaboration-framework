# Proposed formats and exact shapes

Design only. [examples.json](examples.json) uses synthetic values, not candidate evidence, runnable fixtures or installed state. No schema validator/product operation executed.

## Encoding and actual candidate 1

Use existing `distribution.data.json_bytes`: UTF-8 without BOM, ensure_ascii=False, sorted keys, indent 2, no NaN, one final LF. SHA-256 hashes raw bytes. Git OID is distinct. Future readers require closed keys, duplicate rejection, strict Unicode, bounded depth/size and exact types. Integer versions reject bool/float. Digest is not authority.

Current selection fields: `schema_version`, `mode`, `release_version`, `source:{commit,tree}`, `profile`, `components:[{id,version,metadata_version,members,required_dependencies,optional_dependencies}]`, `adapters:[{id,package,template,installed_entrypoint,entrypoint_source,output}]`, `build_inputs:[SourceIdentity]`, `generator:{id,implementation:[SourceIdentity]}`.

`SourceIdentity = {path,git_blob,mode,size,sha256}`. `Member = {path,destination,owner,kind,mode,size,sha256,source?}`. Path is `payload/<destination>` or `runtime/<destination>`; kind matches. Payload owner is package ID, source required. Runtime owner is `codex/<id>`, source omitted, mode 100644. Files document is `{schema_version:1,files:[Member]}`. Source mode is 100644 or 100755.

Build fields: `schema_version`, `outcome`, `run_id`, `completed_at`, `candidate_identity`, `candidate_sha256`, `identity_inputs`, `source_commit`, `profile`, `runtime:{python,pyyaml,os}`, `executing_implementation:[{source:SourceIdentity,execution_file_sha256}]`, `mode_materialization`, `installation`, `behavioral_validation`, `publication`. Last three are not-performed. This is build completion, not installation approval.

Identity-input keys are exactly metadata/selection.json and metadata/files.json with raw SHA-256 values. Candidate digest hashes canonical JSON of that map; identity is `development:<full-commit>:<digest>`. Revalidate all source/profile/member/adapter bindings. Require canonical metadata bytes for lossless embedding in lock. Time/run/host do not enter content identity. Consume shared loader's actual version handling; never reproduce metadata parsing in installer. Metadata-v3 support waits for #346 delivered source and explicit adapter/entry selection.

## Lock 1

`.ai/framework.lock` fields are exactly:

| Field | Meaning |
| --- | --- |
| lock_version | Integer 1. |
| installation_id | Stable 32 lowercase hex ID created at first install; retained on update; not authentication. |
| engine | `{id:"framework-managed-installation",version:"1.0.0"}`. |
| mode_policy | posix-permissions or windows-inventory-only. |
| candidate_identity | Exact development content identity. |
| selection | Complete unchanged parsed candidate selection document v1. |
| inventory | Complete unchanged parsed candidate files document v1. |

Canonical re-encoding reproduces candidate metadata hashes/identity. No second component/schema/adapter registry. Raw lock hash is external, never self-referential. Inventory excludes lock/markers/guard/project files. Actual read-back is needed: lock alone does not prove installation. No status/time/host path/config contents/token/receipt/cached pass. Unknown lock version is unsupported; no lock migration edge in v1. Missing lock grants no existing-file ownership. Tracked installation needs explicit project attributes to preserve raw bytes/modes; CRLF/filter drift on clone is a real conflict.

## Package operation 1

Durable `<recovery_root>/i-<id>/operation.json` and target `.ai/framework.operation` use IDENTICAL bytes and one format. Immutable, written after complete object closure. Marker deletion ends activation; no phase journal.

| Field | Meaning |
| --- | --- |
| operation_version, operation_id | Integer 1 and exclusive 32-hex directory ID. |
| engine, installation_id | Same exact engine and old/new lock installation ID. |
| project_root | Explicit canonical absolute root, local locator, never portable payload/committed lock. |
| operation_root | Exact durable operation directory, matching caller selection. |
| durability | `{declared_by,declaration_reference,failure_domain}`; owner assertion, not automatic proof. |
| plan_sha256 | Accepted transient plan hash including before/after and readiness selection. |
| before_lock_sha256 | Raw old lock object hash, null for uninstalled. |
| after_lock_sha256 | Raw new lock object hash. |
| candidate_metadata | Three exact metadata/*.json names mapped to raw object hashes. Build completion stays separate from lock identity. |
| protected_inputs | `{path,sha256}` rows; null sha means selected absent path. Read/compare only, exact inputs from selected owner, not repository discovery. |
| compatibility | `{owner,selection_reference,selection_sha256}` binds selected compatibility contract, not a pass or generic converter. Actual result rechecked. |
| project_data_action | Exactly none. |

Objects use exclusive `objects/<sha256>` raw bytes. Required closure: old/new locks, every old/new inventory byte object, all three actual candidate metadata documents. Equal bytes deduplicate inside operation. Mode comes from lock, not backup filesystem. No config/data bytes copied by package engine. Read back complete closure before marker; missing correspondence blocks recovery. Do not duplicate inventory/phase arrays or embed logs.

Local paths in operation require project-owned ignore/access choices; diagnostics redact absolute paths. Exact complete durable record plus explicit current-state selection can recover a damaged marker. Malformed durable record is inadmissible. No migration to a different engine/version is implied.

## Conditional M01 state 1

M01 is a separate transaction, not a package operation. Propose one small record only when actual conversion is selected; no additional progress journal or success receipt. Future sole producer/reader/validator is coordinator-assigned config-transition implementer, agreed with Lesson/v2 config owners. This is a proposed recovery shape, not a competing configuration format.

Durable `<recovery_root>/m01-<id>/operation.json` and local `.ai/config-transition.operation` are identical immutable bytes. Objects contain only selected exact config before/after bytes. Fields:

- `transition_version:1`, `operation_id` (32 hex), `engine:{id:"framework-config-transition",version:"1.0.0"}`.
- `edge:"p2-json-config-1-to-2"`, `project_root`, `operation_root`, `durability` with same meanings as above.
- `plan_sha256`, `targets:[{role,path,before_sha256,after_sha256}]` with exactly one project row and optionally one local row. Paths unique, explicit and contained/authorized; before/after objects required. No unrelated files.
- `consumer_selection:{reference,sha256}`: exact selected consumers and conditional need, not a fabricated compatible result.

The config owner parses actual closed input semantics, generates after bytes differing only in exact integer version, then records hashes. Pairs remain non-atomic. Marker exists before first replacement; guard refuses either marker. Native coordination excludes overlapping package/config transitions. Complete pair and current selected reader checks precede marker removal; old incompatible readers remain inactive. State inference uses before/after hashes. External edits/missing durable bytes block finish/restore.

M01 API is version 1, separate `plan`, `convert`, `recover`. Plan requires exact project/local files, expected hashes, selected consumers, explicit scratch/durable roots and `intent=convert|restore-snapshot`. Convert consumes exact accepted plan. Interrupted recover needs explicit operation directory/hash, current expected file/marker hashes and finish/restore direction. Once completed, old record is read-only recovery evidence; later restore requires a NEW plan and full files still equal original after bytes plus current reader/data compatibility. Never reverse edited v2 by integer replacement. No reverse edge is promised; snapshot restoration cannot lose later semantics. Coordinator must select the exact facade/path and closed API detail variants before implementation; no generic schema conversion framework.

## API 1 package requests and plan

All requests: api_version 1, operation, project_root. Inspect adds optional candidate_root. Plan/apply add candidate_root, candidate_identity, expected_lock_sha256 (null absent), mode_policy, scratch_root, staging_root, recovery_root (parent), durability, project_config_paths, compatibility, project_data_action none. Apply adds expected_plan_sha256. Recover adds operation_root, operation_sha256, direction, expected_lock_sha256, expected_marker_sha256 (null absent), reconstruct_missing_managed (false default). Valid unrelated control records cannot be overwritten by supplying their hash. Guarded-invoke adds skill_id, tool_id, skill_operation, arguments under selected package public contract; no arbitrary executable. This initial tool-only shape requires explicit extension for v3 instruction operations, not a fake tool_id.

Plan has exactly: api_version, operation=plan, project_root, candidate_identity, engine, expected_lock_sha256, mode_policy, roots, durability, compatibility, project_data_action, protected_inputs, delta, preserved_unknown, path_budget, prerequisites. Roots contains candidate/scratch/staging/recovery absolute paths. Delta rows: `{destination,action,before,after}`; descriptors null or `{sha256,size,mode,owner,kind}`. Sort by stable path/ID; no UUID/time/ambient host inventory in hash. Prerequisites `{id,status,owner,next_action}`; unresolved blocks apply. Path budget records selected backend/budgets and relative-role measurements, not a support certification.

Plan result: `{api_version:1,operation:"plan",outcome:"planned",plan,plan_sha256}`. Common result: `{api_version,operation,outcome,changed,details,diagnostics}`. Diagnostics `{code,path,reason,next_action}` use relative path/null. Details are operation-specific: inspection state/inventory; apply/recover actual lock hash, counts, retained locator; guarded invocation actual package result. Implementation must select CLOSED detail variants before shipping, not arbitrary extra fields. No fabricated counts; partial change remains partial. These are transient API outputs, not more persistent product-state formats.

Synthetic examples instantiate new shapes and delta/request rows. Hashes/declarations/source are deliberately artificial and arrays demonstrate shape, not complete actual Lesson selection. They cannot pass product semantic admission and must never be sent to an installer. Direct JSON parsing here proves syntax only.

## Format accountability

| Format/version | Producer | Reader/validator owner | Version/migration owner |
| --- | --- | --- | --- |
| Manifest/profile 1 | Source selection owner | Existing distribution selection | Coordinator; no installer rewrite. |
| Package metadata 1/2, selected future 3 | Capability owner | #346/shared loader and capability owner | P5/coordinator; preserve v1/v2. |
| Candidate documents 1 | Existing assembly | Distribution candidate reader; P7 exercises | Distribution; initially v1 only. |
| Lock 1 | Installer after actual apply | installation_state reader + actual files/guard | Distribution; no migration edge. |
| Package operation 1 / marker | Apply | Same state reader, durable closure/current state | Distribution; exact same engine. |
| M01 state 1 / marker | Separate config-transition owner | Same owner + real config readers | Config-transition owner; sole selected 1->2 edge, no state-version migration. |
| API 1 plan/request/result | Caller/facade | Operation-specific product facade | Respective installer/config owner; transient. |
| SHA objects / inert guard | Apply/converter / native backend | Hash/containment / native held lock | No additional record schema or registry. |
| Config/record versions | Project/capability owner | Selected actual public readers/validators | Owner; M01 only where selected/needed. |

No product schema is created here. Later schemas live beside their state owner, not in a new global registry. Workflow JSON/YAML uses proportionately adapted existing source templates; not a new installed format. Required shared loader/adapter changes remain coordinator-owned. This design adds no mandatory shared runtime to independent skills.
