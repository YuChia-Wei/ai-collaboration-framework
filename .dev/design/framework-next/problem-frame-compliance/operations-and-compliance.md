# Operations, evidence and target compliance

All interfaces below are proposals. No commands shown here were executed.
Package implementations must preserve the four distinct outcomes below.

| Boundary | Responsibility | Cannot establish |
| --- | --- | --- |
| Authoring | Extract selected intent/observations; choose family; retain source bindings, external-system constraints and questions | Approval, successful parsing, implementation or compliance |
| Structural read/validation | Strict input/version/shape, uniqueness, references, package/path binding; return actual byte digest | Truth of a statement, source approval or code/test meaning |
| Semantic review | Check intent, authority, completeness, consistency, feasibility, GWT alignment, missing criteria and unsupported families | Actual target execution or authenticated approval from a field label |
| Target runtime compliance | Match complete selected criteria to code, assertions, real executions, environment and target gate | Broader correctness, unseen families/profiles or future revisions |

## Problem-frame-author public interface

Instruction operations are draft and review-draft. They require no Python or
configuration merely to return prose. draft takes one selected use case/family,
source references and authority, observations, optional explicit template,
desired format and authorized destination. It returns family rationale,
extraction sheet, full draft/payload, source bindings, uncertainties, omissions
and actual delivery location. Code-only recovery remains observed/inferred;
missing intent never becomes normative. review-draft critiques the selected
artifact and gaps without writing, approving or claiming runtime compliance.

Tool identity is proposed `problem-frame-author.fs`, entry
`scripts/problem_frame.py`. Invoke one operation with `--request <absolute
JSON file>`; do not evaluate request strings as shell text. The CLI protocol is
not a new persistent record family or shared runtime. It accepts only a closed
object matching the selected operation, produces one JSON response and uses
nonzero exit for non-ok results.

Common request fields: project_root, package_root; optional project_config,
local_config, overrides, write_roots. Defaults/constraints are exactly the
configuration contract, not authority inferred from destination. Unknown keys,
duplicate keys, nonfinite values and wrong types fail. No shell command,
provider, approval or runtime credential is an accepted request field.

| Operation | Additional request fields | Result / mutation |
| --- | --- | --- |
| explain | none | Effective own settings, field origins, exact supported family/version and missing operation prerequisites; no store creation |
| create | reference, record | Complete supplied record; validate and publish once; return raw digest, reference, structure result and publication state |
| inspect | reference, optional expected_sha256 | Read exact existing snapshot; structure result, record, digest, complete criterion IDs/pointers; no write |
| validate | reference, optional expected_sha256 | Same actual structural validator and digest, with diagnostics; no semantic/runtime claim |
| render | reference, optional expected_sha256 | Same owner read/validation, selected inert template, complete result-only Markdown; no export write |

No query, revise, status transition, migration, delete or execution tool is in
the first version. create's record.id and reference basename must agree; no
identity allocation is hidden in serialization. Serialize with sorted object
keys, two-space indentation, UTF-8 without BOM, LF and one trailing newline;
preserve array order and Unicode text. Digest is over actual persisted bytes.
Read-back compares exact bytes. Formatting canonicalization at creation does not
normalize source meaning.

Response envelope fields: operation; outcome; changed (boolean or null when
unknown); mutation_state (none/published/uncertain); reference (nullable);
subject_sha256 (nullable); result (object or null); diagnostics (array of
code/location/message); residue (array of known contained operation-owned
temporary references). outcome is ok, invalid-input, unsupported-family,
unsupported-version, unsupported-format, conflict, blocked, unavailable or
io-error. Exit codes: 0 ok; 2 invalid/unsupported; 3 conflict/blocked; 4
unavailable/io-error. Diagnostics use logical input locations rather than
unrelated absolute paths. A success response cannot contain a fabricated runtime
or compliance result. Absence of a dependency is unavailable, not invalid input.
Readers never create directories or rewrite unsupported records.

Python >=3.11,<4, selected YAML metadata support and JSON Schema Draft 2020-12
validation support apply only to tool operations. Future exact package metadata
must declare actually used libraries, not an unused dependency. The schema
uses only contained #/$defs references; disable remote resolution. Content
validation performs bounded shape and reference checks only; no network,
recursive source scan, target build or analysis language execution.

## Spec-compliance-validator public interface

This package owns instruction operations only, configuration:null, no tool,
record schema, store, artifact roles or machine templates. A prose report
outline is an ordinary packaged reference. Required/optional package dependency
arrays stay empty: select an actual format reader as an operation input, not a
mandatory authoring workflow. For the new CBF family, that reader must be its
owning problem-frame-author tool and exact schema version. Missing owner tool
means structural validation unavailable. No copied private validator is allowed.

