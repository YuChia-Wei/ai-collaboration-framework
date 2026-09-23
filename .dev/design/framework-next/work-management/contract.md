# Work management selected implementation contract

Selected by the coordinator shared contract at 0d0556d4c60105a28eb39cfb06efab9b069728cb. Owned source is now implemented at src/skills/pr and src/skills/local-backlog; package references carry the complete portable contract. No runtime/schema acceptance is claimed. Original checkpoint 446a579d remains historical design evidence.

## 1. Independent packages and authority

| Surface | Owner / writer | Boundary |
| --- | --- | --- |
| PR instructions/schema/templates/tools | `pr@0.1.0` | Empty required and optional skill dependencies. |
| Local backlog instructions/schema/templates/tools | `local-backlog@0.1.0` | Empty required and optional skill dependencies. |
| Settings, constraints, records and custom templates | Project | Package replacement never migrates data or grants permissions. |
| Selected Git objects/diff | Project repository; tools read only | No branch, commit, fetch, push or checkout action. |
| GitHub PR | Provider, through authorized PR adapter operations | Local proposal is not a second provider-state authority. |
| Local work item | Selected local store | Online references do not become writable mirrors. |
| Authorization, capability observations, execution result | Runtime/caller | Saved config proves none of these. |

Neither skill requires workflow, ADR, Lesson, a source checkout, a private source policy or an online work-item reference. Links are data, not executable instructions.

## 2. Selected configuration v2 (WM-C1 / D-P3-01)

Keep P2 settings shape and precedence. Namespace `pr` defaults to `store: {kind: filesystem, root: notes/pull-requests, tracking: tracked}` and `template: {origin: package, path: templates/pr.md}`. Namespace `local-backlog` defaults to `notes/work-items` with the same store shape and `templates/work-item.md`.

Caller supplies absolute existing `project_root` / `package_root`, optional explicit `project_config` / `local_config`, selected-namespace `overrides`, and optional narrowing `write_roots`. Relative config filenames resolve against project root, never cwd. No ambient search, interpolation or credentials fields.

Resolution remains invocation > local > project > package defaults. Store leaves merge; template replaces atomically. Missing inherits; null, duplicate keys, non-finite values, wrong exact types and unknown selected fields fail. Project-only `constraints.<namespace>.write_roots` and `locked_fields` retain P2 semantics. Project/default roots before overrides establish bounds; overrides cannot expand them. Locks are store.root, store.tracking and template. Local config must already be ignored/untracked when inside a Git project.

**Selected decision:** config_version is exact integer 2. Project root keys are config_version plus optional skills/constraints; local root keys are config_version plus optional skills only. Validate all namespace IDs and object envelopes, then only the selected namespace deeply. Other namespace objects stay inert and do not prove capabilities or combine permissions. Unknown selected fields fail. Both selected files must be v2; absence selects defaults. Version 1 remains the closed P2 Lesson contract and is unsupported by these two skills. No registry or shared parser is introduced.

Metadata_version is 2. Each project role adds read_schemas containing exactly its single writable schema identity; all other closed metadata/resource shapes remain. Both packages retain version 0.1.0 and empty skill dependencies.

Static defaults need no provider field. A provider target is explicit operation input copied into a PR proposal when selected. No shared parser/helper extraction is proposed without owner allocation.

## 3. Local storage, records and results

Each record is a single UTF-8 JSON file with immutable UUID4-derived identity, schema_version 1.0.0, actual timezone-aware created_at/updated_at, owner project, strict owned fields and optional namespaced JSON extensions. IDs are store-scoped. Filename must match ID; updated_at cannot precede created_at. Preserve extensions on revision. Unknown versions are unsupported; migration/import/delete and automatic authority transfer are unsupported.

Only direct matching children of the selected store are read. Query returns ID-sorted matches, actual record SHA-256 and per-file errors with partial=true when necessary. A partial result cannot prove absence. Initial limits: 4 MiB request/record/diff, 10,000 selected record filenames; over-limit is unsupported rather than silent truncation.

Use P2 conservative path semantics: no links/reparse points, traversal, ambiguous/device/volume-root paths or overlap with package/config/template files. External stores require explicit project write roots and runtime permission. Create only parents inside both accepted project and caller roots; retain newly created empty directories on failure. Tracking is intent, not evidence of actual Git state and never authority to stage or change ignore rules. Changing bindings selects a collection; it does not move records. Durable logical references must retain their store binding separately.

Local writes support one cooperating writer per store. Exclusively create an invocation-token lock; reread target under lock; compare expected raw-byte SHA-256; serialize to a same-directory temporary file; exclusively publish new records or atomically replace the selected existing record. Recheck containment/identity before publishing. Clean only the invocation's verified temporary file and token-matching lock. P2's documented supported local filesystem set is the initial target, not tested certification. No claim covers uncoordinated external editors, shared/network backends, power-loss durability or automatic stale-lock recovery.

