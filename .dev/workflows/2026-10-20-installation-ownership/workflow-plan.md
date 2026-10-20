# Installation ownership repair

## Current continuation — 2026-10-21

Completed: this project is now installed from public v0.20.2. The independent
review of `6a552659b0aec503237bae6c0db4b7cbc2ac0c58` reported no actionable
findings; actual public post-inspect reports 137 owned members and no drift.
All 4,386 files outside the managed/edit set, including nine original untracked
records, retained exact bytes at the immediate post-install observation.
See [actual acceptance and all OWN/DOC criteria](self-install-v0202-accepted.md).
`INSTALL` and the local workflow are complete; provider states remain separate.

The owner now explicitly requests self-reinstallation from public v0.20.2,
preservation of custom content/history, and assessment against #472/#473.
The source repair was integrated through PR #474 and v0.20.2 was published.
This continuation starts from `3c7434fd3ea65bcbf519fef3e3ca232a0bc59043` on
`codex/2026-10-21-self-install-v0202`; it does not authorize a new product
compatibility implementation, release replacement, Issue closure or another
push/PR/merge. The nine prior untracked records remain untouched.

The initial `INSTALL` attempt stopped before apply: both the formal package's
inspect and breaking reinstall plan rejected this project's RC3 lock.
See [the actual-target acceptance assessment](self-install-v0202-assessment.md)
for all OWN/DOC criteria, retained commands/results and the owner checkpoint.
This workflow retains the unique real-target compatibility/recovery state; it
does not reopen the completed source implementation or require its tests again.

The owner subsequently approved the project-specific RC3 migration plan and
explicitly authorized building the procedure, isolated rehearsal, recovery
validation, necessary independent review, then direct installation of public
v0.20.2 in this project. Preserve custom content, history and all nine existing
untracked records; assess #472/#473 afterward. This supersedes the earlier
compatibility checkpoint, not the product's supported compatibility boundary.
Use the exact installed RC3 engine pin for read-only ownership verification,
retire only its verified 135 members and lock, then use the unchanged released
v0.20.2 public API. The local bridge is `rc3-migrate.py`; it is not packaged.

Validation is selected by the actual installation/recovery risk: one partial
retirement and refusal to overwrite unknown bytes; one interrupted public new
installation followed by official restore and old-file restoration; one complete
isolated migration with paired navigation edits and preservation read-back.
Record coordination-file disposition explicitly. Successful completed installs
cannot be rolled back through replay of an already completed operation.
Freeze the implemented bridge and evidence in a local commit for independent
read-only review before actual-target writes. Then observe quiescence afresh,
snapshot the target, execute and read back the accepted installation criteria.
No push, PR, merge, Issue closure, new release or history cleanup is selected.

## Initial implementation authority — 2026-10-20

Owner authorized implementation of #472 and #473, necessary tests and independent
review on 2026-10-20. Target is v0.20.2. Reinstallation, publication, push, PR,
merge and provider state changes are not selected. Preserve both existing
untracked workflow directories. Parent is the sole tracked writer.

The accepted behavior is OWN-01–07 and DOC-01–05: verified installed ownership,
default preservation of unknown/custom content, conflicts for managed drift
(including committed changes), and bounded observation rather than enumerating
project history. OWN-08/DOC-06 require separately authorized real installation;
source or disposable fixture tests cannot establish that result.

Implementation uses slice-implementer, generic mode, for one installation
protection outcome. Source radius: distribution ownership/planning/reinstall
helpers, their immediate tests and portable installation instructions. Public
request and lock versions, member limits and published assets stay unchanged.
Graph lookup returned stale catalog source locations; exact Git-tracked source
reads are the explicit fallback for the affected functions.

Compatibility decision: after the exact change and effect on existing custom
skills were explained, the owner explicitly approved the project_edits allowlist
as a v0.20.2 protection correction. It narrows previously accepted arbitrary
edits without adding required fields or changing API/lock versions. Other
project files use a separately authorized project edit, not installer authority.
Unknown legacy ownership fails closed; this repair does not invent RC3 upgrade
support. Older destructive requests lacking verified ownership are refused.

## Work and validation

1. Implement owned-path admission and bounded preview; retain destination,
   alias/link, marker, Git baseline and drift checks.
2. Resolve project-edit compatibility; align the canonical portable guidance
   and actual request producers. No new custom-resource registry.
3. Run affected distribution tests for ownership, preservation, collision,
   preimage, preview and project-edit behavior. Add missing regression cases.
   Select disposable packaged-route verification for the changed installation
   boundary after the implementation is stable; this is not a source-project
   reinstall or release acceptance.
