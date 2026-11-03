# .NET generation

Install the release's `generation` bundle with `install-generation.py --project
<project-root>`. It places tools in `.ai/tools/dotnet-generation`. See the
[delivery guide](DELIVERY.md) for package registration and platform executables.

## Choose a generator

| Template | Output | Target |
| --- | --- | --- |
| `aicf-miniapi` | One project with Domain/Application/Infrastructure folders | .NET 10 Minimal API, `/work-items` |
| `aicf-webapi` | Domain, Application, Infrastructure and WebApi projects in a `.slnx` | .NET 10 controller API, `/api/work-items` |
| `aicf-usecase` | Interface, implementation, input and output | C# application item |
| `aicf-class` | One class | C# item |
| `aicf-interface` | One interface | C# item |

API starters store work items in memory. POST `{"title":"Pack the order"}` to
the route, then GET the response's `Location`. Replace this sample behavior with
the accepted domain behavior. Generated applications have no tool dependency.

Register the packaged `.nupkg`, then use `dotnet new <short-name> --help`.
For items, choose a valid type name and `--namespace`; preview paths with
`--dry-run` and resolve collisions before writing. Run a generated WebApi via
`dotnet run --project <output>/WebApi/<name>.WebApi.csproj`.

## Insert a fragment

[SnippetTool](snippet-tool/README.md) supports `list`, `search`, `inspect` and
`render`. Inspect the context, parameters and usings before rendering. It returns
text; the caller inserts it and validates the affected code.

Available fragments: interface method, string/null/cancellation guards,
constructor assignment, Guid ID, readonly property, domain interfaces and
optional ES aggregate mechanics. ES is selected only by the target's architecture.

Keep custom catalogs outside managed tools and select them with `source`.
For custom native templates, extract the nupkg into a target-owned directory,
change identity/name/shortName, then register that directory. Template sources
and `.template.config` belong inside the nupkg, not as loose installed resources.
