# .NET generation

Install the release's `generation` bundle with `install-generation.py --project
<project-root>`. It places tools in `.ai/tools/dotnet-generation`. See the
[delivery guide](DELIVERY.md) for directory/package registration, platform
executables, installation diagnostics and tool version/control guidance.

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

`--name` replaces the starter's project names and root namespace; `WorkItem`
and its routes remain a fixed reference feature. The controller starter uses
`<name>.Controllers` and `<name>.Models.*` inside the `<name>.WebApi` project;
the project suffix is not part of those namespaces. Adapt the sample to the
target's naming rules. Both starters use the host's default error behavior:
Minimal API responses can be empty, while `[ApiController]` supplies
ProblemDetails and content-type checks. For example, a POST without body or
Content-Type yields 400 in the Minimal API and 415 in the controller starter.
They do not define a shared production error contract; select one when replacing
the reference feature.

Project templates target `net10.0` with no `--framework` option. Item templates
emit C# only; they do not select a project TFM. .NET 10 is the supported baseline;
this delivery does not establish .NET 8 compatibility.

Register either an extracted template directory or the packaged `.nupkg` as
shown in the delivery guide, then use `dotnet new <short-name> --help`.
For items, choose a valid type name and `--namespace`; preview paths with
`--dry-run` and resolve collisions before writing. The namespace defaults to
`Example`; supply the target namespace explicitly. Run a generated WebApi via
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
and `.template.config` are delivered inside the nupkg and can be extracted as a
complete directory for direct registration without building a new package.
