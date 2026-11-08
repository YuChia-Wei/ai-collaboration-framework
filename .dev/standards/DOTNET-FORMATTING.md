# .NET Formatting Standard

This standard governs this source repository's C# formatting. Consumer projects
own their EditorConfig and automation choices; framework installation does not
adopt this source policy or enable an AI hook.

## Rules and entry point

The root `.editorconfig` owns source formatting values: UTF-8, LF, a final newline,
spaces, and four-space C# indentation. Keep template-specific settings when the
template deliberately demonstrates another value. Do not change embedded source
fixtures or expected strings merely to match the surrounding test file's layout.

Use the SDK's `dotnet format whitespace` for ordinary generated or edited C#.
The optional [thin PowerShell entry](../../src/tools/dotnet/formatting/Format-Dotnet.ps1)
resolves an explicit project/solution and file selection, runs from the workspace
directory, and returns native output and exit status. See its
[usage and migration notes](../../src/tools/dotnet/formatting/README.md).
An explicit `-Apply` changes files; the default checks them. Relative file names
are relative to the selected project/solution directory. Absolute file names
also work for files beneath that directory. Choose the owning project or an
enclosing solution for other selected files. Use the explicit whole-workspace
option when the requested scope includes all workspace sources.
Absolute paths must retain the workspace-root casing. The script refuses literal
glob characters and POSIX backslashes; native SDK include matching remains
case-insensitive and can match case-distinct sources on case-sensitive volumes.

`style`, `analyzers`, and `All` may apply diagnostic fixes beyond whitespace.
Choose them explicitly for the requested change and inspect the resulting diff.
Do not run broad cleanup over unrelated source changes as an incidental task step.
Use the actual target's SDK and EditorConfig; do not silently change SDK selection
or remove project-defined analyzers/generators to make formatting succeed.

The script defaults to `--no-restore`. Restore the selected workspace separately
when its assets are missing. The `-Restore` switch permits the SDK mode's normal
restore behavior; whitespace mode does not perform an implicit restore.
SDK loading can execute
project build logic; a check is not an operating-system write sandbox. The native
command does not supply the removed FormatTool JSON envelope, consent protocol,
file snapshots, transaction rollback, or strict selection-admission semantics.
An existing path that is not a workspace item can be unmatched; inspect the
selection and actual formatter result instead of treating exit zero alone as
proof that every requested file was formatted.

## Work sequence and evidence

Format the changed C# before final validation, inspect the diff, then run only
the checks justified by the actual semantic effect under
[source development policy](SOURCE-DEVELOPMENT-POLICY.md). Whitespace-only edits
do not require another product suite unless they affect parsing, exact output,
template content, or another relevant contract. Format failures remain visible;
do not report success from an unexecuted command or silently discard the changes.

Tests for the thin script cover its own path/argument and exit-code boundary with
a small real SDK fixture. SDK formatter and analyzer correctness belongs upstream;
do not recreate the old wrapper's test matrix. Delivery checks verify that the
script is present and usable from its documented bundle location.

## Optional completion hooks

No hook is enabled by this standard. The #594 assessment records feasibility and
limitations. A later selected hook should use an explicit repository and file
scope, bounded synchronous execution and visible errors. A model `Stop` event is
a turn boundary; it does not establish that the conversation or workflow is done.
The hook adapter must follow the provider's output protocol and must not request
another model turn merely to run formatting. Git status alone cannot attribute
edits to the current AI turn. Reconcile concurrent writers and any formatting
after tests before claiming final-state acceptance.

Reference: [Microsoft dotnet format](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-format).
