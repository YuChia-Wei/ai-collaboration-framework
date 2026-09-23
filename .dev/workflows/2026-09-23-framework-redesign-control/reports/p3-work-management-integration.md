# P3 work-management source integration

Coordinator source/content inspection under U001, not independent audit or runtime acceptance.

## Received subject and inventory

Initial source delivery: `5e632ed50242f13b44bec1884de24c496f5a93ea`, assigned F:/framework-next/335, clean status read back. It preserves the design checkpoint and starts from joint contract `0d0556d4c60105a28eb39cfb06efab9b069728cb`. Its 27 changed paths stay inside the two package and two owned design/workflow roots.

Direct parsing/comparison of the fixed commit's Git inventory, metadata and integration-proposal.json confirms pr@0.1.0 has exactly 10 members and local-backlog@0.1.0 exactly 8. Both use metadata v2, empty required/optional dependencies and one read_schemas value equal to the writable schema. This is a direct content comparison, not loader execution/schema validation or assembled package evidence.

## Inspection coverage and finding

Source inspection covered the package-owned provider adapter, public pr.fs call boundary, explicit request/grant/expected-state checks, remote pre/post reads and uncertain-mutation reporting; PR immutable Git subject and validation binding; isolated config v2, closed metadata, schema guards, store constraints, single-record publication/cleanup and local backlog transitions. AST text inspection compared shared owner-local function bodies without importing them. Private cross-skill imports were not introduced in this source set.

A fresh non-persisted F: graph excluded both new scripts directories. Exact committed source and a direct AST symbol inventory were therefore used for those known paths. Graph output did not attest an index SHA and was navigation only; no absence claim follows from it.

**CR335-001 — worktree Git config omitted from comparison preflight.** At the initial delivery, pr.py git_subject inspects `git config --local --null --list`, then performs a diff whose effective configuration can also include config.worktree. [Git's --local/--worktree and scope documentation](https://git-scm.com/docs/git-config) establishes that distinction. Worktree-specific diff.* or include/includeIf input can bypass the selected rejection policy, for example diff.orderFile. This is a source-backed finding, not an executed reproduction. The original same task is assigned a minimal owned-source/docs correction; no fixture, product call, tests or repository Git-setting changes are authorized by this correction.

Finding status: source-corrected; runtime verification deferred to P7. Corrective commit `5409641f19244bc44467af7fba3fc496d7f5195c` directly follows the preserved initial delivery. Its eight changed paths stay within the assigned PR/design/workflow roots. The affected source diff now inspects both --local and --worktree through the existing bounded/sanitized helper, explicitly disables include expansion during each read, and applies the same diff/include/promisor rejection to both. Existing environment sanitization, pinned recipe and output/time bounds are unchanged. Documentation and receiving records agree with that scope. Coordinator read back the clean worker branch and inspected this affected diff; no runtime reproduction was performed. The package inventory and local-backlog source are unchanged by the correction.

## Explicit limits and next action

One cooperating filesystem/provider writer remains a requirement; pre/post checks are not arbitrary-writer CAS. Caller grant/evidence references are checked for binding, not independently authenticated. GitHub operations stay same-repository GitHub.com draft create/title-body update with no blind retry. Provider/schema/path/runtime behavior remains unexecuted. Default store-parent constraints and bounded response limits remain visible for P7.

The initial source and corrective commits are now locally integrated with their identities preserved. Online PR integration and the resulting Issue/Project read-back are next. The full five-package manifest/profile continuation for #337 waits for actual #334 delivery as well. No speculative mapping or root runtime cutover. Product CLI/help, tests, schema validation, provider trials, builds/install/migrations and CI remain deferred-by-owner under U001 to program #322/P7.
