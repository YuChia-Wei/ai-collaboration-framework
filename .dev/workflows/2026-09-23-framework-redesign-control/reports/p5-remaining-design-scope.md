# Remaining P5 bounded design assignments

The coordinator selects two independent design Issues from D342-06 in the [P5 contract](../../../design/framework-next/p5-selected-contract.md). The owner authorized work sequencing and Issue/task creation. Each Issue uses one independent gpt-6-astra / ultra task and exact assigned F: worktree, no sub-agents or executor-created conversations. Both are design-only; implementation follows an explicit coordinator selection against the delivered contract.

| Issue | Exclusive design/workflow roots | Complete result |
| --- | --- | --- |
| [#351](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/351) | `.dev/design/framework-next/problem-frame-compliance/`; `.dev/workflows/2026-09-23-problem-frame-compliance-design/` | Select a bounded CBF/SWF family/version or justified alternative; distinguish authoring, structural validation, semantic review and target compliance; define format/tools/owners and explicit optional .NET prerequisites; retain unsupported families; propose source slices and decisions. |
| [#352](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/352) | `.dev/design/framework-next/optional-context-maintenance/`; `.dev/workflows/2026-09-23-optional-context-maintenance-design/` | Compare prose-only audit/export, project format reuse and a minimal owned assessment; select optional audit/governance duties, necessary semantic customization state and source-only exclusions; propose useful operations, schema ownership if needed, P3 candidate handoffs and source slices. |

Inputs are actual source and #342 design, selected metadata-v3 contract, delivered P3/P4 and locally integrated #346/#348. Missing #347 source is not implied by its assignment. Related old Issues retain their own acceptance and status. No universal rule engine, duplicate registry, mandatory shared runtime, fabricated validator or 95-schema rewrite is requested. Preserve existing root routes and history until their explicit cutover.

New schemas, if justified, must have selected producer/reader/validator/version/migration responsibilities and realistic recovery/identity/finalization boundaries. A schema-only proposal must state the missing implementation. A prose-only operation must not invent machine execution or a record store merely to fit metadata.

Source implementation, package mapping, root/custom changes, historical migration, tests/trials/CI and provider writes are outside these design workers. They return local coherent commits and final handoffs; coordinator reads them directly and owns shared indexes/push/PR/online merge. All suspended verification remains deferred-by-owner to program #322 coordinator / P7 under U001. Exact planned commit-message validation remains the sole validator exception.
