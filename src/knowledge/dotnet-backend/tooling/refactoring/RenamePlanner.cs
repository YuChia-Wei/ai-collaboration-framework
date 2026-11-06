using System.Text;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CodeActions;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.FindSymbols;
using Microsoft.CodeAnalysis.Rename;
using Microsoft.CodeAnalysis.Text;

namespace RefactorTool;

internal static class RenamePlanner
{
    public static async Task<Plan> Preview(Request request)
    {
        Data.Require(SyntaxFacts.IsValidIdentifier(request.NewName) && !request.NewName.StartsWith('@') &&
            SyntaxFacts.GetKeywordKind(request.NewName) == SyntaxKind.None && SyntaxFacts.GetContextualKeywordKind(request.NewName) == SyntaxKind.None,
            "invalid_name", "New name must be an unescaped C# identifier (reserved/contextual keywords are unsupported).");
        request = request with { Workspace = Path.GetFullPath(request.Workspace), File = request.File is null ? null : Path.GetFullPath(request.File), Project = request.Project is null ? null : Path.GetFullPath(request.Project) };
        using var loaded = await WorkspaceLoader.Load(request);
        var before = loaded.Workspace.CurrentSolution;
        var symbol = await Select(before, request);
        Data.Require(IsSupported(symbol), "unsupported_symbol", "Select a source class/interface, ordinary method, property, field, parameter or local.");
        Data.Require(symbol.Name != request.NewName, "unchanged_name", "New name is identical to the current name.");
        var targets = new List<ISymbol> { symbol };
        if (request.RenameOverloads && symbol is IMethodSymbol method)
            targets.AddRange(method.ContainingType.GetMembers(method.Name).OfType<IMethodSymbol>().Where(m => m.MethodKind == MethodKind.Ordinary));
        var references = new List<ReferencedSymbol>();
        foreach (var target in targets.Distinct(SymbolEqualityComparer.Default))
            references.AddRange(await SymbolFinder.FindReferencesAsync(target, before));
        var definitions = references.Select(r => r.Definition).Append(symbol).Distinct(SymbolEqualityComparer.Default).ToList();
        definitions.AddRange(targets);
        foreach (var definition in definitions.Distinct(SymbolEqualityComparer.Default))
        {
            RequireEditable(definition, loaded);
            CheckExternalContract(definition, loaded);
            if (definition.ContainingType is not null && definition is not IParameterSymbol and not ILocalSymbol)
                for (var type = definition.ContainingType; type is not null; type = type.BaseType)
                    Data.Require(!type.GetMembers(request.NewName).Any(), "name_collision", $"Name already exists in {type}: {request.NewName}");
        }
        foreach (var reference in references.SelectMany(r => r.Locations))
            Data.Require(reference.Document.FilePath is not null && before.GetDocument(reference.Document.Id) is not null && !loaded.IsUneditable(reference.Document.FilePath),
                "uneditable_reference", "A related reference is generated or has no editable source file.");
        var baseline = await Errors(before);
        Data.Require(!baseline.Any(d => d.Id is "CS0006" or "CS0012" or "CS0518" or "CS1705"), "missing_metadata", "Compilation requires missing or incompatible metadata.", baseline);
        var (annotated, nameOfTargets) = await TrackNameof(before, definitions, request.RenameOverloads, loaded);
        var selected = await Select(annotated, request);
        var after = await Renamer.RenameSymbolAsync(annotated, selected,
            new SymbolRenameOptions(RenameOverloads: request.RenameOverloads, RenameInStrings: false, RenameInComments: false, RenameFile: false), request.NewName);
        after = await CompleteNameof(after, nameOfTargets, request.NewName);
        var changes = after.GetChanges(before);
        Data.Require(!changes.GetAddedProjects().Any() && !changes.GetRemovedProjects().Any(), "unsupported_change", "Rename must preserve the project graph.");
        var edits = new List<FileEdit>();
        var changedTexts = new Dictionary<string, IReadOnlyList<TextChange>>(Paths.Comparer);
        var patch = new StringBuilder();
        foreach (var projectChange in changes.GetProjectChanges())
        {
            Data.Require(!projectChange.GetAddedDocuments().Any() && !projectChange.GetRemovedDocuments().Any(), "unsupported_change", "Rename only supports modifications; new/deleted/moved documents are rejected before writes.");
            foreach (var id in projectChange.GetChangedDocuments())
            {
                var original = before.GetDocument(id)!;
                var updated = after.GetDocument(id)!;
                Data.Require(original.FilePath == updated.FilePath && original.FilePath is not null && !loaded.IsUneditable(original.FilePath), "uneditable_source", "Rename requires editable source and never moves files.");
                var root = await updated.GetSyntaxRootAsync();
                Data.Require(!root!.GetAnnotatedNodesAndTokens(ConflictAnnotation.Kind).Any(), "rename_conflict", $"Roslyn reported a rename conflict: {original.FilePath}");
                var oldText = await original.GetTextAsync();
                var newText = await updated.GetTextAsync();
                var textChanges = (await updated.GetTextChangesAsync(original)).ToArray();
                changedTexts[original.FilePath!] = textChanges;
                var oldBytes = File.ReadAllBytes(original.FilePath!);
                var encoding = oldText.Encoding ?? new UTF8Encoding(false, true);
                var preamble = encoding.GetPreamble();
                var hasPreamble = preamble.Length > 0 && oldBytes.AsSpan().StartsWith(preamble);
                var originalPayload = encoding.GetBytes(oldText.ToString());
                var originalRoundTrip = hasPreamble ? preamble.Concat(originalPayload).ToArray() : originalPayload;
                Data.Require(oldBytes.SequenceEqual(originalRoundTrip), "lossy_encoding", $"Original source cannot round-trip without changing unrelated bytes: {original.FilePath}");
                var payload = encoding.GetBytes(newText.ToString());
                Data.Require(encoding.GetString(payload) == newText.ToString(), "lossy_encoding", $"New source cannot be represented by its original encoding: {original.FilePath}");
                var newBytes = hasPreamble ? preamble.Concat(payload).ToArray() : payload;
                if (oldBytes.SequenceEqual(newBytes)) continue;
                edits.Add(new(original.FilePath!, "modify", Convert.ToBase64String(oldBytes), Convert.ToBase64String(newBytes)));
                // A complete replacement hunk is intentionally simple and lossless in
                // the plan; the patch is the human-readable review projection.
                patch.Append(Patch(Path.GetRelativePath(Path.GetDirectoryName(request.Workspace)!, original.FilePath!), oldText.ToString(), newText.ToString()));
            }
        }
        var currentErrors = await Errors(after);
        var remaining = baseline.ToList();
        var added = new List<DiagnosticInfo>();
        foreach (var diagnostic in currentErrors)
        {
            var mapped = diagnostic;
            if (diagnostic.File is not null && changedTexts.TryGetValue(diagnostic.File, out var textChanges))
                mapped = diagnostic with { Start = MapBack(diagnostic.Start, textChanges) };
            var match = remaining.FindIndex(d => d.Project == mapped.Project && d.Id == mapped.Id && d.Message == mapped.Message && d.File == mapped.File && d.Start == mapped.Start && d.Length == mapped.Length);
            if (match >= 0) remaining.RemoveAt(match); else added.Add(diagnostic);
        }
        Data.Require(added.Count == 0, "new_compilation_errors", "Rename introduces compilation errors; original errors are reported separately.", new { baseline, added });
        Data.Require(edits.Count > 0, "no_changes", "No editable changes were produced.");
        loaded.VerifyInputs();
        return new Plan
        {
            Request = request, Sdk = loaded.Sdk, Roslyn = typeof(Compilation).Assembly.GetName().Version!.ToString(),
            Symbol = Display(symbol), RelatedSymbols = definitions.Select(Display).Distinct().Order(StringComparer.Ordinal).ToArray(),
            Projects = loaded.Projects.ToArray(), Inputs = loaded.Inputs.Select(p => new InputFile(p.Key, p.Value)).ToArray(),
            Edits = edits.OrderBy(e => e.Path, StringComparer.Ordinal).ToArray(), BaselineErrors = baseline.ToArray(), NewErrors = [],
            Patch = patch.ToString(), Limits = loaded.Limits.Concat(new[] {
                "Only the selected configuration and its active conditional code are analyzed; other configurations require separate review.",
                "Only loaded C# source references are covered. External binaries/repos, reflection strings, serialization/database contracts, Razor/XAML and other languages are not updated.",
                "Public API rename may break external consumers. Compilation diagnostics are not proof of behavioral equivalence.",
                "Apply locks captured existing inputs against ordinary writes/deletion. Directory membership is not locked; files created after workspace enumeration are outside that guarantee.",
                "Comments, ordinary string literals, filenames, folders, project and assembly names remain unchanged; resolvable cref and nameof are semantic references.",
                request.RenameOverloads ? "All ordinary overloads and Roslyn-related source interface/override members are renamed." : "Only the selected overload and Roslyn-related source interface/override members are renamed."
            }).Distinct().ToArray()
        };
    }

