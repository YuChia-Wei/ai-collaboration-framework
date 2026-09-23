# Windows path compatibility repair

Issue: https://github.com/YuChia-Wei/ai-collaboration-framework/issues/378
Program: #322. Owner: local-change-implementer. Applicability: framework-source.

The assigned worktree is F:/framework-next/378, branch
codex/2026-09-23-windows-path-compatibility, starting commit
70cff755bad2c2bc55bb10f7259af3871009bb03 (initially clean).

WPC-001 diagnoses and repairs only the selected reader and writer compatibility
paths, focused tests/framework_next regressions and this workflow. The intended
reader fallback is restricted to Windows error 1 with direct stable ancestry and
canonical long-name verification. Writer error 144 can query the selected directory
handle after direct-path/identity checks; no drive-root substitution is selected.
Existing filesystem sets, limits, locks and recovery semantics remain applicable.

Use focused positive/negative API simulations, then minimal actual F: assembly
and reader, Lesson public write/read, and one necessary case for each other
distinct backend. Stop equivalent retries after shared setup failure. Preserve
all prior residues and F:/ai-context-tests. New evidence belongs to one unique run
under F:/framework-next/p7-runs/378-compatibility.

U001 adapts the software-development templates proportionally. Effective-rule
packets, legacy validators, formal audit/lease/handoff packets and CI remain
`deferred-by-owner` (program #322 coordinator/P7; next: post-pilot review).
Only #378-selected small checks and exact commit-message validation are enabled.
Declared dispatch: OpenAI Codex, gpt-6-astra / ultra; this is not independent
runtime attestation. No agents, new tasks, callback or provider writes.

Current state: bootstrap continuation approved in live #378 and directly in
this task. Only src/tools/maintain_framework.py::_direct and necessary private
stdlib helpers join the source scope. Focused path checks precede a clean exact
engine commit and one fresh full public plan. Prior refusals remain retained. See [repair observations](reports/repair.md) and
[bounded evidence summary](reports/observations.json). Source review and
online integration belong to coordinator 01a0ce78-db26-74e1-a615-2bd0599f7d0c.
Return coherent local commits before first push. #368/#369/#373 acceptance,
pilot, release and CI remain separate.
