# Source skill routing audit

Input: `dc55bb509dc7af4a2f2380054c48c63eadfd02af`; scope is all 19 directories in
`src/skills/`, their entries, relevant methods and declared operation metadata.
Root read the context family. Three bounded read-only agents examined engineering,
execution and record families; root reviewed their findings and owns all edits.
This is a static instruction audit, not an agent routing benchmark.

## Complete disposition

Paths below are relative to `src/skills/<skill>/`. Unchanged means sufficient for
this routing question, not a global quality or behavior certification.

| Skill | Disposition | Source basis and selected change |
| --- | --- | --- |
| ai-context-init | Clarified | `SKILL.md`, `references/initialize.md`: missing foundations versus facts/commands/navigation refresh; rule/precedence redesign has another owner. |
| ai-context-auditor | Clarified | `SKILL.md`, `references/audit.md`: findings/comparison keeps subject read-only; no universal pre-edit audit. |
| ai-context-governance | Clarified | `SKILL.md`, `references/maintenance.md`: default ongoing context maintenance, rules/responsibilities/conflicts; explicit factual refresh can remain with init. |
| requirement-author | Unchanged | `SKILL.md`, `references/authoring.md`: requested requirement artifact controls selection, not source-code input or GWT wording. |
| spec-author | Unchanged | `SKILL.md`, `references/authoring.md`: production/entity/adapter/formal-test outputs already separate from requirements and scenario sets. |
| bdd-gwt-test-designer | Clarified | `SKILL.md` exposes the scenario-set versus formal-test-spec distinction already in `references/design.md`. |
| problem-frame-author | Clarified | `SKILL.md`, `references/authoring.md`: draft feedback versus full criterion/evidence assessment; naming a command does not select CBF. |
| spec-compliance-validator | Clarified | `SKILL.md`, `references/compliance.md`: complete criterion/evidence planning and assessment versus draft or scenario design. |
| ddd-ca-hex-architect | Unchanged | `SKILL.md`, `references/review.md`: architecture design/artifact review and optional record handoffs are explicit. |
| code-reviewer | Clarified | `SKILL.md`, `references/review.md`: selected code/diff/implementation-guidance defects versus symptom investigation; specialist artifact reviews retain their owners. |
| diagnostic-analyst | Clarified | `SKILL.md`, `references/diagnose.md`: observed discrepancy and causal evidence; settled repair need not repeat diagnosis. |
| local-change-implementer | Clarified | `SKILL.md`, `references/implement.md`: one target/operation preserving boundaries; a public class's internal method fix can remain local. |
| slice-implementer | Clarified | `SKILL.md`, `references/implement.md`: complete behavior, coordinated refactor or concrete tests; retains internal edit ownership. |
| software-development-orchestrator | Clarified table only | Existing entry already separates connected stages from bounded single-stage work. Synchronize candidate table in `references/orchestrate.md` with selected output distinctions. |
| adr-author | Clarified and corrected | Entry distinguishes architectural choice records from design/observations; remove unsupported `reconcile` result prose from `references/operations.md`. |
| lesson-author | Clarified and corrected | Entry distinguishes observations from diagnosis/decisions/rule edits; remove unsupported `reconcile` result prose from `references/operations.md`. |
| local-backlog | Unchanged | `SKILL.md`, `references/operations.md`: local-file records, truthful state and reference-only Issue links; no remote synchronization or development execution authority. |
| pr-author | Clarified | Entry/description name exact read/create/update boundary; `references/github.md` already excludes merge, closure and other provider administration. |
| standards-promotion | Unchanged | Entry and `references/authority.md` already restrict it to selected standalone experiments, proposal-only writes and separate adoption/content/effect observations; no apply operation. |

The ADR/Lesson operation tables and metadata have no `reconcile`; the removed
sentences described promotion's result dimensions. Promotion's own reconcile
documentation stays intact. No tool behavior is added or removed.

## Representative selection checks

These are root-reviewed static examples of intended instruction meaning. They
are not executed agent tasks, source-code tests or downstream acceptance results.

| Request | Expected route and boundary |
| --- | --- |
| Existing codebase lacks AGENTS and a useful context entry | Init initialize; existing implementation does not prevent first context setup. |
| Refresh AGENTS build commands and repository facts using current files | Init refresh when selected; preserve existing rules and custom sections. |
| Maintain existing context after a module move and reconcile conflicting rules | Governance; ongoing maintenance can include facts and navigation. |
| Redesign document responsibilities or change collaboration rule precedence | Governance with actual owner authority; outside init refresh. |
| Check context for contradictions, or compare two context revisions | Auditor; subject remains read-only. |
| Fix this already identified context rule inconsistency | Authorized governance apply; no forced audit or proposal ceremony. |
| Explicitly use the only installed init package for a factual refresh | Init refresh remains independently useful; no mandatory peer installation. |
| Update the framework's src skill instructions | Source-product maintenance under source policy; not downstream governance merely because text is context. |
| Write business requirements from code and express acceptance as GWT | Requirement author; observation is not automatically adopted intent. |
| Produce a formal-test specification containing GWT | Spec author; formal artifact controls selection. |
| Design or review only a GWT matrix or .feature | BDD designer; runner installation and test implementation are separate. |
| Review a commanded-behavior frame draft for missing boundaries | Problem-frame review-draft. |
| Plan evidence for every criterion or assess those criteria against actual execution | Compliance validator; missing required evidence remains unavailable. |
| Compare aggregate or dependency boundary alternatives | Architect; an ADR is added only when that record is requested/required. |
| Find defects in this retry/cancellation PR diff | Code reviewer; static causal findings need not force diagnosis. |
| Explain why requests sometimes execute twice | Diagnostic analyst; uncertainty and competing causes remain explicit. |
| Fix a known null branch inside a public class without changing contracts | Local implementer; public class presence does not force a slice. |
| Tune one repository SQL query while preserving results and contracts | Local implementer; the word query is not a behavior-mode selector. |
| Implement an accepted query API with authorization, mapping and tests | Slice implementer query; owns its internal local edits. |
| Extract an accepted outbound port across adapter, DI and contract tests | Slice implementer generic; coordinated boundary change. |
| Implement tests from complete accepted GWT scenarios | Slice implementer generic; no mandatory redesign of those scenarios. |
| Deliver a feature needing requirements, design, implementation and review | Orchestrator; routine inspect/edit/test within one settled fix remains with its implementer. |
| Preserve architecture alternatives, tradeoffs and owner decision evidence | ADR author; accepted record does not prove implementation. |
| Preserve an observed incident with evidence, confidence and applicability | Lesson author; tentative observations need no invented confirmed cause. |
| Add or update a local work item and acceptance criteria | Local backlog; remote Issue state is a separate provider operation. |
| Prepare PR content from a real commit diff or create an authorized draft PR | PR author; review/merge/Issue closure retain separate owners. |
| Store and observe a single rule replacement proposal in a selected experiment | Experimental promotion if actually available; ordinary authorized rule editing does not require it. |

Peer names express optional choices. No metadata dependency or universal pipeline
was introduced; explicit in-scope user selection and actual target policy govern.
