using System.Reflection;
using System.Text.Json.Serialization;

namespace FormatTool;

[JsonUnmappedMemberHandling(JsonUnmappedMemberHandling.Disallow)]
internal sealed class Request
{
    public int SchemaVersion { get; set; }
    public string Workspace { get; set; } = "";
    public string[] Files { get; set; } = [];
    public string Mode { get; set; } = "";
    public string Action { get; set; } = "";
    public bool AllowRestore { get; set; }
    public string[] Diagnostics { get; set; } = [];
    public string? Severity { get; set; }
    public string[] AllowedProjectAnalyzers { get; set; } = [];
}

internal sealed class Result
{
    public int SchemaVersion { get; } = 1;
    public string ToolVersion { get; } = typeof(Result).Assembly.GetCustomAttribute<AssemblyInformationalVersionAttribute>()!.InformationalVersion;
    public string Status { get; set; } = "failed";
    public string? ErrorCode { get; set; }
    public string? Message { get; set; }
    public string? SdkVersion { get; set; }
    public string? FormatterVersion { get; set; }
    public string? Workspace { get; set; }
    public string? PathBase { get; set; }
    public string? Mode { get; set; }
    public string? Action { get; set; }
    public string[] Diagnostics { get; set; } = [];
    public string? Severity { get; set; }
    public RuleCapability[] RuleCapabilities { get; } = Rules.Capabilities;
    public string[] ProjectAnalyzers { get; set; } = [];
    public string[] ReferencedProjects { get; set; } = [];
    public string[] SelectedFiles { get; set; } = [];
    public string[] LoadedProjects { get; set; } = [];
    public string[] ConfigurationFiles { get; set; } = [];
    public string[] ChangedFiles { get; set; } = [];
    public string[] UnexpectedChangedFiles { get; set; } = [];
    public Finding[] Findings { get; set; } = [];
    public Finding[] RemainingFindings { get; set; } = [];
    public List<CommandResult> Commands { get; } = [];
    public string[] Notes { get; } =
    [
        "Files are Compile members; SDK generated-code exclusions still apply. Generated code is never explicitly included.",
        "ConfigurationFiles lists ancestor .editorconfig candidates, not an independently evaluated rule set. Commands retain the SDK configuration/load log.",
        "Missing settings use this SDK's defaults. Unknown and vendor-specific settings are not claimed as applied.",
        "Check requests no formatter source writes. Trusted MSBuild/restore may write intermediates or run custom targets. Observed Compile-file changes are reported; this is not a sandbox or rollback transaction.",
        "A clean result concerns selected formatting only, not compilation or business correctness."
    ];
}

internal sealed record Finding(string File, string DiagnosticId, int Line, int Column, string Description);
internal sealed record RuleCapability(string DiagnosticId, string Mode, string Availability, string SdkVersion);
internal sealed record CommandResult(string[] Arguments, string WorkingDirectory, int ExitCode, string StandardOutput, string StandardError);
internal sealed class ToolFailure(string code, string message) : Exception(message)
{
    public string Code { get; } = code;
}

[JsonSourceGenerationOptions(PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase, WriteIndented = true)]
[JsonSerializable(typeof(Request))]
[JsonSerializable(typeof(Result))]
internal partial class WireJson : JsonSerializerContext;
