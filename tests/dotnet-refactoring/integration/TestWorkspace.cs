using System.Diagnostics;
using System.Reflection;
using System.Runtime.Loader;
using System.Text;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.Diagnostics;
using Microsoft.CodeAnalysis.Text;

namespace RefactorTool.IntegrationTests;

internal sealed class TestDirectory : IDisposable
{
    private readonly List<string> junctions = [];
    internal string Root { get; } = CreateScratch();

    private static string CreateScratch()
    {
        var configured = Environment.GetEnvironmentVariable("AICF_TEST_WORK");
        var directory = Directory.CreateDirectory(Path.GetFullPath(configured ?? Path.GetTempPath()));
        // macOS's default temp directory is reached through /var. Resolve
        // existing ancestors so portable cases exercise ordinary source paths.
        return PhysicalDirectory(directory).CreateSubdirectory($"refactor-{Guid.NewGuid():N}").FullName;
    }

    private static DirectoryInfo PhysicalDirectory(DirectoryInfo directory)
    {
        if (directory.Parent is null)
            return directory;

        var parent = PhysicalDirectory(directory.Parent);
        var entry = new DirectoryInfo(Path.Combine(parent.FullName, directory.Name));
        return (DirectoryInfo?)entry.ResolveLinkTarget(returnFinalTarget: true) ?? entry;
    }

    internal string PathFor(string relative) => Path.GetFullPath(relative, Root);

    internal string Write(string relative, string text) => Write(relative, Encoding.UTF8.GetBytes(text));

    internal string Write(string relative, byte[] bytes)
    {
        var path = PathFor(relative);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        File.WriteAllBytes(path, bytes);
        return path;
    }

    internal async Task Junction(string relative, string target)
    {
        var pwsh = RefactorTestProfile.RequirePwsh();
        var path = PathFor(relative);
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        // This command creates the real OS fixture. Assertions remain in xUnit.
        var result = await RunProcess(pwsh, Root,
            ["-NoProfile", "-Command", "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path $env:REFACTOR_TEST_LINK -Target $env:REFACTOR_TEST_TARGET | Out-Null"],
            TimeSpan.FromSeconds(30), new Dictionary<string, string> { ["REFACTOR_TEST_LINK"] = path, ["REFACTOR_TEST_TARGET"] = target });
        Assert.True(result.ExitCode == 0, result.Output + result.Error);
        junctions.Add(path);
    }

    internal void RemoveJunction(string relative)
    {
        var path = PathFor(relative);
        Assert.True(File.GetAttributes(path).HasFlag(FileAttributes.ReparsePoint));
        Directory.Delete(path);
        Assert.True(junctions.Remove(path));
    }

    internal static async Task<(int ExitCode, string Output, string Error)> RunProcess(string executable, string cwd,
        string[] args, TimeSpan limit, Dictionary<string, string>? environment = null)
    {
        var start = new ProcessStartInfo(executable)
        {
            WorkingDirectory = cwd,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8
        };
        foreach (var arg in args) start.ArgumentList.Add(arg);
        // Locator configures the test host. Let each child resolve its own SDK.
        start.Environment.Remove("MSBUILD_EXE_PATH");
        start.Environment.Remove("MSBuildExtensionsPath");
        start.Environment.Remove("MSBuildSDKsPath");
        start.Environment["DOTNET_CLI_UI_LANGUAGE"] = "en-US";
        // A reusable build node can retain this process's redirected pipes.
        // Keep test fixture commands isolated and finish their output with the command.
        start.Environment["MSBUILDDISABLENODEREUSE"] = "1";
        start.Environment["DOTNET_CLI_USE_MSBUILD_SERVER"] = "0";
        if (environment is not null)
            foreach (var (key, value) in environment) start.Environment[key] = value;
        using var process = Process.Start(start)!;
        using var timeout = new CancellationTokenSource(limit);
        var output = process.StandardOutput.ReadToEndAsync(timeout.Token);
        var error = process.StandardError.ReadToEndAsync(timeout.Token);
        try
        {
            await process.WaitForExitAsync(timeout.Token);
            return (process.ExitCode, await output, await error);
        }
        catch (OperationCanceledException)
        {
            var exited = process.HasExited;
            if (!exited) process.Kill(entireProcessTree: true);
            await process.WaitForExitAsync();
            throw new TimeoutException($"{executable} {string.Join(' ', args)} exceeded {limit} while {(exited ? "draining output" : "waiting for exit")}.");
        }
    }

