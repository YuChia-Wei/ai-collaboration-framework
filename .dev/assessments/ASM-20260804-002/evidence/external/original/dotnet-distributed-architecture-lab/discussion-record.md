# AI Context And Architecture Kit Standards Discussion Record

## Record Metadata

- `workflow_id`: `2026-07-30-ai-context-architecture-kit-standards-discussion`
- `owner_skill`: `ai-context-governance`
- `status`: `in_progress`
- `created_at`: `2026-07-30T23:54:50+08:00`
- `updated_at`: `2026-08-02T20:22:21+08:00`
- `decision_owner`: repository maintainer
- `purpose`: preserve the owner-led discussion and its reasoning until the owner decides whether to create upstream issues or merge this record to `main`.

## Discussion Objective And Scope Alignment

The primary objective is to produce owner-approved, issue-ready feedback for `ai-collaboration-prompts-dotnet-backend` about how AI Context should own software-engineering semantics, technology profiles, concrete implementation constraints, target customization, executable validation bindings, and the transition from bundled .NET tools to Architecture Kit. This downstream repository supplies implementation and upgrade evidence for that design.

The durable record preserves the reasoning needed to write that issue without depending on hidden conversation context. The intended outputs are the upstream issue body, Architecture Kit companion requirements, a target-adoption model, and an implementation and verification checklist.

This discussion does not itself modify canonical AI Context, implement or package Architecture Kit, adopt an external testing project, or refactor product code. External skills and sub-agent routing are relevant only where they affect the framework's knowledge-loading and execution boundaries; they are not a replacement primary objective.

## Repositories And Evidence Inspected

### Target Repository

- Repository: `dotnet-distributed-architecture-lab`.
- Current baseline when this discussion was persisted: `main@a06ba3a6de9cfcb3ee0c4d1de3bb8a533780129e`.
- Historical comparison point: `780dcacda46d45b6dd13d64484062f9ccbf49b7a`, dated 2026-04-23, the last observed late-April commit before the AI Context v0.6.0-era restructuring.
- The historical repository combined normative documents, prompts, grep-oriented shell checks, reusable Building Blocks, and product implementation. Its `check-all.sh` orchestrated many textual checks and retained unsupported or Java-derived checks.
- The current repository separates reusable context, project truth, runtime wrappers, analyzer/tooling code, and semantic customization records more explicitly.

### AI Context Source Repository

- Repository: `ai-collaboration-prompts-dotnet-backend`.
- Initial observed source state during the discussion: local `main` at `98e90bb4649961b1c09105346f7376b197b126a8`; latest published tag observed as `v0.7.0`; v0.8.0 work was still focused on repository resource governance.
- Refreshed source state on 2026-08-02: local `codex/2026-08-02-python-prerequisite-diagnostics` at `c2b35adf4bdb00ca4536ff8e2062dc5d2c3e93ff`; latest observed published tag remained `v0.7.0`.
- Sub-agent reachability verification later on 2026-08-02 inspected the same source branch at `1a668976ed448861da1740030a519bc24b5d9fed`. Its source profile still uses dynamic canonical loading for most roles and ships the promoted Codex `context-translator` adapter as framework-managed `.codex/agents/**` content.
- Issue-draft preparation later on 2026-08-02 inspected the same active source branch at `8c3fb8d722fbc4cbdd576718fb85265d857935a6`. The rule registry remained flat, the customization subject schema remained `capability | rule | contract`, `tools/**` remained framework-managed and non-packable, and no Architecture Kit binding was present.
- Current requirements already distinguish standard analyzers and formatters from custom deterministic architecture analyzers, and state that mapping completeness or event-history completeness may require tests or review rather than syntax guessing.
- The .NET distribution profile still installs `tools/**` as framework-managed content. The Analyzer README explicitly describes source-included usage and says not to package it as NuGet until the rules and skill integration stabilize; the Analyzer and validation projects remain non-packable.

### Architecture Kit Repository

- Repository: `dotnet-architecture-kit`.
- Observed branch and commit: `proj-temp@da45952d4962e4e0f11b046d09022847519657d9`.
- No repository tag was observed. The repository remains in initial extraction and NuGet product-planning state; package names, boundaries, public API, versioning, diagnostic compatibility, and publication contracts are intentionally not finalized.
- Root build configuration and the Analyzer project both set `IsPackable` to `false`.
- Planning material proposed that Architecture Kit become the canonical implementation source while AI Context retains engineering guidance, analyzer usage guidance, and compatible-version references.

## Confirmed Decisions

### DEC-001 — Responsibility Boundary

- AI Context owns cross-language software-engineering concepts, design direction, and default practices.
- AI Context must also state concrete externally observable constraints when those constraints affect compliant implementation.
- Architecture Kit owns the .NET implementation of deterministic checks; it must not become an independent semantic owner of software-engineering rules.
- A target repository decides how strongly it relies on AI guidance and executable enforcement according to its selected technology profile and installed tooling.

### DEC-002 — Target Customization Is Allowed But Must Be Traceable

- Software-engineering and architecture defaults may be replaced or adjusted by a target team with explicit evidence such as an ADR.
- The non-silent governance contract is the durable baseline: target decisions, agent guidance, analyzer configuration, and actual implementation must remain consistent and traceable.
- The framework should avoid treating architecture preferences such as DDD, CQRS, GWT, or a specific encapsulation technique as universally non-overridable merely to simplify enforcement.

### DEC-003 — Installation And Adoption Review

- Architecture Kit may bootstrap a project with the recommended AI Context .NET defaults enabled.
- The team should perform a rule-control or adoption review and pin the resulting target policy.
- Installing or upgrading a NuGet package must not silently redefine the project's adopted engineering policy.

### DEC-004 — New Rules Require Team Confirmation

- Newly introduced engineering rules must wait for team review before joining the target's adopted policy.
- The existence of an analyzer implementation is a validation capability; it is not by itself evidence that the target adopted the rule.
- Team members may accept or reject rules in bulk, but the explicit confirmation stage must exist.

### DEC-005 — Review Engineering Semantics, Not Every Diagnostic

- The primary review unit is the engineering rule that the team agrees or disagrees with.
- A team does not need mandatory ceremony for every Roslyn diagnostic that implements an already understood rule.
- Diagnostic-level concerns such as false positives, excessive strictness, or unsuitable severity may be raised and recorded when material.

### DEC-006 — Concrete Constraints Must Be Available Before Generation

- AI Context must not stop at a high-level statement such as "an aggregate encapsulates state" when the enforcement profile expects concrete constraints such as no public setter or no exposed mutable collection.
- The agent-facing projection must make the applicable concrete constraints available before code generation to prevent predictable analyzer failures and unnecessary AI-credit consumption.
- Analyzer internals such as Roslyn traversal algorithms do not belong in AI Context; externally observable compliance semantics do.

### DEC-007 — Diagnostic Handling Is Evidence-First

- An agent receiving an analyzer diagnostic must first identify the corresponding engineering rule, confirm applicability, inspect target ADR or customization evidence, and determine whether the problem is code, configuration, rule drift, or analyzer behavior.
- The agent should modify code only after this comparison rather than treating every diagnostic as an unconditional rewrite command.

### DEC-008 — .NET Profile Owns Architecture Kit Compatibility

