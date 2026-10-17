# Independent User Story capability

## Authority and delivery

The owner explicitly authorized local implementation and validation of #459 on
2026-10-17: create independent `user-story-author`, with plan, draft, normalize,
whole-Story review and selected-AC review, using the three previously inspected
template discussions. That selects the former standalone alternative. Issue #459
is the existing work binding; its eight criteria are fixed in criteria.json.

Reuse the clean dedicated branch `codex/2026-10-17-method-knowledge-skills`, which
started from main at b8cfbcc12c98c71a5b2d045febde69c292ef898f. This new workflow
starts at cf0651dc467fd9806b41935283e835c32957424a, after the separately completed
#454–458 local delivery. Those dependencies are local commits, not main adoption.
One coordinator owns integration; at most one tracked writer is active.

Owner-selected scope: local source/manifest/manual changes, necessary isolated
validation and local commits. Push, PR, merge, Issue closure, publication and
real-project installation remain separate. #461 is explicitly outside this task.
The owner's #461 reminder applies now: avoid broad repeated validation for
whitespace, documentation or terminal-record-only changes.

## Accepted design

- New optional, standalone `user-story-author@0.1.0`, metadata 3 instruction
  package, no required skill/provider/knowledge/runtime-tool dependency.
- Public operations plan/draft/normalize/review; review receives whole Story or
  selected AC IDs/content spans. It reads needed context but reports only the
  selected subject and never changes the reviewed artifact or provider state.
- Caller-selected templates take precedence. Defaults retain user-value,
  business-rule and technical Description sections from the two discussions,
  separate AC output, and portable sources/dependencies/unknowns/next-step/authority.
- Preserve existing GWT and non-Gherkin criteria, IDs, statuses and decisions.
  Research work describes a bounded learning outcome and stopping condition.
- Requirement-author retains broader PRD/Feature requirements; the new skill owns
  dedicated Story planning/authoring/review. Test-designer retains test design.
  None of these owners becomes a mandatory authoring pipeline.
- All runtime resources originate under src/skills/user-story-author. Private
  conversations and their illustrative financial data are not runtime dependencies.
- Add the catalog component and manuals; keep current presets and installed
  source-project projections unchanged, following existing optional-package practice.
  Update only directly affected owner-routing versions and current catalog counts.

## Proportionate validation plan

1. Author inspect the complete new skill, references/templates/examples, owner
   routing and manifest. Run the existing distribution suite once for metadata,
   manifest and adapters; no prose-mirroring tests or new product validators.
2. Commit the candidate and obtain one independent scoped read-only review of
   immutable diff, eight criteria and source rules. Resolve findings before costly
   final assembly. Cosmetic findings require only their affected checks.
3. After source content stabilizes, run the source-policy default suite once.
   Do not repeat it for terminal records or semantically empty changes. Material
   repairs get only the tests whose inputs/behavior changed, with explicit reasons.
4. Assemble one fixed catalog. Install two small isolated consumers: Story alone
   with both adapters/original naming, and Story + test-designer with prefixed
   naming for the selected combination. No old-ID migration is introduced.
5. Three fresh bounded actor assignments cover the four operations, all three
   templates, whole/selected-AC review, preserved GWT/custom form and independent
   handoff into test design. Fixed prompts/expectations precede execution; actors
   receive inputs only. Parent judges actual output and resource reads.
6. Reuse prior unrelated migration/drift/customization, optional BDD/DDD and CBF
   evidence only after exact relevant source/dependency/runner equivalence. Do
   not rerun the #457 matrix for a newly added independent package. Record limits.

Metadata/manifest checks are input-sensitive; actor results bind instruction and
input bytes; install results bind selected package/engine/host state. Full tests
bind tested source/configuration/environment. Git identity alone does not require
re-execution. Record-only commits get deterministic subject rebind and record checks.

## Work and next action

The coordinator owns design, integration and final judgments. Bounded implementation
may be delegated under source policy with this exact scope; independent review
remains separate from author work. Local tasks are implementation and validation-review.
Start by creating the new source package and direct catalog/routing/manual changes.
Do not add another work-management store or update #461 policy in this workflow.
