# Git Commit Policy

This policy defines commit title format, commit body structure, and commit timing for agent-assisted work.

## Title Format

Use exactly one of these title forms:

```text
<type>(#<issue-number>): <summary>
<type>(<scope>): <summary>
```

For multiple issue numbers:

```text
<type>(#<issue-number>,#<issue-number>): <summary>
```

The issue-number and scope forms are alternatives. The `|` character in
historical examples was meta-notation for “or”; it is not a literal title
character. New commits on or after `2026-08-10T00:40:00+08:00` must use the
canonical form above. The executable policy retains an explicit deprecated
compatibility pattern for earlier shared history; do not rewrite those commits.

Examples:

```text
docs(#123): define language policy
workflow(#124): add workflow gate
refactor(#125,#128): split backend-specific prompt rules
docs(ai-context): inventory context boundaries
```

## Types

Use these commit types:

| Type | Use |
| --- | --- |
| `docs` | Documentation, policy, standards, guides, specs, requirements. |
| `workflow` | Workflow artifacts, task status, review reports, process tracking. |
| `feat` | User-facing or externally visible behavior. |
| `fix` | Bug fixes. |
| `refactor` | Structure changes without intended behavior change. |
| `test` | Test additions or corrections. |
| `chore` | Tooling, housekeeping, generated metadata, or repository maintenance. |
| `merge` | Intentional non-fast-forward integration commits. |

The executable subset of this policy is declared in
`GIT-COMMIT-POLICY.yaml` and enforced by
`.ai/scripts/validate-git-commits.py`. The Markdown document remains the
human-facing source for intent and exceptions; keep both files synchronized.
For source-repository history without target adoption evidence, the validator
selects the canonical pattern prospectively and the named legacy pattern only
for commits before the recorded cutover.

### Initialized Target Adoption

An initialized target can adopt this grammar without rewriting its history by
recording the optional validated provenance field
`policy_adoptions.commit_subject_grammar`:

```yaml
policy_id: git-commit-subject/v2
legacy_history_tip: <full lowercase 40-character target commit SHA>
adopted_at: <ISO-8601 timestamp with offset>
incoming_policy_sha256: <raw SHA-256 of this incoming YAML policy>
decision_evidence: <repository-relative decision record>
```

When explicit target adoption evidence is supplied to the validator, the
legacy pattern applies only to commits reachable from `legacy_history_tip`.
Commits after that history boundary must use the canonical grammar even if
their timestamp predates the source cutover. The adoption timestamp is audit
evidence only; it never selects a grammar. A missing, malformed,
nonexistent, or non-reachable boundary fails closed. If no target adoption
context is supplied, source-repository timestamp behavior remains unchanged.

## Scope

The scope should name the affected boundary, not the file extension. Prefer:

- `ai-context`
- `governance`
- `dotnet-backend`
- `ai-context-init`
- `skills`
- `workflow`
- `testing`
- `architecture`

## Body Format

Workflow-stage commits should include this body:

```text
Why:
- <why this change exists>

What:
- <main change>
- <main change>

Validation:
- <command or check>
- <skipped validation and reason, if any>

Workflow:
- <workflow-id>
- Stage: <stage-id>
- Task: <task-id>

Co-Authored-By: <AI runtime> (<model>, <reasoning_effort>) <noreply@provider-domain>
```

Small direct-mode commits may omit the body when the title is sufficient and the user did not ask for detailed traceability.

Transient read-only analysis has no repository artifacts and therefore requires no branch, workflow, or commit. A durable report-only assessment commits only assessment-owned artifacts and required assessment index updates; read-only evidence gathering does not authorize changes to the assessed context. Remediation commits belong to the workflow that owns those changes.

Standalone durable assessments commit only assessment-owned artifacts and index
updates. They do not create workflow artifacts solely for persistence and do not
authorize remediation of the assessed surface.

When a later workflow merges a standalone assessment branch and validates a
combined commit range, the assessment creation commit retains this standalone
assessment contract. Its subject, matching `Assessment-Id`, and AI signature are
validated, but workflow-only `Why`, `What`, `Validation`, and `Workflow`
sections are not retroactively required. Workflow-stage commits in the same
range remain subject to the full workflow body contract.

Workflow range validation follows the workflow branch's first-parent history.
Merged assessment or other independently governed side branches retain their
own validation and are not recursively revalidated as workflow-stage ancestry.
The workflow merge commit itself remains in the first-parent range and must
satisfy the workflow commit contract.

## Assessment Search Identity

Follow `.dev/standards/ASSESSMENT-ARTIFACT-POLICY.md` for assessment identity
and lifecycle. Assessment creation and material assessment-update subjects must
include the stable ID:

```text
docs(assessment): [ASM-20260713-001] add AI context health assessment
```

Add an `Assessment-Id` trailer before the AI signature trailer:

```text
Assessment-Id: ASM-20260713-001
Co-Authored-By: OpenAI Codex (gpt-5.6-sol, high) <noreply@openai.com>
```

Downstream commits may use repeatable `Assessment-Id` trailers without placing
every assessment ID in the subject. Preserve the ID when amending, rebasing,
cherry-picking, or otherwise rewriting a commit.

## AI Model Signature Trailer

Every repository-created local commit authored with material AI assistance,
including workflow commits and AI-created merge commits, must end with a Git
`Co-Authored-By` trailer that identifies the AI runtime, model, and reasoning
effort:

