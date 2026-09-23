# Portable problem-frame and compliance design

Status: recommendation for coordinator selection, not an implemented or adopted
package. Issue [#351](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/351),
program #322, D342-06. Source baseline:
`731d658b6004110fd59224ca39aa3a5d63891d91`.
[Evidence](../../../workflows/2026-09-23-problem-frame-compliance-design/evidence/source-evidence.json)
pins the bounded tracked inputs; [provider observation](../../../workflows/2026-09-23-problem-frame-compliance-design/evidence/related-issues.json)
records the five Issues. No product operation was executed.

## Recommended first delivery

Select **CBF**, family **problem-frame.cbf**, exact record version **1.0.0**,
as one UTF-8 JSON snapshot per bounded command/use case. The proposed package
`problem-frame-author@0.1.0` owns its schema, semantic authoring instructions,
real create/read/structure-validation tools, version dispatch and unsupported
migration response together. Ship none as an available tool until the whole
bounded implementation exists.

Select `spec-compliance-validator@0.1.0` as a distinct instruction package:
assemble criteria, review meaning, assess supplied target execution evidence
and return a scoped conclusion. It does not duplicate the frame parser or
pretend that a keyword/filename check executes target compliance. The first
optional technology instructions are explicitly selected `dotnet@0.1.0`;
this is an instruction profile identifier, not a .NET SDK version or a global
distribution profile.

The proposed schema and example are design artifacts, **not schema-validated
fixtures**. Use [format-contract.md](format-contract.md),
[operations-and-compliance.md](operations-and-compliance.md) and
[implementation-handoff.md](implementation-handoff.md) as the complete bounded
implementation input. The coordinator must select D351-01 through D351-05
before assigning source work.

## Why CBF first, and what happens to SWF

| Git-tracked evidence at the baseline | Consequence |
| --- | --- |
| Authoring playbook explicitly prefers CBF and lists separate CBF/SWF file sets. | Preserve family selection; never relabel SWF as CBF for convenience. |
| The tracked problem-frame subtree has one concrete five-file CBF external-system template and semantic guidance. Its YAML has no independent record version. | CBF has a concrete extraction source; call the new version a new contract, not legacy v1 compatibility. |
| SWF is documented through workpiece/aggregate and requirements/*.yaml, AC coverage and optional entity contracts. No SWF template is present in the explicitly enumerated tracked subtree. | Preserve these responsibilities and historical documents; a concrete SWF writer/schema requires its own family decision and representative target input. This is a scoped inventory conclusion, not absence across all repositories/history. |
| Legacy artifact registry row 77 names the semantic author, with empty producer/validator arrays. | A registered artifact kind is not an executable structural validator. |
| Compliance references mix portable criteria with xUnit/BDDfy/NSubstitute, contract exceptions, path conventions and 100% language. | Carry portable reasoning forward; technology rules apply only from selected target authority. |
| check-spec-compliance.sh searches quoted name fields and matching .cs filenames, and ends with exit 0 even when components are missing. | Its output cannot establish CBF schema validity, complete assertions, C# semantics or a runtime pass. Do not port it as the new validator. |

## Alternatives considered

| Option | Useful result | Cost/limit | Recommendation |
| --- | --- | --- | --- |
| Schema-free CBF/SWF prose with explicit caller template | Immediate drafting and semantic review; no Python/config/store needed | No deterministic criterion identity/reference checks or reproducible machine input; explicit unsupported structural validation | Retain as an instruction fallback for a requested prose artifact or external format. It must not masquerade as the selected structured family. |
| Preserve five-file legacy CBF YAML and add tools | Familiar layout and rich original fields | Unversioned inputs, distributed identity/reference updates, YAML dialect and multi-file recovery; SWF remains a different file set | Preserve legacy bytes and read selected sources as prose. Do not adopt this as the first writable machine contract. |
| One new CBF JSON snapshot with typed statement/assertion IDs | Useful structural checking and bounded creation; simple criteria extraction and exact byte binding | Explicit new-format selection; semantic review still required; no automatic historical conversion | Recommended first structured family. |
| CBF+SWF generic frame engine or shared runtime | Potential future reuse | Premature abstraction, more schemas/migrations and target semantics without demonstrated need | Deferred; no new common runtime or registry. |

## Retain, exclude, defer

Retain actor/command/controlled-domain boundaries; inputs, pre/postconditions,
invariants, outcomes/errors/events; source authority and observed/inferred
distinctions; external authority, duplication, retry/timeout and asynchronous
confirmation reasoning; scenario IDs, separate observable assertions, criterion
links and non-executed test anchors. Legacy FC1-FC6 are useful prompts for an
external integration, not six universally mandatory claims for every command.
Field semantics from SEMANTICS.md become explicit target statements where
applicable; the new core does not enforce CLR setters or aggregate architecture.

The first structured reader/writer supports only `problem-frame.cbf@1.0.0`.
SWF persistence, query frames, arbitrary family extensions, legacy YAML import,
in-place editing, finalized/approved/compliant flags, shared indexes, automatic
test generation, language AST analysis, provider activity and automated migration
are unsupported. No schema definition version is inferred from a playbook,
template or package version.

Deferred responsibilities remain visible: SWF workpiece/AC/entity-contract
authoring; legacy multi-file compatibility; optional evidence/report persistence;
additional runtime profiles; any target-specific enforcement implementation.
They are not deleted or silently counted as covered. Existing root routes,
legacy tools and historical bytes remain unchanged pending explicit P6/P7
disposition.

## User-visible behavior

A caller can request a sourced draft with explicit questions and receive it in
conversation without selecting a destination. Selecting the structured CBF
format enables an explicitly located JSON snapshot and useful field/version/
reference errors; the tool never approves requirements or certifies code.

SWF and legacy YAML stay available as original sources. The new reader reports
unsupported machine formats, while requested semantic review preserves their
meaning and format differences. A .NET runtime conclusion additionally needs an
explicit profile, target authority, environment and real evidence. Missing
prerequisites remain unavailable.