    private static int MapBack(int position, IReadOnlyList<TextChange> changes)
    {
        var delta = 0;
        foreach (var change in changes.OrderBy(c => c.Span.Start))
        {
            var start = change.Span.Start + delta;
            var length = change.NewText?.Length ?? 0;
            if (position < start) break;
            if (position < start + length) return change.Span.Start;
            delta += length - change.Span.Length;
        }
        return position - delta;
    }

    private static async Task<(Solution Solution, Dictionary<DocumentId, List<SyntaxAnnotation>> Targets)> TrackNameof(Solution solution, List<ISymbol> definitions, bool overloads, LoadedWorkspace loaded)
    {
        var identities = definitions.Select(s => (s.ContainingAssembly?.Identity.ToString(), s.OriginalDefinition.GetDocumentationCommentId())).ToHashSet();
        var updated = solution;
        var targets = new Dictionary<DocumentId, List<SyntaxAnnotation>>();
        foreach (var document in solution.Projects.SelectMany(p => p.Documents))
        {
            var root = await document.GetSyntaxRootAsync();
            var model = await document.GetSemanticModelAsync();
            var tokens = new Dictionary<SyntaxToken, SyntaxAnnotation>();
            foreach (var invocation in root!.DescendantNodes().OfType<InvocationExpressionSyntax>().Where(n => n.Expression is IdentifierNameSyntax { Identifier.ValueText: "nameof" } && n.ArgumentList.Arguments.Count == 1))
            {
                var expression = invocation.ArgumentList.Arguments[0].Expression;
                // A real nameof has a constant value. A user-defined method with
                // this spelling must never be treated as the language operator.
                if (!model!.GetConstantValue(invocation).HasValue) continue;
                var group = model.GetMemberGroup(expression);
                var bound = model.GetSymbolInfo(expression).Symbol;
                var members = group.Length > 0 ? group.ToArray() : bound is null ? [] : new[] { bound };
                bool Included(ISymbol member) => member.OriginalDefinition.GetDocumentationCommentId() is { } id
                    ? identities.Contains((member.ContainingAssembly?.Identity.ToString(), id))
                    : definitions.Any(d => SymbolEqualityComparer.Default.Equals(d, member));
                if (!members.Any(Included)) continue;
                Data.Require((overloads || members.Length == 1) && members.All(Included), "ambiguous_nameof", $"nameof refers to an overload group in {document.FilePath}; review renameOverloads=true to rename that group.");
                var token = NameToken(expression);
                Data.Require(token.RawKind != 0, "unsupported_nameof", $"Unsupported nameof expression: {expression}");
                tokens[token] = new SyntaxAnnotation("RefactorTool.Nameof", Guid.NewGuid().ToString("N"));
            }
            if (tokens.Count == 0) continue;
            Data.Require(document.FilePath is not null && !loaded.IsUneditable(document.FilePath), "uneditable_reference", "A related nameof reference is generated.");
            updated = updated.WithDocumentSyntaxRoot(document.Id, root.ReplaceTokens(tokens.Keys, (original, rewritten) => rewritten.WithAdditionalAnnotations(tokens[original])));
            targets[document.Id] = tokens.Values.ToList();
        }
        return (updated, targets);
    }

