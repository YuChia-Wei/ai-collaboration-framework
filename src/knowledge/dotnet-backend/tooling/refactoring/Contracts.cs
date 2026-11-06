using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RefactorTool;

internal sealed record Request
{
    public string Workspace { get; init; } = "";
    public string Configuration { get; init; } = "Debug";
    public string? Framework { get; init; }
    public string? File { get; init; }
    public int? Line { get; init; }
    public int? Column { get; init; }
    public string? Symbol { get; init; }
    public string? Project { get; init; }
    public string NewName { get; init; } = "";
    public bool RenameOverloads { get; init; }
}

internal sealed record InputFile(string Path, string Hash);
internal sealed record FileEdit(string Path, string Kind, string Before, string After);
internal sealed record ProjectInfo(string Path, string Framework, string Configuration,
    string Nullable, string LanguageVersion, string[] Defines, string[] References);
internal sealed record DiagnosticInfo(string Project, string Id, string Message, string? File, int Start, int Length);
internal sealed record Plan
{
    public string Contract { get; init; } = "refactor-plan/1";
    public Request Request { get; init; } = new();
    public string Sdk { get; init; } = "";
    public string Roslyn { get; init; } = "";
    public string Symbol { get; init; } = "";
    public string[] RelatedSymbols { get; init; } = [];
    public ProjectInfo[] Projects { get; init; } = [];
    public InputFile[] Inputs { get; init; } = [];
    public FileEdit[] Edits { get; init; } = [];
    public DiagnosticInfo[] BaselineErrors { get; init; } = [];
    public DiagnosticInfo[] NewErrors { get; init; } = [];
    public string[] Limits { get; init; } = [];
    public string Patch { get; init; } = "";
}

internal sealed class RefactorFailure(string code, string message, object? detail = null) : Exception(message)
{
    public string Code { get; } = code;
    public object? Detail { get; } = detail;
}

internal static class Data
{
    public static readonly JsonSerializerOptions Json = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true,
        AllowDuplicateProperties = false,
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
    };
    public static string Hash(byte[] value) => Convert.ToHexStringLower(SHA256.HashData(value));
    public static string Serialize<T>(T value) => JsonSerializer.Serialize(value, Json);
    public static T Read<T>(string path) => JsonSerializer.Deserialize<T>(System.IO.File.ReadAllText(path), Json)
        ?? throw new RefactorFailure("invalid_input", "JSON must not be null.");
    public static void Require(bool condition, string code, string message, object? detail = null)
    {
        if (!condition) throw new RefactorFailure(code, message, detail);
    }
}
