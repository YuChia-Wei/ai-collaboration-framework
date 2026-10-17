# Local source delivery: common method knowledge and skill boundaries

Selected local work for #454–458 is complete. The coordinator assessed all 29
fixed acceptance criteria using source inspection, an independent immutable
review, actual isolated installation/update trials and eight fresh-context actor
cases. This completes the local workflow, not GitHub integration, Issue closure,
publication or downstream adoption.

## Identity and authority

- Workflow: `2026-10-17-method-knowledge-skills`.
- Branch: `codex/2026-10-17-method-knowledge-skills`.
- Base: `b8cfbcc12c98c71a5b2d045febde69c292ef898f`.
- Document checkpoint: `4aa86f90576e6a3d9fb650a038e79039188c2824`.
- Integrated source checkpoint: `893bcb9dcf14bb11e714c84f06250e246338e986`.
- Final validated source: `c9057655e38d263cc6917232fc1b7a553548933d`.
- Exact fixed criteria: [acceptance-criteria.json](acceptance-criteria.json).
- Actor prompts and predeclared parent expectations: [behavior-cases.json](behavior-cases.json).
- Per-criterion local disposition: [acceptance-results.json](acceptance-results.json).
- Parent: OpenAI Codex, `gpt-6-astra` / `xhigh`. Actual bounded actors and installed
  trial executor: `gpt-6.1-sol` / `low`, as explicitly selected for bounded work.

The source policies and accepted #454–458 criteria were fixed for review and
execution. GitHub read-back at approximately 2026-10-17 05:06 UTC found all five
Issues still open with the same `updated_at` values recorded in the criteria
snapshot. The first sandbox read failed to connect; the authorized normal network
read succeeded. That failed read is not a provider-state observation.

The original [workflow plan](workflow-plan.md) is preserved as the implementation
plan and its historical checkpoint. This report is the current entrypoint. Its
source scope, criteria and authorization are unchanged; later #459 clarification
is recorded separately below.

## Delivered behavior

| Issue | Local result |
| --- | --- |
| #454 | Optional Context Map guidance supports synchronous/asynchronous/no interaction, explicit model sharing and contract ownership without a universal broker or storage-layout mandate. Current manuals and exact versions are synchronized. |
| #455 | BDD guidance is split into discovery, formulation, automation, Gherkin and a concrete example, with task-specific entry points and optional installed consumption. |
| #456 | DDD guidance covers domain discovery, strategic/tactical design, model evolution and an example. Language, invariant ownership and external confirmation remain separate from transport and deployment choices. |
| #457 | `test-designer@0.4.0` is the canonical owner for general/GWT/formal test design. `spec-author@0.2.0` retains production/entity/adapter specification. Explicit skill/resource ID migration preserves accepted content and rejects obsolete selection. |
| #458 | `requirement-author@0.2.0` adds bounded exploration while preserving direct draft/normalize. Orchestration, architecture and implementation handoffs follow the selected semantic owners without a mandatory author pipeline. |

`engineering-common@0.3.0` contains the new optional resources.
`dotnet-backend@0.1.3` changes only metadata/exact dependency closure. No managed
source-project installation was upgraded; its installed entries remain separate
from the newly developed package. Historical target-specific role documents and
problem-frame-author behavior were preserved.

## Checks and independent review

The final source command `python -I -B tests/run.py` passed **243 tests**, with
zero errors, failures or skips, in **69.102321 seconds**. The exact result and raw
log hashes are in [source-suite.json](evidence/source-suite.json). No test or loader
contract was weakened, and no product tests were added merely to mirror prose.

Independent `/root/bdd_immutable_review` reviewed base through `893bcb9d` using
the installed code-reviewer and source policy rule 6. It identified two low
findings: an extra EOF blank line and a stale common-resource count. The author
repaired both; the reviewer re-executed the affected checks at `c9057655`, verified
the complete base-to-source `git diff --check`, and found no new supported defect.
All other 3,137 tree entries and governing criteria/methods were identical between
those two review heads. Unchanged review conclusions were reused only with that
proof. [Independent review record](evidence/independent-review.json) binds the
original report hashes, findings and dispositions; the reviewer did not claim to
have run the parent's source tests, installation trials or actors.

