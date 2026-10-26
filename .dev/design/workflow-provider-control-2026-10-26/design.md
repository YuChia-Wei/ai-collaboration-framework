# Workflow local groups and project provider controls

Date: 2026-10-26. Basis: [requirements](../../requirement/workflow-provider-control-2026-10-26/requirement.md), current #520/#513 and inspected source commit `bf7269cfa1afdded005fb4c2e500834fdcb38746`. This is the selected implementation design, not a test result.

## Compatibility and ownership

Add `workflow-records/local-group/1` through `tools/local-group.py`. Existing `workflow-records/1`, `source-store/1`, `source-store/2`, Git formats, native SQLite schemas and Board APIs remain compatible. A new group owns one logical workflow and fresh storage. Legacy native writers must reject its distinct SQLite schema. Do not silently attach or migrate an existing native database.

The new modules belong to `src/skills/workflow-records/tools/workflow_records/`; metadata declares their complete runtime closure. Project provider code and settings stay outside `.ai/core`, installed runtime directories and framework packages. No ambient imports, directory scans, automatic plugin discovery, credentials or network clients are added.

## Single authority and local persistence

An explicit locator config identifies group/project/workflow identity and a persistent control directory. Initialization defaults to a Local file member; SQLite is optional. Persist member identity, immutable generation, physical location, authority epoch, configuration revision and selected authority in control state. The locator is not an editable authority switch.

Use one stable OS advisory lock for every group read, mutation, sync and administrative operation. Windows uses a real OS lock released on process exit; a sentinel's existence is not ownership. Canonicalize paths, reject overlap/symlink escape and unsafe relative document paths. Supported entrypoints enforce the lock; arbitrary filesystem/SQL modification remains outside that guarantee and detected drift fails closed.

Each carrier holds a versioned complete local envelope containing workflow metadata/tasks/documents/attachments, immutable command receipts and fixed synchronization intents. Local file stores ordinary bounded UTF-8 JSON with binary bytes explicitly base64 encoded; it is an ongoing file carrier, not an archive import. SQLite stores an equivalent versioned envelope in a distinct schema. Structured extensions and original document/attachment bytes are preserved.

The smallest atomic file commit is a flushed temporary envelope plus same-directory atomic replacement. SQLite uses one transaction and head CAS. The selected carrier's commit includes accepted command, canonical request digest, logical revision, immutable resulting payload and fixed target generations with initial pending states. No replica dispatch precedes that commit. A bounded envelope limit is checked before mutation; exceeding it reports a limit instead of truncating history. The implementation may partition immutable cuts/blobs if necessary, but must preserve the same commit boundary.

Control state owns configuration/authority only; it is not a second workflow-data authority. Administrative operations use a durable transition record and recoverable final control replacement. Reconcile an unfinished transition before admitting later operations. Configuration mutation must not silently overwrite concurrent state. No local carrier is promoted because another is unavailable.

## Public operations and synchronization

Provide explicit initialize/configuration/context/read/resume/create/task/checkpoint/revise/document operations, operation lookup, local synchronization/status, membership configuration and authority selection. Every mutation has a stable operation ID and semantic request digest. Identical replay returns the original result before ordinary stale-CAS checks; a changed request under the same ID conflicts. Requests identify the complete group, expected configuration revision, authority epoch and current logical revision as applicable.

Reduce a workflow command once, preserving extensions, and serialize its content once. Local synchronization applies the persisted content to the original target generation in order. It checks expected parent and identity, never re-runs the reducer or invents a new operation ID. A replica conflict, outage or interrupted delivery remains pending/unknown with a bounded retry count. Read original receipts after a lost response. Report local acceptance separately from synchronization completion; never claim cross-carrier rollback.

Adding a fresh member records an explicit baseline transfer. Membership changes affect future commands and retain earlier fixed targets. Authority selection requires no unresolved transition and both active members at the same complete current cut, including byte integrity and operation closure. It increments authority epoch and configuration revision under the same lock; stale requests cannot write after the switch. Selected-authority reads do not fall back.

## Project remote provider control

Use a separate versioned `workflow-records/provider-control/1` contract exposed by the group CLI. A project supplies an explicit registration candidate with provider ID, implementation reference/version, protocol version, project/scope, non-secret settings or settings-file reference and declared capabilities. No provider process is launched by this increment. Framework code neither imports the implementation nor validates its backend-specific settings semantics.

Register/update creates an immutable disabled generation in the selected local authority. Inspect/list return identity, declared capabilities, settings digest, enabled state and configuration revision, explicitly marking backend verification unavailable. Enable/disable use CAS and stable control operation identities. Enabling is an explicit selection for future handoffs, not a backend readiness claim. Multiple registrations remain distinct; replacements never retarget earlier operations.

The generic extension boundary is a host-mediated adapter port: prepare produces a bounded immutable versioned request for an explicitly selected enabled generation; downstream host code executes its own implementation and supplies an observation. The request carries complete project/workflow/provider/binding identity, generation, capability, operation ID, digest, expected provider revision and persisted payload. Observe validates the matching envelope/scope/digest and records accepted/rejected/conflict/unknown separately from local acceptance. Unknown outcomes require lookup/reconciliation using the original identity, not silent replay through another provider. No automatic remote dispatch is added.

Provider generations snapshot bounded canonical non-secret settings at registration,
including settings-file inputs, and retain the original digest/content. Provider
configuration has its own event-owned revision in the selected carrier; membership
and authority revision remain control-owned. A fixed target pins its predecessor
intent. First prepare resolves the predecessor's accepted opaque provider revision
and persists the exact command. Observations echo the local logical cut separately
from the opaque provider revision and are host-correlated assertions, not backend
attestation. Repeated prepare/lookup preserves the original command/digest.

Failed local delivery attempts retain bounded unknown/conflict observations in the
authority. A dispatch limit never prevents status/remote lookup. Explicit CAS
`group-resume-intent` adds a bounded dispatch budget and authorizes that original
intent without changing its identity, payload or target. It may resume a retained
disabled generation without enabling that generation for future commands.

Remote bindings are explicit replica targets in this local-authority contract. Generic provider descriptors do not hardcode a remote vendor; remote command authority is not enabled by a capability declaration. A future remote-authority contract would require its own accepted transfer semantics. Workflow Board remains the existing supplied experimental adapter; its DTOs are not silently relabeled as this new generic port.

Only framework envelope/schema/configuration and handoff behavior is tested. Non-network prescribed observations may exercise the control contract. Downstream adapter implementations, network calls, credentials, remote persistence and provider behavior are neither implemented nor verified here.

## Complete recovery

Export under the group lock includes control identity/history, all member envelopes, command/control receipts, fixed intents, payloads and observations. Preflight validates bounds, closed identities and content hashes. Restore targets fresh paths and is inactive with a new instance identity; it performs no remote calls. Explicit deactivation and single-successor activation prevent a supported API from activating multiple restores. If an original store is unavailable, fail closed rather than claiming a transfer. Native SQLite-only backup is not substituted for complete-group backup.

## Validation

The changes affect persistence, authority, recovery and runtime closure; focused tests are necessary. Exercise actual public CLI file-only behavior, both authority choices and switch directions, byte preservation, stale CAS/epoch, operation replay, ordered interrupted sync, corruption/divergence, selected-authority outage, process concurrency/lock release, complete inactive restore, old-native rejection and unchanged legacy compatibility. Luna subagents run independent local scenarios with synthetic data. A fixed-commit independent review examines the authority and recovery boundaries. Physical power-loss guarantees and real remote backend acceptance remain unverified.
