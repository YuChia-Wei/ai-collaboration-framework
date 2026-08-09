# LESSON-<CATEGORY-CODE>-<NNN>: <Title>

> This template creates a non-normative evidence record. It does not authorize
> implementation or replace a standard, policy, guide, runbook, assessment, or
> workflow.

| Field | Value |
| --- | --- |
| Lesson ID | `LESSON-<CATEGORY-CODE>-<NNN>` |
| Category | `<category>` |
| Lifecycle | `<active-or-promoted-or-superseded>` |
| Normative Authority | `none` |
| Origin Evidence | <durable repository or provider references> |
| Evidence Subject | <revision, run, incident, or assessment identity> |
| Promotion Target | `none` or <authorized target link> |
| Supersedes | `none` or <lesson link> |
| Superseded By | `none` or <lesson link> |

## Origin Evidence

Identify the durable sources, subject revision or execution identity, and which
facts came from each source. Separate confirmed evidence from inference. Do not
copy mutable logs when a stable report or evidence summary already exists.

## Context And Symptom

Describe the observed situation and symptom without generalizing beyond the
evidence.

## Confirmed Conditions And Root Cause

List the conditions that were reproduced or read back and the confirmed cause.
Name unresolved points explicitly.

## Reusable Conclusion

State the learning that can be reused within the confirmed conditions. Keep it
descriptive and non-normative.

## Non-Applicable Cases

List conditions where the conclusion does not apply or where a similar symptom
has a different cause.

## Remediation Example

Record the remediation that was confirmed. Label host-specific or
environment-specific commands as evidence examples, not portable defaults.

## Verification

Record the exact verification route and durable outcome. Preserve earlier
failed or blocked evidence rather than relabeling it.

## Promotion And Supersession

Record the current promotion target, successor, or retained `none` values. A
guide, runbook, policy, or validator change needs separately authorized work.

## Security And Portability Boundary

Exclude credentials, secrets, private endpoints, hostnames, and raw machine
state. Explain which facts are reusable and which remain local to the observed
environment.
