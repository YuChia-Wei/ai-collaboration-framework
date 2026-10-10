# Workflow record dependency inventory

Baseline: `42b99e954e3d6fbf595075a079357f0ce1df057f`. Current tracked source and
online #439/#440/#416 were read. Graph discovery returned no relevant entries;
index extraction coverage was unproven, so this inventory uses exact tracked
paths and direct call sites. No search absence is used as an absence proof.

| Source | Actual dependency | Disposition |
| --- | --- | --- |
| `src/skills/software-development-orchestrator/skill-package.yaml` | instruction operations, configuration null, no tools/schemas/templates | retain optional orchestration; no fabricated CRUD |
| `src/skills/software-development-orchestrator/references/orchestrate.md` | project-selected writer, checkpoint and document reads | add conditional common-entry consumer instructions; no mandatory store |
| `.dev/standards/SOURCE-DEVELOPMENT-POLICY.md` | source-owned workflow identity/handoff; adopted ordinary-source precedence | governing source policy; not exported as portable rules |
| `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` | locator, Git-trackable artifact_root, entrypoint, task identity, optional lifecycle contract | compatibility input; no schema migration or policy rewrite |
| `.dev/workflows/2026-10-02-skill-routing/` | real locator, tasks, plan, extra fields, results and evidence | selected copied regression fixture; preserve all original bytes |
| `.dev/workflows/2026-10-04-release-boundaries/` | additional current extension fields and task/result variants | comparison only; no full-history acceptance claim |
| `tools/maintenance/validate-assessment-artifacts.py` / `validate_assessments` | direct existence lookup for `relations.workflow_refs` | actual opt-in common parser integration; preserve default existence-only semantics |
| `tools/maintenance/validate-git-commits.py` / `validate_message` | workflow ID in commit message only | unchanged; not a record-reader integration claim |
| `tools/maintenance/validate-workflow-handoff.py` | retained legacy checkpoint YAML, registry and source policy | unchanged; not an ordinary-source prerequisite |
| `.dev/standards/WORKFLOW-HANDOFF-POLICY.md` | distinguishes ordinary source from unavailable legacy template/aggregate route | no restoration under this slice |
| `tools/maintenance/validate-terminal-issue-closure.py` | legacy terminal evidence glob under workflows | not selected; preserve historical evidence ownership |
| `tools/maintenance/python-entrypoints.json` | contains historical workflow-validator declarations | declarations are not availability; no route inferred from them |
| `.dev/standards/WORKFLOW-ARTIFACT-POLICY.md` validation section | explicitly records removed legacy artifact-validator route | new bounded validate does not claim to restore it |
| `tests/source/test_source_workflow.py` | GitHub Actions YAML | unrelated to working-record runtime coverage |
| `src/distribution/manifest.yaml` | exact per-skill member list | new module is not installed/packaged; separate future delivery |

## Selected producer/reader chain

The project-owned writer continues creating locator/tasks/plans. Git discovery
assigns an explicit ref without rewriting them. `WorkflowRecords` routes common
requests to `GitStore`; the CLI and resume consumer call that entry. Checkpoint
adds one file in the same store. The selected assessment reader calls common
validation only with explicit configuration. Actual CLI and validator processes
are tested; source instruction changes alone are not agent-execution evidence.

## Design choices under the owner's development direction

Choose a source CLI and reusable module over adding mandatory Python/store
dependencies to orchestrator or introducing an unreviewed package/catalog change.
Choose one additive checkpoint/receipt envelope over multi-file updates to
locator/task/plan, because the latter requires a distinct transaction/recovery
contract. Content revisions cover core inputs; Git SHA remains source provenance.
Unknown document formats and missing tasks stay visible rather than producing
empty successful records. Local and board providers remain separate slices.

The complete contract and three-mode scenarios are in
[`src/workflow_records/README.md`](../../../src/workflow_records/README.md).
The human guide is [`docs/workflow-records.md`](../../../docs/workflow-records.md).
The contract is versioned independently of board APIs and product release tags.

Open follow-up decisions: optional package placement/version; create and export/
import support; additional historical layouts; local engine/runtime; multi-file
updates; any cross-clone consistency guarantee. None is silently selected here.
