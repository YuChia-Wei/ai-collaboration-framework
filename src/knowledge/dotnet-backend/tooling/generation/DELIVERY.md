# .NET generation tools

Install this complete directory into an existing project:

```text
python install-generation.py --project /path/to/project
```

The installer verifies the manifest and writes `.ai/tools/dotnet-generation`.
It does not register templates, edit project code or select a technology stack.
Updates replace only an unchanged previous installation; modified or unknown
files cause a refusal. Keep custom snippets and templates outside this directory.

With the .NET 10 SDK, register the installed package:

```text
dotnet new install .ai/tools/dotnet-generation/templates/AICF.Dotnet.Templates.<version>.nupkg
dotnet new list aicf
dotnet new aicf-webapi --name Orders --output Orders
```

The package includes `aicf-miniapi`, `aicf-webapi`, `aicf-usecase`, `aicf-class`
and `aicf-interface`. Use `--help` and `--dry-run` before generating into an
existing project. `dotnet new uninstall AICF.Dotnet.Templates` unregisters it.
For customization, extract the nupkg (ZIP) into a project-owned directory,
change template identity and shortName, then register that directory.
The C# sources and `.template.config` inside the package are required by
`dotnet new`; they are not loose installed project files.

Run `snippets/win-x64/SnippetTool.exe` on Windows x64 or
`snippets/linux-x64/SnippetTool` on Linux x64 with `--request request.json`.
Neither needs an installed .NET runtime. Linux needs the platform's native
runtime dependencies (Ubuntu 24.04 is the tested baseline).
Use `{"schemaVersion":1,"operation":"list"}`, then inspect one ID before rendering it.
See `snippets/README.md` for request fields and customization.
Rendering returns text; insertion and compilation remain explicit steps.

`generation.json` identifies the source commit, release version and file hashes.
The application generated from a template does not depend on these tools.
