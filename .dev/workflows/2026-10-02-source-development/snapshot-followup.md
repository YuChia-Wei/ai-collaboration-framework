# Snapshot regression correction

PR #428 merged as `cb1e04792d935269780de5bd7eb7077d6b6a438f` after final-head
Source change gate [36972030225](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/36972030225)
passed 223 tests in 48.512 s, with independent review and live admission read-back.
Local and remote main matched the reviewed/tested tree. #369/#427 closed and
Project Done were observed. The later automatic snapshot
[36972231337](https://github.com/YuChia-Wei/ai-collaboration-framework/actions/runs/36972231337)
failed before artifact creation. Source CI success is preserved; snapshot success
must not be inferred from it.

The retained builder diagnostic artifact `11212336138` reported public builder
`invalid-shape`. Direct source tracing and the production `ordered` check exposed
two defects introduced by init's manifest insertion: component identities were
not sorted by `(kind, id)`, and init's member rows were not sorted by source path.
Existing lightweight declaration tests checked closure and shape but missed those
builder preconditions. The builder's fail-closed contract remains correct.

T6/#427 reopens delivery under the owner's existing repair-and-validate instruction.
Use branch `codex/2026-10-02-source-delivery-fix` from merged main and this same
workflow. Reorder only the new component and its members; do not change package
bytes, versions, selected presets, builder behavior or pipeline authority.
Add one in-place source-declaration test using the real production ordering
function for manifest components, adapters, profiles and each component's members.
The test creates no installation, candidate, Git fixture or large I/O workload.

Before repair, the distribution suite ran 36 tests and reproduced exactly two
errors (components and ai-context-init members), with no skips, in 2.494 s.
A repair helper then failed before mutation; the shell nevertheless repeated the
same 36-test failure (2.466 s). After correcting the helper and applying the
manifest repair, all 36 tests passed with zero errors, failures or skips in
2.415 s. All three outputs are retained; the failed helper attempt is not a pass.
Independent affected review and actual final-head Source change gate are required
before the correction PR merges. The subsequent main snapshot must be read back
separately before #427 is closed again; keep it referenced/deferred in that PR.
No tag, public release or downstream installation is selected.

## Additional committed-input verification

Independent reviewer `source_cutover_review` found no supported actionable
findings on e6a701da2e65603d6d06b901ffedc3ffa355cff3. The affected gate on that
commit passed 78 tests (42 schemas, 36 distribution), content and whitespace in
18.889 s. Those results cover their stated scope only.

A separate production `build_catalog` invocation with physical emission replaced
by a capture boundary proceeded beyond the manifest checks but failed in
`parent_documents`: the new project-initialization preset's adapter list was also
unsorted. This was a real committed-input failure, not a physical build result.
Extend the source test to check preset skill/knowledge/adapter ordering and adapter
member ordering with production `ordered`. It reproduces exactly one error for
the new preset (36 tests, 2.431 s). Reorder only that list; preserve its membership.
Root authorizes the changed-input rerun under the same bounded repair task.
A new immutable review, gate and catalog pre-emission check supersede the earlier
subject for merge admission; final provider evidence belongs to PR #429 and #427.

After the preset repair, all 36 distribution checks passed in 2.460 s, with
zero errors, failures or skips.
