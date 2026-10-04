# Local validation checkpoint

Implementation input: `e859d4e4cf2ce08fc2f46cd6d124cccc6a18173d`.
Root is the only author/writer; no sub-agent or model inference was used.

## Executed checks

| Command | Outcome | Evidence and limits |
| --- | --- | --- |
| `python -I -B tests/run.py --suite schemas --suite distribution --suite source` (first sandbox attempt) | failed: 104 tests, 8 failures, 19 errors, 0 skips, 5.189985 s | Old model tests expected fixed candidates; several maintenance fixtures also hit Windows temporary-directory permissions. Retained `focused-1` logs. This was not a pass. |
| Same focused command after model fixture/contract corrections, with host temporary-directory permission | passed: 107 tests, 0 failures/errors/skips, 5.898265 s | Retained `focused-2` logs. Host rerun separates the environment failure from actual behavior. |
| `python -I -B tests/run.py --suite release --suite tools --suite loader --suite platform` | passed: 100 tests, 0 failures/errors/skips, 34.448578 s | Retained `remaining-1` logs. Offline release fixtures and simulated platform paths are not native installation or provider acceptance. |
| `python -I -B tests/run.py` after final behavioral regressions | passed: 173 tests, 0 failures/errors/skips, 37.052854 s | Exact fixed CI command, local host execution. Retained `default-1` logs. |
| `git diff --check` | passed | Working diff whitespace only. |
| `git diff --exit-code -- .ai .agents .claude` | passed | Existing managed installation remains unchanged. Source `.codex/agents` changes are explicitly owner-authorized; no hot-reload is claimed. |

Logs are ignored under `.dev/ai-context/local/release-boundaries/` with separate
stdout/stderr per attempt. Schema/source checks confirm all six current roles
use policy 2, inherited profiles reject fixed bindings, discovery does not
freeze/escalate a model, and provider/adapter mismatch remains rejected.
Legacy policy 1 remains readable; it is not the policy of these six roles.

Current declarations contain 26 components and 409 members (18 skills, two
knowledge packages, six roles). All 23 standalone engine members are under
`src/`; the three consumer CLIs are under `src/tools`. Root build tools are not
members. Actual immutable catalog/archive and CLI execution remain the next
check; declaration/unit results are not claimed as that execution.

## Retained boundaries

Only three GitHub workflows remain: source checks, package snapshots and Draft
Release delivery. Native path filters select automatic PR checks and main-push
snapshots for `src/**` and `tools/**`; manual packaging/tag behavior remains.
No Actions, branch protection, credential, provider or publication settings
were changed. Actual current-head hosted success and scoped independent review
remain pending before separately authorized integration. Historical #435
dispositions and the five protected history roots are preserved.

See [capability assessment](capability-assessment.md) for current initialization
and model-maintenance coverage. The fuller first-team starter kit is a concrete
product gap/proposal, not implemented or owner-adopted scope in this checkpoint.