- The .NET technology profile should explicitly declare the compatible Architecture Kit version range.
- This package dependency belongs only to the .NET profile and must not bind universal software-engineering knowledge to .NET analyzer concepts.
- A profile upgrade and Architecture Kit compatibility review are explicit policy events, not incidental effects of package restore.

### DEC-009 — Layered Target Rule Decision Records

- The target repository should have a compact target rule profile that records the currently effective rule-adoption state.
- ADRs remain required decision evidence for material target alternatives or deviations; their target-owned lifecycle already protects them from AI Context installation and upgrade replacement.
- The semantic customization ledger must retain a corresponding traceable relationship when the target profile changes or replaces framework behavior, so future upgrade reconciliation can locate the target intent and its source evidence.
- Installation, upgrade, and reinstallation must preserve the target's confirmed decisions rather than silently resetting them to the incoming framework defaults.

### DEC-010 — Customization Ledger Records Semantic Deltas Only

- The target rule profile is target-owned truth and holds the complete effective rule state.
- `customizations.yaml` records only target semantics that differ from the installed AI Context baseline; it does not mirror unchanged adopted defaults.
- Each semantic-delta entry links the affected rule-profile subject and its ADR or other approved decision evidence so upgrades can trace and reconcile the target intent.
- If installation, upgrade, or reinstallation overwrites the target rule profile without reconciliation, that is an ownership-contract defect rather than a recovery responsibility assigned to the customization ledger.

### DEC-011 — Rules Are Non-Blocking Until Team Review

- Initial AI Context profile defaults enter the target rule profile as `pending-review`; they are not yet target-adopted policy.
- A `pending-review` rule must not block normal builds before the team confirms it.
- Team review transitions each rule, individually or in an approved batch, to an explicit effective disposition such as adopted, deviated, or not applicable.
- New rules introduced by later AI Context profile versions follow the same `pending-review` gate and do not become active policy merely because the context or Architecture Kit package was upgraded.
- This decision refines the bootstrap behavior in `DEC-003`: recommended defaults may be presented immediately, but enforcement remains non-blocking until review.

### DEC-012 — AI Context Governance Does Not Imply Analyzer Activation

- AI Context is collaboration context and documentation; by itself it cannot emit compiler diagnostics, configure IDE warnings, or affect a build.
- `pending-review` is a target governance state. During installation or initialization, the AI should ask the installing user or developer to review the proposed rules and must not present an unconfirmed default as target-owned truth.
- If the review is deferred, AI Context records the unresolved or pending decision and continues only within the permissions of that state; this does not create Analyzer severity.
- Architecture Kit installation, diagnostic defaults, `.editorconfig` projection, and build enforcement are separate .NET-profile concerns that apply only when the corresponding tooling is present and selected.
- This decision supersedes any reading of `DEC-011` that treats `pending-review` as an Analyzer severity. `DEC-011` means the target has not authorized enforcement, not that AI Context itself must produce a non-blocking warning.

### DEC-013 — Installation May Finish With A Pending Continuation Point

- AI Context installation or initialization should ask the installing user or developer about relevant unresolved choices.
- If the user defers a decision, installation may finalize with an explicit `pending-review` continuation checkpoint rather than blocking indefinitely.
- The checkpoint must identify the unresolved subject, the user or owner who should decide, the default behavior while pending, and the exact continuation action.
- Language-specific tooling questions should be asked only when the corresponding technology profile applies; Architecture Kit adoption is a .NET concern rather than a universal installation question.

### DEC-014 — AI Context Defaults Are Active Guidance

- Written AI Context default rules are active agent guidance as soon as the context is installed, unless target-owned evidence such as an ADR and semantic customization changes them.
- New rules delivered by an approved AI Context upgrade become part of the installed baseline guidance; their Analyzer enforcement remains a separate technology-tool decision.
- Standard technology-profile configuration such as `.editorconfig` formatting and code-style defaults may be installed active as part of that selected profile.
- This decision supersedes the semantic-adoption portions of `DEC-004` and `DEC-011`. Those decisions continue only as historical reasoning about enforcement review and target deviations; they no longer delay whether the AI follows installed baseline guidance.
- This decision also refines `DEC-012`: pending review applies to unresolved optional integration or customization choices, not to the existence of installed baseline guidance.

### DEC-015 — Architecture Kit Is Preferred But Explicitly Opt-In

- The .NET profile should recommend Architecture Kit as the preferred deterministic enforcement companion for .NET development.
- Architecture Kit is not mandatory. AI Context installation asks the relevant .NET developer or owner whether to adopt it.
- Before explicit approval, the Architecture Kit NuGet package is not added to the target project; therefore no Architecture Kit diagnostic can execute.
- A deferred decision is preserved as a `pending-review` continuation checkpoint without weakening the active AI Context guidance or standard `.editorconfig` defaults.
- Installing, configuring, upgrading, or removing Architecture Kit remains a target-owned .NET tooling decision with traceable evidence.

### DEC-016 — Architecture Kit Approval Adopts A Complete Versioned Ruleset

- Explicit approval to install an Architecture Kit NuGet version means accepting the complete diagnostic ruleset delivered by that package version rather than selecting diagnostics before installation.
- Package-defined diagnostic enablement and severity form the initial enforcement baseline after installation.
- The target repository may override individual diagnostic severities or disable a diagnostic through target-owned `.editorconfig` configuration.
- Upgrading Architecture Kit is a separate reviewed version-adoption event because a newer package may change the accepted ruleset or its default enforcement behavior.
- This decision resolves the post-approval activation question in favor of package defaults plus explicit `.editorconfig` overrides; it does not yet decide which override reasons require ADR or semantic-customization evidence.

### DEC-017 — Diagnostic Overrides Are Classified By Intent

- The resulting `.editorconfig` severity alone does not determine whether an override is a semantic customization; the reason for the override is authoritative.
- A semantic deviation rejects, replaces, or narrows the engineering meaning adopted from AI Context. It must update the target rule profile and be supported by ADR evidence plus a corresponding semantic-delta entry in `customizations.yaml`.
- Enforcement tuning changes how strongly or visibly an accepted rule is reported without changing the team's engineering position. It is target-owned enforcement configuration and does not require an AI Context semantic-customization entry by default.
- A tooling waiver responds to an Analyzer defect, false positive, unsupported code shape, or similar implementation limitation while retaining the engineering rule. It requires traceable tool-waiver evidence but is not an AI Context semantic customization.
- Identical changes such as setting a diagnostic to `none` may therefore have different governance requirements: disagreement with the rule is a semantic deviation, while temporary suppression for a false positive is a tooling waiver.

### DEC-018 — Tooling Waivers Require Local Evidence And A Review Trigger

- Every Analyzer tooling waiver must identify the affected Diagnostic ID, preserve a project-local explanation of the defect, false positive, unsupported code shape, or other limitation, and define an explicit condition that triggers reconsideration.
- Creating or linking an Architecture Kit issue is optional rather than a prerequisite for a target repository to apply the waiver.
- An upstream issue remains useful when the behavior is reproducible or should be corrected in Architecture Kit, but the target team's ability to record and use a justified waiver must not depend on external issue management.
- A tooling waiver remains distinct from a semantic customization because the team continues to accept the underlying engineering rule.
- The exact standard review triggers and whether a calendar expiry is required remain to be decided.

