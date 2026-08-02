# Python Runtime Fallback And Entrypoint Ownership Assessment

## Evidence Metadata

- `generated_by`: `OpenAI Codex repository-native and host-local assessment`
- `generated_at`: `2026-08-02T12:03:33+08:00`
- `source_revision`: `d27fb8adbaf890f9f926c2de6bf66aa6917a83d0`
- `source_branch`: `codex/2026-08-02-python-prerequisite-diagnostics`
- `issue`: `https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/69`
- `baseline_finding`: `ASM-20260730-001#AIC-004`
- `decision_state`: `D-001 approved as Option A with portable-first sequencing; all fallback and ownership recommendations remain unapproved`

## Evidence Used

- `.ai/scripts/check-all.sh`, `.ai/scripts/README.md`, `.ai/scripts/shell-assets.yaml`, and `requirements.txt` for the current resolver, installation, gate, and shell contracts.
- `.ai/distribution/profiles/dotnet-backend.yaml` and `.ai/distribution/templates/INSTALL.md` for portable/source-only classification and extracted-package commands.
- `.ai/assets/skills/README.MD` and `.ai/scripts/tests/test_skill_script_colocation.py` for the current canonical script-ownership rule and locked compatibility paths.
- Direct host command and executable probes for `python`, `python3`, `python3.14`, `codex`, `claude`, `chatgpt`, and the current Codex bundled runtime metadata.
- Official product documentation for publicly documented installation prerequisites: [Codex CLI npm installation](https://openai.com/index/introducing-upgrades-to-codex/), [ChatGPT Windows application requirements](https://help.openai.com/en/articles/9982051-using-the-chatgpt-windows-app), and [Claude Code setup requirements](https://docs.anthropic.com/en/docs/claude-code/getting-started).

The Codebase Memory MCP index was probed first, but its current graph still omits Python code under hidden `.ai/**` paths. Ownership and behavior conclusions therefore use direct tracked files, manifests, tests, and host probes under `AICTX-EVIDENCE-001`.

## Approved D-001 Boundary And Sequencing

The owner selected Option A: all 25 production `__main__` CLI surfaces are in scope, while 45 direct test CLIs and four import-only modules remain outside the user-facing prerequisite contract.

Implementation must be split into two ordered batches:

1. Portable/downstream batch: the 12 production CLIs projected into downstream packages or retained as portable compatibility paths.
2. Source-only batch: the 13 maintainer, CI, release, provider, evaluation, and source-governance CLIs used only in this repository.

The portable batch must be designed, implemented, and validated before the source-only batch begins. This sequencing does not approve a fallback architecture, automatic installation, provider-runtime discovery, OS-native launcher, or ownership move.

## Corrected Host Observation

The earlier statement that the host had no installed Python runtime was too broad. The precise observed state is:

| Probe | Observed result | Design implication |
| --- | --- | --- |
| `python` | Resolves to an unprovisioned Windows App Execution Alias and cannot start Python. | The current generic command candidate is unusable. |
| `python3` | Resolves to an unprovisioned Windows App Execution Alias and cannot start Python. | The current fallback candidate is also unusable. |
| `python3.14` | Resolves to `<user-home>\.local\bin\python3.14.exe`, starts Python 3.14.1, and reports a uv-managed `sys.prefix`. | A usable versioned interpreter is already discoverable on `PATH`, but `check-all.sh` does not probe versioned command names. |
| `python3.14 -c "import yaml"` | Fails with `ModuleNotFoundError`. | Interpreter discovery and dependency readiness are separate gates. |
| Current Codex bundled Python | Private current-host path reports Python 3.12.13; PyYAML is absent until separately installed. | A tool bundle may rescue interpreter startup but does not guarantee repository dependencies. |
| `codex` / `claude` / `chatgpt` | Codex and Claude commands are installed; no `chatgpt` command is registered. | Agent-product presence is host-specific and does not prove a reusable Python-runtime contract. |

The uv-managed `python3.14.exe` happens to be stored beside other executables under `.local/bin`; directory adjacency is not ownership evidence. The Codex bundled runtime is confirmed only for this installation and bundle version. The reviewed official installation pages do not publish a stable, cross-product Python executable path or promise that PyYAML is installed. Treating provider-private paths as a default repository contract would therefore be an inference, not supported portability evidence.

## Current Repository Fallback Contract

1. `check-all.sh` gives `AI_CONTEXT_PYTHON` first priority.
2. Without an override, it probes only `python` and `python3` and requires Python 3.11 or newer.
3. If no candidate passes the version probe, the aggregate gate fails before running validators.
4. Dependencies are installed manually into an owner-selected environment using `python -m pip install -r requirements.txt`; repository scripts do not auto-install them.
5. The extracted package repeats the pinned `requirements.txt` and documents a direct Python command.
6. There is no Python-specific PowerShell launcher and no repository contract for discovering Codex, Claude Code, ChatGPT Desktop, uv, or another tool's private runtime.
7. `check-all.sh` is the only current non-Python prerequisite resolver. Direct Python entrypoints bypass it.

## Fallback Option Assessment

| Approach | Missing interpreter | Missing PyYAML | Mutation / trust impact | Assessment |
| --- | --- | --- | --- | --- |
| Fail closed without execution | Detectable only through a non-Python launcher | Yes, after Python starts | No mutation; deterministic and offline-safe | Required terminal behavior after all approved recovery candidates fail. |
| Explicit `AI_CONTEXT_PYTHON` override | Yes, when the owner supplies a path | Only if the selected environment is ready | No automatic mutation; owner controls trust | Keep as the highest-priority supported source. |
| Probe generic and versioned commands | Often; this host would find `python3.14` | No | Read-only probes; deterministic order is required | Recommended default discovery expansion. |
| Discover agent-tool bundled runtimes | Sometimes | Not guaranteed; current Codex bundle lacks PyYAML | Private paths, update drift, sandbox/permission boundaries, unclear cross-provider contract | Consider only through explicit opt-in provider adapters or owner-provided paths; do not hard-code as the default. |
| Explicit isolated dependency bootstrap | Requires an existing interpreter | Yes | Network and filesystem mutation; can be bounded to a dedicated environment and explicit command | Feasible as a later opt-in recovery mode, not an implicit validator side effect. |
| Silent dependency or Python installation | Potentially | Potentially | Network, supply-chain, privilege, environment ownership, cleanup, CI, and reproducibility risks | Not recommended as default behavior. |
| OS-native launcher delegating to Python | Yes | Yes, by probing before delegation | Adds PowerShell/POSIX maintenance but keeps validator semantics in Python | Recommended architecture candidate for a supported human-facing command. |
| Full OS-native reimplementation of validators | Yes | Avoids Python | Duplicates 25 behavior contracts and creates semantic drift across operating systems | Reject unless Python itself is intentionally removed as a project dependency. |
| Ask an installed AI agent to execute the script | Agent may locate a runtime | Agent may install or provision with approval | Non-deterministic availability and authorization; not usable by CI or non-agent users | Useful assistance, but not a validator prerequisite contract. |

## Unapproved Layered Architecture Candidate

A bounded design candidate is:

1. An OS-native launcher performs only discovery and prerequisite diagnostics.
2. Discovery checks an explicit owner override, stable host commands, then approved optional adapters in a deterministic order.
3. Every candidate is probed for executable identity, Python 3.11+, and required imports before selection.
4. If no ready candidate exists, execution fails closed before validator imports or target mutation.
5. Any environment creation or dependency installation requires a separate explicit operation and must not modify an agent product's managed runtime.
6. The selected Python interpreter executes one canonical Python implementation; PowerShell and POSIX launchers do not duplicate validator semantics.

This candidate is evidence for discussion only. D-002 and D-004 remain pending.

## Current Script Ownership Rule

The canonical registry currently requires exactly one owning skill for behavior that belongs to one skill. Multi-skill, provider, release, package, workflow, and source-repository-wide automation remains under `.ai/scripts/`. Published legacy paths may remain there only as thin compatibility entrypoints.

The colocation contract already enforces two canonical skill-owned production scripts and the root compatibility path for the orchestrator acceptance validator. Changing this rule or moving paths affects skill specs, package projection, compatibility commands, tests, documentation, and possibly downstream users.

## Preliminary Ownership Classification For The 25 CLIs

| Entrypoint | Distribution | Preliminary canonical ownership | Reason |
| --- | --- | --- | --- |
| `.ai/assets/skills/software-development-orchestrator/scripts/validate-software-development-orchestrator-acceptance.py` | portable | Keep skill-owned | Exactly one canonical skill owns the acceptance behavior. |
| `.ai/scripts/plan-ai-context-package-apply.py` | portable | Keep repo-common | Package apply is consumed by initialization and upgrade lifecycles and crosses skill ownership. |
| `.ai/scripts/validate-ai-context-target.py` | portable | Keep repo-common | Target provenance/customization validation is shared by init, upgrade, governance, and audit lifecycles. |
| `.ai/scripts/validate-ai-context.py` | portable | Keep repo-common | Repository-wide navigation, wrapper, language, registry, and routing contracts cross many skills. |
| `.ai/scripts/validate-assessment-artifacts.py` | portable | Keep repo-common | Assessment production and remediation/verification coordination have different owners. |
| `.ai/scripts/validate-dependency-versions.py` | portable | Keep repo-common | Enforces repository, CI, package, Python, and .NET dependency contracts. |
| `.ai/scripts/validate-file-disposition-manifest.py` | portable | Keep repo-common | Disposition evidence is shared across remediation, release, and downstream migration. |
| `.ai/scripts/validate-git-commits.py` | portable | Keep repo-common | Git policy applies to every workflow and skill. |
| `.ai/scripts/validate-shell-assets.py` | portable | Keep repo-common | Validates repository-wide shell orchestration and compatibility assets. |
| `.ai/scripts/validate-software-development-orchestrator-acceptance.py` | portable | Keep thin compatibility path | Canonical behavior remains skill-owned; this published root route only delegates. |
| `.ai/scripts/validate-workflow-artifacts.py` | portable | Keep repo-common | Workflow metadata and task contracts are shared across workflow-owning skills. |
| `.ai/scripts/validate-workflow-handoff.py` | portable | Keep repo-common | Cross-runtime, cross-model, and cross-skill handoff is repository-wide. |
| `.ai/assets/skills/ai-context-upgrader/scripts/compare-ai-context-versions.py` | source-only | Keep skill-owned | The comparison is a single-owner upgrader capability and is already contract-tested in place. |
| `.ai/scripts/build-ai-context-package.py` | source-only | Keep repo-common | Source release/package production crosses skill and distribution ownership. |
| `.ai/scripts/measure-ai-context-load.py` | source-only | Keep repo-common | Measures source-wide runtime, routing, release, handoff, and development traces. |
| `.ai/scripts/plan-github-backlog-migration.py` | source-only | Keep repo-common | Provider migration crosses workflow and backlog ownership rather than one skill. |
| `.ai/scripts/prepare-ai-context-release.py` | source-only | Keep repo-common | Coordinates release state, gates, Git state, and owner handoff. |
| `.ai/scripts/render-ai-context-release-notes.py` | source-only | Keep repo-common | Release rendering consumes repository-wide release/package truth. |
| `.ai/scripts/validate-ai-behavior-evaluation.py` | source-only | Keep repo-common | Deterministic evaluation spans capability and release contracts. |
| `.ai/scripts/validate-ai-context-package.py` | source-only | Keep repo-common | Package-envelope validation is a distribution-wide contract. |
| `.ai/scripts/validate-ai-context-release-state.py` | source-only | Keep repo-common | Release-state gates span repository, Git, package, and hosted evidence. |
| `.ai/scripts/validate-ai-context-versions.py` | source-only | Keep repo-common | Source release registry validation delegates shared target validation and crosses lifecycle owners. |
| `.ai/scripts/validate-repository-config-contract.py` | source-only | Keep repo-common | Repository configuration ownership is source-wide. |
| `.ai/scripts/validate-skill-transition.py` | source-only | Keep repo-common | Transition compatibility necessarily spans multiple skills. |
| `.ai/scripts/validate-source-governance.py` | source-only | Keep repo-common | Discovers and enforces source-wide governance registries and checks. |

Preliminary count by physical entrypoint: two canonical skill-owned scripts, one repo-level thin compatibility route to a skill-owned script, and 22 repo-common scripts.

## Ownership Hotspots

- The shared prerequisite resolver/bootstrap itself serves both skill-owned and repo-common CLIs, so the current ownership rule points to a repo-common component under `.ai/scripts/`, projected into downstream packages where needed.
- A skill-owned CLI should depend on the shared prerequisite component without transferring its domain behavior to the repository-common layer.
- The existing root orchestrator acceptance wrapper should stay thin; adding prerequisite domain logic directly to the wrapper would create two behavioral owners.
- Moving any of the 22 preliminary repo-common scripts into one skill would require evidence that the other consuming lifecycles are only adapters, not co-owners.
- Moving the two canonical skill scripts back to `.ai/scripts/` would require changing the canonical ownership policy and its deterministic colocation test, not merely relocating files.

## Pending Owner Decisions

1. `D-002A`: default action when no fully ready interpreter/dependency environment is found.
2. `D-002B`: trusted discovery sources and deterministic candidate order, including whether provider-specific adapters are allowed.
3. `D-002C`: supported OS-native launcher coverage and invocation contract.
4. `D-004`: dependency recovery command and whether an explicit isolated bootstrap mode is offered.
5. `D-006`: final canonical ownership classification, shared prerequisite-component placement, package projection, and compatibility routes.

No recommendation in this assessment authorizes implementation or automatic environment mutation.
