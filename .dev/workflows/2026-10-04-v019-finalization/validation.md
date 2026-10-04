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

## Immutable package and installation

The actual local builder used source, tooling and workflow commit
`fefb019e3337c9ce6edb0ccfc299f12e9a899d74` with this command:

```powershell
python -I -B .github/scripts/build-release.py --repository C:/Github/YuChia/ai-collaboration-prompts-dotnet-backend --source-commit fefb019e3337c9ce6edb0ccfc299f12e9a899d74 --tooling-commit fefb019e3337c9ce6edb0ccfc299f12e9a899d74 --workflow-commit fefb019e3337c9ce6edb0ccfc299f12e9a899d74 --workflow .github/workflows/package-candidate.yml --repository-name YuChia-Wei/ai-collaboration-framework --run-id local-finalization --run-attempt 1 --work-root C:/aicf-f19a/w --output C:/aicf-f19a/o
```

The builder passed in 94.927722 seconds, from `2026-10-04T11:11:29.658608Z`
to `2026-10-04T11:13:04.586330Z`. This is local snapshot provenance, not an
Actions run or new release candidate tag. It verified archive-entry and extracted
raw hashes. The archive has 26 components (18 skills, two knowledge packages,
six sub-agents), 412 component members, 11 presets and 23 pinned engine files.
Init is 0.2.0 with 15 members. Docs and source-project records are outside the ZIP.

| Identity | Actual value |
| --- | --- |
| Archive | `ai-collaboration-framework-snapshot-fefb019e3337c9ce6edb0ccfc299f12e9a899d74.zip` |
| Size | 918424 bytes |
| Archive SHA-256 | `547b4aa111d0f95e11ce51f559c2ee697ceca58559a70ebd2e2542649fb6f57c` |
| Engine pin SHA-256 | `ad19a96898e10807b34e0536c3b7ad8c4fb8f65e66f744f6a543c1577228b036` |
| Catalog identity | `catalog:1:0.0.0-rc.280354017391416:fefb019e3337c9ce6edb0ccfc299f12e9a899d74:b2e77e91c8693a53a7cb008e3a87cfa8f2c96edfa86aea6840c1e50ef3c52bed` |

The extracted `engine/src/tools/derive-subset.py` actually derived
`project-initialization@0.1.0`, original names, both adapters and no knowledge.
The extracted `maintain_framework.py` executed API 2 inspect/plan/apply/inspect
with real plan hashes and disjoint roots in `C:/aicf-f19a`. All selected plans
were read back before apply. No agent was active in the affected target during
maintenance; all three quiescence declarations were true.

| Scenario | Actual result |
| --- | --- |
| New target `n`: install init 0.2.0 | passed; 17 managed members; four pre-existing project files unchanged; post-inspect `managed-bytes-consistent`. |
| Existing target `m`: install init 0.1.0 from the prior `02dde10854c2a2c3f626a41c1c974a4937b2b288` snapshot | passed; seven project files unchanged. |
| Existing target `m`: update to the current init 0.2.0 candidate | passed; 14 add/change entries plus three unchanged entries; all seven project files SHA-256-identical; post-inspect consistent. |
| New target `n`, after initialization and first task: deselect all skills/adapters through an empty Selection 2 candidate | passed; exactly 17 managed entries removed, managed-owned count zero, both runtime entries and core entry absent; all seven project files SHA-256-identical, including authored AGENTS, CLAUDE and first-task guide. |

Removal leaves an empty managed selection/lock; it is not a claim to remove
every framework directory. Authored references to a removed optional skill remain
target-owned maintenance work, not permission for the installer to rewrite docs.
Update/removal evidence concerns these synthetic projects, not legacy v0.18
migration, recovery, filesystem durability or real downstream adoption.

## Actual instruction and fresh-context execution

Each initial executor started with no parent conversation history and inherited
runtime settings without model/effort/provider overrides. Entry paths were
explicitly supplied; this is actual instruction execution in fresh agent contexts,
not a test of native Codex or Claude automatic discovery. Claude-rendered entry
reading still executed in the Codex agent surface, not a Claude runtime.

| Agent and selected operation | Actual output and checks |
| --- | --- |
| `/root/initialize_new`: initialize `n` via its installed Codex entry | Added only AGENTS, thin CLAUDE and `.dev/guides/first-task.md`; reused README and owner-facts by meaning; preserved all 23 existing files; 22 links resolved; commands remained `discovered`. No product/test/Git changes or starter-task execution. |
| `/root/initialize_existing`: initialize `m` via its installed Claude-rendered entry | Added `docs/first-task.md`; appended necessary navigation/facts to AGENTS and docs index. Preserved original AGENTS 625 bytes, index 106 bytes and all 24 other files; 17 links resolved. Reused CONTRIBUTING/product overview; no duplicate `.dev` or new policy. |
| `/root/initialize_new`: one repeated initialize | No changes or added files; all 26 full-target file hashes unchanged; 22 links and Claude import valid. Parent's project-file snapshot also matched before the first task. |
| `/root/initialize_existing`: one selected factual refresh | Parent first moved identical test bytes to `checks/test_label.py` and updated README's command. Refresh changed only AGENTS facts and first-task paths/commands; reverse substitution recovered original text; 472-byte custom-rule prefix and 25 unselected files preserved; 14 links resolved. No rule adoption or application execution. |
| `/root/first_task`: new context executes both selected guide examples | Started at target AGENTS and reading map; completed read-only explanation first, then added only two README-defined assertions in `tests/test_label.py`. Ran `python -B -m unittest discover -s tests -v` from `n`: three tests passed, exit 0. All 25 other files unchanged; no installation or missing-specialist block. |

