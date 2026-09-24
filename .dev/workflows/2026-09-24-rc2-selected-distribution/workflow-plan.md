# RC2 selected distribution implementation

Issue #406 / program #322. Assigned baseline 238f58bede46a8466699b5f9cd2307acb7155ac0.
Owner: slice-implementer, generic mode; sole writer of the assigned S3 worktree.
Scope: distribution excluding S4 renderers; presets; maintenance bootstrap; selected builder entrypoints; two RC2 tests and direct engine-source test; this workflow only.

Implementation is in progress. Acceptance is S3-A1 through S3-A10 from Issue #406.
S1 contracts and accepted S2/S4 handoffs remain read-only authority.
No source adoption, target mutation, push, PR, merge, publication or CI restoration.

U001: direct UTF-8, JSON/YAML, AST, link/member/hash, Git/scope/diff and exact commit-message checks only. Parser, builder, installation, recovery, runtime and test execution remain deferred-by-owner to the program coordinator / S6 / P7.

Initial identity: matching assigned branch and baseline; clean.
Graph: indexed framework_rc2_406 without persistence; tools excluded and scoped regex discovery returned no results. Explicit tracked-file fallback used for shared semantic and caller inspection.
Failure history: an attempted coordinator callback was rejected by automatic approval review for missing destination disclosure authorization. No message was sent. No repository mutation or behavioral execution occurred before this record. A suspected regex discrepancy was resolved by direct code-point inspection: the S1 version patterns contain one backslash per literal dot and agree with prose.

## Implementation checkpoint

Catalog/subset shared readers, exact metadata-4 branch, explicit presets, engine-2
bootstrap/bundle, four API-2 operations and paired project-intent recovery have been
authored. The new artifact CLIs accept independently selected engine pins and run
through retained verified source bytes. Narrow S6 cases are authored, not executed.

Actual direct checks so far: changed Python AST and UTF-8 readability; JSON/YAML
parsing; S2 raw handoff hash; all 235 accepted S2 Git member hashes/sizes; preservation
of all eight preset skill/adapter choices; read-only S4 renderer/template raw bytes
match Git; git diff --check; exact checkpoint message validation. No behavior pass.

Failure history extension:

- Automatic approval review rejected the first engine/API/lock/maintenance edit
  batch; none of that batch was applied. The user then directly replied
  "核准上述 #406 有界實作" to the exact scoped question. The same bounded core edit
  was subsequently admitted and applied.
- Automatic approval review rejected a CLI batch because its --save-selection
  option added a separate configuration-writing capability. That batch was not
  applied. The safer accepted implementation omits the option entirely; presets
  return explicit data and project config saving uses authorized paired intents.
- No outgoing callback is retried. Coordinator receives normal local handoff/readback.

Accepted #407 dependency is to be received only after this clean local checkpoint:
producer b4dfe1cbc60193f3cb84b3ee8b427e871b063fdc; coordinator receiving commit
2ea6884701b92760266a610c1caede0ebf13201e; handoff raw SHA-256
1d9a6bc06efd27dab6a29ead3082863fcf3fb1b72d27e7c17baf03919f550dbb.
Receiving that exact source/workflow commit is explicitly assigned by the coordinator;
S3 authors no consumer or shared coordinator files. Only owned manifest rows are
updated afterward. Final source/consumer closure and checks remain pending.
