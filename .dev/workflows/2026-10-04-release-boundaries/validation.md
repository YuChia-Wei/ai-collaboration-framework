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
members.

## Immutable archive and consumer CLI execution

Implementation and tooling subject:
`02dde10854c2a2c3f626a41c1c974a4937b2b288`. The checkout was clean before and
after execution. The final local closeout changes only workflow records and the
workflow index, with no product, tool, test or runtime-profile byte changes.

The actual local command was:

```powershell
python -I -B .github/scripts/build-release.py --repository C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend --source-commit 02dde10854c2a2c3f626a41c1c974a4937b2b288 --tooling-commit 02dde10854c2a2c3f626a41c1c974a4937b2b288 --workflow-commit 02dde10854c2a2c3f626a41c1c974a4937b2b288 --workflow .github/workflows/package-candidate.yml --repository-name YuChia-Wei/ai-collaboration-framework --run-id local-validation --run-attempt 1 --work-root C:/aicf-b-02dde/w --output C:/aicf-b-02dde/o
```

Result: `built`; builder interval 2026-10-04T04:58:49.978647Z through
05:00:29.450503Z (99.471856 seconds). `local-validation` explicitly labels
local provenance; it is not a GitHub run. The snapshot's numeric RC-shaped
catalog label is an existing builder requirement, not a new release candidate.

- Archive: `ai-collaboration-framework-snapshot-02dde10854c2a2c3f626a41c1c974a4937b2b288.zip`,
  909116 bytes; SHA-256
  `2b449e159e60f2a441594eaa342b20c482a761c43e56acddb1ff72a766d60c1b`.
- Builder verified raw archive hashes and extracted bytes. Additional archive
  inspection confirmed all 23 pinned members under `engine/src/`, no
  `engine/tools/`, no source-owned `docs/` or `.dev/` payload, and no removed
  `EXTERNAL-AI-DISCUSSION` resource.
- Retained evidence: `C:/aicf-b-02dde/o/release-manifest.json`,
  `w/builder.stdout`, `w/builder.stderr`, and `cli-validation.json` under the
  same task-owned root. Prior attempts and these scratch artifacts remain.

The extracted `w/x/engine/src/tools/derive-subset.py` then ran with `-I -B`,
the extracted catalog and independently selected pin, and each exact preset
`sub-agents@0.1.0` / `sub-agents-claude@0.1.0`. Explicit disjoint output/scratch
roots were `dc`/`tc` and `da`/`ta` under that root. Both returned `assembled`:
six roles each, 4.997 and 5.291 seconds respectively. Neither desired selection
contains `model_resolution`. Their full stdout/stderr remain in the task root.
These are real physical subset builds; no target installation, breaking
reinstall, runtime discovery or agent/model inference occurred in this check.

## Retained boundaries

Only three GitHub workflows remain: source checks, package snapshots and Draft
Release delivery. Native path filters select automatic PR checks and main-push
snapshots for `src/**` and `tools/**`; manual packaging/tag behavior remains.
No Actions, branch protection, credential, provider or publication settings
were changed. Actual current-head hosted success and scoped independent review
remain pending before separately authorized integration. Historical #435
dispositions and the five protected history roots are preserved.

Read-only GitHub checks on 2026-10-04 found `branches/main/protection` returning
404 `Branch not protected`, and `rules/branches/main` returning `[]`. At that
observation there was no active provider required-check rule conflicting with
the selected path filters. This is not a future-state guarantee or a provider
mutation.

See [capability assessment](capability-assessment.md) for current initialization
and model-maintenance coverage. The fuller first-team starter kit is a concrete
product gap/proposal, not implemented or owner-adopted scope in this checkpoint.
