# Review, repairs and commit checkpoint

The owner requested review, necessary repairs and commit on 2026-10-03. Scope is
Issue #435's local cleanup relative to
`b52c68d64373bb54688109b9174bd4a9cea2b577`, preserving the existing sub-agent work
already in that commit. Review used `code-reviewer`; bounded selector repair used
`local-change-implementer` and project policy. No sub-agent was dispatched.

This is author-side review of the working diff, followed by repairs. It is not
the independent immutable review required before later integration.

## Findings and disposition

| ID | Impact and evidence | Disposition |
| --- | --- | --- |
| R1 (P2) | The new common technology-selection resource exposed .NET GWT/base-class/mocking conventions as universal invariants. A non-.NET consumer could apply unselected profile rules. | Fixed: common guidance now preserves only adopted invariants and identifies profile-owned defaults; .NET rules retain their existing profile owner. |
| R2 (P2) | `test-standards.md` still required `.dev/project-config.yaml#technologySelections` while the migrated method lets the target choose its record destination. A selection elsewhere could be ignored and NSubstitute incorrectly chosen. | Fixed: read the target-selected record; default only under an adopted profile. Reconciled exact TEST-MOCK-001 text and all affected source/catalog hashes. |
| R3 (P2) | The existing source selector rejected `.dev/README.MD` as unknown ownership. This previously dormant gap blocks the cleanup's actual change gate. Reproduced through `select` with a before/after README fixture. | Fixed: classify the project entry alongside `.dev/INDEX.md`, retaining source checks and independent review. A regression test failed before the fix and passed afterward. |
| R4 (P2) | The newly authored workflow used `issue` instead of `work_items`/`issue_refs`, a noncanonical completed-task finding status, and a root JSON evidence file outside supported workflow record formats. The prior ad hoc locator check missed these admission failures. | Fixed: canonical online Issue binding and `finding_status: addressed`; separate pending integration requirements; preserve the integrity capture in a supported Markdown evidence file. Actual selector/content preflight passes. |

The remaining diff was inspected for source/project ownership, declaration and
reference closure, preserved history/installed content, bilingual root alignment,
retained experience and version/publication claims. No additional actionable
defect was found within that scope. Optional installed specialist knowledge was
not selected; this review evaluates visible source contracts and does not claim
.NET runtime or architecture acceptance.

## Validation before commit

- The new README regression failed before the selector correction with
  `unknown ownership; coordinator must select checks: .dev/README.MD`.
- `python -I -B tests/run.py --suite schemas --suite distribution --suite source`:
  passed, 146 tests, zero failures/errors/skips, 8.03234 seconds with host permissions.
- Working-tree selector/content preflight: no ownership errors; selected exactly
  content, whitespace, schemas, distribution and source, retaining
  `independent-scoped-review`. This preflight is not an immutable gate result.
- Final catalog hashes, owner section parity, protected-tree canonical diff and
  whitespace inspection are checked before staging/commit.
- Validate the exact complete message file using
  `python -I -B tools/maintenance/validate-git-commits.py --message-file .dev/ai-context/local/commit-messages/issue-435.txt --workflow-id 2026-10-03-documentation-boundaries`
  before committing those bytes. The first message draft was rejected because
  the validator reserves additional Co-Authored-By trailers for sub-agents. The
  corrected message uses the current primary session trailer and retains initial
  primary authorship in the body and DOC-001; no sub-agent identity is fabricated.

Immediately after commit, run the real source selector against the fixed input
commit and new HEAD. Its actual result belongs in the ignored local diagnostic
`.dev/ai-context/local/review-435/committed-gate.json`, retaining the exact SHA
without another tracked edit that would invalidate the checked subject. This
checkpoint records the scheduled check, not a preemptive pass. Hosted admission
and independent review remain pending before separately authorized integration.

Issue #435 remains open. Push, PR, merge, self-installation and publication are
outside this checkpoint. The owner retains the later stable 0.19.0/rc5 decision.
