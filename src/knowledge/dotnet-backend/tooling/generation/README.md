# .NET generation

Use native .NET templates in `dotnet-new/` to generate a project, solution or
C# source files. Use [SnippetTool](snippet-tool/README.md) to render a fragment
for insertion into an existing interface or method.

## Native templates

| Source directory under `dotnet-new/` | Preview short name | Kind | Generated layout |
| --- | --- | --- | --- |
| `miniapi` | `aicf-miniapi` | Project | One ASP.NET Core project with `Domain/`, `Application/` and `Infrastructure/` folders. `Program.cs` maps `/work-items`. |
| `web-api` | `aicf-webapi` | Project | A `.slnx` with Domain, Application, Infrastructure and WebApi projects. WebApi has the `Program.cs` composition root, a controller at `/api/work-items`, and request and response models. |
| `use-case` | `aicf-usecase` | Item | Four files in the output directory. For `--name DescribeLabel`, they are `IDescribeLabelUseCase.cs`, `DescribeLabelUseCase.cs`, `DescribeLabelInput.cs` and `DescribeLabelOutput.cs`. |
| `class` | `aicf-class` | Item | One `<Name>.cs` file containing a C# class. |
| `interface` | `aicf-interface` | Item | One `<Name>.cs` file containing a C# interface. |

Both API templates target .NET 10 and serve JSON. POST a body such as
`{"title":"Pack the order"}` to the listed route, then follow the response's
`Location` to read the work item. Data lasts for the lifetime of the process.

### Quick start

With the .NET 10 SDK, run these commands from this directory. Installation
registers the local template sources for the current user.

```powershell
dotnet new install ./dotnet-new/miniapi ./dotnet-new/web-api ./dotnet-new/use-case ./dotnet-new/class ./dotnet-new/interface
dotnet new list aicf
dotnet new aicf-miniapi --name Example.Orders --output ./Example.Orders
dotnet run --project ./Example.Orders
```

For the controller-based solution, use `dotnet new aicf-webapi --name
Example.OrdersApi --output ./Example.OrdersApi` and run
`dotnet run --project ./Example.OrdersApi/WebApi/Example.OrdersApi.WebApi.csproj`.

Generate an item in the project with a valid C# type name and a dot-separated
namespace. The item templates default to `Example` if `--namespace` is omitted.

```powershell
dotnet new aicf-usecase --name DescribeLabel --namespace Example.Orders.Application --output ./Example.Orders/Application --dry-run
```

Remove `--dry-run` after reviewing the paths. If the SDK reports a destructive
collision, choose a different name or output directory. The Use Case starter
returns the trimmed text and its length. Replace that example with the target behavior
and wire the Use Case into its caller as needed.

Generated files belong to the target project. For a team template, copy its
entire directory including `.template.config` and give the copy its own
versioned `identity`, `name` and unique `shortName` in `template.json` before
installing it. Use `dotnet new uninstall` to list registered packages and
`dotnet new uninstall <installation-path>` to remove a directory installation.

## C# snippets

Extract a self-contained archive for your platform and keep the executable and
catalog assets together. It runs without a separately installed .NET SDK or
shared runtime. Pass `--request request.json` to the executable and choose
`list`, `search`, `inspect` or `render` in the request. Use the returned metadata
to check the insertion context and required types or usings, then insert the
rendered text and validate the affected code. The renderer works on text.
Keep team catalogs and bodies outside the tool directory and select the catalog
with the request's `source`. The [snippet guide](snippet-tool/README.md) includes
the request schema and examples.

Build an archive on the target OS with PowerShell 7 and the .NET 10 SDK.

```powershell
./Publish-Snippets.ps1 -Version 0.1.0-dev.1 -RuntimeIdentifier win-x64 -OutputRoot <fresh-output-root>
```

The script produces a ZIP on Windows or tar.gz on Linux, with a SHA-256 sidecar.
The default is self-contained CoreCLR. `-NativeAot` selects an evaluation build
that also needs the platform's native compiler and libraries, including MSVC
Build Tools and the Windows SDK on Windows. Extracted CoreCLR and Native AOT
archives were exercised in Windows 11 x64 Sandbox and Ubuntu 24.04 x64 without
a preinstalled modern .NET SDK or shared runtime. Those are the tested platforms.
The consuming project needs APIs compatible with its selected snippet, such as
.NET 8+ for the shipped guard, and has no SnippetTool dependency.