The final report commit changes only workflow evidence/status. The selected
source/docs/tools/tests/authority/criteria tree contains 609 entries with SHA-256
`d740ec1245bd34f2f2871694ce80f529c248f55ad192a2e942af46fa66708fdd`.
[Frozen subject](evidence/frozen-subject.json) declares the exact paths and hash
method (`git ls-tree -r <commit> -- <selected paths>`, raw stdout bytes). Current
terminal HEAD must be rebound to this same content; a record commit is not a new
source-test or review execution.

## Actual isolated installation and update

The fixed-source main trial took **204.684596 seconds**; the separately selected
prefixed update took **63.248148 seconds**. Both completed with exit 0 and no
timeout. The executor guarded clean fixed source before each step, used separate
packaged processes and returned a completion callback. No tracked source changed
while these checks or actors were active.

| Case | Actual result |
| --- | --- |
| A | Four skills plus common knowledge, original naming, Codex and Claude entries: fresh installation/read-back; 33 resources and 58 payloads identical to fixed source. |
| B | Three skills, no knowledge, prefixed naming, both adapters: fresh installation/read-back; zero resources and 16 source-identical payloads. |
| C | Retired `bdd-gwt-test-designer` selection rejected with `blocked / selection-unavailable`; rejection is the expected negative-case result. |
| E | Deliberate owned-file drift rejected with `conflict / owned-drift`. Only the fixture's exact original bytes were restored before the normal update. |
| D | Old baseline original consumer updated to the fixed new source: 33 resources, 47 source-identical payloads, explicit resource-ID mapping, unchanged handoff binding and two custom-content hashes preserved. |
| D2 | Equivalent prefixed update: both new entries are `aicf-test-designer`, both old entries absent, resource mapping/bindings/custom hashes preserved; 33 resources and 47 source-identical payloads. |

Exact commands, driver hashes and the one-execution authorization are in
[installed execution binding](evidence/installed-execution-binding.json).
[Installed trial records](evidence/installed-trials.json) retain step argv,
durations, actual responses summarized by case and raw summary hashes/locations.
Raw requests, responses, locks, plans and engine pins remain under
`C:/mk-c9057655`; the earlier trial remains under `C:/mk-893bcb9d`.

These are synthetic, unpublished `0.0.0` consumers under Windows inventory-only
mode and process-termination durability. Both adapter installations were tested;
Claude's native runtime was not invoked. The old F-drive build was read-only and
was not refreshed. No real project's installation, release asset or global Temp
setting was changed.

## Actual actor results

Each actor started without parent conversation turns, received only its fixed
prompt and verified installed consumer inputs, and could write only its ignored
output/receipt. Parent expectations were not supplied. The eight actual outputs
and receipt text are preserved under `evidence/actors/`. Git's configured newline
normalization changes CRLF to LF where applicable; actor verification records both
the original raw hashes and archived Git blob hashes. Prose and receipt values
are unchanged. The parent separately read the outputs and assessed the predefined
expectations. [A7 handoff](evidence/A7-handoff.json) preserves the exact supplied
text, including escaped original line endings, and its digest.

