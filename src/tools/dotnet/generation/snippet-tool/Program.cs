using System.Reflection;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization.Metadata;

namespace SnippetTool;

internal static class Program
{
    internal const int SchemaVersion = 1;
    private static readonly UTF8Encoding Utf8 = new(encoderShouldEmitUTF8Identifier: false, throwOnInvalidBytes: true);

    private static int Main(string[] args)
    {
        Console.OutputEncoding = Utf8;
        return Run(args, Console.Out, Console.Error);
    }

    internal static int Run(string[] args, TextWriter output, TextWriter errorOutput)
    {
        try
        {
            switch (args)
            {
                case ["--help"]:
                    output.WriteLine("SnippetTool --request <request.json> | --version | --help");
                    return 0;
                case ["--version"]:
                    output.WriteLine(typeof(Program).Assembly
                        .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion);
                    return 0;
                case ["--request", var path] when !string.IsNullOrWhiteSpace(path):
                    var result = Execute(Path.GetFullPath(path));
                    Write(output, result, WireJson.Default.Success);
                    return 0;
                default:
                    throw new SnippetError("invalid-arguments", "Use --request <request.json>, --version, or --help.");
            }
        }
        catch (SnippetError error)
        {
            Write(errorOutput, new Failure(SchemaVersion, new Error(error.Code, error.Message)), WireJson.Default.Failure);
            return 1;
        }
        catch (ArgumentException)
        {
            Write(errorOutput, new Failure(SchemaVersion, new Error("invalid-path", "The selected path is invalid.")), WireJson.Default.Failure);
            return 1;
        }
    }

    private static Success Execute(string requestPath)
    {
        var request = ReadJson(requestPath, WireJson.Default.Request, "request");
        if (request.SchemaVersion != SchemaVersion)
            throw new SnippetError("unsupported-request-schema", "Request schemaVersion must be 1.");

        Validate(request);
        var sourcePath = request.Source is null
            ? Path.Combine(AppContext.BaseDirectory, "snippets", "catalog.json")
            : Path.GetFullPath(request.Source, Path.GetDirectoryName(requestPath)!);
        var catalog = Catalog.Load(sourcePath);

        if (request.Operation is "list" or "search")
            return new Success(SchemaVersion, request.Operation, catalog.Identity, Snippets: catalog.List(request.Query));

        var snippet = catalog.Find(request.Id!);
        var body = catalog.ReadBody(snippet);
        var parts = Expansion.Parse(body, snippet.Parameters);
        if (request.Operation == "inspect")
            return new Success(SchemaVersion, "inspect", catalog.Identity, Snippet: snippet, Body: body);

        var text = Expansion.Render(parts, snippet.Parameters, request.Parameters, request.Indent ?? 0, request.Newline ?? "lf");
        return new Success(SchemaVersion, "render", catalog.Identity, Snippet: snippet, Text: text);
    }

    private static void Validate(Request request)
    {
        var hasRenderOptions = request.Parameters is not null || request.Indent is not null || request.Newline is not null;
        var valid = request.Operation switch
        {
            "list" => request.Query is null && request.Id is null && !hasRenderOptions,
            "search" => !string.IsNullOrWhiteSpace(request.Query) && request.Id is null && !hasRenderOptions,
            "inspect" => Catalog.IsId(request.Id) && request.Query is null && !hasRenderOptions,
            "render" => Catalog.IsId(request.Id) && request.Query is null,
            _ => false
        };
        if (!valid || request.Source is not null && string.IsNullOrWhiteSpace(request.Source))
            throw new SnippetError("invalid-request", "Operation or fields are invalid for the selected operation.");
        if (request.Indent is < 0 or > 256 || request.Newline is not (null or "lf" or "crlf"))
            throw new SnippetError("invalid-request", "Indent must be 0–256 and newline must be lf or crlf.");
    }

    internal static T ReadJson<T>(string path, JsonTypeInfo<T> typeInfo, string kind) where T : class
    {
        try
        {
            return JsonSerializer.Deserialize(ReadUtf8(path, kind), typeInfo)
                ?? throw new JsonException();
        }
        catch (JsonException error)
        {
            throw new SnippetError($"invalid-{kind}", $"Invalid {kind} JSON at {error.Path ?? "$"}.");
        }
    }

    internal static string ReadUtf8(string path, string kind)
    {
        try
        {
            // Fail before opening zero-length special files such as Unix FIFOs.
            if (new FileInfo(path).Length == 0)
                throw new SnippetError($"invalid-{kind}", $"The selected {kind} must be a nonempty file.");
            var bytes = File.ReadAllBytes(path);
            var start = bytes.AsSpan().StartsWith("\uFEFF"u8) ? 3 : 0;
            return Utf8.GetString(bytes.AsSpan(start));
        }
        catch (DecoderFallbackException)
        {
            throw new SnippetError($"invalid-{kind}", $"The selected {kind} is not UTF-8.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            throw new SnippetError($"unreadable-{kind}", $"Could not read the selected {kind}.");
        }
    }

    private static void Write<T>(TextWriter writer, T result, JsonTypeInfo<T> typeInfo)
    {
        writer.Write(JsonSerializer.Serialize(result, typeInfo));
        writer.Write('\n');
    }
}
