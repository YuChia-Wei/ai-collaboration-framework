# Independent User Story capability: local delivery

Local implementation and selected validation for #459 are complete. The eight
fixed criteria are individually assessed in [acceptance-results.json](acceptance-results.json).
This record does not close the online Issue or authorize integration/publication.

## Source and behavior

- Branch: `codex/2026-10-17-method-knowledge-skills`.
- Input: `cf0651dc467fd9806b41935283e835c32957424a`.
- Reviewed, tested and installed source: `09b4b4e7372c550e6903d2957a5d7611d49ecd06`.
- Owner authority and intended design: [workflow-plan.md](workflow-plan.md).
- Fixed Issue snapshot: [criteria.json](criteria.json); no provider mutation.
- Owning coordinator: OpenAI Codex, gpt-6-astra/high. Bounded implementation,
  independent review, installation and fresh actors were dispatched gpt-6.1-sol/low.
  This states selected profiles, not provider billing or independently measured cost.

`user-story-author@0.1.0` is a standalone optional source package. It supports
independent plan/draft/normalize/review, including whole Story or exact AC selection.
The user-value, business-rule and technical Description guides preserve the three
selected template structures. Title, Description and AC are separate; caller formats,
existing GWT/non-Gherkin criteria, IDs, statuses and unknowns remain authoritative.
Research uses a bounded learning outcome. Portable handoff records sources, decisions,
dependencies, unknown impact, next step and authority without requiring provider fields.

Direct owner routing is aligned in requirement-author@0.2.1 and orchestrator@0.3.1.
Test-designer remains the test-design owner; no mandatory authoring chain was added.
The catalog has 20 skills. Presets and this project's installed 17-skill projection
are unchanged. All ten new package members originate in src; no private conversation
or external example data is a runtime dependency.

## Validation and retained failures

The initial distribution run executed 73 tests with 4 errors, 0 failures/skips.
All errors arose from an invalid template declaration. Null-configuration instruction
packages require empty managed templates; the prose Description guides were moved
into metadata references, retaining their paths and manifest members. No engine or
schema relaxation was made. The affected four SourceDeclarationTests then passed.
The initial result and affected repair log are preserved in evidence; raw initial
log remains `.dev/ai-context/local/story-459/distribution-log.txt`.

After repair and immutable review, `python -I -B tests/run.py` passed **243 tests**,
0 errors/failures/skips, **69.152907 seconds**. This was the one default-suite run
for this new capability. [Source suite record](evidence/source-suite.json).

Independent `/root/story_review` reviewed the immutable base-to-source diff,
all new package members, direct owner/catalog/manual changes, eight criteria and
behavior cases. Clean fixed HEAD was observed before and after. No actionable
finding was supported. This was static review, separate from installation and
actors. [Review record](evidence/independent-review.json).

## Actual isolated consumers

One frozen-source driver execution completed in **129.196088 seconds**, exit 0.
All 14 child operations completed with no timeout/retry/drift. The packaged engine
performed derive, inspect, exact-delta plan, apply, read-back and resource verification.

| Consumer | Selection and adapter names | Actual read-back |
| --- | --- | --- |
| A | user-story-author alone; original naming; Codex + Claude | 12 owned members, 10 source-identical payloads, managed-bytes-consistent |
| B | Story + test-designer; prefixed naming; Codex + Claude | 19 owned members, 15 source-identical payloads, managed-bytes-consistent |

Both selections have zero knowledge resources. Raw requests, responses, locks,
engine pins and child argv remain at `C:/s459-09b4b4e7`.
[Installed trial record](evidence/installed-trials.json) and
[exact task driver](evidence/installed-driver.py) preserve the execution definition.
These are synthetic unpublished 0.0.0 consumers under Windows inventory-only mode
and process-termination durability. Claude native runtime was not invoked.

## Actual fresh-context behavior

Actors received prompt-only inputs and verified installed resources, without parent
conversation or expectation lists. Parent read the actual outputs and authenticated
recorded file hashes against installed inventory, raw locks and source payloads.

| Case | Observed result |
| --- | --- |
| [S1](evidence/actors/S1.md) | Four independent outcome slices and three distinct Story drafts; success/failure and preserved state retained, Owner validity remains unknown, technical constraints remain prose, research stays planning-only. |
| [S2](evidence/actors/S2.md) | Custom Goal/Rules/Open and original AC IDs/status/GWT preserved; AC-2-only review stays bounded; whole-Story review remains a separate output with no automatic repair or test design. |
| [S3](evidence/actors/S3.md) | Fresh agent reconstructs source/status/unknown/authority from actual Story alone, then uses test-designer for explicitly authorized GWT notes retaining all six state/screen observations and independent oracles. |

The standalone [handoff](evidence/actors/S1-user-value.md) is an exact raw subsection
of S1; [handoff binding](evidence/handoff.json) retains its bytes as escaped text
and SHA-256. All actors loaded zero knowledge bodies. Optional absence was disclosed
without source fallback. [Actor verification](evidence/actor-verification.json)
separates parent judgments, mechanical hashes and selected execution profiles.
Raw receipts are preserved; Git newline normalization is separately hashed.
The exact S1 handoff includes its original separating blank line at EOF. The
record whitespace check reports that one expected artifact warning; it is retained
to preserve the copied handoff. All other changed records pass the whitespace check.

Limits: S1 initially printed the complete owned-file metadata inventory and could
not independently observe runtime model labels; no extra knowledge bodies were read.
S3 first observed the lock after reading a hash-verified runtime entry, then before
core/metadata/design consumption; subsequent lock and all file hashes matched.
This supports the selected behavior observations, not complete before-all-reads
protocol compliance. It is not concealed or turned into a universal reliability pass.

## Proportionate reuse and closeout

The unchanged prior test-designer A2 formal-design observation and unrelated
migration/drift/customization evidence retain their original #454–458 subject.
[Reuse proof](evidence/reuse-proof.json) compares exact Git entries for engine,
adapters, product tools, test-designer, knowledge, presets, source tools/tests and
selected policies. The changed manifest is explicitly excluded from old engine
identity and is validated by the new default suite and actual catalog/installs.
Changed requirement/orchestrator routing was independently inspected; old actor
results are not relabeled as execution of their new entries.

The owner’s #461 cost concern is applied within this task: the metadata repair
reran only four affected checks before the one final default suite; old migration
matrices and the eight-actor batch were not repeated. Terminal record changes get
JSON/YAML/link/whitespace checks and deterministic subject rebind, not another full
suite or install. No #461 implementation or policy modification is included.

The final record commit changes only this workflow's evidence/status.
[Frozen subject](evidence/frozen-subject.json) specifies exact selected paths and
raw Git-tree digest; final HEAD must match that digest. Record-only identity drift
reuses the existing review/tests with this proof, not a new execution claim.

Remaining external steps need their own authority: push/PR, exact PR-head hosted
Source change gate, integration, Issue/Project closure, publication and real-project
installation. None was performed. Local workflow completion means this selected
source and validation work is complete; source-policy release/native deferrals remain.
