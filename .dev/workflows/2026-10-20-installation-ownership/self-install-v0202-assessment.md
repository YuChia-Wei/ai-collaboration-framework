# Public v0.20.2 self-reinstallation: blocked before mutation

Observed on 2026-10-21, Asia/Taipei. Scope is this exact source repository,
baseline `3c7434fd3ea65bcbf519fef3e3ca232a0bc59043`, its real installed state,
and the live OWN-01–08 / DOC-01–06 criteria of Issues #472 and #473.
The owner explicitly authorized this installation and preservation of existing
custom content/history. No product repair, new release or Issue closure is
inferred. Methods: installed diagnostic-analyst and spec-compliance-validator;
no .NET profile, actor execution or new test matrix was selected.

## Actual subject and execution

- Public release: v0.20.2, release ID 418964031; source/tagged commit
  `3c7434fd3ea65bcbf519fef3e3ca232a0bc59043`.
- ZIP SHA-256: `9ca52a7ee2cfc043e4781d941b04a9eb664e2def75bb0837c890a9e81dd79b15`.
  Its Actions/Draft/public equality was verified during release; this turn
  rechecked all 482 extracted package entries against that public manifest.
- Existing installation is still `0.19.0-rc.3`, source
  `5ed50d1b59115a2677711dbb91fcb8cc12dc2148`, lock version 2. The earlier
  v0.20.1 attempt stopped without apply; it never upgraded this target.
- Preserve the existing 17-skill capability selection, both adapters, original
  naming, empty knowledge/bindings, and the previously approved replacement
  `bdd-gwt-test-designer` -> `test-designer`. No additional capabilities selected.
- Official `engine/src/tools/derive-subset.py` succeeded with the new catalog,
  selection and engine pin. Candidate:
  `subset:3:0.20.2:3c7434fd3ea65bcbf519fef3e3ca232a0bc59043:67797fb9be0794438fa99071a5f82053b7bfe5cd2e6e93cf905c461b42dc5dd6`.
- Official `maintain_framework.py` inspect returned exit 1, `blocked`,
  `changed:false`, `invalid-shape`; owned/drift observations are unavailable.
- Official `reinstall-framework.py` plan returned exit 1, `blocked`,
  `changed:false`, `removed:[]`, diagnostic `reinstall-input`.
  The read-only compatibility probe supplied 135 old managed paths plus their
  lock, no whole-history preservation list and no project edits. It is never
  an apply-ready request: approved navigation/selection edits would still need
  fresh preparation if ownership admission became available.
- No apply, cleanup, source change, old-lock edit, package modification, history
  relocation or count-limit change occurred. All 3,240 Git-tracked or
  non-ignored existing files in the independent before/after snapshot had equal
  raw hashes; `git diff --name-status HEAD --` was empty before this record.
  This snapshot is evidence, not a required installer input or a claim to have
  hashed every ignored file. The nine earlier untracked records are included
  and remain unchanged/uncommitted.

External retained evidence on the execution host is `C:/tmp/si202/`:
`selection.json`, `derive-response.json`, `inspect-before-request.json`,
`inspect-before-response.json`, `compatibility-plan-request.json`,
`compatibility-plan-response.json`, `compatibility-plan-execution.json`,
`compatibility-diagnostic-trace.json`, `project-before-hashes.json` and
`preservation-check.json`. Commands used Python `-I -B` with the exact public
package at `C:/tmp/v0202-release/package`; derive uses explicit catalog identity,
selection, pin and external output/scratch, while both consumer operations take
their retained JSON on stdin. These host paths are not portable availability
claims; the important outcomes and identities are retained here.

## Bounded diagnosis and missing route

Hypotheses were a new candidate failure, unrelated-history budget rejection, or
incompatible old ownership evidence. Successful derive and the exception path
support the third explanation at the observed boundary. External tracing of the
unchanged public plan shows `Lock: lexical grammar` from
`contracts.validate` -> `catalog.lock_bytes` -> `read_lock` ->
`observe_installation` -> `reinstallation._owned_cleanup` -> `_prepare`.
It stops before affected-path inventory, preview and destructive work.

The old lock's catalog build inputs and 24-file engine closure retain
`tools/build-catalog.py`, `tools/derive-subset.py` and
`tools/reinstall-framework.py`. The current contract requires source paths under
`src/`, and its current engine closure has 23 files. This is an observed
historical-format incompatibility, not proof that changing one field would
complete migration. No controlled migration intervention was performed;
additional legacy compatibility differences remain untested.

The first tracing harness used text-only StringIO, which the CLI rejected before
reading its required binary stdin. Correcting the harness to TextIOWrapper over
BytesIO exposed the same product refusal. Neither run edited the package or
target. This harness failure is not a product regression or successful install.

