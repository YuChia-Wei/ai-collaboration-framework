using System.Text;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CodeActions;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.FindSymbols;
using Microsoft.CodeAnalysis.Operations;
using Microsoft.CodeAnalysis.Rename;
using Microsoft.CodeAnalysis.Text;

namespace RefactorTool;

internal static class RenamePlanner
{
    public static async Task<Plan> Preview(Request request)
    {
        request = Normalize(request);
        using var loaded = await WorkspaceLoader.Load(request);
        return await PlanRename(request, loaded);
    }

    internal static Request Normalize(Request request)
    {
        Data.Require(SyntaxFacts.IsValidIdentifier(request.NewName) && !request.NewName.StartsWith('@') &&
            SyntaxFacts.GetKeywordKind(request.NewName) == SyntaxKind.None,
            "invalid_name", "New name must be an unescaped C# identifier other than a reserved keyword.");
        return request with { Workspace = Path.GetFullPath(request.Workspace), File = request.File is null ? null : Path.GetFullPath(request.File), Project = request.Project is null ? null : Path.GetFullPath(request.Project) };
    }

    internal static async Task<Plan> PlanRename(Request request, LoadedWorkspace loaded)
    {
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
            RequireEditableDocument(reference.Document, loaded, "uneditable_reference");
        var baseline = await Errors(before);
        Data.Require(!baseline.Any(d => d.Id is "CS0006" or "CS0012" or "CS0518" or "CS1705"), "missing_metadata", "Compilation requires missing or incompatible metadata.", baseline);
        var (annotated, nameOfTargets) = await TrackNameof(before, definitions, request.RenameOverloads, loaded);
        var invocationTargets = new Dictionary<DocumentId, InvocationBinding[]>();
        if (symbol is IMethodSymbol)
            (annotated, invocationTargets) = await TrackInvocations(annotated, references.SelectMany(r => r.Locations));
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
                Data.Require(original.FilePath == updated.FilePath, "unsupported_change", "Rename never moves files.");
                RequireEditableDocument(original, loaded, "uneditable_source");
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
                patch.Append(Patch(Path.GetRelativePath(Path.GetDirectoryName(request.Workspace)!, original.FilePath!), oldText, newText, textChanges));
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
        await RequirePreservedInvocations(after, invocationTargets, request.NewName);
        Data.Require(edits.Count > 0, "no_changes", "No editable changes were produced.");
        loaded.VerifyInputs();
        return new Plan
        {
            Request = request, Sdk = loaded.Sdk, Roslyn = typeof(Compilation).Assembly.GetName().Version!.ToString(),
            Symbol = Display(symbol), RelatedSymbols = definitions.Select(Display).Distinct().Order(StringComparer.Ordinal).ToArray(),
            Projects = loaded.Projects.ToArray(), Inputs = loaded.Inputs.Values.ToArray(),
            Edits = edits.OrderBy(e => e.Path, StringComparer.Ordinal).ToArray(), BaselineErrors = baseline.ToArray(), NewErrors = [],
            Patch = patch.ToString(), Limits = loaded.Limits.Concat(new[] {
                "Only the selected configuration and its active conditional code are analyzed; other configurations require separate review.",
                "Only loaded C# source references are covered. External binaries/repos, reflection strings, serialization/database contracts, Razor/XAML and other languages are not updated.",
                "Public API rename may break external consumers. Compilation diagnostics are not proof of behavioral equivalence.",
                "Windows file sharing protects captured existing inputs from ordinary writes/deletion during apply. Directory membership is not locked; new directory entries and path aliases are outside that guarantee.",
                "Comments, ordinary string literals, filenames, folders, project and assembly names remain unchanged; resolvable cref and nameof are semantic references.",
                request.RenameOverloads ? "Ordinary overloads declared by the selected method's containing type and their Roslyn-related source interface/override members are renamed; other overloads on related or base types are not automatically included." : "Only the selected overload and Roslyn-related source interface/override members are renamed."
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
        foreach (var document in solution.Projects.SelectMany(p => p.Documents).Concat(loaded.GeneratedDocuments))
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
                Data.Require((overloads || members.Length == 1) && members.All(Included), "ambiguous_nameof", overloads
                    ? $"nameof includes methods outside the selected rename scope in {document.FilePath}; overload expansion is limited to the selected method's containing type and its Roslyn-related members."
                    : $"nameof refers to an overload group in {document.FilePath}; review renameOverloads=true to rename that group.");
                var token = NameToken(expression);
                Data.Require(token.RawKind != 0, "unsupported_nameof", $"Unsupported nameof expression: {expression}");
                tokens[token] = new SyntaxAnnotation("RefactorTool.Nameof", Guid.NewGuid().ToString("N"));
            }
            if (tokens.Count == 0) continue;
            RequireEditableDocument(document, loaded, "uneditable_reference");
            updated = updated.WithDocumentSyntaxRoot(document.Id, root.ReplaceTokens(tokens.Keys, (original, rewritten) => rewritten.WithAdditionalAnnotations(tokens[original])));
            targets[document.Id] = tokens.Values.ToList();
        }
        return (updated, targets);
    }

    private sealed record InvocationBinding(SyntaxAnnotation Annotation, IMethodSymbol Method, int Line);

    private static async Task<(Solution Solution, Dictionary<DocumentId, InvocationBinding[]> Targets)> TrackInvocations(
        Solution solution, IEnumerable<ReferenceLocation> references)
    {
        var targets = new Dictionary<DocumentId, InvocationBinding[]>();
        foreach (var locations in references.Where(r => !r.IsImplicit).GroupBy(r => r.Document.Id))
        {
            var document = solution.GetDocument(locations.Key)!;
            var root = (await document.GetSyntaxRootAsync())!;
            var model = (await document.GetSemanticModelAsync())!;
            var bindings = new Dictionary<InvocationExpressionSyntax, InvocationBinding>();
            foreach (var reference in locations)
            {
                var token = root.FindToken(reference.Location.SourceSpan.Start);
                var call = token.Parent?.FirstAncestorOrSelf<InvocationExpressionSyntax>();
                if (call is null || token.Span != reference.Location.SourceSpan || NameToken(call.Expression) != token ||
                    model.GetOperation(call) is not IInvocationOperation invocation)
                    continue;

                var line = token.GetLocation().GetLineSpan().StartLinePosition.Line + 1;
                bindings.TryAdd(call, new(new SyntaxAnnotation(), invocation.TargetMethod, line));
            }

            if (bindings.Count == 0) continue;
            var annotated = root.ReplaceNodes(bindings.Keys, (original, rewritten) =>
                rewritten.WithAdditionalAnnotations(bindings[original].Annotation));
            solution = solution.WithDocumentSyntaxRoot(document.Id, annotated);
            targets[document.Id] = bindings.Values.ToArray();
        }

        return (solution, targets);
    }

    private static async Task RequirePreservedInvocations(Solution solution, Dictionary<DocumentId, InvocationBinding[]> targets, string newName)
    {
        foreach (var (id, bindings) in targets)
        {
            var document = solution.GetDocument(id)!;
            var root = (await document.GetSyntaxRootAsync())!;
            var model = (await document.GetSemanticModelAsync())!;
            foreach (var binding in bindings)
            {
                var calls = root.GetAnnotatedNodes(binding.Annotation).Take(2).ToArray();
                Data.Require(calls.Length == 1 && calls[0] is InvocationExpressionSyntax,
                    "rename_conflict", $"Rename could not track the invocation at {document.FilePath}:{binding.Line}.");
                var actual = (model.GetOperation(calls[0]) as IInvocationOperation)?.TargetMethod;
                Data.Require(actual is not null && actual.Name == newName && MethodIdentity(actual).Equals(MethodIdentity(binding.Method)),
                    "rename_binding_changed", $"Rename would change the method called at {document.FilePath}:{binding.Line}.",
                    new { before = Display(binding.Method), after = actual is null ? null : Display(actual) });
            }
        }
    }

    private static (AssemblyIdentity Assembly, string Signature) MethodIdentity(IMethodSymbol method)
    {
        var definition = (method.ReducedFrom ?? method).OriginalDefinition;
        // The name changes intentionally. The assembly, declaring type and signature must still agree.
        var signature = string.Concat(definition.ToDisplayParts(SymbolDisplayFormat.CSharpErrorMessageFormat)
            .Where(part => part.Kind != SymbolDisplayPartKind.MethodName));
        return (definition.ContainingAssembly.Identity, signature);
    }

    private static SyntaxToken NameToken(SyntaxNode expression) => expression switch
    {
        SimpleNameSyntax name => name.Identifier,
        MemberAccessExpressionSyntax access => access.Name.Identifier,
        MemberBindingExpressionSyntax binding => binding.Name.Identifier,
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
            var spelling = SyntaxFacts.GetContextualKeywordKind(newName) == SyntaxKind.None ? newName : "@" + newName;
            solution = solution.WithDocumentSyntaxRoot(documentId, root.ReplaceTokens(tokens, (original, rewritten) =>
                SyntaxFactory.Identifier(rewritten.LeadingTrivia, SyntaxKind.IdentifierToken, spelling, newName, rewritten.TrailingTrivia)));
        }
        return solution;
    }

