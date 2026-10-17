# BDD as shared engineering knowledge

Use this guidance when a task needs shared understanding of behavior, concrete
examples or a bridge from requirements to verification. BDD is a collaborative
method, not a runner, file format or mandatory sequence of skills. This resource
does not adopt project rules, approve requirements or authorize implementation.

## Three iterative practices

| Practice | Useful work | Observable output |
| --- | --- | --- |
| Discovery | Discuss a small outcome with people who know the business, delivery and testing constraints; explore rules, examples and unknowns. | Agreed examples, explicit questions and a bounded next decision. |
| Formulation | Express selected examples precisely enough for people to check their shared understanding. | Readable behavior examples with source/status and expected outcomes. Gherkin is one possible form. |
| Automation | Connect agreed examples to the real system through tests and use their feedback while implementing behavior. | Executed checks and their actual results, with the tested boundary and limitations. |

These practices inform each other. A counterexample found while designing a test
can reopen a requirement question. Existing acceptance criteria can be enough to
start scenario design; there is no need to manufacture an earlier document.
Writing a scenario is formulation evidence, not proof that the system behaves
that way. Installing a test tool proves neither collaboration nor acceptance.

## Discovery through Example Mapping

Start with one small story or desired outcome. Keep these concerns distinguishable:

- A **rule** or acceptance criterion describes a constraint or expected result.
- An **example** makes that rule concrete with circumstances and an outcome.
- A **question** retains missing knowledge instead of silently choosing a rule.
- A newly found **story** may be split out when it has a separate useful outcome.

The following library example is illustrative, not a supplied product requirement:

| Item | Example |
| --- | --- |
| Story | A library member wants to renew a loan without an unnecessary visit. |
| R1 / AC1, assumed agreed for this example | A loan with another member's reservation cannot be renewed. |
| E1 | Loan L7 has a reservation; its borrower requests renewal; renewal is refused and the due date stays the same. |
| E2 | Loan L8 has no reservation. Whether renewal is allowed still depends on any other applicable rules. |
| Q1 | Can an overdue loan be renewed? Who can confirm this? |
| Possible later story | Inform a waiting member when a reserved item is returned. |

E2 does not establish that absence of a reservation guarantees renewal. Q1 must
remain open until its owner supplies a rule. Record provisional examples as such;
do not turn a plausible answer into an approved oracle. Stop when the current
slice is sufficiently understood, or identify the exact decision/evidence needed
next. A useful question can be the outcome of a discovery-only task.

## Traceability without artificial one-to-one mapping

A work-tracker Feature is not necessarily a Gherkin Feature. A story may have
several rules, and one rule may need success, boundary and rejection examples.
One scenario can cover several related outcomes. Preserve existing IDs and
source revisions; use clearly local labels when none exist.

For the library example, E1 can become a refusal scenario with two observations:
the refusal and the unchanged due date. Keep both when handing it to a test
implementer. If the source of an expected outcome changes, reassess affected
scenarios rather than treating their earlier approval as permanent.

Avoid making a new document for each name in this vocabulary. A short table in
an existing Issue can preserve the necessary relationships. User intent, an
author's recommendation, an accepted rule, observed implementation and an
executed result remain different kinds of evidence.

## Ownership and proportional use

| Need | Appropriate responsibility |
| --- | --- |
| Learn or apply the method | This task-selected knowledge; it does not require a new skill. |
| Clarify a story or requirement | The selected author/exploration operation and the people who own its decisions. |
| Design or review scenarios | The selected scenario operation owns coverage, setup, expected-value sources and test-level judgment. |
| Implement and execute tests | Separately authorized implementation and target-owned commands. |
| Choose runners, storage, review gates or required formats | The target project or explicitly selected technology profile. |

For exploration only, retain rules, examples and questions; do not force a
`.feature` or claim test coverage. For scenarios only, use the available behavior
source directly. For a combined request, reuse the same rules and IDs while
making unresolved examples provisional. Method guidance does not merge these
operations or create a mandatory requirements-to-release pipeline.

Knowledge selection makes guidance available, not a binding project rule. A
consumer with missing optional knowledge reports that coverage as unavailable
and can continue work supported by its own instructions and caller inputs.
Neither missing knowledge nor an example authorizes installing packages or
loading undeclared source resources.

## Sources and limits

Original synthesis and illustrative library example, checked 2026-10-14 against
[Cucumber BDD](https://cucumber.io/docs/bdd/) and
[Example Mapping](https://cucumber.io/docs/bdd/example-mapping/).
The ownership and handoff distinctions above are this framework's application
of the method. They do not claim Cucumber requires this framework's skills,
approval model, tracker or package protocol.