### DEC-019 — Tooling Waiver Review Is Event-Driven

- A tooling waiver must be reconsidered when the target upgrades Architecture Kit or when the technical design of the affected code changes materially.
- Ordinary edits that do not change the relevant code shape or design do not by themselves trigger review.
- A fixed calendar expiry or periodic review date is not required by the default policy.
- Reconsideration does not automatically remove the waiver. The team reviews the current Analyzer behavior and affected design, then records whether the waiver is retained, revised, or removed.
- If retained after a trigger, the local waiver evidence must be refreshed so it explains why the limitation still applies to the current package version or code design.

### DEC-020 — Drift Detection Uses Structural And Semantic Layers

- Architecture Kit owns deterministic structural drift detection when it is installed. Its executable validation surface compares the installed package's Diagnostic catalog, package defaults, target `.editorconfig` overrides, target rule-profile entries, and required evidence references.
- Architecture Kit verifies facts such as valid Diagnostic IDs, non-default overrides having a classified target record, and referenced evidence being present. It must not infer whether the team's engineering rationale is semantically correct.
- AI Context installation, upgrade, and explicit review workflows own semantic classification and reconciliation. They determine whether an override is a semantic deviation, enforcement tuning, or tooling waiver and whether the corresponding ADR, customization, or waiver evidence is appropriate.
- AI Context must not replace deterministic structural validation with prose or ad hoc text matching when the Architecture Kit validation capability is installed and available.
- Architecture Kit must report structural drift without silently rewriting `.editorconfig`, the target rule profile, ADRs, or `customizations.yaml`; target-owned intent remains subject to explicit reconciliation.

### DEC-021 — Native Development Behavior And CI Consistency Checks Stay Separate

- Editing `.editorconfig` takes effect through normal .NET, Roslyn, IDE, and build behavior. AI Context and Architecture Kit do not add an immediate governance check merely because that file changed.
- Human developers and AI agents are both legitimate authors. A deliberate `.editorconfig` edit must not be treated as suspicious or expanded into an automatic semantic-reconciliation task that consumes AI tokens.
- Architecture Kit structural consistency validation is intended for an explicit final CI stage that compares effective context and configuration after development changes have accumulated.
- The framework default for a context-versus-configuration mismatch is a non-blocking CI warning or reminder. It does not add a new build error or enlarge the runtime effect of the individual `.editorconfig` edit.
- Native Analyzer behavior remains independent: if the target itself configures a Diagnostic as an error, Roslyn may fail the build for that Diagnostic. That result is not the governance-consistency warning described here.
- AI Context performs semantic reconciliation when installation, upgrade, explicit review, or a CI consistency warning calls for it; it does not continuously inspect every configuration edit.
- A target team may adopt stricter CI policy through its own decision, but neither AI Context nor Architecture Kit makes that stricter behavior the cross-project default.

### DEC-022 — The Rule Model Uses Fully Separated Semantic Entities

- The AI Context rule schema will model engineering concepts, normative rules, concrete observable constraints, and enforcement capabilities as separately identified entities rather than embedding all detail in one rule document.
- Relationships among those entities must be explicit and reference stable identities so a concept can support multiple rules, a rule can produce multiple constraints, and a constraint can have multiple enforcement capabilities or technology bindings.
- This choice intentionally accepts greater schema and maintenance complexity in exchange for precise traceability, independent evolution, and clearer cross-language reuse.
- Canonical normalization does not mean every entity is injected into every AI prompt. A compact applicable projection is required so the richer source model does not increase routine token usage unnecessarily.
- Two schema sub-decisions remain open: the boundary between abstract enforcement capability and technology-specific implementation binding, and the projection and customization identity used by a consuming target.

### DEC-023 — Enforcement Uses Core Abstractions And Technology Bindings

- AI Context core knowledge owns technology-independent engineering concepts, rules, constraints, and abstract enforcement capabilities such as static analysis, executable tests, or human review.
- Technology profiles act as implementation-facing adapters or infrastructure. They bind stable core constraint and capability identities to technology constructs, tools, package versions, Diagnostic IDs, and configuration surfaces.
- `.editorconfig` belongs to the technology implementation and configuration layer. It controls effective tool behavior but does not independently own the engineering meaning or the reason for a target semantic deviation.
- Architecture Kit is a concrete .NET implementation mechanism behind the .NET profile's bindings; universal AI Context knowledge must not depend on Architecture Kit, Roslyn, or `.editorconfig` concepts.
- The dependency direction follows Clean Architecture and the Dependency Inversion Principle: technology bindings depend inward on stable core identities, while the core does not depend outward on any technology profile.
- The separation also supports Single Responsibility by isolating engineering meaning, collaboration workflow, and technology enforcement; Open/Closed behavior by allowing new technology profiles and bindings without rewriting stable core semantics; and Interface Segregation through compact task-relevant projections.
- This is an architectural analogy and dependency rule, not a claim that documentation directories literally form runtime Clean Architecture assemblies.

### DEC-024 — Core Owns Cross-Language Intent And Profiles Own Ecosystem Idioms

- A meaningful engineering intent that applies across languages belongs in AI Context core knowledge; exact syntax, naming, types, framework conventions, and validation bindings belong in the applicable technology profile.
- A technology profile may own a rule directly when no useful cross-language engineering abstraction exists. The framework must not invent an artificial core concept solely to make every technology rule appear universal.
- A profile-owned rule may later be promoted to a core concept or rule only through explicit semantic review and versioned migration after credible cross-technology evidence emerges.
- For asynchronous APIs, core knowledge may define that asynchronous completion and usage semantics must be clear in a public contract. It must not require an `Async` method-name suffix across all languages.
- The `Async` suffix convention is a .NET-profile rule derived from .NET TAP conventions, with its .NET-specific applicability and exceptions. TypeScript, Java, Rust, and other profiles define their own idiomatic representations without inheriting the .NET naming constraint.
- Target customizations compare against the owner of the affected semantic rule: changing the universal asynchronous-contract intent is a core semantic deviation, while changing the .NET `Async` naming convention is a .NET-profile semantic deviation.

### DEC-025 — Artifacts Reference Normalized Entities By Role

- The normalized canonical model may retain stable identities for concept, rule, constraint, abstract enforcement capability, and technology implementation binding, but consuming artifacts do not receive unrestricted references to every entity type.
- The compact target rule profile records the complete effective semantic state by referencing applicable core or technology-profile rule and constraint identities. Concept references may provide context, but rule and constraint identities are the effective decision units.
- ADRs and `customizations.yaml` reference semantic subjects only: concept, rule, or constraint identities. They do not use a Diagnostic ID or tool binding as a substitute for the engineering intent being changed.
- Enforcement-tuning records reference the affected constraint, abstract capability, and technology binding or Diagnostic ID. They do not create semantic-customization entries when the engineering meaning remains unchanged.
- Tooling waivers reference the technology binding or Diagnostic ID and its linked constraint, together with the local rationale and event-driven review evidence defined by `DEC-018` and `DEC-019`.
- Routine AI projections include only the concepts, rules, constraints, and target semantic deltas applicable to the current task and selected profiles. Capability, package, command, and Diagnostic binding details are added only for implementation, validation, upgrade, or diagnostic-handling tasks that need them.
- Structural validation verifies reference integrity across these role boundaries; it does not broaden the semantic authority of `.editorconfig`, package metadata, or a Diagnostic identifier.

