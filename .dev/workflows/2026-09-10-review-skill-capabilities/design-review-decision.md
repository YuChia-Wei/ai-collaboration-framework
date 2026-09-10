# Existing Skill Modes And Handoffs

Issue: #290. Decision: keep the existing architecture and BDD skills with
explicit `design` and `review` modes. No new skill or mandatory stage is added.
This is the implementation decision within the owner's local authorization;
provider Owner-review and release admission remain separate states.

| Capability | Owned artifact | Review input/output | Shared versus selected rules | Next owner |
| --- | --- | --- | --- | --- |
| Architecture design/review | Architecture proposal and decision record | Fixed proposal plus requirements/quality constraints -> evidence-backed findings, valid alternatives, uncertainty and corrections | DDD/CA/HEX method and shared subject/evidence contract; target-selected language, broker, ORM, DI and tooling rules | requirement-author for requirement decisions; spec-author for specs; BDD designer for scenarios; applicable implementer after accepted design and authorization |
| BDD design/review | GWT scenario/assertion design | Fixed scenarios plus ACs -> coverage, assertability, precondition, layer and failure findings | GWT method and shared subject/evidence contract; selected testing framework/runner/mocking conventions | requirement-author for ambiguous intent; spec-author for spec artifacts; architect for boundary decisions; slice-implementer for separately authorized concrete tests |
| Code review | Findings about executable code | Fixed code plus intended behavior -> code defects and review coverage | Common reviewer plus installed selected technology extensions | local-change-implementer or slice-implementer within authorized scope |
| Spec compliance | Selected compliance verdict | Accepted requirements/specs and required implementation/execution evidence | Existing compliance skill and its gate | Spec-compliance-validator owns the verdict; design/review completion is insufficient |

The two authoring skills already own the reasoning criteria needed to assess
their artifacts. Sharing mode, subject and reporting semantics avoids duplicate
entry points and leaves criterion ownership clear. Separate review skills would
add wrappers, routing, package and maintenance work without a demonstrated
capability benefit in the selected examples. A new mandatory stage would add
execution cost even to small design tasks; no evidence here justifies it.

An author can use `review` for a self-check. Independence requires a reviewer
who did not author or repair the fixed artifact plus the applicable evidence
contract; using the same skill neither grants nor prevents independence.

Existing identities, authoring outputs, GWT ordering, optional `.feature` design,
BDD-to-implementation handoff and exact effective-rule semantics remain.
Common assets stay in software development core. Existing .NET architecture
guidance moves behind the optional component's design route; canonical .NET
standards, rule IDs, transaction exceptions and target opt-outs remain owners.
For later upgrades, normal package provenance and customization reconciliation
must classify locally customized moved references before removal. This source
change does not itself prove downstream upgrade or production adoption.
