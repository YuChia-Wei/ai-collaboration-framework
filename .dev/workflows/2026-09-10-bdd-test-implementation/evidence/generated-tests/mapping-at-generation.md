# Generated Budget Query Test Mapping

Source: `.dev/workflows/2026-09-10-bdd-test-implementation/generation-cases.yaml`
(`bdd-293-generation`, revision `ef8b63d7650e640feb8de7730b0f88e557f5dc88`).
Test level: isolated use-case unit test. The real subject is
`GwtStepMethods.BudgetQuery.QueryAsync`; only
`GwtStepMethods.IBudgetRepository.GetAllAsync` is substituted with NSubstitute.

The same five source scenarios are implemented independently in both selected
profiles. `DefaultBddfy` uses the xUnit + BDDfy default fluent chain;
`PlainXunit` is the explicitly selected BDDfy opt-out and calls the same GWT
steps directly. Each test has a `[Trait("Scenario", "GENERATED-XX")]` and a
method name containing the same source ID, so every row is independently
discoverable. Generated code has not been built or executed by this task.

| Source ID | DefaultBddfy test | PlainXunit test | Given data and When input | Then / And assertions |
| --- | --- | --- | --- | --- |
| `GENERATED-01` | `DefaultBddfy/GeneratedBudgetQueryTests.cs::GENERATED_01_Should_return_zero_for_a_missing_query_month` | `PlainXunit/GeneratedBudgetQueryTests.cs::GENERATED_01_Should_return_zero_for_a_missing_query_month` | Given `MonthlyBudget("202205", 62m)`; query `2022-04-01` through `2022-04-02` via `WhenQueryingBudget` | `ThenAmountShouldBe(0m)` asserts the exact missing-month total |
| `GENERATED-02` | `DefaultBddfy/GeneratedBudgetQueryTests.cs::GENERATED_02_Should_prorate_the_selected_days` | `PlainXunit/GeneratedBudgetQueryTests.cs::GENERATED_02_Should_prorate_the_selected_days` | Given `MonthlyBudget("202209", 90m)`; query `2022-09-03` through `2022-09-05` via `WhenQueryingBudget` | `ThenAmountShouldBe(9m)` asserts the exact total |
| `GENERATED-03` | `DefaultBddfy/GeneratedBudgetQueryTests.cs::GENERATED_03_Should_sum_budgets_across_a_month_boundary` | `PlainXunit/GeneratedBudgetQueryTests.cs::GENERATED_03_Should_sum_budgets_across_a_month_boundary` | Given `MonthlyBudget("202112", 310m)` and `MonthlyBudget("202201", 620m)`; query `2021-12-31` through `2022-01-02` via `WhenQueryingBudget` | `ThenAmountShouldBe(50m)` asserts the exact inclusive cross-month total |
| `GENERATED-04` | `DefaultBddfy/GeneratedBudgetQueryTests.cs::GENERATED_04_Should_reject_an_inverted_range_before_reading_budgets` | `PlainXunit/GeneratedBudgetQueryTests.cs::GENERATED_04_Should_reject_an_inverted_range_before_reading_budgets` | Given `MonthlyBudget("202209", 90m)`; query `2022-09-05` through `2022-09-04` via `WhenQueryingAnInvalidRange` | `ThenTheRangeShouldBeRejected` asserts exact `ArgumentException` and `ParamName == "end"`; `ThenTheRepositoryShouldNotBeRead` awaits NSubstitute `DidNotReceive` for `GetAllAsync` |
| `GENERATED-05` | `DefaultBddfy/GeneratedBudgetQueryTests.cs::GENERATED_05_Should_prorate_a_fractional_total` | `PlainXunit/GeneratedBudgetQueryTests.cs::GENERATED_05_Should_prorate_a_fractional_total` | Given `MonthlyBudget("202206", 15m)`; query `2022-06-01` through `2022-06-03` via `WhenQueryingBudget` | `ThenAmountShouldBe(1.5m)` asserts the exact fractional total |

## Step responsibilities

`GivenBudgets` configures the controlled repository response and receives all
scenario values from the test body. `WhenQueryingBudget` awaits exactly one
real `BudgetQuery.QueryAsync` action and captures its nullable result.
`WhenQueryingAnInvalidRange` awaits `Record.ExceptionAsync` around exactly that
real action and captures the exception for Then assertions. `ThenAmountShouldBe`
checks that a result was captured and compares the stated expected decimal;
it does not recalculate the subject algorithm. The invalid-range Then methods
check both exception requirements and the zero repository-read requirement.

## Execution status

All ten profile-specific tests are **generated, unexecuted**. Build, discovery,
test execution and result evidence remain pending for the root integration
owner. This mapping is a controlled example exercise and does not claim
general generation reliability or downstream adoption.
