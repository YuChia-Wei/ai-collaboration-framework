# v0.7.0 Candidate Integration Handoff

## Candidate State

- Release record: `validated`
- Candidate phase at `cc0113700afd7bf75c8a4183f9ef8dca5caf4a4e`: passed
- Canonical Included Work: `GOV-002`, `GOV-003`, `PKG-004`, `REL-003`
- Breaking change: false
- Exact automatic source: `v0.6.0`
- Tag, hosted release, and publication: not created

## Package State

The exact `cc01137` build preserved the independently verified 606-path
payload and exact v0.6.0 migration manifests:

- `files.yaml`: `6c4a22889e525509521398439e3cdf9ca362b99f1f52ff434fe691fa4c213b64`
- `migration.yaml`: `9007e03abea33a9756c0fd407eab1235d0467f20942aa5f38054a617d7f04f70`
- ZIP: `1fa9945310842e7f08d2c28847c9f3ac2bfbf30eb6e56c0f4b5e697a677a0346`
- tar.gz: `07c2dcd5895dfde38539f8ff48928c6661d4b079fc89a7e68f15d52de769743d`

Archive parity passed. Generated release notes retained authored content and
contained each canonical Included Work ID exactly once.

## Validation Summary

- Release-state tests: 23/23 passed.
- Release-note renderer tests: 6/6 passed.
- Backlog release tests: 6/6 passed.
- Version-governance tests: 19/19 passed.
- Packaging matrix: 26 passed; one environment-gated downstream integration
  fixture skipped and not counted as passed.
- Package apply matrix: 23 passed; one Windows symlink capability fixture
  skipped and not counted as passed.
- Profile projection: 3/3 passed.
- Workflow, assessment, AI-context, YAML/JSON, and diff validation: passed.
- Independent verification: `ASM-20260728-001` passed the required candidate
  package-fixture gate after first failing and driving the compatibility fix.

## Aggregate Gate

The single local `critical` aggregate execution is recorded as **failed**, not
passed: 41 of 44 required checks passed, three .NET test commands failed because
WSL could not resolve `dotnet`, and the commit-range slot was not applicable
without `COMMIT_RANGE`. The aggregate was not rerun.

The same three required commands then ran individually with the Windows .NET
SDK and passed:

- analyzer template tests: 49/49
- configuration validation tests: 2/2
- building-block behavior tests: 5/5

The final commit range is validated separately. The hosted PR required checks
must provide a green aggregate result before merge; the failed local aggregate
is never relabeled as passed.

## Hosted Package Remediation

PR #15 initially passed the hosted Ubuntu quick and read-only governance gates
but failed the package candidate gate. The new fail-closed compatibility check
correctly rejected rebuilding historical v0.6.0 without its own v0.5.0
migration input.

The candidate and publication workflows now obtain each automatic-upgrade
baseline from the immutable published release ZIP plus adjacent checksum,
validate that archive, and only then extract `metadata/files.yaml`. They no
longer rebuild a historical release with the current builder. The workflow
contract tests and full packaging matrix passed after this correction; hosted
checks must rerun and all pass before merge.

## Remaining Authorized Steps

1. Validate the final branch commit range and candidate state.
2. Push the branch and open a ready PR.
3. Require hosted checks, including the aggregate/package candidate jobs, to
   pass before merge.
4. Merge through the PR-only policy and synchronize local `main`.
5. Run current-main pre-tag preparation and stop before tag or publication.

GitHub Issues/Projects adoption, provider resources, tag creation, and release
publication remain outside this workflow checkpoint.
