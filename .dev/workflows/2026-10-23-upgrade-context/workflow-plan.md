# Upgrade context delivery

## Authority and baseline

On 2026-10-23 the user requested a latest-version recheck, solution arrangement,
Feature/User Story creation and development. This authorizes the local source
implementation and necessary validation. Push, PR, merge, release and downstream
installation remain separate. Public requirements are #500, #501 and #502;
authorization and continuation remain in this workflow.

Local and remote main were both 83df8fcef8b2b05388eb876490fb148f75e8f79a.
The worktree was clean. Compared with the prior a7ecb86 assessment, root starter
0.2.4 adds public requirement rules but the refresh boundary and installer
not-assessed results still lack an actionable context handoff. Prior preview
observations are historical, not newly executed downstream acceptance.
Graph discovery located inspect but does not establish complete current coverage;
material conclusions use the selected current tracked sources.

## Delivery design

One cohesive branch covers #501 and #502. Add advisory context_follow_up only to
consistent installed inspect and successful apply/unchanged. Do not read root
semantics or imply a confirmed mismatch. It persists on subsequent inspect,
because context completion remains target-owned and no second ledger is created.
Keep recovery/error diagnostics and writes unchanged. Use existing refresh and
governance operations; strengthen their upgrade handoff and thin root navigation.
Update product guidance for in-place preview callers without rewriting historical
F: scripts or applying the source changes to the preview.

## Validation plan and state

Use focused maintenance contract tests for installed/uninstalled/drift/marker
inspect and apply/unchanged/failure/recovery output boundaries. They use mocked
observations, not an installation acceptance claim. Check source package/version
consistency and changed Markdown links. Source hosted gate remains required for
future integration. Independent scoped review is required for the installation
output contract and instruction changes against an immutable commit.

IMPLEMENT source changes and author inspection are complete. The installer adds
only an output advisory; refresh keeps its existing authority and hands selected
rule changes to existing governance. Source package versions are init 0.2.5 and
governance 0.1.3. Installed source-project projections remain unchanged.

Validation on 2026-10-23 with Python 3.13.14:
- `python -I -B tests/framework_next/test_maintenance_contracts.py`: 33 passed,
  including unchanged apply remaining read-only while returning the advisory.
  Fixtures used process-local TEMP/TMP at verified RAMDRIVE F:/aicf500-context;
  fixture cleanup completed. This is mocked/fixture evidence, not target adoption.
- `python -I -B tests/framework_next/test_contracts.py`: initially failed two
  manifest/metadata version comparisons. Synchronized the two manifest versions;
  rerun: 12 passed. No unrelated versions changed.
- Changed documentation/reference local links: six files checked, no missing
  local paths. `git diff --check`: passed. Author inspected the complete diff.

Next: independent scoped read-only review of the immutable implementation commit,
then any separately authorized push/PR and current-head hosted Source change gate.
Independent review has not been performed; author checks do not substitute for it.
No full installation matrix, runtime actor trial or publication is selected.
Feature #500 and Stories #501/#502 remain open; local implementation is not
integration or Issue completion. The workflow remains in progress for review.

Preferred eventual integration is linear: this is one cohesive outcome without
a separate migration or release boundary. Integration is not performed here.
