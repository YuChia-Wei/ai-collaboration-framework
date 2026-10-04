# Install-time model resolution extension

Owner authority is the 2026-10-03 follow-up asking for programmable selection
and the explicit 5.6 -> 6.x migration. The source installation slice stays under
Issue #434. No provider mutation, inference, credential creation, global setting
change, publication or downstream adoption is selected.

## Policy and compatibility

Canonical role model policy declares 6 Luna for translator; 6.1 Sol then 6 Sol
for the three former Terra roles; 6 Astra for the two former Sol roles. Codex
effort stays max / medium / high / xhigh as appropriate. Claude uses pinned
Haiku 4.5, Opus 5.5 and Fable 5.1 respectively. Luna/Haiku is a task-position
mapping based on current official model descriptions, not cross-provider
benchmark equivalence. Sonnet is a separately selected quality option; rumored
Fable versions are outside the candidate policy.

Selection v3 optionally binds normalized observations and resolved models.
Existing selections without resolution keep fixed defaults. Catalog/readback
recomputes approved candidate priority and exact rendered bytes; the lock
retains that selection, hashes and template binding. Project configuration is
saved only by an explicit caller edit. Published/installed earlier engines need
the new verified catalog/engine pair; no old released artifact is mutated.

## Completed evidence on first fixed implementation

Implementation commit: `b220256921736b17c86217ccfee8b2d4434b5bfe`.

- `python -I -B tests/run.py --suite distribution --suite schemas --suite source`
  passed 144 tests, no failures/errors/skips, 8.033738 seconds.
- `python -I -B .github/scripts/check-source-change.py --base afa04b19a1905c4a614a8242b98e5146b862ad69 --head b220256921736b17c86217ccfee8b2d4434b5bfe`
  passed 144 tests in 44.316 seconds. This is local source evidence; admission
  was not evaluated and independent review remained required.
- Live local Codex CLI app-server model/list succeeded without thread/turn or
  inference. The eight returned model IDs include the four approved GPT-6
  candidates and the preserved role efforts. Visibility is not inference access.
- `python -I -B artifacts/verify-model-delivery.py` completed actual full catalog
  assembly, independently pinned 24-file engine, source-free dual-adapter subset
  derivation, plan/apply/inspect and managed drift/collision/selection-tamper
  refusal. All 42 managed files match their inventory. Controlled synthetic
  observations force 6 Sol fallback; installation itself is real. Four custom
  settings/profiles remain byte-identical. Elapsed 113.618561 seconds; clean
  tracked state before/after. Isolated root `C:/Windows/Temp/m434-k5jg7uel`
  is retained, with no cleanup or adoption selected.

Ignored evidence: `artifacts/sub-agents-model-source-gate.json`,
`artifacts/sub-agents-live-codex-models.json`,
`artifacts/model-sub-agents-terminal.json`,
`artifacts/model-sub-agents-{physical,installation}-result.json`, and
`artifacts/sub-agents-model-attempts.md`. Terminal schema validation passed.

## Independent finding and affected repair

The existing authorized independent reviewer `/root/sub_agents_review`, using
the `bounded-general-worker` execution profile and `code-reviewer` owning route,
reviewed exact `afa04b19a1905c4a614a8242b98e5146b862ad69..b220256921736b17c86217ccfee8b2d4434b5bfe`
read-only. Review status failed with one P2 parser finding: eager evaluation of
the fallback id lookup rejects a model-only page; malformed scalar/row inputs
can raise uncaught AttributeError. No additional actionable defect was reported.
Its mocked reproductions are behavior failures, retained rather than replaced
by the parent suite pass. Parent accepts a bounded compatibility/parser repair.

Explicit identifier/effort validation and conditional lookup now reject malformed
inputs with ValueError, accept model-only and id-only pages, and keep the same
provider/model/effort policy. Updated distribution suite passed 53 tests before
the final strict-null regression addition. The repaired immutable commit needs
affected independent review and fresh gate/physical engine evidence. Prior
physical success remains pinned above; it is not an exact-new-head claim.

## Evidence boundaries

Claude API transport is tested using mocks, including explicit key requirement,
provider refusal, pagination and secret exclusion. No live Anthropic API key
was read and no API request/inference was executed. Claude subscription/runtime
availability remains caller-supplied observations. Source-project already loaded
runtime profiles and this session's agent execution identity are separate from
the reusable product's new defaults; no runtime adoption is asserted.
Hosted CI, merge, publication, native/P7 and actual role execution remain outside
this local source completion claim. Parent owns affected repair/review and final
local handoff; maintainer owns future provider integration and release selection.

## Corrected immutable completion

Corrected product: `d980df4cec53a884267cc6b323bf427d74a12b02`.
The final strict-null distribution suite passed all 53 tests in 4.538859 seconds.
Fresh full-delivery Source change gate (base
`37a588c8c0b6f5e760079c563e71d742af8f962d`) passed 171 tests in 64.088 seconds:
43 schemas, 53 distribution, 49 source and 26 platform, without failures,
errors or skips. Admission remains not-evaluated; native acceptance is a
separately selected owner obligation, not a local source-test pass.

Corrected physical command `python -I -B artifacts/verify-model-repaired-delivery.py`
passed in 130.869819 seconds against a fresh independently pinned 24-file engine.
All 42 dual-adapter managed bytes, collision/drift/tamper refusal, four custom
settings/profiles and clean before/after source state were checked again.
The fixed standalone engine also actually executed `--discover-codex-models`
and derived a new source-free subset with 6.1 Sol, 6 Luna and 6 Astra from the
local CLI catalog, without inference. Claude observations remain controlled
synthetic inputs. Retained isolated root: `C:/Windows/Temp/mr434-o64ujl1v`.
Ignored records use the `model-repaired-sub-agents` / `sub-agents-model-repaired`
prefixes, so the earlier b220 records and failed review remain intact.

The same independent reviewer accepted the P2 repair on the exact corrected
head, verified 36 file/authority preflight rows, and independently ran two
targeted parser tests (passed, 0.115 seconds). It inspected the parent source
gate and actual installation records without claiming its own full-suite run.
No remaining actionable defect was reported; parent disposition: accept.
T1/T2 and this local source workflow are complete. A record-only completion
commit receives a fresh current-head source gate and deterministic product
hash/review binding as handoff checks; these do not invent another implementation
stage or provider admission. Issue #434 remains open, with no push, PR, merge,
publication, downstream adoption, actual inference or cleanup selected.
