using System.Text.Json.Serialization;

namespace SnippetTool;

internal sealed record Request(
    int SchemaVersion, string? Operation, string? Source, string? Query, string? Id,
    Dictionary<string, string?>? Parameters, int? Indent, string? Newline);

internal sealed record SourceIdentity(string Id, string Version);
internal sealed record CatalogDocument(int SchemaVersion, SourceIdentity? Source, SnippetDefinition[]? Snippets);

internal sealed record SnippetDefinition(
    string Id, string Title, string Description, string Context, string BodyFile,
    string[] Tags, string[] RequiredUsings, string[] Preconditions,
    Dictionary<string, ParameterDefinition> Parameters)
{
    internal SnippetSummary Summary() => new(Id, Title, Description, Context, Tags);
}

internal sealed record ParameterDefinition(string Kind, string? Default, string[]? Values);
internal sealed record SnippetSummary(string Id, string Title, string Description, string Context, string[] Tags);

internal sealed record Success(
    int SchemaVersion, string Operation, SourceIdentity Source,
    SnippetSummary[]? Snippets = null, SnippetDefinition? Snippet = null,
    string? Body = null, string? Text = null);

internal sealed record Failure(int SchemaVersion, Error Error);
internal sealed record Error(string Code, string Message);

internal sealed class SnippetError(string code, string message) : Exception(message)
{
    internal string Code { get; } = code;
}

[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    AllowDuplicateProperties = false)]
[JsonSerializable(typeof(Request))]
[JsonSerializable(typeof(CatalogDocument))]
[JsonSerializable(typeof(Success))]
[JsonSerializable(typeof(Failure))]
internal sealed partial class WireJson : JsonSerializerContext;