    public void Dispose()
    {
        foreach (var path in junctions.AsEnumerable().Reverse())
        {
            if (File.GetAttributes(path).HasFlag(FileAttributes.ReparsePoint)) Directory.Delete(path);
        }
        Directory.Delete(Root, recursive: true);
    }
}

internal sealed class SemanticWorkspace : IDisposable
{
    internal const string Service = """
        namespace Demo;
        public interface IService { int Get(int value); }
        public class Service : IService {
            public int Field = 1;
            public int Property { get; set; }
            public virtual int Get(int value) { int local = value; return local + Field; }
            public int Get(string value) => value.Length;
        }
        public class Derived : Service { public override int Get(int value) => base.Get(value); }
        public class Other { public int Get(int value) => value; }
        """;
    internal const string Consumer = """
        using Demo;
        /// <see cref="Service.Get(int)"/>
        public class Use { public int Run() { IService service = new Service(); return service.Get(2) + new Derived().Get(3) + new Other().Get(4); } public string Name => nameof(IService.Get); public string Text => "Get Service"; } // Get Service
        """;
    internal const string GetInt = "M:Demo.Service.Get(System.Int32)";
    internal const string Property = "P:Demo.Service.Property";
    private static readonly MetadataReference[] References = ((string)AppContext.GetData("TRUSTED_PLATFORM_ASSEMBLIES")!)
        .Split(Path.PathSeparator)
        .Where(path => Path.GetDirectoryName(path) == Path.GetDirectoryName(typeof(object).Assembly.Location))
        .Select(path => MetadataReference.CreateFromFile(path))
        .ToArray();
    private readonly TestDirectory directory = new();
    private readonly ProjectId first;
    private readonly ProjectId? second;
    private FixtureAnalyzerLoader? analyzerLoader;

    internal SemanticWorkspace(string? consumer = null)
    {
        first = AddProject("A");
        if (consumer is not null)
        {
            second = AddProject("B");
            Assert.True(Loaded.Workspace.TryApplyChanges(Loaded.Workspace.CurrentSolution.AddProjectReference(second, new(first))));
            Add("B/Use.cs", consumer);
        }
    }

    internal LoadedWorkspace Loaded { get; } = new(new AdhocWorkspace(), "component");
    internal string Source => directory.PathFor("A/Service.cs");
    internal string Output => directory.PathFor("A/ISelected.cs");
    internal string ConsumerPath => directory.PathFor("B/Use.cs");
    internal Request Rename => new()
    {
        Workspace = directory.PathFor("Demo.slnx"),
        Project = directory.PathFor("A/A.csproj"),
        Symbol = GetInt,
        NewName = "Fetch"
    };
    internal Request Extract => Rename with
    {
        Operation = "extract-interface",
        Symbol = "T:Demo.Service",
        NewName = "ISelected",
        Namespace = "Contracts",
        OutputFile = Output,
        Members = [GetInt, Property]
    };

