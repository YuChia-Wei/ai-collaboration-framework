# Issue #370 CR-002 affected re-review

**CR-002 is resolved in the reviewed source. No new substantiated finding.**
C-001 remains an unverified casing hypothesis and was not selected for repair
or renewed investigation. This conclusion is source review, not native acceptance.

- Fixed delivery/start: `af5c4e39e193ef9cd161f203a5da211cfd95f7bf`.
- Worker execution checkpoint: `698654d77c81d2837c45e9e156e76d67734f6a28`.
- Prior review delivery: `6d9184e8e01d826131d03dd603422b5a3a1a7e4a`.
- Assigned root/branch: `F:/framework-next/370`, `codex/2026-09-24-current-engine-review`.
- Scope: coordinator's [CR-002 continuation](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/370#issuecomment-5800331565), U001, same independent Astra/ultra conversation; no agents, nested tasks or callbacks. No provider command was run for this continuation.
- Common `code-reviewer` reasoning, proportional `ai-context-governance` records; no technology-specific .NET or formal audit gate is claimed.

## Source binding and disposition

[Bounded evidence inventory](cr002-review-evidence.json) records exact raw
SHA-256 and Git blobs for all eleven execution files and selected worker records.
Checkout/delivery/execution-checkpoint raw bytes agree. Within the ten-file
EnginePin closure only `src/distribution/git_source.py` changed since the prior
review; the other nine and `assembly.py` are byte-identical. No installed target
or old full EnginePin is implicitly updated by that statement.

The revised [direct_directory](../../../src/distribution/git_source.py#L44)
invokes [the private helper](../../../src/distribution/git_source.py#L28) only
inside Windows error 1, after usable ancestor identities and before final
identity recheck. It queries the selected drive, requires a successful bounded
response whose current mapping has exactly a direct device form, and permits
only drive types 2/3/5/6. Directory mappings such as `\??\F:\source\subdir`,
device subpaths, remote/unknown mappings, zero/oversized responses and query
errors cannot reach successful admission. The first response string is the
current mapping per [QueryDosDeviceW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-querydosdevicew).

For the original source-admitted example (repository `F:/source`, `X:` mapped to
`F:/source/subdir`, output `X:/out`), refusal now occurs before the unchanged
[output_parent](../../../src/distribution/assembly.py#L60) containment checks.
The unchanged [_assemble](../../../src/distribution/assembly.py#L142) admits both
output and scratch before its first `OwnedDirectory` allocation. The same guard
also applies to GitSource root admission. This closes the specific descendant
alias gap without trying to infer omitted ancestry or changing a drive mapping.

AST comparison of the entire GitSource module, after removing only the new
helper/call and restoring its docstring in memory, equals the prior module.
Absolute/traversal/segment rules, direct-directory/link/reparse checks, usable
and stable identities, normal strict resolution and non-Windows/other-error
refusal therefore retain their prior implementation. Assembly allocation and
containment, the nine unchanged engine files, and both PR/local-backlog metadata
files retain exact bytes; no hardlink/read/output budget or loader change is
introduced. This is preservation evidence, not fresh behavioral coverage of
every unchanged guard. Host integrity and external concurrent writers remain
outside the existing supported contract.

## Focused test and receipt assessment

The explicitly named test/capture files were inspected as text and AST because
the bounded distribution graph does not cover them. Existing test method ASTs
are unchanged. The two added methods and one helper provide meaningful evidence:

- `test_simulated_windows_drive_mapping_refusals` calls the real predicate with
  mocked Win32 responses. It covers four admitted local types, fourteen refusal
  inputs including query failure, and verifies selected drive/buffer arguments.
- `test_simulated_descendant_drive_alias_refused_before_allocation` assigns
  different repository/subdirectory identities and explicitly establishes that
  the visible alias ancestry omits the repository root. It calls real
  `output_parent`, then real assembly control flow with immutable selection
  stubbed and `OwnedDirectory` replaced by an allocation sentinel. Both output
  and scratch must raise the mapping diagnostic, and allocation must remain
  uncalled. Removing the new refusal would make these assertions fail.
- The existing C5 calls real assembly twice and real candidate readers, checks
  all emitted bytes/inventory and independently recomputed candidate identity,
  then applies five labelled synthetic corruptions with restoration/read-back.
  The new Win32 alias cases are simulations; C5 does not create a drive alias.

The [worker report](../2026-09-23-source-contract-checks/cr002-repair-report.md),
[checks](../2026-09-23-source-contract-checks/cr002-checks.json) and
[exact capture](../2026-09-23-source-contract-checks/evidence/cr002-execution.json)
consistently record one attempt, six named methods passed, zero failures/errors/
skips and exit 0 on the execution checkpoint. Two actual Lesson builds each
had thirteen files; five corruption refusals remain synthetic. Reported timing
is 7.216 seconds unittest / 7.488 seconds captured command. These are attributed
worker observations, not tests run by this reviewer.

Independent data checks established: eleven recorded execution hashes equal
Git/checkpoint/checkout bytes; decoded base64 streams match their SHA-256 and
1758/999-byte sizes; readable copies differ only by CRLF normalization; decoded
JSON lines equal the recorded observations; six named `ok` lines and the final
unittest result agree. All four committed historical before/after inventories
match recursively with exact types. Their 142/27/27/44 entry counts, source tree,
head/clean-state fields and summary bindings are internally consistent.
The capture script was read and parsed, never imported or run.

The committed evidence supports the worker's bounded claims. The original
ignored `.bin` files and historical roots were **not** reread live here; current
physical preservation/cleanup is not independently attested. No whole-suite,
current native alias reproduction, full maintenance engine, target, publication
or CI pass follows from these receipts. No additional execution was performed.

## Review checks and handoff

Fresh nonpersisted fast graph `issue370-cr002-repair`: 13 File nodes, 231 nodes /
1560 edges, zero skipped. Search/snippets and inbound trace cover the predicate
and direct producer callers. Raw Git comparison and stable HEAD bind discovery;
the graph itself supplies no commit attestation. Direct UTF-8/AST, exact source
preservation and receipt parsing/hash checks passed without product/test imports.
Final record/link/scope and full planned-message results are in [task.json](task.json).

Only this report, [bounded evidence](cr002-review-evidence.json), existing task
and workflow change. [Original review](report.md), [loader review](affected-review.md),
[current-engine review](current-engine-review.md) and its hash inventory retain
their exact prior raw bytes. Artifact identity is the containing commit of this
report; resolve `git log -1 --format=%H -- .dev/workflows/2026-09-23-installation-source-review/cr002-affected-review.md`.

Coordinator `01a0ce78-db26-74e1-a615-2bd0599f7d0c` owns first transport, repair
and Issue dispositions. No further source correction is identified in this
bounded re-review. C-001 stays unverified; native/target/policy/CI/publication
remain separate. Unselected legacy/full/formal/hosted gates remain
**deferred-by-owner**, U001, program #322 coordinator / P7. No push, provider,
source/test, runtime-setting or credential mutation occurred.
