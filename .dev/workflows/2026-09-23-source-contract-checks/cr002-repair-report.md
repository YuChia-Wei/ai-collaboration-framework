# Issue #368 CR-002 affected repair

The bounded CR-002 repair and selected execution are complete locally: all six
methods passed once on clean source commit
`698654d77c81d2837c45e9e156e76d67734f6a28`. Original #370 affected independent
re-review and coordinator integration remain pending.

## Authority and subject

Continue the original assigned worktree/branch from
`6d9184e8e01d826131d03dd603422b5a3a1a7e4a`, the #370 review delivery for
`ae40e6cb0d49cdfb8e2174c732d74e1d918d0c2f`. The
[owner continuation](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/368#issuecomment-5800095738)
was read live; its exact body, timestamp and digest are in
[the bounded record](cr002-checks.json). U001 remains applicable.
The original declared Astra/ultra conversation is retained; no separate agent,
task or callback. This is declared provenance, not independent runtime attestation.
`local-change-implementer` owns the one private source predicate change;
`ai-context-governance` owns these proportionate existing workflow records.

## Change and preserved boundaries

The error-1 fallback now queries the selected drive's current DOS mapping and
requires one direct local device spelling plus an admitted local drive type,
using the existing maintenance/bootstrap predicate. Microsoft documents
[the current mapping as the first returned string](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-querydosdevicew)
and [the drive-type return values](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getdrivetypew).
The query has a fixed 32768-character buffer; zero or out-of-bound lengths,
directory mappings, remote/unknown types and query errors refuse admission.
The helper is private stdlib code in the existing `git_source.py`; it adds no
engine file, dependency, backend guarantee or filesystem mutation.

Only the Windows error-1 arm changes. Original absolute/traversal/segment rules,
all-ancestor link/reparse refusals, usable and stable identities and other-error
refusal remain. Assembly containment/allocation, hardlink protections and
read/output budgets retain their source bytes. PR/local-backlog metadata retain
their existing alias-expanded bytes and semantics; no metadata edits occur.

Two new methods simulate Win32 inputs. They admit four direct local drive types,
refuse directory/root aliases and malformed/unavailable mappings, and model
`X:` pointing to the proper descendant `F:/source/subdir`. Assertions establish
that lexical and visible-ancestor identity checks alone omit the repository root.
The real assembly control flow must refuse both output and scratch inputs before
`OwnedDirectory` allocation; source selection is explicitly stubbed in that
test. No actual SUBST mapping, native reproduction or settings changes.

## Selected execution and handoff

After the minimal source commit, run the existing contracts runner once with
`PathAdmissionTests` (five methods) and the existing actual C5 Lesson
assembly/reader method. Use only `F:/framework-next/p7-runs/368-contracts`,
90 seconds outer timeout and unchanged 256-file / 16-MiB / 256-visible-process
ceilings. [The capture script](evidence/cr002-capture.py) is the earlier
one-shot raw-stream/evidence capture adapted to this selection, not a new
product/public/native driver. Preserve all old failed roots and raw streams.
Stop after failure, timeout or evidence loss; no unchanged retry.

C-001 is unverified and excluded. All other legacy/full/native/provider/CI
acceptance remains `deferred-by-owner`: program #322 coordinator / P7.
Source repair, selected execution, independent review, integration and Issue
closure remain separate. Coordinator owns first integration; the original #370
owns affected re-review. #368/#370 remain open; no push or provider mutation.

## Actual execution and evidence

- Executed/source checkpoint: `698654d77c81d2837c45e9e156e76d67734f6a28`.
- Starting review delivery: `6d9184e8e01d826131d03dd603422b5a3a1a7e4a`.
- Source tree: `29e9dc1c1d66e59ec55a87d0c135d00f78235e7a`.
- One attempt, six passed, zero failures/errors/skips, exit 0.
  Unittest: 7.216 s; capture child command: 7.488 s; outer limit: 90 s.
- Five path methods include four simulated admitted drive types and 14 simulated
  refusal inputs, plus source-descendant output/scratch refusal before allocation.
  Existing direct-path, link/reparse, identity-drift, other-error and containment
  assertions also passed. Simulated results are not native alias reproduction.
- Actual C5 assembled Lesson twice, 13 files per candidate, then exercised the
  actual candidate reader and its five labelled synthetic corruption refusals.
  Candidate identity:
  `development:698654d77c81d2837c45e9e156e76d67734f6a28:0cca4a6ed0413b629f1cc0f09006b89b554267317370b172a3a29853d62da5ac`.
- Measured before cleanup: 52 observed file names / 573594 logical bytes;
  51 retained files / 573583 bytes; 26 helper-authored bytes. Parent fixture
  process counter: 89 Git processes. Including the runner gives 90; adding
  the capture Python and its seven Git reads gives 98 known launches within
  this capture. These are bounded observations, not global I/O/process totals.
- All three historical #368 failure roots and the named #373 PR failure root
  retain identical path, identity, attributes, size, mtime and content inventories.
  New successful root `fn-ca5616d76af342efab7d7f3a58aad07f` is absent after cleanup;
  no new failure residue. Historical failures are neither deleted nor relabelled.

[Exact capture](evidence/cr002-execution.json) retains the complete original
stdout (1758 bytes) and stderr (999 bytes) as base64 with SHA-256 digests,
before/after inventories, argv, runtime and executing-file hashes. The original
ignored `.bin` files remain at the recorded capture directory. The readable
[stdout](evidence/cr002-selected.stdout.txt) and
[stderr](evidence/cr002-selected.stderr.txt) normalize CRLF only; exact bytes
remain in the capture. All 11 bound execution files still match the planned
hashes. Python 3.13.14 / PyYAML 6.0.3 / jsonschema 4.26.0 / referencing 0.37.0 /
Git 2.55.0.windows.3 were read back; no runtime settings were changed.

Direct AST/JSON/YAML parsing, changed local-link checks and `git diff --check`
passed. Assembly and both metadata files equal the review-delivery bytes.
Removing only the added private helper/call and changed docstring restores the
exact prior GitSource source. These are preservation checks, not fresh execution
of every hardlink/read-budget or metadata contract. No full 22-method pass,
current replay of the earlier eight core assertions, native maintenance,
publication, target acceptance, CI restoration or independent review is claimed.
The delivery commit contains only this workflow's result/status evidence; source
and test bytes remain those of the executed checkpoint.
