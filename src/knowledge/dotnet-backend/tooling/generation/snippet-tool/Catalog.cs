using System.Text.RegularExpressions;

namespace SnippetTool;

internal sealed class Catalog
{
    private static readonly Regex IdPattern = new(@"\A[a-z][a-z0-9]*(?:-[a-z0-9]+)*\z", RegexOptions.NonBacktracking);
    private static readonly Regex VersionPattern = new(
        @"\A(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*)?\z",
        RegexOptions.NonBacktracking);
    private readonly string directory;
    private readonly SnippetDefinition[] snippets;

    private Catalog(string directory, SourceIdentity identity, SnippetDefinition[] snippets)
    {
        this.directory = directory;
        Identity = identity;
        this.snippets = snippets;
    }

    internal SourceIdentity Identity { get; }

    internal static Catalog Load(string path)
    {
        var document = Program.ReadJson(path, WireJson.Default.CatalogDocument, "catalog");
        if (document.SchemaVersion != Program.SchemaVersion)
            throw new SnippetError("unsupported-catalog-schema", "Catalog schemaVersion must be 1.");

        if (document.Source is not { } source || !IsId(source.Id) ||
            source.Version is null || !VersionPattern.IsMatch(source.Version) || document.Snippets is null)
            throw new SnippetError("invalid-catalog", "Catalog must have a source ID, source version, and snippets array.");

        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var snippet in document.Snippets)
        {
            if (snippet is null || !IsId(snippet.Id) ||
                string.IsNullOrWhiteSpace(snippet.Title) || string.IsNullOrWhiteSpace(snippet.Description) ||
                string.IsNullOrWhiteSpace(snippet.Context) || !IsBodyFile(snippet.BodyFile) ||
                !IsTextArray(snippet.Tags) || !IsTextArray(snippet.RequiredUsings) ||
                !IsTextArray(snippet.Preconditions) || snippet.Parameters is null)
                throw new SnippetError("invalid-catalog", "Snippet metadata or body filename is invalid.");

            if (!ids.Add(snippet.Id))
                throw new SnippetError("duplicate-snippet-id", $"Snippet ID '{snippet.Id}' is declared more than once.");

            foreach (var (name, definition) in snippet.Parameters)
                Expansion.ValidateDefinition(name, definition);
        }
        return new Catalog(Path.GetDirectoryName(path)!, source, document.Snippets);
    }

    internal SnippetSummary[] List(string? query) =>
        snippets.Where(snippet => query is null || Matches(snippet, query))
            .OrderBy(snippet => snippet.Id, StringComparer.Ordinal)
            .Select(snippet => snippet.Summary())
            .ToArray();

    internal SnippetDefinition Find(string id) =>
        Array.Find(snippets, snippet => snippet.Id == id) ??
        throw new SnippetError("snippet-not-found", $"No snippet has ID '{id}' in the selected catalog.");

    internal string ReadBody(SnippetDefinition snippet)
    {
        var path = Path.Combine(directory, snippet.BodyFile);
        try
        {
            if ((File.GetAttributes(path) & (FileAttributes.ReparsePoint | FileAttributes.Directory)) != 0)
                throw new SnippetError("invalid-body", "The selected body must be a nonsymlink file beside its catalog.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            throw new SnippetError("unreadable-body", "Could not read the selected body.");
        }
        return Program.ReadUtf8(path, "body");
    }

    internal static bool IsId(string? value) => value is not null && IdPattern.IsMatch(value);

    private static bool IsBodyFile(string? value) =>
        value is not null && value.EndsWith(".snippet", StringComparison.Ordinal) &&
        IsId(value[..^".snippet".Length]);

    private static bool IsTextArray(string[]? values) =>
        values is not null && values.All(value => !string.IsNullOrWhiteSpace(value));

    private static bool Matches(SnippetDefinition snippet, string query)
    {
        bool Has(string text) => text.Contains(query, StringComparison.OrdinalIgnoreCase);
        return Has(snippet.Id) || Has(snippet.Title) || Has(snippet.Description) ||
            Has(snippet.Context) || snippet.Tags.Any(Has);
    }
}