    private static SyntaxToken NameToken(SyntaxNode expression) => expression switch
    {
        SimpleNameSyntax name => name.Identifier,
        MemberAccessExpressionSyntax access => access.Name.Identifier,
        AliasQualifiedNameSyntax alias => alias.Name.Identifier,
        QualifiedNameSyntax qualified => qualified.Right.Identifier,
        _ => default
    };

    private static async Task<Solution> CompleteNameof(Solution solution, Dictionary<DocumentId, List<SyntaxAnnotation>> targets, string newName)
    {
        foreach (var (documentId, annotations) in targets)
        {
            var document = solution.GetDocument(documentId)!;
            var root = (await document.GetSyntaxRootAsync())!;
            var tokens = new List<SyntaxToken>();
            foreach (var annotation in annotations)
            {
                var matches = root.GetAnnotatedTokens(annotation).ToArray();
                Data.Require(matches.Length == 1, "lost_nameof_target", "Roslyn did not preserve the identified nameof token; no plan is produced.");
                tokens.Add(matches[0]);
            }
            solution = solution.WithDocumentSyntaxRoot(documentId, root.ReplaceTokens(tokens, (original, rewritten) =>
                SyntaxFactory.Identifier(rewritten.LeadingTrivia, newName, rewritten.TrailingTrivia)));
        }
        return solution;
    }

