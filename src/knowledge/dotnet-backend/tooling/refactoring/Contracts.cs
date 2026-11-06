using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RefactorTool;

internal sealed record Request
{
    [JsonRequired]
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

internal sealed record InputFile(string Path, string Hash,
    [property: JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] string? CanonicalPath = null);
internal sealed record FileEdit(string Path, string Kind, string Before, string After);
internal sealed record ProjectInfo(string Path, string Framework, string Configuration,
    string Nullable, string LanguageVersion, string[] Defines, string[] References);
internal sealed record DiagnosticInfo(string Project, string Id, string Message, string? File, int Start, int Length);
internal sealed record Plan
{
    [JsonRequired]
    public string Contract { get; init; } = "refactor-plan/1";
    [JsonRequired]
    public Request Request { get; init; } = new();
    public string Sdk { get; init; } = "";
    public string Roslyn { get; init; } = "";
    public string Symbol { get; init; } = "";
    public string[] RelatedSymbols { get; init; } = [];
    public ProjectInfo[] Projects { get; init; } = [];
    [JsonRequired]
    public InputFile[] Inputs { get; init; } = [];
    [JsonRequired]
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
        RespectNullableAnnotations = true,
        RespectRequiredConstructorParameters = true,
        AllowDuplicateProperties = false,
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
    };
    public static string Hash(byte[] value) => Convert.ToHexStringLower(SHA256.HashData(value));
    public static string Hash(Stream value) => Convert.ToHexStringLower(SHA256.HashData(value));
    public static string Serialize<T>(T value) => JsonSerializer.Serialize(value, Json);
    public static T Read<T>(string path, bool strictPath = false) where T : class
    {
        try
        {
            path = Path.GetFullPath(path);
            Require((File.GetAttributes(path) & FileAttributes.Directory) == 0, "invalid_input", $"Expected a JSON file: {path}");
            if (strictPath) Paths.RegularFile(path);
            var text = File.ReadAllText(path, new System.Text.UTF8Encoding(false, true));
            return JsonSerializer.Deserialize<T>(text, Json)
                ?? throw new RefactorFailure("invalid_input", "JSON must not be null.");
        }
        catch (Exception error) when (error is JsonException or FileNotFoundException or DirectoryNotFoundException or
            ArgumentException or System.Text.DecoderFallbackException or NotSupportedException)
        {
            throw new RefactorFailure("invalid_input", $"Invalid JSON input '{path}': {error.Message}");
        }
    }
    public static void Require(bool condition, string code, string message, object? detail = null)
    {
        if (!condition) throw new RefactorFailure(code, message, detail);
    }
}
