# Issue #351 design delivery report

Report ID: remediation-report-2026-09-23-problem-frame-compliance-design.
Owner: ai-context-governance. Created/updated: 2026-09-23T10:15:03+08:00. Status: final design report.
Template: ai-context-governance-remediation-report 2.0.1,
`.ai/assets/skills/ai-context-governance/templates/ai-context-remediation-report-template.md`.
U001 adaptation: bounded design report, not an assessment-resolution or
independent verification receipt.

## Completed design scope

Recommended CBF problem-frame.cbf@1.0.0, closed single JSON snapshots,
one package owning producer/reader/structure validator/version/migration refusal,
create-only persistence, and a separate instruction compliance capability.
SWF/legacy YAML remain preserved and machine unsupported; no silent family
loss. Optional .NET requires explicit target authority/runtime/evidence.
D351-01..05 require coordinator selection before source work.

[Design](../../../design/framework-next/problem-frame-compliance/README.md),
[format/API](../../../design/framework-next/problem-frame-compliance/format-contract.md),
[compliance](../../../design/framework-next/problem-frame-compliance/operations-and-compliance.md)
and [implementation/P7 handoff](../../../design/framework-next/problem-frame-compliance/implementation-handoff.md)
are complete for review. The schema and example are proposals, not implemented
or validated format support.

## Evidence and limitations

Source inventory uses direct Git-tracked Markdown/YAML/JSON and a selected shell
helper, with baseline Git blobs and raw SHA-256 in
[source-evidence.json](../evidence/source-evidence.json). No graph/shared index
was changed: the work inspects non-code contracts/templates/configuration and
the directly named shell script, not code-symbol discovery.
The bounded tracked .dev/problem-frames inventory supports the local CBF/SWF
comparison; no whole-history or downstream inventory is claimed.

[Issue bodies](../evidence/related-issues.json) were read with gh issue view for
351/342/316/318/317, with no provider mutation. 351 OPEN, 342 CLOSED, and the
three older Issues OPEN at observation. Scope overlap does not close them.
No private runtime, credential or unrelated target source was collected.

Preserved preparation failures: the initially guessed coordinator reports path
for p5-selected-contract.md was absent; the report link resolved the actual
.dev/design/framework-next path. The first sandbox GitHub read failed because
the configured loopback proxy refused connection. The scoped require_escalated
read succeeded. Neither failure is hidden or treated as product failure. The first batch write exceeded the Windows command-line limit (os error 206) before process creation; per-file scoped writes then succeeded. This was a preparation failure, not product execution.
A memory keyword lookup yielded no needed design authority; current tracked
evidence and live Issue read-back were used instead.

## Actual checks

Initial direct check: 12 UTF-8 files, five JSON documents, one YAML document
and 18 local Markdown links read/parsed/resolved without error. Final staged
check: 13 UTF-8 files, six JSON documents, one YAML document and 19 local links;
no errors. Staged scope and git diff --cached --check passed. The exact planned
message validator passed before commit; its bytes are hash-bound in
[checks.json](../evidence/checks.json). Only UTF-8,
JSON/YAML syntax, changed references/content, exact scope/Git/diff and the sole
allowed full planned commit-message validator are permitted. Syntax is not
schema validation, product execution, compliance, compatibility or independent
review. No product import, help, test or validator beyond the message exception
was used.

## Disposition

D342-06/#351 design responsibility: completed for selection, with the local
commit as the handoff boundary. The exact final HEAD/status is returned in the
final task response; no self-referential commit hash is fabricated here. Source implementation: outside this Issue. Assessment
ASM-20260923-00-6oq: no finding-resolution claim. Verification assessment:
deferred-by-owner under U001, not fabricated. Provider integration and Issue/
Project status: coordinator-owned, not performed here.

All product CLI/help, schema validation, tests/fixtures, build/package/install,
migration/compatibility, audit/lease/effective-rule/handoff/legacy validation and
CI are **deferred-by-owner**. Owner: **program #322 coordinator / P7**.
Reason: source redesign U001. Next: select and execute redesigned checks against
implemented source, observe actual outcomes and retain limitations.

## Next task

Coordinator reads local commit/final HEAD and clean status, selects D351-01..05,
then assigns S351-A, S351-B and later exact shared mappings. The proposed shared
row is in implementation-handoff.md. No callback, push, PR, merge, shared-index
write or Issue closure is performed. Root cutover, publication and target
adoption remain separate.
