using System.Text;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Editing;
using Microsoft.CodeAnalysis.Text;

namespace RefactorTool;

internal static class InterfacePlanner
{
    public static async Task<Plan> Preview(Request request)
    {
        Data.Require(Identifier(request.NewName) && request.Namespace is not null &&
            (request.Namespace.Length == 0 || request.Namespace.Split('.').All(Identifier)),
            "invalid_name", "Interface name and namespace components must be unescaped C# identifiers other than reserved keywords.");
        Data.Require(request.Members.Distinct(StringComparer.Ordinal).Count() == request.Members.Length,
            "invalid_members", "Member declaration IDs must be unique.");
        request = request with { Workspace = Path.GetFullPath(request.Workspace),
            File = request.File is null ? null : Path.GetFullPath(request.File),
            Project = request.Project is null ? null : Path.GetFullPath(request.Project),
            OutputFile = Path.GetFullPath(request.OutputFile!), Members = request.Members.Order(StringComparer.Ordinal).ToArray() };
        using var loaded = await WorkspaceLoader.Load(request);
        var before = loaded.Workspace.CurrentSolution;
        var selected = await RenamePlanner.Select(before, request);
        Data.Require(selected is INamedTypeSymbol { TypeKind: TypeKind.Class, IsStatic: false, ContainingType: null } &&
            selected.DeclaringSyntaxReferences.Length == 1 && selected.DeclaredAccessibility is Accessibility.Public or Accessibility.Internal,
            "unsupported_class", "Select a single-declaration, public/internal, nonstatic top-level class.");
        var type = (INamedTypeSymbol)selected;
        var syntax = await type.DeclaringSyntaxReferences[0].GetSyntaxAsync() as ClassDeclarationSyntax;
        Data.Require(syntax is not null && !syntax.Modifiers.Any(SyntaxKind.PartialKeyword) &&
            type.BaseType?.SpecialType == SpecialType.System_Object && !type.IsFileLocal,
            "unsupported_class", "Records, partial/file-local classes and class inheritance are not included in this subset.");
        RenamePlanner.RequireEditable(type, loaded);
        var document = before.GetDocument(syntax!.SyntaxTree)!;
        var project = document.Project;
        var output = request.OutputFile!;
        var folder = Path.GetDirectoryName(project.FilePath!)!;
        var relativeOutput = Path.GetRelativePath(folder, output);
        Data.Require(Paths.IsWithin(output, folder) && Path.GetExtension(output).Equals(".cs", StringComparison.OrdinalIgnoreCase) &&
            !output.EndsWith(".g.cs", StringComparison.OrdinalIgnoreCase) && !output.EndsWith(".generated.cs", StringComparison.OrdinalIgnoreCase) &&
            relativeOutput.Split(Path.DirectorySeparatorChar).All(p => p.IndexOfAny(Path.GetInvalidFileNameChars()) < 0 && p.TrimEnd(' ', '.') == p &&
                !System.Text.RegularExpressions.Regex.IsMatch(p.Split('.')[0], @"^(CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])$", System.Text.RegularExpressions.RegexOptions.IgnoreCase)) &&
            !relativeOutput.Split(Path.DirectorySeparatorChar).Any(p => p.Equals("obj", StringComparison.OrdinalIgnoreCase) || p.Equals("bin", StringComparison.OrdinalIgnoreCase)) &&
            !loaded.Inputs.ContainsKey(output), "invalid_output", "Use a new authored .cs file inside the selected project, outside obj/bin/generated paths.");
        Paths.AbsentFile(output);
        await CompileInclusion.Require(loaded, project.FilePath!, output, request);
        var baseline = await RenamePlanner.Errors(before);
        Data.Require(baseline.Count == 0, "compilation_errors", "Extract Interface requires an error-free loaded workspace.", baseline);
        var compilation = (await project.GetCompilationAsync())!;
        var model = (await document.GetSemanticModelAsync())!;
        var nullable = model.GetNullableContext(syntax.SpanStart);
        var members = new List<ISymbol>();
        foreach (var id in request.Members)
        {
            var found = DocumentationCommentId.GetSymbolsForDeclarationId(id, compilation).ToArray();
            Data.Require(found.Length == 1 && SymbolEqualityComparer.Default.Equals(found[0].ContainingType, type),
                "invalid_members", $"Select exact members declared by the source class: {id}");
            var member = found[0];
            RequireMember(member);
            RenamePlanner.RequireEditable(member, loaded);
            var declaration = await member.DeclaringSyntaxReferences.Single().GetSyntaxAsync();
            Data.Require(model.GetNullableContext(declaration.SpanStart) == nullable,
                "unsupported_member", "Selected members must share the class declaration's nullable context.");
            members.Add(member);
        }
        Data.Require(type.TypeParameters.All(p => p.GetAttributes().Length == 0), "unsupported_class", "Attributed type parameters are unsupported.");
        var generator = SyntaxGenerator.GetGenerator(loaded.Workspace, LanguageNames.CSharp);
        var generatedClass = (ClassDeclarationSyntax)generator.Declaration(type);
        var declarations = members.Select(m => Declaration(generator, m)).ToArray();
        var contract = SyntaxFactory.InterfaceDeclaration(Escape(request.NewName))
            .WithModifiers(SyntaxFactory.TokenList(SyntaxFactory.Token(type.DeclaredAccessibility == Accessibility.Public ? SyntaxKind.PublicKeyword : SyntaxKind.InternalKeyword)))
            .WithTypeParameterList(generatedClass.TypeParameterList).WithConstraintClauses(generatedClass.ConstraintClauses)
            .WithMembers(SyntaxFactory.List(declarations));
        MemberDeclarationSyntax top = request.Namespace!.Length == 0 ? contract :
            SyntaxFactory.NamespaceDeclaration(SyntaxFactory.ParseName(string.Join('.', request.Namespace.Split('.').Select(Escape))))
                .WithMembers(SyntaxFactory.SingletonList<MemberDeclarationSyntax>(contract));
        var oldText = await document.GetTextAsync();
        var newline = oldText.ToString().Contains("\r\n", StringComparison.Ordinal) ? "\r\n" : "\n";
        var annotations = (nullable & NullableContext.AnnotationsEnabled) != 0 ? "enable" : "disable";
        var warnings = (nullable & NullableContext.WarningsEnabled) != 0 ? "enable" : "disable";
        var interfaceText = SourceText.From($"#nullable {annotations} annotations{newline}#nullable {warnings} warnings{newline}" +
            top.NormalizeWhitespace(eol: newline).ToFullString() + newline, new UTF8Encoding(false, true));
        var qualified = "global::" + (request.Namespace.Length == 0 ? "" : string.Join('.', request.Namespace.Split('.').Select(Escape)) + ".") + Escape(request.NewName) +
            (type.TypeParameters.Length == 0 ? "" : "<" + string.Join(", ", type.TypeParameters.Select(p => Escape(p.Name))) + ">");
        // Insert only the base-list text; method bodies, trivia and all consumers
        // remain byte-for-byte untouched outside this insertion.
        var position = syntax.BaseList?.Types.Last().Span.End ?? syntax.ParameterList?.Span.End ?? syntax.TypeParameterList?.Span.End ?? syntax.Identifier.Span.End;
        var insertion = new TextChange(new TextSpan(position, 0), (syntax.BaseList is null ? " : " : ", ") + qualified);
        var changedText = oldText.WithChanges(insertion);
        var addedId = DocumentId.CreateNewId(project.Id);
        var after = before.WithDocumentText(document.Id, changedText).AddDocument(addedId, Path.GetFileName(output), interfaceText, filePath: output);
        var errors = await RenamePlanner.Errors(after);
        Data.Require(errors.Count == 0, "new_compilation_errors", "Extract Interface introduces compilation errors or a visibility/name conflict.", errors);
        await RequireUnchangedBindings(before, after, document.Id, insertion,
            request.Namespace!.Split('.', StringSplitOptions.RemoveEmptyEntries).Append(request.NewName).ToHashSet(StringComparer.Ordinal));
        var newCompilation = (await after.GetProject(project.Id)!.GetCompilationAsync())!;
        var newRoot = (await after.GetDocument(addedId)!.GetSyntaxRootAsync())!;
        var newModel = newCompilation.GetSemanticModel(newRoot.SyntaxTree);
        var interfaceSymbol = (INamedTypeSymbol)newModel.GetDeclaredSymbol(newRoot.DescendantNodes().OfType<InterfaceDeclarationSyntax>().Single())!;
        var changedType = (INamedTypeSymbol)DocumentationCommentId.GetSymbolsForDeclarationId(type.GetDocumentationCommentId()!, newCompilation).Single();
        var implemented = changedType.Interfaces.SingleOrDefault(i => SymbolEqualityComparer.Default.Equals(i.OriginalDefinition, interfaceSymbol));
        var interfaceMembers = implemented?.GetMembers().Where(m => m is IPropertySymbol or IMethodSymbol { MethodKind: MethodKind.Ordinary }).ToArray() ?? [];
        Data.Require(implemented is not null && interfaceMembers.Length == members.Count && interfaceMembers.All(m =>
            changedType.FindImplementationForInterfaceMember(m) is { } implementation && request.Members.Contains(implementation.GetDocumentationCommentId(), StringComparer.Ordinal) &&
            Signature(implementation) == Signature(m)) && Constraints(type.TypeParameters) == Constraints(interfaceSymbol.TypeParameters),
            "implementation_mismatch", "Every generated member must bind to the explicitly selected original implementation.");
        var oldBytes = File.ReadAllBytes(document.FilePath!);
        var encoding = oldText.Encoding ?? new UTF8Encoding(false, true);
        var preamble = encoding.GetPreamble();
        var hasPreamble = preamble.Length > 0 && oldBytes.AsSpan().StartsWith(preamble);
        byte[] Encode(SourceText text) => (hasPreamble ? preamble : []).Concat(encoding.GetBytes(text.ToString())).ToArray();
        Data.Require(oldBytes.SequenceEqual(Encode(oldText)) && encoding.GetString(encoding.GetBytes(changedText.ToString())) == changedText.ToString(),
            "lossy_encoding", "Source must round-trip using its original encoding.");
        var edits = new[] { new FileEdit(document.FilePath!, "modify", Convert.ToBase64String(oldBytes), Convert.ToBase64String(Encode(changedText))),
            new FileEdit(output, "create", "", Convert.ToBase64String(Encoding.UTF8.GetBytes(interfaceText.ToString()))) };
        loaded.VerifyInputs();
        Paths.AbsentFile(output);
        var rootFolder = Path.GetDirectoryName(request.Workspace)!;
        var patch = RenamePlanner.Patch(Path.GetRelativePath(rootFolder, document.FilePath!), oldText, changedText, [insertion]);
        patch += RenamePlanner.Patch(Path.GetRelativePath(rootFolder, output), SourceText.From(""), interfaceText,
            [new TextChange(new TextSpan(0, 0), interfaceText.ToString())]).Replace("--- a/" + Path.GetRelativePath(rootFolder, output).Replace('\\', '/'), "--- /dev/null", StringComparison.Ordinal);
        return new Plan { Request = request, Sdk = loaded.Sdk, Roslyn = typeof(Compilation).Assembly.GetName().Version!.ToString(),
            Symbol = type.GetDocumentationCommentId()!, RelatedSymbols = request.Members, Projects = loaded.Projects.ToArray(),
            Inputs = loaded.Inputs.Values.ToArray(), Edits = edits.OrderBy(e => e.Path, StringComparer.Ordinal).ToArray(), Patch = patch,
            Limits = loaded.Limits.Concat(new[] {
                "Extract Interface covers one configuration and stable evaluated Compile globs; no project file, consumer types, DI registrations or method bodies are rewritten.",
                "Only single-declaration top-level classes with no class inheritance and explicit public instance methods/properties are supported; see README for refused signature shapes.",
                "New files are UTF-8 without BOM. Apply creates outputs exclusively before changing existing source; failures can leave empty/partial new files and require the reported manual recovery.",
                "Existing input handles protect against ordinary writes/deletion. Directory membership/path aliases and noncooperating writers are not locked; no cross-file atomicity is promised."
            }).Distinct().ToArray() };
    }