CLI shape: `python <absolute-entrypoint> --request <absolute-json-file|->`. One JSON request/result, common operation/roots/settings above. Result: `operation,outcome,mutation_state,diagnostics`, plus actual output references/digests. Outcomes: succeeded, invalid-input, unsupported, unavailable, blocked, conflict, failed. A dispatcher can report not-executed when nothing ran. Mutation state is none/committed/unknown. Failure does not prove rollback; preserve uncertainty and reread before retry.

| Shared operation | Additional input | Output / effect |
| --- | --- | --- |
| explain | None | Effective settings/provenance, roots/locks, capability not-probed; no write. |
| inspect | reference: {role,id} | Validated record and raw-byte digest; no write. |
| query | Optional literal text, default empty | Case-insensitive title/summary matches, digests and partial diagnostics; no write. |
| revise | reference, expected_sha256, complete authored content | Compare under lock; preserve identity/created time/extensions and skill-controlled fields; equal content is byte/time-preserving no-op. |
| render | reference | Inert Markdown result bound to real record/template digests; exporting is a separate caller write. |

Templates substitute once and escape authored plain text; no includes, code or recursive expansion. Unknown/malformed/missing required tokens fail. PR tokens: id,title,summary,subject,validation,references. Backlog tokens: id,title,summary,state,state_reason,acceptance,completion_evidence,references. Required sections cannot be hidden by a custom template. Rendered views are never authoritative input.

## 4. Local backlog

Schema `local-backlog.record@1.0.0`; filename `<id>.work-item.json`; ID `work-<32 lowercase UUID4 hex>`. Authored content: title,summary,acceptance,references and create-only extensions. Controlled state fields: state,state_reason,completion_evidence,writable_authority, plus identity/version/times.

Writable authority is exactly `local`. A GitHub Issue link has relationship `reference-only`, pointing to separately owned work rather than a synchronized duplicate. Remote-authoritative mirrors, online item writes, authority switching and two-way sync are unsupported. This source repository's GitHub authority is unaffected.

| Current state | Allowed next states | Required meaning |
| --- | --- | --- |
| New | draft via create | Candidate only; no implementation permission inferred. |
| draft | planned,cancelled | Real planning/withdrawal decision and nonblank reason. |
| planned | in_progress,blocked,cancelled | Actual start/obstacle/cancellation; planning is not execution authority. |
| in_progress | blocked,completed,cancelled | Completed requires nonempty evidence against acceptance criteria. |
| blocked | planned,in_progress,cancelled | Explain resolved obstacle/replanning; no direct completion. |
| completed,cancelled | None | Read-only terminal record in v1; correction/reopening needs a future operation. |

`create(content)` generates ID/times, local authority, draft state, reason "Created as candidate work.", empty completion_evidence, then exclusive publication. Query related work when deciding to create; no semantic dedup guarantee is implied.

`transition(reference,expected_sha256,expected_state,target_state,reason,completion_evidence)` checks digest/state/table under lock. Evidence is nonempty only for completed; otherwise it must be empty. Revise is limited to nonterminal records and never changes state. The tool checks structure/transition constraints; the project/caller decides whether actual evidence satisfies criteria. References are not fetched, dependencies are not scheduled and local completion never changes an Issue, Project or PR.

## 5. PR proposal and real diff binding

Schema `pr.record@1.0.0`; filename `<id>.pr.json`; ID `pr-<32 lowercase UUID4 hex>`; state always prepared. No authoritative published/merged flag is stored.

Authored content: title,summary,validation,references, optional provider_target, create-only extensions. Body is derived from these fields and selected template; no independent mutable body copy exists.

`prepare` requires absolute existing repository_root inside the project, explicit full base_commit/head_commit OIDs and content. Resolve commits without replacement refs or lazy fetch; select one unique merge base. Reject unrelated histories, multiple merge bases, missing objects and empty diff. Report dirty working-tree/index state; it is not included. No inferred HEAD, checkout or fetch.

Subject fields: object_format,base_commit,head_commit,merge_base,base_tree,head_tree,diff_sha256,git_version,diff_recipe. Recipe `pr.diff/v1` uses actual merge-base-to-head binary/full-index diff with no external diff, textconv, renames or color; fixed a/ and b/ prefixes, Myers algorithm, no indent heuristic, three context lines and zero inter-hunk context. Use explicit Git argument arrays, disable replacement/lazy fetch/prompt and sanitize ambient Git config/environment. Do not execute attributes-driven external programs. Record actual diff-byte SHA-256 and Git version; no cross-version canonicalization claim. If exact reproduction cannot be established, return conflict instead of refreshing the subject silently.

Use Git's documented `--attr-source=<selected-head>` so attributes come from the selected commit, not dirty worktree files; require a supporting Git version. Disable system/global attributes and config for the child process, bind core.attributesFile to the platform null device, and refuse nonempty repository info/attributes or unaccounted local diff-driver/config overrides rather than silently incorporating them. These are process-local controls, not edits to Git settings. The [Git command reference](https://git-scm.com/docs/git) and [attribute precedence](https://git-scm.com/docs/gitattributes) define those inputs. The implementation pins short submodule/no-relative output and rejects unaccounted local diff/include/promisor configuration; root status ignores nested submodule dirtiness. Summary remains authored content reviewed against the returned actual diff; the tool cannot prove semantic accuracy. New base/head or content scope requires a new prepare and evidence reconciliation. Controlled subject fields cannot be revised.