    private static async Task<ISymbol> Select(Solution solution, Request request)
    {
        Data.Require((request.Symbol is not null) != (request.File is not null), "invalid_selector", "Select either file/line/column or project/documentation symbol ID.");
        if (request.Symbol is not null)
        {
            Data.Require(request.Project is not null && request.Line is null && request.Column is null, "invalid_selector", "A documentation symbol ID requires an explicit project and no position.");
            var projects = solution.Projects.Where(p => Paths.Comparer.Equals(p.FilePath, request.Project)).ToArray();
            Data.Require(projects.Length == 1, "ambiguous_project", "Project must identify exactly one loaded project.");
            var compilation = await projects[0].GetCompilationAsync();
            var symbols = DocumentationCommentId.GetSymbolsForDeclarationId(request.Symbol, compilation!).Distinct(SymbolEqualityComparer.Default).ToArray();
            Data.Require(symbols.Length == 1, "ambiguous_symbol", "Symbol ID must resolve to exactly one declaration.");
            return symbols[0];
        }
        Data.Require(request.Line > 0 && request.Column > 0 && request.Project is null, "invalid_selector", "File selection requires 1-based line and UTF-16 column, without project.");
        var documents = solution.Projects.SelectMany(p => p.Documents).Where(d => Paths.Comparer.Equals(d.FilePath, request.File)).ToArray();
        Data.Require(documents.Length == 1, "ambiguous_document", "File must identify exactly one loaded document.");
        var document = documents[0];
        var text = await document.GetTextAsync();
        Data.Require(request.Line <= text.Lines.Count, "invalid_position", "Line is outside the document.");
        var line = text.Lines[request.Line!.Value - 1];
        Data.Require(request.Column <= line.Span.Length, "invalid_position", "Column must be inside an identifier.");
        var position = line.Start + request.Column!.Value - 1;
        var root = await document.GetSyntaxRootAsync();
        var token = root!.FindToken(position, findInsideTrivia: true);
        Data.Require(token.IsKind(SyntaxKind.IdentifierToken) && token.Span.Contains(position), "invalid_position", "Position must be within the selected identifier.");
        var model = (await document.GetSemanticModelAsync())!;
        if (token.Parent is ExpressionSyntax or CrefSyntax)
            Data.Require(model.GetSymbolInfo(token.Parent).CandidateSymbols.Length <= 1, "ambiguous_symbol", "Position has multiple symbol candidates; choose an exact declaration.");
        var nameOf = token.Parent?.AncestorsAndSelf().OfType<InvocationExpressionSyntax>().FirstOrDefault(n =>
            n.Expression is IdentifierNameSyntax { Identifier.ValueText: "nameof" } && n.ArgumentList.Arguments.Count == 1 && model.GetConstantValue(n).HasValue);
        if (nameOf is not null)
        {
            var expression = nameOf.ArgumentList.Arguments[0].Expression;
            var nameToken = NameToken(expression);
            if (token == nameToken)
                Data.Require(model.GetMemberGroup(expression).Length <= 1, "ambiguous_symbol", "Position identifies an overload group; choose a declaration or exact signature ID.");
        }
        var symbol = await SymbolFinder.FindSymbolAtPositionAsync(document, position);
        Data.Require(symbol is not null, "unresolved_symbol", "Position is unresolved or ambiguous; choose a declaration or exact symbol ID.");
        return symbol!;
    }