### DEC-026 — Technology Profiles Bind Only Credible Mechanical Validation

- An applicable engineering rule remains active AI guidance whether or not its technology profile has a mechanical validation binding.
- Profile authors should first perform evidence-based discovery of language-native compilers, analyzers, linters, formatters, test frameworks, architecture-test tools, or other established mechanisms that can validate the constraint deterministically.
- A profile binds a tool only when the tool and mapping are credible, maintained, versionable, and sufficiently deterministic for the stated constraint. The existence of an arbitrary command or text-search script is not enough.
- When no credible mechanical binding is selected, the profile records an AI-assessed or unbound capability state. The AI implements against the concrete constraint and performs reasoned self-review without claiming that mechanical verification passed.
- A human-review requirement may still be selected by a target team for risk, approval, or accountability reasons, but it is not the universal fallback merely because a mechanical tool is absent.
- AI Context must not require generic `.sh` validation, fabricate language-specific heuristics, or weaken the engineering rule solely because no tool binding is available.
- An unbound state means that the current profile has not selected a trustworthy binding; it does not assert that the wider ecosystem has no possible tool. Later discovery may add a binding through the normal profile and versioning lifecycle.
- The additional Architecture Kit expectations in the .NET profile reflect the owner's chosen .NET quality strategy and the mature native Analyzer ecosystem. They do not create a universal prerequisite for AI-assisted software development in other languages.

### DEC-027 — Tool Compatibility And Rule Mapping Are One-Way

- The .NET technology profile owns the mapping from AI Context constraint and capability identities to Architecture Kit package versions and Diagnostic IDs.
- The profile declares the compatible Architecture Kit NuGet version range. Architecture Kit does not need to reference AI Context rule IDs, understand its schema, or publish a reverse compatibility contract.
- Architecture Kit owns its package versions, Diagnostic IDs, default severities, Analyzer behavior, and ordinary release documentation as an independent tool contract, comparable to other analyzer packages that do not bind themselves to a consuming team's internal rule model.
- AI Context and the target repository bear the accepted upgrade cost: when Architecture Kit changes, the .NET profile or consuming workflow verifies that mapped Diagnostic IDs and expected behavior remain compatible before updating the declared range.
- Lockstep AI Context and Architecture Kit releases are not required. A package upgrade may occur independently, and a profile update occurs only when its supported range or mapping evidence changes.
- No custom two-sided manifest is required merely to make Architecture Kit aware of AI Context. Framework-side or target-side CI consistency checks use the one-way profile mapping plus observable package and configuration behavior.

### DEC-028 — AI Context And Architecture Kit Version Independently

- AI Context core semantic changes and technology-profile rule or mapping changes require an AI Context release.
- Architecture Kit Analyzer implementation, Diagnostic behavior, and package-contract changes require an Architecture Kit package release.
- Adding a Diagnostic for an already-defined constraint does not require an AI Context release unless the .NET profile's binding, supported version range, or exposed constraint changes.
- A feature changes both versions only when it intentionally changes both contracts. The repositories do not share version numbers, release order, or a lockstep release train.
- This version-ownership decision defines the target contract. It does not assert that an external Architecture Kit package is currently ready or authorize removal of AI Context's bundled validation tools.

### DEC-029 — Bundled Tools Remain The Sole Supported Provider Until Cutover

- Before Architecture Kit satisfies the full cutover gate, the AI Context .NET profile supports only its source-included `tools/**` provider for custom mechanical validation.
- AI Context does not publish or route an opt-in Architecture Kit preview binding during this period, and target repositories do not run both providers for the same Diagnostic set.
- Architecture Kit development, package design, and consumer testing may continue independently in its own repository without changing the active AI Context provider contract.
- Moving the .NET profile to Architecture Kit is one separately approved cutover after the immutable package, Diagnostic-to-constraint crosswalk, behavior or parity evidence, consumer installation and upgrade guidance, compatible version range, and owner approval are all available.
- This decision controls framework support and routing. It does not yet decide how an existing target repository behaves at the cutover release when its team has not approved the new NuGet package.

### DEC-030 — Cutover Is An Explicit Breaking Change Without Legacy Retention

- The readiness-gated AI Context release that changes the .NET provider removes the bundled source tools and documents the change as breaking.
- An existing target may complete the AI Context upgrade without installing Architecture Kit. If the team defers the package decision, custom architecture diagnostics are unavailable until it later installs an approved package version.
- The migration guide and upgrade-facing output must explicitly require the responsible people to choose whether to install Architecture Kit now or handle the package later. Deferral is an acknowledged state, not an implicit claim that mechanical validation still exists.
- AI Context does not retain the old bundled tools for upgraded targets and does not block the complete framework upgrade on package approval.
- The framework need not add a more elaborate downstream compatibility bridge at this stage because adoption is still limited. Future evidence of wider adoption may justify revisiting migration assistance without changing the semantic ownership model.

### DEC-031 — Technology Profiles Own Examples And Action Skills Route Them

- The .NET technology profile owns its concrete rules, ecosystem conventions, canonical examples, pitfalls, and tool-binding references.
- Existing action-oriented skills such as architecture, review, and implementation load only the smallest applicable profile-owned reference subset for the current task. Selective loading does not transfer semantic ownership into the skill.
- A skill owns execution procedure, task classification, loading maps, output contracts, and stop or handoff conditions; it must not duplicate or silently redefine profile rules.
- AI Context does not introduce a general-purpose `dotnet-engineering` skill merely to contain .NET knowledge.
- A new narrow skill is justified only when a stable, repeatable execution workflow has its own trigger, inputs, outputs, validation, and responsibility boundary.
- The same ownership model should extend to future technology profiles, including frontend profiles: profiles own technology truth and examples, while reusable action skills select the applicable profile references.

### DEC-032 — External Skills Use Three Support Tiers

- Unregistered external skills may coexist with AI Context, but the framework makes no compatibility claim for them. Repository truth and the effective target profile still take precedence when they are used.
- A target-approved external-skill registry or allowlist is the default mechanism for formal team support. It records upstream identity and version or commit provenance, applicable capability and technology profile, approval state, and known overlaps without copying the external skill into AI Context.
- AI Context-maintained adapters are reserved for a small number of important integrations that repeatedly require stable preconditions, reference loading, output normalization, or handoff behavior. Adapters remain thin and do not fork the external skill's implementation or semantic content.
- External skill output cannot bypass workflow gates, approval boundaries, target-owned commands, or completion contracts. An external skill is an execution provider beneath project and AI Context authority.
- Selective installation and registration are required to limit discovery cost and ambiguous triggers; official or popular origin alone does not make an entire catalog target-approved.

### DEC-033 — Evaluate Existing Canonical Roles Before External Orchestration

- Do not introduce or pilot `kevintsengtw/dotnet-testing-agent-orchestration-codex` at this stage.
- AI Context already owns canonical delegated-role definitions under `.ai/assets/sub-agent-role-prompts/`; the immediate question is whether those existing roles are operationally reachable and actually used by their owning skills and supported runtimes.
- The external repository remains comparative evidence for orchestration techniques only. It is not a registered provider, dependency, copied asset, or planned adapter under the current discussion.

