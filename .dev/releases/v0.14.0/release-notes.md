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
`ad1973304e7fd2f170434c1fb5c77ff20c229fae`. The suffixed-declaration validator
fix is committed and pushed at `ea0414edf1260f0a317ee4b406b9eafb29d7f859`.

At pushed clean head `60e68922752ffc331bcd614db1676c94605a21fa`, the candidate
release-state gate passed and a fresh exact-head Sol audit passed with its
receipt submitted. One hosted watch then completed with Build and validate
candidate, Read-only governance contract, and Ubuntu PR profile gate failed;
Ubuntu and Windows prerequisite contracts passed. Each failed-job log was
fetched once. The candidate failure is the renderer's stale multi-source
requirement for migration schema `2.0.0`, whereas v0.14.0 uses `3.0.0`; the
governance/profile failures share a payload-user-view fixture that omitted the
canonical `target_owned_reference_patterns` allowlist.

The only current repair is uncommitted in the renderer, release-notes tests,
and payload-user-view fixture. The renderer sandbox baseline was blocked by
Temp `WinError 5`; the payload baseline had 4 failures and 3 errors. Normal ACL
renderer 20/20, payload 6/6, direct candidate renderer CLI, AST/scoped diff, and
independent precommit review passed. This is not hosted admission. Commit and
push the exact repair plus reconciled narratives, then rerun the candidate gate,
obtain a fresh Sol audit and receipt, and run one hosted watch. PR #232 remains
draft/open/unmerged; #206 remains open terminal-close; #222 remains deferred;
no hosted admission, merge, Issue closure, provider closure, tag, GitHub
Release, or publication is claimed.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
