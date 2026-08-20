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

At pushed clean head `66ec616b4d2c5e42129ae1a09557039d15ddb7df`, the candidate
release-state gate passed. A fresh exact-head Sol audit then failed with exactly
one cross-artifact finding: active narratives still called the now-committed
prior repair uncommitted and described commit/push as next work. It otherwise
passed renderer 20/20, payload 6/6, route 25/25, release-state 36/36, direct
renderer, terminal/workflow/source/AI/version/12-commit checks, and package plus
route cross-bindings; it made no repair and no receipt was submitted.

Separate live checks then terminally reached four PASS / one FAIL: Read-only
governance contract, Ubuntu PR profile gate, Ubuntu prerequisite contract, and
Windows prerequisite contract passed; Build and validate candidate failed. Its
sole log fetch, run `32428716122` / job `96615867346`, showed the candidate
validator received the pull-request merge-ref `GITHUB_SHA` rather than the exact
#206 terminal-close head, while the local exact-head candidate gate had passed.

The current source-candidate head carries the two-file checkout/validator-commit
correction using `${{ github.event.pull_request.head.sha || github.sha }}`.
Focused 10/10, YAML/diff, and independent mutation review passed. The first
independent review failure—that `PR_HEAD_SHA` alone left checkout at merge ref—is
retained. Next: exact clean candidate gate, fresh Sol audit and receipt, then one
hosted watch. PR #232 remains draft/open/unmerged; #206 open terminal-close; #222
deferred; no hosted admission, merge, Issue closure, provider closure, tag,
GitHub Release, or publication is claimed.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
