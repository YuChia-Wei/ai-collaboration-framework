using FormatTool;

namespace FormatTool.UnitTests;

public sealed class CleanupRulesTests
{
    [Theory]
    [InlineData("style", null, null, "invalid-request")]
    [InlineData("style", "IDE0008", null, "invalid-request")]
    [InlineData("style", "IDE9999", "warn", "unsupported-diagnostic")]
    [InlineData("analyzers", "IDE0008", "warn", "unsupported-diagnostic")]
    [InlineData("analyzers", "CA1040", "warn", "no-fixer")]
    [InlineData("whitespace", "IDE0008", "warn", "invalid-request")]
    public void Should_reject_unsupported_cleanup_when_validating_the_request(
        string mode, string? diagnostic, string? severity, string expectedCode)
    {
        Request request = null!;
        Exception? failure = null;

        this.Given(GivenTheRequestedCleanup, "the requested cleanup")
            .When(WhenValidatingTheCleanup, "validating the cleanup")
            .Then(ThenReportTheExpectedFailure, "report the expected failure")
            .BDDfy();

        void GivenTheRequestedCleanup() => request = new Request
        {
            Mode = mode,
            Diagnostics = diagnostic is null ? [] : [diagnostic],
            Severity = severity
        };

        void WhenValidatingTheCleanup() => failure = Record.Exception(() => Rules.Validate(request));

        void ThenReportTheExpectedFailure() => Assert.Equal(expectedCode, Assert.IsType<ToolFailure>(failure).Code);
    }
}
