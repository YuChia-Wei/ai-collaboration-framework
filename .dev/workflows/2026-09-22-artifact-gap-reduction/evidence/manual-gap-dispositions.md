# Original Manual Gap Dispositions

Source: the sixteen manual-gap records at main `237a01f437f3005ea57885714f6ebfc3037d196d`. Owner: ai-context-governance; final integration owner: root. Scope: Issue #320. This is a maintained decision table, not generated execution evidence.

| Original kind | Disposition | Evidence-based action | Preserved boundary / next condition |
| --- | --- | --- | --- |
| acceptance-evidence-ledger | implemented | Existing file/receipt inputs; derive hashes and report projection; preserve explicit outcomes. | Actual receipts still come from their execution owner. |
| independent-review-input | implemented | Derive commit/tree identity, selected authority bytes and subject digest; run current preflight. | Criteria and classification remain explicit; no independent result is generated. |
| independent-review-subject | implemented | Canonical content is produced by build_review_subject inside review-input preparation. | No second subject algorithm or admission authority. |
| validation-dependency-observation-request | implemented | Assemble current request with pinned subject and checked dependency file references. | Does not import or execute the selected callable; no complete-closure claim. |
| execution-prepare-request | implemented | Assemble current request constants and reuse input/Git/review checks. | Packet/dispatch validation and actual execution remain later operations. |
| validation-gate-classification | implemented-partial | Existing group/external gate reason-only authoring. | Identity, membership, sensitivities, eligibility, profiles and environment contract are protected. |
| routing-rule-ownership-catalogs | implemented-partial | Existing rule derived_consumers only; exact citation and contained unique paths. | Canonical ownership, strength and semantic routing require a concrete owner-approved change. |
| tooling-registries | split-mixed-route | Existing shell writer registered separately; Python, fixture and Bash registries expose separate manual routes. | Those three are coupled code/semantic authority, not ordinary editable metadata. |
| engineering-guardrails-provider-contract | semantic-owner | Accepted baseline binds entire documents; generic editing would violate its change-control contract. | Repository owner must select a new baseline ID/version and coordinated digest changes before a concrete change. |
| source-git-provider-policy | semantic-owner | Retain owning governance skill; fields define authorization, provider, grammar/history and required gates. | Repository owner selects a concrete policy change; validate that invariant instead of inventing a general writer. |
| worktree-snapshot-lease | retained-manual | Existing validator/lock acquisition cannot substitute for coordinated acquire/release and crash recovery. | A future custody operation must bind holder, actual snapshot and artifact release, with interrupted-write recovery; owner ai-context-governance. |
| cli-execution-routing-local | retained-manual | Opt-in persistence requires successful recovery and explicit exact-value/path/action disclosure. | No personal binding was read or written. Owner supplies a concrete persistence decision; a future dedicated private writer must preserve it. |
| validation-freeze | retained-manual | Prerequisites describe completed mutations, declarations and workflow state, not fillable defaults. | Owner records actual freeze/release sequencing; a future lifecycle producer needs observation and invalidation, not only serialization. |
| validation-reuse-receipt | retained-manual | Complete dependency, original execution, environment, authority and fresh-gate proof are required. | Use validation lifecycle owner; no expanded reuse policy or work from Issues 307/308 is absorbed. |
| upgrade-route-matrix | retained-manual | Origins, cutovers, deprecations, package identity and execution evidence must be reconciled together. | Upgrade owner supplies concrete route evidence; preserve legacy parse-only status. No current route change is requested. |
| workflow-handoff-checkpoint | retained-manual | Checkpoint creation couples observed Git/gates/attribution with registry publication and post-commit receiver checks. | Future adapter must support captured-observation replay and handoff-specific multi-file recovery; current generic create recovery is insufficient. |

The remaining manual labels are retained deliberately. No unsupported operation is counted as executable, and no decision-bearing lifecycle record is relabelled merely because a serializer exists. The two semantic-owner classifications identify the correct authoring responsibility, not new automated capability.
