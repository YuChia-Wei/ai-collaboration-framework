# Shared Story, acceptance and handoff contract

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

For portable handoff, provide concise context beside the fields (or in the target's
chosen location): sources and their versions/status; real parent/dependency
references or clearly labelled local proposal labels; accepted decisions; unknowns
and their impact; smallest next step and current authority/required owner decision.
Include only relevant dependencies, identifying none known versus not established.
A receiving agent must be able to continue from the artifact without private chat.
Do not impose custom provider fields, a work-item hierarchy or an execution
workflow. A draft/review is not approval, implemented behavior or executed acceptance.
