# Framework package build and Draft Release

Issue [#418](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/418)
selects this source-only delivery flow for Catalog 1 / Engine 2. The owner's
2026-10-04 continuation retains these two packaging workflows and source checks,
and removes obsolete automation. This does not establish full P7 acceptance.

| Trigger | Result |
| --- | --- |
| Push to `main` changing `src/**` or `tools/**`, or manual **Build framework snapshot** from `main` | Generic snapshot ZIP, checksum and external manifest in Actions artifacts; no Release |
| Push an existing annotated `vMAJOR.MINOR.PATCH` or `vMAJOR.MINOR.PATCH-rc.N` tag | Exact tagged source package and owned GitHub Draft Release |
| Manual **Prepare framework draft** from `main`, input an existing annotated tag | Current immutable workflow tooling builds a compatible tagged product source, then prepares its draft |

New draft titles contain only the version. RC display titles use `v0.19.0-rc3` while the canonical tag and package identity retain `v0.19.0-rc.3`. Existing human-edited titles remain preserved on retries.

No tags are created or moved. Current tooling requires the selected source tag
to contain the current engine contract and the release README template described
below. Older tags lacking either require their compatible historical tooling;
there is no fallback to current checkout product resources. The original tag
object and peeled source commit remain unchanged. Product code executes in a
separate clean checkout of the exact source commit. The workflow/tooling commit
is recorded separately.

Catalog 1 accepts stable and `rc.N` versions only. Other SemVer prereleases,
including `beta` or `dev`, fail before draft mutation. Main snapshots use
`0.0.0-rc.<positive integer derived from the first 12 SHA digits>` as a
builder-compatible distribution label. Artifact and ZIP names say `snapshot`
and carry the full source SHA; this label grants no release status.

## Contents and identities

One ZIP contains `catalog/` (complete catalog and all actual metadata),
`engine/` (standalone 23-file Engine 2 closure and `engine.json`),
`engine-pin.json`, `README.md` and `content-hashes.json`. Before any product
execution, the tool AST-reads both literal `ENGINE_FILES` declarations, requires
their agreement and creates an independent pin from raw Git blobs. Executing
checkout bytes must match. All current engine members live under `src/`;
downstream CLIs are `src/tools/maintain_framework.py`, `src/tools/derive-subset.py`
and `src/tools/reinstall-framework.py`. `tools/build-catalog.py` remains a
source-checkout build command and is excluded from the engine, as are all other
root build tools and `.github/` helpers. Shared distribution modules remain
because the consumer derives and validates subsets with them.

This layout differs from RC4's 24-file engine. Already published bytes and their
old command paths are unchanged; rebuilding an old-format tag needs its
compatible historical tooling. Do not combine the current source-only engine
pin with an RC4 engine or claim that a new build replaces published assets.

External `release-manifest.json` binds source/tag identities, catalog identity,
engine pin hash, all archive entries, ZIP size/SHA-256 and immutable
repository/workflow/tooling/run/attempt provenance. The ZIP has a checksum and no
self-referential archive hash. The tool verifies raw ZIP entries, extracts them
and checks raw hashes again. No MQ/project selection, `.dev` history, target
installation, scratch files or credentials are packaged.

New builds emit `framework-release-assets/2`. The reusable ZIP `README.md`
comes from the regular UTF-8 Git blob
`src/distribution/templates/release-readme.md` at the selected **source commit**,
not the workflow/tooling commit. The renderer uses `string.Template` with exactly
`label`, `source_commit`, `catalog_identity` and `release_version`; unknown,
missing or malformed placeholders fail. A missing source template fails without
reading a replacement from the working tree.

The external manifest's mandatory `provenance.readme_source` contains the fixed
source path, source commit, Git blob identity, raw SHA-256, byte size and original
`template_utf8`. The offline verifier checks those byte identities, renders the
four manifest-selected values again and requires exact agreement with ZIP README
bytes. Version 2 also requires each catalog member's source path to be a safe
`src/` path. The template is not an extra ZIP member, catalog build input or
engine member; the engine remains the same 23-file closure. Generated manifests,
pins and hashes remain source-project release orchestration.

The reader retains `framework-release-assets/1` handling for existing artifacts.
A successful version-1 read validates the legacy envelope only: its README source
evidence is absent, and it does not establish the version-2 source-only rule.
Published version-1 ZIPs, manifests, tags and notes are never rewritten by this
change. Draft ownership still binds the exact existing manifest bytes, so a
new version-2 rebuild cannot replace assets admitted with a version-1 manifest.

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
A fresh tag/draft read follows those downloads before reporting Draft ready.

After a successful build and transient writer failure, use **Re-run failed
jobs** to reuse original artifact bytes and build-attempt identity. Retain that
artifact and `draft-receipt-<run>-<attempt>`. A full rerun rebuilds time-bearing
metadata and deliberately fails against the old admission marker. Incomplete
uploads, lost artifacts, differing bytes and foreign drafts need explicit owner
reconciliation; automation never deletes or overwrites assets. HTTP failures
retain a receipt and never broaden credentials. The writer persists each POST
intent before sending it and records provider IDs only after a valid acknowledgement.
A timeout, failed response or malformed acknowledgement leaves that operation's
write outcome explicitly unknown; inspect provider state before a retry. Draft creation omits
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
python -I -B tests/run.py --suite release
```

The fixture command covers only offline release-helper behavior; tests are owned
under `tests/release/`. Current local schema/tool/data suites use
[`tests/run.py`](../../../tests/readme.md). Native installation and legacy trials
remain deferred or retired as documented there; local outputs are not uploaded automatically.
Hosted writer execution belongs to the authorized workflow.
