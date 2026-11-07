using System.Text;
using System.Text.RegularExpressions;

namespace SnippetTool;

internal static class Expansion
{
    private static readonly Regex NamePattern = new(@"\A[A-Za-z_][A-Za-z0-9_]*\z", RegexOptions.NonBacktracking);
    private static readonly HashSet<string> Keywords = new(
        """
        abstract as base bool break byte case catch char checked class const continue decimal default delegate
        do double else enum event explicit extern false finally fixed float for foreach goto if implicit in
        int interface internal is lock long namespace new null object operator out override params private
        protected public readonly ref return sbyte sealed short sizeof stackalloc static string struct switch
        this throw true try typeof uint ulong unchecked unsafe ushort using virtual void volatile while
        __arglist __makeref __reftype __refvalue
        """.Split([' ', '\r', '\n'], StringSplitOptions.RemoveEmptyEntries), StringComparer.Ordinal);

    internal sealed record Part(string Text, bool IsParameter = false);

    internal static void ValidateDefinition(string name, ParameterDefinition? definition)
    {
        if (!NamePattern.IsMatch(name) || definition is null)
            throw new SnippetError("invalid-catalog", "Parameter name or declaration is invalid.");

        var kindValid = definition.Kind switch
        {
            "identifier" or "text" => definition.Values is null,
            "enum" => definition.Values is { Length: > 0 } choices &&
                choices.All(value => !string.IsNullOrWhiteSpace(value)) &&
                choices.Distinct(StringComparer.Ordinal).Count() == choices.Length,
            _ => false
        };
        if (!kindValid || definition.Default is not null && !IsValidValue(definition, definition.Default))
            throw new SnippetError("invalid-catalog", $"Parameter '{name}' has an invalid kind, values list, or default.");
    }

    internal static List<Part> Parse(string body, Dictionary<string, ParameterDefinition> definitions)
    {
        var parts = new List<Part>();
        var position = 0;
        while (body.IndexOf("${", position, StringComparison.Ordinal) is var opening && opening >= 0)
        {
            var escaped = opening > position && body[opening - 1] == '$';
            var literalEnd = escaped ? opening - 1 : opening;
            parts.Add(new Part(body[position..literalEnd]));
            if (escaped)
            {
                parts.Add(new Part("${"));
                position = opening + 2;
                continue;
            }

            var closing = body.IndexOf('}', opening + 2);
            if (closing < 0 || !NamePattern.IsMatch(body[(opening + 2)..closing]))
                throw new SnippetError("invalid-placeholder", "A body placeholder must use the form ${name}.");

            var name = body[(opening + 2)..closing];
            if (!definitions.ContainsKey(name))
                throw new SnippetError("unknown-placeholder", $"The body uses undeclared placeholder '{name}'.");

            parts.Add(new Part(name, IsParameter: true));
            position = closing + 1;
        }
        parts.Add(new Part(body[position..]));
        return parts;
    }

    internal static string Render(List<Part> parts, Dictionary<string, ParameterDefinition> definitions,
        Dictionary<string, string?>? supplied, int indent, string newline)
    {
        supplied ??= [];
        foreach (var name in supplied.Keys.Order(StringComparer.Ordinal))
        {
            if (!definitions.ContainsKey(name))
                throw new SnippetError("unknown-parameter", $"Parameter '{name}' is undeclared.");
        }

        var values = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var (name, definition) in definitions.OrderBy(pair => pair.Key, StringComparer.Ordinal))
        {
            var value = supplied.TryGetValue(name, out var provided) ? provided :
                definition.Default ?? throw new SnippetError("missing-parameter", $"Parameter '{name}' is required.");
            if (value is null || !IsValidValue(definition, value))
                throw new SnippetError("invalid-parameter", $"Parameter '{name}' must match its declared {definition.Kind} kind.");
            values.Add(name, value);
        }

        var text = new StringBuilder();
        foreach (var part in parts)
            text.Append(part.IsParameter ? values[part.Text] : part.Text);

        var lines = text.ToString().Replace("\r\n", "\n", StringComparison.Ordinal).Replace('\r', '\n').Split('\n');
        var prefix = new string(' ', indent);
        return string.Join(newline == "crlf" ? "\r\n" : "\n",
            lines.Select(line => line.Length == 0 ? line : prefix + line));
    }

    private static bool IsValidValue(ParameterDefinition definition, string value) =>
        definition.Kind switch
        {
            "identifier" => NamePattern.IsMatch(value) && !Keywords.Contains(value),
            "enum" => definition.Values!.Contains(value, StringComparer.Ordinal),
            "text" => true,
            _ => false
        };
}