### DEC-034 — Sub-Agent Reachability Is A Separate Issue Topic

- Sub-agent owning-skill reachability, runtime invocation, test-implementation ownership, and downstream adapter installation drift are excluded from the main rules-and-Architecture-Kit issue.
- Preserve the current findings as separate follow-up notes without creating a new issue or reopening the completed historical adapter-promotion issue.
- The main issue may state that sub-agent routing is out of scope, but it must not propose a sub-agent implementation or external provider pilot.

### DEC-035 — Retain Drafts On The Current Branch Only

- Do not merge the discussion workflow or issue drafts to `main` at this stage.
- Do not copy the discussion record or drafts into the AI Context source repository at this stage.
- Prepare copy-ready issue material locally for owner review. GitHub issue creation, push, merge, and cross-repository retention require later explicit authorization.

### DEC-036 — Related Issues Reference One Primary Proposal

- The new rule-architecture proposal is the single complete issue representation of this discussion. Related issues record only completion state, ownership boundaries, and reciprocal links rather than duplicating the full proposal.
- After the proposal receives an issue number, `#61` should record the completed deliberation round and pending owner disposition through its canonical backlog source before synchronizing the GitHub projection.
- `#75` and `#43` should receive bounded reciprocal relationships without absorbing this proposal's rule semantics or prematurely changing their acceptance criteria.
- Closed `#58` remains closed. A separately authorized sub-agent reachability issue may cite it as prior adapter-contract evidence.

### DEC-037 — The Dedicated Remote Branch Is The Cross-Machine Transport

- The owner pushed `codex/2026-07-30-ai-context-architecture-kit-standards-discussion` to `origin` to continue the active discussion from another computer.
- This supersedes only the no-push portion of `DEC-035`. The discussion remains unmerged, no upstream AI Context artifact has been copied, and no GitHub issue has been created.
- A cross-machine continuation must use the dedicated branch plus a repository-native handoff checkpoint; hidden chat context is not required to reconstruct the decisions, issue draft, deferred sub-agent notes, or next decision.
- Any checkpoint commit created after the observed remote tip must itself be pushed before the computer switch or it will remain local-only evidence.

## Conflict Reconciliation

- `DEC-020` remains valid for ownership: Architecture Kit supplies deterministic structural comparison and AI Context owns semantic interpretation.
- `DEC-021` narrows the operational reading of `DEC-020`. "When installed" means the validation capability is available, not that it runs automatically on every edit, IDE analysis, or ordinary build.
- The earlier statement that Architecture Kit reports structural drift now means an explicit CI consistency stage reports it as a warning by default.
- `DEC-017` through `DEC-019` remain compatible. Their evidence and review requirements apply when an override is classified or reconsidered; they do not require AI to inspect every `.editorconfig` change as it happens.
- A material affected-code design change remains a tooling-waiver review event, but identifying that event belongs to normal human or AI review and CI workflow context rather than a mandatory per-edit Analyzer heuristic.
- `DEC-022` is compatible with the earlier ownership boundary only if normalized enforcement data does not make Roslyn or Architecture Kit implementation details part of universal software-engineering semantics; that boundary is the next explicit decision.
- `DEC-023` resolves that compatibility condition through the two-level abstract-capability and technology-binding model.
- `DEC-024` resolves the technology-native ownership boundary: profiles may own non-universal rules, while meaningful cross-language intent remains core-owned.
- `DEC-027` supersedes the portion of `DEC-020` that assigned target rule-profile and evidence comparison to Architecture Kit itself. Architecture Kit supplies the mechanical Analyzer behavior; AI Context and target CI own the one-way mapping and cross-artifact consistency check.
- `DEC-027` also refines `DEC-021`: the explicit final CI warning remains, but its context-consistency logic is framework-side or target-side rather than a requirement that Architecture Kit parse AI Context records.
- `DEC-001`, `DEC-027`, and `DEC-028` define the intended steady-state ownership boundary. They do not make the still-unpublished Architecture Kit the active provider today.
- Until a separately approved cutover, AI Context's source-included `tools/**` remain the current transitional .NET mechanical-validation implementation. This is a time-bounded ownership exception, not a second semantic authority.
- `DEC-015` and `DEC-016` apply to an external Architecture Kit package only after that package is available and explicitly approved. They do not disable or remove the currently distributed source-included tools.
- `DEC-029` rejects the previously considered framework-level Architecture Kit preview. The provider transition is a single readiness-gated cutover, not a gradual supported-provider rollout.
- `DEC-030` resolves the remaining cutover conflict in favor of a visible validation gap when package adoption is deferred. It preserves `DEC-013`: AI Context installation or upgrade may finish with a pending package decision.
- `DEC-030` also preserves `DEC-014` and `DEC-015`: AI guidance and ordinary profile configuration remain active, while an unapproved Architecture Kit package remains absent. The release must not report custom mechanical validation as passed or available in that state.
- `DEC-031` resolves the reference-versus-skill question without moving canonical examples under skills. It preserves early visibility of concrete constraints while using progressive, task-specific reference loading to control context cost.
- `DEC-032` confirms the three-tier external-skill model and resolves the prior admission-policy question in favor of a target-approved registry for team-supported integrations, with permissive unregistered use and rare framework adapters at the outer tiers.
- `DEC-033` closes the proposed external test-provider pilot without changing `DEC-032`. External compatibility remains defined, but the sub-agent discussion returns to the reachability and use of AI Context's existing canonical delegated roles.
- `DEC-034` removes that reachability topic from the main issue while preserving it for a dedicated follow-up discussion.
- `DEC-035` continues to prohibit merge, upstream copy, and issue creation. `DEC-037` supersedes its no-push restriction solely to use the dedicated remote branch as the cross-machine transport.

## Confirmed Transition Policy

The current evidence supports deciding the destination now while deferring the migration. A safe transition needs to distinguish provider availability from rule semantics:

- `bundled-source`: the current AI Context-managed `tools/**` provider and present default.
- `architecture-kit-nuget`: the intended external provider only after its package identity and complete cutover contract are approved.
- Only one provider should enforce the same Diagnostic set by default in a target repository; routine dual execution would create duplicate findings and noise.
- Cutover should require at least a published immutable package, Diagnostic and constraint crosswalk, behavior/parity evidence, consumer installation and upgrade guidance, a declared compatible version range in the .NET profile, and explicit owner approval.
- Removing the bundled source is a separately reviewed, breaking AI Context migration after target consumption is proven; upgraded targets do not receive a legacy-provider retention path.

AI Context does not offer the external binding before that cutover. At the cutover, downstream teams either install an approved Architecture Kit version or explicitly defer it and continue without custom mechanical validation.

## Architecture Kit Activation Clarification

