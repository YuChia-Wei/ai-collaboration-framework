# .NET template selection

Use the [generation guide](../tooling/generation/README.md) to select a packaged
project or item template. Use snippets for fragments inside existing files.

Choose behavior and invariant ownership before generating code. Controllers
adapt transport; Use Cases own application behavior; Domain owns business rules.
Persistence and messaging stay in selected adapters. Generated code requires the
same target tests and review as handwritten code.