The current reinstall guide and accepted #472 scope explicitly do not restore
RC3 direct-upgrade/historical-lock support. Reinstall cannot silently ignore
that lock, and rewriting its hashes/paths would destroy the evidence required
to establish ownership. No supported migration path has been established here.
The owner was asked whether to authorize a separate concrete RC3 migration and
ownership-verification plan, retaining the old lock and public v0.20.2 assets.

## Complete scenario assessment

The original Issue tables are ordinary requirements, not a CBF machine document;
no CBF parser or schema-validation claim applies. Every original scenario ID is
included below. Prior evidence retains its original subject and evidence level.
No source/fixture result is relabeled as this target's successful installation.

| Criterion and required observation | Evidence and result | Limit / next action |
| --- | --- | --- |
| OWN-01: records retain bytes/paths, no cleanup/implicit edits or Git deletion/rename | Prior disposable record-category test passed; this target's probe selects no records or edits and causes no Git/raw-byte change | Successful actual-target reinstall preservation remains unavailable |
| OWN-02: team skills, references, config and runtime entries survive without inferred ownership | Prior disposable custom-resource test passed; current before/after snapshot unchanged | No successful update/reinstall of this real target |
| OWN-03: committed/uncommitted managed edits conflict before destructive work | Prior fixed-subject fixture/native evidence retained | Do not inject managed drift into the real project; not rerun here |
| OWN-04: custom destination collision, including identical bytes, conflicts before writes | Prior fixed-subject fixture/native evidence retained | Not rerun on the real project |
| OWN-05: custom/history cleanup or equivalent project edits are rejected despite Git tracking | Prior fixed-subject fixture/native evidence retained; current probe contains only hash-matching old inventory/lock paths | Current engine cannot yet validate this historical inventory; caller hashes do not confer ownership |
| OWN-06: >4,096 unrelated history files do not alone block a small selection; integrity checks remain | Earlier 4,097-history packaged fixture passed; current probe does not enumerate history as installer input | Actual target stops earlier at lock compatibility, so it cannot prove successful bounded planning here |
| OWN-07: unknown ownership, plan/preimage drift, marker, link/alias fail closed without bypass | Prior selected negative evidence retained; current incompatible lock fails before mutation | Current generic diagnostics do not identify the precise field; trace supplies bounded diagnostic evidence, not new format support |
| OWN-08: authorized real install, consistent post-inspect, matching selection/adapters, only owned/approved edits, custom/record/draft preservation | **Unavailable / blocked**: no apply or post-install inspect; existing version remains RC3 | Restore/select an authorized verified RC3 migration route, then perform actual installation and full selected preservation checks |
| DOC-01: generated update/reinstall plan preserves records/extensions without directory-based ownership | Source guidance and earlier fixtures support the contract; probe does not select those resources | No accepted final plan exists for this real target |
| DOC-02: instructions reject tracked custom cleanup without ownership evidence | Current guide states Git recovery is not ownership; this operation preserves the rejected target | No destructive workaround attempted |
| DOC-03: retain precise conflicts and owner decisions; reinstall is not an overwrite shortcut | Source guidance aligned; current failure/trace and unresolved legacy decision retained | Public error is generic, not a precise managed-file conflict; no claim that drift was successfully assessed |
| DOC-04: protected resources cannot be rewritten through project edits | Existing source/fixture evidence for the 11-path boundary retained; probe has no project edits | Real-target edit plan is not yet prepared/admitted |
| DOC-05: small plan avoids history cleanup, moving and whole-history reclassification | Actual probe uses 136 old managed/lock candidates without whole-history pins; no history change or product test rerun | Independent hash snapshot is acceptance evidence only, not installation input |
| DOC-06: accepted real installation is proved by Git/raw content, not static/prior results | **Unavailable / blocked**: refusal and unchanged bytes prove no mutation, not successful installation | Must follow successful OWN-08; do not close the Issues on prior package tests |

Overall actual-target acceptance is **unavailable** because OWN-08 and DOC-06
lack a successful supported installation. This does not contradict the prior
v0.20.1-origin disposable acceptance or establish an RC3 support promise.
Source implementation, public release and this project's adoption remain
separate states. Existing independent reviews and 83 local / 253 hosted tests
are not rerun merely to format this assessment.

## Open-Issue scope repair

Read all 12 open Issues and existing label definitions. Rechecked each selected
Issue was still OPEN and lacked scope immediately before adding exactly one
label. Added `scope:framework` to #472, and `scope:mixed` to #473, #416 and #305.
#473 covers portable guidance and source-owned guidance reconciliation; #416
covers portable workflow choices and source workflow transition; #305 covers
source checkout and portable installation/recovery path budgets. These mixed
boundaries follow the current descriptions, not a new taxonomy.

Read-back confirms all 12 open Issues now have one existing scope label.
No closed Issue, existing label, body, Issue state or Project field was changed.
Provider-only label maintenance does not require a source policy change or test.
