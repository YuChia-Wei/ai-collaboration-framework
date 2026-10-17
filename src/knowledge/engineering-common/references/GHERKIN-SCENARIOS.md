# Expressing behavior with Gherkin

Use this guidance when Gherkin is requested or a selected scenario artifact
needs review. Scenario notes and decision tables can also express examples;
using BDD does not require a `.feature` file. A selected target owns file
placement, language dialect, runner, step definitions and execution commands.

## Syntax and design advice have different force

Gherkin uses `Feature:`, `Rule:`, `Scenario:` and `Scenario Outline:` headings.
`Examples:` supplies rows for an outline. `Given`, `When`, `Then`, `And` and
`But` introduce separate step lines without a colon. An `AND` embedded in a
sentence is just step text, not a second step. A step data table is an argument;
it is not an outline's set of example executions. Keywords can be localized;
use the target's selected dialect rather than translating them arbitrarily.

By contrast, recommending one main event and short behavior-focused scenarios
is design guidance, not a claim that Gherkin forbids action sequences. When a
sequence is essential, explain the behavior it demonstrates. Formatting alone
does not establish useful examples or sufficient assertions.

## Concrete state, event and observations

The following fictional library rule is assumed agreed only for this example:
another member's reservation prevents renewal, and refusal preserves the due
date. Labels R1/AC1 are local illustrative labels.

```gherkin
Feature: Renew a library loan
  Rule: A reservation prevents renewal
    Scenario: Refuse renewal of a reserved loan
      Given member Ada borrowed loan L7 with a due date of 20 October
      And member Ben has reserved the item on loan L7
      When Ada requests renewal of loan L7
      Then Ada receives a refusal because the item is reserved
      And Ada can see that loan L7 is still due on 20 October
```

Given establishes the relevant state; When identifies the event; Then describes
an observation with an expected result. Here both refusal and preservation of
the due date matter. Their expected values come from R1/AC1, not from copying
the implementation's output. A test fixture will also need an explicit clock
and calendar context if those affect this behavior.

Prefer the actor's or external system's observable contract over private storage
details for business acceptance. A lower-level test may inspect a domain result
or exception when that is its selected contract; state its boundary and avoid
presenting it as end-to-end evidence.

## Counterexamples and corrections

| Weak example | What to clarify or change |
| --- | --- |
| `Then renewal works correctly` | Specify the visible result and its independently supported expected value. |
| `Then the assistant understands the rule` | Identify an inspectable output, such as the recorded rule and open questions. |
| `Then Ada can submit a request AND the renewal succeeds` | Separate capability from a later submission event; success also needs an agreed rule. |
| `Given the previous scenario renewed the loan` | Establish this scenario's own loan state; do not rely on earlier execution. |
| `Then the private renewal table has three rows` | Explain why this is a selected contract or assert the externally relevant effect instead. |
| An overdue-loan scenario with an invented rejection policy | Retain the policy question and mark the affected example provisional. |

Scenarios may be ordered to help a reader follow a journey, but each must remain
independently executable. `Background` can express shared context; it does not
pass state from a previous scenario. Keep setup isolation and cleanup with the
target's fixture mechanism rather than prescribing a database or browser tool.

Use `Scenario Outline` when rows share the same behavior and step roles. Keep
data-row identity and the source of each expected value in the scenario mapping;
split materially different preconditions or events. Tags and headings support
organization but are not proof of coverage or a new authorization boundary.

## From expression to evidence

Before handoff, check the source/status of each rule, concrete data, unknowns,
important outcomes and the chosen observable boundary. The existing selected
GWT handoff contract owns implementation traceability; this guide does not
replace it or prescribe a new record format.

A rendered `.feature` remains a design artifact until connected to the system
and executed. Report parsing, step binding, test execution and behavior coverage
according to what actually occurred. A green test with no meaningful assertion
does not establish the described result; a mock cannot prove a real dependency's
behavior. Do not install a runner as a side effect of writing an example.

## Sources and limits

Original examples and framework handoff advice, checked 2026-10-14 against
[Gherkin Reference](https://cucumber.io/docs/gherkin/reference/),
[Writing better Gherkin](https://cucumber.io/docs/bdd/better-gherkin/) and
[Cucumber scenario state](https://cucumber.io/docs/cucumber/state/).
This is a focused expression guide, not a complete grammar or runner manual.
