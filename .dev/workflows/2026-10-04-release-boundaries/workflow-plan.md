# Release boundary continuation

Input: `e859d4e4cf2ce08fc2f46cd6d124cccc6a18173d` on
`codex/2026-10-03-sub-agents`. The owner's 2026-10-04 conversation extends
the existing #322 redesign, #434 sub-agent and #435 ownership work.

## Accepted changes

- Let GitHub workflow `paths` select only `src/**` and `tools/**`; run a fixed
  current test command. Remove the Python Git-diff selector and obsolete
  non-packaging/non-merge workflows/scripts. Reconcile current source policy.
- Move downstream subset/reinstall CLIs to `src/tools`; exclude build tools
  from the current standalone engine and update direct callers/tests/manuals.
- Remove external-AI discussion from the common knowledge package. Preserve
  existing historical disposition records; those project records are not payload.
- Default portable roles and source runtime profiles to runtime-owned model and
  reasoning selection. No automatic higher-cost model/effort escalation. Assess
  existing discovery/maintenance support before proposing another tool or skill.
- Inventory initialization resources, project inventory ownership and missing
  first-team onboarding resources. Do not copy source project governance into
  products or implement a new collaboration kit without its selected scope.

## Tasks and acceptance

`T1`: implement the accepted changes; inspect direct dependencies; verify the
fixed workflow commands, package declarations, relocated CLI bootstrap, engine
closure and inherited role projections. Record actual tests and limitations.

`T2`: report initialization/maintenance ownership and gaps using current source
and installed evidence. Preserve distinctions between local tests, independent
review, hosted CI, product publication and target adoption.

Graph discovery was freshly indexed for this checkout; tracked files and direct
callers verify material conclusions. Model availability is not spending consent.
No model inference, external write or new task is part of this continuation.

## Progress

Authorized local work is complete. Implementation, local focused/default checks,
the immutable archive build and both physical role subsets are recorded in
[validation](validation.md). The
[capability assessment](capability-assessment.md) identifies existing init and
project-config ownership and the starter-kit gap. Product changes are committed
at `02dde10854c2a2c3f626a41c1c974a4937b2b288`; local closeout changes only these
workflow records and the workflow index. No independent review, hosted,
publication or target-adoption pass is claimed. Before integration, the next
authorized owner must arrange the required scoped independent review and actual
hosted checks. Any starter-kit implementation needs its selected product scope;
the assessment does not silently add it to this completed local task.