    private ProjectId AddProject(string name)
    {
        var id = ProjectId.CreateNewId();
        var project = Microsoft.CodeAnalysis.ProjectInfo.Create(id, VersionStamp.Create(), name, name, LanguageNames.CSharp,
            filePath: directory.PathFor($"{name}/{name}.csproj"),
            compilationOptions: new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary, nullableContextOptions: NullableContextOptions.Enable),
            parseOptions: new CSharpParseOptions(LanguageVersion.CSharp14, DocumentationMode.Diagnose),
            metadataReferences: References);
        Assert.True(Loaded.Workspace.TryApplyChanges(Loaded.Workspace.CurrentSolution.AddProject(project)));
        return id;
    }

    internal void Add(string relative, string source, bool bom = false) =>
        Add(relative, (bom ? Encoding.UTF8.GetPreamble() : []).Concat(Encoding.UTF8.GetBytes(source)).ToArray());

    internal void Add(string relative, byte[] bytes)
    {
        var path = directory.Write(relative, bytes);
        Loaded.Capture(path, editable: true);
        Loaded.EditableSources.Add(path);
        using var stream = new MemoryStream(bytes);
        var text = SourceText.From(stream, Encoding.UTF8);
        var id = DocumentId.CreateNewId(relative.StartsWith("B/", StringComparison.Ordinal) ? second! : first);
        Assert.True(Loaded.Workspace.TryApplyChanges(Loaded.Workspace.CurrentSolution.AddDocument(id, Path.GetFileName(path), text, filePath: path)));
    }

    internal void AddGenerator(string source)
    {
        var path = directory.Write("Generator.dll", EmitGenerator(source, typeof(Compilation).Assembly.Location));
        analyzerLoader = new FixtureAnalyzerLoader();
        var analyzer = new AnalyzerFileReference(path, analyzerLoader);
        Assert.Single(analyzer.GetGenerators(LanguageNames.CSharp));
        Assert.True(Loaded.Workspace.TryApplyChanges(Loaded.Workspace.CurrentSolution.AddAnalyzerReference(first, analyzer)));
        Loaded.Capture(path);
    }

    internal static byte[] EmitGenerator(string source, string codeAnalysisPath)
    {
        var references = References.Append(MetadataReference.CreateFromFile(codeAnalysisPath));
        var compilation = CSharpCompilation.Create("TestGenerator" + Guid.NewGuid().ToString("N"),
            [CSharpSyntaxTree.ParseText(source)], references,
            new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary));
        using var image = Emit(compilation);
        return image.ToArray();
    }

    private sealed class FixtureAnalyzerLoader : IAnalyzerAssemblyLoader
    {
        private readonly AssemblyLoadContext context = new(null, isCollectible: true);

        // This fixture generator only depends on the already loaded runtime and
        // Roslyn assemblies. Stream loading leaves the fixture PE deletable.
        public void AddDependencyLocation(string fullPath) { }

        public Assembly LoadFromPath(string fullPath)
        {
            using var stream = File.OpenRead(fullPath);
            return context.LoadFromStream(stream);
        }

        internal void Unload() => context.Unload();
    }

    internal async Task<Plan> PlanRename(Request request) =>
        await RenamePlanner.PlanRename(RenamePlanner.Normalize(request), Loaded);

    internal async Task<Plan> PlanExtraction(Request request)
    {
        var normalized = InterfacePlanner.Normalize(request);
        var target = await InterfacePlanner.SelectTarget(normalized, Loaded);
        return await InterfacePlanner.BuildPlan(normalized, Loaded, target);
    }

    internal async Task<string> RunConsumer(Plan plan, string consumer)
    {
        var solution = Loaded.Workspace.CurrentSolution;
        foreach (var edit in plan.Edits)
        {
            var text = SourceText.From(After(edit), Encoding.UTF8);
            var document = solution.GetDocumentIdsWithFilePath(edit.Path).SingleOrDefault();
            solution = document is null
                ? solution.AddDocument(DocumentId.CreateNewId(first), Path.GetFileName(edit.Path), text)
                : solution.WithDocumentText(document, text);
        }
        // Emit the consumer separately so public accessibility and metadata
        // signatures are checked across the same boundary as a project reference.
        var compilation = (CSharpCompilation)(await solution.GetProject(first)!.GetCompilationAsync())!;
        var unique = Guid.NewGuid().ToString("N");
        using var library = Emit(compilation.WithAssemblyName("Library" + unique));
        var probeOptions = new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary,
            nullableContextOptions: NullableContextOptions.Enable, generalDiagnosticOption: ReportDiagnostic.Error)
            .WithSpecificDiagnosticOptions(new Dictionary<string, ReportDiagnostic> { ["CS1591"] = ReportDiagnostic.Suppress });
        var probeSource = CSharpSyntaxTree.ParseText(consumer, (CSharpParseOptions)solution.GetProject(first)!.ParseOptions!);
        var probeReferences = References.Append(MetadataReference.CreateFromImage(library.ToArray()));
        using var probe = Emit(CSharpCompilation.Create("Consumer" + unique, [probeSource], probeReferences, probeOptions));
        var context = new System.Runtime.Loader.AssemblyLoadContext(null, isCollectible: true);
        try
        {
            context.LoadFromStream(library);
            var assembly = context.LoadFromStream(probe);
            return Assert.IsType<string>(assembly.GetType("Probe")!.GetMethod("Run")!.Invoke(null, null));
        }
        finally { context.Unload(); }
    }

    private static MemoryStream Emit(CSharpCompilation compilation)
    {
        var image = new MemoryStream();
        var emitted = compilation.Emit(image);
        Assert.True(emitted.Success, string.Join(Environment.NewLine, emitted.Diagnostics));
        image.Position = 0;
        return image;
    }

    internal static string After(FileEdit edit) => Encoding.UTF8.GetString(Convert.FromBase64String(edit.After));
    internal static string After(Plan plan, string path) => After(Assert.Single(plan.Edits, edit => edit.Path == path));

    public void Dispose()
    {
        Loaded.Dispose();
        analyzerLoader?.Unload();
        directory.Dispose();
    }
}