Validation entries contain id,command,disposition,subject_head,subject_diff_sha256,evidence,reason; IDs must be unique and head/diff must match the subject. Dispositions: planned,not-executed,succeeded,failed,blocked,deferred,not-applicable. Succeeded/failed require actual execution evidence references. Deferred reason names owner and next action. Caller supplies evidence; this skill checks binding/structure, not external evidence truth, and never executes checks. Rendering preserves every disposition/reason without deriving an overall green result. Empty validation means no execution evidence supplied. No copied success can satisfy a new subject.

Shared revise preserves subject; render returns record/template/body hashes and subject. A caller may prepare with empty validation, inspect actual subject, then revise with correctly bound evidence. Local rendering does not establish remote freshness.

## 6. One GitHub adapter

Package-owned `pr.github` at scripts/github.py is an explicitly declared tool entrypoint. It uses same-package `pr.fs` public inspect/render operations with explicit roots rather than private cross-skill imports. No helper field, separate tracker platform or credentials manager is introduced.

Initial boundary: GitHub.com, same-repository branches, existing Git and gh api. Forks/Enterprise are unsupported initially. Use explicit endpoint/method/host, bounded timeouts/response size, JSON stdin and argument arrays. Never log auth headers/tokens or invoke login/refresh/setup. Existing authenticated runtime capability requires caller authorization; static metadata and local config provide neither. Missing network/tool/auth/permission remains unavailable/blocked.

[GitHub PR API](https://docs.github.com/en/rest/pulls/pulls) supplies read/create/update endpoints; [gh api](https://cli.github.com/manual/gh_api) supports explicit methods and request input. Pin a documented API version at implementation time. Neither interface grants authority.

| Operation | Input and expected state | Permitted effect and read-back |
| --- | --- | --- |
| provider-read | Explicit {provider:github,host:github.com,repository:owner/name,number} | Fresh PR projection, observed_at and expected-state token. No local write. |
| provider-create | Record reference, expected record/template/body SHA-256 and scoped runtime grant reference; stored provider_target names repository,base_ref,head_ref | Read remote refs/unique merge base and match proposal; completely enumerate matching open PRs. Any match/incomplete pagination blocks create. POST title/body/head/base,draft=true only. GET returned PR and compare. |
| provider-update | Same local candidate/grant binding, selected number, expected provider token | Fresh open/unmerged target observation must match token and proposal subject. PATCH title/body only; GET and compare exact fields. |

Before write, recheck local candidate bytes and remote selection. Result reports actual PR number/URL, observation, selected head/diff binding and mutation state. Local record stays a proposal; provider result persistence is a separate caller-owned action.

Expected token is SHA-256 over UTF-8 sorted-key compact JSON of host,repository,number,state,draft,merged,title,body,base/head repository/ref/OID and updated_at. Observation time is excluded. Required fields cannot be dropped; only documented null body normalizes to empty text. Expected updatedAt alone is not equivalent. Post-write read-back must match requested title/body and selected branch identities; create additionally requires draft state.

The runtime grant reference binds actual caller permission to operation/target/body digest. A string or boolean cannot independently attest approval: runtime enforces permission before dispatch; tool checks consistency and reports the supplied reference without claiming authentication of human intent. Reuse existing authority when its scope still covers the candidate.

**Selected WM-C3 / D-P3-04:** preflight/post-read are optimistic observations, not atomic compare-and-swap. [GitHub conditional request guidance](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api#use-conditional-requests-if-appropriate) does not establish conditional PATCH support here. A concurrent writer can be overwritten between read/write without detectable post-read evidence. Require explicitly coordinated single-writer use; callers requiring server-enforced CAS receive unsupported. A caller declaration is not proof of actual exclusion or permission. Do not invent If-Match guarantees.

Timeout/lost response after dispatch returns failed/unknown with reconciliation action. Re-read selected PR or complete matching-create lookup before any new authorized attempt; no blind POST retry or automatic rollback. Successful response followed by mismatch/read failure remains committed/unknown as evidence permits, never succeeded. No distributed transaction joins local files and GitHub.

## 7. Authority and unsupported operations

| Action | Boundary |
| --- | --- |
| Local prepare/revise/create/transition | Requires scope for that local artifact; never implies provider permission. |
| Provider create/update | Requires exact operation/target/candidate authority; existing credentials only show capability. |
| Observed opened/updated PR | Does not complete local work or authorize integration. |
| Merge, PR close/reopen/ready/auto-merge, reviews, labels, assignees, Issue/Project mutation | Unsupported by this adapter. |
| Release/publication, branch push/delete, auth/config/credential changes | Unsupported; no inferred authority. |
| Conversion/import/sync, legacy backlog reactivation, arbitrary providers | Unsupported in this slice. |

Render references as Related. Block provider publication of authored Issue-closing directives; this adapter does not own closure. It cannot control unrelated repository automation and does not claim to. Runtime auth, static requirements and execution evidence remain separate throughout.
