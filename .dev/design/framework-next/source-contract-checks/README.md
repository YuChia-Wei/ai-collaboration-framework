# Source contract implementation handoff

Issue #368 implements the [selected P7 V1 contract](../p7-execution-selection.md).
Use the [runner/helper interface](../../../../tests/framework_next/README.md)
and [actual repair execution report](../../../workflows/2026-09-23-source-contract-checks/repair-report.md).

C1-C3/C5 are implemented as stdlib unittest cases; only the contracts layer is
available. V2/V3 callers must retain nonzero unavailable selections until their
actual modules and commands are integrated. There is no shared parser, framework
registry, receipt platform or new package member. Direct user confirmation additionally authorized four bounded source repairs:
GitSource, assembly, and PR/local-backlog metadata alias expansion.

C1-C3 now pass against the committed repaired source, and two actual Lesson
candidates match content/identity. The actual installation reader remains blocked
on its separate F: strict-root call. Coordinator must assign that reader boundary;
do not relax the parser, monkeypatch the caller or route data to another drive.
C5 aggregate and affected independent review remain incomplete.

Coordinator owns integration, shared mapping and next assignments. Root, native,
CI, independent review and all-profile build acceptance remain unclaimed.
