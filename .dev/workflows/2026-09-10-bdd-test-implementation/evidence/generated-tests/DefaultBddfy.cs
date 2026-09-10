using GwtStepMethods;
using NSubstitute;
using TestStack.BDDfy;
using Xunit;

namespace GwtStepMethods.DefaultBddfy;

public sealed class GeneratedBudgetQueryTests
{
    private readonly IBudgetRepository _repository = Substitute.For<IBudgetRepository>();
    private readonly BudgetQuery _query;
    private decimal? _actual;
    private Exception? _exception;

    public GeneratedBudgetQueryTests()
    {
        _query = new BudgetQuery(_repository);
    }

    [Fact]
    [Trait("Scenario", "GENERATED-01")]
    public void GENERATED_01_Should_return_zero_for_a_missing_query_month()
    {
        this.Given(x => x.GivenBudgets(new MonthlyBudget("202205", 62m)))
            .When(x => x.WhenQueryingBudget(
                new DateOnly(2022, 4, 1), new DateOnly(2022, 4, 2)))
            .Then(x => x.ThenAmountShouldBe(0m))
            .BDDfy();
    }

    [Fact]
    [Trait("Scenario", "GENERATED-02")]
    public void GENERATED_02_Should_prorate_the_selected_days()
    {
        this.Given(x => x.GivenBudgets(new MonthlyBudget("202209", 90m)))
            .When(x => x.WhenQueryingBudget(
                new DateOnly(2022, 9, 3), new DateOnly(2022, 9, 5)))
            .Then(x => x.ThenAmountShouldBe(9m))
            .BDDfy();
    }

    [Fact]
    [Trait("Scenario", "GENERATED-03")]
    public void GENERATED_03_Should_sum_budgets_across_a_month_boundary()
    {
        this.Given(x => x.GivenBudgets(
                new MonthlyBudget("202112", 310m),
                new MonthlyBudget("202201", 620m)))
            .When(x => x.WhenQueryingBudget(
                new DateOnly(2021, 12, 31), new DateOnly(2022, 1, 2)))
            .Then(x => x.ThenAmountShouldBe(50m))
            .BDDfy();
    }

    [Fact]
    [Trait("Scenario", "GENERATED-04")]
    public void GENERATED_04_Should_reject_an_inverted_range_before_reading_budgets()
    {
        this.Given(x => x.GivenBudgets(new MonthlyBudget("202209", 90m)))
            .When(x => x.WhenQueryingAnInvalidRange(
                new DateOnly(2022, 9, 5), new DateOnly(2022, 9, 4)))
            .Then(x => x.ThenTheRangeShouldBeRejected())
            .And(x => x.ThenTheRepositoryShouldNotBeRead())
            .BDDfy();
    }

    [Fact]
    [Trait("Scenario", "GENERATED-05")]
    public void GENERATED_05_Should_prorate_a_fractional_total()
    {
        this.Given(x => x.GivenBudgets(new MonthlyBudget("202206", 15m)))
            .When(x => x.WhenQueryingBudget(
                new DateOnly(2022, 6, 1), new DateOnly(2022, 6, 3)))
            .Then(x => x.ThenAmountShouldBe(1.5m))
            .BDDfy();
    }

    private void GivenBudgets(params MonthlyBudget[] budgets)
    {
        _repository.GetAllAsync(Arg.Any<CancellationToken>())
            .Returns(Task.FromResult<IReadOnlyList<MonthlyBudget>>(budgets));
    }

    private async Task WhenQueryingBudget(DateOnly start, DateOnly end)
    {
        _actual = await _query.QueryAsync(start, end, CancellationToken.None);
    }

    private async Task WhenQueryingAnInvalidRange(DateOnly start, DateOnly end)
    {
        _exception = await Record.ExceptionAsync(
            () => _query.QueryAsync(start, end, CancellationToken.None));
    }

    private void ThenAmountShouldBe(decimal expected)
    {
        Assert.True(_actual.HasValue, "The query action must produce a result.");
        Assert.Equal(expected, _actual.Value);
    }

    private void ThenTheRangeShouldBeRejected()
    {
        var exception = Assert.IsType<ArgumentException>(_exception);
        Assert.Equal("end", exception.ParamName);
    }

    private async Task ThenTheRepositoryShouldNotBeRead()
    {
        await _repository.DidNotReceive().GetAllAsync(Arg.Any<CancellationToken>());
    }
}
