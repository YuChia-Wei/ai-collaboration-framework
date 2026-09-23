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

Current state: local bounded repair completed, including the directly approved
bootstrap continuation. Seven focused bootstrap/path regressions and one complete
actual F: public plan passed on clean aa2bffb52c0acf521302cf9f08c649ad54246c98.
Prior source observations and all failures remain retained. See
[repair observations](reports/repair.md), [bootstrap continuation](reports/bootstrap-continuation.md)
and [exact engine observations](reports/bootstrap-observations.json).

Coordinator 01a0ce78-db26-74e1-a615-2bd0599f7d0c owns affected source review and
online integration. Executor stops before first push. No Issue/Project mutation,
apply/recover, rc.1 pilot, release or CI completion is implied. #368/#369/#373
retain their separate acceptance and owner decisions.
