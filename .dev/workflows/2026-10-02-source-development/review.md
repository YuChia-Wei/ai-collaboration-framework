# Independent source cutover review

Reviewer: delegated agent `source_cutover_review`, separate from the root writer.
Actual dispatch selected `gpt-6-sol` / `high`; this records the invocation setting,
not a provider billing claim. Owning method: installed `code-reviewer` common
review. Authority: direct owner decision in [adoption.md](adoption.md).
Criteria: [review-scope.md](review-scope.md).

Reviewed immutable base `4f231fe7f08eaa9ae296ec243be524658f8d3849` to head
`3ca6756cc088241b668378460aa827c9b24cf0f1`, tree
`69868b01ebae7931b63a7ad72b44e85d17407a74`. The reviewer observed clean state at
start/end; root performed only ignored validation/provider preparation during
the review. No tracked repair was performed by the reviewer.

The returned report found **no supported actionable findings** in the inspected
policy/root bilingual/YAML/PR form, selector/runner/tests/workflows/dependencies,
workflow records and optional initialization metadata/resources/seeds. It traced
both diff sides, suite mapping, workflow ownership and rejection of nonzero,
skipped or empty reports. The CI inspection covered Windows/Python 3.13, exact
event SHAs, pinned actions and read permissions. Initialization remained optional
and authoring-only. Old U001 wording was inspected; explicit adopted-source
precedence resolved its applicability rather than silently waiving retained work.

The reviewer ran `git diff --check` on the selected range and used tracked-file
reads because the discovery index was bound to earlier `7e48f656`. No test suites,
provider calls, installation or agent scenarios were executed by this reviewer.
Local test evidence remains the coordinator's execution, not the reviewer's.
Hosted/source activation, real consumer initialization/custom-content preservation,
native/release acceptance and merge admission are separate evidence classes.

## Affected follow-up and repair

The same independent reviewer inspected delta `3ca6756c..c82b0c32` at clean head
`c82b0c32188d0d1fa03699f33b33dff9615a9fec`, tree
`a6cb7554fcb83e71554a7dd5afc7bd5464cb92e7`. It found one blocker: the incidental
snapshot workflow comment change makes `.github/workflows/package-candidate.yml`
enter the diff, but this separately retained release workflow is outside the
source selector's selected ownership and is rejected before tests. The reviewer
confirmed the new evidence/status records otherwise represented its prior report
and pending hosted state accurately; it did not assert equal trees.

Root restored that one comment to its original reviewed bytes. Release workflow
behavior remains unchanged and the retained #418 comment stays historical. This
removes the incidental path from the base-to-head diff without broadening the
selector's release authority or weakening its rejection. The repair and new
failure records receive affected review on the next immutable head.

At head `cc4b42d9070d952370abd3ffa03b6c88381fd482`, tree
`989febaeec3e5046132990db23752a6c9bb9f396`, the reviewer confirmed the blocker
removed: the snapshot workflow is byte-identical to the original reviewed/base
file and absent from the net diff; selector behavior is unchanged. Its independent
substantive review remains applicable to unchanged implementation/policy bytes,
with an explicit new head binding rather than an assertion of equal full trees.
One minor evidence sentence still listed enablement as pending; this closeout
corrects it. The original snapshot comment remains a disclosed historical wording
limit within the separately retained release workflow. It is not used to infer
current provider state. These evidence/status updates need one final affected
review and hosted head binding recorded on PR #428 before merge.