    private static bool Identifier(string name) => SyntaxFacts.IsValidIdentifier(name) && !name.StartsWith('@') && SyntaxFacts.GetKeywordKind(name) == SyntaxKind.None;
    private static string Escape(string name) => SyntaxFacts.GetKeywordKind(name) != SyntaxKind.None || SyntaxFacts.GetContextualKeywordKind(name) != SyntaxKind.None ? "@" + name : name;

    private static string Type(ITypeSymbol type) => type.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat
        .WithMiscellaneousOptions(SymbolDisplayMiscellaneousOptions.EscapeKeywordIdentifiers | SymbolDisplayMiscellaneousOptions.IncludeNullableReferenceTypeModifier));
    private static string Constraints(IEnumerable<ITypeParameterSymbol> parameters) => string.Join(";", parameters.Select(p =>
        $"{p.Name}:{p.HasReferenceTypeConstraint}:{p.ReferenceTypeConstraintNullableAnnotation}:{p.HasValueTypeConstraint}:{p.HasUnmanagedTypeConstraint}:{p.HasNotNullConstraint}:{p.HasConstructorConstraint}:{p.AllowsRefLikeType}:" +
        string.Join(",", p.ConstraintTypes.Select(Type))));
    private static string Signature(ISymbol member) => member switch {
        IMethodSymbol m => $"{Type(m.ReturnType)}:{m.ReturnNullableAnnotation}:{m.RefKind}:" + Constraints(m.TypeParameters) + ":" +
            string.Join(";", m.Parameters.Select(p => $"{p.Name}:{Type(p.Type)}:{p.NullableAnnotation}:{p.RefKind}:{p.IsParams}")),
        IPropertySymbol p => $"{Type(p.Type)}:{p.NullableAnnotation}:{p.RefKind}:{p.GetMethod?.DeclaredAccessibility == Accessibility.Public}:{p.SetMethod?.DeclaredAccessibility == Accessibility.Public}",
        _ => "unsupported"
    };

    private static async Task RequireUnchangedBindings(Solution before, Solution after, DocumentId changed,
        TextChange insertion, HashSet<string> introducedNames)
    {
        foreach (var document in before.Projects.SelectMany(p => p.Documents))
        {
            var root = (await document.GetSyntaxRootAsync())!;
            var names = root.DescendantNodes(descendIntoTrivia: true).OfType<SimpleNameSyntax>()
                .Where(n => introducedNames.Contains(n.Identifier.ValueText)).ToArray();
            if (names.Length == 0) continue;
            var updated = after.GetDocument(document.Id)!;
            var updatedRoot = (await updated.GetSyntaxRootAsync())!;
            var oldModel = (await document.GetSemanticModelAsync())!;
            var newModel = (await updated.GetSemanticModelAsync())!;
            foreach (var name in names)
            {
                var offset = document.Id == changed && name.SpanStart >= insertion.Span.Start ? insertion.NewText!.Length : 0;
                var counterpart = updatedRoot.FindNode(new TextSpan(name.SpanStart + offset, name.Span.Length), findInsideTrivia: true, getInnermostNodeForTie: true);
                Data.Require(counterpart is SimpleNameSyntax && Binding(oldModel.GetSymbolInfo(name)) == Binding(newModel.GetSymbolInfo(counterpart)),
                    "name_collision", $"New interface/namespace changes an existing name binding: {document.FilePath}:{name.SpanStart} ({name})");
            }
        }
    }

    private static string Binding(SymbolInfo info)
    {
        static string Identity(ISymbol symbol) => symbol is IAliasSymbol alias ? Identity(alias.Target) :
            $"{symbol.Kind}|{symbol.ContainingAssembly?.Identity}|{symbol.GetDocumentationCommentId()}|{symbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat)}";
        return info.Symbol is { } symbol ? Identity(symbol) : info.CandidateReason + ":" +
            string.Join(";", info.CandidateSymbols.Select(Identity).Order(StringComparer.Ordinal));
    }

    private static void RequireMember(ISymbol member)
    {
        var supported = member.DeclaredAccessibility == Accessibility.Public && !member.IsStatic && member.DeclaringSyntaxReferences.Length == 1 && member.GetAttributes().Length == 0;
        supported &= member switch {
            IMethodSymbol m => m.MethodKind == MethodKind.Ordinary && !m.IsOverride && !m.ReturnsByRef && !m.ReturnsByRefReadonly &&
                m.PartialDefinitionPart is null && m.PartialImplementationPart is null && m.ExplicitInterfaceImplementations.Length == 0 &&
                m.GetReturnTypeAttributes().Length == 0 && m.TypeParameters.All(p => p.GetAttributes().Length == 0) &&
                m.Parameters.All(p => !p.IsOptional && (p.ScopedKind == ScopedKind.None || p.RefKind == RefKind.Out) &&
                    !p.DeclaringSyntaxReferences.Any(r => r.GetSyntax() is ParameterSyntax s && s.Modifiers.Any(SyntaxKind.ScopedKeyword)) &&
                    p.GetAttributes().Length == 0) && SafeType(m.ReturnType) && m.Parameters.All(p => SafeType(p.Type)),
            IPropertySymbol p => !p.IsIndexer && !p.IsOverride && !p.ReturnsByRef && !p.ReturnsByRefReadonly && p.ExplicitInterfaceImplementations.Length == 0 &&
                p.SetMethod?.IsInitOnly != true && new[] { p.GetMethod, p.SetMethod }.Where(a => a is not null).All(a => a!.GetAttributes().Length == 0 && a.GetReturnTypeAttributes().Length == 0 &&
                    a.Parameters.All(parameter => parameter.GetAttributes().Length == 0)) && SafeType(p.Type),
            _ => false
        };
        Data.Require(supported, "unsupported_member", $"Unsupported member shape: {member.GetDocumentationCommentId()}. Select public instance methods/properties without attributes, optional/scoped parameters, ref returns, indexers, init, explicit implementations, overrides or unsafe types.");
    }

    private static bool SafeType(ITypeSymbol type) => type is not IPointerTypeSymbol and not IFunctionPointerTypeSymbol &&
        (type is not IArrayTypeSymbol array || SafeType(array.ElementType)) &&
        (type is not INamedTypeSymbol named || named.TypeArguments.All(SafeType));

    private static MemberDeclarationSyntax Declaration(SyntaxGenerator generator, ISymbol member)
    {
        var syntax = (MemberDeclarationSyntax)generator.Declaration(member);
        return syntax switch {
            MethodDeclarationSyntax method => method.WithModifiers(default).WithBody(null).WithExpressionBody(null)
                .WithSemicolonToken(SyntaxFactory.Token(SyntaxKind.SemicolonToken)),
            PropertyDeclarationSyntax property => property.WithModifiers(default).WithInitializer(null).WithExpressionBody(null).WithSemicolonToken(default)
                .WithAccessorList(SyntaxFactory.AccessorList(SyntaxFactory.List(property.AccessorList!.Accessors
                    .Where(a => a.Modifiers.Count == 0 || a.Modifiers.Any(SyntaxKind.PublicKeyword))
                    .Select(a => a.WithModifiers(default).WithBody(null).WithExpressionBody(null).WithSemicolonToken(SyntaxFactory.Token(SyntaxKind.SemicolonToken)))))),
            _ => throw new RefactorFailure("unsupported_member", "Cannot generate this member declaration.")
        };
    }
}
