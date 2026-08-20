# REL-v0.14.0 — Retained-Origin Upgrade Source Candidate

This governed source candidate defines the v0.14.0 package identity and
retained-origin compatibility contract. It is not a tag, GitHub Release, or
publication record.

## Highlights

- Records exact migration inputs for governed sources v0.13.0, v0.9.0, and
  v0.6.0 under the v0.14.0 package identity.
- Establishes the source-only support-matrix and route-evidence locations for
  the retained origins.
- Carries the UPG-003 compatibility work through the canonical nine-item
  release scope.

## Compatibility

v0.14.0 is a breaking migration checkpoint with a minimum governed source of
v0.6.0. The candidate records v0.13.0, v0.9.0, and v0.6.0 as exact package
migration inputs. Their direct or orchestrated route classification must come
only from the completed support matrix and its receipt-bound evidence.

## Release Validation

ZIP/TAR package parity was validated at immutable package foundation
`60572c01e31abf58191d38adb5ca39e05338b08d`. The planner-byte fix and three
receipt-bound canonical direct-route proofs for v0.13.0, v0.9.0, and v0.6.0
are committed in distinct source candidate
`ad1973304e7fd2f170434c1fb5c77ff20c229fae`. Its exact-head audit found stale
active narratives, first reconciled in draft/open PR #232 initial head
`aaae7aaf9f64be49574f9b35a6ca7e011bf9d593` against
`main@bf8ad9c624ffc2154722dfb266c9090c72e4ac5f`. At historical pushed head
`0a9a25784d6fd3ba2429fb19bd04b45fac327029`, the candidate phase failed because
the helper looked only for `terminal-issue-closure-declaration.yaml` and missed
the same-workflow suffixed S3 declaration.

That validator fix is committed and pushed at
`ea0414edf1260f0a317ee4b406b9eafb29d7f859`, where the exact clean candidate
release-state gate passed. A fresh Sol High exact-head audit of that commit
terminally failed with exactly one blocking finding: active narratives were
stale. It otherwise passed release-state 36/36, route 25/25,
terminal/workflow/AI-context/source-governance/version-registry/commit-policy/
AST-YAML-JSON-diff checks, and the package plus three route cross-bindings; the
audit made no repair.

In the single live audit snapshot, draft/open PR #232 had exact base
`bf8ad9c624ffc2154722dfb266c9090c72e4ac5f`, head
`ea0414edf1260f0a317ee4b406b9eafb29d7f859`, and body; #206 was open
terminal-close and #222 open deferred. Build and validate candidate was a
completed `FAILURE`; Read-only governance and Ubuntu PR profile were
`IN_PROGRESS`; and Ubuntu and Windows prerequisites were `SUCCESS`. No logs
were fetched. These are hosted observations, not hosted admission.

The next admissible subject is the exact PR head containing this narrative
reconciliation: rerun the candidate release-state gate on that exact clean head,
then obtain a fresh Sol audit and hosted admission. Issue #206 remains open,
#222 remains deferred, and no hosted admission, merge, Issue closure, provider
closure, tag, GitHub Release, or publication is claimed.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
