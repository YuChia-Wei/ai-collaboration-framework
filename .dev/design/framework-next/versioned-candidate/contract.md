# Explicit distribution candidates and stable planning

Authority: [Issue #381](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/381), under #322 U001. This is unpublished assembly/reading, with no change to published legacy release tooling or target policy.

## Version and identity

Component versions retain exact MAJOR.MINOR.PATCH and independent values. Distribution labels accept only canonical MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-rc.N, with positive canonical N. ASCII numeric segments have no leading zeros except a single zero in the three base segments. Prefixes, build metadata, beta labels, whitespace, omitted/empty versions, booleans and numbers are refused. No general SemVer resolver/comparator is introduced.

| Invocation | Selection | Generator | Identity |
| --- | --- | --- | --- |
| Existing assemble / tools/build-development.py | schema 1, development, release_version null | framework-development-assembly | development:COMMIT:DIGEST |
| assemble_versioned / tools/build-candidate.py | schema 2, versioned, exact release_version | framework-versioned-assembly | versioned:VERSION:COMMIT:DIGEST |

The new API requires keyword release_version. The new CLI requires --repository, full --commit, --profile, --release-version, --output-root and --scratch-root. Invalid versions fail before source/output allocation. Nothing infers a version from date, branch, tag, profile or lock.

DIGEST is SHA-256 of canonical JSON mapping metadata/selection.json and metadata/files.json to their complete raw SHA-256 digests. Selection binds version, source commit/tree, components, profile, full input provenance, adapter outputs and generator implementation. Build schema 1 binds that identity and executing files and keeps installation/behavioral_validation/publication not-performed. Build time/run ID stay outside candidate identity. Stable-shaped labels do not establish publication.

Candidate and lock readers share the selection/inventory parser; filesystem and retained recovery metadata share _candidate_documents, and retained locks use _lock_bytes. Closed schema/mode/generator combinations preserve exact integer typing, canonical bytes, all hashes, ownership/path/link/reparse/hardlink/alias checks and budgets. Lock, inventory and build schema 1 remain unchanged. Helpers stay in existing pinned modules; no engine/bootstrap closure expansion or apply/recover changes.

## Complete profile

src/profiles/complete.yaml explicitly selects all 18 manifest components: lesson 0.2.0, the other 17 at 0.1.0, with Codex. It is a full independent selection, not an overlay, union or automatic expansion. Expected committed inventory is 113 payload members and 18 generated entries. Mismatch fails rather than revising expected inventory. Existing profiles retain their choices.

## Later rc.1 to stable input contract

The current rc candidate is not installed state. A separately authorized future installation would publish a lock embedding schema-2 rc.1 selection. A later caller supplies the following to existing API 1 plan via python -I -B <engine>/src/tools/maintain_framework.py:

- Explicit project_root and the freshly observed raw lock SHA-256 as expected_lock_sha256. Lock absence is a distinct first-install condition.
- A separately supplied stable candidate_root and exact versioned:VERSION:COMMIT:DIGEST identity. All bytes and explicit selection are checked. No automatic download, numeric ordering, compatibility/publication inference or implicit replacement.
- An explicitly selected immutable engine_root, its full current source commit and raw SHA-256 of every member in the existing complete engine closure. The bootstrap compiles verified bytes and verifies origins/closure. Candidate source, installed engine provenance and executing engine pin are distinct. A new engine needs its own pin; the distribution label never upgrades it.
- Existing mode policy, explicit scratch/staging/recovery roots, supported durability declaration, protected inputs and project_data_action none. Ownership, drift, markers, budgets and pin/hash gates remain effective.

Planning compares actual descriptors and exact candidate identity. If a new distribution label retains identical component/runtime bytes, all delta entries may be unchanged while the operation is not a no-op: a later authorized apply would publish the changed selection identity in the lock. Identical identity/inventory can be a no-op. Numeric increase or removal of rc does not authorize an upgrade. Unsupported schema or mismatched identity/hash/pin fails closed.

Project configuration, dotnet-mq-arch-lab customizations, .NET rules, legacy routes, data migration, quiescence, activation and target acceptance remain target-owned. Focused tests label manual rc locks and future stable metadata as fixtures. They establish selected reader/planning semantics, never actual stable release, successful target upgrade, native interruption/recovery or publication.