The fresh task changed test SHA-256 from
`05455a00f95a051b4123f5b4b65a61d396a5e0dc4082ce20677fc8950d83a66a` to
`5c20f05fd32a9e48b1f6c19fe726a375887e5310bf628fcddbe16cc411edab16`.
Application SHA-256 stayed
`829539575a34f4ebd99d21f1867bce174d6a8f2728abb9ec96d24e042974dd42`.
No .NET/DDD or third-party test framework was introduced. Explicit unknowns
included production constraints, roadmap and supported Python minor versions.
Both initialize operations stopped after the usable starting point; parent
separately authorized repeat, refresh and first-task scenarios.

Two agents initially encountered sandbox read denial for the external fixture;
narrow approved host access completed the checks. Those environment attempts
are not product defects or passed sandbox executions. An extra draft-writing
delegation encountered the concurrent agent limit before execution; the parent
prepared the draft directly. No model escalation or additional visible chat was
created. All fixture operations used Windows; no native/hosted claim follows.

Parent retained the exact fixture/setup helper under ignored
`.dev/ai-context/local/v019-finalization/acceptance.py`. Package build output,
derived subsets, requests, plans, responses and preimage snapshots remain in
`C:/aicf-f19a`, with API evidence under `ev/`. Nothing there is a published asset.
Agent reports above record the actual invocation results; they are not unit-test
simulations of an instruction evaluator.

## Independent review and repairs

| Reviewer and immutable subject | Scope and disposition |
| --- | --- |
| `/root/init_review`, `8a59cc4670dfe741ba800c63f438640f5847c4fa..fefb019e3337c9ce6edb0ccfc299f12e9a899d74` | Read-only review of all 30 changed files, A1–A7, init resources/declarations and direct manual/CLI consumers. One P2 finding R1: installation manual retained an unqualified RC4 Windows-execution statement. No other supported finding. |
| `/root/init_review`, `c9143d0ce440399290fbabbd68841aa7bd434adf` | Independently confirmed R1 resolved by the sole two-line manual correction; clean fixed HEAD and unchanged criteria/authority; no new defect. |
| `/root/remaining_review`, `e859d4e4cf2ce08fc2f46cd6d124cccc6a18173d..fefb019e3337c9ce6edb0ccfc299f12e9a899d74` | CI native path triggers, retired classifier, source-only 23-file engine/CLI closure, inherited model-policy v2 and role selection, external-discussion removal and direct authority callers. No actionable finding. |
| `/root/remaining_review`, fixed `c9143d0ce440399290fbabbd68841aa7bd434adf` using `b52c68d64373bb54688109b9174bd4a9cea2b577..7208464b0d4e91a253f6980a77e59de661e2f009` to select #435 changes | Common/.NET knowledge and ownership boundaries; actual catalog/source/normative hashes, member sets and 12 selected references; target-selected mocking defaults and historical/current distinction. No actionable finding. This supplies the independent review missing from the earlier author-only checkpoint. |

Both reviewers used the current source policy and code-reviewer common method;
they made no writes or test/provider invocations. No specialist security, .NET
runtime or legacy/P7 coverage is claimed. Their graph identity was stale, so
fixed Git diffs/tracked sources supplied evidence. The source remained frozen
through each review. Review advice authored no committed product content.

Final author inspection also found the two human root READMEs still naming init
0.1.0. Both now name 0.2.0 and describe the accepted starting point; the historical
2026-10-02 introduction record intentionally keeps its original version. This is
a navigation/version correction, not a package or authority change. Current
manual/resource checks were repeated for these affected document surfaces:
41 Markdown files, 276 case-exact local links, 16 JSON examples and version
agreement in all four root entry documents passed. The 19 PowerShell blocks
were unchanged by these final prose corrections; their prior parse result is
reused without claiming a second command execution.

## Acceptance disposition and next boundary

| Criteria | Disposition | Evidence |
| --- | --- | --- |
| A1 | passed in selected local fixture | Real init-only/no-knowledge installation and `n` instruction execution. |
| A2 | passed in selected local fixture | `m` reuses product/rule/index documents; exact custom bytes retained. |
| A3 | passed in selected local fixture | Python/stdlib only, no forced .NET rules or unavailable specialist dependency. |
| A4 | passed in selected local fixtures | Unchanged repeat; factual refresh preserves custom rules and unselected bytes. |
| A5 | passed in selected local fixtures | Actual package version update preserves existing documents; deselection preserves initialized documents. |
| A6 | passed on explicit fresh-agent execution surface | New context follows reading map and completes scoped explanation/test task; native discovery not tested. |
| A7 | passed in observed runs and static review | Initialization stops before task execution; owner gaps remain explicit and follow-up tasks have separate scope. |

The package/tested product subject stays `fefb019e...`; subsequent README/manual
and workflow records do not change `src`, `tools`, `tests`, `.github`, governing
policy or installed projections. Exact Git equivalence must be read back at the
final local commit; this reuses bounded product evidence, not a rebuilt artifact
with a new source identity. A later tagged build needs its own manifest/assets.

Live provider read-back on 2026-10-04: no PR for the finalization branch; main is
`dd1453e8cf23bf62a5b28c70ed08f475856dda41`; #322 remains OPEN; newest public
prerelease is `v0.19.0-rc.4`, latest stable listed is `v0.18.0`. No current-head
hosted check, push, merge, new tag, draft or publication occurred for this work.
Local source finalization is complete. Integration still requires authorized
push/PR, actual current-head `Source change gate`, maintainer acceptance and
separate merge authority. Tag/draft/publication remain separately selected.
