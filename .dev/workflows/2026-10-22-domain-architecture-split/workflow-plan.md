# Domain modeling and software architecture split

## Authority and coherent delivery

Owner's 2026-10-22 instruction authorizes complete design, another agent's review before
source edits, Chinese Feature/User Story creation, then local implementation and necessary
validation. Accepted names: domain-model-designer and software-architect. Retire the old
combined skill without alias. Preserve unrelated untracked 2026-10-19/20 workflow folders.

One coherent delivery contains [Feature #476](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/476)
and Stories [#477](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/477),
[#478](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/478),
[#479](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/479), and
[#480](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/480).
Domain work comes first; distribute the complete coordinated result together.

Local-workflow [Feature #481](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/481)
and design [Story #483](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/483),
customization [Feature #482](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/482)
and design [Story #484](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/484)
are separate future work. They were created and read back open with Chinese scope/ACs;
no implementation or provider/data migration is included here. Issue parentage is explicit
bidirectional body links; native GitHub sub-issue fields were not set by the connector.

## Design and baseline

- Source baseline: f96fffe0af6e9e4f79d5f2f4be05bb3665553123.
- [Complete design](../../design/skill-evolution-2026-10-22/README.md).
- Initial immutable design: 4ade82bcc2eb4f8bc1230dbe9905c4db58293cbf.
- Review: /root/split_design_review, separate author, fresh context, read-only fixed commit.
- Current phase: implementation. R1-R3 corrections at3a3e3098 independently verified resolved; src unchanged at the design gate.
- Parent is the only tracked writer. Read-only delegates assist discovery/review only.
- Configured fallback model/effort: gpt-6-astra/low; actual provider execution identity is
  not exposed. Delegates inherit session settings; no model/effort override was requested.

## Work and acceptance

DESIGN owns self-contained documentation, immutable review, finding disposition and Issues.
IMPLEMENT owns the five principal skill boundaries, two new packages, knowledge/preset/version
closure, old-ID removal and human/source navigation. VERIFY owns the directly affected
checks, fixed-source review and honest delivery limitations. See each task JSON for state.

Acceptance is A-AC-01 through A-AC-13 in skill-contracts.md and F-AC/Story criteria in Issues.
Existing distribution/schema suites and narrow selection/binding tests are selected because
public operation/selection/dependency contracts change. Full installation/native/E2E/AI model
matrices are not selected. Document-only stage used local-link validation (110 links in 11
changed Markdown files) and git diff --check; no product test pass is claimed for that stage.

## Delivery boundary and next action

Design review and Issue corrections are complete. Implement, validate, commit and
record the final independent review. Push, PR, main merge, hosted CI, Issue closure, Project
fields, self-installation, downstream upgrade, release/tag/publication are outside current
authority. Local passing checks will not be reported as hosted or installed acceptance.