| Case | Actual bounded result | Knowledge bodies read |
| --- | --- | --- |
| [A1](evidence/actors/A1.md) | Exploration keeps R1/AC1, refusal and unchanged date; asks a small owner-policy question batch; overdue/no-reservation outcomes remain unknown. | Discovery + collaborative discovery: 2 |
| [A2](evidence/actors/A2.md) | Direct formal decision-table design preserves T-valid/T-invalid, source-derived boundaries and independent oracles; no BDD requirement. | 0 |
| [A3](evidence/actors/A3.md) | Compares separate/combined model responsibilities in the required monolith; protects local I1 without claiming external refund confirmation or inventing policy. | Five relevant DDD resources; no model-evolution or unrelated library |
| [A4](evidence/actors/A4.md) | Absent knowledge still permits bounded GWT handoff; R1/AC1/S1 and both observations preserved, package coverage unavailable. | 0 |
| [A5](evidence/actors/A5.md) | Explicitly required installed DDD coverage remains unmet; supplied-fact language analysis can continue. | 0 |
| [A6](evidence/actors/A6.md) | Requirement draft/normalize and production/entity/adapter drafts preserve R1/D1/D2, REQ-7/AC-a/AC-b/Q9 and unknowns. | Formulation + domain discovery: 2 |
| [A7](evidence/actors/A7.md) | New context reconstructs goal, decisions, unknowns, next step and authority from actual A1 output, with no original chat. | 0 |
| [A8](evidence/actors/A8.md) | Direct GWT notes preserve refusal and unchanged-date oracles, local scenario identity and unknown policies without forced rediscovery or Gherkin. | Formulation only: 1 |

The parent authenticated every recorded installed-content hash against current
bytes and lock inventory, and every loaded knowledge resource against exact
versions, operation allowlists and matching selectors/bindings. All starting and
ending locks match. A7's supplied handoff hash matches the actual A1 output.
[Actor verification](evidence/actor-verification.json) distinguishes installed
resource counts from loaded-body counts and records the parent judgments.

Receipt limitations remain visible: some initial metadata outputs were oversized
and truncated; these listed metadata and did not read the referenced knowledge
bodies. A4's raw `installed_resource_count=22` labels the inventory-file count;
the authoritative reader contains zero knowledge resources. The parent records
both counts explicitly without overwriting that original receipt. These cases
support the selected observations, not general model reliability. A5's correct
unavailable result satisfies the negative-case expectation; it does not turn the
missing required coverage into a pass.

## Retained failures and unexecuted surfaces

[Document checkpoint](docfix-checkpoint.md) and
[integration checkpoint](integration-checkpoint.md) retain earlier version-closure,
YAML alias/order, sandbox Temp/cleanup, unsupported CLI argument and preset-order
failures. The first `893bcb9d` catalog trial failed its path budget before any
consumer install; a new explicitly selected short root resolved the environmental
path constraint without changing product limits. The successful older trial
remains bound to its older source; final actors used only `c9057655` consumers.
The original independent whitespace failure also remains recorded.

Hosted CI, push, PR creation, merge, Issue closure, Project completion, tags,
release publication, native Claude execution, native recovery matrices and real
downstream adoption were not performed. No local pass substitutes for those
states. Issues #454–458 have local evidence ready for a separately authorized
integration step; #452 keeps its prior distinct delivery history.

## #459 clarification and next work

During this workflow, the owner clarified that PRD/Feature work belongs with
requirement-author and that Story planning/authoring plus individual-AC review
needs an independent skill. #459 was updated while preserving its original A/B
discussion. It remains outside this implementation subject.

The reviewed owner-supplied template discussions contain user-value, business-rule
and technical Description structures with separate ACs. The applied example in
the second discussion uses flexible Expected Behavior/Business Rules headings;
it is not a fourth compulsory template. Example financial amounts/dates are
illustrative, not accepted business policy. Private chat identities stay outside
this source record.

The proposed #459 interface is `user-story-author` with plan, draft, normalize and
review, where review can select a whole Story or individual AC IDs. That spelling
and operation design are proposals, not an installed route. Caller-selected
templates should take precedence over defaults; single-AC review should assess
meaning, traceability, ambiguity and observable acceptance without forcing Story
rewrites or test design. #460 remains a separate Problem Frames proposal. No new
Story skill or Problem Frames capability was implemented by this workflow.

Next owner: the coordinator/user selects the separate #459 design/implementation
step or authorizes GitHub integration of the completed #454–458 local work. This
record grants neither authorization by itself.
