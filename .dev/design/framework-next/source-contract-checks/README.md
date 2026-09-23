# Source contract implementation handoff

Issue #368 implements the [selected P7 V1 contract](../p7-execution-selection.md).
Use the [runner/helper interface](../../../../tests/framework_next/README.md)
and [actual execution report](../../../workflows/2026-09-23-source-contract-checks/report.md).

C1-C3/C5 are implemented as stdlib unittest cases; only the contracts layer is
available. V2/V3 callers must retain nonzero unavailable selections until their
actual modules and commands are integrated. There is no shared parser, framework
registry, receipt platform or new package member. This work changes only the
four assigned test files and its own design/workflow artifacts.

Remaining source defects require coordinator assignment: PR/backlog metadata
must satisfy the existing no-anchor loader contract; Windows strict-resolution
backend behavior needs its owning distribution/installation decision. Do not
relax the parser or silently route native data to another drive. This branch
provides failing regression evidence rather than claiming selected acceptance.

Coordinator owns integration, shared mapping and next assignments. Root, native,
CI, independent review and all-profile build acceptance remain unclaimed.