4. Commit the validated implementation, then obtain independent read-only
   review of the fixed base-to-head diff. Repair and return affected findings.
5. Report local completion and remaining provider/installation/publication
   boundaries separately. Hosted source gate is required for future PR
   integration; no hosted pass is claimed here.

Two read-only sub-agents assess existing custom skill/resource creation rules
and patch compatibility at the input commit. Parent integrates their evidence
and future-work recommendation; they have no write or registry authority.

## Results and acceptance boundaries

`python -I -B tests/run.py --suite distribution`: 80 tests passed, 0 failures,
0 errors, 0 skips, 8.975409 seconds, on the normal Windows host. Initial sandbox
attempt returned 37 temporary fixture permission errors (WinError 5), zero
assertion failures, and is retained as blocked-by-environment evidence. It is
not a successful product run. `git diff --check` passed.

The suite verifies bounded history observation and selected preview inputs,
cleanup ownership admission, exact drift paths, markers and project-edit
admission including retained recovery records. Small mocked reader observations
are not packaged installation evidence. This 80-test run preceded the review
repair below; it is not relabeled as an 82-test run of the final commit.

Independent review by `security_coverage` of
`92ee2c89d5ab58912402c5789ba56659d8bb40af..ab4a1fddd19dac8256c548c3c9fa98f4aabdf096`
found one P2: the scanner compared old and prospective destination namespaces
together and rejected an owned cleanup file becoming a candidate directory.
The author accepted and repaired it, retaining rejection of unremoved parent
collisions. Two directly affected cases passed:
`python -I -B tests/framework_next/test_maintenance_contracts.py MaintenanceContractTests.test_verified_cleanup_file_can_become_a_candidate_directory MaintenanceContractTests.test_file_to_directory_transition_reaches_reinstall_preview`
(2 tests, 0 failures/errors, 0.095 seconds). The prepare/preview case uses controlled
Git/engine/candidate evidence and real path observation; it is not native
installation acceptance. Independent re-review of
`ab4a1fddd19dac8256c548c3c9fa98f4aabdf096..66eca564fcef5e53897ed6ec2986727948b6513f`
resolved the finding and found no new actionable issue in the affected scope.
The full review boundary and limitations are in [independent-review.json](independent-review.json).

The first local snapshot built from `ab4a1fdd` successfully (archive SHA-256
`bb1b11ed6551b29072b8cf7f188b36a609be25630bfb88f2828e54f643e03929`), before
this review repair. It has no installation acceptance and will not be used as
the final repaired subject. No published artifact was changed.

The final local package was built from
`66eca564fcef5e53897ed6ec2986727948b6513f` in an isolated clean worktree:

```text
python -I -B .github/scripts/build-release.py --repository F:/git-worktree/v0202-ownership-validation/ai-collaboration-prompts-dotnet-backend --source-commit 66eca564fcef5e53897ed6ec2986727948b6513f --tooling-commit 66eca564fcef5e53897ed6ec2986727948b6513f --workflow-commit 66eca564fcef5e53897ed6ec2986727948b6513f --workflow .github/workflows/package-candidate.yml --run-id local-ownership-validation --run-attempt 2 --work-root C:/tmp/aicf-0202-build2 --output C:/tmp/aicf-0202-output2
```

Build passed; final archive SHA-256 is
`c6e68ec42e96ea6b8395cef053daa4c7650eeb9d71e73f93d6a6bbd99be13de3`.
The local candidate's generated version is `0.0.0-rc.113166573174000`, not a
published v0.20.2. Both extracted packages matched their original archive bytes
(482 files each); the old origin is the immutable public v0.20.1 archive.

Disposable native Windows checks used the packaged CLI entry points without
importing product implementation into the driver. Commands:

```text
python -I -B .dev/ai-context/local/ownership-trials.py C:/tmp/aicf-self-0201-20261020/package C:/tmp/aicf-0202-output2/package C:/tmp/own202-t1
python -I -B .dev/ai-context/local/ownership-trials.py C:/tmp/aicf-self-0201-20261020/package C:/tmp/aicf-0202-output2/package C:/tmp/own202-t2
python -I -B .dev/ai-context/local/ownership-trials-continue.py C:/tmp/aicf-self-0201-20261020/package C:/tmp/aicf-0202-output2/package C:/tmp/own202-t2
```