    private static bool IsSupported(ISymbol symbol) => symbol switch
    {
        INamedTypeSymbol type => type.TypeKind is TypeKind.Class or TypeKind.Interface,
        IMethodSymbol method => method.MethodKind == MethodKind.Ordinary,
        IPropertySymbol or IFieldSymbol or IParameterSymbol or ILocalSymbol => true,
        _ => false
    };
    private static string Display(ISymbol symbol) => symbol.GetDocumentationCommentId() ?? symbol.ToDisplayString(SymbolDisplayFormat.CSharpErrorMessageFormat);
    internal static bool Generated(string path) => path.Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar).Any(s => s is "obj" or "bin") ||
        path.EndsWith(".g.cs", StringComparison.OrdinalIgnoreCase) || path.EndsWith(".generated.cs", StringComparison.OrdinalIgnoreCase) ||
        File.ReadLines(path).Take(5).Any(l => l.Contains("<auto-generated", StringComparison.OrdinalIgnoreCase));
    private static void RequireEditable(ISymbol symbol, LoadedWorkspace loaded)
    {
        Data.Require(symbol.Locations.Length > 0 && symbol.Locations.All(l => l.IsInSource && l.SourceTree is not null && !loaded.IsUneditable(l.SourceTree.FilePath)),
            "uneditable_symbol", $"Related symbol is not wholly editable source: {symbol}");
        foreach (var location in symbol.Locations)
            Data.Require((File.GetAttributes(location.SourceTree!.FilePath) & FileAttributes.ReadOnly) == 0, "read_only_source", $"Read-only declaration: {location.SourceTree.FilePath}");
    }
    private static void CheckExternalContract(ISymbol symbol, LoadedWorkspace loaded)
    {
        ISymbol? overridden = symbol switch { IMethodSymbol m => m.OverriddenMethod, IPropertySymbol p => p.OverriddenProperty, _ => null };
        if (overridden is not null) RequireEditable(overridden, loaded);
        if (symbol.ContainingType is null) return;
        foreach (var contract in symbol.ContainingType.AllInterfaces.SelectMany(i => i.GetMembers()))
            if (SymbolEqualityComparer.Default.Equals(symbol.ContainingType.FindImplementationForInterfaceMember(contract), symbol)) RequireEditable(contract, loaded);
    }
    private static async Task<List<DiagnosticInfo>> Errors(Solution solution)
    {
        var result = new List<DiagnosticInfo>();
        foreach (var project in solution.Projects)
        {
            var compilation = await project.GetCompilationAsync();
            Data.Require(compilation is not null, "missing_compilation", $"No compilation for {project.FilePath}");
            result.AddRange(compilation!.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).Select(d =>
                new DiagnosticInfo(project.FilePath!, d.Id, d.GetMessage(System.Globalization.CultureInfo.InvariantCulture), d.Location.SourceTree?.FilePath, d.Location.SourceSpan.Start, d.Location.SourceSpan.Length)));
        }
        return result.OrderBy(d => d.Project).ThenBy(d => d.File).ThenBy(d => d.Start).ThenBy(d => d.Id).ToList();
    }
    private static string Patch(string path, string before, string after)
    {
        static string[] Lines(string text) => text.Length == 0 ? [] : text.EndsWith('\n') ? text[..^1].Split('\n') : text.Split('\n');
        var oldLines = Lines(before); var newLines = Lines(after);
        var result = new StringBuilder($"--- a/{path.Replace('\\', '/')}\n+++ b/{path.Replace('\\', '/')}\n@@ -{(oldLines.Length == 0 ? 0 : 1)},{oldLines.Length} +{(newLines.Length == 0 ? 0 : 1)},{newLines.Length} @@\n");
        foreach (var line in oldLines) result.Append('-').Append(line).Append('\n');
        if (before.Length > 0 && !before.EndsWith('\n')) result.Append("\\ No newline at end of file\n");
        foreach (var line in newLines) result.Append('+').Append(line).Append('\n');
        if (after.Length > 0 && !after.EndsWith('\n')) result.Append("\\ No newline at end of file\n");
        return result.ToString();
    }
}
