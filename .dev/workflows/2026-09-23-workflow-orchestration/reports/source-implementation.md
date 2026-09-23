# P4 source implementation checkpoint

Status: source implemented; verification deferred-by-owner. Issue #341 source delivery
is distinct from provider closure, shared package mapping, installation and acceptance.
Workflow-owned P4-CONTRACT and P4-SOURCE are completed. Program #322 remains in progress.

Retained design: 7f821ee866e7e54e551036785e19dffaa3d7ac39.
Selected implementation baseline: 9aa93ff4b9df396d28d0a9ae1bd2dd24715e05c0.
[Selected contract](../../../design/framework-next/p4-selected-contract.md) resolves C341-01..05.
Updated: 2026-09-23T01:44:27+00:00.

## Actual source delivered

software-development-orchestrator@0.1.0; metadata/config v2; sole
software-development-orchestrator.record@1.0.0 readable/writable schema. Exactly:

| Member | Purpose |
| --- | --- |
| SKILL.md | Independently selectable organizational entry |
| skill-package.yaml | Closed metadata v2, exact roles/runtime/resources/operations |
| references/configuration.md | Isolated config v2, paths, locks and default provenance |
| references/operations.md | Ten operations, closed record/request shapes, lifecycle/history |
| references/retention.md | Explicit previews, protected evidence/reference meaning |
| references/composition.md | Actual P3 semantic handoffs and terminal-candidate limits |
| references/example.md | Inert minimal, tracked/ignored, failure/deferral/retrospective examples |
| schemas/workflow-record.schema.json | Owned closed Draft 2020-12 shape with local definitions |
| templates/workflow.md | Inert required-token Markdown view |
| scripts/workflow.py | Owned standalone Python tool; no private cross-skill imports |

Operations: explain, create, inspect, query, checkpoint, transition, resume,
retrospect, render, retention-preview. The script alone owns operational defaults
30/90/null days and 12000 characters. Metadata defaults remain store/template.
Explain distinguishes metadata, executable, project, local and invocation sources.

One record preserves stable tasks/dependencies, caller-attributed evidence, failures,
deferrals, owner questions, exact next action and revision history. Content changes
invalidate current retrospective while retaining historical candidates. Same-value
writes preserve bytes/time. Terminal workflow/task data stays immutable; continued
knowledge work needs a separately reconciled linked workflow or specialist record.

Retention never writes, schedules, deletes, archives or compacts. Unknown external
inbound references remain unknown; incomplete scans and meaningful evidence
protections remain visible. Purge never returns safe-to-delete. Required resume
meaning over budget fails explicitly instead of being truncated.

## Source evidence and implementation limits

P3 public interfaces were read from the selected integrated source: ac4175948045590d1a1942022435ab438ad30ac3,
knowledge 552e218d039245482ed422be7d4fb642d5463ff0, work-management
5409641f19244bc44467af7fba3fc496d7f5195c and mappings b38ef4a8dce57c2cb78fda6ae9c100d689605245.
Knowledge candidate instructions require actual query/decision inputs; promotion
also requires actual target/source bindings and bytes. No foreign request/hash,
approval, artifact creation or provider action is fabricated.

The narrow local-backlog graph index reported scripts/ excluded. The explicit
tracked-file fallback read local_backlog.py directly; source Git blob and worktree
hash matched fbe3362bef17e8de5161b6bb180c7a9cf60864ed. Selected parser/path/config/
single-file publication primitives were copied as source text through AST boundaries,
then owned/adapted locally. No product module was imported or executed. No shared
runtime was introduced. Governance entries/U001 were unchanged between the retained
design and selected source baseline; the previously read actual skill.yaml and
runtime wrapper remain the owning route.

Known limits: exact metadata/config/schema versions only; no historical importer,
conversion or store relocation; filesystem only with the stated local write backend
allowlist; cooperating single writer only, no OS CAS against unrelated editors,
distributed lock, multi-file transaction or power-loss guarantee. Package source
existence and syntax do not certify those behaviors. References and evidence are
caller-attributed; no authenticated approval service. Bounded complete summaries
can be unsupported when meaningful content exceeds the chosen budget.

## Actual limited checks and preparation failures

- Initial assigned root/branch/full HEAD/common-dir/clean state matched the retained
  design. Authorized fast-forward to 9aa93ff4b9df396d28d0a9ae1bd2dd24715e05c0 succeeded;
  post-fast-forward HEAD and clean status were read back.
- Direct source read/parse: 10 UTF-8 members, 1 JSON, 1 YAML, 1 Python AST; 8 local
  Markdown targets resolved. Metadata inspection showed exactly store/template
  defaults and the ten selected operations. No schema validator/product import.
- A combined source-write command exceeded Windows process command length (error
  206) before process creation; no file mutation occurred. Splitting by member
  completed the authorized writes.
- One orchestration JS string had a parse-time quoting error before any command
  ran or file changed. The corrected direct edit preserved original checkpoint
  provenance and updated selection state.
- Final direct changed-file inspection via PowerShell here-string piped to python -B -:
  19 strict UTF-8 reads, 4 JSON parses, 2 YAML parses, 1 Python AST parse, 32 local
  Markdown targets and 15 same-document schema references resolved; exit 0.
  This was reference inspection, not schema validation.
- The first staged git diff --cached --check returned exit 2 for one extra blank
  line at workflow.py EOF. The extra blank line was removed; the same check then
  returned exit 0. No source behavior or gate was weakened.
- python -B .ai/scripts/validate-git-commits.py --message-file
  .dev/workflows/2026-09-23-workflow-orchestration/source-commit-message.tmp
  --workflow-id 2026-09-23-workflow-orchestration returned exit 0:
  Git commit validation passed for planned message. The exact ignored message
  file is used by git commit -F; no range/history validator was run.
- Staged scope is exactly 19 paths inside the three assigned roots. Final report/
  handoff updates receive direct parsing and diff read-back before commit.

Product CLI including help, schema acceptance, tests/fixtures, builds/packages,
installation/migration trials, audits/review packets/leases/effective-rule packets,
legacy validators beyond the explicit commit-message exception, and CI were not run.
Disposition: deferred-by-owner, authority U001, owner program #322 coordinator / P7.
Next verification action: select actual focused checks for lifecycle/history and
evidence preservation, default/config isolation, bounded summaries/previews, path/
lock/publication failures and package reconstruction once mapping is assigned.
No direct syntax observation substitutes for these outcomes.

## Handoff

[source-handoff.json](../source-handoff.json) resolves the exact source checkpoint
from its containing Git commit; the coordinator callback supplies full HEAD.
Original design handoff/report remain intact. Only the authorized source/design/
workflow roots changed. Shared loader/manifest/profiles/index/root runtime/settings
were not edited. No push, PR, provider/Project/credential change, release or adoption.

No new owner-sensitive decision remains inside the selected source scope.
Coordinator owns content reconciliation, actual mapping, first push and integration.
#316 remains separate legacy authoring work for P5/P7 disposition. Do not infer its
acceptance or closure from this source delivery.