The first setup stopped before apply because the driver omitted the existing
configuration preservation pin. The second setup reached 16 successful checks,
then stopped because the driver expected `owned-drift` for a reinstall hardlink;
the implementation correctly returned the earlier `hardlinked-file` rejection.
The corrected continuation retained those successful checks, rechecked the
hardlink case and completed the remaining cases. Neither harness interruption is
reported as a product pass. Requests, responses and driver files are local
diagnostic artifacts, not new product tooling or a required validation system.

[native-validation.json](native-validation.json) retains 26 completed cases:
25 expected refusals with unchanged project bytes, and one public-origin update
and reinstall scenario with successful post-inspect. That scenario preserved
19 custom/record sentinels (apart from the explicitly approved additive AGENTS
navigation edit) and all 4,097 unrelated history files. Reinstall observed only
14 affected paths and one explicit preservation pin; no `.dev` tree was copied
into preview. Protected Git diff was empty. Reinstall changed no file bytes
other than its new lock installation identity.

| Criterion | Outcome in this scope | Evidence |
| --- | --- | --- |
| OWN-01 | Passed in disposable fixture | Seven record categories retained; protected Git diff empty |
| OWN-02 | Passed in disposable fixture | Custom skill entries, support and configuration retained across update/reinstall |
| OWN-03 | Passed in disposable fixture | Uncommitted update and committed reinstall managed drift rejected with exact path |
| OWN-04 | Passed in disposable fixture | Byte-identical custom destination rejected in both routes |
| OWN-05 | Passed in disposable fixture | Four protected path examples rejected through cleanup and both project-edit routes |
| OWN-06 | Passed in disposable fixture | 4,097 unrelated history files retained with bounded 14-path inventory |
| OWN-07 | Passed in selected source and native cases | Missing ownership, plan drift, markers, hardlinks, aliases and preimage protections; not an exhaustive platform/recovery matrix |
| OWN-08 | Not run; deferred to owner-selected real installation | Disposable fixture success does not establish source-project or team-project adoption |
| DOC-01 | Source guidance aligned; fixture corroboration | Default preservation and bounded ownership in both guides and packaged README |
| DOC-02 | Source guidance aligned; fixture corroboration | Git tracking never substitutes for installed ownership |
| DOC-03 | Source guidance aligned; fixture corroboration | Managed drift and unowned collisions retain conflicts; no overwrite shortcut |
| DOC-04 | Source guidance aligned; fixture corroboration | Shared 11-path project-edit allowlist and explicit review requirement |
| DOC-05 | Source guidance aligned; fixture corroboration | Bounded affected-path planning; no history reclassification or limit increase |
| DOC-06 | Real installation not run; deferred to owner | Guides distinguish static, source, fixture and installation evidence |

DOC outcomes are source review and deterministic fixture evidence, not an AI
actor trial following the guides. Source AGENTS/CLAUDE and generated installed
resources required no change. That local implementation phase completed at
`b33bad07`; it is reopened for the owner-authorized review remediation below.
Hosted source CI, PR acceptance, integration, Issue closure and publication are
not performed. Issues #472/#473 remain open on provider read-back.
Real installation requires separate authority and reconciliation of the target's
actual installed ownership; this change does not restore an RC3 migration route.
No test rerun is selected merely for these final record changes.

## Custom resource follow-up

Read-only agents event_evolution and performance_ownership assessed the fixed
input independently from the dirty implementation. Existing canonical sources
already preserve managed core and projections (governance maintenance method
lines 19–32; initialization method lines 156–161). The legacy ownership registry
is not a current custom inventory. Selection and Lock2 are closed catalog and
installed-state contracts; they cannot accept arbitrary custom skill IDs.

v0.20.2 includes only installation documentation clarification: choose a
project-owned authoring location, preserve managed core, maintain the target's
existing index/reading map where applicable, and distinguish navigation from
runtime discovery/adoption. No new skill operation, schema, mandatory registry
or historical backfill is introduced; unregistered resources remain protected.

The owner selected v0.21 or later for further evaluation based on actual use.
Future candidate: target-owned custom AI resource creation/discovery lifecycle.
Before designing a registry, collect representative consumer cases and identify
the target's owner, runtime, existing index and collision handling. Candidate
acceptance: new resources have an agreed canonical path and reachable navigation;
managed-name collisions stop before writes; targets without conventions obtain
an explicit placement decision; unrelated historical resources remain untouched;
creation, navigation, discovery, adoption and execution are reported separately.
Mandatory registration, stable-ID/CRUD tooling, automatic activation, importer
support and migrations require separate requirements and compatibility decisions.
This is a deferred plan, not a scheduled release or a created provider Issue.

## Reopened review remediation — 2026-10-21

