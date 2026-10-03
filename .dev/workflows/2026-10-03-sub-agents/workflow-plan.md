# Publish and install reusable sub-agent profiles

Issue: [#434](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/434).
Owner: `software-development-orchestrator`; root is the sole tracked writer
and integration owner. Source policy is the 2026-10-02 adopted
`SOURCE-DEVELOPMENT-POLICY.md`, including conditional independent review.

## Authority and source

The owner manually staged the migration of six roles from `.dev/agents/` to
`src/sub-agents/`, requested release and installation settings on 2026-10-03,
authorized the online Issue, and separately authorized one read-only review
sub-agent. Implementation starts from local commit
`37a588c8c0b6f5e760079c563e71d742af8f962d`; five earlier local manual/removal
commits above `main` are preserved, outside this delivery's review diff. They
are not asserted integrated into main.

No push, PR, merge, tag, publication, actual downstream installation,
credential/protection changes, Issue closure or branch cleanup is selected.

## Accepted bounded outcome

Owner follow-up selects programmatic install-time model discovery and migration:
5.6 Terra -> 6.1 Sol then 6 Sol; 5.6 Luna -> 6 Luna; 5.6 Sol -> 6 Astra.
Use task-position mapping Haiku for focused translator, Opus 5.5 for standard
analysis, Fable 5.1 for deep analysis; no official cross-provider equivalence
claim or rumored Fable upgrade. Preserve role effort and tool/sandbox boundaries.
Resume T1/T2 for this affected installation slice, owned by `slice-implementer`
under the orchestrator. Add canonical candidate policy, optional selection-v3
model resolution, exact profile rendering/reconstruction and bounded CLI catalog
discovery. Explicit direct API discovery uses caller-selected existing API auth;
subscription/gateway discovery remains caller-supplied observations. No inference,
auth changes, provider settings or actual downstream adoption selected.
Acceptance includes candidate priority and effort refusal, provider/role closure,
immutable plan/lock hashes, default compatibility, paginated discovery tests,
real isolated resolved-profile install and affected immutable independent review.

- All six role manifests, private playbooks and supported profiles become
  declared catalog components with exact source/member identity.
- A separate `sub-agents@0.1.0` preset and selection version 3 explicitly
  select roles, including mixed skill/role selection. Existing v1/v2 selections
  and presets do not implicitly select roles.
- Reuse catalog/subset/Engine 2 installation safety: reconstruct exact bytes,
  admit bounded destinations, reject drift and unowned collisions. Never take
  ownership of project `.codex/config.toml`, custom profiles or credentials.
- Canonical payload goes to `.ai/core/sub-agents/`; runtime profiles go to
  `.codex/agents/` and `.claude/agents/` for all six roles.
  Unsupported role/adapter pairs fail explicitly. Copilot installation is
  outside the current adapter contract.
- Fix moved active source references and retain historical records. Selected
  source ownership checks cover both sides of the migration, without treating
  an arbitrary legacy/runtime tree as a new source owner.

Role settings are configuration evidence; actual model access, invocation,
behavior, downstream acceptance and hosted/publication success remain separate.
No additional product-requirement/specification stage or compliance claim is
selected for this configuration slice.

## Work and validation

T1 implements the packages, selection/projection, immediate ownership consumers,
user guide and focused tests. T2 performs one independent scoped read-only
review on the immutable local implementation commit, then records disposition
and local handoff. Two tasks are sufficient because this durable transition
changes catalog/installation ownership and crosses a conditional review boundary.

Relevant commands are `python -I -B tests/run.py --suite schemas`,
`--suite distribution`, `--suite source`, `--suite platform`, and
`--suite release`; no whole-history/nightly matrix is selected. Local catalog
assembly and source-free derivation must use exact committed engine bytes and
an independently constructed pin. Installation verification uses an isolated
disposable target for this newly selected role scenario, not a downstream
adoption or role execution claim.

Discovery used a fresh Codebase Memory MCP fast index on the initial source.
The tool did not expose an index commit identity, and excluded `.github/scripts`
and some tools; those scopes use explicit Git-tracked file reads. Graph output
is only discovery evidence, not closure or absence proof.

## Retained attempts and disposition

During final handoff the owner explicitly requested Claude support for the
remaining five roles. Resume the same bounded #434 workflow: add a separate
`sub-agents-claude@0.1.0` preset, exact declared Claude runtime members and
strict read-only tool allowlists. New analyzer profiles inherit the caller's
Claude model; the existing translator retains Haiku. Codex selection remains
unchanged. Require focused tests, real Claude-only isolated installation, and
affected independent review on a new immutable commit. This changes the reviewed
product/acceptance, so prior implementation review cannot establish this scope.
The pre-extension source gate on
`9e5fe009591dca2ce7a40712c2dc16812177d6d9` passed 162 tests in 51.429 seconds.
An intervening invocation with literal `--head HEAD` was refused before checks;
its ignored failure log is retained separately, not counted as a pass.

The first Claude distribution run executed 46 tests and reported 25 errors:
the existing Claude frontmatter parser accepted LF only, while new Windows
profile writes materialized CRLF. Repair parsing to accept both newline styles,
without changing source/projection bytes or hashes; add CRLF acceptance coverage
and retain the failed log as `artifacts/sub-agents-claude-distribution-failed.log`.
Re-run the affected suite after that material parser change.

Claude physical verification selects one source-read-only external CLI task,
`python -I -B artifacts/verify-claude-delivery.py`, after the implementation
commit is clean and fixed. Classify it as long-running because it assembles the
full declared catalog; use one isolated process and bounded terminal completion
wait, with no tracked writes or repair during execution. The task may write
only ignored local evidence and its explicit isolated temporary target. Bind
the terminal result to exact commit, content digest, command, elapsed duration,
outcome and evidence. Retain temporary artifacts; no downstream adoption,
publication, role invocation or cleanup is selected. Failure, interruption or
drift blocks this physical claim and requires affected reconciliation.

Claude implementation `fcaf7aa76d0a958b894f0176d7116193f9f3b636`
passed its 164-test Source change gate and physical 36-file Claude installation
scenario (124.646720 seconds; clean tracked state before/after). However the
independent reviewer rejected its model validation: arbitrary analyzer and
translator model values were accepted by the package checker. Parent accepts
that finding; require exact `inherit` / `haiku` plus wrong/missing/cross-role
model regression cases. No tracked repair occurred during the external task.
Preserve original evidence under `artifacts/claude-sub-agents-*`; new corrected
head evidence uses `artifacts/claude-sub-agents-corrected-*`. Because the engine
parser changed, repeat fixed-head physical assembly/install rather than silently
rebinding the old engine pin or source identity. Re-plan under this workflow
after the material repair, then perform affected independent review again.

The first `tests/run.py --suite distribution` execution ran 36 tests and failed
with 12 Windows sandbox temporary-root access/cleanup errors (`WinError 5`).
Pure metadata/projection tests passed within that failed execution. This is
environment failure, not a passing suite or an established product regression.
Retry selects host permission with the affected new test cases; no global TEMP,
fixture acceleration or alternate storage setting is changed.

The host-permission focused run then executed 188 tests with five errors, zero
failures/skips. Four new in-memory projection tests supplied an incomplete
subset envelope; one new drift test omitted the reader descriptor's `path`.
These were test preparation defects. The revised retry plan constructs and
validates a complete Subset contract and supplies the real reader descriptor
before rerunning affected suites. Retain both earlier attempts; unchanged
schema/source/platform/release passes from that run remain supporting evidence.

The first distribution-only retry ran 44 tests and found four aliased-input
preparation errors: composing the in-memory fixture shared the same catalog pin
between `desired` and Subset. The revised fixture passes through canonical JSON
bytes, as actual subset readers do, before validation; it does not relax the
production alias guard. Re-run only the affected distribution suite.

The final release-suite invocation accidentally reused the default sandbox and
reported 26 temporary-root access errors. A host-permission rerun on the same
immutable implementation commit passed all 26 tests. No product repair was
needed; both logs remain in local ignored artifacts.

Before that Claude extension, T1 and T2 reached local implementation completion. Commit
`89815900f7d0aa05a53eb9902f8883fdc87649de` passed the selected Source change gate
(162 tests), the release suite (26 tests), physical catalog/subset construction,
and the selected isolated installation scenario. The authorized independent
reviewer found no supported actionable defects. See [validation](validation.md)
and [review](review.md) for scope, commands, provenance and limitations.

The following record-only commit changes this workflow and its index. It does
not change the reviewed implementation, acceptance or governing authority.
Final-head source checks and an explicit current-head read-only reviewer binding
are required before the local handoff. Their output is retained in ignored
`artifacts/sub-agents-source-gate-final.json` and
`artifacts/sub-agents-final-binding.json`; these are local evidence, not hosted CI.

Next owner: the human maintainer selects push/PR and integration. Issue #434
remains open with `Refs`, because local completion does not establish hosted
checks, maintainer acceptance, merge, release or downstream adoption. The
selector's native-acceptance owner-selection requirement remains unresolved for
any future operation that needs it; this focused isolated scenario does not
discharge that broader admission condition.

The first record-only head `cf407f6b22293559fdcf99e816107b1b46370339`
failed the fresh Source change gate before test dispatch: both completed tasks
used `result` / `finding_status: none`, whereas the actual selector requires
`result_summary` / `finding_status: addressed`. The same independent reviewer
also identified this administrative defect and blocked final binding. Repair
only the two task records and record this attempt; product, criteria and
authority remain unchanged. Preserve the failure as
`artifacts/sub-agents-source-gate-record-failed.json` and rerun the affected
fresh gate/reviewer binding on the new immutable head.

## Completed Claude extension

Updated: `2026-10-03T08:56:55+08:00`. All six Claude projections and the independent Claude
preset are locally complete on `51a939c5b1de1ca32b7c46a130f29532a4424ff6`. Source gate passed 164 tests;
corrected exact-engine physical assembly and 36-file installation passed. The
same independent reviewer accepted the corrected scope after the model finding
was addressed. See [Claude validation](claude-validation.md). Retain prior
failures and old-head outcomes above; they do not establish corrected-head
success.

The final commit updates only workflow records/index. Verify the current head
with a fresh Source change gate and read-only reviewer binding of that
administrative delta. Product bytes are checked against
`artifacts/claude-sub-agents-reviewed-subject.json`; do not claim full-tree
equivalence across changed records. Logs are retained as
`artifacts/sub-agents-claude-final-source-gate.json` and
`artifacts/claude-sub-agents-final-binding.json`. The human maintainer owns any
subsequently authorized integration/publication/adoption; #434 stays open.
