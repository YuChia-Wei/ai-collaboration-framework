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

## Immutable source review and affected validation

- Source subject: `36bf509952c9cbb8a4aecc751cda0cfc961303bb` against the base above.
- Independent reviewer: `/root/routing_final_review`, read-only and not an author
  of the diff. Reviewed all 26 changed files, all 19 source entries and relevant
  methods/operation metadata/source policy. No supported actionable findings;
  fixed HEAD and clean worktree observed at completion. Parent accepted the review.
- Criteria: the five Issue 432 acceptance criteria and source policy rules 2-7,
  including context selection, complete routing disposition, optionality, semantic
  radius, real operations, managed/release boundaries and truthful evidence.
- `python -I -B .github/scripts/check-source-change.py --base dc55bb509dc7af4a2f2380054c48c63eadfd02af --head 36bf509952c9cbb8a4aecc751cda0cfc961303bb`:
  passed content, whitespace and source (46 tests, no skips/errors/failures),
  overall duration 24.585 seconds. Independent review is a separate admission
  requirement; the selector correctly reported admission itself not evaluated.
- `python -I -B tools/maintenance/validate-git-commits.py --range dc55bb509dc7af4a2f2380054c48c63eadfd02af..36bf509952c9cbb8a4aecc751cda0cfc961303bb --workflow-id 2026-10-02-skill-routing`:
  passed for the authored source commit; its planned message was also validated.
- Deterministic Git/manifest inventory: 19 source skills, 18 distributed, 14
  changed, 26 total files. No metadata, script, schema, manifest, profile, installed
  projection or release path changed. The five unchanged skill dispositions and
  27 static selection scenarios are retained in `routing-audit.md`.

The completion update changes only workflow evidence/state and its index row.
It does not claim whole-tree equivalence: all 19 changed skill-file blobs must
match the reviewed subject at final admission, while the new record diff receives
affected review and checks. Final commit binding, hosted CI, PR merge and separate
Issue/Project read-back are retained in the authorized provider records; they are
not asserted passed in this pre-provider source record.
