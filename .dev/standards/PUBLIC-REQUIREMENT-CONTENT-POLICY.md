# Public requirement content policy

Rule ID: `PUBLIC-REQ-001`. Source-repository policy for new or edited public
requirement content. Related delivery: #496, #497, #498.

## Mandatory public requirement boundary

For public Epic, Feature, User Story and Issue/ticket content, including comments,
MUST describe the product need independently: problem, beneficiary or outcome,
scope, relevant scenarios, observable acceptance and real dependencies. Readers
must not need a private conversation to reconstruct the requirement.

MUST NOT publish execution authorization or its approval/revision history, agent handoff,
resume instructions or execution checkpoints in that requirement channel. Record
and retrieve authorization and handoff through the target's workflow mechanism.
An Issue system is not a substitute workflow store. If that mechanism is unavailable,
report the missing record or blocked handoff; do not silently fall back to an Issue,
comment, or another store, and do not claim a transfer occurred.

Feature inventories, requirement/design discussion, product decisions and supported
requirement revisions/status, linked
Issues, and concise completed/pending/deferred feature summaries MAY remain.
Explain dependencies such as "requires #123's API" and link relevant result evidence
without copying execution logs. Product approval/permission behavior is valid
requirement content; permission for an agent to push or merge is execution authority.
Classify by purpose and meaning, not forbidden words or headings.

Before creating or updating content, check this boundary and correct violations
within the authorized scope. In a read-only review, report the selected violation
and a bounded correction; do not edit it. Keep valid requirements, IDs, decisions,
uncertainty and acceptance meaning. Do not mandate one wording, heading order,
provider, Workflow Board deployment or new storage product. Unselected historical
records remain unchanged. Drafting or reviewing requirements never grants execution
permission or proves implementation, adoption or acceptance.

This repository uses `.dev/workflows/` for workflow authorization and handoff.
Live Issues retain requirement scope and functional status, and Project fields
retain their existing planning responsibilities. A conversation can supply the
owner decision; capture necessary continuation evidence in the workflow, never
in the Issue. This changes record placement, not the requirement for authority.
