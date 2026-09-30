# Framework package build and Draft Release

Issue [#418](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/418)
selects this source-only delivery flow for Catalog 1 / Engine 2. The owner
activates only these two workflows; seven other workflows remain disabled.
This does not adopt #369's dormant source gates or exit P7.

| Trigger | Result |
| --- | --- |
| Merge/push to `main`, or manual **Build framework snapshot** from `main` | Generic snapshot ZIP, checksum and external manifest in Actions artifacts; no Release |
| Push an existing annotated `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-rc.N` tag | Exact tagged source package and owned GitHub Draft Release |
| Manual **Prepare framework draft** from `main`, input an existing annotated tag | Current immutable workflow tooling builds the old tagged product source, then prepares its draft |

No tags are created or moved. For an older tag such as `v0.19.0-rc.3`, select
`main` as workflow ref and that tag as the `tag` input. The original tag object
and peeled source commit remain unchanged. Product code executes in a separate
clean checkout of the exact source commit. The workflow/tooling commit is
recorded separately.

Catalog 1 accepts stable and `rc.N` versions only. Other SemVer prereleases,
including `beta` or `dev`, fail before draft mutation. Main snapshots use
`0.0.0-rc.<positive integer derived from the first 12 SHA digits>` as a
builder-compatible distribution label. Artifact and ZIP names say `snapshot`
and carry the full source SHA; this label grants no release status.

## Contents and identities

One ZIP contains `catalog/` (complete catalog and all actual metadata),
`engine/` (standalone 24-file Engine 2 closure and `engine.json`),
`engine-pin.json`, `README.md` and `content-hashes.json`. Before any product
execution, the tool AST-reads both literal `ENGINE_FILES` declarations, requires
their agreement and creates an independent pin from raw Git blobs. Executing
checkout bytes must match. Source-only `.github/` tools are excluded from the
downstream engine.

External `release-manifest.json` binds source/tag identities, catalog identity,
engine pin hash, all archive entries, ZIP size/SHA-256 and immutable
repository/workflow/tooling/run/attempt provenance. The ZIP has a checksum and no
self-referential archive hash. The tool verifies raw ZIP entries, extracts them
and checks raw hashes again. No MQ/project selection, `.dev` history, target
installation, scratch files or credentials are packaged.

Actual build receipts contain time/environment data; rebuilding one source
commit can yield different ZIP bytes. A matching source or catalog label alone
cannot justify replacing an asset.

## Draft retries and failures

The read-only build uploads an immutable Actions artifact. A separate writer
uses only `GITHUB_TOKEN` with `contents: write`. It has no Issue, Project, PAT,
AI or publication operation. Action references use verified immutable commits.
Product code never receives the writer token.

Authenticated paginated release listing discovers drafts. The writer refuses
public releases, foreign markers, differing source/tag/manifest identities,
extra/duplicate assets, mismatching bytes and incomplete `starter` uploads. It
checks the remote tag and draft state around uploads. Human publication racing
an upload cannot be made atomic through the Releases API; the writer stops at
the next observed change.

Keep the hidden ownership/admission marker when editing notes. Reruns never
PATCH body or title. All existing assets are downloaded and verified before any
missing asset is added; every final asset is downloaded and compared again.

After a successful build and transient writer failure, use **Re-run failed
jobs** to reuse original artifact bytes and build-attempt identity. Retain that
artifact and `draft-receipt-<run>-<attempt>`. A full rerun rebuilds time-bearing
metadata and deliberately fails against the old admission marker. Incomplete
uploads, lost artifacts, differing bytes and foreign drafts need explicit owner
reconciliation; automation never deletes or overwrites assets. HTTP failures
retain a receipt and never broaden credentials. Draft creation omits
`target_commitish` after checking the existing tag. If GitHub still rejects a
historical workflow change with this token, report that limitation.

## Notes and final publication

After draft readiness, the owner separately invokes Codex or ChatGPT in a
GitHub-authenticated session with repository write capability, or edits GitHub
directly. Supply these facts from the Actions run and manifest:

```text
Draft URL:
Existing annotated tag and tag object:
Exact source commit:
Prior published tag:
Build run URL, run ID and original build attempt:
Workflow/tooling commit:
Catalog identity and engine pin SHA-256:
ZIP asset name, size and SHA-256:
```

Ask that session to inspect `prior-tag..source`, merged PRs and associated Issue
evidence, then author accurate notes with compatibility changes and actual
validation limits. Explicitly request the draft edit. Review the notes and
separately authorize public publication. An arbitrary ChatGPT chat does not
automatically have GitHub write access. This pipeline uses no AI model/token.

Notes may change without rebuilding assets. This new path has no per-version
tracked notes, asset-admission/generated archive prerequisites or post-tag
source metadata commit. Historical published-format records retain their
contract. Build success and Draft ready do not establish tests, runtime/native
acceptance, P7 completion, Issue closure or a public release.

## Local commands

Use Python 3.10+ and PyYAML 6.x, a clean tooling checkout and fresh short external
roots. Keep earlier attempts. `$tooling` and `$source` are full immutable SHAs:

```powershell
python -I -B .github/scripts/build-release.py --repository (Get-Location).Path --source-commit $source --tooling-commit $tooling --workflow-commit $tooling --workflow .github/workflows/package-candidate.yml --run-id local-snapshot --run-attempt 1 --work-root F:/r418s --output F:/r418so
python -I -B .github/scripts/build-release.py --repository (Get-Location).Path --tag v0.19.0-rc.3 --tooling-commit $tooling --workflow-commit $tooling --workflow .github/workflows/publish-release.yml --run-id local-tag --run-attempt 1 --work-root F:/r418t --output F:/r418to
python -I -B .github/tests/test-release-tools.py
```

The fixture command covers only release transport. Framework/native/legacy
test suites remain deferred. Local outputs are not uploaded automatically.
Hosted writer execution belongs to the authorized workflow.