```text
Co-Authored-By: <AI runtime> (<model>, <reasoning_effort>) <noreply@provider-domain>
```

Examples:

```text
Co-Authored-By: Claude Code (claude-sonnet-5, high) <noreply@anthropic.com>
Co-Authored-By: GitHub Copilot (gpt-5.4, medium) <noreply@github.com>
Co-Authored-By: OpenAI Codex (gpt-5.6-sol, xhigh) <noreply@openai.com>
```

Rules:

- place the trailer after all body sections, separated from the body by one blank line;
- keep the trailer as the final non-empty line, or use one trailer per materially contributing AI runtime/model;
- use the active session's model and reasoning effort when available; otherwise resolve each missing value from the effective configured default after applying the client's documented precedence, then from the client's documented built-in default;
- preserve provider-reported model and reasoning labels as written; do not translate, rank, or replace values such as `xhigh`, `extended`, or `thinking` merely to resemble another provider;
- when a sub-agent materially produces content included in the commit, add an additional trailer whose runtime label ends in `Sub-Agent`, for example `OpenAI Codex Sub-Agent (gpt-5.6-terra, medium)`; do not add a sub-agent co-author for read-only discovery, review, or advice that did not produce committed content;
- when multiple materially contributing sub-agents have the same runtime, model, reasoning effort, and address, retain only one identical trailer;
- task artifacts record the primary executing model and reasoning effort; additional sub-agent contributors are represented by their marked commit trailers;
- apply the common signature shape to repository-created local commits; preserve provider-native commits without rewriting them, and activate provider-specific generation rules only after real fixtures prove the client can emit or retain the approved shape;
- do not add an AI trailer to a human-only commit;
- apply this rule prospectively; do not rewrite existing history solely to add missing trailers.

## Commit Timing

Create a commit when:

- a workflow stage is completed and validated;
- a task JSON status is updated to `completed`;
- a policy or source-of-truth document is introduced;
- a file move or large rename is completed and references are checked;
- the user explicitly asks for a commit.
- a standalone assessment draft reaches a durable resume checkpoint or becomes final.

Do not commit when:

- the working tree includes unrelated user changes;
- validation is still running or unresolved;
- a task is halfway through a file move;
- the next immediate step may invalidate the current diff;
- the user asked not to commit.

## Workflow Commit Rule

For workflow mode, the default density is one validated commit per durable
stage or coherent bounded task batch. A skill invocation is not a commit
boundary by itself. Commit at these boundaries when they form a durable,
validated unit:

1. workflow bootstrap;
2. inventory completed;
3. each policy completed;
4. each skill or wrapper sync completed;
5. each file move batch completed;
6. final validation completed.

If several small policy tasks are completed together and validated together, they may share one commit.

### Safe History Compression

Fixup, squash, or equivalent compression is allowed only when all affected
commits are unshared and unpushed and the active repository policy permits the
rewrite. Compression must not destroy or blur:

- an approved source-of-truth baseline;
- an externally referenced review, assessment, or validation evidence commit;
- shared or pushed history;
- an explicit checkpoint or handoff commit;
- a boundary that another person or automation is expected to review or resume.

Do not rewrite shared or pushed history merely to reduce commit count. If the
history is already shared, add the next coherent corrective commit and preserve
the existing evidence trail.

## Workflow Branch And Merge Rule

Branch naming, branch-first creation, push, checkpoint merge, continuation, and
positive linear-versus-merge-commit topology selection are owned by
`.dev/TEAM-GIT-FLOW-RULES.MD`.

For commit-policy purposes:

- create workflow commits only on the dedicated workflow or continuation branch;
- include checkpoint state in the commit body when the workflow will be handed off or merged before completion;
- do not treat a commit, push, or merge as evidence that the workflow is complete;
- use the pull-request-only `main` integration rule owned by `.dev/TEAM-GIT-FLOW-RULES.MD`; a local merge must not bypass it;
- verify the workflow closing checklist separately from Git transport state.

## Validation Notes

Before commit, run the narrowest meaningful validation:

- Markdown or documentation-only changes: `git diff --check` and reference search when links changed.
- JSON task changes: parse changed JSON files.
- Code changes: run the relevant test command or state why tests were not run.

The commit body must mention skipped validation when the skipped check would normally apply.
AI-assisted commits must also satisfy the AI model signature trailer contract above.

Write the complete planned commit message to a contained ignored message file
and validate those exact bytes before invoking `git commit`:

```bash
python .ai/scripts/validate-git-commits.py \
  --message-file .dev/ai-context/local/commit-messages/<message-file>.txt \
  --workflow-id <workflow-id>
git commit -F .dev/ai-context/local/commit-messages/<message-file>.txt
```

Do not validate a reconstructed message after the commit or use separate
command-line fragments that can drift from the committed body.

For workflow closeout, validate the workflow branch range explicitly:

```bash
python .ai/scripts/validate-git-commits.py --range main..HEAD --workflow-id <workflow-id>
```

`check-all.sh` runs this check when `COMMIT_RANGE` is set. Set
`WORKFLOW_ID` with it for workflow-stage section and identity validation.
Human-only commits are outside the AI-signature contract and should not be
included in a range whose purpose is AI-assisted workflow closeout.
