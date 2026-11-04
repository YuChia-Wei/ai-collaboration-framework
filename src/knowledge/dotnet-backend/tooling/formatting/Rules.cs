namespace FormatTool;

internal static class Rules
{
    internal const string SdkVersion = "10.0.403";
    internal static readonly RuleCapability[] Capabilities =
    [
        new("IDE0008", "style", "supported", SdkVersion),
        new("CA1805", "analyzers", "supported", SdkVersion),
        new("CA1040", "analyzers", "no-fixer", SdkVersion)
    ];

    public static void Validate(Request request)
    {
        if (request.Diagnostics == null || request.AllowedProjectAnalyzers == null ||
            request.AllowedProjectAnalyzers.Any(string.IsNullOrWhiteSpace))
            throw new ToolFailure("invalid-request", "Diagnostic and analyzer selections must be arrays, not null.");
        if (request.Mode == "whitespace")
        {
            if (request.Diagnostics.Length > 0 || request.Severity != null || request.AllowedProjectAnalyzers.Length > 0)
                throw new ToolFailure("invalid-request", "Whitespace does not accept cleanup selections.");
            return;
        }
        if (request.Diagnostics.Length == 0 || request.Diagnostics.Any(string.IsNullOrWhiteSpace) ||
            request.Severity is not ("info" or "warn" or "error"))
            throw new ToolFailure("invalid-request", "Cleanup requires nonempty diagnostic IDs and severity info, warn, or error.");
        foreach (var id in request.Diagnostics)
        {
            var capability = Capabilities.SingleOrDefault(rule => rule.DiagnosticId == id && rule.Mode == request.Mode);
            if (capability == null)
                throw new ToolFailure("unsupported-diagnostic", $"{id} is not supported in {request.Mode} by this tool's SDK {SdkVersion} rule list.");
            if (capability.Availability == "no-fixer")
                throw new ToolFailure("no-fixer", $"{id} has no associated SDK {SdkVersion} code fix; no cleanup was executed.");
        }
    }
}
