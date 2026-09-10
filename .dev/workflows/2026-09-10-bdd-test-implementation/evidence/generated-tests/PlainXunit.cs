using GwtStepMethods;
using NSubstitute;
using Xunit;

namespace GwtStepMethods.PlainXunit;

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
    public async Task GENERATED_01_Should_return_zero_for_a_missing_query_month()
    {
        GivenBudgets(new MonthlyBudget("202205", 62m));
        await WhenQueryingBudget(new DateOnly(2022, 4, 1), new DateOnly(2022, 4, 2));
        ThenAmountShouldBe(0m);
    }

    [Fact]
    [Trait("Scenario", "GENERATED-02")]
    public async Task GENERATED_02_Should_prorate_the_selected_days()
    {
        GivenBudgets(new MonthlyBudget("202209", 90m));
        await WhenQueryingBudget(new DateOnly(2022, 9, 3), new DateOnly(2022, 9, 5));
        ThenAmountShouldBe(9m);
    }

    [Fact]
    [Trait("Scenario", "GENERATED-03")]
    public async Task GENERATED_03_Should_sum_budgets_across_a_month_boundary()
    {
        GivenBudgets(
            new MonthlyBudget("202112", 310m),
            new MonthlyBudget("202201", 620m));
        await WhenQueryingBudget(new DateOnly(2021, 12, 31), new DateOnly(2022, 1, 2));
        ThenAmountShouldBe(50m);
    }

    [Fact]
    [Trait("Scenario", "GENERATED-04")]
    public async Task GENERATED_04_Should_reject_an_inverted_range_before_reading_budgets()
    {
        GivenBudgets(new MonthlyBudget("202209", 90m));
        await WhenQueryingAnInvalidRange(new DateOnly(2022, 9, 5), new DateOnly(2022, 9, 4));
        ThenTheRangeShouldBeRejected();
        await ThenTheRepositoryShouldNotBeRead();
    }

    [Fact]
    [Trait("Scenario", "GENERATED-05")]
    public async Task GENERATED_05_Should_prorate_a_fractional_total()
    {
        GivenBudgets(new MonthlyBudget("202206", 15m));
        await WhenQueryingBudget(new DateOnly(2022, 6, 1), new DateOnly(2022, 6, 3));
        ThenAmountShouldBe(1.5m);
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
