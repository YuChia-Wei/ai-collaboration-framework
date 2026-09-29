# Script Inventory

## Summary

`.ai/scripts` currently mixes four different responsibilities:

1. AI workflow and context governance scripts.
2. Shell orchestrators that run multiple checks.
3. Grep-based C# semantic checks generated from markdown standards.
4. Runtime/config/file-system checks that may remain as scripts or become dotnet tools/tests.

The risky category is the third one. It attempts to validate C# architecture and design rules through plain-text matching. Those rules should move to Roslyn analyzers, architecture tests, `.editorconfig`, `dotnet format`, or dotnet tests.

## Inventory

| Path | Current behavior | C# semantic check? | Transition class | Recommendation |
| --- | --- | --- | --- | --- |
| `.ai/scripts/check-all.sh` | Runs multiple check scripts in quick/full/critical modes. Still contains old JPA/Spring pending text. | Indirectly | `keep-as-orchestrator` | Keep only as a thin runner for dotnet-native tools; remove direct dependency on grep C# validators after replacements exist. |
| `src/tools/dotnet/code-review.sh` | Selects check scripts from changed files and produces review-oriented output. Still contains old JPA naming. | Indirectly | `keep-as-orchestrator` | Convert to analyzer/test/report collector and AI review helper; do not keep as regex-based C# validator. |
| `.ai/scripts/check-prompt-portability.sh` | Scans `.ai/assets/shared` for non-portable ADR references and source-project terms. | No | `keep-ai-workflow-script` | Candidate to keep because it checks AI context portability, not C# semantics. Consider future dotnet context-lint tool if it grows. |
| `src/tools/dotnet/check-coding-standards.sh` | Checks standards docs, prompt references, duplicated rule text, and script path hygiene. | No, mostly docs/context | `keep-ai-workflow-script` | Keep or convert later to repo context lint. It is not a Roslyn analyzer candidate. |
| `src/tools/dotnet/check-dockerfile-csproj-copy-sync.ps1` | Checks Dockerfile `COPY` lines against project references. | No | `replace-with-dotnet-tool-or-test` | Keep short term as PowerShell glue; long-term candidate for dotnet tool or CI validation. |
| `src/tools/dotnet/check-mutation-coverage.sh` | Runs `dotnet test` and Stryker.NET, then parses Stryker output. | No | `replace-with-dotnet-tool-or-test` | Keep as orchestrator only if useful; formal validation should be Stryker.NET configuration and CI task. |
| `.ai/scripts/test-profile-startup.sh` | Runs profile startup checks for configured runtime profiles. | No | `replace-with-dotnet-tool-or-test` | Prefer integration/smoke tests; shell may remain as local convenience runner. |
| `src/tools/dotnet/validate-dual-profile-config.sh` | Validates dual profile configuration files and startup shape. | No | `replace-with-dotnet-tool-or-test` | Prefer integration/config tests or dotnet tool if cross-file validation remains useful. |
| `src/tools/dotnet/check-spec-compliance.sh` | Reads spec JSON and checks for named files in `src`. | No semantic C# analysis, but code-file existence check | `replace-with-dotnet-tool-or-test` | Replace with spec compliance validator implementation or dotnet tool; shell is acceptable only as transitional glue. |
| `src/tools/dotnet/check-dotnet-config.sh` | Greps csproj, appsettings, and source for EF/Wolverine/outbox/in-memory DB configuration. | Partial | `replace-with-dotnet-tool-or-test` | Split: package/config checks to dotnet tool; C# API usage checks to analyzer. |
| `.ai/scripts/check-projection-config.sh` | Former source/config grep for projection registration. | Partial | `replaced-with-dotnet-test` | Replaced by `DotnetBackendValidation` EF model registration tests and removed in validator phase 3. |
| `src/tools/dotnet/check-test-di-compliance.sh` | Greps test code/config for DI/test setup patterns. | Yes | `replace-with-roslyn-analyzer` | Replace C# checks with analyzer or test architecture rules. |
| `src/tools/dotnet/check-data-class-annotations.sh` | Greps `*Data.cs` files for annotations/attributes. | Yes | `replace-with-roslyn-analyzer` | Replace with analyzer rule on symbols/attributes. |
| `src/tools/dotnet/check-domain-events-compliance.sh` | Greps event files for event type, interfaces, metadata, and type mapping. | Yes | `replace-with-roslyn-analyzer` | Replace with analyzer rules for event shape and forbidden legacy interfaces. |
| `src/tools/dotnet/check-framework-api-compliance.sh` | Greps source for framework API usage and naming patterns. | Yes | `replace-with-roslyn-analyzer` | Replace with analyzer for forbidden/required API usage. |
| `.ai/scripts/check-repository-compliance.sh` | Removed; formerly auto-generated grep checks. | No | `replaced-by-DBA1001` | Semantic analyzer coverage is authoritative. |
| `.ai/scripts/check-usecase-compliance.sh` | Former auto-generated grep checks from use case standards. | Yes | `replaced-with-roslyn-analyzer` | Replaced by `DBA1002` and `DBA1010`-`DBA1012`, then removed in validator phase 3. |
| `.ai/scripts/check-aggregate-compliance.sh` | Former auto-generated grep checks from aggregate standards. | Yes | `replaced-with-roslyn-analyzer` | Replaced by `DBA1003` and `DBA1009`, then removed in validator phase 3. |
| `.ai/scripts/check-controller-compliance.sh` | Auto-generated grep checks from controller standards. | Yes | `replaced-with-roslyn-analyzer` | Replaced by `DBA1004`-`DBA1006` and removed in validator phase 2. |
| `.ai/scripts/check-mapper-compliance.sh` | Former auto-generated grep checks from mapper standards. | Yes | `replaced-with-roslyn-analyzer` | Replaced by `DBA1007`-`DBA1008` and removed in validator phase 3. |
| `.ai/scripts/check-projection-compliance.sh` | Former auto-generated grep checks from projection standards. | Yes | `replaced-with-analyzer-and-tests` | Replaced by `DBA1013`, configuration tests, and explicit AI review ownership, then removed in validator phase 3. |
| `.ai/scripts/check-archive-compliance.sh` | Auto-generated grep checks from archive standards. | Yes | `replace-with-roslyn-analyzer` | Later analyzer candidate if archive rules remain part of dotnet-backend profile. |
| `src/tools/dotnet/check-test-compliance.sh` | Auto-generated grep checks from test standards. | Yes | `replace-with-roslyn-analyzer` | Replace with analyzer, `.editorconfig`, or test architecture rules depending on rule. |
| `.ai/scripts/generate-check-scripts-from-md.sh` | Generates grep-based shell checks from markdown coding standards. | Produces C# text checks | `retire-generated-regex-check` | Retire after analyzer/test mapping is stable. It should not remain the formal validation generator. |
| `.ai/scripts/parse-md-rules.py` | Parser used by the markdown-to-shell generator. | Produces C# text checks | `retire-generated-regex-check` | Retire with the generator. |
| `.ai/scripts/MD-SCRIPT-GENERATION-GUIDE.md` | Documents markdown-to-shell generation. | N/A | `retire-generated-regex-check` | Replace with analyzer authoring guidance or archive as historical artifact. |
| `.ai/scripts/README.md` | Documents current scripts as active `.NET` workflow checks. | N/A | `needs-update` | Update to mark transitional status and new validation direction. |

## Generated Directory

Files under `.ai/scripts/generated/` are generated grep-based C# checks:

- `check-archive.sh`
- `check-controller.sh`
- `check-test.sh`

Transition class: `retire-generated-regex-check`.

Recommendation: do not treat these as future validation assets. Retire them once analyzer/test coverage exists for the corresponding rule family.

## Priority Groups

### First Batch

- repository rules
- use case rules
- domain entity / aggregate rules

### Second Batch

- controller boundary rules
- mapper boundary rules
- domain event shape rules
- test DI / test framework rules

### Tool/Test Batch

- Dockerfile and csproj copy sync
- spec file to implementation existence checks
- profile startup
- dual profile config
- mutation testing runner

### AI Context Governance Batch

- prompt portability
- coding standards doc consistency
- future context lint rules

## Important Boundary

Do not remove software engineering reasoning context from `.ai`, `.dev`, or skills. Analyzer coverage only replaces executable C# validation. It does not replace AI design reasoning used by `bdd-gwt-test-designer`, `code-reviewer`, `ddd-ca-hex-architect`, or related skills.
