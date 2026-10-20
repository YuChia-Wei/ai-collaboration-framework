# Installation ownership repair

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

## Results and remaining work

`python -I -B tests/run.py --suite distribution`: 80 tests passed, 0 failures,
0 errors, 0 skips, 8.975409 seconds, on the normal Windows host. Initial sandbox
attempt returned 37 temporary fixture permission errors (WinError 5), zero
assertion failures, and is retained as blocked-by-environment evidence. It is
not a successful product run. `git diff --check` passed.

The suite verifies bounded history observation and selected preview inputs,
cleanup ownership admission, exact drift paths, markers and project-edit
admission including retained recovery records. Small mocked reader observations
are not packaged installation evidence. Packaged route and independent review
remain pending.

Independent review by `security_coverage` of
`92ee2c89d5ab58912402c5789ba56659d8bb40af..ab4a1fddd19dac8256c548c3c9fa98f4aabdf096`
found one P2: the scanner compared old and prospective destination namespaces
together and rejected an owned cleanup file becoming a candidate directory.
The author accepted and repaired it, retaining rejection of unremoved parent
collisions. Two directly affected cases passed:
`python -I -B tests/framework_next/test_maintenance_contracts.py MaintenanceContractTests.test_verified_cleanup_file_can_become_a_candidate_directory MaintenanceContractTests.test_file_to_directory_transition_reaches_reinstall_preview`
(2 tests, 0 failures/errors, 0.095 seconds). The prepare/preview case uses controlled
Git/engine/candidate evidence and real path observation; it is not native
installation acceptance. Affected independent re-review is still pending.

The first local snapshot built from `ab4a1fdd` successfully (archive SHA-256
`bb1b11ed6551b29072b8cf7f188b36a609be25630bfb88f2828e54f643e03929`), before
this review repair. It has no installation acceptance and will not be used as
the final repaired subject. No published artifact was changed.

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
