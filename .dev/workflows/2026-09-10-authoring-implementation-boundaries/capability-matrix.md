# Capability Matrix And Decision

Issues: #276 and #279. Source baseline: `7ad859fd3724cfd7d9a3f8165c003fb812c5c2e9`.

| Skill | Unique responsibility and output | Shared mechanics | Stop/handoff |
| --- | --- | --- | --- |
| requirement-author | Business intent, rules and ACs in requirement markdown | Source references, inferred/observed status, questions and next-output packet | Missing stakeholder authority is explicit; spec or architecture only for a needed distinct artifact/decision |
| spec-author | Selected production/entity/adapter/test spec and schema | Same traceability packet; source intake | Unknown architecture ownership goes to its owner; formal test-spec GWT stays here |
| problem-frame-author | CBF/SWF extraction sheet and required file set with source bindings | Same traceability packet; source intake | Observed code-only recovery stays inferred; no invented approved requirements or compliance |
| local-change-implementer | One target/operation plus direct usage and immediate tests | Authorization, normative/finding separation, compatibility and focused validation | New type, changed semantic contract, boundary or radius leaves local scope |
| slice-implementer | Coordinated bounded implementation goal; one command/query/reactor/generic mode | Same source separation and validation; can contain local edits | Architecture only for unresolved/changed decisions; optional local subtask delegation retains slice ownership |

Input overlap is expected: the same requirement or code may serve several output
types. It does not establish interchangeable responsibilities. The five skill
IDs, capability-slot mappings, frame/spec schemas and historical references remain.

The selected local design retains the skills and clarifies routing. Two compact
shared references own cross-skill selection and handoff rules; each skill retains
its output schema, domain steps and exact effective-rule consumption contract.
No new runtime router, skill, mandatory authoring stage or migration alias is
introduced. In particular, the repeated effective-rule declarations are required
per-consumer contracts, not accidental duplication to remove in this work.

Consolidation would require measurable routing/maintenance benefit and a safe
migration plan. Neither a smaller skill count nor overlapping inputs proves that
benefit. The controlled paired exercise will measure the chosen clarification;
its final report must state actual findings and limitations before final
acceptance. This decision does not claim production usage or observed savings.

The source-backed repair targets are:

- A276-01: output type is not explicit in shared-input/ambiguous routing guidance.
- A276-02: formal test-spec requests containing GWT can be redirected to scenario
  design, and code-only framing is contradicted by required input wording.
- A279-01: multi-file handoff wording conflicts with allowed direct call sites.
- A279-02: blanket new-abstraction architecture handoffs can repeat settled
  design; local substeps can create unnecessary owner round trips.
- A279-03: the slice handoff guide still describes the code reviewer as .NET-only
  after the integrated common reviewer change.

## Final Disposition

Retain the five identities and the two shared boundary contracts. See
[delivery report](remediation-report.md) for the complete trigger/input/schema
comparison, observed failures and six-case remediation, increased context-byte
envelope and unchanged required contract duplication. No routing, maintenance
or production-cost saving justifies consolidation in this evidence.
