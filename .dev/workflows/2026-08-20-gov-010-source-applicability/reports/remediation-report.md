# GOV-010 Remediation Report

## Scope

- Online authority: GitHub Issue #219 and the repository owner's explicit authorization.
- Delivery PR: #223 with terminal-close declaration.
- Source baseline: `094670feab495137e3d5e30a62291e572a164028`.
- Implementation checkpoint: `19d2c952014c2a135bd9a34824cf9e5610932ec8`.
- No local roadmap or backlog record supplied planning, scope, priority, release, or completion truth.

## Delivered Boundary

- Added explicit `framework-source` and `initialized-target` resolver modes.
- Framework-source execution reads fixed policy, evidence schema, resolver, and catalog bytes from Git `HEAD`; requires exact working-tree parity; binds repository identity, commit, status, selectors, explicit rule IDs, selection evidence, rule bytes, and digests.
- Framework-source execution neither reads nor creates downstream provenance, customization, effective state, or packet authorities.
- Initialized-target behavior retains the existing fail-closed target authority, freshness, routing, and digest contract.
- Ten canonical action skills use one mode-explicit consumption contract without remembered-default, broad-scan, alternate-skill, or provenance-fabrication fallback.
- Source execution policy, evidence schema, and workflow evidence are excluded from downstream packages; the portable resolver remains included.

## Focused Evidence

- Resolver suite: 27 tests passed; 2 existing skips.
- Action-skill contract: 3 tests passed.
- Package isolation fixture: 1 test passed in 1.383 seconds for ZIP, TAR, extracted payload, and retained resolver behavior.
- Wrapper metadata: 16 tests passed on the routed host execution surface.
- AI-context, source-governance, source-disposition, workflow-artifact, YAML parsing, commit-policy, and diff checks passed.
- Actual clean framework-source execution at checkpoint `19d2c952014c2a135bd9a34824cf9e5610932ec8` resolved `AICTX-EVIDENCE-001`; status digest was the empty-tree SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; packet digest was `900b871b60f868a630df57ec6a5bf884334c904a0dff2e8d36ddb3e972609453`.

## Retained Failed Evidence

- One broader package test-file run timed out after 124.025 seconds with no output. It was not converted to a pass and was not rerun as the same operation.
- Read-back found no remaining run-owned Python process and no `.tmp/p` residue.
- The changed package behavior is covered by the narrower passing fixture above; hosted exact-head checks remain separately required.

## Remaining Provider Gates

- Freeze the final clean PR head and rerun actual framework-source evidence.
- Obtain a fresh exact-head independent Sol High audit with zero blocking findings.
- Require every hosted check at that head to succeed.
- Capture live merge-admission evidence, merge only the admitted head, and read back PR, Issue #219, and Project state.
