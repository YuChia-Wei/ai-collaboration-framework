# CI-001 And CI-002 Local Static Slice

## Completed

- Selected the official Node.js 24-native artifact majors:
  `actions/upload-artifact@v7` and `actions/download-artifact@v8`.
- Preserved candidate and publication artifact names, paths, retention,
  compression, missing-file failure, inter-job naming, tag revalidation,
  checksums, archive parity, and release mutation boundaries.
- Added PR-scoped concurrency to Governance, Portable Gates, and Package
  Candidate. Only pull-request runs cancel superseded executions; manual runs
  remain serialized without cancellation.
- Added `.dev/assessments/**` to Portable Gates and removed the concrete
  v0.5.0 workflow-instance trigger from general Governance.
- Defined fail-closed contracts for all four workflows, including trigger
  paths, jobs, timeouts, permissions, artifact handoff, and mutation ownership.
- Documented the self-hosted runner floor of 2.327.1 and the intentional
  fast-Python-governance versus full-portable-gate overlap.

## Local Verification

- GitHub workflow lifecycle contract: 5 passed.
- Governance workflow contract: 7 passed.
- Packaging release-workflow contract: 3 passed.
- Aggregate runner fail-closed regression: 27 passed.
- Shell asset parity and AI-context validation: passed.
- Deprecated active artifact action literals: none.

## Remaining Decision And Hosted Boundary

`releases/release-phase-checks.yaml` and
`validate-ai-context-release-state.py` are intentionally fixed to v0.5.0.
Replacing the singleton with v0.6.0 would destroy historical revalidation.
The recommended repair is
`releases/<version>/release-phase-checks.yaml`, with a reusable
publication template and dynamic sanctioned command construction.

CI-001 also cannot close from local YAML. It requires a governed v0.6 candidate
that actually executes upload v7, and an authorized publication rehearsal or
real tag execution that exercises upload v7 and download v8 without Node.js 20
annotations. Hosted cancellation behavior likewise requires two superseding PR
updates. No push or hosted mutation was authorized in this slice.
