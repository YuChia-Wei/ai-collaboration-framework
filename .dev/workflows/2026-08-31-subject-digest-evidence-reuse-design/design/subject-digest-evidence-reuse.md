# GOV-017 Content-Equivalent Evidence Reuse Design

## Document Status

- Issue: [#270](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/270)
- Status: owner-review proposal
- Target release: `v0.16.0`
- Scope: design, examples, historical analysis, and enablement gates
- Not authorized: production implementation, current-gate enablement, push, pull request, merge, release, or publication

## Executive Decision

Adopt a canonical `subject_manifest` and `subject_digest` as an extension of the
existing validation-evidence lifecycle. Do not build a second cache, dependency
resolver, runtime fingerprint, or reuse vocabulary.

The design has two identities with different jobs:

1. `subject_digest` identifies the complete applicable behavioral subject for
   an eligible gate.
2. commit SHA identifies provenance, exact-head review, hosted admission,
   provider state, tag/release binding, and every other immutable history event.

The immediate operational recommendation is:

1. complete the #267 and #268 prerequisite delivery first;
2. implement the shared manifest and rebind contract for #270;
3. enable exactly one pilot, `multi-hop-upgrade-transaction`;
4. observe at least three qualifying head transitions before expanding the
   allowlist;
5. keep actual Windows/Linux upgrade evidence, exact-head audit, hosted
   contexts, provider admission, tag/release binding, and mutable provider state
   fresh throughout.

This is faster and simpler than introducing a new evidence subsystem because
the repository already has:

- per-gate input closure resolution;
- selected-input content fingerprints;
- policy and runner fingerprints;
- actual Python/PyYAML runtime identity;
- environment classes;
- authenticated validation records;
- a `validation-reuse-receipt` contract;
- the `reused-with-proof` audit disposition;
- fail-closed tests for unknown closure, authority drift, environment drift,
  identity substitution, and missing hosted contexts.

The missing layer is a stable, canonical identity projection that can be sealed
with the original evidence and cheaply regenerated at a different commit.

## Owner Requirements And Decisions

| Topic | Owner direction | Design disposition |
| --- | --- | --- |
| Sensitivity model | Use the recommended multi-axis model. | Sensitivities are a set, not a mutually exclusive enum. |
| Enablement speed | Avoid another cycle of SHA-only waste. | Finish design now; enable one pilot immediately after prerequisites, not all gates now. |
| #267 and #268 | Determine whether completing them first is better. | Yes. Deliver them first as one cohesive dependency delivery with separate acceptance results. |
| Manifest complexity | Meet the need without unnecessary complexity. | Compose existing authenticated component digests; do not duplicate their full payloads. |
| Rebind effect | Explain the behavior, not only the schema. | This document includes scenario outcomes and work-impact boundaries. |
| History | No special handling. | No migration or backfill; old evidence stays under its original rules. |
| Pilot | Start with one and observe. | Pilot `multi-hop-upgrade-transaction`; actual-upgrade lanes remain fresh. |
| Benefit evidence | Observe conversation rework and rerun frequency. | Use durable repository history plus prior workflow/conversation records; separate proven and upper-bound claims. |

## Existing Contract Reused By This Design

The current `VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT` already separates:

- `identity-sensitive` evidence, which is always fresh;
- `input-sensitive` evidence, which may reuse authenticated content closure;
- `environment-sensitive` evidence, which also requires compatible environment
  dimensions; and
- `provider-sensitive` evidence, which requires live provider read-back.

The current aggregate registry has 74 checks:

- 64 `reuse-by-input`;
- 2 `reuse-by-fingerprint`; and
- 8 `no-reuse`.

Current cache identity already combines validator policy, actual runtime,
check ID, profile, selected input fingerprint, and environment class. Release
and `nightly-full` still run as required contexts; an internal eligible gate may
reuse proof, but the terminal context itself never disappears.

GOV-017 therefore adds a reusable identity envelope and a rebind operation. It
does not change the evidence taxonomy or weaken current terminal behavior.

## Multi-Axis Gate Classification

Each gate declares zero or more sensitivities:

| Sensitivity | What changes invalidate or refresh it | Reuse consequence |
| --- | --- | --- |
| `identity` | commit, commit range, reviewed head, tag object, integration identity | Always fresh. |
| `input` | tracked bytes or declared/transitive dependency closure | Digest reuse may apply when closure is complete and equivalent. |
| `environment` | actual runtime, toolchain, operating/filesystem/storage semantics selected by the gate | Required dimensions must match; unknown dimensions block. |
| `provider` | PR body/base/head, reviews, hosted contexts, Issue/Project/Release state | Live provider read-back is required. |

`reuse_eligibility` is derived separately. A gate with `input` and
`environment` sensitivity can be reusable. Any `identity` or `provider`
sensitivity that is part of the gate's acceptance makes that gate fresh even if
some behavioral sub-results are reusable.

## Current Gate Decision Table

The table is an enablement decision, not a statement that every declared input
closure is already proven complete.

### Pilot: subject-digest reuse after #267/#268

| Gate | Sensitivities | Decision | Reason |
| --- | --- | --- | --- |
| `multi-hop-upgrade-transaction` | `input`, `environment` | enable one pilot after prerequisites | 360-second budget, deterministic local contract, existing resolver/runtime identity, and multiple historical tracked-subject equivalence groups. It does not satisfy actual-upgrade acceptance. |

### Later allowlist candidates: remain on current behavior for now

These 63 `reuse-by-input` gates remain candidates, not newly enabled:

`assessment-artifacts`, `assessment-artifacts-tests`, `workflow-artifacts`,
`workflow-implementation-contract`, `workflow-lifecycle-contract`,
`git-commit-policy`, `workflow-handoff`, `workflow-handoff-checkpoints`,
`orchestrator-capability-contract`, `orchestrator-acceptance`,
`skill-script-colocation`, `semantic-customization-lifecycle`,
`semantic-customization-skill-contract`, `ai-context-navigation`,
`ai-context-wrapper-metadata`, `ai-context-language-policy`,
`ai-context-source-include-evidence`, `governance-term-routing`,
`target-ai-context-version`, `source-ai-context-version`, `package-apply`,
`payload-user-view`, `upgrade-route-package-projection`,
`provider-role-package-projection`, `dependency-versions`,
`dependency-versions-tests`, `python-source-entrypoints`, `shell-assets`,
`file-disposition-manifest`, `profile-registry-contract`,
`test-fixture-routing-contract`, `validation-evidence-contract`,
`validation-process-supervisor-contract`,
`immutable-history-validation-contract`, `coding-standards-integrity`,
`code-review-routing-contract`, `profile-projection`, `document-projection`,
`coding-standards-structural`, `sdk-free-framework-contract`,
`engineering-guardrails-provider-contract`,
`source-version-governance-tests`, `release-state-tests`,
`release-preparation-tests`, `release-notes-renderer`,
`ai-behavior-evaluation`, `ai-context-load-measurement`,
`repository-config-contract`, `repository-config-contract-tests`,
`skill-transition`, `skill-transition-tests`, `effective-rules`,
`effective-rule-action-skill`, `source-governance-manifest`,
`validation-lifecycle-contract`, `validation-lifecycle-tests`,
`agent-execution-guardrails-contract`, `agent-execution-guardrails-tests`,
`terminal-issue-closure`, `terminal-issue-closure-tests`,
`repository-identity-tests`, `governance-workflow-contract`, and
`github-workflow-contract`.

The two current `reuse-by-fingerprint` gates also remain later candidates:

- `package-smoke`; and
- `package-full-matrix`.

They already have useful package identities, but their full governed subject is
broader than the output payload alone. Their release/nightly contexts must still
run and report a truthful terminal outcome.

### Always fresh or explicitly not reusable

| Registry gate | Sensitivities | Decision |
| --- | --- | --- |
| `selected-git-commits` | `identity`, `input` | Re-execute for the current range. |
| `aggregate-runner-contract` | `input`, `environment` | Re-execute because it verifies the reuse runner and aggregate control surface itself. |
| `validation-evidence-exhaustive-contract` | `input`, `environment` | Re-execute because it is the exhaustive fail-closed evidence mechanism gate. |
| `spec-implementation` | `input`, `environment` | Keep `no-reuse` until a complete target-owned manifest exists. |
| `source-release-closeout-contract` | `identity`, `input`, `provider` | Keep fresh in closeout. Local contract tests never substitute live historical/provider verification. |
| `test-di-compliance` | `input`, `environment` | Keep current advisory/no-reuse behavior. |
| `template-synchronization` | `input`, `environment` | Keep current advisory/no-reuse behavior. |
| `adr-index-update` | `input`, `environment` | Keep current advisory/no-reuse behavior. |

Fresh gates outside the 74-check local registry remain fresh without exception:

- exact-head independent audit;
- required hosted contexts;
- live merge admission and review state;
- tag and Release identity/binding;
- Issue, Project, and other mutable provider state; and
- actual Windows/Linux upgrade evidence until separately classified and
  approved.

## Canonical Subject Manifest

### Design goal

Use the smallest new structure that can prove the complete subject while
reusing existing authoritative receipts. Do not copy thousands of dependency
entries into every higher-level record.

### Manifest shape

`subject-manifest/v1` contains:

1. `gate_id` and approved classification;
2. an `identity_projection` made only of stable, authenticated component
   identities;
3. `subject_digest`, the SHA-256 of canonical JSON for that exact projection;
4. component references and their authenticated SHA-256 digests; and
5. provenance, including the original commit and tree.

The identity projection is:

```json
{
  "schema_version": "subject-identity/v1",
  "gate_id": "<stable-gate-id>",
  "classification_digest": "<sha256>",
  "tracked_closure_digest": "<sha256>",
  "invocation_digest": "<sha256>",
  "authority_digest": "<sha256>",
  "runtime_digest": "<sha256>",
  "environment_digest": "<sha256>"
}
```

Canonicalization uses the repository's existing rule: UTF-8 JSON, recursively
sorted keys, no insignificant whitespace, and `ensure_ascii=false`.

`subject_digest` is:

```text
sha256(canonical_json(identity_projection))
```

Commit, tree, branch, timestamps, evidence paths, provider run IDs, and
human-readable descriptions are provenance. They are intentionally excluded
from `subject_digest` but remain mandatory in the manifest or rebind receipt
where applicable.

### Component contracts

| Component | Existing authority reused | Required behavior |
| --- | --- | --- |
| Classification | approved gate decision registry | Multi-axis sensitivities and explicit allowlist state. Unknown classification blocks. |
| Tracked closure | `check-all.sh --resolve-input-closure`, Git blob/mode records, closure receipt | Complete sorted path set, no unknown paths, authenticated original bytes, fresh current resolution. |
| Invocation | existing argv/cwd/profile fingerprints | Exact command, working directory, and selected profile. |
| Authority | runner, registry, resolver, policy, configuration fingerprints | Every governing byte must match. Missing authority blocks. |
| Runtime | `validation-runtime-identity/v1` | Actual Python implementation/version/ABI and installed PyYAML identity. |
| Environment | environment contract selected by the gate | Baseline platform dimensions plus gate-specific filesystem/storage/tool dimensions. |

### Environment boundary

Do not fingerprint the whole host. That would reintroduce unnecessary
invalidation and create privacy risk.

Every reusable gate gets:

- a baseline runtime/platform contract; and
- an optional gate-specific environment overlay.

Examples of overlay dimensions are Git version, filesystem semantic class,
case sensitivity, symlink/reparse capability, durability-storage class, and
cold/warm benchmark condition. Only declared applicable dimensions are hashed.
Unknown applicable dimensions block reuse.

For the pilot, use Python/PyYAML runtime identity, Git version, OS family, and
filesystem semantic class. Do not include hostname, username, absolute paths,
machine ID, credentials, or unrelated hardware inventory.

## Original Evidence Authentication

History compaction can eventually make the original commit object unavailable.
Rebind must therefore accept exactly one of these original-subject proofs:

1. the original Git object is still resolvable and the authoritative resolver
   reproduces the sealed manifest; or
2. the original manifest was generated and validated during the original
   execution, sealed into its immutable terminal evidence, and its manifest
   and evidence digests remain authenticated.

A plain later-created manifest containing an old SHA is insufficient. If the
original subject cannot be resolved and no trusted sealed manifest exists,
rebind is `blocked`, not reused.

## Final-Head Rebind Gate

### Inputs

- original passed execution evidence;
- original sealed `subject_manifest`;
- current commit SHA;
- current approved gate classification;
- fresh current `subject_manifest`; and
- required original-evidence authentication.

### Deterministic checks

1. The original result is a real `passed` execution or an authenticated reuse
   chain rooted in one.
2. The gate is currently allowlisted and has no identity/provider-sensitive
   acceptance being replaced.
3. Both manifests use recognized schemas and the same classification authority.
4. Original manifest authentication is valid.
5. Current closure resolution is complete and has no unknown paths.
6. Every identity-projection component is present and authenticated.
7. Original and current `subject_digest` values are equal.
8. Provenance records both commit SHAs without rewriting the original record.
9. Every required fresh gate is named and remains replaceable-by-reuse `false`.

### Outcomes

| Outcome | Meaning |
| --- | --- |
| `reused-with-proof` | Expensive behavioral evidence applies to the current subject; it was not executed at the current SHA. |
| `re-executed` | A known relevant component drifted, so the gate must run again. |
| `blocked` | Closure, authentication, authority, environment, or classification is unknown or invalid. |

### Truthful wording

Allowed:

> Gate `multi-hop-upgrade-transaction` reused evidence originally executed at
> `<old-sha>` because approved subject manifests were equivalent; final-head
> exact audit and hosted/provider gates were executed separately for
> `<new-sha>`.

Forbidden:

> The old run audited or executed `<new-sha>`.

The rebind record is append-only. It never modifies the original evidence.

## Behavioral Effects By Change Type

| Change | Expensive eligible gate | Rebind | Still fresh |
| --- | --- | --- | --- |
| Commit-message amend | Reuse when manifest is equal. | `reused-with-proof` | selected commit policy, exact-head audit, hosted/provider admission |
| Squash with equivalent applicable content | Reuse when sealed original proof exists. | `reused-with-proof` | commit range/history gates and final-head gates |
| Rebase with only out-of-closure base changes | Reuse after fresh current closure resolution. | `reused-with-proof` | exact-head and provider gates |
| Merge commit with the same tree/subject | Reuse. | `reused-with-proof` | audit of merge head and required hosted contexts |
| Tracked byte changes inside closure | Re-execute. | `re-executed` | all ordinary final-head gates |
| Declared/transitive dependency changes | Re-execute. | `re-executed` | all ordinary final-head gates |
| Runner, policy, resolver, config, command, or profile changes | Re-execute. | `re-executed` | all ordinary final-head gates |
| Runtime or applicable environment changes | Re-execute; unknown dimensions block. | `re-executed` or `blocked` | all ordinary final-head gates |
| Provider state/body/review/check changes | Local behavioral evidence may remain applicable, but it cannot answer provider acceptance. | Local result unchanged. | provider read-back and admission |
| Old evidence without a subject manifest | No new reuse. | not eligible | existing rules apply |
| Original commit unavailable and no trusted sealed manifest | No reuse. | `blocked` | re-execution required |

## Dependency Sequencing And Cost

### Option A: enable reuse before #267/#268

The implementation diff could be small because most component fingerprints
already exist. The assurance cost is high:

- undeclared inputs can create false equivalence;
- identity-substitution and evidence-omission paths are not exercised by the
  incident corpus;
- every reuse requires heavier manual owner review;
- later #267/#268 findings can force schema and fixture rewrites; and
- a false reuse can invalidate release or audit confidence, which is more
  expensive than the validation saved.

Disposition: reject for current gates.

### Option B: wait for all possible exploratory work in #267/#268

This is safest but can delay the first benefit beyond what the owner needs.
Exploratory mutants and advisory broad-declaration tuning do not all need to
block one bounded pilot.

Disposition: unnecessarily broad as a pilot prerequisite.

### Recommended option: complete the accepted #267/#268 scope first

Deliver #267 and #268 together when their branch, validation, reviewer,
release, and rollback boundaries remain cohesive, while preserving separate
Issue acceptance ledgers.

Required outputs before pilot enablement:

- #268: the pilot's file/subprocess/Git/environment/runtime observation report,
  explicit coverage limits, no observed-but-undeclared dependency, and no
  claim that observation alone proves closure;
- #267: critical identity-substitution and evidence-omission mutants plus the
  applicable validation-chain/semantic-bypass cases, with every critical mutant
  detected; and
- #270: approved classification, canonical manifest, rebind validator, fixtures,
  and one exact allowlist entry.

This costs two prerequisite acceptance scopes and their governed validation,
review, and admission cycle before the first pilot. It avoids building a second
temporary trust model and makes that cost reusable by every later gate.

## Pilot Design

### Selected gate

`multi-hop-upgrade-transaction`

### Why this gate

- It has a 360-second registry budget and recorded real-world rerun pressure.
- Its tracked closure is explicitly declared and resolver-supported.
- It already uses the shared runtime and policy fingerprints.
- Historical heads form clear tracked-subject equivalence groups.
- It is deterministic local behavioral evidence.
- It can be cleanly distinguished from trusted actual-upgrade evidence, which
  remains fresh.

### Pilot stop conditions

Stop or disable the pilot if:

- #267 leaves any critical relevant mutant surviving;
- #268 observes an undeclared dependency;
- any closure or environment dimension is unknown;
- rebind and re-execution disagree on an equivalent fixture;
- a rebound record uses misleading current-SHA execution wording;
- exact-head or hosted/provider gates are skipped or disappear; or
- the allowlist expands without a separate owner decision.

### Observation gate

Observe three qualifying head transitions, not an arbitrary number of days.
For each transition, record:

- why the SHA changed;
- whether the tracked subject remained equivalent;
- whether full eligibility was proven;
- rebind duration;
- avoided execution duration when known;
- owner/agent manual review required;
- exact-head and provider gates that still ran; and
- any false-positive, false-negative, or blocked decision.

Expansion requires zero false reuse, zero missing fresh gates, and an explicit
owner-approved next allowlist entry.

## Historical Avoided-Work Analysis

The retained analysis is in
`../evidence/historical-equivalence-analysis.yaml`. Its digest is an analysis
aid, not the proposed production `subject_digest`.

### Confirmed tracked-subject equivalence

For the ten v0.14.0 candidate heads recorded by the release workflow:

- `package-apply` had one equivalent group spanning the first nine heads; only
  the final fixture change altered its tracked subject;
- `multi-hop-upgrade-transaction` had two equivalent groups, with eight
  within-group SHA transitions that did not change its tracked subject; and
- `package-full-matrix` had two equivalent groups, also with eight
  within-group SHA transitions that did not change its tracked subject.

For the v0.15.0 preparation sequence, the final four heads after the substantive
upgrade-predecessor correction had the same tracked subject for all three gates.
The later commits repaired workflow/provider evidence, not those gate inputs.

Three recent source-head to merge-head pairs had identical repository trees and
identical analyzed subjects:

- `1745a11b` to `5fedacee`;
- `1dfef09e` to `78bfde42`; and
- `6dbe01fa` to `a6efd162`.

These are strong examples of why final-head rebind is useful. They do not make
the exact-head audit or hosted checks reusable.

### Known duration evidence

The #250/#252 delivery recorded these source-head lanes:

- fast Windows: `13.163s`;
- medium synthetic: `299.278s`;
- trusted Windows actual upgrade: `93.181s`; and
- trusted Linux actual upgrade: `42.821s`.

The total is `448.443s` (`7m 28.443s`). Under this proposal, only a separately
approved eligible behavioral gate could be rebound. The trusted actual-upgrade
results remain fresh in the initial design, so `448.443s` is an observed work
envelope, not a claimed saving.

The #251 delivery recorded Ubuntu package-apply `81.500s` and Windows focused
tests `59.855s`, totaling `141.355s`. Its source and merge trees were identical.
Again, this demonstrates the available envelope; exact eligibility depends on
the approved manifest and matching environment.

The v0.13 downstream history cleanup compressed 62 commits to one while keeping
the exact same tree. The new design could preserve eligible behavioral evidence,
but commit-policy, workflow SHA references, and exact-head/provider decisions
would still refresh. No reliable wall-clock saving is claimed because the
retained record does not contain a complete duration breakdown.

### Conversation and workflow impact

Recent workflows repeatedly contained this sequence:

1. run expensive validation and exact-head review;
2. discover a workflow, evidence, or provider-binding repair;
3. create a new commit SHA;
4. determine manually which earlier work is stale;
5. rerun or conservatively discard evidence; and
6. wait for the new hosted head.

GOV-017 removes step 4 for approved gates and can remove the expensive part of
step 5 when the manifest proves equivalence. It does not remove repair work,
fresh exact-head review, or provider waiting.

### Confidence labels

| Label | Meaning |
| --- | --- |
| `full-eligibility-proven` | Tracked closure, authority, runtime, environment, and original evidence authentication all match. Count as avoided execution. |
| `tracked-subject-confirmed` | Git bytes and declared closure match, but historical runtime/environment/authentication is incomplete. Report as an upper-bound candidate only. |
| `conversation-signal` | A prior record describes rerun/rework pressure without enough machine evidence. Use for prioritization, not saved-time claims. |
| `not-avoidable` | Relevant content changed, execution failed/blocked, or a fresh identity/provider gate was required. Never count as saved. |

## Implementation Boundary After Owner Approval

The implementation should extend these existing owners:

- `VALIDATION-EVIDENCE-LIFECYCLE-CONTRACT.md` and its schema;
- `validate-validation-lifecycle.py`;
- `validation-evidence.py` for manifest generation/sealing;
- `check-all.sh` for authoritative current-subject resolution;
- validation lifecycle and evidence fail-closed tests; and
- a gate-classification/allowlist authority owned by the validation lifecycle.

Do not place authoritative classification in this workflow proposal, HTML, a
conversation, or a filename convention.

## Approval Gates

The current design phase can complete without further mutation authority.
Separate future approvals are required for:

1. design acceptance;
2. cohesive #267/#268 implementation;
3. #270 manifest/rebind implementation;
4. pilot enablement for `multi-hop-upgrade-transaction`;
5. allowlist expansion;
6. push and pull request;
7. merge and Issue/Project terminal mutation; and
8. release/publication.

No approval implies the next one.

