# Python Runtime Selection History And OS-Native Alternatives

## Evidence Metadata

- `generated_by`: `OpenAI Codex repository and Git-history assessment`
- `generated_at`: `2026-08-02T12:39:54+08:00`
- `source_revision`: `d5ae808626508cba857ea412ae1d543fa86095e6`
- `source_branch`: `codex/2026-08-02-python-prerequisite-diagnostics`
- `issue`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69`
- `baseline_finding`: `ASM-20260730-001#AIC-004`
- `evidence_rule`: repository facts and engineering inferences are separated below; inferred intent is not treated as historical project truth

## Bottom Line

The repository does not contain a current ADR or other comparison-backed decision that selected Python as the canonical validator runtime. Git history shows an incremental adoption path instead of a single runtime-selection event:

1. Python first entered the tracked history as one Markdown parser inside a much larger imported tooling set.
2. Repository-governance validators were later added in Python, initially using only the standard library.
3. PyYAML was introduced when validators began parsing nested YAML contracts rather than flat locator fields.
4. Packaging and governance automation then accumulated around the existing Python path.
5. Clean-environment reviews subsequently added dependency declarations and interpreter discovery after portability failures were found.

Therefore, the defensible historical conclusion is **emergent path dependence**, not “the repository evaluated its runtime options and approved Python.” Python may still be a reasonable implementation choice, but the repository has not yet recorded that justification.

## Git-Backed Timeline

| Date | Commit | Observed fact | What it does and does not prove |
| --- | --- | --- | --- |
| 2026-04-13 | `92b02d59e01cbb9759b38b4ef5346b85b6fc1c10` (`temp`) | The first tracked `*.py` file was `.ai/scripts/parse-md-rules.py`, added with a Bash generator and a large imported repository-context set. The generator explicitly checked for `python3`. | Proves Python was already embedded in the imported toolchain. The commit message contains no runtime comparison or selection rationale. |
| 2026-04-13 historical tree | historical `ADR-052-script-generation-from-markdown-documentation.md` | The ADR selected Markdown-to-shell generation and listed “a Python environment is required for the parser” as a neutral consequence. | Acknowledges the prerequisite, but does not explain why Python was chosen over Bash, PowerShell, .NET, or another runtime. This ADR is not present in the current ADR set. |
| 2026-07-10 | `aa69c79d56179c31be8899684209525e310307f1` | `.ai/scripts/validate-workflow-artifacts.py` was introduced in Python. Its first version used a small standard-library flat-YAML parser and no PyYAML import. | Shows Python was selected for new governance code before the external YAML dependency was necessary. The workflow task and commit explain the validation need, not the language choice. |
| 2026-07-11 | `7f75c77d5f24d8b08e14a12a5bb6ba856e68f420` | `validate-ai-context.py` added `import yaml` to validate a structured rule-ownership registry. | Shows why a real YAML parser became useful, but does not record why PyYAML/Python was preferred over alternative toolchains. |
| 2026-07-12 | `7d846f1f5c19bdb9141a5efad13478d00b33a313` | `validate-workflow-artifacts.py` replaced part of its flat parsing with `yaml.safe_load` as backlog and workflow schemas became nested. | Demonstrates the technical pressure that spread PyYAML: structured mappings, lists, types, and parse errors exceeded the original flat parser. |
| 2026-07-15 | `2ac316cec5fd4257125572699352f73edee9112d` and `ab318f73a1758dbf5b4e01d2a9341eac8425d981` | Deterministic package building and safe package application were implemented in Python, using filesystem, Git, archive, hash, temporary-directory, JSON, and YAML behavior. | Shows the existing Python base made additional automation cheap and cohesive. It is still not a runtime-selection record. |
| 2026-07-15 | `1a25eb023e69d85c32a7459e7a9dc749e30e5d26` | An independent review found that the shipped planner required PyYAML but clean targets had neither a governed dependency declaration nor an actionable error. The package requirement was then pinned. | Proves prerequisite experience was repaired after implementation, rather than designed before Python/PyYAML became a downstream contract. |
| 2026-07-19 | `e76d89ca7927152cd993af7d53c3f0eb8a322384` | Root `requirements.txt`, Python 3.11+ discovery, and source bootstrap documentation were added because existing gates were not portable on clean environments. | Confirms the same reactive pattern at repository scope. |

The later AI-assisted packaging commits explicitly carry `Co-Authored-By: OpenAI Codex (GPT-5)`. Earlier commits do not provide model attribution precise enough to identify which AI, if any, made each individual language choice. The history supports “AI-assisted incremental selection” more strongly than a deliberate owner-approved runtime decision, but it does not support attributing every early choice to one named model.

## Why An AI Agent Would Commonly Choose Python

The following points are engineering inferences, not recorded historical intent:

- The validation domain is mostly repository files, Markdown, YAML, JSON, TOML, Git subprocesses, hashes, archives, and temporary directories. Python has concise, mature libraries for these tasks.
- One Python implementation can run on Windows, macOS, and Linux, avoiding separate Bash and PowerShell implementations for validator semantics.
- Python's standard library makes deterministic subprocess fixtures and disposable Git-repository tests straightforward.
- A source script is easy for an agent to add and patch without introducing a compile, publish, runtime-identifier, or binary-release pipeline.
- Once the first validators existed in Python, reusing their modules and test patterns reduced the local cost of each next validator.
- PyYAML is a familiar direct solution for complete YAML parsing, while the repository's initial hand-written flat parser could not safely represent nested mappings, lists, nulls, booleans, or general YAML parse failures.

