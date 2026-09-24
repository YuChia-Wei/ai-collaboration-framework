# RC2 S1 selection contract workflow

- Workflow: `2026-09-24-rc2-selection-contract`.
- Owner: `ai-context-governance`; Issue [#401](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/401), program [#322](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/322).
- Baseline: `6f5a13046f1978ba4b8701e4ae772faecde2c2ff`; branch `codex/2026-09-24-rc2-selection-contract`.
- Scope: exact S1 contracts, complete bounded migration/capability inventories and dependent handoff.
- Execution: U001; one S1 document writer. Model/effort template metadata is declared dispatch information, not independent runtime attestation. Local assignment details remain ignored.

The owner authorized the selected S1 direction and continuation. The live Issue
was read and matched the assigned A1–A6 scope. Shared indexes, control workflow,
Issues, PRs, integration and separate source/target adoption stay coordinator-owned.
This task stops before first push. No historical provider-review refusal is treated
as a local contract-authoring blocker; no public metadata comment was sent here.

## Plan and results

| Task | Completion criterion | Current result |
| --- | --- | --- |
| S1-A1 | Exact selection/content/catalog/subset/lock versions, fields, digest/closure and failure semantics | [Formats and schemas](../../design/framework-next/rc2-contracts/formats.md) authored; no parser implementation |
| S1-A2 | rc.1 compatibility, prefix/ownership/deselection and paired recovery | [Compatibility contract](../../design/framework-next/rc2-contracts/compatibility-and-recovery.md) authored; execution deferred |
| S1-A3 | Every scoped source file/rule has identity and migration/retention disposition | [272-file inventory](../../design/framework-next/rc2-contracts/migration-inventory.json), all 194 profile files and 14 rules; 11 unregistered document hash discrepancies preserved |
| S1-A4 | Minimal shared consumer binding and source/mq-lab examples preserve actual target truth | [Consumption](../../design/framework-next/rc2-contracts/consumption.md); fixed target read only, 14 rules/4 customizations/20 routes |
| S1-A5 | Exact dependent member/owner/interface handoff, all source capabilities and narrow S6 checks | [Handoff](../../design/framework-next/rc2-contracts/implementation-handoff.md); 235 planned members and 21 capability identities |
| S1-A6 | Bounded direct checks, exact-message local commit and pre-push coordinator handoff | Final state and checks in [delivery.md](delivery.md) and [checks.json](checks.json) |

## U001 adaptation and evidence

The workflow/task templates are used proportionally. Required local checks are
UTF-8, direct JSON/YAML parsing, schema-document reference readability, changed
Markdown links, Git root/branch/HEAD/status, changed-path scope, diff inspection,
`git diff --check` and the existing exact commit-message check. Direct parsing is
not schema compliance, behavioral validation, independent review or target admission.

All legacy/critical/full validators, package/compatibility/install/upgrade trials,
formal handoff/audit/lease/acceptance-ledger machinery, native checks, hosted gates
and CI remain **deferred-by-owner**, owner **program #322 coordinator / P7**.
Next action: the coordinator selects later implementation and S6/P7 checks under
the appropriate source/target authority. No empty audit record simulates them.

## Observed limitations and preserved failures

- Initial `gh issue view` failed through the sandbox proxy. The available GitHub
  connector subsequently read live Issue #401 successfully; no credential changes.
- Graph architecture discovery initially lacked a required project argument; its
  suggested list-projects tool was not available. Indexing the assigned tree then
  succeeded with persistence disabled. Index result did not expose a verifiable
  indexed commit and excluded 30 directory groups, including src/tools. Graph
  lookup was discovery only; tracked Git bytes/direct call sites bound conclusions.
- First inventory authoring attempt expected a flat shared normative hash and failed
  with KeyError; shared catalog stores it under source_governance_provenance. The
  corrected authoring script completed. First capability extraction expected id;
  the legacy schema uses asset_id. That authoring failure was retained and corrected.
  These were document-generation failures, not product-test attempts or passes.
- Target status warned about unreadable ignored prerequisite-fixture directories.
  Each of the 12 selected tracked authority files matched its fixed Git blob;
  no complete untracked-target cleanliness claim is made.
- Eleven unregistered profile catalog file hashes differ from their fixed source
  files. Actual source identities and recorded hashes are both retained; no semantic
  rule IDs, effective target state or legacy catalog bytes were rewritten.

## Remaining ownership

No unresolved S1 owner decision. S2 authors content; S3 integrates shared
manifest/profiles/distribution/engine protocol; S4 delivers adapters through the
serialized seam; S5 updates consumers before separately owned source and target
adoption; S6/P7 owns actual selected execution. A required semantic change discovered
later returns to the coordinator rather than being disguised as link relocation.

R1–R8 retain their original meaning. rc.1 tag/source, maintenance engine, candidate,
lock and mq-lab target identities are preserved in the contract. #369 native,
Actions/CI, dormant policy adoption, stable and new rc.2 tag/Release remain unselected.
The optional coordinator index row is in delivery.md; this task edits no shared index.
