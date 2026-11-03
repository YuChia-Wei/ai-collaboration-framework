# .NET generation

Both API profiles target the .NET 10 SDK and use a single ASP.NET Core
project with one `Program.cs` composition root. The Web SDK supplies the
ASP.NET Core host. Both templates serve JSON endpoints and omit Razor,
views, static assets, and frontend tooling.

| Template | HTTP adapter | Work item route |
| --- | --- | --- |
| `aicf-miniapi` | Minimal API endpoints in `Program.cs` | `/work-items` |
| `aicf-webapi` | `ControllerBase` actions with explicit request and response models | `/api/work-items` |

The `aicf-` short names are provisional names for the current preview.

Both samples create and read work items in process memory. The aggregate
owns the title invariant, and the Use Cases call application-owned ports.
The Controller-based template follows the Inventory Web API adapter in
`dotnet-mq-arch-lab` at `7a0bff401bea86428b5c24eab6362ef2170d20d7`.
It uses the reference's controller registration, direct Use Case interface
calls, and HTTP model mapping in a standalone single-domain project.

The native templates are readable directories under `dotnet-new/`. Run the
commands below from this generation directory. They install template sources
into the SDK's template registry for the current user.

```powershell
dotnet new install ./dotnet-new/miniapi ./dotnet-new/web-api ./dotnet-new/use-case ./dotnet-new/class ./dotnet-new/interface
dotnet new list aicf
dotnet new aicf-usecase --help
dotnet new aicf-miniapi --name Example.Orders --output ./Example.Orders --dry-run
dotnet new aicf-miniapi --name Example.Orders --output ./Example.Orders
dotnet run --project ./Example.Orders

dotnet new aicf-webapi --name Example.OrdersApi --output ./Example.OrdersApi
dotnet run --project ./Example.OrdersApi
```

Send `POST /work-items` to the Minimal API or `POST /api/work-items` to the
Controller-based API with JSON such as `{"title":"Pack the order"}`, then
follow the response's `Location` to read it. In-memory data lasts for the
lifetime of the process.

```powershell
dotnet new aicf-usecase --name DescribeLabel --namespace Example.Orders.Application --output ./Example.Orders/Application
dotnet new aicf-class --name PackingNote --namespace Example.Orders.Domain --output ./Example.Orders/Domain
dotnet new aicf-interface --name IOrderReader --namespace Example.Orders.Application --output ./Example.Orders/Application
dotnet build ./Example.Orders
```

Use valid C# type identifiers for item names and dot-separated identifiers
for namespaces. The Use Case item emits a port, implementation, input and
output. Its starter behavior trims text and returns it with its length. Replace
this example with the target operation and its tests before adopting it as
business behavior. For an HTTP caller, import the chosen namespace in
`Program.cs`, register the port and implementation before `builder.Build()`,
then map the HTTP request to the input in the endpoint.

```csharp
builder.Services.AddTransient<IDescribeLabelUseCase, DescribeLabelUseCase>();
```

Add an endpoint only when the target needs one. The template writes its source
files into the chosen directory. Use `--dry-run` before writing to a populated
directory. On a collision, review the reported path and choose a new name or
location. The ordinary invocation refuses destructive replacements.

Generated files belong to the target project. To maintain a custom template,
copy the whole source directory including `.template.config`, then give the copy
its own versioned `identity`, `name`, and unique `shortName` in `template.json`
before installing it. Invoke that short name to select the custom template.
List registered template packages and remove directory installations with these
commands from the original generation directory.

```powershell
dotnet new uninstall
dotnet new uninstall ./dotnet-new/miniapi ./dotnet-new/web-api ./dotnet-new/use-case ./dotnet-new/class ./dotnet-new/interface
```

## Snippet delivery and prerequisites

The [.NET 10 console and snippet inventory](snippet-tool/README.md) provide
`list`, `search`, `inspect` and `render`. Use them for fragments inside an existing
interface or method. Inspect the selected metadata, pass parameters explicitly,
then insert the returned text with the target's editor and validate the affected
context. Rendering does not perform AST merging or semantic refactoring.

Build a versioned self-contained archive using PowerShell 7 and the .NET 10 SDK:

```powershell
./Publish-Snippets.ps1 -Version 0.1.0-dev.1 -RuntimeIdentifier win-x64 -OutputRoot <fresh-output-root>
```

The package contains the executable, its runtime closure, default snippet data,
README and `package.json`; a SHA-256 sidecar accompanies the archive. Package on
the target OS. Windows uses ZIP; Linux uses tar.gz to preserve executable modes.
Add `-NativeAot` only with the platform's native compiler prerequisites. The
tool uses an independent preview version; package production is separate from
Framework publication. No `dotnet tool` package is provided.

Local validation covers the Windows x64 CoreCLR archive and both Linux x64
CoreCLR and Native AOT archives produced by this script. Both Linux archives
passed extracted CLI and custom-source checks in a clean Ubuntu 24.04 container
without an installed .NET SDK or runtime. This does not establish clean Windows
host acceptance or support for every Linux distribution or architecture.
Windows AOT builds require Visual Studio 2022 or later with Desktop development
with C++ and its default components, including the Windows SDK. Native AOT
remains an evaluation candidate; performance observations precede support and
threshold decisions. No performance acceptance limit has been selected.

Extract each tool version into a fresh directory and retain the complete package.
Keep team catalogs and bodies in a separate directory and select them with the
request's `source`; updating the tool must not overwrite those copies. Generated
code belongs to the target and is not regenerated on tool upgrades.

Running the self-contained snippet package needs neither an installed .NET SDK
nor a separately installed .NET runtime. Native `dotnet new`, building generated
projects and building this tool from source need the .NET 10 SDK. Both API templates use
`Microsoft.NET.Sdk.Web` and the ASP.NET Core shared framework,
with no third-party PackageReference. The interface snippet needs the declared
types/usings; the guard uses `ArgumentException.ThrowIfNullOrWhiteSpace` (.NET 8+).
Other targets must select compatible custom snippets. This does not promise
universal .NET Framework or .NET 6 compatibility. Generated applications have no
dependency on the snippet tool, its runtime or the template directory.
