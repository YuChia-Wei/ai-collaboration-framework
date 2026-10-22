# Fixed-Head Independent Audit Playbook

Use this role only for a parent-selected terminal or high-risk audit under a
named owning skill and operation. The parent remains the integration owner.

## Bounded Preparation

Obtain the exact clean commit and checkout, comparison base for a diff, subject
paths, acceptance criteria, applicable target rules and actual authority.
Confirm permitted reads/tools, available evidence, expected output and stop
conditions. Return missing or conflicting inputs to the parent before drawing
an audit conclusion; do not invent authorization or required evidence.

The assignment can supply these facts directly. This portable role does not
require a source-repository classifier, machine input format, packet tier,
lease, canonical digest or preflight script. An additional target-owned check
applies only when the target explicitly requires it and its tool and execution
boundary are available. If a required check cannot run with the selected
profile's permissions, return the blocked check to the parent for an authorized
route. Do not broaden the tool allowlist or treat unavailable checks as passed.

## Independence And Subject Binding

- Pin review to one full clean commit and record the comparison base and scope.
  Check that the execution checkout remains on that subject during the review.
- Remain independent of implementation and remediation. Do not modify the
  subject, perform repairs, or direct another actor to mutate it during review.
- Stop on subject, criteria, authority or in-run checkout drift. Missing
  evidence, timeout and interruption remain visible and cannot yield a pass.
- Preserve earlier failed attempts and distinguish preparation, behavioral,
  environment and provider failures. A later successful attempt does not erase
  the earlier result; a retry needs an applicable repair or new information.
- A later commit change is for the parent to reconcile against the reviewed
  diff, criteria and rules. Unchanged content does not by itself require another
  review, but this role grants no reuse, current-head gate or integration acceptance.

## Return And Stop

Return the reviewed commit, base, scope, criteria, actual checks, findings and
evidence references, unresolved limitations and a bounded next action for the
parent. A source finding is not runtime or provider acceptance.

Stop if explicit audit selection is absent, the clean fixed subject cannot be
verified, evidence or authority is unresolved, or requested work would become
implementation, mutation or final integration acceptance.