- "Architecture Kit diagnostics do not automatically apply" was ambiguous. The intended boundary is that installing or upgrading AI Context alone must not silently add, upgrade, or reconfigure an Architecture Kit package reference.
- When the Analyzer package is absent, no Architecture Kit diagnostic can run.
- When the package is present but a diagnostic descriptor is disabled by default, that diagnostic requires an explicit project configuration before it reports.
- When the package is present and a diagnostic descriptor is enabled by default, Roslyn may report it immediately without a target `.editorconfig`; a warning may also become build-blocking when the target treats warnings as errors.
- Approval is version-scoped: installing an approved package version activates that version's complete ruleset according to its package defaults, while `.editorconfig` remains the target-owned control surface for diagnostic-level overrides.
- Pending review now means "package absent." Standard `.editorconfig` formatting defaults remain a separate technology-profile configuration concern.

## Terminology Note

- The working shorthand in this discussion remains "AI Context."
- The owner intends to consider "AI Collaboration Framework" as the future canonical product name, but this discussion does not authorize a repository-wide rename.

## Working Model

```text
Universal software-engineering concept
  -> concrete, externally observable default constraints
  -> active AI Context baseline guidance
  -> target ADR-backed semantic deviations
  -> standard technology-profile configuration
  -> current bundled-source mechanical validation during the transition
  -> future optional Architecture Kit recommendation and explicit approval
  -> approved external version installation and package-default enforcement
  -> target-owned .editorconfig diagnostic overrides
     -> semantic deviation: target rule profile + ADR + customization ledger
     -> enforcement tuning: target enforcement record
     -> Analyzer limitation: Diagnostic ID + local rationale + event-driven review; upstream issue optional
  -> native deterministic .NET diagnostics during development
  -> explicit framework/target CI structural consistency warning using one-way bindings
  -> AI Context semantic reconciliation when review is triggered
  -> evidence-first diagnostic handling
```

## Shared-Understanding Scenarios

### Scenario A — Universal Aggregate Encapsulation With A .NET Binding

- Core concept: aggregate encapsulation.
- Core rule: aggregate state changes through controlled behavior.
- Core constraint: externally writable state is not exposed.
- Core enforcement capability: the constraint is statically analyzable.
- .NET profile binding: Architecture Kit package and Diagnostic ID implement that capability for C#.
- Target configuration: `.editorconfig` selects the effective Diagnostic severity; an ADR and semantic customization are needed only if the team changes the engineering meaning.

### Scenario B — The Same Constraint In Another Technology

- A Java or Rust profile reuses the same core concept, rule, and constraint identities.
- Its binding may select a language-native analyzer, a test framework, or review-only validation according to available tooling.
- Absence of an equivalent Roslyn mechanism does not change the core engineering meaning and does not cause .NET implementation details to leak into universal context.

### Scenario C — A Human Changes `.editorconfig`

- The edit immediately follows native IDE, Roslyn, and build behavior.
- AI Context does not assume that only an AI could have made the change and does not spend tokens reconciling the change immediately.
- An explicit final CI consistency stage may later remind the team that effective configuration and recorded context differ.
- The team then decides whether the edit is enforcement tuning, a tooling waiver, or evidence of a semantic deviation.

### Scenario D — A Technology-Native Convention

- A convention such as the C# `Async` method-name suffix may not have a useful language-independent constraint at the same level of specificity.
- Core owns the broader asynchronous-contract clarity intent, while the exact `Async` suffix convention is owned by the .NET profile.
- If another technology-specific convention has no useful cross-language intent, its profile may own the entire rule without manufacturing a core abstraction.

## Cross-Language Evidence — Asynchronous Naming

This evidence was inspected on 2026-08-02 and informed the owner-confirmed boundary in `DEC-024`.

### .NET

- Microsoft's Task-based Asynchronous Pattern guidance explicitly uses the `Async` suffix for methods returning awaitable types and documents limited exceptions when asynchronous intent is already clear from a task-combinator API or framework context.
- Evidence: <https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap> and <https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios>.

### TypeScript

- Official TypeScript documentation expresses asynchronous behavior through the `async` keyword and `Promise` return contract. Its examples use names such as `printDelayed`, `delay`, `doWork`, and `func` without requiring an `Async` suffix.
- Evidence: <https://www.typescriptlang.org/docs/handbook/release-notes/typescript-1-7.html> and <https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-2.html>.

### Java

- Java's standard `CompletableFuture` API represents asynchronous completion through `Future` and `CompletionStage` types. It uses names such as `supplyAsync` and `thenApplyAsync` to distinguish asynchronous execution variants from related non-async continuation methods.
- The evidence supports a Java API-specific naming distinction, not a universal Java rule that every method returning a future must end in `Async`; this second statement is an inference from the standard API rather than an explicit Java language-wide prohibition or mandate.
- Evidence: <https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/CompletableFuture.html>.

### Rust

- Rust marks asynchronous functions with `async fn`, which produces a `Future`; its general function naming convention is snake case. Official examples do not prescribe an `_async` suffix.
- Evidence: <https://doc.rust-lang.org/std/keyword.async.html> and <https://doc.rust-lang.org/book/ch03-03-how-functions-work.html>.

### Confirmed Governance Interpretation

- A universal requirement that every asynchronous method name end in `Async` would impose a .NET TAP idiom on ecosystems that expose asynchronous intent through different syntax, types, or API distinctions.
- A cross-language core may instead own the engineering intent that asynchronous completion and usage semantics are explicit in the public contract.
- Each technology profile may then own the concrete idiom: .NET TAP naming and awaitable types, TypeScript `async` and `Promise`, Java future or completion-stage APIs and their local naming semantics, and Rust `async fn` or `Future`.
- Under this model, a technology-specific rule traces to a core concept when a meaningful cross-language engineering intent exists; its exact syntax and naming constraint remain in the technology profile. A rule with no useful cross-language intent may remain profile-owned rather than forcing an artificial abstraction.

## External Skill Compatibility Evidence And Candidate Model

This evidence was refreshed on 2026-08-02 after the owner confirmed `DEC-031`. It informs an extension question and is not yet a confirmed external-skill governance decision.

### Current External Ecosystem

- The .NET team's `dotnet/skills` repository publishes an open-Agent-Skills-compatible plugin collection for core .NET, data, diagnostics, MSBuild, NuGet, upgrades, testing, ASP.NET Core, Blazor, and other focused areas. It documents both Codex plugin-marketplace installation and individual skill installation: <https://github.com/dotnet/skills>.
- Its `dotnet-test` plugin includes .NET test execution, generation, quality analysis, coverage, testability improvement, and test-framework migration surfaces. Several of these overlap in action scope with AI Context test design, implementation, review, and compliance capabilities even when their normative goals differ: <https://github.com/dotnet/skills/tree/main/plugins/dotnet-test>.
- Microsoft's broader `microsoft/skills` repository contains Azure SDK and Foundry skills across .NET, TypeScript, Python, Java, and other languages, demonstrating that future multi-profile repositories may install several vendor skills without those skills sharing one semantic owner: <https://github.com/microsoft/skills>.
- Microsoft Agent Framework documents progressive disclosure: only skill discovery metadata is normally advertised, then the main skill body and resources are loaded on demand. It also warns against overly broad skills and treats third-party skill instructions and scripts as dependencies requiring review: <https://learn.microsoft.com/en-us/agent-framework/journey/adding-skills> and <https://learn.microsoft.com/en-us/agent-framework/agents/skills>.

### Confirmed Compatibility Boundary

