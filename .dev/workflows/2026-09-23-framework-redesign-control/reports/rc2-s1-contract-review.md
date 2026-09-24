# S1 contract content review

Issue #401 / program #322. Accepted for bounded document integration:
`32a2b59dd38f9335f60cf2edd8eac4d6d95f95cf`, preserving original
`e27ff21cf06c91abdf5fde4f70c1bddb632b1898`. This is coordinator content review
under U001, not an independent audit, schema-compliance or behavioral pass.

## Acceptance and evidence

| Acceptance | Observed bounded delivery |
| --- | --- |
| S1-A1 | Exact desired-selection/content/catalog/subset/lock/engine versions, closed schema documents, canonical digest boundaries, dependencies and illustrative formats. |
| S1-A2 | Old/new read-write matrix, explicit unsupported writes, ownership and prefix transitions, paired managed/project-owned recovery. Correction preserves the legacy renderer/template and adds separate v2 seams. |
| S1-A3 | All 272 inventoried source paths/modes/blob IDs/sizes/raw SHA-256 values matched baseline Git objects. Complete 194-file .NET profile; 232 portable sources plus 3 new metadata/index members produce 235 unique planned members. |
| S1-A4 | Target 14-rule set matches inventory; four customizations and 20 route selectors are retained with fixed authority sources and coverage limits. No target gate was run. |
| S1-A5 | Explicit 21-capability inventory, 18 installed successors and retained legacy duties; exact S2/S3/S4/S5 ownership/interfaces and separately categorized S6 cases. |
| S1-A6 | Local commits, direct-check records, bounded completed document workflow and first-push handoff. Online integration remains separate. |

## Findings and disposition

- S1-R1: The original same-name renderer instruction could route legacy
  generation/verification through aicf output. Corrected contract preserves
  `codex.project_entry` and its old template, introduces `project_entry_v2`
  and `skill-entry-v2.md.template` for both new adapters, and assigns explicit
  format/API caller dispatch to S3. New source shapes in legacy write mode
  are unsupported-write; no field stripping or implicit --profile reinterpretation.
- Lifecycle alignment: completed workflow now has current_phase completed;
  local completion and pending provider integration remain separate fields.

Both corrections were inspected in the exact new diff. All five substantive
inventory/baseline documents retain their original reviewed Git blob identities,
so their deterministic comparisons remain applicable. The revised subject has
41 UTF-8 documents only under the two assigned roots; JSON/YAML parsing and
diff whitespace checks passed. New rejected runtime task/local-path identifiers
are absent from the proposed publication. The independent runtime and exact
local dispatch details remain local, outside this report.

The original delivery separately records 36 Markdown links and 52 schema-document
references checked; the correction records 21 links and two anchors. These are
direct reference checks, not schema compliance. The coordinator's initial attempt
to read an assumed adapter.yaml path failed; the actual legacy template was then
confirmed from the tracked manifest and Git tree. No absence claim followed that
preparation error.

## Limits and next work

Eleven unregistered guidance catalog hashes differ from the fixed source blobs;
S1 exposes both identities, and S2 must rebuild relocated metadata from actual
bytes. No rule ID or normative adoption is invented. Historical failures and
unreadable ignored target-fixture status remain in the S1 record.

No product parser, content migration, adapter implementation, installation, actual
runtime discovery, target gate, native execution or hosted validation is claimed.
Legacy/critical/formal/behavioral/hosted machinery remains deferred-by-owner under
U001, responsible owner program #322 coordinator/P7. The next concrete step is
online S1 integration followed by S2/S4; S3 then integrates their exact inputs.
The full rc.2 program and R1-R8 remain open.