The owner supplied two external reviews of `92ee2c89..b33bad07` and authorized
the necessary repair, regression tests, documentation and independent re-review.
The nine untracked files in the two earlier workflow directories must remain
unchanged and uncommitted until their own work resumes. No push, PR, integration,
actual project reinstall or publication is selected. Task `FIX` and the original
review/native results remain historical evidence for their stated subjects;
task `REVIEWFIX` owns this follow-up.

Findings and accepted bounded behavior:

- External R1 / F-02: verified old managed members absent from the candidate
  must be explicitly cleaned or preserved before preview/cleanup. Preserve the
  existing explicit keep option; do not adopt the second review's stronger
  `owned <= clean` suggestion, which would forbid intentional preservation.
  Unknown custom/history files still need no classification. An explicit kept
  member leaves new lock management and may retain runtime discovery or broken
  dependencies; docs must explain that consequence.
- External F-01: `execute(apply)` must accept an old cleanup file becoming an
  ordinary parent directory of candidate members after successful installation.
  An actual file, link or unrelated directory remains a failure. The earlier
  `66eca564` repair only covered prepare/preview; it did not fix this final check.
- Documentation: explicitly describe missing managed files as drift, and map
  #473's classification requirement onto existing cleanup/preservation/edit/
  preview/diagnostic fields. Do not claim the owner waived output classification
  or that `preserved_unknown` enumerates all retained resources.

Validation selection and test necessity:

- Extend the existing prepare/preview regression through real
  `reinstallation.execute(apply)` with real disposable filesystem changes;
  the nested installer and external Git/ownership admission remain controlled
  dependencies. Include legal directory transition, file remnant and unrelated
  directory outcomes. Replace the preview-only test rather than duplicating it.
- Add one parameterized old-member disposition test: omitted, cleanup and
  explicit keep. Assert refusal before preview/write or the actual final file
  presence, respectively. The two added/expanded tests have six distinct rows.
- Keep the separate unremoved-parent collision case: it covers admission before
  cleanup, unlike the final-state apply cases. Retain the 4,097-history boundary
  fixture for OWN-06, but replace its brittle exact read-call count with the
  meaningful condition that unrelated history/custom files are never read.
- Run the affected distribution suite once after both fixes to cover shared
  admission and final-state behavior. No new OS/actor matrix, performance
  benchmark, registry checker, package rebuild or repetition of the previous 26
  packaged scenarios is required by these two narrow corrections. The real
  reinstallation wrapper and filesystem behavior are exercised directly; nested
  installer implementation, public format and packaging are unchanged.
- Obtain independent read-only review of the fixed follow-up commit, including
  whether the test scope or rejection rules are unnecessarily restrictive.

Before product edits, the expanded apply test reproduced F-01:
`cleanup-incomplete` instead of `reinstalled`. The first R1 test setup lacked its
`.ai` parent (three fixture errors, not product evidence); after fixing setup,
only the omitted row failed with `planned` instead of `blocked`, reproducing R1.
Cleanup/explicit keep already passed. Commands were the two selected methods in
`tests/framework_next/test_maintenance_contracts.py` using Python `-I -B` on the
normal Windows host; no actual project installation was touched.

The first external review reports 82 distribution tests passed on `b33bad07`
in 8.03 seconds. This is attributed supplied evidence, not a run by this author.
The second external review reports static inspection only. Neither report
establishes the new repaired subject's validation or independent acceptance.

Author validation after both repairs:
`python -I -B tests/run.py --suite distribution` passed 83 tests, zero failures,
errors or skips on native Windows (runner duration 9.235719 seconds; unittest
reported 8.997 seconds). This is the current follow-up run, not a relabeling of
the earlier 80/82 results. The two reviewed regressions pass all six rows.
Independent reviewer `/root/security_coverage` reviewed the immutable
`b33bad07c980fe3c86925d04cf2008eca1d4f8c5..b0da96993e681eb0c30ad2079c3ca53192a7e47a`
diff and direct dependencies. Both external R1/F-02 and F-01 are resolved in that
scope; no new actionable finding was reported. The reviewer traced the actual
apply/final-observation path and found no unnecessarily restrictive relevant
test or need for a broader matrix. Review details and evidence limits are in
[independent-review-followup.json](independent-review-followup.json).

`REVIEWFIX` is complete. The local workflow is complete again; integration,
actual target installation and release boundaries remain unchanged. All nine
untracked prior workflow files matched their pre-repair raw hashes and remain
uncommitted at the owner's direction. Final changes after the reviewed source
commit only record the review and lifecycle; no behavioral test rerun is selected.