- File-format or runtime compatibility means an external `SKILL.md` can be discovered and invoked; it does not prove semantic, workflow, permission, or completion-claim compatibility.
- Active repository truth, target ADRs and customizations, and applicable AI Context rules constrain every external skill. An external skill supplies execution knowledge and cannot silently override those authorities.
- External skill outputs must not bypass workflow gates, approval boundaries, target test commands, or the repository's definition of completion. For example, generating tests is not equivalent to passing a spec-compliance gate.
- Installation should be selective. Registering an entire vendor catalog increases discovery cost and trigger collisions even when detailed resources use progressive disclosure.
- An external skill should retain its upstream identity and version or commit provenance rather than being copied into an AI Context canonical skill and allowed to drift.
- `DEC-032` applies these principles through unregistered, target-approved, and adapted support tiers.

## Sub-Agent Orchestration Evidence And Candidate Model

This extension was raised after the external-skill tiers were confirmed. The evidence below is current, but the adoption shape remains pending owner confirmation.

### Existing AI Context Capability

- AI Context already distinguishes top-level skills from bounded delegated role prompts in `.ai/SUB-AGENT-SYSTEM.MD`. It defines test-generation roles for use cases, aggregates, controllers, and reactors, plus implementation, review, mutation-testing, and translation roles.
- Existing delegation rules keep the main agent responsible for integration, review, and final validation; a general sub-agent is read-only by default and may not redefine architecture, skill boundaries, or workflow scope.
- `software-development-orchestrator` already produces explicit handoff packets and routes the `test-execution` capability in this order: target-profile commands, a separately evaluated external skill, then a fallback contract.
- The current local test roles are bounded implementation roles. They do not yet form a reusable Research -> Plan -> Implement -> Build -> Test -> Fix -> Lint orchestration pipeline.

### External Pattern Evidence

- The official `dotnet-test` plugin uses a user-facing test-generation skill and nested agents for research, planning, implementation, building, testing, fixing, and linting. It keeps reference-only helper skills out of the user-facing menu and loads them by name: <https://github.com/dotnet/skills/tree/main/plugins/dotnet-test>.
- Its documentation also shows a portability constraint: nested sub-agent invocation differs by runtime, while an inline fallback preserves the result when nested delegation is unavailable. AI Context therefore cannot make nested fan-out a universal prerequisite.

### Current Operational Reachability

- `.ai/SUB-AGENT-SYSTEM.MD` declares eighteen active role routes and states that seventeen roles use dynamic canonical loading. This is a governance and routing contract, not an executable dispatcher; placing a role under `.ai/assets/sub-agent-role-prompts/` does not by itself cause a runtime to discover or invoke it.
- All non-translator manifests have empty `wrapper_targets` and `adapter_metadata`. They can be used only when an owning skill or main agent explicitly reads the canonical role and delegates it through an available generic worker. If no caller loads the routing table or manifest, the role is inert.
- `slice-implementer` has the strongest current connection. Its command, query, and reactor mode references make the corresponding role manifests and playbooks mandatory inputs. Their guidance therefore applies when those modes are followed, but the skill does not require a separate worker to be spawned; execution may remain inline in the main agent.
- Aggregate, controller, outbox, and profile-config implementation roles are listed under `slice-implementer` in the central routing table, but the current skill exposes only command, query, reactor, and generic execution modes. The additional roles are discoverable through the central table or architecture source map, not through an explicit implementation-mode route.
- `problem-frame-author`, `bdd-gwt-test-designer`, and `code-reviewer` do not currently cite their mapped delegated-role manifests in their canonical skill specs or runtime wrappers. The central table describes an intended relationship, but does not guarantee that these skills will load or invoke the problem-frame, test-generation, or review workers.
- The test route has an additional responsibility mismatch: `bdd-gwt-test-designer` explicitly stops before final test-code implementation, while its mapped test sub-agent roles produce concrete test code. No current top-level capability contract explicitly owns that transition and invocation.
- `software-development-orchestrator` can produce a handoff packet for a skill or sub-agent, but its capability profile maps top-level skills and leaves `test-execution` to target commands, an evaluated external provider, or fallback. It does not map or automatically invoke the canonical role-prompt inventory.
- `context-translator` is the only promoted runtime-native role. The current AI Context source repository contains its Codex, Claude, and Copilot adapters and packages `.codex/agents/**`. This installed target contains the canonical declaration plus the Claude and Copilot adapters, but lacks `.codex/agents/context-translator.toml` because its target-retained `.gitignore` omitted the `!/.codex/agents/**` exception. Running `validate-ai-context.py` reproduces the missing Codex adapter error. The named translator is therefore not available through this target's current Codex runtime configuration.
- The current Codex session exposes generic collaboration workers separately from top-level skill wrappers, but does not surface these canonical role IDs as automatically callable named agents. The main agent must still select a role, read its contract, construct the bounded handoff, and retain integration responsibility.

### Owner-Provided Test Orchestration Reference — Not Adopted

- The owner provided `kevintsengtw/dotnet-testing-agent-orchestration-codex` as a concrete external test-skill candidate: <https://github.com/kevintsengtw/dotnet-testing-agent-orchestration-codex>.
- Its current release describes one test orchestrator coordinating four bounded roles: Analyzer, Writer, Executor, and Reviewer. The orchestration value comes from role isolation, canonical JSON handoffs, runtime validators, approval gates, and bounded redispatch rather than from parallel fan-out alone.
- The orchestrator retains the main-thread coordination role and prohibits itself from writing tests. It uses fresh, self-contained delegated contexts, passes canonical artifact paths between stages, requires one Writer per target, and separates production-code refactoring behind explicit user approval.
- The package is a complete runtime bundle rather than a single `SKILL.md`: orchestrator skills depend on role definitions, scripts, validators, configuration, run-state, and separately installed technical testing skills. Any pilot must therefore pin and validate the complete upstream release or commit.
- Current upstream documents demonstrate a provenance risk that the three-tier model must handle. The root README and `CHANGELOG.md` describe the v1.1.0 single-Writer design, while `docs/architecture/overview.md` still contains the older split-Writer topology. Registration must name the authoritative release contract and cannot treat every file in an external repository as equally current.
- The repository's token measurements are explicitly estimates of visible context rather than provider billing truth. Role isolation may reduce context per agent and parallel execution may reduce elapsed time, but total agent, token, and tool cost can increase.
- Under `DEC-033`, these observations remain design comparisons only and do not create a pilot or dependency.

### Candidate Adoption Boundary — Owner Confirmation Required

- Reuse the orchestration topology, not the external skill's engineering semantics. AI Context and the effective target profile still own testing intent, framework defaults, GWT requirements, approval, and completion gates.
- One top-level skill or orchestrator owns the pipeline and final synthesis. Delegated roles receive bounded inputs, outputs, file or artifact permissions, validation expectations, and stop conditions.
- Parallel read-only research or review is the safest default. Mutating workers require disjoint scopes; the parent owns integration and the durable commit checkpoint.
- Sub-agent execution is optional and size-triggered. Small test changes remain direct; runtimes without delegation use the same stage contract inline.
- Fan-out depth, worker count, and build-test-fix iterations must be bounded because parallelism can reduce elapsed time while increasing total token and tool cost.
- `DEC-033` removes the external-provider pilot from the current direction. The remaining design question is how an owning skill makes an explicit direct-versus-delegated decision for an existing canonical role, while keeping small tasks inline and preserving a usable path for runtimes without sub-agent support.
- Any future role integration should make selection, loaded references, input envelope, output contract, permissions, retry bounds, and fallback observable. Merely marking a manifest `active` or listing it in `.ai/SUB-AGENT-SYSTEM.MD` is insufficient evidence that the role executes.

