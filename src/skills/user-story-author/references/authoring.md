# Draft or normalize a Story

Apply the [shared contract](story-contract.md). Select the caller/target template
before bundled defaults. Choose user-value for an actor's outcome, business-rules
for a policy/check decision, technical for an independent technical outcome or
bounded research adaptation. Explain a non-obvious selection briefly. A value-led
Story may include Expected Behavior/Business Rules when useful; that flexibility
does not create a fourth compulsory template.

For draft, map supplied intent, decisions, examples and constraints into Title,
Description and separate Acceptance Criteria. The five primary Description
sections normally remain visible; mark a material missing input as unknown with
its impact instead of filling it with invented prose. Omit empty Open Questions.
Caller templates may use a different structure. Add only supported detail;
input/output/UI, rule priority, versions and deployment are conditional, not defaults.
Use existing FR/BR/TR identifiers when provided. If useful, propose explicit local
labels; do not pretend those labels were accepted or assigned by a provider.

For normalize, first identify allowed changes and source meaning/status. Preserve
custom templates, terminology, IDs, accepted GWT and non-Gherkin AC. Record actual
material changes (such as moving a supplied rule to its matching section) and
flag ambiguity or conflicts for their owner. Do not silently strengthen/weaken AC,
resolve an unknown, change approval or translate criteria into another form.
If no material change was made, say so. Suggestions outside scope stay suggestions.

Check value/outcome, boundaries, source support, observable AC and handoff sufficiency.
Missing necessary decisions remain visible; do not force PRD, spec or test-design
stages to compensate. Return the fields plus relevant portable context, actual
normalization changes and remaining decisions. No write beyond the selected destination.
