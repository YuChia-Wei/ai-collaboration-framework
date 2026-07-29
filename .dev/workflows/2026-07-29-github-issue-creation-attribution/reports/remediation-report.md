# GitHub Issue Creation Attribution Report

## Docs Updated

- The source-repository GitHub provider contract now defines `created-by:codex` as the visible formal-Issue attribution and a hidden runtime/model/reasoning marker as detailed provenance.
- The formal Issue renderer and focused tests enforce exactly one label and marker while excluding public Proposal intake.
- The provider mapping receipt now records the four existing canaries as Stage B in progress; Project identity remains null.

## Boundary Decisions

- The label means Codex initially created or projected the Issue content. It does not mean assignee, owner, approver, or current manager.
- Proposal Issues remain attributable to their submitting GitHub users and receive no automatic Codex attribution.
- Existing closing comments remain unchanged at their original immutable `27bc777` source snapshot; updating the label did not rewrite historical delivery evidence.
- Current Issue bodies link to the merged provider-contract snapshot `e83b759` and contain the hidden detailed marker.
- The remaining 37 backlog Issues and GitHub Project remain outside this authorization.

## Validation

- Local provider contract: 17/17 tests passed before PR #25.
- Dry-run: 41 items, 5 open, 36 closed, 0 blocked; 41 labels, 41 hidden markers, and zero visible attribution sections.
- PR #25 hosted checks: package candidate, governance contract, and Ubuntu quick gate all passed.
- Provider label read-back matched name, color, and description.
- Issues #21-#24 each matched exact title, fresh-main body, hidden markers, labels, empty assignees, lifecycle state, close reason, and original closing comment.
- No Project or additional Issue was created.

## Next Task

Integrate this receipt through a continuation PR. After that, wait for explicit owner approval before creating the remaining 37 Issues and the Project.
