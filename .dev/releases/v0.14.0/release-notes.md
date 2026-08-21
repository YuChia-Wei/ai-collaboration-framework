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

At pushed clean head `b4b38b136d69a1d3e3938598edcb4c6d7285b795`, the exact
local candidate command failed before online admission because durable
`release.yaml` evidence contained a literal GitHub expression, rejected as an
unfilled template marker. The exact diagnostic is retained in the S3 task
evidence. This is a narrative-encoding failure, not a workflow identity failure.

The preceding clean `66ec616b4d2c5e42129ae1a09557039d15ddb7df` candidate
release-state gate pass remains retained evidence. Its fresh exact-head Sol audit
then failed with exactly one cross-artifact finding: active narratives still
called the now-committed prior repair uncommitted and described commit/push as
next work. It otherwise passed renderer 20/20, payload 6/6, route 25/25,
release-state 36/36, direct renderer, terminal/workflow/source/AI/version/
12-commit checks, and package plus route cross-bindings; it made no repair and
no receipt was submitted.

Separate live checks then terminally reached four PASS / one FAIL: Read-only
governance contract, Ubuntu PR profile gate, Ubuntu prerequisite contract, and
Windows prerequisite contract passed; Build and validate candidate failed. Its
sole log fetch, run `32428716122` / job `96615867346`, showed the candidate
validator received the pull-request merge-ref `GITHUB_SHA` rather than the exact
#206 terminal-close head, while the local exact-head candidate gate had passed.

At pushed clean `fab9cf6787f0d4fad9384c29a6e0f514389667ba`, the exact local
candidate gate passed. A fresh exact-head Sol audit then failed with no receipt
after live candidate run `32431077702` / job `96622569129` failed. The audit
identified two blockers: an archived v0.13 schema 2.2 package without canonical
`target_owned_reference_patterns`, and downstream renderer, builder, and
source-disposition behavior still binding merge-ref `GITHUB_SHA` instead of the
selected candidate identity.

The current source-candidate head is `fab9`; the next commit will bind the
four-file compatibility and identity repair. Only an archived schema 2.2.0
package with that absent field infers the exact canonical list; altered present
values, current packages, and schema 2.3 packages with the field absent remain
fail-closed. The retained v0.13 archive and canonical v0.14 package at
`60572c01` pass. One job-level `CANDIDATE_COMMIT` selects the PR head or
dispatch SHA and binds checkout, renderer, validator, builder, source
disposition, and artifact identity; `PR_BASE_SHA` and `PR_HEAD_SHA` remain
separate for changed-record discovery. Current-byte payload 7/7 and
workflow-contract 10/10, AST/YAML/diff checks, and independent read-only review
of raw binary Git diff SHA-256
`4ecaef44a9b0636588df882308a3ea784c80e5669daf5b68bf7614590b93e349` passed
with no blockers. Next: parent commit and push of the exact repair head, the
candidate gate, fresh Sol audit and receipt, then one hosted watch. PR #232
remains draft/open/unmerged; #206 open terminal-close; #222 deferred; no hosted
admission, merge, Issue closure, provider closure, tag, GitHub Release, or
publication is claimed.

<!--
The renderer appends canonical Included Work and release provenance. Keep this
authored content phase-neutral and omit generated automation details.
-->