    internal static async Task<ISymbol> Select(Solution solution, Request request)
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
    internal static void RequireEditable(ISymbol symbol, LoadedWorkspace loaded)
    {
        Data.Require(symbol.Locations.Length > 0, "uneditable_symbol", $"Related symbol has no source declaration: {symbol}");
        foreach (var location in symbol.Locations)
        {
            Data.Require(location.IsInSource && location.SourceTree is not null,
                "uneditable_symbol", $"Related declaration is outside loaded source: {symbol}");
            var path = location.SourceTree!.FilePath;
            RequireEditablePath(path, loaded, "uneditable_symbol");
            Data.Require((File.GetAttributes(path) & FileAttributes.ReadOnly) == 0, "read_only_source", $"Read-only declaration: {path}");
        }
    }

    private static void RequireEditableDocument(Document document, LoadedWorkspace loaded, string code)
    {
        if (document is SourceGeneratedDocument)
            throw new RefactorFailure(code, $"Required edit is in source-generator output: {document.FilePath}");
        RequireEditablePath(document.FilePath, loaded, code);
    }

    private static void RequireEditablePath(string? path, LoadedWorkspace loaded, string code)
    {
        if (path is not null && loaded.UneditableSources.TryGetValue(path, out var reason))
            throw new RefactorFailure(code, $"Required edit is uneditable ({reason}): {path}");
        Data.Require(path is not null && loaded.EditableSources.Contains(path),
            code, $"Required edit has no editable source file: {path}");
    }
    private static void CheckExternalContract(ISymbol symbol, LoadedWorkspace loaded)
    {
        if (symbol is IMethodSymbol { PartialImplementationPart: { } implementation }) RequireEditable(implementation, loaded);
        ISymbol? overridden = symbol switch { IMethodSymbol m => m.OverriddenMethod, IPropertySymbol p => p.OverriddenProperty, _ => null };
        if (overridden is not null) RequireEditable(overridden, loaded);
        if (symbol.ContainingType is null) return;
        foreach (var contract in symbol.ContainingType.AllInterfaces.SelectMany(i => i.GetMembers()))
            if (SymbolEqualityComparer.Default.Equals(symbol.ContainingType.FindImplementationForInterfaceMember(contract), symbol)) RequireEditable(contract, loaded);
    }
    internal static async Task<List<DiagnosticInfo>> Errors(Solution solution)
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
    internal static string Patch(string path, SourceText before, SourceText after, IReadOnlyList<TextChange> changes)
    {
        const int context = 3;
        var oldLines = new PatchLines(before.ToString());
        var newLines = new PatchLines(after.ToString());
        // Convert the character edits into line ranges on both sides. Including
        // a line touched at its start also handles insertion/deletion of a
        // newline without creating mismatched unchanged ranges.
        var blocks = new List<(int OldStart, int OldEnd, int NewStart, int NewEnd)>();
        var offset = 0;
        foreach (var change in changes.OrderBy(c => c.Span.Start))
        {
            var newStart = change.Span.Start + offset;
            var newLength = change.NewText?.Length ?? 0;
            var block = (OldStart: oldLines.IndexOf(change.Span.Start),
                OldEnd: Math.Min(oldLines.Count, oldLines.IndexOf(change.Span.End) + 1),
                NewStart: newLines.IndexOf(newStart),
                NewEnd: Math.Min(newLines.Count, newLines.IndexOf(newStart + newLength) + 1));
            offset += newLength - change.Span.Length;
            if (blocks.Count > 0 && (blocks[^1].OldEnd >= block.OldStart || blocks[^1].NewEnd >= block.NewStart))
            {
                var last = blocks[^1];
                blocks[^1] = (last.OldStart, block.OldEnd, last.NewStart, block.NewEnd);
            }
            else blocks.Add(block);
        }

        var result = new StringBuilder($"--- a/{path.Replace('\\', '/')}\n+++ b/{path.Replace('\\', '/')}\n");
        for (var first = 0; first < blocks.Count;)
        {
            var last = first;
            while (last + 1 < blocks.Count && blocks[last + 1].OldStart - blocks[last].OldEnd <= context * 2)
                last++;
            var start = blocks[first];
            var end = blocks[last];
            var leading = Math.Min(context, Math.Min(start.OldStart, start.NewStart));
            var trailing = Math.Min(context, Math.Min(oldLines.Count - end.OldEnd, newLines.Count - end.NewEnd));
            var oldStart = start.OldStart - leading;
            var newStart = start.NewStart - leading;
            var oldEnd = end.OldEnd + trailing;
            var newEnd = end.NewEnd + trailing;
            static string Range(int start, int end) => end == start ? $"{start},0" : $"{start + 1},{end - start}";
            result.Append($"@@ -{Range(oldStart, oldEnd)} +{Range(newStart, newEnd)} @@\n");
            for (var i = first; i <= last; i++)
            {
                var block = blocks[i];
                AppendLines(oldLines, oldStart, block.OldStart, ' ');
                AppendLines(oldLines, block.OldStart, block.OldEnd, '-');
                AppendLines(newLines, block.NewStart, block.NewEnd, '+');
                oldStart = block.OldEnd;
            }
            AppendLines(oldLines, oldStart, oldEnd, ' ');
            first = last + 1;
        }
        return result.ToString();

        void AppendLines(PatchLines lines, int start, int end, char prefix)
        {
            for (var i = start; i < end; i++)
            {
                var content = lines[i];
                result.Append(prefix).Append(content);
                if (content[^1] != '\n') result.Append("\n\\ No newline at end of file\n");
            }
        }
    }

    private sealed class PatchLines(string text)
    {
        private readonly int[] starts = LineStarts(text);
        public int Count => starts.Length - (starts[^1] == text.Length ? 1 : 0);

        public int IndexOf(int position)
        {
            var index = Array.BinarySearch(starts, position);
            return index >= 0 ? index : ~index - 1;
        }

        public ReadOnlySpan<char> this[int index] =>
            text.AsSpan(starts[index], (index + 1 < starts.Length ? starts[index + 1] : text.Length) - starts[index]);

        private static int[] LineStarts(string text)
        {
            // Unified diff splits on LF. CR and other C# line terminators
            // belong to the payload, including a CR at the end of the file.
            var offsets = new List<int> { 0 };
            for (var index = text.IndexOf('\n'); index >= 0; index = text.IndexOf('\n', index + 1))
                offsets.Add(index + 1);
            return offsets.ToArray();
        }
    }
}
