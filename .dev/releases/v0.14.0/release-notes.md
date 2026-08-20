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
`ad1973304e7fd2f170434c1fb5c77ff20c229fae`. The exact-head audit of that
commit found only stale active narratives, repaired in draft/open PR #232
initial head `aaae7aaf9f64be49574f9b35a6ca7e011bf9d593` against
`main@bf8ad9c624ffc2154722dfb266c9090c72e4ac5f`.

After pushed head `0a9a25784d6fd3ba2429fb19bd04b45fac327029`, one live
PR #232 read-back passed the exact base, head, and body binding; #206 and #222
remained open. Its five hosted checks were `IN_PROGRESS` observations, not
results. The candidate phase then failed because the helper looked only for
`terminal-issue-closure-declaration.yaml` and missed the same-workflow suffixed
S3 declaration. The uncommitted repair scans canonical
`terminal-issue-closure*.yaml` records with exact schema, contract, uniqueness,
and live PR/current-HEAD/body/base requirements; it is not candidate admission.

The next gate is combined-diff validation, commit and push of the validator-fix
evidence, candidate re-admission on the new exact clean head, then fresh Sol
audit and hosted admission. Issue #206 remains open until merge, #222 remains
deferred, and no candidate/hosted admission, merge, Issue closure, provider
closure, tag, GitHub Release, or publication is claimed.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
