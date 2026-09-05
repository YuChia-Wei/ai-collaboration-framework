# Issue 280 Local Remediation

The local implementation binds one admitted artifact set to candidate CI,
tag staging, draft upload verification and published provider read-back. From
v0.16.0 onward a missing tracked admission or a route/source/provider identity
disagreement blocks. Historical v0.15.0/v0.15.1 assets were downloaded and rebound
in new workflow evidence; no historical release directory, tag or public asset
was modified. Independent review is pending on the first immutable commit.

## Acceptance And Evidence

| Acceptance | Local evidence | Disposition |
| --- | --- | --- |
| REL018-AC1 | v0.16.0 provider digest mismatch, missing digest, wrong size/name/ID and transport drift fixtures | Passed as synthetic failure tests |
| REL018-AC2 | Workflow stages admitted bytes; real v0.15.1 ZIP/tar source projection, staging and fresh provider read-back in `evidence/published-routes/actual-transport-check.json` | Implementation and local real-byte transport passed; first new release publication deferred |
| REL018-AC3 | All incoming target matrix edges must bind the admitted archive digest and payload; published admission requires fresh provider and downloaded-byte verification | Implemented; actual v0.16.0 routes/publication remain Issue 272 and release-stage gates |
| REL018-AC4 | `evidence/published-routes/asset-lifecycle.json`, public read-backs, rebound support matrix and three canonical route resolutions | Passed for historical backfill |
| REL018-AC5 | Actual v0.14.0 → v0.15.0 and v0.15.0 → v0.15.1 edge outputs each include executed archive-owned portable validation | Passed; 8.729s and 9.206s respectively |
| REL018-AC6 | Only new evidence copies were written; originals and tags remain outside the diff; no provider mutation commands executed | Passed for this local work |
| REL018-AC7 | Missing admission, omitted/changed selected inputs, conflicting archive identity and unavailable/mismatching provider fail closed | Passed as bounded tests; future provider failure remains a blocking outcome |
| REL018-AC8 | Provider publication receipts remain ignored/hosted artifacts; source record stays terminal before tag | Implemented without routine source closeout |

The rebinding target is v0.15.1. v0.15.0 resolves directly; v0.9.0 and v0.6.0
resolve through the unchanged public v0.14.0 edge and both newly bound public
archives. Unchanged v0.14.0 validator, archive and receipt bytes were copied by
explicit referenced path with digest verification and reused; those edges were
not re-executed. The two new historical validators differ only in immutable
published archive/source provenance constants. Both public payload fingerprints
match their old candidate fingerprints while their archive hashes differ.

## Focused Verification

- Release asset identity: 13 tests passed, including source-input omission/drift,
  history-only rebind and exact-byte staging.
- GitHub workflow contract: 12 tests passed, including conditional legacy build,
  unchanged candidate staging and provider comparison before/after publication.
- Release-state regressions: 37 tests passed after repairing stale historical
  test calls; no production horizon gate or old release record was weakened.
- Python prerequisite/entrypoint contract: 14 tests passed.
- Validation profile registry: 10 tests passed. The new no-reuse gate is required
  in fast, PR, release and nightly-full profiles.
- Shell lifecycle/required-command validation, AI-context structure/language,
  workflow artifacts and whitespace checks passed before review freeze.
- Real v0.15.1 archive parity, original source projection, copying and fresh
  provider asset checks passed with all four published ZIP/tar/checksum assets.

No aggregate release/full-matrix run, new-release upload, target upgrade, tag,
PR, merge, Issue closure or Project mutation is claimed. New-release hosted
behavior still needs its actual authorized publication gate.

## Preserved Failures And Limits

The first historical archive command incorrectly asked a parity validator to
compare different versions; separate archive checks then passed. The first
v0.15.0 edge run lacked an origin manifest referenced only in argv; after adding
that declared input, both edges passed. Raw attempts remain in ignored Issue 280
validation artifacts. Release-state attempt 1 exposed missing arguments in
pre-existing fixtures; attempt 2 exposed their historical broad declaration.
The workflow authorized bounded attempt 3 after separately asserting that the
old declaration remains rejected as a current source candidate.

GitHub draft pages may use an `untagged-*` URL even with an existing tag; the
implementation locates the release by CLI database ID, then reads REST data by
that ID. Draft page allowance never applies to published receipts. This behavior
is evidenced in [GitHub CLI issue 11589](https://github.com/cli/cli/issues/11589),
and name/size/digest fields follow the [GitHub Releases REST contract](https://docs.github.com/en/rest/releases/releases).
No actual draft was created for this work.

The code graph omitted these source-only Python/context paths. Discovery used
explicit Git-tracked file reads and current repository validators; graph search
absence was not treated as proof. The source-only changes introduce no portable
package schema rename.

## Handoff

Integrate the separately reviewed Issue 269 capability and this delivery before
preparing Issue 272's v0.16.0 candidate. Use the published v0.15.1 archive/origin
manifest from the backfill and the retained v0.9.0/v0.6.0 origins. Validate all
three actual direct edges against the same admitted archive. Complete release
scope, compatibility, aggregate validation, exact-subject review and provider
preflight before requesting tag/publication authorization. Issue 280 must retain
its deferred publication acceptance until the actual new-release read-back.