Those incentives optimize implementation speed and one-codebase portability. They do **not** automatically optimize first-use experience for a human team. The accumulated cost was transferred to every user as a Python 3.11+ and PyYAML bootstrap requirement. The repository currently documents that cost, but does not justify it against alternatives.

## Why The Team Question Is Material

“Install Python and PyYAML before using the AI-context validators” is not merely an internal implementation detail once the scripts are packaged for downstream use. It affects:

- onboarding time and administrator approval;
- corporate supply-chain and package-source policy;
- offline or restricted machines;
- CI base images and cache ownership;
- Windows command discovery and App Execution Alias behavior;
- responsibility for virtual-environment creation, upgrades, and cleanup;
- whether users regard this framework as native to a .NET backend repository.

The present honest answer to a team member is: “the tooling grew around Python because it was convenient for cross-platform structured-file automation, and PyYAML is used for the repository's YAML contracts; a formal comparison-backed runtime decision was never recorded.” That explains the history, but it is not yet a satisfactory product-level justification.

## What “OS Native” Means In Practice

There is no single OS-native scripting language across the supported desktop and CI environments.

| Choice | Advantage | Material problems for this repository |
| --- | --- | --- |
| Bash | Already fits Linux/macOS and the repository's current shell orchestration. Excellent as a thin command launcher. | Windows needs Git Bash, WSL, or another POSIX layer; Bash has no built-in YAML parser; quoting, path conversion, subprocess status, arrays, Unicode, and command availability differ by host. |
| Windows PowerShell 5.1 | Preinstalled on supported Windows systems and suitable for interpreter discovery and actionable diagnostics. | Not native on macOS/Linux; its behavior differs from PowerShell 7; no built-in YAML parser; TOML and archive behavior are less uniform; a full validator port would require a second test matrix. |
| PowerShell 7 (`pwsh`) | More consistent and cross-platform than Windows PowerShell. | It is itself an additional installation on many systems, so it replaces rather than removes a prerequisite. YAML still normally requires a module or custom parser. |
| `cmd.exe` batch | Available on Windows with no extra installation. | Poor fit for nested YAML/JSON/TOML, Unicode, robust error handling, reusable modules, and deterministic test fixtures; Windows-only. |
| Separate Bash and PowerShell implementations | Can start on common POSIX and Windows hosts without Python and can produce native prerequisite guidance. | Duplicates behavior and tests. Reimplementing 25 CLIs creates two semantic authorities and a high drift risk. Both still lack a complete native YAML parser. |
| Thin Bash and PowerShell launchers delegating to one implementation | Solves the “Python cannot start to explain missing Python” boundary and keeps platform-specific discovery small. | Does not remove the canonical runtime or PyYAML prerequisite; it only makes discovery and failure understandable. |
| .NET tool or framework-dependent CLI | Matches the repository's .NET audience, offers structured libraries and one semantic implementation. | Requires a compatible .NET runtime/SDK and a restore/install step; converting all current validators is a material product change. |
| Self-contained .NET, Go, or Rust binaries | Can remove end-user language/runtime installation for supported targets. | Requires build, platform/architecture matrices, artifact integrity, release distribution, update, signing/trust, and source-versus-binary provenance governance. |

## Practical Boundary Recommendation

For Issue #69 alone, OS-native scripts are best suited to a **thin launcher layer**:

1. perform read-only interpreter and dependency discovery;
2. print the stable prerequisite diagnostic when Python cannot start;
3. never install or mutate the environment implicitly;
4. delegate validator semantics to one canonical implementation when a ready environment exists.

Using OS-native syntax for all validator semantics is possible, but it is not a diagnostic-only change. It would be a runtime migration requiring a separate comparison-backed architecture decision, replacement sequencing, compatibility policy, and duplicated or rebuilt tests.

Because the owner raised real downstream onboarding friction, retaining Python should no longer be an unexamined assumption. Before implementation, the workflow must decide whether to:

- retain Python and treat Issue #69 as diagnostic/launcher remediation;
- select a different canonical runtime and expand this workflow accordingly; or
- complete bounded diagnostics now and open a separately governed runtime-migration proposal with explicit ownership.

## Translation Routing Deviation

The two existing owner-review translations in this workflow were produced by the primary `gpt-5.6-sol` agent instead of the promoted low-cost `context-translator` route.

Repository evidence is explicit:

- `.ai/SUB-AGENT-SYSTEM.MD` routes a derived Traditional Chinese translation after English finalization to `context-translator` under the owning main workflow.
- `.ai/assets/sub-agent-role-prompts/context-translator/sub-agent.yaml` requires a caller-verified low-cost runtime.
- `.codex/agents/context-translator.toml` selects `gpt-5.6-terra` with `model_reasoning_effort = "low"`.

There was no unavailable-runtime or quality-based reason to bypass this route. The primary agent read the language policy and governance references but failed to consult and apply the active sub-agent routing document before translating. This was a routing/discovery error, not a defensible design decision.

Structural and semantic parity checks passed for the two translation pairs, so the deviation does not by itself prove their content is incorrect. It does mean the requested cost-routing process was not followed. Any correction must give `context-translator` exactly one finalized English source and one output path per invocation, then leave final parity validation and commits to the main agent.

## Pending Decisions Introduced By This Assessment

- `D-009`: canonical validator runtime disposition—retain Python for Issue #69, migrate runtime in this workflow, or create a separately governed migration proposal.
- `D-TR-001`: whether to have the low-cost `context-translator` replace/revalidate the two existing zh-TW evidence files before continuing the design discussion.

No production script, dependency, or runtime behavior was changed by this assessment.
