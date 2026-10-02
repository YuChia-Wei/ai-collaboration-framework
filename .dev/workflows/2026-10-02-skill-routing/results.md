# Results and evidence

Base: `dc55bb509dc7af4a2f2380054c48c63eadfd02af`; Issue 432.
Three actual read-only audits (`routing_engineering_audit`,
`routing_execution_audit`, `routing_records_audit`) and root's context-family audit
cover 19 source skill directories. Root reviewed all reports and inspected the
integrated diff. Fourteen skills receive changes across 19 prose files; five remain
unchanged. Runtime projections, metadata operations/dependencies/versions,
distribution manifest, profiles, scripts, schemas and release artifacts are intact.

## Checks observed before the first review commit

- `git diff --check`: passed.
- `python -I -B C:/Users/h4227/.codex/skills/.system/skill-creator/scripts/quick_validate.py <changed-skill>`:
  all 14 changed skill packages passed frontmatter/name/scaffold checks; this is
  structural validation, not behavioral acceptance.
- `python -I -B tests/run.py --suite source`: passed; 46 executed, 0 errors,
  failures or skips; reported duration 2.315974 seconds.
- Static route examples and operation-table/metadata comparison are recorded in
  `routing-audit.md`; they are not actual agent acceptance.
- Immutable affected selector, independent review and hosted current-head CI are
  pending at this checkpoint. Final evidence will retain exact full commit IDs.

## Retained preparation failures and limits

- Initial GitHub read in the restricted network failed at the proxy; the authorized
  host-permission read succeeded. No provider write was inferred from failure.
- Reads guessed a previous task's `.md` suffix, a generated-entry reference path,
  and `tests/manifest.yaml`; those paths do not exist. Tracked filenames, the
  generated entry's actual installed link, and `src/distribution/manifest.yaml`
  supplied the correct owners. These were discovery failures, not product failures.
- A PowerShell glob passed literally to rg failed; the scoped `-g` search corrected it.
- The first graph request lacked its project identity. A fast nonpersistent index
  identified the project, but excludes `.github/scripts`, package script folders
  and maintenance tools. Selected tracked-file reads are the explicit fallback
  for the source selector and operation contracts; graph absence is not evidence.

No new tests mirror the wording. No native installation, managed refresh, package
publication, release, downstream adoption or real agent scenario execution is
selected. This task does not discharge legacy/P7 deferrals or close other Issues.
Source version identifiers remain unchanged because no operation or dependency
contract or release allocation is selected; immutable source identity binds this
instruction revision, and existing released bytes remain unchanged.