| Operation | Inputs | Complete output |
| --- | --- | --- |
| plan-validation | Explicit artifact/version or external format; selected intent/rules; target subject/scope; evidence requirements | Full criterion inventory, authority/uncertainty, applicability, target runtime prerequisites, proposed target-owned commands and gaps; no execution claim |
| review-semantics | Selected bytes/source bindings; real structure result if required; bounded code/tests when supplied | Meaning, completeness and contract/GWT alignment findings with criterion IDs and source/code/assertion locations; structural and runtime limits |
| assess-runtime | Fixed frame/rule/code/test subject, explicit target profile, authentic supplied runs or separately authorized real target execution | Per-criterion evidence matrix, actual command/environment/outcomes, missing coverage, scoped gate result and exclusions |

These operations may be composed within one task. They are not a forced
author -> implement -> validate pipeline. A useful result can be unavailable
runtime compliance plus specific semantic findings. No automatic remediation,
test creation, provider update, release gate or source workflow is implied.
If authorized target execution is requested, use the target-owned execution
surface and commands; otherwise assess supplied observations without rerunning.
Target safety/long-running requirements remain target authority.

## Evidence states and conclusion algorithm

The report binds: artifact family/version/raw digest and logical frame identity;
selected normative sources/revisions/digests and authority; target commit or
explicit content identities for relevant code/tests/config/dependencies; selected
profile/version; environment/SDK/test runner/provider; exact command/arguments,
working directory, observation time, execution result and accessible evidence.
Git absence is allowed with explicit file/content identities; neither an
unbound log nor test method name counts as a run on the selected subject.

Every criterion row contains ID and exact text; origin/authority; applicable
or excluded with decision/rationale; required evidence level; implementation
and assertion location; observed run/evidence reference; result; and limitation.
Non-runtime intent rules may require document/source evidence; runtime behavior
requires the actual target evidence level selected for that criterion.

Row results are satisfied, contradicted, unavailable, deferred or excluded.
A missing test/assertion in an accessible, completely inspected selected scope
can be contradicted; an inaccessible scope is unavailable. A skipped test
provides no satisfying observation. A deferred or excluded item never becomes
satisfied. Authoring/structure/semantic/runtime each have their own reported
stage outcome; a structure pass does not propagate.

Use separate stage findings and overall result so partial failures remain
visible. Compute overall runtime conclusion in this order:

1. Any observed contradiction in the selected required criteria means
   **not-compliant**, retaining unavailable/deferred rows beside it.
2. Without a contradiction, any missing authority, required runtime/profile,
   evidence, valid subject binding, structural result or unresolved required
   criterion means **unavailable**. Preserve the specific deferred label when
   an owner intentionally deferred a row.
3. If no applicable required criteria remain, return **unavailable** with an
   empty-scope explanation, never a vacuous pass.
4. Only when every applicable required criterion is satisfied using the required
   evidence and no unresolved required scope remains: **compliant-within-scope**.
   Name the scope, exclusions, versions, subject and observed environment.

Show counts by these states if helpful. There is no source-derived universal
100% score. A target may explicitly require all selected criteria; meeting that
gate must still be expressed within scope. Excluded criteria need real target
decisions and remain visible. Never lower the evidence level to convert a
missing real database/message-flow run into a unit-test pass.

A changed frame, intended rule, code/test/config/dependency subject invalidates
affected evidence. Reuse requires demonstrated matching subjects and applicable
environment/command; an old success is not evidence of a new invocation.
P7 restoration is source-program authority, never a downstream proof of behavior.

## Explicit optional .NET profile

The proposed bundled reference profiles/dotnet.md supplies intake and mapping
instructions only. Caller selects dotnet@0.1.0 explicitly; file extensions,
a .csproj or the legacy skill name do not activate it. Profile absence/unselected
means .NET-specific runtime assessment unavailable; portable semantic review
can still proceed.

Required inputs for a .NET runtime conclusion:

- Target-owned normative requirements, accepted architecture and testing/analyzer
  decisions with exact selected frame/criteria; no framework xUnit/BDDfy/
  NSubstitute, BaseTestClass, DDD, ORM or exception-type default.
- Explicit solution/project/test paths, SDK/runtime and runner/package versions,
  restore/build/test authority, actual permitted execution environment and
  selected commands. Missing SDK or executable projects is unavailable.
- Exact target code/test/config/package subject and result provenance; build
  outcomes plus criterion-linked assertion/execution results at required test
  levels, including real infrastructure when required.
- Explicit applicability of external authority, idempotency, timeout/retry,
  concurrency, persistence and message side effects. A passing unit test cannot
  establish transaction/outbox or external-system acceptance.

The reference may show placeholders for target-provided dotnet build/test argv,
but never chooses project paths, install/restore actions, library versions,
credentials, analyzers or infrastructure. Check input/handler signatures,
pre/post/invariant meaning, event attributes, errors and observable GWT
conditions against actual target choices. Awaitable event evidence is assessed
when events apply. Style and behavioral compliance remain distinct. A nonzero
build/test result is preserved even if other rows pass.

Other runtimes can supply an explicit target-owned profile with named authority
and evidence obligations; the first package claims no bundled specialist
coverage beyond the selected .NET instructions. Unknown profiles report
unavailable coverage, not a generic success.
