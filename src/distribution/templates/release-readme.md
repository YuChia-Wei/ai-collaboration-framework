# AI Collaboration Framework ${label}

Source: `${source_commit}`
Catalog: `${catalog_identity}`
Version: `${release_version}` (${package_classification})

## Install collaboration resources

Use `engine/src/tools/derive-subset.py` with an explicit selection, `catalog`,
its identity and `engine-pin.json`. Then use the pinned engine's
`maintain_framework.py` inspect, plan and apply operations. Python 3.11+ and
PyYAML 6.x are required. Keep work directories outside the target project.
Review removals and conflicts before apply; modified managed files and unknown
collisions must be reconciled. Recover an interrupted operation with its original
engine and journal.

| Available adapter | Version |
| --- | --- |
${adapter_rows}

Select both `claude` and `codex` for both native skill entry trees. Installation
selection is explicit; the ZIP is not an initialized project.

## Install .NET generation tools

Run `python generation/install-generation.py --project <project-root>`.
It installs the packaged templates, SnippetTool executables and SDK formatting
script into `.ai/tools/dotnet-generation`. Check `generation/generation.json`
for this bundle's exact RIDs, delivery mode and hashes. Three-RID Native AOT
bundles include Windows x64, Linux x64 and Apple silicon. Earlier two-RID
bundles include Windows x64 and Linux x64. See `generation/README.md` for
startup instructions and the matching external snippet data.
No template registration or application generation happens during installation.

`content-hashes.json` and the external release manifest identify the exact bytes.
Verify the ZIP checksum before use. A snapshot is a local/CI build, not a public
release; check GitHub for publication status. Source, build, installation and
application behavior are separate evidence.
