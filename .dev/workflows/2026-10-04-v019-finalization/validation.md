# Candidate evidence

Input: `8a59cc4670dfe741ba800c63f438640f5847c4fa`. The parent is the only tracked
author. No source-project managed installation or runtime profile was edited.
The owner-approved init responsibility and acceptance are in
[the plan](workflow-plan.md).

## Author checks before immutable packaging

| Check | Actual result | Limit |
| --- | --- | --- |
| `python -I -B tests/framework_next/test_contracts.py` | passed, 9 tests, 5.103 s | Source declaration/reference checks, not agent behavior. |
| `python -I -B tests/run.py` | passed, 173 tests, zero failures/errors/skips, runner 37.018019 s | Exact current CI command executed locally; schema/tool/distribution/release/source suites. |
| Manual/resource link and example inspection | passed: 18 manuals, 39 Markdown files, 250 case-exact local links, 16 JSON examples | Local paths and syntax, not remote-link availability or command execution. |
| PowerShell block parse, first attempt | failed on six unquoted angle-bracket placeholders in the existing sub-agent CLI example | Retained failure; no CLI was executed by the parser. |
| PowerShell block parse after correcting that example | passed, 19 blocks | Syntax only; actual package/installation execution is separate. |
| `git diff --check` | passed | Working diff whitespace. |
| `git diff --exit-code -- .ai .agents .claude .codex` | passed | Source project's existing installed/runtime files unchanged by this slice. |

Logs and the bounded link checker are ignored under
`.dev/ai-context/local/v019-finalization/`: `default-1.stdout.log`,
`default-1.stderr.log`, `check-manuals.py`, `manual-check.json`,
`powershell-blocks.json`, `manual-parse-1-failure.txt`. The first parse failure
was corrected, not reclassified as a pass. These checks do not execute the
new-release download example or claim 0.19.0 is public.

The read-only inventory used inherited settings and canonical role
`src/sub-agents/mechanical-evidence-worker/sub-agent.yaml`. It confirmed the
existing init operations/dependency boundary and declaration/test call sites;
it authored no product files and was not an independent acceptance review.
Graph discovery missed a tracked test and returned no relevant distribution
symbols despite direct definitions. Explicit tracked-file fallback over the
selected files supplied those conclusions; graph absence was not used as proof.

## Pending evidence

Actual immutable package/subset/installation, two initialization targets,
repeat/refresh preservation, selected removal, fresh-context first task and
scoped independent review remain pending. Hosted checks, integration, tag,
publication and real downstream adoption have not occurred for this subject.
