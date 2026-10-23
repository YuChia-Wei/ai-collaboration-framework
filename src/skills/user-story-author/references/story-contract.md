# Shared Story, acceptance and handoff contract

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

Start with the requested operation, subject, sources/revisions, target rules,
accepted decisions, template/language and current authority. Reuse supplied
information. Missing information blocks only dependent claims; mark unknowns and
ask the smallest necessary question without fabricating completion of the rest.
Facts, accepted decisions, local proposals and unknowns must remain distinguishable.
Do not invent IDs, parent links, metrics, dates, priority, approval or provider state.

A usable Story identifies the beneficiary and value (or technical/learning
outcome), scope in/out, observable acceptance and relevant failure/exception
boundaries. Bind material claims to supplied sources; distinguish absent evidence
from a contradicted claim. Preserve source IDs, statuses, accepted Given/When/Then
and non-Gherkin criteria. Gherkin conversion is optional and requires the caller's
selection; never silently change acceptance meaning or status to fit a template.

Keep three output fields distinct: **Title**, **Description**, **Acceptance
Criteria**. They can be pasted separately into Azure DevOps or another work-item
system; no provider, custom field or online record is required. Titles name an
outcome, not a checklist of implementation verbs. Description follows the selected
template. AC state observable conditions/results and applicable failure boundaries,
using source-backed measures when available; an unknown threshold stays unknown.
Do not invent tests or implementation constraints to make a criterion measurable.

Public Story context includes sources/versions, real parent/dependency references,
product decisions and unknowns with their requirement impact. Execution context,
authority, next-agent actions and continuation checkpoints MUST instead be handed
off through the workflow mechanism. Return them separately from publishable fields;
never append them to an Issue body or comment. Do not claim they were persisted
without a successful write to the selected workflow. Preserve target workflow
selection and report unavailable support without inventing a replacement store.

## Optional methods and responsibility

For requested selected knowledge, follow [the installed protocol](knowledge.md)
with capability `requirements` and the actual public operation. Planning uses
its discovery row; draft/normalize/review use their authoring row. Read only
needed leaf resources, not an undeclared BDD index. Without knowledge, common
work based on caller sources remains available with its coverage limits.

BDD discovery/formulation can clarify rules and observable examples, and DDD
discovery can clarify language. They do not authorize context/aggregate ownership,
persistence or transaction decisions. Carry concrete model questions to its
owner and software mechanism questions to the architecture owner only when needed.
GWT in AC is not test design; reuse the same example IDs when test level, data,
isolation, oracle or coverage design is later requested.
