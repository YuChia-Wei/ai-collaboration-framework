# CP-2 Portable Compatibility Checkpoint

- Workflow: `2026-08-02-python-prerequisite-diagnostics`
- Task: `AIC-004-diagnostic-implementation`
- Canonical work item: `TOOL-002`
- Provider Story: GitHub Issue `#77`
- Implementation commit: `3f863be4a57e64ac068983081854648277719b81`
- Recorded at: `2026-08-03T01:05:00+08:00`
- Outcome: `passed`

## Authorization And Checkpoint Acceptance

The repository owner requested this continuation to plan and create the User
Story, implement the approved result, and continue through pull request and
merge unless a material problem requires a question. That instruction is the
prospective acceptance source for continuing from CP-2 once every bounded
portable criterion below passes. It does not authorize release preparation,
tagging, publication, or work owned by Proposals #75 or #76.

## Implemented Boundary

Commit `3f863be` adds the governed 25-entry registry, a no-write Python
prerequisite core, POSIX and PowerShell discovery launchers, and direct guards
for exactly the 12 portable production CLIs. It also adds target-owned routine
validation selection, source-only exclusion for `.dev/validation.local.conf`,
one-result `check-all.sh` discovery, Ubuntu/Windows focused CI jobs, package
projection, and the approved human and agent-facing documentation.

Published direct command paths and prerequisite exit mappings are unchanged:
the package planner retains exit `2`; the other registered prerequisite
failures retain exit `1`. Diagnostics do not install Python or dependencies,
start network access, write bytecode, mutate a target, create a release, or
claim a blocked outcome as passed.

## Verification Evidence

| Surface | Result |
| --- | --- |
| Shared prerequisite core | `14 passed` |
| PowerShell launcher | `4 passed` |
| POSIX launcher under Git Bash | `5 passed` |
| Registry and package projection contract | `4 passed` |
| Dependency-version contract | `15 passed` |
| Shell fail-closed and single-discovery regression | `30 passed` |
| Routine-validation activation policy | `3 passed` |
| Orchestrator capability contract | `13 passed` |
| Technology-selection contract | `3 passed` |
| GitHub workflow contract | `6 passed` |
| Package apply regression | `25 passed`, `1 skipped` because this Windows host cannot create the symlink fixture |
| Tracked local-opt-in negative package proof | `passed` with elevated Temp fixture access |
| Clean install and v0.7.0-to-candidate upgrade proof | `passed` with the real package planner and governed provenance |
| AI-context validation | `passed`: 24 indexes, 16 canonical skills, 2 runtime roots, 345 language-policy files, 13 rules, 34 manifests, 10 mappings |
| Root bilingual structural parity | `passed` |
| `.dev/releases/v0.8.0` existence check | `false` |
| `git diff --check` | `passed` before commit |

The complete `test_ai_context_packaging.py -v` invocation exceeded the first
bounded 304-second local tool window without emitting a failure. A timeout is
not a pass; the complete source-wide package suite remains required exactly
once in the final validation stage after the 13 source-only CLIs are guarded.
The two changed package behaviors have their own passing focused proofs above.

## Translation Routing Deviation

The finalized English root-README paragraph was scheduled for the promoted
low-cost `context-translator` route required by D-TR-001. The collaboration
runtime refused a fourth thread with `team thread limit reached`. No primary
agent translation fallback was used. The existing low-cost documentation
worker translated only the bounded paragraph, and the primary agent verified
sentence mapping, exact option names, exact link target, and root structural
parity. This execution deviation changes neither the approved content nor the
canonical language boundary.

## CP-2 Decision

CP-2 is satisfied. The portable task is complete at commit `3f863be`; the
owner's continuation instruction accepts this passing checkpoint and activates
`AIC-004-source-diagnostic-implementation`. The 13-entry source-only batch must
reuse the same registry/core contract, remain outside portable package
projection, preserve source release and governance behavior, and return to a
single complete final gate plus independent audit before workflow closeout.
