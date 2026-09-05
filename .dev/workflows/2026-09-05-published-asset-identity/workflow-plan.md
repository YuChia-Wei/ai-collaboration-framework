# Published Asset Identity

- Issue: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/280
- Authorization: the owner accepted the proposed sequence and instructed Codex on 2026-09-05 to proceed with Issues 269 and 280, pausing for material owner decisions. Local implementation, required public-byte download/backfill, tests, independent review and commits are within that scope. Push/PR/merge, provider terminal mutations and release publication remain separate.
- Baseline: clean main `a12eb16d2fc85c0085c33f2eea1fd01ace0a5a41`. Issue 269 is locally complete on `codex/2026-09-05-diagnostic-analyst` at `54c919ae36b49c60d797754d198f78307edda10f`; it has not been integrated.
- Owner: ai-context-governance. Delivery is separate from diagnostic capability; this workflow retains publication identity and historical route recovery evidence across lifecycle gates.
- Intended topology: merge commit, because candidate/published identity and historical recovery form a resumable integration unit.

## Design Direction

New publication must stage the exact admitted ZIP/tar and sidecars, never rebuild on tag. Candidate source SHA remains provenance; compare the admitted portable content/configuration with the tagged source before transport. Use content-addressed archive identity alongside logical package/release identity and retain candidate provenance distinctly from provider publication evidence.
Provider name, size and SHA-256 are mandatory. Missing or conflicting bytes fail closed. Historical backfill uses exact public v0.15.0/v0.15.1 bytes in new evidence, leaving original tags, assets and records untouched. Rebound archives must execute their own incoming portable validator and their edge validator.

## Acceptance Ledger

- REL018-AC1: mismatch between admitted/uploaded and provider digests fails a v0.16.0 fixture.
- REL018-AC2: publication promotes exact admitted archives and records provider name/size/digest. Actual first publication remains a later release-stage gate.
- REL018-AC3: governed post-publication routes bind exact public asset bytes.
- REL018-AC4: historical candidate and published identities remain distinct and future routes select the public bytes.
- REL018-AC5: each rebound archive executes portable and edge boundaries.
- REL018-AC6: historical tags/Release assets remain immutable.
- REL018-AC7: unavailable/missing/conflicting provider evidence blocks.
- REL018-AC8: no routine source closeout is introduced.

## Initial Evidence

Both public ZIPs match the live provider digest and size, and each passes standalone archive validation and its own embedded portable validator (639 payload files, 16 portable entrypoints). The initial command passed two different versions to a parity validator and failed; that was an invocation error, not package corruption. Subsequent one-archive validations passed. Exact raw provider/download/execution evidence is retained under ignored issue-280 validation artifacts.

## Sequence And Gate

### Owner decision: publication acceptance

On 2026-09-05 the owner selected "keep Issue 280 open; close after publication
acceptance." Preserve that deferred acceptance in Issue 280. Its v0.16.0
provider binding belongs to coordination (open before publication, closed only
after successful public-byte read-back), disjoint from prepublication-closed
Included Work. This tracking decision does not authorize publication.

### Bounded validation retry 03

The workflow authorizes one third release-state test attempt after correcting
the pre-existing historical fixture calls: attempt 1 lacked the now-required
automatic-origin argument; attempt 2 exposed the historical v0.14 broader
declaration versus the current source-candidate horizon. The repair tests the
retained matrix with its representative predecessor and separately asserts that
the broader historical declaration remains rejected for new candidate admission.
No historical release record or production gate is weakened.

1. Implement REL018-promotion; validate failure fixtures and effective workflow wiring.
2. Rebind historical public archives and routes with actual portable/edge evidence.
3. Independently review a clean immutable commit and preserve unresolved release-stage acceptance.
4. Prepare the concrete handoff for Issue 272 and the later v0.16.0 release assessment. Do not relabel fixture success as observed publication.

## Local Completion

Both local tasks are complete after independent review and correction verification. The owner selected Issue 280 publication coordination; online delivery and Issue 272 execution remain separate gates.

## Provider Delivery Authorization

On 2026-09-05 the owner explicitly approved pushing both Issue 269 and 280 branches, creating pull requests, and merging after all required checks pass. Issue 269 closes after verified integration; Issue 280 remains open until actual v0.16.0 publication acceptance. Publication and Issue 272 implementation are separate.
