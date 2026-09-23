# Issue #370 affected-source review of CR-001

- Disposition: **CR-001 resolved in the reviewed source; no substantiated new source defect found in the affected delta.** Public-entry and native obligations remain open.
- Reviewed source/start: `0d29b9abf36804cb2587732232d807a1b754c3a0`; repair delta base: `fe6c63f87cb54e166fc796fd315f11e3c2212823`.
- Worktree/branch: `F:/framework-next/370`, `codex/2026-09-23-installation-source-review`; starting state clean, persistent common Git directory unchanged.
- Refs: [Issue #370](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/370), [repair Issue #371](https://github.com/YuChia-Wei/ai-collaboration-framework/issues/371); both read live as OPEN, no comments. The live #370 affected-review addendum matches this assignment.
- Original finding: [report.md](report.md) at `6de20bfeb059d74f1ba0ede96c28d312db04235f`, against `38e6458f8d3e81dc2568daf1fa467571fb529fee`; its bytes remain unchanged.
- Review artifact commit: containing commit of this file, resolved by `git log -1 --format=%H -- .dev/workflows/2026-09-23-installation-source-review/affected-review.md`.
- Created: 2026-09-23T15:51:31+08:00; updated: 2026-09-23T15:52:30+08:00.
- Method: same independent code-reviewer common route, ai-context-governance workflow and U001 adaptations as the original review. Coordinator-declared gpt-6-astra / ultra; no additional runtime attestation, sub-agents, callbacks or legacy review machinery. Template: code-review-assessment-report-template.md 1.1.0, adapted to this existing workflow.

## Fixed identity and exact scope

Only [src/tools/maintain_framework.py](../../../src/tools/maintain_framework.py) changes product bytes in the selected repair. New blob `8e7e8a225fac619e85258b73cc4aa488fdaf908c`, raw SHA-256 `8030be53ee2988e21628ad11f348ad18a5f4114a0fcdb79e96dc473e23bdcf3d`.

All nine distribution EnginePin files listed in the original report are byte-identical to that original subject. All ten checkout files equal this review's fixed commit. The repair base also equals the original ten-file closure. These comparisons used direct raw `git cat-file blob` output, not normalized checkout identity. No repeat review of unchanged installation/recovery logic is claimed.

Read [test_engine_source.py](../../../tests/framework_next/test_engine_source.py) (blob `0c231a23bb17957d804b46e311dadedff938e631`, SHA-256 `bfe916dc9f86c08b50549ed1b750b8a798c68c62f62f4ca96efd90ecad0ae249`) and the repair's [report](../2026-09-23-engine-source-pin/report.md)/[evidence](../2026-09-23-engine-source-pin/evidence.json) for coverage classification. Their bytes/hashes were independently bound to this fixed commit. None was imported or executed by this reviewer.

Graph discovery freshly indexed only `src/tools` as `issue370-entry`, fast mode, persistence false: one File node (`maintain_framework.py`), 31 nodes, 64 edges, zero skipped. Search/snippet results cover the finder and main. The tool has no commit attestation; raw Git checks bind its source externally. The explicitly named test/evidence used tracked-file reads; no graph absence claim.

## Source disposition

| Boundary | Source reasoning |
| --- | --- |
| Verified bytes, not a later file/cache read | Entry lines 121-137 perform the existing exact row/path/stat/size/hash admission, then retain the same bytes object in `sources`. `exec_module` at lines 85-88 compiles that object with its verified filename; it never calls SourceLoader/get_code or reads a cache. This closes the CR-001 path even when a cache is valid for normal Python loading. |
| Package initialization and recursive imports | The finder is inserted first at lines 147-149 before importing `distribution`. Lines 72-80 return an explicit self-loader spec for every mapped local name, including the package; recursive imports use the same map and standard module initialization/cycle handling. The package search location remains metadata, not a local fallback for unmapped names. |
| Delayed imports and unknown names | The finder remains active through `execute(raw)` and result serialization, and is removed in the dispatch finally block (lines 169-178). Any unmapped `distribution.*` name raises ImportError at lines 75-76 before later finders can search local files/caches. Already loaded modules originated in this retained-byte path; preloaded local modules are refused before finder installation. |
| Origins and host boundary | Specs retain the selected filename/origin and package location. Non-distribution names return None, leaving the existing isolated stdlib/PyYAML boundary unchanged; the checkout is never added to sys.path. No host dependencies, formats or EnginePin members were added. |
| Existing admission/failures | EnginePin constants/byte budgets and `_direct`, `_pairs`, `_reject_number` were AST-compared unchanged. Source/root/type/hash checks precede finder installation. The unchanged state owner still rechecks source hashes, HEAD, origin and module closure at operation admission. Handled bootstrap refusal removes the finder; dispatch failure remains a failure. |

This conclusion concerns the actual known local source and ordinary import machinery. It does not add protection against arbitrary mutation of interpreter state by already executing code, hostile host libraries or nonparticipating source writers. Those remain outside the accepted host/quiescence boundary. No further product repair is identified by this affected review.

## Test evidence classification

The following are **repair-worker observations read from committed evidence**, not runs performed or independently reproduced here.

| Evidence | What it supports and what it does not |
| --- | --- |
| 9 focused tests reported passing, exit 0, no skips/errors/failures | Test source uses the actual finder/bootstrap with synthetic package bodies and deliberately different caches accepted by a real SourceFileLoader control. It covers all nine mapped modules, package/recursive import, unchecked-hash and timestamp caches, retained bytes after disk change, unknown import refusal, malformed hash/type/closure/preloaded refusals, and finder cleanup. |
| Bootstrap unit seam, lines 116-125 | `__file__`, `_direct`, argv and streams are replaced; normal cases bypass native path checks. Synthetic execute functions do not exercise the public API/state owner's HEAD/origin admission. The separate real nine-module import at lines 232-243 establishes import/loader plumbing only, without installation operations. |
| Delayed and host cases, lines 212-230 | The delayed case verifies refusal of an unknown local name; it is not a positive delayed allowed-module test. Host identity assertions use already imported json/PyYAML, so they do not alone establish fresh host resolution. The corresponding source branches were inspected above; these limits are not new product findings. |
| Exactly one unmodified public-entry attempt | Committed result is child exit 1, source-bootstrap, unsupported, changed=false, empty stderr: blocked before dispatch. The recorded valid-cache control and unchanged pin/source/cache do not convert that refusal into public pinned-source execution success. |
| Public harness, lines 246-277 | Its deliberately incomplete inspect request omits api_version/project_root and creates no installed project. Even a future bootstrap success with that request would not establish successful operation admission or native maintenance. Tool shell exit 1, child exit 1 and harness's source return 2 are retained as distinct observations. |

The generic public refusal does not identify its exact failing predicate. The earlier F: strict-resolve observation remains externally reported, not independently reproduced or established as this attempt's root cause. No retry, native probe, path substitution or path repair was performed here.

## Checks and remaining obligations

This reviewer performed explicit root/branch/HEAD/common-dir/clean-state reads; bounded repair diff inspection; live read-only Issue reads; exact raw source/test/repair-evidence/original-report bindings; UTF-8 and AST parsing of the changed entry and new test; unchanged constant/helper AST comparisons; graph-guided source reasoning and test/evidence reading. These direct checks passed, without product or test imports.

Direct record UTF-8/JSON/YAML syntax, local reference/scope, original-report preservation and Git diff checks passed. The complete planned-message validator passed (exit 0) for affected-commit-message.tmp and this workflow ID; final staged scope/diff inspection precedes the local commit. Writes are only this affected-review.md and updates to this workflow's task.json/workflow.yaml, plus an ignored contained message file. The original report and repair-worker records remain unchanged.

CR-001's source repair is independently supported on this exact subject. **Public-entry execution, full EnginePin operation admission, native installation/recovery, and selected P7 acceptance remain unestablished.** They cannot be closed by this source disposition or the worker's unit result. Source or authority drift requires affected review again.

Coordinator owns transport and bounded Issue disposition, plus subsequent authorized public/native evidence. The rejected work in the original #368/#369 tasks stays with those owners and approval boundaries; this review supplies no bypass or takeover. CI, legacy validators/matrices, audit/lease/receipt tooling, adoption and publication remain **deferred-by-owner** under U001 to program #322 coordinator / P7. No push, provider mutation or Issue closure occurred.