## Remaining Discussion Roadmap

The standards-ownership design, Architecture Kit boundary, external-skill admission model, and issue-scope split are complete. No additional architecture decision is currently required before issue review.

The future product rename from "AI Context" to "AI Collaboration Framework" is noted but excluded from this count and from the current issue scope unless the owner explicitly reopens it.

1. Review the revised copy-ready main issue draft and its related-issue synchronization contract.
2. Decide whether to retain the full downstream workflow only as external evidence or import a bounded raw evidence package through the AI Context external-review assessment lifecycle.
3. Keep the sub-agent observations as deferred separate-issue notes until their own discussion is authorized.
4. After owner approval, separately choose whether to create the upstream issue. Keep the current workflow branch unmerged and do not copy artifacts into the source repository unless later authorized.

## Workflow Portability Assessment — Owner Decision Pending

- This workflow is a downstream repository record. Its locator, plan, task, branch, commit history, inspected target evidence, and continuation state describe `dotnet-distributed-architecture-lab`, not an authorized execution workflow in the AI Context source repository.
- Copying the complete directory into the source repository's `.dev/workflows/` would misrepresent downstream discussion state as upstream execution state and could confuse workflow discovery, branch metadata, validators, and future remediation ownership.
- The current AI Context assessment policy already defines an external-review intake: raw external material remains attributed evidence, a repo-native assessment reproduces and normalizes material claims, backlog references stable assessment findings, and `.dev/workflows/` is reserved for authorized execution.
- Recommended boundary: retain this complete workflow as the originating record; if full provenance is needed upstream, import a bounded immutable evidence package containing the discussion record, issue draft, source repository/ref/commit, and hashes under a repo-native external-review assessment; create a new upstream workflow only after the proposal is accepted and implementation is authorized.
- If the originating branch remains local and unmerged, it is not yet a durable cross-repository reference. Before upstream intake, either publish an immutable branch/ref with explicit authorization or copy the bounded evidence package into the upstream assessment so its bytes and provenance can be retained without importing downstream workflow identity.

## Expected Outputs And Application

1. **Durable decision record** — this file remains the complete reasoning trail and resumption source. It can be retained on the workflow branch or merged to `main` as target-project knowledge when the owner decides.
2. **Issue-ready AI Context feedback** — a finished GitHub issue body will consolidate the problem, goals, non-goals, decisions, proposed ownership boundaries, schema and lifecycle requirements, migration concerns, and acceptance criteria for `ai-collaboration-prompts-dotnet-backend`.
3. **Architecture Kit companion requirements** — independent package and Diagnostic behavior, stable Diagnostic identities where feasible, default-severity documentation, and release information needed by the one-way .NET-profile mapping will be separated into a companion section or a distinct Architecture Kit issue draft if the owner wants separate tracking.
4. **Target adoption model** — a concise mapping will show how a consuming repository uses its target rule profile, ADRs, `customizations.yaml`, `.editorconfig`, tooling waivers, and Architecture Kit package reference during install, development, upgrade, and reconciliation.
5. **Implementation and verification checklist** — work will be split by owning repository so AI Context schema and workflow changes, Architecture Kit implementation work, and downstream migration can be planned and validated independently.

Current prepared artifacts:

- `ai-context-rule-architecture-issue-draft.md`: copy-ready main upstream issue title and body.
- `sub-agent-follow-up-notes.md`: deferred observations for a separately scoped future discussion.

These outputs remain proposals and issue material until the owner separately authorizes canonical AI Context changes, Architecture Kit implementation, issue creation, push, or merge.

## Open Questions

No unresolved architecture direction currently blocks preparation of the main issue. Remaining choices are publication actions rather than design assumptions:

1. Owner review and requested edits to the issue draft.
2. Whether and when to create the upstream issue.
3. Whether the upstream repository needs a bounded external-review evidence package or only the normalized issue. The recommendation is not to copy the complete downstream workflow into upstream `.dev/workflows/`; the current authorization remains to do neither.

## GitHub Issue Inventory Check

- A connector-backed search of open and closed issues on 2026-08-02 found no direct duplicate for the layered engineering-rule, target-policy, and Architecture Kit binding proposal.
- Open issue `#61` is a standards-simplification deliberation enabler. The main draft is framed as a concrete candidate outcome rather than a replacement for that deliberation.
- Open issue `#75` owns aggregate `check-all` source-versus-downstream validation composition and remains outside this issue.
- Open issue `#43` owns existing AI-agent repository compatibility intake; it may supply migration evidence but does not own rule semantics.
- Closed issue `#58` completed the dynamic-versus-native sub-agent adapter contract. The deferred follow-up notes cover post-contract owning-skill reachability and downstream installation drift instead of duplicating `#58`.

## Cross-Machine Readiness Audit

- At the start of the audit, local `HEAD` and `origin/codex/2026-07-30-ai-context-architecture-kit-standards-discussion` both resolved to `85212e42beb23f322d5e1c5880ebd9241cb992ae`; the worktree was clean and the branch had no ahead/behind commits.
- Conversation-to-record reconciliation found all thirty-six prior engineering and governance decisions in `DEC-001` through `DEC-036`. The owner-reported remote transport decision is now retained as `DEC-037`.
- The copy-ready main issue, related-issue synchronization contract, deferred sub-agent findings, workflow plan, task state, and external-review retention recommendation are all present. No additional unstored engineering decision was found.
- Deterministic tracked-file scans found no Windows, macOS, or Linux absolute user-home path in current `HEAD`, branch-added lines relative to `main`, reachable file history, or commit messages. The handoff checkpoint necessarily records the validated commit's Git author email as attribution evidence; that identity value is not a filesystem path.
- The requested `LUNA MAX` runtime was not available in this session. Exact Git searches were used for the path inventory because they are cheaper and more deterministic than another model pass.
- The required critical gate executed all thirty checks after supplying transient Python and NuGet prerequisites. Twenty-nine passed; `AI Context Navigation and Runtime Contracts` failed because `.codex/agents/context-translator.toml` is absent while the canonical manifest declares it. This is the already-recorded downstream adapter drift, now identified as `AICDISC-ADAPTER-001`.
- Normal continuation is fail-closed until `AICDISC-ADAPTER-001` is remediated through separately authorized AI-context work and the critical gate passes. The handoff checkpoint preserves this blocker without modifying canonical context or silently treating it as a discussion-record defect.

## Continuation Contract

- Append owner-confirmed decisions with stable `DEC-*` identifiers.
- Keep tentative proposals under Open Questions until the owner confirms them.
- Do not silently rewrite the reasoning of a confirmed decision; add a superseding decision when the owner changes direction.
- Update this record and the workflow resume checkpoint after each material discussion stage.
- Do not create upstream issues, modify canonical standards, push, merge, or close the workflow without explicit owner authorization.
